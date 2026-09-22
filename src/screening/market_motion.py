"""Market-motion frames and the per-stock tracker derived from them.

A *frame* is one completed observation of the buy-opportunity population: every
qualified buy signal (score >= 60 of 125) plus an honest outcome for every stock
that has ever qualified and is still being tracked. Frames are immutable,
timestamp-keyed JSON files; the tracker (tiers, streaks, denominators) is
DERIVED on read and never stored, exactly like the pick-history ledger.

This is deliberately a separate store from ``pick_history``: that ledger's whole
vocabulary is "one recorded session per ET day" and its badges must never be
inflated by several intraday frames.

Evaluation states (a ticker's outcome in one frame):

    qualified       scored, is_buy, score >= threshold; has real coordinates
    not_qualified   scored but below the threshold; has real coordinates
    not_scored      the scanner did not score it (Phase != 2, or it failed the
                    Minervini template); NO reliable coordinates, ``drop_reason``
    error           the run tried and failed to evaluate it
    not_evaluated   the run did not look at it (roster overflow, partial scope)

"Absent" is never interpreted as "dropped": absence and error/not_evaluated are
all *unknown* and are excluded from denominators. An unknown session breaks a
streak, because claiming consecutive quality across a gap would be a guess.
"""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from functools import lru_cache
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from src.utils.json_safe import sanitize_nan

SCHEMA_VERSION = 1
SCORING_VERSION = "v1"

RUN_KIND_DAILY_FULL = "daily_full"
RUN_KIND_INTRADAY = "intraday_rescore"
RUN_KIND_LEGACY = "legacy_report"
RUN_KINDS = (RUN_KIND_DAILY_FULL, RUN_KIND_INTRADAY, RUN_KIND_LEGACY)
_DAILY_KINDS = (RUN_KIND_DAILY_FULL, RUN_KIND_LEGACY)

EVAL_QUALIFIED = "qualified"
EVAL_NOT_QUALIFIED = "not_qualified"
EVAL_NOT_SCORED = "not_scored"
EVAL_ERROR = "error"
EVAL_NOT_EVALUATED = "not_evaluated"
EVALUATIONS = (EVAL_QUALIFIED, EVAL_NOT_QUALIFIED, EVAL_NOT_SCORED, EVAL_ERROR, EVAL_NOT_EVALUATED)
_UNKNOWN_EVALS = (EVAL_ERROR, EVAL_NOT_EVALUATED)

COVERAGE_COMPLETE = "complete_for_scope"
COVERAGE_TOP50 = "top50_only"
COVERAGE_KINDS = (COVERAGE_COMPLETE, COVERAGE_TOP50)

MAX_SCORE = 125
BUY_THRESHOLD = 60
RS_METRIC = "rs_slope_20"

TIER_ACTIVE = "active"
TIER_WATCHING = "watching"
TIER_RETIRED = "retired"
RETIRE_AFTER_SESSIONS = 10
DEFAULT_ROSTER_CAP = 500
HISTORY_CAP = 30

DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "data" / "market_motion"

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_RUN_ID_RE = re.compile(r"\d{8}T\d{6}Z-(?:daily_full|intraday_rescore|legacy_report)")
_TICKER_RE = re.compile(r"[A-Z0-9][A-Z0-9.\-^]{0,9}")
_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍✓⚠]"
)

_POINT_NUMERIC = ("score", "rs", "current_price", "stop_loss", "rr_ratio")
_POINT_OPTIONAL = (
    "phase", "entry_quality", "rank", "top_reason", "drop_reason", "error_code",
)


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def normalise_ticker(value: Any) -> str:
    return "" if value is None else str(value).strip().upper()


def strip_emoji(text: Any) -> str:
    """Remove emoji/dingbat glyphs (project rule: no emoji in stored UI text)."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", _EMOJI_RE.sub("", str(text))).strip()


def _num(value: Any) -> float | None:
    """A finite float or None. Never coerces a missing value to zero."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _utc(value: datetime | str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"invalid generated_at: {value!r}") from exc
    if not isinstance(value, datetime):
        raise ValueError("generated_at must be an ISO string or datetime")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


