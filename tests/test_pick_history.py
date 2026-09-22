import json
import math
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.screening.pick_history import (
    DEFAULT_LEDGER_ROOT,
    LIST_NAMES,
    RUN_KIND_DAILY_FULL,
    SCHEMA_VERSION,
    SCORING_VERSION,
    build_snapshot,
    compute_history,
    load_snapshots,
    record_scan,
    session_date_et,
    snapshot_path,
    validate_snapshot,
    write_snapshot,
)


SCOPE = {"total_universe": 3770, "analyzed": 1973, "completed": True}


def _row(ticker, score=100.0, **extra):
    return {"ticker": ticker, "score": score, "composite_score": score, **extra}


def _snapshot(day, shortlist, top20=None, generated_at=None):
    return build_snapshot(
        session_date=day,
        generated_at=generated_at or f"{day}T17:00:00Z",
        provenance="live",
        scope=SCOPE,
        shortlist=shortlist,
        top20=shortlist if top20 is None else top20,
    )


def test_public_constants_and_default_root_are_stable():
    assert SCHEMA_VERSION == 1
    assert SCORING_VERSION == "v1"
    assert RUN_KIND_DAILY_FULL == "daily_full"
    assert LIST_NAMES == ("shortlist", "top20")
    assert DEFAULT_LEDGER_ROOT == Path(__file__).resolve().parents[1] / "data" / "pick_history"


def test_session_date_et_handles_utc_boundary_and_naive_as_utc():
    assert session_date_et(datetime(2026, 9, 19, 2, 30, tzinfo=timezone.utc)) == "2026-09-18"
    assert session_date_et(datetime(2026, 9, 19, 2, 30)) == "2026-09-18"
    assert session_date_et(datetime(2026, 9, 19, 5, 0, tzinfo=timezone.utc)) == "2026-09-19"


def test_build_snapshot_has_exact_shape_normalises_and_drops_blank_tickers():
    snapshot = build_snapshot(
        session_date="2026-09-18",
        generated_at="2026-09-18T13:00:00-04:00",
        provenance="backfill",
        scope=SCOPE,
        shortlist=[_row(" lila ", 90, passed_filters=True), _row(" ")],
        top20=[{"ticker": "ltc", "score": 80, "combined_score": 110}],
        source={"source_commit": "abc"},
    )

    assert list(snapshot) == [
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
    ]
    assert snapshot["generated_at"] == "2026-09-18T17:00:00Z"
    assert snapshot["lists"]["shortlist"] == [
        {
            "ticker": "LILA",
            "rank": 1,
            "score": 90,
            "composite_score": 90,
            "passed_filters": True,
        }
    ]
    assert snapshot["lists"]["top20"] == [
        {"ticker": "LTC", "rank": 1, "score": 80, "combined_score": 110}
    ]


def test_friday_to_monday_is_a_two_session_streak_without_coverage_gap():
    snapshots = [
        _snapshot("2026-09-18", [_row("LILA")]),
        _snapshot("2026-09-21", [_row("LILA")]),
    ]

    history = compute_history(snapshots)

    assert history["tickers"]["LILA"]["current_streak"] == 2
    assert history["tickers"]["LILA"]["longest_streak"] == 2
    assert history["coverage_gaps"] == []


def test_zero_candidate_session_breaks_streaks_and_sets_result():
    first = _snapshot("2026-09-18", [_row("LILA")])
    empty = _snapshot("2026-09-21", [], top20=[])

    history = compute_history([first, empty])

    assert empty["result"] == "no_candidates"
    assert history["denominator"] == 2
    assert history["tickers"]["LILA"]["current_streak"] == 0
    assert history["tickers"]["LILA"]["longest_streak"] == 1
    assert history["tickers"]["LILA"]["is_active_today"] is False


def test_none_list_is_excluded_but_empty_list_is_an_observation():
    present = _snapshot("2026-09-14", [_row("LILA")])
    not_produced = _snapshot("2026-09-15", None, top20=[_row("LTC")])
    empty = _snapshot("2026-09-16", [], top20=[_row("LTC")])

    history = compute_history([present, not_produced, empty])

    assert history["sessions_available"] == 2
    assert history["sessions"] == ["2026-09-14", "2026-09-16"]
    assert history["denominator"] == 2
    assert history["tickers"]["LILA"]["current_streak"] == 0


