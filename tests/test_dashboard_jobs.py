"""Characterization tests for dashboard.py's job registry and read-only
"empty shape, not error" routes — written before the UI modernization sprint
(TASK-003) extracts/touches the frontend code that depends on this backend
contract. These lock in behavior found and fixed earlier this session:
unbounded JOBS growth, and routes that must return 200 with an empty shape
rather than an error when no data exists yet.

No network calls — these test the job registry and route contracts
directly, not real scans/fetches.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import dashboard


def _client():
    dashboard.app.config["TESTING"] = True
    return dashboard.app.test_client()


def test_unknown_job_returns_404():
    client = _client()
    resp = client.get("/api/jobs/does-not-exist")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "unknown job"


def test_prune_old_jobs_keeps_running_and_recent_jobs():
    with dashboard.JOBS_LOCK:
        dashboard.JOBS.clear()
        now = time.time()
        dashboard.JOBS["old-finished"] = {
            "kind": "news", "status": "success", "output": [],
            "returncode": 0, "started": now - dashboard.JOB_RETENTION_SECONDS - 60,
            "proc": None, "result_path": None,
        }
        dashboard.JOBS["recent-finished"] = {
            "kind": "news", "status": "success", "output": [],
            "returncode": 0, "started": now - 5,
            "proc": None, "result_path": None,
        }
        dashboard.JOBS["still-running"] = {
            "kind": "scan", "status": "running", "output": [],
            "returncode": None, "started": now - dashboard.JOB_RETENTION_SECONDS - 60,
            "proc": None, "result_path": None,
        }

    dashboard._prune_old_jobs()

    with dashboard.JOBS_LOCK:
        assert "old-finished" not in dashboard.JOBS, "a long-finished job must be pruned"
        assert "recent-finished" in dashboard.JOBS, "a recently-finished job must survive the retention window"
        assert "still-running" in dashboard.JOBS, "a running job must never be pruned, regardless of age"
        dashboard.JOBS.clear()


def test_momentum_status_empty_shape_not_error():
    client = _client()
    resp = client.get("/api/momentum-status/__nonexistent_group__")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == {}
    assert body["generated"] is None


def test_news_empty_shape_not_error():
    client = _client()
    resp = client.get("/api/news/__nonexistent_group__")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["news"] == {}


def test_price_history_empty_shape_not_error():
    client = _client()
    resp = client.get("/api/price-history/__nonexistent_group__")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["prices"] == {}


def test_read_json_parses_literal_nan_without_raising(tmp_path):
    # Python's json.loads accepts a literal NaN token (a non-standard
    # extension) rather than raising JSONDecodeError, so _read_json parses it
    # through as float('nan') instead of falling back to `default`. This
    # characterizes actual behavior — sanitize_nan() elsewhere is what turns
    # NaN into null before writing, not _read_json on the way back in.
    bad_file = tmp_path / "bad.json"
    bad_file.write_text('{"value": NaN}', encoding="utf-8")
    result = dashboard._read_json(bad_file, {"fallback": True})
    assert result != {"fallback": True}, "a literal NaN token must not trigger the default fallback"
    assert result["value"] != result["value"], "the parsed value should be float('nan') (nan != nan)"


def test_read_json_falls_back_on_malformed_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text('{"value": ', encoding="utf-8")
    result = dashboard._read_json(bad_file, {"fallback": True})
    assert result == {"fallback": True}


def test_read_json_falls_back_on_missing_file(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    result = dashboard._read_json(missing, {"fallback": True})
    assert result == {"fallback": True}


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
