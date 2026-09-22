#!/usr/bin/env python3
"""Interactive web dashboard for Stock Screener results.

Usage:
    python dashboard.py                    # Start dashboard on port 5050
    python dashboard.py --port 8080        # Custom port
    python dashboard.py --scan             # Run test scan first, then launch
    python dashboard.py --scan --full      # Run full scan first, then launch
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, render_template, request

from src.screening import market_motion, pick_history
from src.screening.market_motion_publisher import publish_frames
from src.screening.market_motion_scheduler import MarketMotionScheduler

# When bundled as a standalone .app (py2app sets sys.frozen), this file lives
# inside the bundle's Resources folder, not the real project checkout — but
# the dashboard always needs to read/write the real repo (git pull/push via
# /api/sync, data/ files, and it shells out to the project's own venv to run
# scripts). So PROJECT_ROOT deliberately does NOT follow __file__ when frozen;
# it points at the real checkout instead, overridable via STOCK_SCREENER_ROOT
# for anyone whose folder lives somewhere other than the default.
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(os.environ.get("STOCK_SCREENER_ROOT", str(Path.home() / "Desktop" / "stock-screener"))).resolve()
else:
    PROJECT_ROOT = Path(__file__).parent.resolve()

# py2app's own bootstrap chdir's the frozen process into the .app bundle's
# Resources folder before this module even runs — wrong for us either way, we
# always want PROJECT_ROOT. Setting it here (rather than passing cwd= on each
# subprocess call below) is what keeps those calls eligible for macOS's safe
# posix_spawn() path instead of fork()+exec() — see the comment in
# _launch_job() for why that distinction matters for the packaged .app.
os.chdir(str(PROJECT_ROOT))

app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"), static_folder=str(PROJECT_ROOT / "static"))

SCAN_DIR = PROJECT_ROOT / "data" / "daily_scans"
PICK_HISTORY_ROOT = PROJECT_ROOT / "data" / "pick_history"
MARKET_MOTION_ROOT = PROJECT_ROOT / "data" / "market_motion"
BACKTEST_DIR = PROJECT_ROOT / "data" / "backtest_history"
ADHOC_DIR = PROJECT_ROOT / "data" / "adhoc_simulations"
POSITIONS_CSV = PROJECT_ROOT / "data" / "positions_latest.csv"
VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"
SAMPLE_UNIVERSE_MAX = 150


def _venv_python():
    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


# The plain "git" on PATH (/usr/bin/git) is actually a stub that shells out to
# `xcodebuild -find git` to locate the real binary — on a machine with a
# broken/corrupted Xcode.app (as opposed to just the separate, lighter-weight
# Command Line Tools), that stub fails with an unrelated-looking dlopen error
# and git (and the Sync button) stops working entirely, even though a real,
# working git binary is usually still sitting right here. Preferring it
# sidesteps the broken xcodebuild lookup rather than depending on it.
_CLT_GIT = Path("/Library/Developer/CommandLineTools/usr/bin/git")


def _git_binary():
    if _CLT_GIT.exists():
        return str(_CLT_GIT)
    return shutil.which("git") or "/usr/bin/git"


def _read_json(path, default):
    """Load a JSON file, falling back to `default` if it's missing/unreadable
    — every read-only route uses this so "no data yet" is always a normal 200
    response, never a bare error."""
    path = Path(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return default


def parse_scan_file(filepath):
    """Parse a scan .txt file into structured data."""
    text = Path(filepath).read_text(encoding="utf-8")

    data = {
        "scan_date": "",
        "generated": "",
        "stats": {},
        "spy": {},
        "breadth": {},
        "regime": "",
        "buy_signals": [],
        "sell_signals": [],
    }

    # Header stats
    m = re.search(r"Scan Date:\s*(.+)", text)
    if m:
        data["scan_date"] = m.group(1).strip()

    m = re.search(r"Generated:\s*(.+)", text)
    if m:
        data["generated"] = m.group(1).strip()

    m = re.search(r"Total Universe:\s*([\d,]+)", text)
    if m:
        data["stats"]["total_universe"] = int(m.group(1).replace(",", ""))

    m = re.search(r"Analyzed:\s*([\d,]+)", text)
    if m:
        data["stats"]["analyzed"] = int(m.group(1).replace(",", ""))

    m = re.search(r"Processing Time:\s*([\d.]+)", text)
    if m:
        data["stats"]["processing_minutes"] = float(m.group(1))

    m = re.search(r"Error Rate:\s*([\d.]+)%", text)
    if m:
        data["stats"]["error_rate"] = float(m.group(1))

    m = re.search(r"Buy Signals:\s*(\d+)", text)
    if m:
        data["stats"]["buy_count"] = int(m.group(1))

    m = re.search(r"Sell Signals:\s*(\d+)", text)
    if m:
        data["stats"]["sell_count"] = int(m.group(1))

    # SPY
    m = re.search(r"Phase:\s*(\d)\s*-\s*(.+)", text)
    if m:
        data["spy"]["phase"] = int(m.group(1))
        data["spy"]["phase_name"] = m.group(2).strip()

    m = re.search(r"Trend:\s*(\w+)", text)
    if m:
        data["spy"]["trend"] = m.group(1).strip()

    m = re.search(r"Current Price:\s*\$([\d.]+)", text)
    if m:
        data["spy"]["price"] = float(m.group(1))

    m = re.search(r"Confidence:\s*(\d+)%", text)
    if m:
        data["spy"]["confidence"] = int(m.group(1))

    # Breadth
    for phase_num, label in [(1, "phase_1"), (2, "phase_2"), (3, "phase_3"), (4, "phase_4")]:
        m = re.search(
            rf"Phase {phase_num} \([^)]+\):\s*(\d+)\s*stocks\s*\(([\d.]+)%\)", text
        )
        if m:
            data["breadth"][f"{label}_count"] = int(m.group(1))
            data["breadth"][f"{label}_pct"] = float(m.group(2))

    m = re.search(r"Market Regime:\s*(.+)", text)
    if m:
        data["regime"] = m.group(1).strip()

    # Buy signals — extract each signal as header+details block
    buy_pattern = re.compile(
        r"BUY #(\d+):\s*(\w+)\s*\|\s*Score:\s*([\d.]+)/(\d+)"
        r".*?(?=BUY #\d+:|SELL #\d+:|={50,}.*(?:TOP SELL|END OF|ADDITIONAL)|\Z)",
        re.DOTALL,
    )
    for bm in buy_pattern.finditer(text):
        block = bm.group(0)
        signal = {
            "rank": int(bm.group(1)),
            "ticker": bm.group(2),
            "score": float(bm.group(3)),
            "max_score": int(bm.group(4)),
            "reasons": [],
        }

        m = re.search(r"Current Price:\s*\$([\d.]+)", block)
        if m:
            signal["current_price"] = float(m.group(1))

        m = re.search(r"Phase:\s*(\d)", block)
        if m:
            signal["phase"] = int(m.group(1))

        m = re.search(r"Entry Quality:\s*(\w+)", block)
        if m:
            signal["entry_quality"] = m.group(1)

        m = re.search(r"Stop Loss:\s*\$([\d.]+)", block)
        if m:
            signal["stop_loss"] = float(m.group(1))

        m = re.search(r"Risk/Reward:\s*([\d.]+):1\s*\(Risk \$([\d.]+),\s*Reward \$([\d.]+)\)", block)
        if m:
            signal["rr_ratio"] = float(m.group(1))
            signal["risk"] = float(m.group(2))
            signal["reward"] = float(m.group(3))

        m = re.search(r"RS:\s*([-\d.]+)", block)
        if m:
            signal["rs"] = float(m.group(1))

        m = re.search(r"Volume:\s*([\d.]+)x", block)
        if m:
            signal["volume_ratio"] = float(m.group(1))

        m = re.search(r"Reddit Mentions \(24h\):\s*(\d+)", block)
        if m:
            signal["reddit_mentions"] = int(m.group(1))

        reasons = re.findall(r"[•]\s*(.+)", block)
        signal["reasons"] = [r.strip() for r in reasons[:7]]

        m = re.search(r"Overall Assessment:\s*\n(.+)", block)
        if m:
            signal["assessment"] = m.group(1).strip()

        data["buy_signals"].append(signal)

    # Sell signals
    sell_pattern = re.compile(
        r"SELL #(\d+):\s*(\w+)\s*\|\s*Score:\s*([\d.]+)/(\d+)"
        r".*?(?=SELL #\d+:|={50,}.*(?:END OF|ADDITIONAL)|\Z)",
        re.DOTALL,
    )
    for sm in sell_pattern.finditer(text):
        block = sm.group(0)
        signal = {
            "rank": int(sm.group(1)),
            "ticker": sm.group(2),
            "score": float(sm.group(3)),
            "max_score": int(sm.group(4)),
            "reasons": [],
        }

        m = re.search(r"Current Price:\s*\$([\d.]+)", block)
        if m:
            signal["current_price"] = float(m.group(1))

        m = re.search(r"Phase:\s*(\d)\s*\|\s*.*Severity:\s*(\w+)", block)
        if m:
            signal["phase"] = int(m.group(1))
            signal["severity"] = m.group(2)

        m = re.search(r"Breakdown:\s*\$([\d.]+)", block)
        if m:
            signal["breakdown_level"] = float(m.group(1))

        m = re.search(r"Reddit Mentions \(24h\):\s*(\d+)", block)
        if m:
            signal["reddit_mentions"] = int(m.group(1))

        reasons = re.findall(r"[•]\s*(.+)", block)
        signal["reasons"] = [r.strip() for r in reasons[:5]]

        data["sell_signals"].append(signal)

    return data


def _scan_report_meta(path):
    """Read the small report header and return its universe/run metadata."""
    try:
        with Path(path).open(encoding="utf-8", errors="replace") as handle:
            header = handle.read(4096)
    except (OSError, TypeError, ValueError):
        return None, None

    universe_match = re.search(r"Total Universe:\s*([\d,]+)", header)
    if not universe_match:
        return None, None
    try:
        total_universe = int(universe_match.group(1).replace(",", ""))
    except ValueError:
        return None, None
    run_kind_match = re.search(r"Run Kind:\s*([\w-]+)", header)
    run_kind = run_kind_match.group(1) if run_kind_match else None
    return total_universe, run_kind


def get_scan_files():
    """Get list of available scan files, newest first."""
    if not SCAN_DIR.exists():
        return []
    files = sorted(SCAN_DIR.glob("optimized_scan_*.txt"), reverse=True)
    scans = []
    for f in files:
        total_universe, run_kind = _scan_report_meta(f)
        scans.append({
            "name": f.stem,
            "path": str(f),
            "date": f.stem.replace("optimized_scan_", ""),
            "total_universe": total_universe,
            "run_kind": run_kind,
            "is_sample": total_universe is not None and total_universe <= SAMPLE_UNIVERSE_MAX,
        })
    return scans


def get_backtest_files():
    """Get list of walk-forward backtest history files, newest first."""
    if not BACKTEST_DIR.exists():
        return []
    files = sorted(BACKTEST_DIR.glob("walk_forward_*.json"), reverse=True)
    out = []
    for f in files:
        data = _read_json(f, {})
        out.append({"name": f.stem, "path": str(f), "generated": data.get("generated")})
    return out


# ---------------------------------------------------------------------------
# Background job runner — generalized version of control_panel.py's
# STATE-dict + subprocess.Popen + polling pattern, keyed by a generated job_id
# (instead of a fixed command id) so multiple differently-configured
# simulations can run/be polled independently in one session.
# ---------------------------------------------------------------------------

JOBS = {}
JOBS_LOCK = threading.Lock()


def _market_motion_jobs_busy():
    with JOBS_LOCK:
        return any(job.get("status") in ("queued", "running") for job in JOBS.values())


def _run_market_motion_command(command):
    result = subprocess.run(
        command, env=_clean_subprocess_env(),
        capture_output=True, encoding="utf-8", errors="replace",
        timeout=20 * 60, close_fds=False,
    )
    output = result.stdout or ""
    if result.stderr:
        output += ("\n" if output else "") + result.stderr
    return output, result.returncode


_MARKET_MOTION_SCHEDULER = None
_MARKET_MOTION_SCHEDULER_LOCK = threading.Lock()


def _get_market_motion_scheduler():
    global _MARKET_MOTION_SCHEDULER
    with _MARKET_MOTION_SCHEDULER_LOCK:
        if _MARKET_MOTION_SCHEDULER is None:
            def pull_after_publish():
                result = _git_pull()
                output = result.stderr or result.stdout or ""
                return result.returncode == 0, output

            _MARKET_MOTION_SCHEDULER = MarketMotionScheduler(
                run_command=_run_market_motion_command,
                publish_fn=lambda: publish_frames(
                    PROJECT_ROOT, git_binary=_git_binary(), pull_fn=pull_after_publish,
                ),
                settings_path=PROJECT_ROOT / "data" / "market_motion_settings.json",
                frames_root=MARKET_MOTION_ROOT,
                jobs_busy_fn=_market_motion_jobs_busy,
                command=[_venv_python(), str(PROJECT_ROOT / "run_intraday_rescore.py")],
                repo_root=PROJECT_ROOT,
            )
        return _MARKET_MOTION_SCHEDULER


def start_background_services():
    """Start dashboard-owned daemons. Safe to call more than once."""
    _get_market_motion_scheduler().start()


def _clean_subprocess_env():
    """A copy of the current environment with PYTHONHOME/PYTHONPATH stripped —
    see the comment in _launch_job() for why those two specifically break a
    venv/bin/python subprocess when this process is the packaged .app. Also
    forces unbuffered child stdout: Python fully block-buffers stdout when
    it's a pipe (not a terminal), so without this every print() in the child
    script sits in a buffer until the process exits and flushes everything at
    once — the live output panel would show nothing the whole run, then the
    entire report appears all at once right as the job finishes, which reads
    exactly like it's stuck rather than actually working."""
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env["PYTHONUNBUFFERED"] = "1"
    return env