@lru_cache(maxsize=1)
def _et() -> ZoneInfo:
    # Lazy: read-only callers never need tz data.
    return ZoneInfo("America/New_York")


def session_date_from_bar(value: Any) -> str:
    """The trading-session date (YYYY-MM-DD) a price bar belongs to.

    A frame's session date is the date of the DATA (SPY's newest daily bar), not
    the wall-clock date the job ran: a weekend or holiday run holds Friday's
    data and must be labelled Friday. Accepts date, datetime or pandas
    Timestamp; tz-aware values are converted to America/New_York, naive values
    are taken as already being an exchange date.
    """
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(_et())
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and _DATE_RE.fullmatch(value[:10]):
        return value[:10]
    raise ValueError(f"cannot derive a session date from {value!r}")


def is_data_current(bar_value: Any, now: datetime | None = None) -> bool:
    """True when the newest bar is today's (ET) session, i.e. the market traded
    today. False on weekends/holidays (and before the first bar of the day)."""
    now = datetime.now(timezone.utc) if now is None else _utc(now)
    return session_date_from_bar(bar_value) == now.astimezone(_et()).date().isoformat()


def make_run_id(generated_at: datetime | str | None, run_kind: str) -> str:
    return f"{_utc(generated_at):%Y%m%dT%H%M%SZ}-{run_kind}"


def _check_date(value: Any, name: str) -> None:
    if not isinstance(value, str) or not _DATE_RE.fullmatch(value):
        raise ValueError(f"{name} must be YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be YYYY-MM-DD") from exc


# ---------------------------------------------------------------------------
# points
# ---------------------------------------------------------------------------

def make_point(ticker: Any, evaluation: str, **fields: Any) -> dict[str, Any]:
    """Build one slim point. Non-finite numbers become absent, emoji is stripped."""
    if evaluation not in EVALUATIONS:
        raise ValueError(f"unknown evaluation {evaluation!r}")
    point: dict[str, Any] = {"ticker": normalise_ticker(ticker), "evaluation": evaluation}
    for key in _POINT_NUMERIC:
        value = _num(fields.get(key))
        if value is not None:
            point[key] = round(value, 4)
    for key in _POINT_OPTIONAL:
        value = fields.get(key)
        if value is None or value == "":
            continue
        if key in ("top_reason", "drop_reason", "error_code", "entry_quality"):
            value = strip_emoji(value)
            if not value:
                continue
        elif key in ("phase", "rank"):
            value = int(value) if _num(value) is not None else None
            if value is None:
                continue
        point[key] = value
    return point


def normalize_buy_signal(signal: dict[str, Any], rank: int | None = None) -> dict[str, Any]:
    """Map a scanner buy signal (``score_buy_signal`` output) to a qualified point.

    The in-memory signal has no ``max_score``; ``rs`` is ``details['rs_slope']``
    (the 20-day RS slope the report prints as "RS:") and ``rr_ratio`` is
    ``risk_reward_ratio``. Accepts already-flat dicts (``rs``/``rr_ratio``) too,
    so report-parsed signals go through the same function.
    """
    details = signal.get("details") or {}
    rs = signal.get("rs") if "rs" in signal else details.get("rs_slope")
    rr = signal.get("rr_ratio") if "rr_ratio" in signal else signal.get("risk_reward_ratio")
    reasons = signal.get("reasons") or []
    return make_point(
        signal.get("ticker"),
        EVAL_QUALIFIED,
        score=signal.get("score"),
        rs=rs,
        phase=signal.get("phase"),
        entry_quality=signal.get("entry_quality"),
        current_price=signal.get("current_price"),
        stop_loss=signal.get("stop_loss"),
        rr_ratio=rr,
        rank=rank if rank is not None else signal.get("rank"),
        top_reason=reasons[0] if reasons else None,
    )


