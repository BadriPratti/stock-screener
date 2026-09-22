import importlib.util
import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "backfill_pick_history", PROJECT_ROOT / "scripts" / "backfill_pick_history.py"
)
bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bf)

from src.screening import pick_history  # noqa: E402

SHA = "a" * 40


def _shortlist_doc(generated, tickers=("AAA", "BBB", "CCC")):
    return {
        "generated": generated,
        "result": "success",
        "shortlist": [
            {"ticker": t, "score": 95.0 - i, "composite_score": 120.0 - i,
             "combined_score": 120.0 - i, "passed_filters": True}
            for i, t in enumerate(tickers)
        ],
    }


def _top20_doc(generated, tickers=("AAA", "BBB", "CCC", "DDD")):
    return {
        "generated": generated,
        "result": "success",
        "top20": [{"ticker": t, "score": 95.0 - i, "combined_score": 120.0 - i} for i, t in enumerate(tickers)],
    }


def _report(generated="2026-09-14 23:10:20", universe="3,766 stocks", analyzed="1,982 stocks"):
    return (
        "OPTIMIZED FULL MARKET SCAN - ALL US STOCKS\n"
        "Scan Date: 2026-09-14\n"
        f"Generated: {generated}\n"
        f"Total Universe: {universe}\n"
        f"Analyzed: {analyzed}\n"
    )


def _entry(date="2026-09-14", sha=SHA, report="data/daily_scans/optimized_scan_x.txt"):
    return {"session_date": date, "commit": sha, "report": report}


def _fake_git(entries_data):
    """entries_data: {sha: dict(author, shortlist, top20, report_path, report)}."""
    def run_git(*args):
        if args[:3] == ("show", "-s", "--format=%an"):
            return entries_data[args[3]]["author"] + "\n"
        if args[0] == "show" and ":" in args[1]:
            sha, path = args[1].split(":", 1)
            data = entries_data[sha]
            if path == bf.SHORTLIST_PATH:
                return json.dumps(data["shortlist"])
            if path == bf.TOP20_PATH:
                return json.dumps(data["top20"])
            if path == data["report_path"]:
                return data["report"]
        raise bf.BackfillError(f"unexpected git call {args}")
    return run_git


def _good(date="2026-09-14", sha=SHA, generated="2026-09-14T23:10:20.556302"):
    report_path = f"data/daily_scans/optimized_scan_{date.replace('-', '')}.txt"
    return _entry(date, sha, report_path), {
        "author": bf.BOT_AUTHOR,
        "shortlist": _shortlist_doc(generated),
        "top20": _top20_doc(generated.replace(":20.5", ":19.3")),
        "report_path": report_path,
        "report": _report(generated=generated[:19].replace("T", " ")),
    }


def test_manifest_shape_is_explicit_and_sane():
    dates = [e["session_date"] for e in bf.ACCEPTED_SESSIONS]
    assert dates == sorted(set(dates)) and len(dates) == 5
    for entry in bf.ACCEPTED_SESSIONS:
        assert re.fullmatch(r"[0-9a-f]{40}", entry["commit"])
        assert entry["report"].startswith("data/daily_scans/optimized_scan_")


def test_collect_session_builds_backfill_snapshot():
    entry, data = _good()
    snapshot = bf.collect_session(entry, _fake_git({SHA: data}))

    assert snapshot["provenance"] == "backfill"
    assert snapshot["session_date"] == "2026-09-14"
    assert snapshot["source"] == {"source_commit": SHA, "report_path": entry["report"]}
    assert snapshot["scope"] == {"total_universe": 3766, "analyzed": 1982, "completed": True}
    assert [r["ticker"] for r in snapshot["lists"]["shortlist"]] == ["AAA", "BBB", "CCC"]
    assert [r["rank"] for r in snapshot["lists"]["top20"]] == [1, 2, 3, 4]
    assert snapshot["result"] == "success"


def test_manual_commit_author_is_rejected():
    entry, data = _good()
    data["author"] = "Badri Prati"
    with pytest.raises(bf.BackfillError, match="not the automated"):
        bf.collect_session(entry, _fake_git({SHA: data}))


def test_sample_universe_report_is_rejected():
    entry, data = _good()
    data["report"] = _report(universe="100 stocks", analyzed="55 stocks")
    with pytest.raises(bf.BackfillError, match="not a full-universe scan"):
        bf.collect_session(entry, _fake_git({SHA: data}))


