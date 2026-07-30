#!/usr/bin/env python3
"""Command Control Panel — run the project's key commands from a browser and watch them work live.

Usage:
    python control_panel.py                # start on port 5060, opens browser
    python control_panel.py --port 8090
"""

import argparse
import threading
import time
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

PROJECT_ROOT = Path(__file__).parent.resolve()
VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"
VENV_PIP = PROJECT_ROOT / "venv" / "bin" / "pip"

import subprocess  # noqa: E402  (kept near usage below for clarity)

COMMANDS = {
    "setup": {
        "label": "Setup Environment",
        "description": "Create venv + install all dependencies",
        "cmd": [
            "bash", "-c",
            f'python3 -m venv "{PROJECT_ROOT / "venv"}" && '
            f'"{VENV_PIP}" install --upgrade pip && '
            f'"{VENV_PIP}" install -r "{PROJECT_ROOT / "requirements.txt"}" && '
            f'"{VENV_PIP}" install flask',
        ],
    },
    "test_scan": {
        "label": "Quick Test Scan",
        "description": "100 stocks · ~1 minute",
        "cmd": [str(VENV_PYTHON), "run_optimized_scan.py", "--test-mode", "--git-storage", "--workers", "2"],
    },
    "full_scan": {
        "label": "Full Market Scan",
        "description": "3,800+ stocks · ~15-30 minutes",
        "cmd": [str(VENV_PYTHON), "run_optimized_scan.py", "--conservative", "--git-storage"],
        "confirm": True,
    },
    "dashboard": {
        "label": "Launch Results Dashboard",
        "description": "Starts the results dashboard on :5050 (keeps running until stopped)",
        "cmd": [str(VENV_PYTHON), "dashboard.py"],
        "link": "http://localhost:5050",
    },
}

STATE = {
    cid: {"status": "idle", "output": [], "returncode": None, "started": None, "proc": None}
    for cid in COMMANDS
}
LOCK = threading.Lock()


