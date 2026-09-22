"""Tests for the /api/market-motion endpoints and the /api/scan path containment."""

from datetime import datetime, timezone

import pytest

import dashboard
from src.screening import market_motion as mm


def q(t, score=100.0, rs=0.3):
    return mm.make_point(t, mm.EVAL_QUALIFIED, score=score, rs=rs, phase=2, entry_quality="Good")


def write(root, day, points, kind=mm.RUN_KIND_DAILY_FULL, hour=17, coverage=None):
    gen = datetime.fromisoformat(day).replace(hour=hour, tzinfo=timezone.utc)
    frame = mm.build_frame(run_kind=kind, generated_at=gen, session_date=day, points=points,
                           scope={"mode": "full_universe", "completed": True}, coverage=coverage)
    mm.write_frame(frame, root)
    return frame


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "MARKET_MOTION_ROOT", tmp_path)
    return dashboard.app.test_client()


def test_empty_store_returns_empty_shapes(client):
    body = client.get("/api/market-motion").get_json()
    assert body["frames"] == [] and body["latest_run_id"] is None and body["has_more"] is False
    assert body["score_model"] == {"max_score": 125, "buy_threshold": 60}
    latest = client.get("/api/market-motion/latest").get_json()
    assert latest["latest_run_id"] is None and latest["total_frames"] == 0
    tracker = client.get("/api/market-motion/tracker").get_json()
    assert tracker["tickers"] == {} and tracker["sessions_available"] == 0
    assert tracker["roster"] == {"cap": 500, "active": 0, "watching": 0, "overflow": 0}


def test_frames_are_ordered_paginated_and_latest_tracks_newest(client, tmp_path):
    ids = [write(tmp_path, f"2026-09-{d}", [q("AAA")])["run_id"] for d in (14, 15, 16, 17, 18)]
    body = client.get("/api/market-motion?limit=2").get_json()
    assert [f["run_id"] for f in body["frames"]] == ids[-2:]
    assert body["has_more"] is True and body["total_frames"] == 5 and body["latest_run_id"] == ids[-1]
    older = client.get(f"/api/market-motion?limit=2&before={ids[-2]}").get_json()
    assert [f["run_id"] for f in older["frames"]] == ids[1:3] and older["has_more"] is True
    assert older["latest_run_id"] == ids[-1]
    oldest = client.get(f"/api/market-motion?limit=10&before={ids[1]}").get_json()
    assert [f["run_id"] for f in oldest["frames"]] == ids[:1] and oldest["has_more"] is False
    latest = client.get("/api/market-motion/latest").get_json()
    assert latest["latest_run_id"] == ids[-1] and latest["total_frames"] == 5 and latest["run_kind"] == "daily_full"


def test_bad_parameters_fall_back_with_warnings_never_errors(client, tmp_path):
    write(tmp_path, "2026-09-18", [q("AAA")])
    body = client.get("/api/market-motion?limit=abc&before=../../etc/passwd").get_json()
    assert len(body["frames"]) == 1
    assert any("Invalid limit" in w for w in body["warnings"]) and any("Invalid before" in w for w in body["warnings"])
    assert any("clamped" in w for w in client.get("/api/market-motion?limit=999").get_json()["warnings"])
    missing = client.get("/api/market-motion?before=20250101T000000Z-daily_full").get_json()
    assert any("was not found" in w for w in missing["warnings"]) and len(missing["frames"]) == 1
    tracker = client.get("/api/market-motion/tracker?tiers=bogus&window=x").get_json()
    assert any("No valid tier" in w for w in tracker["warnings"]) and any("Invalid window" in w for w in tracker["warnings"])


def test_corrupt_frame_is_skipped_with_a_warning(client, tmp_path):
    write(tmp_path, "2026-09-17", [q("AAA")])
    (tmp_path / "snapshots" / "daily_full" / "20260918T170000Z-daily_full.json").write_text("{oops")
    body = client.get("/api/market-motion").get_json()
    assert len(body["frames"]) == 1 and len(body["warnings"]) == 1