def outcome_point(
    ticker: Any,
    *,
    signal: dict[str, Any] | None = None,
    phase: Any = None,
    error: str | None = None,
    threshold: float = BUY_THRESHOLD,
) -> dict[str, Any]:
    """Outcome for a tracked ticker that did NOT qualify in this run.

    ``signal`` is the ``score_buy_signal`` result when the scanner scored it. A
    real score with a real RS below the threshold is ``not_qualified`` and keeps
    coordinates. A zero/absent score (Phase != 2, failed Minervini template) is
    ``not_scored``: it has no honest coordinates, only a ``drop_reason``.
    With neither a signal nor a phase, ``error`` marks a failed evaluation and
    no arguments at all marks ``not_evaluated``.
    """
    if error:
        return make_point(ticker, EVAL_ERROR, error_code=error)
    if signal is None:
        if phase is not None:
            # Phase 3/4 is a real reason. A phase 1/2 stock with no scored signal
            # simply was not scored this run (e.g. the regime gate suppressed buys).
            reason = f"phase_{phase}" if phase in (3, 4) else "not_scored"
            return make_point(ticker, EVAL_NOT_SCORED, phase=phase, drop_reason=reason)
        return make_point(ticker, EVAL_NOT_EVALUATED)
    details = signal.get("details") or {}
    score = _num(signal.get("score"))
    rs = _num(signal.get("rs") if "rs" in signal else details.get("rs_slope"))
    # Same numpy.bool_ identity trap as above: `is True`/`is not True` looks
    # right but silently fails for numpy-typed booleans, which is exactly
    # what score_buy_signal's is_buy is. Truthy checks only.
    is_buy = bool(signal.get("is_buy"))
    if score is not None and score > 0 and rs is not None and not is_buy:
        return make_point(
            ticker, EVAL_NOT_QUALIFIED, score=score, rs=rs,
            phase=signal.get("phase", phase), drop_reason="below_buy_threshold",
        )
    if is_buy and score is not None and score >= threshold and rs is not None:
        return normalize_buy_signal(signal)
    return make_point(
        ticker, EVAL_NOT_SCORED, phase=signal.get("phase", phase),
        drop_reason=signal.get("reason") or "not_scored",
    )