def test_missing_weekday_reports_gap_without_breaking_streak():
    snapshots = [
        _snapshot("2026-09-17", [_row("LILA")]),
        _snapshot("2026-09-21", [_row("LILA")]),
    ]

    history = compute_history(snapshots)

    assert history["coverage_gaps"] == [
        {"after": "2026-09-17", "before": "2026-09-21", "missing_weekdays": 1}
    ]
    assert history["tickers"]["LILA"]["current_streak"] == 2


def test_same_date_rewrite_replaces_and_identical_rewrite_is_byte_stable(tmp_path):
    first = _snapshot("2026-09-18", [_row("LILA", 100)])
    path = write_snapshot(first, root=tmp_path)
    original_bytes = path.read_bytes()
    write_snapshot(first, root=tmp_path)
    assert path.read_bytes() == original_bytes

    replacement = _snapshot("2026-09-18", [_row("LTC", 120)])
    write_snapshot(replacement, root=tmp_path)

    assert len(list(path.parent.glob("*.json"))) == 1
    assert json.loads(path.read_text())["lists"]["shortlist"][0]["ticker"] == "LTC"


def test_validation_failure_preserves_file_and_leaves_no_temp(tmp_path):
    valid = _snapshot("2026-09-18", [_row("LILA")])
    path = write_snapshot(valid, root=tmp_path)
    original_bytes = path.read_bytes()
    invalid = deepcopy(valid)
    invalid["lists"]["shortlist"][0]["rank"] = 2

    with pytest.raises(ValueError, match="consecutive"):
        write_snapshot(invalid, root=tmp_path)

    assert path.read_bytes() == original_bytes
    assert list(path.parent.glob("*.tmp")) == []


def test_window_larger_than_available_uses_actual_denominator():
    history = compute_history(
        [_snapshot("2026-09-17", [_row("LILA")]), _snapshot("2026-09-18", [])],
        window=20,
    )
    assert history["sessions_available"] == 2
    assert history["denominator"] == 2
    assert history["window_requested"] == 20


def test_small_window_uses_window_counts_and_full_ledger_streak_stats():
    snapshots = [
        _snapshot("2026-09-14", [_row("LILA", 10)]),
        _snapshot("2026-09-15", [_row("LILA", 20)]),
        _snapshot("2026-09-16", []),
        _snapshot("2026-09-17", [_row("LILA", 30)]),
        _snapshot("2026-09-18", [_row("LILA", 40)]),
    ]

    stats = compute_history(snapshots, window=2)["tickers"]["LILA"]

    assert stats["appearances"] == 2
    assert stats["denominator"] == 2
    assert stats["total_appearances"] == 4
    assert stats["first_seen"] == "2026-09-14"
    assert stats["current_streak"] == 2
    assert stats["longest_streak"] == 2
    assert stats["average_score"] == 35.0


def test_load_skips_corrupt_invalid_and_filename_mismatch_with_warnings(tmp_path):
    valid = _snapshot("2026-09-18", [_row("LILA")])
    valid_path = write_snapshot(valid, root=tmp_path)
    directory = valid_path.parent
    (directory / "2026-09-15.json").write_text("{broken", encoding="utf-8")
    invalid = deepcopy(valid)
    invalid["schema_version"] = 99
    (directory / "2026-09-16.json").write_text(json.dumps(invalid), encoding="utf-8")
    mismatch = deepcopy(valid)
    mismatch["session_date"] = "2026-09-17"
    (directory / "2026-09-19.json").write_text(json.dumps(mismatch), encoding="utf-8")

    snapshots, warnings = load_snapshots(root=tmp_path)

    assert [item["session_date"] for item in snapshots] == ["2026-09-18"]
    assert len(warnings) == 3
    assert "2026-09-15.json" in warnings[0]
    assert "2026-09-16.json" in warnings[1]
    assert "2026-09-19.json" in warnings[2]


def test_load_missing_directory_returns_empty_shape(tmp_path):
    assert load_snapshots(root=tmp_path) == ([], [])