# How long a job is allowed to run before the dashboard force-kills it. Needed
# because a hung network call somewhere deep in a third-party library (a scan
# hit this: yfinance/urllib3 claims a 10s timeout on price history, but a real
# run still blocked forever in an SSL socket read to a Yahoo Finance host that
# had already dropped the connection — the retry/timeout logic just never
# kicked in) can otherwise sit forever, holding the job "running" and, via the
# close_fds=False tradeoff above, an inherited copy of the Flask listening
# socket — which is what took the whole dashboard offline last time this
# happened, not just the one job.
JOB_TIMEOUT_SECONDS = {"scan": 45 * 60}
DEFAULT_JOB_TIMEOUT_SECONDS = 10 * 60


def _kill_hung_job(job_id, proc):
    if proc.poll() is not None:
        return  # already finished naturally, nothing to do
    proc.kill()
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job:
            job["output"].append(
                "[dashboard] job exceeded its time limit and was terminated — "
                "likely a hung network call to a third-party data source that "
                "stopped responding without raising an error."
            )
            job["status"] = "error"


def _launch_job(job_id, cmd, result_path):
    with JOBS_LOCK:
        JOBS[job_id]["status"] = "running"
        kind = JOBS[job_id]["kind"]

    try:
        # No cwd= here on purpose — CPython's subprocess module only takes the
        # safe posix_spawn() path on macOS when cwd is None; passing cwd forces
        # the traditional fork()+exec() path instead, which is unsafe from a
        # process that has Cocoa/WebKit loaded (true when running inside the
        # packaged .app, via pywebview) and can cause bizarre, hard-to-reproduce
        # subprocess failures. main()/dashboard.py's own process cwd is set to
        # PROJECT_ROOT at startup instead (see chdir near the top of this file
        # and in mac_app/main.py), and every cmd argument is an absolute path,
        # so dropping cwd= here doesn't change what actually runs.
        #
        # close_fds=False for the same reason: this system's Python lacks
        # posix_spawn_closefrom, so posix_spawn eligibility requires close_fds
        # to be explicitly False (its default is True). The child inheriting
        # the parent's other open fds (e.g. the Flask listening socket) is an
        # acceptable tradeoff here — a local single-user tool, not a server
        # handling untrusted subprocess args — versus the alternative of
        # falling back to the unsafe fork() path.
        #
        # env=_clean_subprocess_env() because the packaged .app's own launcher
        # sets PYTHONHOME and PYTHONPATH to point at the *bundle's* Resources
        # folder — every subprocess call here runs venv/bin/python instead
        # (a real, separate Python 3.13), but it still inherits those two
        # variables by default, which override its own interpreter's normal
        # stdlib/site-packages resolution and point it at the bundle's instead.
        # That's what was actually causing `ModuleNotFoundError: No module
        # named 'zoneinfo'` deep inside pandas — venv/bin/python was loading
        # its standard library from the app bundle, not from itself.
        # encoding='utf-8' explicitly — a GUI-launched .app has no LANG/LC_ALL
        # set (a Terminal shell normally sets these), so text=True's default
        # locale-based decoding falls back to ASCII and crashes on any non-
        # ASCII character in the child's output (e.g. the em-dashes/bullets in
        # position_manager.py's rationale text).
        proc = subprocess.Popen(
            cmd, env=_clean_subprocess_env(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding="utf-8", errors="replace", bufsize=1, close_fds=False,
        )
        with JOBS_LOCK:
            JOBS[job_id]["proc"] = proc

        timeout_seconds = JOB_TIMEOUT_SECONDS.get(kind, DEFAULT_JOB_TIMEOUT_SECONDS)
        watchdog = threading.Timer(timeout_seconds, _kill_hung_job, args=(job_id, proc))
        watchdog.daemon = True
        watchdog.start()
        try:
            for line in proc.stdout:
                with JOBS_LOCK:
                    JOBS[job_id]["output"].append(line.rstrip("\n"))
            proc.wait()
        finally:
            watchdog.cancel()

        with JOBS_LOCK:
            JOBS[job_id]["returncode"] = proc.returncode
            JOBS[job_id]["status"] = "success" if proc.returncode == 0 else "error"
            JOBS[job_id]["proc"] = None
            JOBS[job_id]["result_path"] = result_path
    except Exception as exc:
        with JOBS_LOCK:
            JOBS[job_id]["output"].append(f"[dashboard] failed to launch: {exc}")
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["proc"] = None


def _build_job(kind, body):
    """Build (cmd, result_path) for a job kind from a request body, using each
    underlying script's own argparse defaults when a param is omitted."""
    python = _venv_python()
    job_id = uuid.uuid4().hex[:12]

    if kind == "scan":
        cmd = [python, str(PROJECT_ROOT / "run_optimized_scan.py")]
        if not body.get("full"):
            cmd.append("--test-mode")
        if body.get("enable_llm_agents"):
            cmd.append("--enable-llm-agents")
        result_path = str(SCAN_DIR / "shortlist_latest.json")

    elif kind == "backtest-top3":
        result_path = str(ADHOC_DIR / f"backtest_top3_{job_id}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "backtest_top3.py"),
            "--days", str(body.get("days", 7)),
            "--sample", str(body.get("sample", 150)),
            "--investment", str(body.get("investment", 1000)),
            "--json-out", result_path,
        ]

    elif kind == "backtest-monte-carlo":
        result_path = str(ADHOC_DIR / f"monte_carlo_{job_id}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "backtest_top3_monte_carlo.py"),
            "--days", str(body.get("days", 7)),
            "--pool", str(body.get("pool", 300)),
            "--sample", str(body.get("sample", 150)),
            "--iterations", str(body.get("iterations", 100)),
            "--investment", str(body.get("investment", 1000)),
            "--json-out", result_path,
        ]

    elif kind == "walk-forward":
        result_path = str(BACKTEST_DIR / "latest.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "walk_forward_backtest.py"),
            "--universe-size", str(body.get("universe_size", 250)),
            "--lookback-months", str(body.get("lookback_months", 9)),
            "--step-days", str(body.get("step_days", 14)),
            "--top-n", str(body.get("top_n", 10)),
            "--max-hold-days", str(body.get("max_hold_days", 60)),
            "--investment-per-trade", str(body.get("investment_per_trade", 1000)),
            "--seed", str(body.get("seed", 42)),
        ]

    elif kind == "positions":
        if not POSITIONS_CSV.exists():
            return None, None, None
        result_path = str(ADHOC_DIR / "positions_latest.json")
        cmd = [python, str(PROJECT_ROOT / "manage_positions.py"), "--csv", str(POSITIONS_CSV), "--json-out", result_path]

    elif kind == "news":
        tickers = body.get("tickers") or []
        group = body.get("group", "misc")
        if not tickers:
            return None, None, None
        result_path = str(ADHOC_DIR / f"news_{group}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "fetch_news.py"),
            "--tickers", ",".join(tickers),
            "--json-out", result_path,
        ]

    elif kind == "price-history":
        tickers = body.get("tickers") or []
        group = body.get("group", "misc")
        if not tickers:
            return None, None, None
        result_path = str(ADHOC_DIR / f"price_history_{group}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "fetch_price_history.py"),
            "--tickers", ",".join(tickers),
            "--json-out", result_path,
        ]

    elif kind == "momentum-status":
        tickers = body.get("tickers") or []
        group = body.get("group", "misc")
        if not tickers:
            return None, None, None
        result_path = str(ADHOC_DIR / f"momentum_status_{group}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "fetch_momentum_status.py"),
            "--tickers", ",".join(tickers),
            "--group", group,
            "--json-out", result_path,
        ]

    else:
        return None, None, None

    return job_id, cmd, result_path


JOB_RETENTION_SECONDS = 15 * 60  # how long a finished job stays pollable after completion


def _prune_old_jobs():
    """Drop finished jobs older than JOB_RETENTION_SECONDS. Without this, JOBS
    grows without bound — the dashboard's own "Live" auto-refresh (every 90s,
    across positions/news/price-history) now starts a job on every tick for as
    long as the app stays open, so an all-day session could otherwise pile up
    thousands of entries (each holding its full output line list) in memory.
    Called opportunistically on every new job start rather than on a timer."""
    now = time.time()
    with JOBS_LOCK:
        stale = [
            jid for jid, job in JOBS.items()
            if job["status"] not in ("queued", "running") and (now - job["started"]) > JOB_RETENTION_SECONDS
        ]
        for jid in stale:
            del JOBS[jid]


@app.route("/api/jobs/<kind>", methods=["POST"])
def api_start_job(kind):
    if kind == "positions" and not POSITIONS_CSV.exists():
        return jsonify({"error": "no positions CSV uploaded yet"}), 400

    body = request.json or {}
    job_id, cmd, result_path = _build_job(kind, body)
    if job_id is None:
        return jsonify({"error": f"unknown job kind: {kind}"}), 404

    _prune_old_jobs()
    ADHOC_DIR.mkdir(parents=True, exist_ok=True)
    with JOBS_LOCK:
        JOBS[job_id] = {
            "kind": kind, "status": "queued", "output": [], "returncode": None,
            "started": time.time(), "proc": None, "result_path": None,
        }
    threading.Thread(target=_launch_job, args=(job_id, cmd, result_path), daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/api/jobs/<job_id>")
def api_job_status(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "unknown job"}), 404
        elapsed = (time.time() - job["started"]) if job["status"] == "running" else None
        return jsonify({
            "status": job["status"], "output": job["output"],
            "returncode": job["returncode"], "elapsed": elapsed,
            "result_path": job["result_path"],
        })


@app.route("/api/jobs/<job_id>/stop", methods=["POST"])
def api_job_stop(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "unknown job"}), 404
        proc = job["proc"]
    if proc and proc.poll() is None:
        proc.terminate()
        with JOBS_LOCK:
            job["status"] = "stopped"
        return jsonify({"ok": True})
    return jsonify({"error": "not running"}), 409