def test_report_timestamp_skew_is_rejected():
    entry, data = _good()
    data["report"] = _report(generated="2026-09-14 20:47:07")
    with pytest.raises(bf.BackfillError, match="from report"):
        bf.collect_session(entry, _fake_git({SHA: data}))


def test_manifest_date_that_disagrees_with_timestamps_is_rejected():
    entry, data = _good()
    entry["session_date"] = "2026-09-15"
    with pytest.raises(bf.BackfillError, match="resolve to ET session 2026-09-14"):
        bf.collect_session(entry, _fake_git({SHA: data}))


def test_non_success_result_is_rejected():
    entry, data = _good()
    data["top20"]["result"] = "no_candidates"
    with pytest.raises(bf.BackfillError, match="expected 'success'"):
        bf.collect_session(entry, _fake_git({SHA: data}))


def _three_sessions():
    entries, data = [], {}
    for i, day in enumerate(("2026-09-14", "2026-09-15", "2026-09-16")):
        sha = f"{i}" * 40
        entry, blob = _good(date=day, sha=sha, generated=f"{day}T17:31:20.556302")
        entries.append(entry)
        data[sha] = blob
    return entries, data


def test_bad_entry_means_nothing_is_written(tmp_path):
    entries, data = _three_sessions()
    data["1" * 40]["author"] = "someone else"
    with pytest.raises(bf.BackfillError):
        bf.backfill(tmp_path, _fake_git(data), sessions=entries)
    assert not list(tmp_path.rglob("*.json"))


def test_dry_run_writes_nothing(tmp_path):
    entries, data = _three_sessions()
    snapshots, written = bf.backfill(tmp_path, _fake_git(data), dry_run=True, sessions=entries)
    assert len(snapshots) == 3 and written == []
    assert not list(tmp_path.rglob("*.json"))


def test_rerun_is_byte_identical(tmp_path):
    entries, data = _three_sessions()
    bf.backfill(tmp_path, _fake_git(data), sessions=entries)
    first = {p.name: p.read_bytes() for p in tmp_path.rglob("*.json")}
    bf.backfill(tmp_path, _fake_git(data), sessions=entries)
    second = {p.name: p.read_bytes() for p in tmp_path.rglob("*.json")}
    assert len(first) == 3 and first == second


def test_live_session_is_never_overwritten_without_force(tmp_path):
    entries, data = _three_sessions()
    live = pick_history.build_snapshot(
        session_date="2026-09-15", generated_at="2026-09-15T17:00:00Z", provenance="live",
        scope={"total_universe": 3770, "analyzed": 1973, "completed": True},
        shortlist=[{"ticker": "ZZZ", "score": 1.0}], top20=[{"ticker": "ZZZ", "score": 1.0}],
    )
    live_path = pick_history.write_snapshot(live, root=tmp_path)
    before = live_path.read_bytes()

    with pytest.raises(bf.BackfillError, match="live session"):
        bf.backfill(tmp_path, _fake_git(data), sessions=entries)
    assert live_path.read_bytes() == before

    bf.backfill(tmp_path, _fake_git(data), force=True, sessions=entries)
    assert json.loads(live_path.read_text())["provenance"] == "backfill"


def _real_history_available():
    try:
        run_git = bf.make_git_runner(bf.find_git())
        for entry in bf.ACCEPTED_SESSIONS:
            run_git("cat-file", "-e", entry["commit"])
        return run_git
    except bf.BackfillError:
        return None


def test_real_history_backfill_matches_the_sprint_findings(tmp_path):
    run_git = _real_history_available()
    if run_git is None:
        pytest.skip("accepted commits are not reachable in this checkout (shallow clone or no git)")

    bf.backfill(tmp_path, run_git)
    snapshots, warnings = pick_history.load_snapshots(tmp_path)
    assert warnings == [] and len(snapshots) == 5
    assert all(s["provenance"] == "backfill" for s in snapshots)
    assert all(len(s["lists"]["top20"]) == 20 and len(s["lists"]["shortlist"]) == 5 for s in snapshots)

    history = pick_history.compute_history(snapshots, "shortlist", window=5)
    lila, lilak, ltc = (history["tickers"][t] for t in ("LILA", "LILAK", "LTC"))
    assert (lila["appearances"], lila["denominator"], lila["current_streak"]) == (5, 5, 5)
    assert (lilak["appearances"], lilak["current_streak"]) == (4, 2)
    assert (ltc["appearances"], ltc["current_streak"]) == (3, 3)
    assert history["coverage_gaps"] == []
