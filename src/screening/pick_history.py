"""Persistent scan snapshots and derived pick-consistency statistics."""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
from functools import lru_cache
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from src.utils.json_safe import sanitize_nan


SCHEMA_VERSION = 1
SCORING_VERSION = "v1"
RUN_KIND_DAILY_FULL = "daily_full"
DEFAULT_LEDGER_ROOT = Path(__file__).resolve().parents[2] / "data" / "pick_history"
LIST_NAMES = ("shortlist", "top20")
_RUN_KINDS = (RUN_KIND_DAILY_FULL,)
_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
_SCORE_FIELDS = ("score", "composite_score", "combined_score")


@lru_cache(maxsize=1)
def _et() -> ZoneInfo:
    # Resolved on first use, not at import: read-only callers (the dashboard's
    # history API) never need tz data, so a missing tz database must not be
    # able to break importing this module.
    return ZoneInfo("America/New_York")


def _as_datetime(value: datetime | str | None) -> datetime:
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
    return value


def _utc_iso(value: datetime | str | None) -> str:
    return _as_datetime(value).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def session_date_et(dt: datetime | str | None = None) -> str:
    """Return the America/New_York date for a timestamp."""
    return _as_datetime(dt).astimezone(_et()).date().isoformat()


def _normalise_ticker(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _slim_rows(rows: list[dict[str, Any]] | None, list_name: str) -> list[dict[str, Any]] | None:
    if rows is None:
        return None

    slim: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in rows:
        ticker = _normalise_ticker(raw.get("ticker"))
        # A duplicate from an upstream quirk (e.g. a merged batch) must not cost
        # the whole day's snapshot; the first occurrence holds the better rank.
        if not ticker or ticker in seen:
            continue
        seen.add(ticker)
        rank = len(slim) + 1
        if list_name == "shortlist":
            row = {
                "ticker": ticker,
                "rank": rank,
                "score": raw.get("score"),
                "composite_score": raw.get("composite_score"),
                "passed_filters": raw.get("passed_filters"),
            }
        else:
            row = {
                "ticker": ticker,
                "rank": rank,
                "score": raw.get("score"),
                "combined_score": raw.get("combined_score"),
            }
        slim.append(sanitize_nan(row))
    return slim


def build_snapshot(
    *,
    session_date: str,
    generated_at: datetime | str,
    provenance: str,
    scope: dict[str, Any],
    shortlist: list[dict[str, Any]] | None,
    top20: list[dict[str, Any]] | None,
    run_kind: str = RUN_KIND_DAILY_FULL,
    source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a slim version-one pick-history snapshot."""
    lists = {
        "shortlist": _slim_rows(shortlist, "shortlist"),
        "top20": _slim_rows(top20, "top20"),
    }
    produced = [rows for rows in lists.values() if rows is not None]
    result = "no_candidates" if produced and all(not rows for rows in produced) else "success"
    return sanitize_nan(
        {
            "schema_version": SCHEMA_VERSION,
            "run_kind": run_kind,
            "provenance": provenance,
            "session_date": session_date,
            "generated_at": _utc_iso(generated_at),
            "scoring_version": SCORING_VERSION,
            "source": dict(source or {}),
            "scope": dict(scope),
            "result": result,
            "lists": lists,
        }
    )


def _validate_session_date(value: Any) -> None:
    if not isinstance(value, str) or not _DATE_PATTERN.fullmatch(value):
        raise ValueError("session_date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("session_date must be YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise ValueError("session_date must be YYYY-MM-DD")


def validate_snapshot(snapshot: Any) -> None:
    """Raise ValueError when a snapshot violates the version-one contract."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a dict")
    required_fields = {
        "schema_version",
        "run_kind",
        "provenance",
        "session_date",
        "generated_at",
        "scoring_version",
        "source",
        "scope",
        "result",
        "lists",
    }
    missing_fields = sorted(required_fields - snapshot.keys())
    if missing_fields:
        raise ValueError(f"snapshot is missing required fields: {', '.join(missing_fields)}")
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if snapshot.get("run_kind") not in _RUN_KINDS:
        raise ValueError(f"unknown run_kind: {snapshot.get('run_kind')!r}")
    if snapshot.get("provenance") not in ("live", "backfill"):
        raise ValueError("provenance must be 'live' or 'backfill'")
    _validate_session_date(snapshot.get("session_date"))

    lists = snapshot.get("lists")
    if not isinstance(lists, dict):
        raise ValueError("lists must be a dict")

    produced = 0
    for list_name in LIST_NAMES:
        if list_name not in lists:
            raise ValueError(f"lists is missing {list_name}")
        rows = lists.get(list_name)
        if rows is None:
            continue
        produced += 1
        if not isinstance(rows, list):
            raise ValueError(f"lists.{list_name} must be a list or None")

        seen: set[str] = set()
        for position, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                raise ValueError(f"lists.{list_name} row {position} must be a dict")
            if "ticker" not in row or not _normalise_ticker(row.get("ticker")):
                raise ValueError(f"lists.{list_name} row {position} is missing ticker")
            if "rank" not in row:
                raise ValueError(f"lists.{list_name} row {position} is missing rank")
            ticker = _normalise_ticker(row["ticker"])
            if ticker in seen:
                raise ValueError(f"duplicate ticker {ticker!r} in {list_name}")
            seen.add(ticker)
            rank = row["rank"]
            if isinstance(rank, bool) or not isinstance(rank, int) or rank != position:
                raise ValueError(f"lists.{list_name} ranks must be consecutive integers starting at 1")
            for field in _SCORE_FIELDS:
                value = row.get(field)
                if isinstance(value, float) and not math.isfinite(value):
                    raise ValueError(f"non-finite {field} for {ticker} in {list_name}")

    if not produced:
        raise ValueError("at least one list must be produced")


def snapshot_path(
    session_date: str,
    run_kind: str = RUN_KIND_DAILY_FULL,
    root: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the canonical path for a session snapshot."""
    ledger_root = DEFAULT_LEDGER_ROOT if root is None else Path(root)
    return ledger_root / "snapshots" / run_kind / f"{session_date}.json"


def write_snapshot(
    snapshot: dict[str, Any], root: str | os.PathLike[str] | None = None
) -> Path:
    """Validate and atomically replace a session snapshot."""
    validate_snapshot(snapshot)
    clean_snapshot = sanitize_nan(snapshot)
    final_path = snapshot_path(snapshot["session_date"], snapshot["run_kind"], root)
    final_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=final_path.parent,
            prefix=f".{final_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            json.dump(clean_snapshot, handle, indent=2, sort_keys=True, allow_nan=False)
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


def record_scan(
    *,
    shortlist: list[dict[str, Any]] | None,
    top20: list[dict[str, Any]] | None,
    scope: dict[str, Any],
    generated_at: datetime | str | None = None,
    source: dict[str, Any] | None = None,
    root: str | os.PathLike[str] | None = None,
    provenance: str = "live",
    allow_downgrade: bool = False,
) -> Path:
    """Build and persist a daily full-universe snapshot.

    A later same-day run that finds NO candidates never replaces a same-day
    session that found some: a full-universe scan legitimately finding nothing
    right after finding picks is far more likely a broken or rate-limited run
    than a real market change, and recording it would reset every streak.
    """
    timestamp = datetime.now(timezone.utc) if generated_at is None else generated_at
    snapshot = build_snapshot(
        session_date=session_date_et(timestamp),
        generated_at=timestamp,
        provenance=provenance,
        scope=scope,
        shortlist=shortlist,
        top20=top20,
        source=source,
    )
    if not allow_downgrade and snapshot["result"] == "no_candidates":
        existing_path = snapshot_path(snapshot["session_date"], snapshot["run_kind"], root)
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            existing = None
        if isinstance(existing, dict) and existing.get("result") == "success":
            raise ValueError(
                f"refusing to replace the {snapshot['session_date']} session that found candidates "
                "with a no-candidates run (pass allow_downgrade=True to force)"
            )
    return write_snapshot(snapshot, root=root)


def load_snapshots(
    root: str | os.PathLike[str] | None = None,
    run_kind: str = RUN_KIND_DAILY_FULL,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Load valid snapshots, skipping bad files with warnings."""
    directory = snapshot_path("placeholder", run_kind, root).parent
    if not directory.is_dir():
        return [], []

    snapshots: list[dict[str, Any]] = []
    warnings: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                snapshot = json.load(handle)
            validate_snapshot(snapshot)
            if path.stem != snapshot["session_date"]:
                raise ValueError(
                    f"filename date {path.stem!r} does not match session_date "
                    f"{snapshot['session_date']!r}"
                )
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            warnings.append(f"Skipped {path.name}: {exc}")
            continue
        snapshots.append(snapshot)

    snapshots.sort(key=lambda item: item["session_date"])
    return snapshots, warnings


def _numeric_score(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _row_score(row: dict[str, Any], list_name: str) -> float | None:
    preferred = "composite_score" if list_name == "shortlist" else "combined_score"
    score = _numeric_score(row.get(preferred))
    return score if score is not None else _numeric_score(row.get("score"))


def _missing_weekdays(after: str, before: str) -> int:
    start = date.fromisoformat(after).toordinal() + 1
    stop = date.fromisoformat(before).toordinal()
    return sum(date.fromordinal(day).weekday() < 5 for day in range(start, stop))


def _empty_history(
    list_name: str, window: int, warnings: list[str], run_kind: str
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "list": list_name,
        "run_kind": run_kind,
        "window_requested": window,
        "sessions_available": 0,
        "sessions": [],
        "denominator": 0,
        "latest_session_date": None,
        "coverage_gaps": [],
        "warnings": warnings,
        "tickers": {},
    }


def compute_history(
    snapshots: list[dict[str, Any]],
    list_name: str = "shortlist",
    window: int = 5,
    warnings: list[str] | None = None,
    run_kind: str = RUN_KIND_DAILY_FULL,
) -> dict[str, Any]:
    """Derive consistency statistics from ordered recorded scan sessions."""
    if list_name not in LIST_NAMES:
        raise ValueError(f"unknown list_name: {list_name!r}")
    window = max(1, window)
    output_warnings = list(warnings) if warnings is not None else []
    if not snapshots:
        return _empty_history(list_name, window, output_warnings, run_kind)

    ordered = sorted(snapshots, key=lambda item: item["session_date"])
    coverage_gaps = []
    for previous, current in zip(ordered, ordered[1:]):
        missing = _missing_weekdays(previous["session_date"], current["session_date"])
        if missing:
            coverage_gaps.append(
                {
                    "after": previous["session_date"],
                    "before": current["session_date"],
                    "missing_weekdays": missing,
                }
            )

    produced = [snapshot for snapshot in ordered if snapshot["lists"][list_name] is not None]
    if not produced:
        result = _empty_history(list_name, window, output_warnings, run_kind)
        result["coverage_gaps"] = coverage_gaps
        return result

    window_sessions = produced[-window:]
    session_dates = [snapshot["session_date"] for snapshot in window_sessions]
    denominator = len(window_sessions)

    full_presence: dict[str, list[bool]] = {}
    full_rows: dict[str, list[tuple[str, dict[str, Any], str | None]]] = {}
    for session_index, snapshot in enumerate(produced):
        present = {_normalise_ticker(row["ticker"]): row for row in snapshot["lists"][list_name]}
        for ticker in full_presence:
            full_presence[ticker].append(False)
        for ticker, row in present.items():
            if ticker not in full_presence:
                full_presence[ticker] = [False] * session_index + [True]
            else:
                full_presence[ticker][-1] = True
            full_rows.setdefault(ticker, []).append(
                (snapshot["session_date"], row, snapshot.get("scoring_version"))
            )

    window_rows: dict[str, list[tuple[str, dict[str, Any], str | None]]] = {}
    for snapshot in window_sessions:
        for row in snapshot["lists"][list_name]:
            ticker = _normalise_ticker(row["ticker"])
            window_rows.setdefault(ticker, []).append(
                (snapshot["session_date"], row, snapshot.get("scoring_version"))
            )

    ticker_stats: dict[str, dict[str, Any]] = {}
    for ticker in sorted(window_rows):
        appearances = window_rows[ticker]
        all_appearances = full_rows[ticker]
        presence = full_presence[ticker]
        longest = 0
        running = 0
        for appeared in presence:
            running = running + 1 if appeared else 0
            longest = max(longest, running)
        current = 0
        for appeared in reversed(presence):
            if not appeared:
                break
            current += 1

        scores = [_row_score(row, list_name) for _, row, _ in appearances]
        numeric_scores = [score for score in scores if score is not None]
        latest_score = scores[-1]
        score_delta = None
        if len(appearances) >= 2:
            previous_score = scores[-2]
            if (
                latest_score is not None
                and previous_score is not None
                and appearances[-1][2] == appearances[-2][2]
            ):
                score_delta = round(latest_score - previous_score, 4)

        ranks = [row["rank"] for _, row, _ in appearances]
        history = [
            {
                "date": session_date,
                "rank": row["rank"],
                "score": round(score, 4) if score is not None else None,
            }
            for (session_date, row, _), score in zip(appearances, scores)
        ]
        ticker_stats[ticker] = {
            "appearances": len(appearances),
            "denominator": denominator,
            "appearance_rate": round(len(appearances) / denominator, 4),
            "current_streak": current,
            "longest_streak": longest,
            "total_appearances": len(all_appearances),
            "first_seen": all_appearances[0][0],
            "last_seen": all_appearances[-1][0],
            "is_active_today": presence[-1],
            "best_rank": min(ranks),
            "average_rank": round(sum(ranks) / len(ranks), 4),
            "average_score": (
                round(sum(numeric_scores) / len(numeric_scores), 4) if numeric_scores else None
            ),
            "latest_score": round(latest_score, 4) if latest_score is not None else None,
            "score_delta": score_delta,
            "history": history,
        }

    return sanitize_nan(
        {
            "schema_version": SCHEMA_VERSION,
            "list": list_name,
            "run_kind": run_kind,
            "window_requested": window,
            "sessions_available": len(produced),
            "sessions": session_dates,
            "denominator": denominator,
            "latest_session_date": produced[-1]["session_date"],
            "coverage_gaps": coverage_gaps,
            "warnings": output_warnings,
            "tickers": ticker_stats,
        }
    )