def _better(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Pick the more informative of two points for the same ticker."""
    def key(p: dict[str, Any]) -> tuple:
        return (
            p["evaluation"] == EVAL_QUALIFIED,
            p["evaluation"] not in _UNKNOWN_EVALS,
            -(p.get("rank") or 10**9),
            p.get("score") or 0.0,
        )
    return a if key(a) >= key(b) else b


def dedupe_points(points: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """One point per ticker, order of first appearance, best information wins."""
    order: list[str] = []
    best: dict[str, dict[str, Any]] = {}
    for raw in points:
        ticker = normalise_ticker(raw.get("ticker"))
        if not ticker:
            continue
        point = dict(raw, ticker=ticker)
        if ticker not in best:
            order.append(ticker)
            best[ticker] = point
        else:
            best[ticker] = _better(best[ticker], point)
    return [best[t] for t in order]


# ---------------------------------------------------------------------------
# frames
# ---------------------------------------------------------------------------

def build_frame(
    *,
    run_kind: str,
    generated_at: datetime | str,
    session_date: str,
    points: Iterable[dict[str, Any]],
    scope: dict[str, Any],
    coverage: dict[str, Any] | None = None,
    regime: dict[str, Any] | None = None,
    fundamentals_as_of: str | None = None,
    provenance: str = "live",
    source: dict[str, Any] | None = None,
    scoring_version: str = SCORING_VERSION,
) -> dict[str, Any]:
    """Build a version-one frame. Points are deduplicated by ticker."""
    if run_kind not in RUN_KINDS:
        raise ValueError(f"unknown run_kind {run_kind!r}")
    deduped = dedupe_points(points)
    qualified = sum(1 for p in deduped if p["evaluation"] == EVAL_QUALIFIED)
    cov = dict(coverage or {})
    cov.setdefault("kind", COVERAGE_COMPLETE)
    cov.setdefault("qualified_total", qualified)
    cov.setdefault("located_points", qualified)
    scope_out = dict(scope)
    scope_out.setdefault("completed", True)
    frame = {
        "schema_version": SCHEMA_VERSION,
        "run_id": make_run_id(generated_at, run_kind),
        "run_kind": run_kind,
        "provenance": provenance,
        "generated_at": _iso(_utc(generated_at)),
        "session_date": session_date,
        "scoring_version": scoring_version,
        "score_model": {"max_score": MAX_SCORE, "buy_threshold": BUY_THRESHOLD, "rs_metric": RS_METRIC},
        "regime": dict(regime or {"should_generate_buys": None, "source_run_id": None}),
        "fundamentals_as_of": fundamentals_as_of,
        "source": dict(source or {}),
        "scope": scope_out,
        "coverage": cov,
        "points": deduped,
    }
    return sanitize_nan(frame)


def validate_frame(frame: Any) -> None:
    """Raise ValueError if ``frame`` violates the version-one schema."""
    if not isinstance(frame, dict):
        raise ValueError("frame must be an object")
    if frame.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version {frame.get('schema_version')!r}")
    if frame.get("run_kind") not in RUN_KINDS:
        raise ValueError(f"unknown run_kind {frame.get('run_kind')!r}")
    run_id = frame.get("run_id")
    if not isinstance(run_id, str) or not _RUN_ID_RE.fullmatch(run_id):
        raise ValueError("run_id is malformed")
    if not run_id.endswith("-" + frame["run_kind"]):
        raise ValueError("run_id does not match run_kind")
    _check_date(frame.get("session_date"), "session_date")
    generated = frame.get("generated_at")
    if not isinstance(generated, str):
        raise ValueError("generated_at must be an ISO string")
    _utc(generated)
    if _iso(_utc(generated)) != generated:
        raise ValueError("generated_at must be canonical UTC ('...Z')")
    if make_run_id(generated, frame["run_kind"]) != run_id:
        raise ValueError("run_id does not match generated_at")
    if not isinstance(frame.get("scoring_version"), str) or not frame["scoring_version"]:
        raise ValueError("scoring_version must be a non-empty string")
    model = frame.get("score_model")
    if not isinstance(model, dict) or not (_num(model.get("max_score")) or 0) > 0:
        raise ValueError("score_model.max_score must be positive")
    scope = frame.get("scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("completed"), bool):
        raise ValueError("scope.completed must be a boolean")
    coverage = frame.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("kind") not in COVERAGE_KINDS:
        raise ValueError("coverage.kind is invalid")
    points = frame.get("points")
    if not isinstance(points, list):
        raise ValueError("points must be a list")
    seen: set[str] = set()
    for i, p in enumerate(points):
        if not isinstance(p, dict):
            raise ValueError(f"points[{i}] must be an object")
        ticker = p.get("ticker")
        if not isinstance(ticker, str) or not _TICKER_RE.fullmatch(ticker):
            raise ValueError(f"points[{i}].ticker is invalid")
        if ticker in seen:
            raise ValueError(f"duplicate ticker {ticker}")
        seen.add(ticker)
        evaluation = p.get("evaluation")
        if evaluation not in EVALUATIONS:
            raise ValueError(f"points[{i}].evaluation is invalid")
        # A qualified buy may lack an RS reading (the scanner leaves rs_slope None
        # when the RS series is unavailable): it still counts as qualified, it
        # just has no honest x coordinate. not_qualified is only ever recorded
        # WITH coordinates, otherwise it would be not_scored.
        required = ("score",) if evaluation == EVAL_QUALIFIED else ("score", "rs") if evaluation == EVAL_NOT_QUALIFIED else ()
        for field in required:
            if _num(p.get(field)) is None:
                raise ValueError(f"points[{i}] ({evaluation}) needs a finite {field}")
        for field in _POINT_NUMERIC:
            if field in p and _num(p[field]) is None:
                raise ValueError(f"points[{i}].{field} must be finite")


def frame_path(frame_or_kind: dict[str, Any] | str, run_id: str | None = None,
               root: str | os.PathLike[str] | None = None) -> Path:
    base = DEFAULT_ROOT if root is None else Path(root)
    if isinstance(frame_or_kind, dict):
        kind, rid = frame_or_kind["run_kind"], frame_or_kind["run_id"]
    else:
        kind, rid = frame_or_kind, run_id
    return base / "snapshots" / kind / f"{rid}.json"


def write_frame(frame: dict[str, Any], root: str | os.PathLike[str] | None = None) -> Path:
    """Validate then atomically write a frame (same run_id replaces itself)."""
    validate_frame(frame)
    clean = sanitize_nan(frame)
    final_path = frame_path(clean, root=root)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=final_path.parent,
            prefix=f".{final_path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            json.dump(clean, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, final_path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
    return final_path


def load_frames(
    root: str | os.PathLike[str] | None = None,
    run_kinds: Iterable[str] | None = None,
    completed_only: bool = True,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Load valid frames ordered by (generated_at, run_id). Corrupt files are
    skipped with a warning; incomplete frames are skipped unless asked for."""
    base = DEFAULT_ROOT if root is None else Path(root)
    kinds = tuple(run_kinds) if run_kinds is not None else RUN_KINDS
    frames: list[dict[str, Any]] = []
    warnings: list[str] = []
    for kind in kinds:
        directory = base / "snapshots" / kind
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            if path.name.startswith("."):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                validate_frame(data)
                if data["run_id"] != path.stem or data["run_kind"] != kind:
                    raise ValueError("file name does not match run_id/run_kind")
            except (OSError, ValueError) as exc:
                warnings.append(f"Skipped {kind}/{path.name}: {exc}")
                continue
            if completed_only and not data["scope"]["completed"]:
                continue
            frames.append(data)
    frames.sort(key=lambda f: (f["generated_at"], f["run_id"]))
    return frames, warnings


def thin_intraday(root: str | os.PathLike[str] | None = None, keep_full_sessions: int = 30) -> list[Path]:
    """Keep every intraday frame for the newest ``keep_full_sessions`` session
    dates; for older dates keep only the last frame of the day. Returns the
    removed paths. Only touches ``snapshots/intraday_rescore``."""
    frames, _ = load_frames(root, run_kinds=(RUN_KIND_INTRADAY,), completed_only=False)
    dates = sorted({f["session_date"] for f in frames})
    old_dates = set(dates[:-keep_full_sessions]) if keep_full_sessions > 0 else set(dates)
    removed: list[Path] = []
    for d in old_dates:
        day = [f for f in frames if f["session_date"] == d]
        for f in day[:-1]:
            path = frame_path(f, root=root)
            try:
                path.unlink()
                removed.append(path)
            except FileNotFoundError:
                pass
    return removed


# ---------------------------------------------------------------------------
# tracker (derived on read)
# ---------------------------------------------------------------------------

def _coverage_rank(frame: dict[str, Any]) -> tuple:
    return (
        frame["run_kind"] == RUN_KIND_DAILY_FULL,
        frame["coverage"]["kind"] == COVERAGE_COMPLETE,
        frame["generated_at"],
    )


def select_daily_sessions(frames: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """One primary frame per session date, chronological. A live full-universe
    frame beats a top-50 legacy backfill for the same date; among equals the
    latest wins. Intraday frames are never session records."""
    best: dict[str, dict[str, Any]] = {}
    for frame in frames:
        if frame["run_kind"] not in _DAILY_KINDS or not frame["scope"].get("completed"):
            continue
        cur = best.get(frame["session_date"])
        if cur is None or _coverage_rank(frame) > _coverage_rank(cur):
            best[frame["session_date"]] = frame
    return [best[d] for d in sorted(best)]


def _state(point: dict[str, Any] | None) -> str:
    """'Q' qualified, 'N' observed-not-qualified, 'U' unknown."""
    if point is None or point["evaluation"] in _UNKNOWN_EVALS:
        return "U"
    return "Q" if point["evaluation"] == EVAL_QUALIFIED else "N"


def _is_positioned(point: dict[str, Any] | None) -> bool:
    return bool(point) and _num(point.get("score")) is not None and _num(point.get("rs")) is not None \
        and point["evaluation"] in (EVAL_QUALIFIED, EVAL_NOT_QUALIFIED)


def compute_tracker(
    frames: Iterable[dict[str, Any]],
    *,
    window: int | None = None,
    retire_after: int = RETIRE_AFTER_SESSIONS,
    history_cap: int = HISTORY_CAP,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Derive per-ticker tracker records. Pure; no I/O.

    A ticker is *tracked* once it has qualified in any recorded daily session.
    Streaks and the tier come from the full daily-session history; ``window``
    only limits the appearances/denominator figures (like pick-history).
    """
    all_frames = sorted(
        (f for f in frames if f["scope"].get("completed")),
        key=lambda f: (f["generated_at"], f["run_id"]),
    )
    sessions = select_daily_sessions(all_frames)
    dates = [s["session_date"] for s in sessions]
    by_session = [{p["ticker"]: p for p in s["points"]} for s in sessions]
    top50_dates = [s["session_date"] for s in sessions if s["coverage"]["kind"] == COVERAGE_TOP50]

    tracked = {t for m in by_session for t, p in m.items() if p["evaluation"] == EVAL_QUALIFIED}
    win = None if window is None else max(1, int(window))
    win_start = 0 if win is None else max(0, len(sessions) - win)

    newest_frame = all_frames[-1] if all_frames else None
    # The frame streak is a same-session, tooltip-only figure: frames of the newest
    # session date, so it can never masquerade as (or leak into) the day streak.
    newest_date = newest_frame["session_date"] if newest_frame else None
    today_frames = [f for f in all_frames if f["run_kind"] != RUN_KIND_LEGACY and f["session_date"] == newest_date]
    latest_by_ticker: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    position_by_ticker: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for frame in all_frames:
        for p in frame["points"]:
            if p["ticker"] in tracked and p["evaluation"] not in _UNKNOWN_EVALS:
                latest_by_ticker[p["ticker"]] = (frame, p)
            if p["ticker"] in tracked and _is_positioned(p):
                position_by_ticker[p["ticker"]] = (frame, p)

    tickers: dict[str, dict[str, Any]] = {}
    counts = {TIER_ACTIVE: 0, TIER_WATCHING: 0, TIER_RETIRED: 0}
    for ticker in sorted(tracked):
        states = [_state(m.get(ticker)) for m in by_session]

        longest = run = 0
        for s in states:
            run = run + 1 if s == "Q" else 0
            longest = max(longest, run)
        current = 0
        for s in reversed(states):
            if s != "Q":
                break
            current += 1

        q_idx = [i for i, s in enumerate(states) if s == "Q"]
        last_q = q_idx[-1]
        since = len(states) - 1 - last_q
        tier = TIER_ACTIVE if since == 0 else TIER_WATCHING if since <= retire_after else TIER_RETIRED
        counts[tier] += 1

        w_states = states[win_start:]
        observed = sum(1 for s in w_states if s != "U")
        qualified_n = sum(1 for s in w_states if s == "Q")

        scores = [
            _num(by_session[i][ticker].get("score")) for i in q_idx
            if _num(by_session[i][ticker].get("score")) is not None
        ]

        # score trend: only across the same scoring_version, latest two scored sessions
        scored_idx = [
            i for i, m in enumerate(by_session)
            if ticker in m and _is_positioned(m[ticker])
        ]
        trend = None
        latest_daily_score = None
        if scored_idx:
            latest_daily_score = _num(by_session[scored_idx[-1]][ticker]["score"])
            if len(scored_idx) >= 2:
                a, b = scored_idx[-2], scored_idx[-1]
                if sessions[a]["scoring_version"] == sessions[b]["scoring_version"]:
                    trend = round(_num(by_session[b][ticker]["score"]) - _num(by_session[a][ticker]["score"]), 4)

        history = []
        for i in range(max(0, len(sessions) - history_cap), len(sessions)):
            p = by_session[i].get(ticker)
            entry: dict[str, Any] = {"date": dates[i], "state": {"Q": "qualified", "N": "not_qualified", "U": "unknown"}[states[i]]}
            if p is not None and p["evaluation"] not in _UNKNOWN_EVALS:
                if _num(p.get("score")) is not None:
                    entry["score"] = p["score"]
                if _num(p.get("rs")) is not None:
                    entry["rs"] = p["rs"]
            history.append(entry)

        # streak across recent frames (intraday + daily), newest backwards
        frame_streak = 0
        for frame in reversed(today_frames):
            point = next((p for p in frame["points"] if p["ticker"] == ticker), None)
            if _state(point) != "Q":
                break
            frame_streak += 1

        latest_frame, latest_point = latest_by_ticker.get(ticker, (None, None))
        pos_frame, pos_point = position_by_ticker.get(ticker, (None, None))
        record: dict[str, Any] = {
            "tier": tier,
            "first_qualified": dates[q_idx[0]],
            "last_qualified": dates[last_q],
            "sessions_since_qualified": since,
            "current_streak_days": current,
            "longest_streak_days": longest,
            "current_streak_frames": frame_streak,
            "sessions_qualified": qualified_n,
            "sessions_observed": observed,
            "unknown_sessions": sum(1 for s in w_states if s == "U"),
            "best_score": max(scores) if scores else None,
            "average_score": round(sum(scores) / len(scores), 4) if scores else None,
            "latest_daily_score": latest_daily_score,
            "score_trend": trend,
            "history": history,
            "latest": None,
            "position": None,
        }
        if latest_frame is not None:
            record["latest"] = {
                "run_id": latest_frame["run_id"],
                "run_kind": latest_frame["run_kind"],
                "generated_at": latest_frame["generated_at"],
                "is_newest_frame": newest_frame is not None and latest_frame["run_id"] == newest_frame["run_id"],
                **{k: v for k, v in latest_point.items() if k != "ticker"},
            }
        if pos_frame is not None:
            record["position"] = {
                "score": pos_point["score"],
                "rs": pos_point["rs"],
                "max_score": pos_frame["score_model"]["max_score"],
                "run_id": pos_frame["run_id"],
                "generated_at": pos_frame["generated_at"],
                "is_current": latest_frame is not None and pos_frame["run_id"] == latest_frame["run_id"],
            }
        tickers[ticker] = record

    return {
        "schema_version": SCHEMA_VERSION,
        "sessions": dates,
        "sessions_available": len(sessions),
        "window": win,
        "denominator_sessions": len(sessions) - win_start,
        "latest_session_date": dates[-1] if dates else None,
        "newest_frame": (
            {"run_id": newest_frame["run_id"], "run_kind": newest_frame["run_kind"],
             "generated_at": newest_frame["generated_at"], "session_date": newest_frame["session_date"]}
            if newest_frame else None
        ),
        "retire_after_sessions": retire_after,
        "top50_only_sessions": top50_dates,
        "counts": counts,
        "tickers": tickers,
        "warnings": list(warnings or []),
    }


def tracked_tickers(frames: Iterable[dict[str, Any]]) -> set[str]:
    """Every ticker that has ever qualified in a recorded frame (any tier)."""
    return {
        p["ticker"]
        for f in frames if f["scope"].get("completed")
        for p in f["points"] if p["evaluation"] == EVAL_QUALIFIED
    }


def build_roster(tracker: dict[str, Any], cap: int = DEFAULT_ROSTER_CAP) -> dict[str, Any]:
    """Intraday re-score roster: ACTIVE (score desc) then WATCHING (most recently
    qualified first, then score desc), capped. RETIRED tickers are never included."""
    def score(rec: dict[str, Any]) -> float:
        pos = rec.get("position") or {}
        return _num(pos.get("score")) or _num(rec.get("latest_daily_score")) or 0.0

    active = sorted(
        (t for t, r in tracker["tickers"].items() if r["tier"] == TIER_ACTIVE),
        key=lambda t: (-score(tracker["tickers"][t]), t),
    )
    watching = sorted(
        (t for t, r in tracker["tickers"].items() if r["tier"] == TIER_WATCHING),
        key=lambda t: (tracker["tickers"][t]["sessions_since_qualified"], -score(tracker["tickers"][t]), t),
    )
    ordered = active + watching
    limit = max(0, int(cap))
    return {
        "tickers": ordered[:limit],
        "active": len(active),
        "watching": len(watching),
        "overflow": max(0, len(ordered) - limit),
        "cap": limit,
    }
