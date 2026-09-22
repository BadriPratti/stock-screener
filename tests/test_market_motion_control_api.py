import json
import subprocess
import sys
from pathlib import Path

import pytest

import dashboard


class FakeScheduler:
    def __init__(self):
        self.settings = {"enabled": False, "publish_to_github": True}
        self.running = False

    def status(self):
        return {
            **self.settings, "running": self.running, "last_run": None,
            "last_publish": None, "next_run_at": None,
            "slots": ["09:35", "11:35", "13:35", "15:35"],
            "newest_frame": None, "message": "Off" if not self.settings["enabled"] else "Next run 09:35 ET",
        }

    def update_settings(self, changes):
        self.settings.update(changes)
        return self.status()

    def run_now(self):
        if self.running:
            return {"started": False, "reason": "already running"}
        self.running = True
        return {"started": True, "reason": None}


@pytest.fixture
def client(monkeypatch):
    fake = FakeScheduler()
    monkeypatch.setattr(dashboard, "_get_market_motion_scheduler", lambda: fake)
    dashboard.app.config["TESTING"] = True
    return dashboard.app.test_client(), fake


def test_default_state_is_off(client):
    http, _ = client
    response = http.get("/api/market-motion/scheduler")
    assert response.status_code == 200
    assert response.get_json()["enabled"] is False
    assert response.get_json()["publish_to_github"] is True


def test_post_toggles_boolean_settings(client):
    http, _ = client
    response = http.post(
        "/api/market-motion/scheduler",
        json={"enabled": True, "publish_to_github": False},
    )
    assert response.status_code == 200
    assert response.get_json()["enabled"] is True
    assert response.get_json()["publish_to_github"] is False


@pytest.mark.parametrize("kwargs", [
    {"data": "not json", "content_type": "text/plain"},
    {"data": "{broken", "content_type": "application/json"},
    {"json": {}},
    {"json": {"enabled": 1}},
    {"json": {"enabled": True, "extra": False}},
])
def test_post_rejects_invalid_bodies(client, kwargs):
    http, _ = client
    assert http.post("/api/market-motion/scheduler", **kwargs).status_code == 400


def test_run_now_returns_accepted_then_conflict(client):
    http, _ = client
    first = http.post("/api/market-motion/run-now")
    assert first.status_code == 202 and first.get_json() == {"started": True, "reason": None}
    second = http.post("/api/market-motion/run-now")
    assert second.status_code == 409 and second.get_json()["reason"] == "already running"


def test_importing_dashboard_does_not_start_scheduler_thread():
    root = Path(__file__).parents[1]
    script = (
        "import json,threading; before={t.name for t in threading.enumerate()}; "
        "import dashboard; after={t.name for t in threading.enumerate()}; "
        "print(json.dumps(sorted(after-before)))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=root,
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    assert json.loads(result.stdout.strip()) == []
