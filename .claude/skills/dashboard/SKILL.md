---
name: dashboard
description: Launch the local GUI dashboard (Shortlist, Market, Backtests, Run Simulation, Full Scan) and open it in the browser. Use when the user says "open the dashboard," "show me the dashboard," "launch dashboard," or wants to see the Top 5 shortlist / backtest results / run a simulation visually instead of via CLI/email.
---

Launch `dashboard.py` locally (port 5050) and confirm it's up — this is a fully local Flask app, no GitHub Actions or network calls involved in starting it.

1. Check if something is already listening on port 5050 (`lsof -i :5050` or `curl -s -o /dev/null -w "%{http_code}" http://localhost:5050/`). If it responds, the dashboard is already running — just tell the user the URL (`http://localhost:5050`) and stop; do not start a second instance.
2. Otherwise, start it in the background: `venv/bin/python dashboard.py --port 5050` (omit `--no-browser` so it auto-opens the user's actual browser — this is a local desktop app, not a headless service). Run this with `run_in_background: true` since it's a long-lived server, not a one-shot command.
3. Wait ~2-3 seconds, then confirm it's actually up with `curl -s -o /dev/null -w "%{http_code}" http://localhost:5050/` (expect `200`).
4. Tell the user: the dashboard is running at `http://localhost:5050`, briefly what's on it (Shortlist = the real Top 5 filtered by fundamentals/news/congress-trading agents, Market = today's Top 20 + Buy/Sell signals, Backtests = real historical simulation results, Run Simulation = trigger fresh backtests and watch them run live, Full Scan = trigger a real scan with an option to enable the AI agents).
5. It keeps running in the background after this skill returns — mention that to stop it later they can close the terminal/process, or ask to have it stopped.
