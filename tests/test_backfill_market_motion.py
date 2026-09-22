"""Tests for scripts/backfill_market_motion.py."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import backfill_market_motion as bf  # noqa: E402
from src.screening import market_motion as mm  # noqa: E402

REPORT_TMPL = """================================================================================
OPTIMIZED FULL MARKET SCAN - ALL US STOCKS
Scan Date: {date}
Generated: {date} 17:07:46
================================================================================

SCANNING STATISTICS
--------------------------------------------------------------------------------
Total Universe: {universe} stocks
Analyzed: 1,973 stocks
Processing Time: 62.8 minutes
Buy Signals: {total}
Sell Signals: 10

################################################################################
BUY #1: AAA | Score: 107.8/125
################################################################################
Phase: 2
Entry Quality: Good
Stop Loss: $42.73
Risk/Reward: 2.5:1 (Risk $1.00, Reward $2.50)
RS: 0.355
  • Strong relative strength

################################################################################
BUY #2: BBB | Score: {score2}/125
################################################################################
Phase: 2
Entry Quality: Extended
Stop Loss: $10.00
RS: -0.05
"""


def make_runner(author="github-actions[bot]", universe="3,770", total=364, score2="90.0", date="2026-09-18"):
    text = REPORT_TMPL.format(date=date, universe=universe, total=total, score2=score2)

    def run_git(*args):
        if args[:3] == ("show", "-s", "--format=%an"):
            return author + "\n"
        if args[0] == "show":
            return text
        raise AssertionError(args)
    return run_git


ENTRY = {"session_date": "2026-09-18", "commit": "a" * 40, "report": "data/daily_scans/optimized_scan_x.txt"}


def test_collect_frame_marks_top50_only_and_never_invents_points():
    frame = bf.collect_frame(ENTRY, make_runner())
    assert frame["run_kind"] == "legacy_report" and frame["provenance"] == "backfill"
    assert frame["coverage"] == {"kind": "top50_only", "qualified_total": 364, "located_points": 2}
    assert [p["ticker"] for p in frame["points"]] == ["AAA", "BBB"]
    aaa = frame["points"][0]
    assert (aaa["score"], aaa["rs"], aaa["phase"], aaa["entry_quality"]) == (107.8, 0.355, 2, "Good")
    assert frame["points"][1]["rs"] == -0.05
    assert frame["source"]["source_commit"] == "a" * 40
    assert frame["session_date"] == "2026-09-18" and frame["run_id"].endswith("-legacy_report")
    mm.validate_frame(frame)


@pytest.mark.parametrize("kwargs,msg", [
    ({"author": "Somebody"}, "author"),
    ({"universe": "100"}, "full-universe"),
    ({"total": 1}, "inconsistent"),
    ({"date": "2026-09-19"}, "ET session"),
])
def test_collect_frame_refuses_anything_doubtful(kwargs, msg):
    with pytest.raises(bf.BackfillError, match=msg):
        bf.collect_frame(ENTRY, make_runner(**kwargs))


def test_backfill_is_two_phase_idempotent_and_dry_run_writes_nothing(tmp_path):
    bad = dict(ENTRY, session_date="2026-09-17")
    with pytest.raises(bf.BackfillError):
        bf.backfill(tmp_path, make_runner(), sessions=(ENTRY, bad))          # second entry fails validation
    assert not list(tmp_path.rglob("*.json"))                                 # nothing partial written

    frames, written = bf.backfill(tmp_path, make_runner(), dry_run=True, sessions=(ENTRY,))
    assert len(frames) == 1 and written == [] and not list(tmp_path.rglob("*.json"))

    _, written = bf.backfill(tmp_path, make_runner(), sessions=(ENTRY,))
    first = written[0].read_bytes()
    _, written = bf.backfill(tmp_path, make_runner(), sessions=(ENTRY,))
    assert written[0].read_bytes() == first                                   # byte-identical rerun


def test_backfill_refuses_to_overwrite_a_live_frame(tmp_path):
    frame = bf.collect_frame(ENTRY, make_runner())
    live = dict(frame, provenance="live")
    path = mm.frame_path(live, root=tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(live))
    with pytest.raises(bf.BackfillError, match="refusing"):
        bf.backfill(tmp_path, make_runner(), sessions=(ENTRY,))
    bf.backfill(tmp_path, make_runner(), sessions=(ENTRY,), force=True)


def _working_git():
    for candidate in (shutil.which("git"), "/Library/Developer/CommandLineTools/usr/bin/git"):
        if candidate and subprocess.run([candidate, "--version"], capture_output=True).returncode == 0:
            return candidate
    return None


def test_real_git_history_backfills_five_sessions_with_expected_tracker(tmp_path):
    git = _working_git()
    if git is None:
        pytest.skip("no usable git binary")
    if subprocess.run([git, "cat-file", "-e", bf.ACCEPTED_SESSIONS[0]["commit"]], cwd=ROOT).returncode != 0:
        pytest.skip("accepted commits are not present in this clone")
    frames, written = bf.backfill(tmp_path, bf.make_git_runner(git))
    assert len(written) == 5
    assert [f["session_date"] for f in frames] == ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]
    assert all(f["coverage"]["kind"] == "top50_only" and f["coverage"]["located_points"] == 50 for f in frames)
    assert [f["coverage"]["qualified_total"] for f in frames] == [479, 436, 461, 429, 364]

    loaded, warnings = mm.load_frames(tmp_path)
    assert warnings == [] and len(loaded) == 5
    tracker = mm.compute_tracker(loaded)
    assert tracker["sessions_available"] == 5
    assert len(tracker["tickers"]) == 84                                     # distinct tickers in the five top-50 lists
    in_all_five = [t for t, r in tracker["tickers"].items() if r["current_streak_days"] == 5]
    assert len(in_all_five) == 25
    assert tracker["top50_only_sessions"] == tracker["sessions"]
    # a ticker seen once is 1 of 5 observed only if located; the other sessions are UNKNOWN, not misses
    once = next(r for r in tracker["tickers"].values() if r["sessions_qualified"] == 1)
    assert once["sessions_observed"] == 1 and once["unknown_sessions"] == 4
