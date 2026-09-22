# Verified facts for the Live Chart council (extracted by the sprint lead; treat as data)

## What the Market "Buy Opportunity Map" plots today
- static/js/views/market.js: buildBuyOpportunityPoints(scan.buy_signals) -> {x: rs, y: score/max_score*100, signal}. One Chart.js scatter dataset, one canvas #marketScatterChart, rebuilt from scratch (destroy + new Chart) by renderMarketScatterChart() in static/js/charts.js (classic <script>, globals, NOT an ES module). Chart.js 4.4.7 vendored (static/js/vendor/chart.umd.min.js), no plugins other than a local rs-zero-line plugin.
- buy_signals come from dashboard.py parse_scan_file(), which REGEX-PARSES the human-readable text report (data/daily_scans/optimized_scan_*.txt). The scanner (run_optimized_scan.py save_report) only writes the TOP 50 buy signals in detail (buy_signals[:50]); the remaining buys are listed as bare tickers under "ADDITIONAL BUYS" with no score/rs. So the chart today plots at most 50 dots.
- Real numbers (see buy_signal_facts.txt): full scans report 364-479 total buy signals but only 50 have detail. Across the 5 recorded full scans there are 84 distinct tickers in the top-50 lists, 25 of them in all 5; ~37-39 of 50 carry over scan to scan. Score-as-%-of-max only ranges 81-93% in the top 50 (very compressed vertical axis); rs ranges about -0.15..1.34.
- Per-signal fields available: ticker, rank, score, max_score, phase, entry_quality, stop_loss, risk, reward, rr_ratio, rs, volume_ratio (sometimes), reddit_mentions, reasons[], current_price (sometimes). See sample_buy_signal.json.
- The pick-history ledger (src/screening/pick_history.py, data/pick_history/snapshots/daily_full/YYYY-MM-DD.json) currently stores ONLY shortlist and top20 lists (slim rows), NOT buy_signals. One snapshot per America/New_York calendar date, same-date rerun REPLACES the file (idempotent), only the full-universe daily scan is recorded (midday 100-stock sample is deliberately excluded). "Day" = recorded session; streaks/appearance-counts/denominators all count sessions. 26 + 74 tests lock this in; schema_version=1; compute_history is derived on read.
- /api/pick-history?list=shortlist|top20&window=N exists. /api/scans lists reports with total_universe/run_kind/is_sample. /api/scan?path= returns parse_scan_file() output.

## Scheduling reality (verified from repo + git log + gh)
- Repo BadriPratti/stock-screener is PUBLIC -> GitHub-hosted runner minutes are free/unmetered for public repos. The real costs are: Anthropic API calls (only made on the Top 20 pool when --enable-llm-agents), data-provider rate limits (yfinance etc.), email volume, git history growth, and push contention.
- Daily workflow: cron '0 12 * * 1-5', job timeout 120 min, command `python run_optimized_scan.py --conservative --git-storage --enable-llm-agents --run-kind daily-full`. Every recorded full scan: Universe ~3,770, analyzed ~1,970, "Processing Time: 62.8 minutes" (job ~64 min). --conservative = 2 workers, 1.0s delay. --aggressive (5 workers, 0.3s) exists but warns it MAY HIT RATE LIMITS.
- Observed GitHub scheduled-run delay: the workflow file itself documents that actual starts land ~4-5 hours after the cron time (16:11-17:39 UTC vs 12:00 UTC scheduled), every run since 2026-08-31. Scheduled workflows are best-effort; a "every 2 hours" cron will drift, skip, and bunch up. Git log confirms: full scans committed ~17:07-17:35 UTC; midday sample committed ~19:26-20:00 UTC (cron 17:00 UTC).
- Midday workflow: cron '0 17 * * 1-5', `--test-mode --run-kind midday-sample`, ~0.8 minute, random 100-stock sample; it does NOT write canonical top20/shortlist and does not record the ledger.
- Each workflow has its own concurrency group (screening-daily, screening-midday), cancel-in-progress false. GitHub keeps 1 running + 1 pending per group; a newer pending run cancels the older pending one.
- Both workflows commit to main and push via ad-m/github-push-action with NO rebase-before-push (deferred hardening). Two workflows pushing at once can reject one push.
- run_optimized_scan.py sends the scan-report email (EmailNotifier.send_scan_report) at the end of every run and a "scan started" email at the start; the ledger write is fail-soft and happens before the email.
- Local alternative: dashboard.py already has an in-app job runner (/api/jobs/<kind>) that can run scans on the user's Mac; the app is a pywebview desktop app + Flask. A local scheduler would avoid GitHub cron drift but only runs while the Mac is on.

## Frontend constraints
- Native ES modules, no build step, no framework; charts.js is a classic script exposing globals; tests are plain Node scripts. No emoji anywhere. Slot ids/requests are scoped per list to avoid stale-response paints. The dashboard has a per-view "Live" auto-refresh and a 5-minute auto-sync (git pull) running app-wide.
- prefers-reduced-motion is NOT currently handled anywhere in dashboard.css.

## Cross-sprint constraints
- SPRINT_PLAN_CHART_MODAL.md (full-screen analysis modal, per-ticker price chart) is planned but NOT approved/built. Its files: ui-helpers.js, shortlist.js, market.js, dashboard.css, charts.js, dashboard.html, router.js. The live chart would also touch market.js/charts.js/dashboard.css/ui-helpers.js.
- User has a large body of UNCOMMITTED work in the tree. position/ holds real account data and must never be read or referenced.
