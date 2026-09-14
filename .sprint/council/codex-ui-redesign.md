Reading additional input from stdin...
OpenAI Codex v0.154.0
--------
[1mworkdir:[0m /Users/badripratti/Desktop/stock-screener
[1mmodel:[0m gpt-5.6-sol
[1mprovider:[0m openai
[1mapproval:[0m never
[1msandbox:[0m workspace-write [workdir, /tmp, $TMPDIR]
[1mreasoning effort:[0m medium
[1mreasoning summaries:[0m none
[1msession id:[0m 01a09dd2-5091-7fa1-8928-8e53daa5cf9e
--------
[36muser[0m

You are participating in an Engineering Council.

Do not modify any files.

Repository:
/Users/badripratti/Desktop/stock-screener

Engineering problem:
The user wants the entire dashboard UI 'completely updated to be more modern,
more easy to use, and more structured.' This is a Flask backend
(dashboard.py) serving a vanilla-JS single-page app (static/js/dashboard.js,
~1000+ lines, no framework, hash-based routing, template-string HTML,
inline styles), static/css/dashboard.css (dark theme only, no design-system
tokens), and templates/dashboard.html. 6 views: Positions, Shortlist, Market,
Backtests, Run Simulation, Full Scan. Chart.js for charts. Packaged as a
native macOS app via py2app + pywebview (mac_app/) — no existing build step
(no bundler, no npm build), dashboard.py serves static files directly.

User goal:
Modern, easy to use, more structured UI. Determine what that concretely means
and how to get there given this app's actual architecture and constraints.

Independently investigate the repository and propose the best approach.

Return:

1. Your understanding of the problem
2. Likely root cause / architectural challenge (why does the current UI feel
   unstructured — be specific, cite files)
3. Relevant files/modules
4. Recommended solution — and explicitly address: does this justify
   introducing a frontend framework + build step (React/Vue/etc), or is a
   design-system-on-vanilla-JS approach better given this is a packaged
   single-user local app with no existing build pipeline?
5. Alternative solutions considered
6. Risks (especially: packaging/build implications for mac_app/, and risk of
   breaking the 90-second live-refresh/job-polling system already built)
7. Edge cases
8. Testing strategy
9. Any assumptions
10. Anything another engineer might easily miss

Do not simply agree with another agent. Use evidence from the repository.

[35m[3mcodex[0m[0m
I’ll inspect the app structure, UI rendering, refresh/polling flows, and macOS packaging without changing files, then turn that evidence into a concrete modernization recommendation.
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "pwd && rg --files -g '"'!*__pycache__*'"' | sed -n '1,240p'"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
/Users/badripratti/Desktop/stock-screener
src/screening/quant_engine.py
src/screening/phase_indicators.py
src/screening/indicators.py
src/screening/__init__.py
src/screening/optimized_batch_processor.py
src/screening/signal_engine.py
src/screening/screener.py
src/screening/top20_ranker.py
src/screening/benchmark.py
src/screening/batch_processor.py
src/notifications/scheduler.py
src/notifications/__init__.py
src/notifications/email_notifier.py
src/notifications/slack_notifier.py
src/data/fetcher.py
src/data/robinhood_positions.py
src/data/quality.py
src/data/git_storage_fetcher.py
src/data/insider_trading.py
src/data/apewisdom_sentiment.py
src/data/fundamentals_fetcher.py
src/data/smart_fetcher.py
src/data/storage.py
src/data/fidelity_positions.py
src/data/reddit_sentiment.py
src/data/__init__.py
src/data/fmp_fetcher.py
src/data/enhanced_fundamentals.py
src/data/universe_fetcher.py
src/data/earnings_risk.py
src/utils/json_safe.py
src/utils/__init__.py
src/agents/fundamentals_auditor.py
src/agents/congress_trades.py
src/agents/shortlist.py
src/agents/catalyst_sentiment.py
src/agents/llm_client.py
src/agents/__init__.py
src/__init__.py
src/analysis/position_manager.py
src/analysis/__init__.py
QUICK_START.md
assets/example-output.png
data/daily_scans/optimized_scan_20260729_222415.txt
data/daily_scans/optimized_scan_20260730_085210.txt
data/daily_scans/optimized_scan_20260729_223432.txt
data/daily_scans/optimized_scan_20260729_223608.txt
data/daily_scans/shortlist_latest.json
data/daily_scans/optimized_scan_20260729_221947.txt
data/daily_scans/optimized_scan_20260730_225116.txt
data/daily_scans/top20_latest.json
data/daily_scans/latest_optimized_scan.txt
data/daily_scans/optimized_scan_20260909_172815.txt
data/catalyst_sentiment/sentiment_20260821_140943.json
data/catalyst_sentiment/sentiment_20260831_203549.json
data/catalyst_sentiment/sentiment_20260902_173310.json
data/catalyst_sentiment/sentiment_20260819_141739.json
data/catalyst_sentiment/sentiment_20260903_172314.json
data/catalyst_sentiment/sentiment_20260826_142311.json
data/catalyst_sentiment/sentiment_20260804_224737.json
data/catalyst_sentiment/sentiment_20260816_141712.json
data/catalyst_sentiment/sentiment_20260907_183406.json
data/catalyst_sentiment/sentiment_20260827_232037.json
data/catalyst_sentiment/sentiment_20260828_232752.json
data/catalyst_sentiment/sentiment_20260825_141712.json
data/catalyst_sentiment/sentiment_20260909_172815.json
data/catalyst_sentiment/sentiment_20260901_174024.json
data/catalyst_sentiment/sentiment_20260904_172630.json
data/catalyst_sentiment/sentiment_20260824_141351.json
data/catalyst_sentiment/sentiment_20260909_171235.json
data/catalyst_sentiment/sentiment_20260911_170840.json
data/catalyst_sentiment/latest.json
data/catalyst_sentiment/sentiment_20260908_173723.json
data/catalyst_sentiment/sentiment_20260910_170652.json
data/catalyst_sentiment/sentiment_20260820_141138.json
run_optimized_scan.py
config.yaml
automated_position_report.py
requirements.txt
LICENSE
run_test.sh
START_HERE.md
CHANGELOG.md
control_panel.py
README.md
data/congress_trades/signals_20260910_170653.json
data/congress_trades/signals_20260909_171236.json
data/congress_trades/signals_20260824_141352.json
data/congress_trades/signals_20260903_172314.json
data/congress_trades/signals_20260816_140315.json
data/congress_trades/signals_20260907_183407.json
data/congress_trades/signals_20260902_173310.json
data/congress_trades/signals_20260821_140944.json
data/congress_trades/signals_20260826_142311.json
data/congress_trades/signals_20260908_173724.json
data/congress_trades/signals_20260827_232037.json
data/congress_trades/signals_20260819_141740.json
data/congress_trades/signals_20260828_232753.json
data/congress_trades/signals_20260911_170841.json
data/congress_trades/signals_20260831_203550.json
dashboard.py
data/congress_trades/signals_20260909_172815.json
data/congress_trades/signals_20260820_141138.json
data/congress_trades/signals_20260825_141713.json
data/congress_trades/signals_20260904_172631.json
data/congress_trades/latest.json
data/congress_trades/signals_20260901_174025.json
CONTRIBUTING.md
position/Portfolio_Positions_Sep-08-2026.csv
run_screen.sh
manage_positions.py
tests/test_quality.py
tests/test_enhanced_fundamentals.py
tests/test_fetcher.py
tests/test_smart_fetcher.py
tests/test_git_storage_fetcher.py
tests/__init__.py
tests/test_email_full.py
tests/test_screener.py
tests/test_quant_engine.py
scripts/backtest_top3.py
scripts/daily_scanner.sh
scripts/run_quant_engine.py
scripts/run_catalyst_sentiment.py
scripts/backtest_top3_monte_carlo.py
scripts/fetch_momentum_status.py
scripts/check_throttling.sh
scripts/fetch_news.py
scripts/run_fundamentals_auditor.py
scripts/check_positions.py
scripts/compare_old_vs_new_weights.py
scripts/component_correlation_analysis.py
scripts/walk_forward_backtest.py
scripts/backtest_critic.py
scripts/fetch_price_history.py
scripts/run_full_market_scan.py
data/fundamentals_audit/audit_20260831_203549.json
data/fundamentals_audit/audit_20260816_141611.json
data/fundamentals_audit/audit_20260821_140943.json
data/fundamentals_audit/audit_20260826_142311.json
data/fundamentals_audit/audit_20260907_183406.json
data/fundamentals_audit/audit_20260816_141010.json
data/fundamentals_audit/audit_20260903_172314.json
data/fundamentals_audit/audit_20260819_141739.json
data/fundamentals_audit/audit_20260902_173310.json
data/fundamentals_audit/audit_20260816_141320.json
data/fundamentals_audit/audit_20260828_232752.json
data/fundamentals_audit/audit_20260804_224647.json
data/fundamentals_audit/audit_20260827_232037.json
data/fundamentals_audit/audit_20260909_172331.json
data/fundamentals_audit/audit_20260820_141138.json
data/fundamentals_audit/audit_20260908_173723.json
data/fundamentals_audit/audit_20260910_170652.json
data/fundamentals_audit/audit_20260911_170840.json
data/fundamentals_audit/audit_20260901_174024.json
data/fundamentals_audit/audit_20260909_171235.json
data/fundamentals_audit/audit_20260824_141351.json
data/fundamentals_audit/audit_20260904_172630.json
data/fundamentals_audit/audit_20260825_141712.json
data/fundamentals_audit/latest.json
mac_app/setup.py
mac_app/README.md
mac_app/main.py
mac_app/assets/AppIcon.icns
docs/REVISED_SMART_CACHING_STRATEGY.md
docs/DEPLOYMENT_CHECKLIST.md
docs/RATE_LIMIT_SOLUTION.md
docs/ENHANCED_FUNDAMENTALS_USAGE.md
docs/ABOUT.md
docs/FULL_MARKET_SCANNER_README.md
docs/FMP_INTEGRATION_STATUS.md
docs/SETUP_CRON_JOB.md
docs/NOTIFICATIONS_COMPLETE.md
docs/FULL_MARKET_IMPLEMENTATION.md
docs/SMART_CACHING_STRATEGY.md
docs/SETUP_FMP.md
docs/README.md
docs/POSITION_AUTOMATION.md
docs/SIMPLE_TRADE_TRACKER.md
docs/QUANT_ENGINE_README.md
docs/ROBINHOOD_SETUP.md
docs/NOTIFICATIONS_SETUP.md
docs/TRADE_TRACKING_SPREADSHEET.md
docs/IMPLEMENTATION_SUMMARY.md
docs/GITHUB_ACTIONS_SETUP.md
docs/SCREENING_MODULE_SUMMARY.md
docs/DETECTING_RATE_LIMITS.md
docs/OPTIMIZED_SCANNER_README.md
docs/FIDELITY_SETUP.md
docs/LOCAL_TEST_RESULTS.md
docs/PROJECT_SUMMARY.md
templates/dashboard.html
static/css/dashboard.css
static/js/dashboard.js
static/js/charts.js
examples/demo.py
examples/screening_demo.py
examples/example_entry_dates.json
examples/quality_check_demo.py
data/fundamentals_cache/AVGO_fundamentals.json
data/fundamentals_cache/JRSH_fundamentals.json
data/fundamentals_cache/EGP_fundamentals.json
data/fundamentals_cache/ICFI_fundamentals.json
data/fundamentals_cache/KTOS_fundamentals.json
data/fundamentals_cache/AOUT_fundamentals.json
data/fundamentals_cache/CAL_fundamentals.json
data/fundamentals_cache/APLS_fundamentals.json
data/fundamentals_cache/TTSH_fundamentals.json
data/fundamentals_cache/NBHC_fundamentals.json
data/fundamentals_cache/DNUT_fundamentals.json
data/fundamentals_cache/DKNG_fundamentals.json
data/fundamentals_cache/NAT_fundamentals.json
data/fundamentals_cache/LOVE_fundamentals.json
data/fundamentals_cache/AOS_fundamentals.json
data/fundamentals_cache/QVCGA_fundamentals.json
data/fundamentals_cache/WSO_fundamentals.json
data/fundamentals_cache/KGS_fundamentals.json
data/fundamentals_cache/SND_fundamentals.json
data/fundamentals_cache/KT_fundamentals.json
data/fundamentals_cache/EEX_fundamentals.json
data/fundamentals_cache/AXS_fundamentals.json
data/fundamentals_cache/GIFI_fundamentals.json
data/fundamentals_cache/UVV_fundamentals.json
data/fundamentals_cache/MIAX_fundamentals.json
data/fundamentals_cache/DELL_fundamentals.json
data/fundamentals_cache/EXLS_fundamentals.json
data/fundamentals_cache/SATS_fundamentals.json
data/fundamentals_cache/BTSG_fundamentals.json
data/fundamentals_cache/HURN_fundamentals.json
data/fundamentals_cache/MIDD_fundamentals.json
data/fundamentals_cache/ENTA_fundamentals.json
data/fundamentals_cache/MTRN_fundamentals.json
data/fundamentals_cache/BBVA_fundamentals.json
data/fundamentals_cache/ASGN_fundamentals.json
data/fundamentals_cache/MTCH_fundamentals.json
data/fundamentals_cache/IONS_fundamentals.json
data/fundamentals_cache/RITM_fundamentals.json
data/fundamentals_cache/ELV_fundamentals.json
data/fundamentals_cache/NBN_fundamentals.json
data/fundamentals_cache/ONB_fundamentals.json

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "wc -l dashboard.py static/js/dashboard.js static/js/charts.js static/css/dashboard.css templates/dashboard.html mac_app/main.py mac_app/setup.py && sed -n '1,240p' templates/dashboard.html && sed -n '1,260p' static/css/dashboard.css"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
     784 dashboard.py
    1156 static/js/dashboard.js
     151 static/js/charts.js
     211 static/css/dashboard.css
      57 templates/dashboard.html
      63 mac_app/main.py
      40 mac_app/setup.py
    2462 total
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stock Screener</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
</head>
<body>

<div class="app">
  <nav class="sidebar">
    <div class="brand">Stock Screener</div>
    <a href="#/positions" class="nav-item" data-view="positions">
      <span class="nav-item-title">Positions</span>
      <span class="nav-item-sub">Your portfolio</span>
    </a>
    <a href="#/shortlist" class="nav-item" data-view="shortlist">
      <span class="nav-item-title">Shortlist</span>
      <span class="nav-item-sub">Today's email picks</span>
    </a>
    <a href="#/market" class="nav-item" data-view="market">
      <span class="nav-item-title">Market</span>
      <span class="nav-item-sub">Full scan, all signals</span>
    </a>
    <a href="#/backtests" class="nav-item" data-view="backtests">
      <span class="nav-item-title">Backtests</span>
      <span class="nav-item-sub">Past performance, not email</span>
    </a>
    <a href="#/run" class="nav-item" data-view="run">
      <span class="nav-item-title">Run Simulation</span>
      <span class="nav-item-sub">Test a strategy</span>
    </a>
    <a href="#/scan" class="nav-item" data-view="scan">
      <span class="nav-item-title">Full Scan</span>
      <span class="nav-item-sub">Trigger a new scan</span>
    </a>
    <div class="sidebar-footer">Not financial advice.</div>
  </nav>

  <main class="main">
    <header class="topbar">
      <h1 id="pageTitle">Positions</h1>
      <div id="pageMeta" class="page-meta"></div>
      <button class="btn" id="syncBtn" style="margin-left:auto" title="git pull to fetch today's emailed picks">Sync latest</button>
    </header>
    <div class="content" id="content"></div>
  </main>
</div>

<div class="toast" id="toast" style="opacity:0"></div>

<script src="{{ url_for('static', filename='js/charts.js') }}"></script>
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
</body>
</html>
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface-2: #21242f;
  --border: #2a2d3a;
  --text: #e4e6eb;
  --muted: #8b8fa3;
  --green: #22c55e;
  --red: #ef4444;
  --yellow: #eab308;
  --blue: #3b82f6;
  --purple: #a855f7;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
a { color: inherit; }

/* --- App shell: sidebar + main --- */
.app { display: flex; min-height: 100vh; }

.sidebar {
  width: 220px; flex-shrink: 0; background: var(--surface);
  border-right: 1px solid var(--border); padding: 20px 0;
  display: flex; flex-direction: column; position: sticky; top: 0; height: 100vh;
}
.brand { font-size: 15px; font-weight: 700; padding: 0 20px 20px; }
.nav-item {
  display: block; padding: 8px 20px;
  color: var(--muted); text-decoration: none;
  border-left: 3px solid transparent; transition: all 0.15s;
}
.nav-item:hover { color: var(--text); background: rgba(255,255,255,0.03); }
.nav-item.active { color: var(--text); background: rgba(59,130,246,0.08); border-left-color: var(--blue); }
.nav-item-title { display: block; font-size: 14px; font-weight: 500; }
.nav-item-sub { display: block; font-size: 10.5px; color: var(--muted); opacity: 0.75; margin-top: 1px; }
.sidebar-footer { margin-top: auto; padding: 16px 20px 0; color: var(--muted); font-size: 11px; }

.main { flex: 1; min-width: 0; }
.topbar {
  background: var(--surface); border-bottom: 1px solid var(--border);
  padding: 18px 32px; display: flex; align-items: baseline; gap: 14px;
}
.topbar h1 { font-size: 19px; font-weight: 700; }
.page-meta { color: var(--muted); font-size: 13px; }
.content { max-width: 1300px; margin: 0 auto; padding: 24px 32px 60px; }

/* --- Buttons --- */
.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px; transition: all 0.15s; }
.btn:hover { border-color: var(--blue); }
.btn.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
.btn.primary:hover { opacity: 0.9; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* --- Layout helpers --- */
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }

.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
.stat-card .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.stat-card .value { font-size: 28px; font-weight: 700; }
.stat-card .sub { color: var(--muted); font-size: 12px; margin-top: 4px; }
.stat-card.green .value { color: var(--green); }
.stat-card.red .value { color: var(--red); }
.stat-card.blue .value { color: var(--blue); }
.stat-card.yellow .value { color: var(--yellow); }
.stat-card.purple .value { color: var(--purple); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 16px; }
.card h2 { font-size: 15px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.card .card-sub { color: var(--muted); font-size: 12px; margin-top: -10px; margin-bottom: 14px; }

.chart-wrap { position: relative; height: 250px; }

/* --- Signal tables (Market view) --- */
.signal-table { width: 100%; border-collapse: collapse; }
.signal-table th { text-align: left; padding: 10px 12px; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
.signal-table td { padding: 12px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: top; }
.signal-table tr:hover { background: rgba(59,130,246,0.04); }

.ticker { font-weight: 700; font-size: 14px; color: var(--blue); }
.score-bar { height: 6px; border-radius: 3px; background: var(--border); overflow: hidden; width: 80px; display: inline-block; vertical-align: middle; margin-left: 6px; }
.score-bar .fill { height: 100%; border-radius: 3px; }
.score-num { font-weight: 600; font-size: 13px; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.badge.good { background: rgba(34,197,94,0.15); color: var(--green); }
.badge.extended { background: rgba(234,179,8,0.15); color: var(--yellow); }
.badge.poor { background: rgba(239,68,68,0.15); color: var(--red); }
.badge.critical { background: rgba(239,68,68,0.25); color: var(--red); }
.badge.high { background: rgba(239,68,68,0.15); color: var(--red); }
.badge.medium { background: rgba(234,179,8,0.15); color: var(--yellow); }
.badge.neutral { background: rgba(255,255,255,0.08); color: var(--muted); }

/* --- Momentum status indicator (hot / stable / basing / avoid) + day streak --- */
.momentum-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 9px; border-radius: 5px; font-size: 11px; font-weight: 700;
  border: 1px solid transparent; white-space: nowrap;
}
.momentum-badge .streak { font-weight: 500; opacity: 0.85; }
.momentum-badge.hot { background: rgba(239,68,68,0.18); color: #ff6b6b; border-color: rgba(239,68,68,0.35); }
.momentum-badge.stable { background: rgba(34,197,94,0.15); color: var(--green); border-color: rgba(34,197,94,0.3); }
.momentum-badge.basing { background: rgba(59,130,246,0.12); color: #7dd3fc; border-color: rgba(59,130,246,0.3); }
.momentum-badge.avoid { background: rgba(0,0,0,0.35); color: #f87171; border-color: rgba(239,68,68,0.4); }

.reasons-list { list-style: none; padding: 0; margin-top: 4px; }
.reasons-list li { font-size: 11px; color: var(--muted); padding: 1px 0; }

.expand-btn { background: none; border: none; color: var(--blue); cursor: pointer; font-size: 11px; padding: 2px 0; }
.expand-btn:hover { text-decoration: underline; }

.trade-link { display: inline-flex; align-items: center; gap: 4px; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; white-space: nowrap; border: 1px solid transparent; }
.trade-link.buy { background: rgba(34,197,94,0.15); color: var(--green); }
.trade-link.buy:hover { background: rgba(34,197,94,0.28); }
.trade-link.sell { background: rgba(239,68,68,0.15); color: var(--red); }
.trade-link.sell:hover { background: rgba(239,68,68,0.28); }

.no-data { text-align: center; padding: 60px 20px; color: var(--muted); }
.no-data h2 { font-size: 18px; margin-bottom: 8px; color: var(--text); }

.banner { background: rgba(234,179,8,0.1); border: 1px solid rgba(234,179,8,0.3); color: var(--yellow); border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 20px; }
.banner a { color: var(--yellow); text-decoration: underline; }

/* "This is what your email sends" / "this is historical, not email" style notes */
.source-note {
  padding: 10px 14px; border-radius: 8px; font-size: 12px; line-height: 1.5;
  margin-bottom: 18px; border: 1px solid;
}
.source-note.email { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.3); color: var(--purple); }
.source-note.historical { background: rgba(59,130,246,0.08); border-color: rgba(59,130,246,0.3); color: var(--blue); }
.source-note b { font-weight: 700; }
.source-note a { text-decoration: underline; }

.regime-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.regime-badge.risk-on { background: rgba(34,197,94,0.15); color: var(--green); }
.regime-badge.risk-off { background: rgba(239,68,68,0.15); color: var(--red); }
.regime-badge.transitional { background: rgba(234,179,8,0.15); color: var(--yellow); }

.scan-select { background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 6px; font-size: 13px; }

/* --- Market view: news sections --- */
.news-ticker-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
.news-ticker-block { min-width: 0; }
.news-headline { display: block; padding: 7px 0; border-bottom: 1px solid var(--border); text-decoration: none; }
.news-headline:last-child { border-bottom: none; }
.news-headline-title { font-size: 12.5px; color: var(--text); line-height: 1.4; }
.news-headline:hover .news-headline-title { color: var(--blue); }
.news-headline-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }

/* --- Shortlist cards --- */
.shortlist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.pick-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px; position: relative; }
.pick-card.backfilled { border-color: rgba(234,179,8,0.35); }
.pick-rank { position: absolute; top: 14px; right: 16px; color: var(--muted); font-size: 12px; font-weight: 700; }
.pick-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
.pick-header .ticker { font-size: 20px; }
.pick-scores { display: flex; gap: 16px; margin-bottom: 12px; }
.pick-scores .score-block .label { color: var(--muted); font-size: 10px; text-transform: uppercase; }
.pick-scores .score-block .value { font-size: 16px; font-weight: 700; }
.pick-badges { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.agent-badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600; width: fit-content; }
.agent-badge.pos { background: rgba(34,197,94,0.15); color: var(--green); }
.agent-badge.neg { background: rgba(239,68,68,0.15); color: var(--red); }
.agent-badge.neu { background: rgba(255,255,255,0.06); color: var(--muted); }
.agent-badge-sub { font-size: 11px; color: var(--muted); margin: -3px 0 3px 2px; }
.backfill-note { font-size: 11px; color: var(--yellow); margin-bottom: 10px; }

.chart-toggle-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; flex-shrink: 0;
  background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px;
  color: var(--text); cursor: pointer; padding: 0;
}
.chart-toggle-btn svg { width: 17px; height: 17px; }
.chart-toggle-btn:hover { border-color: var(--blue); color: var(--blue); background: rgba(59,130,246,0.1); }
.chart-toggle-btn.active { border-color: var(--blue); background: rgba(59,130,246,0.12); color: var(--blue); }
.position-chart-wrap { height: 180px; margin-top: 14px; }

/* --- "Live" auto-refresh indicator --- */
.live-badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 600; color: var(--green); margin-left: 10px;
}
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: live-pulse 2s ease-in-out infinite; }
@keyframes live-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }

/* --- Run Simulation panels --- */
.sim-card .sim-desc { color: var(--muted); font-size: 12px; margin-bottom: 14px; }
.sim-params { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
.sim-params label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--muted); }
.sim-params input {
  background: var(--surface-2); border: 1px solid var(--border); color: var(--text);
  padding: 6px 8px; border-radius: 6px; font-size: 13px; width: 90px;
}
.job-output {
  background: #0a0b10; border: 1px solid var(--border); border-radius: 8px; padding: 12px;
  font-family: 'SF Mono', Menlo, monospace; font-size: 11px; color: var(--muted);
  max-height: 220px; overflow-y: auto; white-space: pre-wrap; margin-top: 12px; display: none;
}
.status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-left: 10px; }
.status-pill.idle { background: rgba(255,255,255,0.06); color: var(--muted); }
.status-pill.running { background: rgba(59,130,246,0.15); color: var(--blue); }
.status-pill.success { background: rgba(34,197,94,0.15); color: var(--green); }
.status-pill.error { background: rgba(239,68,68,0.15); color: var(--red); }

.spinner { display: inline-block; width: 10px; height: 10px; border: 2px solid rgba(255,255,255,0.2); border-top-color: currentColor; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.toast { position: fixed; bottom: 24px; right: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; font-size: 13px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); z-index: 100; transition: opacity 0.3s; max-width: 360px; }

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '200,280p' static/css/dashboard.css; nl -ba static/js/dashboard.js | sed -n '1,260p'; nl -ba static/js/dashboard.js | sed -n '260,620p'"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
  max-height: 220px; overflow-y: auto; white-space: pre-wrap; margin-top: 12px; display: none;
}
.status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-left: 10px; }
.status-pill.idle { background: rgba(255,255,255,0.06); color: var(--muted); }
.status-pill.running { background: rgba(59,130,246,0.15); color: var(--blue); }
.status-pill.success { background: rgba(34,197,94,0.15); color: var(--green); }
.status-pill.error { background: rgba(239,68,68,0.15); color: var(--red); }

.spinner { display: inline-block; width: 10px; height: 10px; border: 2px solid rgba(255,255,255,0.2); border-top-color: currentColor; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.toast { position: fixed; bottom: 24px; right: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; font-size: 13px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); z-index: 100; transition: opacity 0.3s; max-width: 360px; }
     1	// Stock Screener dashboard — vanilla JS single-page app. Hash-based routing
     2	// (no router library), fetch() for data, Chart.js (via charts.js) for charts.
     3	
     4	const content = document.getElementById('content');
     5	const pageTitle = document.getElementById('pageTitle');
     6	const pageMeta = document.getElementById('pageMeta');
     7	
     8	const VIEWS = {
     9	  positions: { title: 'Positions', render: renderPositionsView },
    10	  shortlist: { title: 'Shortlist', render: renderShortlistView },
    11	  market: { title: 'Market', render: renderMarketView },
    12	  backtests: { title: 'Backtests', render: renderBacktestsView },
    13	  run: { title: 'Run Simulation', render: renderRunView },
    14	  scan: { title: 'Full Scan', render: renderScanView },
    15	};
    16	
    17	// Tracks which view is actually on screen right now. View render functions
    18	// are async — if you navigate away while one is still awaiting its first
    19	// fetch, that stale call resolves later and, without this check, would paint
    20	// its (now-irrelevant) content over whatever view you've since navigated to.
    21	// Every render function checks `_currentView === '<its own name>'` right
    22	// after each await, before touching pageMeta/content, and bails out silently
    23	// if it's lost the race.
    24	let _currentView = null;
    25	
    26	function route() {
    27	  _stopLive();
    28	  const hash = (location.hash || '#/positions').replace('#/', '');
    29	  const view = VIEWS[hash] ? hash : 'positions';
    30	  _currentView = view;
    31	  document.querySelectorAll('.nav-item').forEach(a => {
    32	    a.classList.toggle('active', a.dataset.view === view);
    33	  });
    34	  pageTitle.textContent = VIEWS[view].title;
    35	  pageMeta.innerHTML = '';
    36	  content.innerHTML = '<div class="no-data"><span class="spinner"></span> Loading…</div>';
    37	  VIEWS[view].render();
    38	}
    39	window.addEventListener('hashchange', route);
    40	
    41	// --- "Live" auto-refresh -------------------------------------------------
    42	// This is a local, single-user Flask app with no push/streaming layer, so
    43	// "live" here means: while a view that supports it is open, quietly re-pull
    44	// fresh data on a timer and patch it into the DOM. Stopped on every route
    45	// change so a background view never keeps polling once you've navigated away.
    46	
    47	const LIVE_INTERVAL_MS = 90 * 1000; // 90 seconds — cheap yfinance-only pulls, no LLM cost
    48	let _liveTimer = null;
    49	
    50	function _stopLive() {
    51	  if (_liveTimer) { clearInterval(_liveTimer); _liveTimer = null; }
    52	}
    53	function _startLive(fn) {
    54	  _stopLive();
    55	  _liveTimer = setInterval(fn, LIVE_INTERVAL_MS);
    56	}
    57	function liveBadgeHTML() {
    58	  return '<span class="live-badge"><span class="live-dot"></span>Live — updates every 90s</span>';
    59	}
    60	
    61	// If a live-refresh tick's job hasn't finished by the time the next tick
    62	// fires (e.g. yfinance is slow), skip that tick instead of stacking another
    63	// overlapping job on top — the next one will pick up fresh data anyway.
    64	const _liveInFlight = new Set();
    65	async function _liveGuarded(key, fn) {
    66	  if (_liveInFlight.has(key)) return;
    67	  _liveInFlight.add(key);
    68	  try {
    69	    await fn();
    70	  } finally {
    71	    _liveInFlight.delete(key);
    72	  }
    73	}
    74	
    75	// Chart toggle buttons (Positions + Shortlist share this). Open/closed state
    76	// persists in this module-level set across re-renders and silent refreshes,
    77	// keyed by the canvas element id, so a chart you had open stays open through
    78	// a live refresh instead of collapsing every cycle.
    79	const CHART_ICON = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 6"/><polyline points="15 6 21 6 21 12"/></svg>';
    80	const _openCharts = new Set();
    81	
    82	function chartToggleButtonHTML(chartId) {
    83	  return `<button class="chart-toggle-btn" data-chart-id="${chartId}" title="Price history">${CHART_ICON}</button>`;
    84	}
    85	
    86	// getSeries(ticker) -> {history, entry, stop} | null. Attaches click handlers
    87	// (call once per DOM render) and immediately re-opens any chart that was
    88	// already open before this render (e.g. across a live refresh).
    89	function wireChartToggles(container, getSeries, idPrefix) {
    90	  container.querySelectorAll('.chart-toggle-btn').forEach(btn => {
    91	    const chartId = btn.dataset.chartId;
    92	    const wrap = document.getElementById(`${chartId}-wrap`);
    93	    if (!wrap) return;
    94	    const ticker = chartId.slice(idPrefix.length);
    95	
    96	    if (_openCharts.has(chartId)) {
    97	      wrap.style.display = 'block';
    98	      btn.classList.add('active');
    99	      const series = getSeries(ticker);
   100	      if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
   101	    }
   102	
   103	    btn.addEventListener('click', () => {
   104	      const nowVisible = wrap.style.display !== 'block';
   105	      wrap.style.display = nowVisible ? 'block' : 'none';
   106	      btn.classList.toggle('active', nowVisible);
   107	      if (nowVisible) {
   108	        _openCharts.add(chartId);
   109	        const series = getSeries(ticker);
   110	        if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
   111	      } else {
   112	        _openCharts.delete(chartId);
   113	      }
   114	    });
   115	  });
   116	}
   117	
   118	// For a silent live refresh where the cards themselves aren't re-rendered
   119	// (Shortlist) — just repaint whichever charts are currently open with fresh data.
   120	function refreshOpenCharts(getSeries, idPrefix) {
   121	  _openCharts.forEach(chartId => {
   122	    if (!chartId.startsWith(idPrefix)) return;
   123	    if (!document.getElementById(`${chartId}-wrap`)) return; // stale id from a different view
   124	    const ticker = chartId.slice(idPrefix.length);
   125	    const series = getSeries(ticker);
   126	    if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
   127	  });
   128	}
   129	
   130	// --- Momentum status (hot / stable / basing / avoid) + day-streak --------
   131	// Shared across Shortlist, Positions, and Market — same classification the
   132	// screening engine itself uses (Phase + distance from the 50-day average),
   133	// so a badge here always means the same thing it means in a scan report.
   134	
   135	const MOMENTUM_LABELS = { hot: 'HOT', stable: 'STABLE', basing: 'BASING', avoid: 'AVOID' };
   136	
   137	function momentumBadgeHTML(entry) {
   138	  if (!entry || !entry.status) return '';
   139	  const label = MOMENTUM_LABELS[entry.status] || entry.status.toUpperCase();
   140	  const dayWord = entry.days === 1 ? 'day' : 'days';
   141	  return `<span class="momentum-badge ${entry.status}" title="${entry.label} — ${entry.days} ${dayWord}">${label}<span class="streak">Day ${entry.days}</span></span>`;
   142	}
   143	
   144	// Injects a badge into a per-ticker slot element (id="momentum-slot-<ticker>")
   145	// once the classification job completes. Call after slots exist in the DOM.
   146	async function loadMomentumStatus(tickers, group, onLoaded) {
   147	  if (!tickers.length) return;
   148	  await startJob('momentum-status', { tickers, group }, async (st) => {
   149	    if (st.status !== 'success') return;
   150	    const data = await fetchJSON(`/api/momentum-status/${group}`);
   151	    onLoaded(data.status || {});
   152	  });
   153	}
   154	
   155	function paintMomentumSlots(tickers, statusMap) {
   156	  tickers.forEach(ticker => {
   157	    const slot = document.getElementById(`momentum-slot-${ticker}`);
   158	    if (slot && statusMap[ticker]) slot.innerHTML = momentumBadgeHTML(statusMap[ticker]);
   159	  });
   160	}
   161	
   162	// --- Shared helpers -----------------------------------------------------
   163	
   164	async function fetchJSON(url, opts) {
   165	  const res = await fetch(url, opts);
   166	  return res.json();
   167	}
   168	
   169	function showToast(msg) {
   170	  const t = document.getElementById('toast');
   171	  t.textContent = msg;
   172	  t.style.opacity = '1';
   173	  clearTimeout(t._timer);
   174	  t._timer = setTimeout(() => { t.style.opacity = '0'; }, 5000);
   175	}
   176	
   177	function redditCell(count) {
   178	  if (count == null) return '<span style="color:var(--muted)">-</span>';
   179	  if (count === 0) return '<span style="color:var(--muted)">0</span>';
   180	  const hot = count >= 10;
   181	  return `<span style="color:${hot ? 'var(--yellow)' : 'var(--text)'};font-weight:${hot ? 700 : 400}">${count}</span>`;
   182	}
   183	
   184	function cleanEmoji(text) {
   185	  return (text || '').replace(/[🟢🔴🟡⭐⚠✓🚨]/g, '').trim();
   186	}
   187	
   188	// Escapes free text before it's interpolated into innerHTML. Needed anywhere
   189	// the string didn't originate from this codebase — news headlines/publishers
   190	// (raw Yahoo Finance feed data), and LLM-generated summaries/flags (ultimately
   191	// derived from external filings/press) — a crafted string containing HTML
   192	// could otherwise execute JS in the dashboard's own origin, which has several
   193	// unauthenticated routes (sync, scan, positions upload).
   194	function escapeHtml(text) {
   195	  const div = document.createElement('div');
   196	  div.textContent = text == null ? '' : String(text);
   197	  return div.innerHTML;
   198	}
   199	
   200	// Only allow http(s) URLs as link targets — a "javascript:" (or other
   201	// executable) scheme in externally-sourced data (e.g. a news item's URL)
   202	// would otherwise run when clicked, same class of risk as the innerHTML issue.
   203	function safeHref(url) {
   204	  try {
   205	    const parsed = new URL(url, location.href);
   206	    return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '#';
   207	  } catch {
   208	    return '#';
   209	  }
   210	}
   211	
   212	function toggleReasons(btn) {
   213	  const extra = btn.previousElementSibling;
   214	  if (extra.style.display === 'none') {
   215	    extra.style.display = '';
   216	    btn.textContent = 'less';
   217	  } else {
   218	    extra.style.display = 'none';
   219	  }
   220	}
   221	
   222	function fidelityLink(ticker, label, cls) {
   223	  return `<a class="trade-link ${cls}" href="https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol=${ticker}" target="_blank" rel="noopener">${label} ↗</a>`;
   224	}
   225	
   226	// Agent badges — same color logic as src/notifications/email_notifier.py
   227	// (_catalyst_badge_html / _congress_badge_html / _fundamentals_flags_html) so
   228	// the dashboard and the email read consistently.
   229	
   230	function catalystBadgeHTML(sentiment) {
   231	  if (!sentiment) return '';
   232	  const score = sentiment.catalyst_score || 0;
   233	  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
   234	  const ctype = (sentiment.catalyst_type || 'other').replace(/_/g, ' ');
   235	  const sign = score > 0 ? '+' : '';
   236	  return `<div><span class="agent-badge ${cls}">Catalyst ${sign}${score} — ${escapeHtml(ctype)}</span>
   237	    <div class="agent-badge-sub">${escapeHtml(sentiment.summary)}</div></div>`;
   238	}
   239	
   240	function congressBadgeHTML(signal) {
   241	  if (!signal || !signal.has_data) return '';
   242	  const score = signal.score || 0;
   243	  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
   244	  const sign = score > 0 ? '+' : '';
   245	  return `<div><span class="agent-badge ${cls}">Congress ${sign}${score.toFixed(1)}</span>
   246	    <div class="agent-badge-sub">${escapeHtml(signal.summary)}</div></div>`;
   247	}
   248	
   249	function fundamentalsFlagsHTML(audit) {
   250	  if (!audit) return '';
   251	  const red = audit.red_flags || [];
   252	  const green = audit.green_flags || [];
   253	  let html = '';
   254	  if (red.length) {
   255	    const more = red.length > 1 ? ` (+${red.length - 1} more)` : '';
   256	    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${escapeHtml(red[0].flag)}${more}</div>`;
   257	  }
   258	  if (green.length) {
   259	    const more = green.length > 1 ? ` (+${green.length - 1} more)` : '';
   260	    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
   260	    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
   261	  }
   262	  return html;
   263	}
   264	
   265	// --- Background job runner (Run Simulation / Full Scan views) ----------
   266	
   267	// Resolves only once the job reaches a terminal state (success/error/stopped),
   268	// not right after it starts — every caller does `await startJob(...)` expecting
   269	// that to mean "the job is done," and several (via _liveGuarded) depend on it
   270	// to know when it's safe to start the next refresh cycle. It used to resolve
   271	// as soon as the initial POST came back, which silently defeated that guard.
   272	async function startJob(kind, body, onUpdate) {
   273	  const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
   274	    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
   275	  });
   276	  return new Promise((resolve) => {
   277	    const poll = async () => {
   278	      const st = await fetchJSON(`/api/jobs/${job_id}`);
   279	      onUpdate(st);
   280	      if (st.status === 'running' || st.status === 'queued') {
   281	        setTimeout(poll, 1500);
   282	      } else {
   283	        resolve(job_id);
   284	      }
   285	    };
   286	    poll();
   287	  });
   288	}
   289	
   290	function jobCardHTML(id, title, desc, paramsHTML) {
   291	  return `
   292	    <div class="card sim-card">
   293	      <h2>${title} <span class="status-pill idle" id="${id}-pill">idle</span></h2>
   294	      <div class="sim-desc">${desc}</div>
   295	      <div class="sim-params">${paramsHTML}</div>
   296	      <button class="btn primary" id="${id}-run">Run</button>
   297	      <div class="job-output" id="${id}-output"></div>
   298	      <div id="${id}-result" style="margin-top:12px"></div>
   299	    </div>`;
   300	}
   301	
   302	// Job cards (Run Simulation, Full Scan) kick off long-running background jobs
   303	// (a real detached subprocess on the server — it was never actually stopped by
   304	// navigating away). What used to break on navigation was the UI side: the
   305	// click handler closed over the specific DOM nodes present at click-time, so
   306	// leaving the page and coming back re-rendered a fresh "idle" card with no
   307	// memory of the job still running (or just finished) underneath it. _activeJobs
   308	// tracks job_id per card id at module scope — outside any view's DOM — so it
   309	// survives a route change, and wireJobCard reconnects to it on every render.
   310	const _activeJobs = {}; // cardId -> most recent job_id for that card (running OR finished), survives across renders
   311	const _watchingJobIds = {}; // cardId -> job_id an active setTimeout poll loop is already chasing
   312	
   313	function watchJob(id, jobId, onResult) {
   314	  _activeJobs[id] = jobId;
   315	  // Reconnecting to a job you're already polling (e.g. navigating back and
   316	  // forth while it runs) would otherwise stack up a duplicate setTimeout
   317	  // chain each time — same end state, just wasted polling. The next tick of
   318	  // the existing loop repaints the freshly-mounted card within ~1.5s anyway.
   319	  if (_watchingJobIds[id] === jobId) return;
   320	  _watchingJobIds[id] = jobId;
   321	
   322	  const poll = async () => {
   323	    const st = await fetchJSON(`/api/jobs/${jobId}`);
   324	    if (st.error) {
   325	      // The server prunes finished jobs after a while — if you reconnect to
   326	      // one long after it ended, just drop back to idle instead of crashing
   327	      // on the missing `output` field.
   328	      if (_activeJobs[id] === jobId) delete _activeJobs[id];
   329	      if (_watchingJobIds[id] === jobId) delete _watchingJobIds[id];
   330	      return;
   331	    }
   332	    const btn = document.getElementById(`${id}-run`);
   333	    const pill = document.getElementById(`${id}-pill`);
   334	    const out = document.getElementById(`${id}-output`);
   335	    // Paint only if this card is actually on screen right now — if you've
   336	    // navigated elsewhere these are null and we just skip rendering. The job
   337	    // itself keeps running server-side regardless; we'll catch up next poll,
   338	    // or immediately via this same function when you navigate back.
   339	    if (btn && pill && out) {
   340	      out.style.display = 'block';
   341	      out.textContent = st.output.join('\n');
   342	      out.scrollTop = out.scrollHeight;
   343	      if (st.status === 'running' || st.status === 'queued') {
   344	        btn.disabled = true;
   345	        pill.className = 'status-pill running';
   346	        pill.innerHTML = '<span class="spinner"></span> running';
   347	      } else {
   348	        btn.disabled = false;
   349	        pill.className = `status-pill ${st.status}`;
   350	        pill.textContent = st.status;
   351	      }
   352	    }
   353	
   354	    if (st.status === 'running' || st.status === 'queued') {
   355	      setTimeout(poll, 1500);
   356	    } else {
   357	      // Deliberately NOT clearing _activeJobs[id] here — it's what lets
   358	      // wireJobCard reconnect and show the finished result if the job
   359	      // completed while you were on a different page (the common case for
   360	      // anything that finishes in under a minute or two). It's only replaced
   361	      // when this card starts a new job, never otherwise.
   362	      if (_watchingJobIds[id] === jobId) delete _watchingJobIds[id];
   363	      if (st.status === 'success' && onResult) {
   364	        const resultEl = document.getElementById(`${id}-result`);
   365	        if (resultEl) await onResult(st, resultEl);
   366	      }
   367	    }
   368	  };
   369	  poll();
   370	}
   371	
   372	function wireJobCard(id, kind, getParams, onResult) {
   373	  // Reconnect to a job started before navigating away and back.
   374	  if (_activeJobs[id]) {
   375	    watchJob(id, _activeJobs[id], onResult);
   376	  }
   377	
   378	  document.getElementById(`${id}-run`).addEventListener('click', async () => {
   379	    const btn = document.getElementById(`${id}-run`);
   380	    const pill = document.getElementById(`${id}-pill`);
   381	    const out = document.getElementById(`${id}-output`);
   382	    const resultEl = document.getElementById(`${id}-result`);
   383	    // Disable synchronously, before the POST round-trip, so a rapid double
   384	    // click can't start two overlapping jobs for the same card.
   385	    btn.disabled = true;
   386	    pill.className = 'status-pill running';
   387	    pill.innerHTML = '<span class="spinner"></span> running';
   388	    out.style.display = 'block';
   389	    out.textContent = '';
   390	    if (resultEl) resultEl.innerHTML = '';
   391	
   392	    const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
   393	      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(getParams()),
   394	    });
   395	    watchJob(id, job_id, onResult);
   396	  });
   397	}
   398	
   399	// --- View: Shortlist (default landing view) -----------------------------
   400	
   401	async function renderShortlistView() {
   402	  const data = await fetchJSON('/api/shortlist');
   403	  if (_currentView !== 'shortlist') return; // navigated away before this resolved
   404	  if (!data.shortlist || data.shortlist.length === 0) {
   405	    const top20 = await fetchJSON('/api/top20');
   406	    if (_currentView !== 'shortlist') return;
   407	    content.innerHTML = `
   408	      <div class="banner">
   409	        No filtered shortlist yet — run a scan with AI agents enabled from the
   410	        <a href="#/scan">Full Scan</a> page to get a Top 5 filtered by fundamentals,
   411	        news sentiment, and congressional trading. Showing the raw Top 20 pool below instead.
   412	      </div>
   413	      ${renderTop20Table(top20.top20 || [])}
   414	    `;
   415	    const fallbackTickers = (top20.top20 || []).map(s => s.ticker);
   416	    loadMomentumStatus(fallbackTickers, 'shortlist-fallback', (statusMap) => paintMomentumSlots(fallbackTickers, statusMap));
   417	    return;
   418	  }
   419	  pageMeta.textContent = data.generated ? `Generated ${new Date(data.generated).toLocaleString()}` : '';
   420	
   421	  const tickers = data.shortlist.map(s => s.ticker);
   422	
   423	  const cards = data.shortlist.map((s, i) => {
   424	    const badges = [
   425	      catalystBadgeHTML(data.catalyst_sentiments[s.ticker]),
   426	      congressBadgeHTML(data.congress_signals[s.ticker]),
   427	      fundamentalsFlagsHTML(data.fundamentals_audits[s.ticker]),
   428	    ].filter(Boolean).join('');
   429	    const backfillNote = !s.passed_filters
   430	      ? `<div class="backfill-note">Backfilled — didn't clear filters: ${(s.drop_reasons || []).join('; ') || 'below filter bar'}</div>`
   431	      : '';
   432	    const chartId = `short-chart-${s.ticker}`;
   433	    return `
   434	      <div class="pick-card ${!s.passed_filters ? 'backfilled' : ''}">
   435	        <div class="pick-rank">#${i + 1}</div>
   436	        <div class="pick-header">
   437	          <span class="ticker">${s.ticker}</span>
   438	          <span id="${chartId}-slot"></span>
   439	        </div>
   440	        <div class="pick-scores">
   441	          <div class="score-block"><div class="label">Composite</div><div class="value">${s.composite_score ?? '-'}</div></div>
   442	          <div class="score-block"><div class="label">Base Score</div><div class="value">${s.combined_score ?? s.score ?? '-'}</div></div>
   443	        </div>
   444	        <div style="margin-bottom:10px"><span id="momentum-slot-${s.ticker}"></span></div>
   445	        ${backfillNote}
   446	        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
   447	        ${fidelityLink(s.ticker, 'Buy on Fidelity', 'buy')}
   448	        <div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
   449	      </div>`;
   450	  }).join('');
   451	
   452	  content.innerHTML = `
   453	    <div class="source-note email">
   454	      <b>This is what your daily email sends.</b> Same 5 picks, same links — the email is just a snapshot of this page.
   455	    </div>
   456	    <div class="shortlist-grid">${cards}</div>
   457	    <div id="shortlistNews" style="margin-top:24px"></div>`;
   458	
   459	  loadShortlistCharts(tickers);
   460	  loadShortlistNews(tickers);
   461	  loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap));
   462	  _startLive(() => {
   463	    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
   464	    _liveGuarded('shortlist-news', () => loadShortlistNews(tickers, true));
   465	    _liveGuarded('shortlist-momentum', () => loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap)));
   466	  });
   467	}
   468	
   469	let _shortlistPrices = {};
   470	let _marketTop20Tickers = [];
   471	
   472	function _shortlistSeries(ticker) {
   473	  const h = _shortlistPrices[ticker];
   474	  return h && h.length ? { history: h, entry: null, stop: null } : null;
   475	}
   476	
   477	async function loadShortlistCharts(tickers, silent) {
   478	  if (!tickers.length) return;
   479	  await startJob('price-history', { tickers, group: 'shortlist' }, async (st) => {
   480	    if (st.status !== 'success') return;
   481	    const data = await fetchJSON('/api/price-history/shortlist');
   482	    _shortlistPrices = data.prices || {};
   483	
   484	    if (!silent) {
   485	      // First load: drop a chart button into each card that actually has history.
   486	      tickers.forEach(ticker => {
   487	        const slot = document.getElementById(`short-chart-${ticker}-slot`);
   488	        if (slot && _shortlistPrices[ticker] && _shortlistPrices[ticker].length) {
   489	          slot.innerHTML = chartToggleButtonHTML(`short-chart-${ticker}`);
   490	        }
   491	      });
   492	      wireChartToggles(content, _shortlistSeries, 'short-chart-');
   493	    } else {
   494	      // Live refresh: buttons already exist — just repaint whichever are open.
   495	      refreshOpenCharts(_shortlistSeries, 'short-chart-');
   496	    }
   497	  });
   498	}
   499	
   500	async function loadShortlistNews(tickers, silent) {
   501	  const el = document.getElementById('shortlistNews');
   502	  if (!el) return;
   503	  if (!silent) {
   504	    el.innerHTML = _newsSectionHTML('shortlist', 'News on your shortlist', 'loading');
   505	  }
   506	  await _loadNewsGroup('shortlist', tickers, 'No shortlist yet.', silent);
   507	}
   508	
   509	function renderTop20Table(top20) {
   510	  if (!top20.length) return '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan from the Full Scan page.</p></div>';
   511	  const rows = top20.map((s, i) => {
   512	    const links = (s.why_links || []).slice(0, 3).map(l =>
   513	      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
   514	    ).join('');
   515	    return `<tr>
   516	      <td>#${i + 1}</td>
   517	      <td><span class="ticker">${s.ticker}</span></td>
   518	      <td><span class="score-num">${s.combined_score ?? s.score ?? '-'}</span></td>
   519	      <td><span id="momentum-slot-${s.ticker}"></span></td>
   520	      <td>${redditCell(s.reddit_mentions_24h)}</td>
   521	      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
   522	      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
   523	    </tr>`;
   524	  }).join('');
   525	  return `
   526	    <div class="card">
   527	      <h2>Top 20 — Combined Pool</h2>
   528	      <div style="overflow-x:auto"><table class="signal-table">
   529	        <thead><tr><th>#</th><th>Ticker</th><th>Combined Score</th><th>Momentum</th><th>Reddit</th><th>Why it's moving</th><th>Trade</th></tr></thead>
   530	        <tbody>${rows}</tbody>
   531	      </table></div>
   532	    </div>`;
   533	}
   534	
   535	// --- View: Market (today's Top 20 / Buy / Sell / regime) ---------------
   536	
   537	async function renderMarketView() {
   538	  const scans = await fetchJSON('/api/scans');
   539	  if (_currentView !== 'market') return; // navigated away before this resolved
   540	  if (!scans.length) {
   541	    content.innerHTML = '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan to get started.</p></div>';
   542	    return;
   543	  }
   544	  content.innerHTML = `
   545	    <div class="source-note email">
   546	      <b>This is the full pool your email's picks are drawn from.</b> Buy/Sell Signals and the Top 20 table
   547	      here are the same lists that get emailed (capped at 15 rows there; everything's shown here) — the
   548	      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
   549	    </div>
   550	    <div style="margin-bottom:16px">
   551	      <select class="scan-select" id="scanSelect"></select>
   552	    </div>
   553	    <div id="marketBody"></div>
   554	    <div id="newsSections" style="margin-top:24px"></div>`;
   555	  const sel = document.getElementById('scanSelect');
   556	  scans.forEach(s => {
   557	    const opt = document.createElement('option');
   558	    opt.value = s.path;
   559	    opt.textContent = s.date.replace('_', ' ');
   560	    sel.appendChild(opt);
   561	  });
   562	  sel.addEventListener('change', () => loadMarketScan(sel.value));
   563	  loadMarketScan(scans[0].path);
   564	  loadMarketNews();
   565	  _startLive(() => {
   566	    _liveGuarded('market-news', () => loadMarketNews(true));
   567	    _liveGuarded('market-momentum', () => loadMomentumStatus(
   568	      _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
   569	    ));
   570	  });
   571	}
   572	
   573	async function loadMarketNews(silent) {
   574	  const el = document.getElementById('newsSections');
   575	  if (!el) return; // navigated away before this resolved
   576	  if (!silent) {
   577	    el.innerHTML = _newsSectionHTML('positions', 'News on your positions', 'loading') +
   578	                    _newsSectionHTML('buy', "News on what the scanner's telling you to buy", 'loading');
   579	  }
   580	
   581	  const [positionsData, top20Data] = await Promise.all([
   582	    fetchJSON('/api/positions'), fetchJSON('/api/top20'),
   583	  ]);
   584	  const positionTickers = (positionsData.position_analyses || []).map(a => a.ticker);
   585	  const buyTickers = (top20Data.top20 || []).slice(0, 8).map(s => s.ticker);
   586	
   587	  await Promise.all([
   588	    _loadNewsGroup('positions', positionTickers, 'Upload your positions in the Positions tab to see news for them here.', silent),
   589	    _loadNewsGroup('buy', buyTickers, 'No Top 20 pool yet — run a scan from the Full Scan tab first.', silent),
   590	  ]);
   591	}
   592	
   593	function _newsSectionHTML(group, title, bodyHTML) {
   594	  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
   595	}
   596	
   597	async function _loadNewsGroup(group, tickers, emptyMsg, silent) {
   598	  const bodyEl = document.getElementById(`news-${group}-body`);
   599	  if (!bodyEl) return; // navigated away before this resolved
   600	  if (!tickers.length) {
   601	    bodyEl.innerHTML = `<div style="color:var(--muted);font-size:13px">${emptyMsg}</div>`;
   602	    return;
   603	  }
   604	  if (!silent) {
   605	    bodyEl.innerHTML = '<div style="color:var(--muted);font-size:13px"><span class="spinner"></span> Fetching real headlines…</div>';
   606	  }
   607	
   608	  await startJob('news', { tickers, group }, async (st) => {
   609	    const el = document.getElementById(`news-${group}-body`);
   610	    if (!el) return; // navigated away mid-job
   611	    if (st.status === 'success') {
   612	      const data = await fetchJSON(`/api/news/${group}`);
   613	      el.innerHTML = _renderNewsGroupHTML(data.news || {});
   614	    } else if (!silent && (st.status === 'error' || st.status === 'stopped')) {
   615	      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
   616	    }
   617	  });
   618	}
   619	
   620	function _renderNewsGroupHTML(newsByTicker) {

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba static/js/dashboard.js | sed -n '620,1160p'; nl -ba static/js/charts.js | sed -n '1,190p'"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
   620	function _renderNewsGroupHTML(newsByTicker) {
   621	  const tickers = Object.keys(newsByTicker);
   622	  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
   623	  return `<div class="news-ticker-grid">${tickers.map(ticker => {
   624	    const items = newsByTicker[ticker] || [];
   625	    const list = items.length
   626	      ? items.map(h => `
   627	          <a href="${safeHref(h.url)}" target="_blank" rel="noopener" class="news-headline">
   628	            <div class="news-headline-title">${escapeHtml(h.title)}</div>
   629	            <div class="news-headline-meta">${escapeHtml(h.publisher || 'Unknown source')}${h.pub_date ? ' · ' + escapeHtml(new Date(h.pub_date).toLocaleDateString()) : ''}</div>
   630	          </a>`).join('')
   631	      : '<div style="color:var(--muted);font-size:12px">No recent headlines.</div>';
   632	    return `<div class="news-ticker-block"><div class="ticker" style="margin-bottom:6px">${escapeHtml(ticker)}</div>${list}</div>`;
   633	  }).join('')}</div>`;
   634	}
   635	
   636	async function loadMarketScan(path) {
   637	  const [scan, top20] = await Promise.all([
   638	    fetchJSON('/api/scan?path=' + encodeURIComponent(path)),
   639	    fetchJSON('/api/top20'),
   640	  ]);
   641	  if (_currentView !== 'market') return; // navigated away before this resolved
   642	  if (scan.error) {
   643	    document.getElementById('marketBody').innerHTML = '<div class="no-data"><h2>No scan data</h2></div>';
   644	    return;
   645	  }
   646	  pageMeta.textContent = `${scan.scan_date} · ${scan.stats.analyzed || '?'} analyzed · ${scan.regime}`;
   647	
   648	  const buyCount = scan.stats.buy_count ?? scan.buy_signals.length;
   649	  const sellCount = scan.stats.sell_count ?? scan.sell_signals.length;
   650	  const topScore = scan.buy_signals.length ? scan.buy_signals[0].score : '-';
   651	  const regimeClass = scan.regime.includes('RISK-ON') ? 'risk-on' : scan.regime.includes('RISK-OFF') ? 'risk-off' : 'transitional';
   652	
   653	  document.getElementById('marketBody').innerHTML = `
   654	    <div class="stats-row">
   655	      <div class="stat-card green"><div class="label">Buy Signals</div><div class="value">${buyCount}</div><div class="sub">Phase 2 confirmed uptrends</div></div>
   656	      <div class="stat-card red"><div class="label">Sell Signals</div><div class="value">${sellCount}</div><div class="sub">Phase 3/4 breakdowns</div></div>
   657	      <div class="stat-card blue"><div class="label">Top Score</div><div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div><div class="sub">${scan.buy_signals.length ? scan.buy_signals[0].ticker : '-'}</div></div>
   658	      <div class="stat-card"><div class="label">Universe</div><div class="value">${(scan.stats.analyzed || 0).toLocaleString()}</div><div class="sub">of ${(scan.stats.total_universe || 0).toLocaleString()} | ${scan.stats.processing_minutes || '?'} min</div></div>
   659	      <div class="stat-card ${scan.spy.phase === 2 ? 'green' : scan.spy.phase === 4 ? 'red' : 'yellow'}"><div class="label">SPY Phase</div><div class="value">${scan.spy.phase || '?'}</div><div class="sub">${scan.spy.trend || ''} @ $${(scan.spy.price || 0).toFixed(2)}</div></div>
   660	    </div>
   661	    <div class="grid-2">
   662	      <div class="card"><h2>Market Breadth</h2><div class="chart-wrap"><canvas id="breadthChart"></canvas></div></div>
   663	      <div class="card">
   664	        <h2>SPY Regime</h2>
   665	        <span class="regime-badge ${regimeClass}">${scan.regime}</span>
   666	        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px">
   667	          <div><div style="color:var(--muted);font-size:11px">Phase</div><div style="font-size:18px;font-weight:700">${scan.spy.phase} - ${scan.spy.phase_name || ''}</div></div>
   668	          <div><div style="color:var(--muted);font-size:11px">Confidence</div><div style="font-size:18px;font-weight:700">${scan.spy.confidence || '?'}%</div></div>
   669	        </div>
   670	      </div>
   671	    </div>
   672	    ${renderTop20Table(top20.top20 || [])}
   673	    <div class="card">
   674	      <h2 style="color:var(--green)">Buy Signals</h2>
   675	      <div style="overflow-x:auto"><table class="signal-table">
   676	        <thead><tr><th>#</th><th>Ticker</th><th>Score</th><th>Entry</th><th>Stop Loss</th><th>R:R</th><th>RS</th><th>Reddit</th><th>Key Reasons</th><th>Trade</th></tr></thead>
   677	        <tbody>${renderBuyRows(scan.buy_signals)}</tbody>
   678	      </table></div>
   679	    </div>
   680	    <div class="card">
   681	      <h2 style="color:var(--red)">Sell Signals</h2>
   682	      <div style="overflow-x:auto"><table class="signal-table">
   683	        <thead><tr><th>#</th><th>Ticker</th><th>Score</th><th>Severity</th><th>Breakdown</th><th>Reddit</th><th>Reasons</th><th>Trade</th></tr></thead>
   684	        <tbody>${renderSellRows(scan.sell_signals)}</tbody>
   685	      </table></div>
   686	    </div>`;
   687	
   688	  renderBreadthChart('breadthChart', scan.breadth);
   689	
   690	  // Stashed at module scope (not a local var) so the live-refresh closure set
   691	  // up in renderMarketView — which persists across scan-selector changes —
   692	  // always reads the CURRENT Top 20 list rather than whatever it was when
   693	  // the interval was first created.
   694	  _marketTop20Tickers = (top20.top20 || []).map(s => s.ticker);
   695	  loadMomentumStatus(_marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap));
   696	}
   697	
   698	function renderBuyRows(signals) {
   699	  if (!signals.length) return '<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
   700	  return signals.map(s => {
   701	    const pct = (s.score / (s.max_score || 125)) * 100;
   702	    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
   703	    const entryClass = (s.entry_quality || '').toLowerCase();
   704	    const topReasons = (s.reasons || []).slice(0, 3).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
   705	    const extra = (s.reasons || []).slice(3);
   706	    const extraHTML = extra.length
   707	      ? `<div class="extra-reasons" style="display:none">${extra.map(r => `<li>${cleanEmoji(r)}</li>`).join('')}</div><button class="expand-btn" onclick="toggleReasons(this)">+${extra.length} more</button>`
   708	      : '';
   709	    return `<tr>
   710	      <td>${s.rank}</td>
   711	      <td><span class="ticker">${s.ticker}</span></td>
   712	      <td><span class="score-num">${s.score}</span><div class="score-bar"><div class="fill" style="width:${pct}%;background:${barColor}"></div></div></td>
   713	      <td><span class="badge ${entryClass}">${s.entry_quality || '-'}</span></td>
   714	      <td>${s.stop_loss ? '$' + s.stop_loss.toFixed(2) : '-'}</td>
   715	      <td style="color:${(s.rr_ratio || 0) >= 3 ? 'var(--green)' : (s.rr_ratio || 0) >= 2 ? 'var(--text)' : 'var(--yellow)'}">${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : '-'}</td>
   716	      <td style="color:${(s.rs || 0) > 0.1 ? 'var(--green)' : (s.rs || 0) > 0 ? 'var(--text)' : 'var(--red)'}">${s.rs != null ? s.rs.toFixed(3) : '-'}</td>
   717	      <td>${redditCell(s.reddit_mentions)}</td>
   718	      <td><ul class="reasons-list">${topReasons}</ul>${extraHTML}</td>
   719	      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
   720	    </tr>`;
   721	  }).join('');
   722	}
   723	
   724	function renderSellRows(signals) {
   725	  if (!signals.length) return '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
   726	  return signals.map(s => {
   727	    const sevClass = (s.severity || 'medium').toLowerCase();
   728	    const reasons = (s.reasons || []).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
   729	    return `<tr>
   730	      <td>${s.rank}</td>
   731	      <td><span class="ticker">${s.ticker}</span></td>
   732	      <td><span class="score-num">${s.score}</span></td>
   733	      <td><span class="badge ${sevClass}">${(s.severity || '?').toUpperCase()}</span></td>
   734	      <td>${s.breakdown_level ? '$' + s.breakdown_level.toFixed(2) : '-'}</td>
   735	      <td>${redditCell(s.reddit_mentions)}</td>
   736	      <td><ul class="reasons-list">${reasons}</ul></td>
   737	      <td>${fidelityLink(s.ticker, 'Sell', 'sell')}</td>
   738	    </tr>`;
   739	  }).join('');
   740	}
   741	
   742	// --- View: Positions (upload a Fidelity CSV, get hold/trim/add recommendations) --
   743	
   744	const POSITION_ACTION_LABELS = {
   745	  hold: { label: 'hold', cls: 'neutral' },
   746	  trail_to_breakeven: { label: 'trail to breakeven', cls: 'good' },
   747	  trail_to_profit: { label: 'trail to profit', cls: 'good' },
   748	  take_partial_and_trail: { label: 'consider trimming', cls: 'medium' },
   749	  take_major_partial_and_trail_tight: { label: 'trim + trail tight', cls: 'poor' },
   750	};
   751	
   752	function _positionsUploadCardHTML(data, expanded) {
   753	  const hasResults = data.position_analyses && data.position_analyses.length;
   754	  // Once you have results, the big upload form is just noise — collapse it to
   755	  // a one-line bar with an "Update positions" toggle instead of always
   756	  // showing the full form front and center.
   757	  if (hasResults && !expanded) {
   758	    return `
   759	      <div class="card" id="pos-upload-card" style="display:flex;align-items:center;gap:12px;padding:14px 20px">
   760	        <span style="color:var(--muted);font-size:13px">Showing ${data.position_analyses.length} position${data.position_analyses.length === 1 ? '' : 's'} from your last upload.</span>
   761	        <button class="btn" id="pos-expand" style="margin-left:auto">Update positions</button>
   762	      </div>`;
   763	  }
   764	  return `
   765	    <div class="card sim-card" id="pos-upload-card" style="max-width:600px">
   766	      <h2>Upload Your Positions <span class="status-pill idle" id="pos-pill">idle</span></h2>
   767	      <div class="sim-desc">
   768	        Export a Positions CSV from Fidelity (Accounts &amp; Trade -&gt; Positions -&gt; Download) and upload it here.
   769	        Nothing leaves this machine — no login, no credentials, just the file you already downloaded. Only your
   770	        entry price and quantity are used; current prices come from cached market data, not the CSV.
   771	      </div>
   772	      <input type="file" id="pos-file" accept=".csv" style="margin-bottom:12px;display:block;color:var(--text);font-size:13px">
   773	      <button class="btn primary" id="pos-analyze">${data.has_csv ? 'Re-analyze' : 'Upload &amp; Analyze'}</button>
   774	      <div class="job-output" id="pos-output"></div>
   775	    </div>`;
   776	}
   777	
   778	async function renderPositionsView() {
   779	  const data = await fetchJSON('/api/positions');
   780	  if (_currentView !== 'positions') return; // navigated away before this resolved
   781	  const hasResults = data.position_analyses && data.position_analyses.length;
   782	  content.innerHTML = `
   783	    ${_positionsUploadCardHTML(data, false)}
   784	    <div id="pos-results" style="margin-top:20px"></div>`;
   785	
   786	  if (hasResults) {
   787	    pageMeta.innerHTML = liveBadgeHTML();
   788	    renderPositionsResults(data);
   789	    _startLive(() => _liveGuarded('positions', refreshPositionsLive));
   790	  }
   791	  wirePositionsUpload(data);
   792	}
   793	
   794	// Silent live refresh: re-runs the (cheap, yfinance-only) positions analysis
   795	// in the background and patches fresh prices/gains/charts in without touching
   796	// the upload card or showing a loading spinner.
   797	async function refreshPositionsLive() {
   798	  await startJob('positions', {}, async (st) => {
   799	    if (st.status === 'success') {
   800	      renderPositionsResults(await fetchJSON('/api/positions'));
   801	    }
   802	  });
   803	}
   804	
   805	function wirePositionsUpload(data) {
   806	  const expandBtn = document.getElementById('pos-expand');
   807	  if (expandBtn) {
   808	    expandBtn.addEventListener('click', () => {
   809	      document.getElementById('pos-upload-card').outerHTML = _positionsUploadCardHTML(data, true);
   810	      wirePositionsUpload(data);
   811	    });
   812	    return; // collapsed state has no analyze button yet
   813	  }
   814	
   815	  document.getElementById('pos-analyze').addEventListener('click', async () => {
   816	    const fileInput = document.getElementById('pos-file');
   817	    const btn = document.getElementById('pos-analyze');
   818	    const pill = document.getElementById('pos-pill');
   819	    const out = document.getElementById('pos-output');
   820	    btn.disabled = true;
   821	
   822	    if (fileInput.files.length) {
   823	      pill.className = 'status-pill running';
   824	      pill.innerHTML = '<span class="spinner"></span> uploading';
   825	      const form = new FormData();
   826	      form.append('csv', fileInput.files[0]);
   827	      const uploadRes = await fetch('/api/positions/upload', { method: 'POST', body: form }).then(r => r.json());
   828	      if (!uploadRes.success) {
   829	        showToast('Upload failed: ' + (uploadRes.error || 'unknown error'));
   830	        btn.disabled = false;
   831	        pill.className = 'status-pill error';
   832	        pill.textContent = 'error';
   833	        return;
   834	      }
   835	    } else if (!data.has_csv) {
   836	      showToast('Choose a CSV file first');
   837	      btn.disabled = false;
   838	      return;
   839	    }
   840	
   841	    out.style.display = 'block';
   842	    out.textContent = '';
   843	    pill.className = 'status-pill running';
   844	    pill.innerHTML = '<span class="spinner"></span> analyzing';
   845	
   846	    await startJob('positions', {}, async (st) => {
   847	      out.textContent = st.output.join('\n');
   848	      out.scrollTop = out.scrollHeight;
   849	      if (st.status === 'success' || st.status === 'error' || st.status === 'stopped') {
   850	        btn.disabled = false;
   851	        pill.className = `status-pill ${st.status}`;
   852	        pill.textContent = st.status;
   853	        if (st.status === 'success') {
   854	          renderPositionsResults(await fetchJSON('/api/positions'));
   855	        }
   856	      }
   857	    });
   858	  });
   859	}
   860	
   861	function renderPositionsResults(data) {
   862	  const summary = data.summary || {};
   863	  const analyses = data.position_analyses || [];
   864	  const resultsEl = document.getElementById('pos-results');
   865	  if (!resultsEl) return;
   866	
   867	  if (!analyses.length) {
   868	    resultsEl.innerHTML = '<div class="no-data"><h2>No positions found</h2></div>';
   869	    return;
   870	  }
   871	
   872	  const cards = analyses.map(a => {
   873	    const meta = POSITION_ACTION_LABELS[a.action] || { label: a.action || 'hold', cls: 'neutral' };
   874	    const gainColor = a.current_gain_pct >= 0 ? 'var(--green)' : 'var(--red)';
   875	    const gainSign = a.current_gain_pct >= 0 ? '+' : '';
   876	
   877	    let extra = '';
   878	    if (a.recommended_stop) {
   879	      extra += `<div class="agent-badge-sub">Recommended stop: $${a.recommended_stop.toFixed(2)}</div>`;
   880	    }
   881	    if (a.add_on_signal) {
   882	      extra += `<div class="agent-badge-sub" style="color:var(--green);margin-top:6px">Add-on candidate — ${a.add_on_rationale}</div>`;
   883	    }
   884	    (a.warnings || []).forEach(w => {
   885	      extra += `<div class="agent-badge-sub" style="color:var(--yellow)">${w}</div>`;
   886	    });
   887	
   888	    const chartId = `pos-chart-${a.ticker}`;
   889	    const hasHistory = a.price_history && a.price_history.length;
   890	
   891	    return `
   892	      <div class="pick-card">
   893	        <div class="pick-header">
   894	          <span class="ticker">${a.ticker}</span>
   895	          ${hasHistory ? chartToggleButtonHTML(chartId) : ''}
   896	          <span class="badge ${meta.cls}" style="margin-left:${hasHistory ? '8px' : 'auto'}">${meta.label}</span>
   897	        </div>
   898	        <div class="pick-scores">
   899	          <div class="score-block"><div class="label">Entry</div><div class="value">$${a.entry_price.toFixed(2)}</div></div>
   900	          <div class="score-block"><div class="label">Current</div><div class="value">$${a.current_price.toFixed(2)}</div></div>
   901	          <div class="score-block"><div class="label">Gain</div><div class="value" style="color:${gainColor}">${gainSign}${a.current_gain_pct}%</div></div>
   902	        </div>
   903	        <div style="margin-bottom:10px"><span id="momentum-slot-${a.ticker}"></span></div>
   904	        ${extra}
   905	        ${hasHistory ? `<div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>` : ''}
   906	      </div>`;
   907	  }).join('');
   908	
   909	  resultsEl.innerHTML = `
   910	    <div class="stats-row">
   911	      <div class="stat-card"><div class="label">Positions</div><div class="value">${summary.total_positions || 0}</div></div>
   912	      <div class="stat-card yellow"><div class="label">Need Adjustment</div><div class="value">${summary.positions_need_adjustment || 0}</div></div>
   913	      <div class="stat-card green"><div class="label">Add-On Candidates</div><div class="value">${summary.add_on_candidates || 0}</div></div>
   914	      <div class="stat-card ${(summary.average_gain_pct || 0) >= 0 ? 'green' : 'red'}"><div class="label">Avg Gain</div><div class="value">${(summary.average_gain_pct || 0) >= 0 ? '+' : ''}${summary.average_gain_pct || 0}%</div></div>
   915	    </div>
   916	    <div class="shortlist-grid">${cards}</div>`;
   917	
   918	  wireChartToggles(resultsEl, (ticker) => {
   919	    const a = analyses.find(x => x.ticker === ticker);
   920	    return a ? { history: a.price_history, entry: a.entry_price, stop: a.recommended_stop } : null;
   921	  }, 'pos-chart-');
   922	
   923	  const posTickers = analyses.map(a => a.ticker);
   924	  loadMomentumStatus(posTickers, 'positions', (statusMap) => paintMomentumSlots(posTickers, statusMap));
   925	}
   926	
   927	// --- View: Backtests ------------------------------------------------------
   928	
   929	async function renderBacktestsView() {
   930	  const history = await fetchJSON('/api/backtest/history');
   931	  if (_currentView !== 'backtests') return; // navigated away before this resolved
   932	  content.innerHTML = `
   933	    <div class="source-note historical">
   934	      <b>This is a report card, not your email.</b> It shows how the screener's scoring would have performed
   935	      on real historical stocks and prices — win rate, returns, drawdown. It doesn't contain today's picks;
   936	      for those, see <a href="#/shortlist" style="color:var(--blue)">Shortlist</a> or
   937	      <a href="#/market" style="color:var(--blue)">Market</a>. Run a fresh one from
   938	      <a href="#/run" style="color:var(--blue)">Run Simulation</a>.
   939	    </div>
   940	    <div style="margin-bottom:16px">
   941	      <select class="scan-select" id="backtestSelect">
   942	        <option value="">Latest</option>
   943	      </select>
   944	    </div>
   945	    <div id="backtestBody"></div>`;
   946	  const sel = document.getElementById('backtestSelect');
   947	  history.forEach(h => {
   948	    const opt = document.createElement('option');
   949	    opt.value = h.path;
   950	    opt.textContent = `${h.name} (${h.generated ? new Date(h.generated).toLocaleDateString() : '?'})`;
   951	    sel.appendChild(opt);
   952	  });
   953	  sel.addEventListener('change', () => loadBacktest(sel.value));
   954	  loadBacktest('');
   955	}
   956	
   957	async function loadBacktest(path) {
   958	  const [summaryData, tradesData] = await Promise.all([
   959	    path ? fetchJSON('/api/backtest/run?path=' + encodeURIComponent(path)) : fetchJSON('/api/backtest/latest'),
   960	    fetchJSON('/api/backtest/trades' + (path ? '?path=' + encodeURIComponent(path) : '')),
   961	  ]);
   962	  if (_currentView !== 'backtests') return; // navigated away before this resolved
   963	  const summary = summaryData.summary || {};
   964	  const trades = tradesData.trades || [];
   965	
   966	  if (!summary.total_trades) {
   967	    document.getElementById('backtestBody').innerHTML = `
   968	      <div class="no-data"><h2>No backtest history yet</h2><p>Run a Walk-Forward simulation from the Run Simulation page.</p></div>`;
   969	    return;
   970	  }
   971	  pageMeta.textContent = summaryData.generated ? `Generated ${new Date(summaryData.generated).toLocaleString()}` : '';
   972	
   973	  document.getElementById('backtestBody').innerHTML = `
   974	    <div class="stats-row">
   975	      <div class="stat-card ${summary.win_rate_pct >= 40 ? 'green' : 'yellow'}"><div class="label">Win Rate</div><div class="value">${(summary.win_rate_pct || 0).toFixed(1)}%</div><div class="sub">${summary.total_trades} trades</div></div>
   976	      <div class="stat-card ${summary.avg_return_pct >= 0 ? 'green' : 'red'}"><div class="label">Avg Return</div><div class="value">${(summary.avg_return_pct || 0).toFixed(2)}%</div><div class="sub">median ${(summary.median_return_pct || 0).toFixed(2)}%</div></div>
   977	      <div class="stat-card blue"><div class="label">Sharpe-like</div><div class="value">${(summary.sharpe_like || 0).toFixed(2)}</div><div class="sub">avg win ${(summary.avg_win_pct || 0).toFixed(1)}% / loss ${(summary.avg_loss_pct || 0).toFixed(1)}%</div></div>
   978	      <div class="stat-card red"><div class="label">Max Drawdown</div><div class="value">${(summary.max_drawdown_pct || 0).toFixed(1)}%</div><div class="sub">$${(summary.max_drawdown_dollars || 0).toFixed(0)}</div></div>
   979	      <div class="stat-card purple"><div class="label">Avg Days Held</div><div class="value">${(summary.avg_days_held || 0).toFixed(1)}</div><div class="sub">${summary.total_periods || '?'} periods</div></div>
   980	    </div>
   981	    <div class="grid-2">
   982	      <div class="card"><h2>Cumulative P&amp;L (by exit date)</h2><div class="chart-wrap"><canvas id="equityChart"></canvas></div></div>
   983	      <div class="card"><h2>Exit Reasons</h2><div class="chart-wrap"><canvas id="exitChart"></canvas></div></div>
   984	    </div>
   985	    <div class="card">
   986	      <h2>Trades <span style="font-weight:400;color:var(--muted);font-size:12px">(click a column to sort)</span></h2>
   987	      <div style="overflow-x:auto"><table class="signal-table" id="tradesTable">
   988	        <thead><tr>
   989	          <th data-key="ticker">Ticker</th><th data-key="period">Entry Date</th><th data-key="score">Score</th>
   990	          <th data-key="exit_reason">Exit Reason</th><th data-key="days_held">Days Held</th><th data-key="return_pct">Return %</th><th data-key="dollar_pnl">$ P&amp;L</th>
   991	        </tr></thead>
   992	        <tbody>${renderTradeRows(trades)}</tbody>
   993	      </table></div>
   994	    </div>`;
   995	
   996	  renderEquityCurveChart('equityChart', tradesData.equity_curve || []);
   997	  renderExitReasonChart('exitChart', summary.exit_reasons || {});
   998	
   999	  let sortKey = null, sortDir = 1;
  1000	  document.querySelectorAll('#tradesTable th[data-key]').forEach(th => {
  1001	    th.style.cursor = 'pointer';
  1002	    th.addEventListener('click', () => {
  1003	      const key = th.dataset.key;
  1004	      sortDir = sortKey === key ? -sortDir : 1;
  1005	      sortKey = key;
  1006	      const sorted = [...trades].sort((a, b) => {
  1007	        const av = a[key], bv = b[key];
  1008	        if (typeof av === 'string') return sortDir * String(av).localeCompare(String(bv));
  1009	        return sortDir * ((av || 0) - (bv || 0));
  1010	      });
  1011	      document.querySelector('#tradesTable tbody').innerHTML = renderTradeRows(sorted);
  1012	    });
  1013	  });
  1014	}
  1015	
  1016	function renderTradeRows(trades) {
  1017	  return trades.map(t => `<tr>
  1018	    <td><span class="ticker">${t.ticker}</span></td>
  1019	    <td>${t.period || '-'}</td>
  1020	    <td>${t.score ?? '-'}</td>
  1021	    <td><span class="badge ${t.exit_reason === 'stop_loss' ? 'poor' : t.exit_reason === 'sell_signal' ? 'medium' : 'good'}">${(t.exit_reason || '-').replace('_', ' ')}</span></td>
  1022	    <td>${t.days_held ?? '-'}</td>
  1023	    <td style="color:${(t.return_pct || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">${(t.return_pct || 0).toFixed(2)}%</td>
  1024	    <td style="color:${(t.dollar_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">$${(t.dollar_pnl || 0).toFixed(2)}</td>
  1025	  </tr>`).join('');
  1026	}
  1027	
  1028	// --- View: Run Simulation --------------------------------------------------
  1029	
  1030	function renderRunView() {
  1031	  content.innerHTML = `
  1032	    <div class="grid-3">
  1033	      ${jobCardHTML('top3', 'Quick Backtest (Top 3)', 'What would the top-3 buy signals have been N days ago, held to today?', `
  1034	        <label>Days back<input type="number" id="top3-days" value="7"></label>
  1035	        <label>Sample size<input type="number" id="top3-sample" value="150"></label>
  1036	        <label>Investment $<input type="number" id="top3-investment" value="1000"></label>
  1037	      `)}
  1038	      ${jobCardHTML('mc', 'Monte Carlo', 'Re-samples many top-3 portfolios from one fetched pool — win rate distribution, not one basket.', `
  1039	        <label>Days back<input type="number" id="mc-days" value="7"></label>
  1040	        <label>Pool size<input type="number" id="mc-pool" value="300"></label>
  1041	        <label>Sample size<input type="number" id="mc-sample" value="150"></label>
  1042	        <label>Iterations<input type="number" id="mc-iterations" value="100"></label>
  1043	      `)}
  1044	      ${jobCardHTML('wf', 'Full Walk-Forward', 'Rigorous multi-period backtest — walks a fixed universe through many historical dates. Slow (minutes+).', `
  1045	        <label>Universe size<input type="number" id="wf-universe_size" value="250"></label>
  1046	        <label>Lookback (mo)<input type="number" id="wf-lookback_months" value="9"></label>
  1047	        <label>Top N/period<input type="number" id="wf-top_n" value="10"></label>
  1048	        <label>Max hold (days)<input type="number" id="wf-max_hold_days" value="60"></label>
  1049	      `)}
  1050	    </div>`;
  1051	
  1052	  wireJobCard('top3', 'backtest-top3', () => ({
  1053	    days: +document.getElementById('top3-days').value,
  1054	    sample: +document.getElementById('top3-sample').value,
  1055	    investment: +document.getElementById('top3-investment').value,
  1056	  }), async (st, resultEl) => {
  1057	    if (!st.result_path) return;
  1058	    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
  1059	    if (res.error) return;
  1060	    resultEl.innerHTML = `<div style="font-size:13px">
  1061	      <strong style="color:${res.total_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.total_profit.toFixed(2)} (${res.total_return_pct.toFixed(2)}%)</strong>
  1062	      — ${res.picks.map(p => p.ticker).join(', ')}</div>`;
  1063	  });
  1064	
  1065	  wireJobCard('mc', 'backtest-monte-carlo', () => ({
  1066	    days: +document.getElementById('mc-days').value,
  1067	    pool: +document.getElementById('mc-pool').value,
  1068	    sample: +document.getElementById('mc-sample').value,
  1069	    iterations: +document.getElementById('mc-iterations').value,
  1070	  }), async (st, resultEl) => {
  1071	    if (!st.result_path) return;
  1072	    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
  1073	    if (res.error || !res.iterations_run) { resultEl.innerHTML = '<div style="color:var(--muted);font-size:13px">Not enough qualifiers found.</div>'; return; }
  1074	    resultEl.innerHTML = `<div style="font-size:13px">
  1075	      Win rate <strong>${res.win_rate.toFixed(1)}%</strong> · avg <strong style="color:${res.avg_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.avg_profit.toFixed(2)} (${res.avg_pct.toFixed(2)}%)</strong>
  1076	      over ${res.iterations_run} iterations${res.score_return_correlation != null ? ` · score/return correlation r=${res.score_return_correlation.toFixed(3)}` : ''}</div>`;
  1077	  });
  1078	
  1079	  wireJobCard('wf', 'walk-forward', () => ({
  1080	    universe_size: +document.getElementById('wf-universe_size').value,
  1081	    lookback_months: +document.getElementById('wf-lookback_months').value,
  1082	    top_n: +document.getElementById('wf-top_n').value,
  1083	    max_hold_days: +document.getElementById('wf-max_hold_days').value,
  1084	  }), async (st, resultEl) => {
  1085	    resultEl.innerHTML = `<a href="#/backtests" class="btn primary">View results →</a>`;
  1086	  });
  1087	}
  1088	
  1089	// --- View: Full Scan --------------------------------------------------------
  1090	
  1091	function renderScanView() {
  1092	  content.innerHTML = `
  1093	    <div class="card sim-card" style="max-width:520px">
  1094	      <h2>Run a Scan <span class="status-pill idle" id="scan-pill">idle</span></h2>
  1095	      <div class="sim-desc">Test scan covers ~100 stocks (~1 min). Full scan covers the ~3,800-stock universe (15-30 min).</div>
  1096	      <div class="sim-params" style="align-items:center">
  1097	        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-full" style="width:auto"> Full scan (unchecked = quick test scan)</label>
  1098	      </div>
  1099	      <div class="sim-params" style="align-items:center">
  1100	        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-agents" style="width:auto"> Enable AI agents (Fundamentals/Catalyst/Congress → Top 5 shortlist, needs ANTHROPIC_API_KEY)</label>
  1101	      </div>
  1102	      <button class="btn primary" id="scan-run">Run</button>
  1103	      <div class="job-output" id="scan-output"></div>
  1104	      <div id="scan-result" style="margin-top:12px"></div>
  1105	    </div>`;
  1106	
  1107	  wireJobCard('scan', 'scan', () => ({
  1108	    full: document.getElementById('scan-full').checked,
  1109	    enable_llm_agents: document.getElementById('scan-agents').checked,
  1110	  }), async (st, resultEl) => {
  1111	    resultEl.innerHTML = `<a href="#/market" class="btn primary">View Market →</a> <a href="#/shortlist" class="btn">View Shortlist →</a>`;
  1112	  });
  1113	}
  1114	
  1115	// silent=true (used by auto-sync): stays quiet unless it actually pulls new
  1116	// data, so a background sync every few minutes doesn't spam toasts for
  1117	// "already up to date" or for a transient failure — the manual button still
  1118	// surfaces both of those explicitly when you click it yourself.
  1119	async function doSync(silent) {
  1120	  try {
  1121	    const res = await fetchJSON('/api/sync', { method: 'POST' });
  1122	    if (res.success) {
  1123	      if (!res.output.includes('Already up to date')) {
  1124	        showToast('Pulled latest data — refreshing…');
  1125	        route();
  1126	      } else if (!silent) {
  1127	        showToast('Already up to date.');
  1128	      }
  1129	    } else if (!silent) {
  1130	      showToast('Sync failed: ' + (res.output || 'unknown error').slice(0, 200));
  1131	    }
  1132	    return res;
  1133	  } catch (e) {
  1134	    if (!silent) showToast('Sync error: ' + e.message);
  1135	    return { success: false };
  1136	  }
  1137	}
  1138	
  1139	document.getElementById('syncBtn').addEventListener('click', async () => {
  1140	  const btn = document.getElementById('syncBtn');
  1141	  btn.disabled = true;
  1142	  btn.innerHTML = '<span class="spinner"></span> Syncing…';
  1143	  await doSync(false);
  1144	  btn.disabled = false;
  1145	  btn.innerHTML = 'Sync latest';
  1146	});
  1147	
  1148	// Auto-sync: pulls in the background every few minutes so today's emailed
  1149	// picks show up here without you having to click Sync — runs app-wide (not
  1150	// tied to the current view, unlike the per-view "Live" refresh) since new
  1151	// data can land at any time regardless of what page you're on.
  1152	const AUTO_SYNC_INTERVAL_MS = 5 * 60 * 1000;
  1153	setInterval(() => doSync(true), AUTO_SYNC_INTERVAL_MS);
  1154	doSync(true); // also try once right away, in case new data landed since last time the app was open
  1155	
  1156	route();
     1	// Chart.js render helpers. Each function destroys any previous instance on
     2	// the given canvas id before creating a new one, so views can be re-rendered
     3	// freely (e.g. switching backtest runs) without leaking chart instances.
     4	
     5	const _chartInstances = {};
     6	
     7	function _destroyChart(canvasId) {
     8	  if (_chartInstances[canvasId]) {
     9	    _chartInstances[canvasId].destroy();
    10	    delete _chartInstances[canvasId];
    11	  }
    12	}
    13	
    14	function renderBreadthChart(canvasId, breadth) {
    15	  _destroyChart(canvasId);
    16	  const ctx = document.getElementById(canvasId).getContext('2d');
    17	  _chartInstances[canvasId] = new Chart(ctx, {
    18	    type: 'doughnut',
    19	    data: {
    20	      labels: ['Phase 1 (Base)', 'Phase 2 (Uptrend)', 'Phase 3 (Distribution)', 'Phase 4 (Downtrend)'],
    21	      datasets: [{
    22	        data: [breadth.phase_1_pct || 0, breadth.phase_2_pct || 0, breadth.phase_3_pct || 0, breadth.phase_4_pct || 0],
    23	        backgroundColor: ['#eab308', '#22c55e', '#f97316', '#ef4444'],
    24	        borderColor: '#1a1d27',
    25	        borderWidth: 3,
    26	      }],
    27	    },
    28	    options: {
    29	      responsive: true,
    30	      maintainAspectRatio: false,
    31	      plugins: {
    32	        legend: { position: 'right', labels: { color: '#8b8fa3', font: { size: 11 }, padding: 12 } },
    33	        tooltip: { callbacks: { label: (c) => `${c.label}: ${c.parsed}% (${breadth[`phase_${c.dataIndex + 1}_count`] || 0} stocks)` } },
    34	      },
    35	    },
    36	  });
    37	}
    38	
    39	function renderEquityCurveChart(canvasId, equityCurve) {
    40	  _destroyChart(canvasId);
    41	  const ctx = document.getElementById(canvasId).getContext('2d');
    42	  const labels = equityCurve.map(p => p.date.slice(0, 10));
    43	  const values = equityCurve.map(p => p.cumulative_pnl);
    44	  const positive = values.length && values[values.length - 1] >= 0;
    45	  _chartInstances[canvasId] = new Chart(ctx, {
    46	    type: 'line',
    47	    data: {
    48	      labels,
    49	      datasets: [{
    50	        label: 'Cumulative P&L ($)',
    51	        data: values,
    52	        borderColor: positive ? '#22c55e' : '#ef4444',
    53	        backgroundColor: positive ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
    54	        fill: true,
    55	        tension: 0.15,
    56	        pointRadius: 0,
    57	        borderWidth: 2,
    58	      }],
    59	    },
    60	    options: {
    61	      responsive: true,
    62	      maintainAspectRatio: false,
    63	      scales: {
    64	        x: { ticks: { color: '#8b8fa3', maxTicksLimit: 8, font: { size: 10 } }, grid: { color: '#2a2d3a' } },
    65	        y: { ticks: { color: '#8b8fa3', font: { size: 10 }, callback: (v) => '$' + v }, grid: { color: '#2a2d3a' } },
    66	      },
    67	      plugins: {
    68	        legend: { display: false },
    69	        tooltip: { callbacks: { label: (c) => `Cumulative: $${c.parsed.y.toFixed(2)}` } },
    70	      },
    71	    },
    72	  });
    73	}
    74	
    75	function renderExitReasonChart(canvasId, exitReasons) {
    76	  _destroyChart(canvasId);
    77	  const ctx = document.getElementById(canvasId).getContext('2d');
    78	  const labels = Object.keys(exitReasons || {});
    79	  const values = labels.map(l => exitReasons[l]);
    80	  const colors = { stop_loss: '#ef4444', max_hold: '#3b82f6', sell_signal: '#eab308' };
    81	  _chartInstances[canvasId] = new Chart(ctx, {
    82	    type: 'bar',
    83	    data: {
    84	      labels: labels.map(l => l.replace('_', ' ')),
    85	      datasets: [{
    86	        data: values,
    87	        backgroundColor: labels.map(l => colors[l] || '#8b8fa3'),
    88	        borderRadius: 4,
    89	      }],
    90	    },
    91	    options: {
    92	      responsive: true,
    93	      maintainAspectRatio: false,
    94	      plugins: { legend: { display: false } },
    95	      scales: {
    96	        x: { ticks: { color: '#8b8fa3', font: { size: 11 } }, grid: { display: false } },
    97	        y: { ticks: { color: '#8b8fa3', font: { size: 10 } }, grid: { color: '#2a2d3a' } },
    98	      },
    99	    },
   100	  });
   101	}
   102	
   103	// Real historical price chart for one position — NOT a forecast/projection
   104	// (no future data exists to plot honestly). entryPrice/stopLoss are drawn as
   105	// flat reference lines so you can see where the current price sits relative
   106	// to your cost basis and the recommended stop, over real price history.
   107	function renderPositionChart(canvasId, priceHistory, entryPrice, stopLoss) {
   108	  _destroyChart(canvasId);
   109	  const ctx = document.getElementById(canvasId).getContext('2d');
   110	  const labels = priceHistory.map(p => p.date);
   111	  const closes = priceHistory.map(p => p.close);
   112	  const datasets = [{
   113	    label: 'Price',
   114	    data: closes,
   115	    borderColor: '#3b82f6',
   116	    backgroundColor: 'rgba(59,130,246,0.08)',
   117	    fill: true,
   118	    tension: 0.15,
   119	    pointRadius: 0,
   120	    borderWidth: 2,
   121	  }];
   122	  if (entryPrice) {
   123	    datasets.push({
   124	      label: 'Your entry', data: labels.map(() => entryPrice),
   125	      borderColor: '#8b8fa3', borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5, fill: false,
   126	    });
   127	  }
   128	  if (stopLoss) {
   129	    datasets.push({
   130	      label: 'Recommended stop', data: labels.map(() => stopLoss),
   131	      borderColor: '#ef4444', borderDash: [3, 3], pointRadius: 0, borderWidth: 1.5, fill: false,
   132	    });
   133	  }
   134	  _chartInstances[canvasId] = new Chart(ctx, {
   135	    type: 'line',
   136	    data: { labels, datasets },
   137	    options: {
   138	      responsive: true,
   139	      maintainAspectRatio: false,
   140	      interaction: { mode: 'index', intersect: false },
   141	      plugins: {
   142	        legend: { display: true, position: 'top', labels: { color: '#8b8fa3', font: { size: 10 }, boxWidth: 12 } },
   143	        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: $${c.parsed.y.toFixed(2)}` } },
   144	      },
   145	      scales: {
   146	        x: { ticks: { color: '#8b8fa3', maxTicksLimit: 6, font: { size: 10 } }, grid: { color: '#2a2d3a' } },
   147	        y: { ticks: { color: '#8b8fa3', font: { size: 10 }, callback: (v) => '$' + v }, grid: { color: '#2a2d3a' } },
   148	      },
   149	    },
   150	  });
   151	}

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba dashboard.py | sed -n '1,220p'; nl -ba dashboard.py | sed -n '220,520p'; nl -ba dashboard.py | sed -n '520,820p'; nl -ba mac_app/main.py; nl -ba mac_app/setup.py; nl -ba mac_app/README.md | sed -n '1,220p'; rg -n \"dashboard|static|templates|Chart|py2app|package_data|DATA_FILES|AUTO_SYNC|LIVE_INTERVAL|setTimeout|setInterval|jobs\" README.md QUICK_START.md START_HERE.md tests mac_app dashboard.py static templates"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
     1	#!/usr/bin/env python3
     2	"""Interactive web dashboard for Stock Screener results.
     3	
     4	Usage:
     5	    python dashboard.py                    # Start dashboard on port 5050
     6	    python dashboard.py --port 8080        # Custom port
     7	    python dashboard.py --scan             # Run test scan first, then launch
     8	    python dashboard.py --scan --full      # Run full scan first, then launch
     9	"""
    10	
    11	import argparse
    12	import json
    13	import os
    14	import re
    15	import shutil
    16	import subprocess
    17	import sys
    18	import threading
    19	import time
    20	import uuid
    21	import webbrowser
    22	from pathlib import Path
    23	from threading import Timer
    24	
    25	from flask import Flask, jsonify, render_template, request
    26	
    27	# When bundled as a standalone .app (py2app sets sys.frozen), this file lives
    28	# inside the bundle's Resources folder, not the real project checkout — but
    29	# the dashboard always needs to read/write the real repo (git pull/push via
    30	# /api/sync, data/ files, and it shells out to the project's own venv to run
    31	# scripts). So PROJECT_ROOT deliberately does NOT follow __file__ when frozen;
    32	# it points at the real checkout instead, overridable via STOCK_SCREENER_ROOT
    33	# for anyone whose folder lives somewhere other than the default.
    34	if getattr(sys, "frozen", False):
    35	    PROJECT_ROOT = Path(os.environ.get("STOCK_SCREENER_ROOT", str(Path.home() / "Desktop" / "stock-screener"))).resolve()
    36	else:
    37	    PROJECT_ROOT = Path(__file__).parent.resolve()
    38	
    39	# py2app's own bootstrap chdir's the frozen process into the .app bundle's
    40	# Resources folder before this module even runs — wrong for us either way, we
    41	# always want PROJECT_ROOT. Setting it here (rather than passing cwd= on each
    42	# subprocess call below) is what keeps those calls eligible for macOS's safe
    43	# posix_spawn() path instead of fork()+exec() — see the comment in
    44	# _launch_job() for why that distinction matters for the packaged .app.
    45	os.chdir(str(PROJECT_ROOT))
    46	
    47	app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"), static_folder=str(PROJECT_ROOT / "static"))
    48	
    49	SCAN_DIR = PROJECT_ROOT / "data" / "daily_scans"
    50	BACKTEST_DIR = PROJECT_ROOT / "data" / "backtest_history"
    51	ADHOC_DIR = PROJECT_ROOT / "data" / "adhoc_simulations"
    52	POSITIONS_CSV = PROJECT_ROOT / "data" / "positions_latest.csv"
    53	VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"
    54	
    55	
    56	def _venv_python():
    57	    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    58	
    59	
    60	# The plain "git" on PATH (/usr/bin/git) is actually a stub that shells out to
    61	# `xcodebuild -find git` to locate the real binary — on a machine with a
    62	# broken/corrupted Xcode.app (as opposed to just the separate, lighter-weight
    63	# Command Line Tools), that stub fails with an unrelated-looking dlopen error
    64	# and git (and the Sync button) stops working entirely, even though a real,
    65	# working git binary is usually still sitting right here. Preferring it
    66	# sidesteps the broken xcodebuild lookup rather than depending on it.
    67	_CLT_GIT = Path("/Library/Developer/CommandLineTools/usr/bin/git")
    68	
    69	
    70	def _git_binary():
    71	    if _CLT_GIT.exists():
    72	        return str(_CLT_GIT)
    73	    return shutil.which("git") or "/usr/bin/git"
    74	
    75	
    76	def _read_json(path, default):
    77	    """Load a JSON file, falling back to `default` if it's missing/unreadable
    78	    — every read-only route uses this so "no data yet" is always a normal 200
    79	    response, never a bare error."""
    80	    path = Path(path)
    81	    if not path.exists():
    82	        return default
    83	    try:
    84	        return json.loads(path.read_text(encoding="utf-8"))
    85	    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
    86	        return default
    87	
    88	
    89	def parse_scan_file(filepath):
    90	    """Parse a scan .txt file into structured data."""
    91	    text = Path(filepath).read_text(encoding="utf-8")
    92	
    93	    data = {
    94	        "scan_date": "",
    95	        "generated": "",
    96	        "stats": {},
    97	        "spy": {},
    98	        "breadth": {},
    99	        "regime": "",
   100	        "buy_signals": [],
   101	        "sell_signals": [],
   102	    }
   103	
   104	    # Header stats
   105	    m = re.search(r"Scan Date:\s*(.+)", text)
   106	    if m:
   107	        data["scan_date"] = m.group(1).strip()
   108	
   109	    m = re.search(r"Generated:\s*(.+)", text)
   110	    if m:
   111	        data["generated"] = m.group(1).strip()
   112	
   113	    m = re.search(r"Total Universe:\s*([\d,]+)", text)
   114	    if m:
   115	        data["stats"]["total_universe"] = int(m.group(1).replace(",", ""))
   116	
   117	    m = re.search(r"Analyzed:\s*([\d,]+)", text)
   118	    if m:
   119	        data["stats"]["analyzed"] = int(m.group(1).replace(",", ""))
   120	
   121	    m = re.search(r"Processing Time:\s*([\d.]+)", text)
   122	    if m:
   123	        data["stats"]["processing_minutes"] = float(m.group(1))
   124	
   125	    m = re.search(r"Error Rate:\s*([\d.]+)%", text)
   126	    if m:
   127	        data["stats"]["error_rate"] = float(m.group(1))
   128	
   129	    m = re.search(r"Buy Signals:\s*(\d+)", text)
   130	    if m:
   131	        data["stats"]["buy_count"] = int(m.group(1))
   132	
   133	    m = re.search(r"Sell Signals:\s*(\d+)", text)
   134	    if m:
   135	        data["stats"]["sell_count"] = int(m.group(1))
   136	
   137	    # SPY
   138	    m = re.search(r"Phase:\s*(\d)\s*-\s*(.+)", text)
   139	    if m:
   140	        data["spy"]["phase"] = int(m.group(1))
   141	        data["spy"]["phase_name"] = m.group(2).strip()
   142	
   143	    m = re.search(r"Trend:\s*(\w+)", text)
   144	    if m:
   145	        data["spy"]["trend"] = m.group(1).strip()
   146	
   147	    m = re.search(r"Current Price:\s*\$([\d.]+)", text)
   148	    if m:
   149	        data["spy"]["price"] = float(m.group(1))
   150	
   151	    m = re.search(r"Confidence:\s*(\d+)%", text)
   152	    if m:
   153	        data["spy"]["confidence"] = int(m.group(1))
   154	
   155	    # Breadth
   156	    for phase_num, label in [(1, "phase_1"), (2, "phase_2"), (3, "phase_3"), (4, "phase_4")]:
   157	        m = re.search(
   158	            rf"Phase {phase_num} \([^)]+\):\s*(\d+)\s*stocks\s*\(([\d.]+)%\)", text
   159	        )
   160	        if m:
   161	            data["breadth"][f"{label}_count"] = int(m.group(1))
   162	            data["breadth"][f"{label}_pct"] = float(m.group(2))
   163	
   164	    m = re.search(r"Market Regime:\s*(.+)", text)
   165	    if m:
   166	        data["regime"] = m.group(1).strip()
   167	
   168	    # Buy signals — extract each signal as header+details block
   169	    buy_pattern = re.compile(
   170	        r"BUY #(\d+):\s*(\w+)\s*\|\s*Score:\s*([\d.]+)/(\d+)"
   171	        r".*?(?=BUY #\d+:|SELL #\d+:|={50,}.*(?:TOP SELL|END OF|ADDITIONAL)|\Z)",
   172	        re.DOTALL,
   173	    )
   174	    for bm in buy_pattern.finditer(text):
   175	        block = bm.group(0)
   176	        signal = {
   177	            "rank": int(bm.group(1)),
   178	            "ticker": bm.group(2),
   179	            "score": float(bm.group(3)),
   180	            "max_score": int(bm.group(4)),
   181	            "reasons": [],
   182	        }
   183	
   184	        m = re.search(r"Phase:\s*(\d)", block)
   185	        if m:
   186	            signal["phase"] = int(m.group(1))
   187	
   188	        m = re.search(r"Entry Quality:\s*(\w+)", block)
   189	        if m:
   190	            signal["entry_quality"] = m.group(1)
   191	
   192	        m = re.search(r"Stop Loss:\s*\$([\d.]+)", block)
   193	        if m:
   194	            signal["stop_loss"] = float(m.group(1))
   195	
   196	        m = re.search(r"Risk/Reward:\s*([\d.]+):1\s*\(Risk \$([\d.]+),\s*Reward \$([\d.]+)\)", block)
   197	        if m:
   198	            signal["rr_ratio"] = float(m.group(1))
   199	            signal["risk"] = float(m.group(2))
   200	            signal["reward"] = float(m.group(3))
   201	
   202	        m = re.search(r"RS:\s*([-\d.]+)", block)
   203	        if m:
   204	            signal["rs"] = float(m.group(1))
   205	
   206	        m = re.search(r"Volume:\s*([\d.]+)x", block)
   207	        if m:
   208	            signal["volume_ratio"] = float(m.group(1))
   209	
   210	        m = re.search(r"Reddit Mentions \(24h\):\s*(\d+)", block)
   211	        if m:
   212	            signal["reddit_mentions"] = int(m.group(1))
   213	
   214	        reasons = re.findall(r"[•]\s*(.+)", block)
   215	        signal["reasons"] = [r.strip() for r in reasons[:7]]
   216	
   217	        m = re.search(r"Overall Assessment:\s*\n(.+)", block)
   218	        if m:
   219	            signal["assessment"] = m.group(1).strip()
   220	
   220	
   221	        data["buy_signals"].append(signal)
   222	
   223	    # Sell signals
   224	    sell_pattern = re.compile(
   225	        r"SELL #(\d+):\s*(\w+)\s*\|\s*Score:\s*([\d.]+)/(\d+)"
   226	        r".*?(?=SELL #\d+:|={50,}.*(?:END OF|ADDITIONAL)|\Z)",
   227	        re.DOTALL,
   228	    )
   229	    for sm in sell_pattern.finditer(text):
   230	        block = sm.group(0)
   231	        signal = {
   232	            "rank": int(sm.group(1)),
   233	            "ticker": sm.group(2),
   234	            "score": float(sm.group(3)),
   235	            "max_score": int(sm.group(4)),
   236	            "reasons": [],
   237	        }
   238	
   239	        m = re.search(r"Phase:\s*(\d)\s*\|\s*.*Severity:\s*(\w+)", block)
   240	        if m:
   241	            signal["phase"] = int(m.group(1))
   242	            signal["severity"] = m.group(2)
   243	
   244	        m = re.search(r"Breakdown:\s*\$([\d.]+)", block)
   245	        if m:
   246	            signal["breakdown_level"] = float(m.group(1))
   247	
   248	        m = re.search(r"Reddit Mentions \(24h\):\s*(\d+)", block)
   249	        if m:
   250	            signal["reddit_mentions"] = int(m.group(1))
   251	
   252	        reasons = re.findall(r"[•]\s*(.+)", block)
   253	        signal["reasons"] = [r.strip() for r in reasons[:5]]
   254	
   255	        data["sell_signals"].append(signal)
   256	
   257	    return data
   258	
   259	
   260	def get_scan_files():
   261	    """Get list of available scan files, newest first."""
   262	    if not SCAN_DIR.exists():
   263	        return []
   264	    files = sorted(SCAN_DIR.glob("optimized_scan_*.txt"), reverse=True)
   265	    return [{"name": f.stem, "path": str(f), "date": f.stem.replace("optimized_scan_", "")} for f in files]
   266	
   267	
   268	def get_backtest_files():
   269	    """Get list of walk-forward backtest history files, newest first."""
   270	    if not BACKTEST_DIR.exists():
   271	        return []
   272	    files = sorted(BACKTEST_DIR.glob("walk_forward_*.json"), reverse=True)
   273	    out = []
   274	    for f in files:
   275	        data = _read_json(f, {})
   276	        out.append({"name": f.stem, "path": str(f), "generated": data.get("generated")})
   277	    return out
   278	
   279	
   280	# ---------------------------------------------------------------------------
   281	# Background job runner — generalized version of control_panel.py's
   282	# STATE-dict + subprocess.Popen + polling pattern, keyed by a generated job_id
   283	# (instead of a fixed command id) so multiple differently-configured
   284	# simulations can run/be polled independently in one session.
   285	# ---------------------------------------------------------------------------
   286	
   287	JOBS = {}
   288	JOBS_LOCK = threading.Lock()
   289	
   290	
   291	def _clean_subprocess_env():
   292	    """A copy of the current environment with PYTHONHOME/PYTHONPATH stripped —
   293	    see the comment in _launch_job() for why those two specifically break a
   294	    venv/bin/python subprocess when this process is the packaged .app. Also
   295	    forces unbuffered child stdout: Python fully block-buffers stdout when
   296	    it's a pipe (not a terminal), so without this every print() in the child
   297	    script sits in a buffer until the process exits and flushes everything at
   298	    once — the live output panel would show nothing the whole run, then the
   299	    entire report appears all at once right as the job finishes, which reads
   300	    exactly like it's stuck rather than actually working."""
   301	    env = os.environ.copy()
   302	    env.pop("PYTHONHOME", None)
   303	    env.pop("PYTHONPATH", None)
   304	    env["PYTHONUNBUFFERED"] = "1"
   305	    return env
   306	
   307	
   308	# How long a job is allowed to run before the dashboard force-kills it. Needed
   309	# because a hung network call somewhere deep in a third-party library (a scan
   310	# hit this: yfinance/urllib3 claims a 10s timeout on price history, but a real
   311	# run still blocked forever in an SSL socket read to a Yahoo Finance host that
   312	# had already dropped the connection — the retry/timeout logic just never
   313	# kicked in) can otherwise sit forever, holding the job "running" and, via the
   314	# close_fds=False tradeoff above, an inherited copy of the Flask listening
   315	# socket — which is what took the whole dashboard offline last time this
   316	# happened, not just the one job.
   317	JOB_TIMEOUT_SECONDS = {"scan": 45 * 60}
   318	DEFAULT_JOB_TIMEOUT_SECONDS = 10 * 60
   319	
   320	
   321	def _kill_hung_job(job_id, proc):
   322	    if proc.poll() is not None:
   323	        return  # already finished naturally, nothing to do
   324	    proc.kill()
   325	    with JOBS_LOCK:
   326	        job = JOBS.get(job_id)
   327	        if job:
   328	            job["output"].append(
   329	                "[dashboard] job exceeded its time limit and was terminated — "
   330	                "likely a hung network call to a third-party data source that "
   331	                "stopped responding without raising an error."
   332	            )
   333	            job["status"] = "error"
   334	
   335	
   336	def _launch_job(job_id, cmd, result_path):
   337	    with JOBS_LOCK:
   338	        JOBS[job_id]["status"] = "running"
   339	        kind = JOBS[job_id]["kind"]
   340	
   341	    try:
   342	        # No cwd= here on purpose — CPython's subprocess module only takes the
   343	        # safe posix_spawn() path on macOS when cwd is None; passing cwd forces
   344	        # the traditional fork()+exec() path instead, which is unsafe from a
   345	        # process that has Cocoa/WebKit loaded (true when running inside the
   346	        # packaged .app, via pywebview) and can cause bizarre, hard-to-reproduce
   347	        # subprocess failures. main()/dashboard.py's own process cwd is set to
   348	        # PROJECT_ROOT at startup instead (see chdir near the top of this file
   349	        # and in mac_app/main.py), and every cmd argument is an absolute path,
   350	        # so dropping cwd= here doesn't change what actually runs.
   351	        #
   352	        # close_fds=False for the same reason: this system's Python lacks
   353	        # posix_spawn_closefrom, so posix_spawn eligibility requires close_fds
   354	        # to be explicitly False (its default is True). The child inheriting
   355	        # the parent's other open fds (e.g. the Flask listening socket) is an
   356	        # acceptable tradeoff here — a local single-user tool, not a server
   357	        # handling untrusted subprocess args — versus the alternative of
   358	        # falling back to the unsafe fork() path.
   359	        #
   360	        # env=_clean_subprocess_env() because the packaged .app's own launcher
   361	        # sets PYTHONHOME and PYTHONPATH to point at the *bundle's* Resources
   362	        # folder — every subprocess call here runs venv/bin/python instead
   363	        # (a real, separate Python 3.13), but it still inherits those two
   364	        # variables by default, which override its own interpreter's normal
   365	        # stdlib/site-packages resolution and point it at the bundle's instead.
   366	        # That's what was actually causing `ModuleNotFoundError: No module
   367	        # named 'zoneinfo'` deep inside pandas — venv/bin/python was loading
   368	        # its standard library from the app bundle, not from itself.
   369	        # encoding='utf-8' explicitly — a GUI-launched .app has no LANG/LC_ALL
   370	        # set (a Terminal shell normally sets these), so text=True's default
   371	        # locale-based decoding falls back to ASCII and crashes on any non-
   372	        # ASCII character in the child's output (e.g. the em-dashes/bullets in
   373	        # position_manager.py's rationale text).
   374	        proc = subprocess.Popen(
   375	            cmd, env=_clean_subprocess_env(),
   376	            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
   377	            encoding="utf-8", errors="replace", bufsize=1, close_fds=False,
   378	        )
   379	        with JOBS_LOCK:
   380	            JOBS[job_id]["proc"] = proc
   381	
   382	        timeout_seconds = JOB_TIMEOUT_SECONDS.get(kind, DEFAULT_JOB_TIMEOUT_SECONDS)
   383	        watchdog = threading.Timer(timeout_seconds, _kill_hung_job, args=(job_id, proc))
   384	        watchdog.daemon = True
   385	        watchdog.start()
   386	        try:
   387	            for line in proc.stdout:
   388	                with JOBS_LOCK:
   389	                    JOBS[job_id]["output"].append(line.rstrip("\n"))
   390	            proc.wait()
   391	        finally:
   392	            watchdog.cancel()
   393	
   394	        with JOBS_LOCK:
   395	            JOBS[job_id]["returncode"] = proc.returncode
   396	            JOBS[job_id]["status"] = "success" if proc.returncode == 0 else "error"
   397	            JOBS[job_id]["proc"] = None
   398	            JOBS[job_id]["result_path"] = result_path
   399	    except Exception as exc:
   400	        with JOBS_LOCK:
   401	            JOBS[job_id]["output"].append(f"[dashboard] failed to launch: {exc}")
   402	            JOBS[job_id]["status"] = "error"
   403	            JOBS[job_id]["proc"] = None
   404	
   405	
   406	def _build_job(kind, body):
   407	    """Build (cmd, result_path) for a job kind from a request body, using each
   408	    underlying script's own argparse defaults when a param is omitted."""
   409	    python = _venv_python()
   410	    job_id = uuid.uuid4().hex[:12]
   411	
   412	    if kind == "scan":
   413	        cmd = [python, str(PROJECT_ROOT / "run_optimized_scan.py")]
   414	        if not body.get("full"):
   415	            cmd.append("--test-mode")
   416	        if body.get("enable_llm_agents"):
   417	            cmd.append("--enable-llm-agents")
   418	        result_path = str(SCAN_DIR / "shortlist_latest.json")
   419	
   420	    elif kind == "backtest-top3":
   421	        result_path = str(ADHOC_DIR / f"backtest_top3_{job_id}.json")
   422	        cmd = [
   423	            python, str(PROJECT_ROOT / "scripts" / "backtest_top3.py"),
   424	            "--days", str(body.get("days", 7)),
   425	            "--sample", str(body.get("sample", 150)),
   426	            "--investment", str(body.get("investment", 1000)),
   427	            "--json-out", result_path,
   428	        ]
   429	
   430	    elif kind == "backtest-monte-carlo":
   431	        result_path = str(ADHOC_DIR / f"monte_carlo_{job_id}.json")
   432	        cmd = [
   433	            python, str(PROJECT_ROOT / "scripts" / "backtest_top3_monte_carlo.py"),
   434	            "--days", str(body.get("days", 7)),
   435	            "--pool", str(body.get("pool", 300)),
   436	            "--sample", str(body.get("sample", 150)),
   437	            "--iterations", str(body.get("iterations", 100)),
   438	            "--investment", str(body.get("investment", 1000)),
   439	            "--json-out", result_path,
   440	        ]
   441	
   442	    elif kind == "walk-forward":
   443	        result_path = str(BACKTEST_DIR / "latest.json")
   444	        cmd = [
   445	            python, str(PROJECT_ROOT / "scripts" / "walk_forward_backtest.py"),
   446	            "--universe-size", str(body.get("universe_size", 250)),
   447	            "--lookback-months", str(body.get("lookback_months", 9)),
   448	            "--step-days", str(body.get("step_days", 14)),
   449	            "--top-n", str(body.get("top_n", 10)),
   450	            "--max-hold-days", str(body.get("max_hold_days", 60)),
   451	            "--investment-per-trade", str(body.get("investment_per_trade", 1000)),
   452	            "--seed", str(body.get("seed", 42)),
   453	        ]
   454	
   455	    elif kind == "positions":
   456	        if not POSITIONS_CSV.exists():
   457	            return None, None, None
   458	        result_path = str(ADHOC_DIR / "positions_latest.json")
   459	        cmd = [python, str(PROJECT_ROOT / "manage_positions.py"), "--csv", str(POSITIONS_CSV), "--json-out", result_path]
   460	
   461	    elif kind == "news":
   462	        tickers = body.get("tickers") or []
   463	        group = body.get("group", "misc")
   464	        if not tickers:
   465	            return None, None, None
   466	        result_path = str(ADHOC_DIR / f"news_{group}.json")
   467	        cmd = [
   468	            python, str(PROJECT_ROOT / "scripts" / "fetch_news.py"),
   469	            "--tickers", ",".join(tickers),
   470	            "--json-out", result_path,
   471	        ]
   472	
   473	    elif kind == "price-history":
   474	        tickers = body.get("tickers") or []
   475	        group = body.get("group", "misc")
   476	        if not tickers:
   477	            return None, None, None
   478	        result_path = str(ADHOC_DIR / f"price_history_{group}.json")
   479	        cmd = [
   480	            python, str(PROJECT_ROOT / "scripts" / "fetch_price_history.py"),
   481	            "--tickers", ",".join(tickers),
   482	            "--json-out", result_path,
   483	        ]
   484	
   485	    elif kind == "momentum-status":
   486	        tickers = body.get("tickers") or []
   487	        group = body.get("group", "misc")
   488	        if not tickers:
   489	            return None, None, None
   490	        result_path = str(ADHOC_DIR / f"momentum_status_{group}.json")
   491	        cmd = [
   492	            python, str(PROJECT_ROOT / "scripts" / "fetch_momentum_status.py"),
   493	            "--tickers", ",".join(tickers),
   494	            "--group", group,
   495	            "--json-out", result_path,
   496	        ]
   497	
   498	    else:
   499	        return None, None, None
   500	
   501	    return job_id, cmd, result_path
   502	
   503	
   504	JOB_RETENTION_SECONDS = 15 * 60  # how long a finished job stays pollable after completion
   505	
   506	
   507	def _prune_old_jobs():
   508	    """Drop finished jobs older than JOB_RETENTION_SECONDS. Without this, JOBS
   509	    grows without bound — the dashboard's own "Live" auto-refresh (every 90s,
   510	    across positions/news/price-history) now starts a job on every tick for as
   511	    long as the app stays open, so an all-day session could otherwise pile up
   512	    thousands of entries (each holding its full output line list) in memory.
   513	    Called opportunistically on every new job start rather than on a timer."""
   514	    now = time.time()
   515	    with JOBS_LOCK:
   516	        stale = [
   517	            jid for jid, job in JOBS.items()
   518	            if job["status"] not in ("queued", "running") and (now - job["started"]) > JOB_RETENTION_SECONDS
   519	        ]
   520	        for jid in stale:
   520	        for jid in stale:
   521	            del JOBS[jid]
   522	
   523	
   524	@app.route("/api/jobs/<kind>", methods=["POST"])
   525	def api_start_job(kind):
   526	    if kind == "positions" and not POSITIONS_CSV.exists():
   527	        return jsonify({"error": "no positions CSV uploaded yet"}), 400
   528	
   529	    body = request.json or {}
   530	    job_id, cmd, result_path = _build_job(kind, body)
   531	    if job_id is None:
   532	        return jsonify({"error": f"unknown job kind: {kind}"}), 404
   533	
   534	    _prune_old_jobs()
   535	    ADHOC_DIR.mkdir(parents=True, exist_ok=True)
   536	    with JOBS_LOCK:
   537	        JOBS[job_id] = {
   538	            "kind": kind, "status": "queued", "output": [], "returncode": None,
   539	            "started": time.time(), "proc": None, "result_path": None,
   540	        }
   541	    threading.Thread(target=_launch_job, args=(job_id, cmd, result_path), daemon=True).start()
   542	    return jsonify({"job_id": job_id})
   543	
   544	
   545	@app.route("/api/jobs/<job_id>")
   546	def api_job_status(job_id):
   547	    with JOBS_LOCK:
   548	        job = JOBS.get(job_id)
   549	        if not job:
   550	            return jsonify({"error": "unknown job"}), 404
   551	        elapsed = (time.time() - job["started"]) if job["status"] == "running" else None
   552	        return jsonify({
   553	            "status": job["status"], "output": job["output"],
   554	            "returncode": job["returncode"], "elapsed": elapsed,
   555	            "result_path": job["result_path"],
   556	        })
   557	
   558	
   559	@app.route("/api/jobs/<job_id>/stop", methods=["POST"])
   560	def api_job_stop(job_id):
   561	    with JOBS_LOCK:
   562	        job = JOBS.get(job_id)
   563	        if not job:
   564	            return jsonify({"error": "unknown job"}), 404
   565	        proc = job["proc"]
   566	    if proc and proc.poll() is None:
   567	        proc.terminate()
   568	        with JOBS_LOCK:
   569	            job["status"] = "stopped"
   570	        return jsonify({"ok": True})
   571	    return jsonify({"error": "not running"}), 409
   572	
   573	
   574	def _git_pull():
   575	    return subprocess.run(
   576	        [_git_binary(), "pull", "--ff-only"],
   577	        capture_output=True, encoding="utf-8", errors="replace", timeout=60, close_fds=False,
   578	    )
   579	
   580	
   581	@app.route("/api/sync", methods=["POST"])
   582	def api_sync():
   583	    """git pull the repo so today's committed scan/shortlist/backtest data
   584	    (from the scheduled GitHub Actions runs that send the email) shows up
   585	    here too, without the user having to leave the dashboard to do it."""
   586	    try:
   587	        # Absolute git path (not the bare "git", which posix_spawn eligibility
   588	        # requires — see the comment in _launch_job()) and no cwd= (process cwd
   589	        # is already PROJECT_ROOT, set once at startup).
   590	        result = _git_pull()
   591	
   592	        # A local job run (Full Scan / Positions / etc., all launched from
   593	        # this same dashboard) writes into the same data/ paths the automated
   594	        # workflow commits to — if you've run anything locally since the last
   595	        # sync, those two can diverge and block a fast-forward pull. Since
   596	        # data/ is always regenerable output (never something hand-authored),
   597	        # the automated commit is the one that actually matters here: discard
   598	        # the local modifications and retry once rather than surfacing a git
   599	        # merge error for what's really just stale scan output.
   600	        if result.returncode != 0 and "overwritten by merge" in (result.stdout + result.stderr):
   601	            subprocess.run(
   602	                [_git_binary(), "checkout", "--", "data/"],
   603	                capture_output=True, encoding="utf-8", errors="replace", timeout=30, close_fds=False,
   604	            )
   605	            result = _git_pull()
   606	
   607	        return jsonify({
   608	            "success": result.returncode == 0,
   609	            "output": (result.stdout + result.stderr).strip(),
   610	        })
   611	    except Exception as e:
   612	        return jsonify({"success": False, "output": str(e)})
   613	
   614	
   615	@app.route("/api/positions/upload", methods=["POST"])
   616	def api_positions_upload():
   617	    """Save a Fidelity Positions CSV export uploaded from the browser. Never
   618	    leaves this machine — no credentials, no login, just the file you already
   619	    downloaded yourself. Overwrites the previous upload (single "current
   620	    portfolio" file, not a history)."""
   621	    f = request.files.get("csv")
   622	    if not f or not f.filename:
   623	        return jsonify({"success": False, "error": "no file uploaded"}), 400
   624	    POSITIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
   625	    f.save(str(POSITIONS_CSV))
   626	    return jsonify({"success": True})
   627	
   628	
   629	@app.route("/api/positions")
   630	def api_positions():
   631	    """Last computed position analysis, if any. Empty/`reason` shape (not an
   632	    error) when nothing's been uploaded or analyzed yet, matching the other
   633	    read-only routes."""
   634	    has_csv = POSITIONS_CSV.exists()
   635	    data = _read_json(ADHOC_DIR / "positions_latest.json", None)
   636	    if data is None:
   637	        return jsonify({
   638	            "has_csv": has_csv,
   639	            "position_analyses": [], "summary": {"total_positions": 0}, "urgent_actions": [],
   640	        })
   641	    data["has_csv"] = has_csv
   642	    return jsonify(data)
   643	
   644	
   645	@app.route("/api/news/<group>")
   646	def api_news(group):
   647	    """Last fetched news batch for a group ("positions" or "buy"). Empty shape
   648	    (not an error) when nothing's been fetched yet."""
   649	    return jsonify(_read_json(ADHOC_DIR / f"news_{group}.json", {"generated": None, "tickers": [], "news": {}}))
   650	
   651	
   652	@app.route("/api/price-history/<group>")
   653	def api_price_history(group):
   654	    """Last fetched price-history batch for a group (e.g. "shortlist"). Empty
   655	    shape (not an error) when nothing's been fetched yet."""
   656	    return jsonify(_read_json(ADHOC_DIR / f"price_history_{group}.json", {"generated": None, "tickers": [], "prices": {}}))
   657	
   658	
   659	@app.route("/api/momentum-status/<group>")
   660	def api_momentum_status(group):
   661	    """Last computed hot/stable/basing/avoid classification (+ day-streak) for
   662	    a group. Empty shape (not an error) when nothing's been fetched yet."""
   663	    return jsonify(_read_json(ADHOC_DIR / f"momentum_status_{group}.json", {"generated": None, "tickers": [], "status": {}}))
   664	
   665	
   666	# ---------------------------------------------------------------------------
   667	# Read-only data routes
   668	# ---------------------------------------------------------------------------
   669	
   670	@app.route("/")
   671	def index():
   672	    return render_template("dashboard.html")
   673	
   674	
   675	@app.route("/api/scans")
   676	def api_scans():
   677	    return jsonify(get_scan_files())
   678	
   679	
   680	@app.route("/api/scan")
   681	def api_scan():
   682	    path = request.args.get("path", "")
   683	    if not path:
   684	        latest = SCAN_DIR / "latest_optimized_scan.txt"
   685	        if latest.exists():
   686	            path = str(latest)
   687	        else:
   688	            return jsonify({"error": "No scan data"})
   689	
   690	    if not Path(path).exists():
   691	        return jsonify({"error": "File not found"})
   692	
   693	    return jsonify(parse_scan_file(path))
   694	
   695	
   696	@app.route("/api/top20")
   697	def api_top20():
   698	    return jsonify(_read_json(SCAN_DIR / "top20_latest.json", {"generated": None, "top20": []}))
   699	
   700	
   701	@app.route("/api/shortlist")
   702	def api_shortlist():
   703	    return jsonify(_read_json(SCAN_DIR / "shortlist_latest.json", {
   704	        "generated": None, "shortlist": [],
   705	        "fundamentals_audits": {}, "catalyst_sentiments": {}, "congress_signals": {},
   706	    }))
   707	
   708	
   709	@app.route("/api/backtest/latest")
   710	def api_backtest_latest():
   711	    data = _read_json(BACKTEST_DIR / "latest.json", None)
   712	    if data is None:
   713	        return jsonify({"generated": None, "params": {}, "summary": {}, "component_correlations": {}, "trade_count": 0})
   714	    return jsonify({
   715	        "generated": data.get("generated"),
   716	        "params": data.get("params", {}),
   717	        "summary": data.get("summary", {}),
   718	        "component_correlations": data.get("component_correlations", {}),
   719	        "trade_count": len(data.get("trades", [])),
   720	    })
   721	
   722	
   723	@app.route("/api/backtest/trades")
   724	def api_backtest_trades():
   725	    path = request.args.get("path")
   726	    data = _read_json(path if path else (BACKTEST_DIR / "latest.json"), {"trades": []})
   727	    trades = data.get("trades", [])
   728	
   729	    # Cumulative P&L ordered by exit date — realized-P&L equity curve.
   730	    dated = [t for t in trades if t.get("exit_date")]
   731	    dated.sort(key=lambda t: t["exit_date"])
   732	    equity_curve = []
   733	    running = 0.0
   734	    for t in dated:
   735	        running += t.get("dollar_pnl", 0) or 0
   736	        equity_curve.append({"date": t["exit_date"], "cumulative_pnl": round(running, 2)})
   737	
   738	    return jsonify({"trades": trades, "equity_curve": equity_curve})
   739	
   740	
   741	@app.route("/api/backtest/history")
   742	def api_backtest_history():
   743	    return jsonify(get_backtest_files())
   744	
   745	
   746	@app.route("/api/backtest/run")
   747	def api_backtest_run():
   748	    path = request.args.get("path", "")
   749	    if not path or not Path(path).exists():
   750	        return jsonify({"error": "File not found"}), 404
   751	    return jsonify(_read_json(path, {}))
   752	
   753	
   754	def open_browser(port):
   755	    webbrowser.open(f"http://localhost:{port}")
   756	
   757	
   758	if __name__ == "__main__":
   759	    parser = argparse.ArgumentParser(description="Stock Screener Dashboard")
   760	    parser.add_argument("--port", type=int, default=5050)
   761	    parser.add_argument("--scan", action="store_true", help="Run a test scan before launching")
   762	    parser.add_argument("--full", action="store_true", help="With --scan, run full scan instead of test")
   763	    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
   764	    args = parser.parse_args()
   765	
   766	    if args.scan:
   767	        print("Running scan before dashboard launch...")
   768	        cmd = [_venv_python(), str(PROJECT_ROOT / "run_optimized_scan.py")]
   769	        if not args.full:
   770	            cmd.append("--test-mode")
   771	        subprocess.run(cmd)
   772	
   773	    if not args.no_browser:
   774	        Timer(1.5, open_browser, [args.port]).start()
   775	
   776	    print(f"\n  Dashboard running at http://localhost:{args.port}\n")
   777	    # 127.0.0.1, not 0.0.0.0: this app has zero authentication — every route
   778	    # (including git pull, running scans/backtests, and reading arbitrary
   779	    # local JSON files via the backtest ?path= params) is reachable by anyone
   780	    # who can open the URL. 0.0.0.0 would expose all of that to the whole
   781	    # LAN/WiFi, not just this machine. Matches mac_app/main.py, which already
   782	    # binds 127.0.0.1 for the packaged .app that most people actually run.
   783	    # threaded=True — see the matching comment in mac_app/main.py.
   784	    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True)
     1	#!/usr/bin/env python3
     2	"""py2app entry point for the Stock Screener.app bundle.
     3	
     4	Runs the real project's dashboard.py Flask app in a background thread, then
     5	opens it in its own native window via pywebview (no browser tabs/address bar)
     6	instead of the default browser — this is what makes it feel like a real app
     7	rather than "a terminal command that happens to open a browser tab."
     8	
     9	Imports dashboard.py as a module rather than duplicating its code, so any
    10	future edits to the dashboard are picked up automatically without rebuilding
    11	this .app. The bundle only carries a self-contained Python + Flask + pywebview
    12	runtime; all the actual behavior (reading/writing data/, running scripts via
    13	the project's own venv, git pull/push) still targets the real project folder.
    14	"""
    15	import os
    16	import sys
    17	import threading
    18	from pathlib import Path
    19	
    20	# This process loads Cocoa/WebKit (via pywebview below), which Apple documents
    21	# as unsafe to fork() from — and dashboard.py's background jobs (Run Simulation,
    22	# Full Scan, Positions, Sync) all fork()+exec() a subprocess. Without this, those
    23	# can fail with bizarre, hard-to-reproduce errors (e.g. a stdlib import failing
    24	# deep inside a C extension for no real reason) that don't happen when the same
    25	# subprocess is spawned from a plain terminal (no WebKit loaded there). Must be
    26	# set before pywebview/webview is imported.
    27	os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
    28	
    29	PROJECT_ROOT = Path(os.environ.get("STOCK_SCREENER_ROOT", str(Path.home() / "Desktop" / "stock-screener"))).resolve()
    30	
    31	if not (PROJECT_ROOT / "dashboard.py").exists():
    32	    sys.exit(
    33	        f"Stock Screener: couldn't find the project at {PROJECT_ROOT}.\n"
    34	        "Set STOCK_SCREENER_ROOT if the project folder has moved, then relaunch."
    35	    )
    36	
    37	sys.path.insert(0, str(PROJECT_ROOT))
    38	import dashboard  # noqa: E402 — the real project's dashboard.py; importing does NOT run its __main__ block
    39	
    40	PORT = 5050
    41	
    42	
    43	def _run_flask():
    44	    # threaded=True: the dashboard's own "Live" auto-refresh (positions, news,
    45	    # momentum-status, price-history, all on their own ~90s timers) plus
    46	    # auto-sync plus whatever job-status polling is in flight can easily have
    47	    # several requests in the air at once. Werkzeug's dev server defaults to
    48	    # handling one request at a time; under that, a single slow request (e.g.
    49	    # a git pull, or a big JSON payload for a long-running scan's output)
    50	    # blocks every other request — including a plain page load — until it
    51	    # finishes, which reads as "the app just isn't opening."
    52	    dashboard.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)
    53	
    54	
    55	threading.Thread(target=_run_flask, daemon=True).start()
    56	
    57	import webview  # noqa: E402
    58	
    59	webview.create_window(
    60	    "Stock Screener", f"http://127.0.0.1:{PORT}",
    61	    width=1440, height=900, min_size=(900, 600),
    62	)
    63	webview.start()
     1	"""py2app build config for Stock Screener.app.
     2	
     3	Build (from the project root, using the project's own venv so Flask etc. are
     4	available to bundle):
     5	    venv/bin/pip install py2app          # one-time
     6	    cd mac_app && ../venv/bin/python setup.py py2app
     7	    open dist/Stock\\ Screener.app
     8	
     9	Bundles Flask + its own dependencies, plus pywebview and its macOS backend
    10	(pyobjc's Cocoa/WebKit bridge) — dashboard.py never imports pandas/yfinance/
    11	etc. directly, it shells out to the project's real venv (venv/bin/python) to
    12	run scripts, so there's no scientific-Python packaging to fight here.
    13	"""
    14	from setuptools import setup
    15	
    16	APP = ['main.py']
    17	OPTIONS = {
    18	    'argv_emulation': False,
    19	    'iconfile': 'assets/AppIcon.icns',
    20	    'plist': {
    21	        'CFBundleName': 'Stock Screener',
    22	        'CFBundleDisplayName': 'Stock Screener',
    23	        'CFBundleIdentifier': 'com.stockscreener.dashboard',
    24	        'CFBundleShortVersionString': '1.0.0',
    25	        'CFBundleVersion': '1.0.0',
    26	        'LSUIElement': False,  # show a Dock icon (it's a real app, not a background agent)
    27	        'NSHighResolutionCapable': True,
    28	    },
    29	    'packages': [
    30	        'flask', 'jinja2', 'werkzeug', 'click', 'itsdangerous', 'markupsafe', 'blinker',
    31	        'webview', 'objc', 'Cocoa', 'WebKit', 'Quartz', 'Security', 'UniformTypeIdentifiers',
    32	    ],
    33	}
    34	
    35	setup(
    36	    app=APP,
    37	    name='Stock Screener',
    38	    options={'py2app': OPTIONS},
    39	    setup_requires=['py2app'],
    40	)
     1	# Stock Screener.app
     2	
     3	A standalone macOS app wrapper around `dashboard.py`. It bundles its own Python + Flask + pywebview runtime (via py2app) so it can be double-clicked from Applications/Dock/Launchpad without needing a terminal or the project's venv activated — and it opens in its own native window (via `pywebview`, using macOS's WebKit), not a browser tab.
     4	
     5	`mac_app/main.py` runs the real `dashboard.py`'s Flask app in a background thread, then opens a `pywebview` window pointed at it — no `webbrowser.open()` call in this path at all, so launching/relaunching the app never pops open your default browser.
     6	
     7	It still operates on the real project checkout on disk (`~/Desktop/stock-screener` by default, override with the `STOCK_SCREENER_ROOT` env var if you move the folder) — data files, git pull/push (the Sync button), and running backtest scripts all go through the real repo and its own `venv/bin/python`, exactly like running `python dashboard.py` normally. The app bundle itself only needs to run Flask + pywebview; the heavier dependencies (pandas, yfinance, etc.) are never bundled since `dashboard.py` shells out to scripts rather than importing them directly.
     8	
     9	## Rebuilding after changes
    10	
    11	Only needed if you change `dashboard.py`'s dependencies (not needed for changes to routes/logic/HTML/CSS/JS — those are read live from the real project folder, no rebuild required):
    12	
    13	```bash
    14	venv/bin/pip install py2app pywebview   # one-time
    15	cd mac_app
    16	rm -rf build dist
    17	../venv/bin/python setup.py py2app
    18	```
    19	
    20	### Known gotcha: conda-linked native libraries
    21	
    22	On this machine, the venv's Python is a conda-based interpreter, and several of its C extensions link against `@rpath/lib*.dylib` copies that live in `~/miniconda3/lib/` rather than a system path — py2app's dependency walker doesn't reliably follow those. Two hit so far: `ctypes` needs `libffi.8.dylib`; `ssl` (imported by `pywebview.http`) needs `libssl.3.dylib` + `libcrypto.3.dylib`. If the built app fails silently (or shows an `ImportError: ... Library not loaded` when run directly from the terminal — see Debugging below), fix each missing one the same way:
    23	
    24	```bash
    25	APP="dist/Stock Screener.app"
    26	for lib in libffi.8.dylib libssl.3.dylib libcrypto.3.dylib; do
    27	  cp ~/miniconda3/lib/"$lib" "$APP/Contents/Frameworks/"
    28	  install_name_tool -id "@rpath/$lib" "$APP/Contents/Frameworks/$lib"
    29	done
    30	codesign --force --deep --sign - "$APP"
    31	```
    32	
    33	If a *different* missing library shows up later, the pattern is the same: `otool -L` the `.so`/`.dylib` the traceback names to find what it's looking for, locate the real one under `~/miniconda3/lib/`, copy it into `Contents/Frameworks/`, fix its `-id` to `@rpath/<name>`, re-sign.
    34	
    35	Then reinstall: `cp -R "dist/Stock Screener.app" "/Applications/Stock Screener.app"` (or drag it in Finder).
    36	
    37	## Debugging a launch failure
    38	
    39	Run the binary directly to see real output instead of it failing silently:
    40	```bash
    41	"/Applications/Stock Screener.app/Contents/MacOS/Stock Screener"
    42	```
dashboard.py:2:"""Interactive web dashboard for Stock Screener results.
dashboard.py:5:    python dashboard.py                    # Start dashboard on port 5050
dashboard.py:6:    python dashboard.py --port 8080        # Custom port
dashboard.py:7:    python dashboard.py --scan             # Run test scan first, then launch
dashboard.py:8:    python dashboard.py --scan --full      # Run full scan first, then launch
dashboard.py:27:# When bundled as a standalone .app (py2app sets sys.frozen), this file lives
dashboard.py:29:# the dashboard always needs to read/write the real repo (git pull/push via
dashboard.py:39:# py2app's own bootstrap chdir's the frozen process into the .app bundle's
dashboard.py:47:app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"), static_folder=str(PROJECT_ROOT / "static"))
dashboard.py:308:# How long a job is allowed to run before the dashboard force-kills it. Needed
dashboard.py:315:# socket — which is what took the whole dashboard offline last time this
dashboard.py:329:                "[dashboard] job exceeded its time limit and was terminated — "
dashboard.py:347:        # subprocess failures. main()/dashboard.py's own process cwd is set to
dashboard.py:401:            JOBS[job_id]["output"].append(f"[dashboard] failed to launch: {exc}")
dashboard.py:507:def _prune_old_jobs():
dashboard.py:508:    """Drop finished jobs older than JOB_RETENTION_SECONDS. Without this, JOBS
dashboard.py:509:    grows without bound — the dashboard's own "Live" auto-refresh (every 90s,
dashboard.py:524:@app.route("/api/jobs/<kind>", methods=["POST"])
dashboard.py:534:    _prune_old_jobs()
dashboard.py:545:@app.route("/api/jobs/<job_id>")
dashboard.py:559:@app.route("/api/jobs/<job_id>/stop", methods=["POST"])
dashboard.py:585:    here too, without the user having to leave the dashboard to do it."""
dashboard.py:593:        # this same dashboard) writes into the same data/ paths the automated
dashboard.py:672:    return render_template("dashboard.html")
dashboard.py:767:        print("Running scan before dashboard launch...")
README.md:56:**Problem:** Most stock screeners rely on static fundamental metrics (P/E, P/B) or generic technical patterns that don't adapt to market conditions. They ignore:
README.md:771:  - Web dashboard for historical tracking
README.md:835:  - Interactive dashboard for browsing signals
templates/dashboard.html:8:<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
templates/dashboard.html:54:<script src="{{ url_for('static', filename='js/charts.js') }}"></script>
templates/dashboard.html:55:<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
static/js/dashboard.js:1:// Stock Screener dashboard — vanilla JS single-page app. Hash-based routing
static/js/dashboard.js:2:// (no router library), fetch() for data, Chart.js (via charts.js) for charts.
static/js/dashboard.js:47:const LIVE_INTERVAL_MS = 90 * 1000; // 90 seconds — cheap yfinance-only pulls, no LLM cost
static/js/dashboard.js:55:  _liveTimer = setInterval(fn, LIVE_INTERVAL_MS);
static/js/dashboard.js:75:// Chart toggle buttons (Positions + Shortlist share this). Open/closed state
static/js/dashboard.js:80:const _openCharts = new Set();
static/js/dashboard.js:89:function wireChartToggles(container, getSeries, idPrefix) {
static/js/dashboard.js:96:    if (_openCharts.has(chartId)) {
static/js/dashboard.js:100:      if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
static/js/dashboard.js:108:        _openCharts.add(chartId);
static/js/dashboard.js:110:        if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
static/js/dashboard.js:112:        _openCharts.delete(chartId);
static/js/dashboard.js:120:function refreshOpenCharts(getSeries, idPrefix) {
static/js/dashboard.js:121:  _openCharts.forEach(chartId => {
static/js/dashboard.js:126:    if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
static/js/dashboard.js:174:  t._timer = setTimeout(() => { t.style.opacity = '0'; }, 5000);
static/js/dashboard.js:192:// could otherwise execute JS in the dashboard's own origin, which has several
static/js/dashboard.js:228:// the dashboard and the email read consistently.
static/js/dashboard.js:273:  const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
static/js/dashboard.js:278:      const st = await fetchJSON(`/api/jobs/${job_id}`);
static/js/dashboard.js:281:        setTimeout(poll, 1500);
static/js/dashboard.js:302:// Job cards (Run Simulation, Full Scan) kick off long-running background jobs
static/js/dashboard.js:311:const _watchingJobIds = {}; // cardId -> job_id an active setTimeout poll loop is already chasing
static/js/dashboard.js:316:  // forth while it runs) would otherwise stack up a duplicate setTimeout
static/js/dashboard.js:323:    const st = await fetchJSON(`/api/jobs/${jobId}`);
static/js/dashboard.js:325:      // The server prunes finished jobs after a while — if you reconnect to
static/js/dashboard.js:355:      setTimeout(poll, 1500);
static/js/dashboard.js:384:    // click can't start two overlapping jobs for the same card.
static/js/dashboard.js:392:    const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
static/js/dashboard.js:459:  loadShortlistCharts(tickers);
static/js/dashboard.js:463:    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
static/js/dashboard.js:477:async function loadShortlistCharts(tickers, silent) {
static/js/dashboard.js:492:      wireChartToggles(content, _shortlistSeries, 'short-chart-');
static/js/dashboard.js:495:      refreshOpenCharts(_shortlistSeries, 'short-chart-');
static/js/dashboard.js:662:      <div class="card"><h2>Market Breadth</h2><div class="chart-wrap"><canvas id="breadthChart"></canvas></div></div>
static/js/dashboard.js:688:  renderBreadthChart('breadthChart', scan.breadth);
static/js/dashboard.js:918:  wireChartToggles(resultsEl, (ticker) => {
static/js/dashboard.js:982:      <div class="card"><h2>Cumulative P&amp;L (by exit date)</h2><div class="chart-wrap"><canvas id="equityChart"></canvas></div></div>
static/js/dashboard.js:983:      <div class="card"><h2>Exit Reasons</h2><div class="chart-wrap"><canvas id="exitChart"></canvas></div></div>
static/js/dashboard.js:996:  renderEquityCurveChart('equityChart', tradesData.equity_curve || []);
static/js/dashboard.js:997:  renderExitReasonChart('exitChart', summary.exit_reasons || {});
static/js/dashboard.js:1152:const AUTO_SYNC_INTERVAL_MS = 5 * 60 * 1000;
static/js/dashboard.js:1153:setInterval(() => doSync(true), AUTO_SYNC_INTERVAL_MS);
mac_app/setup.py:1:"""py2app build config for Stock Screener.app.
mac_app/setup.py:5:    venv/bin/pip install py2app          # one-time
mac_app/setup.py:6:    cd mac_app && ../venv/bin/python setup.py py2app
mac_app/setup.py:10:(pyobjc's Cocoa/WebKit bridge) — dashboard.py never imports pandas/yfinance/
mac_app/setup.py:23:        'CFBundleIdentifier': 'com.stockscreener.dashboard',
mac_app/setup.py:38:    options={'py2app': OPTIONS},
mac_app/setup.py:39:    setup_requires=['py2app'],
static/js/charts.js:1:// Chart.js render helpers. Each function destroys any previous instance on
static/js/charts.js:7:function _destroyChart(canvasId) {
static/js/charts.js:14:function renderBreadthChart(canvasId, breadth) {
static/js/charts.js:15:  _destroyChart(canvasId);
static/js/charts.js:17:  _chartInstances[canvasId] = new Chart(ctx, {
static/js/charts.js:39:function renderEquityCurveChart(canvasId, equityCurve) {
static/js/charts.js:40:  _destroyChart(canvasId);
static/js/charts.js:45:  _chartInstances[canvasId] = new Chart(ctx, {
static/js/charts.js:75:function renderExitReasonChart(canvasId, exitReasons) {
static/js/charts.js:76:  _destroyChart(canvasId);
static/js/charts.js:81:  _chartInstances[canvasId] = new Chart(ctx, {
static/js/charts.js:107:function renderPositionChart(canvasId, priceHistory, entryPrice, stopLoss) {
static/js/charts.js:108:  _destroyChart(canvasId);
static/js/charts.js:134:  _chartInstances[canvasId] = new Chart(ctx, {
mac_app/README.md:3:A standalone macOS app wrapper around `dashboard.py`. It bundles its own Python + Flask + pywebview runtime (via py2app) so it can be double-clicked from Applications/Dock/Launchpad without needing a terminal or the project's venv activated — and it opens in its own native window (via `pywebview`, using macOS's WebKit), not a browser tab.
mac_app/README.md:5:`mac_app/main.py` runs the real `dashboard.py`'s Flask app in a background thread, then opens a `pywebview` window pointed at it — no `webbrowser.open()` call in this path at all, so launching/relaunching the app never pops open your default browser.
mac_app/README.md:7:It still operates on the real project checkout on disk (`~/Desktop/stock-screener` by default, override with the `STOCK_SCREENER_ROOT` env var if you move the folder) — data files, git pull/push (the Sync button), and running backtest scripts all go through the real repo and its own `venv/bin/python`, exactly like running `python dashboard.py` normally. The app bundle itself only needs to run Flask + pywebview; the heavier dependencies (pandas, yfinance, etc.) are never bundled since `dashboard.py` shells out to scripts rather than importing them directly.
mac_app/README.md:11:Only needed if you change `dashboard.py`'s dependencies (not needed for changes to routes/logic/HTML/CSS/JS — those are read live from the real project folder, no rebuild required):
mac_app/README.md:14:venv/bin/pip install py2app pywebview   # one-time
mac_app/README.md:17:../venv/bin/python setup.py py2app
mac_app/README.md:22:On this machine, the venv's Python is a conda-based interpreter, and several of its C extensions link against `@rpath/lib*.dylib` copies that live in `~/miniconda3/lib/` rather than a system path — py2app's dependency walker doesn't reliably follow those. Two hit so far: `ctypes` needs `libffi.8.dylib`; `ssl` (imported by `pywebview.http`) needs `libssl.3.dylib` + `libcrypto.3.dylib`. If the built app fails silently (or shows an `ImportError: ... Library not loaded` when run directly from the terminal — see Debugging below), fix each missing one the same way:
mac_app/main.py:2:"""py2app entry point for the Stock Screener.app bundle.
mac_app/main.py:4:Runs the real project's dashboard.py Flask app in a background thread, then
mac_app/main.py:9:Imports dashboard.py as a module rather than duplicating its code, so any
mac_app/main.py:10:future edits to the dashboard are picked up automatically without rebuilding
mac_app/main.py:21:# as unsafe to fork() from — and dashboard.py's background jobs (Run Simulation,
mac_app/main.py:31:if not (PROJECT_ROOT / "dashboard.py").exists():
mac_app/main.py:38:import dashboard  # noqa: E402 — the real project's dashboard.py; importing does NOT run its __main__ block
mac_app/main.py:44:    # threaded=True: the dashboard's own "Live" auto-refresh (positions, news,
mac_app/main.py:52:    dashboard.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)

[35m[3mcodex[0m[0m
The central issue is already visible: the app has useful safeguards and capable features, but presentation, state, rendering, and polling all live in one global script. I’m tracing those coupling points now so the recommendation preserves behavior instead of treating this as a cosmetic reskin.
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba dashboard.py | sed -n '480,790p'; git status --short; rg -n \"inline|style=|innerHTML|addEventListener|fetchJSON|startJob|_startLive|_liveGuarded\" static/js/dashboard.js | awk -F: '{count["'$3]++} END{}'"' ; printf 'inline_style_count '; rg -o 'style=\"' static/js/dashboard.js templates/dashboard.html | wc -l; printf 'innerHTML_count '; rg -o 'innerHTML' static/js/dashboard.js | wc -l; printf 'fetchJSON_count '; rg -o 'fetchJSON\\(' static/js/dashboard.js | wc -l; printf 'test_dashboard_refs '; rg -l \"dashboard|/api/jobs|positions/upload\" tests | wc -l; find . -maxdepth 2 -iname 'package.json' -o -iname '*playwright*' -o -iname '*vite*' -o -iname '*webpack*'"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 57ms:[0m
?? .sprint/council/
?? position/
inline_style_count       73
innerHTML_count       41
fetchJSON_count       25
test_dashboard_refs        0

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba dashboard.py | sed -n '406,505p'; nl -ba templates/dashboard.html; nl -ba static/css/dashboard.css | sed -n '1,220p'; nl -ba mac_app/main.py | sed -n '1,90p'; nl -ba mac_app/setup.py | sed -n '1,70p'"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 9ms:[0m
     1	#!/usr/bin/env python3
     2	"""py2app entry point for the Stock Screener.app bundle.
     3	
     4	Runs the real project's dashboard.py Flask app in a background thread, then
     5	opens it in its own native window via pywebview (no browser tabs/address bar)
     6	instead of the default browser — this is what makes it feel like a real app
     7	rather than "a terminal command that happens to open a browser tab."
     8	
     9	Imports dashboard.py as a module rather than duplicating its code, so any
    10	future edits to the dashboard are picked up automatically without rebuilding
    11	this .app. The bundle only carries a self-contained Python + Flask + pywebview
    12	runtime; all the actual behavior (reading/writing data/, running scripts via
    13	the project's own venv, git pull/push) still targets the real project folder.
    14	"""
    15	import os
    16	import sys
    17	import threading
    18	from pathlib import Path
    19	
    20	# This process loads Cocoa/WebKit (via pywebview below), which Apple documents
    21	# as unsafe to fork() from — and dashboard.py's background jobs (Run Simulation,
    22	# Full Scan, Positions, Sync) all fork()+exec() a subprocess. Without this, those
    23	# can fail with bizarre, hard-to-reproduce errors (e.g. a stdlib import failing
    24	# deep inside a C extension for no real reason) that don't happen when the same
    25	# subprocess is spawned from a plain terminal (no WebKit loaded there). Must be
    26	# set before pywebview/webview is imported.
    27	os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
    28	
    29	PROJECT_ROOT = Path(os.environ.get("STOCK_SCREENER_ROOT", str(Path.home() / "Desktop" / "stock-screener"))).resolve()
    30	
    31	if not (PROJECT_ROOT / "dashboard.py").exists():
    32	    sys.exit(
    33	        f"Stock Screener: couldn't find the project at {PROJECT_ROOT}.\n"
    34	        "Set STOCK_SCREENER_ROOT if the project folder has moved, then relaunch."
    35	    )
    36	
    37	sys.path.insert(0, str(PROJECT_ROOT))
    38	import dashboard  # noqa: E402 — the real project's dashboard.py; importing does NOT run its __main__ block
    39	
    40	PORT = 5050
    41	
    42	
    43	def _run_flask():
    44	    # threaded=True: the dashboard's own "Live" auto-refresh (positions, news,
    45	    # momentum-status, price-history, all on their own ~90s timers) plus
    46	    # auto-sync plus whatever job-status polling is in flight can easily have
    47	    # several requests in the air at once. Werkzeug's dev server defaults to
    48	    # handling one request at a time; under that, a single slow request (e.g.
    49	    # a git pull, or a big JSON payload for a long-running scan's output)
    50	    # blocks every other request — including a plain page load — until it
    51	    # finishes, which reads as "the app just isn't opening."
    52	    dashboard.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)
    53	
    54	
    55	threading.Thread(target=_run_flask, daemon=True).start()
    56	
    57	import webview  # noqa: E402
    58	
    59	webview.create_window(
    60	    "Stock Screener", f"http://127.0.0.1:{PORT}",
    61	    width=1440, height=900, min_size=(900, 600),
    62	)
    63	webview.start()
     1	"""py2app build config for Stock Screener.app.
     2	
     3	Build (from the project root, using the project's own venv so Flask etc. are
     4	available to bundle):
     5	    venv/bin/pip install py2app          # one-time
     6	    cd mac_app && ../venv/bin/python setup.py py2app
     7	    open dist/Stock\\ Screener.app
     8	
     9	Bundles Flask + its own dependencies, plus pywebview and its macOS backend
    10	(pyobjc's Cocoa/WebKit bridge) — dashboard.py never imports pandas/yfinance/
    11	etc. directly, it shells out to the project's real venv (venv/bin/python) to
    12	run scripts, so there's no scientific-Python packaging to fight here.
    13	"""
    14	from setuptools import setup
    15	
    16	APP = ['main.py']
    17	OPTIONS = {
    18	    'argv_emulation': False,
    19	    'iconfile': 'assets/AppIcon.icns',
    20	    'plist': {
    21	        'CFBundleName': 'Stock Screener',
    22	        'CFBundleDisplayName': 'Stock Screener',
    23	        'CFBundleIdentifier': 'com.stockscreener.dashboard',
    24	        'CFBundleShortVersionString': '1.0.0',
    25	        'CFBundleVersion': '1.0.0',
    26	        'LSUIElement': False,  # show a Dock icon (it's a real app, not a background agent)
    27	        'NSHighResolutionCapable': True,
    28	    },
    29	    'packages': [
    30	        'flask', 'jinja2', 'werkzeug', 'click', 'itsdangerous', 'markupsafe', 'blinker',
    31	        'webview', 'objc', 'Cocoa', 'WebKit', 'Quartz', 'Security', 'UniformTypeIdentifiers',
    32	    ],
    33	}
    34	
    35	setup(
    36	    app=APP,
    37	    name='Stock Screener',
    38	    options={'py2app': OPTIONS},
    39	    setup_requires=['py2app'],
    40	)

[35m[3mcodex[0m[0m
## 1. Understanding of the problem

“Completely updated” should mean more than changing colors and border radii. The dashboard needs:

- Clear information architecture: monitoring, research, history, and execution should feel like distinct groups.
- Consistent visual hierarchy across all six views.
- Reusable interaction patterns for cards, tables, forms, loading, errors, jobs, and empty states.
- Better data density and scanability without hiding important trading context.
- Explicit feedback for freshness, syncing, long-running operations, and failures.
- Keyboard accessibility, visible focus states, adequate contrast, and reduced-motion support.
- Reliable behavior inside the 900×600 minimum pywebview window as well as the normal 1440×900 size.

The backend/API model is already broadly suitable. This is primarily a frontend architecture and product-design problem, with polling and packaging constraints that must be preserved.

## 2. Root cause / architectural challenge

The UI feels unstructured because the presentation system is fragmented even though the feature set is substantial.

- Navigation is one undifferentiated list of six destinations. Monitoring pages, historical analysis, and destructive/expensive actions have equal visual weight in [dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:13).
- The shell provides only a title, free-form metadata, and a global Sync button. Views must invent their own hierarchy inside `content` ([dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:42)).
- The CSS has a small color palette, but not a complete design system. There are no semantic typography, spacing, elevation, focus, control-size, responsive, or light-theme tokens ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1)).
- Responsiveness is minimal: only `.grid-2` has an explicit breakpoint, while the sidebar remains fixed at 220px and tables depend on horizontal scrolling ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:21), [dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:54)).
- `dashboard.js` is 1,156 lines containing routing, API access, escaping, polling, job lifecycle, state, event binding, and all six view templates. That makes consistent UX changes risky and encourages one-off markup ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1)).
- There are approximately 73 inline `style` attributes and 41 `innerHTML` operations. For example, the Market view defines layout, color, tables, metrics, and chart containers in one large string ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:653)). This bypasses reusable CSS patterns and scatters behavior through DOM IDs.
- Each screen uses slightly different loading, error, empty-state, and action conventions. `fetchJSON`, for example, assumes every response is valid JSON and does not check HTTP status ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:164)).
- The UI uses very small 10–13px text extensively, particularly secondary navigation, table headers, badges, and descriptions. That increases visual density without establishing useful hierarchy.
- The current implementation has valuable but subtle concurrency behavior embedded inside UI code: route race checks, refresh guards, preserved chart state, and job reconnection. A wholesale renderer rewrite could easily discard these protections ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:17), [dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:61), [dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:302)).

## 3. Relevant files/modules

Primary UI:

- [templates/dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:1) — application shell, navigation, CDN Chart.js dependency.
- [static/css/dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1) — entire visual system.
- [static/js/dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1) — routing, rendering, state, jobs, live refresh, sync.
- [static/js/charts.js](/Users/badripratti/Desktop/stock-screener/static/js/charts.js:1) — Chart.js lifecycle and hard-coded chart theme.

Backend and lifecycle:

- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:47) — Flask/static configuration.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:280) — background subprocess/job implementation.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:524) — job API.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:670) — dashboard and data routes.
- [mac_app/main.py](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:29) — live project-root loading and threaded pywebview host.
- [mac_app/setup.py](/Users/badripratti/Desktop/stock-screener/mac_app/setup.py:16) — py2app contents.
- [mac_app/README.md](/Users/badripratti/Desktop/stock-screener/mac_app/README.md:9) — current “frontend changes require no app rebuild” deployment assumption.

There are currently no dashboard/API/polling tests under `tests/`.

## 4. Recommended solution

Use a design-system-on-vanilla-JS approach, combined with a serious modular refactor. Do not introduce React/Vue or a required runtime build step for this iteration.

The application has only six routes, no authentication or collaborative state, and relatively simple interactions. Its complexity comes from asynchronous jobs and refresh lifecycle—not from a component tree that requires a virtual DOM. A framework would reorganize the code, but it would not automatically solve the product hierarchy and would substantially increase rewrite and packaging risk.

### Proposed frontend structure

Use native ES modules served directly by Flask:

```text
static/js/
  app.js
  core/
    api.js
    router.js
    jobs.js
    refresh.js
    state.js
  components/
    page-header.js
    metric-card.js
    data-table.js
    status.js
    job-panel.js
    empty-state.js
  views/
    positions.js
    shortlist.js
    market.js
    backtests.js
    simulations.js
    scan.js
  charts/
    theme.js
    renderers.js
```

These can run directly in WebKit using `<script type="module">`; no bundler is required.

### Information architecture

Group navigation by intent:

- Monitor: Positions, Shortlist, Market
- Analyze: Backtests
- Run: Simulations, Full Scan

Make expensive actions visually distinct from passive monitoring. Give every screen the same header anatomy:

- Title and one-line purpose
- “Last updated” or selected snapshot
- Live/sync state
- Contextual primary action

Resolve the current default-route inconsistency: routing defaults to Positions, while the Shortlist section is commented as the default landing view ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:26), [dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:399)).

### Design system

Expand CSS custom properties into semantic tokens:

- Canvas/surface/elevated/overlay colors
- Primary, success, warning, danger, and neutral roles
- Typography scale and tabular-number styles
- 4/8px spacing scale
- Control heights
- Radius, border, shadow, and focus-ring tokens
- Dense and comfortable table/card modes
- Breakpoints and reduced-motion behavior

Build standardized components for buttons, icon buttons, inputs, alerts, status pills, skeletons, empty/error states, cards, tables, and page sections. Eliminate nearly all inline styles.

A light theme is optional; consistency and readability matter more than adding a theme toggle. The existing dark appearance can remain the default.

### Screen-level improvements

- Positions: lead with portfolio health and required actions; make upload/update secondary once data exists; sort urgent adjustments first.
- Shortlist: emphasize rank, recommendation quality, and risks; collapse verbose agent evidence behind accessible disclosures.
- Market: use summary → regime/breadth → ranked opportunities → sells → news. Add filtering/search and sticky table headers.
- Backtests: show selected run and parameters clearly; expose sort state visually and support keyboard sorting.
- Simulations: turn raw parameter cards into a structured form with validation, sensible ranges, estimated duration, and durable job status.
- Full Scan: explicitly separate Quick Scan and Full Scan choices rather than hiding the distinction in a checkbox; warn about the 15–30 minute operation before launch.
- Global status: distinguish “market data refreshed,” “repository synced,” and “background job running.” They are currently easy to conflate.

### Polling architecture

Extract polling before redesigning views:

- A route-scoped refresh controller owns the 90-second interval and aborts or ignores obsolete UI fetches.
- A global job manager owns 1.5-second job observation and survives navigation.
- Auto-sync remains an application-level service.
- Keep the current non-overlap guarantee.
- Use render-generation tokens or `AbortController` so stale requests cannot paint a later route.
- Do not cancel server subprocesses merely because their screen unmounted.
- Preserve finished-job reconnection and open-chart state explicitly.

### Framework decision

React/Vue is not justified today. It becomes reasonable if the roadmap adds several of the following:

- Many more interactive routes
- Shared editable state across screens
- Multi-user/authenticated workflows
- Complex drill-downs or nested routing
- A team already standardized on TypeScript/component tooling
- A maintained frontend release pipeline

If that point arrives, React/Vue with Vite is preferable to incrementally turning the global script into an ad hoc framework. For this iteration, native modules produce most of the maintainability benefit with much less operational change.

## 5. Alternatives considered

- CSS-only reskin: fastest, but leaves the monolithic rendering and inconsistent states intact. It would look newer without becoming materially easier to use.
- React/Vue/Vite rewrite: strongest formal component model, but highest regression surface around jobs, navigation, and refresh. Adds tooling disproportionate to six local-only views.
- HTMX/Jinja partials: could reduce client rendering, but requires moving presentation into Flask endpoints and reworking polling responses. It does not fit the existing JSON/job API particularly well.
- Web Components or Lit: a reasonable middle ground if reusable components become much more complex, but unnecessary for the current component count.
- Adopt a full CSS library: may speed up controls, but tends to produce generic visuals and adds another dependency. A small app-specific token/component layer is easier to package and tune for dense financial data.

## 6. Risks

### Packaging/build

The native app deliberately imports `dashboard.py` and serves `templates/` and `static/` from the live checkout ([mac_app/main.py](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:29), [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:47)). Therefore:

- Native ES modules and CSS require no py2app change.
- A Vite/webpack build would require generated assets to be committed or built before every release.
- Hashed output would need a manifest integrated with Flask/Jinja.
- The macOS app must never depend on Node being installed at runtime.
- If assets were moved into the `.app` bundle, `setup.py` would need explicit resource/data-file handling and the current live-update model would change.
- WebKit compatibility must be tested against the oldest supported macOS version.

Chart.js currently loads from jsDelivr ([dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:7)). The native app can lose charts when offline or when CDN access is blocked. Vendor the pinned Chart.js build into `static/vendor/`.

### Refresh and jobs

Critical behaviors to preserve:

- 90-second refresh cadence ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:47)).
- No overlapping refresh jobs ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:64)).
- 1.5-second job polling ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:272)).
- Job observation across navigation ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:310)).
- Five-minute application-level auto-sync ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1148)).
- Threaded Flask operation, which is necessary for concurrent refresh and polling requests ([mac_app/main.py](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:43)).

The current pollers have weak network-error handling. A failed `fetchJSON` inside a timer can leave a promise unresolved or a UI stuck in “running.” The refactor should add retry/backoff and explicit disconnected states without changing server-job semantics.

## 7. Edge cases

- Empty first-run state: no scans, shortlist, backtests, or positions CSV.
- Partial or malformed historical JSON and scan text.
- Network loss during yfinance/news jobs or while Chart.js would otherwise load.
- Navigating rapidly while initial fetches or refresh jobs are running.
- Auto-sync pulling new data while the user is editing simulation parameters. `doSync()` currently calls `route()`, which can destroy unsaved form state ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1119)).
- A job finishing after its view has unmounted.
- Reloading the entire window loses client `_activeJobs`, even though the server job may still exist.
- Duplicate tickers across Positions, Shortlist, and Market sharing DOM ID conventions.
- Very large signal/reason tables and long news or LLM-generated text.
- Invalid numeric parameters, negative investments, extreme iteration counts, and full-scan double submission.
- Selected historical Market scan versus `/api/top20`, which always returns the latest Top 20; the page can therefore combine different snapshots.
- Color-blind users: green/red must not be the only action or performance indicator.
- 900×600 native window, large system font settings, and keyboard-only use.
- Reduced motion for pulsing live indicators and spinners.

## 8. Testing strategy

Before changing presentation, add behavior characterization tests.

- Flask API tests using `app.test_client()` for empty states, uploads, path validation, job creation/status/stop, and malformed data.
- Browser integration tests covering every hash route and representative empty/populated/error fixtures.
- Fake timers for 90-second refresh, five-minute sync, and 1.5-second job polling.
- Tests for no overlapping live jobs and no stale DOM writes after navigation.
- Navigation-away-and-back tests for running and completed jobs.
- Tests proving auto-sync does not discard active form input unexpectedly.
- Chart lifecycle tests ensuring removed canvases do not retain Chart.js instances.
- Accessibility checks: landmarks, headings, labels, focus order, keyboard table sorting, contrast, and `aria-live` status announcements.
- Visual regression screenshots at 1440×900 and 900×600, including long data, empty states, loading, errors, and active jobs.
- A real packaged-app smoke test on macOS/WebKit: startup, all routes, offline charts, upload dialog, external links, sync, one short job, and one 90-second refresh cycle.

## 9. Assumptions

- This remains a single-user, localhost-only application.
- The six current workflows are the near-term product scope.
- Existing JSON API shapes and subprocess scripts should remain stable.
- Supporting the packaged macOS app is at least as important as browser development convenience.
- A committed vendored dependency is acceptable, while requiring Node at runtime is not.
- “Modern” prioritizes clarity, confidence, and operational feedback over animation or decorative novelty.

## 10. Easily missed issues

- The frontend is not included in the py2app bundle; it is read from the real checkout. That is why UI edits currently require no app rebuild.
- Chart colors are hard-coded separately in `charts.js`, so a CSS redesign alone will leave charts visually inconsistent ([charts.js](/Users/badripratti/Desktop/stock-screener/static/js/charts.js:14)).
- Charts are destroyed only when the same canvas ID is rendered again; route changes do not centrally dispose all removed chart instances.
- The backend offers a stop endpoint, but the current UI exposes no Stop control ([dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:559)).
- Finished jobs are retained server-side for only 15 minutes, while client reconnection state is memory-only ([dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:504)).
- Escaping is applied carefully to some external news/LLM content, but not consistently to every interpolated field or link. Component extraction should centralize safe text and URL rendering.
- The backtest and scan APIs accept filesystem paths supplied by query parameters ([dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:680), [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:723)). Localhost binding reduces exposure, but paths should still be constrained to approved data directories.
- There are currently no automated dashboard tests, making a one-shot rewrite especially risky.

No files were modified.
[2mtokens used[0m
67,999
## 1. Understanding of the problem

“Completely updated” should mean more than changing colors and border radii. The dashboard needs:

- Clear information architecture: monitoring, research, history, and execution should feel like distinct groups.
- Consistent visual hierarchy across all six views.
- Reusable interaction patterns for cards, tables, forms, loading, errors, jobs, and empty states.
- Better data density and scanability without hiding important trading context.
- Explicit feedback for freshness, syncing, long-running operations, and failures.
- Keyboard accessibility, visible focus states, adequate contrast, and reduced-motion support.
- Reliable behavior inside the 900×600 minimum pywebview window as well as the normal 1440×900 size.

The backend/API model is already broadly suitable. This is primarily a frontend architecture and product-design problem, with polling and packaging constraints that must be preserved.

## 2. Root cause / architectural challenge

The UI feels unstructured because the presentation system is fragmented even though the feature set is substantial.

- Navigation is one undifferentiated list of six destinations. Monitoring pages, historical analysis, and destructive/expensive actions have equal visual weight in [dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:13).
- The shell provides only a title, free-form metadata, and a global Sync button. Views must invent their own hierarchy inside `content` ([dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:42)).
- The CSS has a small color palette, but not a complete design system. There are no semantic typography, spacing, elevation, focus, control-size, responsive, or light-theme tokens ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1)).
- Responsiveness is minimal: only `.grid-2` has an explicit breakpoint, while the sidebar remains fixed at 220px and tables depend on horizontal scrolling ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:21), [dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:54)).
- `dashboard.js` is 1,156 lines containing routing, API access, escaping, polling, job lifecycle, state, event binding, and all six view templates. That makes consistent UX changes risky and encourages one-off markup ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1)).
- There are approximately 73 inline `style` attributes and 41 `innerHTML` operations. For example, the Market view defines layout, color, tables, metrics, and chart containers in one large string ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:653)). This bypasses reusable CSS patterns and scatters behavior through DOM IDs.
- Each screen uses slightly different loading, error, empty-state, and action conventions. `fetchJSON`, for example, assumes every response is valid JSON and does not check HTTP status ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:164)).
- The UI uses very small 10–13px text extensively, particularly secondary navigation, table headers, badges, and descriptions. That increases visual density without establishing useful hierarchy.
- The current implementation has valuable but subtle concurrency behavior embedded inside UI code: route race checks, refresh guards, preserved chart state, and job reconnection. A wholesale renderer rewrite could easily discard these protections ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:17), [dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:61), [dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:302)).

## 3. Relevant files/modules

Primary UI:

- [templates/dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:1) — application shell, navigation, CDN Chart.js dependency.
- [static/css/dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1) — entire visual system.
- [static/js/dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1) — routing, rendering, state, jobs, live refresh, sync.
- [static/js/charts.js](/Users/badripratti/Desktop/stock-screener/static/js/charts.js:1) — Chart.js lifecycle and hard-coded chart theme.

Backend and lifecycle:

- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:47) — Flask/static configuration.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:280) — background subprocess/job implementation.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:524) — job API.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:670) — dashboard and data routes.
- [mac_app/main.py](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:29) — live project-root loading and threaded pywebview host.
- [mac_app/setup.py](/Users/badripratti/Desktop/stock-screener/mac_app/setup.py:16) — py2app contents.
- [mac_app/README.md](/Users/badripratti/Desktop/stock-screener/mac_app/README.md:9) — current “frontend changes require no app rebuild” deployment assumption.

There are currently no dashboard/API/polling tests under `tests/`.

## 4. Recommended solution

Use a design-system-on-vanilla-JS approach, combined with a serious modular refactor. Do not introduce React/Vue or a required runtime build step for this iteration.

The application has only six routes, no authentication or collaborative state, and relatively simple interactions. Its complexity comes from asynchronous jobs and refresh lifecycle—not from a component tree that requires a virtual DOM. A framework would reorganize the code, but it would not automatically solve the product hierarchy and would substantially increase rewrite and packaging risk.

### Proposed frontend structure

Use native ES modules served directly by Flask:

```text
static/js/
  app.js
  core/
    api.js
    router.js
    jobs.js
    refresh.js
    state.js
  components/
    page-header.js
    metric-card.js
    data-table.js
    status.js
    job-panel.js
    empty-state.js
  views/
    positions.js
    shortlist.js
    market.js
    backtests.js
    simulations.js
    scan.js
  charts/
    theme.js
    renderers.js
```

These can run directly in WebKit using `<script type="module">`; no bundler is required.

### Information architecture

Group navigation by intent:

- Monitor: Positions, Shortlist, Market
- Analyze: Backtests
- Run: Simulations, Full Scan

Make expensive actions visually distinct from passive monitoring. Give every screen the same header anatomy:

- Title and one-line purpose
- “Last updated” or selected snapshot
- Live/sync state
- Contextual primary action

Resolve the current default-route inconsistency: routing defaults to Positions, while the Shortlist section is commented as the default landing view ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:26), [dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:399)).

### Design system

Expand CSS custom properties into semantic tokens:

- Canvas/surface/elevated/overlay colors
- Primary, success, warning, danger, and neutral roles
- Typography scale and tabular-number styles
- 4/8px spacing scale
- Control heights
- Radius, border, shadow, and focus-ring tokens
- Dense and comfortable table/card modes
- Breakpoints and reduced-motion behavior

Build standardized components for buttons, icon buttons, inputs, alerts, status pills, skeletons, empty/error states, cards, tables, and page sections. Eliminate nearly all inline styles.

A light theme is optional; consistency and readability matter more than adding a theme toggle. The existing dark appearance can remain the default.

### Screen-level improvements

- Positions: lead with portfolio health and required actions; make upload/update secondary once data exists; sort urgent adjustments first.
- Shortlist: emphasize rank, recommendation quality, and risks; collapse verbose agent evidence behind accessible disclosures.
- Market: use summary → regime/breadth → ranked opportunities → sells → news. Add filtering/search and sticky table headers.
- Backtests: show selected run and parameters clearly; expose sort state visually and support keyboard sorting.
- Simulations: turn raw parameter cards into a structured form with validation, sensible ranges, estimated duration, and durable job status.
- Full Scan: explicitly separate Quick Scan and Full Scan choices rather than hiding the distinction in a checkbox; warn about the 15–30 minute operation before launch.
- Global status: distinguish “market data refreshed,” “repository synced,” and “background job running.” They are currently easy to conflate.

### Polling architecture

Extract polling before redesigning views:

- A route-scoped refresh controller owns the 90-second interval and aborts or ignores obsolete UI fetches.
- A global job manager owns 1.5-second job observation and survives navigation.
- Auto-sync remains an application-level service.
- Keep the current non-overlap guarantee.
- Use render-generation tokens or `AbortController` so stale requests cannot paint a later route.
- Do not cancel server subprocesses merely because their screen unmounted.
- Preserve finished-job reconnection and open-chart state explicitly.

### Framework decision

React/Vue is not justified today. It becomes reasonable if the roadmap adds several of the following:

- Many more interactive routes
- Shared editable state across screens
- Multi-user/authenticated workflows
- Complex drill-downs or nested routing
- A team already standardized on TypeScript/component tooling
- A maintained frontend release pipeline

If that point arrives, React/Vue with Vite is preferable to incrementally turning the global script into an ad hoc framework. For this iteration, native modules produce most of the maintainability benefit with much less operational change.

## 5. Alternatives considered

- CSS-only reskin: fastest, but leaves the monolithic rendering and inconsistent states intact. It would look newer without becoming materially easier to use.
- React/Vue/Vite rewrite: strongest formal component model, but highest regression surface around jobs, navigation, and refresh. Adds tooling disproportionate to six local-only views.
- HTMX/Jinja partials: could reduce client rendering, but requires moving presentation into Flask endpoints and reworking polling responses. It does not fit the existing JSON/job API particularly well.
- Web Components or Lit: a reasonable middle ground if reusable components become much more complex, but unnecessary for the current component count.
- Adopt a full CSS library: may speed up controls, but tends to produce generic visuals and adds another dependency. A small app-specific token/component layer is easier to package and tune for dense financial data.

## 6. Risks

### Packaging/build

The native app deliberately imports `dashboard.py` and serves `templates/` and `static/` from the live checkout ([mac_app/main.py](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:29), [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:47)). Therefore:

- Native ES modules and CSS require no py2app change.
- A Vite/webpack build would require generated assets to be committed or built before every release.
- Hashed output would need a manifest integrated with Flask/Jinja.
- The macOS app must never depend on Node being installed at runtime.
- If assets were moved into the `.app` bundle, `setup.py` would need explicit resource/data-file handling and the current live-update model would change.
- WebKit compatibility must be tested against the oldest supported macOS version.

Chart.js currently loads from jsDelivr ([dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:7)). The native app can lose charts when offline or when CDN access is blocked. Vendor the pinned Chart.js build into `static/vendor/`.

### Refresh and jobs

Critical behaviors to preserve:

- 90-second refresh cadence ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:47)).
- No overlapping refresh jobs ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:64)).
- 1.5-second job polling ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:272)).
- Job observation across navigation ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:310)).
- Five-minute application-level auto-sync ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1148)).
- Threaded Flask operation, which is necessary for concurrent refresh and polling requests ([mac_app/main.py](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:43)).

The current pollers have weak network-error handling. A failed `fetchJSON` inside a timer can leave a promise unresolved or a UI stuck in “running.” The refactor should add retry/backoff and explicit disconnected states without changing server-job semantics.

## 7. Edge cases

- Empty first-run state: no scans, shortlist, backtests, or positions CSV.
- Partial or malformed historical JSON and scan text.
- Network loss during yfinance/news jobs or while Chart.js would otherwise load.
- Navigating rapidly while initial fetches or refresh jobs are running.
- Auto-sync pulling new data while the user is editing simulation parameters. `doSync()` currently calls `route()`, which can destroy unsaved form state ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1119)).
- A job finishing after its view has unmounted.
- Reloading the entire window loses client `_activeJobs`, even though the server job may still exist.
- Duplicate tickers across Positions, Shortlist, and Market sharing DOM ID conventions.
- Very large signal/reason tables and long news or LLM-generated text.
- Invalid numeric parameters, negative investments, extreme iteration counts, and full-scan double submission.
- Selected historical Market scan versus `/api/top20`, which always returns the latest Top 20; the page can therefore combine different snapshots.
- Color-blind users: green/red must not be the only action or performance indicator.
- 900×600 native window, large system font settings, and keyboard-only use.
- Reduced motion for pulsing live indicators and spinners.

## 8. Testing strategy

Before changing presentation, add behavior characterization tests.

- Flask API tests using `app.test_client()` for empty states, uploads, path validation, job creation/status/stop, and malformed data.
- Browser integration tests covering every hash route and representative empty/populated/error fixtures.
- Fake timers for 90-second refresh, five-minute sync, and 1.5-second job polling.
- Tests for no overlapping live jobs and no stale DOM writes after navigation.
- Navigation-away-and-back tests for running and completed jobs.
- Tests proving auto-sync does not discard active form input unexpectedly.
- Chart lifecycle tests ensuring removed canvases do not retain Chart.js instances.
- Accessibility checks: landmarks, headings, labels, focus order, keyboard table sorting, contrast, and `aria-live` status announcements.
- Visual regression screenshots at 1440×900 and 900×600, including long data, empty states, loading, errors, and active jobs.
- A real packaged-app smoke test on macOS/WebKit: startup, all routes, offline charts, upload dialog, external links, sync, one short job, and one 90-second refresh cycle.

## 9. Assumptions

- This remains a single-user, localhost-only application.
- The six current workflows are the near-term product scope.
- Existing JSON API shapes and subprocess scripts should remain stable.
- Supporting the packaged macOS app is at least as important as browser development convenience.
- A committed vendored dependency is acceptable, while requiring Node at runtime is not.
- “Modern” prioritizes clarity, confidence, and operational feedback over animation or decorative novelty.

## 10. Easily missed issues

- The frontend is not included in the py2app bundle; it is read from the real checkout. That is why UI edits currently require no app rebuild.
- Chart colors are hard-coded separately in `charts.js`, so a CSS redesign alone will leave charts visually inconsistent ([charts.js](/Users/badripratti/Desktop/stock-screener/static/js/charts.js:14)).
- Charts are destroyed only when the same canvas ID is rendered again; route changes do not centrally dispose all removed chart instances.
- The backend offers a stop endpoint, but the current UI exposes no Stop control ([dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:559)).
- Finished jobs are retained server-side for only 15 minutes, while client reconnection state is memory-only ([dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:504)).
- Escaping is applied carefully to some external news/LLM content, but not consistently to every interpolated field or link. Component extraction should centralize safe text and URL rendering.
- The backtest and scan APIs accept filesystem paths supplied by query parameters ([dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:680), [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:723)). Localhost binding reduces exposure, but paths should still be constrained to approved data directories.
- There are currently no automated dashboard tests, making a one-shot rewrite especially risky.

No files were modified.