def _git_pull():
    return subprocess.run(
        [_git_binary(), "pull", "--ff-only"],
        capture_output=True, encoding="utf-8", errors="replace", timeout=60, close_fds=False,
    )


# git reports this case differently from a conflict on a file it already
# tracks ("Your local changes to the following files would be overwritten"):
# an UNTRACKED file merely sitting at the same path as one the incoming
# commit wants to create. `git checkout -- data/` (the existing recovery
# below) only restores tracked files, so it does nothing for this case and
# the retry fails with the exact same error — which is what actually showed
# up in the dashboard ("Sync failed: ... untracked working tree files would
# be overwritten by merge: data/fundamentals_cache/RMBI_fundamentals.json").
# This happens whenever a local run (Full Scan, or the market-motion
# rescore/seed scans) fetches a fresh per-ticker cache file that the
# automated workflow's own commit also happens to touch.
_UNTRACKED_CONFLICT_HEADER = "untracked working tree files would be overwritten by merge"
_UNTRACKED_CONFLICT_LINE = re.compile(r"^\t(.+)$", re.MULTILINE)


def _safe_untracked_conflict_paths(git_output, project_root, git_binary):
    """Parse the untracked-file paths git's error names, and return only the
    ones it is safe to delete: inside data/ (this project's convention for
    always-regenerable output), never under position/ (real account data,
    never touched), resolving without escaping the project root, and
    confirmed by `git status` to actually be untracked right now — so a
    parsing mistake can never delete something real. Returns None if the
    error isn't this case at all, or [] if it is but nothing in it is safe to
    remove (the caller should then leave the conflict for the user to see).
    """
    if _UNTRACKED_CONFLICT_HEADER not in git_output:
        return None
    header_at = git_output.index(_UNTRACKED_CONFLICT_HEADER)
    tail = git_output[header_at:]
    listed = _UNTRACKED_CONFLICT_LINE.findall(tail)
    data_root = (project_root / "data").resolve()
    safe = []
    for rel in listed:
        rel = rel.strip()
        if not rel:
            continue
        try:
            resolved = (project_root / rel).resolve()
        except (OSError, RuntimeError, ValueError):
            continue
        if data_root not in resolved.parents and resolved != data_root:
            continue
        if not resolved.is_relative_to(project_root):
            continue
        status = subprocess.run(
            [git_binary, "status", "--porcelain=v1", "--", rel],
            capture_output=True, encoding="utf-8", errors="replace", timeout=15,
            cwd=project_root, close_fds=False,
        )
        if not status.stdout.startswith("??"):
            continue  # not actually untracked (or git couldn't confirm it) — leave it alone
        safe.append(resolved)
    return safe


