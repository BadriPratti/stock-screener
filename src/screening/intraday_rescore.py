"""Tracked-roster intraday re-scoring without daily-scan side effects."""

from __future__ import annotations

import json
import logging
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from src.screening import market_motion


logger = logging.getLogger(__name__)

# A run where more than this share of the roster could not be analysed (rate limits,
# network drop-outs) is a broken run, not an observation of the market.
MAX_FAILED_FRACTION = 0.5


def _result(
    status: str,
    reason: str,
    *,
    run_id: str | None = None,
    session_date: str | None = None,
    roster: int = 0,
    analyzed: int = 0,
    started: float,
) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "run_id": run_id,
        "session_date": session_date,
        "roster": roster,
        "analyzed": analyzed,
        "elapsed_seconds": round(max(0.0, time.monotonic() - started), 3),
    }


def _newest_daily_frame(frames: list[dict[str, Any]]) -> dict[str, Any] | None:
    daily = [
        frame
        for frame in frames
        if frame.get("run_kind") in (market_motion.RUN_KIND_DAILY_FULL, market_motion.RUN_KIND_LEGACY)
        and frame.get("scope", {}).get("completed") is True
    ]
    return max(daily, key=lambda frame: (frame["generated_at"], frame["run_id"]), default=None)


def _score_analysis(score_fn: Callable[..., dict[str, Any]], analysis: dict[str, Any]) -> dict[str, Any]:
    """Call the buy scorer with the same inputs as the full scan."""
    return score_fn(
        ticker=analysis["ticker"],
        price_data=analysis["price_data"],
        current_price=analysis["current_price"],
        phase_info=analysis["phase_info"],
        rs_series=analysis["rs_series"],
        fundamentals=analysis.get("quarterly_data"),
        vcp_data=analysis.get("vcp_data"),
    )


def _isolate_fundamentals_cache(processor: Any, temp_root: Path) -> None:
    """Preserve git-cache reads while redirecting any refresh writes to temp."""
    git_fetcher = getattr(processor, "git_fetcher", None)
    source = getattr(git_fetcher, "fundamentals_dir", None)
    if git_fetcher is None or source is None:
        return
    source = Path(source)
    isolated = temp_root / "fundamentals_cache"
    if source.is_dir():
        shutil.copytree(source, isolated)
    else:
        isolated.mkdir(parents=True)
    git_fetcher.fundamentals_dir = isolated
    git_fetcher.metadata_file = isolated / "metadata.json"


def _points_from_analyses(
    roster: list[str],
    overflow: list[str],
    analyses: list[dict[str, Any]],
    score_fn: Callable[..., dict[str, Any]],
    should_generate_buys: Any,
) -> tuple[list[dict[str, Any]], int, int]:
    roster_set = set(roster)
    by_ticker: dict[str, dict[str, Any]] = {}
    for analysis in analyses:
        ticker = market_motion.normalise_ticker(analysis.get("ticker"))
        if ticker in roster_set and ticker not in by_ticker:
            by_ticker[ticker] = analysis

    outcomes: dict[str, dict[str, Any]] = {}
    qualified_signals: list[dict[str, Any]] = []
    for ticker in roster:
        analysis = by_ticker.get(ticker)
        if analysis is None:
            outcomes[ticker] = market_motion.outcome_point(ticker, error="not_analyzed")
            continue

        phase = analysis.get("phase_info", {}).get("phase")
        if phase not in (1, 2):
            outcomes[ticker] = market_motion.outcome_point(ticker, phase=phase)
            continue

        signal = _score_analysis(score_fn, analysis)
        signal["current_price"] = analysis["current_price"]
        # signal_engine.score_buy_signal computes is_buy from numpy-typed
        # intermediate values, so it can come back as numpy.bool_ rather than
        # Python's bool -- `numpy.bool_(True) is True` is False (a different
        # object), which silently misclassified every currently-qualifying
        # stock as not_qualified. Truthy check, not identity.
        if signal.get("is_buy"):
            if should_generate_buys is False:
                point = market_motion.normalize_buy_signal(signal)
                if point.get("rs") is None:
                    # No RS reading means no honest coordinates: not_qualified needs both.
                    outcomes[ticker] = market_motion.make_point(
                        ticker, market_motion.EVAL_NOT_SCORED, phase=phase, drop_reason="regime_gate",
                    )
                else:
                    point["evaluation"] = market_motion.EVAL_NOT_QUALIFIED
                    point.pop("rank", None)
                    point["drop_reason"] = "regime_gate"
                    outcomes[ticker] = point
            else:
                qualified_signals.append(signal)
        else:
            outcomes[ticker] = market_motion.outcome_point(ticker, signal=signal, phase=phase)

    qualified_signals.sort(
        key=lambda signal: (-float(signal.get("score", 0)), market_motion.normalise_ticker(signal.get("ticker")))
    )
    for rank, signal in enumerate(qualified_signals, start=1):
        ticker = market_motion.normalise_ticker(signal.get("ticker"))
        outcomes[ticker] = market_motion.normalize_buy_signal(signal, rank)

    points = [outcomes[ticker] for ticker in roster]
    points.extend(market_motion.outcome_point(ticker) for ticker in overflow)
    analyzed = len(by_ticker)
    return points, analyzed, len(roster) - analyzed


