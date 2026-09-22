"""In-process scheduler for tracked-stock intraday re-scores."""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
import tempfile
from datetime import datetime, time as wall_time, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from src.screening import market_motion
from src.screening.market_motion_publisher import publish_frames


ET = ZoneInfo("America/New_York")
SLOTS = (wall_time(9, 35), wall_time(11, 35), wall_time(13, 35), wall_time(15, 35))
MARKET_OPEN = wall_time(9, 30)
MARKET_CLOSE = wall_time(16, 15)
DEFAULT_SETTINGS = {"enabled": False, "publish_to_github": True}
RESULT_PREFIX = "MARKET_MOTION_RESULT "


def _iso(value: datetime) -> str:
    return value.astimezone(ET).replace(microsecond=0).isoformat()


def _atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            json.dump(data, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


class MarketMotionScheduler:
    """Thread-safe scheduler with injected I/O boundaries for deterministic tests."""

    def __init__(
        self,
        *,
        now: Callable[[], datetime] | None = None,
        run_command: Callable[..., Any] | None = None,
        publish_fn: Callable[[], dict[str, Any]] | None = None,
        sleep: Callable[[float], None] | None = None,
        settings_path: str | os.PathLike[str] = "data/market_motion_settings.json",
        frames_root: str | os.PathLike[str] | None = None,
        jobs_busy_fn: Callable[[], bool] | None = None,
        command: list[str] | None = None,
        repo_root: str | os.PathLike[str] | None = None,
    ) -> None:
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._sleep = sleep or time.sleep
        self.settings_path = Path(settings_path)
        self.status_path = self.settings_path.with_name("market_motion_status.json")
        self.frames_root = Path(frames_root) if frames_root is not None else market_motion.DEFAULT_ROOT
        self.repo_root = Path(repo_root) if repo_root is not None else self.frames_root.parent.parent
        self.command = list(command or [str(self.repo_root / "venv" / "bin" / "python"),
                                        str(self.repo_root / "run_intraday_rescore.py")])
        self._run_command = run_command or self._default_run_command
        self._publish_fn = publish_fn or (lambda: publish_frames(self.repo_root))
        self._jobs_busy_fn = jobs_busy_fn or (lambda: False)
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.running = False
        self.settings = self._load_settings()
        persisted = _read_object(self.status_path)
        self.last_run = persisted.get("last_run") if isinstance(persisted.get("last_run"), dict) else None
        self.last_publish = persisted.get("last_publish") if isinstance(persisted.get("last_publish"), dict) else None
        self._attempt_date = persisted.get("attempt_date") if isinstance(persisted.get("attempt_date"), str) else None
        attempted = persisted.get("attempted_slots")
        self._attempted_slots = {value for value in attempted or [] if isinstance(value, str)}
        self._startup_checked_date: str | None = None

    def _load_settings(self) -> dict[str, bool]:
        raw = _read_object(self.settings_path)
        return {
            key: raw.get(key) if isinstance(raw.get(key), bool) else default
            for key, default in DEFAULT_SETTINGS.items()
        }

    def update_settings(self, changes: dict[str, bool]) -> dict[str, Any]:
        with self._lock:
            self.settings.update(changes)
            _atomic_json(self.settings_path, self.settings)
            self._persist_status()
            return self.status()

    def _default_run_command(self, command: list[str]) -> tuple[str, int]:
        env = os.environ.copy()
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)
        env["PYTHONUNBUFFERED"] = "1"
        completed = subprocess.run(
            command, cwd=self.repo_root, env=env, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=20 * 60,
            check=False,
        )
        output = completed.stdout
        if completed.stderr:
            output += ("\n" if output else "") + completed.stderr
        return output, completed.returncode

    def _invoke_command(self) -> tuple[str, int]:
        try:
            value = self._run_command(self.command)
        except TypeError:
            value = self._run_command()
        if hasattr(value, "stdout") and hasattr(value, "returncode"):
            return str(value.stdout or ""), int(value.returncode)
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("run_command must return output and exit code")
        first, second = value
        if isinstance(first, int):
            return str(second or ""), first
        return str(first or ""), int(second)

    def _current_et(self) -> datetime:
        value = self._now()
        if not isinstance(value, datetime):
            raise TypeError("now() must return a datetime")
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(ET)

    def _newest_frame(self) -> dict[str, Any] | None:
        frames, _ = market_motion.load_frames(self.frames_root)
        if not frames:
            return None
        newest = frames[-1]
        return {
            "run_id": newest["run_id"],
            "run_kind": newest["run_kind"],
            "generated_at": newest["generated_at"],
            "session_date": newest["session_date"],
        }

    def _reset_attempts_for(self, today: str) -> None:
        if self._attempt_date != today:
            self._attempt_date = today
            self._attempted_slots = set()

    @staticmethod
    def _slot_name(slot: wall_time) -> str:
        return slot.strftime("%H:%M")

    def _past_slots(self, now_et: datetime) -> list[wall_time]:
        return [slot for slot in SLOTS if slot <= now_et.time()]

    def _mark_past_attempted(self, now_et: datetime) -> None:
        self._attempted_slots.update(self._slot_name(slot) for slot in self._past_slots(now_et))

    def _newest_is_stale(self, now_et: datetime) -> bool:
        newest = self._newest_frame()
        if newest is None:
            return True
        try:
            generated = datetime.fromisoformat(newest["generated_at"].replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return True
        return now_et.astimezone(timezone.utc) - generated.astimezone(timezone.utc) > timedelta(minutes=100)

    def tick(self) -> dict[str, Any]:
        """Evaluate one timer tick and start at most one background run."""
        with self._lock:
            now_et = self._current_et()
            today = now_et.date().isoformat()
            self._reset_attempts_for(today)
            if not self.settings["enabled"] or self.running:
                return self.status()
            if now_et.weekday() >= 5 or not (MARKET_OPEN <= now_et.time() <= MARKET_CLOSE):
                return self.status()
            past = self._past_slots(now_et)
            due = [slot for slot in past if self._slot_name(slot) not in self._attempted_slots]
            if not due:
                return self.status()
            if self._startup_checked_date != today:
                self._startup_checked_date = today
                if not self._newest_is_stale(now_et):
                    self._mark_past_attempted(now_et)
                    self._persist_status()
                    return self.status()
            if self._jobs_busy_fn():
                return self.status()
            self._mark_past_attempted(now_et)
            self._start_worker(now_et)
            return self.status()

    def run_now(self) -> dict[str, Any]:
        with self._lock:
            if self.running:
                return {"started": False, "reason": "already running"}
            if self._jobs_busy_fn():
                return {"started": False, "reason": "another job is running"}
            self._start_worker(self._current_et())
            return {"started": True, "reason": None}

    def _start_worker(self, started_at: datetime) -> None:
        self.running = True
        thread = threading.Thread(target=self._run_once, args=(started_at,), daemon=True,
                                  name="market-motion-run")
        thread.start()

    def _run_once(self, started_at: datetime) -> None:
        result: dict[str, Any]
        publish_result: dict[str, Any] | None = None
        try:
            output, returncode = self._invoke_command()
            payload = None
            for line in output.splitlines():
                if line.startswith(RESULT_PREFIX):
                    try:
                        candidate = json.loads(line[len(RESULT_PREFIX):])
                    except json.JSONDecodeError:
                        continue
                    if isinstance(candidate, dict):
                        payload = candidate
            if payload is None:
                payload = {"status": "failed", "reason": f"missing result line (exit {returncode})"}
            elif returncode != 0 and payload.get("status") != "failed":
                payload = dict(payload, status="failed", reason=f"command exited {returncode}")
            finished = self._current_et()
            result = {
                "status": payload.get("status", "failed"),
                "reason": payload.get("reason"),
                "run_id": payload.get("run_id"),
                "finished_at": _iso(finished),
                "elapsed_seconds": payload.get(
                    "elapsed_seconds", round(max(0.0, (finished - started_at).total_seconds()), 3),
                ),
                "roster": payload.get("roster", 0),
                "analyzed": payload.get("analyzed", 0),
            }
            if result["status"] == "written" and self.settings["publish_to_github"]:
                try:
                    publish_result = self._publish_fn()
                except Exception as exc:
                    publish_result = {"status": "failed", "reason": str(exc), "published": []}
                if not isinstance(publish_result, dict):
                    publish_result = {"status": "failed", "reason": "invalid publisher result", "published": []}
        except Exception as exc:
            finished = self._current_et()
            result = {
                "status": "failed", "reason": str(exc), "run_id": None,
                "finished_at": _iso(finished),
                "elapsed_seconds": round(max(0.0, (finished - started_at).total_seconds()), 3),
                "roster": 0, "analyzed": 0,
            }
        with self._lock:
            self.last_run = result
            if publish_result is not None:
                self.last_publish = {
                    "status": publish_result.get("status", "failed"),
                    "reason": publish_result.get("reason"),
                    "at": result["finished_at"],
                    "published": list(publish_result.get("published") or []),
                }
            self.running = False
            self._persist_status()

    def _next_run(self, now_et: datetime) -> datetime | None:
        if not self.settings["enabled"]:
            return None
        for days_ahead in range(8):
            day = (now_et + timedelta(days=days_ahead)).date()
            if day.weekday() >= 5:
                continue
            for slot in SLOTS:
                candidate = datetime.combine(day, slot, ET)
                if candidate > now_et:
                    return candidate
        return None

    def _message(self, now_et: datetime, next_run: datetime | None) -> str:
        if not self.settings["enabled"]:
            return "Off"
        if self.running:
            return "Running"
        if now_et.weekday() < 5 and now_et.time() < MARKET_OPEN:
            return "Waiting for the market to open"
        if next_run is not None:
            return f"Next run {next_run.strftime('%H:%M')} ET"
        return "Waiting for the next trading day"

    def status(self) -> dict[str, Any]:
        with self._lock:
            now_et = self._current_et()
            next_run = self._next_run(now_et)
            try:
                newest = self._newest_frame()
            except Exception:
                newest = None
            return {
                "enabled": self.settings["enabled"],
                "publish_to_github": self.settings["publish_to_github"],
                "running": self.running,
                "last_run": self.last_run,
                "last_publish": self.last_publish,
                "next_run_at": _iso(next_run) if next_run is not None else None,
                "slots": [self._slot_name(slot) for slot in SLOTS],
                "newest_frame": newest,
                "message": self._message(now_et, next_run),
            }

    def _persist_status(self) -> None:
        data = {
            "last_run": self.last_run,
            "last_publish": self.last_publish,
            "attempt_date": self._attempt_date,
            "attempted_slots": sorted(self._attempted_slots),
        }
        try:
            _atomic_json(self.status_path, data)
        except OSError:
            pass

    def start(self) -> bool:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False
            self._stop.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True,
                                            name="market-motion-scheduler")
            self._thread.start()
            return True

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.tick()
            except Exception:
                pass
            self._sleep(30)

    def stop(self) -> None:
        self._stop.set()