@app.route("/api/sync", methods=["POST"])
def api_sync():
    """git pull the repo so today's committed scan/shortlist/backtest data
    (from the scheduled GitHub Actions runs that send the email) shows up
    here too, without the user having to leave the dashboard to do it."""
    try:
        # Absolute git path (not the bare "git", which posix_spawn eligibility
        # requires — see the comment in _launch_job()) and no cwd= (process cwd
        # is already PROJECT_ROOT, set once at startup).
        result = _git_pull()

        # A local job run (Full Scan / Positions / etc., all launched from
        # this same dashboard) writes into the same data/ paths the automated
        # workflow commits to — if you've run anything locally since the last
        # sync, those two can diverge and block a fast-forward pull. Since
        # data/ is always regenerable output (never something hand-authored),
        # the automated commit is the one that actually matters here: discard
        # the local modifications and retry once rather than surfacing a git
        # merge error for what's really just stale scan output.
        if result.returncode != 0 and "overwritten by merge" in (result.stdout + result.stderr):
            subprocess.run(
                [_git_binary(), "checkout", "--", "data/"],
                capture_output=True, encoding="utf-8", errors="replace", timeout=30, close_fds=False,
            )
            result = _git_pull()

        # Still blocked, and specifically by an untracked file (checkout
        # above can't touch those) — remove exactly the offending, verified-
        # safe file(s) and retry once more.
        if result.returncode != 0:
            combined = result.stdout + result.stderr
            safe_paths = _safe_untracked_conflict_paths(combined, PROJECT_ROOT, _git_binary())
            if safe_paths:
                for path in safe_paths:
                    try:
                        path.unlink()
                    except FileNotFoundError:
                        pass
                result = _git_pull()

        return jsonify({
            "success": result.returncode == 0,
            "output": (result.stdout + result.stderr).strip(),
        })
    except Exception as e:
        return jsonify({"success": False, "output": str(e)})


