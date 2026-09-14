#!/usr/bin/env python3
"""py2app entry point for the Stock Screener.app bundle.

Runs the real project's dashboard.py Flask app in a background thread, then
opens it in its own native window via pywebview (no browser tabs/address bar)
instead of the default browser — this is what makes it feel like a real app
rather than "a terminal command that happens to open a browser tab."

Imports dashboard.py as a module rather than duplicating its code, so any
future edits to the dashboard are picked up automatically without rebuilding
this .app. The bundle only carries a self-contained Python + Flask + pywebview
runtime; all the actual behavior (reading/writing data/, running scripts via
the project's own venv, git pull/push) still targets the real project folder.
"""
import os
import sys
import threading
from pathlib import Path

# This process loads Cocoa/WebKit (via pywebview below), which Apple documents
# as unsafe to fork() from — and dashboard.py's background jobs (Run Simulation,
# Full Scan, Positions, Sync) all fork()+exec() a subprocess. Without this, those
# can fail with bizarre, hard-to-reproduce errors (e.g. a stdlib import failing
# deep inside a C extension for no real reason) that don't happen when the same
# subprocess is spawned from a plain terminal (no WebKit loaded there). Must be
# set before pywebview/webview is imported.
os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

PROJECT_ROOT = Path(os.environ.get("STOCK_SCREENER_ROOT", str(Path.home() / "Desktop" / "stock-screener"))).resolve()

if not (PROJECT_ROOT / "dashboard.py").exists():
    sys.exit(
        f"Stock Screener: couldn't find the project at {PROJECT_ROOT}.\n"
        "Set STOCK_SCREENER_ROOT if the project folder has moved, then relaunch."
    )

sys.path.insert(0, str(PROJECT_ROOT))
import dashboard  # noqa: E402 — the real project's dashboard.py; importing does NOT run its __main__ block

PORT = 5050


def _run_flask():
    # threaded=True: the dashboard's own "Live" auto-refresh (positions, news,
    # momentum-status, price-history, all on their own ~90s timers) plus
    # auto-sync plus whatever job-status polling is in flight can easily have
    # several requests in the air at once. Werkzeug's dev server defaults to
    # handling one request at a time; under that, a single slow request (e.g.
    # a git pull, or a big JSON payload for a long-running scan's output)
    # blocks every other request — including a plain page load — until it
    # finishes, which reads as "the app just isn't opening."
    dashboard.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


threading.Thread(target=_run_flask, daemon=True).start()

import webview  # noqa: E402

webview.create_window(
    "Stock Screener", f"http://127.0.0.1:{PORT}",
    width=1440, height=900, min_size=(900, 600),
)
webview.start()
