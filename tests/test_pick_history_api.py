import json

import pytest

import dashboard
from src.screening import pick_history


SCOPE = {"total_universe": 3770, "analyzed": 1973, "completed": True}


def _row(ticker, score=100.0):
    return {"ticker": ticker, "score": score, "composite_score": score}


def _top20_row(ticker, score=100.0):
    return {"ticker": ticker, "score": score, "combined_score": score}


def _write_session(root, day, shortlist, top20=None):
    snapshot = pick_history.build_snapshot(
        session_date=day,
        generated_at=f"{day}T17:00:00Z",
        provenance="live",
        scope=SCOPE,
        shortlist=shortlist,
        top20=shortlist if top20 is None else top20,
    )
    return pick_history.write_snapshot(snapshot, root=root)


@pytest.fixture
def history_client(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "PICK_HISTORY_ROOT", tmp_path)
    return dashboard.app.test_client()


def test_pick_history_empty_ledger_returns_empty_shape(history_client):
    response = history_client.get("/api/pick-history")

    assert response.status_code == 200
    body = response.get_json()
    assert body["sessions_available"] == 0
    assert body["tickers"] == {}
    assert body["warnings"] == []
    assert body["list"] == "shortlist"
    assert body["window_requested"] == 5


def test_pick_history_populated_ledger_and_top20(history_client, tmp_path):
    _write_session(
        tmp_path,
        "2026-09-16",
        [_row("LILA", 101)],
        [_top20_row("TOP", 91)],
    )
    _write_session(
        tmp_path,
        "2026-09-17",
        [_row("LILA", 102), _row("OTHER", 80)],
        [_top20_row("TOP", 92)],
    )
    _write_session(
        tmp_path,
        "2026-09-18",
        [_row("LILA", 103)],
        [_top20_row("TOP", 93)],
    )

    shortlist = history_client.get("/api/pick-history").get_json()
    assert shortlist["sessions_available"] == 3
    assert shortlist["tickers"]["LILA"]["appearances"] == 3
    assert shortlist["tickers"]["LILA"]["current_streak"] == 3
    assert shortlist["tickers"]["LILA"]["first_seen"] == "2026-09-16"

    top20 = history_client.get("/api/pick-history?list=top20").get_json()
    assert top20["list"] == "top20"
    assert top20["tickers"]["TOP"]["appearances"] == 3


def test_unknown_list_falls_back_with_warning(history_client):
    body = history_client.get("/api/pick-history?list=watchlist").get_json()

    assert body["list"] == "shortlist"
    assert body["warnings"] == ["Unknown list 'watchlist'; using 'shortlist'."]


@pytest.mark.parametrize(
    ("raw_window", "expected", "warning"),
    [
        ("0", 1, "Window 0 was clamped to 1."),
        ("999", 60, "Window 999 was clamped to 60."),
        ("abc", 5, "Invalid window 'abc'; using default 5."),
    ],
)
def test_window_fallbacks_are_safe(history_client, raw_window, expected, warning):
    response = history_client.get(f"/api/pick-history?window={raw_window}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["window_requested"] == expected
    assert body["warnings"] == [warning]


def test_corrupt_snapshot_warns_and_keeps_valid_sessions(history_client, tmp_path):
    valid_path = _write_session(tmp_path, "2026-09-18", [_row("LILA")])
    corrupt_name = "2026-09-17.json"
    (valid_path.parent / corrupt_name).write_text("{broken", encoding="utf-8")

    response = history_client.get("/api/pick-history")

    assert response.status_code == 200
    body = response.get_json()
    assert body["sessions_available"] == 1
    assert body["tickers"]["LILA"]["appearances"] == 1
    assert any(corrupt_name in warning for warning in body["warnings"])


def test_friday_to_monday_streak_continues_through_api(history_client, tmp_path):
    _write_session(tmp_path, "2026-09-18", [_row("LILA")])
    _write_session(tmp_path, "2026-09-21", [_row("LILA")])

    body = history_client.get("/api/pick-history").get_json()

    assert body["sessions"] == ["2026-09-18", "2026-09-21"]
    assert body["tickers"]["LILA"]["current_streak"] == 2
    assert body["coverage_gaps"] == []


def test_pick_history_response_is_strict_json(history_client, tmp_path):
    _write_session(tmp_path, "2026-09-18", [_row("LILA", float("nan"))])

    response = history_client.get("/api/pick-history")
    parsed = json.loads(
        response.get_data(as_text=True),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )

    assert parsed["tickers"]["LILA"]["latest_score"] is None
    assert "NaN" not in response.get_data(as_text=True)


def test_unexpected_compute_failure_degrades_to_empty_shape(
    history_client, monkeypatch
):
    def fail(*args, **kwargs):
        raise RuntimeError("synthetic failure")

    monkeypatch.setattr(dashboard.pick_history, "compute_history", fail)
    response = history_client.get("/api/pick-history")

    assert response.status_code == 200
    body = response.get_json()
    assert body["sessions_available"] == 0
    assert body["tickers"] == {}
    assert any("synthetic failure" in warning for warning in body["warnings"])


def test_scans_include_metadata_without_changing_identity_or_order(tmp_path, monkeypatch):
    reports = {
        "optimized_scan_2026-09-20_1600.txt": (
            "Total Universe: 3,770 stocks\nRun Kind: daily-full\n",
            3770,
            "daily-full",
            False,
        ),
        "optimized_scan_2026-09-20_1200.txt": (
            "Total Universe: 100 stocks\nRun Kind: midday-sample\n",
            100,
            "midday-sample",
            True,
        ),
        "optimized_scan_2026-09-19.txt": (
            "Total Universe: 100 stocks\n",
            100,
            None,
            True,
        ),
        "optimized_scan_2026-09-18.txt": (
            "Generated: 2026-09-18\nRun Kind: daily-full\n",
            None,
            None,
            False,
        ),
    }
    for filename, (contents, _, _, _) in reports.items():
        (tmp_path / filename).write_text(contents, encoding="utf-8")
    unreadable_name = "optimized_scan_2026-09-17.txt"
    (tmp_path / unreadable_name).mkdir()
    monkeypatch.setattr(dashboard, "SCAN_DIR", tmp_path)

    response = dashboard.app.test_client().get("/api/scans")

    assert response.status_code == 200
    scans = response.get_json()
    expected_names = sorted([*reports, unreadable_name], reverse=True)
    assert [scan["name"] + ".txt" for scan in scans] == expected_names
    assert [scan["date"] for scan in scans] == [
        name.removeprefix("optimized_scan_").removesuffix(".txt")
        for name in expected_names
    ]
    assert [scan["path"] for scan in scans] == [
        str(tmp_path / name) for name in expected_names
    ]

    by_name = {scan["name"] + ".txt": scan for scan in scans}
    for filename, (_, universe, run_kind, is_sample) in reports.items():
        assert by_name[filename]["total_universe"] == universe
        assert by_name[filename]["run_kind"] == run_kind
        assert by_name[filename]["is_sample"] is is_sample
    assert by_name[unreadable_name]["total_universe"] is None
    assert by_name[unreadable_name]["run_kind"] is None
    assert by_name[unreadable_name]["is_sample"] is False
    assert all({"name", "path", "date"} <= scan.keys() for scan in scans)