@app.route("/api/positions/upload", methods=["POST"])
def api_positions_upload():
    """Save a Fidelity Positions CSV export uploaded from the browser. Never
    leaves this machine — no credentials, no login, just the file you already
    downloaded yourself. Overwrites the previous upload (single "current
    portfolio" file, not a history)."""
    f = request.files.get("csv")
    if not f or not f.filename:
        return jsonify({"success": False, "error": "no file uploaded"}), 400
    POSITIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
    f.save(str(POSITIONS_CSV))
    return jsonify({"success": True})


@app.route("/api/positions")
def api_positions():
    """Last computed position analysis, if any. Empty/`reason` shape (not an
    error) when nothing's been uploaded or analyzed yet, matching the other
    read-only routes."""
    has_csv = POSITIONS_CSV.exists()
    data = _read_json(ADHOC_DIR / "positions_latest.json", None)
    if data is None:
        return jsonify({
            "has_csv": has_csv,
            "position_analyses": [], "summary": {"total_positions": 0}, "urgent_actions": [],
        })
    data["has_csv"] = has_csv
    return jsonify(data)


@app.route("/api/news/<group>")
def api_news(group):
    """Last fetched news batch for a group ("positions" or "buy"). Empty shape
    (not an error) when nothing's been fetched yet."""
    return jsonify(_read_json(ADHOC_DIR / f"news_{group}.json", {"generated": None, "tickers": [], "news": {}}))


