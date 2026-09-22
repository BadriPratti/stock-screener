import json
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.screening import market_motion
from src.screening.market_motion_scheduler import MarketMotionScheduler


def _clock(value):
    current = [value]
    return lambda: current[0], current


def _result_line(status="written", reason="frame_written"):
    payload = {
        "status": status, "reason": reason, "run_id": "run-1",
        "elapsed_seconds": 4.5, "roster": 12, "analyzed": 11,
    }
    return "noise\nMARKET_MOTION_RESULT " + json.dumps(payload) + "\n"


def _scheduler(tmp_path, now_value, **kwargs):
    now, holder = _clock(now_value)
    settings = tmp_path / "market_motion_settings.json"
    scheduler = MarketMotionScheduler(
        now=now,
        run_command=kwargs.pop("run_command", lambda command: (_result_line(), 0)),
        publish_fn=kwargs.pop("publish_fn", lambda: {
            "status": "published", "reason": None, "published": ["frame.json"],
        }),
        sleep=lambda seconds: None,
        settings_path=settings,
        frames_root=tmp_path / "frames",
        jobs_busy_fn=kwargs.pop("jobs_busy_fn", lambda: False),
        command=["python", "rescore.py"],
        repo_root=tmp_path,
        **kwargs,
    )
    return scheduler, holder


def _wait_done(scheduler):
    deadline = time.monotonic() + 2
    while scheduler.running and time.monotonic() < deadline:
        time.sleep(0.005)
    assert not scheduler.running


@pytest.mark.parametrize("instant", [
    datetime(2026, 9, 21, 13, 34, tzinfo=timezone.utc),
    datetime(2026, 9, 19, 15, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 21, 21, 0, tzinfo=timezone.utc),
])
def test_not_due_weekend_or_after_close_does_not_run(tmp_path, instant):
    calls = []
    scheduler, _ = _scheduler(tmp_path, instant, run_command=lambda command: calls.append(command))
    scheduler.update_settings({"enabled": True})
    scheduler.tick()
    assert calls == []


def test_at_slot_runs_once_and_missed_slots_catch_up_once(tmp_path):
    calls = []
    scheduler, holder = _scheduler(
        tmp_path, datetime(2026, 9, 21, 13, 35, tzinfo=timezone.utc),
        run_command=lambda command: (calls.append(command) or _result_line(), 0),
    )
    scheduler.update_settings({"enabled": True, "publish_to_github": False})
    scheduler.tick()
    _wait_done(scheduler)
    scheduler.tick()
    assert len(calls) == 1

    holder[0] = datetime(2026, 9, 21, 18, 0, tzinfo=timezone.utc)
    scheduler.tick()
    _wait_done(scheduler)
    assert len(calls) == 2
    assert scheduler.last_run["roster"] == 12


def test_busy_skip_does_not_mark_slot_and_disabled_does_nothing(tmp_path):
    busy = [True]
    calls = []
    scheduler, _ = _scheduler(
        tmp_path, datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc),
        jobs_busy_fn=lambda: busy[0],
        run_command=lambda command: (calls.append(command) or _result_line(), 0),
    )
    scheduler.tick()
    assert calls == []
    scheduler.update_settings({"enabled": True})
    scheduler.tick()
    assert calls == []
    busy[0] = False
    scheduler.tick()
    _wait_done(scheduler)
    assert len(calls) == 1


def test_startup_recent_frame_covers_past_slot_until_next_slot(tmp_path):
    calls = []
    scheduler, holder = _scheduler(
        tmp_path, datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc),
        run_command=lambda command: (calls.append(1) or _result_line(), 0),
    )
    frame = market_motion.build_frame(
        run_kind=market_motion.RUN_KIND_INTRADAY,
        generated_at=datetime(2026, 9, 21, 13, 50, tzinfo=timezone.utc),
        session_date="2026-09-21",
        points=[market_motion.make_point(
            "AAA", market_motion.EVAL_QUALIFIED, score=90, rs=0.2,
        )],
        scope={"mode": "tracked_roster", "completed": True},
    )
    market_motion.write_frame(frame, tmp_path / "frames")
    scheduler.update_settings({"enabled": True})
    scheduler.tick()
    assert calls == []

    holder[0] = datetime(2026, 9, 21, 15, 36, tzinfo=timezone.utc)
    scheduler.tick()
    _wait_done(scheduler)
    assert calls == [1]