def _run_command(cid):
    entry = COMMANDS[cid]
    st = STATE[cid]
    with LOCK:
        st["status"] = "running"
        st["output"] = []
        st["returncode"] = None
        st["started"] = time.time()

    try:
        proc = subprocess.Popen(
            entry["cmd"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        with LOCK:
            st["proc"] = proc

        for line in proc.stdout:
            with LOCK:
                st["output"].append(line.rstrip("\n"))

        proc.wait()
        with LOCK:
            st["returncode"] = proc.returncode
            st["status"] = "success" if proc.returncode == 0 else "error"
            st["proc"] = None
    except Exception as exc:
        with LOCK:
            st["output"].append(f"[control-panel] failed to launch: {exc}")
            st["status"] = "error"
            st["proc"] = None


@app.route("/api/run/<cid>", methods=["POST"])
def api_run(cid):
    if cid not in COMMANDS:
        return jsonify({"error": "unknown command"}), 404
    if STATE[cid]["status"] == "running":
        return jsonify({"error": "already running"}), 409
    threading.Thread(target=_run_command, args=(cid,), daemon=True).start()
    return jsonify({"ok": True})


@app.route("/api/stop/<cid>", methods=["POST"])
def api_stop(cid):
    if cid not in COMMANDS:
        return jsonify({"error": "unknown command"}), 404
    st = STATE[cid]
    with LOCK:
        proc = st["proc"]
    if proc and proc.poll() is None:
        proc.terminate()
        with LOCK:
            st["status"] = "stopped"
        return jsonify({"ok": True})
    return jsonify({"error": "not running"}), 409


@app.route("/api/status/<cid>")
def api_status(cid):
    if cid not in COMMANDS:
        return jsonify({"error": "unknown command"}), 404
    st = STATE[cid]
    with LOCK:
        elapsed = (time.time() - st["started"]) if st["started"] and st["status"] == "running" else None
        return jsonify({
            "status": st["status"],
            "output": st["output"],
            "returncode": st["returncode"],
            "elapsed": elapsed,
        })


@app.route("/")
def index():
    return render_template_string(PAGE_HTML, commands=COMMANDS, root=str(PROJECT_ROOT))


PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Command Control Panel</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --border: #2a2d3a;
    --text: #e4e6eb;
    --muted: #8b8fa3;
    --green: #22c55e;
    --red: #ef4444;
    --yellow: #eab308;
    --blue: #3b82f6;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }

  .header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 20px 32px; }
  .header h1 { font-size: 20px; font-weight: 600; }
  .header .meta { color: var(--muted); font-size: 12px; margin-top: 4px; font-family: monospace; }

  .container { max-width: 900px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }

  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
  .card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
  .card-head h2 { font-size: 15px; font-weight: 600; }
  .card-head .desc { color: var(--muted); font-size: 12px; margin-top: 3px; }

  .pill { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; padding: 4px 10px; border-radius: 20px; white-space: nowrap; }
  .pill.idle { background: rgba(139,143,163,0.15); color: var(--muted); }
  .pill.running { background: rgba(59,130,246,0.15); color: var(--blue); animation: pulse 1.4s infinite; }
  .pill.success { background: rgba(34,197,94,0.15); color: var(--green); }
  .pill.error { background: rgba(239,68,68,0.15); color: var(--red); }
  .pill.stopped { background: rgba(234,179,8,0.15); color: var(--yellow); }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

  .output { background: #05060a; border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px; height: 180px; overflow-y: auto; font-family: 'SF Mono', Menlo, monospace; font-size: 12px; line-height: 1.5; color: #b8fbc0; white-space: pre-wrap; word-break: break-word; margin-bottom: 12px; }
  .output:empty::before { content: "waiting for output…"; color: var(--muted); font-style: italic; }

  .card-actions { display: flex; align-items: center; gap: 10px; }
  .btn { padding: 7px 14px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px; transition: all 0.15s; }
  .btn:hover:not(:disabled) { border-color: var(--blue); }
  .btn.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
  .btn.primary:hover:not(:disabled) { opacity: 0.9; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn.link { background: rgba(34,197,94,0.15); border-color: transparent; color: var(--green); text-decoration: none; display: none; }
  .elapsed { color: var(--muted); font-size: 12px; font-family: monospace; margin-left: auto; }
</style>
</head>
<body>

<div class="header">
  <h1>Stock Screener · Command Control Panel</h1>
  <div class="meta">{{ root }}</div>
</div>

<div class="container" id="app"></div>

<script>
const commands = {{ commands|tojson }};
const pollers = {};

function render() {
  const app = document.getElementById('app');
  for (const [cid, c] of Object.entries(commands)) {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-head">
        <div>
          <h2>${c.label}</h2>
          <div class="desc">${c.description}</div>
        </div>
        <span class="pill idle" id="pill-${cid}">idle</span>
      </div>
      <div class="output" id="output-${cid}"></div>
      <div class="card-actions">
        <button class="btn primary" id="run-${cid}">▶ Run</button>
        <button class="btn" id="stop-${cid}" disabled>■ Stop</button>
        <a class="btn link" id="link-${cid}" href="${c.link || '#'}" target="_blank">Open dashboard →</a>
        <span class="elapsed" id="elapsed-${cid}"></span>
      </div>
    `;
    app.appendChild(card);
    document.getElementById(`run-${cid}`).onclick = () => runCmd(cid);
    document.getElementById(`stop-${cid}`).onclick = () => stopCmd(cid);
  }
}

function runCmd(cid) {
  const c = commands[cid];
  if (c.confirm && !confirm(`${c.label} — ${c.description}. Continue?`)) return;
  document.getElementById('output-' + cid).textContent = '';
  fetch(`/api/run/${cid}`, { method: 'POST' }).then(() => poll(cid));
}

function stopCmd(cid) {
  fetch(`/api/stop/${cid}`, { method: 'POST' });
}

function poll(cid) {
  clearInterval(pollers[cid]);
  pollers[cid] = setInterval(() => tick(cid), 600);
  tick(cid);
}

function tick(cid) {
  fetch(`/api/status/${cid}`).then(r => r.json()).then(data => {
    const pill = document.getElementById('pill-' + cid);
    const out = document.getElementById('output-' + cid);
    const runBtn = document.getElementById('run-' + cid);
    const stopBtn = document.getElementById('stop-' + cid);
    const link = document.getElementById('link-' + cid);
    const elapsed = document.getElementById('elapsed-' + cid);

    pill.className = 'pill ' + data.status;
    pill.textContent = data.returncode !== null && data.status !== 'running'
      ? `${data.status} (exit ${data.returncode})`
      : data.status;

    out.textContent = data.output.join('\\n');
    out.scrollTop = out.scrollHeight;

    if (data.status === 'running') {
      runBtn.disabled = true;
      stopBtn.disabled = false;
      elapsed.textContent = data.elapsed ? Math.round(data.elapsed) + 's' : '';
      if (commands[cid].link && data.output.some(l => l.includes('Running on'))) {
        link.style.display = 'inline-block';
      }
    } else {
      runBtn.disabled = false;
      stopBtn.disabled = true;
      elapsed.textContent = '';
      clearInterval(pollers[cid]);
    }
  });
}

render();
for (const cid of Object.keys(commands)) { poll(cid); }
</script>
</body>
</html>
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5099)
    args = parser.parse_args()
    url = f"http://localhost:{args.port}"
    Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"Control panel running at {url}")
    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