@app.route("/api/price-history/<group>")
def api_price_history(group):
    """Last fetched price-history batch for a group (e.g. "shortlist"). Empty
    shape (not an error) when nothing's been fetched yet."""
    return jsonify(_read_json(ADHOC_DIR / f"price_history_{group}.json", {"generated": None, "tickers": [], "prices": {}}))


@app.route("/api/momentum-status/<group>")
def api_momentum_status(group):
    """Last computed hot/stable/basing/avoid classification (+ day-streak) for
    a group. Empty shape (not an error) when nothing's been fetched yet."""
    return jsonify(_read_json(ADHOC_DIR / f"momentum_status_{group}.json", {"generated": None, "tickers": [], "status": {}}))


# ---------------------------------------------------------------------------
# Read-only data routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.before_request
def _start_services_for_app_window():
    # The pywebview launcher imports this module, then opens the root page. A
    # root-page hook starts services in that launch path while keeping a plain
    # module import (including test collection) completely side-effect free.
    if request.endpoint == "index" and not app.testing:
        start_background_services()


@app.route("/api/scans")
def api_scans():
    return jsonify(get_scan_files())


@app.route("/api/pick-history")
def api_pick_history():
    """Derived pick consistency, with an empty shape rather than API errors."""
    fallback_warnings = []

    list_name = request.args.get("list", "shortlist")
    if list_name not in pick_history.LIST_NAMES:
        fallback_warnings.append(
            f"Unknown list {list_name!r}; using 'shortlist'."
        )
        list_name = "shortlist"

    raw_window = request.args.get("window", "5")
    try:
        window = int(raw_window)
    except (TypeError, ValueError):
        fallback_warnings.append(
            f"Invalid window {raw_window!r}; using default 5."
        )
        window = 5
    else:
        clamped_window = min(60, max(1, window))
        if clamped_window != window:
            fallback_warnings.append(
                f"Window {window} was clamped to {clamped_window}."
            )
        window = clamped_window

    load_warnings = []
    try:
        snapshots, load_warnings = pick_history.load_snapshots(PICK_HISTORY_ROOT)
        result = pick_history.compute_history(
            snapshots,
            list_name=list_name,
            window=window,
            warnings=load_warnings + fallback_warnings,
        )
    except Exception as exc:
        app.logger.exception("Failed to compute pick history")
        result = {
            "schema_version": pick_history.SCHEMA_VERSION,
            "list": list_name,
            "run_kind": pick_history.RUN_KIND_DAILY_FULL,
            "window_requested": window,
            "sessions_available": 0,
            "sessions": [],
            "denominator": 0,
            "latest_session_date": None,
            "coverage_gaps": [],
            "warnings": load_warnings + fallback_warnings + [
                f"Could not compute pick history: {exc}"
            ],
            "tickers": {},
        }
    return jsonify(result)