def test_no_overlap_and_one_job_per_tick(tmp_path):
    release = threading.Event()
    calls = []

    def command(_):
        calls.append(1)
        release.wait(1)
        return _result_line(), 0

    scheduler, _ = _scheduler(
        tmp_path, datetime(2026, 9, 21, 18, 0, tzinfo=timezone.utc), run_command=command,
    )
    scheduler.update_settings({"enabled": True})
    scheduler.tick()
    assert scheduler.running is True
    scheduler.tick()
    assert scheduler.run_now() == {"started": False, "reason": "already running"}
    assert len(calls) == 1
    release.set()
    _wait_done(scheduler)


def test_publish_only_after_written_when_enabled(tmp_path):
    published = []
    scheduler, _ = _scheduler(
        tmp_path, datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc),
        publish_fn=lambda: published.append(1) or {
            "status": "published", "reason": None, "published": ["one"],
        },
    )
    scheduler.update_settings({"enabled": True})
    scheduler.tick()
    _wait_done(scheduler)
    assert published == [1]
    assert scheduler.last_publish["published"] == ["one"]

    skipped, _ = _scheduler(
        tmp_path / "second", datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc),
        run_command=lambda command: (_result_line("skipped", "closed"), 0),
        publish_fn=lambda: published.append(2),
    )
    skipped.update_settings({"enabled": True})
    skipped.tick()
    _wait_done(skipped)
    assert published == [1]


def test_failure_is_recorded_and_next_slot_can_run(tmp_path):
    outputs = ["no stable result", _result_line()]
    scheduler, holder = _scheduler(
        tmp_path, datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc),
        run_command=lambda command: (outputs.pop(0), 1),
    )
    scheduler.update_settings({"enabled": True})
    scheduler.tick()
    _wait_done(scheduler)
    assert scheduler.last_run["status"] == "failed"
    holder[0] = datetime(2026, 9, 21, 16, 0, tzinfo=timezone.utc)
    scheduler.tick()
    _wait_done(scheduler)
    assert scheduler.last_run["status"] == "failed"  # nonzero exit overrides a written payload


def test_run_now_works_disabled_and_refuses_busy(tmp_path):
    calls = []
    scheduler, _ = _scheduler(
        tmp_path, datetime(2026, 9, 20, 2, 0, tzinfo=timezone.utc),
        run_command=lambda command: (calls.append(1) or _result_line("skipped", "market_closed"), 0),
    )
    assert scheduler.status()["message"] == "Off"
    assert scheduler.run_now()["started"] is True
    _wait_done(scheduler)
    assert calls == [1]

    busy, _ = _scheduler(
        tmp_path / "busy", datetime(2026, 9, 20, 2, 0, tzinfo=timezone.utc),
        jobs_busy_fn=lambda: True,
    )
    assert busy.run_now() == {"started": False, "reason": "another job is running"}


def test_status_messages_and_dst_offsets(tmp_path):
    before, _ = _scheduler(tmp_path / "a", datetime(2026, 1, 12, 13, 0, tzinfo=timezone.utc))
    before.update_settings({"enabled": True})
    status = before.status()
    assert status["message"] == "Waiting for the market to open"
    assert status["next_run_at"].endswith("-05:00")

    summer, _ = _scheduler(tmp_path / "b", datetime(2026, 7, 13, 13, 0, tzinfo=timezone.utc))
    summer.update_settings({"enabled": True})
    status = summer.status()
    assert status["message"] == "Waiting for the market to open"
    assert status["next_run_at"].endswith("-04:00")


def test_corrupt_settings_defaults_atomic_write_and_restart_status(tmp_path):
    settings = tmp_path / "market_motion_settings.json"
    settings.write_text("{broken", encoding="utf-8")
    scheduler, _ = _scheduler(tmp_path, datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc))
    assert scheduler.settings == {"enabled": False, "publish_to_github": True}
    scheduler.update_settings({"enabled": True, "publish_to_github": False})
    assert json.loads(settings.read_text()) == {"enabled": True, "publish_to_github": False}
    assert not list(tmp_path.glob(".*.tmp"))
    scheduler.run_now()
    _wait_done(scheduler)

    restarted, _ = _scheduler(tmp_path, datetime(2026, 9, 21, 14, 5, tzinfo=timezone.utc))
    assert restarted.last_run["status"] == "written"


def test_settings_and_status_paths_are_ignored_by_real_repository():
    system_candidate = Path("/Library/Developer/CommandLineTools/usr/bin/git")
    git = str(system_candidate) if system_candidate.exists() else (shutil.which("git") or "git")
    root = market_motion.DEFAULT_ROOT.parents[1]
    for relative in ("data/market_motion_settings.json", "data/market_motion_status.json"):
        result = subprocess.run([git, "check-ignore", "-q", relative], cwd=root)
        assert result.returncode == 0