def test_duplicate_ticker_and_nonconsecutive_rank_are_rejected():
    # build_snapshot de-duplicates raw scanner input (see the next test), so a
    # duplicate can only reach the validator through a hand-built snapshot.
    duplicate = _snapshot("2026-09-18", [_row("LILA"), _row("LTC")])
    duplicate["lists"]["shortlist"][1]["ticker"] = "LILA"
    with pytest.raises(ValueError, match="duplicate ticker"):
        validate_snapshot(duplicate)

    ranks = _snapshot("2026-09-18", [_row("LILA"), _row("LTC")])
    ranks["lists"]["shortlist"][1]["rank"] = 3
    with pytest.raises(ValueError, match="consecutive"):
        validate_snapshot(ranks)


def test_validation_rejects_both_lists_none_and_nonfinite_direct_score():
    neither = _snapshot("2026-09-18", None, top20=None)
    with pytest.raises(ValueError, match="at least one"):
        validate_snapshot(neither)

    nonfinite = _snapshot("2026-09-18", [_row("LILA")])
    nonfinite["lists"]["shortlist"][0]["score"] = math.inf
    with pytest.raises(ValueError, match="non-finite"):
        validate_snapshot(nonfinite)


def test_nan_from_raw_row_is_sanitised_and_json_is_strict(tmp_path):
    snapshot = _snapshot("2026-09-18", [_row("LILA", math.nan)])
    path = write_snapshot(snapshot, root=tmp_path)
    text = path.read_text(encoding="utf-8")
    parsed = json.loads(
        text,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )

    assert "NaN" not in text
    assert parsed["lists"]["shortlist"][0]["score"] is None
    assert parsed["lists"]["shortlist"][0]["composite_score"] is None


def test_score_delta_is_none_across_scoring_versions():
    first = _snapshot("2026-09-17", [_row("LILA", 100)])
    second = _snapshot("2026-09-18", [_row("LILA", 110)])
    second["scoring_version"] = "v2"

    stats = compute_history([first, second])["tickers"]["LILA"]

    assert stats["latest_score"] == 110.0
    assert stats["score_delta"] is None


def test_rank_and_score_math_uses_composite_then_falls_back_to_score():
    first = _snapshot("2026-09-16", [_row("AAA", 10), _row("LILA", 100)])
    second = _snapshot("2026-09-17", [_row("LILA", 110)])
    third = _snapshot("2026-09-18", [_row("AAA", 20), _row("LILA", 120)])
    second["lists"]["shortlist"][0]["composite_score"] = None

    stats = compute_history([first, second, third])["tickers"]["LILA"]

    assert stats["best_rank"] == 1
    assert stats["average_rank"] == 1.6667
    assert stats["average_score"] == 110.0
    assert stats["score_delta"] == 10.0
    assert stats["history"] == [
        {"date": "2026-09-16", "rank": 2, "score": 100.0},
        {"date": "2026-09-17", "rank": 1, "score": 110.0},
        {"date": "2026-09-18", "rank": 2, "score": 120.0},
    ]


def test_top20_uses_combined_score_then_falls_back_to_score():
    snapshots = [
        _snapshot(
            "2026-09-17",
            [],
            top20=[{"ticker": "LILA", "score": 80, "combined_score": 105}],
        ),
        _snapshot(
            "2026-09-18",
            [],
            top20=[{"ticker": "LILA", "score": 90, "combined_score": None}],
        ),
    ]

    stats = compute_history(snapshots, list_name="top20")["tickers"]["LILA"]

    assert stats["average_score"] == 97.5
    assert stats["latest_score"] == 90.0
    assert stats["score_delta"] == -15.0


def test_realistic_sep_14_to_18_fixture():
    days = ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]
    snapshots = []
    for index, day in enumerate(days):
        rows = [_row("LILA", 130 - index)]
        if index >= 2:
            rows.append(_row("LTC", 120 + index))
        snapshots.append(_snapshot(day, rows))

    history = compute_history(snapshots)

    assert history["tickers"]["LILA"]["appearances"] == 5
    assert history["tickers"]["LILA"]["denominator"] == 5
    assert history["tickers"]["LILA"]["current_streak"] == 5
    assert history["tickers"]["LTC"]["appearances"] == 3
    assert history["tickers"]["LTC"]["current_streak"] == 3