# --- Market motion: persistent buy-opportunity frames + per-stock tracker -----

_RUN_ID_PARAM = re.compile(r"\d{8}T\d{6}Z-[a-z_]+")


def _clamped_int(name, default, low, high, warnings):
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        warnings.append(f"Invalid {name} {raw!r}; using default {default}.")
        return default
    clamped = min(high, max(low, value))
    if clamped != value:
        warnings.append(f"{name} {value} was clamped to {clamped}.")
    return clamped


def _empty_motion(warnings):
    return {
        "schema_version": market_motion.SCHEMA_VERSION,
        "score_model": {"max_score": market_motion.MAX_SCORE, "buy_threshold": market_motion.BUY_THRESHOLD},
        "frames": [],
        "latest_run_id": None,
        "total_frames": 0,
        "has_more": False,
        "warnings": warnings,
    }


@app.route("/api/market-motion")
def api_market_motion():
    """Recent completed frames (oldest first) for the replay. Additive; never an API error."""
    fallback = []
    limit = _clamped_int("limit", 20, 1, 60, fallback)
    before = request.args.get("before")
    if before is not None and not _RUN_ID_PARAM.fullmatch(before):
        fallback.append(f"Invalid before {before!r}; ignored.")
        before = None
    try:
        frames, load_warnings = market_motion.load_frames(MARKET_MOTION_ROOT)
        warnings = load_warnings + fallback
        total = len(frames)
        pool = frames
        if before is not None:
            ids = [f["run_id"] for f in frames]
            if before in ids:
                pool = frames[:ids.index(before)]
            else:
                warnings.append(f"before {before!r} was not found; showing the newest frames.")
        selected = pool[-limit:]
        return jsonify({
            "schema_version": market_motion.SCHEMA_VERSION,
            "score_model": {"max_score": market_motion.MAX_SCORE, "buy_threshold": market_motion.BUY_THRESHOLD},
            "frames": selected,
            "latest_run_id": frames[-1]["run_id"] if frames else None,
            "total_frames": total,
            "has_more": len(pool) > len(selected),
            "warnings": warnings,
        })
    except Exception as exc:
        app.logger.exception("Failed to load market motion frames")
        return jsonify(_empty_motion(fallback + [f"Could not load market motion: {exc}"]))


@app.route("/api/market-motion/latest")
def api_market_motion_latest():
    """Small poll target for the Live loop: newest frame id, time and count."""
    try:
        frames, warnings = market_motion.load_frames(MARKET_MOTION_ROOT)
    except Exception as exc:
        app.logger.exception("Failed to load market motion frames")
        return jsonify({"latest_run_id": None, "generated_at": None, "run_kind": None,
                        "total_frames": 0, "warnings": [f"Could not load market motion: {exc}"]})
    newest = frames[-1] if frames else None
    return jsonify({
        "latest_run_id": newest["run_id"] if newest else None,
        "generated_at": newest["generated_at"] if newest else None,
        "run_kind": newest["run_kind"] if newest else None,
        "session_date": newest["session_date"] if newest else None,
        "total_frames": len(frames),
        "warnings": warnings,
    })


@app.route("/api/market-motion/tracker")
def api_market_motion_tracker():
    """Per-stock tracker (tier, streaks, denominators), derived on read."""
    fallback = []
    window = None
    if request.args.get("window") is not None:
        window = _clamped_int("window", 5, 1, 250, fallback)
    min_streak = _clamped_int("min_streak", 0, 0, 250, fallback)
    valid_tiers = (market_motion.TIER_ACTIVE, market_motion.TIER_WATCHING, market_motion.TIER_RETIRED)
    raw_tiers = request.args.get("tiers") or request.args.get("tier") or "active,watching"
    tiers = {t for t in (x.strip() for x in raw_tiers.split(",")) if t in valid_tiers}
    if not tiers:
        fallback.append(f"No valid tier in {raw_tiers!r}; using active,watching.")
        tiers = {market_motion.TIER_ACTIVE, market_motion.TIER_WATCHING}
    try:
        frames, load_warnings = market_motion.load_frames(MARKET_MOTION_ROOT)
        tracker = market_motion.compute_tracker(frames, window=window, warnings=load_warnings + fallback)
        roster = market_motion.build_roster(tracker)
        tracker["tickers"] = {
            t: r for t, r in tracker["tickers"].items()
            if r["tier"] in tiers and r["current_streak_days"] >= min_streak
        }
        tracker["roster"] = {k: roster[k] for k in ("cap", "active", "watching", "overflow")}
        tracker["filters"] = {"tiers": sorted(tiers), "min_streak": min_streak}
        return jsonify(tracker)
    except Exception as exc:
        app.logger.exception("Failed to compute market motion tracker")
        empty = market_motion.compute_tracker([], warnings=fallback + [f"Could not compute tracker: {exc}"])
        empty["roster"] = {"cap": market_motion.DEFAULT_ROSTER_CAP, "active": 0, "watching": 0, "overflow": 0}
        empty["filters"] = {"tiers": sorted(tiers), "min_streak": min_streak}
        return jsonify(empty)


