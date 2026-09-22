#!/usr/bin/env python3
"""One-time, deterministic backfill of market-motion frames from git history.

Reuses the five accepted full-universe sessions of the pick-history backfill
(2026-09-14 .. 2026-09-18, all authored by the automated workflow). For each
one the dated human-readable scan report is parsed ONCE and turned into a
`legacy_report` frame.

Honesty rules:
  * A report details only the top 50 buy signals out of hundreds, so every
    backfilled frame is marked coverage.kind = "top50_only". Tickers outside
    those 50 are UNKNOWN for that session (never "dropped"), and nothing is
    invented for them.
  * Every session is built and validated before any file is written, so a bad
    entry leaves nothing behind. Re-running is byte-identical.

Usage:
    python scripts/backfill_market_motion.py [--root data/market_motion] [--dry-run] [--force]
"""
import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import backfill_pick_history as pick_backfill  # noqa: E402
from src.screening import market_motion  # noqa: E402

BackfillError = pick_backfill.BackfillError
ACCEPTED_SESSIONS = pick_backfill.ACCEPTED_SESSIONS
find_git = pick_backfill.find_git
make_git_runner = pick_backfill.make_git_runner
MAX_DETAILED_BUYS = 50


def _parse_report(text):
    """Parse report text with the dashboard's own parser (single source of truth)."""
    import dashboard  # local import: pulls in Flask, only needed for the one-time backfill

    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    try:
        return dashboard.parse_scan_file(temp)
    finally:
        temp.unlink(missing_ok=True)


def collect_frame(entry, run_git):
    """Build and validate one legacy frame from git. Raises BackfillError on any doubt."""
    label = entry["session_date"]
    sha = entry["commit"]

    author = run_git("show", "-s", "--format=%an", sha).strip()
    if author != pick_backfill.BOT_AUTHOR:
        raise BackfillError(f"{label}: commit {sha[:8]} author is {author!r}, not {pick_backfill.BOT_AUTHOR!r}")

    report_text = run_git("show", f"{sha}:{entry['report']}")
    parsed = _parse_report(report_text)
    stats = parsed["stats"]
    universe = stats.get("total_universe")
    if universe is None or universe < pick_backfill.MIN_FULL_UNIVERSE:
        raise BackfillError(f"{label}: report universe {universe!r} is not a full-universe scan")
    generated = parsed.get("generated")
    if not generated:
        raise BackfillError(f"{label}: report has no Generated header")
    generated_at = pick_backfill._parse_ts(generated)
    if pick_backfill.pick_history.session_date_et(generated_at) != label:
        raise BackfillError(f"{label}: report timestamp resolves to ET session "
                            f"{pick_backfill.pick_history.session_date_et(generated_at)}")

    signals = parsed["buy_signals"]
    if not signals:
        raise BackfillError(f"{label}: report contains no detailed buy signals")
    if len(signals) > MAX_DETAILED_BUYS:
        raise BackfillError(f"{label}: {len(signals)} detailed buys exceeds the report cap {MAX_DETAILED_BUYS}")
    for signal in signals:
        if signal.get("max_score") != market_motion.MAX_SCORE:
            raise BackfillError(f"{label}: {signal.get('ticker')} max_score {signal.get('max_score')!r} "
                                f"is not {market_motion.MAX_SCORE}")
    total = stats.get("buy_count")
    if total is None or total < len(signals):
        raise BackfillError(f"{label}: header buy count {total!r} is inconsistent with {len(signals)} detailed buys")

    points = [market_motion.normalize_buy_signal(s, rank=s.get("rank")) for s in signals]
    frame = market_motion.build_frame(
        run_kind=market_motion.RUN_KIND_LEGACY,
        generated_at=generated_at,
        session_date=label,
        points=points,
        scope={"mode": "legacy_report", "requested": universe, "analyzed": stats.get("analyzed"), "completed": True},
        coverage={"kind": market_motion.COVERAGE_TOP50, "qualified_total": total, "located_points": len(points)},
        regime={"should_generate_buys": True, "source_run_id": None},
        provenance="backfill",
        source={"source_commit": sha, "report_path": entry["report"]},
    )
    market_motion.validate_frame(frame)
    if frame["coverage"]["located_points"] != len(frame["points"]):
        raise BackfillError(f"{label}: duplicate tickers in the report's detailed buys")
    return frame


def backfill(root, run_git, dry_run=False, force=False, sessions=ACCEPTED_SESSIONS):
    frames = [collect_frame(entry, run_git) for entry in sessions]

    for frame in frames:
        path = market_motion.frame_path(frame, root=root)
        if path.exists() and not force:
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                existing = {}
            if existing.get("provenance") not in ("backfill", None):
                raise BackfillError(f"{frame['session_date']}: refusing to overwrite a {existing.get('provenance')!r} "
                                    "frame (use --force)")

    written = []
    if not dry_run:
        for frame in frames:
            written.append(market_motion.write_frame(frame, root=root))
    return frames, written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=str(market_motion.DEFAULT_ROOT))
    parser.add_argument("--dry-run", action="store_true", help="validate everything, write nothing")
    parser.add_argument("--force", action="store_true", help="allow overwriting non-backfill frames")
    args = parser.parse_args(argv)

    try:
        frames, _ = backfill(Path(args.root), make_git_runner(find_git()), dry_run=args.dry_run, force=args.force)
    except BackfillError as exc:
        print(f"backfill aborted, nothing written: {exc}", file=sys.stderr)
        return 1

    for frame in frames:
        cov = frame["coverage"]
        print(f"{frame['session_date']}  {frame['run_id']}  located={cov['located_points']:>3} of {cov['qualified_total']:>3} qualified")
    print(f"{'validated' if args.dry_run else 'wrote'} {len(frames)} legacy frames"
          + ("" if args.dry_run else f" under {args.root}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