def run_rescore(
    processor_factory: Callable[..., Any],
    score_fn: Callable[..., dict[str, Any]],
    frames_root: str | Path | None,
    cap: int,
    now: datetime | None,
    force: bool,
    dry_run: bool,
    *,
    workers: int = 2,
    delay: float = 1.0,
) -> dict[str, Any]:
    """Run one complete tracked-roster re-score and optionally write its frame."""
    started = time.monotonic()
    generated_at = now or datetime.now(timezone.utc)
    try:
        frames, warnings = market_motion.load_frames(frames_root)
        for warning in warnings:
            logger.warning("Market-motion load warning: %s", warning)
        tracker = market_motion.compute_tracker(frames)
        roster_info = market_motion.build_roster(tracker, cap)
        roster = roster_info["tickers"]
        roster_count = len(roster)
        if not roster:
            return _result(
                "skipped",
                "no_tracked_stocks (run a full scan first)",
                roster=0,
                started=started,
            )

        daily_frame = _newest_daily_frame(frames)
        if daily_frame is None:
            return _result(
                "failed",
                "no_completed_daily_frame",
                roster=roster_count,
                started=started,
            )

        ordered_all = market_motion.build_roster(tracker, cap=10**9)["tickers"]
        overflow = ordered_all[roster_count:]

        # process_batch_parallel saves progress even with resume=False. Both its
        # progress and ordinary price cache are isolated from shared scan state.
        with tempfile.TemporaryDirectory(prefix="intraday-rescore-") as temp_dir:
            temp_root = Path(temp_dir)
            processor = processor_factory(
                max_workers=workers,
                rate_limit_delay=delay,
                use_git_storage=True,
                cache_dir=str(temp_root / "cache"),
                results_dir=str(temp_root / "results"),
            )
            _isolate_fundamentals_cache(processor, temp_root)
            if not processor.fetch_spy_data():
                return _result(
                    "failed",
                    "spy_data_unavailable",
                    roster=roster_count,
                    started=started,
                )
            if processor.spy_data is None or len(processor.spy_data.index) == 0:
                return _result(
                    "failed",
                    "spy_data_unavailable",
                    roster=roster_count,
                    started=started,
                )

            last_spy_bar = processor.spy_data.index[-1]
            session_date = market_motion.session_date_from_bar(last_spy_bar)
            if force:
                logger.warning("FORCE enabled: skipping the market-open data-current guard")
            elif not market_motion.is_data_current(last_spy_bar, now=generated_at):
                return _result(
                    "skipped",
                    "market_closed_or_no_bar_today",
                    session_date=session_date,
                    roster=roster_count,
                    started=started,
                )

            batch = processor.process_batch_parallel(
                roster,
                resume=False,
                min_price=5.0,
                min_volume=100000,
            )

        if not isinstance(batch, dict) or batch.get("error"):
            reason = batch.get("error") if isinstance(batch, dict) else "invalid_processor_result"
            return _result(
                "failed",
                f"processor_failed: {reason}",
                session_date=session_date,
                roster=roster_count,
                started=started,
            )

        points, analyzed, failed = _points_from_analyses(
            roster,
            overflow,
            batch.get("analyses") or [],
            score_fn,
            daily_frame.get("regime", {}).get("should_generate_buys"),
        )
        if analyzed == 0 or failed > MAX_FAILED_FRACTION * roster_count:
            return _result(
                "failed",
                "no_stocks_analyzed" if analyzed == 0 else f"too_many_failures ({failed} of {roster_count})",
                session_date=session_date,
                roster=roster_count,
                analyzed=0,
                started=started,
            )

        frame = market_motion.build_frame(
            run_kind=market_motion.RUN_KIND_INTRADAY,
            generated_at=generated_at,
            session_date=session_date,
            provenance="live",
            points=points,
            regime={
                "should_generate_buys": daily_frame.get("regime", {}).get("should_generate_buys"),
                "source_run_id": daily_frame["run_id"],
            },
            fundamentals_as_of=daily_frame["session_date"],
            scope={
                "mode": "tracked_roster",
                "requested": roster_count,
                "analyzed": analyzed,
                "failed": failed,
                "completed": True,
                "roster_cap": max(0, int(cap)),
                "overflow": len(overflow),
                "candidate_source_run_id": daily_frame["run_id"],
            },
            coverage={"kind": market_motion.COVERAGE_COMPLETE},
        )
        market_motion.validate_frame(frame)
        if dry_run:
            logger.info(
                "Dry run: computed %s points for %s analyzed stocks; no frame written",
                len(points),
                analyzed,
            )
            return _result(
                "skipped",
                "dry_run",
                session_date=session_date,
                roster=roster_count,
                analyzed=analyzed,
                started=started,
            )

        market_motion.write_frame(frame, frames_root)
        return _result(
            "written",
            "frame_written",
            run_id=frame["run_id"],
            session_date=session_date,
            roster=roster_count,
            analyzed=analyzed,
            started=started,
        )
    except Exception as exc:
        logger.exception("Intraday re-score failed")
        return _result("failed", str(exc), started=started)


def format_result(result: dict[str, Any]) -> str:
    """Return the scheduler's stable final output line."""
    return "MARKET_MOTION_RESULT " + json.dumps(result, sort_keys=True, separators=(",", ":"))