@app.route("/api/market-motion/scheduler", methods=["GET", "POST"])
def api_market_motion_scheduler():
    scheduler = _get_market_motion_scheduler()
    if request.method == "GET":
        return jsonify(scheduler.status())
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400
    body = request.get_json(silent=True)
    allowed = {"enabled", "publish_to_github"}
    if not isinstance(body, dict) or not body or set(body) - allowed:
        return jsonify({"error": "body may contain only enabled and publish_to_github"}), 400
    if any(not isinstance(value, bool) for value in body.values()):
        return jsonify({"error": "scheduler settings must be boolean"}), 400
    return jsonify(scheduler.update_settings(body))


@app.route("/api/market-motion/run-now", methods=["POST"])
def api_market_motion_run_now():
    result = _get_market_motion_scheduler().run_now()
    return jsonify(result), 202 if result["started"] else 409


def _resolve_scan_path(raw_path):
    """Resolve a client-supplied scan path to a report inside SCAN_DIR, or None.

    The endpoint used to open ANY existing path; only real scan reports
    (optimized_scan_*.txt / latest_optimized_scan.txt directly under SCAN_DIR)
    are served now, whatever the query string says.
    """
    try:
        candidate = Path(raw_path).resolve()
        scan_dir = SCAN_DIR.resolve()
    except (OSError, RuntimeError, ValueError):
        return None
    if candidate.parent != scan_dir or not candidate.is_file():
        return None
    name = candidate.name
    if name == "latest_optimized_scan.txt" or (name.startswith("optimized_scan_") and name.endswith(".txt")):
        return candidate
    return None


@app.route("/api/scan")
def api_scan():
    path = request.args.get("path", "")
    if not path:
        latest = SCAN_DIR / "latest_optimized_scan.txt"
        if latest.exists():
            path = str(latest)
        else:
            return jsonify({"error": "No scan data"})

    resolved = _resolve_scan_path(path)
    if resolved is None:
        return jsonify({"error": "File not found"})

    return jsonify(parse_scan_file(resolved))


@app.route("/api/top20")
def api_top20():
    return jsonify(_read_json(SCAN_DIR / "top20_latest.json", {"generated": None, "result": None, "top20": []}))


@app.route("/api/shortlist")
def api_shortlist():
    return jsonify(_read_json(SCAN_DIR / "shortlist_latest.json", {
        "generated": None, "result": None, "shortlist": [],
        "fundamentals_audits": {}, "catalyst_sentiments": {}, "congress_signals": {},
    }))


@app.route("/api/backtest/latest")
def api_backtest_latest():
    data = _read_json(BACKTEST_DIR / "latest.json", None)
    if data is None:
        return jsonify({"generated": None, "params": {}, "summary": {}, "component_correlations": {}, "trade_count": 0})
    return jsonify({
        "generated": data.get("generated"),
        "params": data.get("params", {}),
        "summary": data.get("summary", {}),
        "component_correlations": data.get("component_correlations", {}),
        "trade_count": len(data.get("trades", [])),
    })


@app.route("/api/backtest/trades")
def api_backtest_trades():
    path = request.args.get("path")
    data = _read_json(path if path else (BACKTEST_DIR / "latest.json"), {"trades": []})
    trades = data.get("trades", [])

    # Cumulative P&L ordered by exit date — realized-P&L equity curve.
    dated = [t for t in trades if t.get("exit_date")]
    dated.sort(key=lambda t: t["exit_date"])
    equity_curve = []
    running = 0.0
    for t in dated:
        running += t.get("dollar_pnl", 0) or 0
        equity_curve.append({"date": t["exit_date"], "cumulative_pnl": round(running, 2)})

    return jsonify({"trades": trades, "equity_curve": equity_curve})


@app.route("/api/backtest/history")
def api_backtest_history():
    return jsonify(get_backtest_files())


@app.route("/api/backtest/run")
def api_backtest_run():
    path = request.args.get("path", "")
    if not path or not Path(path).exists():
        return jsonify({"error": "File not found"}), 404
    return jsonify(_read_json(path, {}))


def open_browser(port):
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Screener Dashboard")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--scan", action="store_true", help="Run a test scan before launching")
    parser.add_argument("--full", action="store_true", help="With --scan, run full scan instead of test")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    if args.scan:
        print("Running scan before dashboard launch...")
        cmd = [_venv_python(), str(PROJECT_ROOT / "run_optimized_scan.py")]
        if not args.full:
            cmd.append("--test-mode")
        subprocess.run(cmd)

    if not args.no_browser:
        Timer(1.5, open_browser, [args.port]).start()

    start_background_services()
    print(f"\n  Dashboard running at http://localhost:{args.port}\n")
    # 127.0.0.1, not 0.0.0.0: this app has zero authentication — every route
    # (including git pull, running scans/backtests, and reading arbitrary
    # local JSON files via the backtest ?path= params) is reachable by anyone
    # who can open the URL. 0.0.0.0 would expose all of that to the whole
    # LAN/WiFi, not just this machine. Matches mac_app/main.py, which already
    # binds 127.0.0.1 for the packaged .app that most people actually run.
    # threaded=True — see the matching comment in mac_app/main.py.
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True)