def test_tracker_filters_and_roster(client, tmp_path):
    days = ["2026-09-14", "2026-09-15", "2026-09-16"]
    write(tmp_path, days[0], [q("LONG"), q("GONE", 90)])
    write(tmp_path, days[1], [q("LONG"), mm.make_point("GONE", mm.EVAL_NOT_SCORED, phase=3, drop_reason="phase_3")])
    write(tmp_path, days[2], [q("LONG"), q("NEW", 80)])
    body = client.get("/api/market-motion/tracker").get_json()
    assert set(body["tickers"]) == {"LONG", "GONE", "NEW"}
    assert body["tickers"]["LONG"]["current_streak_days"] == 3 and body["tickers"]["LONG"]["tier"] == "active"
    assert body["tickers"]["GONE"]["tier"] == "watching" and body["counts"]["active"] == 2
    assert body["roster"] == {"cap": 500, "active": 2, "watching": 1, "overflow": 0}
    assert set(client.get("/api/market-motion/tracker?tiers=watching").get_json()["tickers"]) == {"GONE"}
    assert set(client.get("/api/market-motion/tracker?min_streak=2").get_json()["tickers"]) == {"LONG"}
    windowed = client.get("/api/market-motion/tracker?window=2").get_json()
    assert windowed["tickers"]["LONG"]["sessions_observed"] == 2 and windowed["window"] == 2
    assert windowed["tickers"]["LONG"]["current_streak_days"] == 3          # streak is not windowed
    assert body["filters"] == {"tiers": ["active", "watching"], "min_streak": 0}


def test_response_is_strict_json(client, tmp_path):
    write(tmp_path, "2026-09-18", [q("AAA")])
    raw = client.get("/api/market-motion/tracker").get_data(as_text=True)
    assert "NaN" not in raw and "Infinity" not in raw


# --- /api/scan path containment ---------------------------------------------

@pytest.fixture
def scan_client(tmp_path, monkeypatch):
    scans = tmp_path / "scans"
    scans.mkdir()
    monkeypatch.setattr(dashboard, "SCAN_DIR", scans)
    return dashboard.app.test_client(), scans, tmp_path


def test_scan_endpoint_serves_reports_inside_scan_dir(scan_client):
    client, scans, _ = scan_client
    report = scans / "optimized_scan_20260918_170746.txt"
    report.write_text("Scan Date: 2026-09-18\nTotal Universe: 3,770 stocks\n", encoding="utf-8")
    body = client.get("/api/scan", query_string={"path": str(report)}).get_json()
    assert body["scan_date"] == "2026-09-18" and "error" not in body
    (scans / "latest_optimized_scan.txt").write_text("Scan Date: 2026-09-17\n", encoding="utf-8")
    assert client.get("/api/scan").get_json()["scan_date"] == "2026-09-17"


@pytest.mark.parametrize("make", [
    lambda scans, root: root / "secret.txt",                                   # outside SCAN_DIR
    lambda scans, root: scans / ".." / "secret.txt",                           # traversal
    lambda scans, root: scans / "notes.txt",                                   # inside, but not a scan report
    lambda scans, root: scans / "optimized_scan_x.json",                       # wrong extension
    lambda scans, root: root,                                                   # a directory
    lambda scans, root: scans / "sub" / "optimized_scan_20260918_170746.txt",  # nested
])
def test_scan_endpoint_refuses_anything_that_is_not_a_scan_report(scan_client, make):
    client, scans, root = scan_client
    (root / "secret.txt").write_text("Scan Date: LEAKED\n", encoding="utf-8")
    (scans / "notes.txt").write_text("Scan Date: LEAKED\n", encoding="utf-8")
    (scans / "sub").mkdir()
    (scans / "sub" / "optimized_scan_20260918_170746.txt").write_text("Scan Date: LEAKED\n", encoding="utf-8")
    body = client.get("/api/scan", query_string={"path": str(make(scans, root))}).get_json()
    assert body == {"error": "File not found"}


def test_scan_endpoint_refuses_a_symlink_that_escapes_scan_dir(scan_client):
    client, scans, root = scan_client
    target = root / "elsewhere.txt"
    target.write_text("Scan Date: LEAKED\n", encoding="utf-8")
    link = scans / "optimized_scan_20260918_000000.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks unavailable")
    assert client.get("/api/scan", query_string={"path": str(link)}).get_json() == {"error": "File not found"}


def test_tracker_accepts_tier_as_an_alias_for_tiers(client, tmp_path):
    write(tmp_path, "2026-09-14", [q("GONE"), q("KEEP")])
    write(tmp_path, "2026-09-15", [mm.make_point("GONE", mm.EVAL_NOT_SCORED, phase=3, drop_reason="phase_3"), q("KEEP")])
    assert set(client.get("/api/market-motion/tracker?tier=watching").get_json()["tickers"]) == {"GONE"}