def test_output_is_json_serialisable_deterministic_and_preserves_warning_order():
    snapshots = [_snapshot("2026-09-18", [_row(" lila ", 99.123456)])]
    warnings = ["first", "second"]

    first = compute_history(snapshots, warnings=warnings)
    second = compute_history(deepcopy(snapshots), warnings=warnings)

    assert first == second
    assert first["warnings"] == warnings
    assert first["tickers"]["LILA"]["latest_score"] == 99.1235
    json.dumps(first, allow_nan=False)


def test_empty_input_window_floor_unknown_list_and_paths(tmp_path):
    empty = compute_history([], window=0)
    assert empty["window_requested"] == 1
    assert empty["sessions_available"] == 0
    assert empty["denominator"] == 0
    assert empty["latest_session_date"] is None
    assert empty["tickers"] == {}
    assert snapshot_path("2026-09-18", root=tmp_path) == (
        tmp_path / "snapshots" / "daily_full" / "2026-09-18.json"
    )
    with pytest.raises(ValueError, match="unknown list_name"):
        compute_history([], list_name="unknown")


def test_record_scan_derives_et_date_and_writes_snapshot(tmp_path):
    path = record_scan(
        shortlist=[_row("lila")],
        top20=[],
        scope=SCOPE,
        generated_at="2026-09-19T02:30:00Z",
        source={"git_sha": "abc"},
        root=tmp_path,
    )

    assert path.name == "2026-09-18.json"
    stored = json.loads(path.read_text())
    assert stored["session_date"] == "2026-09-18"
    assert stored["lists"]["shortlist"][0]["ticker"] == "LILA"


def test_build_snapshot_deduplicates_upstream_duplicates_keeping_the_best_rank():
    snapshot = _snapshot("2026-09-18", [_row("LILA", 110), _row("LTC", 105), _row("lila", 90), _row("NVDA", 80)])
    rows = snapshot["lists"]["shortlist"]
    assert [r["ticker"] for r in rows] == ["LILA", "LTC", "NVDA"]
    assert [r["rank"] for r in rows] == [1, 2, 3], "ranks stay consecutive after a duplicate is dropped"
    assert rows[0]["score"] == 110, "the first (best-ranked) occurrence wins"
    validate_snapshot(snapshot)


def test_record_scan_never_replaces_a_good_same_day_session_with_a_no_candidates_run(tmp_path):
    good = record_scan(
        shortlist=[_row("LILA"), _row("LTC")], top20=[_row("LILA")], scope=SCOPE,
        generated_at="2026-09-18T17:07:46Z", root=tmp_path,
    )
    before = good.read_bytes()

    with pytest.raises(ValueError, match="refusing to replace"):
        record_scan(shortlist=[], top20=[], scope=SCOPE, generated_at="2026-09-18T20:00:00Z", root=tmp_path)
    assert good.read_bytes() == before, "the good session is untouched"
    assert [p.name for p in good.parent.iterdir()] == ["2026-09-18.json"], "and no temp file is left behind"

    record_scan(
        shortlist=[_row("ZZZ")], top20=[_row("ZZZ")], scope=SCOPE,
        generated_at="2026-09-18T20:00:00Z", root=tmp_path,
    )
    assert json.loads(good.read_text())["lists"]["shortlist"][0]["ticker"] == "ZZZ", (
        "a later run that finds candidates still replaces it (latest good writer wins)"
    )

    record_scan(
        shortlist=[], top20=[], scope=SCOPE, generated_at="2026-09-18T21:00:00Z",
        root=tmp_path, allow_downgrade=True,
    )
    assert json.loads(good.read_text())["result"] == "no_candidates", "an explicit override is honoured"


def test_a_no_candidates_run_on_a_fresh_day_or_after_another_no_candidates_is_recorded(tmp_path):
    first = record_scan(shortlist=[], top20=[], scope=SCOPE, generated_at="2026-09-21T17:00:00Z", root=tmp_path)
    assert json.loads(first.read_text())["result"] == "no_candidates"
    again = record_scan(shortlist=[], top20=[], scope=SCOPE, generated_at="2026-09-21T19:00:00Z", root=tmp_path)
    assert again == first, "an honest zero-candidate day is a real observation and must be recordable"
