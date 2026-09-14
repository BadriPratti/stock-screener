Reading additional input from stdin...
OpenAI Codex v0.154.0
--------
workdir: /Users/badripratti/Desktop/stock-screener
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: medium
reasoning summaries: none
session id: 01a09da0-9d13-7d32-8474-d58eabe233d3
--------
user

You are participating in an Engineering Council.

Do not modify any files.

Repository:
/Users/badripratti/Desktop/stock-screener

Engineering problem:
Thoroughly audit this repository for real correctness bugs — not style issues.
This is a Flask-based local dashboard app (dashboard.py, static/js/dashboard.js)
backed by a stock-screening engine (src/screening/), external data fetchers
(src/data/ — yfinance, SEC EDGAR, Reddit, ApeWisdom), LLM-driven agents
(src/agents/), backtest scripts (scripts/), and a packaged macOS app (mac_app/).

User goal:
Find real, verifiable bugs across the whole repo — race conditions, unhandled
exceptions, resource leaks, missing timeouts on network calls, NaN/division-by-
zero propagating into JSON output, encoding issues, or anything that could
crash or hang the app or silently corrupt data.

Relevant context:
A prior session already found and fixed: NaN values serializing into invalid
JSON at several script-output boundaries (now guarded via src/utils/json_safe.py
sanitize_nan()), a subprocess inheriting dashboard.py's Flask listening socket
via close_fds=False and outliving it, a single-threaded Flask dev server
head-of-line-blocking on slow requests, and a scan hanging forever on an SSL
socket read to Yahoo Finance with no enforced timeout (yfinance calls lacked
effective timeouts). Do not just confirm these — they're already fixed. Look
for the SAME CLASSES of bug elsewhere, and anything unrelated.

Independently investigate the repository and report your findings.

Return:

1. Your understanding of the problem
2. Files/modules you actually inspected
3. Concrete bugs found, each with file:line and a specific failure scenario
4. Severity per bug (critical/high/medium/low)
5. Anything you suspect but could not fully verify (label it as such)
6. Anything another engineer might easily miss

Do not report style/formatting issues. Only real correctness bugs. Be specific — cite exact file:line for every finding.

codex
I’ll perform a read-only correctness audit, tracing request/data paths across the Flask app, frontend, screeners, fetchers, agents, scripts, and macOS packaging. I’ll prioritize reproducible failure modes and verify each finding against surrounding control flow before reporting it.
exec
/bin/zsh -lc "pwd && rg --files -g '"'!node_modules'"' -g '"'!venv'"' -g '"'!dist'"' -g '"'!build'"' | sed -n '1,240p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 138ms:
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
run_optimized_scan.py
config.yaml
automated_position_report.py
requirements.txt
LICENSE
run_test.sh
START_HERE.md
CHANGELOG.md
position/Portfolio_Positions_Sep-08-2026.csv
tests/__init__.py
tests/test_email_full.py
tests/test_screener.py
tests/test_quant_engine.py
control_panel.py
tests/test_fetcher.py
tests/test_quality.py
tests/test_smart_fetcher.py
tests/test_enhanced_fundamentals.py
tests/test_git_storage_fetcher.py
run_screen.sh
manage_positions.py
dashboard.py
README.md
static/css/dashboard.css
docs/TRADE_TRACKING_SPREADSHEET.md
docs/IMPLEMENTATION_SUMMARY.md
docs/GITHUB_ACTIONS_SETUP.md
docs/SCREENING_MODULE_SUMMARY.md
docs/DETECTING_RATE_LIMITS.md
docs/OPTIMIZED_SCANNER_README.md
docs/FIDELITY_SETUP.md
docs/LOCAL_TEST_RESULTS.md
docs/PROJECT_SUMMARY.md
docs/POSITION_AUTOMATION.md
docs/SIMPLE_TRADE_TRACKER.md
docs/QUANT_ENGINE_README.md
docs/ROBINHOOD_SETUP.md
docs/NOTIFICATIONS_SETUP.md
docs/SMART_CACHING_STRATEGY.md
docs/SETUP_FMP.md
docs/README.md
docs/FULL_MARKET_IMPLEMENTATION.md
docs/NOTIFICATIONS_COMPLETE.md
docs/SETUP_CRON_JOB.md
docs/REVISED_SMART_CACHING_STRATEGY.md
docs/DEPLOYMENT_CHECKLIST.md
docs/RATE_LIMIT_SOLUTION.md
docs/ENHANCED_FUNDAMENTALS_USAGE.md
docs/ABOUT.md
docs/FULL_MARKET_SCANNER_README.md
docs/FMP_INTEGRATION_STATUS.md
data/daily_scans/latest_optimized_scan.txt
data/daily_scans/optimized_scan_20260909_172815.txt
data/daily_scans/optimized_scan_20260729_222415.txt
data/daily_scans/optimized_scan_20260730_085210.txt
data/daily_scans/optimized_scan_20260729_223432.txt
data/daily_scans/optimized_scan_20260729_223608.txt
data/daily_scans/shortlist_latest.json
data/daily_scans/optimized_scan_20260729_221947.txt
data/daily_scans/optimized_scan_20260730_225116.txt
data/daily_scans/top20_latest.json
templates/dashboard.html
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
CONTRIBUTING.md
mac_app/setup.py
mac_app/README.md
mac_app/main.py
data/fundamentals_audit/audit_20260909_171235.json
data/fundamentals_audit/audit_20260824_141351.json
data/fundamentals_audit/audit_20260904_172630.json
data/fundamentals_audit/audit_20260825_141712.json
data/fundamentals_audit/latest.json
data/fundamentals_audit/audit_20260911_170840.json
data/fundamentals_audit/audit_20260901_174024.json
data/fundamentals_audit/audit_20260910_170652.json
static/js/dashboard.js
static/js/charts.js
examples/quality_check_demo.py
data/fundamentals_audit/audit_20260828_232752.json
data/fundamentals_audit/audit_20260804_224647.json
data/fundamentals_audit/audit_20260827_232037.json
data/fundamentals_audit/audit_20260909_172331.json
data/fundamentals_audit/audit_20260820_141138.json
data/fundamentals_audit/audit_20260908_173723.json
data/fundamentals_audit/audit_20260903_172314.json
data/fundamentals_audit/audit_20260819_141739.json
data/fundamentals_audit/audit_20260902_173310.json
data/fundamentals_audit/audit_20260816_141320.json
examples/example_entry_dates.json
data/fundamentals_audit/audit_20260907_183406.json
data/fundamentals_audit/audit_20260816_141010.json
data/fundamentals_audit/audit_20260826_142311.json
data/fundamentals_audit/audit_20260821_140943.json
examples/demo.py
examples/screening_demo.py
data/fundamentals_audit/audit_20260816_141611.json
data/fundamentals_audit/audit_20260831_203549.json
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
data/congress_trades/signals_20260910_170653.json
data/congress_trades/signals_20260909_172815.json
data/congress_trades/signals_20260820_141138.json
data/congress_trades/signals_20260825_141713.json
data/congress_trades/signals_20260904_172631.json
data/congress_trades/latest.json
data/congress_trades/signals_20260901_174025.json
mac_app/assets/AppIcon.icns
data/fundamentals_cache/AMBQ_fundamentals.json
data/fundamentals_cache/THFF_fundamentals.json
data/fundamentals_cache/ICFI_fundamentals.json
data/fundamentals_cache/WFG_fundamentals.json
data/fundamentals_cache/YETI_fundamentals.json
data/fundamentals_cache/AGO_fundamentals.json
data/fundamentals_cache/EGP_fundamentals.json
data/fundamentals_cache/WSFS_fundamentals.json
data/fundamentals_cache/JPM_fundamentals.json
data/fundamentals_cache/RYZ_fundamentals.json
data/fundamentals_cache/ACA_fundamentals.json
data/fundamentals_cache/HBT_fundamentals.json
data/fundamentals_cache/TH_fundamentals.json
data/fundamentals_cache/RDN_fundamentals.json
data/fundamentals_cache/LOVE_fundamentals.json
data/fundamentals_cache/AOS_fundamentals.json
data/fundamentals_cache/QVCGA_fundamentals.json
data/fundamentals_cache/WSO_fundamentals.json
data/fundamentals_cache/KGS_fundamentals.json
data/fundamentals_cache/SND_fundamentals.json
data/fundamentals_cache/JRSH_fundamentals.json
data/fundamentals_cache/INVE_fundamentals.json
data/fundamentals_cache/TTSH_fundamentals.json
data/fundamentals_cache/NBHC_fundamentals.json
data/fundamentals_cache/DNUT_fundamentals.json
data/fundamentals_cache/DKNG_fundamentals.json
data/fundamentals_cache/NAT_fundamentals.json
data/fundamentals_cache/CAL_fundamentals.json
data/fundamentals_cache/APLS_fundamentals.json
data/fundamentals_cache/AOUT_fundamentals.json
data/fundamentals_cache/KTOS_fundamentals.json
data/fundamentals_cache/GDDY_fundamentals.json
data/fundamentals_cache/BOH_fundamentals.json
data/fundamentals_cache/TENB_fundamentals.json
data/fundamentals_cache/BWEN_fundamentals.json
data/fundamentals_cache/LKFN_fundamentals.json
data/fundamentals_cache/MTG_fundamentals.json
data/fundamentals_cache/STRT_fundamentals.json
data/fundamentals_cache/AVGO_fundamentals.json
data/fundamentals_cache/NBN_fundamentals.json
data/fundamentals_cache/ONB_fundamentals.json

exec
/bin/zsh -lc 'wc -l dashboard.py static/js/dashboard.js src/data/*.py src/screening/*.py src/agents/*.py scripts/*.py mac_app/*.py' in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     784 dashboard.py
    1124 static/js/dashboard.js
      14 src/data/__init__.py
      86 src/data/apewisdom_sentiment.py
     116 src/data/earnings_risk.py
     257 src/data/enhanced_fundamentals.py
     384 src/data/fetcher.py
     152 src/data/fidelity_positions.py
     466 src/data/fmp_fetcher.py
     420 src/data/fundamentals_fetcher.py
     347 src/data/git_storage_fetcher.py
     235 src/data/insider_trading.py
     621 src/data/quality.py
     146 src/data/reddit_sentiment.py
     284 src/data/robinhood_positions.py
     347 src/data/smart_fetcher.py
     648 src/data/storage.py
     222 src/data/universe_fetcher.py
      27 src/screening/__init__.py
     353 src/screening/batch_processor.py
     299 src/screening/benchmark.py
     358 src/screening/indicators.py
     517 src/screening/optimized_batch_processor.py
     916 src/screening/phase_indicators.py
     348 src/screening/quant_engine.py
     533 src/screening/screener.py
     942 src/screening/signal_engine.py
     130 src/screening/top20_ranker.py
      10 src/agents/__init__.py
     168 src/agents/catalyst_sentiment.py
     153 src/agents/congress_trades.py
     343 src/agents/fundamentals_auditor.py
      40 src/agents/llm_client.py
      77 src/agents/shortlist.py
     153 scripts/backtest_critic.py
     158 scripts/backtest_top3.py
     201 scripts/backtest_top3_monte_carlo.py
      71 scripts/check_positions.py
     145 scripts/compare_old_vs_new_weights.py
     158 scripts/component_correlation_analysis.py
     149 scripts/fetch_momentum_status.py
      43 scripts/fetch_news.py
      59 scripts/fetch_price_history.py
      65 scripts/run_catalyst_sentiment.py
     379 scripts/run_full_market_scan.py
      68 scripts/run_fundamentals_auditor.py
     146 scripts/run_quant_engine.py
     393 scripts/walk_forward_backtest.py
      63 mac_app/main.py
      40 mac_app/setup.py
   14158 total

exec
/bin/zsh -lc "rg -n \"requests\\.(get|post|put|delete|request)|urlopen|httpx|urllib|subprocess\\.|Popen|Thread|Executor|open\\(|json\\.dump|jsonify|send_file|\\.json\\(|yfinance|yf\\.|Ticker\\(\" dashboard.py src scripts mac_app static/js/dashboard.js" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
dashboard.py:25:from flask import Flask, jsonify, render_template, request
dashboard.py:282:# STATE-dict + subprocess.Popen + polling pattern, keyed by a generated job_id
dashboard.py:310:# hit this: yfinance/urllib3 claims a 10s timeout on price history, but a real
dashboard.py:374:        proc = subprocess.Popen(
dashboard.py:376:            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
dashboard.py:527:        return jsonify({"error": "no positions CSV uploaded yet"}), 400
dashboard.py:532:        return jsonify({"error": f"unknown job kind: {kind}"}), 404
dashboard.py:541:    threading.Thread(target=_launch_job, args=(job_id, cmd, result_path), daemon=True).start()
dashboard.py:542:    return jsonify({"job_id": job_id})
dashboard.py:550:            return jsonify({"error": "unknown job"}), 404
dashboard.py:552:        return jsonify({
dashboard.py:564:            return jsonify({"error": "unknown job"}), 404
dashboard.py:570:        return jsonify({"ok": True})
dashboard.py:571:    return jsonify({"error": "not running"}), 409
dashboard.py:575:    return subprocess.run(
dashboard.py:601:            subprocess.run(
dashboard.py:607:        return jsonify({
dashboard.py:612:        return jsonify({"success": False, "output": str(e)})
dashboard.py:623:        return jsonify({"success": False, "error": "no file uploaded"}), 400
dashboard.py:626:    return jsonify({"success": True})
dashboard.py:637:        return jsonify({
dashboard.py:642:    return jsonify(data)
dashboard.py:649:    return jsonify(_read_json(ADHOC_DIR / f"news_{group}.json", {"generated": None, "tickers": [], "news": {}}))
dashboard.py:656:    return jsonify(_read_json(ADHOC_DIR / f"price_history_{group}.json", {"generated": None, "tickers": [], "prices": {}}))
dashboard.py:663:    return jsonify(_read_json(ADHOC_DIR / f"momentum_status_{group}.json", {"generated": None, "tickers": [], "status": {}}))
dashboard.py:677:    return jsonify(get_scan_files())
dashboard.py:688:            return jsonify({"error": "No scan data"})
dashboard.py:691:        return jsonify({"error": "File not found"})
dashboard.py:693:    return jsonify(parse_scan_file(path))
dashboard.py:698:    return jsonify(_read_json(SCAN_DIR / "top20_latest.json", {"generated": None, "top20": []}))
dashboard.py:703:    return jsonify(_read_json(SCAN_DIR / "shortlist_latest.json", {
dashboard.py:713:        return jsonify({"generated": None, "params": {}, "summary": {}, "component_correlations": {}, "trade_count": 0})
dashboard.py:714:    return jsonify({
dashboard.py:738:    return jsonify({"trades": trades, "equity_curve": equity_curve})
dashboard.py:743:    return jsonify(get_backtest_files())
dashboard.py:750:        return jsonify({"error": "File not found"}), 404
dashboard.py:751:    return jsonify(_read_json(path, {}))
dashboard.py:755:    webbrowser.open(f"http://localhost:{port}")
dashboard.py:771:        subprocess.run(cmd)
static/js/dashboard.js:47:const LIVE_INTERVAL_MS = 90 * 1000; // 90 seconds — cheap yfinance-only pulls, no LLM cost
static/js/dashboard.js:62:// fires (e.g. yfinance is slow), skip that tick instead of stacking another
static/js/dashboard.js:166:  return res.json();
static/js/dashboard.js:762:// Silent live refresh: re-runs the (cheap, yfinance-only) positions analysis
static/js/dashboard.js:795:      const uploadRes = await fetch('/api/positions/upload', { method: 'POST', body: form }).then(r => r.json());
scripts/backtest_top3.py:25:import yfinance as yf
scripts/backtest_top3.py:54:    spy = yf.Ticker('SPY').history(period='2y')
scripts/backtest_top3.py:62:            hist = yf.Ticker(ticker).history(period='2y')
scripts/backtest_top3.py:154:    out_path.write_text(json.dumps(sanitize_nan(out), indent=2, default=str))
src/screening/quant_engine.py:17:import yfinance as yf
src/screening/phase_indicators.py:87:    # yfinance sometimes returns timezone-aware data, sometimes naive, sometimes RangeIndex
src/screening/optimized_batch_processor.py:14:from concurrent.futures import ThreadPoolExecutor, as_completed
src/screening/optimized_batch_processor.py:20:import yfinance as yf
src/screening/optimized_batch_processor.py:84:        # Thread-safe rate limiting
src/screening/optimized_batch_processor.py:105:            with open(self.progress_file, 'rb') as f:
src/screening/optimized_batch_processor.py:125:            with open(self.progress_file, 'wb') as f:
src/screening/optimized_batch_processor.py:132:        """Thread-safe rate limiting - ensures minimum delay between ANY requests.
src/screening/optimized_batch_processor.py:168:            # Ensure DatetimeIndex (yfinance should return this, but verify)
src/screening/optimized_batch_processor.py:202:            # Thread-safe rate limiting (locks ensure only 1 request at a time)
src/screening/optimized_batch_processor.py:211:                import yfinance as yf
src/screening/optimized_batch_processor.py:212:                long_hist = yf.Ticker(ticker).history(period='5y', interval='1d')
src/screening/optimized_batch_processor.py:402:        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
scripts/run_quant_engine.py:40:        with open(config_path, 'r') as f:
scripts/run_quant_engine.py:66:        with open(filepath, 'w') as f:
src/screening/top20_ranker.py:14:import yfinance as yf
src/screening/top20_ranker.py:24:    """Best-effort recent news headlines for a ticker via yfinance. Never raises."""
src/screening/top20_ranker.py:26:        news = yf.Ticker(ticker).news or []
scripts/backtest_top3_monte_carlo.py:28:import yfinance as yf
scripts/backtest_top3_monte_carlo.py:58:    spy = yf.Ticker('SPY').history(period='2y')
scripts/backtest_top3_monte_carlo.py:65:            hist = yf.Ticker(ticker).history(period='2y')
scripts/backtest_top3_monte_carlo.py:197:    out_path.write_text(json.dumps(sanitize_nan(out), indent=2, default=str))
src/screening/batch_processor.py:75:            with open(self.progress_file, 'rb') as f:
src/screening/batch_processor.py:101:            with open(self.progress_file, 'wb') as f:
scripts/fetch_news.py:4:headline fetcher directly (yfinance), no Claude/LLM call involved here at all.
scripts/fetch_news.py:34:    out_path.write_text(json.dumps({
mac_app/setup.py:10:(pyobjc's Cocoa/WebKit bridge) — dashboard.py never imports pandas/yfinance/
scripts/fetch_momentum_status.py:29:import yfinance as yf
scripts/fetch_momentum_status.py:73:    HISTORY_PATH.write_text(json.dumps(sanitize_nan(history), indent=2), encoding="utf-8")
scripts/fetch_momentum_status.py:116:            price_data = yf.Ticker(ticker).history(period="1y", interval="1d")
scripts/fetch_momentum_status.py:139:    out_path.write_text(json.dumps(sanitize_nan({
mac_app/main.py:22:# Full Scan, Positions, Sync) all fork()+exec() a subprocess. Without this, those
mac_app/main.py:55:threading.Thread(target=_run_flask, daemon=True).start()
scripts/compare_old_vs_new_weights.py:19:import yfinance as yf
scripts/compare_old_vs_new_weights.py:66:    spy = yf.Ticker('SPY').history(period='2y')
scripts/compare_old_vs_new_weights.py:73:            hist = yf.Ticker(ticker).history(period='2y')
scripts/check_positions.py:65:        with open(filename, 'w') as f:
scripts/component_correlation_analysis.py:27:import yfinance as yf
scripts/component_correlation_analysis.py:71:    spy = yf.Ticker('SPY').history(period='2y')
scripts/component_correlation_analysis.py:78:            hist = yf.Ticker(ticker).history(period='2y')
scripts/backtest_critic.py:143:    report_path.write_text(json.dumps({
scripts/check_throttling.sh:79:    with open('$PROGRESS_FILE', 'rb') as f:
scripts/run_full_market_scan.py:190:    with open(filepath, 'w') as f:
scripts/run_full_market_scan.py:197:    with open(latest_path, 'w') as f:
scripts/walk_forward_backtest.py:46:import yfinance as yf
scripts/walk_forward_backtest.py:136:    Catalyst Sentiment can't get the same treatment — yfinance's news feed has no
scripts/walk_forward_backtest.py:186:    spy = yf.Ticker('SPY').history(period='2y')
scripts/walk_forward_backtest.py:193:            h = yf.Ticker(ticker).history(period='2y')
scripts/walk_forward_backtest.py:350:    with open(path, 'w') as f:
scripts/walk_forward_backtest.py:351:        json.dump(result, f, indent=2, default=str)
scripts/walk_forward_backtest.py:353:    with open(latest_path, 'w') as f:
scripts/walk_forward_backtest.py:354:        json.dump(result, f, indent=2, default=str)
scripts/fetch_price_history.py:4:yfinance only, no LLM call involved.
scripts/fetch_price_history.py:16:import yfinance as yf
scripts/fetch_price_history.py:22:    otherwise get written by json.dumps as an invalid, unparseable JSON token.
scripts/fetch_price_history.py:25:        hist = yf.Ticker(ticker).history(period="9mo")
scripts/fetch_price_history.py:50:    out_path.write_text(json.dumps({
src/data/earnings_risk.py:11:Uses yfinance's Ticker.calendar (earnings date) and Ticker.option_chain (real market IV) —
src/data/earnings_risk.py:19:import yfinance as yf
src/data/earnings_risk.py:43:            t = yf.Ticker(ticker)
src/data/earnings_risk.py:76:    def _expected_move(self, ticker_obj: yf.Ticker, earnings_date: date) -> Optional[float]:
src/data/fetcher.py:16:import yfinance as yf
src/data/fetcher.py:113:            with open(cache_path, 'rb') as f:
src/data/fetcher.py:129:            with open(cache_path, 'wb') as f:
src/data/fetcher.py:135:    def _fetch_with_retry(self, ticker: str) -> Optional[yf.Ticker]:
src/data/fetcher.py:142:            yfinance Ticker object if successful, None otherwise.
src/data/fetcher.py:146:                stock = yf.Ticker(ticker)
src/data/fetcher.py:281:            # DO NOT reset_index() - we want to preserve the DatetimeIndex from yfinance
src/data/fetcher.py:284:            # Ensure index is DatetimeIndex (yfinance should provide this)
src/data/fetcher.py:286:                logger.warning(f"{ticker}: yfinance returned non-DatetimeIndex: {type(hist.index)}")
src/agents/fundamentals_auditor.py:114:                with open(cache_file, "rb") as f:
src/agents/fundamentals_auditor.py:123:        data = resp.json()
src/agents/fundamentals_auditor.py:128:        with open(cache_file, "wb") as f:
src/agents/fundamentals_auditor.py:199:            items = resp.json().get("directory", {}).get("item", [])
src/agents/fundamentals_auditor.py:340:    (OUTPUT_DIR / f"audit_{timestamp}.json").write_text(json.dumps(payload, indent=2))
src/agents/fundamentals_auditor.py:341:    (OUTPUT_DIR / "latest.json").write_text(json.dumps(payload, indent=2))
src/agents/congress_trades.py:37:                with open(CACHE_PATH) as f:
src/agents/congress_trades.py:43:        resp = requests.get(DATA_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
src/agents/congress_trades.py:45:        transactions = resp.json()
src/agents/congress_trades.py:49:            with open(CACHE_PATH) as f:
src/agents/congress_trades.py:54:    with open(CACHE_PATH, 'w') as f:
src/agents/congress_trades.py:55:        json.dump(transactions, f)
src/agents/congress_trades.py:148:    with open(out_dir / f"signals_{ts}.json", 'w') as f:
src/agents/congress_trades.py:149:        json.dump(payload, f, indent=2, default=str)
src/agents/congress_trades.py:150:    with open(out_dir / "latest.json", 'w') as f:
src/agents/congress_trades.py:151:        json.dump(payload, f, indent=2, default=str)
src/data/fidelity_positions.py:78:    with open(path, newline='', encoding='utf-8-sig') as f:
src/data/git_storage_fetcher.py:21:import yfinance as yf
src/data/git_storage_fetcher.py:57:            stock = yf.Ticker(ticker)
src/data/git_storage_fetcher.py:62:                # Verify DatetimeIndex (yfinance should return this by default)
src/data/git_storage_fetcher.py:64:                    logger.warning(f"{ticker}: yfinance returned non-DatetimeIndex: {type(data.index)}")
src/data/git_storage_fetcher.py:103:                with open(fundamental_file, 'r') as f:
src/data/git_storage_fetcher.py:127:                with open(fundamental_file, 'w') as f:
src/data/git_storage_fetcher.py:128:                    json.dump(cache_data, f, indent=2, default=str)
src/data/git_storage_fetcher.py:157:            with open(file_path, 'r') as f:
src/data/git_storage_fetcher.py:264:                with open(self.metadata_file, 'r') as f:
src/data/git_storage_fetcher.py:274:        with open(self.metadata_file, 'w') as f:
src/data/git_storage_fetcher.py:275:            json.dump(metadata, f, indent=2)
src/data/git_storage_fetcher.py:293:                with open(file_path, 'r') as f:
src/data/git_storage_fetcher.py:334:                with open(file_path, 'r') as f:
src/notifications/slack_notifier.py:220:            response = requests.post(
src/notifications/slack_notifier.py:281:                response = requests.post(
src/data/insider_trading.py:72:                with open(cache_file, "rb") as f:
src/data/insider_trading.py:81:        data = resp.json()
src/data/insider_trading.py:86:        with open(cache_file, "wb") as f:
src/data/insider_trading.py:143:            items = resp.json().get("directory", {}).get("item", [])
src/data/fmp_fetcher.py:143:            response = requests.get(url, params=params, timeout=10)
src/data/fmp_fetcher.py:158:            data = response.json()
src/data/fmp_fetcher.py:187:            with open(cache_path, 'rb') as f:
src/data/fmp_fetcher.py:199:            with open(cache_path, 'wb') as f:
src/data/fmp_fetcher.py:220:            with open(cache_path, 'rb') as f:
src/data/fmp_fetcher.py:232:            with open(cache_path, 'wb') as f:
src/data/fmp_fetcher.py:253:            with open(cache_path, 'rb') as f:
src/data/fmp_fetcher.py:265:            with open(cache_path, 'wb') as f:
src/data/fmp_fetcher.py:286:            with open(cache_path, 'rb') as f:
src/data/fmp_fetcher.py:298:            with open(cache_path, 'wb') as f:
src/agents/catalyst_sentiment.py:2:headlines (yfinance) and SEC Form 4 insider-buying data already available in the
src/agents/catalyst_sentiment.py:22:import yfinance as yf
src/agents/catalyst_sentiment.py:61:    """Recent news headlines via yfinance. Never raises."""
src/agents/catalyst_sentiment.py:63:        news = yf.Ticker(ticker).news or []
src/agents/catalyst_sentiment.py:165:    (OUTPUT_DIR / f"sentiment_{timestamp}.json").write_text(json.dumps(payload, indent=2))
src/agents/catalyst_sentiment.py:166:    (OUTPUT_DIR / "latest.json").write_text(json.dumps(payload, indent=2))
src/data/apewisdom_sentiment.py:62:                resp = requests.get(url, timeout=REQUEST_TIMEOUT)
src/data/apewisdom_sentiment.py:64:                data = resp.json()
src/data/enhanced_fundamentals.py:1:"""Enhanced fundamentals wrapper that intelligently uses FMP + yfinance.
src/data/enhanced_fundamentals.py:5:- Falls back to yfinance if FMP unavailable or rate limited
src/data/enhanced_fundamentals.py:10:- Use yfinance for initial screening (fast, no rate limits)
src/data/enhanced_fundamentals.py:32:    """Unified fundamentals fetcher using FMP + yfinance."""
src/data/enhanced_fundamentals.py:47:                logger.warning(f"FMP initialization failed: {e}. Using yfinance only.")
src/data/enhanced_fundamentals.py:49:            logger.info("FMP_API_KEY not set - using yfinance only")
src/data/enhanced_fundamentals.py:79:                        logger.warning(f"FMP returned no data for {ticker}, falling back to yfinance")
src/data/enhanced_fundamentals.py:81:                    logger.warning(f"FMP fetch failed for {ticker}: {e}. Using yfinance.")
src/data/enhanced_fundamentals.py:83:                logger.warning(f"FMP daily limit reached ({self.fmp_daily_limit}). Using yfinance.")
src/data/enhanced_fundamentals.py:85:        # Fall back to yfinance
src/data/enhanced_fundamentals.py:148:        # NET MARGIN (not available in yfinance!)
src/data/enhanced_fundamentals.py:155:        # OPERATING MARGIN (not available in yfinance!)
src/data/universe_fetcher.py:148:                with open(self.cache_file, 'rb') as f:
src/data/universe_fetcher.py:189:        with open(self.cache_file, 'wb') as f:
src/data/universe_fetcher.py:209:        with open(self.cache_file, 'rb') as f:
src/data/fundamentals_fetcher.py:14:import yfinance as yf
src/data/fundamentals_fetcher.py:45:        stock = yf.Ticker(ticker)
src/data/fundamentals_fetcher.py:162:        # Try to get inventory breakdown (not always available in yfinance)
src/data/smart_fetcher.py:18:import yfinance as yf
src/data/smart_fetcher.py:74:                with open(cache_path, 'rb') as f:
src/data/smart_fetcher.py:76:                with open(cache_meta_path, 'rb') as f:
src/data/smart_fetcher.py:100:                stock = yf.Ticker(ticker)
src/data/smart_fetcher.py:127:                stock = yf.Ticker(ticker)
src/data/smart_fetcher.py:171:                with open(cache_path, 'rb') as f:
src/data/smart_fetcher.py:187:                with open(cache_path, 'wb') as f:
src/data/smart_fetcher.py:248:            with open(cache_path, 'wb') as f:
src/data/smart_fetcher.py:255:            with open(cache_meta_path, 'wb') as f:
src/data/smart_fetcher.py:276:            with open(cache_path, 'rb') as f:
src/utils/json_safe.py:5:pandas/yfinance data at some point, which can leave a NaN behind — an SMA
src/utils/json_safe.py:7:an average over an empty list. Python's json.dumps happily serializes NaN
mac_app/README.md:5:`mac_app/main.py` runs the real `dashboard.py`'s Flask app in a background thread, then opens a `pywebview` window pointed at it — no `webbrowser.open()` call in this path at all, so launching/relaunching the app never pops open your default browser.
mac_app/README.md:7:It still operates on the real project checkout on disk (`~/Desktop/stock-screener` by default, override with the `STOCK_SCREENER_ROOT` env var if you move the folder) — data files, git pull/push (the Sync button), and running backtest scripts all go through the real repo and its own `venv/bin/python`, exactly like running `python dashboard.py` normally. The app bundle itself only needs to run Flask + pywebview; the heavier dependencies (pandas, yfinance, etc.) are never bundled since `dashboard.py` shells out to scripts rather than importing them directly.
src/analysis/position_manager.py:21:import yfinance as yf
src/analysis/position_manager.py:47:        """Get price data from cache or yfinance.
src/analysis/position_manager.py:63:                logger.debug(f"{ticker}: Cache fetch failed, falling back to yfinance: {e}")
src/analysis/position_manager.py:65:        # Fallback to yfinance
src/analysis/position_manager.py:67:            stock = yf.Ticker(ticker)
src/analysis/position_manager.py:70:                logger.debug(f"{ticker}: Fetched fresh price data from yfinance")
src/analysis/position_manager.py:91:                with open(fundamental_file, 'r') as f:

exec
/bin/zsh -lc "nl -ba dashboard.py | sed -n '1,430p'; nl -ba dashboard.py | sed -n '430,784p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
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

codex
The dashboard’s job lifecycle and file boundaries already expose a few plausible concurrency/security failures. I’m now checking whether they are reachable from the actual frontend and whether shared output paths or subprocess state can misattribute results under overlapping refreshes.
exec
/bin/zsh -lc "nl -ba src/data/fetcher.py | sed -n '1,384p'; nl -ba src/data/smart_fetcher.py | sed -n '1,347p'; nl -ba src/data/storage.py | sed -n '1,648p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Data fetching module for retrieving stock data from Yahoo Finance.
     2	
     3	This module provides a robust interface for fetching stock fundamentals and
     4	price history with caching, error handling, and retry logic.
     5	"""
     6	
     7	import logging
     8	import os
     9	import pickle
    10	import time
    11	from datetime import datetime, timedelta
    12	from pathlib import Path
    13	from typing import Dict, List, Optional, Tuple
    14	
    15	import pandas as pd
    16	import yfinance as yf
    17	
    18	# Configure logging
    19	logging.basicConfig(
    20	    level=logging.INFO,
    21	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    22	)
    23	logger = logging.getLogger(__name__)
    24	
    25	
    26	class YahooFinanceFetcher:
    27	    """Fetches stock data from Yahoo Finance with caching and error handling.
    28	
    29	    This class provides methods to fetch fundamental data and price history
    30	    for stocks, with automatic caching to reduce API calls and retry logic
    31	    for network failures.
    32	
    33	    Attributes:
    34	        cache_dir: Directory path for storing cached data files.
    35	        cache_expiry_hours: Number of hours before cache expires (default: 24).
    36	        max_retries: Maximum number of retry attempts for API calls (default: 3).
    37	        retry_delay: Delay in seconds between retry attempts (default: 2).
    38	
    39	    Example:
    40	        >>> fetcher = YahooFinanceFetcher()
    41	        >>> fundamentals = fetcher.fetch_fundamentals("AAPL")
    42	        >>> prices = fetcher.fetch_price_history("AAPL", period="5y")
    43	        >>> all_data = fetcher.fetch_multiple(["AAPL", "MSFT", "GOOGL"])
    44	    """
    45	
    46	    def __init__(
    47	        self,
    48	        cache_dir: str = "./data/cache",
    49	        cache_expiry_hours: int = 24,
    50	        max_retries: int = 3,
    51	        retry_delay: int = 2
    52	    ) -> None:
    53	        """Initialize the YahooFinanceFetcher.
    54	
    55	        Args:
    56	            cache_dir: Directory path for caching data. Created if it doesn't exist.
    57	            cache_expiry_hours: Hours before cached data expires.
    58	            max_retries: Maximum retry attempts for failed API calls.
    59	            retry_delay: Seconds to wait between retries.
    60	        """
    61	        self.cache_dir = Path(cache_dir)
    62	        self.cache_dir.mkdir(parents=True, exist_ok=True)
    63	        self.cache_expiry_hours = cache_expiry_hours
    64	        self.max_retries = max_retries
    65	        self.retry_delay = retry_delay
    66	        logger.info(f"YahooFinanceFetcher initialized with cache_dir: {cache_dir}")
    67	
    68	    def _get_cache_path(self, ticker: str, data_type: str) -> Path:
    69	        """Get the cache file path for a given ticker and data type.
    70	
    71	        Args:
    72	            ticker: Stock ticker symbol.
    73	            data_type: Type of data ('fundamentals' or 'prices').
    74	
    75	        Returns:
    76	            Path object for the cache file.
    77	        """
    78	        return self.cache_dir / f"{ticker}_{data_type}.pkl"
    79	
    80	    def _is_cache_valid(self, cache_path: Path) -> bool:
    81	        """Check if cached data is still valid.
    82	
    83	        Args:
    84	            cache_path: Path to the cache file.
    85	
    86	        Returns:
    87	            True if cache exists and hasn't expired, False otherwise.
    88	        """
    89	        if not cache_path.exists():
    90	            return False
    91	
    92	        file_modified = datetime.fromtimestamp(cache_path.stat().st_mtime)
    93	        expiry_time = datetime.now() - timedelta(hours=self.cache_expiry_hours)
    94	
    95	        is_valid = file_modified > expiry_time
    96	        if is_valid:
    97	            logger.debug(f"Cache valid for {cache_path.name}")
    98	        else:
    99	            logger.debug(f"Cache expired for {cache_path.name}")
   100	
   101	        return is_valid
   102	
   103	    def _load_from_cache(self, cache_path: Path) -> Optional[any]:
   104	        """Load data from cache file.
   105	
   106	        Args:
   107	            cache_path: Path to the cache file.
   108	
   109	        Returns:
   110	            Cached data if successful, None otherwise.
   111	        """
   112	        try:
   113	            with open(cache_path, 'rb') as f:
   114	                data = pickle.load(f)
   115	            logger.info(f"Loaded data from cache: {cache_path.name}")
   116	            return data
   117	        except Exception as e:
   118	            logger.warning(f"Failed to load cache {cache_path.name}: {e}")
   119	            return None
   120	
   121	    def _save_to_cache(self, data: any, cache_path: Path) -> None:
   122	        """Save data to cache file.
   123	
   124	        Args:
   125	            data: Data to cache.
   126	            cache_path: Path to save the cache file.
   127	        """
   128	        try:
   129	            with open(cache_path, 'wb') as f:
   130	                pickle.dump(data, f)
   131	            logger.info(f"Saved data to cache: {cache_path.name}")
   132	        except Exception as e:
   133	            logger.warning(f"Failed to save cache {cache_path.name}: {e}")
   134	
   135	    def _fetch_with_retry(self, ticker: str) -> Optional[yf.Ticker]:
   136	        """Fetch ticker data with retry logic.
   137	
   138	        Args:
   139	            ticker: Stock ticker symbol.
   140	
   141	        Returns:
   142	            yfinance Ticker object if successful, None otherwise.
   143	        """
   144	        for attempt in range(self.max_retries):
   145	            try:
   146	                stock = yf.Ticker(ticker)
   147	                # Test if ticker is valid by accessing info
   148	                _ = stock.info
   149	                return stock
   150	            except Exception as e:
   151	                logger.warning(
   152	                    f"Attempt {attempt + 1}/{self.max_retries} failed for {ticker}: {e}"
   153	                )
   154	                if attempt < self.max_retries - 1:
   155	                    time.sleep(self.retry_delay)
   156	                else:
   157	                    logger.error(f"Failed to fetch {ticker} after {self.max_retries} attempts")
   158	                    return None
   159	
   160	    def fetch_fundamentals(self, ticker: str) -> Dict[str, any]:
   161	        """Fetch fundamental data for a stock.
   162	
   163	        Retrieves key fundamental metrics including current price, 52-week high/low,
   164	        P/E ratio, P/B ratio, debt-to-equity, and free cash flow.
   165	
   166	        Args:
   167	            ticker: Stock ticker symbol (e.g., 'AAPL').
   168	
   169	        Returns:
   170	            Dictionary containing fundamental metrics. Returns empty dict on failure.
   171	
   172	        Example:
   173	            >>> fetcher = YahooFinanceFetcher()
   174	            >>> data = fetcher.fetch_fundamentals("AAPL")
   175	            >>> print(data['pe_ratio'])
   176	        """
   177	        cache_path = self._get_cache_path(ticker, 'fundamentals')
   178	
   179	        # Check cache first
   180	        if self._is_cache_valid(cache_path):
   181	            cached_data = self._load_from_cache(cache_path)
   182	            if cached_data is not None:
   183	                return cached_data
   184	
   185	        # Fetch from API
   186	        logger.info(f"Fetching fundamentals for {ticker}")
   187	        stock = self._fetch_with_retry(ticker)
   188	
   189	        if stock is None:
   190	            logger.error(f"Could not fetch fundamentals for {ticker}")
   191	            return {}
   192	
   193	        try:
   194	            info = stock.info
   195	
   196	            # Extract fundamental metrics with safe defaults
   197	            fundamentals = {
   198	                'ticker': ticker,
   199	                'name': info.get('longName', ticker),
   200	                'sector': info.get('sector', 'Unknown'),
   201	                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
   202	                'week_52_high': info.get('fiftyTwoWeekHigh'),
   203	                'week_52_low': info.get('fiftyTwoWeekLow'),
   204	                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
   205	                'pb_ratio': info.get('priceToBook'),
   206	                'debt_to_equity': info.get('debtToEquity'),
   207	                'free_cash_flow': info.get('freeCashflow'),
   208	                'market_cap': info.get('marketCap'),
   209	                'trailing_eps': info.get('trailingEps'),
   210	                'forward_eps': info.get('forwardEps'),
   211	                'dividend_yield': info.get('dividendYield'),
   212	                'fetch_date': datetime.now().isoformat()
   213	            }
   214	
   215	            # Log warnings for missing data
   216	            missing_fields = [k for k, v in fundamentals.items() if v is None and k not in ['ticker', 'name', 'sector', 'fetch_date']]
   217	            if missing_fields:
   218	                logger.warning(f"Missing data for {ticker}: {', '.join(missing_fields)}")
   219	
   220	            # Cache the results
   221	            self._save_to_cache(fundamentals, cache_path)
   222	
   223	            logger.info(f"Successfully fetched fundamentals for {ticker}")
   224	            return fundamentals
   225	
   226	        except Exception as e:
   227	            logger.error(f"Error extracting fundamentals for {ticker}: {e}")
   228	            return {}
   229	
   230	    def fetch_price_history(
   231	        self,
   232	        ticker: str,
   233	        period: str = "5y",
   234	        interval: str = "1d"
   235	    ) -> pd.DataFrame:
   236	        """Fetch historical price data for a stock.
   237	
   238	        Retrieves OHLCV (Open, High, Low, Close, Volume) data for the specified period.
   239	
   240	        Args:
   241	            ticker: Stock ticker symbol (e.g., 'AAPL').
   242	            period: Time period for historical data. Valid values: 1d, 5d, 1mo, 3mo,
   243	                   6mo, 1y, 2y, 5y, 10y, ytd, max. Default is '5y'.
   244	            interval: Data interval. Valid values: 1m, 2m, 5m, 15m, 30m, 60m, 90m,
   245	                     1h, 1d, 5d, 1wk, 1mo, 3mo. Default is '1d'.
   246	
   247	        Returns:
   248	            DataFrame with columns: Date (index), Open, High, Low, Close, Volume.
   249	            Returns empty DataFrame on failure.
   250	
   251	        Example:
   252	            >>> fetcher = YahooFinanceFetcher()
   253	            >>> prices = fetcher.fetch_price_history("AAPL", period="1y")
   254	            >>> print(prices.head())
   255	        """
   256	        cache_path = self._get_cache_path(ticker, f'prices_{period}_{interval}')
   257	
   258	        # Check cache first
   259	        if self._is_cache_valid(cache_path):
   260	            cached_data = self._load_from_cache(cache_path)
   261	            if cached_data is not None and isinstance(cached_data, pd.DataFrame):
   262	                return cached_data
   263	
   264	        # Fetch from API
   265	        logger.info(f"Fetching price history for {ticker} (period={period}, interval={interval})")
   266	        stock = self._fetch_with_retry(ticker)
   267	
   268	        if stock is None:
   269	            logger.error(f"Could not fetch price history for {ticker}")
   270	            return pd.DataFrame()
   271	
   272	        try:
   273	            # Fetch historical data
   274	            hist = stock.history(period=period, interval=interval)
   275	
   276	            if hist.empty:
   277	                logger.warning(f"No price history data available for {ticker}")
   278	                return pd.DataFrame()
   279	
   280	            # Clean up the DataFrame - keep DatetimeIndex for consistency with git_fetcher
   281	            # DO NOT reset_index() - we want to preserve the DatetimeIndex from yfinance
   282	            hist.columns = [col.capitalize() for col in hist.columns]
   283	
   284	            # Ensure index is DatetimeIndex (yfinance should provide this)
   285	            if not isinstance(hist.index, pd.DatetimeIndex):
   286	                logger.warning(f"{ticker}: yfinance returned non-DatetimeIndex: {type(hist.index)}")
   287	                return pd.DataFrame()
   288	
   289	            # Select only OHLCV columns (no 'Date' column - it's the index)
   290	            available_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
   291	            hist = hist[[col for col in available_cols if col in hist.columns]]
   292	
   293	            # Cache the results
   294	            self._save_to_cache(hist, cache_path)
   295	
   296	            logger.info(f"Successfully fetched {len(hist)} price records for {ticker}")
   297	            return hist
   298	
   299	        except Exception as e:
   300	            logger.error(f"Error fetching price history for {ticker}: {e}")
   301	            return pd.DataFrame()
   302	
   303	    def fetch_multiple(
   304	        self,
   305	        tickers: List[str],
   306	        period: str = "5y"
   307	    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
   308	        """Fetch fundamentals and price history for multiple stocks.
   309	
   310	        Args:
   311	            tickers: List of stock ticker symbols.
   312	            period: Time period for historical data (default: '5y').
   313	
   314	        Returns:
   315	            Tuple of (fundamentals_df, prices_df):
   316	                - fundamentals_df: DataFrame with one row per ticker
   317	                - prices_df: DataFrame with all price data, includes 'ticker' column
   318	
   319	        Example:
   320	            >>> fetcher = YahooFinanceFetcher()
   321	            >>> fundamentals, prices = fetcher.fetch_multiple(["AAPL", "MSFT", "GOOGL"])
   322	            >>> print(fundamentals[['ticker', 'pe_ratio', 'pb_ratio']])
   323	        """
   324	        logger.info(f"Fetching data for {len(tickers)} tickers")
   325	
   326	        all_fundamentals = []
   327	        all_prices = []
   328	
   329	        for ticker in tickers:
   330	            # Fetch fundamentals
   331	            fundamentals = self.fetch_fundamentals(ticker)
   332	            if fundamentals:
   333	                all_fundamentals.append(fundamentals)
   334	
   335	            # Fetch price history
   336	            prices = self.fetch_price_history(ticker, period=period)
   337	            if not prices.empty:
   338	                prices['ticker'] = ticker
   339	                all_prices.append(prices)
   340	
   341	        # Combine all data
   342	        fundamentals_df = pd.DataFrame(all_fundamentals) if all_fundamentals else pd.DataFrame()
   343	        prices_df = pd.concat(all_prices, ignore_index=True) if all_prices else pd.DataFrame()
   344	
   345	        logger.info(
   346	            f"Fetched {len(all_fundamentals)}/{len(tickers)} fundamentals, "
   347	            f"{len(all_prices)}/{len(tickers)} price histories"
   348	        )
   349	
   350	        return fundamentals_df, prices_df
   351	
   352	    def clear_cache(self, ticker: Optional[str] = None) -> None:
   353	        """Clear cached data.
   354	
   355	        Args:
   356	            ticker: If provided, clears cache only for this ticker.
   357	                   If None, clears all cached data.
   358	
   359	        Example:
   360	            >>> fetcher = YahooFinanceFetcher()
   361	            >>> fetcher.clear_cache("AAPL")  # Clear only AAPL cache
   362	            >>> fetcher.clear_cache()  # Clear all cache
   363	        """
   364	        if ticker:
   365	            # Clear cache for specific ticker
   366	            pattern = f"{ticker}_*.pkl"
   367	            removed = 0
   368	            for cache_file in self.cache_dir.glob(pattern):
   369	                try:
   370	                    cache_file.unlink()
   371	                    removed += 1
   372	                except Exception as e:
   373	                    logger.warning(f"Failed to remove cache file {cache_file}: {e}")
   374	            logger.info(f"Cleared {removed} cache file(s) for {ticker}")
   375	        else:
   376	            # Clear all cache
   377	            removed = 0
   378	            for cache_file in self.cache_dir.glob("*.pkl"):
   379	                try:
   380	                    cache_file.unlink()
   381	                    removed += 1
   382	                except Exception as e:
   383	                    logger.warning(f"Failed to remove cache file {cache_file}: {e}")
   384	            logger.info(f"Cleared {removed} cache file(s)")
     1	"""Smart data fetcher with incremental updates and earnings-aware caching.
     2	
     3	This module provides an optimized data fetching strategy that minimizes API calls:
     4	- Incremental price updates (fetch only new days, not full history)
     5	- Earnings-aware fundamental refresh (only update during earnings season)
     6	- GitHub Actions cache integration (persist data across workflow runs)
     7	
     8	Reduces API calls by 89-96% compared to naive full fetching.
     9	"""
    10	
    11	import logging
    12	import pickle
    13	from datetime import datetime, timedelta
    14	from pathlib import Path
    15	from typing import Dict, Optional
    16	
    17	import pandas as pd
    18	import yfinance as yf
    19	
    20	logging.basicConfig(
    21	    level=logging.INFO,
    22	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    23	)
    24	logger = logging.getLogger(__name__)
    25	
    26	
    27	class SmartDataFetcher:
    28	    """Fetches data intelligently with incremental updates and smart caching."""
    29	
    30	    def __init__(self, cache_dir: str = "./data/cache"):
    31	        """Initialize smart fetcher.
    32	
    33	        Args:
    34	            cache_dir: Root directory for cache storage
    35	        """
    36	        self.cache_dir = Path(cache_dir)
    37	        self.cache_dir.mkdir(parents=True, exist_ok=True)
    38	
    39	        # Separate subdirectories for different data types
    40	        self.price_cache_dir = self.cache_dir / "price_history"
    41	        self.fundamental_cache_dir = self.cache_dir / "fundamentals"
    42	        self.price_cache_dir.mkdir(exist_ok=True)
    43	        self.fundamental_cache_dir.mkdir(exist_ok=True)
    44	
    45	        logger.info(f"SmartDataFetcher initialized with cache: {cache_dir}")
    46	
    47	    def fetch_price_incremental(
    48	        self,
    49	        ticker: str,
    50	        required_days: int = 250
    51	    ) -> pd.DataFrame:
    52	        """Fetch price data incrementally.
    53	
    54	        Strategy:
    55	        - If cache exists and is recent (≤5 days old): fetch only last 5 days and merge
    56	        - If cache is old or missing: fetch full period (1 year)
    57	
    58	        Args:
    59	            ticker: Stock ticker symbol
    60	            required_days: Number of days needed for indicators (default 250 for 200 SMA)
    61	
    62	        Returns:
    63	            DataFrame with at least required_days of price data
    64	        """
    65	        cache_path = self.price_cache_dir / f"{ticker}_prices.pkl"
    66	        cache_meta_path = self.price_cache_dir / f"{ticker}_prices_meta.pkl"
    67	
    68	        # Try to load cached data
    69	        cached_data = None
    70	        cache_date = None
    71	
    72	        if cache_path.exists() and cache_meta_path.exists():
    73	            try:
    74	                with open(cache_path, 'rb') as f:
    75	                    cached_data = pickle.load(f)
    76	                with open(cache_meta_path, 'rb') as f:
    77	                    cache_meta = pickle.load(f)
    78	                    cache_date = cache_meta.get('last_updated')
    79	
    80	                logger.debug(f"{ticker}: Found cached data from {cache_date}")
    81	            except Exception as e:
    82	                logger.warning(f"{ticker}: Failed to load cache: {e}")
    83	                cached_data = None
    84	
    85	        # Determine if we can do incremental update
    86	        can_increment = False
    87	        days_old = 0
    88	
    89	        if cached_data is not None and cache_date is not None:
    90	            days_old = (datetime.now() - cache_date).days
    91	            # Can increment if cache is recent and has enough data
    92	            if days_old <= 5 and len(cached_data) >= required_days - 10:
    93	                can_increment = True
    94	
    95	        if can_increment:
    96	            # INCREMENTAL UPDATE - fetch only recent data
    97	            logger.info(f"{ticker}: Incremental update (cache {days_old} days old)")
    98	
    99	            try:
   100	                stock = yf.Ticker(ticker)
   101	                # Fetch last 5 days to ensure overlap with cache
   102	                new_data = stock.history(period='5d', interval='1d')
   103	
   104	                if not new_data.empty:
   105	                    # Merge cached + new data
   106	                    merged = self._merge_price_data(cached_data, new_data, required_days)
   107	
   108	                    # Save updated cache
   109	                    self._save_price_cache(ticker, merged)
   110	
   111	                    logger.info(f"{ticker}: Incremental update successful ({len(merged)} days)")
   112	                    return merged
   113	                else:
   114	                    logger.warning(f"{ticker}: Incremental fetch returned no data, using cache")
   115	                    return cached_data
   116	
   117	            except Exception as e:
   118	                logger.error(f"{ticker}: Incremental update failed: {e}, using cache")
   119	                return cached_data if cached_data is not None else pd.DataFrame()
   120	
   121	        else:
   122	            # FULL FETCH - no cache or cache too old
   123	            reason = "no cache" if cached_data is None else f"cache {days_old} days old"
   124	            logger.info(f"{ticker}: Full fetch ({reason})")
   125	
   126	            try:
   127	                stock = yf.Ticker(ticker)
   128	                # Fetch 1 year of data (~250 trading days)
   129	                data = stock.history(period='1y', interval='1d')
   130	
   131	                if not data.empty:
   132	                    # Save to cache
   133	                    self._save_price_cache(ticker, data)
   134	                    logger.info(f"{ticker}: Full fetch successful ({len(data)} days)")
   135	                    return data
   136	                else:
   137	                    logger.warning(f"{ticker}: Full fetch returned no data")
   138	                    return pd.DataFrame()
   139	
   140	            except Exception as e:
   141	                logger.error(f"{ticker}: Full fetch failed: {e}")
   142	                return pd.DataFrame()
   143	
   144	    def fetch_fundamentals_smart(self, ticker: str) -> Dict:
   145	        """Fetch fundamentals with earnings-aware caching.
   146	
   147	        Refresh logic:
   148	        - During earnings season (6-week windows): refresh if >7 days old
   149	        - Outside earnings season: refresh if >90 days old
   150	        - Never fetched before: fetch now
   151	
   152	        Earnings seasons:
   153	        - Q4: Jan 15 - Feb 15
   154	        - Q1: Apr 15 - May 15
   155	        - Q2: Jul 15 - Aug 15
   156	        - Q3: Oct 15 - Nov 15
   157	
   158	        Args:
   159	            ticker: Stock ticker symbol
   160	
   161	        Returns:
   162	            Dict with quarterly fundamental data
   163	        """
   164	        cache_path = self.fundamental_cache_dir / f"{ticker}_fundamentals.pkl"
   165	
   166	        # Check if we need to refresh
   167	        should_refresh = self._should_refresh_fundamentals(cache_path)
   168	
   169	        if not should_refresh and cache_path.exists():
   170	            try:
   171	                with open(cache_path, 'rb') as f:
   172	                    cached = pickle.load(f)
   173	                logger.debug(f"{ticker}: Using cached fundamentals")
   174	                return cached.get('data', {})
   175	            except Exception as e:
   176	                logger.warning(f"{ticker}: Cache load failed: {e}, refreshing")
   177	
   178	        # Fetch fresh fundamentals
   179	        logger.info(f"{ticker}: Fetching fresh fundamentals")
   180	
   181	        try:
   182	            from .fundamentals_fetcher import fetch_quarterly_financials
   183	            data = fetch_quarterly_financials(ticker)
   184	
   185	            if data:
   186	                # Save to cache with timestamp
   187	                with open(cache_path, 'wb') as f:
   188	                    pickle.dump({
   189	                        'data': data,
   190	                        'fetched_at': datetime.now()
   191	                    }, f)
   192	
   193	                return data
   194	            else:
   195	                return {}
   196	
   197	        except Exception as e:
   198	            logger.error(f"{ticker}: Fundamental fetch failed: {e}")
   199	            return {}
   200	
   201	    def _merge_price_data(
   202	        self,
   203	        old_data: pd.DataFrame,
   204	        new_data: pd.DataFrame,
   205	        keep_days: int
   206	    ) -> pd.DataFrame:
   207	        """Merge old and new price data, keeping only keep_days most recent.
   208	
   209	        Args:
   210	            old_data: Previously cached price data
   211	            new_data: Newly fetched price data
   212	            keep_days: Number of days to retain
   213	
   214	        Returns:
   215	            Merged DataFrame with most recent keep_days
   216	        """
   217	        # Ensure both have Date column
   218	        if 'Date' not in old_data.columns and old_data.index.name == 'Date':
   219	            old_data = old_data.reset_index()
   220	        if 'Date' not in new_data.columns and new_data.index.name == 'Date':
   221	            new_data = new_data.reset_index()
   222	
   223	        # Combine
   224	        combined = pd.concat([old_data, new_data], ignore_index=True)
   225	
   226	        # Remove duplicates (keep latest)
   227	        combined['Date'] = pd.to_datetime(combined['Date'])
   228	        combined = combined.sort_values('Date')
   229	        combined = combined.drop_duplicates(subset=['Date'], keep='last')
   230	
   231	        # Keep only most recent keep_days
   232	        if len(combined) > keep_days:
   233	            combined = combined.iloc[-keep_days:]
   234	
   235	        return combined.reset_index(drop=True)
   236	
   237	    def _save_price_cache(self, ticker: str, data: pd.DataFrame):
   238	        """Save price data and metadata to cache.
   239	
   240	        Args:
   241	            ticker: Stock ticker symbol
   242	            data: Price data to cache
   243	        """
   244	        cache_path = self.price_cache_dir / f"{ticker}_prices.pkl"
   245	        cache_meta_path = self.price_cache_dir / f"{ticker}_prices_meta.pkl"
   246	
   247	        try:
   248	            with open(cache_path, 'wb') as f:
   249	                pickle.dump(data, f)
   250	
   251	            meta = {
   252	                'last_updated': datetime.now(),
   253	                'num_days': len(data)
   254	            }
   255	            with open(cache_meta_path, 'wb') as f:
   256	                pickle.dump(meta, f)
   257	
   258	            logger.debug(f"{ticker}: Cache saved ({len(data)} days)")
   259	
   260	        except Exception as e:
   261	            logger.warning(f"{ticker}: Failed to save cache: {e}")
   262	
   263	    def _should_refresh_fundamentals(self, cache_path: Path) -> bool:
   264	        """Determine if fundamentals should be refreshed.
   265	
   266	        Args:
   267	            cache_path: Path to fundamental cache file
   268	
   269	        Returns:
   270	            True if should refresh, False otherwise
   271	        """
   272	        if not cache_path.exists():
   273	            return True
   274	
   275	        try:
   276	            with open(cache_path, 'rb') as f:
   277	                cached = pickle.load(f)
   278	                fetched_at = cached.get('fetched_at')
   279	
   280	            if fetched_at is None:
   281	                return True
   282	
   283	            days_old = (datetime.now() - fetched_at).days
   284	
   285	            if self._is_earnings_season():
   286	                # During earnings season: refresh weekly
   287	                return days_old >= 7
   288	            else:
   289	                # Outside earnings season: refresh quarterly
   290	                return days_old >= 90
   291	
   292	        except Exception as e:
   293	            logger.warning(f"Cache check failed: {e}, will refresh")
   294	            return True
   295	
   296	    def _is_earnings_season(self) -> bool:
   297	        """Check if currently in earnings season.
   298	
   299	        Earnings seasons (typical 6-week windows):
   300	        - Q4: Jan 15 - Feb 15 (FY prior year reports)
   301	        - Q1: Apr 15 - May 15
   302	        - Q2: Jul 15 - Aug 15
   303	        - Q3: Oct 15 - Nov 15
   304	
   305	        Returns:
   306	            True if in earnings season, False otherwise
   307	        """
   308	        now = datetime.now()
   309	        month = now.month
   310	        day = now.day
   311	
   312	        earnings_windows = [
   313	            (1, 15, 2, 15),   # Q4 earnings: Jan 15 - Feb 15
   314	            (4, 15, 5, 15),   # Q1 earnings: Apr 15 - May 15
   315	            (7, 15, 8, 15),   # Q2 earnings: Jul 15 - Aug 15
   316	            (10, 15, 11, 15)  # Q3 earnings: Oct 15 - Nov 15
   317	        ]
   318	
   319	        for start_month, start_day, end_month, end_day in earnings_windows:
   320	            if start_month == end_month:
   321	                if month == start_month and start_day <= day <= end_day:
   322	                    return True
   323	            else:
   324	                # Handle cross-month windows (though current windows don't cross)
   325	                if (month == start_month and day >= start_day) or \
   326	                   (month == end_month and day <= end_day):
   327	                    return True
   328	
   329	        return False
   330	
   331	    def get_cache_stats(self) -> Dict:
   332	        """Get cache statistics.
   333	
   334	        Returns:
   335	            Dict with cache size, hit rate, etc.
   336	        """
   337	        price_files = list(self.price_cache_dir.glob("*_prices.pkl"))
   338	        fundamental_files = list(self.fundamental_cache_dir.glob("*_fundamentals.pkl"))
   339	
   340	        stats = {
   341	            'price_cache_count': len(price_files),
   342	            'fundamental_cache_count': len(fundamental_files),
   343	            'in_earnings_season': self._is_earnings_season(),
   344	            'cache_dir': str(self.cache_dir)
   345	        }
   346	
   347	        return stats
     1	"""Database storage module for stock data using SQLAlchemy.
     2	
     3	This module provides a PostgreSQL/SQLite storage layer for persisting stock
     4	fundamentals and price history data with efficient querying capabilities.
     5	"""
     6	
     7	import logging
     8	import os
     9	from datetime import datetime
    10	from typing import Dict, List, Optional
    11	
    12	import pandas as pd
    13	from dotenv import load_dotenv
    14	from sqlalchemy import (
    15	    Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint,
    16	    create_engine, func, Index
    17	)
    18	from sqlalchemy.exc import IntegrityError, SQLAlchemyError
    19	from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
    20	from sqlalchemy.pool import QueuePool
    21	
    22	# Load environment variables
    23	load_dotenv()
    24	
    25	# Configure logging
    26	logging.basicConfig(
    27	    level=logging.INFO,
    28	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    29	)
    30	logger = logging.getLogger(__name__)
    31	
    32	# SQLAlchemy Base
    33	Base = declarative_base()
    34	
    35	
    36	class Stock(Base):
    37	    """Stock master table storing basic stock information.
    38	
    39	    Attributes:
    40	        id: Primary key.
    41	        ticker: Unique stock ticker symbol (e.g., 'AAPL').
    42	        name: Company name.
    43	        sector: Industry sector.
    44	        last_updated: Timestamp of last data update.
    45	    """
    46	
    47	    __tablename__ = 'stocks'
    48	
    49	    id = Column(Integer, primary_key=True, autoincrement=True)
    50	    ticker = Column(String(10), unique=True, nullable=False, index=True)
    51	    name = Column(String(200))
    52	    sector = Column(String(100))
    53	    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    54	
    55	    # Relationships
    56	    fundamentals = relationship('Fundamental', back_populates='stock', cascade='all, delete-orphan')
    57	    price_history = relationship('PriceHistory', back_populates='stock', cascade='all, delete-orphan')
    58	
    59	    def __repr__(self) -> str:
    60	        return f"<Stock(ticker='{self.ticker}', name='{self.name}', sector='{self.sector}')>"
    61	
    62	
    63	class Fundamental(Base):
    64	    """Fundamental metrics table storing financial ratios and metrics.
    65	
    66	    Attributes:
    67	        id: Primary key.
    68	        stock_id: Foreign key to Stock table.
    69	        date: Date of fundamental data.
    70	        pe_ratio: Price-to-Earnings ratio.
    71	        pb_ratio: Price-to-Book ratio.
    72	        debt_equity: Debt-to-Equity ratio.
    73	        fcf_yield: Free Cash Flow yield.
    74	        market_cap: Market capitalization.
    75	        current_price: Current stock price.
    76	        week_52_high: 52-week high price.
    77	        week_52_low: 52-week low price.
    78	        trailing_eps: Trailing EPS.
    79	        forward_eps: Forward EPS.
    80	        dividend_yield: Dividend yield percentage.
    81	    """
    82	
    83	    __tablename__ = 'fundamentals'
    84	
    85	    id = Column(Integer, primary_key=True, autoincrement=True)
    86	    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    87	    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    88	    pe_ratio = Column(Float)
    89	    pb_ratio = Column(Float)
    90	    debt_equity = Column(Float)
    91	    fcf_yield = Column(Float)
    92	    market_cap = Column(Float)
    93	    current_price = Column(Float)
    94	    week_52_high = Column(Float)
    95	    week_52_low = Column(Float)
    96	    trailing_eps = Column(Float)
    97	    forward_eps = Column(Float)
    98	    dividend_yield = Column(Float)
    99	
   100	    # Relationships
   101	    stock = relationship('Stock', back_populates='fundamentals')
   102	
   103	    # Composite index for efficient queries
   104	    __table_args__ = (
   105	        Index('ix_fundamentals_stock_date', 'stock_id', 'date'),
   106	    )
   107	
   108	    def __repr__(self) -> str:
   109	        return f"<Fundamental(stock_id={self.stock_id}, date='{self.date}', pe={self.pe_ratio})>"
   110	
   111	
   112	class PriceHistory(Base):
   113	    """Price history table storing daily OHLCV data.
   114	
   115	    Attributes:
   116	        id: Primary key.
   117	        stock_id: Foreign key to Stock table.
   118	        date: Trading date.
   119	        open: Opening price.
   120	        high: High price.
   121	        low: Low price.
   122	        close: Closing price.
   123	        volume: Trading volume.
   124	    """
   125	
   126	    __tablename__ = 'price_history'
   127	
   128	    id = Column(Integer, primary_key=True, autoincrement=True)
   129	    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
   130	    date = Column(DateTime, nullable=False, index=True)
   131	    open = Column(Float)
   132	    high = Column(Float)
   133	    low = Column(Float)
   134	    close = Column(Float)
   135	    volume = Column(Float)
   136	
   137	    # Relationships
   138	    stock = relationship('Stock', back_populates='price_history')
   139	
   140	    # Composite unique constraint to prevent duplicate entries
   141	    __table_args__ = (
   142	        UniqueConstraint('stock_id', 'date', name='uix_stock_date'),
   143	        Index('ix_price_history_stock_date', 'stock_id', 'date'),
   144	    )
   145	
   146	    def __repr__(self) -> str:
   147	        return f"<PriceHistory(stock_id={self.stock_id}, date='{self.date}', close={self.close})>"
   148	
   149	
   150	class DataQualityLog(Base):
   151	    """Data quality check log table storing quality check results.
   152	
   153	    Attributes:
   154	        id: Primary key.
   155	        ticker: Stock ticker symbol.
   156	        check_date: Date when quality check was performed.
   157	        overall_score: Overall quality score (0-100).
   158	        has_critical_issues: Whether critical issues were found.
   159	        needs_refresh: Whether data needs to be refreshed.
   160	        num_issues: Total number of issues found.
   161	        issue_summary: Summary of issues (first 5).
   162	    """
   163	
   164	    __tablename__ = 'data_quality_log'
   165	
   166	    id = Column(Integer, primary_key=True, autoincrement=True)
   167	    ticker = Column(String(10), nullable=False, index=True)
   168	    check_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
   169	    overall_score = Column(Float)
   170	    has_critical_issues = Column(Integer)  # SQLite doesn't have Boolean, use 0/1
   171	    needs_refresh = Column(Integer)  # SQLite doesn't have Boolean, use 0/1
   172	    num_issues = Column(Integer)
   173	    issue_summary = Column(String(1000))
   174	
   175	    # Composite index for efficient queries
   176	    __table_args__ = (
   177	        Index('ix_quality_log_ticker_date', 'ticker', 'check_date'),
   178	    )
   179	
   180	    def __repr__(self) -> str:
   181	        return f"<DataQualityLog(ticker='{self.ticker}', score={self.overall_score}, date='{self.check_date}')>"
   182	
   183	
   184	class StockDatabase:
   185	    """Database interface for storing and querying stock data.
   186	
   187	    This class provides methods to save and retrieve stock fundamentals and
   188	    price history data using SQLAlchemy ORM with support for PostgreSQL and SQLite.
   189	
   190	    Attributes:
   191	        engine: SQLAlchemy engine instance.
   192	        Session: SQLAlchemy session factory.
   193	
   194	    Example:
   195	        >>> db = StockDatabase()
   196	        >>> db.save_stock_fundamentals("AAPL", {"pe_ratio": 25.5, "pb_ratio": 45.2})
   197	        >>> history = db.get_price_history("AAPL", "2023-01-01", "2024-01-01")
   198	        >>> cheap = db.query_cheap_stocks(pe_max=15, pb_max=1.5)
   199	    """
   200	
   201	    def __init__(self, db_url: Optional[str] = None) -> None:
   202	        """Initialize the StockDatabase with connection to PostgreSQL or SQLite.
   203	
   204	        Args:
   205	            db_url: Database URL. If None, reads from DATABASE_URL environment variable.
   206	                   Falls back to SQLite if not provided.
   207	
   208	        Example:
   209	            >>> db = StockDatabase("postgresql://user:pass@localhost:5432/stocks")
   210	            >>> db = StockDatabase("sqlite:///./stock_screener.db")
   211	            >>> db = StockDatabase()  # Uses environment variable or SQLite
   212	        """
   213	        if db_url is None:
   214	            db_url = os.getenv('DATABASE_URL', 'sqlite:///./stock_screener.db')
   215	
   216	        logger.info(f"Initializing database connection: {db_url.split('@')[-1]}")
   217	
   218	        # Create engine with connection pooling for production
   219	        if db_url.startswith('postgresql'):
   220	            self.engine = create_engine(
   221	                db_url,
   222	                poolclass=QueuePool,
   223	                pool_size=5,
   224	                max_overflow=10,
   225	                pool_pre_ping=True,  # Verify connections before using
   226	                echo=False
   227	            )
   228	        else:
   229	            self.engine = create_engine(db_url, echo=False)
   230	
   231	        # Create session factory
   232	        self.Session = sessionmaker(bind=self.engine)
   233	
   234	        # Create all tables
   235	        Base.metadata.create_all(self.engine)
   236	        logger.info("Database tables created/verified successfully")
   237	
   238	    def _get_or_create_stock(self, session: Session, ticker: str, name: str = None, sector: str = None) -> Stock:
   239	        """Get existing stock or create new one.
   240	
   241	        Args:
   242	            session: SQLAlchemy session.
   243	            ticker: Stock ticker symbol.
   244	            name: Company name (optional).
   245	            sector: Industry sector (optional).
   246	
   247	        Returns:
   248	            Stock ORM object.
   249	        """
   250	        stock = session.query(Stock).filter_by(ticker=ticker.upper()).first()
   251	
   252	        if stock is None:
   253	            stock = Stock(
   254	                ticker=ticker.upper(),
   255	                name=name or ticker,
   256	                sector=sector or 'Unknown'
   257	            )
   258	            session.add(stock)
   259	            session.flush()  # Get the ID without committing
   260	            logger.info(f"Created new stock entry: {ticker}")
   261	        else:
   262	            # Update name and sector if provided
   263	            if name and stock.name != name:
   264	                stock.name = name
   265	            if sector and stock.sector != sector:
   266	                stock.sector = sector
   267	            stock.last_updated = datetime.utcnow()
   268	
   269	        return stock
   270	
   271	    def save_stock_fundamentals(self, ticker: str, data: Dict[str, any]) -> None:
   272	        """Save fundamental data for a stock.
   273	
   274	        Args:
   275	            ticker: Stock ticker symbol.
   276	            data: Dictionary containing fundamental metrics. Expected keys:
   277	                 'name', 'sector', 'pe_ratio', 'pb_ratio', 'debt_to_equity',
   278	                 'free_cash_flow', 'current_price', 'week_52_high', 'week_52_low',
   279	                 'market_cap', 'trailing_eps', 'forward_eps', 'dividend_yield'.
   280	
   281	        Raises:
   282	            SQLAlchemyError: If database operation fails.
   283	
   284	        Example:
   285	            >>> db = StockDatabase()
   286	            >>> data = {
   287	            ...     'name': 'Apple Inc.',
   288	            ...     'sector': 'Technology',
   289	            ...     'pe_ratio': 25.5,
   290	            ...     'pb_ratio': 45.2,
   291	            ...     'debt_to_equity': 1.73
   292	            ... }
   293	            >>> db.save_stock_fundamentals("AAPL", data)
   294	        """
   295	        session = self.Session()
   296	        try:
   297	            # Get or create stock
   298	            stock = self._get_or_create_stock(
   299	                session,
   300	                ticker,
   301	                data.get('name'),
   302	                data.get('sector')
   303	            )
   304	
   305	            # Create fundamental entry
   306	            fundamental = Fundamental(
   307	                stock_id=stock.id,
   308	                date=datetime.utcnow(),
   309	                pe_ratio=data.get('pe_ratio'),
   310	                pb_ratio=data.get('pb_ratio'),
   311	                debt_equity=data.get('debt_to_equity'),
   312	                fcf_yield=self._calculate_fcf_yield(data),
   313	                market_cap=data.get('market_cap'),
   314	                current_price=data.get('current_price'),
   315	                week_52_high=data.get('week_52_high'),
   316	                week_52_low=data.get('week_52_low'),
   317	                trailing_eps=data.get('trailing_eps'),
   318	                forward_eps=data.get('forward_eps'),
   319	                dividend_yield=data.get('dividend_yield')
   320	            )
   321	
   322	            session.add(fundamental)
   323	            session.commit()
   324	            logger.info(f"Saved fundamentals for {ticker}")
   325	
   326	        except SQLAlchemyError as e:
   327	            session.rollback()
   328	            logger.error(f"Failed to save fundamentals for {ticker}: {e}")
   329	            raise
   330	        finally:
   331	            session.close()
   332	
   333	    def _calculate_fcf_yield(self, data: Dict[str, any]) -> Optional[float]:
   334	        """Calculate Free Cash Flow yield.
   335	
   336	        Args:
   337	            data: Dictionary containing 'free_cash_flow' and 'market_cap'.
   338	
   339	        Returns:
   340	            FCF yield as percentage, or None if calculation not possible.
   341	        """
   342	        fcf = data.get('free_cash_flow')
   343	        market_cap = data.get('market_cap')
   344	
   345	        if fcf and market_cap and market_cap > 0:
   346	            return (fcf / market_cap) * 100
   347	        return None
   348	
   349	    def save_price_history(self, ticker: str, df: pd.DataFrame) -> None:
   350	        """Save historical price data for a stock (bulk insert).
   351	
   352	        Args:
   353	            ticker: Stock ticker symbol.
   354	            df: DataFrame with columns: Date, Open, High, Low, Close, Volume.
   355	
   356	        Raises:
   357	            ValueError: If DataFrame is empty or missing required columns.
   358	            SQLAlchemyError: If database operation fails.
   359	
   360	        Example:
   361	            >>> db = StockDatabase()
   362	            >>> prices = pd.DataFrame({
   363	            ...     'Date': ['2024-01-01', '2024-01-02'],
   364	            ...     'Open': [150.0, 151.0],
   365	            ...     'High': [152.0, 153.0],
   366	            ...     'Low': [149.0, 150.0],
   367	            ...     'Close': [151.0, 152.0],
   368	            ...     'Volume': [1000000, 1100000]
   369	            ... })
   370	            >>> db.save_price_history("AAPL", prices)
   371	        """
   372	        if df.empty:
   373	            logger.warning(f"Empty DataFrame provided for {ticker}")
   374	            return
   375	
   376	        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
   377	        missing_cols = [col for col in required_cols if col not in df.columns]
   378	        if missing_cols:
   379	            raise ValueError(f"DataFrame missing required columns: {missing_cols}")
   380	
   381	        session = self.Session()
   382	        try:
   383	            # Get or create stock
   384	            stock = self._get_or_create_stock(session, ticker)
   385	
   386	            # Prepare bulk insert data
   387	            records = []
   388	            for _, row in df.iterrows():
   389	                records.append({
   390	                    'stock_id': stock.id,
   391	                    'date': pd.to_datetime(row['Date']),
   392	                    'open': float(row['Open']) if pd.notna(row['Open']) else None,
   393	                    'high': float(row['High']) if pd.notna(row['High']) else None,
   394	                    'low': float(row['Low']) if pd.notna(row['Low']) else None,
   395	                    'close': float(row['Close']) if pd.notna(row['Close']) else None,
   396	                    'volume': float(row['Volume']) if pd.notna(row['Volume']) else None
   397	                })
   398	
   399	            # Bulk insert with ignore on conflict (for duplicates)
   400	            if records:
   401	                for record in records:
   402	                    try:
   403	                        price = PriceHistory(**record)
   404	                        session.add(price)
   405	                    except IntegrityError:
   406	                        session.rollback()
   407	                        # Update existing record instead
   408	                        existing = session.query(PriceHistory).filter_by(
   409	                            stock_id=record['stock_id'],
   410	                            date=record['date']
   411	                        ).first()
   412	                        if existing:
   413	                            for key, value in record.items():
   414	                                if key not in ['stock_id', 'date']:
   415	                                    setattr(existing, key, value)
   416	
   417	                session.commit()
   418	                logger.info(f"Saved {len(records)} price records for {ticker}")
   419	
   420	        except SQLAlchemyError as e:
   421	            session.rollback()
   422	            logger.error(f"Failed to save price history for {ticker}: {e}")
   423	            raise
   424	        finally:
   425	            session.close()
   426	
   427	    def get_latest_fundamentals(self, ticker: str) -> Dict[str, any]:
   428	        """Retrieve the most recent fundamental data for a stock.
   429	
   430	        Args:
   431	            ticker: Stock ticker symbol.
   432	
   433	        Returns:
   434	            Dictionary containing fundamental metrics, or empty dict if not found.
   435	
   436	        Example:
   437	            >>> db = StockDatabase()
   438	            >>> data = db.get_latest_fundamentals("AAPL")
   439	            >>> print(data['pe_ratio'])
   440	        """
   441	        session = self.Session()
   442	        try:
   443	            stock = session.query(Stock).filter_by(ticker=ticker.upper()).first()
   444	
   445	            if not stock:
   446	                logger.warning(f"Stock {ticker} not found in database")
   447	                return {}
   448	
   449	            # Get most recent fundamental entry
   450	            fundamental = (
   451	                session.query(Fundamental)
   452	                .filter_by(stock_id=stock.id)
   453	                .order_by(Fundamental.date.desc())
   454	                .first()
   455	            )
   456	
   457	            if not fundamental:
   458	                logger.warning(f"No fundamental data found for {ticker}")
   459	                return {}
   460	
   461	            return {
   462	                'ticker': stock.ticker,
   463	                'name': stock.name,
   464	                'sector': stock.sector,
   465	                'date': fundamental.date.isoformat(),
   466	                'pe_ratio': fundamental.pe_ratio,
   467	                'pb_ratio': fundamental.pb_ratio,
   468	                'debt_equity': fundamental.debt_equity,
   469	                'fcf_yield': fundamental.fcf_yield,
   470	                'market_cap': fundamental.market_cap,
   471	                'current_price': fundamental.current_price,
   472	                'week_52_high': fundamental.week_52_high,
   473	                'week_52_low': fundamental.week_52_low,
   474	                'trailing_eps': fundamental.trailing_eps,
   475	                'forward_eps': fundamental.forward_eps,
   476	                'dividend_yield': fundamental.dividend_yield
   477	            }
   478	
   479	        except SQLAlchemyError as e:
   480	            logger.error(f"Failed to get fundamentals for {ticker}: {e}")
   481	            return {}
   482	        finally:
   483	            session.close()
   484	
   485	    def get_price_history(
   486	        self,
   487	        ticker: str,
   488	        start_date: str,
   489	        end_date: str
   490	    ) -> pd.DataFrame:
   491	        """Retrieve historical price data for a stock within a date range.
   492	
   493	        Args:
   494	            ticker: Stock ticker symbol.
   495	            start_date: Start date in 'YYYY-MM-DD' format.
   496	            end_date: End date in 'YYYY-MM-DD' format.
   497	
   498	        Returns:
   499	            DataFrame with columns: Date, Open, High, Low, Close, Volume.
   500	            Returns empty DataFrame if no data found.
   501	
   502	        Example:
   503	            >>> db = StockDatabase()
   504	            >>> prices = db.get_price_history("AAPL", "2023-01-01", "2024-01-01")
   505	            >>> print(prices.head())
   506	        """
   507	        session = self.Session()
   508	        try:
   509	            stock = session.query(Stock).filter_by(ticker=ticker.upper()).first()
   510	
   511	            if not stock:
   512	                logger.warning(f"Stock {ticker} not found in database")
   513	                return pd.DataFrame()
   514	
   515	            # Parse dates
   516	            start = datetime.strptime(start_date, '%Y-%m-%d')
   517	            end = datetime.strptime(end_date, '%Y-%m-%d')
   518	
   519	            # Query price history
   520	            prices = (
   521	                session.query(PriceHistory)
   522	                .filter(
   523	                    PriceHistory.stock_id == stock.id,
   524	                    PriceHistory.date >= start,
   525	                    PriceHistory.date <= end
   526	                )
   527	                .order_by(PriceHistory.date)
   528	                .all()
   529	            )
   530	
   531	            if not prices:
   532	                logger.warning(f"No price history found for {ticker} in date range")
   533	                return pd.DataFrame()
   534	
   535	            # Convert to DataFrame
   536	            data = {
   537	                'Date': [p.date for p in prices],
   538	                'Open': [p.open for p in prices],
   539	                'High': [p.high for p in prices],
   540	                'Low': [p.low for p in prices],
   541	                'Close': [p.close for p in prices],
   542	                'Volume': [p.volume for p in prices]
   543	            }
   544	
   545	            df = pd.DataFrame(data)
   546	            logger.info(f"Retrieved {len(df)} price records for {ticker}")
   547	            return df
   548	
   549	        except ValueError as e:
   550	            logger.error(f"Invalid date format: {e}")
   551	            return pd.DataFrame()
   552	        except SQLAlchemyError as e:
   553	            logger.error(f"Failed to get price history for {ticker}: {e}")
   554	            return pd.DataFrame()
   555	        finally:
   556	            session.close()
   557	
   558	    def query_cheap_stocks(
   559	        self,
   560	        pe_max: float = 15,
   561	        pb_max: float = 1.5,
   562	        min_market_cap: Optional[float] = None
   563	    ) -> List[str]:
   564	        """Query stocks that meet value investing criteria.
   565	
   566	        Args:
   567	            pe_max: Maximum P/E ratio threshold (default: 15).
   568	            pb_max: Maximum P/B ratio threshold (default: 1.5).
   569	            min_market_cap: Minimum market cap filter (optional).
   570	
   571	        Returns:
   572	            List of ticker symbols meeting the criteria.
   573	
   574	        Example:
   575	            >>> db = StockDatabase()
   576	            >>> cheap_stocks = db.query_cheap_stocks(pe_max=15, pb_max=1.5)
   577	            >>> print(cheap_stocks)
   578	            ['AAPL', 'MSFT', 'GOOGL']
   579	        """
   580	        session = self.Session()
   581	        try:
   582	            # Subquery to get latest fundamental for each stock
   583	            subq = (
   584	                session.query(
   585	                    Fundamental.stock_id,
   586	                    func.max(Fundamental.date).label('max_date')
   587	                )
   588	                .group_by(Fundamental.stock_id)
   589	                .subquery()
   590	            )
   591	
   592	            # Main query with filters
   593	            query = (
   594	                session.query(Stock.ticker)
   595	                .join(Fundamental, Stock.id == Fundamental.stock_id)
   596	                .join(subq, (Fundamental.stock_id == subq.c.stock_id) &
   597	                           (Fundamental.date == subq.c.max_date))
   598	                .filter(
   599	                    Fundamental.pe_ratio.isnot(None),
   600	                    Fundamental.pb_ratio.isnot(None),
   601	                    Fundamental.pe_ratio > 0,
   602	                    Fundamental.pe_ratio <= pe_max,
   603	                    Fundamental.pb_ratio > 0,
   604	                    Fundamental.pb_ratio <= pb_max
   605	                )
   606	            )
   607	
   608	            # Add market cap filter if specified
   609	            if min_market_cap is not None:
   610	                query = query.filter(
   611	                    Fundamental.market_cap.isnot(None),
   612	                    Fundamental.market_cap >= min_market_cap
   613	                )
   614	
   615	            results = query.order_by(Stock.ticker).all()
   616	            tickers = [r[0] for r in results]
   617	
   618	            logger.info(
   619	                f"Found {len(tickers)} stocks with PE <= {pe_max} and PB <= {pb_max}"
   620	            )
   621	            return tickers
   622	
   623	        except SQLAlchemyError as e:
   624	            logger.error(f"Failed to query cheap stocks: {e}")
   625	            return []
   626	        finally:
   627	            session.close()
   628	
   629	    def get_all_tickers(self) -> List[str]:
   630	        """Get list of all tickers in the database.
   631	
   632	        Returns:
   633	            List of ticker symbols.
   634	
   635	        Example:
   636	            >>> db = StockDatabase()
   637	            >>> tickers = db.get_all_tickers()
   638	            >>> print(tickers)
   639	        """
   640	        session = self.Session()
   641	        try:
   642	            stocks = session.query(Stock.ticker).order_by(Stock.ticker).all()
   643	            return [s[0] for s in stocks]
   644	        except SQLAlchemyError as e:
   645	            logger.error(f"Failed to get all tickers: {e}")
   646	            return []
   647	        finally:
   648	            session.close()

exec
/bin/zsh -lc "nl -ba src/data/storage.py | sed -n '1,190p'; nl -ba src/data/smart_fetcher.py | sed -n '45,347p'; nl -ba src/data/git_storage_fetcher.py | sed -n '1,347p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Database storage module for stock data using SQLAlchemy.
     2	
     3	This module provides a PostgreSQL/SQLite storage layer for persisting stock
     4	fundamentals and price history data with efficient querying capabilities.
     5	"""
     6	
     7	import logging
     8	import os
     9	from datetime import datetime
    10	from typing import Dict, List, Optional
    11	
    12	import pandas as pd
    13	from dotenv import load_dotenv
    14	from sqlalchemy import (
    15	    Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint,
    16	    create_engine, func, Index
    17	)
    18	from sqlalchemy.exc import IntegrityError, SQLAlchemyError
    19	from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
    20	from sqlalchemy.pool import QueuePool
    21	
    22	# Load environment variables
    23	load_dotenv()
    24	
    25	# Configure logging
    26	logging.basicConfig(
    27	    level=logging.INFO,
    28	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    29	)
    30	logger = logging.getLogger(__name__)
    31	
    32	# SQLAlchemy Base
    33	Base = declarative_base()
    34	
    35	
    36	class Stock(Base):
    37	    """Stock master table storing basic stock information.
    38	
    39	    Attributes:
    40	        id: Primary key.
    41	        ticker: Unique stock ticker symbol (e.g., 'AAPL').
    42	        name: Company name.
    43	        sector: Industry sector.
    44	        last_updated: Timestamp of last data update.
    45	    """
    46	
    47	    __tablename__ = 'stocks'
    48	
    49	    id = Column(Integer, primary_key=True, autoincrement=True)
    50	    ticker = Column(String(10), unique=True, nullable=False, index=True)
    51	    name = Column(String(200))
    52	    sector = Column(String(100))
    53	    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    54	
    55	    # Relationships
    56	    fundamentals = relationship('Fundamental', back_populates='stock', cascade='all, delete-orphan')
    57	    price_history = relationship('PriceHistory', back_populates='stock', cascade='all, delete-orphan')
    58	
    59	    def __repr__(self) -> str:
    60	        return f"<Stock(ticker='{self.ticker}', name='{self.name}', sector='{self.sector}')>"
    61	
    62	
    63	class Fundamental(Base):
    64	    """Fundamental metrics table storing financial ratios and metrics.
    65	
    66	    Attributes:
    67	        id: Primary key.
    68	        stock_id: Foreign key to Stock table.
    69	        date: Date of fundamental data.
    70	        pe_ratio: Price-to-Earnings ratio.
    71	        pb_ratio: Price-to-Book ratio.
    72	        debt_equity: Debt-to-Equity ratio.
    73	        fcf_yield: Free Cash Flow yield.
    74	        market_cap: Market capitalization.
    75	        current_price: Current stock price.
    76	        week_52_high: 52-week high price.
    77	        week_52_low: 52-week low price.
    78	        trailing_eps: Trailing EPS.
    79	        forward_eps: Forward EPS.
    80	        dividend_yield: Dividend yield percentage.
    81	    """
    82	
    83	    __tablename__ = 'fundamentals'
    84	
    85	    id = Column(Integer, primary_key=True, autoincrement=True)
    86	    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    87	    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    88	    pe_ratio = Column(Float)
    89	    pb_ratio = Column(Float)
    90	    debt_equity = Column(Float)
    91	    fcf_yield = Column(Float)
    92	    market_cap = Column(Float)
    93	    current_price = Column(Float)
    94	    week_52_high = Column(Float)
    95	    week_52_low = Column(Float)
    96	    trailing_eps = Column(Float)
    97	    forward_eps = Column(Float)
    98	    dividend_yield = Column(Float)
    99	
   100	    # Relationships
   101	    stock = relationship('Stock', back_populates='fundamentals')
   102	
   103	    # Composite index for efficient queries
   104	    __table_args__ = (
   105	        Index('ix_fundamentals_stock_date', 'stock_id', 'date'),
   106	    )
   107	
   108	    def __repr__(self) -> str:
   109	        return f"<Fundamental(stock_id={self.stock_id}, date='{self.date}', pe={self.pe_ratio})>"
   110	
   111	
   112	class PriceHistory(Base):
   113	    """Price history table storing daily OHLCV data.
   114	
   115	    Attributes:
   116	        id: Primary key.
   117	        stock_id: Foreign key to Stock table.
   118	        date: Trading date.
   119	        open: Opening price.
   120	        high: High price.
   121	        low: Low price.
   122	        close: Closing price.
   123	        volume: Trading volume.
   124	    """
   125	
   126	    __tablename__ = 'price_history'
   127	
   128	    id = Column(Integer, primary_key=True, autoincrement=True)
   129	    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
   130	    date = Column(DateTime, nullable=False, index=True)
   131	    open = Column(Float)
   132	    high = Column(Float)
   133	    low = Column(Float)
   134	    close = Column(Float)
   135	    volume = Column(Float)
   136	
   137	    # Relationships
   138	    stock = relationship('Stock', back_populates='price_history')
   139	
   140	    # Composite unique constraint to prevent duplicate entries
   141	    __table_args__ = (
   142	        UniqueConstraint('stock_id', 'date', name='uix_stock_date'),
   143	        Index('ix_price_history_stock_date', 'stock_id', 'date'),
   144	    )
   145	
   146	    def __repr__(self) -> str:
   147	        return f"<PriceHistory(stock_id={self.stock_id}, date='{self.date}', close={self.close})>"
   148	
   149	
   150	class DataQualityLog(Base):
   151	    """Data quality check log table storing quality check results.
   152	
   153	    Attributes:
   154	        id: Primary key.
   155	        ticker: Stock ticker symbol.
   156	        check_date: Date when quality check was performed.
   157	        overall_score: Overall quality score (0-100).
   158	        has_critical_issues: Whether critical issues were found.
   159	        needs_refresh: Whether data needs to be refreshed.
   160	        num_issues: Total number of issues found.
   161	        issue_summary: Summary of issues (first 5).
   162	    """
   163	
   164	    __tablename__ = 'data_quality_log'
   165	
   166	    id = Column(Integer, primary_key=True, autoincrement=True)
   167	    ticker = Column(String(10), nullable=False, index=True)
   168	    check_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
   169	    overall_score = Column(Float)
   170	    has_critical_issues = Column(Integer)  # SQLite doesn't have Boolean, use 0/1
   171	    needs_refresh = Column(Integer)  # SQLite doesn't have Boolean, use 0/1
   172	    num_issues = Column(Integer)
   173	    issue_summary = Column(String(1000))
   174	
   175	    # Composite index for efficient queries
   176	    __table_args__ = (
   177	        Index('ix_quality_log_ticker_date', 'ticker', 'check_date'),
   178	    )
   179	
   180	    def __repr__(self) -> str:
   181	        return f"<DataQualityLog(ticker='{self.ticker}', score={self.overall_score}, date='{self.check_date}')>"
   182	
   183	
   184	class StockDatabase:
   185	    """Database interface for storing and querying stock data.
   186	
   187	    This class provides methods to save and retrieve stock fundamentals and
   188	    price history data using SQLAlchemy ORM with support for PostgreSQL and SQLite.
   189	
   190	    Attributes:
    45	        logger.info(f"SmartDataFetcher initialized with cache: {cache_dir}")
    46	
    47	    def fetch_price_incremental(
    48	        self,
    49	        ticker: str,
    50	        required_days: int = 250
    51	    ) -> pd.DataFrame:
    52	        """Fetch price data incrementally.
    53	
    54	        Strategy:
    55	        - If cache exists and is recent (≤5 days old): fetch only last 5 days and merge
    56	        - If cache is old or missing: fetch full period (1 year)
    57	
    58	        Args:
    59	            ticker: Stock ticker symbol
    60	            required_days: Number of days needed for indicators (default 250 for 200 SMA)
    61	
    62	        Returns:
    63	            DataFrame with at least required_days of price data
    64	        """
    65	        cache_path = self.price_cache_dir / f"{ticker}_prices.pkl"
    66	        cache_meta_path = self.price_cache_dir / f"{ticker}_prices_meta.pkl"
    67	
    68	        # Try to load cached data
    69	        cached_data = None
    70	        cache_date = None
    71	
    72	        if cache_path.exists() and cache_meta_path.exists():
    73	            try:
    74	                with open(cache_path, 'rb') as f:
    75	                    cached_data = pickle.load(f)
    76	                with open(cache_meta_path, 'rb') as f:
    77	                    cache_meta = pickle.load(f)
    78	                    cache_date = cache_meta.get('last_updated')
    79	
    80	                logger.debug(f"{ticker}: Found cached data from {cache_date}")
    81	            except Exception as e:
    82	                logger.warning(f"{ticker}: Failed to load cache: {e}")
    83	                cached_data = None
    84	
    85	        # Determine if we can do incremental update
    86	        can_increment = False
    87	        days_old = 0
    88	
    89	        if cached_data is not None and cache_date is not None:
    90	            days_old = (datetime.now() - cache_date).days
    91	            # Can increment if cache is recent and has enough data
    92	            if days_old <= 5 and len(cached_data) >= required_days - 10:
    93	                can_increment = True
    94	
    95	        if can_increment:
    96	            # INCREMENTAL UPDATE - fetch only recent data
    97	            logger.info(f"{ticker}: Incremental update (cache {days_old} days old)")
    98	
    99	            try:
   100	                stock = yf.Ticker(ticker)
   101	                # Fetch last 5 days to ensure overlap with cache
   102	                new_data = stock.history(period='5d', interval='1d')
   103	
   104	                if not new_data.empty:
   105	                    # Merge cached + new data
   106	                    merged = self._merge_price_data(cached_data, new_data, required_days)
   107	
   108	                    # Save updated cache
   109	                    self._save_price_cache(ticker, merged)
   110	
   111	                    logger.info(f"{ticker}: Incremental update successful ({len(merged)} days)")
   112	                    return merged
   113	                else:
   114	                    logger.warning(f"{ticker}: Incremental fetch returned no data, using cache")
   115	                    return cached_data
   116	
   117	            except Exception as e:
   118	                logger.error(f"{ticker}: Incremental update failed: {e}, using cache")
   119	                return cached_data if cached_data is not None else pd.DataFrame()
   120	
   121	        else:
   122	            # FULL FETCH - no cache or cache too old
   123	            reason = "no cache" if cached_data is None else f"cache {days_old} days old"
   124	            logger.info(f"{ticker}: Full fetch ({reason})")
   125	
   126	            try:
   127	                stock = yf.Ticker(ticker)
   128	                # Fetch 1 year of data (~250 trading days)
   129	                data = stock.history(period='1y', interval='1d')
   130	
   131	                if not data.empty:
   132	                    # Save to cache
   133	                    self._save_price_cache(ticker, data)
   134	                    logger.info(f"{ticker}: Full fetch successful ({len(data)} days)")
   135	                    return data
   136	                else:
   137	                    logger.warning(f"{ticker}: Full fetch returned no data")
   138	                    return pd.DataFrame()
   139	
   140	            except Exception as e:
   141	                logger.error(f"{ticker}: Full fetch failed: {e}")
   142	                return pd.DataFrame()
   143	
   144	    def fetch_fundamentals_smart(self, ticker: str) -> Dict:
   145	        """Fetch fundamentals with earnings-aware caching.
   146	
   147	        Refresh logic:
   148	        - During earnings season (6-week windows): refresh if >7 days old
   149	        - Outside earnings season: refresh if >90 days old
   150	        - Never fetched before: fetch now
   151	
   152	        Earnings seasons:
   153	        - Q4: Jan 15 - Feb 15
   154	        - Q1: Apr 15 - May 15
   155	        - Q2: Jul 15 - Aug 15
   156	        - Q3: Oct 15 - Nov 15
   157	
   158	        Args:
   159	            ticker: Stock ticker symbol
   160	
   161	        Returns:
   162	            Dict with quarterly fundamental data
   163	        """
   164	        cache_path = self.fundamental_cache_dir / f"{ticker}_fundamentals.pkl"
   165	
   166	        # Check if we need to refresh
   167	        should_refresh = self._should_refresh_fundamentals(cache_path)
   168	
   169	        if not should_refresh and cache_path.exists():
   170	            try:
   171	                with open(cache_path, 'rb') as f:
   172	                    cached = pickle.load(f)
   173	                logger.debug(f"{ticker}: Using cached fundamentals")
   174	                return cached.get('data', {})
   175	            except Exception as e:
   176	                logger.warning(f"{ticker}: Cache load failed: {e}, refreshing")
   177	
   178	        # Fetch fresh fundamentals
   179	        logger.info(f"{ticker}: Fetching fresh fundamentals")
   180	
   181	        try:
   182	            from .fundamentals_fetcher import fetch_quarterly_financials
   183	            data = fetch_quarterly_financials(ticker)
   184	
   185	            if data:
   186	                # Save to cache with timestamp
   187	                with open(cache_path, 'wb') as f:
   188	                    pickle.dump({
   189	                        'data': data,
   190	                        'fetched_at': datetime.now()
   191	                    }, f)
   192	
   193	                return data
   194	            else:
   195	                return {}
   196	
   197	        except Exception as e:
   198	            logger.error(f"{ticker}: Fundamental fetch failed: {e}")
   199	            return {}
   200	
   201	    def _merge_price_data(
   202	        self,
   203	        old_data: pd.DataFrame,
   204	        new_data: pd.DataFrame,
   205	        keep_days: int
   206	    ) -> pd.DataFrame:
   207	        """Merge old and new price data, keeping only keep_days most recent.
   208	
   209	        Args:
   210	            old_data: Previously cached price data
   211	            new_data: Newly fetched price data
   212	            keep_days: Number of days to retain
   213	
   214	        Returns:
   215	            Merged DataFrame with most recent keep_days
   216	        """
   217	        # Ensure both have Date column
   218	        if 'Date' not in old_data.columns and old_data.index.name == 'Date':
   219	            old_data = old_data.reset_index()
   220	        if 'Date' not in new_data.columns and new_data.index.name == 'Date':
   221	            new_data = new_data.reset_index()
   222	
   223	        # Combine
   224	        combined = pd.concat([old_data, new_data], ignore_index=True)
   225	
   226	        # Remove duplicates (keep latest)
   227	        combined['Date'] = pd.to_datetime(combined['Date'])
   228	        combined = combined.sort_values('Date')
   229	        combined = combined.drop_duplicates(subset=['Date'], keep='last')
   230	
   231	        # Keep only most recent keep_days
   232	        if len(combined) > keep_days:
   233	            combined = combined.iloc[-keep_days:]
   234	
   235	        return combined.reset_index(drop=True)
   236	
   237	    def _save_price_cache(self, ticker: str, data: pd.DataFrame):
   238	        """Save price data and metadata to cache.
   239	
   240	        Args:
   241	            ticker: Stock ticker symbol
   242	            data: Price data to cache
   243	        """
   244	        cache_path = self.price_cache_dir / f"{ticker}_prices.pkl"
   245	        cache_meta_path = self.price_cache_dir / f"{ticker}_prices_meta.pkl"
   246	
   247	        try:
   248	            with open(cache_path, 'wb') as f:
   249	                pickle.dump(data, f)
   250	
   251	            meta = {
   252	                'last_updated': datetime.now(),
   253	                'num_days': len(data)
   254	            }
   255	            with open(cache_meta_path, 'wb') as f:
   256	                pickle.dump(meta, f)
   257	
   258	            logger.debug(f"{ticker}: Cache saved ({len(data)} days)")
   259	
   260	        except Exception as e:
   261	            logger.warning(f"{ticker}: Failed to save cache: {e}")
   262	
   263	    def _should_refresh_fundamentals(self, cache_path: Path) -> bool:
   264	        """Determine if fundamentals should be refreshed.
   265	
   266	        Args:
   267	            cache_path: Path to fundamental cache file
   268	
   269	        Returns:
   270	            True if should refresh, False otherwise
   271	        """
   272	        if not cache_path.exists():
   273	            return True
   274	
   275	        try:
   276	            with open(cache_path, 'rb') as f:
   277	                cached = pickle.load(f)
   278	                fetched_at = cached.get('fetched_at')
   279	
   280	            if fetched_at is None:
   281	                return True
   282	
   283	            days_old = (datetime.now() - fetched_at).days
   284	
   285	            if self._is_earnings_season():
   286	                # During earnings season: refresh weekly
   287	                return days_old >= 7
   288	            else:
   289	                # Outside earnings season: refresh quarterly
   290	                return days_old >= 90
   291	
   292	        except Exception as e:
   293	            logger.warning(f"Cache check failed: {e}, will refresh")
   294	            return True
   295	
   296	    def _is_earnings_season(self) -> bool:
   297	        """Check if currently in earnings season.
   298	
   299	        Earnings seasons (typical 6-week windows):
   300	        - Q4: Jan 15 - Feb 15 (FY prior year reports)
   301	        - Q1: Apr 15 - May 15
   302	        - Q2: Jul 15 - Aug 15
   303	        - Q3: Oct 15 - Nov 15
   304	
   305	        Returns:
   306	            True if in earnings season, False otherwise
   307	        """
   308	        now = datetime.now()
   309	        month = now.month
   310	        day = now.day
   311	
   312	        earnings_windows = [
   313	            (1, 15, 2, 15),   # Q4 earnings: Jan 15 - Feb 15
   314	            (4, 15, 5, 15),   # Q1 earnings: Apr 15 - May 15
   315	            (7, 15, 8, 15),   # Q2 earnings: Jul 15 - Aug 15
   316	            (10, 15, 11, 15)  # Q3 earnings: Oct 15 - Nov 15
   317	        ]
   318	
   319	        for start_month, start_day, end_month, end_day in earnings_windows:
   320	            if start_month == end_month:
   321	                if month == start_month and start_day <= day <= end_day:
   322	                    return True
   323	            else:
   324	                # Handle cross-month windows (though current windows don't cross)
   325	                if (month == start_month and day >= start_day) or \
   326	                   (month == end_month and day <= end_day):
   327	                    return True
   328	
   329	        return False
   330	
   331	    def get_cache_stats(self) -> Dict:
   332	        """Get cache statistics.
   333	
   334	        Returns:
   335	            Dict with cache size, hit rate, etc.
   336	        """
   337	        price_files = list(self.price_cache_dir.glob("*_prices.pkl"))
   338	        fundamental_files = list(self.fundamental_cache_dir.glob("*_fundamentals.pkl"))
   339	
   340	        stats = {
   341	            'price_cache_count': len(price_files),
   342	            'fundamental_cache_count': len(fundamental_files),
   343	            'in_earnings_season': self._is_earnings_season(),
   344	            'cache_dir': str(self.cache_dir)
   345	        }
   346	
   347	        return stats
     1	"""Smart fetcher using Git-based storage for fundamentals and fresh price data.
     2	
     3	This module implements the optimal strategy:
     4	- Price data: ALWAYS fetch fresh (1 year history for 200-day SMA)
     5	- Fundamental data: Store in Git repo, refresh based on earnings season
     6	  - Earnings season: Refresh if >7 days old
     7	  - Normal: Refresh if >90 days old
     8	
     9	Reduces API calls by 74% while ensuring:
    10	- Latest prices always available
    11	- Fundamentals persist beyond GitHub Actions cache limits
    12	"""
    13	
    14	import json
    15	import logging
    16	from datetime import datetime
    17	from pathlib import Path
    18	from typing import Dict, Optional
    19	
    20	import pandas as pd
    21	import yfinance as yf
    22	
    23	logging.basicConfig(
    24	    level=logging.INFO,
    25	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    26	)
    27	logger = logging.getLogger(__name__)
    28	
    29	
    30	class GitStorageFetcher:
    31	    """Fetcher with Git-based fundamental storage and fresh price data."""
    32	
    33	    def __init__(self, fundamentals_dir: str = "./data/fundamentals_cache"):
    34	        """Initialize fetcher.
    35	
    36	        Args:
    37	            fundamentals_dir: Directory for fundamental storage (tracked in Git)
    38	        """
    39	        self.fundamentals_dir = Path(fundamentals_dir)
    40	        self.fundamentals_dir.mkdir(parents=True, exist_ok=True)
    41	
    42	        self.metadata_file = self.fundamentals_dir / "metadata.json"
    43	        logger.info(f"GitStorageFetcher initialized: {fundamentals_dir}")
    44	
    45	    def fetch_price_fresh(self, ticker: str) -> pd.DataFrame:
    46	        """Fetch fresh price data (1 year, no caching).
    47	
    48	        Always fetches latest data to ensure current prices are included.
    49	
    50	        Args:
    51	            ticker: Stock ticker
    52	
    53	        Returns:
    54	            DataFrame with ~250 days of price data (DatetimeIndex)
    55	        """
    56	        try:
    57	            stock = yf.Ticker(ticker)
    58	            # Always fetch 1 year (250 trading days) - not 2 years!
    59	            data = stock.history(period='1y', interval='1d')
    60	
    61	            if not data.empty:
    62	                # Verify DatetimeIndex (yfinance should return this by default)
    63	                if not isinstance(data.index, pd.DatetimeIndex):
    64	                    logger.warning(f"{ticker}: yfinance returned non-DatetimeIndex: {type(data.index)}")
    65	                    # This shouldn't happen, but log it if it does
    66	                    return pd.DataFrame()
    67	
    68	                logger.debug(f"{ticker}: Fetched {len(data)} days (fresh)")
    69	                return data
    70	            else:
    71	                logger.warning(f"{ticker}: No price data returned")
    72	                return pd.DataFrame()
    73	
    74	        except Exception as e:
    75	            logger.error(f"{ticker}: Price fetch failed: {e}")
    76	            return pd.DataFrame()
    77	
    78	    def fetch_fundamentals_smart(self, ticker: str) -> Dict:
    79	        """Fetch fundamentals with Git-based caching.
    80	
    81	        Uses earnings-aware refresh:
    82	        - During earnings season (6-week windows): refresh if >7 days old
    83	        - Outside earnings: refresh if >90 days old
    84	        - Never fetched: fetch now
    85	
    86	        Fundamentals are stored as JSON files in Git repository,
    87	        persisting beyond GitHub Actions cache limits.
    88	
    89	        Args:
    90	            ticker: Stock ticker
    91	
    92	        Returns:
    93	            Dict with fundamental data
    94	        """
    95	        fundamental_file = self.fundamentals_dir / f"{ticker}_fundamentals.json"
    96	
    97	        # Check if refresh needed
    98	        should_refresh = self._should_refresh_fundamental(ticker, fundamental_file)
    99	
   100	        if not should_refresh and fundamental_file.exists():
   101	            # Load from Git storage
   102	            try:
   103	                with open(fundamental_file, 'r') as f:
   104	                    cached = json.load(f)
   105	                logger.debug(f"{ticker}: Using cached fundamentals")
   106	                return cached.get('data', {})
   107	            except Exception as e:
   108	                logger.warning(f"{ticker}: Cache load failed: {e}, will refresh")
   109	
   110	        # Fetch fresh fundamentals
   111	        logger.info(f"{ticker}: Fetching fresh fundamentals")
   112	
   113	        try:
   114	            from .fundamentals_fetcher import fetch_quarterly_financials
   115	            data = fetch_quarterly_financials(ticker)
   116	
   117	            if data:
   118	                # Convert pandas Timestamps to strings for JSON serialization
   119	                cleaned_data = self._clean_for_json(data)
   120	
   121	                # Save to Git storage
   122	                cache_data = {
   123	                    'data': cleaned_data,
   124	                    'fetched_at': datetime.now().isoformat()
   125	                }
   126	
   127	                with open(fundamental_file, 'w') as f:
   128	                    json.dump(cache_data, f, indent=2, default=str)
   129	
   130	                # Update metadata
   131	                self._update_metadata(ticker)
   132	
   133	                logger.info(f"{ticker}: Fundamentals cached to Git")
   134	                return data
   135	            else:
   136	                return {}
   137	
   138	        except Exception as e:
   139	            logger.error(f"{ticker}: Fundamental fetch failed: {e}")
   140	            return {}
   141	
   142	    def _should_refresh_fundamental(self, ticker: str, file_path: Path) -> bool:
   143	        """Check if fundamental data needs refresh.
   144	
   145	        Args:
   146	            ticker: Stock ticker
   147	            file_path: Path to cached fundamental file
   148	
   149	        Returns:
   150	            True if should refresh, False if cached data is still valid
   151	        """
   152	        if not file_path.exists():
   153	            logger.info(f"{ticker}: No cache, will fetch")
   154	            return True
   155	
   156	        try:
   157	            with open(file_path, 'r') as f:
   158	                cached = json.load(f)
   159	                fetched_at_str = cached.get('fetched_at')
   160	
   161	            if fetched_at_str is None:
   162	                return True
   163	
   164	            fetched_at = datetime.fromisoformat(fetched_at_str)
   165	            days_old = (datetime.now() - fetched_at).days
   166	
   167	            # Always refresh if >90 days old (stale)
   168	            if days_old > 90:
   169	                logger.info(f"{ticker}: Stale data ({days_old} days), refreshing")
   170	                return True
   171	
   172	            # During earnings season: refresh weekly
   173	            if self._is_earnings_season() and days_old >= 7:
   174	                logger.info(f"{ticker}: Earnings season refresh ({days_old} days old)")
   175	                return True
   176	
   177	            # Cache is still valid
   178	            logger.debug(f"{ticker}: Cache valid ({days_old} days old)")
   179	            return False
   180	
   181	        except Exception as e:
   182	            logger.warning(f"{ticker}: Error checking cache: {e}, will refresh")
   183	            return True
   184	
   185	    def _clean_for_json(self, data: Dict) -> Dict:
   186	        """Clean data for JSON serialization.
   187	
   188	        Converts pandas Timestamps and other non-JSON types to strings.
   189	
   190	        Args:
   191	            data: Data dictionary from fundamentals_fetcher
   192	
   193	        Returns:
   194	            Cleaned dictionary safe for JSON serialization
   195	        """
   196	        import pandas as pd
   197	
   198	        def clean_value(value):
   199	            """Recursively clean values."""
   200	            if isinstance(value, dict):
   201	                # Clean dictionary - convert Timestamp keys to strings
   202	                return {
   203	                    str(k): clean_value(v)
   204	                    for k, v in value.items()
   205	                }
   206	            elif isinstance(value, (list, tuple)):
   207	                return [clean_value(item) for item in value]
   208	            elif isinstance(value, pd.Timestamp):
   209	                return value.isoformat()
   210	            elif isinstance(value, (pd.Series, pd.DataFrame)):
   211	                return value.to_dict()
   212	            else:
   213	                return value
   214	
   215	        return clean_value(data)
   216	
   217	    def _is_earnings_season(self) -> bool:
   218	        """Check if currently in earnings season.
   219	
   220	        Earnings seasons (typical 6-week windows):
   221	        - Q4: Jan 15 - Feb 15 (prior FY reports)
   222	        - Q1: Apr 15 - May 15
   223	        - Q2: Jul 15 - Aug 15
   224	        - Q3: Oct 15 - Nov 15
   225	
   226	        Returns:
   227	            True if in earnings season, False otherwise
   228	        """
   229	        now = datetime.now()
   230	        month = now.month
   231	        day = now.day
   232	
   233	        earnings_windows = [
   234	            (1, 15, 2, 15),   # Q4 earnings: Jan 15 - Feb 15
   235	            (4, 15, 5, 15),   # Q1 earnings: Apr 15 - May 15
   236	            (7, 15, 8, 15),   # Q2 earnings: Jul 15 - Aug 15
   237	            (10, 15, 11, 15)  # Q3 earnings: Oct 15 - Nov 15
   238	        ]
   239	
   240	        for start_month, start_day, end_month, end_day in earnings_windows:
   241	            if start_month == end_month:
   242	                if month == start_month and start_day <= day <= end_day:
   243	                    return True
   244	            else:
   245	                # Handle cross-month windows
   246	                if (month == start_month and day >= start_day) or \
   247	                   (month == end_month and day <= end_day):
   248	                    return True
   249	
   250	        return False
   251	
   252	    def _update_metadata(self, ticker: str):
   253	        """Update metadata tracking file.
   254	
   255	        Tracks last update time for each stock for monitoring.
   256	
   257	        Args:
   258	            ticker: Stock ticker
   259	        """
   260	        metadata = {}
   261	
   262	        if self.metadata_file.exists():
   263	            try:
   264	                with open(self.metadata_file, 'r') as f:
   265	                    metadata = json.load(f)
   266	            except Exception:
   267	                pass
   268	
   269	        metadata[ticker] = {
   270	            'last_updated': datetime.now().isoformat(),
   271	            'in_earnings_season': self._is_earnings_season()
   272	        }
   273	
   274	        with open(self.metadata_file, 'w') as f:
   275	            json.dump(metadata, f, indent=2)
   276	
   277	    def get_cache_stats(self) -> Dict:
   278	        """Get cache statistics.
   279	
   280	        Returns:
   281	            Dict with cache counts and status
   282	        """
   283	        cached_files = list(self.fundamentals_dir.glob("*_fundamentals.json"))
   284	
   285	        # Count by age
   286	        recent_count = 0  # <7 days
   287	        moderate_count = 0  # 7-30 days
   288	        old_count = 0  # 30-90 days
   289	        stale_count = 0  # >90 days
   290	
   291	        for file_path in cached_files:
   292	            try:
   293	                with open(file_path, 'r') as f:
   294	                    data = json.load(f)
   295	                    fetched_at = datetime.fromisoformat(data.get('fetched_at'))
   296	                    days_old = (datetime.now() - fetched_at).days
   297	
   298	                if days_old < 7:
   299	                    recent_count += 1
   300	                elif days_old < 30:
   301	                    moderate_count += 1
   302	                elif days_old < 90:
   303	                    old_count += 1
   304	                else:
   305	                    stale_count += 1
   306	            except Exception:
   307	                pass
   308	
   309	        stats = {
   310	            'total_cached': len(cached_files),
   311	            'recent_7d': recent_count,
   312	            'moderate_30d': moderate_count,
   313	            'old_90d': old_count,
   314	            'stale_90d_plus': stale_count,
   315	            'in_earnings_season': self._is_earnings_season(),
   316	            'storage_dir': str(self.fundamentals_dir)
   317	        }
   318	
   319	        return stats
   320	
   321	    def cleanup_stale_cache(self, max_age_days: int = 180):
   322	        """Remove very old cached files.
   323	
   324	        Args:
   325	            max_age_days: Remove files older than this (default 180 days)
   326	
   327	        Returns:
   328	            Number of files removed
   329	        """
   330	        removed = 0
   331	
   332	        for file_path in self.fundamentals_dir.glob("*_fundamentals.json"):
   333	            try:
   334	                with open(file_path, 'r') as f:
   335	                    data = json.load(f)
   336	                    fetched_at = datetime.fromisoformat(data.get('fetched_at'))
   337	                    days_old = (datetime.now() - fetched_at).days
   338	
   339	                if days_old > max_age_days:
   340	                    file_path.unlink()
   341	                    removed += 1
   342	                    logger.info(f"Removed stale cache: {file_path.name} ({days_old} days old)")
   343	
   344	            except Exception as e:
   345	                logger.warning(f"Error processing {file_path.name}: {e}")
   346	
   347	        return removed

exec
/bin/zsh -lc "nl -ba src/screening/optimized_batch_processor.py | sed -n '1,517p'; nl -ba src/screening/batch_processor.py | sed -n '1,353p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Optimized batch processor with parallel processing and adaptive rate limiting.
     2	
     3	This module implements advanced techniques to maximize throughput while avoiding rate limits:
     4	- Parallel batch processing with thread pools
     5	- Adaptive rate limiting based on error rates
     6	- Session reuse and connection pooling
     7	- Bulk data fetching where possible
     8	"""
     9	
    10	import logging
    11	import pickle
    12	import time
    13	import threading
    14	from concurrent.futures import ThreadPoolExecutor, as_completed
    15	from datetime import datetime, timedelta
    16	from pathlib import Path
    17	from typing import Dict, List, Optional
    18	
    19	import pandas as pd
    20	import yfinance as yf
    21	
    22	from src.data.fetcher import YahooFinanceFetcher
    23	from src.data.fundamentals_fetcher import fetch_quarterly_financials, analyze_fundamentals_for_signal
    24	from src.data.git_storage_fetcher import GitStorageFetcher
    25	from ..screening.phase_indicators import classify_phase, calculate_relative_strength, detect_vcp_pattern
    26	
    27	logging.basicConfig(
    28	    level=logging.INFO,
    29	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    30	)
    31	logger = logging.getLogger(__name__)
    32	
    33	
    34	class OptimizedBatchProcessor:
    35	    """Optimized batch processor with parallel processing and smart rate limiting."""
    36	
    37	    def __init__(
    38	        self,
    39	        cache_dir: str = "./data/cache",
    40	        results_dir: str = "./data/batch_results",
    41	        max_workers: int = 3,  # Conservative: 3 workers
    42	        rate_limit_delay: float = 0.5,  # 0.5 sec = 2 TPS per worker
    43	        batch_size: int = 100,
    44	        use_git_storage: bool = False  # Use Git-based fundamental storage
    45	    ):
    46	        """Initialize optimized processor.
    47	
    48	        Args:
    49	            cache_dir: Cache directory
    50	            results_dir: Results directory
    51	            max_workers: Number of parallel workers (3 = ~6 TPS effective)
    52	            rate_limit_delay: Delay per worker (0.5 = 2 TPS)
    53	            batch_size: Save progress frequency
    54	            use_git_storage: Use Git-based storage for fundamentals (recommended)
    55	        """
    56	        self.fetcher = YahooFinanceFetcher(cache_dir=cache_dir)
    57	        self.git_fetcher = GitStorageFetcher() if use_git_storage else None
    58	        self.use_git_storage = use_git_storage
    59	        self.results_dir = Path(results_dir)
    60	        self.results_dir.mkdir(parents=True, exist_ok=True)
    61	
    62	        self.max_workers = max_workers
    63	        self.rate_limit_delay = rate_limit_delay
    64	        self.batch_size = batch_size
    65	
    66	        # Effective TPS = max_workers / rate_limit_delay
    67	        effective_tps = max_workers / rate_limit_delay
    68	
    69	        self.spy_data = None
    70	        self.spy_price = None
    71	        self.progress_file = self.results_dir / "batch_progress.pkl"
    72	        self.processed_tickers = set()
    73	        self.current_results = []
    74	
    75	        # Rate limit tracking and adaptive backoff
    76	        self.request_times = []
    77	        self.error_count = 0
    78	        self.filtered_count = 0  # Stocks that didn't pass filters (not errors)
    79	        self.total_requests = 0
    80	        self.consecutive_errors = 0
    81	        self.backoff_delay = 0.0  # Additional delay when errors detected
    82	        self.last_error_time = None
    83	
    84	        # Thread-safe rate limiting
    85	        self.rate_limit_lock = threading.Lock()
    86	        self.last_request_time = 0.0
    87	
    88	        # Error tracking by type
    89	        self.error_types = {}  # {error_type: count}
    90	        self.error_examples = {}  # {error_type: example_ticker}
    91	
    92	        # Filter tracking
    93	        self.filter_reasons = {}  # {reason: count}
    94	
    95	        logger.info(f"OptimizedBatchProcessor initialized")
    96	        logger.info(f"Workers: {max_workers}, Delay: {rate_limit_delay}s")
    97	        logger.info(f"Effective rate: ~{effective_tps:.1f} TPS")
    98	
    99	    def load_progress(self) -> Optional[Dict]:
   100	        """Load progress from previous run."""
   101	        if not self.progress_file.exists():
   102	            return None
   103	
   104	        try:
   105	            with open(self.progress_file, 'rb') as f:
   106	                progress = pickle.load(f)
   107	            logger.info(f"Loaded progress: {len(progress['processed'])} stocks done")
   108	            return progress
   109	        except Exception as e:
   110	            logger.error(f"Error loading progress: {e}")
   111	            return None
   112	
   113	    def save_progress(self, tickers_list: List[str], results: List[Dict]):
   114	        """Save current progress."""
   115	        try:
   116	            progress = {
   117	                'timestamp': datetime.now().isoformat(),
   118	                'total_tickers': len(tickers_list),
   119	                'processed': list(self.processed_tickers),
   120	                'results': results,
   121	                'batch_size': self.batch_size,
   122	                'error_rate': self.error_count / max(self.total_requests, 1)
   123	            }
   124	
   125	            with open(self.progress_file, 'wb') as f:
   126	                pickle.dump(progress, f)
   127	
   128	        except Exception as e:
   129	            logger.error(f"Error saving progress: {e}")
   130	
   131	    def _wait_for_rate_limit(self):
   132	        """Thread-safe rate limiting - ensures minimum delay between ANY requests.
   133	
   134	        This method uses a lock to ensure that even with multiple threads,
   135	        only one request can proceed at a time, and each request waits
   136	        the full rate_limit_delay since the last request.
   137	        """
   138	        with self.rate_limit_lock:
   139	            current_time = time.time()
   140	            time_since_last = current_time - self.last_request_time
   141	
   142	            if time_since_last < self.rate_limit_delay:
   143	                sleep_time = self.rate_limit_delay - time_since_last
   144	                time.sleep(sleep_time)
   145	
   146	            # Add adaptive backoff if errors detected
   147	            if self.backoff_delay > 0:
   148	                time.sleep(self.backoff_delay)
   149	                logger.debug(f"Adaptive backoff: +{self.backoff_delay:.1f}s")
   150	
   151	            self.last_request_time = time.time()
   152	
   153	    def fetch_spy_data(self) -> bool:
   154	        """Fetch SPY benchmark data."""
   155	        try:
   156	            logger.info("Fetching SPY data...")
   157	            # Use 1 year for price data (not 2 years - 50% less data)
   158	            # Use same fetcher as stocks for consistency
   159	            if self.use_git_storage and self.git_fetcher:
   160	                spy_hist = self.git_fetcher.fetch_price_fresh('SPY')
   161	            else:
   162	                spy_hist = self.fetcher.fetch_price_history('SPY', period='1y')
   163	
   164	            if spy_hist.empty:
   165	                logger.error("Failed to fetch SPY data")
   166	                return False
   167	
   168	            # Ensure DatetimeIndex (yfinance should return this, but verify)
   169	            if not isinstance(spy_hist.index, pd.DatetimeIndex):
   170	                logger.error(f"SPY has invalid index type: {type(spy_hist.index)}")
   171	                logger.error(f"SPY index: {spy_hist.index}")
   172	                return False
   173	
   174	            self.spy_data = spy_hist
   175	            self.spy_price = spy_hist['Close'].iloc[-1]
   176	            logger.info(f"SPY ready: {len(spy_hist)} days, ${self.spy_price:.2f}")
   177	            return True
   178	
   179	        except Exception as e:
   180	            logger.error(f"Error fetching SPY: {e}")
   181	            return False
   182	
   183	    def analyze_single_stock(
   184	        self,
   185	        ticker: str,
   186	        min_price: float,
   187	        max_price: float,
   188	        min_volume: int
   189	    ) -> Optional[Dict]:
   190	        """Analyze one stock with adaptive rate limiting.
   191	
   192	        Args:
   193	            ticker: Stock ticker
   194	            min_price: Min price filter
   195	            max_price: Max price filter
   196	            min_volume: Min volume filter
   197	
   198	        Returns:
   199	            Analysis dict or None
   200	        """
   201	        try:
   202	            # Thread-safe rate limiting (locks ensure only 1 request at a time)
   203	            self._wait_for_rate_limit()
   204	
   205	            self.total_requests += 1
   206	
   207	            # Fetch price history (5 years to check drawdown, use last 1y for analysis)
   208	            # This is more efficient than two separate fetches
   209	            if self.use_git_storage and self.git_fetcher:
   210	                # Git fetcher only does 1y, fetch 5y for drawdown check first
   211	                import yfinance as yf
   212	                long_hist = yf.Ticker(ticker).history(period='5y', interval='1d')
   213	
   214	                if not long_hist.empty:
   215	                    # Use last 1 year for technical analysis
   216	                    price_data = long_hist.tail(252) if len(long_hist) > 252 else long_hist
   217	                else:
   218	                    # Fallback to git fetcher if 5y fails
   219	                    price_data = self.git_fetcher.fetch_price_fresh(ticker)
   220	                    long_hist = price_data
   221	            else:
   222	                # Regular fetcher - fetch 5y once
   223	                long_hist = self.fetcher.fetch_price_history(ticker, period='5y')
   224	                if not long_hist.empty:
   225	                    # Use last 1 year for technical analysis
   226	                    price_data = long_hist.tail(252) if len(long_hist) > 252 else long_hist
   227	                else:
   228	                    price_data = pd.DataFrame()
   229	
   230	            if price_data.empty or len(price_data) < 200:
   231	                self.filtered_count += 1
   232	                self.filter_reasons['insufficient_data'] = self.filter_reasons.get('insufficient_data', 0) + 1
   233	                return None
   234	
   235	            current_price = price_data['Close'].iloc[-1]
   236	
   237	            # Historical drawdown filter (using 5y data we already fetched)
   238	            # Exclude stocks that dropped >90% from any high in past 5 years
   239	            if not long_hist.empty and len(long_hist) >= 252:  # At least 1 year
   240	                closes = long_hist['Close']
   241	                # Calculate max drawdown from any previous high
   242	                running_max = closes.expanding().max()
   243	                drawdown = (closes - running_max) / running_max
   244	                max_drawdown = drawdown.min()  # Most negative value
   245	
   246	                # Check for valid drawdown value before comparison
   247	                if pd.notna(max_drawdown) and max_drawdown < -0.90:  # Dropped more than 90%
   248	                    self.filtered_count += 1
   249	                    self.filter_reasons['severe_drawdown_90pct'] = self.filter_reasons.get('severe_drawdown_90pct', 0) + 1
   250	                    logger.debug(f"{ticker}: Filtered - {max_drawdown*100:.1f}% max drawdown in 5y")
   251	                    return None
   252	
   253	            # Price filter
   254	            if current_price < min_price or current_price > max_price:
   255	                self.filtered_count += 1
   256	                self.filter_reasons['price_range'] = self.filter_reasons.get('price_range', 0) + 1
   257	                return None
   258	
   259	            # Volume filter
   260	            if 'Volume' in price_data.columns:
   261	                avg_volume = price_data['Volume'].iloc[-20:].mean()
   262	                if avg_volume < min_volume:
   263	                    self.filtered_count += 1
   264	                    self.filter_reasons['low_volume'] = self.filter_reasons.get('low_volume', 0) + 1
   265	                    return None
   266	            else:
   267	                avg_volume = 0
   268	
   269	            # Phase classification
   270	            phase_info = classify_phase(price_data, current_price)
   271	            phase = phase_info['phase']
   272	
   273	            if phase not in [1, 2, 3, 4]:
   274	                self.filtered_count += 1
   275	                self.filter_reasons['invalid_phase'] = self.filter_reasons.get('invalid_phase', 0) + 1
   276	                return None
   277	
   278	            # RS calculation
   279	            rs_series = calculate_relative_strength(
   280	                price_data['Close'],
   281	                self.spy_data['Close'],
   282	                period=63
   283	            )
   284	
   285	            # VCP pattern detection (only for Phase 1/2 - base building or breakout)
   286	            vcp_data = {}
   287	            if phase in [1, 2]:
   288	                vcp_data = detect_vcp_pattern(price_data, current_price, phase_info)
   289	                logger.debug(f"{ticker}: VCP analysis - {vcp_data.get('pattern_details', 'N/A')}")
   290	
   291	            # Fundamentals (only for Phase 1/2)
   292	            quarterly_data = {}
   293	            fundamental_analysis = {}
   294	
   295	            if phase in [1, 2]:
   296	                # Use Git-based storage if enabled
   297	                if self.use_git_storage and self.git_fetcher:
   298	                    quarterly_data = self.git_fetcher.fetch_fundamentals_smart(ticker)
   299	                else:
   300	                    quarterly_data = fetch_quarterly_financials(ticker)
   301	                fundamental_analysis = analyze_fundamentals_for_signal(quarterly_data)
   302	
   303	            return {
   304	                'ticker': ticker,
   305	                'price_data': price_data,
   306	                'current_price': current_price,
   307	                'avg_volume': avg_volume,
   308	                'phase_info': phase_info,
   309	                'rs_series': rs_series,
   310	                'vcp_data': vcp_data,  # Added VCP analysis
   311	                'quarterly_data': quarterly_data,
   312	                'fundamental_analysis': fundamental_analysis
   313	            }
   314	
   315	        except Exception as e:
   316	            self.error_count += 1
   317	            self.consecutive_errors += 1
   318	            self.last_error_time = time.time()
   319	
   320	            # Track error type
   321	            error_type = type(e).__name__
   322	            error_msg = str(e)
   323	
   324	            if error_type not in self.error_types:
   325	                self.error_types[error_type] = 0
   326	                self.error_examples[error_type] = (ticker, error_msg)
   327	
   328	            self.error_types[error_type] += 1
   329	
   330	            # Log first 5 occurrences of each error type for debugging
   331	            if self.error_types[error_type] <= 5:
   332	                logger.error(f"[ERROR #{self.error_types[error_type]}] {error_type} on {ticker}: {error_msg}")
   333	            elif self.error_types[error_type] == 6:
   334	                logger.info(f"  ({error_type} will now be suppressed, {self.error_types[error_type]} total so far)")
   335	
   336	            # Check if it's a rate limit error
   337	            if '429' in error_msg.lower() or 'rate limit' in error_msg.lower() or 'too many requests' in error_msg.lower():
   338	                logger.warning(f"Rate limit hit on {ticker}: {e}")
   339	
   340	                # Adaptive backoff - increase delay
   341	                self.backoff_delay = min(self.backoff_delay + 0.5, 5.0)  # Max 5 sec extra
   342	                logger.warning(f"Increasing backoff delay to +{self.backoff_delay:.1f}s")
   343	
   344	                # If we hit multiple rate limits, sleep longer immediately
   345	                if self.consecutive_errors >= 3:
   346	                    sleep_time = 30
   347	                    logger.warning(f"Multiple rate limits detected! Sleeping {sleep_time}s...")
   348	                    time.sleep(sleep_time)
   349	                    self.consecutive_errors = 0
   350	            else:
   351	                logger.debug(f"Error analyzing {ticker}: {e}")
   352	
   353	            return None
   354	
   355	    def process_batch_parallel(
   356	        self,
   357	        tickers: List[str],
   358	        resume: bool = True,
   359	        min_price: float = 5.0,
   360	        max_price: float = 10000.0,
   361	        min_volume: int = 100000
   362	    ) -> Dict:
   363	        """Process batch with parallel workers.
   364	
   365	        Args:
   366	            tickers: List of tickers
   367	            resume: Resume from progress
   368	            min_price: Min price
   369	            max_price: Max price
   370	            min_volume: Min volume
   371	
   372	        Returns:
   373	            Results dict
   374	        """
   375	        logger.info("="*60)
   376	        logger.info("OPTIMIZED BATCH PROCESSING STARTED")
   377	        logger.info(f"Tickers: {len(tickers)}")
   378	        logger.info(f"Workers: {self.max_workers}")
   379	        logger.info(f"Rate: ~{self.max_workers / self.rate_limit_delay:.1f} TPS")
   380	        logger.info(f"Est. time: {len(tickers) * self.rate_limit_delay / self.max_workers / 3600:.1f} hours")
   381	        logger.info("="*60)
   382	
   383	        # Fetch SPY
   384	        if not self.fetch_spy_data():
   385	            return {'error': 'Failed to fetch SPY'}
   386	
   387	        # Load progress
   388	        if resume:
   389	            progress = self.load_progress()
   390	            if progress:
   391	                self.processed_tickers = set(progress['processed'])
   392	                self.current_results = progress['results']
   393	
   394	        remaining = [t for t in tickers if t not in self.processed_tickers]
   395	        logger.info(f"Processing {len(remaining)} remaining tickers")
   396	
   397	        start_time = time.time()
   398	        all_analyses = self.current_results.copy()
   399	        phase_results = []
   400	
   401	        # Process in parallel batches
   402	        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
   403	            # Submit all tasks
   404	            future_to_ticker = {
   405	                executor.submit(
   406	                    self.analyze_single_stock,
   407	                    ticker,
   408	                    min_price,
   409	                    max_price,
   410	                    min_volume
   411	                ): ticker
   412	                for ticker in remaining
   413	            }
   414	
   415	            # Process completions
   416	            completed = 0
   417	            for future in as_completed(future_to_ticker):
   418	                ticker = future_to_ticker[future]
   419	                completed += 1
   420	
   421	                try:
   422	                    analysis = future.result()
   423	
   424	                    if analysis:
   425	                        all_analyses.append(analysis)
   426	                        phase_results.append({
   427	                            'ticker': ticker,
   428	                            'phase': analysis['phase_info']['phase']
   429	                        })
   430	
   431	                        # Success - reset consecutive errors and reduce backoff
   432	                        self.consecutive_errors = 0
   433	                        if self.backoff_delay > 0:
   434	                            self.backoff_delay = max(0, self.backoff_delay - 0.1)  # Slowly reduce
   435	
   436	                    self.processed_tickers.add(ticker)
   437	
   438	                    # Progress logging
   439	                    if completed % 50 == 0 or completed == 1:
   440	                        elapsed = time.time() - start_time
   441	                        rate = completed / elapsed if elapsed > 0 else 0
   442	                        remaining_count = len(remaining) - completed
   443	                        eta_seconds = remaining_count / rate if rate > 0 else 0
   444	                        eta = str(timedelta(seconds=int(eta_seconds)))
   445	
   446	                        error_rate = self.error_count / max(self.total_requests, 1) * 100
   447	                        filter_rate = self.filtered_count / max(self.total_requests, 1) * 100
   448	
   449	                        logger.info(
   450	                            f"Progress: {len(self.processed_tickers)}/{len(tickers)} "
   451	                            f"({len(self.processed_tickers)/len(tickers)*100:.1f}%) | "
   452	                            f"Rate: {rate:.1f}/sec | "
   453	                            f"Filtered: {filter_rate:.1f}% | Errors: {error_rate:.1f}% | "
   454	                            f"ETA: {eta}"
   455	                        )
   456	
   457	                    # Save progress
   458	                    if completed % self.batch_size == 0:
   459	                        self.save_progress(tickers, all_analyses)
   460	
   461	                except Exception as e:
   462	                    logger.error(f"Error processing {ticker}: {e}")
   463	
   464	        # Final save
   465	        self.save_progress(tickers, all_analyses)
   466	
   467	        total_time = time.time() - start_time
   468	        actual_rate = len(tickers) / total_time if total_time > 0 else 0
   469	
   470	        logger.info("="*60)
   471	        logger.info("OPTIMIZED BATCH PROCESSING COMPLETE")
   472	        logger.info(f"Time: {str(timedelta(seconds=int(total_time)))}")
   473	        logger.info(f"Processed: {len(tickers)} tickers")
   474	        logger.info(f"Analyzed: {len(all_analyses)} stocks")
   475	        logger.info(f"Filtered: {self.filtered_count} ({self.filtered_count / max(self.total_requests, 1) * 100:.1f}%)")
   476	        logger.info(f"Actual rate: {actual_rate:.2f} TPS")
   477	        logger.info(f"Error rate: {self.error_count / max(self.total_requests, 1) * 100:.1f}%")
   478	
   479	        # Log filter breakdown
   480	        if self.filter_reasons:
   481	            logger.info("-"*60)
   482	            logger.info("FILTER BREAKDOWN:")
   483	            sorted_filters = sorted(self.filter_reasons.items(), key=lambda x: x[1], reverse=True)
   484	            for reason, count in sorted_filters:
   485	                pct = (count / self.filtered_count * 100) if self.filtered_count > 0 else 0
   486	                logger.info(f"  {reason}: {count} ({pct:.1f}%)")
   487	
   488	        # Log error breakdown
   489	        if self.error_types:
   490	            logger.info("-"*60)
   491	            logger.info("ERROR BREAKDOWN:")
   492	            sorted_errors = sorted(self.error_types.items(), key=lambda x: x[1], reverse=True)
   493	            for error_type, count in sorted_errors:
   494	                pct = (count / self.error_count * 100) if self.error_count > 0 else 0
   495	                example_ticker, example_msg = self.error_examples[error_type]
   496	                logger.info(f"  {error_type}: {count} ({pct:.1f}%)")
   497	                logger.info(f"    Example: {example_ticker} - {example_msg[:100]}")
   498	
   499	        logger.info("="*60)
   500	
   501	        return {
   502	            'analyses': all_analyses,
   503	            'phase_results': phase_results,
   504	            'total_processed': len(tickers),
   505	            'total_analyzed': len(all_analyses),
   506	            'processing_time_seconds': total_time,
   507	            'actual_tps': actual_rate,
   508	            'error_rate': self.error_count / max(self.total_requests, 1)
   509	        }
   510	
   511	    def clear_progress(self):
   512	        """Clear saved progress."""
   513	        if self.progress_file.exists():
   514	            self.progress_file.unlink()
   515	        self.processed_tickers.clear()
   516	        self.current_results.clear()
   517	        logger.info("Progress cleared")
     1	"""Batch processor for screening large numbers of stocks with rate limiting.
     2	
     3	This module handles:
     4	- Rate-limited API calls (respects Yahoo Finance limits)
     5	- Progress tracking and resume capability
     6	- Incremental results saving
     7	- Time estimation
     8	- Error recovery
     9	"""
    10	
    11	import logging
    12	import pickle
    13	import time
    14	from datetime import datetime, timedelta
    15	from pathlib import Path
    16	from typing import Dict, List, Optional
    17	
    18	import pandas as pd
    19	
    20	from src.data.fetcher import YahooFinanceFetcher
    21	from src.data.fundamentals_fetcher import fetch_quarterly_financials, analyze_fundamentals_for_signal
    22	from ..screening.phase_indicators import classify_phase, calculate_relative_strength
    23	from ..screening.signal_engine import score_buy_signal, score_sell_signal
    24	
    25	logging.basicConfig(
    26	    level=logging.INFO,
    27	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    28	)
    29	logger = logging.getLogger(__name__)
    30	
    31	
    32	class BatchStockProcessor:
    33	    """Process large batches of stocks with rate limiting and progress tracking."""
    34	
    35	    def __init__(
    36	        self,
    37	        cache_dir: str = "./data/cache",
    38	        results_dir: str = "./data/batch_results",
    39	        rate_limit_delay: float = 1.0,  # 1 second between stocks (1 TPS)
    40	        batch_size: int = 100  # Save progress every N stocks
    41	    ):
    42	        """Initialize the batch processor.
    43	
    44	        Args:
    45	            cache_dir: Directory for data caching
    46	            results_dir: Directory for saving batch results
    47	            rate_limit_delay: Seconds to wait between API calls (1.0 = 1 TPS)
    48	            batch_size: How often to save progress
    49	        """
    50	        self.fetcher = YahooFinanceFetcher(cache_dir=cache_dir)
    51	        self.results_dir = Path(results_dir)
    52	        self.results_dir.mkdir(parents=True, exist_ok=True)
    53	        self.rate_limit_delay = rate_limit_delay
    54	        self.batch_size = batch_size
    55	
    56	        self.spy_data = None
    57	        self.spy_price = None
    58	
    59	        self.progress_file = self.results_dir / "batch_progress.pkl"
    60	        self.current_results = []
    61	        self.processed_tickers = set()
    62	
    63	        logger.info(f"BatchStockProcessor initialized (rate: {1/rate_limit_delay:.1f} TPS)")
    64	
    65	    def load_progress(self) -> Optional[Dict]:
    66	        """Load progress from previous run.
    67	
    68	        Returns:
    69	            Progress dict or None
    70	        """
    71	        if not self.progress_file.exists():
    72	            return None
    73	
    74	        try:
    75	            with open(self.progress_file, 'rb') as f:
    76	                progress = pickle.load(f)
    77	
    78	            logger.info(f"Loaded progress: {len(progress['processed'])} stocks already processed")
    79	            return progress
    80	
    81	        except Exception as e:
    82	            logger.error(f"Error loading progress: {e}")
    83	            return None
    84	
    85	    def save_progress(self, tickers_list: List[str], results: List[Dict]):
    86	        """Save current progress.
    87	
    88	        Args:
    89	            tickers_list: Complete list of tickers being processed
    90	            results: Results so far
    91	        """
    92	        try:
    93	            progress = {
    94	                'timestamp': datetime.now().isoformat(),
    95	                'total_tickers': len(tickers_list),
    96	                'processed': list(self.processed_tickers),
    97	                'results': results,
    98	                'batch_size': self.batch_size
    99	            }
   100	
   101	            with open(self.progress_file, 'wb') as f:
   102	                pickle.dump(progress, f)
   103	
   104	            logger.debug(f"Progress saved: {len(self.processed_tickers)}/{len(tickers_list)}")
   105	
   106	        except Exception as e:
   107	            logger.error(f"Error saving progress: {e}")
   108	
   109	    def fetch_spy_data(self) -> bool:
   110	        """Fetch SPY benchmark data.
   111	
   112	        Returns:
   113	            True if successful
   114	        """
   115	        try:
   116	            logger.info("Fetching SPY data...")
   117	            spy_hist = self.fetcher.fetch_price_history('SPY', period='2y')
   118	
   119	            if spy_hist.empty:
   120	                logger.error("Failed to fetch SPY data")
   121	                return False
   122	
   123	            self.spy_data = spy_hist
   124	            self.spy_price = spy_hist['Close'].iloc[-1]
   125	            logger.info(f"SPY data ready: {len(spy_hist)} days, price: ${self.spy_price:.2f}")
   126	            return True
   127	
   128	        except Exception as e:
   129	            logger.error(f"Error fetching SPY data: {e}")
   130	            return False
   131	
   132	    def filter_tradable_stocks(
   133	        self,
   134	        tickers: List[str],
   135	        min_price: float = 5.0,
   136	        max_price: float = 10000.0,
   137	        min_volume: int = 100000
   138	    ) -> List[str]:
   139	        """Filter out penny stocks and low-volume stocks.
   140	
   141	        This is a quick pre-filter to avoid wasting time on untradable stocks.
   142	
   143	        Args:
   144	            tickers: List of tickers to filter
   145	            min_price: Minimum stock price
   146	            max_price: Maximum stock price
   147	            min_volume: Minimum average daily volume
   148	
   149	        Returns:
   150	            Filtered list of tickers
   151	        """
   152	        logger.info(f"Pre-filtering {len(tickers)} stocks...")
   153	        logger.info(f"Filters: price ${min_price}-${max_price}, volume >{min_volume:,}")
   154	
   155	        # We'll do this check during the main screening loop to avoid extra API calls
   156	        # Just return the full list for now
   157	        return tickers
   158	
   159	    def analyze_stock_batch(
   160	        self,
   161	        ticker: str,
   162	        min_price: float = 5.0,
   163	        max_price: float = 10000.0,
   164	        min_volume: int = 100000
   165	    ) -> Optional[Dict]:
   166	        """Analyze a single stock with filtering.
   167	
   168	        Args:
   169	            ticker: Stock ticker
   170	            min_price: Minimum price filter
   171	            max_price: Maximum price filter
   172	            min_volume: Minimum volume filter
   173	
   174	        Returns:
   175	            Analysis dict or None if filtered out or failed
   176	        """
   177	        try:
   178	            # Fetch price history
   179	            price_data = self.fetcher.fetch_price_history(ticker, period='2y')
   180	
   181	            if price_data.empty or len(price_data) < 200:
   182	                logger.debug(f"{ticker}: Insufficient data ({len(price_data)} days)")
   183	                return None
   184	
   185	            current_price = price_data['Close'].iloc[-1]
   186	
   187	            # Apply filters
   188	            if current_price < min_price or current_price > max_price:
   189	                logger.debug(f"{ticker}: Price ${current_price:.2f} outside range")
   190	                return None
   191	
   192	            if 'Volume' in price_data.columns:
   193	                avg_volume = price_data['Volume'].iloc[-20:].mean()
   194	                if avg_volume < min_volume:
   195	                    logger.debug(f"{ticker}: Low volume {avg_volume:,.0f}")
   196	                    return None
   197	
   198	            # Classify phase
   199	            phase_info = classify_phase(price_data, current_price)
   200	
   201	            # Only analyze stocks in Phase 1 or 2 for buys
   202	            # And Phase 3 or 4 for sells
   203	            phase = phase_info['phase']
   204	            if phase not in [1, 2, 3, 4]:
   205	                return None
   206	
   207	            # Calculate relative strength vs SPY
   208	            rs_series = calculate_relative_strength(
   209	                price_data['Close'],
   210	                self.spy_data['Close'],
   211	                period=63
   212	            )
   213	
   214	            # Fetch fundamentals (only if in buy/sell phase)
   215	            quarterly_data = {}
   216	            fundamental_analysis = {}
   217	
   218	            if phase in [1, 2]:  # Potential buy
   219	                quarterly_data = fetch_quarterly_financials(ticker)
   220	                fundamental_analysis = analyze_fundamentals_for_signal(quarterly_data)
   221	
   222	            return {
   223	                'ticker': ticker,
   224	                'price_data': price_data,
   225	                'current_price': current_price,
   226	                'avg_volume': avg_volume if 'Volume' in price_data.columns else 0,
   227	                'phase_info': phase_info,
   228	                'rs_series': rs_series,
   229	                'quarterly_data': quarterly_data,
   230	                'fundamental_analysis': fundamental_analysis
   231	            }
   232	
   233	        except Exception as e:
   234	            logger.debug(f"Error analyzing {ticker}: {e}")
   235	            return None
   236	
   237	    def process_batch(
   238	        self,
   239	        tickers: List[str],
   240	        resume: bool = True,
   241	        min_price: float = 5.0,
   242	        max_price: float = 10000.0,
   243	        min_volume: int = 100000
   244	    ) -> Dict:
   245	        """Process a batch of tickers with rate limiting and progress tracking.
   246	
   247	        Args:
   248	            tickers: List of tickers to process
   249	            resume: Resume from previous progress if available
   250	            min_price: Minimum stock price
   251	            max_price: Maximum stock price
   252	            min_volume: Minimum average daily volume
   253	
   254	        Returns:
   255	            Dict with all results
   256	        """
   257	        logger.info("="*60)
   258	        logger.info("BATCH PROCESSING STARTED")
   259	        logger.info(f"Total tickers: {len(tickers)}")
   260	        logger.info(f"Rate limit: {1/self.rate_limit_delay:.1f} requests/sec")
   261	        logger.info(f"Estimated time: {len(tickers) * self.rate_limit_delay / 3600:.1f} hours")
   262	        logger.info("="*60)
   263	
   264	        # Load SPY data
   265	        if not self.fetch_spy_data():
   266	            return {'error': 'Failed to fetch SPY data'}
   267	
   268	        # Load progress if resuming
   269	        if resume:
   270	            progress = self.load_progress()
   271	            if progress:
   272	                self.processed_tickers = set(progress['processed'])
   273	                self.current_results = progress['results']
   274	                logger.info(f"Resuming: {len(self.processed_tickers)} already done")
   275	
   276	        # Filter already processed
   277	        remaining_tickers = [t for t in tickers if t not in self.processed_tickers]
   278	        logger.info(f"Processing {len(remaining_tickers)} remaining tickers")
   279	
   280	        start_time = time.time()
   281	        all_analyses = self.current_results.copy()
   282	        phase_results = []
   283	
   284	        for i, ticker in enumerate(remaining_tickers, 1):
   285	            # Rate limiting
   286	            if i > 1:  # Don't delay on first request
   287	                time.sleep(self.rate_limit_delay)
   288	
   289	            # Progress logging
   290	            if i % 10 == 0 or i == 1:
   291	                elapsed = time.time() - start_time
   292	                rate = i / elapsed if elapsed > 0 else 0
   293	                remaining = len(remaining_tickers) - i
   294	                eta_seconds = remaining / rate if rate > 0 else 0
   295	                eta = str(timedelta(seconds=int(eta_seconds)))
   296	
   297	                logger.info(
   298	                    f"Progress: {len(self.processed_tickers) + i}/{len(tickers)} "
   299	                    f"({(len(self.processed_tickers) + i)/len(tickers)*100:.1f}%) | "
   300	                    f"Rate: {rate:.1f}/sec | ETA: {eta}"
   301	                )
   302	
   303	            # Analyze stock
   304	            analysis = self.analyze_stock_batch(
   305	                ticker,
   306	                min_price=min_price,
   307	                max_price=max_price,
   308	                min_volume=min_volume
   309	            )
   310	
   311	            if analysis:
   312	                all_analyses.append(analysis)
   313	                phase_results.append({
   314	                    'ticker': ticker,
   315	                    'phase': analysis['phase_info']['phase']
   316	                })
   317	
   318	            # Mark as processed
   319	            self.processed_tickers.add(ticker)
   320	
   321	            # Save progress periodically
   322	            if i % self.batch_size == 0:
   323	                self.save_progress(tickers, all_analyses)
   324	                logger.info(f"Progress checkpoint saved ({len(all_analyses)} analyzed)")
   325	
   326	        # Final save
   327	        self.save_progress(tickers, all_analyses)
   328	
   329	        total_time = time.time() - start_time
   330	        logger.info("="*60)
   331	        logger.info("BATCH PROCESSING COMPLETE")
   332	        logger.info(f"Total time: {str(timedelta(seconds=int(total_time)))}")
   333	        logger.info(f"Processed: {len(tickers)} tickers")
   334	        logger.info(f"Analyzed: {len(all_analyses)} stocks")
   335	        logger.info(f"Filtered out: {len(tickers) - len(all_analyses)} stocks")
   336	        logger.info("="*60)
   337	
   338	        return {
   339	            'analyses': all_analyses,
   340	            'phase_results': phase_results,
   341	            'total_processed': len(tickers),
   342	            'total_analyzed': len(all_analyses),
   343	            'processing_time_seconds': total_time
   344	        }
   345	
   346	    def clear_progress(self):
   347	        """Clear saved progress to start fresh."""
   348	        if self.progress_file.exists():
   349	            self.progress_file.unlink()
   350	            logger.info("Progress cleared")
   351	
   352	        self.processed_tickers.clear()
   353	        self.current_results.clear()

exec
/bin/zsh -lc "nl -ba run_optimized_scan.py | sed -n '1,420p'; nl -ba scripts/run_full_market_scan.py | sed -n '1,379p'; nl -ba src/screening/top20_ranker.py | sed -n '1,130p'; nl -ba src/agents/shortlist.py | sed -n '1,100p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	#!/usr/bin/env python3
     2	"""Optimized full market scanner with parallel processing.
     3	
     4	This version uses parallel workers to achieve 10-25 TPS safely while
     5	avoiding rate limits through:
     6	- Thread pool with 5 workers
     7	- Per-worker rate limiting (0.2s = 5 TPS each)
     8	- Adaptive backoff on errors
     9	- Session pooling
    10	
    11	Expected runtime: 15-30 minutes for 3,800+ stocks
    12	
    13	Usage:
    14	    python run_optimized_scan.py
    15	    python run_optimized_scan.py --workers 10  # Faster but riskier
    16	    python run_optimized_scan.py --conservative  # Slower but safer (3 workers)
    17	"""
    18	
    19	import argparse
    20	import json
    21	import logging
    22	import random
    23	import sys
    24	from datetime import datetime
    25	from pathlib import Path
    26	
    27	from src.data.universe_fetcher import USStockUniverseFetcher
    28	from src.screening.optimized_batch_processor import OptimizedBatchProcessor
    29	from src.screening.benchmark import (
    30	    analyze_spy_trend,
    31	    calculate_market_breadth,
    32	    format_benchmark_summary,
    33	    should_generate_signals
    34	)
    35	from src.screening.signal_engine import score_buy_signal, score_sell_signal
    36	from src.data.enhanced_fundamentals import EnhancedFundamentalsFetcher
    37	from src.data.reddit_sentiment import RedditSentimentFetcher
    38	from src.data.apewisdom_sentiment import ApeWisdomSentimentFetcher
    39	from src.data.insider_trading import InsiderTradingFetcher
    40	from src.data.earnings_risk import EarningsRiskFetcher
    41	from src.screening.top20_ranker import build_top20
    42	from src.agents.fundamentals_auditor import audit_candidates
    43	from src.agents.catalyst_sentiment import analyze_candidates
    44	from src.agents.congress_trades import get_signals_for_candidates as get_congress_signals
    45	from src.agents.shortlist import build_shortlist
    46	from src.utils.json_safe import sanitize_nan
    47	
    48	logging.basicConfig(
    49	    level=logging.INFO,
    50	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    51	)
    52	logger = logging.getLogger(__name__)
    53	
    54	
    55	def save_report(results, buy_signals, sell_signals, spy_analysis, breadth, output_dir="./data/daily_scans"):
    56	    """Save comprehensive report."""
    57	    Path(output_dir).mkdir(parents=True, exist_ok=True)
    58	
    59	    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    60	    date_str = datetime.now().strftime('%Y-%m-%d')
    61	
    62	    output = []
    63	    output.append("="*80)
    64	    output.append("OPTIMIZED FULL MARKET SCAN - ALL US STOCKS")
    65	    output.append(f"Scan Date: {date_str}")
    66	    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    67	    output.append("="*80)
    68	    output.append("")
    69	
    70	    # Stats
    71	    output.append("SCANNING STATISTICS")
    72	    output.append("-"*80)
    73	    output.append(f"Total Universe: {results['total_processed']:,} stocks")
    74	    output.append(f"Analyzed: {results['total_analyzed']:,} stocks")
    75	    output.append(f"Processing Time: {results['processing_time_seconds']/60:.1f} minutes")
    76	    output.append(f"Actual TPS: {results['actual_tps']:.2f}")
    77	
    78	    error_rate = results['error_rate'] * 100
    79	    if error_rate < 1:
    80	        error_emoji = "🟢"
    81	    elif error_rate < 5:
    82	        error_emoji = "🟡"
    83	    else:
    84	        error_emoji = "🔴"
    85	    output.append(f"{error_emoji} Error Rate: {error_rate:.2f}%")
    86	
    87	    # Buy/Sell signal counts with emoji
    88	    if len(buy_signals) > 0:
    89	        output.append(f"🟢 Buy Signals: {len(buy_signals)}")
    90	    else:
    91	        output.append(f"Buy Signals: {len(buy_signals)}")
    92	
    93	    if len(sell_signals) > 0:
    94	        output.append(f"🔴 Sell Signals: {len(sell_signals)}")
    95	    else:
    96	        output.append(f"Sell Signals: {len(sell_signals)}")
    97	    output.append("")
    98	
    99	    # Benchmark
   100	    output.append(format_benchmark_summary(spy_analysis, breadth))
   101	    output.append("")
   102	
   103	    # Buy signals
   104	    output.append("="*80)
   105	    output.append(f"🟢 TOP BUY SIGNALS (Score >= 70) - {len(buy_signals)} Total")
   106	    output.append("="*80)
   107	    output.append("")
   108	
   109	    if buy_signals:
   110	        for i, signal in enumerate(buy_signals[:50], 1):
   111	            score = signal['score']
   112	            # Score-based emoji (green/yellow with star for exceptional)
   113	            if score >= 90:
   114	                score_emoji = "⭐"  # Exceptional - star
   115	            elif score >= 80:
   116	                score_emoji = "🟢"  # Very good - green
   117	            elif score >= 70:
   118	                score_emoji = "🟢"  # Good - green
   119	            else:
   120	                score_emoji = "🟡"  # Borderline - yellow
   121	
   122	            output.append(f"\n{'#'*80}")
   123	            output.append(f"{score_emoji} BUY #{i}: {signal['ticker']} | Score: {signal['score']}/125")
   124	            output.append(f"{'#'*80}")
   125	            output.append(f"Phase: {signal['phase']}")
   126	
   127	            # Entry quality with emoji
   128	            entry_quality = signal.get('entry_quality', 'Unknown')
   129	            if entry_quality == 'Good':
   130	                output.append(f"🟢 Entry Quality: {entry_quality}")
   131	            elif entry_quality == 'Extended':
   132	                output.append(f"🟡 Entry Quality: {entry_quality}")
   133	            else:
   134	                output.append(f"🔴 Entry Quality: {entry_quality}")
   135	
   136	            # CRITICAL: Stop loss and R/R ratio
   137	            if signal.get('stop_loss'):
   138	                output.append(f"Stop Loss: ${signal['stop_loss']:.2f}")
   139	                details = signal.get('details', {})
   140	                risk_amt = details.get('risk_amount', 0)
   141	                reward_amt = details.get('reward_amount', 0)
   142	                rr_ratio = signal.get('risk_reward_ratio', 0)
   143	                # R/R ratio emoji
   144	                if rr_ratio >= 3:
   145	                    rr_emoji = "🟢"  # Excellent R/R
   146	                elif rr_ratio >= 2:
   147	                    rr_emoji = "🟢"  # Good R/R
   148	                else:
   149	                    rr_emoji = "🟡"  # Poor R/R
   150	                output.append(f"{rr_emoji} Risk/Reward: {rr_ratio:.1f}:1 (Risk ${risk_amt:.2f}, Reward ${reward_amt:.2f})")
   151	
   152	            if signal.get('breakout_price'):
   153	                output.append(f"Breakout: ${signal['breakout_price']:.2f}")
   154	
   155	            details = signal.get('details', {})
   156	            if 'rs_slope' in details:
   157	                rs_slope = details['rs_slope']
   158	                # RS emoji (green = good, yellow = ok, red = bad)
   159	                if rs_slope > 0.5:
   160	                    rs_emoji = "🟢"  # Strong RS
   161	                elif rs_slope > 0:
   162	                    rs_emoji = "🟡"  # Positive RS
   163	                else:
   164	                    rs_emoji = "🔴"  # Weak RS
   165	                output.append(f"{rs_emoji} RS: {rs_slope:.3f}")
   166	            if 'volume_ratio' in details:
   167	                vol_ratio = details['volume_ratio']
   168	                # Volume emoji
   169	                if vol_ratio > 1.5:
   170	                    vol_emoji = "🟢"  # High volume
   171	                elif vol_ratio > 1.0:
   172	                    vol_emoji = "🟡"  # Above average
   173	                else:
   174	                    vol_emoji = "🔴"  # Low volume
   175	                output.append(f"{vol_emoji} Volume: {vol_ratio:.1f}x")
   176	
   177	            # VCP pattern details if detected
   178	            vcp_data = details.get('vcp_data')
   179	            if vcp_data:
   180	                vcp_quality = vcp_data.get('quality', 0)
   181	                contractions = vcp_data.get('contractions', 0)
   182	                pattern = vcp_data.get('pattern', 'N/A')
   183	
   184	                if vcp_quality >= 80:
   185	                    vcp_emoji = "⭐"  # Exceptional VCP
   186	                elif vcp_quality >= 60:
   187	                    vcp_emoji = "🟢"  # Good VCP
   188	                elif vcp_quality >= 50:
   189	                    vcp_emoji = "🟡"  # Marginal VCP
   190	                else:
   191	                    vcp_emoji = "🟡"  # Partial pattern
   192	
   193	                if vcp_quality >= 50:
   194	                    output.append(f"{vcp_emoji} VCP: {pattern} (quality: {vcp_quality:.0f}/100)")
   195	
   196	            if signal.get('reddit_mentions_24h') is not None:
   197	                output.append(f"💬 Reddit Mentions (24h): {signal['reddit_mentions_24h']}")
   198	
   199	            output.append("\nKey Reasons:")
   200	            for reason in signal['reasons'][:7]:  # Show 7 instead of 5
   201	                output.append(f"  • {reason}")
   202	
   203	            if signal.get('fundamental_snapshot'):
   204	                output.append(signal['fundamental_snapshot'])
   205	
   206	        if len(buy_signals) > 50:
   207	            output.append(f"\n{'='*80}")
   208	            output.append(f"ADDITIONAL BUYS ({len(buy_signals)-50} more)")
   209	            output.append(f"{'='*80}\n")
   210	            remaining = [s['ticker'] for s in buy_signals[50:]]
   211	            for i in range(0, len(remaining), 10):
   212	                output.append(", ".join(remaining[i:i+10]))
   213	    else:
   214	        output.append("✗ NO BUY SIGNALS TODAY")
   215	
   216	    # Sell signals
   217	    output.append(f"\n\n{'='*80}")
   218	    output.append(f"🔴 TOP SELL SIGNALS (Score >= 60) - {len(sell_signals)} Total")
   219	    output.append(f"{'='*80}")
   220	    output.append("")
   221	
   222	    if sell_signals:
   223	        for i, signal in enumerate(sell_signals[:30], 1):
   224	            score = signal['score']
   225	            severity = signal['severity']
   226	
   227	            # Severity emoji (red/yellow with alarm for critical)
   228	            if severity == 'critical':
   229	                severity_emoji = "🚨"  # Critical - alarm
   230	            elif severity == 'high':
   231	                severity_emoji = "🔴"  # High - red
   232	            else:
   233	                severity_emoji = "🟡"  # Moderate - yellow
   234	
   235	            # Score emoji (higher score = more urgent to sell)
   236	            if score >= 80:
   237	                score_emoji = "🚨"  # Very urgent - alarm
   238	            elif score >= 70:
   239	                score_emoji = "🔴"  # Urgent - red
   240	            else:
   241	                score_emoji = "🟡"  # Warning - yellow
   242	
   243	            output.append(f"\n{'#'*80}")
   244	            output.append(f"{score_emoji} SELL #{i}: {signal['ticker']} | Score: {signal['score']}/110")
   245	            output.append(f"{'#'*80}")
   246	            output.append(f"Phase: {signal['phase']} | {severity_emoji} Severity: {severity.upper()}")
   247	            if signal.get('breakdown_level'):
   248	                output.append(f"Breakdown: ${signal['breakdown_level']:.2f}")
   249	            details = signal.get('details', {})
   250	            if 'rs_slope' in details:
   251	                rs_slope = details['rs_slope']
   252	                # RS emoji for sell signals (negative is expected)
   253	                if rs_slope < -0.5:
   254	                    rs_emoji = "🔴"  # Very weak RS
   255	                elif rs_slope < 0:
   256	                    rs_emoji = "🟡"  # Weak RS
   257	                else:
   258	                    rs_emoji = "🟢"  # Still positive RS (unusual for sell)
   259	                output.append(f"{rs_emoji} RS: {rs_slope:.3f}")
   260	            if signal.get('reddit_mentions_24h') is not None:
   261	                output.append(f"💬 Reddit Mentions (24h): {signal['reddit_mentions_24h']}")
   262	            output.append("\nSell Reasons:")
   263	            for reason in signal['reasons'][:5]:
   264	                output.append(f"  • {reason}")
   265	
   266	            if signal.get('fundamental_snapshot'):
   267	                output.append(signal['fundamental_snapshot'])
   268	
   269	        if len(sell_signals) > 30:
   270	            output.append(f"\n{'='*80}")
   271	            output.append(f"ADDITIONAL SELLS ({len(sell_signals)-30} more)")
   272	            output.append(f"{'='*80}\n")
   273	            remaining = [s['ticker'] for s in sell_signals[30:]]
   274	            for i in range(0, len(remaining), 10):
   275	                output.append(", ".join(remaining[i:i+10]))
   276	    else:
   277	        output.append("✗ NO SELL SIGNALS TODAY")
   278	
   279	    output.append(f"\n\n{'='*80}")
   280	    output.append("END OF SCAN")
   281	    output.append(f"{'='*80}\n")
   282	
   283	    report_text = "\n".join(output)
   284	
   285	    # Save
   286	    filepath = Path(output_dir) / f"optimized_scan_{timestamp}.txt"
   287	    with open(filepath, 'w') as f:
   288	        f.write(report_text)
   289	
   290	    latest_path = Path(output_dir) / "latest_optimized_scan.txt"
   291	    with open(latest_path, 'w') as f:
   292	        f.write(report_text)
   293	
   294	    logger.info(f"Report saved: {filepath}")
   295	    print(report_text)
   296	
   297	    return filepath
   298	
   299	
   300	def main():
   301	    parser = argparse.ArgumentParser(description='Optimized Full Market Scanner')
   302	    parser.add_argument('--workers', type=int, default=3, help='Parallel workers (default: 3)')
   303	    parser.add_argument('--delay', type=float, default=0.5, help='Delay per worker (default: 0.5s)')
   304	    parser.add_argument('--conservative', action='store_true', help='Ultra-conservative mode (2 workers, 1.0s delay)')
   305	    parser.add_argument('--aggressive', action='store_true', help='Faster mode (5 workers, 0.3s delay) - MAY HIT RATE LIMITS!')
   306	    parser.add_argument('--resume', action='store_true', help='Resume from progress')
   307	    parser.add_argument('--clear-progress', action='store_true', help='Clear progress')
   308	    parser.add_argument('--test-mode', action='store_true', help='Test with 100 stocks')
   309	    parser.add_argument('--min-price', type=float, default=5.0, help='Min price')
   310	    parser.add_argument('--min-volume', type=int, default=100000, help='Min volume')
   311	    parser.add_argument('--use-fmp', action='store_true', help='Use FMP for enhanced fundamentals on buy signals')
   312	    parser.add_argument('--git-storage', action='store_true', help='Use Git-based storage for fundamentals (recommended)')
   313	    parser.add_argument('--enable-llm-agents', action='store_true',
   314	                         help='Run the Fundamentals Auditor + Catalyst Sentiment agents (Claude API calls) '
   315	                              'on the Top 20 shortlist. Needs ANTHROPIC_API_KEY set; no-ops with a warning otherwise.')
   316	
   317	    args = parser.parse_args()
   318	
   319	    # Presets
   320	    if args.conservative:
   321	        args.workers = 2
   322	        args.delay = 1.0
   323	        logger.info("Ultra-conservative mode: 2 workers, 1.0s delay (~2 TPS)")
   324	    elif args.aggressive:
   325	        args.workers = 5
   326	        args.delay = 0.3
   327	        logger.warning("Aggressive mode: 5 workers, 0.3s delay (~17 TPS) - MAY HIT RATE LIMITS!")
   328	
   329	    effective_tps = args.workers / args.delay
   330	    logger.info(f"Configuration: {args.workers} workers × {1/args.delay:.1f} TPS = ~{effective_tps:.1f} TPS effective")
   331	
   332	    # "Hard search activated" notification — fires immediately on scan start, not
   333	    # at the end, so a manual/scheduled trigger is confirmed without waiting 15-30 min.
   334	    if not args.test_mode:
   335	        from src.notifications.email_notifier import EmailNotifier
   336	        EmailNotifier().send_notification(
   337	            subject="[Stock Screener] Hard Search Activated 🚀",
   338	            message=(
   339	                "Your full market scan (3,800+ stocks) just started.\n\n"
   340	                f"Workers: {args.workers} | Effective rate: ~{effective_tps:.1f} TPS\n"
   341	                "Expected runtime: 15-30 minutes.\n\n"
   342	                "You'll get a second email with the buy/sell signals when it finishes."
   343	            ),
   344	        )
   345	
   346	    # Initialize enhanced fundamentals fetcher
   347	    fundamentals_fetcher = EnhancedFundamentalsFetcher()
   348	    if args.use_fmp and fundamentals_fetcher.fmp_available:
   349	        logger.info("FMP enabled - will use for buy signal fundamentals")
   350	    elif args.use_fmp:
   351	        logger.warning("--use-fmp specified but FMP_API_KEY not set. Using yfinance only.")
   352	
   353	    try:
   354	        # Fetch universe
   355	        universe_fetcher = USStockUniverseFetcher()
   356	        logger.info("Fetching stock universe...")
   357	        tickers = universe_fetcher.fetch_universe()
   358	
   359	        if not tickers:
   360	            logger.error("Failed to fetch universe")
   361	            sys.exit(1)
   362	
   363	        logger.info(f"Universe: {len(tickers):,} stocks")
   364	
   365	        if args.test_mode:
   366	            # universe_fetcher sorts alphabetically, so tickers[:100] would always be
   367	            # the same ~100 "A" names every run — random sample instead for real coverage.
   368	            tickers = random.sample(tickers, min(100, len(tickers)))
   369	            logger.info(f"TEST MODE: {len(tickers)} random stocks")
   370	
   371	        # Initialize processor
   372	        processor = OptimizedBatchProcessor(
   373	            max_workers=args.workers,
   374	            rate_limit_delay=args.delay,
   375	            use_git_storage=args.git_storage
   376	        )
   377	
   378	        if args.git_storage:
   379	            logger.info("Git-based fundamental storage enabled - 74% API call reduction!")
   380	
   381	        if args.clear_progress:
   382	            processor.clear_progress()
   383	
   384	        # Process
   385	        results = processor.process_batch_parallel(
   386	            tickers,
   387	            resume=args.resume,
   388	            min_price=args.min_price,
   389	            min_volume=args.min_volume
   390	        )
   391	
   392	        if 'error' in results:
   393	            logger.error(results['error'])
   394	            sys.exit(1)
   395	
   396	        # Analysis
   397	        logger.info("Generating signals...")
   398	        spy_analysis = analyze_spy_trend(processor.spy_data, processor.spy_price)
   399	        breadth = calculate_market_breadth(results['phase_results'])
   400	        signal_rec = should_generate_signals(spy_analysis, breadth)
   401	
   402	        # Buy signals
   403	        buy_signals = []
   404	        if signal_rec['should_generate_buys']:
   405	            for analysis in results['analyses']:
   406	                if analysis['phase_info']['phase'] in [1, 2]:
   407	                    signal = score_buy_signal(
   408	                        ticker=analysis['ticker'],
   409	                        price_data=analysis['price_data'],
   410	                        current_price=analysis['current_price'],
   411	                        phase_info=analysis['phase_info'],
   412	                        rs_series=analysis['rs_series'],
   413	                        fundamentals=analysis.get('quarterly_data'),  # Pass raw quarterly data, not analyzed
   414	                        vcp_data=analysis.get('vcp_data')  # Added VCP data
   415	                    )
   416	                    if signal['is_buy']:
   417	                        # Use FMP for enhanced snapshot if requested and available
   418	                        signal['fundamental_snapshot'] = fundamentals_fetcher.create_snapshot(
   419	                            analysis['ticker'],
   420	                            quarterly_data=analysis.get('quarterly_data', {}),
     1	#!/usr/bin/env python3
     2	"""Full market scanner for ALL publicly traded US stocks.
     3	
     4	This script:
     5	1. Fetches the latest list of all US-listed stocks
     6	2. Filters out penny stocks and low-volume stocks
     7	3. Processes them in batches with rate limiting (1 TPS)
     8	4. Tracks progress and can resume if interrupted
     9	5. Generates comprehensive buy/sell lists
    10	6. Saves results incrementally
    11	
    12	Designed to run daily at 6:30 AM EST after market data is updated.
    13	
    14	Usage:
    15	    python run_full_market_scan.py
    16	    python run_full_market_scan.py --resume
    17	    python run_full_market_scan.py --clear-progress
    18	    python run_full_market_scan.py --min-price 10 --min-volume 500000
    19	"""
    20	
    21	import argparse
    22	import logging
    23	import sys
    24	from datetime import datetime
    25	from pathlib import Path
    26	
    27	from src.data.universe_fetcher import USStockUniverseFetcher
    28	from src.screening.batch_processor import BatchStockProcessor
    29	from src.screening.benchmark import (
    30	    analyze_spy_trend,
    31	    calculate_market_breadth,
    32	    format_benchmark_summary,
    33	    should_generate_signals
    34	)
    35	from src.screening.signal_engine import score_buy_signal, score_sell_signal
    36	from src.data.fundamentals_fetcher import create_fundamental_snapshot
    37	
    38	logging.basicConfig(
    39	    level=logging.INFO,
    40	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    41	)
    42	logger = logging.getLogger(__name__)
    43	
    44	
    45	def save_daily_report(
    46	    results: dict,
    47	    buy_signals: list,
    48	    sell_signals: list,
    49	    spy_analysis: dict,
    50	    breadth: dict,
    51	    output_dir: str = "./data/daily_scans"
    52	):
    53	    """Save comprehensive daily market scan report.
    54	
    55	    Args:
    56	        results: Batch processing results
    57	        buy_signals: List of buy signals
    58	        sell_signals: List of sell signals
    59	        spy_analysis: SPY analysis
    60	        breadth: Market breadth
    61	        output_dir: Output directory
    62	    """
    63	    Path(output_dir).mkdir(parents=True, exist_ok=True)
    64	
    65	    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    66	    date_str = datetime.now().strftime('%Y-%m-%d')
    67	
    68	    # Create comprehensive report
    69	    output = []
    70	
    71	    output.append("="*80)
    72	    output.append("FULL MARKET SCAN - ALL US-LISTED STOCKS")
    73	    output.append(f"Scan Date: {date_str}")
    74	    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    75	    output.append("="*80)
    76	    output.append("")
    77	
    78	    # Scanning statistics
    79	    output.append("SCANNING STATISTICS")
    80	    output.append("-"*80)
    81	    output.append(f"Total Universe: {results['total_processed']:,} stocks")
    82	    output.append(f"Analyzed: {results['total_analyzed']:,} stocks")
    83	    output.append(f"Filtered Out: {results['total_processed'] - results['total_analyzed']:,} stocks")
    84	    output.append(f"Processing Time: {results['processing_time_seconds']/3600:.1f} hours")
    85	    output.append(f"Buy Signals: {len(buy_signals)}")
    86	    output.append(f"Sell Signals: {len(sell_signals)}")
    87	    output.append("")
    88	
    89	    # Benchmark summary
    90	    output.append(format_benchmark_summary(spy_analysis, breadth))
    91	    output.append("")
    92	
    93	    # Top buy signals
    94	    output.append("="*80)
    95	    output.append(f"TOP BUY SIGNALS (Score >= 70) - {len(buy_signals)} Total")
    96	    output.append("="*80)
    97	    output.append("")
    98	
    99	    if buy_signals:
   100	        # Show top 50 with details, then just ticker list for rest
   101	        top_n = 50
   102	
   103	        for i, signal in enumerate(buy_signals[:top_n], 1):
   104	            output.append(f"\n{'#'*80}")
   105	            output.append(f"BUY #{i}: {signal['ticker']} | Score: {signal['score']}/100")
   106	            output.append(f"{'#'*80}")
   107	            output.append(f"Phase: {signal['phase']}")
   108	
   109	            if signal.get('breakout_price'):
   110	                output.append(f"Breakout Price: ${signal['breakout_price']:.2f}")
   111	
   112	            details = signal.get('details', {})
   113	            if 'rs_slope' in details:
   114	                output.append(f"RS Slope: {details['rs_slope']:.3f}")
   115	            if 'volume_ratio' in details:
   116	                output.append(f"Volume: {details['volume_ratio']:.1f}x average")
   117	
   118	            output.append("\nKey Reasons:")
   119	            for reason in signal['reasons'][:5]:  # Top 5 reasons
   120	                output.append(f"  • {reason}")
   121	
   122	            if signal.get('fundamental_snapshot'):
   123	                output.append(signal['fundamental_snapshot'])
   124	
   125	        # Remaining buys as ticker list
   126	        if len(buy_signals) > top_n:
   127	            output.append(f"\n{'='*80}")
   128	            output.append(f"ADDITIONAL BUY SIGNALS ({len(buy_signals) - top_n} more)")
   129	            output.append(f"{'='*80}\n")
   130	
   131	            remaining = [s['ticker'] for s in buy_signals[top_n:]]
   132	            # Format as comma-separated list, 10 per line
   133	            for i in range(0, len(remaining), 10):
   134	                output.append(", ".join(remaining[i:i+10]))
   135	
   136	    else:
   137	        output.append("✗ NO BUY SIGNALS TODAY")
   138	        output.append("\nMarket conditions not favorable for new positions.")
   139	
   140	    # Top sell signals
   141	    output.append(f"\n\n{'='*80}")
   142	    output.append(f"TOP SELL SIGNALS (Score >= 60) - {len(sell_signals)} Total")
   143	    output.append(f"{'='*80}")
   144	    output.append("")
   145	
   146	    if sell_signals:
   147	        # Show top 30 with details
   148	        top_n = 30
   149	
   150	        for i, signal in enumerate(sell_signals[:top_n], 1):
   151	            output.append(f"\n{'#'*80}")
   152	            output.append(f"SELL #{i}: {signal['ticker']} | Score: {signal['score']}/100 | Severity: {signal['severity'].upper()}")
   153	            output.append(f"{'#'*80}")
   154	            output.append(f"Phase: {signal['phase']}")
   155	
   156	            if signal.get('breakdown_level'):
   157	                output.append(f"Breakdown Level: ${signal['breakdown_level']:.2f}")
   158	
   159	            details = signal.get('details', {})
   160	            if 'rs_slope' in details:
   161	                output.append(f"RS Rollover: {details['rs_slope']:.3f}")
   162	            if 'volume_ratio' in details:
   163	                output.append(f"Volume: {details['volume_ratio']:.1f}x average")
   164	
   165	            output.append("\nKey Reasons:")
   166	            for reason in signal['reasons'][:5]:
   167	                output.append(f"  • {reason}")
   168	
   169	        # Remaining sells as ticker list
   170	        if len(sell_signals) > top_n:
   171	            output.append(f"\n{'='*80}")
   172	            output.append(f"ADDITIONAL SELL SIGNALS ({len(sell_signals) - top_n} more)")
   173	            output.append(f"{'='*80}\n")
   174	
   175	            remaining = [s['ticker'] for s in sell_signals[top_n:]]
   176	            for i in range(0, len(remaining), 10):
   177	                output.append(", ".join(remaining[i:i+10]))
   178	
   179	    else:
   180	        output.append("✗ NO SELL SIGNALS TODAY")
   181	
   182	    output.append(f"\n\n{'='*80}")
   183	    output.append("END OF DAILY MARKET SCAN")
   184	    output.append(f"{'='*80}\n")
   185	
   186	    # Save report
   187	    report_text = "\n".join(output)
   188	
   189	    filepath = Path(output_dir) / f"market_scan_{timestamp}.txt"
   190	    with open(filepath, 'w') as f:
   191	        f.write(report_text)
   192	
   193	    logger.info(f"Report saved to {filepath}")
   194	
   195	    # Also save as "latest" for easy access
   196	    latest_path = Path(output_dir) / "latest_scan.txt"
   197	    with open(latest_path, 'w') as f:
   198	        f.write(report_text)
   199	
   200	    logger.info(f"Latest scan link: {latest_path}")
   201	
   202	    # Print summary to console
   203	    print(report_text)
   204	
   205	    return filepath
   206	
   207	
   208	def main():
   209	    """Main entry point."""
   210	    parser = argparse.ArgumentParser(
   211	        description='Full Market Scanner - All US-Listed Stocks'
   212	    )
   213	    parser.add_argument(
   214	        '--resume',
   215	        action='store_true',
   216	        help='Resume from previous progress'
   217	    )
   218	    parser.add_argument(
   219	        '--clear-progress',
   220	        action='store_true',
   221	        help='Clear progress and start fresh'
   222	    )
   223	    parser.add_argument(
   224	        '--min-price',
   225	        type=float,
   226	        default=5.0,
   227	        help='Minimum stock price (default: $5.00)'
   228	    )
   229	    parser.add_argument(
   230	        '--max-price',
   231	        type=float,
   232	        default=10000.0,
   233	        help='Maximum stock price (default: $10,000)'
   234	    )
   235	    parser.add_argument(
   236	        '--min-volume',
   237	        type=int,
   238	        default=100000,
   239	        help='Minimum average daily volume (default: 100,000)'
   240	    )
   241	    parser.add_argument(
   242	        '--rate-limit',
   243	        type=float,
   244	        default=1.0,
   245	        help='Seconds between API calls (default: 1.0 = 1 TPS)'
   246	    )
   247	    parser.add_argument(
   248	        '--test-mode',
   249	        action='store_true',
   250	        help='Test mode - only process first 100 stocks'
   251	    )
   252	
   253	    args = parser.parse_args()
   254	
   255	    logger.info("="*80)
   256	    logger.info("FULL MARKET SCANNER - ALL US-LISTED STOCKS")
   257	    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
   258	    logger.info("="*80)
   259	
   260	    try:
   261	        # Initialize components
   262	        universe_fetcher = USStockUniverseFetcher()
   263	        processor = BatchStockProcessor(rate_limit_delay=args.rate_limit)
   264	
   265	        # Clear progress if requested
   266	        if args.clear_progress:
   267	            processor.clear_progress()
   268	            logger.info("Progress cleared - starting fresh")
   269	
   270	        # Fetch stock universe
   271	        logger.info("Fetching US stock universe...")
   272	        tickers = universe_fetcher.fetch_universe()
   273	
   274	        if not tickers:
   275	            logger.error("Failed to fetch stock universe")
   276	            sys.exit(1)
   277	
   278	        logger.info(f"Universe loaded: {len(tickers):,} stocks")
   279	
   280	        # Test mode - limit to first 100
   281	        if args.test_mode:
   282	            tickers = tickers[:100]
   283	            logger.info(f"TEST MODE: Limited to {len(tickers)} stocks")
   284	
   285	        # Process all stocks
   286	        results = processor.process_batch(
   287	            tickers,
   288	            resume=args.resume,
   289	            min_price=args.min_price,
   290	            max_price=args.max_price,
   291	            min_volume=args.min_volume
   292	        )
   293	
   294	        if 'error' in results:
   295	            logger.error(f"Processing failed: {results['error']}")
   296	            sys.exit(1)
   297	
   298	        # Analyze SPY and calculate breadth
   299	        logger.info("Calculating market metrics...")
   300	        spy_analysis = analyze_spy_trend(processor.spy_data, processor.spy_price)
   301	        breadth = calculate_market_breadth(results['phase_results'])
   302	
   303	        # Determine if we should generate signals
   304	        signal_rec = should_generate_signals(spy_analysis, breadth)
   305	
   306	        # Score buy signals
   307	        buy_signals = []
   308	        if signal_rec['should_generate_buys']:
   309	            logger.info("Scoring buy signals...")
   310	            for analysis in results['analyses']:
   311	                if analysis['phase_info']['phase'] in [1, 2]:
   312	                    buy_signal = score_buy_signal(
   313	                        ticker=analysis['ticker'],
   314	                        price_data=analysis['price_data'],
   315	                        current_price=analysis['current_price'],
   316	                        phase_info=analysis['phase_info'],
   317	                        rs_series=analysis['rs_series'],
   318	                        fundamentals=analysis.get('fundamental_analysis')
   319	                    )
   320	
   321	                    if buy_signal['is_buy']:
   322	                        buy_signal['fundamental_snapshot'] = create_fundamental_snapshot(
   323	                            analysis['ticker'],
   324	                            analysis.get('quarterly_data', {})
   325	                        )
   326	                        buy_signals.append(buy_signal)
   327	
   328	            buy_signals = sorted(buy_signals, key=lambda x: x['score'], reverse=True)
   329	            logger.info(f"Found {len(buy_signals)} buy signals")
   330	
   331	        # Score sell signals
   332	        sell_signals = []
   333	        if signal_rec['should_generate_sells']:
   334	            logger.info("Scoring sell signals...")
   335	            for analysis in results['analyses']:
   336	                if analysis['phase_info']['phase'] in [3, 4]:
   337	                    sell_signal = score_sell_signal(
   338	                        ticker=analysis['ticker'],
   339	                        price_data=analysis['price_data'],
   340	                        current_price=analysis['current_price'],
   341	                        phase_info=analysis['phase_info'],
   342	                        rs_series=analysis['rs_series']
   343	                    )
   344	
   345	                    if sell_signal['is_sell']:
   346	                        sell_signals.append(sell_signal)
   347	
   348	            sell_signals = sorted(sell_signals, key=lambda x: x['score'], reverse=True)
   349	            logger.info(f"Found {len(sell_signals)} sell signals")
   350	
   351	        # Generate and save report
   352	        logger.info("Generating daily report...")
   353	        save_daily_report(
   354	            results,
   355	            buy_signals,
   356	            sell_signals,
   357	            spy_analysis,
   358	            breadth
   359	        )
   360	
   361	        logger.info("="*80)
   362	        logger.info("FULL MARKET SCAN COMPLETE")
   363	        logger.info(f"Total Buy Signals: {len(buy_signals)}")
   364	        logger.info(f"Total Sell Signals: {len(sell_signals)}")
   365	        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
   366	        logger.info("="*80)
   367	
   368	    except KeyboardInterrupt:
   369	        logger.info("\nScan interrupted by user - progress has been saved")
   370	        logger.info("Run with --resume to continue from where you left off")
   371	        sys.exit(0)
   372	
   373	    except Exception as e:
   374	        logger.error(f"Fatal error: {e}", exc_info=True)
   375	        sys.exit(1)
   376	
   377	
   378	if __name__ == '__main__':
   379	    main()
     1	"""Combine technical/fundamental buy signals with Reddit buzz and insider buying into
     2	a ranked top-20 shortlist, with links explaining why each stock is moving.
     3	
     4	Ranking rule: a stock must already be a qualified buy signal (passed the full
     5	Minervini technical/fundamental screen in signal_engine.py) to be eligible here —
     6	Reddit mentions and insider buying only re-rank and enrich within that already-
     7	qualified pool, they never substitute for it. This module adds no new tickers.
     8	"""
     9	
    10	import logging
    11	import math
    12	from typing import Dict, List, Optional
    13	
    14	import yfinance as yf
    15	
    16	logger = logging.getLogger(__name__)
    17	
    18	REDDIT_MENTION_WEIGHT = 5.0  # bonus points per log(1 + mentions); diminishing returns
    19	INSIDER_BUY_WEIGHT = 3.0  # bonus points per log(1 + $thousands bought); diminishing returns
    20	NEWS_ITEMS_PER_TICKER = 2
    21	
    22	
    23	def _fetch_news_links(ticker: str, limit: int = NEWS_ITEMS_PER_TICKER) -> List[Dict]:
    24	    """Best-effort recent news headlines for a ticker via yfinance. Never raises."""
    25	    try:
    26	        news = yf.Ticker(ticker).news or []
    27	    except Exception as e:
    28	        logger.debug(f"News fetch failed for {ticker}: {e}")
    29	        return []
    30	
    31	    links = []
    32	    for item in news[:limit]:
    33	        content = item.get('content', {})
    34	        title = content.get('title')
    35	        url = (
    36	            (content.get('canonicalUrl') or {}).get('url')
    37	            or (content.get('clickThroughUrl') or {}).get('url')
    38	        )
    39	        if title and url:
    40	            links.append({'title': title, 'url': url})
    41	    return links
    42	
    43	
    44	def build_top20(
    45	    buy_signals: List[Dict],
    46	    reddit_mentions: Optional[Dict[str, Dict]] = None,
    47	    insider_signals: Optional[Dict[str, Dict]] = None,
    48	    limit: int = 20,
    49	) -> List[Dict]:
    50	    """Rank qualified buy signals by combined technical + Reddit-buzz + insider-buying score.
    51	
    52	    News links are only fetched for the final top N (not the whole buy_signals pool),
    53	    since each lookup is a network call — ranking happens first on score alone, then
    54	    news links are attached to just the finalists. Reddit and insider "why" links come
    55	    for free from data already fetched for the whole pool (needed for scoring anyway).
    56	
    57	    Args:
    58	        buy_signals: Already-scored, already-qualified buy signals.
    59	        reddit_mentions: Optional {ticker: {'count', 'top_post_title', 'top_post_url'}}
    60	            from RedditSentimentFetcher.fetch_mentions(). Missing/empty is fine —
    61	            ranking then falls back to pure technical score.
    62	        insider_signals: Optional {ticker: {'purchases_90d', 'total_buy_value', 'buyers',
    63	            'top_buy_url'}} from InsiderTradingFetcher.get_insider_signal().
    64	        limit: Max entries to return.
    65	
    66	    Returns:
    67	        List of signal dicts (+ combined_score, reddit_mentions_24h, insider_buy_value,
    68	        why_links), sorted best-first, length <= limit.
    69	    """
    70	    reddit_mentions = reddit_mentions or {}
    71	    insider_signals = insider_signals or {}
    72	    ranked = []
    73	
    74	    for signal in buy_signals:
    75	        ticker = signal['ticker']
    76	        reddit_info = reddit_mentions.get(ticker, {})
    77	        mention_count = reddit_info.get('count', 0)
    78	        reddit_boost = math.log1p(mention_count) * REDDIT_MENTION_WEIGHT
    79	
    80	        insider_info = insider_signals.get(ticker, {})
    81	        buy_value = insider_info.get('total_buy_value', 0)
    82	        insider_boost = math.log1p(buy_value / 1000) * INSIDER_BUY_WEIGHT
    83	
    84	        entry = dict(signal)
    85	        entry['reddit_mentions_24h'] = mention_count
    86	        entry['insider_buy_value_90d'] = buy_value
    87	        entry['combined_score'] = round(signal['score'] + reddit_boost + insider_boost, 2)
    88	        entry['_reddit_info'] = reddit_info
    89	        entry['_insider_info'] = insider_info
    90	        ranked.append(entry)
    91	
    92	    ranked.sort(key=lambda s: s['combined_score'], reverse=True)
    93	    top = ranked[:limit]
    94	
    95	    for entry in top:
    96	        reddit_info = entry.pop('_reddit_info', {})
    97	        insider_info = entry.pop('_insider_info', {})
    98	        why_links = []
    99	
   100	        # Earnings risk is a WARNING, not a bullish reason — shown first, distinct label.
   101	        earnings_risk = entry.get('earnings_risk')
   102	        if earnings_risk and earnings_risk.get('has_upcoming_earnings'):
   103	            why_links.append({
   104	                'label': '⚠️ Earnings Risk',
   105	                'title': earnings_risk['note'],
   106	                'url': f"https://finance.yahoo.com/calendar/earnings?symbol={entry['ticker']}",
   107	            })
   108	
   109	        if insider_info.get('top_buy_url'):
   110	            top_buyer = (insider_info.get('buyers') or [{}])[0]
   111	            buyer_desc = top_buyer.get('officer_title') or ('Director' if top_buyer.get('is_director') else 'Insider')
   112	            why_links.append({
   113	                'label': f"Insider Buy (${entry['insider_buy_value_90d']:,.0f}/90d)",
   114	                'title': f"{top_buyer.get('owner_name', 'Insider')} ({buyer_desc}) bought {top_buyer.get('shares', 0):.0f} shares @ ${top_buyer.get('price', 0):.2f}",
   115	                'url': insider_info['top_buy_url'],
   116	            })
   117	
   118	        if reddit_info.get('top_post_url'):
   119	            why_links.append({
   120	                'label': f"Reddit ({entry['reddit_mentions_24h']} mentions/24h)",
   121	                'title': reddit_info.get('top_post_title'),
   122	                'url': reddit_info['top_post_url'],
   123	            })
   124	
   125	        for news_item in _fetch_news_links(entry['ticker']):
   126	            why_links.append({'label': 'News', 'title': news_item['title'], 'url': news_item['url']})
   127	
   128	        entry['why_links'] = why_links
   129	
   130	    return top
     1	"""Builds the final Top 5 shortlist from the Top 20 pool by actually filtering on
     2	the LLM agents' output, instead of just labeling it.
     3	
     4	Drop rules (a candidate is filtered out of the ranked pool, not the email —
     5	see below):
     6	  - Fundamentals Auditor says red flags outweigh green flags
     7	  - Catalyst Sentiment score <= -2 (a real negative catalyst, not just noise)
     8	
     9	Survivors are ranked by composite_score = technical score + catalyst_score*2 +
    10	congress_score*3 (congress weighted highest since it's a distinct, hard-to-fake
    11	data source; catalyst next since it's Claude's live news read; base score is
    12	already what got the candidate into the Top 20 pool in the first place).
    13	
    14	If fewer than `size` candidates survive the drop rules, the list is backfilled
    15	from the filtered-out pool (best composite_score first) so the email is never
    16	empty on a slow-news day — those backfilled entries keep their drop_reasons so
    17	it's visible in the email that they didn't fully clear the bar.
    18	"""
    19	
    20	from typing import Dict, List, Optional
    21	
    22	
    23	def build_shortlist(
    24	    top20: List[Dict],
    25	    fundamentals_audits: Optional[Dict[str, Dict]] = None,
    26	    catalyst_sentiments: Optional[Dict[str, Dict]] = None,
    27	    congress_signals: Optional[Dict[str, Dict]] = None,
    28	    size: int = 5,
    29	) -> List[Dict]:
    30	    fundamentals_audits = fundamentals_audits or {}
    31	    catalyst_sentiments = catalyst_sentiments or {}
    32	    congress_signals = congress_signals or {}
    33	
    34	    scored = []
    35	    for s in top20:
    36	        ticker = s['ticker']
    37	        drop_reasons = []
    38	
    39	        audit = fundamentals_audits.get(ticker)
    40	        if audit and audit.get('overall_assessment') == 'red_flags_outweigh':
    41	            drop_reasons.append('Fundamentals Auditor: red flags outweigh green')
    42	
    43	        sentiment = catalyst_sentiments.get(ticker)
    44	        catalyst_score = sentiment.get('catalyst_score', 0) if sentiment else 0
    45	        if sentiment and catalyst_score <= -2:
    46	            ctype = (sentiment.get('catalyst_type') or 'other').replace('_', ' ')
    47	            drop_reasons.append(f"Catalyst Sentiment: {ctype} ({catalyst_score:+d})")
    48	
    49	        congress = congress_signals.get(ticker)
    50	        congress_score = congress.get('score', 0) if congress else 0
    51	
    52	        composite = s.get('combined_score', s.get('score', 0)) + catalyst_score * 2 + congress_score * 3
    53	
    54	        scored.append({
    55	            **s,
    56	            'drop_reasons': drop_reasons,
    57	            'passed_filters': not drop_reasons,
    58	            'catalyst_score': catalyst_score,
    59	            'congress_score': congress_score,
    60	            'composite_score': round(composite, 2),
    61	        })
    62	
    63	    passed = sorted(
    64	        [s for s in scored if s['passed_filters']],
    65	        key=lambda s: s['composite_score'], reverse=True,
    66	    )
    67	    shortlist = passed[:size]
    68	
    69	    if len(shortlist) < size:
    70	        chosen_tickers = {s['ticker'] for s in shortlist}
    71	        backfill = sorted(
    72	            [s for s in scored if s['ticker'] not in chosen_tickers],
    73	            key=lambda s: s['composite_score'], reverse=True,
    74	        )
    75	        shortlist += backfill[:size - len(shortlist)]
    76	
    77	    return shortlist

exec
/bin/zsh -lc "nl -ba run_optimized_scan.py | sed -n '380,620p'; nl -ba src/data/universe_fetcher.py | sed -n '1,222p'; nl -ba src/data/reddit_sentiment.py; nl -ba src/data/apewisdom_sentiment.py" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
   380	
   381	        if args.clear_progress:
   382	            processor.clear_progress()
   383	
   384	        # Process
   385	        results = processor.process_batch_parallel(
   386	            tickers,
   387	            resume=args.resume,
   388	            min_price=args.min_price,
   389	            min_volume=args.min_volume
   390	        )
   391	
   392	        if 'error' in results:
   393	            logger.error(results['error'])
   394	            sys.exit(1)
   395	
   396	        # Analysis
   397	        logger.info("Generating signals...")
   398	        spy_analysis = analyze_spy_trend(processor.spy_data, processor.spy_price)
   399	        breadth = calculate_market_breadth(results['phase_results'])
   400	        signal_rec = should_generate_signals(spy_analysis, breadth)
   401	
   402	        # Buy signals
   403	        buy_signals = []
   404	        if signal_rec['should_generate_buys']:
   405	            for analysis in results['analyses']:
   406	                if analysis['phase_info']['phase'] in [1, 2]:
   407	                    signal = score_buy_signal(
   408	                        ticker=analysis['ticker'],
   409	                        price_data=analysis['price_data'],
   410	                        current_price=analysis['current_price'],
   411	                        phase_info=analysis['phase_info'],
   412	                        rs_series=analysis['rs_series'],
   413	                        fundamentals=analysis.get('quarterly_data'),  # Pass raw quarterly data, not analyzed
   414	                        vcp_data=analysis.get('vcp_data')  # Added VCP data
   415	                    )
   416	                    if signal['is_buy']:
   417	                        # Use FMP for enhanced snapshot if requested and available
   418	                        signal['fundamental_snapshot'] = fundamentals_fetcher.create_snapshot(
   419	                            analysis['ticker'],
   420	                            quarterly_data=analysis.get('quarterly_data', {}),
   421	                            use_fmp=args.use_fmp
   422	                        )
   423	                        buy_signals.append(signal)
   424	
   425	        buy_signals = sorted(buy_signals, key=lambda x: x['score'], reverse=True)
   426	
   427	        # Sell signals
   428	        sell_signals = []
   429	        if signal_rec['should_generate_sells']:
   430	            for analysis in results['analyses']:
   431	                if analysis['phase_info']['phase'] in [3, 4]:
   432	                    signal = score_sell_signal(
   433	                        ticker=analysis['ticker'],
   434	                        price_data=analysis['price_data'],
   435	                        current_price=analysis['current_price'],
   436	                        phase_info=analysis['phase_info'],
   437	                        rs_series=analysis['rs_series'],
   438	                        fundamentals=analysis.get('quarterly_data')  # Pass raw quarterly data, not analyzed
   439	                    )
   440	                    if signal['is_sell']:
   441	                        # Add fundamental snapshot
   442	                        signal['fundamental_snapshot'] = fundamentals_fetcher.create_snapshot(
   443	                            analysis['ticker'],
   444	                            quarterly_data=analysis.get('quarterly_data', {}),
   445	                            use_fmp=args.use_fmp
   446	                        )
   447	                        sell_signals.append(signal)
   448	
   449	        sell_signals = sorted(sell_signals, key=lambda x: x['score'], reverse=True)
   450	
   451	        # Earnings risk warning — NOT a bullish/bearish signal, just a heads-up that a
   452	        # high-uncertainty event (which trend-following can't predict) is imminent. No
   453	        # credentials needed, always available, applies to both buy and sell signals.
   454	        tickers_of_interest = {s['ticker'] for s in buy_signals} | {s['ticker'] for s in sell_signals}
   455	        if tickers_of_interest:
   456	            logger.info(f"Checking earnings risk for {len(tickers_of_interest)} signal tickers...")
   457	            earnings_fetcher = EarningsRiskFetcher()
   458	            flagged = 0
   459	            for signal in buy_signals + sell_signals:
   460	                risk = earnings_fetcher.get_earnings_risk(signal['ticker'])
   461	                if risk['has_upcoming_earnings']:
   462	                    signal['earnings_risk'] = risk
   463	                    # Inserted into `reasons` (not a separate field) so it flows through
   464	                    # the existing text report / email "top reason" / dashboard bullet
   465	                    # rendering automatically, without needing parallel display code.
   466	                    signal['reasons'].insert(0, f"⚠️ {risk['note']}")
   467	                    flagged += 1
   468	            logger.info(f"Earnings risk: {flagged} tickers have earnings within 14 days")
   469	
   470	        # Reddit mentions. Prefers the official PRAW-based fetcher if
   471	        # REDDIT_CLIENT_ID/SECRET are set (configurable subreddit list, real-time);
   472	        # otherwise falls back to ApeWisdom's free public API (no credentials,
   473	        # no setup, but their subreddit/timeframe choices aren't configurable).
   474	        reddit_mentions = {}
   475	        if tickers_of_interest:
   476	            reddit_fetcher = RedditSentimentFetcher()
   477	            if reddit_fetcher.available:
   478	                logger.info(f"Checking Reddit mentions for {len(tickers_of_interest)} signal tickers (PRAW)...")
   479	                reddit_mentions = reddit_fetcher.fetch_mentions(tickers_of_interest)
   480	            else:
   481	                logger.info(f"Checking Reddit mentions for {len(tickers_of_interest)} signal tickers (ApeWisdom, no credentials)...")
   482	                reddit_mentions = ApeWisdomSentimentFetcher().fetch_mentions(tickers_of_interest)
   483	
   484	            if reddit_mentions:
   485	                for signal in buy_signals:
   486	                    signal['reddit_mentions_24h'] = reddit_mentions.get(signal['ticker'], {}).get('count', 0)
   487	                for signal in sell_signals:
   488	                    signal['reddit_mentions_24h'] = reddit_mentions.get(signal['ticker'], {}).get('count', 0)
   489	                total_mentions = sum(v['count'] for v in reddit_mentions.values())
   490	                logger.info(f"Reddit: {total_mentions} mentions found across {len(reddit_mentions)} tickers")
   491	
   492	        # Insider buying (SEC Form 4, "P" open-market purchases only) — no credentials
   493	        # needed, always available, so no gating check like Reddit/FMP.
   494	        insider_signals = {}
   495	        buy_tickers = {s['ticker'] for s in buy_signals}
   496	        if buy_tickers:
   497	            logger.info(f"Checking insider buying (SEC Form 4) for {len(buy_tickers)} buy signal tickers...")
   498	            insider_fetcher = InsiderTradingFetcher()
   499	            for ticker in buy_tickers:
   500	                signal = insider_fetcher.get_insider_signal(ticker)
   501	                if signal['purchases_90d'] > 0:
   502	                    insider_signals[ticker] = signal
   503	            total_insider_value = sum(v['total_buy_value'] for v in insider_signals.values())
   504	            logger.info(f"Insider buying: ${total_insider_value:,.0f} across {len(insider_signals)} tickers")
   505	
   506	        # Top 20: combined technical + Reddit-buzz + insider-buying ranking of the
   507	        # qualified buy pool, with "why is this moving" links
   508	        top20 = []
   509	        if buy_signals:
   510	            logger.info("Building Top 20 shortlist...")
   511	            top20 = build_top20(buy_signals, reddit_mentions, insider_signals)
   512	            top20_path = Path("./data/daily_scans/top20_latest.json")
   513	            top20_path.parent.mkdir(parents=True, exist_ok=True)
   514	            with open(top20_path, 'w') as f:
   515	                # sanitize_nan: this feeds the dashboard's Market/Shortlist views
   516	                # directly — a stray NaN in a technical score would otherwise
   517	                # serialize as an invalid JSON token the browser can't parse.
   518	                json.dump(sanitize_nan({
   519	                    'generated': datetime.now().isoformat(),
   520	                    'top20': top20,
   521	                }), f, indent=2, default=str)
   522	            logger.info(f"Top 20 saved: {top20_path}")
   523	
   524	        # LLM agents (Fundamentals Auditor, Catalyst Sentiment) + free Congress Trades
   525	        # lookup — opt-in since the first two are real Claude API calls per ticker.
   526	        # Only run on the Top 20 shortlist, not the full buy_signals pool, to keep
   527	        # cost bounded. None of these ever modify src/screening/signal_engine.py;
   528	        # results are logged under data/fundamentals_audit/, data/catalyst_sentiment/,
   529	        # data/congress_trades/. Their output actually filters/ranks the final Top 5
   530	        # (see src/agents/shortlist.py) — it's not just informational anymore.
   531	        fundamentals_audits = {}
   532	        catalyst_sentiments = {}
   533	        congress_signals = {}
   534	        shortlist = []
   535	        if args.enable_llm_agents and top20:
   536	            top20_tickers = [s['ticker'] for s in top20]
   537	            logger.info(f"Running Fundamentals Auditor on {len(top20_tickers)} Top 20 tickers...")
   538	            audit_results = audit_candidates(top20_tickers)
   539	            fundamentals_audits = {r['ticker']: r['audit'] for r in audit_results if r['audited']}
   540	            logger.info(f"Running Catalyst Sentiment on {len(top20_tickers)} Top 20 tickers...")
   541	            sentiment_results = analyze_candidates(top20_tickers)
   542	            catalyst_sentiments = {r['ticker']: r['classification'] for r in sentiment_results if r['analyzed']}
   543	            logger.info(f"Running Congress Trades lookup on {len(top20_tickers)} Top 20 tickers...")
   544	            congress_signals = get_congress_signals(top20_tickers)
   545	            shortlist = build_shortlist(
   546	                top20, fundamentals_audits, catalyst_sentiments, congress_signals, size=5,
   547	            )
   548	            logger.info(
   549	                f"Top 5 shortlist: {[s['ticker'] for s in shortlist]} "
   550	                f"({sum(1 for s in shortlist if s['passed_filters'])} passed filters, "
   551	                f"{sum(1 for s in shortlist if not s['passed_filters'])} backfilled)"
   552	            )
   553	
   554	            # Persist alongside top20_latest.json so the local GUI dashboard can
   555	            # show the actual filtered Top 5 (today this only reaches the user
   556	            # via email otherwise).
   557	            shortlist_path = Path("./data/daily_scans/shortlist_latest.json")
   558	            shortlist_path.parent.mkdir(parents=True, exist_ok=True)
   559	            with open(shortlist_path, 'w') as f:
   560	                json.dump(sanitize_nan({
   561	                    'generated': datetime.now().isoformat(),
   562	                    'shortlist': shortlist,
   563	                    'fundamentals_audits': fundamentals_audits,
   564	                    'catalyst_sentiments': catalyst_sentiments,
   565	                    'congress_signals': congress_signals,
   566	                }), f, indent=2, default=str)
   567	            logger.info(f"Shortlist saved: {shortlist_path}")
   568	        elif args.enable_llm_agents:
   569	            logger.info("LLM agents skipped: no Top 20 shortlist was built this run.")
   570	
   571	        # Report
   572	        save_report(results, buy_signals, sell_signals, spy_analysis, breadth)
   573	
   574	        # Email notification (no-ops with a logged warning if EMAIL_* env vars aren't set)
   575	        from src.notifications.email_notifier import EmailNotifier
   576	        EmailNotifier().send_scan_report(
   577	            buy_signals, sell_signals, spy_analysis, breadth, top20=top20,
   578	            fundamentals_audits=fundamentals_audits, catalyst_sentiments=catalyst_sentiments,
   579	            congress_signals=congress_signals, shortlist=shortlist,
   580	        )
   581	
   582	        # Show FMP usage if enabled
   583	        if args.use_fmp:
   584	            usage = fundamentals_fetcher.get_api_usage()
   585	            logger.info("="*60)
   586	            logger.info("FMP API USAGE")
   587	            logger.info(f"Calls used: {usage['fmp_calls_used']}/{usage['fmp_daily_limit']}")
   588	            logger.info(f"Calls remaining: {usage['fmp_calls_remaining']}")
   589	            if 'bandwidth_used_mb' in usage:
   590	                logger.info(f"Bandwidth used: {usage['bandwidth_used_mb']:.1f} MB / {usage['bandwidth_limit_gb']:.1f} GB ({usage['bandwidth_pct_used']:.1f}%)")
   591	                logger.info(f"Earnings season: {'Yes' if usage['is_earnings_season'] else 'No'} (cache: {usage['cache_hours']}h)")
   592	            logger.info("="*60)
   593	
   594	        logger.info("="*60)
   595	        logger.info("SCAN COMPLETE")
   596	        logger.info(f"Time: {results['processing_time_seconds']/60:.1f} minutes")
   597	        logger.info(f"Actual TPS: {results['actual_tps']:.2f}")
   598	        logger.info(f"Buy signals: {len(buy_signals)}")
   599	        logger.info(f"Sell signals: {len(sell_signals)}")
   600	        logger.info("="*60)
   601	
   602	    except KeyboardInterrupt:
   603	        logger.info("\nInterrupted - progress saved")
   604	        sys.exit(0)
   605	    except Exception as e:
   606	        logger.error(f"Fatal error: {e}", exc_info=True)
   607	        sys.exit(1)
   608	
   609	
   610	if __name__ == '__main__':
   611	    main()
     1	"""Fetch and maintain the universe of all publicly traded US stocks.
     2	
     3	This module fetches the complete list of US-listed stocks from multiple sources
     4	and maintains a daily-updated universe for screening.
     5	"""
     6	
     7	import logging
     8	import pickle
     9	from datetime import datetime, timedelta
    10	from pathlib import Path
    11	from typing import Dict, List, Set
    12	
    13	import pandas as pd
    14	import requests
    15	
    16	logging.basicConfig(
    17	    level=logging.INFO,
    18	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    19	)
    20	logger = logging.getLogger(__name__)
    21	
    22	
    23	class USStockUniverseFetcher:
    24	    """Fetches and maintains the universe of all US-listed stocks."""
    25	
    26	    def __init__(self, cache_dir: str = "./data/cache"):
    27	        """Initialize the universe fetcher.
    28	
    29	        Args:
    30	            cache_dir: Directory for caching universe data
    31	        """
    32	        self.cache_dir = Path(cache_dir)
    33	        self.cache_dir.mkdir(parents=True, exist_ok=True)
    34	        self.cache_file = self.cache_dir / "us_stock_universe.pkl"
    35	        logger.info("USStockUniverseFetcher initialized")
    36	
    37	    def _fetch_from_fmp(self) -> List[Dict]:
    38	        """Fetch stock list from Financial Modeling Prep (free tier).
    39	
    40	        Note: This requires a free API key from financialmodelingprep.com
    41	        Falls back to other sources if not available.
    42	        """
    43	        # This is a fallback - will use other sources
    44	        return []
    45	
    46	    def _fetch_nasdaq_listed(self) -> pd.DataFrame:
    47	        """Fetch NASDAQ-listed stocks from NASDAQ FTP.
    48	
    49	        Returns:
    50	            DataFrame with NASDAQ stocks
    51	        """
    52	        try:
    53	            url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
    54	            df = pd.read_csv(url, sep='|')
    55	            df = df[df['Symbol'].notna()]
    56	            df = df[df['Test Issue'] == 'N']  # Exclude test issues
    57	            df = df[['Symbol', 'Security Name']].copy()
    58	            df.columns = ['symbol', 'name']
    59	            logger.info(f"Fetched {len(df)} NASDAQ stocks")
    60	            return df
    61	        except Exception as e:
    62	            logger.error(f"Error fetching NASDAQ stocks: {e}")
    63	            return pd.DataFrame()
    64	
    65	    def _fetch_other_listed(self) -> pd.DataFrame:
    66	        """Fetch non-NASDAQ listed stocks (NYSE, AMEX, etc).
    67	
    68	        Returns:
    69	            DataFrame with other exchange stocks
    70	        """
    71	        try:
    72	            url = "ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt"
    73	            df = pd.read_csv(url, sep='|')
    74	            df = df[df['ACT Symbol'].notna()]
    75	            df = df[df['Test Issue'] == 'N']  # Exclude test issues
    76	            df = df[['ACT Symbol', 'Security Name']].copy()
    77	            df.columns = ['symbol', 'name']
    78	            logger.info(f"Fetched {len(df)} NYSE/AMEX stocks")
    79	            return df
    80	        except Exception as e:
    81	            logger.error(f"Error fetching NYSE/AMEX stocks: {e}")
    82	            return pd.DataFrame()
    83	
    84	    def _filter_stocks(self, df: pd.DataFrame) -> pd.DataFrame:
    85	        """Filter out unwanted tickers.
    86	
    87	        Removes:
    88	        - Tickers with special characters ($, ^, ., etc.)
    89	        - Test symbols
    90	        - Warrants, rights, units
    91	        - Preferred shares
    92	        - ETFs and funds (heuristic)
    93	
    94	        Args:
    95	            df: DataFrame with symbols
    96	
    97	        Returns:
    98	            Filtered DataFrame
    99	        """
   100	        if df.empty:
   101	            return df
   102	
   103	        initial_count = len(df)
   104	
   105	        # Remove symbols with special characters
   106	        df = df[~df['symbol'].str.contains(r'[\$\^\.\-]', regex=True, na=False)]
   107	
   108	        # Remove common suffixes for warrants, rights, units
   109	        suffixes = ['W', 'R', 'U', 'WS', 'WT']
   110	        for suffix in suffixes:
   111	            df = df[~df['symbol'].str.endswith(suffix, na=False)]
   112	
   113	        # Remove preferred shares (usually have letters after symbol)
   114	        # Keep only symbols that are 1-5 uppercase letters
   115	        df = df[df['symbol'].str.match(r'^[A-Z]{1,5}$', na=False)]
   116	
   117	        # Remove obvious ETFs and funds (heuristic based on name)
   118	        etf_keywords = [
   119	            'ETF', 'FUND', 'TRUST', 'INDEX', 'PORTFOLIO',
   120	            'SHARES', 'NOTES', 'BOND', 'TREASURY'
   121	        ]
   122	        name_upper = df['name'].str.upper()
   123	        for keyword in etf_keywords:
   124	            df = df[~name_upper.str.contains(keyword, na=False)]
   125	
   126	        filtered_count = len(df)
   127	        logger.info(f"Filtered {initial_count - filtered_count} stocks, kept {filtered_count}")
   128	
   129	        return df
   130	
   131	    def fetch_universe(self, force_refresh: bool = False) -> List[str]:
   132	        """Fetch the complete universe of US-listed stocks.
   133	
   134	        Args:
   135	            force_refresh: Force refresh even if cached data is recent
   136	
   137	        Returns:
   138	            List of stock ticker symbols
   139	        """
   140	        # Check cache
   141	        if not force_refresh and self.cache_file.exists():
   142	            cache_age = datetime.now() - datetime.fromtimestamp(
   143	                self.cache_file.stat().st_mtime
   144	            )
   145	
   146	            if cache_age < timedelta(days=1):
   147	                logger.info("Loading universe from cache")
   148	                with open(self.cache_file, 'rb') as f:
   149	                    cached_data = pickle.load(f)
   150	                logger.info(f"Loaded {len(cached_data['symbols'])} symbols from cache")
   151	                return cached_data['symbols']
   152	
   153	        logger.info("Fetching fresh universe from exchanges...")
   154	
   155	        # Fetch from multiple sources
   156	        nasdaq_df = self._fetch_nasdaq_listed()
   157	        other_df = self._fetch_other_listed()
   158	
   159	        # Combine
   160	        all_stocks = pd.concat([nasdaq_df, other_df], ignore_index=True)
   161	
   162	        if all_stocks.empty:
   163	            logger.error("Failed to fetch any stocks")
   164	            return []
   165	
   166	        # Remove duplicates
   167	        all_stocks = all_stocks.drop_duplicates(subset=['symbol'])
   168	
   169	        # Filter unwanted symbols
   170	        all_stocks = self._filter_stocks(all_stocks)
   171	
   172	        # Sort by symbol
   173	        all_stocks = all_stocks.sort_values('symbol').reset_index(drop=True)
   174	
   175	        symbols = all_stocks['symbol'].tolist()
   176	
   177	        # Cache the results
   178	        cache_data = {
   179	            'symbols': symbols,
   180	            'fetch_date': datetime.now().isoformat(),
   181	            'count': len(symbols),
   182	            'metadata': {
   183	                'nasdaq_count': len(nasdaq_df),
   184	                'other_count': len(other_df),
   185	                'filtered_count': len(symbols)
   186	            }
   187	        }
   188	
   189	        with open(self.cache_file, 'wb') as f:
   190	            pickle.dump(cache_data, f)
   191	
   192	        logger.info(f"Cached {len(symbols)} symbols")
   193	        logger.info(f"Universe composition: {cache_data['metadata']}")
   194	
   195	        return symbols
   196	
   197	    def get_universe_info(self) -> Dict:
   198	        """Get information about the cached universe.
   199	
   200	        Returns:
   201	            Dict with universe metadata
   202	        """
   203	        if not self.cache_file.exists():
   204	            return {
   205	                'cached': False,
   206	                'count': 0
   207	            }
   208	
   209	        with open(self.cache_file, 'rb') as f:
   210	            cached_data = pickle.load(f)
   211	
   212	        cache_age = datetime.now() - datetime.fromtimestamp(
   213	            self.cache_file.stat().st_mtime
   214	        )
   215	
   216	        return {
   217	            'cached': True,
   218	            'count': cached_data['count'],
   219	            'fetch_date': cached_data['fetch_date'],
   220	            'cache_age_hours': cache_age.total_seconds() / 3600,
   221	            'metadata': cached_data.get('metadata', {})
   222	        }
     1	"""Reddit ticker-mention fetcher for cross-referencing stock buzz with screener signals.
     2	
     3	Uses PRAW (the official Reddit API wrapper) in read-only mode against PUBLIC subreddits.
     4	Never authenticates as a user account, posts, votes, or comments — read-only API access
     5	with an app-only OAuth token, same as any legitimate third-party Reddit client.
     6	"""
     7	
     8	import logging
     9	import os
    10	import re
    11	from datetime import datetime, timedelta, timezone
    12	from typing import Dict, List, Optional, Set
    13	
    14	logger = logging.getLogger(__name__)
    15	
    16	try:
    17	    import praw
    18	    PRAW_AVAILABLE = True
    19	except ImportError:
    20	    PRAW_AVAILABLE = False
    21	
    22	DEFAULT_SUBREDDITS = ['wallstreetbets', 'stocks', 'StockMarket', 'pennystocks']
    23	
    24	# Common short English words/abbreviations that are also valid ticker symbols.
    25	# A bare mention of these (no $ prefix) is almost always the word, not the stock.
    26	COMMON_WORD_BLOCKLIST = {
    27	    'A', 'I', 'ALL', 'ARE', 'FOR', 'ON', 'IT', 'GO', 'SO', 'OR', 'AT', 'BE',
    28	    'DD', 'CEO', 'IPO', 'USA', 'NOW', 'NEW', 'ONE', 'CAN', 'GOOD', 'REAL',
    29	    'PLAY', 'BIG', 'LOVE', 'NEXT', 'OPEN', 'HIGH', 'LOW', 'YOLO', 'EDIT',
    30	    'ANY', 'THE', 'AND', 'BUT', 'NOT', 'YOU', 'SEE', 'WAY', 'DAY', 'GET',
    31	    'FREE', 'HOLD', 'MOON', 'FUD', 'IMO', 'ATH', 'ATM', 'RIP', 'IRA', 'CEO',
    32	    'US', 'UK', 'EU', 'OK', 'PM', 'AM', 'ETF', 'SEC', 'FDA', 'FOMO',
    33	}
    34	
    35	CASHTAG_RE = re.compile(r'\$([A-Z]{1,5})\b')
    36	BARE_TICKER_RE = re.compile(r'\b([A-Z]{2,5})\b')
    37	
    38	
    39	class RedditSentimentFetcher:
    40	    """Read-only fetcher for stock ticker mention counts across public subreddits.
    41	
    42	    Environment Variables:
    43	        REDDIT_CLIENT_ID: From a Reddit "script" app at reddit.com/prefs/apps
    44	        REDDIT_CLIENT_SECRET: Same app
    45	        REDDIT_USER_AGENT: Optional, defaults to a descriptive string Reddit requires
    46	    """
    47	
    48	    def __init__(
    49	        self,
    50	        client_id: Optional[str] = None,
    51	        client_secret: Optional[str] = None,
    52	        user_agent: Optional[str] = None,
    53	    ):
    54	        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
    55	        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
    56	        self.user_agent = user_agent or os.getenv('REDDIT_USER_AGENT', 'stock-screener-bot/1.0 (read-only)')
    57	        self.reddit = None
    58	
    59	        if not PRAW_AVAILABLE:
    60	            logger.warning("praw not installed - Reddit sentiment disabled. pip install praw")
    61	            return
    62	
    63	        if not self.client_id or not self.client_secret:
    64	            logger.warning("Reddit credentials not configured (REDDIT_CLIENT_ID/SECRET) - Reddit sentiment disabled")
    65	            return
    66	
    67	        self.reddit = praw.Reddit(
    68	            client_id=self.client_id,
    69	            client_secret=self.client_secret,
    70	            user_agent=self.user_agent,
    71	        )
    72	        self.reddit.read_only = True
    73	
    74	    @property
    75	    def available(self) -> bool:
    76	        return self.reddit is not None
    77	
    78	    def fetch_mentions(
    79	        self,
    80	        valid_tickers: Set[str],
    81	        subreddits: Optional[List[str]] = None,
    82	        hours: int = 24,
    83	        post_limit: int = 150,
    84	    ) -> Dict[str, Dict]:
    85	        """Scan recent post titles/bodies in the given subreddits for ticker mentions.
    86	
    87	        Args:
    88	            valid_tickers: Known-good ticker symbols to match against (filters noise).
    89	            subreddits: Subreddit names without "r/". Defaults to DEFAULT_SUBREDDITS.
    90	            hours: Only count posts newer than this many hours.
    91	            post_limit: Max newest posts to scan per subreddit.
    92	
    93	        Returns:
    94	            Dict of ticker -> {'count': int, 'top_post_title': str, 'top_post_url': str},
    95	            where the "top post" is the highest-scoring (most-upvoted) post that
    96	            mentioned this ticker — used as the "why is this being talked about" link.
    97	        """
    98	        if not self.available:
    99	            return {}
   100	
   101	        subreddits = subreddits or DEFAULT_SUBREDDITS
   102	        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
   103	        mentions: Dict[str, Dict] = {}
   104	
   105	        for sub_name in subreddits:
   106	            try:
   107	                subreddit = self.reddit.subreddit(sub_name)
   108	                for post in subreddit.new(limit=post_limit):
   109	                    post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
   110	                    if post_time < cutoff:
   111	                        break  # .new() is newest-first, safe to stop scanning this subreddit
   112	
   113	                    text = f"{post.title} {post.selftext or ''}"
   114	                    for ticker in self._extract_tickers(text, valid_tickers):
   115	                        entry = mentions.setdefault(
   116	                            ticker, {'count': 0, 'top_post_title': None, 'top_post_url': None, '_top_post_score': -1}
   117	                        )
   118	                        entry['count'] += 1
   119	                        if post.score > entry['_top_post_score']:
   120	                            entry['_top_post_score'] = post.score
   121	                            entry['top_post_title'] = post.title
   122	                            entry['top_post_url'] = f"https://reddit.com{post.permalink}"
   123	
   124	            except Exception as e:
   125	                logger.warning(f"Reddit fetch failed for r/{sub_name}: {e}")
   126	
   127	        for entry in mentions.values():
   128	            entry.pop('_top_post_score', None)
   129	
   130	        return mentions
   131	
   132	    def _extract_tickers(self, text: str, valid_tickers: Set[str]) -> Set[str]:
   133	        """Extract likely ticker mentions from one post's text, deduped per-post."""
   134	        found = set()
   135	
   136	        # High confidence: $TICKER cashtags
   137	        for match in CASHTAG_RE.findall(text):
   138	            if match in valid_tickers:
   139	                found.add(match)
   140	
   141	        # Lower confidence: bare uppercase words — must be a real ticker AND not a common word
   142	        for match in BARE_TICKER_RE.findall(text):
   143	            if match in valid_tickers and match not in COMMON_WORD_BLOCKLIST:
   144	                found.add(match)
   145	
   146	        return found
     1	"""Reddit ticker-mention fetcher via ApeWisdom's free public API — no Reddit API
     2	app, no credentials, no setup at all.
     3	
     4	ApeWisdom (https://apewisdom.io) already scrapes r/wallstreetbets and other
     5	finance subreddits and publishes ranked ticker-mention counts as a public JSON
     6	API, updated continuously. This is the zero-setup alternative to
     7	src/data/reddit_sentiment.py (which needs a Reddit "script" app's client_id/
     8	secret) — same output shape, so it's a drop-in replacement at the call site.
     9	
    10	Trade-off: you don't control which subreddits/timeframe get scraped (that's
    11	ApeWisdom's own pipeline, not configurable per-request beyond their filter
    12	options), and there's no official uptime/rate-limit guarantee since it's a
    13	free community-run API, not something either of us operates.
    14	"""
    15	
    16	import logging
    17	from typing import Dict, Optional, Set
    18	
    19	import requests
    20	
    21	logger = logging.getLogger(__name__)
    22	
    23	BASE_URL = "https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}"
    24	MAX_PAGES = 8  # covers ApeWisdom's full ranked list (~700-800 tickers)
    25	REQUEST_TIMEOUT = 15
    26	
    27	
    28	class ApeWisdomSentimentFetcher:
    29	    """Free, no-credential Reddit mention-count fetcher via apewisdom.io."""
    30	
    31	    @property
    32	    def available(self) -> bool:
    33	        return True  # no credentials required
    34	
    35	    def fetch_mentions(
    36	        self,
    37	        valid_tickers: Set[str],
    38	        filter_name: str = "all-stocks",
    39	        max_pages: int = MAX_PAGES,
    40	    ) -> Dict[str, Dict]:
    41	        """Fetch current Reddit mention counts for tickers in valid_tickers.
    42	
    43	        Args:
    44	            valid_tickers: Known-good ticker symbols to match against (filters noise).
    45	            filter_name: ApeWisdom filter — "all-stocks", "wallstreetbets",
    46	                "stocks", "options", etc. (their supported subreddit filters).
    47	            max_pages: Safety cap on how many pages to walk.
    48	
    49	        Returns:
    50	            Dict of ticker -> {'count': int, 'top_post_title': None,
    51	            'top_post_url': "https://apewisdom.io/stocks/<ticker>/"} — same
    52	            shape as RedditSentimentFetcher.fetch_mentions() so callers don't
    53	            need to branch on which source is active. top_post_title is None
    54	            since ApeWisdom doesn't expose individual post links, only the
    55	            aggregate mention count.
    56	        """
    57	        mentions: Dict[str, Dict] = {}
    58	
    59	        for page in range(1, max_pages + 1):
    60	            url = BASE_URL.format(filter=filter_name, page=page)
    61	            try:
    62	                resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    63	                resp.raise_for_status()
    64	                data = resp.json()
    65	            except Exception as e:
    66	                logger.warning(f"ApeWisdom fetch failed on page {page}: {e}")
    67	                break
    68	
    69	            results = data.get('results') or []
    70	            if not results:
    71	                break
    72	
    73	            for row in results:
    74	                ticker = (row.get('ticker') or '').upper()
    75	                if ticker not in valid_tickers:
    76	                    continue
    77	                mentions[ticker] = {
    78	                    'count': row.get('mentions', 0),
    79	                    'top_post_title': None,
    80	                    'top_post_url': f"https://apewisdom.io/stocks/{ticker}/",
    81	                }
    82	
    83	            if page >= data.get('pages', page):
    84	                break
    85	
    86	        return mentions

exec
/bin/zsh -lc "nl -ba src/data/insider_trading.py | sed -n '1,235p'; nl -ba src/agents/fundamentals_auditor.py | sed -n '1,343p'; nl -ba src/agents/llm_client.py; nl -ba src/agents/catalyst_sentiment.py; nl -ba src/agents/congress_trades.py" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""SEC Form 4 insider-buying tracker.
     2	
     3	Uses SEC EDGAR's fully public, free API — no account, no API key, no OAuth app.
     4	SEC's only requirement is a descriptive User-Agent header identifying the requester
     5	(their fair-use policy, not a credential). Rate-limited client-side to stay well
     6	under SEC's 10 req/sec cap.
     7	
     8	Only "P" (open market or private purchase) transactions count as a bullish signal.
     9	Most Form 4 filings are routine compensation events (RSU vesting = "M", tax
    10	withholding = "F", grants = "A") that carry no real signal — those are filtered out.
    11	Insider selling ("S") is common for mundane reasons (diversification, taxes) and is
    12	far less predictive than buying, so it's tracked for context but not scored.
    13	"""
    14	
    15	import logging
    16	import os
    17	import pickle
    18	import time
    19	import xml.etree.ElementTree as ET
    20	from datetime import datetime, timedelta, timezone
    21	from pathlib import Path
    22	from typing import Dict, List, Optional
    23	
    24	import requests
    25	
    26	logger = logging.getLogger(__name__)
    27	
    28	# SEC's fair-access policy requires a descriptive User-Agent (name + contact), and
    29	# their bot-detection specifically rejects "AppName/1.0 (description)"-shaped strings
    30	# (looks like a generic bot signature) — a plain "name email" string works reliably.
    31	SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "stock-screener-personal-use contact@example.com")
    32	REQUEST_DELAY = 0.15  # stays well under SEC's 10 req/sec limit
    33	CIK_MAP_CACHE_DAYS = 7
    34	
    35	
    36	class InsiderTradingFetcher:
    37	    """Fetch and analyze SEC Form 4 insider-purchase filings for a ticker."""
    38	
    39	    def __init__(self, cache_dir: str = "./data/cache"):
    40	        self.cache_dir = Path(cache_dir)
    41	        self.cache_dir.mkdir(parents=True, exist_ok=True)
    42	        self.session = requests.Session()
    43	        self.session.headers.update({"User-Agent": SEC_USER_AGENT})
    44	        self._cik_map: Optional[Dict[str, str]] = None
    45	        self._last_request_time = 0.0
    46	
    47	    def _rate_limit(self):
    48	        elapsed = time.time() - self._last_request_time
    49	        if elapsed < REQUEST_DELAY:
    50	            time.sleep(REQUEST_DELAY - elapsed)
    51	        self._last_request_time = time.time()
    52	
    53	    def _get(self, url: str) -> Optional[requests.Response]:
    54	        self._rate_limit()
    55	        try:
    56	            resp = self.session.get(url, timeout=10)
    57	            resp.raise_for_status()
    58	            return resp
    59	        except requests.RequestException as e:
    60	            logger.debug(f"SEC request failed for {url}: {e}")
    61	            return None
    62	
    63	    def _load_cik_map(self) -> Dict[str, str]:
    64	        """Ticker -> zero-padded 10-digit CIK, cached to disk for a week."""
    65	        if self._cik_map is not None:
    66	            return self._cik_map
    67	
    68	        cache_file = self.cache_dir / "sec_ticker_cik_map.pkl"
    69	        if cache_file.exists():
    70	            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
    71	            if age < timedelta(days=CIK_MAP_CACHE_DAYS):
    72	                with open(cache_file, "rb") as f:
    73	                    self._cik_map = pickle.load(f)
    74	                    return self._cik_map
    75	
    76	        resp = self._get("https://www.sec.gov/files/company_tickers.json")
    77	        if resp is None:
    78	            self._cik_map = {}
    79	            return self._cik_map
    80	
    81	        data = resp.json()
    82	        cik_map = {
    83	            entry["ticker"].upper(): f"{entry['cik_str']:010d}"
    84	            for entry in data.values()
    85	        }
    86	        with open(cache_file, "wb") as f:
    87	            pickle.dump(cik_map, f)
    88	        self._cik_map = cik_map
    89	        return cik_map
    90	
    91	    def _get_cik(self, ticker: str) -> Optional[str]:
    92	        return self._load_cik_map().get(ticker.upper())
    93	
    94	    def _recent_form4_filing_urls(self, cik: str, days: int, limit: int) -> List[Dict]:
    95	        """Return [{accession, filing_date, index_url}] for recent Form 4s."""
    96	        url = (
    97	            "https://www.sec.gov/cgi-bin/browse-edgar"
    98	            f"?action=getcompany&CIK={cik}&type=4&dateb=&owner=include"
    99	            f"&count={limit}&output=atom"
   100	        )
   101	        resp = self._get(url)
   102	        if resp is None:
   103	            return []
   104	
   105	        try:
   106	            root = ET.fromstring(resp.content)
   107	        except ET.ParseError:
   108	            return []
   109	
   110	        ns = {"a": "http://www.w3.org/2005/Atom"}
   111	        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date()
   112	        filings = []
   113	        for entry in root.findall("a:entry", ns):
   114	            content = entry.find("a:content", ns)
   115	            if content is None:
   116	                continue
   117	            filing_date_el = content.find("a:filing-date", ns)
   118	            href_el = content.find("a:filing-href", ns)
   119	            if filing_date_el is None or href_el is None:
   120	                continue
   121	            try:
   122	                filing_date = datetime.strptime(filing_date_el.text, "%Y-%m-%d").date()
   123	            except (ValueError, TypeError):
   124	                continue
   125	            if filing_date < cutoff:
   126	                continue
   127	            filings.append({"filing_date": filing_date_el.text, "index_url": href_el.text})
   128	
   129	        return filings
   130	
   131	    def _find_xml_doc_url(self, index_url: str) -> Optional[str]:
   132	        """Use SEC's structured JSON directory index to find the Form 4 XML doc.
   133	
   134	        (The HTML directory listing page renders as a single minified line with
   135	        multiple hrefs per line, so naive HTML link-scraping picks up the wrong
   136	        link — the JSON index avoids that entirely.)
   137	        """
   138	        directory_url = index_url.rsplit("/", 1)[0] + "/"
   139	        resp = self._get(directory_url + "index.json")
   140	        if resp is None:
   141	            return None
   142	        try:
   143	            items = resp.json().get("directory", {}).get("item", [])
   144	        except ValueError:
   145	            return None
   146	
   147	        for item in items:
   148	            name = item.get("name", "")
   149	            if name.lower().endswith(".xml") and "form4" in name.lower():
   150	                return directory_url + name
   151	        return None
   152	
   153	    def _parse_form4_purchases(self, xml_text: str, filing_url: str) -> List[Dict]:
   154	        """Extract only open-market purchase ("P") transactions from a Form 4."""
   155	        try:
   156	            root = ET.fromstring(xml_text)
   157	        except ET.ParseError:
   158	            return []
   159	
   160	        owner_el = root.find("reportingOwner")
   161	        owner_name, is_officer, officer_title, is_director = None, False, None, False
   162	        if owner_el is not None:
   163	            name_el = owner_el.find("reportingOwnerId/rptOwnerName")
   164	            owner_name = name_el.text if name_el is not None else None
   165	            rel_el = owner_el.find("reportingOwnerRelationship")
   166	            if rel_el is not None:
   167	                is_officer = (rel_el.findtext("isOfficer") or "").lower() == "true"
   168	                officer_title = rel_el.findtext("officerTitle")
   169	                is_director = (rel_el.findtext("isDirector") or "").lower() == "true"
   170	
   171	        purchases = []
   172	        for txn in root.findall(".//nonDerivativeTransaction"):
   173	            code = txn.findtext("transactionCoding/transactionCode")
   174	            if code != "P":
   175	                continue
   176	
   177	            shares_text = txn.findtext("transactionAmounts/transactionShares/value")
   178	            price_text = txn.findtext("transactionAmounts/transactionPricePerShare/value")
   179	            date_text = txn.findtext("transactionDate/value")
   180	
   181	            try:
   182	                shares = float(shares_text) if shares_text else 0.0
   183	                price = float(price_text) if price_text else 0.0
   184	            except ValueError:
   185	                shares, price = 0.0, 0.0
   186	
   187	            purchases.append({
   188	                "owner_name": owner_name,
   189	                "is_officer": is_officer,
   190	                "officer_title": officer_title,
   191	                "is_director": is_director,
   192	                "shares": shares,
   193	                "price": price,
   194	                "value": shares * price,
   195	                "date": date_text,
   196	                "filing_url": filing_url,
   197	            })
   198	
   199	        return purchases
   200	
   201	    def get_insider_signal(self, ticker: str, days: int = 90, max_filings: int = 15) -> Dict:
   202	        """Aggregate recent open-market insider purchases for a ticker.
   203	
   204	        Returns a dict that's always safe to use even on total failure:
   205	            {'purchases_90d': int, 'total_buy_value': float, 'buyers': [...], 'top_buy_url': str|None}
   206	        """
   207	        empty = {"purchases_90d": 0, "total_buy_value": 0.0, "buyers": [], "top_buy_url": None}
   208	
   209	        cik = self._get_cik(ticker)
   210	        if not cik:
   211	            return empty
   212	
   213	        filings = self._recent_form4_filing_urls(cik, days=days, limit=max_filings)
   214	        all_purchases = []
   215	        for filing in filings:
   216	            xml_url = self._find_xml_doc_url(filing["index_url"])
   217	            if not xml_url:
   218	                continue
   219	            resp = self._get(xml_url)
   220	            if resp is None:
   221	                continue
   222	            all_purchases.extend(self._parse_form4_purchases(resp.text, filing["index_url"]))
   223	
   224	        if not all_purchases:
   225	            return empty
   226	
   227	        all_purchases.sort(key=lambda p: p["value"], reverse=True)
   228	        total_value = sum(p["value"] for p in all_purchases)
   229	
   230	        return {
   231	            "purchases_90d": len(all_purchases),
   232	            "total_buy_value": total_value,
   233	            "buyers": all_purchases[:5],
   234	            "top_buy_url": all_purchases[0]["filing_url"],
   235	        }
     1	"""Fundamentals Auditor — Part 3. For each Phase 2 candidate, pulls the company's
     2	most recent 10-Q or 10-K from SEC EDGAR, extracts the MD&A section, and asks Claude
     3	to flag qualitative red/green flags a pure numbers score would miss (margin
     4	compression explained away as "one-time," guidance cuts, earnings quality issues,
     5	etc.) — things visible in the prose but invisible to signal_engine.py's line-item math.
     6	
     7	Never modifies src/screening/signal_engine.py. Every flag is logged to
     8	data/fundamentals_audit/ for manual review and eventual backtesting once enough
     9	history accumulates (that wiring is walk_forward_backtest.py's job, not this module's).
    10	"""
    11	
    12	import json
    13	import logging
    14	import os
    15	import pickle
    16	import re
    17	import time
    18	import xml.etree.ElementTree as ET
    19	from datetime import datetime, timedelta
    20	from pathlib import Path
    21	from typing import Dict, List, Literal, Optional
    22	
    23	import requests
    24	from bs4 import BeautifulSoup
    25	from pydantic import BaseModel, Field
    26	
    27	from src.agents.llm_client import MODEL, get_client
    28	
    29	logger = logging.getLogger(__name__)
    30	
    31	# Same fair-access User-Agent convention as insider_trading.py — SEC's bot-detection
    32	# rejects "AppName/1.0 (description)"-shaped strings, so keep this a plain name+email.
    33	SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "stock-screener-personal-use contact@example.com")
    34	REQUEST_DELAY = 0.15
    35	CIK_MAP_CACHE_DAYS = 7
    36	MAX_FILING_CHARS = 60000  # ~15-20K tokens — controls cost regardless of model choice
    37	
    38	OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "fundamentals_audit"
    39	
    40	
    41	class FundamentalFlag(BaseModel):
    42	    flag: str = Field(description="Short label, e.g. 'Margin compression from one-time restructuring costs'")
    43	    category: Literal[
    44	        "margin", "revenue_quality", "guidance", "balance_sheet",
    45	        "cash_flow", "earnings_quality", "customer_concentration", "other",
    46	    ]
    47	    severity: Literal["minor", "moderate", "major"]
    48	    evidence: str = Field(description="The specific language or figure from the filing that supports this flag")
    49	
    50	
    51	class FundamentalsAudit(BaseModel):
    52	    red_flags: List[FundamentalFlag]
    53	    green_flags: List[FundamentalFlag]
    54	    overall_assessment: Literal["red_flags_outweigh", "green_flags_outweigh", "mixed", "no_notable_flags"]
    55	    summary: str = Field(description="2-3 sentence plain-English summary of the qualitative picture")
    56	
    57	
    58	AUDIT_SYSTEM_PROMPT = """You are a skeptical equity research analyst auditing a company's most \
    59	recent SEC filing (10-Q or 10-K). Your job is to catch qualitative issues a pure numbers-based \
    60	screen would miss, such as:
    61	- Margin compression explained away as "one-time" that isn't really one-time
    62	- Revenue growth propped up by a single large customer, acquisition, or one-time item
    63	- Guidance cuts, softened language, or hedged forward-looking statements
    64	- Earnings quality concerns (divergence between GAAP and non-GAAP, unusual adjustments)
    65	- Balance sheet or cash flow deterioration not obvious from headline numbers
    66	
    67	Also note genuine green flags: real margin expansion, clean guidance raises, strengthening \
    68	balance sheet, diversifying revenue.
    69	
    70	Base every flag ONLY on the filing text provided. If the filing is thin or you find nothing \
    71	notable, use overall_assessment='no_notable_flags' rather than inventing flags."""
    72	
    73	
    74	class FundamentalsAuditor:
    75	    """Pulls a ticker's most recent 10-Q/10-K from SEC EDGAR and audits it with Claude."""
    76	
    77	    def __init__(self, cache_dir: str = "./data/cache"):
    78	        self.cache_dir = Path(cache_dir)
    79	        self.cache_dir.mkdir(parents=True, exist_ok=True)
    80	        self.session = requests.Session()
    81	        self.session.headers.update({"User-Agent": SEC_USER_AGENT})
    82	        self._cik_map: Optional[Dict[str, str]] = None
    83	        self._last_request_time = 0.0
    84	        self.client = get_client()
    85	
    86	    @property
    87	    def available(self) -> bool:
    88	        return self.client is not None
    89	
    90	    def _rate_limit(self):
    91	        elapsed = time.time() - self._last_request_time
    92	        if elapsed < REQUEST_DELAY:
    93	            time.sleep(REQUEST_DELAY - elapsed)
    94	        self._last_request_time = time.time()
    95	
    96	    def _get(self, url: str) -> Optional[requests.Response]:
    97	        self._rate_limit()
    98	        try:
    99	            resp = self.session.get(url, timeout=15)
   100	            resp.raise_for_status()
   101	            return resp
   102	        except requests.RequestException as e:
   103	            logger.debug(f"SEC request failed for {url}: {e}")
   104	            return None
   105	
   106	    def _load_cik_map(self) -> Dict[str, str]:
   107	        if self._cik_map is not None:
   108	            return self._cik_map
   109	
   110	        cache_file = self.cache_dir / "sec_ticker_cik_map.pkl"
   111	        if cache_file.exists():
   112	            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
   113	            if age < timedelta(days=CIK_MAP_CACHE_DAYS):
   114	                with open(cache_file, "rb") as f:
   115	                    self._cik_map = pickle.load(f)
   116	                    return self._cik_map
   117	
   118	        resp = self._get("https://www.sec.gov/files/company_tickers.json")
   119	        if resp is None:
   120	            self._cik_map = {}
   121	            return self._cik_map
   122	
   123	        data = resp.json()
   124	        cik_map = {
   125	            entry["ticker"].upper(): f"{entry['cik_str']:010d}"
   126	            for entry in data.values()
   127	        }
   128	        with open(cache_file, "wb") as f:
   129	            pickle.dump(cik_map, f)
   130	        self._cik_map = cik_map
   131	        return cik_map
   132	
   133	    def _get_cik(self, ticker: str) -> Optional[str]:
   134	        return self._load_cik_map().get(ticker.upper())
   135	
   136	    def _recent_10q_10k_filings(self, cik: str, count: int = 40) -> List[Dict]:
   137	        """Recent 10-Q/10-K filings (form type, date, index page URL), newest first."""
   138	        url = (
   139	            "https://www.sec.gov/cgi-bin/browse-edgar"
   140	            f"?action=getcompany&CIK={cik}&type=10-&dateb=&owner=include"
   141	            f"&count={count}&output=atom"
   142	        )
   143	        resp = self._get(url)
   144	        if resp is None:
   145	            return []
   146	
   147	        try:
   148	            root = ET.fromstring(resp.content)
   149	        except ET.ParseError:
   150	            return []
   151	
   152	        ns = {"a": "http://www.w3.org/2005/Atom"}
   153	        filings = []
   154	        for entry in root.findall("a:entry", ns):
   155	            category = entry.find("a:category", ns)
   156	            form_type = category.get("term") if category is not None else None
   157	            if form_type not in ("10-Q", "10-K"):
   158	                continue
   159	            content = entry.find("a:content", ns)
   160	            if content is None:
   161	                continue
   162	            href_el = content.find("a:filing-href", ns)
   163	            date_el = content.find("a:filing-date", ns)
   164	            if href_el is None or date_el is None:
   165	                continue
   166	            filings.append({
   167	                "form_type": form_type,
   168	                "filing_date": date_el.text,
   169	                "index_url": href_el.text,
   170	            })
   171	        return filings
   172	
   173	    def _latest_filing_index_url(self, cik: str) -> Optional[Dict]:
   174	        """Most recent 10-Q or 10-K filing: form type, date, and index page URL."""
   175	        filings = self._recent_10q_10k_filings(cik, count=10)
   176	        return filings[0] if filings else None
   177	
   178	    def _filing_index_url_asof(self, cik: str, as_of_date) -> Optional[Dict]:
   179	        """Most recent 10-Q/10-K filed strictly BEFORE as_of_date — the filing that
   180	        would actually have been public knowledge as of a historical trade's entry
   181	        date. This is what makes a "backtest" of this agent honest rather than
   182	        look-ahead-biased; unlike news (no historical archive), SEC filings carry
   183	        real filing dates we can filter on."""
   184	        as_of_str = as_of_date.isoformat() if hasattr(as_of_date, "isoformat") else str(as_of_date)
   185	        filings = self._recent_10q_10k_filings(cik, count=40)
   186	        eligible = [f for f in filings if f["filing_date"] < as_of_str]
   187	        return eligible[0] if eligible else None
   188	
   189	    def _find_primary_doc_url(self, index_url: str) -> Optional[str]:
   190	        """Largest .htm in the filing directory is reliably the primary document —
   191	        exhibits and press-release attachments are consistently much smaller. Same
   192	        SEC structured JSON directory index trick as insider_trading.py uses for
   193	        Form 4 XML (the HTML listing renders as one unparseable line)."""
   194	        directory_url = index_url.rsplit("/", 1)[0] + "/"
   195	        resp = self._get(directory_url + "index.json")
   196	        if resp is None:
   197	            return None
   198	        try:
   199	            items = resp.json().get("directory", {}).get("item", [])
   200	        except ValueError:
   201	            return None
   202	
   203	        htm_items = [i for i in items if i.get("name", "").lower().endswith(".htm")]
   204	        if not htm_items:
   205	            return None
   206	        largest = max(htm_items, key=lambda i: int(i.get("size", 0) or 0))
   207	        return directory_url + largest["name"]
   208	
   209	    def _extract_filing_text(self, html: str) -> str:
   210	        """Strip HTML to plain text, then bias toward the MD&A section (the part of
   211	        a filing that actually contains qualitative narrative) if we can find it,
   212	        falling back to the start of the document body otherwise."""
   213	        soup = BeautifulSoup(html, "html.parser")
   214	        text = soup.get_text(separator="\n")
   215	        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
   216	        text = "\n".join(lines)
   217	
   218	        # The phrase "Management's Discussion and Analysis" appears once in the table
   219	        # of contents (short line, followed by a page number) and again as the real
   220	        # section header (followed by actual prose) — take the LAST match, since the
   221	        # TOC entry always comes first and the real section is what we want to audit.
   222	        lower = text.lower()
   223	        matches = [
   224	            m.start() for m in re.finditer(r"management.s discussion and analysis", lower)
   225	        ]
   226	        if matches:
   227	            text = text[matches[-1]:]
   228	
   229	        return text[:MAX_FILING_CHARS]
   230	
   231	    def _audit_filing(self, ticker: str, filing: Optional[Dict], not_found_reason: str) -> Dict:
   232	        """Shared fetch -> extract -> LLM-audit pipeline, given an already-resolved filing.
   233	
   234	        Returns a dict that's always safe to use even on total failure:
   235	            {'ticker', 'audited': bool, 'reason': str|None, 'filing_type': str|None,
   236	             'filing_date': str|None, 'audit': FundamentalsAudit-shaped dict|None}
   237	        """
   238	        empty = {
   239	            "ticker": ticker, "audited": False, "reason": None,
   240	            "filing_type": None, "filing_date": None, "audit": None,
   241	        }
   242	
   243	        if not self.available:
   244	            return {**empty, "reason": "ANTHROPIC_API_KEY not set"}
   245	
   246	        if not filing:
   247	            return {**empty, "reason": not_found_reason}
   248	
   249	        doc_url = self._find_primary_doc_url(filing["index_url"])
   250	        if not doc_url:
   251	            return {**empty, "reason": "could not locate primary filing document"}
   252	
   253	        resp = self._get(doc_url)
   254	        if resp is None:
   255	            return {**empty, "reason": "failed to fetch filing document"}
   256	
   257	        filing_text = self._extract_filing_text(resp.text)
   258	        if len(filing_text) < 500:
   259	            return {**empty, "reason": "extracted filing text too short to audit"}
   260	
   261	        try:
   262	            response = self.client.messages.parse(
   263	                model=MODEL,
   264	                max_tokens=8192,
   265	                system=AUDIT_SYSTEM_PROMPT,
   266	                messages=[{
   267	                    "role": "user",
   268	                    "content": (
   269	                        f"Ticker: {ticker}\n"
   270	                        f"Filing: {filing['form_type']} filed {filing['filing_date']}\n\n"
   271	                        f"--- FILING TEXT (MD&A-biased excerpt) ---\n{filing_text}"
   272	                    ),
   273	                }],
   274	                output_format=FundamentalsAudit,
   275	            )
   276	            audit_result = response.parsed_output
   277	        except Exception as e:
   278	            logger.warning(f"Fundamentals audit failed for {ticker}: {e}")
   279	            return {**empty, "reason": f"LLM call failed: {e}"}
   280	
   281	        return {
   282	            "ticker": ticker,
   283	            "audited": True,
   284	            "reason": None,
   285	            "filing_type": filing["form_type"],
   286	            "filing_date": filing["filing_date"],
   287	            "filing_url": doc_url,
   288	            "audit": audit_result.model_dump(),
   289	        }
   290	
   291	    def audit(self, ticker: str) -> Dict:
   292	        """Audit a ticker's MOST RECENT 10-Q/10-K — for live/current scans."""
   293	        if not self.available:
   294	            return self._audit_filing(ticker, None, "ANTHROPIC_API_KEY not set")
   295	        cik = self._get_cik(ticker)
   296	        if not cik:
   297	            return self._audit_filing(ticker, None, "ticker not found in SEC CIK map")
   298	        filing = self._latest_filing_index_url(cik)
   299	        return self._audit_filing(ticker, filing, "no recent 10-Q/10-K found")
   300	
   301	    def audit_asof(self, ticker: str, as_of_date) -> Dict:
   302	        """Audit the filing that was actually public AS OF a historical date — for
   303	        point-in-time backtesting (walk_forward_backtest.py's --audit-fundamentals).
   304	        as_of_date can be a date/datetime or an ISO date string."""
   305	        if not self.available:
   306	            return self._audit_filing(ticker, None, "ANTHROPIC_API_KEY not set")
   307	        cik = self._get_cik(ticker)
   308	        if not cik:
   309	            return self._audit_filing(ticker, None, "ticker not found in SEC CIK map")
   310	        filing = self._filing_index_url_asof(cik, as_of_date)
   311	        return self._audit_filing(ticker, filing, "no 10-Q/10-K filed before as_of_date")
   312	
   313	
   314	_SEVERITY_WEIGHT = {"minor": 1, "moderate": 2, "major": 3}
   315	
   316	
   317	def flags_to_score(audit: Dict) -> float:
   318	    """Collapse a FundamentalsAudit's red/green flags into one signed number, for
   319	    correlating against realized returns in the walk-forward backtest — the same
   320	    treatment as signal_engine.py's other numeric components (trend_score, etc).
   321	    Positive = green-flag-weighted, negative = red-flag-weighted, 0 = a wash or
   322	    no notable flags either way."""
   323	    green = sum(_SEVERITY_WEIGHT.get(f["severity"], 0) for f in (audit.get("green_flags") or []))
   324	    red = sum(_SEVERITY_WEIGHT.get(f["severity"], 0) for f in (audit.get("red_flags") or []))
   325	    return float(green - red)
   326	
   327	
   328	def audit_candidates(tickers: List[str]) -> List[Dict]:
   329	    """Audit a list of tickers, saving one timestamped run to data/fundamentals_audit/."""
   330	    auditor = FundamentalsAuditor()
   331	    results = []
   332	    for ticker in tickers:
   333	        logger.info(f"Fundamentals audit: {ticker}...")
   334	        results.append(auditor.audit(ticker))
   335	
   336	    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
   337	    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   338	    payload = {"generated": datetime.now().isoformat(), "results": results}
   339	
   340	    (OUTPUT_DIR / f"audit_{timestamp}.json").write_text(json.dumps(payload, indent=2))
   341	    (OUTPUT_DIR / "latest.json").write_text(json.dumps(payload, indent=2))
   342	
   343	    return results
     1	"""Shared Claude client setup for the LLM-powered agents.
     2	
     3	Mirrors the optional-integration pattern already used for Reddit (reddit_sentiment.py)
     4	and FMP (fmp_fetcher.py): missing credentials mean the feature no-ops with a logged
     5	warning, not a crash — a scan should never fail just because an optional agent's
     6	API key isn't configured.
     7	"""
     8	
     9	import logging
    10	import os
    11	
    12	from dotenv import load_dotenv
    13	
    14	load_dotenv()
    15	
    16	logger = logging.getLogger(__name__)
    17	
    18	# claude-opus-5 by default: this skill's guidance is to never silently downgrade
    19	# for cost — that's the user's call, not an automatic optimization. Confirmed with
    20	# the user (2026-08-04) for both the Fundamentals Auditor and Catalyst Sentiment agents.
    21	MODEL = "claude-opus-5"
    22	
    23	
    24	def get_client():
    25	    """Return an anthropic.Anthropic client, or None if ANTHROPIC_API_KEY isn't set.
    26	
    27	    Callers should treat None as "agent unavailable this run" and no-op, same as
    28	    RedditSentimentFetcher.available / EnhancedFundamentalsFetcher.fmp_available.
    29	    """
    30	    api_key = os.getenv("ANTHROPIC_API_KEY")
    31	    if not api_key:
    32	        logger.warning(
    33	            "ANTHROPIC_API_KEY not set — LLM agent disabled for this run. "
    34	            "Set it in .env to enable."
    35	        )
    36	        return None
    37	
    38	    import anthropic
    39	
    40	    return anthropic.Anthropic(api_key=api_key)
     1	"""News & Catalyst Sentiment — Part 4. For each Phase 2 candidate, reads recent news
     2	headlines (yfinance) and SEC Form 4 insider-buying data already available in the
     3	pipeline (insider_trading.py) and asks Claude to classify "why is this stock moving"
     4	into a catalyst type, scored numerically (-5 to +5) as a new scoring component — not
     5	just a text bullet.
     6	
     7	Never modifies src/screening/signal_engine.py. Every score is logged to
     8	data/catalyst_sentiment/ for manual review and eventual backtesting via
     9	walk_forward_backtest.py.
    10	
    11	Note on "press releases": Yahoo's news feed already aggregates company press releases
    12	alongside third-party articles, so no separate press-release-only source is wired in
    13	here — a genuinely distinct source would need a new paid API, out of scope for now.
    14	"""
    15	
    16	import json
    17	import logging
    18	from datetime import datetime
    19	from pathlib import Path
    20	from typing import Dict, List, Literal
    21	
    22	import yfinance as yf
    23	from pydantic import BaseModel, Field
    24	
    25	from src.agents.llm_client import MODEL, get_client
    26	from src.data.insider_trading import InsiderTradingFetcher
    27	
    28	logger = logging.getLogger(__name__)
    29	
    30	MAX_HEADLINES = 8
    31	OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "catalyst_sentiment"
    32	
    33	
    34	class CatalystClassification(BaseModel):
    35	    catalyst_type: Literal[
    36	        "earnings_beat", "earnings_miss", "guidance_raise", "guidance_cut",
    37	        "insider_buying", "insider_selling", "analyst_upgrade", "analyst_downgrade",
    38	        "merger_acquisition", "product_news", "regulatory", "sector_momentum",
    39	        "pure_momentum_no_catalyst", "other",
    40	    ]
    41	    catalyst_score: int = Field(
    42	        ge=-5, le=5,
    43	        description="-5 (strongly bearish catalyst) to +5 (strongly bullish catalyst); 0 if no real catalyst",
    44	    )
    45	    confidence: Literal["low", "medium", "high"]
    46	    summary: str = Field(description="1-2 sentence plain-English explanation of why the stock is moving")
    47	
    48	
    49	CATALYST_SYSTEM_PROMPT = """You classify WHY a stock is moving right now, using the recent \
    50	news headlines and SEC Form 4 insider-buying data provided. Pick the single best-fitting \
    51	catalyst_type and score how bullish or bearish that catalyst is on a -5 (strongly bearish) to \
    52	+5 (strongly bullish) scale, where 0 means no real catalyst (pure price/volume momentum with \
    53	no identifiable news driver).
    54	
    55	Be skeptical of hype-y headlines with no substance. If the headlines are generic or stale and \
    56	there's no insider buying signal, classify as 'pure_momentum_no_catalyst' with a score near 0 \
    57	rather than inventing a catalyst."""
    58	
    59	
    60	def _fetch_headlines(ticker: str, limit: int = MAX_HEADLINES) -> List[Dict]:
    61	    """Recent news headlines via yfinance. Never raises."""
    62	    try:
    63	        news = yf.Ticker(ticker).news or []
    64	    except Exception as e:
    65	        logger.debug(f"News fetch failed for {ticker}: {e}")
    66	        return []
    67	
    68	    headlines = []
    69	    for item in news[:limit]:
    70	        content = item.get("content", {})
    71	        title = content.get("title")
    72	        publisher = (content.get("provider") or {}).get("displayName")
    73	        pub_date = content.get("pubDate")
    74	        url = (content.get("canonicalUrl") or {}).get("url")
    75	        if title:
    76	            headlines.append({"title": title, "publisher": publisher, "pub_date": pub_date, "url": url})
    77	    return headlines
    78	
    79	
    80	class CatalystSentimentAgent:
    81	    """Classifies why a stock is moving using news + insider-buying data + Claude."""
    82	
    83	    def __init__(self):
    84	        self.client = get_client()
    85	        self.insider_fetcher = InsiderTradingFetcher()
    86	
    87	    @property
    88	    def available(self) -> bool:
    89	        return self.client is not None
    90	
    91	    def analyze(self, ticker: str) -> Dict:
    92	        """Returns a dict always safe to use even on total failure:
    93	            {'ticker', 'analyzed': bool, 'reason': str|None, 'headlines_used': int,
    94	             'insider_purchases_90d': int, 'classification': dict|None}
    95	        """
    96	        empty = {
    97	            "ticker": ticker, "analyzed": False, "reason": None,
    98	            "headlines_used": 0, "insider_purchases_90d": 0, "classification": None,
    99	        }
   100	
   101	        if not self.available:
   102	            return {**empty, "reason": "ANTHROPIC_API_KEY not set"}
   103	
   104	        headlines = _fetch_headlines(ticker)
   105	        insider_signal = self.insider_fetcher.get_insider_signal(ticker)
   106	
   107	        if not headlines and insider_signal["purchases_90d"] == 0:
   108	            return {**empty, "reason": "no news or insider activity found"}
   109	
   110	        headline_text = "\n".join(
   111	            f'- "{h["title"]}" ({h.get("publisher") or "unknown source"}, {h.get("pub_date") or "date unknown"})'
   112	            for h in headlines
   113	        ) or "(no recent headlines found)"
   114	
   115	        if insider_signal["purchases_90d"] > 0:
   116	            insider_text = (
   117	                f"{insider_signal['purchases_90d']} open-market insider purchase(s) in the last 90 days, "
   118	                f"totaling ${insider_signal['total_buy_value']:,.0f}."
   119	            )
   120	        else:
   121	            insider_text = "No open-market insider purchases in the last 90 days."
   122	
   123	        try:
   124	            response = self.client.messages.parse(
   125	                model=MODEL,
   126	                max_tokens=1024,
   127	                system=CATALYST_SYSTEM_PROMPT,
   128	                messages=[{
   129	                    "role": "user",
   130	                    "content": (
   131	                        f"Ticker: {ticker}\n\n"
   132	                        f"Recent headlines:\n{headline_text}\n\n"
   133	                        f"Insider buying (SEC Form 4): {insider_text}"
   134	                    ),
   135	                }],
   136	                output_format=CatalystClassification,
   137	            )
   138	            classification = response.parsed_output
   139	        except Exception as e:
   140	            logger.warning(f"Catalyst sentiment failed for {ticker}: {e}")
   141	            return {**empty, "reason": f"LLM call failed: {e}"}
   142	
   143	        return {
   144	            "ticker": ticker,
   145	            "analyzed": True,
   146	            "reason": None,
   147	            "headlines_used": len(headlines),
   148	            "insider_purchases_90d": insider_signal["purchases_90d"],
   149	            "classification": classification.model_dump(),
   150	        }
   151	
   152	
   153	def analyze_candidates(tickers: List[str]) -> List[Dict]:
   154	    """Analyze a list of tickers, saving one timestamped run to data/catalyst_sentiment/."""
   155	    agent = CatalystSentimentAgent()
   156	    results = []
   157	    for ticker in tickers:
   158	        logger.info(f"Catalyst sentiment: {ticker}...")
   159	        results.append(agent.analyze(ticker))
   160	
   161	    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
   162	    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   163	    payload = {"generated": datetime.now().isoformat(), "results": results}
   164	
   165	    (OUTPUT_DIR / f"sentiment_{timestamp}.json").write_text(json.dumps(payload, indent=2))
   166	    (OUTPUT_DIR / "latest.json").write_text(json.dumps(payload, indent=2))
   167	
   168	    return results
     1	"""Congress Trades agent — surfaces recent US House stock-trade disclosures for a ticker.
     2	
     3	Data source: TattooedHead/house-stock-watcher-data on GitHub — free, actively
     4	maintained (scrapes the official House Clerk PTR disclosure filings). This is
     5	House only: the old Senate/House Stock Watcher S3 buckets that used to serve
     6	Senate data are dead (AccessDenied, domains no longer resolve), and the only
     7	maintained Senate alternative found is Quiver Quant's paid API. Revisit if
     8	Senate coverage becomes worth paying for.
     9	
    10	No LLM call here — this is a deterministic lookup/aggregation over structured
    11	disclosure data, not a Claude-based classifier like the other two agents.
    12	Never modifies src/screening/signal_engine.py.
    13	"""
    14	
    15	import json
    16	import logging
    17	from datetime import datetime, timedelta
    18	from pathlib import Path
    19	from typing import Dict, List, Optional
    20	
    21	import requests
    22	
    23	logger = logging.getLogger(__name__)
    24	
    25	DATA_URL = "https://raw.githubusercontent.com/TattooedHead/house-stock-watcher-data/main/data/all_transactions.json"
    26	CACHE_PATH = Path("./data/congress_trades_cache/all_transactions.json")
    27	CACHE_MAX_AGE_HOURS = 20
    28	LOOKBACK_DAYS = 45  # STOCK Act filing deadline — catches trades recently made public
    29	
    30	
    31	def _load_all_transactions() -> List[Dict]:
    32	    """Fetch the full House disclosure dataset, cached locally for CACHE_MAX_AGE_HOURS."""
    33	    if CACHE_PATH.exists():
    34	        age_hours = (datetime.now().timestamp() - CACHE_PATH.stat().st_mtime) / 3600
    35	        if age_hours < CACHE_MAX_AGE_HOURS:
    36	            try:
    37	                with open(CACHE_PATH) as f:
    38	                    return json.load(f)
    39	            except (json.JSONDecodeError, OSError):
    40	                pass
    41	
    42	    try:
    43	        resp = requests.get(DATA_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    44	        resp.raise_for_status()
    45	        transactions = resp.json()
    46	    except Exception as e:
    47	        logger.warning(f"Congress trades fetch failed: {e}")
    48	        if CACHE_PATH.exists():
    49	            with open(CACHE_PATH) as f:
    50	                return json.load(f)
    51	        return []
    52	
    53	    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    54	    with open(CACHE_PATH, 'w') as f:
    55	        json.dump(transactions, f)
    56	    return transactions
    57	
    58	
    59	def _parse_date(s: str) -> Optional[datetime]:
    60	    try:
    61	        return datetime.strptime(s, "%m/%d/%Y")
    62	    except (ValueError, TypeError):
    63	        return None
    64	
    65	
    66	def get_congress_signal(
    67	    ticker: str,
    68	    all_transactions: Optional[List[Dict]] = None,
    69	    as_of: Optional[datetime] = None,
    70	) -> Dict:
    71	    """Aggregate House trade disclosures made public in the LOOKBACK_DAYS before `as_of`
    72	    (defaults to now) for one ticker.
    73	
    74	    score is a dollar-weighted net direction capped to +-5 (same scale as
    75	    Catalyst Sentiment): positive = net buying by members of Congress,
    76	    negative = net selling.
    77	
    78	    Passing `as_of` makes this genuinely point-in-time (for backtesting): only
    79	    disclosures with disclosure_date before `as_of` are considered, so it reflects
    80	    what would have actually been public knowledge at that historical moment —
    81	    unlike Catalyst Sentiment, this data source does have a real historical archive.
    82	    """
    83	    if all_transactions is None:
    84	        all_transactions = _load_all_transactions()
    85	
    86	    reference = as_of or datetime.now()
    87	    cutoff = reference - timedelta(days=LOOKBACK_DAYS)
    88	    matches = []
    89	    for t in all_transactions:
    90	        if t.get('ticker') != ticker:
    91	            continue
    92	        d = _parse_date(t.get('disclosure_date', ''))
    93	        if d is None or d < cutoff or d > reference:
    94	            continue
    95	        matches.append(t)
    96	
    97	    if not matches:
    98	        return {
    99	            'ticker': ticker, 'has_data': False,
   100	            'num_purchases': 0, 'num_sales': 0, 'net_amount_mid': 0,
   101	            'politicians': [], 'score': 0.0,
   102	            'summary': 'No House trade disclosures in the last 45 days.',
   103	        }
   104	
   105	    purchases = [t for t in matches if t.get('type') == 'Purchase']
   106	    sales = [t for t in matches if t.get('type') == 'Sale']
   107	    buy_value = sum(t.get('amount_mid', 0) for t in purchases)
   108	    sell_value = sum(t.get('amount_mid', 0) for t in sales)
   109	    net = buy_value - sell_value
   110	    politicians = sorted({t['representative'] for t in matches if t.get('representative')})
   111	
   112	    if net > 0:
   113	        score = min(5.0, 1.0 + net / 50000)
   114	    elif net < 0:
   115	        score = max(-5.0, -1.0 + net / 50000)
   116	    else:
   117	        score = 0.0
   118	
   119	    direction = "net buying" if net > 0 else ("net selling" if net < 0 else "mixed, net-flat")
   120	    who = ', '.join(politicians[:3]) + ('...' if len(politicians) > 3 else '')
   121	    summary = f"{len(matches)} House disclosure(s) in last {LOOKBACK_DAYS}d ({direction}): {who}"
   122	
   123	    return {
   124	        'ticker': ticker, 'has_data': True,
   125	        'num_purchases': len(purchases), 'num_sales': len(sales),
   126	        'net_amount_mid': net, 'politicians': politicians,
   127	        'score': round(score, 2), 'summary': summary,
   128	    }
   129	
   130	
   131	def get_signals_for_candidates(tickers: List[str]) -> Dict[str, Dict]:
   132	    """Batch congress-trade lookup for a candidate list, logged like the other agents."""
   133	    all_transactions = _load_all_transactions()
   134	    if not all_transactions:
   135	        logger.warning("Congress trades data unavailable this run — skipping.")
   136	        return {}
   137	
   138	    signals = {t: get_congress_signal(t, all_transactions) for t in tickers}
   139	
   140	    out_dir = Path("./data/congress_trades")
   141	    out_dir.mkdir(parents=True, exist_ok=True)
   142	    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
   143	    payload = {
   144	        'generated': datetime.now().isoformat(),
   145	        'source': 'house-stock-watcher-data (House only, no free Senate source available)',
   146	        'signals': signals,
   147	    }
   148	    with open(out_dir / f"signals_{ts}.json", 'w') as f:
   149	        json.dump(payload, f, indent=2, default=str)
   150	    with open(out_dir / "latest.json", 'w') as f:
   151	        json.dump(payload, f, indent=2, default=str)
   152	
   153	    return signals

exec
/bin/zsh -lc "rg -n \" / |/\\s*\\(|pct_change|iloc\\[-|mean\\(|std\\(|polyfit|corr\\(|argmax|idxmax|dropna\" src/screening src/analysis scripts | sed -n '1,360p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
scripts/backtest_top3.py:70:            current_price = asof_data['Close'].iloc[-1]
scripts/backtest_top3.py:82:                today_price = hist['Close'].iloc[-1]
scripts/backtest_top3.py:85:                signal['return_pct'] = (today_price - current_price) / current_price * 100
scripts/backtest_top3.py:107:    per_stock = args.investment / len(top3)
scripts/backtest_top3.py:111:        shares = per_stock / s['entry_price_asof']
scripts/backtest_top3.py:150:        'total_return_pct': (total_profit / args.investment * 100) if args.investment else 0.0,
src/screening/quant_engine.py:78:            self.spy_price = spy_hist['Close'].iloc[-1]
src/screening/quant_engine.py:105:            current_price = price_data['Close'].iloc[-1]
src/analysis/position_manager.py:89:            fundamental_file = self.fundamentals_dir / f"{ticker}_fundamentals.json"
src/analysis/position_manager.py:149:        gain_pct = ((current_price - entry_price) / entry_price) * 100
src/analysis/position_manager.py:179:            recent_low = price_data['Low'].iloc[-10:].min()
src/analysis/position_manager.py:189:            history = price_data['Close'].iloc[-180:]
src/analysis/position_manager.py:225:                # Formula: entry * (1 + min(gain_pct - 3, gain_pct * 0.5) / 100)
src/analysis/position_manager.py:233:                profit_based_stop = entry_price * (1 + locked_profit_pct / 100)
src/analysis/position_manager.py:242:                    sma_buffer_pct = max(0.5, 1.5 - (gain_pct / 50))  # Linear from 1.5% to 0.5%
src/analysis/position_manager.py:243:                    sma_based_stop = sma_50 * (1 - sma_buffer_pct / 100)
src/analysis/position_manager.py:249:                    sma_buffer_pct = ((sma_50 - result['recommended_stop']) / sma_50) * 100
src/analysis/position_manager.py:255:                locked_profit = ((result['recommended_stop'] / entry_price) - 1) * 100
src/analysis/position_manager.py:287:                    rationale_lines.append(f"    • Sell {partial_exit_pct:.0f}% at ${current_price:.2f} (lock in ${(current_price - entry_price) * partial_exit_pct / 100:.2f}/share)")
src/analysis/position_manager.py:376:        avg_gain = sum(a['current_gain_pct'] for a in analyses) / total_positions if total_positions > 0 else 0
scripts/run_quant_engine.py:63:        filepath = Path(output_dir) / filename
scripts/run_catalyst_sentiment.py:23:TOP20_PATH = Path(__file__).parent.parent / "data" / "daily_scans" / "top20_latest.json"
scripts/backtest_top3_monte_carlo.py:73:            current_price = asof_data['Close'].iloc[-1]
scripts/backtest_top3_monte_carlo.py:84:                today_price = hist['Close'].iloc[-1]
scripts/backtest_top3_monte_carlo.py:87:                signal['return_pct'] = (today_price - current_price) / current_price * 100
scripts/backtest_top3_monte_carlo.py:104:        mean_s, mean_r = sum(scores) / n, sum(returns) / n
scripts/backtest_top3_monte_carlo.py:108:        corr = cov / (std_s * std_r) if std_s > 0 and std_r > 0 else 0.0
scripts/backtest_top3_monte_carlo.py:132:        per_stock = args.investment / len(top3)
scripts/backtest_top3_monte_carlo.py:134:            (per_stock / s['entry_price_asof']) * s['current_price_today'] for s in top3
scripts/backtest_top3_monte_carlo.py:141:            'profit_pct': profit / args.investment * 100,
scripts/backtest_top3_monte_carlo.py:155:    avg_profit = sum(profits) / len(profits)
scripts/backtest_top3_monte_carlo.py:156:    avg_pct = sum(profit_pcts) / len(profit_pcts)
scripts/backtest_top3_monte_carlo.py:177:            win_rate=wins / len(results) * 100, avg_profit=avg_profit, avg_pct=avg_pct,
src/screening/screener.py:79:            score += 40 - ((pe_ratio - 15) / 15) * 20
src/screening/screener.py:82:            score += 20 - ((pe_ratio - 30) / 20) * 20
src/screening/screener.py:95:            score += 30 - ((pb_ratio - 1.5) / 1.5) * 20
src/screening/screener.py:98:            score += 10 - ((pb_ratio - 3.0) / 2.0) * 10
src/screening/screener.py:111:            score += (fcf_yield / 5.0) * 20
src/screening/screener.py:124:            score += 10 - ((debt_equity - 50) / 50) * 5
src/screening/screener.py:127:            score += 5 - ((debt_equity - 100) / 100) * 5
src/screening/screener.py:194:                support_levels.append(float(sma_50.iloc[-1]))
src/screening/screener.py:195:                logger.debug(f"Added SMA-50: {sma_50.iloc[-1]:.2f}")
src/screening/screener.py:201:                support_levels.append(float(sma_200.iloc[-1]))
src/screening/screener.py:202:                logger.debug(f"Added SMA-200: {sma_200.iloc[-1]:.2f}")
src/screening/screener.py:206:            recent_low = close_prices.iloc[-90:].min()
src/screening/screener.py:212:            week_52_low = close_prices.iloc[-252:].min()
src/screening/screener.py:224:                if abs(level - consolidated[-1]) / consolidated[-1] > 0.005:
src/screening/screener.py:291:            distance_pct = ((current_price - nearest_support) / nearest_support) * 100
src/screening/screener.py:299:                score += 40 - ((distance_pct - 1.0) / 2.0) * 15
src/screening/screener.py:303:                score += 25 - ((distance_pct - 3.0) / 2.0) * 10
src/screening/screener.py:307:                score += 15 - ((distance_pct - 5.0) / 5.0) * 15
src/screening/screener.py:324:            score += 30 - ((rsi - 30) / 10) * 10
src/screening/screener.py:328:            score += 20 - ((rsi - 40) / 10) * 10
src/screening/screener.py:345:            if abs(current_price - s) / current_price <= 0.03
src/screening/screener.py:356:                recent_high = price_history['High'].iloc[-90:].max()
src/screening/screener.py:357:                recent_low = price_history['Low'].iloc[-90:].min()
src/screening/screener.py:361:                    position = (current_price - recent_low) / price_range
src/screening/screener.py:467:                    rsi = float(rsi_series.iloc[-1])
src/screening/screener.py:472:                current_volume = price_history['Volume'].iloc[-1]
src/screening/phase_indicators.py:30:    return prices.rolling(window=period, min_periods=period).mean()
src/screening/phase_indicators.py:46:    recent = series.iloc[-periods:].dropna()
src/screening/phase_indicators.py:54:    if np.std(x) == 0:
src/screening/phase_indicators.py:57:    slope = np.polyfit(x, y, 1)[0]
src/screening/phase_indicators.py:60:    avg_price = np.mean(y)
src/screening/phase_indicators.py:64:    slope_pct = (slope / avg_price) * 100
src/screening/phase_indicators.py:73:    RS = (Stock Price / SPY Price) * 100
src/screening/phase_indicators.py:117:    rs = (stock_prices / spy_aligned) * 100
src/screening/phase_indicators.py:161:    volatility = prices.rolling(window=window).std()
src/screening/phase_indicators.py:163:    if len(volatility.dropna()) < 2:
src/screening/phase_indicators.py:170:    current_vol = volatility.iloc[-1]
src/screening/phase_indicators.py:171:    avg_vol = volatility.iloc[-window*2:-window].mean()
src/screening/phase_indicators.py:174:    contraction_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
src/screening/phase_indicators.py:202:    recent_high = prices.iloc[-window:].max()
src/screening/phase_indicators.py:219:    pivot = prices.iloc[-window:].max()
src/screening/phase_indicators.py:231:        Ratio (current / average)
src/screening/phase_indicators.py:236:    current = volumes.iloc[-1]
src/screening/phase_indicators.py:237:    avg = volumes.iloc[-period-1:-1].mean()
src/screening/phase_indicators.py:242:    return current / avg
src/screening/phase_indicators.py:258:    return ((price - sma) / sma) * 100
src/screening/phase_indicators.py:264:    Phase 1: Base Building / Compression
src/screening/phase_indicators.py:271:    Phase 2: Uptrend / Breakout
src/screening/phase_indicators.py:278:    Phase 3: Distribution / Top
src/screening/phase_indicators.py:321:    sma_50_val = sma_50.iloc[-1]
src/screening/phase_indicators.py:322:    sma_150_val = sma_150.iloc[-1] if not sma_150.isna().all() else 0
src/screening/phase_indicators.py:323:    sma_200_val = sma_200.iloc[-1]
src/screening/phase_indicators.py:327:        week_52_high = high.iloc[-252:].max()
src/screening/phase_indicators.py:328:        week_52_low = low.iloc[-252:].min()
src/screening/phase_indicators.py:342:        avg_volume = volume.iloc[-20:].mean()
src/screening/phase_indicators.py:343:        current_volume = volume.iloc[-1]
src/screening/phase_indicators.py:344:        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
src/screening/phase_indicators.py:369:    # Phase 2: Uptrend / Breakout
src/screening/phase_indicators.py:389:    # Phase 3: Distribution / Top
src/screening/phase_indicators.py:504:        sma_200_1mo_ago = sma_200_series.iloc[-20]
src/screening/phase_indicators.py:505:        sma_200_now = sma_200_series.iloc[-1]
src/screening/phase_indicators.py:529:        distance_from_52w_low = ((current_price - week_52_low) / week_52_low) * 100
src/screening/phase_indicators.py:543:        distance_from_52w_high = ((week_52_high - current_price) / week_52_high) * 100
src/screening/phase_indicators.py:562:    template_score = int((passed_count / 8) * 100)
src/screening/phase_indicators.py:634:        recovery_pct = ((future_high - low_price) / low_price * 100) if low_price > 0 else 0
src/screening/phase_indicators.py:692:                drawdown_pct = ((peak['price'] - trough['price']) / peak['price']) * 100
src/screening/phase_indicators.py:699:                    avg_volume_before = volume.iloc[:contraction_start_idx].tail(20).mean()
src/screening/phase_indicators.py:700:                    avg_volume_during = volume.iloc[contraction_start_idx:contraction_end_idx].mean()
src/screening/phase_indicators.py:701:                    volume_ratio = avg_volume_during / avg_volume_before if avg_volume_before > 0 else 1.0
src/screening/phase_indicators.py:735:            contraction_quality = (contracting_count / (len(contractions) - 1)) * 100
src/screening/phase_indicators.py:742:        volume_quality = (drying_volume_count / len(contractions)) * 100
src/screening/phase_indicators.py:750:            base_length_weeks = base_length_days / 7
src/screening/phase_indicators.py:758:        avg_volume_20d = volume.iloc[-21:-1].mean()
src/screening/phase_indicators.py:759:        current_volume = volume.iloc[-1]
src/screening/phase_indicators.py:760:        breakout_volume_ratio = current_volume / avg_volume_20d if avg_volume_20d > 0 else 1.0
src/screening/phase_indicators.py:766:    distance_from_52w_high = ((week_52_high - current_price) / week_52_high * 100) if week_52_high > 0 else 100
src/screening/phase_indicators.py:775:        contraction_score = min(20, (len(contractions) / max_contractions) * 20)
src/screening/phase_indicators.py:780:    vcp_quality += (contraction_quality / 100) * 30
src/screening/phase_indicators.py:781:    quality_factors.append(f"{contraction_quality:.0f}% tightening ({(contraction_quality / 100) * 30:.0f} pts)")
src/screening/phase_indicators.py:784:    vcp_quality += (volume_quality / 100) * 20
src/screening/phase_indicators.py:785:    quality_factors.append(f"{volume_quality:.0f}% volume drying ({(volume_quality / 100) * 20:.0f} pts)")
src/screening/phase_indicators.py:794:        high_proximity_score = max(0, 20 - (distance_from_52w_high / 25 * 20))
src/screening/phase_indicators.py:875:        avg_volume_20d = volume.iloc[-21:-1].mean()
src/screening/phase_indicators.py:876:        current_volume = volume.iloc[-1]
src/screening/phase_indicators.py:877:        volume_ratio = current_volume / avg_volume_20d if avg_volume_20d > 0 else 1.0
src/screening/phase_indicators.py:905:        if close.iloc[-2] < sma_50 < current_price:
scripts/fetch_momentum_status.py:2:"""Classifies each ticker into a momentum "status" — hot / stable / basing /
scripts/fetch_momentum_status.py:34:HISTORY_PATH = Path(__file__).parent.parent / "data" / "momentum_status" / "history.json"
scripts/fetch_momentum_status.py:39:    'basing': 'Basing / cooling',
scripts/fetch_momentum_status.py:59:    return 'basing'  # phase 0 / insufficient data — treat as neutral, not a buy
scripts/fetch_momentum_status.py:120:            current_price = float(price_data['Close'].iloc[-1])
src/screening/top20_ranker.py:82:        insider_boost = math.log1p(buy_value / 1000) * INSIDER_BUY_WEIGHT
src/screening/indicators.py:39:        >>> print(rsi.iloc[-1])
src/screening/indicators.py:53:    avg_gains = gains.ewm(span=period, min_periods=period, adjust=False).mean()
src/screening/indicators.py:54:    avg_losses = losses.ewm(span=period, min_periods=period, adjust=False).mean()
src/screening/indicators.py:57:    rs = avg_gains / avg_losses.replace(0, np.nan)
src/screening/indicators.py:60:    rsi = 100 - (100 / (1 + rs))
src/screening/indicators.py:80:        >>> print(sma.iloc[-1])
src/screening/indicators.py:86:    return prices.rolling(window=period, min_periods=period).mean()
src/screening/indicators.py:105:        >>> print(ema.iloc[-1])
src/screening/indicators.py:111:    return prices.ewm(span=period, min_periods=period, adjust=False).mean()
src/screening/indicators.py:184:    avg_volume = volumes.iloc[-20:].mean()
src/screening/indicators.py:255:        >>> print(f"Middle: {middle.iloc[-1]:.2f}")
src/screening/indicators.py:265:    rolling_std = prices.rolling(window=period, min_periods=period).std()
src/screening/indicators.py:297:        >>> print(f"MACD: {macd.iloc[-1]:.2f}")
src/screening/indicators.py:356:    atr = true_range.rolling(window=period, min_periods=period).mean()
scripts/run_fundamentals_auditor.py:23:TOP20_PATH = Path(__file__).parent.parent / "data" / "daily_scans" / "top20_latest.json"
src/screening/benchmark.py:103:    phase_1_pct = (phase_counts[1] / total * 100) if total > 0 else 0
src/screening/benchmark.py:104:    phase_2_pct = (phase_counts[2] / total * 100) if total > 0 else 0
src/screening/benchmark.py:105:    phase_3_pct = (phase_counts[3] / total * 100) if total > 0 else 0
src/screening/benchmark.py:106:    phase_4_pct = (phase_counts[4] / total * 100) if total > 0 else 0
src/screening/benchmark.py:153:    # Weak Risk-On / Mixed
src/screening/benchmark.py:155:        return 'RISK-ON (Weak) / Mixed'
src/screening/benchmark.py:161:    # Transitional / Uncertain
src/screening/benchmark.py:163:        return 'TRANSITIONAL / Uncertain'
scripts/compare_old_vs_new_weights.py:33:    'trend_score': 40 / 35,
scripts/compare_old_vs_new_weights.py:34:    'fundamental_score': 40 / 35,
scripts/compare_old_vs_new_weights.py:35:    'entry_score': 1 / 5,
scripts/compare_old_vs_new_weights.py:36:    'rr_score': 15 / 10,
scripts/compare_old_vs_new_weights.py:37:    'volume_score': 10 / 5,
scripts/compare_old_vs_new_weights.py:46:    mean_x, mean_y = sum(xs) / n, sum(ys) / n
scripts/compare_old_vs_new_weights.py:50:    return cov / (std_x * std_y) if std_x > 0 and std_y > 0 else None
scripts/compare_old_vs_new_weights.py:81:            current_price = asof_data['Close'].iloc[-1]
scripts/compare_old_vs_new_weights.py:98:            today_price = hist['Close'].iloc[-1]
scripts/compare_old_vs_new_weights.py:99:            return_pct = (today_price - current_price) / current_price * 100
scripts/compare_old_vs_new_weights.py:127:        per_stock = args.investment / len(top3)
scripts/compare_old_vs_new_weights.py:128:        value = sum((per_stock / r['entry_price']) * r['today_price'] for r in top3)
src/screening/batch_processor.py:59:        self.progress_file = self.results_dir / "batch_progress.pkl"
src/screening/batch_processor.py:124:            self.spy_price = spy_hist['Close'].iloc[-1]
src/screening/batch_processor.py:185:            current_price = price_data['Close'].iloc[-1]
src/screening/batch_processor.py:193:                avg_volume = price_data['Volume'].iloc[-20:].mean()
src/screening/batch_processor.py:261:        logger.info(f"Estimated time: {len(tickers) * self.rate_limit_delay / 3600:.1f} hours")
src/screening/batch_processor.py:292:                rate = i / elapsed if elapsed > 0 else 0
src/screening/batch_processor.py:294:                eta_seconds = remaining / rate if rate > 0 else 0
src/screening/optimized_batch_processor.py:66:        # Effective TPS = max_workers / rate_limit_delay
src/screening/optimized_batch_processor.py:67:        effective_tps = max_workers / rate_limit_delay
src/screening/optimized_batch_processor.py:71:        self.progress_file = self.results_dir / "batch_progress.pkl"
src/screening/optimized_batch_processor.py:122:                'error_rate': self.error_count / max(self.total_requests, 1)
src/screening/optimized_batch_processor.py:175:            self.spy_price = spy_hist['Close'].iloc[-1]
src/screening/optimized_batch_processor.py:235:            current_price = price_data['Close'].iloc[-1]
src/screening/optimized_batch_processor.py:243:                drawdown = (closes - running_max) / running_max
src/screening/optimized_batch_processor.py:261:                avg_volume = price_data['Volume'].iloc[-20:].mean()
src/screening/optimized_batch_processor.py:379:        logger.info(f"Rate: ~{self.max_workers / self.rate_limit_delay:.1f} TPS")
src/screening/optimized_batch_processor.py:380:        logger.info(f"Est. time: {len(tickers) * self.rate_limit_delay / self.max_workers / 3600:.1f} hours")
src/screening/optimized_batch_processor.py:441:                        rate = completed / elapsed if elapsed > 0 else 0
src/screening/optimized_batch_processor.py:443:                        eta_seconds = remaining_count / rate if rate > 0 else 0
src/screening/optimized_batch_processor.py:446:                        error_rate = self.error_count / max(self.total_requests, 1) * 100
src/screening/optimized_batch_processor.py:447:                        filter_rate = self.filtered_count / max(self.total_requests, 1) * 100
src/screening/optimized_batch_processor.py:468:        actual_rate = len(tickers) / total_time if total_time > 0 else 0
src/screening/optimized_batch_processor.py:475:        logger.info(f"Filtered: {self.filtered_count} ({self.filtered_count / max(self.total_requests, 1) * 100:.1f}%)")
src/screening/optimized_batch_processor.py:477:        logger.info(f"Error rate: {self.error_count / max(self.total_requests, 1) * 100:.1f}%")
src/screening/optimized_batch_processor.py:485:                pct = (count / self.filtered_count * 100) if self.filtered_count > 0 else 0
src/screening/optimized_batch_processor.py:494:                pct = (count / self.error_count * 100) if self.error_count > 0 else 0
src/screening/optimized_batch_processor.py:508:            'error_rate': self.error_count / max(self.total_requests, 1)
scripts/backtest_critic.py:22:HISTORY_DIR = Path(__file__).parent.parent / "data" / "backtest_history"
scripts/backtest_critic.py:23:PROPOSALS_DIR = Path(__file__).parent.parent / "data" / "backtest_critic_proposals"
scripts/backtest_critic.py:142:    report_path = PROPOSALS_DIR / f"critic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
scripts/fetch_price_history.py:26:        closes = hist["Close"].iloc[-180:]
scripts/walk_forward_backtest.py:59:HISTORY_DIR = Path(__file__).parent.parent / "data" / "backtest_history"
scripts/walk_forward_backtest.py:66:    mean_x, mean_y = sum(xs) / n, sum(ys) / n
scripts/walk_forward_backtest.py:70:    return cov / (std_x * std_y) if std_x > 0 and std_y > 0 else None
scripts/walk_forward_backtest.py:95:    last = future.iloc[-1]
scripts/walk_forward_backtest.py:125:        'max_drawdown_pct': (max_dd_dollars / total_invested * 100) if total_invested else 0,
scripts/walk_forward_backtest.py:217:            current_price = asof_data['Close'].iloc[-1]
scripts/walk_forward_backtest.py:236:            return_pct = (result['exit_price'] - entry_price) / entry_price * 100
scripts/walk_forward_backtest.py:242:                'dollar_pnl': investment_per_trade * (return_pct / 100),
scripts/walk_forward_backtest.py:284:            'win_rate_pct': len(wins) / len(returns) * 100,
scripts/walk_forward_backtest.py:285:            'avg_return_pct': statistics.mean(returns),
scripts/walk_forward_backtest.py:287:            'avg_win_pct': statistics.mean(wins) if wins else None,
scripts/walk_forward_backtest.py:288:            'avg_loss_pct': statistics.mean(losses) if losses else None,
scripts/walk_forward_backtest.py:290:            'sharpe_like': (statistics.mean(returns) / std_return) if std_return > 0 else 0,
scripts/walk_forward_backtest.py:291:            'avg_days_held': statistics.mean(t['days_held'] for t in all_trades),
scripts/walk_forward_backtest.py:349:    path = HISTORY_DIR / f"walk_forward_{timestamp}.json"
scripts/walk_forward_backtest.py:352:    latest_path = HISTORY_DIR / "latest.json"
scripts/component_correlation_analysis.py:45:    mean_x, mean_y = sum(xs) / n, sum(ys) / n
scripts/component_correlation_analysis.py:51:    return cov / (std_x * std_y)
scripts/component_correlation_analysis.py:86:            current_price = asof_data['Close'].iloc[-1]
scripts/component_correlation_analysis.py:105:                exit_price = fwd_data['Close'].iloc[-1]
scripts/component_correlation_analysis.py:107:                exit_price = hist['Close'].iloc[-1]
scripts/component_correlation_analysis.py:108:            return_pct = (exit_price - current_price) / current_price * 100
scripts/run_full_market_scan.py:189:    filepath = Path(output_dir) / f"market_scan_{timestamp}.txt"
scripts/run_full_market_scan.py:196:    latest_path = Path(output_dir) / "latest_scan.txt"
src/screening/signal_engine.py:57:            recent_low = price_data['Low'].iloc[-10:].min()
src/screening/signal_engine.py:71:        risk_pct = (current_price - stop_loss) / current_price
src/screening/signal_engine.py:81:            base_low = price_data['Low'].iloc[-30:].min()
src/screening/signal_engine.py:89:        risk_pct = (current_price - stop_loss) / current_price
src/screening/signal_engine.py:172:    # 1. TREND STRUCTURE / STAGE QUALITY (50 points) - GRADUAL, NOT BINARY
src/screening/signal_engine.py:191:            (distance_50 / 15.0 * 10) +  # 0-15% → 0-10 pts
src/screening/signal_engine.py:192:            (distance_200 / 20.0 * 5)     # 0-20% → 0-5 pts
src/screening/signal_engine.py:208:            (slope_50 / 0.08 * 10) +   # 0-0.08 → 0-10 pts
src/screening/signal_engine.py:209:            (slope_200 / 0.05 * 5)      # 0-0.05 → 0-5 pts
src/screening/signal_engine.py:251:    trend_score_final = min(trend_score, 40) * (35 / 40)
src/screening/signal_engine.py:283:                q1_growth = ((rev_series.iloc[-1] - rev_series.iloc[-2]) / rev_series.iloc[-2] * 100) if rev_series.iloc[-2] != 0 else 0
src/screening/signal_engine.py:284:                q2_growth = ((rev_series.iloc[-2] - rev_series.iloc[-3]) / rev_series.iloc[-3] * 100) if rev_series.iloc[-3] != 0 else 0
src/screening/signal_engine.py:285:                q3_growth = ((rev_series.iloc[-3] - rev_series.iloc[-4]) / rev_series.iloc[-4] * 100) if rev_series.iloc[-4] != 0 else 0
src/screening/signal_engine.py:288:                avg_qoq_growth = (q1_growth + q2_growth + q3_growth) / 3.0
src/screening/signal_engine.py:294:                # Formula: (avg_qoq / 10) * 15, capped at 0-15
src/screening/signal_engine.py:299:                    revenue_trend_score = min(15, (avg_qoq_growth / 10.0) * 15)
src/screening/signal_engine.py:320:                    revenue_trend_score = min(15, (revenue_yoy / 20.0) * 15)
src/screening/signal_engine.py:332:        # Formula: ((eps_yoy + 20) / 80) * 15, capped at 15
src/screening/signal_engine.py:335:            eps_score = min(15, max(0, ((eps_yoy + 20) / 80.0) * 15))
src/screening/signal_engine.py:352:        # Formula: 10 - (inv_qoq_change / 20) * 10, range 0-10
src/screening/signal_engine.py:357:            inventory_score = min(10, max(0, 10 - (inv_qoq_change / 20.0) * 10))
src/screening/signal_engine.py:386:    fundamental_score_final = fundamental_score * (35 / 40)
src/screening/signal_engine.py:397:        recent_prices = price_data['Close'].iloc[-6:]  # 6 days to get 5 changes
src/screening/signal_engine.py:398:        recent_volume = price_data['Volume'].iloc[-5:]
src/screening/signal_engine.py:399:        avg_volume = price_data['Volume'].iloc[-30:-5].mean()
src/screening/signal_engine.py:419:        avg_vol_up = (volume_on_up_days / up_days) if up_days > 0 else 0
src/screening/signal_engine.py:420:        avg_vol_down = (volume_on_down_days / down_days) if down_days > 0 else 0
src/screening/signal_engine.py:427:        vol_ratio = (avg_vol_up / avg_vol_down) if avg_vol_down > 0 else 1.0
src/screening/signal_engine.py:522:        rr_ratio = reward_amount / risk_amount
src/screening/signal_engine.py:559:    rr_score_final = rr_score * (10 / 15)
src/screening/signal_engine.py:573:    distance_from_52w_high = ((current_price - week_52_high) / week_52_high * 100) if week_52_high > 0 else -100
src/screening/signal_engine.py:588:            high_proximity_score = 3 - ((abs(distance_from_52w_high) - 5) / 10.0) * 1
src/screening/signal_engine.py:593:            high_proximity_score = 2 - ((abs(distance_from_52w_high) - 15) / 10.0) * 1
src/screening/signal_engine.py:607:            sma_score = 2 - (distance_50 / 20.0) * 1
src/screening/signal_engine.py:610:            sma_score = max(0, 1 - ((distance_50 - 20) / 15.0) * 1)
src/screening/signal_engine.py:618:        # Formula: max(0, 2 - abs(distance_50 - 1) / 5 * 2), range 0-2
src/screening/signal_engine.py:625:        proximity_score = max(0, 2 - (deviation / 6.0) * 2)
src/screening/signal_engine.py:782:        pct_below = ((sma_50 - current_price) / sma_50) * 100
src/screening/signal_engine.py:856:        recent_high = close.iloc[-20:].max()

exec
/bin/zsh -lc "nl -ba src/screening/signal_engine.py | sed -n '1,150p'; nl -ba src/screening/signal_engine.py | sed -n '150,660p'; nl -ba src/screening/signal_engine.py | sed -n '740,942p'; nl -ba src/screening/phase_indicators.py | sed -n '40,130p'; nl -ba src/screening/phase_indicators.py | sed -n '480,580p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Signal detection and scoring engine for buy/sell decisions.
     2	
     3	This module implements the buy and sell signal detection based on Phase transitions
     4	and technical/fundamental confluence.
     5	"""
     6	
     7	import logging
     8	from typing import Dict, List, Optional
     9	
    10	import numpy as np
    11	import pandas as pd
    12	
    13	from .phase_indicators import (
    14	    calculate_volume_ratio,
    15	    calculate_rs_slope,
    16	    detect_volatility_contraction,
    17	    detect_breakout,
    18	    validate_minervini_trend_template,
    19	    calculate_sma
    20	)
    21	
    22	logging.basicConfig(
    23	    level=logging.INFO,
    24	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    25	)
    26	logger = logging.getLogger(__name__)
    27	
    28	
    29	def calculate_stop_loss(
    30	    price_data: pd.DataFrame,
    31	    current_price: float,
    32	    phase_info: Dict,
    33	    phase: int
    34	) -> float:
    35	    """Calculate logical stop loss level for swing trading.
    36	
    37	    Stop loss placement rules:
    38	    - Phase 2: Below recent swing low or 50 SMA (whichever is closer), typically 6-8% risk
    39	    - Phase 1: Below base/consolidation low, typically 7-10% risk
    40	    - Maximum risk: 10% from current price (wider stops = don't take trade)
    41	
    42	    Args:
    43	        price_data: OHLCV data
    44	        current_price: Current price
    45	        phase_info: Phase classification dict
    46	        phase: Phase number (1 or 2)
    47	
    48	    Returns:
    49	        Stop loss price level
    50	    """
    51	    sma_50 = phase_info.get('sma_50', 0)
    52	
    53	    if phase == 2:
    54	        # Stage 2: Use 50 SMA or recent swing low, whichever is higher (tighter stop)
    55	        # Look for lowest low in last 10 days (recent pullback low)
    56	        if len(price_data) >= 10:
    57	            recent_low = price_data['Low'].iloc[-10:].min()
    58	        else:
    59	            recent_low = price_data['Low'].min()
    60	
    61	        # Stop should be below recent low with buffer (0.5%)
    62	        swing_low_stop = recent_low * 0.995
    63	
    64	        # Or below 50 SMA with buffer (1%)
    65	        sma_stop = sma_50 * 0.99 if sma_50 > 0 else swing_low_stop
    66	
    67	        # Use the higher of the two (tighter stop = less risk)
    68	        stop_loss = max(swing_low_stop, sma_stop)
    69	
    70	        # But don't place stop too tight (min 3% risk) or too loose (max 10% risk)
    71	        risk_pct = (current_price - stop_loss) / current_price
    72	        if risk_pct < 0.03:  # Too tight
    73	            stop_loss = current_price * 0.97
    74	        elif risk_pct > 0.10:  # Too loose
    75	            stop_loss = current_price * 0.90
    76	
    77	    else:  # Phase 1
    78	        # Stage 1: Stop below base/consolidation low
    79	        # Use lowest low in last 30 days (base low)
    80	        if len(price_data) >= 30:
    81	            base_low = price_data['Low'].iloc[-30:].min()
    82	        else:
    83	            base_low = price_data['Low'].min()
    84	
    85	        # Stop below base low with buffer (1%)
    86	        stop_loss = base_low * 0.99
    87	
    88	        # Max 10% risk rule
    89	        risk_pct = (current_price - stop_loss) / current_price
    90	        if risk_pct > 0.10:
    91	            stop_loss = current_price * 0.90
    92	
    93	    return stop_loss
    94	
    95	
    96	def score_buy_signal(
    97	    ticker: str,
    98	    price_data: pd.DataFrame,
    99	    current_price: float,
   100	    phase_info: Dict,
   101	    rs_series: pd.Series,
   102	    fundamentals: Optional[Dict] = None,
   103	    vcp_data: Optional[Dict] = None
   104	) -> Dict[str, any]:
   105	    """Score a buy signal for swing/position trading (NOT day trading).
   106	
   107	    Based on Weinstein/O'Neil/Minervini Stage 2 methodology with gradual scoring.
   108	
   109	    Scoring Components (0-125), reweighted per component_correlation_analysis.py
   110	    backtesting (2 independent historical windows, real forward returns, no look-ahead):
   111	    - Trend structure/Stage quality: 35 points (was 40 — real but modest correlation)
   112	    - Fundamentals: 35 points (was 40 — untested by the backtest, not disproven; see note below)
   113	    - Entry quality: 25 points (was 5 — BY FAR the strongest predictor found, +0.40/+0.48
   114	      correlation across both windows, stronger than the blended total score itself)
   115	    - Risk/Reward: 10 points (was 15 — weak/inconsistent correlation, +0.04/+0.26)
   116	    - Relative Strength: 10 points (unchanged — correlation flipped sign between windows,
   117	      +0.16/-0.21, too inconsistent to confidently reweight either direction)
   118	    - Volume behavior: 5 points (was 10 — no positive correlation in either window, -0.02/-0.18)
   119	    - VCP pattern bonus: +5 points (unchanged, not separately tested)
   120	
   121	    Note: Fundamentals couldn't be backtested because point-in-time quarterly data (as it
   122	    existed on a historical date, without look-ahead) is harder to reconstruct than price
   123	    history — its weight was trimmed modestly on general principle, not specific evidence.
   124	
   125	    Threshold: >= 60 for signals (docstring previously said 70 - corrected to match code)
   126	
   127	    Args:
   128	        ticker: Stock ticker
   129	        price_data: OHLCV data
   130	        current_price: Current price
   131	        phase_info: Phase classification
   132	        rs_series: Relative strength series
   133	        fundamentals: Optional fundamental analysis
   134	        vcp_data: Optional VCP pattern analysis
   135	
   136	    Returns:
   137	        Dict with buy signal score and details
   138	    """
   139	    phase = phase_info['phase']
   140	
   141	    # MINERVINI REQUIREMENT: Only Phase 2 (confirmed Stage 2 uptrend)
   142	    # Phase 1 stocks are NOT ready - they're still basing/accumulating
   143	    if phase != 2:
   144	        return {
   145	            'ticker': ticker,
   146	            'is_buy': False,
   147	            'score': 0,
   148	            'reason': f'Not in Phase 2 (currently Phase {phase}) - Minervini requires confirmed uptrend',
   149	            'details': {}
   150	        }
   150	        }
   151	
   152	    # Validate Minervini Trend Template (SEPA)
   153	    # This is the core entry criteria from "Trade Like a Stock Market Wizard"
   154	    sma_200 = calculate_sma(price_data['Close'], 200)
   155	    minervini = validate_minervini_trend_template(current_price, phase_info, sma_200)
   156	
   157	    # STRICT FILTER: Must pass at least 7 of 8 Minervini criteria
   158	    if not minervini['passes_template']:
   159	        return {
   160	            'ticker': ticker,
   161	            'is_buy': False,
   162	            'score': 0,
   163	            'reason': f"Fails Minervini Trend Template ({minervini['criteria_passed']}/8 criteria passed)",
   164	            'details': {'minervini': minervini}
   165	        }
   166	
   167	    score = 0
   168	    details = {}
   169	    reasons = []
   170	
   171	    # ========================================================================
   172	    # 1. TREND STRUCTURE / STAGE QUALITY (50 points) - GRADUAL, NOT BINARY
   173	    # ========================================================================
   174	    trend_score = 0
   175	
   176	    sma_50 = phase_info.get('sma_50', 0)
   177	    sma_200 = phase_info.get('sma_200', 0)
   178	    slope_50 = phase_info.get('slope_50', 0)
   179	    slope_200 = phase_info.get('slope_200', 0)
   180	    distance_50 = phase_info.get('distance_from_50sma', 0)
   181	    distance_200 = phase_info.get('distance_from_200sma', 0)
   182	
   183	    # A) Base Stage 2 quality (30 points max) - LINEAR FORMULAS
   184	    if phase == 2:
   185	        # Not all Stage 2 stocks are equal! Grade by strength
   186	        stage2_quality = 0
   187	
   188	        # How far above SMAs? (15 pts) - Linear from 0% to 15%+
   189	        # Formula: min(15, (distance_50 * 0.6) + (distance_200 * 0.4))
   190	        distance_component = min(15, max(0,
   191	            (distance_50 / 15.0 * 10) +  # 0-15% → 0-10 pts
   192	            (distance_200 / 20.0 * 5)     # 0-20% → 0-5 pts
   193	        ))
   194	        stage2_quality += distance_component
   195	
   196	        if distance_50 >= 10:
   197	            reasons.append(f'Strong Stage 2: {distance_50:.1f}% above 50 SMA')
   198	        elif distance_50 >= 3:
   199	            reasons.append(f'Good Stage 2: {distance_50:.1f}% above 50 SMA')
   200	        elif distance_50 >= 0:
   201	            reasons.append(f'Weak Stage 2: {distance_50:.1f}% above 50 SMA')
   202	        else:
   203	            reasons.append(f'Very weak Stage 2: {distance_50:.1f}% from 50 SMA')
   204	
   205	        # SMA slopes - are SMAs rising? (15 pts) - Linear from 0 to 0.08+
   206	        # Formula: (slope_50/0.08 * 10) + (slope_200/0.05 * 5), capped at 15
   207	        slope_component = min(15, max(0,
   208	            (slope_50 / 0.08 * 10) +   # 0-0.08 → 0-10 pts
   209	            (slope_200 / 0.05 * 5)      # 0-0.05 → 0-5 pts
   210	        ))
   211	        stage2_quality += slope_component
   212	
   213	        if slope_50 > 0.05:
   214	            reasons.append(f'SMAs rising strongly (50:{slope_50:.3f}, 200:{slope_200:.3f})')
   215	        elif slope_50 > 0.02:
   216	            reasons.append(f'SMAs rising moderately')
   217	        elif slope_50 > 0:
   218	            reasons.append(f'SMAs rising weakly')
   219	        else:
   220	            reasons.append('⚠ SMAs flat or declining')
   221	
   222	        trend_score += stage2_quality
   223	
   224	    # At this point, we're guaranteed to be in Phase 2 (checked above)
   225	    # Minervini only buys confirmed Stage 2 stocks
   226	
   227	    # B) Breakout detection (10 points) - Enhanced with VCP
   228	    breakout_info = detect_breakout(price_data, current_price, phase_info, vcp_data)
   229	    if breakout_info['is_breakout']:
   230	        trend_score += 10
   231	        breakout_type = breakout_info['breakout_type']
   232	        volume_confirmed = breakout_info.get('volume_confirmed', False)
   233	
   234	        if volume_confirmed:
   235	            reasons.append(f"🟢 {breakout_type} (volume confirmed)")
   236	        else:
   237	            reasons.append(f"🟡 {breakout_type} (low volume)")
   238	        details['breakout'] = breakout_info
   239	
   240	    # C) Over-extension check (10 points penalty)
   241	    if distance_50 > 30:
   242	        trend_score -= 10
   243	        reasons.append(f'⚠ Over-extended: {distance_50:.1f}% above 50 SMA')
   244	    elif distance_50 > 20:
   245	        trend_score -= 5
   246	        reasons.append(f'Moderately extended above 50 SMA')
   247	
   248	    # Reweighted 40->35 pts: component_correlation_analysis.py backtest found trend_score
   249	    # correlates only weakly with forward returns (+0.10, +0.16 across 2 windows) — real
   250	    # but modest, so it gives up a little weight to entry_score (see below).
   251	    trend_score_final = min(trend_score, 40) * (35 / 40)
   252	    score += trend_score_final
   253	    details['trend_score'] = round(trend_score_final, 2)
   254	
   255	    # ========================================================================
   256	    # 2. FUNDAMENTALS (40 points) - EQUAL WEIGHT REVENUE & EPS
   257	    # Revenue Growth: 15 pts (requires 3Q of >5% QoQ for max score)
   258	    # EPS Growth: 15 pts (equal importance to revenue)
   259	    # Inventory: 10 pts (demand indicator)
   260	    # ========================================================================
   261	    fundamental_score = 0
   262	
   263	    if fundamentals:
   264	        # A) Growth trends (30 points total) - EQUAL WEIGHT
   265	        # Revenue and EPS are equally important (15 pts each)
   266	
   267	        # Get quarterly revenue data for trend analysis
   268	        quarterly_revenue = fundamentals.get('quarterly_revenue', {})
   269	        revenue_qoq = fundamentals.get('revenue_qoq_change')  # None or float
   270	        revenue_yoy = fundamentals.get('revenue_yoy_change')  # None or float
   271	        eps_yoy = fundamentals.get('eps_yoy_change')  # None or float
   272	
   273	        # Calculate 3-quarter revenue trend using LINEAR SCORING
   274	        revenue_trend_score = 0
   275	
   276	        if quarterly_revenue and len(quarterly_revenue) >= 4:
   277	            # Get last 4 quarters of revenue (sorted by date)
   278	            import pandas as pd
   279	            rev_series = pd.Series(quarterly_revenue).sort_index()
   280	
   281	            if len(rev_series) >= 4:
   282	                # Calculate QoQ changes for last 3 quarters
   283	                q1_growth = ((rev_series.iloc[-1] - rev_series.iloc[-2]) / rev_series.iloc[-2] * 100) if rev_series.iloc[-2] != 0 else 0
   284	                q2_growth = ((rev_series.iloc[-2] - rev_series.iloc[-3]) / rev_series.iloc[-3] * 100) if rev_series.iloc[-3] != 0 else 0
   285	                q3_growth = ((rev_series.iloc[-3] - rev_series.iloc[-4]) / rev_series.iloc[-4] * 100) if rev_series.iloc[-4] != 0 else 0
   286	
   287	                # Calculate average QoQ growth across 3 quarters
   288	                avg_qoq_growth = (q1_growth + q2_growth + q3_growth) / 3.0
   289	
   290	                # LINEAR SCALE: Map avg QoQ growth to 0-15 points
   291	                # 0% or negative → 0 pts (no growth = no points)
   292	                # +5% avg → 7.5 pts (your minimum threshold for good)
   293	                # +10% avg → 15 pts (excellent - capped at max)
   294	                # Formula: (avg_qoq / 10) * 15, capped at 0-15
   295	                # Only positive growth gets points
   296	                if avg_qoq_growth <= 0:
   297	                    revenue_trend_score = 0
   298	                else:
   299	                    revenue_trend_score = min(15, (avg_qoq_growth / 10.0) * 15)
   300	
   301	                # Add strong penalty if latest quarter is declining >2%
   302	                if q1_growth < -2:
   303	                    fundamental_score -= 15  # Penalty for recent decline
   304	                    reasons.append(f'🔴 Revenue: Recent decline {q1_growth:.1f}% QoQ (3Q avg: {avg_qoq_growth:.1f}%, PENALTY)')
   305	                # Color-code based on average and show progression
   306	                elif avg_qoq_growth >= 5:
   307	                    reasons.append(f'🟢 Revenue: 3Q avg {avg_qoq_growth:.1f}% QoQ ({q3_growth:.1f}% → {q2_growth:.1f}% → {q1_growth:.1f}%)')
   308	                elif avg_qoq_growth >= 0:
   309	                    reasons.append(f'🟡 Revenue: 3Q avg {avg_qoq_growth:.1f}% QoQ ({q3_growth:.1f}% → {q2_growth:.1f}% → {q1_growth:.1f}%)')
   310	                else:
   311	                    reasons.append(f'🔴 Revenue: 3Q avg {avg_qoq_growth:.1f}% QoQ ({q3_growth:.1f}% → {q2_growth:.1f}% → {q1_growth:.1f}%)')
   312	        else:
   313	            # No quarterly data - use YoY if available
   314	            if revenue_yoy is not None and revenue_yoy != 0:
   315	                # Same logic: 0% or negative = 0 pts, +20% YoY = 15 pts (max)
   316	                if revenue_yoy <= 0:
   317	                    revenue_trend_score = 0
   318	                    reasons.append(f'🔴 Revenue: {revenue_yoy:.0f}% YoY declining (no QoQ data)')
   319	                else:
   320	                    revenue_trend_score = min(15, (revenue_yoy / 20.0) * 15)
   321	                    if revenue_yoy >= 10:
   322	                        reasons.append(f'🟢 Revenue: {revenue_yoy:.0f}% YoY (no QoQ data)')
   323	                    else:
   324	                        reasons.append(f'🟡 Revenue: {revenue_yoy:.0f}% YoY (no QoQ data)')
   325	            else:
   326	                revenue_trend_score = 0  # No data = 0 points
   327	                reasons.append('🔴 Revenue data unavailable')
   328	
   329	        fundamental_score += revenue_trend_score
   330	
   331	        # EPS component (15 pts) - Equal importance to revenue
   332	        # Formula: ((eps_yoy + 20) / 80) * 15, capped at 15
   333	        # -20% EPS → 0 pts, 0% → 3.75 pts, +20% → 7.5 pts, +60% → 15 pts (max)
   334	        if eps_yoy is not None and eps_yoy != 0:
   335	            eps_score = min(15, max(0, ((eps_yoy + 20) / 80.0) * 15))
   336	
   337	            if eps_yoy >= 50:
   338	                reasons.append(f'🟢 EPS: +{eps_yoy:.0f}% YoY (strong earnings)')
   339	            elif eps_yoy >= 20:
   340	                reasons.append(f'🟢 EPS: +{eps_yoy:.0f}% YoY')
   341	            elif eps_yoy >= 0:
   342	                reasons.append(f'🟡 EPS: +{eps_yoy:.0f}% YoY')
   343	            else:
   344	                reasons.append(f'🔴 EPS: {eps_yoy:.0f}% YoY')
   345	        else:
   346	            eps_score = 7.5  # Neutral if missing (half of 15)
   347	        fundamental_score += eps_score
   348	
   349	        # B) Inventory signal (10 points) - LINEAR based on actual QoQ %
   350	        inv_qoq_change = fundamentals.get('inventory_qoq_change')  # None or float
   351	
   352	        # Formula: 10 - (inv_qoq_change / 20) * 10, range 0-10
   353	        # -20% inventory draw = 20 pts (capped at 10)
   354	        # 0% = 10 pts (neutral)
   355	        # +20% buildup = 0 pts
   356	        if inv_qoq_change is not None:
   357	            inventory_score = min(10, max(0, 10 - (inv_qoq_change / 20.0) * 10))
   358	            fundamental_score += inventory_score
   359	
   360	            if inv_qoq_change < -5:
   361	                reasons.append(f'✓ Inventory drawing ({inv_qoq_change:.1f}% QoQ - strong demand)')
   362	            elif inv_qoq_change < 5:
   363	                reasons.append(f'Inventory neutral ({inv_qoq_change:.1f}% QoQ)')
   364	            elif inv_qoq_change < 15:
   365	                reasons.append(f'⚠ Inventory building ({inv_qoq_change:.1f}% QoQ)')
   366	            else:
   367	                reasons.append(f'⚠ Inventory building rapidly ({inv_qoq_change:.1f}% QoQ - demand concern)')
   368	        else:
   369	            # No inventory data - use neutral score (50% of max = 5 pts)
   370	            inventory_score = 5
   371	            fundamental_score += inventory_score
   372	            # Don't add to reasons - many companies don't have inventory
   373	
   374	        # C) Profit margins expansion (10 points bonus)
   375	        # TODO: Add when margin data available
   376	        fundamental_score += 10  # Placeholder - assume neutral
   377	
   378	    else:
   379	        # No fundamentals available - neutral score
   380	        fundamental_score = 20  # Half of 40
   381	        reasons.append('No fundamental data available')
   382	
   383	    # Reweighted 40->35 pts: this backtest couldn't validate fundamental_score at all
   384	    # (requires real point-in-time quarterly data, harder to get without look-ahead than
   385	    # truncating price history) — modest reduction reflects "untested," not "disproven."
   386	    fundamental_score_final = fundamental_score * (35 / 40)
   387	    details['fundamental_score'] = round(fundamental_score_final, 2)
   388	    score += fundamental_score_final
   389	
   390	    # ========================================================================
   391	    # 3. VOLUME BEHAVIOR (10 points) - DIRECTIONAL CONTEXT MATTERS!
   392	    # ========================================================================
   393	    volume_score = 0
   394	
   395	    if 'Volume' in price_data.columns and len(price_data) >= 30:
   396	        # Look at last 5 days to understand volume context
   397	        recent_prices = price_data['Close'].iloc[-6:]  # 6 days to get 5 changes
   398	        recent_volume = price_data['Volume'].iloc[-5:]
   399	        avg_volume = price_data['Volume'].iloc[-30:-5].mean()
   400	
   401	        # Calculate price change context
   402	        up_days = 0
   403	        down_days = 0
   404	        volume_on_up_days = 0
   405	        volume_on_down_days = 0
   406	
   407	        for i in range(1, len(recent_prices)):
   408	            price_change = recent_prices.iloc[i] - recent_prices.iloc[i-1]
   409	            vol = recent_volume.iloc[i-1]
   410	
   411	            if price_change > 0:
   412	                up_days += 1
   413	                volume_on_up_days += vol
   414	            else:
   415	                down_days += 1
   416	                volume_on_down_days += vol
   417	
   418	        # Average volume on up vs down days
   419	        avg_vol_up = (volume_on_up_days / up_days) if up_days > 0 else 0
   420	        avg_vol_down = (volume_on_down_days / down_days) if down_days > 0 else 0
   421	
   422	        # Score based on volume ratio - LINEAR
   423	        # Formula: 5 + (vol_ratio - 1) * 10, range 0-10
   424	        # ratio 0.5 (heavy on down) = 0 pts
   425	        # ratio 1.0 (equal) = 5 pts
   426	        # ratio 1.5+ (heavy on up) = 10 pts
   427	        vol_ratio = (avg_vol_up / avg_vol_down) if avg_vol_down > 0 else 1.0
   428	        volume_score = min(10, max(0, 5 + (vol_ratio - 1.0) * 10))
   429	
   430	        if vol_ratio >= 1.3:
   431	            reasons.append(f'✓ Volume heavier on up days ({avg_vol_up/1e6:.1f}M vs {avg_vol_down/1e6:.1f}M, ratio {vol_ratio:.2f})')
   432	        elif vol_ratio >= 1.1:
   433	            reasons.append(f'Volume slightly heavier on up days (ratio {vol_ratio:.2f})')
   434	        elif vol_ratio >= 0.9:
   435	            reasons.append(f'Volume pattern neutral (ratio {vol_ratio:.2f})')
   436	        else:
   437	            reasons.append(f'⚠ Volume heavier on down days (ratio {vol_ratio:.2f} - distribution)')
   438	
   439	        details['avg_vol_up'] = round(avg_vol_up, 0)
   440	        details['avg_vol_down'] = round(avg_vol_down, 0)
   441	    else:
   442	        volume_score = 5  # Neutral if no data
   443	
   444	    # Reweighted 10->5 pts: component_correlation_analysis.py backtest found volume_score
   445	    # showed NO positive correlation with forward returns in either of 2 independent
   446	    # windows (-0.02, -0.18) — cut in half rather than removed entirely since it's still
   447	    # only 2 windows of evidence, but this is the weakest-performing component tested.
   448	    volume_score_final = volume_score * 0.5
   449	    details['volume_score'] = round(volume_score_final, 2)
   450	    score += volume_score_final
   451	
   452	    # ========================================================================
   453	    # 4. RELATIVE STRENGTH (10 points) - Market-relative performance
   454	    # ========================================================================
   455	    # RS measures stock performance vs SPY (market-relative strength)
   456	    # Different from technical trend which is absolute price structure
   457	    # Strong RS = stock outperforming market
   458	
   459	    rs_score = 0
   460	
   461	    if len(rs_series) >= 20 and not rs_series.isna().all():
   462	        rs_slope = calculate_rs_slope(rs_series, 20)
   463	        details['rs_slope'] = round(rs_slope, 3)
   464	
   465	        # SMOOTH LINEAR scoring based on RS slope (NO BUCKETS)
   466	        # RS slope ranges typically from -0.30 to +0.30
   467	        # Formula: 5 + (rs_slope * 16.67), capped at 0-10
   468	        # Examples:
   469	        #   rs_slope = +0.30 → 5 + (0.30 * 16.67) = 10.0 pts (max)
   470	        #   rs_slope = +0.15 → 5 + (0.15 * 16.67) = 7.5 pts
   471	        #   rs_slope =  0.00 → 5 + (0.00 * 16.67) = 5.0 pts (neutral)
   472	        #   rs_slope = -0.15 → 5 + (-0.15 * 16.67) = 2.5 pts
   473	        #   rs_slope = -0.30 → 5 + (-0.30 * 16.67) = 0.0 pts (min)
   474	        rs_score = min(10, max(0, 5 + (rs_slope * 16.67)))
   475	
   476	        if rs_slope > 0.10:
   477	            reasons.append(f'✓ Strong RS: {rs_slope:.3f} (outperforming SPY)')
   478	        elif rs_slope > 0.03:
   479	            reasons.append(f'Positive RS: {rs_slope:.3f}')
   480	        elif rs_slope > -0.03:
   481	            reasons.append(f'Neutral RS: {rs_slope:.3f}')
   482	        elif rs_slope > -0.10:
   483	            reasons.append(f'Weak RS: {rs_slope:.3f}')
   484	        else:
   485	            reasons.append(f'⚠ Declining RS: {rs_slope:.3f} (underperforming SPY)')
   486	    else:
   487	        details['rs_slope'] = None
   488	        rs_score = 5  # Neutral if missing
   489	
   490	    score += rs_score
   491	    details['rs_score'] = round(rs_score, 2)
   492	
   493	    # ========================================================================
   494	    # 5. STOP LOSS CALCULATION (not scored, but critical for risk mgmt)
   495	    # ========================================================================
   496	    stop_loss = calculate_stop_loss(price_data, current_price, phase_info, phase)
   497	    details['stop_loss'] = stop_loss
   498	
   499	    # ========================================================================
   500	    # 6. RISK/REWARD RATIO (15 points) - CRITICAL for growth stocks!
   501	    # ========================================================================
   502	    # For growth stocks, asymmetric upside is essential
   503	    # We want stocks with 3:1+ R/R ratios for maximum growth potential
   504	    rr_score = 0
   505	    risk_amount = current_price - stop_loss if stop_loss else 0
   506	
   507	    # Calculate reward potential (more aggressive for growth stocks)
   508	    if phase == 2:
   509	        # Stage 2: Use 30% upside as target (aggressive growth target)
   510	        reward_target = current_price * 1.30
   511	    else:  # Phase 1
   512	        # Stage 1: Use breakout level + 25% as target
   513	        if breakout_info.get('is_breakout'):
   514	            reward_target = breakout_info['breakout_level'] * 1.25
   515	        else:
   516	            reward_target = sma_50 * 1.25  # Target 50 SMA + 25%
   517	
   518	    reward_amount = reward_target - current_price
   519	
   520	    # Calculate R/R ratio
   521	    if risk_amount > 0:
   522	        rr_ratio = reward_amount / risk_amount
   523	
   524	        # AGGRESSIVE LINEAR scoring for growth stocks:
   525	        # < 2:1 = 0 pts (reject - not enough upside)
   526	        # 2:1 = 3 pts (minimum acceptable)
   527	        # 3:1 = 9 pts (good)
   528	        # 4:1 = 12 pts (excellent)
   529	        # 5:1+ = 15 pts (outstanding - maximum)
   530	        # Formula: For R/R >= 2, score = min(15, (rr_ratio - 2) * 6 + 3)
   531	        if rr_ratio < 2.0:
   532	            rr_score = 0  # Reject poor R/R
   533	        else:
   534	            rr_score = min(15, ((rr_ratio - 2.0) * 6) + 3)
   535	
   536	        details['risk_reward_ratio'] = round(rr_ratio, 2)
   537	        details['risk_amount'] = round(risk_amount, 2)
   538	        details['reward_amount'] = round(reward_amount, 2)
   539	        details['reward_target'] = round(reward_target, 2)
   540	
   541	        if rr_ratio >= 5.0:
   542	            reasons.append(f'🟢 Outstanding R/R: {rr_ratio:.1f}:1 (${reward_amount:.2f} upside, ${risk_amount:.2f} risk)')
   543	        elif rr_ratio >= 4.0:
   544	            reasons.append(f'🟢 Excellent R/R: {rr_ratio:.1f}:1 (${reward_amount:.2f} upside, ${risk_amount:.2f} risk)')
   545	        elif rr_ratio >= 3.0:
   546	            reasons.append(f'🟢 Good R/R: {rr_ratio:.1f}:1 (${reward_amount:.2f} upside)')
   547	        elif rr_ratio >= 2.0:
   548	            reasons.append(f'🟡 Acceptable R/R: {rr_ratio:.1f}:1')
   549	        else:
   550	            reasons.append(f'🔴 Poor R/R: {rr_ratio:.1f}:1 (need 2:1+ for growth)')
   551	    else:
   552	        details['risk_reward_ratio'] = 0
   553	        rr_score = 0
   554	
   555	    # Reweighted 15->10 pts: component_correlation_analysis.py backtest found rr_score's
   556	    # correlation with forward returns was weak/inconsistent between the 2 windows tested
   557	    # (+0.04, +0.26) — still risk-management-relevant (why it isn't cut further), just not
   558	    # a strong predictor on its own.
   559	    rr_score_final = rr_score * (10 / 15)
   560	    score += rr_score_final
   561	    details['rr_score'] = round(rr_score_final, 2)
   562	
   563	    # ========================================================================
   564	    # 7. ENTRY QUALITY (5 points) - Minervini Pivot Point Methodology
   565	    # ========================================================================
   566	    # Minervini's ideal entry is the PIVOT POINT - a breakout from a proper base
   567	    # near 52-week highs on expanding volume, NOT just pullbacks to 50 SMA
   568	    entry_score = 0
   569	
   570	    # Calculate proximity to 52-week high (key Minervini metric)
   571	    # phase_info contains 'week_52_high' from phase classification
   572	    week_52_high = phase_info.get('week_52_high', current_price)
   573	    distance_from_52w_high = ((current_price - week_52_high) / week_52_high * 100) if week_52_high > 0 else -100
   574	
   575	    if phase == 2:
   576	        # Stage 2 uptrend - score based on PIVOT POINT criteria
   577	        # Minervini's rule: Within 25% of 52-week high is ideal
   578	        # The CLOSER to 52-week high, the BETTER (indicates leadership)
   579	
   580	        # Primary factor: Proximity to 52-week high (3 pts)
   581	        if distance_from_52w_high >= -5:
   582	            # At or near 52-week high (ideal pivot breakout zone)
   583	            high_proximity_score = 3
   584	            reasons.append(f'🟢 At 52W high: {abs(distance_from_52w_high):.1f}% from high (pivot zone)')
   585	        elif distance_from_52w_high >= -15:
   586	            # Within 15% of high (good - near pivot zone)
   587	            # Linear from 3 pts (at -5%) to 2 pts (at -15%)
   588	            high_proximity_score = 3 - ((abs(distance_from_52w_high) - 5) / 10.0) * 1
   589	            reasons.append(f'🟢 Near 52W high: {abs(distance_from_52w_high):.1f}% from high')
   590	        elif distance_from_52w_high >= -25:
   591	            # Within 25% of high (acceptable - Minervini's threshold)
   592	            # Linear from 2 pts (at -15%) to 1 pt (at -25%)
   593	            high_proximity_score = 2 - ((abs(distance_from_52w_high) - 15) / 10.0) * 1
   594	            reasons.append(f'🟡 Within 25% of 52W high: {abs(distance_from_52w_high):.1f}% from high')
   595	        else:
   596	            # More than 25% below high (lagging, not leading)
   597	            high_proximity_score = 0
   598	            reasons.append(f'🔴 Far from 52W high: {abs(distance_from_52w_high):.1f}% below (not a leader)')
   599	
   600	        entry_score += high_proximity_score
   601	
   602	        # Secondary factor: Distance from 50 SMA (2 pts)
   603	        # Must be ABOVE 50 SMA, but distance less critical for pivot breakouts
   604	        if distance_50 > 0 and distance_50 <= 20:
   605	            # Above 50 SMA and not overextended (good)
   606	            # Linear from 2 pts (at 0%) to 1 pt (at 20%)
   607	            sma_score = 2 - (distance_50 / 20.0) * 1
   608	        elif distance_50 > 20:
   609	            # More than 20% above 50 SMA (getting extended)
   610	            sma_score = max(0, 1 - ((distance_50 - 20) / 15.0) * 1)
   611	        else:
   612	            # Below 50 SMA (not in proper Stage 2)
   613	            sma_score = 0
   614	
   615	        entry_score += sma_score
   616	    else:  # Phase 1
   617	        # Stage 1: Best entry near breakout zone (-3% to +5% from 50 SMA) = 2 pts
   618	        # Formula: max(0, 2 - abs(distance_50 - 1) / 5 * 2), range 0-2
   619	        # Target zone is -3% to +5%, with ideal at +1%
   620	        # +1% from 50 SMA = 2 pts (perfect breakout positioning)
   621	        # -3% or +5% from 50 SMA = 0.4 pts (edge of ideal zone)
   622	        # Beyond that = 0 pts
   623	        ideal_position = 1.0  # 1% above 50 SMA is ideal for breakout
   624	        deviation = abs(distance_50 - ideal_position)
   625	        proximity_score = max(0, 2 - (deviation / 6.0) * 2)
   626	        entry_score += proximity_score
   627	
   628	        if distance_50 >= -1 and distance_50 <= 3:
   629	            reasons.append(f'✓ Excellent breakout zone: {distance_50:.1f}% from 50 SMA')
   630	        elif distance_50 >= -4 and distance_50 <= 6:
   631	            reasons.append(f'Good entry zone: {distance_50:.1f}% from 50 SMA')
   632	        elif distance_50 >= -7 and distance_50 <= 9:
   633	            reasons.append(f'Approaching entry zone: {distance_50:.1f}% from 50 SMA')
   634	        else:
   635	            reasons.append(f'Outside ideal entry zone: {distance_50:.1f}% from 50 SMA')
   636	
   637	    # Reweighted 5->25 pts: component_correlation_analysis.py backtest found entry_score
   638	    # was BY FAR the strongest predictor of forward returns of any component, consistently
   639	    # across 2 independent windows (+0.40, +0.48) — stronger than the blended total score
   640	    # itself (+0.18, +0.08). It was previously only 4% of the total score despite being the
   641	    # most reliable signal found; this brings its weight in line with that evidence.
   642	    entry_score_final = entry_score * 5
   643	    score += entry_score_final
   644	    details['entry_score'] = round(entry_score_final, 2)
   645	
   646	    # ========================================================================
   647	    # 8. VCP PATTERN BONUS (5 points) - Minervini's VCP Methodology
   648	    # ========================================================================
   649	    # Valid VCP patterns get bonus points as they indicate institutional accumulation
   650	    # and high-probability setup formation
   651	    vcp_bonus = 0
   652	
   653	    if vcp_data and vcp_data.get('is_vcp'):
   654	        # VCP detected - award bonus based on quality
   655	        vcp_quality = vcp_data.get('vcp_quality', 0)
   656	
   657	        if vcp_quality >= 80:
   658	            # Exceptional VCP (80-100 quality)
   659	            vcp_bonus = 5
   660	            reasons.append(f"⭐ VCP pattern: {vcp_data.get('pattern_details', 'N/A')} (quality: {vcp_quality:.0f}/100)")
   740	        fundamentals: Optional fundamental analysis dict
   741	
   742	    Returns:
   743	        Dict with sell signal score and details
   744	    """
   745	    phase = phase_info['phase']
   746	
   747	    # Only consider Phase 3 and Phase 4, or transitions from Phase 2
   748	    if phase not in [3, 4]:
   749	        return {
   750	            'ticker': ticker,
   751	            'is_sell': False,
   752	            'score': 0,
   753	            'severity': 'none',
   754	            'reason': f'No sell signal (Phase {phase})',
   755	            'details': {}
   756	        }
   757	
   758	    score = 0
   759	    details = {}
   760	    reasons = []
   761	
   762	    # 1. BREAKDOWN STRUCTURE (60 points)
   763	    breakdown_score = 0
   764	
   765	    sma_50 = phase_info.get('sma_50', 0)
   766	    sma_200 = phase_info.get('sma_200', 0)
   767	    slope_50 = phase_info.get('slope_50', 0)
   768	
   769	    # Phase transition
   770	    if previous_phase == 2 and phase in [3, 4]:
   771	        breakdown_score += 30
   772	        reasons.append(f'Phase transition: {previous_phase} -> {phase}')
   773	    elif phase == 4:
   774	        breakdown_score += 25
   775	        reasons.append('In Phase 4 (Downtrend)')
   776	    elif phase == 3:
   777	        breakdown_score += 15
   778	        reasons.append('In Phase 3 (Distribution)')
   779	
   780	    # Breakdown below 50 SMA
   781	    if current_price < sma_50:
   782	        pct_below = ((sma_50 - current_price) / sma_50) * 100
   783	        if pct_below > 5:
   784	            breakdown_score += 20
   785	            reasons.append(f'Broke below 50 SMA by {pct_below:.1f}%')
   786	        elif pct_below > 2:
   787	            breakdown_score += 15
   788	            reasons.append(f'Below 50 SMA by {pct_below:.1f}%')
   789	        else:
   790	            breakdown_score += 10
   791	            reasons.append(f'Just below 50 SMA ({pct_below:.1f}%)')
   792	
   793	        details['breakdown_level'] = round(sma_50, 2)
   794	
   795	    # Check if 50 SMA is turning down
   796	    if slope_50 < 0:
   797	        breakdown_score += 10
   798	        reasons.append(f'50 SMA declining (slope: {slope_50:.4f})')
   799	
   800	    score += min(breakdown_score, 60)
   801	    details['breakdown_score'] = min(breakdown_score, 60)
   802	
   803	    # 2. VOLUME CONFIRMATION (30 points)
   804	    volume_score = 0
   805	
   806	    if 'Volume' in price_data.columns and len(price_data) >= 20:
   807	        volume_ratio = calculate_volume_ratio(price_data['Volume'], 20)
   808	
   809	        # High volume on breakdown is bearish
   810	        if volume_ratio >= 1.5:
   811	            volume_score = 30
   812	            reasons.append(f'High volume breakdown: {volume_ratio:.1f}x')
   813	        elif volume_ratio >= 1.3:
   814	            volume_score = 20
   815	            reasons.append(f'Elevated volume: {volume_ratio:.1f}x')
   816	        elif volume_ratio >= 1.1:
   817	            volume_score = 10
   818	            reasons.append(f'Moderate volume: {volume_ratio:.1f}x')
   819	        else:
   820	            volume_score = 5
   821	            reasons.append(f'Low volume breakdown: {volume_ratio:.1f}x')
   822	
   823	        details['volume_ratio'] = round(volume_ratio, 2)
   824	
   825	    score += volume_score
   826	    details['volume_score'] = volume_score
   827	
   828	    # 3. RS WEAKNESS (10 points)
   829	    rs_score = 0
   830	
   831	    if len(rs_series) >= 15:
   832	        rs_slope = calculate_rs_slope(rs_series, 15)
   833	
   834	        if rs_slope < 0:
   835	            if rs_slope < -2.0:
   836	                rs_score = 10
   837	                reasons.append(f'Sharp RS decline: {rs_slope:.2f}')
   838	            elif rs_slope < -1.0:
   839	                rs_score = 7
   840	                reasons.append(f'RS declining: {rs_slope:.2f}')
   841	            else:
   842	                rs_score = 5
   843	                reasons.append(f'Weak RS rollover: {rs_slope:.2f}')
   844	        else:
   845	            rs_score = 0
   846	            reasons.append(f'RS still positive: {rs_slope:.2f}')
   847	
   848	        details['rs_slope'] = round(rs_slope, 3)
   849	
   850	    score += rs_score
   851	    details['rs_score'] = rs_score
   852	
   853	    # Check for failed breakout
   854	    close = price_data['Close']
   855	    if len(close) >= 20:
   856	        recent_high = close.iloc[-20:].max()
   857	        if recent_high > sma_50 and current_price < sma_50:
   858	            score += 10
   859	            reasons.append('Failed breakout - closed back inside base')
   860	
   861	    # Final score
   862	    final_score = max(0, min(score, 100))
   863	
   864	    # Determine severity
   865	    if final_score >= 80:
   866	        severity = 'critical'
   867	    elif final_score >= 70:
   868	        severity = 'high'
   869	    elif final_score >= 60:
   870	        severity = 'medium'
   871	    else:
   872	        severity = 'low'
   873	
   874	    # Determine if this is a valid sell signal (>= 60)
   875	    is_sell = final_score >= 60
   876	
   877	    return {
   878	        'ticker': ticker,
   879	        'is_sell': is_sell,
   880	        'score': round(final_score, 1),
   881	        'severity': severity,
   882	        'phase': phase,
   883	        'breakdown_level': details.get('breakdown_level'),
   884	        'reasons': reasons,
   885	        'details': details
   886	    }
   887	
   888	
   889	def format_signal_output(signal: Dict, signal_type: str = 'buy') -> str:
   890	    """Format signal for human-readable output.
   891	
   892	    Args:
   893	        signal: Signal dict from score_buy_signal or score_sell_signal
   894	        signal_type: 'buy' or 'sell'
   895	
   896	    Returns:
   897	        Formatted string
   898	    """
   899	    ticker = signal['ticker']
   900	    score = signal['score']
   901	    phase = signal['phase']
   902	
   903	    if signal_type == 'buy':
   904	        output = f"\n{'='*60}\n"
   905	        output += f"BUY SIGNAL: {ticker} | Score: {score}/100 | Phase {phase}\n"
   906	        output += f"{'='*60}\n"
   907	
   908	        if 'breakout_price' in signal and signal['breakout_price']:
   909	            output += f"Breakout Level: ${signal['breakout_price']:.2f}\n"
   910	
   911	        details = signal.get('details', {})
   912	        if 'rs_slope' in details:
   913	            output += f"RS Slope: {details['rs_slope']:.3f}\n"
   914	        if 'volume_ratio' in details:
   915	            output += f"Volume vs Avg: {details['volume_ratio']:.1f}x\n"
   916	        if 'distance_from_50sma' in details:
   917	            output += f"Distance from 50 SMA: {details['distance_from_50sma']:.1f}%\n"
   918	
   919	        output += f"\nReasons:\n"
   920	        for reason in signal['reasons']:
   921	            output += f"  • {reason}\n"
   922	
   923	    else:  # sell
   924	        severity = signal.get('severity', 'unknown')
   925	        output = f"\n{'='*60}\n"
   926	        output += f"SELL SIGNAL: {ticker} | Score: {score}/100 | Severity: {severity.upper()} | Phase {phase}\n"
   927	        output += f"{'='*60}\n"
   928	
   929	        if 'breakdown_level' in signal and signal['breakdown_level']:
   930	            output += f"Breakdown Level: ${signal['breakdown_level']:.2f}\n"
   931	
   932	        details = signal.get('details', {})
   933	        if 'rs_slope' in details:
   934	            output += f"RS Slope: {details['rs_slope']:.3f}\n"
   935	        if 'volume_ratio' in details:
   936	            output += f"Volume vs Avg: {details['volume_ratio']:.1f}x\n"
   937	
   938	        output += f"\nReasons:\n"
   939	        for reason in signal['reasons']:
   940	            output += f"  • {reason}\n"
   941	
   942	    return output
    40	    Returns:
    41	        Slope as percentage change per day
    42	    """
    43	    if len(series) < periods or series.isna().all():
    44	        return 0.0
    45	
    46	    recent = series.iloc[-periods:].dropna()
    47	    if len(recent) < 2:
    48	        return 0.0
    49	
    50	    # Linear regression slope
    51	    x = np.arange(len(recent))
    52	    y = recent.values
    53	
    54	    if np.std(x) == 0:
    55	        return 0.0
    56	
    57	    slope = np.polyfit(x, y, 1)[0]
    58	
    59	    # Convert to percentage per day
    60	    avg_price = np.mean(y)
    61	    if avg_price == 0:
    62	        return 0.0
    63	
    64	    slope_pct = (slope / avg_price) * 100
    65	
    66	    return slope_pct
    67	
    68	
    69	def calculate_relative_strength(stock_prices: pd.Series, spy_prices: pd.Series,
    70	                                  period: int = 63) -> pd.Series:
    71	    """Calculate Relative Strength vs SPY.
    72	
    73	    RS = (Stock Price / SPY Price) * 100
    74	
    75	    Args:
    76	        stock_prices: Stock closing prices
    77	        spy_prices: SPY closing prices
    78	        period: Period for RS calculation (default 63 = ~3 months)
    79	
    80	    Returns:
    81	        Series of RS values
    82	    """
    83	    if len(stock_prices) == 0 or len(spy_prices) == 0:
    84	        return pd.Series([np.nan] * len(stock_prices), index=stock_prices.index)
    85	
    86	    # Normalize indexes to timezone-naive DatetimeIndex to avoid comparison errors
    87	    # yfinance sometimes returns timezone-aware data, sometimes naive, sometimes RangeIndex
    88	    stock_prices = stock_prices.copy()
    89	    spy_prices = spy_prices.copy()
    90	
    91	    # Ensure both have DatetimeIndex (not RangeIndex)
    92	    if not isinstance(stock_prices.index, pd.DatetimeIndex):
    93	        logger.warning(f"Stock has non-DatetimeIndex: {type(stock_prices.index)}")
    94	        return pd.Series([np.nan] * len(stock_prices), index=stock_prices.index)
    95	
    96	    if not isinstance(spy_prices.index, pd.DatetimeIndex):
    97	        logger.warning(f"SPY has non-DatetimeIndex: {type(spy_prices.index)}")
    98	        return pd.Series([np.nan] * len(stock_prices), index=stock_prices.index)
    99	
   100	    # Remove timezone info if present (convert to timezone-naive)
   101	    if stock_prices.index.tz is not None:
   102	        stock_prices.index = stock_prices.index.tz_localize(None)
   103	
   104	    if spy_prices.index.tz is not None:
   105	        spy_prices.index = spy_prices.index.tz_localize(None)
   106	
   107	    # Align the series by DATE (not position) - stocks and SPY trade on same days
   108	    # Use reindex to align SPY to stock dates, then forward fill any gaps
   109	    spy_aligned = spy_prices.reindex(stock_prices.index, method='ffill')
   110	
   111	    # Check if we have valid aligned data
   112	    if spy_aligned.isna().all():
   113	        logger.warning("SPY alignment failed - all NaN after reindex")
   114	        return pd.Series([np.nan] * len(stock_prices), index=stock_prices.index)
   115	
   116	    # Calculate RS
   117	    rs = (stock_prices / spy_aligned) * 100
   118	
   119	    # Fill any remaining NaN with forward fill
   120	    rs = rs.ffill()
   121	
   122	    return rs
   123	
   124	
   125	def calculate_rs_slope(rs_series: pd.Series, periods: int = 15) -> float:
   126	    """Calculate the slope of RS over recent periods (3-week slope).
   127	
   128	    Args:
   129	        rs_series: Relative strength series
   130	        periods: Number of periods (default 15 = ~3 weeks)
   480	    sma_50 = phase_info.get('sma_50', 0)
   481	    sma_150 = phase_info.get('sma_150', 0)
   482	    sma_200 = phase_info.get('sma_200', 0)
   483	    week_52_high = phase_info.get('week_52_high', 0)
   484	    week_52_low = phase_info.get('week_52_low', 0)
   485	
   486	    criteria = {}
   487	    passed_count = 0
   488	
   489	    # Criterion 1: Price > 150 SMA AND 200 SMA
   490	    c1 = current_price > sma_150 and current_price > sma_200
   491	    criteria['price_above_150_200'] = c1
   492	    if c1:
   493	        passed_count += 1
   494	
   495	    # Criterion 2: 150 SMA > 200 SMA
   496	    c2 = sma_150 > sma_200
   497	    criteria['sma_150_above_200'] = c2
   498	    if c2:
   499	        passed_count += 1
   500	
   501	    # Criterion 3: 200 SMA trending up for at least 1 month
   502	    # Calculate 200 SMA slope over 20 days (1 month)
   503	    if len(sma_200_series) >= 20:
   504	        sma_200_1mo_ago = sma_200_series.iloc[-20]
   505	        sma_200_now = sma_200_series.iloc[-1]
   506	        sma_200_rising = sma_200_now > sma_200_1mo_ago
   507	    else:
   508	        sma_200_rising = phase_info.get('slope_200', 0) > 0
   509	
   510	    c3 = sma_200_rising
   511	    criteria['sma_200_rising'] = c3
   512	    if c3:
   513	        passed_count += 1
   514	
   515	    # Criterion 4: 50 SMA > 150 SMA (strongest configuration)
   516	    c4 = sma_50 > sma_150
   517	    criteria['sma_50_above_150'] = c4
   518	    if c4:
   519	        passed_count += 1
   520	
   521	    # Criterion 5: Price > 50 SMA
   522	    c5 = current_price > sma_50
   523	    criteria['price_above_50'] = c5
   524	    if c5:
   525	        passed_count += 1
   526	
   527	    # Criterion 6: Price at least 30% above 52-week low
   528	    if week_52_low > 0:
   529	        distance_from_52w_low = ((current_price - week_52_low) / week_52_low) * 100
   530	        c6 = distance_from_52w_low >= 30
   531	        criteria['price_30pct_above_52w_low'] = c6
   532	        criteria['distance_from_52w_low_pct'] = round(distance_from_52w_low, 1)
   533	    else:
   534	        c6 = False
   535	        criteria['price_30pct_above_52w_low'] = c6
   536	        criteria['distance_from_52w_low_pct'] = 0
   537	
   538	    if c6:
   539	        passed_count += 1
   540	
   541	    # Criterion 7: Price within 25% of 52-week high
   542	    if week_52_high > 0:
   543	        distance_from_52w_high = ((week_52_high - current_price) / week_52_high) * 100
   544	        c7 = distance_from_52w_high <= 25
   545	        criteria['price_near_52w_high'] = c7
   546	        criteria['distance_from_52w_high_pct'] = round(distance_from_52w_high, 1)
   547	    else:
   548	        c7 = False
   549	        criteria['price_near_52w_high'] = c7
   550	        criteria['distance_from_52w_high_pct'] = 100
   551	
   552	    if c7:
   553	        passed_count += 1
   554	
   555	    # Criterion 8: Phase must be 2 (our proxy for confirmed uptrend)
   556	    c8 = phase_info.get('phase') == 2
   557	    criteria['confirmed_stage_2'] = c8
   558	    if c8:
   559	        passed_count += 1
   560	
   561	    # Template score (0-100)
   562	    template_score = int((passed_count / 8) * 100)
   563	
   564	    # Passes template if 7 or 8 criteria met (Minervini uses strict standards)
   565	    passes_template = passed_count >= 7
   566	
   567	    return {
   568	        'passes_template': passes_template,
   569	        'criteria_passed': passed_count,
   570	        'criteria_total': 8,
   571	        'template_score': template_score,
   572	        'criteria_details': criteria
   573	    }
   574	
   575	
   576	def detect_vcp_pattern(price_data: pd.DataFrame, current_price: float,
   577	                        phase_info: Dict, min_contractions: int = 2,
   578	                        max_contractions: int = 6) -> Dict[str, any]:
   579	    """Detect Minervini's Volatility Contraction Pattern (VCP).
   580	

exec
/bin/zsh -lc "nl -ba scripts/backtest_top3.py; nl -ba scripts/backtest_top3_monte_carlo.py; nl -ba scripts/walk_forward_backtest.py | sed -n '1,393p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	#!/usr/bin/env python3
     2	"""Point-in-time backtest: what would the top-3 buy signals have been N days ago,
     3	and what would $1000 split across them be worth today?
     4	
     5	Critically, this feeds the real scoring engine only price data available THROUGH
     6	the as-of date (no look-ahead) — it does not just take today's picks and pretend
     7	they were made earlier, which would be look-ahead bias (today's picks are selected
     8	because they look good NOW; a week ago the algorithm may not have flagged them
     9	at all). Runs against a random sample of the universe, same approach as --test-mode.
    10	
    11	Usage:
    12	    python scripts/backtest_top3.py
    13	    python scripts/backtest_top3.py --days 7 --sample 150 --investment 1000
    14	"""
    15	
    16	import argparse
    17	import json
    18	import logging
    19	import random
    20	import sys
    21	from datetime import datetime, timedelta
    22	from pathlib import Path
    23	
    24	import pandas as pd
    25	import yfinance as yf
    26	
    27	sys.path.insert(0, str(Path(__file__).parent.parent))
    28	
    29	from src.data.universe_fetcher import USStockUniverseFetcher
    30	from src.screening.phase_indicators import classify_phase, calculate_relative_strength
    31	from src.screening.signal_engine import score_buy_signal
    32	from src.utils.json_safe import sanitize_nan
    33	
    34	logging.basicConfig(level=logging.WARNING)
    35	logger = logging.getLogger(__name__)
    36	
    37	
    38	def main():
    39	    parser = argparse.ArgumentParser()
    40	    parser.add_argument('--days', type=int, default=7, help='Lookback days for the as-of date')
    41	    parser.add_argument('--sample', type=int, default=150, help='Random ticker sample size')
    42	    parser.add_argument('--investment', type=float, default=1000.0, help='Total $ invested, split evenly')
    43	    parser.add_argument('--json-out', type=str, default=None,
    44	                         help='Optional path to also write structured JSON results (stdout output unchanged)')
    45	    args = parser.parse_args()
    46	
    47	    as_of = (datetime.now() - timedelta(days=args.days)).date()
    48	    print(f"Backtesting: what would the top-3 buy signals have been as of {as_of}?")
    49	    print(f"Using ONLY price data through {as_of} (no look-ahead) — random {args.sample}-ticker sample\n")
    50	
    51	    universe = USStockUniverseFetcher().fetch_universe()
    52	    sample = random.sample(universe, min(args.sample, len(universe)))
    53	
    54	    spy = yf.Ticker('SPY').history(period='2y')
    55	    spy.index = spy.index.tz_localize(None)
    56	    spy_asof = spy.loc[:pd.Timestamp(as_of)]
    57	
    58	    candidates = []
    59	    scanned, errors = 0, 0
    60	    for ticker in sample:
    61	        try:
    62	            hist = yf.Ticker(ticker).history(period='2y')
    63	            if hist.empty:
    64	                continue
    65	            hist.index = hist.index.tz_localize(None)
    66	            asof_data = hist.loc[:pd.Timestamp(as_of)]
    67	            if len(asof_data) < 200:
    68	                continue
    69	
    70	            current_price = asof_data['Close'].iloc[-1]
    71	            phase_info = classify_phase(asof_data, current_price)
    72	            if phase_info['phase'] not in [1, 2]:
    73	                continue
    74	
    75	            rs_series = calculate_relative_strength(asof_data['Close'], spy_asof['Close'], period=63)
    76	            signal = score_buy_signal(
    77	                ticker=ticker, price_data=asof_data, current_price=current_price,
    78	                phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
    79	            )
    80	
    81	            if signal['is_buy']:
    82	                today_price = hist['Close'].iloc[-1]
    83	                signal['entry_price_asof'] = float(current_price)
    84	                signal['current_price_today'] = float(today_price)
    85	                signal['return_pct'] = (today_price - current_price) / current_price * 100
    86	                candidates.append(signal)
    87	
    88	            scanned += 1
    89	        except Exception as e:
    90	            errors += 1
    91	            logger.debug(f"{ticker}: {e}")
    92	            continue
    93	
    94	    candidates.sort(key=lambda s: s['score'], reverse=True)
    95	    top3 = candidates[:3]
    96	
    97	    print(f"Scanned {scanned}/{len(sample)} tickers ({errors} errors/skipped).")
    98	    print(f"Found {len(candidates)} qualifying buy signals as of {as_of}.\n")
    99	
   100	    if not top3:
   101	        print("No qualifying buy signals found in this sample — try a larger --sample size.")
   102	        if args.json_out:
   103	            _write_json_out(args, as_of, scanned, len(candidates), [], 0.0, 0.0)
   104	        return
   105	
   106	    print(f"{'='*70}\nTOP 3 (as they would have been recommended on {as_of})\n{'='*70}\n")
   107	    per_stock = args.investment / len(top3)
   108	    total_value = 0.0
   109	
   110	    for i, s in enumerate(top3, 1):
   111	        shares = per_stock / s['entry_price_asof']
   112	        value_today = shares * s['current_price_today']
   113	        profit = value_today - per_stock
   114	        total_value += value_today
   115	
   116	        print(f"#{i} {s['ticker']} — score {s['score']}/125")
   117	        print(f"    Entry ({as_of}): ${s['entry_price_asof']:.2f}  ->  Today: ${s['current_price_today']:.2f}  ({s['return_pct']:+.2f}%)")
   118	        print(f"    ${per_stock:.2f} invested -> {shares:.4f} shares -> worth ${value_today:.2f} today (${profit:+.2f})")
   119	        print()
   120	
   121	    total_profit = total_value - args.investment
   122	    print(f"{'='*70}")
   123	    print(f"TOTAL: ${args.investment:.2f} invested -> ${total_value:.2f} today")
   124	    print(f"PROFIT/LOSS: ${total_profit:+.2f} ({total_profit/args.investment*100:+.2f}%)")
   125	    print(f"{'='*70}")
   126	    print("\nNote: small random sample of the universe, not the full ~3,800-stock scan —")
   127	    print("results will vary between runs. Not financial advice.")
   128	
   129	    if args.json_out:
   130	        _write_json_out(args, as_of, scanned, len(candidates), top3, total_value, total_profit)
   131	
   132	
   133	def _write_json_out(args, as_of, scanned, candidates_found, top3, total_value, total_profit):
   134	    """Optional structured JSON alongside the printed report — used by the GUI
   135	    dashboard's job runner. Never affects stdout output or the CLI/skill usage."""
   136	    out = {
   137	        'generated': datetime.now().isoformat(),
   138	        'as_of_date': str(as_of),
   139	        'days': args.days, 'sample': args.sample, 'investment': args.investment,
   140	        'scanned': scanned, 'candidates_found': candidates_found,
   141	        'picks': [
   142	            {
   143	                'ticker': s['ticker'], 'score': s['score'],
   144	                'entry_price': s['entry_price_asof'], 'exit_price': s['current_price_today'],
   145	                'return_pct': s['return_pct'],
   146	            } for s in top3
   147	        ],
   148	        'total_invested': args.investment, 'total_value_today': total_value,
   149	        'total_profit': total_profit,
   150	        'total_return_pct': (total_profit / args.investment * 100) if args.investment else 0.0,
   151	    }
   152	    out_path = Path(args.json_out)
   153	    out_path.parent.mkdir(parents=True, exist_ok=True)
   154	    out_path.write_text(json.dumps(sanitize_nan(out), indent=2, default=str))
   155	
   156	
   157	if __name__ == '__main__':
   158	    main()
     1	#!/usr/bin/env python3
     2	"""Monte Carlo version of backtest_top3.py: fetch + score a pool of tickers ONCE
     3	(point-in-time, no look-ahead, same as backtest_top3.py), then re-sample many
     4	different "top 3" portfolios from that same pool without re-fetching data.
     5	
     6	Scoring a ticker doesn't depend on which other tickers are in the sample (only on
     7	its own price history + SPY), so this is equivalent to running the single-shot
     8	backtest many times over fresh random draws, at a fraction of the network cost.
     9	
    10	Tradeoff: all iterations draw from the same fixed pool rather than fresh random
    11	tickers from the full universe each time, so iterations aren't fully independent
    12	of each other (less externally valid than truly independent draws) — but it's the
    13	only way to run this many iterations without hammering Yahoo Finance for an hour+.
    14	
    15	Usage:
    16	    python scripts/backtest_top3_monte_carlo.py --iterations 100 --pool 300 --sample 150
    17	"""
    18	
    19	import argparse
    20	import json
    21	import logging
    22	import random
    23	import sys
    24	from datetime import datetime, timedelta
    25	from pathlib import Path
    26	
    27	import pandas as pd
    28	import yfinance as yf
    29	
    30	sys.path.insert(0, str(Path(__file__).parent.parent))
    31	
    32	from src.data.universe_fetcher import USStockUniverseFetcher
    33	from src.screening.phase_indicators import classify_phase, calculate_relative_strength
    34	from src.screening.signal_engine import score_buy_signal
    35	from src.utils.json_safe import sanitize_nan
    36	
    37	logging.basicConfig(level=logging.WARNING)
    38	logger = logging.getLogger(__name__)
    39	
    40	
    41	def main():
    42	    parser = argparse.ArgumentParser()
    43	    parser.add_argument('--days', type=int, default=7)
    44	    parser.add_argument('--pool', type=int, default=300, help='Tickers to fetch+score once')
    45	    parser.add_argument('--sample', type=int, default=150, help='Tickers drawn per iteration')
    46	    parser.add_argument('--iterations', type=int, default=100)
    47	    parser.add_argument('--investment', type=float, default=1000.0)
    48	    parser.add_argument('--json-out', type=str, default=None,
    49	                         help='Optional path to also write structured JSON results (stdout output unchanged)')
    50	    args = parser.parse_args()
    51	
    52	    as_of = (datetime.now() - timedelta(days=args.days)).date()
    53	    print(f"Pre-fetching + scoring a pool of {args.pool} tickers as of {as_of} (one-time cost)...")
    54	
    55	    universe = USStockUniverseFetcher().fetch_universe()
    56	    pool_tickers = random.sample(universe, min(args.pool, len(universe)))
    57	
    58	    spy = yf.Ticker('SPY').history(period='2y')
    59	    spy.index = spy.index.tz_localize(None)
    60	    spy_asof = spy.loc[:pd.Timestamp(as_of)]
    61	
    62	    qualifiers = []  # tickers that were real buy signals as of as_of, with real forward return
    63	    for i, ticker in enumerate(pool_tickers):
    64	        try:
    65	            hist = yf.Ticker(ticker).history(period='2y')
    66	            if hist.empty:
    67	                continue
    68	            hist.index = hist.index.tz_localize(None)
    69	            asof_data = hist.loc[:pd.Timestamp(as_of)]
    70	            if len(asof_data) < 200:
    71	                continue
    72	
    73	            current_price = asof_data['Close'].iloc[-1]
    74	            phase_info = classify_phase(asof_data, current_price)
    75	            if phase_info['phase'] not in [1, 2]:
    76	                continue
    77	
    78	            rs_series = calculate_relative_strength(asof_data['Close'], spy_asof['Close'], period=63)
    79	            signal = score_buy_signal(
    80	                ticker=ticker, price_data=asof_data, current_price=current_price,
    81	                phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
    82	            )
    83	            if signal['is_buy']:
    84	                today_price = hist['Close'].iloc[-1]
    85	                signal['entry_price_asof'] = float(current_price)
    86	                signal['current_price_today'] = float(today_price)
    87	                signal['return_pct'] = (today_price - current_price) / current_price * 100
    88	                qualifiers.append(signal)
    89	        except Exception as e:
    90	            logger.debug(f"{ticker}: {e}")
    91	            continue
    92	
    93	        if (i + 1) % 100 == 0:
    94	            print(f"  ...{i + 1}/{len(pool_tickers)} scored")
    95	
    96	    print(f"\nPool scored: {len(qualifiers)} qualifying buy signals out of {len(pool_tickers)} tickers.\n")
    97	
    98	    # Does the score actually predict forward return? Pearson correlation.
    99	    corr = None
   100	    if len(qualifiers) >= 5:
   101	        scores = [s['score'] for s in qualifiers]
   102	        returns = [s['return_pct'] for s in qualifiers]
   103	        n = len(scores)
   104	        mean_s, mean_r = sum(scores) / n, sum(returns) / n
   105	        cov = sum((s - mean_s) * (r - mean_r) for s, r in zip(scores, returns))
   106	        std_s = (sum((s - mean_s) ** 2 for s in scores)) ** 0.5
   107	        std_r = (sum((r - mean_r) ** 2 for r in returns)) ** 0.5
   108	        corr = cov / (std_s * std_r) if std_s > 0 and std_r > 0 else 0.0
   109	        print(f"Score-vs-{args.days}-day-forward-return correlation among qualifiers: r = {corr:+.3f}")
   110	        print("(1.0 = score perfectly predicts return, 0 = no relationship, negative = higher score did worse)\n")
   111	
   112	    if len(qualifiers) < 3:
   113	        print("Not enough qualifiers in this pool to run iterations — try a bigger --pool.")
   114	        if args.json_out:
   115	            _write_json_out(args, as_of, len(qualifiers), corr, [])
   116	        return
   117	
   118	    qualifier_tickers = {s['ticker'] for s in qualifiers}
   119	    qualifiers_by_ticker = {s['ticker']: s for s in qualifiers}
   120	
   121	    print(f"Running {args.iterations} Monte Carlo draws of {args.sample} tickers each from the {args.pool}-ticker pool...\n")
   122	
   123	    results = []
   124	    for _ in range(args.iterations):
   125	        drawn = set(random.sample(pool_tickers, min(args.sample, len(pool_tickers))))
   126	        present_qualifiers = [qualifiers_by_ticker[t] for t in drawn if t in qualifier_tickers]
   127	        if not present_qualifiers:
   128	            continue
   129	        present_qualifiers.sort(key=lambda s: s['score'], reverse=True)
   130	        top3 = present_qualifiers[:3]
   131	
   132	        per_stock = args.investment / len(top3)
   133	        total_value = sum(
   134	            (per_stock / s['entry_price_asof']) * s['current_price_today'] for s in top3
   135	        )
   136	        profit = total_value - args.investment
   137	        results.append({
   138	            'tickers': [s['ticker'] for s in top3],
   139	            'total_value': total_value,
   140	            'profit': profit,
   141	            'profit_pct': profit / args.investment * 100,
   142	        })
   143	
   144	    if not results:
   145	        print("No iteration drew any qualifying tickers — try a bigger --sample or --pool.")
   146	        if args.json_out:
   147	            _write_json_out(args, as_of, len(qualifiers), corr, [])
   148	        return
   149	
   150	    profits = [r['profit'] for r in results]
   151	    profit_pcts = [r['profit_pct'] for r in results]
   152	    wins = sum(1 for p in profits if p > 0)
   153	    losses = sum(1 for p in profits if p < 0)
   154	
   155	    avg_profit = sum(profits) / len(profits)
   156	    avg_pct = sum(profit_pcts) / len(profit_pcts)
   157	    best = max(results, key=lambda r: r['profit'])
   158	    worst = min(results, key=lambda r: r['profit'])
   159	    sorted_pcts = sorted(profit_pcts)
   160	    median_pct = sorted_pcts[len(sorted_pcts) // 2]
   161	
   162	    print(f"{'='*70}")
   163	    print(f"RESULTS: {len(results)} valid iterations (as of {as_of}, {args.days} days ago)")
   164	    print(f"{'='*70}")
   165	    print(f"Win rate:        {wins}/{len(results)} ({wins/len(results)*100:.1f}%) profitable, {losses} losses")
   166	    print(f"Average result:  ${avg_profit:+.2f} ({avg_pct:+.2f}%) per $1,000")
   167	    print(f"Median result:   {median_pct:+.2f}%")
   168	    print(f"Best run:        {', '.join(best['tickers'])} -> ${best['profit']:+.2f} ({best['profit_pct']:+.2f}%)")
   169	    print(f"Worst run:       {', '.join(worst['tickers'])} -> ${worst['profit']:+.2f} ({worst['profit_pct']:+.2f}%)")
   170	    print(f"{'='*70}")
   171	    print("\nNote: iterations draw from a shared fixed pool (not fully independent),")
   172	    print("and this is a statistical illustration, not investment advice.")
   173	
   174	    if args.json_out:
   175	        _write_json_out(
   176	            args, as_of, len(qualifiers), corr, results,
   177	            win_rate=wins / len(results) * 100, avg_profit=avg_profit, avg_pct=avg_pct,
   178	            median_pct=median_pct, best=best, worst=worst,
   179	        )
   180	
   181	
   182	def _write_json_out(args, as_of, qualifiers_found, corr, results, **stats):
   183	    """Optional structured JSON alongside the printed report — used by the GUI
   184	    dashboard's job runner. Never affects stdout output or the CLI usage."""
   185	    out = {
   186	        'generated': datetime.now().isoformat(),
   187	        'as_of_date': str(as_of),
   188	        'days': args.days, 'pool': args.pool, 'sample': args.sample,
   189	        'iterations': args.iterations, 'investment': args.investment,
   190	        'qualifiers_found': qualifiers_found,
   191	        'score_return_correlation': corr,
   192	        'iterations_run': len(results),
   193	        **stats,
   194	    }
   195	    out_path = Path(args.json_out)
   196	    out_path.parent.mkdir(parents=True, exist_ok=True)
   197	    out_path.write_text(json.dumps(sanitize_nan(out), indent=2, default=str))
   198	
   199	
   200	if __name__ == '__main__':
   201	    main()
     1	#!/usr/bin/env python3
     2	"""Walk-forward backtest: the rigorous version.
     3	
     4	Fixes the weaknesses of scripts/backtest_top3*.py (single/few time windows, top-3
     5	concentration, fixed-N-day snapshot exits, fresh random samples each run):
     6	
     7	1. Walks a FIXED ticker universe through MANY historical entry dates (not one),
     8	   spanning real bull/correction/choppy stretches, not one arbitrary week.
     9	2. Takes the top N (default 10) picks per period, not top 3.
    10	3. Each ticker's full price history is fetched ONCE and reused across every
    11	   walk-forward date (in-memory slicing) — network cost stays bounded to the
    12	   universe size regardless of how many periods are tested.
    13	4. Trades exit on REAL rules — stop-loss breach (intraday low), a Phase 3/4
    14	   breakdown (re-running the actual phase classifier day-by-day going forward),
    15	   or a max holding period cap, whichever comes first.
    16	5. Reports win rate, avg win/loss, max drawdown, and a Sharpe-like consistency
    17	   ratio across ALL trades — not one dollar figure from one basket.
    18	6. --seed makes runs REPRODUCIBLE (same universe sample every time) — the
    19	   previous version resampled randomly on every invocation, so "rerun the same
    20	   command" silently tested different stocks. Default seed is fixed; pass
    21	   --seed 0 (or any int) explicitly to compare specific runs, or omit --seed
    22	   entirely for a fresh random draw when you want that instead.
    23	7. Tracks each trade's individual scoring COMPONENTS (trend/fundamental/entry/
    24	   R:R/RS/volume) at entry time, and reports each component's correlation with
    25	   realized return — this is what scripts/backtest_critic.py compares between
    26	   runs to detect drift.
    27	8. Saves full structured results to data/backtest_history/ as JSON, so future
    28	   runs have a baseline to compare against.
    29	
    30	Usage:
    31	    python scripts/walk_forward_backtest.py
    32	    python scripts/walk_forward_backtest.py --universe-size 3800 --lookback-months 12 \
    33	        --step-days 14 --top-n 15 --max-hold-days 60 --seed 42
    34	"""
    35	
    36	import argparse
    37	import json
    38	import logging
    39	import random
    40	import statistics
    41	import sys
    42	from datetime import date, datetime, timedelta
    43	from pathlib import Path
    44	
    45	import pandas as pd
    46	import yfinance as yf
    47	
    48	sys.path.insert(0, str(Path(__file__).parent.parent))
    49	
    50	from src.data.universe_fetcher import USStockUniverseFetcher
    51	from src.screening.phase_indicators import classify_phase, calculate_relative_strength
    52	from src.screening.signal_engine import score_buy_signal
    53	from src.utils.json_safe import sanitize_nan
    54	
    55	logging.basicConfig(level=logging.WARNING)
    56	logger = logging.getLogger(__name__)
    57	
    58	COMPONENTS = ['trend_score', 'fundamental_score', 'entry_score', 'rr_score', 'rs_score', 'volume_score']
    59	HISTORY_DIR = Path(__file__).parent.parent / "data" / "backtest_history"
    60	
    61	
    62	def pearson(xs, ys):
    63	    n = len(xs)
    64	    if n < 5:
    65	        return None
    66	    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    67	    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    68	    std_x = (sum((x - mean_x) ** 2 for x in xs)) ** 0.5
    69	    std_y = (sum((y - mean_y) ** 2 for y in ys)) ** 0.5
    70	    return cov / (std_x * std_y) if std_x > 0 and std_y > 0 else None
    71	
    72	
    73	def simulate_trade(hist: pd.DataFrame, entry_date: pd.Timestamp, entry_price: float,
    74	                    stop_loss: float, max_hold_days: int) -> dict:
    75	    """Walk forward day-by-day using REAL subsequent price data already in memory.
    76	    Exits on stop-loss breach, a Phase 3/4 breakdown, or max_hold_days — first wins."""
    77	    future = hist.loc[hist.index > entry_date].iloc[:max_hold_days]
    78	    if future.empty:
    79	        return None
    80	
    81	    for i in range(len(future)):
    82	        day = future.index[i]
    83	        row = future.iloc[i]
    84	
    85	        if stop_loss and row['Low'] <= stop_loss:
    86	            return {'exit_price': stop_loss, 'exit_reason': 'stop_loss', 'days_held': i + 1, 'exit_date': day}
    87	
    88	        if i > 0 and i % 3 == 0:
    89	            data_through_today = hist.loc[:day]
    90	            if len(data_through_today) >= 200:
    91	                phase_info = classify_phase(data_through_today, row['Close'])
    92	                if phase_info['phase'] in [3, 4]:
    93	                    return {'exit_price': row['Close'], 'exit_reason': 'sell_signal', 'days_held': i + 1, 'exit_date': day}
    94	
    95	    last = future.iloc[-1]
    96	    return {'exit_price': last['Close'], 'exit_reason': 'max_hold', 'days_held': len(future), 'exit_date': future.index[-1]}
    97	
    98	
    99	def compute_max_drawdown(trades: list, investment_per_trade: float) -> dict:
   100	    """Builds a cumulative P&L curve ordered by EXIT date (when P&L is realized)
   101	    and finds the largest peak-to-trough decline.
   102	
   103	    Simplifying assumption, stated plainly: this treats every trade as an
   104	    independent $investment_per_trade position (not a single compounding
   105	    account), and orders by exit date even though trades can overlap in time
   106	    (a new batch can open while an earlier one is still held). It's an
   107	    approximation of "how much could you be down at once," not a literal
   108	    portfolio equity curve — good enough to catch a strategy that has ugly
   109	    losing streaks, not precise enough to use for real position sizing.
   110	    """
   111	    if not trades:
   112	        return {'max_drawdown_pct': 0, 'max_drawdown_dollars': 0}
   113	
   114	    ordered = sorted(trades, key=lambda t: t['exit_date'])
   115	    cumulative = 0.0
   116	    peak = 0.0
   117	    max_dd_dollars = 0.0
   118	    for t in ordered:
   119	        cumulative += t['dollar_pnl']
   120	        peak = max(peak, cumulative)
   121	        max_dd_dollars = max(max_dd_dollars, peak - cumulative)
   122	
   123	    total_invested = len(trades) * investment_per_trade
   124	    return {
   125	        'max_drawdown_pct': (max_dd_dollars / total_invested * 100) if total_invested else 0,
   126	        'max_drawdown_dollars': max_dd_dollars,
   127	    }
   128	
   129	
   130	def audit_fundamentals_for_trades(all_trades: list, sample_size: int, seed: int) -> None:
   131	    """Point-in-time Fundamentals Auditor pass over a (sampled) subset of trades —
   132	    mutates each sampled trade in place with a 'fundamentals_audit_score' field.
   133	
   134	    This is genuinely point-in-time (not look-ahead-biased): audit_asof() only
   135	    considers SEC filings that were actually filed before that trade's entry date.
   136	    Catalyst Sentiment can't get the same treatment — yfinance's news feed has no
   137	    historical archive, so scoring today's news against an old trade would be
   138	    look-ahead bias. That agent instead just logs going forward (see
   139	    src/agents/catalyst_sentiment.py + the daily email wiring) until enough real
   140	    point-in-time history accumulates on its own.
   141	
   142	    Real Claude API calls + SEC fetches, one per sampled trade — slow (each audit
   143	    took ~15-50s in testing) and not free (~$0.05-0.15/call on claude-opus-5), which
   144	    is why this is capped to `sample_size` trades by default rather than all of them.
   145	    """
   146	    from src.agents.fundamentals_auditor import FundamentalsAuditor, flags_to_score
   147	
   148	    auditor = FundamentalsAuditor()
   149	    if not auditor.available:
   150	        print("\n--audit-fundamentals requested but ANTHROPIC_API_KEY isn't set — skipping.")
   151	        return
   152	
   153	    rng = random.Random(seed)
   154	    sampled = all_trades if sample_size >= len(all_trades) else rng.sample(all_trades, sample_size)
   155	
   156	    print(f"\nAuditing fundamentals (point-in-time) for {len(sampled)}/{len(all_trades)} trades "
   157	          f"— this makes real Claude API calls, expect it to be slow...")
   158	    for i, trade in enumerate(sampled):
   159	        entry_date = date.fromisoformat(trade['period'])
   160	        result = auditor.audit_asof(trade['ticker'], entry_date)
   161	        trade['fundamentals_audit_score'] = flags_to_score(result['audit']) if result['audited'] else None
   162	        if (i + 1) % 10 == 0:
   163	            print(f"  ...{i + 1}/{len(sampled)} audited")
   164	
   165	
   166	def run_walk_forward(universe_size: int, lookback_months: int, step_days: int, top_n: int,
   167	                      max_hold_days: int, investment_per_trade: float, seed: int,
   168	                      audit_fundamentals: bool = False, audit_sample_size: int = 40) -> dict:
   169	    if seed is not None:
   170	        random.seed(seed)
   171	
   172	    latest_entry = date.today() - timedelta(days=max_hold_days)
   173	    earliest_entry = latest_entry - timedelta(days=lookback_months * 30)
   174	    entry_dates = []
   175	    d = earliest_entry
   176	    while d <= latest_entry:
   177	        entry_dates.append(d)
   178	        d += timedelta(days=step_days)
   179	
   180	    print(f"Walk-forward backtest: {len(entry_dates)} entry dates from {earliest_entry} to {latest_entry}")
   181	    print(f"Universe size: {universe_size} (seed={seed}), top {top_n} picks/date, max {max_hold_days}-day hold\n")
   182	
   183	    universe = USStockUniverseFetcher().fetch_universe()
   184	    sample = universe if universe_size >= len(universe) else random.sample(universe, universe_size)
   185	
   186	    spy = yf.Ticker('SPY').history(period='2y')
   187	    spy.index = spy.index.tz_localize(None)
   188	
   189	    print(f"Fetching price history for {len(sample)} tickers (one-time cost — this is the slow part)...")
   190	    histories = {}
   191	    for i, ticker in enumerate(sample):
   192	        try:
   193	            h = yf.Ticker(ticker).history(period='2y')
   194	            if h.empty or len(h) < 200:
   195	                continue
   196	            h.index = h.index.tz_localize(None)
   197	            histories[ticker] = h
   198	        except Exception as e:
   199	            logger.debug(f"{ticker}: {e}")
   200	        if (i + 1) % 100 == 0:
   201	            print(f"  ...{i + 1}/{len(sample)} fetched, {len(histories)} usable")
   202	
   203	    print(f"\n{len(histories)} tickers usable. Walking forward through {len(entry_dates)} dates...\n")
   204	
   205	    all_trades = []
   206	    for period_i, entry_date_d in enumerate(entry_dates):
   207	        entry_ts = pd.Timestamp(entry_date_d)
   208	        spy_asof = spy.loc[:entry_ts]
   209	        if len(spy_asof) < 63:
   210	            continue
   211	
   212	        candidates = []
   213	        for ticker, hist in histories.items():
   214	            asof_data = hist.loc[:entry_ts]
   215	            if len(asof_data) < 200:
   216	                continue
   217	            current_price = asof_data['Close'].iloc[-1]
   218	            phase_info = classify_phase(asof_data, current_price)
   219	            if phase_info['phase'] != 2:
   220	                continue
   221	            rs_series = calculate_relative_strength(asof_data['Close'], spy_asof['Close'], period=63)
   222	            signal = score_buy_signal(
   223	                ticker=ticker, price_data=asof_data, current_price=current_price,
   224	                phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
   225	            )
   226	            if signal['is_buy']:
   227	                candidates.append((signal, current_price, hist))
   228	
   229	        candidates.sort(key=lambda c: c[0]['score'], reverse=True)
   230	        picks = candidates[:top_n]
   231	
   232	        for signal, entry_price, hist in picks:
   233	            result = simulate_trade(hist, entry_ts, entry_price, signal.get('stop_loss'), max_hold_days)
   234	            if result is None:
   235	                continue
   236	            return_pct = (result['exit_price'] - entry_price) / entry_price * 100
   237	            trade = {
   238	                'period': entry_date_d.isoformat(), 'ticker': signal['ticker'], 'score': signal['score'],
   239	                'entry_price': entry_price, 'exit_price': result['exit_price'],
   240	                'exit_reason': result['exit_reason'], 'days_held': result['days_held'],
   241	                'exit_date': result['exit_date'], 'return_pct': return_pct,
   242	                'dollar_pnl': investment_per_trade * (return_pct / 100),
   243	            }
   244	            for comp in COMPONENTS:
   245	                trade[comp] = (signal.get('details') or {}).get(comp, 0) or 0
   246	            all_trades.append(trade)
   247	
   248	        if (period_i + 1) % 5 == 0:
   249	            print(f"  ...{period_i + 1}/{len(entry_dates)} periods walked, {len(all_trades)} trades so far")
   250	
   251	    if audit_fundamentals and all_trades:
   252	        audit_fundamentals_for_trades(all_trades, audit_sample_size, seed or 0)
   253	
   254	    # Component correlations (needed by backtest_critic.py to detect drift between runs)
   255	    component_correlations = {}
   256	    if len(all_trades) >= 5:
   257	        returns = [t['return_pct'] for t in all_trades]
   258	        for comp in ['score'] + COMPONENTS:
   259	            vals = [t[comp] for t in all_trades]
   260	            component_correlations[comp] = pearson(vals, returns)
   261	
   262	        audited = [t for t in all_trades if t.get('fundamentals_audit_score') is not None]
   263	        if len(audited) >= 5:
   264	            component_correlations['fundamentals_audit_score'] = pearson(
   265	                [t['fundamentals_audit_score'] for t in audited],
   266	                [t['return_pct'] for t in audited],
   267	            )
   268	
   269	    drawdown = compute_max_drawdown(all_trades, investment_per_trade)
   270	
   271	    summary = {}
   272	    if all_trades:
   273	        returns = [t['return_pct'] for t in all_trades]
   274	        wins = [r for r in returns if r > 0]
   275	        losses = [r for r in returns if r <= 0]
   276	        std_return = statistics.stdev(returns) if len(returns) > 1 else 0
   277	        exit_reasons = {}
   278	        for t in all_trades:
   279	            exit_reasons[t['exit_reason']] = exit_reasons.get(t['exit_reason'], 0) + 1
   280	
   281	        summary = {
   282	            'total_trades': len(all_trades),
   283	            'total_periods': len(entry_dates),
   284	            'win_rate_pct': len(wins) / len(returns) * 100,
   285	            'avg_return_pct': statistics.mean(returns),
   286	            'median_return_pct': statistics.median(returns),
   287	            'avg_win_pct': statistics.mean(wins) if wins else None,
   288	            'avg_loss_pct': statistics.mean(losses) if losses else None,
   289	            'std_return_pct': std_return,
   290	            'sharpe_like': (statistics.mean(returns) / std_return) if std_return > 0 else 0,
   291	            'avg_days_held': statistics.mean(t['days_held'] for t in all_trades),
   292	            'exit_reasons': exit_reasons,
   293	            **drawdown,
   294	        }
   295	
   296	    # exit_date isn't JSON-serializable (Timestamp) — stringify before saving/returning
   297	    for t in all_trades:
   298	        t['exit_date'] = str(t['exit_date'])
   299	
   300	    return {
   301	        'generated': datetime.now().isoformat(),
   302	        'params': {
   303	            'universe_size': universe_size, 'lookback_months': lookback_months,
   304	            'step_days': step_days, 'top_n': top_n, 'max_hold_days': max_hold_days,
   305	            'investment_per_trade': investment_per_trade, 'seed': seed,
   306	        },
   307	        'summary': summary,
   308	        'component_correlations': component_correlations,
   309	        'trades': all_trades,
   310	    }
   311	
   312	
   313	def print_report(result: dict):
   314	    summary = result['summary']
   315	    if not summary:
   316	        print("No trades generated — try a bigger --universe-size or longer --lookback-months.")
   317	        return
   318	
   319	    print(f"\n{'='*78}")
   320	    print(f"RESULTS: {summary['total_trades']} total trades across {summary['total_periods']} periods")
   321	    print(f"{'='*78}\n")
   322	    print(f"Win rate:              {summary['win_rate_pct']:.1f}%")
   323	    print(f"Average return/trade:  {summary['avg_return_pct']:+.2f}%")
   324	    print(f"Median return/trade:   {summary['median_return_pct']:+.2f}%")
   325	    print(f"Avg win:               {summary['avg_win_pct']:+.2f}%" if summary['avg_win_pct'] is not None else "Avg win: n/a")
   326	    print(f"Avg loss:              {summary['avg_loss_pct']:+.2f}%" if summary['avg_loss_pct'] is not None else "Avg loss: n/a")
   327	    print(f"Return std dev:        {summary['std_return_pct']:.2f}%")
   328	    print(f"Sharpe-like ratio:     {summary['sharpe_like']:.3f}")
   329	    print(f"Max drawdown:          {summary['max_drawdown_pct']:.2f}% (${summary['max_drawdown_dollars']:,.2f})")
   330	    print(f"Avg days held:         {summary['avg_days_held']:.1f}")
   331	    print(f"Exit reasons:          {summary['exit_reasons']}")
   332	
   333	    print(f"\n{'='*78}")
   334	    print("COMPONENT CORRELATIONS (each component's value at entry vs. realized return)")
   335	    print(f"{'='*78}")
   336	    for comp, r in result['component_correlations'].items():
   337	        r_str = f"{r:+.3f}" if r is not None else "n/a"
   338	        print(f"  {comp:<20} r = {r_str}")
   339	
   340	
   341	def save_result(result: dict) -> Path:
   342	    # sanitize_nan: this feeds the dashboard's Backtests view directly — a
   343	    # stray NaN anywhere in here (e.g. a correlation computed over too few
   344	    # points) would otherwise serialize as an invalid `NaN` JSON token that
   345	    # silently breaks JSON.parse() in the browser.
   346	    result = sanitize_nan(result)
   347	    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
   348	    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
   349	    path = HISTORY_DIR / f"walk_forward_{timestamp}.json"
   350	    with open(path, 'w') as f:
   351	        json.dump(result, f, indent=2, default=str)
   352	    latest_path = HISTORY_DIR / "latest.json"
   353	    with open(latest_path, 'w') as f:
   354	        json.dump(result, f, indent=2, default=str)
   355	    return path
   356	
   357	
   358	def main():
   359	    parser = argparse.ArgumentParser()
   360	    parser.add_argument('--universe-size', type=int, default=250,
   361	                         help='Ticker sample size. Set to 3800+ (or any value >= universe size) for the full universe.')
   362	    parser.add_argument('--lookback-months', type=int, default=9)
   363	    parser.add_argument('--step-days', type=int, default=14)
   364	    parser.add_argument('--top-n', type=int, default=10)
   365	    parser.add_argument('--max-hold-days', type=int, default=60)
   366	    parser.add_argument('--investment-per-trade', type=float, default=1000.0)
   367	    parser.add_argument('--seed', type=int, default=42,
   368	                         help='Fixed by default so reruns are reproducible. Omit for a fresh random draw.')
   369	    parser.add_argument('--no-seed', action='store_true', help='Disable the fixed seed for a fresh random draw.')
   370	    parser.add_argument('--audit-fundamentals', action='store_true',
   371	                         help='Run the point-in-time Fundamentals Auditor (real Claude API calls) against a '
   372	                              'sample of the resulting trades and report its correlation with realized return. '
   373	                              'Needs ANTHROPIC_API_KEY; slow (~15-50s/trade) and not free — see --audit-sample-size.')
   374	    parser.add_argument('--audit-sample-size', type=int, default=40,
   375	                         help='Max trades to run through --audit-fundamentals (default 40, randomly sampled). '
   376	                              'Set >= total trade count to audit all of them (slow/costly at full scale).')
   377	    args = parser.parse_args()
   378	
   379	    result = run_walk_forward(
   380	        universe_size=args.universe_size, lookback_months=args.lookback_months,
   381	        step_days=args.step_days, top_n=args.top_n, max_hold_days=args.max_hold_days,
   382	        investment_per_trade=args.investment_per_trade, seed=None if args.no_seed else args.seed,
   383	        audit_fundamentals=args.audit_fundamentals, audit_sample_size=args.audit_sample_size,
   384	    )
   385	
   386	    print_report(result)
   387	    path = save_result(result)
   388	    print(f"\nFull results + component correlations saved to {path}")
   389	    print("(also copied to data/backtest_history/latest.json for backtest_critic.py to compare against)")
   390	
   391	
   392	if __name__ == '__main__':
   393	    main()

exec
/bin/zsh -lc "rg -n \"backtest|investment|iterations|live|startJob|poll|group|fetch\\(\" templates/dashboard.html static/js/dashboard.js | sed -n '1,360p'; nl -ba static/js/dashboard.js | sed -n '130,240p'; nl -ba static/js/dashboard.js | sed -n '680,850p'; nl -ba templates/dashboard.html | sed -n '480,720p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
static/js/dashboard.js:2:// (no router library), fetch() for data, Chart.js (via charts.js) for charts.
static/js/dashboard.js:12:  backtests: { title: 'Backtests', render: renderBacktestsView },
static/js/dashboard.js:43:// "live" here means: while a view that supports it is open, quietly re-pull
static/js/dashboard.js:45:// change so a background view never keeps polling once you've navigated away.
static/js/dashboard.js:48:let _liveTimer = null;
static/js/dashboard.js:51:  if (_liveTimer) { clearInterval(_liveTimer); _liveTimer = null; }
static/js/dashboard.js:55:  _liveTimer = setInterval(fn, LIVE_INTERVAL_MS);
static/js/dashboard.js:57:function liveBadgeHTML() {
static/js/dashboard.js:58:  return '<span class="live-badge"><span class="live-dot"></span>Live — updates every 90s</span>';
static/js/dashboard.js:61:// If a live-refresh tick's job hasn't finished by the time the next tick
static/js/dashboard.js:64:const _liveInFlight = new Set();
static/js/dashboard.js:65:async function _liveGuarded(key, fn) {
static/js/dashboard.js:66:  if (_liveInFlight.has(key)) return;
static/js/dashboard.js:67:  _liveInFlight.add(key);
static/js/dashboard.js:71:    _liveInFlight.delete(key);
static/js/dashboard.js:78:// a live refresh instead of collapsing every cycle.
static/js/dashboard.js:88:// already open before this render (e.g. across a live refresh).
static/js/dashboard.js:118:// For a silent live refresh where the cards themselves aren't re-rendered
static/js/dashboard.js:146:async function loadMomentumStatus(tickers, group, onLoaded) {
static/js/dashboard.js:148:  await startJob('momentum-status', { tickers, group }, async (st) => {
static/js/dashboard.js:150:    const data = await fetchJSON(`/api/momentum-status/${group}`);
static/js/dashboard.js:165:  const res = await fetch(url, opts);
static/js/dashboard.js:243:async function startJob(kind, body, onUpdate) {
static/js/dashboard.js:247:  const poll = async () => {
static/js/dashboard.js:251:      setTimeout(poll, 1500);
static/js/dashboard.js:254:  poll();
static/js/dashboard.js:279:const _watchingJobIds = {}; // cardId -> job_id an active setTimeout poll loop is already chasing
static/js/dashboard.js:283:  // Reconnecting to a job you're already polling (e.g. navigating back and
static/js/dashboard.js:285:  // chain each time — same end state, just wasted polling. The next tick of
static/js/dashboard.js:290:  const poll = async () => {
static/js/dashboard.js:305:    // itself keeps running server-side regardless; we'll catch up next poll,
static/js/dashboard.js:323:      setTimeout(poll, 1500);
static/js/dashboard.js:337:  poll();
static/js/dashboard.js:431:    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
static/js/dashboard.js:432:    _liveGuarded('shortlist-news', () => loadShortlistNews(tickers, true));
static/js/dashboard.js:433:    _liveGuarded('shortlist-momentum', () => loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap)));
static/js/dashboard.js:447:  await startJob('price-history', { tickers, group: 'shortlist' }, async (st) => {
static/js/dashboard.js:534:    _liveGuarded('market-news', () => loadMarketNews(true));
static/js/dashboard.js:535:    _liveGuarded('market-momentum', () => loadMomentumStatus(
static/js/dashboard.js:561:function _newsSectionHTML(group, title, bodyHTML) {
static/js/dashboard.js:562:  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
static/js/dashboard.js:565:async function _loadNewsGroup(group, tickers, emptyMsg, silent) {
static/js/dashboard.js:566:  const bodyEl = document.getElementById(`news-${group}-body`);
static/js/dashboard.js:576:  await startJob('news', { tickers, group }, async (st) => {
static/js/dashboard.js:577:    const el = document.getElementById(`news-${group}-body`);
static/js/dashboard.js:580:      const data = await fetchJSON(`/api/news/${group}`);
static/js/dashboard.js:658:  // Stashed at module scope (not a local var) so the live-refresh closure set
static/js/dashboard.js:755:    pageMeta.innerHTML = liveBadgeHTML();
static/js/dashboard.js:757:    _startLive(() => _liveGuarded('positions', refreshPositionsLive));
static/js/dashboard.js:762:// Silent live refresh: re-runs the (cheap, yfinance-only) positions analysis
static/js/dashboard.js:766:  await startJob('positions', {}, async (st) => {
static/js/dashboard.js:795:      const uploadRes = await fetch('/api/positions/upload', { method: 'POST', body: form }).then(r => r.json());
static/js/dashboard.js:814:    await startJob('positions', {}, async (st) => {
static/js/dashboard.js:898:  const history = await fetchJSON('/api/backtest/history');
static/js/dashboard.js:899:  if (_currentView !== 'backtests') return; // navigated away before this resolved
static/js/dashboard.js:909:      <select class="scan-select" id="backtestSelect">
static/js/dashboard.js:913:    <div id="backtestBody"></div>`;
static/js/dashboard.js:914:  const sel = document.getElementById('backtestSelect');
static/js/dashboard.js:927:    path ? fetchJSON('/api/backtest/run?path=' + encodeURIComponent(path)) : fetchJSON('/api/backtest/latest'),
static/js/dashboard.js:928:    fetchJSON('/api/backtest/trades' + (path ? '?path=' + encodeURIComponent(path) : '')),
static/js/dashboard.js:930:  if (_currentView !== 'backtests') return; // navigated away before this resolved
static/js/dashboard.js:935:    document.getElementById('backtestBody').innerHTML = `
static/js/dashboard.js:936:      <div class="no-data"><h2>No backtest history yet</h2><p>Run a Walk-Forward simulation from the Run Simulation page.</p></div>`;
static/js/dashboard.js:941:  document.getElementById('backtestBody').innerHTML = `
static/js/dashboard.js:1004:        <label>Investment $<input type="number" id="top3-investment" value="1000"></label>
static/js/dashboard.js:1010:        <label>Iterations<input type="number" id="mc-iterations" value="100"></label>
static/js/dashboard.js:1012:      ${jobCardHTML('wf', 'Full Walk-Forward', 'Rigorous multi-period backtest — walks a fixed universe through many historical dates. Slow (minutes+).', `
static/js/dashboard.js:1020:  wireJobCard('top3', 'backtest-top3', () => ({
static/js/dashboard.js:1023:    investment: +document.getElementById('top3-investment').value,
static/js/dashboard.js:1026:    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
static/js/dashboard.js:1033:  wireJobCard('mc', 'backtest-monte-carlo', () => ({
static/js/dashboard.js:1037:    iterations: +document.getElementById('mc-iterations').value,
static/js/dashboard.js:1040:    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
static/js/dashboard.js:1041:    if (res.error || !res.iterations_run) { resultEl.innerHTML = '<div style="color:var(--muted);font-size:13px">Not enough qualifiers found.</div>'; return; }
static/js/dashboard.js:1044:      over ${res.iterations_run} iterations${res.score_return_correlation != null ? ` · score/return correlation r=${res.score_return_correlation.toFixed(3)}` : ''}</div>`;
static/js/dashboard.js:1053:    resultEl.innerHTML = `<a href="#/backtests" class="btn primary">View results →</a>`;
templates/dashboard.html:27:    <a href="#/backtests" class="nav-item" data-view="backtests">
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
   188	function toggleReasons(btn) {
   189	  const extra = btn.previousElementSibling;
   190	  if (extra.style.display === 'none') {
   191	    extra.style.display = '';
   192	    btn.textContent = 'less';
   193	  } else {
   194	    extra.style.display = 'none';
   195	  }
   196	}
   197	
   198	function fidelityLink(ticker, label, cls) {
   199	  return `<a class="trade-link ${cls}" href="https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol=${ticker}" target="_blank" rel="noopener">${label} ↗</a>`;
   200	}
   201	
   202	// Agent badges — same color logic as src/notifications/email_notifier.py
   203	// (_catalyst_badge_html / _congress_badge_html / _fundamentals_flags_html) so
   204	// the dashboard and the email read consistently.
   205	
   206	function catalystBadgeHTML(sentiment) {
   207	  if (!sentiment) return '';
   208	  const score = sentiment.catalyst_score || 0;
   209	  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
   210	  const ctype = (sentiment.catalyst_type || 'other').replace(/_/g, ' ');
   211	  const sign = score > 0 ? '+' : '';
   212	  return `<div><span class="agent-badge ${cls}">Catalyst ${sign}${score} — ${ctype}</span>
   213	    <div class="agent-badge-sub">${sentiment.summary || ''}</div></div>`;
   214	}
   215	
   216	function congressBadgeHTML(signal) {
   217	  if (!signal || !signal.has_data) return '';
   218	  const score = signal.score || 0;
   219	  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
   220	  const sign = score > 0 ? '+' : '';
   221	  return `<div><span class="agent-badge ${cls}">Congress ${sign}${score.toFixed(1)}</span>
   222	    <div class="agent-badge-sub">${signal.summary || ''}</div></div>`;
   223	}
   224	
   225	function fundamentalsFlagsHTML(audit) {
   226	  if (!audit) return '';
   227	  const red = audit.red_flags || [];
   228	  const green = audit.green_flags || [];
   229	  let html = '';
   230	  if (red.length) {
   231	    const more = red.length > 1 ? ` (+${red.length - 1} more)` : '';
   232	    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${red[0].flag}${more}</div>`;
   233	  }
   234	  if (green.length) {
   235	    const more = green.length > 1 ? ` (+${green.length - 1} more)` : '';
   236	    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${green[0].flag}${more}</div>`;
   237	  }
   238	  return html;
   239	}
   240	
   680	      <td><span class="score-num">${s.score}</span><div class="score-bar"><div class="fill" style="width:${pct}%;background:${barColor}"></div></div></td>
   681	      <td><span class="badge ${entryClass}">${s.entry_quality || '-'}</span></td>
   682	      <td>${s.stop_loss ? '$' + s.stop_loss.toFixed(2) : '-'}</td>
   683	      <td style="color:${(s.rr_ratio || 0) >= 3 ? 'var(--green)' : (s.rr_ratio || 0) >= 2 ? 'var(--text)' : 'var(--yellow)'}">${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : '-'}</td>
   684	      <td style="color:${(s.rs || 0) > 0.1 ? 'var(--green)' : (s.rs || 0) > 0 ? 'var(--text)' : 'var(--red)'}">${s.rs != null ? s.rs.toFixed(3) : '-'}</td>
   685	      <td>${redditCell(s.reddit_mentions)}</td>
   686	      <td><ul class="reasons-list">${topReasons}</ul>${extraHTML}</td>
   687	      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
   688	    </tr>`;
   689	  }).join('');
   690	}
   691	
   692	function renderSellRows(signals) {
   693	  if (!signals.length) return '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
   694	  return signals.map(s => {
   695	    const sevClass = (s.severity || 'medium').toLowerCase();
   696	    const reasons = (s.reasons || []).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
   697	    return `<tr>
   698	      <td>${s.rank}</td>
   699	      <td><span class="ticker">${s.ticker}</span></td>
   700	      <td><span class="score-num">${s.score}</span></td>
   701	      <td><span class="badge ${sevClass}">${(s.severity || '?').toUpperCase()}</span></td>
   702	      <td>${s.breakdown_level ? '$' + s.breakdown_level.toFixed(2) : '-'}</td>
   703	      <td>${redditCell(s.reddit_mentions)}</td>
   704	      <td><ul class="reasons-list">${reasons}</ul></td>
   705	      <td>${fidelityLink(s.ticker, 'Sell', 'sell')}</td>
   706	    </tr>`;
   707	  }).join('');
   708	}
   709	
   710	// --- View: Positions (upload a Fidelity CSV, get hold/trim/add recommendations) --
   711	
   712	const POSITION_ACTION_LABELS = {
   713	  hold: { label: 'hold', cls: 'neutral' },
   714	  trail_to_breakeven: { label: 'trail to breakeven', cls: 'good' },
   715	  trail_to_profit: { label: 'trail to profit', cls: 'good' },
   716	  take_partial_and_trail: { label: 'consider trimming', cls: 'medium' },
   717	  take_major_partial_and_trail_tight: { label: 'trim + trail tight', cls: 'poor' },
   718	};
   719	
   720	function _positionsUploadCardHTML(data, expanded) {
   721	  const hasResults = data.position_analyses && data.position_analyses.length;
   722	  // Once you have results, the big upload form is just noise — collapse it to
   723	  // a one-line bar with an "Update positions" toggle instead of always
   724	  // showing the full form front and center.
   725	  if (hasResults && !expanded) {
   726	    return `
   727	      <div class="card" id="pos-upload-card" style="display:flex;align-items:center;gap:12px;padding:14px 20px">
   728	        <span style="color:var(--muted);font-size:13px">Showing ${data.position_analyses.length} position${data.position_analyses.length === 1 ? '' : 's'} from your last upload.</span>
   729	        <button class="btn" id="pos-expand" style="margin-left:auto">Update positions</button>
   730	      </div>`;
   731	  }
   732	  return `
   733	    <div class="card sim-card" id="pos-upload-card" style="max-width:600px">
   734	      <h2>Upload Your Positions <span class="status-pill idle" id="pos-pill">idle</span></h2>
   735	      <div class="sim-desc">
   736	        Export a Positions CSV from Fidelity (Accounts &amp; Trade -&gt; Positions -&gt; Download) and upload it here.
   737	        Nothing leaves this machine — no login, no credentials, just the file you already downloaded. Only your
   738	        entry price and quantity are used; current prices come from cached market data, not the CSV.
   739	      </div>
   740	      <input type="file" id="pos-file" accept=".csv" style="margin-bottom:12px;display:block;color:var(--text);font-size:13px">
   741	      <button class="btn primary" id="pos-analyze">${data.has_csv ? 'Re-analyze' : 'Upload &amp; Analyze'}</button>
   742	      <div class="job-output" id="pos-output"></div>
   743	    </div>`;
   744	}
   745	
   746	async function renderPositionsView() {
   747	  const data = await fetchJSON('/api/positions');
   748	  if (_currentView !== 'positions') return; // navigated away before this resolved
   749	  const hasResults = data.position_analyses && data.position_analyses.length;
   750	  content.innerHTML = `
   751	    ${_positionsUploadCardHTML(data, false)}
   752	    <div id="pos-results" style="margin-top:20px"></div>`;
   753	
   754	  if (hasResults) {
   755	    pageMeta.innerHTML = liveBadgeHTML();
   756	    renderPositionsResults(data);
   757	    _startLive(() => _liveGuarded('positions', refreshPositionsLive));
   758	  }
   759	  wirePositionsUpload(data);
   760	}
   761	
   762	// Silent live refresh: re-runs the (cheap, yfinance-only) positions analysis
   763	// in the background and patches fresh prices/gains/charts in without touching
   764	// the upload card or showing a loading spinner.
   765	async function refreshPositionsLive() {
   766	  await startJob('positions', {}, async (st) => {
   767	    if (st.status === 'success') {
   768	      renderPositionsResults(await fetchJSON('/api/positions'));
   769	    }
   770	  });
   771	}
   772	
   773	function wirePositionsUpload(data) {
   774	  const expandBtn = document.getElementById('pos-expand');
   775	  if (expandBtn) {
   776	    expandBtn.addEventListener('click', () => {
   777	      document.getElementById('pos-upload-card').outerHTML = _positionsUploadCardHTML(data, true);
   778	      wirePositionsUpload(data);
   779	    });
   780	    return; // collapsed state has no analyze button yet
   781	  }
   782	
   783	  document.getElementById('pos-analyze').addEventListener('click', async () => {
   784	    const fileInput = document.getElementById('pos-file');
   785	    const btn = document.getElementById('pos-analyze');
   786	    const pill = document.getElementById('pos-pill');
   787	    const out = document.getElementById('pos-output');
   788	    btn.disabled = true;
   789	
   790	    if (fileInput.files.length) {
   791	      pill.className = 'status-pill running';
   792	      pill.innerHTML = '<span class="spinner"></span> uploading';
   793	      const form = new FormData();
   794	      form.append('csv', fileInput.files[0]);
   795	      const uploadRes = await fetch('/api/positions/upload', { method: 'POST', body: form }).then(r => r.json());
   796	      if (!uploadRes.success) {
   797	        showToast('Upload failed: ' + (uploadRes.error || 'unknown error'));
   798	        btn.disabled = false;
   799	        pill.className = 'status-pill error';
   800	        pill.textContent = 'error';
   801	        return;
   802	      }
   803	    } else if (!data.has_csv) {
   804	      showToast('Choose a CSV file first');
   805	      btn.disabled = false;
   806	      return;
   807	    }
   808	
   809	    out.style.display = 'block';
   810	    out.textContent = '';
   811	    pill.className = 'status-pill running';
   812	    pill.innerHTML = '<span class="spinner"></span> analyzing';
   813	
   814	    await startJob('positions', {}, async (st) => {
   815	      out.textContent = st.output.join('\n');
   816	      out.scrollTop = out.scrollHeight;
   817	      if (st.status === 'success' || st.status === 'error' || st.status === 'stopped') {
   818	        btn.disabled = false;
   819	        pill.className = `status-pill ${st.status}`;
   820	        pill.textContent = st.status;
   821	        if (st.status === 'success') {
   822	          renderPositionsResults(await fetchJSON('/api/positions'));
   823	        }
   824	      }
   825	    });
   826	  });
   827	}
   828	
   829	function renderPositionsResults(data) {
   830	  const summary = data.summary || {};
   831	  const analyses = data.position_analyses || [];
   832	  const resultsEl = document.getElementById('pos-results');
   833	  if (!resultsEl) return;
   834	
   835	  if (!analyses.length) {
   836	    resultsEl.innerHTML = '<div class="no-data"><h2>No positions found</h2></div>';
   837	    return;
   838	  }
   839	
   840	  const cards = analyses.map(a => {
   841	    const meta = POSITION_ACTION_LABELS[a.action] || { label: a.action || 'hold', cls: 'neutral' };
   842	    const gainColor = a.current_gain_pct >= 0 ? 'var(--green)' : 'var(--red)';
   843	    const gainSign = a.current_gain_pct >= 0 ? '+' : '';
   844	
   845	    let extra = '';
   846	    if (a.recommended_stop) {
   847	      extra += `<div class="agent-badge-sub">Recommended stop: $${a.recommended_stop.toFixed(2)}</div>`;
   848	    }
   849	    if (a.add_on_signal) {
   850	      extra += `<div class="agent-badge-sub" style="color:var(--green);margin-top:6px">Add-on candidate — ${a.add_on_rationale}</div>`;

exec
/bin/zsh -lc "nl -ba static/js/dashboard.js | sed -n '235,345p'; nl -ba static/js/dashboard.js | sed -n '980,1070p'; nl -ba src/analysis/position_manager.py | sed -n '1,410p'; nl -ba manage_positions.py | sed -n '1,260p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
   235	    const more = green.length > 1 ? ` (+${green.length - 1} more)` : '';
   236	    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${green[0].flag}${more}</div>`;
   237	  }
   238	  return html;
   239	}
   240	
   241	// --- Background job runner (Run Simulation / Full Scan views) ----------
   242	
   243	async function startJob(kind, body, onUpdate) {
   244	  const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
   245	    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
   246	  });
   247	  const poll = async () => {
   248	    const st = await fetchJSON(`/api/jobs/${job_id}`);
   249	    onUpdate(st);
   250	    if (st.status === 'running' || st.status === 'queued') {
   251	      setTimeout(poll, 1500);
   252	    }
   253	  };
   254	  poll();
   255	  return job_id;
   256	}
   257	
   258	function jobCardHTML(id, title, desc, paramsHTML) {
   259	  return `
   260	    <div class="card sim-card">
   261	      <h2>${title} <span class="status-pill idle" id="${id}-pill">idle</span></h2>
   262	      <div class="sim-desc">${desc}</div>
   263	      <div class="sim-params">${paramsHTML}</div>
   264	      <button class="btn primary" id="${id}-run">Run</button>
   265	      <div class="job-output" id="${id}-output"></div>
   266	      <div id="${id}-result" style="margin-top:12px"></div>
   267	    </div>`;
   268	}
   269	
   270	// Job cards (Run Simulation, Full Scan) kick off long-running background jobs
   271	// (a real detached subprocess on the server — it was never actually stopped by
   272	// navigating away). What used to break on navigation was the UI side: the
   273	// click handler closed over the specific DOM nodes present at click-time, so
   274	// leaving the page and coming back re-rendered a fresh "idle" card with no
   275	// memory of the job still running (or just finished) underneath it. _activeJobs
   276	// tracks job_id per card id at module scope — outside any view's DOM — so it
   277	// survives a route change, and wireJobCard reconnects to it on every render.
   278	const _activeJobs = {}; // cardId -> most recent job_id for that card (running OR finished), survives across renders
   279	const _watchingJobIds = {}; // cardId -> job_id an active setTimeout poll loop is already chasing
   280	
   281	function watchJob(id, jobId, onResult) {
   282	  _activeJobs[id] = jobId;
   283	  // Reconnecting to a job you're already polling (e.g. navigating back and
   284	  // forth while it runs) would otherwise stack up a duplicate setTimeout
   285	  // chain each time — same end state, just wasted polling. The next tick of
   286	  // the existing loop repaints the freshly-mounted card within ~1.5s anyway.
   287	  if (_watchingJobIds[id] === jobId) return;
   288	  _watchingJobIds[id] = jobId;
   289	
   290	  const poll = async () => {
   291	    const st = await fetchJSON(`/api/jobs/${jobId}`);
   292	    if (st.error) {
   293	      // The server prunes finished jobs after a while — if you reconnect to
   294	      // one long after it ended, just drop back to idle instead of crashing
   295	      // on the missing `output` field.
   296	      if (_activeJobs[id] === jobId) delete _activeJobs[id];
   297	      if (_watchingJobIds[id] === jobId) delete _watchingJobIds[id];
   298	      return;
   299	    }
   300	    const btn = document.getElementById(`${id}-run`);
   301	    const pill = document.getElementById(`${id}-pill`);
   302	    const out = document.getElementById(`${id}-output`);
   303	    // Paint only if this card is actually on screen right now — if you've
   304	    // navigated elsewhere these are null and we just skip rendering. The job
   305	    // itself keeps running server-side regardless; we'll catch up next poll,
   306	    // or immediately via this same function when you navigate back.
   307	    if (btn && pill && out) {
   308	      out.style.display = 'block';
   309	      out.textContent = st.output.join('\n');
   310	      out.scrollTop = out.scrollHeight;
   311	      if (st.status === 'running' || st.status === 'queued') {
   312	        btn.disabled = true;
   313	        pill.className = 'status-pill running';
   314	        pill.innerHTML = '<span class="spinner"></span> running';
   315	      } else {
   316	        btn.disabled = false;
   317	        pill.className = `status-pill ${st.status}`;
   318	        pill.textContent = st.status;
   319	      }
   320	    }
   321	
   322	    if (st.status === 'running' || st.status === 'queued') {
   323	      setTimeout(poll, 1500);
   324	    } else {
   325	      // Deliberately NOT clearing _activeJobs[id] here — it's what lets
   326	      // wireJobCard reconnect and show the finished result if the job
   327	      // completed while you were on a different page (the common case for
   328	      // anything that finishes in under a minute or two). It's only replaced
   329	      // when this card starts a new job, never otherwise.
   330	      if (_watchingJobIds[id] === jobId) delete _watchingJobIds[id];
   331	      if (st.status === 'success' && onResult) {
   332	        const resultEl = document.getElementById(`${id}-result`);
   333	        if (resultEl) await onResult(st, resultEl);
   334	      }
   335	    }
   336	  };
   337	  poll();
   338	}
   339	
   340	function wireJobCard(id, kind, getParams, onResult) {
   341	  // Reconnect to a job started before navigating away and back.
   342	  if (_activeJobs[id]) {
   343	    watchJob(id, _activeJobs[id], onResult);
   344	  }
   345	
   980	    });
   981	  });
   982	}
   983	
   984	function renderTradeRows(trades) {
   985	  return trades.map(t => `<tr>
   986	    <td><span class="ticker">${t.ticker}</span></td>
   987	    <td>${t.period || '-'}</td>
   988	    <td>${t.score ?? '-'}</td>
   989	    <td><span class="badge ${t.exit_reason === 'stop_loss' ? 'poor' : t.exit_reason === 'sell_signal' ? 'medium' : 'good'}">${(t.exit_reason || '-').replace('_', ' ')}</span></td>
   990	    <td>${t.days_held ?? '-'}</td>
   991	    <td style="color:${(t.return_pct || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">${(t.return_pct || 0).toFixed(2)}%</td>
   992	    <td style="color:${(t.dollar_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">$${(t.dollar_pnl || 0).toFixed(2)}</td>
   993	  </tr>`).join('');
   994	}
   995	
   996	// --- View: Run Simulation --------------------------------------------------
   997	
   998	function renderRunView() {
   999	  content.innerHTML = `
  1000	    <div class="grid-3">
  1001	      ${jobCardHTML('top3', 'Quick Backtest (Top 3)', 'What would the top-3 buy signals have been N days ago, held to today?', `
  1002	        <label>Days back<input type="number" id="top3-days" value="7"></label>
  1003	        <label>Sample size<input type="number" id="top3-sample" value="150"></label>
  1004	        <label>Investment $<input type="number" id="top3-investment" value="1000"></label>
  1005	      `)}
  1006	      ${jobCardHTML('mc', 'Monte Carlo', 'Re-samples many top-3 portfolios from one fetched pool — win rate distribution, not one basket.', `
  1007	        <label>Days back<input type="number" id="mc-days" value="7"></label>
  1008	        <label>Pool size<input type="number" id="mc-pool" value="300"></label>
  1009	        <label>Sample size<input type="number" id="mc-sample" value="150"></label>
  1010	        <label>Iterations<input type="number" id="mc-iterations" value="100"></label>
  1011	      `)}
  1012	      ${jobCardHTML('wf', 'Full Walk-Forward', 'Rigorous multi-period backtest — walks a fixed universe through many historical dates. Slow (minutes+).', `
  1013	        <label>Universe size<input type="number" id="wf-universe_size" value="250"></label>
  1014	        <label>Lookback (mo)<input type="number" id="wf-lookback_months" value="9"></label>
  1015	        <label>Top N/period<input type="number" id="wf-top_n" value="10"></label>
  1016	        <label>Max hold (days)<input type="number" id="wf-max_hold_days" value="60"></label>
  1017	      `)}
  1018	    </div>`;
  1019	
  1020	  wireJobCard('top3', 'backtest-top3', () => ({
  1021	    days: +document.getElementById('top3-days').value,
  1022	    sample: +document.getElementById('top3-sample').value,
  1023	    investment: +document.getElementById('top3-investment').value,
  1024	  }), async (st, resultEl) => {
  1025	    if (!st.result_path) return;
  1026	    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
  1027	    if (res.error) return;
  1028	    resultEl.innerHTML = `<div style="font-size:13px">
  1029	      <strong style="color:${res.total_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.total_profit.toFixed(2)} (${res.total_return_pct.toFixed(2)}%)</strong>
  1030	      — ${res.picks.map(p => p.ticker).join(', ')}</div>`;
  1031	  });
  1032	
  1033	  wireJobCard('mc', 'backtest-monte-carlo', () => ({
  1034	    days: +document.getElementById('mc-days').value,
  1035	    pool: +document.getElementById('mc-pool').value,
  1036	    sample: +document.getElementById('mc-sample').value,
  1037	    iterations: +document.getElementById('mc-iterations').value,
  1038	  }), async (st, resultEl) => {
  1039	    if (!st.result_path) return;
  1040	    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
  1041	    if (res.error || !res.iterations_run) { resultEl.innerHTML = '<div style="color:var(--muted);font-size:13px">Not enough qualifiers found.</div>'; return; }
  1042	    resultEl.innerHTML = `<div style="font-size:13px">
  1043	      Win rate <strong>${res.win_rate.toFixed(1)}%</strong> · avg <strong style="color:${res.avg_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.avg_profit.toFixed(2)} (${res.avg_pct.toFixed(2)}%)</strong>
  1044	      over ${res.iterations_run} iterations${res.score_return_correlation != null ? ` · score/return correlation r=${res.score_return_correlation.toFixed(3)}` : ''}</div>`;
  1045	  });
  1046	
  1047	  wireJobCard('wf', 'walk-forward', () => ({
  1048	    universe_size: +document.getElementById('wf-universe_size').value,
  1049	    lookback_months: +document.getElementById('wf-lookback_months').value,
  1050	    top_n: +document.getElementById('wf-top_n').value,
  1051	    max_hold_days: +document.getElementById('wf-max_hold_days').value,
  1052	  }), async (st, resultEl) => {
  1053	    resultEl.innerHTML = `<a href="#/backtests" class="btn primary">View results →</a>`;
  1054	  });
  1055	}
  1056	
  1057	// --- View: Full Scan --------------------------------------------------------
  1058	
  1059	function renderScanView() {
  1060	  content.innerHTML = `
  1061	    <div class="card sim-card" style="max-width:520px">
  1062	      <h2>Run a Scan <span class="status-pill idle" id="scan-pill">idle</span></h2>
  1063	      <div class="sim-desc">Test scan covers ~100 stocks (~1 min). Full scan covers the ~3,800-stock universe (15-30 min).</div>
  1064	      <div class="sim-params" style="align-items:center">
  1065	        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-full" style="width:auto"> Full scan (unchecked = quick test scan)</label>
  1066	      </div>
  1067	      <div class="sim-params" style="align-items:center">
  1068	        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-agents" style="width:auto"> Enable AI agents (Fundamentals/Catalyst/Congress → Top 5 shortlist, needs ANTHROPIC_API_KEY)</label>
  1069	      </div>
  1070	      <button class="btn primary" id="scan-run">Run</button>
     1	#!/usr/bin/env python3
     2	"""Position management and stop loss recommendations.
     3	
     4	Analyzes current Fidelity positions and recommends:
     5	- When to move stop loss up (trail stops)
     6	- New stop loss levels with rationale
     7	- When to take partial profits
     8	- Exit target adjustments
     9	
    10	Only provides recommendations for SHORT-TERM positions (held <1 year).
    11	Long-term positions (held 1+ years) are excluded to preserve favorable tax treatment.
    12	
    13	Uses cached price data from daily scans - no additional API calls needed.
    14	"""
    15	
    16	import logging
    17	from typing import Dict, List, Optional
    18	from datetime import datetime, timedelta
    19	from pathlib import Path
    20	import json
    21	import yfinance as yf
    22	import pandas as pd
    23	
    24	from src.screening.phase_indicators import classify_phase
    25	from src.data.git_storage_fetcher import GitStorageFetcher
    26	
    27	logger = logging.getLogger(__name__)
    28	
    29	
    30	class PositionManager:
    31	    """Analyze positions and recommend stop loss adjustments.
    32	
    33	    Uses cached fundamentals and price data to avoid extra API calls.
    34	    """
    35	
    36	    def __init__(self, use_cache: bool = True):
    37	        """Initialize position manager.
    38	
    39	        Args:
    40	            use_cache: Use cached fundamentals and price data (recommended)
    41	        """
    42	        self.use_cache = use_cache
    43	        self.git_fetcher = GitStorageFetcher() if use_cache else None
    44	        self.fundamentals_dir = Path("./data/fundamentals_cache")
    45	
    46	    def _get_price_data(self, ticker: str) -> pd.DataFrame:
    47	        """Get price data from cache or yfinance.
    48	
    49	        Args:
    50	            ticker: Stock ticker
    51	
    52	        Returns:
    53	            DataFrame with price data
    54	        """
    55	        if self.use_cache and self.git_fetcher:
    56	            try:
    57	                # Try to get cached data first
    58	                price_data = self.git_fetcher.fetch_price_fresh(ticker)
    59	                if not price_data.empty:
    60	                    logger.debug(f"{ticker}: Using cached price data")
    61	                    return price_data
    62	            except Exception as e:
    63	                logger.debug(f"{ticker}: Cache fetch failed, falling back to yfinance: {e}")
    64	
    65	        # Fallback to yfinance
    66	        try:
    67	            stock = yf.Ticker(ticker)
    68	            price_data = stock.history(period='1y', interval='1d')
    69	            if not price_data.empty:
    70	                logger.debug(f"{ticker}: Fetched fresh price data from yfinance")
    71	            return price_data
    72	        except Exception as e:
    73	            logger.error(f"{ticker}: Failed to fetch price data: {e}")
    74	            return pd.DataFrame()
    75	
    76	    def _get_cached_fundamentals(self, ticker: str) -> Dict:
    77	        """Get cached fundamentals if available.
    78	
    79	        Args:
    80	            ticker: Stock ticker
    81	
    82	        Returns:
    83	            Dict with fundamental data, or empty dict if not cached
    84	        """
    85	        if not self.use_cache:
    86	            return {}
    87	
    88	        try:
    89	            fundamental_file = self.fundamentals_dir / f"{ticker}_fundamentals.json"
    90	            if fundamental_file.exists():
    91	                with open(fundamental_file, 'r') as f:
    92	                    data = json.load(f)
    93	                    logger.debug(f"{ticker}: Loaded cached fundamentals")
    94	                    return data.get('data', {})
    95	        except Exception as e:
    96	            logger.debug(f"{ticker}: Could not load cached fundamentals: {e}")
    97	
    98	        return {}
    99	
   100	    def analyze_position(
   101	        self,
   102	        ticker: str,
   103	        entry_price: float,
   104	        current_price: float,
   105	        entry_date: Optional[datetime] = None
   106	    ) -> Dict:
   107	        """Analyze a single position and recommend stop management.
   108	
   109	        Args:
   110	            ticker: Stock symbol
   111	            entry_price: Your average entry price
   112	            current_price: Current market price
   113	            entry_date: When you entered (optional, for tax treatment check)
   114	
   115	        Returns:
   116	            Dict with recommendations:
   117	            - should_adjust_stop: bool
   118	            - recommended_stop: float (new stop level)
   119	            - current_gain_pct: float
   120	            - rationale: str (why adjust)
   121	            - action: str (trail_to_breakeven, trail_to_profit, take_partial, hold)
   122	            - tax_treatment: str (short_term or long_term)
   123	        """
   124	        result = {
   125	            'ticker': ticker,
   126	            'entry_price': entry_price,
   127	            'current_price': current_price,
   128	            'should_adjust_stop': False,
   129	            'recommended_stop': None,
   130	            'current_gain_pct': 0,
   131	            'rationale': '',
   132	            'action': 'hold',
   133	            'tax_treatment': 'unknown',
   134	            'warnings': []
   135	        }
   136	
   137	        # Validate prices
   138	        if entry_price <= 0:
   139	            result['warnings'].append('Invalid entry price (zero or negative) - cannot analyze')
   140	            result['rationale'] = f"Cannot analyze - invalid entry price: ${entry_price:.2f}"
   141	            return result
   142	
   143	        if current_price <= 0:
   144	            result['warnings'].append('Invalid current price (zero or negative) - cannot analyze')
   145	            result['rationale'] = f"Cannot analyze - invalid current price: ${current_price:.2f}"
   146	            return result
   147	
   148	        # Calculate current gain
   149	        gain_pct = ((current_price - entry_price) / entry_price) * 100
   150	        result['current_gain_pct'] = round(gain_pct, 2)
   151	
   152	        # Check tax treatment
   153	        if entry_date:
   154	            days_held = (datetime.now() - entry_date).days
   155	            if days_held >= 365:
   156	                result['tax_treatment'] = 'long_term'
   157	                result['rationale'] = f"LONG-TERM HOLD ({days_held} days) - Preserve long-term capital gains tax rate. No stop adjustment recommended."
   158	                return result
   159	            else:
   160	                result['tax_treatment'] = 'short_term'
   161	                result['days_held'] = days_held
   162	
   163	        # Fetch price data and analyze (uses cache by default)
   164	        try:
   165	            price_data = self._get_price_data(ticker)
   166	
   167	            if price_data.empty or len(price_data) < 50:
   168	                result['warnings'].append('Insufficient price data for analysis')
   169	                return result
   170	
   171	            # Calculate phase and technical levels
   172	            phase_info = classify_phase(price_data, current_price)
   173	            phase = phase_info['phase']
   174	
   175	            sma_50 = phase_info.get('sma_50', 0)
   176	            sma_200 = phase_info.get('sma_200', 0)
   177	
   178	            # Recent swing low (last 10 days)
   179	            recent_low = price_data['Low'].iloc[-10:].min()
   180	
   181	            result['phase'] = phase
   182	            result['sma_50'] = round(sma_50, 2)
   183	            result['recent_low'] = round(recent_low, 2)
   184	
   185	            # Compact price history for the dashboard's per-position chart —
   186	            # computed here (not a separate fetch on click) since price_data
   187	            # is already in memory. ~8 months of daily closes is enough to see
   188	            # the trend/pullback context without bloating the JSON response.
   189	            history = price_data['Close'].iloc[-180:]
   190	            result['price_history'] = [
   191	                {'date': str(idx.date()) if hasattr(idx, 'date') else str(idx), 'close': round(float(c), 2)}
   192	                for idx, c in history.items() if pd.notna(c)
   193	            ]
   194	
   195	            # ADD-ON (SCALE IN) SIGNAL — independent of the exit-side logic below.
   196	            # Flags a position as a good "buy more" point: still in a confirmed
   197	            # Phase 2 uptrend, pulled back to (not through) the rising 50 SMA —
   198	            # a classic continuation entry — and not yet a big enough winner that
   199	            # the exit logic below would already be recommending a trim (that
   200	            # starts at gain_pct >= 15, so this is capped just under it to never
   201	            # overlap with a trim recommendation on the same position).
   202	            result['add_on_signal'] = False
   203	            result['add_on_rationale'] = ''
   204	            if phase == 2 and sma_50 > 0 and sma_50 <= current_price <= sma_50 * 1.03 and gain_pct < 15:
   205	                result['add_on_signal'] = True
   206	                result['add_on_rationale'] = (
   207	                    f"Pulled back to the rising 50 SMA (${sma_50:.2f}) without breaking it, still in a "
   208	                    f"confirmed Phase 2 uptrend, and not yet an extended winner ({gain_pct:+.1f}%) — "
   209	                    f"a classic continuation add point if you want to size up."
   210	                )
   211	
   212	            # STOP LOSS ADJUSTMENT LOGIC - LINEAR FORMULAS (NO BUCKETS)
   213	            # Based on continuous gain percentage scaling
   214	
   215	            if gain_pct < 5:
   216	                # Small gain - don't adjust yet
   217	                result['action'] = 'hold'
   218	                result['rationale'] = f"Position up {gain_pct:.1f}% - hold initial stop. Wait for 5%+ gain before adjusting."
   219	
   220	            else:
   221	                # Gains of 5%+ trigger stop adjustments
   222	                result['should_adjust_stop'] = True
   223	
   224	                # CALCULATE PROFIT-BASED STOP (scales linearly with gain)
   225	                # Formula: entry * (1 + min(gain_pct - 3, gain_pct * 0.5) / 100)
   226	                # - At 5% gain → lock in ~1% profit (entry * 1.01)
   227	                # - At 10% gain → lock in ~3.5% profit (entry * 1.035)
   228	                # - At 20% gain → lock in ~8.5% profit (entry * 1.085)
   229	                # - At 40% gain → lock in ~18.5% profit (entry * 1.185)
   230	                # This scales smoothly - bigger gains = more profit locked in
   231	
   232	                locked_profit_pct = min(gain_pct - 3, gain_pct * 0.5)
   233	                profit_based_stop = entry_price * (1 + locked_profit_pct / 100)
   234	
   235	                # CALCULATE SMA-BASED STOP (if applicable)
   236	                sma_based_stop = None
   237	                if sma_50 > 0 and sma_50 < current_price:
   238	                    # Distance below 50 SMA scales with gain size
   239	                    # Small gains (5-15%) → 1% below SMA
   240	                    # Medium gains (15-30%) → 0.7% below SMA
   241	                    # Large gains (30%+) → 0.5% below SMA
   242	                    sma_buffer_pct = max(0.5, 1.5 - (gain_pct / 50))  # Linear from 1.5% to 0.5%
   243	                    sma_based_stop = sma_50 * (1 - sma_buffer_pct / 100)
   244	
   245	                # USE WHICHEVER STOP IS HIGHER (more conservative)
   246	                if sma_based_stop and sma_based_stop > profit_based_stop:
   247	                    result['recommended_stop'] = round(sma_based_stop, 2)
   248	                    stop_type = "SMA-based"
   249	                    sma_buffer_pct = ((sma_50 - result['recommended_stop']) / sma_50) * 100
   250	                else:
   251	                    result['recommended_stop'] = round(profit_based_stop, 2)
   252	                    stop_type = "profit-based"
   253	
   254	                # Calculate what % profit is locked in
   255	                locked_profit = ((result['recommended_stop'] / entry_price) - 1) * 100
   256	
   257	                # DETERMINE ACTION AND PARTIAL EXIT % (scales linearly)
   258	                # Formula for partial exit: min(50, max(0, (gain_pct - 15) * 2.5))
   259	                # - 0-15% gain → No partial exit (0%)
   260	                # - 20% gain → 12.5% partial exit
   261	                # - 25% gain → 25% partial exit
   262	                # - 30% gain → 37.5% partial exit
   263	                # - 35% gain → 50% partial exit (capped)
   264	                partial_exit_pct = min(50, max(0, (gain_pct - 15) * 2.5))
   265	
   266	                if partial_exit_pct > 35:
   267	                    result['action'] = 'take_major_partial_and_trail_tight'
   268	                    action_desc = f"SELL {partial_exit_pct:.0f}%"
   269	                elif partial_exit_pct > 10:
   270	                    result['action'] = 'take_partial_and_trail'
   271	                    action_desc = f"CONSIDER SELLING {partial_exit_pct:.0f}%"
   272	                elif gain_pct >= 10:
   273	                    result['action'] = 'trail_to_profit'
   274	                    action_desc = "TRAIL TO PROFIT"
   275	                else:
   276	                    result['action'] = 'trail_to_breakeven'
   277	                    action_desc = "TRAIL TO BREAKEVEN"
   278	
   279	                # BUILD RATIONALE
   280	                rationale_lines = []
   281	                rationale_lines.append(f"Position up {gain_pct:.1f}% - {action_desc}")
   282	                rationale_lines.append("")
   283	
   284	                if partial_exit_pct > 0:
   285	                    remaining_pct = 100 - partial_exit_pct
   286	                    rationale_lines.append(f"  RECOMMENDED ACTION:")
   287	                    rationale_lines.append(f"    • Sell {partial_exit_pct:.0f}% at ${current_price:.2f} (lock in ${(current_price - entry_price) * partial_exit_pct / 100:.2f}/share)")
   288	                    rationale_lines.append(f"    • Trail remaining {remaining_pct:.0f}% with stop at ${result['recommended_stop']:.2f}")
   289	                    rationale_lines.append(f"    • Effective: locks minimum +{locked_profit:.1f}% on full position")
   290	                else:
   291	                    rationale_lines.append(f"  NEW STOP LOSS: ${result['recommended_stop']:.2f}")
   292	                    rationale_lines.append(f"    • Locks in minimum +{locked_profit:.1f}% profit")
   293	                    rationale_lines.append(f"    • Stop type: {stop_type}")
   294	
   295	                rationale_lines.append("")
   296	                rationale_lines.append(f"  Technical: Phase {phase} | 50 SMA: ${sma_50:.2f}")
   297	
   298	                # Add Phase 3 warning for big winners
   299	                if phase == 3 and gain_pct >= 20:
   300	                    rationale_lines.append(f"  WARNING: Stock in Phase 3 (distribution). Consider tighter exit.")
   301	
   302	                result['rationale'] = "\n".join(rationale_lines)
   303	                result['partial_exit_pct'] = round(partial_exit_pct, 1)
   304	                result['locked_profit_pct'] = round(locked_profit, 2)
   305	
   306	            # Additional checks
   307	            if phase == 3 or phase == 4:
   308	                result['warnings'].append(
   309	                    f'Stock in Phase {phase} (distribution/decline). Consider tighter stops or exit.'
   310	                )
   311	
   312	            if current_price < sma_50 and sma_50 > 0:
   313	                result['warnings'].append(
   314	                    f'Price broke below 50 SMA (${sma_50:.2f}). Trend weakening - review position.'
   315	                )
   316	
   317	        except Exception as e:
   318	            logger.error(f"Error analyzing {ticker}: {e}")
   319	            result['warnings'].append(f'Analysis error: {str(e)}')
   320	
   321	        return result
   322	
   323	    def analyze_portfolio(
   324	        self,
   325	        positions: List[Dict],
   326	        entry_dates: Optional[Dict[str, datetime]] = None
   327	    ) -> Dict:
   328	        """Analyze all positions and generate comprehensive report.
   329	
   330	        Args:
   331	            positions: List of position dicts from src.data.fidelity_positions.load_positions()
   332	            entry_dates: Optional dict of {ticker: entry_date} for tax treatment
   333	
   334	        Returns:
   335	            Dict with:
   336	            - position_analyses: List of individual position analyses
   337	            - summary: Portfolio-level stats
   338	            - urgent_actions: List of positions needing immediate attention
   339	        """
   340	        if not positions:
   341	            return {
   342	                'position_analyses': [],
   343	                'summary': {'total_positions': 0},
   344	                'urgent_actions': []
   345	            }
   346	
   347	        entry_dates = entry_dates or {}
   348	        analyses = []
   349	
   350	        for pos in positions:
   351	            ticker = pos['ticker']
   352	            entry_date = entry_dates.get(ticker)
   353	
   354	            logger.info(f"Analyzing {ticker}: entry=${pos['average_buy_price']:.2f}, current=${pos['current_price']:.2f}")
   355	
   356	            analysis = self.analyze_position(
   357	                ticker=ticker,
   358	                entry_price=pos['average_buy_price'],
   359	                current_price=pos['current_price'],
   360	                entry_date=entry_date
   361	            )
   362	
   363	            analysis['quantity'] = pos['quantity']
   364	            analyses.append(analysis)
   365	
   366	        # Generate summary
   367	        total_positions = len(analyses)
   368	        positions_to_adjust = sum(1 for a in analyses if a['should_adjust_stop'])
   369	        short_term_positions = sum(
   370	            1 for a in analyses if a['tax_treatment'] == 'short_term'
   371	        )
   372	        long_term_positions = sum(
   373	            1 for a in analyses if a['tax_treatment'] == 'long_term'
   374	        )
   375	
   376	        avg_gain = sum(a['current_gain_pct'] for a in analyses) / total_positions if total_positions > 0 else 0
   377	
   378	        add_on_candidates = sum(1 for a in analyses if a.get('add_on_signal'))
   379	
   380	        summary = {
   381	            'total_positions': total_positions,
   382	            'positions_need_adjustment': positions_to_adjust,
   383	            'add_on_candidates': add_on_candidates,
   384	            'short_term_positions': short_term_positions,
   385	            'long_term_positions': long_term_positions,
   386	            'average_gain_pct': round(avg_gain, 2)
   387	        }
   388	
   389	        # Urgent actions (Phase 3/4 warnings, big winners, breakdowns)
   390	        urgent = []
   391	        for analysis in analyses:
   392	            if analysis['warnings']:
   393	                urgent.append({
   394	                    'ticker': analysis['ticker'],
   395	                    'reason': analysis['warnings'],
   396	                    'current_gain': analysis['current_gain_pct']
   397	                })
   398	            elif analysis.get('action') in ['take_partial_and_trail', 'take_partial_and_trail_tight']:
   399	                urgent.append({
   400	                    'ticker': analysis['ticker'],
   401	                    'reason': 'Big winner - consider taking partial profits',
   402	                    'current_gain': analysis['current_gain_pct']
   403	                })
   404	
   405	        return {
   406	            'position_analyses': analyses,
   407	            'summary': summary,
   408	            'urgent_actions': urgent,
   409	            'timestamp': datetime.now()
   410	        }
     1	#!/usr/bin/env python3
     2	"""Position management tool - integrates Fidelity positions with stop loss recommendations.
     3	
     4	Reads your current Fidelity positions from a CSV you export yourself and
     5	analyzes each one to recommend:
     6	- When to trail stops up
     7	- Exact new stop loss levels
     8	- When to take partial profits
     9	- Warnings for Phase 3/4 transitions
    10	
    11	ONLY analyzes SHORT-TERM positions (held <1 year) to avoid disrupting long-term tax treatment.
    12	
    13	How to get the CSV: Fidelity website -> Accounts & Trade -> Positions ->
    14	click the download/export icon near the top of the positions table.
    15	
    16	Usage:
    17	    python manage_positions.py --csv ~/Downloads/Portfolio_Positions.csv
    18	    python manage_positions.py --csv positions.csv --export  # Save report to file
    19	"""
    20	
    21	import json
    22	import sys
    23	import logging
    24	import argparse
    25	from datetime import datetime
    26	from pathlib import Path
    27	
    28	from src.data.fidelity_positions import load_positions
    29	from src.analysis.position_manager import PositionManager
    30	from src.utils.json_safe import sanitize_nan
    31	
    32	logging.basicConfig(
    33	    level=logging.INFO,
    34	    format='%(asctime)s - %(levelname)s - %(message)s'
    35	)
    36	logger = logging.getLogger(__name__)
    37	
    38	
    39	def main():
    40	    parser = argparse.ArgumentParser(description='Position Management with Stop Loss Recommendations')
    41	    parser.add_argument('--csv', type=str, required=True,
    42	                         help='Path to a Fidelity Positions CSV export (Accounts & Trade -> Positions -> Download)')
    43	    parser.add_argument('--export', action='store_true', help='Export report to file')
    44	    parser.add_argument('--entry-dates', type=str, help='JSON file with entry dates (optional)')
    45	    parser.add_argument('--json-out', type=str, default=None,
    46	                         help='Optional path to also write structured JSON results (used by the GUI dashboard)')
    47	    args = parser.parse_args()
    48	
    49	    print("\n" + "="*80)
    50	    print("POSITION MANAGEMENT - STOP LOSS RECOMMENDATIONS")
    51	    print("="*80)
    52	    print("\nThis tool will:")
    53	    print("  - Read your current Fidelity positions from the CSV you exported")
    54	    print("  - Analyze each position's technical structure")
    55	    print("  - Recommend stop loss adjustments for SHORT-TERM holdings")
    56	    print("  - Identify when to take partial profits, and good add-on points")
    57	    print("  - LONG-TERM positions (1+ years) are EXCLUDED")
    58	    print("      (to preserve favorable capital gains tax treatment)")
    59	    print("\n" + "="*80 + "\n")
    60	
    61	    try:
    62	        print(f"Reading positions from {args.csv}...")
    63	        positions = load_positions(args.csv)
    64	    except (FileNotFoundError, ValueError) as e:
    65	        print(f"\nERROR: {e}\n")
    66	        sys.exit(1)
    67	
    68	    if not positions:
    69	        print("="*80)
    70	        print("No open positions found in the CSV")
    71	        print("="*80)
    72	        if args.json_out:
    73	            _write_json_out(args, {'position_analyses': [], 'summary': {'total_positions': 0}, 'urgent_actions': []})
    74	        return
    75	
    76	    print(f"Found {len(positions)} positions\n")
    77	
    78	    # Load entry dates if provided
    79	    entry_dates = None
    80	    if args.entry_dates:
    81	        try:
    82	            with open(args.entry_dates, 'r') as f:
    83	                dates_data = json.load(f)
    84	                from datetime import datetime as dt
    85	                entry_dates = {
    86	                    ticker: dt.fromisoformat(date_str)
    87	                    for ticker, date_str in dates_data.items()
    88	                }
    89	            print(f"Loaded entry dates for {len(entry_dates)} tickers\n")
    90	        except Exception as e:
    91	            print(f"Could not load entry dates: {e}")
    92	            print("Proceeding without entry date data (will not filter by tax treatment)\n")
    93	
    94	    # Analyze positions
    95	    print("Analyzing positions and calculating stop recommendations...\n")
    96	    manager = PositionManager()
    97	    analysis = manager.analyze_portfolio(positions, entry_dates)
    98	
    99	    # Generate report
   100	    report = manager.format_portfolio_report(analysis)
   101	    print(report)
   102	
   103	    # Export if requested
   104	    if args.export:
   105	        output_dir = Path("./data/position_reports")
   106	        output_dir.mkdir(parents=True, exist_ok=True)
   107	
   108	        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
   109	        filename = output_dir / f"position_management_{timestamp}.txt"
   110	
   111	        with open(filename, 'w') as f:
   112	            f.write(report)
   113	
   114	        print(f"\nReport exported to: {filename}")
   115	
   116	    if args.json_out:
   117	        _write_json_out(args, analysis)
   118	
   119	
   120	def _write_json_out(args, analysis):
   121	    """Optional structured JSON alongside the printed report — used by the GUI
   122	    dashboard's Positions view. Never affects stdout output or the CLI usage."""
   123	    out_path = Path(args.json_out)
   124	    out_path.parent.mkdir(parents=True, exist_ok=True)
   125	    out_path.write_text(json.dumps(sanitize_nan(analysis), indent=2, default=str))
   126	
   127	
   128	if __name__ == '__main__':
   129	    main()

exec
/bin/zsh -lc "nl -ba src/data/fidelity_positions.py; nl -ba src/data/robinhood_positions.py | sed -n '1,284p'; nl -ba src/data/earnings_risk.py; nl -ba scripts/fetch_momentum_status.py" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Fidelity position loader — reads positions from a CSV you export yourself
     2	from Fidelity's website. No login automation, no credentials handled by this
     3	tool: Fidelity actively blocks scraping/unofficial API access, unlike
     4	Robinhood's already-gray-area unofficial API that the old
     5	src/data/robinhood_positions.py used.
     6	
     7	How to export (Fidelity website):
     8	  Accounts & Trade -> Positions -> click the download/export icon near the
     9	  top of the positions table -> saves "Portfolio_Positions_<date>.csv".
    10	
    11	Produces the same dict shape src/analysis/position_manager.py expects
    12	(ticker, average_buy_price, current_price, quantity) — a drop-in replacement
    13	for RobinhoodPositionFetcher.fetch_positions() from the caller's point of view.
    14	
    15	If Fidelity's actual export from your account uses different column names
    16	than expected below, share the header row and COLUMN_ALIASES can be adjusted.
    17	"""
    18	
    19	import csv
    20	import logging
    21	from pathlib import Path
    22	from typing import Dict, List, Optional
    23	
    24	logger = logging.getLogger(__name__)
    25	
    26	# Fidelity's standard Positions CSV export column names, matched
    27	# case-insensitively. A couple of common aliases are tolerated in case the
    28	# export format varies slightly by account type.
    29	COLUMN_ALIASES = {
    30	    'ticker': ['symbol'],
    31	    'description': ['description'],
    32	    'quantity': ['quantity', 'qty'],
    33	    'last_price': ['last price', 'lastprice'],
    34	    'current_value': ['current value'],
    35	    'average_cost_basis': ['average cost basis', 'avg cost basis', 'cost basis per share'],
    36	    'cost_basis_total': ['cost basis total', 'total cost basis'],
    37	}
    38	
    39	# Fidelity's export includes cash/money-market sweep lines and a trailing
    40	# disclaimer footer that aren't real equity positions — skip these tickers.
    41	_NON_POSITION_TICKERS = {'CASH', 'SPAXX', 'FDRXX', 'FZFXX', 'PENDING ACTIVITY'}
    42	
    43	
    44	def _clean_money(val: Optional[str]) -> Optional[float]:
    45	    if val is None:
    46	        return None
    47	    val = val.strip().replace('$', '').replace(',', '')
    48	    if val in ('', '--', 'n/a', 'N/A'):
    49	        return None
    50	    negative = val.startswith('(') and val.endswith(')')
    51	    if negative:
    52	        val = val[1:-1]
    53	    try:
    54	        num = float(val)
    55	        return -num if negative else num
    56	    except ValueError:
    57	        return None
    58	
    59	
    60	def _find_column(headers: List[str], aliases: List[str]) -> Optional[str]:
    61	    lowered = {h.strip().lower(): h for h in headers}
    62	    for alias in aliases:
    63	        if alias in lowered:
    64	            return lowered[alias]
    65	    return None
    66	
    67	
    68	def load_positions(csv_path: str) -> List[Dict]:
    69	    """Parse a Fidelity Positions CSV export into position dicts.
    70	
    71	    Returns dicts with: ticker, average_buy_price, current_price, quantity,
    72	    description, current_value (the last two informational only).
    73	    """
    74	    path = Path(csv_path)
    75	    if not path.exists():
    76	        raise FileNotFoundError(f"CSV not found: {csv_path}")
    77	
    78	    with open(path, newline='', encoding='utf-8-sig') as f:
    79	        rows = list(csv.reader(f))
    80	
    81	    if not rows:
    82	        return []
    83	
    84	    header = rows[0]
    85	    col = {name: _find_column(header, aliases) for name, aliases in COLUMN_ALIASES.items()}
    86	    if col['ticker'] is None:
    87	        raise ValueError(
    88	            f"Couldn't find a Symbol column in {csv_path}. Headers found: {header}. "
    89	            "Fidelity may have changed their export format — share this header row to fix it."
    90	        )
    91	
    92	    idx = {name: header.index(c) for name, c in col.items() if c is not None}
    93	
    94	    def cell(row, name):
    95	        i = idx.get(name)
    96	        return row[i] if i is not None and len(row) > i else None
    97	
    98	    positions = []
    99	    for row in rows[1:]:
   100	        ticker = (cell(row, 'ticker') or '').strip().upper()
   101	        if not ticker or ticker in _NON_POSITION_TICKERS:
   102	            continue
   103	        if not any(c.isalpha() for c in ticker):
   104	            continue  # skips blank/disclaimer rows that slipped past the ticker check
   105	
   106	        quantity = _clean_money(cell(row, 'quantity'))
   107	        last_price = _clean_money(cell(row, 'last_price'))
   108	        avg_cost = _clean_money(cell(row, 'average_cost_basis'))
   109	        if quantity is None or last_price is None or avg_cost is None:
   110	            logger.warning(f"Skipping {ticker}: missing quantity/price/cost-basis in CSV row")
   111	            continue
   112	
   113	        unrealized_pl_pct = (last_price - avg_cost) / avg_cost * 100 if avg_cost else 0.0
   114	
   115	        positions.append({
   116	            'ticker': ticker,
   117	            'quantity': quantity,
   118	            'average_buy_price': avg_cost,
   119	            'current_price': last_price,
   120	            'unrealized_pl_pct': unrealized_pl_pct,
   121	            'description': (cell(row, 'description') or '').strip(),
   122	            'current_value': _clean_money(cell(row, 'current_value')),
   123	        })
   124	
   125	    logger.info(f"Loaded {len(positions)} positions from {csv_path}")
   126	    return positions
   127	
   128	
   129	def format_positions_report(positions: List[Dict]) -> str:
   130	    """Format positions as a readable text report (mirrors the old
   131	    RobinhoodPositionFetcher.format_positions_report output style)."""
   132	    if not positions:
   133	        return "No open positions"
   134	
   135	    from datetime import datetime
   136	
   137	    lines = ["=" * 60, "CURRENT FIDELITY POSITIONS (from CSV export)",
   138	              f"Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 60, ""]
   139	
   140	    for i, pos in enumerate(positions, 1):
   141	        lines.append(f"{i}. {pos['ticker']}")
   142	        lines.append(f"   Shares: {pos['quantity']}")
   143	        lines.append(f"   Entry: ${pos['average_buy_price']:.2f}")
   144	        lines.append(f"   Current: ${pos['current_price']:.2f}")
   145	        pl_sign = "+" if pos['unrealized_pl_pct'] >= 0 else ""
   146	        lines.append(f"   P/L: {pl_sign}{pos['unrealized_pl_pct']:.2f}%")
   147	        lines.append("")
   148	
   149	    lines.append("=" * 60)
   150	    lines.append(f"Total positions: {len(positions)}")
   151	    lines.append("=" * 60)
   152	    return "\n".join(lines)
     1	#!/usr/bin/env python3
     2	"""Robinhood position fetcher - READ ONLY.
     3	
     4	This module ONLY fetches your current stock positions (ticker + entry price).
     5	It does NOT:
     6	- Read account balances or portfolio value
     7	- Execute any trades
     8	- Modify any positions
     9	- Access buying power or cash
    10	
    11	Authentication: Uses robin_stocks library with MFA support.
    12	"""
    13	
    14	import os
    15	import logging
    16	from typing import List, Dict, Optional
    17	from datetime import datetime
    18	
    19	try:
    20	    import robin_stocks.robinhood as rh
    21	    ROBINHOOD_AVAILABLE = True
    22	except ImportError:
    23	    ROBINHOOD_AVAILABLE = False
    24	
    25	logger = logging.getLogger(__name__)
    26	
    27	
    28	class RobinhoodPositionFetcher:
    29	    """Fetch current stock positions from Robinhood (read-only)."""
    30	
    31	    def __init__(self):
    32	        """Initialize fetcher.
    33	
    34	        Requires environment variable:
    35	        - ROBINHOOD_USERNAME: Your Robinhood email
    36	
    37	        Password and MFA will be prompted interactively (never stored).
    38	        """
    39	        if not ROBINHOOD_AVAILABLE:
    40	            raise ImportError(
    41	                "robin_stocks not installed. Install with: pip install robin-stocks"
    42	            )
    43	
    44	        self.username = os.getenv('ROBINHOOD_USERNAME')
    45	        self.logged_in = False
    46	
    47	        if not self.username:
    48	            raise ValueError(
    49	                "Missing ROBINHOOD_USERNAME environment variable. "
    50	                "Set with: export ROBINHOOD_USERNAME='your_email@example.com'"
    51	            )
    52	
    53	    def login(self, password: Optional[str] = None, mfa_code: Optional[str] = None) -> bool:
    54	        """Login to Robinhood with interactive password and SMS MFA.
    55	
    56	        Args:
    57	            password: Password (will prompt if not provided)
    58	            mfa_code: SMS MFA code (will prompt if needed)
    59	
    60	        Returns:
    61	            True if login successful
    62	        """
    63	        try:
    64	            logger.info("Logging into Robinhood (read-only mode)...")
    65	
    66	            # Get password if not provided
    67	            if not password:
    68	                import getpass
    69	                password = getpass.getpass(f"Robinhood password for {self.username}: ")
    70	
    71	            # Initial login attempt (will trigger SMS if 2FA enabled)
    72	            try:
    73	                login_result = rh.login(self.username, password)
    74	
    75	                if login_result:
    76	                    self.logged_in = True
    77	                    logger.info("✓ Robinhood login successful (no MFA required)")
    78	                    return True
    79	
    80	            except Exception as e:
    81	                error_msg = str(e).lower()
    82	
    83	                # Check if MFA is required
    84	                if 'mfa' in error_msg or 'challenge' in error_msg or 'verification' in error_msg:
    85	                    logger.info("MFA required - check your phone for SMS code from Robinhood")
    86	
    87	                    # Prompt for SMS code if not provided
    88	                    if not mfa_code:
    89	                        mfa_code = input("Enter SMS code from Robinhood: ").strip()
    90	
    91	                    # Try login with MFA
    92	                    login_result = rh.login(
    93	                        self.username,
    94	                        password,
    95	                        mfa_code=mfa_code,
    96	                        by_sms=True
    97	                    )
    98	
    99	                    if login_result:
   100	                        self.logged_in = True
   101	                        logger.info("✓ Robinhood login successful with SMS MFA")
   102	                        return True
   103	                else:
   104	                    raise e
   105	
   106	            logger.error("✗ Robinhood login failed")
   107	            return False
   108	
   109	        except Exception as e:
   110	            logger.error(f"Login error: {e}")
   111	            return False
   112	
   113	    def fetch_positions(self) -> List[Dict]:
   114	        """Fetch current stock positions (READ ONLY).
   115	
   116	        Returns list of positions with:
   117	        - ticker: Stock symbol
   118	        - quantity: Number of shares (rounded to int)
   119	        - average_buy_price: Average entry price
   120	        - current_price: Latest market price
   121	        - unrealized_pl_pct: Unrealized P/L percentage
   122	
   123	        Does NOT include:
   124	        - Account balance
   125	        - Total portfolio value
   126	        - Buying power
   127	        - Any dollar amounts beyond per-share prices
   128	
   129	        Returns:
   130	            List of position dicts
   131	        """
   132	        if not self.logged_in:
   133	            logger.error("Not logged in. Call login() first.")
   134	            return []
   135	
   136	        try:
   137	            logger.info("Fetching current positions (read-only)...")
   138	
   139	            # Get positions - this returns stocks you currently own
   140	            positions = rh.get_open_stock_positions()
   141	
   142	            if not positions:
   143	                logger.info("No open positions found")
   144	                return []
   145	
   146	            result = []
   147	            for position in positions:
   148	                try:
   149	                    # Extract basic position info (NO account balances)
   150	                    quantity = float(position.get('quantity', 0))
   151	                    if quantity <= 0:
   152	                        continue
   153	
   154	                    # Get instrument data to find ticker
   155	                    instrument_url = position.get('instrument')
   156	                    instrument_data = rh.get_instrument_by_url(instrument_url)
   157	                    ticker = instrument_data.get('symbol', 'UNKNOWN')
   158	
   159	                    # Get prices
   160	                    avg_buy_price = float(position.get('average_buy_price', 0))
   161	
   162	                    # Get current market price
   163	                    current_price_data = rh.get_latest_price(ticker)
   164	                    current_price = float(current_price_data[0]) if current_price_data else 0
   165	
   166	                    # Calculate unrealized P/L %
   167	                    if avg_buy_price > 0 and current_price > 0:
   168	                        pl_pct = ((current_price - avg_buy_price) / avg_buy_price) * 100
   169	                    else:
   170	                        pl_pct = 0
   171	
   172	                    result.append({
   173	                        'ticker': ticker,
   174	                        'quantity': int(round(quantity)),  # Round to whole shares
   175	                        'average_buy_price': round(avg_buy_price, 2),
   176	                        'current_price': round(current_price, 2),
   177	                        'unrealized_pl_pct': round(pl_pct, 2)
   178	                    })
   179	
   180	                except Exception as e:
   181	                    logger.warning(f"Error processing position: {e}")
   182	                    continue
   183	
   184	            logger.info(f"✓ Fetched {len(result)} positions")
   185	            return result
   186	
   187	        except Exception as e:
   188	            logger.error(f"Error fetching positions: {e}")
   189	            return []
   190	
   191	    def logout(self):
   192	        """Logout from Robinhood."""
   193	        if self.logged_in:
   194	            try:
   195	                rh.logout()
   196	                self.logged_in = False
   197	                logger.info("Logged out from Robinhood")
   198	            except Exception as e:
   199	                logger.warning(f"Logout warning: {e}")
   200	
   201	    def get_position_tickers(self) -> List[str]:
   202	        """Get just the tickers of current positions.
   203	
   204	        Useful for checking if you already own a stock before buying.
   205	
   206	        Returns:
   207	            List of ticker symbols
   208	        """
   209	        positions = self.fetch_positions()
   210	        return [p['ticker'] for p in positions]
   211	
   212	    def format_positions_report(self) -> str:
   213	        """Format positions as a readable text report.
   214	
   215	        Returns:
   216	            Formatted string with position details
   217	        """
   218	        positions = self.fetch_positions()
   219	
   220	        if not positions:
   221	            return "No open positions"
   222	
   223	        lines = []
   224	        lines.append("="*60)
   225	        lines.append("CURRENT ROBINHOOD POSITIONS (Read-Only)")
   226	        lines.append(f"Fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
   227	        lines.append("="*60)
   228	        lines.append("")
   229	
   230	        for i, pos in enumerate(positions, 1):
   231	            lines.append(f"{i}. {pos['ticker']}")
   232	            lines.append(f"   Shares: {pos['quantity']}")
   233	            lines.append(f"   Entry: ${pos['average_buy_price']:.2f}")
   234	            lines.append(f"   Current: ${pos['current_price']:.2f}")
   235	
   236	            pl_sign = "+" if pos['unrealized_pl_pct'] >= 0 else ""
   237	            lines.append(f"   P/L: {pl_sign}{pos['unrealized_pl_pct']:.2f}%")
   238	            lines.append("")
   239	
   240	        lines.append("="*60)
   241	        lines.append(f"Total positions: {len(positions)}")
   242	        lines.append("="*60)
   243	
   244	        return "\n".join(lines)
   245	
   246	
   247	def main():
   248	    """Example usage - fetch and display current positions."""
   249	    import sys
   250	
   251	    if not ROBINHOOD_AVAILABLE:
   252	        print("ERROR: robin_stocks not installed")
   253	        print("Install with: pip install robin-stocks")
   254	        sys.exit(1)
   255	
   256	    # Initialize fetcher
   257	    try:
   258	        fetcher = RobinhoodPositionFetcher()
   259	    except ValueError as e:
   260	        print(f"ERROR: {e}")
   261	        print("\nSet environment variable:")
   262	        print("  export ROBINHOOD_USERNAME='your_email@example.com'")
   263	        print("\nPassword and MFA will be prompted (never stored in files)")
   264	        sys.exit(1)
   265	
   266	    # Login (will prompt for password and SMS MFA interactively)
   267	    if not fetcher.login():
   268	        print("Login failed. Check credentials.")
   269	        sys.exit(1)
   270	
   271	    try:
   272	        # Fetch and display positions
   273	        print("\n" + fetcher.format_positions_report())
   274	
   275	        # Also show just tickers
   276	        tickers = fetcher.get_position_tickers()
   277	        print(f"\nTickers you currently own: {', '.join(tickers)}")
   278	
   279	    finally:
   280	        fetcher.logout()
   281	
   282	
   283	if __name__ == '__main__':
   284	    main()
     1	"""Earnings-event risk warning — a fundamentally different signal from the rest of this
     2	screener: not "is this stock trending" but "is a high-uncertainty news event imminent."
     3	
     4	Trend-following (this screener's core methodology) cannot predict discrete jumps like
     5	earnings beats/misses — that information doesn't exist in price/volume history before the
     6	event. This module doesn't try to predict the DIRECTION of an earnings move; it flags WHEN
     7	one is coming and how big the options market expects it to be, via the standard "ATM
     8	straddle" expected-move calculation options traders use. That's a risk-sizing signal
     9	("this could gap past your stop-loss overnight"), not a buy/sell signal.
    10	
    11	Uses yfinance's Ticker.calendar (earnings date) and Ticker.option_chain (real market IV) —
    12	both already a dependency, no new API key needed.
    13	"""
    14	
    15	import logging
    16	from datetime import date, datetime, timedelta
    17	from typing import Dict, Optional
    18	
    19	import yfinance as yf
    20	
    21	logger = logging.getLogger(__name__)
    22	
    23	DEFAULT_LOOKAHEAD_DAYS = 14
    24	
    25	
    26	class EarningsRiskFetcher:
    27	    """Flags imminent earnings events and the options-implied expected move."""
    28	
    29	    def get_earnings_risk(self, ticker: str, lookahead_days: int = DEFAULT_LOOKAHEAD_DAYS) -> Dict:
    30	        """Check whether a ticker has earnings coming up soon, and how big a move the
    31	        options market is pricing in around that date.
    32	
    33	        Returns a dict that's always safe to use even on total failure:
    34	            {'has_upcoming_earnings': False, 'earnings_date': None, 'days_until': None,
    35	             'expected_move_pct': None, 'note': str}
    36	        """
    37	        empty = {
    38	            'has_upcoming_earnings': False, 'earnings_date': None,
    39	            'days_until': None, 'expected_move_pct': None, 'note': None,
    40	        }
    41	
    42	        try:
    43	            t = yf.Ticker(ticker)
    44	            calendar = t.calendar
    45	            earnings_dates = calendar.get('Earnings Date') if calendar else None
    46	            if not earnings_dates:
    47	                return empty
    48	
    49	            earnings_date = earnings_dates[0]
    50	            days_until = (earnings_date - date.today()).days
    51	
    52	            if days_until < 0 or days_until > lookahead_days:
    53	                return empty
    54	
    55	            expected_move_pct = self._expected_move(t, earnings_date)
    56	
    57	            note = (
    58	                f"Earnings in {days_until} day{'s' if days_until != 1 else ''} "
    59	                f"({earnings_date.isoformat()})"
    60	            )
    61	            if expected_move_pct is not None:
    62	                note += f" — options market pricing in ~±{expected_move_pct:.1f}% move"
    63	
    64	            return {
    65	                'has_upcoming_earnings': True,
    66	                'earnings_date': earnings_date.isoformat(),
    67	                'days_until': days_until,
    68	                'expected_move_pct': expected_move_pct,
    69	                'note': note,
    70	            }
    71	
    72	        except Exception as e:
    73	            logger.debug(f"Earnings risk check failed for {ticker}: {e}")
    74	            return empty
    75	
    76	    def _expected_move(self, ticker_obj: yf.Ticker, earnings_date: date) -> Optional[float]:
    77	        """ATM straddle price as % of stock price = the options market's implied expected
    78	        move around the given date. Standard technique: (ATM call + ATM put) / stock price.
    79	
    80	        Most precise for near-term earnings (within ~1-2 weeks), where a weekly options
    81	        expiration lands close to the report date. For earnings further out, the nearest
    82	        available expiration may be well past the report, overstating the earnings-specific
    83	        move with several extra weeks of ordinary time value — real limitation, not hidden.
    84	        """
    85	        try:
    86	            expirations = ticker_obj.options
    87	            if not expirations:
    88	                return None
    89	
    90	            target_exp = None
    91	            for exp_str in expirations:
    92	                exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
    93	                if exp_date >= earnings_date:
    94	                    target_exp = exp_str
    95	                    break
    96	            if not target_exp:
    97	                return None
    98	
    99	            price = ticker_obj.history(period='1d')['Close'].iloc[-1]
   100	            chain = ticker_obj.option_chain(target_exp)
   101	            calls, puts = chain.calls, chain.puts
   102	            if calls.empty or puts.empty:
   103	                return None
   104	
   105	            atm_strike = calls.iloc[(calls['strike'] - price).abs().argsort()[:1]]['strike'].values[0]
   106	            atm_call = calls[calls['strike'] == atm_strike]['lastPrice']
   107	            atm_put = puts[puts['strike'] == atm_strike]['lastPrice']
   108	            if atm_call.empty or atm_put.empty or atm_call.values[0] == 0:
   109	                return None
   110	
   111	            straddle = atm_call.values[0] + atm_put.values[0]
   112	            return float(straddle / price * 100)
   113	
   114	        except Exception as e:
   115	            logger.debug(f"Expected move calc failed: {e}")
   116	            return None
     1	#!/usr/bin/env python3
     2	"""Classifies each ticker into a momentum "status" — hot / stable / basing /
     3	avoid — using the same Phase + distance-from-50-SMA logic the real screening
     4	engine (src/screening/signal_engine.py) already scores buy signals with, and
     5	tracks how many consecutive calendar days a ticker has held its current
     6	status (a running "day N of this trend" streak, persisted across runs).
     7	
     8	Status buckets:
     9	  hot    - Phase 2 uptrend, but stock is stretched >20% above its 50 SMA.
    10	           Real momentum, but the entry-quality math in signal_engine.py
    11	           penalizes chasing this — high risk/reward is already spent.
    12	  stable - Phase 2 uptrend, healthy distance from the 50 SMA (<=20%) and the
    13	           SMA is still rising. This is the "good entry zone."
    14	  basing - Phase 1 (base building), or a Phase 2 stock whose 50 SMA has gone
    15	           flat/rolling over — momentum stalling, not yet a downtrend.
    16	  avoid  - Phase 3 (distribution) or Phase 4 (downtrend). Not a buy.
    17	
    18	Usage:
    19	    python scripts/fetch_momentum_status.py --tickers GKOS,NVDA --group shortlist --json-out out.json
    20	"""
    21	import argparse
    22	import json
    23	from datetime import date, datetime
    24	from pathlib import Path
    25	import sys
    26	
    27	sys.path.insert(0, str(Path(__file__).parent.parent))
    28	
    29	import yfinance as yf
    30	
    31	from src.screening.phase_indicators import classify_phase
    32	from src.utils.json_safe import sanitize_nan
    33	
    34	HISTORY_PATH = Path(__file__).parent.parent / "data" / "momentum_status" / "history.json"
    35	
    36	STATUS_LABELS = {
    37	    'hot': 'Hot — extended',
    38	    'stable': 'Stable uptrend',
    39	    'basing': 'Basing / cooling',
    40	    'avoid': 'Avoid — downtrend',
    41	}
    42	
    43	
    44	def classify_status(phase_info: dict) -> str:
    45	    phase = phase_info.get('phase', 0)
    46	    distance_50 = phase_info.get('distance_from_50sma', 0)
    47	    slope_50 = phase_info.get('slope_50', 0)
    48	
    49	    if phase in (3, 4):
    50	        return 'avoid'
    51	    if phase == 1:
    52	        return 'basing'
    53	    if phase == 2:
    54	        if distance_50 > 20:
    55	            return 'hot'
    56	        if slope_50 <= 0:
    57	            return 'basing'
    58	        return 'stable'
    59	    return 'basing'  # phase 0 / insufficient data — treat as neutral, not a buy
    60	
    61	
    62	def _load_history() -> dict:
    63	    if HISTORY_PATH.exists():
    64	        try:
    65	            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    66	        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
    67	            return {}
    68	    return {}
    69	
    70	
    71	def _save_history(history: dict):
    72	    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    73	    HISTORY_PATH.write_text(json.dumps(sanitize_nan(history), indent=2), encoding="utf-8")
    74	
    75	
    76	def update_streak(history: dict, ticker: str, status: str, today_str: str) -> dict:
    77	    """Advances (or resets) the day-streak for one ticker. Safe to call many
    78	    times on the same calendar day (idempotent) — the streak count only
    79	    changes on an actual day-to-day transition."""
    80	    existing = history.get(ticker)
    81	
    82	    if existing and existing.get('last_seen') == today_str:
    83	        if existing['status'] != status:
    84	            # Flipped status within the same day — restart the streak from today.
    85	            existing['status'] = status
    86	            existing['since'] = today_str
    87	            existing['days'] = 1
    88	        # else: same status, same day — nothing to advance.
    89	        return existing
    90	
    91	    if existing and existing['status'] == status:
    92	        existing['days'] = existing.get('days', 1) + 1
    93	        existing['last_seen'] = today_str
    94	        return existing
    95	
    96	    record = {'status': status, 'since': today_str, 'days': 1, 'last_seen': today_str}
    97	    history[ticker] = record
    98	    return record
    99	
   100	
   101	def main():
   102	    parser = argparse.ArgumentParser()
   103	    parser.add_argument('--tickers', type=str, required=True)
   104	    parser.add_argument('--group', type=str, default='misc')
   105	    parser.add_argument('--json-out', type=str, required=True)
   106	    args = parser.parse_args()
   107	
   108	    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
   109	    today_str = date.today().isoformat()
   110	    history = _load_history()
   111	
   112	    snapshot = {}
   113	    for ticker in tickers:
   114	        print(f"Classifying momentum status for {ticker}...")
   115	        try:
   116	            price_data = yf.Ticker(ticker).history(period="1y", interval="1d")
   117	            if price_data.empty or len(price_data) < 200:
   118	                print(f"  {ticker}: insufficient price history, skipping")
   119	                continue
   120	            current_price = float(price_data['Close'].iloc[-1])
   121	            phase_info = classify_phase(price_data, current_price)
   122	            status = classify_status(phase_info)
   123	            record = update_streak(history, ticker, status, today_str)
   124	            snapshot[ticker] = {
   125	                'status': status,
   126	                'label': STATUS_LABELS[status],
   127	                'days': record['days'],
   128	                'since': record['since'],
   129	                'phase': phase_info.get('phase'),
   130	                'distance_from_50sma': phase_info.get('distance_from_50sma'),
   131	            }
   132	        except Exception as e:
   133	            print(f"  {ticker}: failed ({e})")
   134	
   135	    _save_history(history)
   136	
   137	    out_path = Path(args.json_out)
   138	    out_path.parent.mkdir(parents=True, exist_ok=True)
   139	    out_path.write_text(json.dumps(sanitize_nan({
   140	        'generated': datetime.now().isoformat(),
   141	        'group': args.group,
   142	        'tickers': tickers,
   143	        'status': snapshot,
   144	    }), indent=2), encoding="utf-8")
   145	    print(f"Wrote momentum status for {len(snapshot)} tickers to {out_path}")
   146	
   147	
   148	if __name__ == '__main__':
   149	    main()

exec
/bin/zsh -lc "nl -ba mac_app/main.py; nl -ba control_panel.py | sed -n '1,500p'; nl -ba src/notifications/email_notifier.py | sed -n '1,520p'; nl -ba src/notifications/slack_notifier.py | sed -n '180,310p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
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
     1	#!/usr/bin/env python3
     2	"""Command Control Panel — run the project's key commands from a browser and watch them work live.
     3	
     4	Usage:
     5	    python control_panel.py                # start on port 5060, opens browser
     6	    python control_panel.py --port 8090
     7	"""
     8	
     9	import argparse
    10	import threading
    11	import time
    12	import webbrowser
    13	from pathlib import Path
    14	from threading import Timer
    15	
    16	from flask import Flask, jsonify, render_template_string
    17	
    18	app = Flask(__name__)
    19	
    20	PROJECT_ROOT = Path(__file__).parent.resolve()
    21	VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"
    22	VENV_PIP = PROJECT_ROOT / "venv" / "bin" / "pip"
    23	
    24	import subprocess  # noqa: E402  (kept near usage below for clarity)
    25	
    26	COMMANDS = {
    27	    "setup": {
    28	        "label": "Setup Environment",
    29	        "description": "Create venv + install all dependencies",
    30	        "cmd": [
    31	            "bash", "-c",
    32	            f'python3 -m venv "{PROJECT_ROOT / "venv"}" && '
    33	            f'"{VENV_PIP}" install --upgrade pip && '
    34	            f'"{VENV_PIP}" install -r "{PROJECT_ROOT / "requirements.txt"}" && '
    35	            f'"{VENV_PIP}" install flask',
    36	        ],
    37	    },
    38	    "test_scan": {
    39	        "label": "Quick Test Scan",
    40	        "description": "100 stocks · ~1 minute",
    41	        "cmd": [str(VENV_PYTHON), "run_optimized_scan.py", "--test-mode", "--git-storage", "--workers", "2"],
    42	    },
    43	    "full_scan": {
    44	        "label": "Full Market Scan",
    45	        "description": "3,800+ stocks · ~15-30 minutes",
    46	        "cmd": [str(VENV_PYTHON), "run_optimized_scan.py", "--conservative", "--git-storage"],
    47	        "confirm": True,
    48	    },
    49	    "dashboard": {
    50	        "label": "Launch Results Dashboard",
    51	        "description": "Starts the results dashboard on :5050 (keeps running until stopped)",
    52	        "cmd": [str(VENV_PYTHON), "dashboard.py"],
    53	        "link": "http://localhost:5050",
    54	    },
    55	}
    56	
    57	STATE = {
    58	    cid: {"status": "idle", "output": [], "returncode": None, "started": None, "proc": None}
    59	    for cid in COMMANDS
    60	}
    61	LOCK = threading.Lock()
    62	
    63	
    64	def _run_command(cid):
    65	    entry = COMMANDS[cid]
    66	    st = STATE[cid]
    67	    with LOCK:
    68	        st["status"] = "running"
    69	        st["output"] = []
    70	        st["returncode"] = None
    71	        st["started"] = time.time()
    72	
    73	    try:
    74	        proc = subprocess.Popen(
    75	            entry["cmd"],
    76	            cwd=str(PROJECT_ROOT),
    77	            stdout=subprocess.PIPE,
    78	            stderr=subprocess.STDOUT,
    79	            text=True,
    80	            bufsize=1,
    81	        )
    82	        with LOCK:
    83	            st["proc"] = proc
    84	
    85	        for line in proc.stdout:
    86	            with LOCK:
    87	                st["output"].append(line.rstrip("\n"))
    88	
    89	        proc.wait()
    90	        with LOCK:
    91	            st["returncode"] = proc.returncode
    92	            st["status"] = "success" if proc.returncode == 0 else "error"
    93	            st["proc"] = None
    94	    except Exception as exc:
    95	        with LOCK:
    96	            st["output"].append(f"[control-panel] failed to launch: {exc}")
    97	            st["status"] = "error"
    98	            st["proc"] = None
    99	
   100	
   101	@app.route("/api/run/<cid>", methods=["POST"])
   102	def api_run(cid):
   103	    if cid not in COMMANDS:
   104	        return jsonify({"error": "unknown command"}), 404
   105	    if STATE[cid]["status"] == "running":
   106	        return jsonify({"error": "already running"}), 409
   107	    threading.Thread(target=_run_command, args=(cid,), daemon=True).start()
   108	    return jsonify({"ok": True})
   109	
   110	
   111	@app.route("/api/stop/<cid>", methods=["POST"])
   112	def api_stop(cid):
   113	    if cid not in COMMANDS:
   114	        return jsonify({"error": "unknown command"}), 404
   115	    st = STATE[cid]
   116	    with LOCK:
   117	        proc = st["proc"]
   118	    if proc and proc.poll() is None:
   119	        proc.terminate()
   120	        with LOCK:
   121	            st["status"] = "stopped"
   122	        return jsonify({"ok": True})
   123	    return jsonify({"error": "not running"}), 409
   124	
   125	
   126	@app.route("/api/status/<cid>")
   127	def api_status(cid):
   128	    if cid not in COMMANDS:
   129	        return jsonify({"error": "unknown command"}), 404
   130	    st = STATE[cid]
   131	    with LOCK:
   132	        elapsed = (time.time() - st["started"]) if st["started"] and st["status"] == "running" else None
   133	        return jsonify({
   134	            "status": st["status"],
   135	            "output": st["output"],
   136	            "returncode": st["returncode"],
   137	            "elapsed": elapsed,
   138	        })
   139	
   140	
   141	@app.route("/")
   142	def index():
   143	    return render_template_string(PAGE_HTML, commands=COMMANDS, root=str(PROJECT_ROOT))
   144	
   145	
   146	PAGE_HTML = """
   147	<!DOCTYPE html>
   148	<html lang="en">
   149	<head>
   150	<meta charset="UTF-8">
   151	<meta name="viewport" content="width=device-width, initial-scale=1.0">
   152	<title>Command Control Panel</title>
   153	<style>
   154	  :root {
   155	    --bg: #0f1117;
   156	    --surface: #1a1d27;
   157	    --border: #2a2d3a;
   158	    --text: #e4e6eb;
   159	    --muted: #8b8fa3;
   160	    --green: #22c55e;
   161	    --red: #ef4444;
   162	    --yellow: #eab308;
   163	    --blue: #3b82f6;
   164	  }
   165	  * { margin: 0; padding: 0; box-sizing: border-box; }
   166	  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
   167	
   168	  .header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 20px 32px; }
   169	  .header h1 { font-size: 20px; font-weight: 600; }
   170	  .header .meta { color: var(--muted); font-size: 12px; margin-top: 4px; font-family: monospace; }
   171	
   172	  .container { max-width: 900px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
   173	
   174	  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
   175	  .card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
   176	  .card-head h2 { font-size: 15px; font-weight: 600; }
   177	  .card-head .desc { color: var(--muted); font-size: 12px; margin-top: 3px; }
   178	
   179	  .pill { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; padding: 4px 10px; border-radius: 20px; white-space: nowrap; }
   180	  .pill.idle { background: rgba(139,143,163,0.15); color: var(--muted); }
   181	  .pill.running { background: rgba(59,130,246,0.15); color: var(--blue); animation: pulse 1.4s infinite; }
   182	  .pill.success { background: rgba(34,197,94,0.15); color: var(--green); }
   183	  .pill.error { background: rgba(239,68,68,0.15); color: var(--red); }
   184	  .pill.stopped { background: rgba(234,179,8,0.15); color: var(--yellow); }
   185	  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
   186	
   187	  .output { background: #05060a; border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px; height: 180px; overflow-y: auto; font-family: 'SF Mono', Menlo, monospace; font-size: 12px; line-height: 1.5; color: #b8fbc0; white-space: pre-wrap; word-break: break-word; margin-bottom: 12px; }
   188	  .output:empty::before { content: "waiting for output…"; color: var(--muted); font-style: italic; }
   189	
   190	  .card-actions { display: flex; align-items: center; gap: 10px; }
   191	  .btn { padding: 7px 14px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px; transition: all 0.15s; }
   192	  .btn:hover:not(:disabled) { border-color: var(--blue); }
   193	  .btn.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
   194	  .btn.primary:hover:not(:disabled) { opacity: 0.9; }
   195	  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
   196	  .btn.link { background: rgba(34,197,94,0.15); border-color: transparent; color: var(--green); text-decoration: none; display: none; }
   197	  .elapsed { color: var(--muted); font-size: 12px; font-family: monospace; margin-left: auto; }
   198	</style>
   199	</head>
   200	<body>
   201	
   202	<div class="header">
   203	  <h1>Stock Screener · Command Control Panel</h1>
   204	  <div class="meta">{{ root }}</div>
   205	</div>
   206	
   207	<div class="container" id="app"></div>
   208	
   209	<script>
   210	const commands = {{ commands|tojson }};
   211	const pollers = {};
   212	
   213	function render() {
   214	  const app = document.getElementById('app');
   215	  for (const [cid, c] of Object.entries(commands)) {
   216	    const card = document.createElement('div');
   217	    card.className = 'card';
   218	    card.innerHTML = `
   219	      <div class="card-head">
   220	        <div>
   221	          <h2>${c.label}</h2>
   222	          <div class="desc">${c.description}</div>
   223	        </div>
   224	        <span class="pill idle" id="pill-${cid}">idle</span>
   225	      </div>
   226	      <div class="output" id="output-${cid}"></div>
   227	      <div class="card-actions">
   228	        <button class="btn primary" id="run-${cid}">▶ Run</button>
   229	        <button class="btn" id="stop-${cid}" disabled>■ Stop</button>
   230	        <a class="btn link" id="link-${cid}" href="${c.link || '#'}" target="_blank">Open dashboard →</a>
   231	        <span class="elapsed" id="elapsed-${cid}"></span>
   232	      </div>
   233	    `;
   234	    app.appendChild(card);
   235	    document.getElementById(`run-${cid}`).onclick = () => runCmd(cid);
   236	    document.getElementById(`stop-${cid}`).onclick = () => stopCmd(cid);
   237	  }
   238	}
   239	
   240	function runCmd(cid) {
   241	  const c = commands[cid];
   242	  if (c.confirm && !confirm(`${c.label} — ${c.description}. Continue?`)) return;
   243	  document.getElementById('output-' + cid).textContent = '';
   244	  fetch(`/api/run/${cid}`, { method: 'POST' }).then(() => poll(cid));
   245	}
   246	
   247	function stopCmd(cid) {
   248	  fetch(`/api/stop/${cid}`, { method: 'POST' });
   249	}
   250	
   251	function poll(cid) {
   252	  clearInterval(pollers[cid]);
   253	  pollers[cid] = setInterval(() => tick(cid), 600);
   254	  tick(cid);
   255	}
   256	
   257	function tick(cid) {
   258	  fetch(`/api/status/${cid}`).then(r => r.json()).then(data => {
   259	    const pill = document.getElementById('pill-' + cid);
   260	    const out = document.getElementById('output-' + cid);
   261	    const runBtn = document.getElementById('run-' + cid);
   262	    const stopBtn = document.getElementById('stop-' + cid);
   263	    const link = document.getElementById('link-' + cid);
   264	    const elapsed = document.getElementById('elapsed-' + cid);
   265	
   266	    pill.className = 'pill ' + data.status;
   267	    pill.textContent = data.returncode !== null && data.status !== 'running'
   268	      ? `${data.status} (exit ${data.returncode})`
   269	      : data.status;
   270	
   271	    out.textContent = data.output.join('\\n');
   272	    out.scrollTop = out.scrollHeight;
   273	
   274	    if (data.status === 'running') {
   275	      runBtn.disabled = true;
   276	      stopBtn.disabled = false;
   277	      elapsed.textContent = data.elapsed ? Math.round(data.elapsed) + 's' : '';
   278	      if (commands[cid].link && data.output.some(l => l.includes('Running on'))) {
   279	        link.style.display = 'inline-block';
   280	      }
   281	    } else {
   282	      runBtn.disabled = false;
   283	      stopBtn.disabled = true;
   284	      elapsed.textContent = '';
   285	      clearInterval(pollers[cid]);
   286	    }
   287	  });
   288	}
   289	
   290	render();
   291	for (const cid of Object.keys(commands)) { poll(cid); }
   292	</script>
   293	</body>
   294	</html>
   295	"""
   296	
   297	if __name__ == "__main__":
   298	    parser = argparse.ArgumentParser()
   299	    parser.add_argument("--port", type=int, default=5099)
   300	    args = parser.parse_args()
   301	    url = f"http://localhost:{args.port}"
   302	    Timer(1.0, lambda: webbrowser.open(url)).start()
   303	    print(f"Control panel running at {url}")
   304	    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
     1	"""Email notification module for sending screening alerts.
     2	
     3	Supports Gmail, Outlook, and custom SMTP servers with HTML email formatting.
     4	"""
     5	
     6	import logging
     7	import os
     8	import smtplib
     9	from datetime import datetime
    10	from email.mime.multipart import MIMEMultipart
    11	from email.mime.text import MIMEText
    12	from typing import Dict, List, Optional
    13	
    14	import pandas as pd
    15	from dotenv import load_dotenv
    16	
    17	# Load environment variables
    18	load_dotenv()
    19	
    20	# Configure logging
    21	logging.basicConfig(
    22	    level=logging.INFO,
    23	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    24	)
    25	logger = logging.getLogger(__name__)
    26	
    27	FIDELITY_TRADE_URL = "https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol={ticker}"
    28	
    29	
    30	class EmailNotifier:
    31	    """Send screening results via email with HTML formatting.
    32	
    33	    Supports Gmail, Outlook, and custom SMTP servers. Uses environment
    34	    variables for configuration.
    35	
    36	    Environment Variables:
    37	        EMAIL_FROM: Sender email address
    38	        EMAIL_PASSWORD: Sender email password or app-specific password
    39	        EMAIL_TO: Recipient email address (comma-separated for multiple)
    40	        SMTP_SERVER: SMTP server (default: smtp.gmail.com for Gmail)
    41	        SMTP_PORT: SMTP port (default: 587)
    42	
    43	    Example:
    44	        >>> notifier = EmailNotifier()
    45	        >>> notifier.send_screening_results(results_df, top_n=10)
    46	    """
    47	
    48	    def __init__(
    49	        self,
    50	        smtp_server: Optional[str] = None,
    51	        smtp_port: Optional[int] = None,
    52	        email_from: Optional[str] = None,
    53	        email_password: Optional[str] = None,
    54	        email_to: Optional[str] = None
    55	    ) -> None:
    56	        """Initialize the email notifier.
    57	
    58	        Args:
    59	            smtp_server: SMTP server address. Defaults to env EMAIL_SMTP_SERVER or smtp.gmail.com.
    60	            smtp_port: SMTP port. Defaults to env EMAIL_SMTP_PORT or 587.
    61	            email_from: Sender email. Defaults to env EMAIL_FROM.
    62	            email_password: Sender password. Defaults to env EMAIL_PASSWORD.
    63	            email_to: Recipient email(s). Defaults to env EMAIL_TO.
    64	        """
    65	        self.smtp_server = smtp_server or os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    66	        self.smtp_port = smtp_port or int(os.getenv('EMAIL_SMTP_PORT', '587'))
    67	        self.email_from = email_from or os.getenv('EMAIL_FROM')
    68	        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
    69	        self.email_to = email_to or os.getenv('EMAIL_TO')
    70	
    71	        if not self.email_from or not self.email_password:
    72	            logger.warning("Email credentials not configured. Set EMAIL_FROM and EMAIL_PASSWORD.")
    73	
    74	        logger.info(f"EmailNotifier initialized (SMTP: {self.smtp_server}:{self.smtp_port})")
    75	
    76	    def _format_html_table(self, df: pd.DataFrame) -> str:
    77	        """Format DataFrame as HTML table with styling.
    78	
    79	        Args:
    80	            df: DataFrame to format.
    81	
    82	        Returns:
    83	            HTML string with styled table.
    84	        """
    85	        html = '<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">\n'
    86	
    87	        # Header
    88	        html += '  <thead>\n    <tr style="background-color: #2c3e50; color: white;">\n'
    89	        for col in df.columns:
    90	            html += f'      <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">{col}</th>\n'
    91	        html += '    </tr>\n  </thead>\n'
    92	
    93	        # Body
    94	        html += '  <tbody>\n'
    95	        for idx, row in df.iterrows():
    96	            bg_color = '#f9f9f9' if idx % 2 == 0 else 'white'
    97	            html += f'    <tr style="background-color: {bg_color};">\n'
    98	
    99	            for col in df.columns:
   100	                value = row[col]
   101	
   102	                # Format based on column type
   103	                if pd.isna(value):
   104	                    display = 'N/A'
   105	                elif col in ['buy_signal', 'value_score', 'support_score']:
   106	                    # Color code scores
   107	                    val = float(value)
   108	                    if val >= 80:
   109	                        color = '#27ae60'  # Green
   110	                    elif val >= 65:
   111	                        color = '#f39c12'  # Orange
   112	                    else:
   113	                        color = '#95a5a6'  # Gray
   114	                    display = f'<span style="color: {color}; font-weight: bold;">{val:.1f}</span>'
   115	                elif col == 'current_price':
   116	                    display = f'${float(value):.2f}'
   117	                elif col == 'rsi':
   118	                    val = float(value)
   119	                    if val < 30:
   120	                        color = '#e74c3c'  # Red (oversold)
   121	                    elif val < 70:
   122	                        color = '#000'  # Black
   123	                    else:
   124	                        color = '#c0392b'  # Dark red (overbought)
   125	                    display = f'<span style="color: {color};">{val:.1f}</span>'
   126	                elif isinstance(value, (int, float)):
   127	                    display = f'{value:.2f}'
   128	                else:
   129	                    display = str(value)
   130	
   131	                html += f'      <td style="padding: 10px; border: 1px solid #ddd;">{display}</td>\n'
   132	
   133	            html += '    </tr>\n'
   134	
   135	        html += '  </tbody>\n</table>'
   136	        return html
   137	
   138	    def _create_html_email(
   139	        self,
   140	        results: pd.DataFrame,
   141	        top_n: int = 10,
   142	        subject_prefix: str = "[Stock Screener]"
   143	    ) -> str:
   144	        """Create HTML email body with screening results.
   145	
   146	        Args:
   147	            results: DataFrame with screening results.
   148	            top_n: Number of top candidates to include.
   149	            subject_prefix: Prefix for email subject line.
   150	
   151	        Returns:
   152	            HTML email body as string.
   153	        """
   154	        today = datetime.now().strftime('%B %d, %Y')
   155	        total_candidates = len(results)
   156	
   157	        # Get top candidates
   158	        top_results = results.head(top_n)
   159	
   160	        # Select columns for email
   161	        email_cols = [
   162	            'ticker', 'buy_signal', 'value_score', 'support_score',
   163	            'current_price', 'rsi', 'pe_ratio', 'pb_ratio'
   164	        ]
   165	        display_df = top_results[email_cols].copy()
   166	
   167	        # Rename columns for display
   168	        display_df.columns = [
   169	            'Ticker', 'Buy Signal', 'Value', 'Support',
   170	            'Price', 'RSI', 'P/E', 'P/B'
   171	        ]
   172	
   173	        html = f"""
   174	<!DOCTYPE html>
   175	<html>
   176	<head>
   177	    <meta charset="UTF-8">
   178	    <style>
   179	        body {{
   180	            font-family: Arial, sans-serif;
   181	            line-height: 1.6;
   182	            color: #333;
   183	            max-width: 900px;
   184	            margin: 0 auto;
   185	            padding: 20px;
   186	        }}
   187	        .header {{
   188	            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   189	            color: white;
   190	            padding: 30px;
   191	            border-radius: 10px;
   192	            margin-bottom: 30px;
   193	            text-align: center;
   194	        }}
   195	        .header h1 {{
   196	            margin: 0;
   197	            font-size: 28px;
   198	        }}
   199	        .summary {{
   200	            background-color: #f8f9fa;
   201	            padding: 20px;
   202	            border-radius: 8px;
   203	            margin-bottom: 30px;
   204	            border-left: 4px solid #667eea;
   205	        }}
   206	        .legend {{
   207	            background-color: #fff3cd;
   208	            padding: 15px;
   209	            border-radius: 8px;
   210	            margin: 20px 0;
   211	            border-left: 4px solid #ffc107;
   212	        }}
   213	        .footer {{
   214	            margin-top: 30px;
   215	            padding-top: 20px;
   216	            border-top: 2px solid #eee;
   217	            font-size: 12px;
   218	            color: #666;
   219	        }}
   220	        .signal-badge {{
   221	            display: inline-block;
   222	            padding: 4px 8px;
   223	            border-radius: 4px;
   224	            font-weight: bold;
   225	            font-size: 12px;
   226	        }}
   227	        .strong-buy {{ background-color: #d4edda; color: #155724; }}
   228	        .buy {{ background-color: #fff3cd; color: #856404; }}
   229	        .consider {{ background-color: #d1ecf1; color: #0c5460; }}
   230	    </style>
   231	</head>
   232	<body>
   233	    <div class="header">
   234	        <h1>📊 Daily Stock Screening Results</h1>
   235	        <p style="margin: 10px 0 0 0; font-size: 16px;">{today}</p>
   236	    </div>
   237	
   238	    <div class="summary">
   239	        <h2 style="margin-top: 0;">Summary</h2>
   240	        <p><strong>{total_candidates}</strong> stocks screened today. Showing top <strong>{len(top_results)}</strong> candidates.</p>
   241	        <p>
   242	            <span class="signal-badge strong-buy">🔥 STRONG BUY (80+)</span>
   243	            <span class="signal-badge buy">✅ BUY (65-79)</span>
   244	            <span class="signal-badge consider">⚡ CONSIDER (50-64)</span>
   245	        </p>
   246	    </div>
   247	
   248	    <h2>Top {len(top_results)} Candidates</h2>
   249	
   250	    {self._format_html_table(display_df)}
   251	
   252	    <div class="legend">
   253	        <h3 style="margin-top: 0;">📈 What These Scores Mean</h3>
   254	        <ul style="margin: 10px 0;">
   255	            <li><strong>Buy Signal:</strong> Combined score (70+ is actionable)</li>
   256	            <li><strong>Value Score:</strong> Fundamental valuation (80+ is excellent)</li>
   257	            <li><strong>Support Score:</strong> Technical setup (80+ is ready to buy)</li>
   258	            <li><strong>RSI:</strong> <30 = Oversold (buy opportunity), >70 = Overbought</li>
   259	        </ul>
   260	    </div>
   261	
   262	    <div class="footer">
   263	        <p><strong>Automated Stock Screener</strong></p>
   264	        <p>This email was automatically generated by your stock screening system.</p>
   265	        <p>⚠️ This is not financial advice. Always do your own research before investing.</p>
   266	    </div>
   267	</body>
   268	</html>
   269	"""
   270	        return html
   271	
   272	    def send_notification(self, subject: str, message: str) -> bool:
   273	        """Send a short plain-text status notification (e.g. "scan started").
   274	
   275	        Lighter-weight than send_scan_report — no HTML, no signal tables, just a
   276	        quick heads-up. Fails silently (logs + returns False) if unconfigured,
   277	        same as every other notifier method — never raises into the caller.
   278	
   279	        Args:
   280	            subject: Email subject line.
   281	            message: Plain-text body.
   282	
   283	        Returns:
   284	            True if sent successfully, False otherwise.
   285	        """
   286	        if not self.email_from or not self.email_password or not self.email_to:
   287	            logger.warning(f"Email not configured - skipping notification: {subject}")
   288	            return False
   289	
   290	        try:
   291	            msg = MIMEMultipart('alternative')
   292	            msg['From'] = self.email_from
   293	            msg['To'] = self.email_to
   294	            msg['Subject'] = subject
   295	            msg.attach(MIMEText(message, 'plain'))
   296	
   297	            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
   298	                server.starttls()
   299	                server.login(self.email_from, self.email_password)
   300	                recipients = [r.strip() for r in self.email_to.split(',')]
   301	                server.sendmail(self.email_from, recipients, msg.as_string())
   302	
   303	            logger.info(f"✓ Notification email sent: {subject}")
   304	            return True
   305	
   306	        except Exception as e:
   307	            logger.error(f"Failed to send notification email: {e}")
   308	            return False
   309	
   310	    def send_screening_results(
   311	        self,
   312	        results: pd.DataFrame,
   313	        top_n: int = 10,
   314	        subject_prefix: str = "[Stock Screener]"
   315	    ) -> bool:
   316	        """Send screening results via email.
   317	
   318	        Args:
   319	            results: DataFrame with screening results (from screen_candidates).
   320	            top_n: Number of top candidates to include in email.
   321	            subject_prefix: Prefix for email subject line.
   322	
   323	        Returns:
   324	            True if email sent successfully, False otherwise.
   325	
   326	        Example:
   327	            >>> notifier = EmailNotifier()
   328	            >>> results = screen_candidates(db, tickers)
   329	            >>> notifier.send_screening_results(results, top_n=10)
   330	        """
   331	        if not self.email_from or not self.email_password or not self.email_to:
   332	            logger.error("Email configuration incomplete. Check environment variables.")
   333	            return False
   334	
   335	        if results.empty:
   336	            logger.warning("No screening results to send")
   337	            return False
   338	
   339	        try:
   340	            # Create message
   341	            today = datetime.now().strftime('%b %d, %Y')
   342	            subject = f"{subject_prefix} Top {top_n} Candidates - {today}"
   343	
   344	            msg = MIMEMultipart('alternative')
   345	            msg['From'] = self.email_from
   346	            msg['To'] = self.email_to
   347	            msg['Subject'] = subject
   348	
   349	            # Create HTML body
   350	            html_body = self._create_html_email(results, top_n, subject_prefix)
   351	
   352	            # Create plain text fallback
   353	            text_body = self._create_text_fallback(results, top_n)
   354	
   355	            # Attach both versions
   356	            msg.attach(MIMEText(text_body, 'plain'))
   357	            msg.attach(MIMEText(html_body, 'html'))
   358	
   359	            # Send email
   360	            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
   361	            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
   362	                server.starttls()
   363	                server.login(self.email_from, self.email_password)
   364	
   365	                recipients = [r.strip() for r in self.email_to.split(',')]
   366	                server.sendmail(self.email_from, recipients, msg.as_string())
   367	
   368	            logger.info(f"✓ Email sent successfully to {self.email_to}")
   369	            return True
   370	
   371	        except smtplib.SMTPAuthenticationError:
   372	            logger.error("SMTP authentication failed. Check email credentials.")
   373	            return False
   374	        except smtplib.SMTPException as e:
   375	            logger.error(f"SMTP error: {e}")
   376	            return False
   377	        except Exception as e:
   378	            logger.error(f"Failed to send email: {e}")
   379	            return False
   380	
   381	    def send_scan_report(
   382	        self,
   383	        buy_signals: List[Dict],
   384	        sell_signals: List[Dict],
   385	        spy_analysis: Optional[Dict] = None,
   386	        breadth: Optional[Dict] = None,
   387	        top_n: int = 15,
   388	        top20: Optional[List[Dict]] = None,
   389	        fundamentals_audits: Optional[Dict[str, Dict]] = None,
   390	        catalyst_sentiments: Optional[Dict[str, Dict]] = None,
   391	        congress_signals: Optional[Dict[str, Dict]] = None,
   392	        shortlist: Optional[List[Dict]] = None,
   393	    ) -> bool:
   394	        """Send the daily optimized full-market scan results via email.
   395	
   396	        Unlike send_screening_results (which expects a DataFrame in the older
   397	        buy_signal/value_score/pe_ratio shape), this matches the dict shape produced
   398	        by run_optimized_scan.py's score_buy_signal/score_sell_signal — the current
   399	        Minervini-based scanner. Each ticker links straight to its Fidelity trade page.
   400	
   401	        Args:
   402	            buy_signals: List of buy signal dicts (already sorted, highest score first).
   403	            sell_signals: List of sell signal dicts (already sorted, highest score first).
   404	            spy_analysis: Optional SPY trend dict (phase, trend, confidence) for context.
   405	            breadth: Optional market breadth dict.
   406	            top_n: Number of top candidates per list to include in the email.
   407	            top20: Optional pre-ranked pool from top20_ranker.build_top20() —
   408	                combined technical + Reddit-buzz score, with "why it's moving" links.
   409	            fundamentals_audits: Optional {ticker: audit-dict} from
   410	                src.agents.fundamentals_auditor.audit_candidates() — Top 20 only.
   411	            catalyst_sentiments: Optional {ticker: classification-dict} from
   412	                src.agents.catalyst_sentiment.analyze_candidates() — Top 20 only.
   413	            congress_signals: Optional {ticker: signal-dict} from
   414	                src.agents.congress_trades.get_signals_for_candidates() — Top 20 only.
   415	            shortlist: Optional Top 5 from src.agents.shortlist.build_shortlist() —
   416	                the Top 20 pool actually filtered/ranked by the three agents above.
   417	                Rendered as the primary section; top20 is shown below it for reference.
   418	
   419	        Returns:
   420	            True if email sent successfully, False otherwise.
   421	        """
   422	        if not self.email_from or not self.email_password or not self.email_to:
   423	            logger.error("Email configuration incomplete. Check environment variables.")
   424	            return False
   425	
   426	        if not buy_signals and not sell_signals:
   427	            logger.warning("No buy or sell signals to email")
   428	            return False
   429	
   430	        try:
   431	            today = datetime.now().strftime('%b %d, %Y')
   432	            subject = f"[Stock Screener] {len(buy_signals)} Buy / {len(sell_signals)} Sell - {today}"
   433	
   434	            msg = MIMEMultipart('alternative')
   435	            msg['From'] = self.email_from
   436	            msg['To'] = self.email_to
   437	            msg['Subject'] = subject
   438	
   439	            html_body = self._create_scan_html_email(
   440	                buy_signals, sell_signals, spy_analysis, breadth, top_n, top20,
   441	                fundamentals_audits, catalyst_sentiments, congress_signals, shortlist,
   442	            )
   443	            text_body = self._create_scan_text_fallback(
   444	                buy_signals, sell_signals, spy_analysis, top_n, top20, shortlist,
   445	            )
   446	
   447	            msg.attach(MIMEText(text_body, 'plain'))
   448	            msg.attach(MIMEText(html_body, 'html'))
   449	
   450	            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
   451	            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
   452	                server.starttls()
   453	                server.login(self.email_from, self.email_password)
   454	
   455	                recipients = [r.strip() for r in self.email_to.split(',')]
   456	                server.sendmail(self.email_from, recipients, msg.as_string())
   457	
   458	            logger.info(f"✓ Scan report email sent to {self.email_to}")
   459	            return True
   460	
   461	        except smtplib.SMTPAuthenticationError:
   462	            logger.error("SMTP authentication failed. Check email credentials.")
   463	            return False
   464	        except smtplib.SMTPException as e:
   465	            logger.error(f"SMTP error: {e}")
   466	            return False
   467	        except Exception as e:
   468	            logger.error(f"Failed to send scan report email: {e}")
   469	            return False
   470	
   471	    def _scan_row_html(self, ticker: str, cells: List[str], bg: str) -> str:
   472	        """Render one <tr> for the scan report table, with the ticker linked to Fidelity."""
   473	        link = (
   474	            f'<a href="{FIDELITY_TRADE_URL.format(ticker=ticker)}" '
   475	            f'style="color:#1a73e8;text-decoration:none;font-weight:bold;">{ticker} ↗</a>'
   476	        )
   477	        row = f'    <tr style="background-color: {bg};">\n'
   478	        row += f'      <td style="padding: 10px; border: 1px solid #ddd;">{link}</td>\n'
   479	        for cell in cells:
   480	            row += f'      <td style="padding: 10px; border: 1px solid #ddd;">{cell}</td>\n'
   481	        row += '    </tr>\n'
   482	        return row
   483	
   484	    def _reddit_cell(self, count: Optional[int]) -> str:
   485	        """Render a Reddit mention count with hot-ticker styling for the email table."""
   486	        if count is None:
   487	            return '-'
   488	        if count == 0:
   489	            return '0'
   490	        if count >= 10:
   491	            return f'<strong style="color:#e67e22;">{count}</strong>'
   492	        return str(count)
   493	
   494	    def _catalyst_badge_html(self, classification: Optional[Dict]) -> str:
   495	        """Render the Catalyst Sentiment agent's -5..+5 score as a compact colored badge."""
   496	        if not classification:
   497	            return ""
   498	        score = classification.get('catalyst_score', 0)
   499	        ctype = (classification.get('catalyst_type') or 'other').replace('_', ' ')
   500	        if score > 0:
   501	            color, bg = '#155724', '#d4edda'
   502	        elif score < 0:
   503	            color, bg = '#721c24', '#f8d7da'
   504	        else:
   505	            color, bg = '#555', '#eee'
   506	        summary = classification.get('summary', '')
   507	        return (
   508	            f'<div style="margin-top:6px;">'
   509	            f'<span style="background:{bg};color:{color};padding:2px 6px;border-radius:4px;'
   510	            f'font-size:11px;font-weight:bold;">Catalyst {score:+d} — {ctype}</span>'
   511	            f'<div style="font-size:11px;color:#666;margin-top:2px;">{summary}</div>'
   512	            f'</div>'
   513	        )
   514	
   515	    def _congress_badge_html(self, signal: Optional[Dict]) -> str:
   516	        """Render the Congress Trades agent's net buy/sell signal as a compact colored badge.
   517	
   518	        House disclosures only (see src/agents/congress_trades.py for why).
   519	        """
   520	        if not signal or not signal.get('has_data'):
   180	            True if message sent successfully, False otherwise.
   181	
   182	        Example:
   183	            >>> notifier = SlackNotifier()
   184	            >>> results = screen_candidates(db, tickers)
   185	            >>> notifier.send_screening_results(results, top_n=5)
   186	        """
   187	        if results.empty:
   188	            logger.warning("No screening results to send")
   189	            return False
   190	
   191	        try:
   192	            blocks = self._format_slack_blocks(results, top_n)
   193	
   194	            # Try webhook first (simpler)
   195	            if self.webhook_url:
   196	                return self._send_via_webhook(blocks)
   197	            elif self.client:
   198	                return self._send_via_bot(blocks)
   199	            else:
   200	                logger.error("Slack not configured properly")
   201	                return False
   202	
   203	        except Exception as e:
   204	            logger.error(f"Failed to send Slack message: {e}")
   205	            return False
   206	
   207	    def _send_via_webhook(self, blocks: List[Dict]) -> bool:
   208	        """Send message via webhook URL.
   209	
   210	        Args:
   211	            blocks: Slack block elements.
   212	
   213	        Returns:
   214	            True if successful, False otherwise.
   215	        """
   216	        try:
   217	            import requests
   218	
   219	            payload = {"blocks": blocks}
   220	            response = requests.post(
   221	                self.webhook_url,
   222	                json=payload,
   223	                timeout=10
   224	            )
   225	
   226	            if response.status_code == 200:
   227	                logger.info("✓ Slack message sent successfully via webhook")
   228	                return True
   229	            else:
   230	                logger.error(f"Slack webhook failed: {response.status_code} - {response.text}")
   231	                return False
   232	
   233	        except ImportError:
   234	            logger.error("requests library not installed. Install with: pip install requests")
   235	            return False
   236	        except Exception as e:
   237	            logger.error(f"Webhook send failed: {e}")
   238	            return False
   239	
   240	    def _send_via_bot(self, blocks: List[Dict]) -> bool:
   241	        """Send message via bot token.
   242	
   243	        Args:
   244	            blocks: Slack block elements.
   245	
   246	        Returns:
   247	            True if successful, False otherwise.
   248	        """
   249	        try:
   250	            response = self.client.chat_postMessage(
   251	                channel=self.channel,
   252	                blocks=blocks,
   253	                text="Daily Stock Screening Results"  # Fallback text
   254	            )
   255	
   256	            if response['ok']:
   257	                logger.info(f"✓ Slack message sent successfully to {self.channel}")
   258	                return True
   259	            else:
   260	                logger.error(f"Slack bot send failed: {response}")
   261	                return False
   262	
   263	        except Exception as e:
   264	            logger.error(f"Bot send failed: {e}")
   265	            return False
   266	
   267	    def test_connection(self) -> bool:
   268	        """Test Slack connection.
   269	
   270	        Returns:
   271	            True if connection successful, False otherwise.
   272	
   273	        Example:
   274	            >>> notifier = SlackNotifier()
   275	            >>> if notifier.test_connection():
   276	            ...     print("Slack configuration is valid!")
   277	        """
   278	        try:
   279	            if self.webhook_url:
   280	                import requests
   281	                response = requests.post(
   282	                    self.webhook_url,
   283	                    json={"text": "Test message from Stock Screener"},
   284	                    timeout=10
   285	                )
   286	                if response.status_code == 200:
   287	                    logger.info("✓ Slack webhook test successful")
   288	                    return True
   289	                else:
   290	                    logger.error(f"✗ Webhook test failed: {response.status_code}")
   291	                    return False
   292	
   293	            elif self.client:
   294	                response = self.client.auth_test()
   295	                if response['ok']:
   296	                    logger.info(f"✓ Slack bot authenticated as {response['user']}")
   297	                    return True
   298	                else:
   299	                    logger.error("✗ Bot authentication failed")
   300	                    return False
   301	
   302	            else:
   303	                logger.error("✗ Slack not configured")
   304	                return False
   305	
   306	        except Exception as e:
   307	            logger.error(f"✗ Connection test failed: {e}")
   308	            return False

codex
Several candidates are now confirmed by control flow: the legacy control panel can launch duplicate scans due to an unlocked check/start gap, its processes have no watchdog, and SMTP connections have no timeout. I’m validating calculation/storage issues with focused, non-mutating repros and checking test coverage so the final list distinguishes proven bugs from suspicions.
exec
/bin/zsh -lc "rg -n \"timeout|control_panel|save_price_history|momentum|update_streak|api_scan|api_backtest|stop|duplicate|concurrent|SMTP\" tests .github 2>/dev/null || true; if [ -x venv/bin/python ]; then venv/bin/python - <<'PY'
import tempfile
from pathlib import Path
import pandas as pd
from src.data.storage import StockDatabase
p=Path(tempfile.mkdtemp())/'t.db'
db=StockDatabase(f'sqlite:///{p}')
df=pd.DataFrame({'Date':['2024-01-02'],'Open':[1.0],'High':[2.0],'Low':[0.5],'Close':[1.5],'Volume':[100.0]})
db.save_price_history('ABC',df)
try:
 db.save_price_history('ABC',df)
 print('SECOND_SAVE_OK')
except Exception as e:
 print(type(e).__name__, str(e).splitlines()[0])
PY
else echo 'NO_VENV'; fi" in /Users/badripratti/Desktop/stock-screener
 succeeded in 576ms:
2026-09-13 21:57:32,929 - src.data.storage - INFO - Initializing database connection: sqlite:////var/folders/9_/8byz82kn089c6rz3x05wfscc0000gn/T/tmpqhmd5dhg/t.db
2026-09-13 21:57:32,942 - src.data.storage - INFO - Database tables created/verified successfully
2026-09-13 21:57:32,950 - src.data.storage - INFO - Created new stock entry: ABC
2026-09-13 21:57:32,956 - src.data.storage - INFO - Saved 1 price records for ABC
2026-09-13 21:57:32,960 - src.data.storage - ERROR - Failed to save price history for ABC: (sqlite3.IntegrityError) UNIQUE constraint failed: price_history.stock_id, price_history.date
[SQL: INSERT INTO price_history (stock_id, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)]
[parameters: (1, '2024-01-02 00:00:00.000000', 1.0, 2.0, 0.5, 1.5, 100.0)]
(Background on this error at: https://sqlalche.me/e/20/gkpj)
IntegrityError (sqlite3.IntegrityError) UNIQUE constraint failed: price_history.stock_id, price_history.date

exec
/bin/zsh -lc "nl -ba src/data/fundamentals_fetcher.py | sed -n '1,420p'; nl -ba src/data/enhanced_fundamentals.py | sed -n '1,257p'; nl -ba src/data/fmp_fetcher.py | sed -n '1,466p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Enhanced fundamentals fetcher for quarterly financial data.
     2	
     3	This module fetches detailed quarterly financial metrics including:
     4	- Quarterly sales and EPS
     5	- YoY and sequential % changes
     6	- Inventory levels and breakdown
     7	- Margin analysis
     8	"""
     9	
    10	import logging
    11	from typing import Dict, List, Optional
    12	from datetime import datetime
    13	
    14	import yfinance as yf
    15	import pandas as pd
    16	
    17	logging.basicConfig(
    18	    level=logging.INFO,
    19	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    20	)
    21	logger = logging.getLogger(__name__)
    22	
    23	
    24	def _num(quarterly_data: Dict, key: str, default: float = 0) -> float:
    25	    """Get a numeric field from quarterly_data, treating missing AND explicit None as default.
    26	
    27	    dict.get(key, default) only falls back to default when the key is absent — when the
    28	    fetcher stores the key with value None (common for tickers with incomplete filings),
    29	    it returns None and breaks numeric comparisons downstream.
    30	    """
    31	    value = quarterly_data.get(key)
    32	    return default if value is None else value
    33	
    34	
    35	def fetch_quarterly_financials(ticker: str) -> Dict[str, any]:
    36	    """Fetch quarterly financial data for a stock.
    37	
    38	    Args:
    39	        ticker: Stock ticker symbol
    40	
    41	    Returns:
    42	        Dict with quarterly financial metrics
    43	    """
    44	    try:
    45	        stock = yf.Ticker(ticker)
    46	
    47	        # Get quarterly financials
    48	        quarterly_income = stock.quarterly_financials
    49	        quarterly_balance = stock.quarterly_balance_sheet
    50	        quarterly_cashflow = stock.quarterly_cashflow
    51	
    52	        if quarterly_income.empty:
    53	            logger.warning(f"No quarterly income data for {ticker}")
    54	            return {}
    55	
    56	        result = {
    57	            'ticker': ticker,
    58	            'fetch_date': datetime.now().isoformat()
    59	        }
    60	
    61	        # Get quarterly revenue (Total Revenue)
    62	        if 'Total Revenue' in quarterly_income.index:
    63	            revenues = quarterly_income.loc['Total Revenue'].sort_index()
    64	            result['quarterly_revenue'] = revenues.to_dict()
    65	
    66	            if len(revenues) >= 2:
    67	                latest_rev = revenues.iloc[-1]
    68	                prev_rev = revenues.iloc[-2]
    69	                # Check for NaN values - treat as missing data
    70	                import math
    71	                if not math.isnan(latest_rev) and not math.isnan(prev_rev) and prev_rev != 0 and latest_rev != 0:
    72	                    result['revenue_qoq_change'] = ((latest_rev - prev_rev) / prev_rev * 100)
    73	                else:
    74	                    result['revenue_qoq_change'] = None
    75	
    76	            if len(revenues) >= 5:
    77	                latest_rev = revenues.iloc[-1]
    78	                yoy_rev = revenues.iloc[-5]
    79	                # Check for NaN or 0 values - treat as missing data
    80	                import math
    81	                if not math.isnan(latest_rev) and not math.isnan(yoy_rev) and yoy_rev != 0 and latest_rev != 0:
    82	                    result['revenue_yoy_change'] = ((latest_rev - yoy_rev) / yoy_rev * 100)
    83	                else:
    84	                    result['revenue_yoy_change'] = None  # Explicitly mark as missing
    85	
    86	        # Get quarterly EPS (Basic EPS or Diluted EPS)
    87	        eps_key = None
    88	        if 'Diluted EPS' in quarterly_income.index:
    89	            eps_key = 'Diluted EPS'
    90	        elif 'Basic EPS' in quarterly_income.index:
    91	            eps_key = 'Basic EPS'
    92	
    93	        if eps_key:
    94	            eps_values = quarterly_income.loc[eps_key].sort_index()
    95	            result['quarterly_eps'] = eps_values.to_dict()
    96	
    97	            if len(eps_values) >= 2:
    98	                latest_eps = eps_values.iloc[-1]
    99	                prev_eps = eps_values.iloc[-2]
   100	                # Check for NaN values - treat as missing data
   101	                import math
   102	                if not math.isnan(latest_eps) and not math.isnan(prev_eps) and prev_eps != 0 and latest_eps != 0:
   103	                    result['eps_qoq_change'] = ((latest_eps - prev_eps) / abs(prev_eps) * 100)
   104	                else:
   105	                    result['eps_qoq_change'] = None
   106	
   107	            if len(eps_values) >= 5:
   108	                latest_eps = eps_values.iloc[-1]
   109	                yoy_eps = eps_values.iloc[-5]
   110	                import math
   111	                if not math.isnan(latest_eps) and not math.isnan(yoy_eps) and yoy_eps != 0:
   112	                    result['eps_yoy_change'] = ((latest_eps - yoy_eps) / abs(yoy_eps) * 100)
   113	                else:
   114	                    result['eps_yoy_change'] = None  # Explicitly mark as missing
   115	
   116	        # Get gross profit margin
   117	        if 'Gross Profit' in quarterly_income.index and 'Total Revenue' in quarterly_income.index:
   118	            gross_profit = quarterly_income.loc['Gross Profit'].sort_index()
   119	            revenue = quarterly_income.loc['Total Revenue'].sort_index()
   120	
   121	            if len(gross_profit) > 0 and len(revenue) > 0:
   122	                latest_margin = (gross_profit.iloc[-1] / revenue.iloc[-1] * 100) if revenue.iloc[-1] != 0 else 0
   123	                result['gross_margin'] = round(latest_margin, 2)
   124	
   125	                if len(gross_profit) >= 2:
   126	                    prev_margin = (gross_profit.iloc[-2] / revenue.iloc[-2] * 100) if revenue.iloc[-2] != 0 else 0
   127	                    result['margin_change'] = round(latest_margin - prev_margin, 2)
   128	
   129	        # Get operating margin
   130	        if 'Operating Income' in quarterly_income.index and 'Total Revenue' in quarterly_income.index:
   131	            operating_income = quarterly_income.loc['Operating Income'].sort_index()
   132	            revenue = quarterly_income.loc['Total Revenue'].sort_index()
   133	
   134	            if len(operating_income) > 0 and len(revenue) > 0:
   135	                latest_op_margin = (operating_income.iloc[-1] / revenue.iloc[-1] * 100) if revenue.iloc[-1] != 0 else 0
   136	                result['operating_margin'] = round(latest_op_margin, 2)
   137	
   138	        # Get inventory data from balance sheet
   139	        if not quarterly_balance.empty and 'Inventory' in quarterly_balance.index:
   140	            inventory = quarterly_balance.loc['Inventory'].sort_index()
   141	            result['quarterly_inventory'] = inventory.to_dict()
   142	
   143	            if len(inventory) >= 2:
   144	                latest_inv = inventory.iloc[-1]
   145	                prev_inv = inventory.iloc[-2]
   146	                import math
   147	                if not math.isnan(latest_inv) and not math.isnan(prev_inv) and prev_inv != 0 and latest_inv != 0:
   148	                    inv_change = ((latest_inv - prev_inv) / prev_inv * 100)
   149	                    result['inventory_qoq_change'] = round(inv_change, 2)
   150	                else:
   151	                    result['inventory_qoq_change'] = None  # Explicitly mark as missing
   152	
   153	            # Calculate inventory to sales ratio
   154	            if 'Total Revenue' in quarterly_income.index:
   155	                revenues = quarterly_income.loc['Total Revenue'].sort_index()
   156	                if len(revenues) > 0:
   157	                    latest_inv = inventory.iloc[-1]
   158	                    latest_rev = revenues.iloc[-1]
   159	                    inv_to_sales = (latest_inv / latest_rev) if latest_rev != 0 else 0
   160	                    result['inventory_to_sales_ratio'] = round(inv_to_sales, 3)
   161	
   162	        # Try to get inventory breakdown (not always available in yfinance)
   163	        # This is a limitation - detailed inventory breakdown often requires premium data
   164	        result['inventory_breakdown_available'] = False
   165	
   166	        return result
   167	
   168	    except Exception as e:
   169	        logger.error(f"Error fetching quarterly financials for {ticker}: {e}")
   170	        return {}
   171	
   172	
   173	def create_fundamental_snapshot(ticker: str, quarterly_data: Dict) -> str:
   174	    """Create a concise fundamental snapshot summary.
   175	
   176	    Args:
   177	        ticker: Stock ticker
   178	        quarterly_data: Quarterly financial data
   179	
   180	    Returns:
   181	        Formatted snapshot string
   182	    """
   183	    if not quarterly_data:
   184	        return f"FUNDAMENTAL SNAPSHOT - {ticker}\nNo data available"
   185	
   186	    snapshot = f"\n{'='*60}\n"
   187	    snapshot += f"FUNDAMENTAL SNAPSHOT - {ticker}\n"
   188	    snapshot += f"{'='*60}\n"
   189	
   190	    # Revenue analysis with QoQ trend
   191	    yoy = quarterly_data.get('revenue_yoy_change')
   192	    qoq = quarterly_data.get('revenue_qoq_change')
   193	
   194	    # Get quarterly revenue values for trend
   195	    qrev = quarterly_data.get('quarterly_revenue', {})
   196	
   197	    if yoy is not None:
   198	        # Handle QoQ being None (missing data)
   199	        qoq_str = f"{qoq:+.1f}%" if qoq is not None else "N/A"
   200	        if yoy > 20:
   201	            snapshot += f"✓ Revenue: ACCELERATING strongly (YoY: +{yoy:.1f}%, QoQ: {qoq_str})\n"
   202	        elif yoy > 10:
   203	            snapshot += f"✓ Revenue: Growing well (YoY: +{yoy:.1f}%, QoQ: {qoq_str})\n"
   204	        elif yoy > 0:
   205	            snapshot += f"• Revenue: Modest growth (YoY: +{yoy:.1f}%, QoQ: {qoq_str})\n"
   206	        else:
   207	            snapshot += f"✗ Revenue: DETERIORATING (YoY: {yoy:.1f}%, QoQ: {qoq_str})\n"
   208	    else:
   209	        snapshot += "• Revenue: Data not available\n"
   210	
   211	    # Show QoQ trend for past 4 quarters
   212	    if qrev and len(qrev) >= 4:
   213	        import pandas as pd
   214	        rev_series = pd.Series(qrev).sort_index()
   215	        if len(rev_series) >= 4:
   216	            qoq_trends = []
   217	            for i in range(len(rev_series)-1, max(len(rev_series)-5, 0), -1):
   218	                if i > 0:
   219	                    curr = rev_series.iloc[i]
   220	                    prev = rev_series.iloc[i-1]
   221	                    if prev != 0 and not pd.isna(curr) and not pd.isna(prev):
   222	                        qoq_pct = ((curr - prev) / prev) * 100
   223	                        qoq_trends.append(f"{qoq_pct:+.1f}%")
   224	                    else:
   225	                        qoq_trends.append("N/A")
   226	            if qoq_trends:
   227	                snapshot += f"  QoQ Trend (last 4Q): {' → '.join(reversed(qoq_trends))}\n"
   228	
   229	    # EPS analysis with QoQ trend
   230	    eps_yoy = quarterly_data.get('eps_yoy_change')
   231	    eps_qoq = quarterly_data.get('eps_qoq_change')
   232	
   233	    # Get quarterly EPS values for trend
   234	    qeps = quarterly_data.get('quarterly_eps', {})
   235	
   236	    if eps_yoy is not None:
   237	        # Handle QoQ being None (missing data)
   238	        eps_qoq_str = f"{eps_qoq:+.1f}%" if eps_qoq is not None else "N/A"
   239	        if eps_yoy > 25:
   240	            snapshot += f"✓ EPS: STRONG growth (YoY: +{eps_yoy:.1f}%, QoQ: {eps_qoq_str})\n"
   241	        elif eps_yoy > 10:
   242	            snapshot += f"✓ EPS: Growing (YoY: +{eps_yoy:.1f}%, QoQ: {eps_qoq_str})\n"
   243	        elif eps_yoy > 0:
   244	            snapshot += f"• EPS: Slight growth (YoY: +{eps_yoy:.1f}%, QoQ: {eps_qoq_str})\n"
   245	        else:
   246	            snapshot += f"✗ EPS: DECLINING (YoY: {eps_yoy:.1f}%, QoQ: {eps_qoq_str})\n"
   247	    else:
   248	        snapshot += "• EPS: Data not available\n"
   249	
   250	    # Show QoQ trend for past 4 quarters
   251	    if qeps and len(qeps) >= 4:
   252	        import pandas as pd
   253	        eps_series = pd.Series(qeps).sort_index()
   254	        if len(eps_series) >= 4:
   255	            qoq_trends = []
   256	            for i in range(len(eps_series)-1, max(len(eps_series)-5, 0), -1):
   257	                if i > 0:
   258	                    curr = eps_series.iloc[i]
   259	                    prev = eps_series.iloc[i-1]
   260	                    if prev != 0 and not pd.isna(curr) and not pd.isna(prev):
   261	                        qoq_pct = ((curr - prev) / abs(prev)) * 100
   262	                        qoq_trends.append(f"{qoq_pct:+.1f}%")
   263	                    else:
   264	                        qoq_trends.append("N/A")
   265	            if qoq_trends:
   266	                snapshot += f"  QoQ Trend (last 4Q): {' → '.join(reversed(qoq_trends))}\n"
   267	
   268	    # Margin analysis
   269	    if 'gross_margin' in quarterly_data:
   270	        margin = quarterly_data['gross_margin']
   271	        margin_change = _num(quarterly_data, 'margin_change')
   272	
   273	        if margin_change > 1:
   274	            snapshot += f"✓ Margins: EXPANDING ({margin:.1f}%, +{margin_change:.1f}pp QoQ)\n"
   275	        elif margin_change > 0:
   276	            snapshot += f"• Margins: Stable/slightly up ({margin:.1f}%, +{margin_change:.1f}pp QoQ)\n"
   277	        elif margin_change > -1:
   278	            snapshot += f"• Margins: Flat ({margin:.1f}%, {margin_change:.1f}pp QoQ)\n"
   279	        else:
   280	            snapshot += f"✗ Margins: CONTRACTING ({margin:.1f}%, {margin_change:.1f}pp QoQ)\n"
   281	
   282	    # Inventory analysis
   283	    inv_change = quarterly_data.get('inventory_qoq_change')
   284	    inv_to_sales = quarterly_data.get('inventory_to_sales_ratio', 0)
   285	
   286	    if inv_change is not None:
   287	        if inv_change > 10:
   288	            snapshot += f"⚠ Inventory: BUILDING (+{inv_change:.1f}% QoQ, ratio: {inv_to_sales:.2f})\n"
   289	            snapshot += "  → Potential demand weakness or production ramp\n"
   290	        elif inv_change > 5:
   291	            snapshot += f"• Inventory: Moderate build (+{inv_change:.1f}% QoQ, ratio: {inv_to_sales:.2f})\n"
   292	        elif inv_change > 0:
   293	            snapshot += f"• Inventory: Slight increase (+{inv_change:.1f}% QoQ, ratio: {inv_to_sales:.2f})\n"
   294	        elif inv_change > -5:
   295	            snapshot += f"• Inventory: Slight draw ({inv_change:.1f}% QoQ, ratio: {inv_to_sales:.2f})\n"
   296	        else:
   297	            snapshot += f"✓ Inventory: DRAWING ({inv_change:.1f}% QoQ, ratio: {inv_to_sales:.2f})\n"
   298	            snapshot += "  → Strong demand signal\n"
   299	    # Don't show anything if inventory data missing - many companies don't track inventory
   300	
   301	        if not quarterly_data.get('inventory_breakdown_available', False):
   302	            snapshot += "  Note: Detailed breakdown (raw/WIP/finished) not available via API\n"
   303	
   304	    # Overall assessment
   305	    snapshot += "\n"
   306	    snapshot += "Overall Assessment:\n"
   307	
   308	    # Determine if fundamentals support technical breakout
   309	    supports_breakout = True
   310	    concerns = []
   311	
   312	    if _num(quarterly_data, 'revenue_yoy_change') < 0:
   313	        supports_breakout = False
   314	        concerns.append('revenue declining')
   315	
   316	    if _num(quarterly_data, 'eps_yoy_change') < 0:
   317	        supports_breakout = False
   318	        concerns.append('EPS declining')
   319	
   320	    if _num(quarterly_data, 'margin_change') < -2:
   321	        concerns.append('margins contracting')
   322	
   323	    if _num(quarterly_data, 'inventory_qoq_change') > 15:
   324	        concerns.append('inventory building rapidly')
   325	
   326	    if supports_breakout and len(concerns) == 0:
   327	        snapshot += "✓ Fundamentals SUPPORT technical breakout\n"
   328	    elif len(concerns) > 0:
   329	        snapshot += f"⚠ Some concerns: {', '.join(concerns)}\n"
   330	        if not supports_breakout:
   331	            snapshot += "✗ Fundamentals CONTRADICT technical breakout\n"
   332	
   333	    return snapshot
   334	
   335	
   336	def analyze_fundamentals_for_signal(quarterly_data: Dict) -> Dict[str, any]:
   337	    """Analyze fundamentals and return structured assessment.
   338	
   339	    Args:
   340	        quarterly_data: Quarterly financial data
   341	
   342	    Returns:
   343	        Dict with assessment and flags
   344	    """
   345	    if not quarterly_data:
   346	        return {
   347	            'revenue_trend': 'unknown',
   348	            'eps_trend': 'unknown',
   349	            'inventory_signal': 'unknown',
   350	            'supports_breakout': False,
   351	            'penalty_points': 10
   352	        }
   353	
   354	    revenue_yoy = _num(quarterly_data, 'revenue_yoy_change')
   355	    revenue_qoq = quarterly_data.get('revenue_qoq_change')
   356	    eps_yoy = _num(quarterly_data, 'eps_yoy_change')
   357	    inv_change = _num(quarterly_data, 'inventory_qoq_change')
   358	
   359	    # Assess trends
   360	    if revenue_yoy > 10:
   361	        revenue_trend = 'accelerating'
   362	    elif revenue_yoy > 0:
   363	        revenue_trend = 'growing'
   364	    elif revenue_yoy > -5:
   365	        revenue_trend = 'flat'
   366	    else:
   367	        revenue_trend = 'deteriorating'
   368	
   369	    if eps_yoy > 10:
   370	        eps_trend = 'accelerating'
   371	    elif eps_yoy > 0:
   372	        eps_trend = 'growing'
   373	    elif eps_yoy > -5:
   374	        eps_trend = 'flat'
   375	    else:
   376	        eps_trend = 'deteriorating'
   377	
   378	    if inv_change > 15:
   379	        inventory_signal = 'negative'
   380	    elif inv_change > 5:
   381	        inventory_signal = 'caution'
   382	    else:
   383	        inventory_signal = 'neutral'
   384	
   385	    # Check for sequential revenue decline (most recent quarter vs previous quarter)
   386	    sequential_revenue_declining = False
   387	    if revenue_qoq is not None and revenue_qoq < -2:
   388	        sequential_revenue_declining = True
   389	
   390	    # Determine if fundamentals support breakout
   391	    supports_breakout = (
   392	        revenue_trend in ['accelerating', 'growing'] and
   393	        eps_trend in ['accelerating', 'growing'] and
   394	        inventory_signal != 'negative' and
   395	        not sequential_revenue_declining  # Don't support if revenue declining sequentially
   396	    )
   397	
   398	    # Calculate penalty
   399	    penalty = 0
   400	    if revenue_trend == 'deteriorating':
   401	        penalty += 5
   402	    if eps_trend == 'deteriorating':
   403	        penalty += 5
   404	    if inventory_signal == 'negative':
   405	        penalty += 5
   406	
   407	    # STRONG PENALTY for sequential revenue decline >2%
   408	    # This is a red flag - company losing momentum
   409	    if sequential_revenue_declining:
   410	        penalty += 15  # Strong penalty (3x normal)
   411	
   412	    return {
   413	        'revenue_trend': revenue_trend,
   414	        'revenue_qoq': revenue_qoq,
   415	        'sequential_revenue_declining': sequential_revenue_declining,
   416	        'eps_trend': eps_trend,
   417	        'inventory_signal': inventory_signal,
   418	        'supports_breakout': supports_breakout,
   419	        'penalty_points': penalty
   420	    }
     1	"""Enhanced fundamentals wrapper that intelligently uses FMP + yfinance.
     2	
     3	This module provides a unified interface for fetching quarterly fundamentals:
     4	- Tries FMP first (if API key available) for net margins, operating margins, detailed inventory
     5	- Falls back to yfinance if FMP unavailable or rate limited
     6	- Caches results to minimize API calls
     7	
     8	Strategy:
     9	- Use FMP for top buy candidates (detailed analysis)
    10	- Use yfinance for initial screening (fast, no rate limits)
    11	"""
    12	
    13	import logging
    14	import os
    15	from typing import Dict, Optional
    16	
    17	from .fmp_fetcher import FMPFetcher
    18	from .fundamentals_fetcher import (
    19	    fetch_quarterly_financials,
    20	    create_fundamental_snapshot,
    21	    analyze_fundamentals_for_signal
    22	)
    23	
    24	logging.basicConfig(
    25	    level=logging.INFO,
    26	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    27	)
    28	logger = logging.getLogger(__name__)
    29	
    30	
    31	class EnhancedFundamentalsFetcher:
    32	    """Unified fundamentals fetcher using FMP + yfinance."""
    33	
    34	    def __init__(self):
    35	        """Initialize fetcher with FMP if API key available."""
    36	        self.fmp_available = False
    37	        self.fmp_fetcher = None
    38	
    39	        # Check if FMP API key is available
    40	        fmp_api_key = os.getenv('FMP_API_KEY')
    41	        if fmp_api_key:
    42	            try:
    43	                self.fmp_fetcher = FMPFetcher(api_key=fmp_api_key)
    44	                self.fmp_available = True
    45	                logger.info("FMP available - will use for enhanced fundamentals")
    46	            except Exception as e:
    47	                logger.warning(f"FMP initialization failed: {e}. Using yfinance only.")
    48	        else:
    49	            logger.info("FMP_API_KEY not set - using yfinance only")
    50	
    51	        self.fmp_call_count = 0
    52	        self.fmp_daily_limit = 250
    53	
    54	    def fetch_quarterly_data(
    55	        self,
    56	        ticker: str,
    57	        use_fmp: bool = False
    58	    ) -> Dict[str, any]:
    59	        """Fetch quarterly financial data.
    60	
    61	        Args:
    62	            ticker: Stock ticker
    63	            use_fmp: If True and FMP available, use FMP for detailed data
    64	
    65	        Returns:
    66	            Dict with quarterly financial metrics
    67	        """
    68	        # If FMP requested and available, use it
    69	        if use_fmp and self.fmp_available:
    70	            if self.fmp_call_count < self.fmp_daily_limit:
    71	                try:
    72	                    data = self.fmp_fetcher.fetch_comprehensive_fundamentals(ticker)
    73	                    self.fmp_call_count += 4  # 4 API calls per stock
    74	
    75	                    if data and data.get('income_statement'):
    76	                        logger.debug(f"Using FMP data for {ticker}")
    77	                        return self._convert_fmp_to_standard(data)
    78	                    else:
    79	                        logger.warning(f"FMP returned no data for {ticker}, falling back to yfinance")
    80	                except Exception as e:
    81	                    logger.warning(f"FMP fetch failed for {ticker}: {e}. Using yfinance.")
    82	            else:
    83	                logger.warning(f"FMP daily limit reached ({self.fmp_daily_limit}). Using yfinance.")
    84	
    85	        # Fall back to yfinance
    86	        return fetch_quarterly_financials(ticker)
    87	
    88	    def _convert_fmp_to_standard(self, fmp_data: Dict) -> Dict[str, any]:
    89	        """Convert FMP data format to standard format used by signal engine.
    90	
    91	        Args:
    92	            fmp_data: Raw FMP data
    93	
    94	        Returns:
    95	            Dict in standard format
    96	        """
    97	        if not fmp_data or not fmp_data.get('income_statement'):
    98	            return {}
    99	
   100	        income = fmp_data.get('income_statement', [])
   101	        balance = fmp_data.get('balance_sheet', [])
   102	
   103	        if len(income) == 0:
   104	            return {}
   105	
   106	        result = {
   107	            'ticker': fmp_data['ticker'],
   108	            'fetch_date': fmp_data['fetch_date'],
   109	            'data_source': 'fmp'
   110	        }
   111	
   112	        # Latest quarter
   113	        latest_income = income[0]
   114	        prev_income = income[1] if len(income) > 1 else {}
   115	        latest_balance = balance[0] if len(balance) > 0 else {}
   116	        prev_balance = balance[1] if len(balance) > 1 else {}
   117	
   118	        # Revenue
   119	        revenue = latest_income.get('revenue', 0)
   120	        prev_revenue = prev_income.get('revenue', 0)
   121	
   122	        if revenue:
   123	            result['latest_revenue'] = revenue
   124	            if prev_revenue:
   125	                result['revenue_qoq_change'] = ((revenue - prev_revenue) / prev_revenue * 100)
   126	
   127	        # YoY revenue (4 quarters ago)
   128	        if len(income) >= 5:
   129	            yoy_revenue = income[4].get('revenue', 0)
   130	            if yoy_revenue:
   131	                result['revenue_yoy_change'] = ((revenue - yoy_revenue) / yoy_revenue * 100)
   132	
   133	        # EPS
   134	        eps = latest_income.get('eps', 0)
   135	        prev_eps = prev_income.get('eps', 0)
   136	
   137	        if eps:
   138	            result['latest_eps'] = eps
   139	            if prev_eps and prev_eps != 0:
   140	                result['eps_qoq_change'] = ((eps - prev_eps) / abs(prev_eps) * 100)
   141	
   142	        # YoY EPS
   143	        if len(income) >= 5:
   144	            yoy_eps = income[4].get('eps', 0)
   145	            if yoy_eps and yoy_eps != 0:
   146	                result['eps_yoy_change'] = ((eps - yoy_eps) / abs(yoy_eps) * 100)
   147	
   148	        # NET MARGIN (not available in yfinance!)
   149	        net_margin = latest_income.get('netIncomeRatio', 0) * 100
   150	        prev_net_margin = prev_income.get('netIncomeRatio', 0) * 100
   151	
   152	        result['net_margin'] = round(net_margin, 2)
   153	        result['net_margin_change'] = round(net_margin - prev_net_margin, 2)
   154	
   155	        # OPERATING MARGIN (not available in yfinance!)
   156	        operating_margin = latest_income.get('operatingIncomeRatio', 0) * 100
   157	        result['operating_margin'] = round(operating_margin, 2)
   158	
   159	        # Gross margin
   160	        gross_margin = latest_income.get('grossProfitRatio', 0) * 100
   161	        prev_gross_margin = prev_income.get('grossProfitRatio', 0) * 100
   162	
   163	        result['gross_margin'] = round(gross_margin, 2)
   164	        result['margin_change'] = round(gross_margin - prev_gross_margin, 2)
   165	
   166	        # Inventory (detailed in FMP)
   167	        inventory = latest_balance.get('inventory', 0)
   168	        prev_inventory = prev_balance.get('inventory', 0)
   169	
   170	        if inventory:
   171	            result['latest_inventory'] = inventory
   172	            if prev_inventory:
   173	                inv_change = ((inventory - prev_inventory) / prev_inventory * 100)
   174	                result['inventory_qoq_change'] = round(inv_change, 2)
   175	
   176	            if revenue:
   177	                result['inventory_to_sales_ratio'] = round(inventory / revenue, 3)
   178	
   179	        return result
   180	
   181	    def create_snapshot(
   182	        self,
   183	        ticker: str,
   184	        quarterly_data: Optional[Dict] = None,
   185	        use_fmp: bool = False
   186	    ) -> str:
   187	        """Create fundamental snapshot.
   188	
   189	        Args:
   190	            ticker: Stock ticker
   191	            quarterly_data: Pre-fetched data, or will fetch if None
   192	            use_fmp: Use FMP for enhanced snapshot if available
   193	
   194	        Returns:
   195	            Formatted snapshot string
   196	        """
   197	        # Fetch data if not provided
   198	        if quarterly_data is None:
   199	            quarterly_data = self.fetch_quarterly_data(ticker, use_fmp=use_fmp)
   200	
   201	        # If data came from FMP and has enhanced fields, use FMP snapshot
   202	        if (quarterly_data.get('data_source') == 'fmp' and
   203	            self.fmp_available and
   204	            self.fmp_fetcher):
   205	            # Re-fetch FMP data for enhanced snapshot
   206	            fmp_data = self.fmp_fetcher.fetch_comprehensive_fundamentals(ticker)
   207	            if fmp_data:
   208	                return self.fmp_fetcher.create_enhanced_snapshot(ticker, fmp_data)
   209	
   210	        # Fall back to standard snapshot
   211	        return create_fundamental_snapshot(ticker, quarterly_data)
   212	
   213	    def analyze_for_signal(
   214	        self,
   215	        ticker: str,
   216	        quarterly_data: Optional[Dict] = None,
   217	        use_fmp: bool = False
   218	    ) -> Dict[str, any]:
   219	        """Analyze fundamentals for signal engine.
   220	
   221	        Args:
   222	            ticker: Stock ticker
   223	            quarterly_data: Pre-fetched data, or will fetch if None
   224	            use_fmp: Use FMP for enhanced analysis if available
   225	
   226	        Returns:
   227	            Dict with trend analysis and penalty
   228	        """
   229	        if quarterly_data is None:
   230	            quarterly_data = self.fetch_quarterly_data(ticker, use_fmp=use_fmp)
   231	
   232	        return analyze_fundamentals_for_signal(quarterly_data)
   233	
   234	    def get_api_usage(self) -> Dict[str, int]:
   235	        """Get API usage statistics.
   236	
   237	        Returns:
   238	            Dict with FMP call count, limit, and bandwidth
   239	        """
   240	        usage = {
   241	            'fmp_available': self.fmp_available,
   242	            'fmp_calls_used': self.fmp_call_count,
   243	            'fmp_daily_limit': self.fmp_daily_limit,
   244	            'fmp_calls_remaining': max(0, self.fmp_daily_limit - self.fmp_call_count)
   245	        }
   246	
   247	        # Add bandwidth stats if FMP is available
   248	        if self.fmp_available and self.fmp_fetcher:
   249	            bandwidth_stats = self.fmp_fetcher.get_bandwidth_stats()
   250	            usage.update(bandwidth_stats)
   251	
   252	        return usage
   253	
   254	    def reset_usage_counter(self):
   255	        """Reset FMP usage counter (call at start of new day)."""
   256	        self.fmp_call_count = 0
   257	        logger.info("FMP usage counter reset")
     1	"""Financial Modeling Prep (FMP) API fetcher for detailed quarterly fundamentals.
     2	
     3	FMP provides comprehensive financial data including:
     4	- Quarterly income statements (net margins, operating margins)
     5	- Balance sheets (inventory details)
     6	- Cash flow statements
     7	- Ratios and metrics
     8	
     9	Free tier: 250 requests/day
    10	Get free API key: https://site.financialmodelingprep.com/
    11	"""
    12	
    13	import logging
    14	import os
    15	import pickle
    16	import time
    17	from datetime import datetime, timedelta
    18	from pathlib import Path
    19	from typing import Dict, List, Optional
    20	
    21	import requests
    22	from dotenv import load_dotenv
    23	
    24	# Load environment variables
    25	load_dotenv()
    26	
    27	logging.basicConfig(
    28	    level=logging.INFO,
    29	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    30	)
    31	logger = logging.getLogger(__name__)
    32	
    33	
    34	class FMPFetcher:
    35	    """Fetch detailed quarterly fundamentals from Financial Modeling Prep."""
    36	
    37	    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "./data/cache"):
    38	        """Initialize FMP fetcher.
    39	
    40	        Args:
    41	            api_key: FMP API key (or set FMP_API_KEY env variable)
    42	            cache_dir: Directory for caching responses
    43	        """
    44	        self.api_key = api_key or os.getenv('FMP_API_KEY')
    45	
    46	        if not self.api_key:
    47	            logger.warning(
    48	                "No FMP API key found! Set FMP_API_KEY environment variable or pass api_key parameter.\n"
    49	                "Get free key at: https://site.financialmodelingprep.com/developer/docs"
    50	            )
    51	
    52	        self.base_url = "https://financialmodelingprep.com/api/v3"
    53	        self.cache_dir = Path(cache_dir) / "fmp"
    54	        self.cache_dir.mkdir(parents=True, exist_ok=True)
    55	
    56	        # Bandwidth tracking (30-day limit: 20 GB)
    57	        self.bandwidth_used = 0
    58	        self.bandwidth_limit = 20 * 1024 * 1024 * 1024  # 20 GB in bytes
    59	
    60	        logger.info("FMPFetcher initialized")
    61	
    62	    def _get_cache_path(self, ticker: str, endpoint: str) -> Path:
    63	        """Get cache file path."""
    64	        return self.cache_dir / f"{ticker}_{endpoint}.pkl"
    65	
    66	    def _is_cache_valid(self, cache_path: Path, hours: int = 24) -> bool:
    67	        """Check if cache is valid.
    68	
    69	        Uses longer cache (7 days) for non-earnings periods,
    70	        shorter cache (6 hours) during earnings season.
    71	        """
    72	        if not cache_path.exists():
    73	            return False
    74	
    75	        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
    76	
    77	        # Adjust cache duration based on earnings season proximity
    78	        if self._is_earnings_season():
    79	            # During earnings season (Jan 15-Feb 15, Apr 15-May 15, Jul 15-Aug 15, Oct 15-Nov 15)
    80	            # Use shorter cache to catch new earnings
    81	            cache_hours = 6
    82	        else:
    83	            # Outside earnings season, use longer cache to save bandwidth
    84	            cache_hours = 168  # 7 days
    85	
    86	        return datetime.now() - file_time < timedelta(hours=cache_hours)
    87	
    88	    def _is_earnings_season(self) -> bool:
    89	        """Check if currently in earnings season.
    90	
    91	        Earnings seasons (roughly):
    92	        - Q4: Jan 15 - Feb 15
    93	        - Q1: Apr 15 - May 15
    94	        - Q2: Jul 15 - Aug 15
    95	        - Q3: Oct 15 - Nov 15
    96	        """
    97	        now = datetime.now()
    98	        month = now.month
    99	        day = now.day
   100	
   101	        earnings_windows = [
   102	            (1, 15, 2, 15),  # Q4 earnings: Jan 15 - Feb 15
   103	            (4, 15, 5, 15),  # Q1 earnings: Apr 15 - May 15
   104	            (7, 15, 8, 15),  # Q2 earnings: Jul 15 - Aug 15
   105	            (10, 15, 11, 15) # Q3 earnings: Oct 15 - Nov 15
   106	        ]
   107	
   108	        for start_month, start_day, end_month, end_day in earnings_windows:
   109	            if start_month == end_month:
   110	                if month == start_month and start_day <= day <= end_day:
   111	                    return True
   112	            else:
   113	                if (month == start_month and day >= start_day) or \
   114	                   (month == end_month and day <= end_day):
   115	                    return True
   116	
   117	        return False
   118	
   119	    def _fetch(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
   120	        """Fetch from FMP API with rate limiting.
   121	
   122	        Args:
   123	            endpoint: API endpoint
   124	            params: Query parameters
   125	
   126	        Returns:
   127	            JSON response or None
   128	        """
   129	        if not self.api_key:
   130	            logger.error("Cannot fetch without API key")
   131	            return None
   132	
   133	        try:
   134	            # Add API key to params
   135	            params = params or {}
   136	            params['apikey'] = self.api_key
   137	
   138	            url = f"{self.base_url}/{endpoint}"
   139	
   140	            # Rate limiting - be respectful
   141	            time.sleep(0.1)  # 10 requests/second max
   142	
   143	            response = requests.get(url, params=params, timeout=10)
   144	            response.raise_for_status()
   145	
   146	            # Track bandwidth usage
   147	            response_size = len(response.content)
   148	            self.bandwidth_used += response_size
   149	
   150	            # Check bandwidth limit
   151	            if self.bandwidth_used > self.bandwidth_limit:
   152	                logger.warning(
   153	                    f"FMP bandwidth limit exceeded! "
   154	                    f"Used: {self.bandwidth_used / 1024 / 1024:.1f} MB / "
   155	                    f"{self.bandwidth_limit / 1024 / 1024 / 1024:.1f} GB"
   156	                )
   157	
   158	            data = response.json()
   159	
   160	            # Check for error in response
   161	            if isinstance(data, dict) and 'Error Message' in data:
   162	                logger.error(f"FMP API error: {data['Error Message']}")
   163	                return None
   164	
   165	            return data
   166	
   167	        except requests.exceptions.RequestException as e:
   168	            logger.error(f"Error fetching from FMP: {e}")
   169	            return None
   170	
   171	    def fetch_income_statement(self, ticker: str, quarterly: bool = True, limit: int = 8) -> List[Dict]:
   172	        """Fetch income statement data.
   173	
   174	        Args:
   175	            ticker: Stock ticker
   176	            quarterly: True for quarterly, False for annual
   177	            limit: Number of periods to fetch
   178	
   179	        Returns:
   180	            List of income statement periods
   181	        """
   182	        cache_key = f"income_{'q' if quarterly else 'a'}"
   183	        cache_path = self._get_cache_path(ticker, cache_key)
   184	
   185	        # Check cache
   186	        if self._is_cache_valid(cache_path):
   187	            with open(cache_path, 'rb') as f:
   188	                return pickle.load(f)
   189	
   190	        # Fetch from API
   191	        period = "quarter" if quarterly else "annual"
   192	        endpoint = f"income-statement/{ticker}"
   193	        params = {'period': period, 'limit': limit}
   194	
   195	        data = self._fetch(endpoint, params)
   196	
   197	        if data:
   198	            # Cache result
   199	            with open(cache_path, 'wb') as f:
   200	                pickle.dump(data, f)
   201	
   202	        return data or []
   203	
   204	    def fetch_balance_sheet(self, ticker: str, quarterly: bool = True, limit: int = 8) -> List[Dict]:
   205	        """Fetch balance sheet data.
   206	
   207	        Args:
   208	            ticker: Stock ticker
   209	            quarterly: True for quarterly, False for annual
   210	            limit: Number of periods to fetch
   211	
   212	        Returns:
   213	            List of balance sheet periods
   214	        """
   215	        cache_key = f"balance_{'q' if quarterly else 'a'}"
   216	        cache_path = self._get_cache_path(ticker, cache_key)
   217	
   218	        # Check cache
   219	        if self._is_cache_valid(cache_path):
   220	            with open(cache_path, 'rb') as f:
   221	                return pickle.load(f)
   222	
   223	        # Fetch from API
   224	        period = "quarter" if quarterly else "annual"
   225	        endpoint = f"balance-sheet-statement/{ticker}"
   226	        params = {'period': period, 'limit': limit}
   227	
   228	        data = self._fetch(endpoint, params)
   229	
   230	        if data:
   231	            # Cache result
   232	            with open(cache_path, 'wb') as f:
   233	                pickle.dump(data, f)
   234	
   235	        return data or []
   236	
   237	    def fetch_cash_flow(self, ticker: str, quarterly: bool = True, limit: int = 8) -> List[Dict]:
   238	        """Fetch cash flow statement data.
   239	
   240	        Args:
   241	            ticker: Stock ticker
   242	            quarterly: True for quarterly, False for annual
   243	            limit: Number of periods to fetch
   244	
   245	        Returns:
   246	            List of cash flow periods
   247	        """
   248	        cache_key = f"cashflow_{'q' if quarterly else 'a'}"
   249	        cache_path = self._get_cache_path(ticker, cache_key)
   250	
   251	        # Check cache
   252	        if self._is_cache_valid(cache_path):
   253	            with open(cache_path, 'rb') as f:
   254	                return pickle.load(f)
   255	
   256	        # Fetch from API
   257	        period = "quarter" if quarterly else "annual"
   258	        endpoint = f"cash-flow-statement/{ticker}"
   259	        params = {'period': period, 'limit': limit}
   260	
   261	        data = self._fetch(endpoint, params)
   262	
   263	        if data:
   264	            # Cache result
   265	            with open(cache_path, 'wb') as f:
   266	                pickle.dump(data, f)
   267	
   268	        return data or []
   269	
   270	    def fetch_key_metrics(self, ticker: str, quarterly: bool = True, limit: int = 8) -> List[Dict]:
   271	        """Fetch key financial metrics and ratios.
   272	
   273	        Args:
   274	            ticker: Stock ticker
   275	            quarterly: True for quarterly, False for annual
   276	            limit: Number of periods to fetch
   277	
   278	        Returns:
   279	            List of metric periods
   280	        """
   281	        cache_key = f"metrics_{'q' if quarterly else 'a'}"
   282	        cache_path = self._get_cache_path(ticker, cache_key)
   283	
   284	        # Check cache
   285	        if self._is_cache_valid(cache_path):
   286	            with open(cache_path, 'rb') as f:
   287	                return pickle.load(f)
   288	
   289	        # Fetch from API
   290	        period = "quarter" if quarterly else "annual"
   291	        endpoint = f"key-metrics/{ticker}"
   292	        params = {'period': period, 'limit': limit}
   293	
   294	        data = self._fetch(endpoint, params)
   295	
   296	        if data:
   297	            # Cache result
   298	            with open(cache_path, 'wb') as f:
   299	                pickle.dump(data, f)
   300	
   301	        return data or []
   302	
   303	    def fetch_comprehensive_fundamentals(self, ticker: str) -> Dict:
   304	        """Fetch comprehensive quarterly fundamentals.
   305	
   306	        Returns:
   307	            Dict with income statements, balance sheets, cash flow, and metrics
   308	        """
   309	        logger.info(f"Fetching comprehensive fundamentals for {ticker}")
   310	
   311	        return {
   312	            'ticker': ticker,
   313	            'income_statement': self.fetch_income_statement(ticker, quarterly=True, limit=8),
   314	            'balance_sheet': self.fetch_balance_sheet(ticker, quarterly=True, limit=8),
   315	            'cash_flow': self.fetch_cash_flow(ticker, quarterly=True, limit=8),
   316	            'key_metrics': self.fetch_key_metrics(ticker, quarterly=True, limit=8),
   317	            'fetch_date': datetime.now().isoformat()
   318	        }
   319	
   320	    def create_enhanced_snapshot(self, ticker: str, data: Dict = None) -> str:
   321	        """Create enhanced fundamental snapshot with net margins, inventory, etc.
   322	
   323	        Args:
   324	            ticker: Stock ticker
   325	            data: Pre-fetched data, or will fetch if None
   326	
   327	        Returns:
   328	            Formatted snapshot string
   329	        """
   330	        if data is None:
   331	            data = self.fetch_comprehensive_fundamentals(ticker)
   332	
   333	        if not data or not data.get('income_statement'):
   334	            return f"ENHANCED FUNDAMENTAL SNAPSHOT - {ticker}\nNo data available"
   335	
   336	        snapshot = [
   337	            "",
   338	            "="*60,
   339	            f"ENHANCED FUNDAMENTAL SNAPSHOT - {ticker}",
   340	            "="*60,
   341	            ""
   342	        ]
   343	
   344	        # Latest quarter data
   345	        income = data['income_statement'][0] if data.get('income_statement') else {}
   346	        balance = data['balance_sheet'][0] if data.get('balance_sheet') else {}
   347	        prev_income = data['income_statement'][1] if len(data.get('income_statement', [])) > 1 else {}
   348	        prev_balance = data['balance_sheet'][1] if len(data.get('balance_sheet', [])) > 1 else {}
   349	
   350	        # Revenue analysis
   351	        revenue = income.get('revenue', 0)
   352	        prev_revenue = prev_income.get('revenue', 0)
   353	
   354	        if revenue and prev_revenue:
   355	            rev_change = ((revenue - prev_revenue) / prev_revenue * 100)
   356	            if rev_change > 20:
   357	                snapshot.append(f"✓ Revenue: ACCELERATING (${revenue/1e9:.2f}B, +{rev_change:.1f}% QoQ)")
   358	            elif rev_change > 5:
   359	                snapshot.append(f"✓ Revenue: Growing (${revenue/1e9:.2f}B, +{rev_change:.1f}% QoQ)")
   360	            elif rev_change > 0:
   361	                snapshot.append(f"• Revenue: Modest growth (${revenue/1e9:.2f}B, +{rev_change:.1f}% QoQ)")
   362	            else:
   363	                snapshot.append(f"✗ Revenue: DECLINING (${revenue/1e9:.2f}B, {rev_change:.1f}% QoQ)")
   364	
   365	        # EPS analysis
   366	        eps = income.get('eps', 0)
   367	        prev_eps = prev_income.get('eps', 0)
   368	
   369	        if eps and prev_eps:
   370	            eps_change = ((eps - prev_eps) / abs(prev_eps) * 100) if prev_eps != 0 else 0
   371	            if eps_change > 25:
   372	                snapshot.append(f"✓ EPS: STRONG growth (${eps:.2f}, +{eps_change:.1f}% QoQ)")
   373	            elif eps_change > 10:
   374	                snapshot.append(f"✓ EPS: Growing (${eps:.2f}, +{eps_change:.1f}% QoQ)")
   375	            elif eps_change > 0:
   376	                snapshot.append(f"• EPS: Slight growth (${eps:.2f}, +{eps_change:.1f}% QoQ)")
   377	            else:
   378	                snapshot.append(f"✗ EPS: DECLINING (${eps:.2f}, {eps_change:.1f}% QoQ)")
   379	
   380	        # Margin analysis - NET MARGINS!
   381	        net_margin = income.get('netIncomeRatio', 0) * 100  # As percentage
   382	        gross_margin = income.get('grossProfitRatio', 0) * 100
   383	        operating_margin = income.get('operatingIncomeRatio', 0) * 100
   384	
   385	        prev_net_margin = prev_income.get('netIncomeRatio', 0) * 100
   386	        margin_change = net_margin - prev_net_margin
   387	
   388	        snapshot.append("")
   389	        snapshot.append("Margins:")
   390	        snapshot.append(f"  Gross Margin:     {gross_margin:.1f}%")
   391	        snapshot.append(f"  Operating Margin: {operating_margin:.1f}%")
   392	
   393	        if margin_change > 1:
   394	            snapshot.append(f"  Net Margin:       {net_margin:.1f}% ✓ EXPANDING (+{margin_change:.1f}pp)")
   395	        elif margin_change > 0:
   396	            snapshot.append(f"  Net Margin:       {net_margin:.1f}% • Stable (+{margin_change:.1f}pp)")
   397	        elif margin_change > -1:
   398	            snapshot.append(f"  Net Margin:       {net_margin:.1f}% • Flat ({margin_change:.1f}pp)")
   399	        else:
   400	            snapshot.append(f"  Net Margin:       {net_margin:.1f}% ✗ CONTRACTING ({margin_change:.1f}pp)")
   401	
   402	        # Inventory analysis
   403	        inventory = balance.get('inventory', 0)
   404	        prev_inventory = prev_balance.get('inventory', 0)
   405	
   406	        if inventory and prev_inventory:
   407	            inv_change = ((inventory - prev_inventory) / prev_inventory * 100)
   408	            inv_to_revenue = (inventory / revenue * 100) if revenue else 0
   409	
   410	            snapshot.append("")
   411	            snapshot.append("Inventory:")
   412	            snapshot.append(f"  Total: ${inventory/1e9:.2f}B ({inv_to_revenue:.1f}% of revenue)")
   413	
   414	            if inv_change > 15:
   415	                snapshot.append(f"  ⚠ BUILDING rapidly (+{inv_change:.1f}% QoQ)")
   416	                snapshot.append("  → Potential demand weakness")
   417	            elif inv_change > 5:
   418	                snapshot.append(f"  • Moderate build (+{inv_change:.1f}% QoQ)")
   419	            elif inv_change > 0:
   420	                snapshot.append(f"  • Slight increase (+{inv_change:.1f}% QoQ)")
   421	            else:
   422	                snapshot.append(f"  ✓ Drawing down ({inv_change:.1f}% QoQ)")
   423	                snapshot.append("  → Strong demand signal")
   424	
   425	        # Overall assessment
   426	        snapshot.append("")
   427	        snapshot.append("Overall Assessment:")
   428	
   429	        concerns = []
   430	        if revenue and prev_revenue and ((revenue - prev_revenue) / prev_revenue) < 0:
   431	            concerns.append('revenue declining')
   432	        if eps and prev_eps and ((eps - prev_eps) / abs(prev_eps)) < 0:
   433	            concerns.append('EPS declining')
   434	        if margin_change < -2:
   435	            concerns.append('margins contracting')
   436	        if inventory and prev_inventory and ((inventory - prev_inventory) / prev_inventory) > 15:
   437	            concerns.append('inventory building')
   438	
   439	        if len(concerns) == 0:
   440	            snapshot.append("✓ Fundamentals SUPPORT technical breakout")
   441	        else:
   442	            snapshot.append(f"⚠ Concerns: {', '.join(concerns)}")
   443	            if len(concerns) >= 2:
   444	                snapshot.append("✗ Fundamentals CONTRADICT technical breakout")
   445	
   446	        snapshot.append("="*60)
   447	
   448	        return "\n".join(snapshot)
   449	
   450	    def get_bandwidth_stats(self) -> Dict[str, any]:
   451	        """Get bandwidth usage statistics.
   452	
   453	        Returns:
   454	            Dict with bandwidth usage info
   455	        """
   456	        used_mb = self.bandwidth_used / 1024 / 1024
   457	        limit_gb = self.bandwidth_limit / 1024 / 1024 / 1024
   458	        pct_used = (self.bandwidth_used / self.bandwidth_limit * 100) if self.bandwidth_limit > 0 else 0
   459	
   460	        return {
   461	            'bandwidth_used_mb': round(used_mb, 2),
   462	            'bandwidth_limit_gb': round(limit_gb, 2),
   463	            'bandwidth_pct_used': round(pct_used, 2),
   464	            'is_earnings_season': self._is_earnings_season(),
   465	            'cache_hours': 6 if self._is_earnings_season() else 168
   466	        }

exec
/bin/zsh -lc "nl -ba src/data/enhanced_fundamentals.py | sed -n '1,257p'; nl -ba src/screening/quant_engine.py; nl -ba scripts/run_quant_engine.py; nl -ba src/screening/screener.py | sed -n '1,533p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Enhanced fundamentals wrapper that intelligently uses FMP + yfinance.
     2	
     3	This module provides a unified interface for fetching quarterly fundamentals:
     4	- Tries FMP first (if API key available) for net margins, operating margins, detailed inventory
     5	- Falls back to yfinance if FMP unavailable or rate limited
     6	- Caches results to minimize API calls
     7	
     8	Strategy:
     9	- Use FMP for top buy candidates (detailed analysis)
    10	- Use yfinance for initial screening (fast, no rate limits)
    11	"""
    12	
    13	import logging
    14	import os
    15	from typing import Dict, Optional
    16	
    17	from .fmp_fetcher import FMPFetcher
    18	from .fundamentals_fetcher import (
    19	    fetch_quarterly_financials,
    20	    create_fundamental_snapshot,
    21	    analyze_fundamentals_for_signal
    22	)
    23	
    24	logging.basicConfig(
    25	    level=logging.INFO,
    26	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    27	)
    28	logger = logging.getLogger(__name__)
    29	
    30	
    31	class EnhancedFundamentalsFetcher:
    32	    """Unified fundamentals fetcher using FMP + yfinance."""
    33	
    34	    def __init__(self):
    35	        """Initialize fetcher with FMP if API key available."""
    36	        self.fmp_available = False
    37	        self.fmp_fetcher = None
    38	
    39	        # Check if FMP API key is available
    40	        fmp_api_key = os.getenv('FMP_API_KEY')
    41	        if fmp_api_key:
    42	            try:
    43	                self.fmp_fetcher = FMPFetcher(api_key=fmp_api_key)
    44	                self.fmp_available = True
    45	                logger.info("FMP available - will use for enhanced fundamentals")
    46	            except Exception as e:
    47	                logger.warning(f"FMP initialization failed: {e}. Using yfinance only.")
    48	        else:
    49	            logger.info("FMP_API_KEY not set - using yfinance only")
    50	
    51	        self.fmp_call_count = 0
    52	        self.fmp_daily_limit = 250
    53	
    54	    def fetch_quarterly_data(
    55	        self,
    56	        ticker: str,
    57	        use_fmp: bool = False
    58	    ) -> Dict[str, any]:
    59	        """Fetch quarterly financial data.
    60	
    61	        Args:
    62	            ticker: Stock ticker
    63	            use_fmp: If True and FMP available, use FMP for detailed data
    64	
    65	        Returns:
    66	            Dict with quarterly financial metrics
    67	        """
    68	        # If FMP requested and available, use it
    69	        if use_fmp and self.fmp_available:
    70	            if self.fmp_call_count < self.fmp_daily_limit:
    71	                try:
    72	                    data = self.fmp_fetcher.fetch_comprehensive_fundamentals(ticker)
    73	                    self.fmp_call_count += 4  # 4 API calls per stock
    74	
    75	                    if data and data.get('income_statement'):
    76	                        logger.debug(f"Using FMP data for {ticker}")
    77	                        return self._convert_fmp_to_standard(data)
    78	                    else:
    79	                        logger.warning(f"FMP returned no data for {ticker}, falling back to yfinance")
    80	                except Exception as e:
    81	                    logger.warning(f"FMP fetch failed for {ticker}: {e}. Using yfinance.")
    82	            else:
    83	                logger.warning(f"FMP daily limit reached ({self.fmp_daily_limit}). Using yfinance.")
    84	
    85	        # Fall back to yfinance
    86	        return fetch_quarterly_financials(ticker)
    87	
    88	    def _convert_fmp_to_standard(self, fmp_data: Dict) -> Dict[str, any]:
    89	        """Convert FMP data format to standard format used by signal engine.
    90	
    91	        Args:
    92	            fmp_data: Raw FMP data
    93	
    94	        Returns:
    95	            Dict in standard format
    96	        """
    97	        if not fmp_data or not fmp_data.get('income_statement'):
    98	            return {}
    99	
   100	        income = fmp_data.get('income_statement', [])
   101	        balance = fmp_data.get('balance_sheet', [])
   102	
   103	        if len(income) == 0:
   104	            return {}
   105	
   106	        result = {
   107	            'ticker': fmp_data['ticker'],
   108	            'fetch_date': fmp_data['fetch_date'],
   109	            'data_source': 'fmp'
   110	        }
   111	
   112	        # Latest quarter
   113	        latest_income = income[0]
   114	        prev_income = income[1] if len(income) > 1 else {}
   115	        latest_balance = balance[0] if len(balance) > 0 else {}
   116	        prev_balance = balance[1] if len(balance) > 1 else {}
   117	
   118	        # Revenue
   119	        revenue = latest_income.get('revenue', 0)
   120	        prev_revenue = prev_income.get('revenue', 0)
   121	
   122	        if revenue:
   123	            result['latest_revenue'] = revenue
   124	            if prev_revenue:
   125	                result['revenue_qoq_change'] = ((revenue - prev_revenue) / prev_revenue * 100)
   126	
   127	        # YoY revenue (4 quarters ago)
   128	        if len(income) >= 5:
   129	            yoy_revenue = income[4].get('revenue', 0)
   130	            if yoy_revenue:
   131	                result['revenue_yoy_change'] = ((revenue - yoy_revenue) / yoy_revenue * 100)
   132	
   133	        # EPS
   134	        eps = latest_income.get('eps', 0)
   135	        prev_eps = prev_income.get('eps', 0)
   136	
   137	        if eps:
   138	            result['latest_eps'] = eps
   139	            if prev_eps and prev_eps != 0:
   140	                result['eps_qoq_change'] = ((eps - prev_eps) / abs(prev_eps) * 100)
   141	
   142	        # YoY EPS
   143	        if len(income) >= 5:
   144	            yoy_eps = income[4].get('eps', 0)
   145	            if yoy_eps and yoy_eps != 0:
   146	                result['eps_yoy_change'] = ((eps - yoy_eps) / abs(yoy_eps) * 100)
   147	
   148	        # NET MARGIN (not available in yfinance!)
   149	        net_margin = latest_income.get('netIncomeRatio', 0) * 100
   150	        prev_net_margin = prev_income.get('netIncomeRatio', 0) * 100
   151	
   152	        result['net_margin'] = round(net_margin, 2)
   153	        result['net_margin_change'] = round(net_margin - prev_net_margin, 2)
   154	
   155	        # OPERATING MARGIN (not available in yfinance!)
   156	        operating_margin = latest_income.get('operatingIncomeRatio', 0) * 100
   157	        result['operating_margin'] = round(operating_margin, 2)
   158	
   159	        # Gross margin
   160	        gross_margin = latest_income.get('grossProfitRatio', 0) * 100
   161	        prev_gross_margin = prev_income.get('grossProfitRatio', 0) * 100
   162	
   163	        result['gross_margin'] = round(gross_margin, 2)
   164	        result['margin_change'] = round(gross_margin - prev_gross_margin, 2)
   165	
   166	        # Inventory (detailed in FMP)
   167	        inventory = latest_balance.get('inventory', 0)
   168	        prev_inventory = prev_balance.get('inventory', 0)
   169	
   170	        if inventory:
   171	            result['latest_inventory'] = inventory
   172	            if prev_inventory:
   173	                inv_change = ((inventory - prev_inventory) / prev_inventory * 100)
   174	                result['inventory_qoq_change'] = round(inv_change, 2)
   175	
   176	            if revenue:
   177	                result['inventory_to_sales_ratio'] = round(inventory / revenue, 3)
   178	
   179	        return result
   180	
   181	    def create_snapshot(
   182	        self,
   183	        ticker: str,
   184	        quarterly_data: Optional[Dict] = None,
   185	        use_fmp: bool = False
   186	    ) -> str:
   187	        """Create fundamental snapshot.
   188	
   189	        Args:
   190	            ticker: Stock ticker
   191	            quarterly_data: Pre-fetched data, or will fetch if None
   192	            use_fmp: Use FMP for enhanced snapshot if available
   193	
   194	        Returns:
   195	            Formatted snapshot string
   196	        """
   197	        # Fetch data if not provided
   198	        if quarterly_data is None:
   199	            quarterly_data = self.fetch_quarterly_data(ticker, use_fmp=use_fmp)
   200	
   201	        # If data came from FMP and has enhanced fields, use FMP snapshot
   202	        if (quarterly_data.get('data_source') == 'fmp' and
   203	            self.fmp_available and
   204	            self.fmp_fetcher):
   205	            # Re-fetch FMP data for enhanced snapshot
   206	            fmp_data = self.fmp_fetcher.fetch_comprehensive_fundamentals(ticker)
   207	            if fmp_data:
   208	                return self.fmp_fetcher.create_enhanced_snapshot(ticker, fmp_data)
   209	
   210	        # Fall back to standard snapshot
   211	        return create_fundamental_snapshot(ticker, quarterly_data)
   212	
   213	    def analyze_for_signal(
   214	        self,
   215	        ticker: str,
   216	        quarterly_data: Optional[Dict] = None,
   217	        use_fmp: bool = False
   218	    ) -> Dict[str, any]:
   219	        """Analyze fundamentals for signal engine.
   220	
   221	        Args:
   222	            ticker: Stock ticker
   223	            quarterly_data: Pre-fetched data, or will fetch if None
   224	            use_fmp: Use FMP for enhanced analysis if available
   225	
   226	        Returns:
   227	            Dict with trend analysis and penalty
   228	        """
   229	        if quarterly_data is None:
   230	            quarterly_data = self.fetch_quarterly_data(ticker, use_fmp=use_fmp)
   231	
   232	        return analyze_fundamentals_for_signal(quarterly_data)
   233	
   234	    def get_api_usage(self) -> Dict[str, int]:
   235	        """Get API usage statistics.
   236	
   237	        Returns:
   238	            Dict with FMP call count, limit, and bandwidth
   239	        """
   240	        usage = {
   241	            'fmp_available': self.fmp_available,
   242	            'fmp_calls_used': self.fmp_call_count,
   243	            'fmp_daily_limit': self.fmp_daily_limit,
   244	            'fmp_calls_remaining': max(0, self.fmp_daily_limit - self.fmp_call_count)
   245	        }
   246	
   247	        # Add bandwidth stats if FMP is available
   248	        if self.fmp_available and self.fmp_fetcher:
   249	            bandwidth_stats = self.fmp_fetcher.get_bandwidth_stats()
   250	            usage.update(bandwidth_stats)
   251	
   252	        return usage
   253	
   254	    def reset_usage_counter(self):
   255	        """Reset FMP usage counter (call at start of new day)."""
   256	        self.fmp_call_count = 0
   257	        logger.info("FMP usage counter reset")
     1	"""Main Quant Analysis & Execution Engine.
     2	
     3	This is the autonomous engine that:
     4	1. Fetches data (price history + fundamentals)
     5	2. Detects breakout phases
     6	3. Scores stocks
     7	4. Outputs daily buy/sell lists
     8	5. Produces derivative metrics and summaries
     9	6. Provides benchmark stats
    10	"""
    11	
    12	import logging
    13	from typing import Dict, List, Optional
    14	from datetime import datetime, timedelta
    15	
    16	import pandas as pd
    17	import yfinance as yf
    18	
    19	from src.data.fetcher import YahooFinanceFetcher
    20	from src.data.fundamentals_fetcher import (
    21	    fetch_quarterly_financials,
    22	    create_fundamental_snapshot,
    23	    analyze_fundamentals_for_signal
    24	)
    25	from .phase_indicators import (
    26	    classify_phase,
    27	    calculate_relative_strength,
    28	    calculate_sma
    29	)
    30	from .signal_engine import (
    31	    score_buy_signal,
    32	    score_sell_signal,
    33	    format_signal_output
    34	)
    35	from .benchmark import (
    36	    analyze_spy_trend,
    37	    calculate_market_breadth,
    38	    format_benchmark_summary,
    39	    should_generate_signals
    40	)
    41	
    42	logging.basicConfig(
    43	    level=logging.INFO,
    44	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    45	)
    46	logger = logging.getLogger(__name__)
    47	
    48	
    49	class QuantAnalysisEngine:
    50	    """Autonomous Quant Analysis & Execution Engine."""
    51	
    52	    def __init__(self, cache_dir: str = "./data/cache"):
    53	        """Initialize the engine.
    54	
    55	        Args:
    56	            cache_dir: Directory for caching data
    57	        """
    58	        self.fetcher = YahooFinanceFetcher(cache_dir=cache_dir)
    59	        self.spy_data = None
    60	        self.spy_price = None
    61	        logger.info("QuantAnalysisEngine initialized")
    62	
    63	    def fetch_spy_data(self) -> bool:
    64	        """Fetch SPY benchmark data.
    65	
    66	        Returns:
    67	            True if successful
    68	        """
    69	        try:
    70	            logger.info("Fetching SPY data...")
    71	            spy_hist = self.fetcher.fetch_price_history('SPY', period='2y')
    72	
    73	            if spy_hist.empty:
    74	                logger.error("Failed to fetch SPY data")
    75	                return False
    76	
    77	            self.spy_data = spy_hist
    78	            self.spy_price = spy_hist['Close'].iloc[-1]
    79	            logger.info(f"SPY data fetched: {len(spy_hist)} days, current price: ${self.spy_price:.2f}")
    80	            return True
    81	
    82	        except Exception as e:
    83	            logger.error(f"Error fetching SPY data: {e}")
    84	            return False
    85	
    86	    def analyze_stock(self, ticker: str) -> Optional[Dict]:
    87	        """Analyze a single stock.
    88	
    89	        Args:
    90	            ticker: Stock ticker
    91	
    92	        Returns:
    93	            Analysis dict or None if failed
    94	        """
    95	        try:
    96	            logger.info(f"Analyzing {ticker}...")
    97	
    98	            # Fetch price history
    99	            price_data = self.fetcher.fetch_price_history(ticker, period='2y')
   100	
   101	            if price_data.empty or len(price_data) < 200:
   102	                logger.warning(f"{ticker}: Insufficient price data ({len(price_data)} days)")
   103	                return None
   104	
   105	            current_price = price_data['Close'].iloc[-1]
   106	
   107	            # Classify phase
   108	            phase_info = classify_phase(price_data, current_price)
   109	
   110	            # Calculate relative strength vs SPY
   111	            rs_series = calculate_relative_strength(
   112	                price_data['Close'],
   113	                self.spy_data['Close'],
   114	                period=63
   115	            )
   116	
   117	            # Fetch quarterly fundamentals
   118	            quarterly_data = fetch_quarterly_financials(ticker)
   119	            fundamental_analysis = analyze_fundamentals_for_signal(quarterly_data)
   120	
   121	            return {
   122	                'ticker': ticker,
   123	                'price_data': price_data,
   124	                'current_price': current_price,
   125	                'phase_info': phase_info,
   126	                'rs_series': rs_series,
   127	                'quarterly_data': quarterly_data,
   128	                'fundamental_analysis': fundamental_analysis
   129	            }
   130	
   131	        except Exception as e:
   132	            logger.error(f"Error analyzing {ticker}: {e}")
   133	            return None
   134	
   135	    def screen_stocks(self, tickers: List[str]) -> Dict[str, any]:
   136	        """Screen a list of stocks for buy/sell signals.
   137	
   138	        Args:
   139	            tickers: List of stock tickers
   140	
   141	        Returns:
   142	            Dict with buy list, sell list, and benchmark data
   143	        """
   144	        logger.info(f"Screening {len(tickers)} stocks...")
   145	
   146	        # Ensure SPY data is loaded
   147	        if self.spy_data is None:
   148	            if not self.fetch_spy_data():
   149	                logger.error("Cannot proceed without SPY data")
   150	                return {
   151	                    'error': 'Failed to fetch SPY data',
   152	                    'buys': [],
   153	                    'sells': []
   154	                }
   155	
   156	        # Analyze SPY
   157	        spy_analysis = analyze_spy_trend(self.spy_data, self.spy_price)
   158	
   159	        # Analyze all stocks
   160	        all_analyses = []
   161	        phase_results = []
   162	
   163	        for ticker in tickers:
   164	            analysis = self.analyze_stock(ticker)
   165	            if analysis:
   166	                all_analyses.append(analysis)
   167	                phase_results.append({
   168	                    'ticker': ticker,
   169	                    'phase': analysis['phase_info']['phase']
   170	                })
   171	
   172	        logger.info(f"Successfully analyzed {len(all_analyses)}/{len(tickers)} stocks")
   173	
   174	        # Calculate market breadth
   175	        breadth = calculate_market_breadth(phase_results)
   176	
   177	        # Determine if we should generate signals
   178	        signal_recommendation = should_generate_signals(spy_analysis, breadth)
   179	
   180	        # Score buy signals
   181	        buy_candidates = []
   182	        if signal_recommendation['should_generate_buys']:
   183	            for analysis in all_analyses:
   184	                buy_signal = score_buy_signal(
   185	                    ticker=analysis['ticker'],
   186	                    price_data=analysis['price_data'],
   187	                    current_price=analysis['current_price'],
   188	                    phase_info=analysis['phase_info'],
   189	                    rs_series=analysis['rs_series'],
   190	                    fundamentals=analysis['fundamental_analysis']
   191	                )
   192	
   193	                if buy_signal['is_buy']:
   194	                    # Add fundamental snapshot
   195	                    buy_signal['fundamental_snapshot'] = create_fundamental_snapshot(
   196	                        analysis['ticker'],
   197	                        analysis['quarterly_data']
   198	                    )
   199	                    buy_candidates.append(buy_signal)
   200	
   201	        # Sort by score
   202	        buy_candidates = sorted(buy_candidates, key=lambda x: x['score'], reverse=True)
   203	
   204	        # Score sell signals
   205	        sell_candidates = []
   206	        if signal_recommendation['should_generate_sells']:
   207	            for analysis in all_analyses:
   208	                sell_signal = score_sell_signal(
   209	                    ticker=analysis['ticker'],
   210	                    price_data=analysis['price_data'],
   211	                    current_price=analysis['current_price'],
   212	                    phase_info=analysis['phase_info'],
   213	                    rs_series=analysis['rs_series'],
   214	                    previous_phase=None  # Could track this in a database
   215	                )
   216	
   217	                if sell_signal['is_sell']:
   218	                    sell_candidates.append(sell_signal)
   219	
   220	        # Sort by score
   221	        sell_candidates = sorted(sell_candidates, key=lambda x: x['score'], reverse=True)
   222	
   223	        return {
   224	            'timestamp': datetime.now().isoformat(),
   225	            'spy_analysis': spy_analysis,
   226	            'breadth': breadth,
   227	            'signal_recommendation': signal_recommendation,
   228	            'buys': buy_candidates,
   229	            'sells': sell_candidates,
   230	            'total_analyzed': len(all_analyses)
   231	        }
   232	
   233	    def run(self, tickers: List[str]) -> str:
   234	        """Run the complete screening engine and return formatted output.
   235	
   236	        Args:
   237	            tickers: List of stock tickers to screen
   238	
   239	        Returns:
   240	            Formatted output string
   241	        """
   242	        logger.info("="*60)
   243	        logger.info("QUANT ANALYSIS & EXECUTION ENGINE - STARTING")
   244	        logger.info("="*60)
   245	
   246	        # Screen stocks
   247	        results = self.screen_stocks(tickers)
   248	
   249	        if 'error' in results:
   250	            return f"ERROR: {results['error']}"
   251	
   252	        # Format output
   253	        output = []
   254	
   255	        # Header
   256	        output.append("\n" + "="*60)
   257	        output.append("QUANT ANALYSIS & EXECUTION ENGINE")
   258	        output.append(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
   259	        output.append(f"Stocks Analyzed: {results['total_analyzed']}")
   260	        output.append("="*60)
   261	
   262	        # Benchmark Summary
   263	        output.append(format_benchmark_summary(
   264	            results['spy_analysis'],
   265	            results['breadth']
   266	        ))
   267	
   268	        # Buy List
   269	        output.append("\n" + "="*60)
   270	        output.append("BUY LIST (Score >= 70)")
   271	        output.append("="*60)
   272	
   273	        if results['buys']:
   274	            output.append(f"\nFound {len(results['buys'])} BUY signals:\n")
   275	
   276	            for i, buy in enumerate(results['buys'], 1):
   277	                output.append(f"\n{'#'*60}")
   278	                output.append(f"BUY #{i}: {buy['ticker']} | Score: {buy['score']}/100")
   279	                output.append(f"{'#'*60}")
   280	                output.append(f"Phase: {buy['phase']}")
   281	                output.append(f"Breakout Price: ${buy['breakout_price']:.2f}" if buy['breakout_price'] else "Breakout Price: N/A")
   282	
   283	                # Details
   284	                details = buy.get('details', {})
   285	                if 'rs_slope' in details:
   286	                    output.append(f"RS Slope (3-week): {details['rs_slope']:.3f}")
   287	                if 'volume_ratio' in details:
   288	                    output.append(f"Volume vs Avg: {details['volume_ratio']:.1f}x")
   289	                if 'distance_from_50sma' in buy['phase']:
   290	                    phase_info = buy.get('phase_info', {})
   291	                    output.append(f"Distance from 50 SMA: {phase_info.get('distance_from_50sma', 0):.1f}%")
   292	
   293	                # Reasons
   294	                output.append("\nReasons:")
   295	                for reason in buy['reasons']:
   296	                    output.append(f"  • {reason}")
   297	
   298	                # Fundamental Snapshot
   299	                if 'fundamental_snapshot' in buy:
   300	                    output.append(buy['fundamental_snapshot'])
   301	
   302	        else:
   303	            output.append("\n✗ NO BUYS TODAY")
   304	            reasons = results['signal_recommendation'].get('reasons', [])
   305	            if reasons:
   306	                output.append("\nReasons:")
   307	                for reason in reasons:
   308	                    output.append(f"  • {reason}")
   309	
   310	        # Sell List
   311	        output.append("\n" + "="*60)
   312	        output.append("SELL LIST (Score >= 60)")
   313	        output.append("="*60)
   314	
   315	        if results['sells']:
   316	            output.append(f"\nFound {len(results['sells'])} SELL signals:\n")
   317	
   318	            for i, sell in enumerate(results['sells'], 1):
   319	                output.append(f"\n{'#'*60}")
   320	                output.append(f"SELL #{i}: {sell['ticker']} | Score: {sell['score']}/100 | Severity: {sell['severity'].upper()}")
   321	                output.append(f"{'#'*60}")
   322	                output.append(f"Phase: {sell['phase']}")
   323	                output.append(f"Breakdown Level: ${sell['breakdown_level']:.2f}" if sell['breakdown_level'] else "Breakdown Level: N/A")
   324	
   325	                # Details
   326	                details = sell.get('details', {})
   327	                if 'rs_slope' in details:
   328	                    output.append(f"RS Rollover: {details['rs_slope']:.3f}")
   329	                if 'volume_ratio' in details:
   330	                    output.append(f"Volume vs Avg: {details['volume_ratio']:.1f}x")
   331	
   332	                # Reasons
   333	                output.append("\nReasons:")
   334	                for reason in sell['reasons']:
   335	                    output.append(f"  • {reason}")
   336	
   337	        else:
   338	            output.append("\n✗ NO SELLS TODAY")
   339	
   340	        # Footer
   341	        output.append("\n" + "="*60)
   342	        output.append("END OF REPORT")
   343	        output.append("="*60)
   344	
   345	        report = "\n".join(output)
   346	        logger.info("Screening complete")
   347	
   348	        return report
     1	#!/usr/bin/env python3
     2	"""Run the Quant Analysis & Execution Engine.
     3	
     4	This script loads the stock universe from config.yaml and runs the complete
     5	Phase-based screening system.
     6	
     7	Usage:
     8	    python run_quant_engine.py
     9	    python run_quant_engine.py --tickers AAPL MSFT GOOGL
    10	    python run_quant_engine.py --config custom_config.yaml
    11	"""
    12	
    13	import argparse
    14	import logging
    15	import sys
    16	from datetime import datetime
    17	from pathlib import Path
    18	
    19	import yaml
    20	
    21	from src.screening.quant_engine import QuantAnalysisEngine
    22	
    23	logging.basicConfig(
    24	    level=logging.INFO,
    25	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    26	)
    27	logger = logging.getLogger(__name__)
    28	
    29	
    30	def load_config(config_path: str = 'config.yaml') -> dict:
    31	    """Load configuration from YAML file.
    32	
    33	    Args:
    34	        config_path: Path to config file
    35	
    36	    Returns:
    37	        Config dict
    38	    """
    39	    try:
    40	        with open(config_path, 'r') as f:
    41	            config = yaml.safe_load(f)
    42	        logger.info(f"Loaded config from {config_path}")
    43	        return config
    44	    except Exception as e:
    45	        logger.error(f"Error loading config: {e}")
    46	        return {}
    47	
    48	
    49	def save_results(report: str, output_dir: str = './data/results'):
    50	    """Save screening results to file.
    51	
    52	    Args:
    53	        report: Report string
    54	        output_dir: Output directory
    55	    """
    56	    try:
    57	        # Create output directory
    58	        Path(output_dir).mkdir(parents=True, exist_ok=True)
    59	
    60	        # Generate filename with timestamp
    61	        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    62	        filename = f"quant_screen_{timestamp}.txt"
    63	        filepath = Path(output_dir) / filename
    64	
    65	        # Save report
    66	        with open(filepath, 'w') as f:
    67	            f.write(report)
    68	
    69	        logger.info(f"Results saved to {filepath}")
    70	        return str(filepath)
    71	
    72	    except Exception as e:
    73	        logger.error(f"Error saving results: {e}")
    74	        return None
    75	
    76	
    77	def main():
    78	    """Main entry point."""
    79	    parser = argparse.ArgumentParser(
    80	        description='Run Quant Analysis & Execution Engine'
    81	    )
    82	    parser.add_argument(
    83	        '--config',
    84	        type=str,
    85	        default='config.yaml',
    86	        help='Path to config file (default: config.yaml)'
    87	    )
    88	    parser.add_argument(
    89	        '--tickers',
    90	        nargs='+',
    91	        help='Override config with specific tickers'
    92	    )
    93	    parser.add_argument(
    94	        '--no-save',
    95	        action='store_true',
    96	        help='Do not save results to file'
    97	    )
    98	    parser.add_argument(
    99	        '--cache-dir',
   100	        type=str,
   101	        default='./data/cache',
   102	        help='Cache directory (default: ./data/cache)'
   103	    )
   104	
   105	    args = parser.parse_args()
   106	
   107	    # Load config
   108	    config = load_config(args.config)
   109	
   110	    # Get stock universe
   111	    if args.tickers:
   112	        tickers = args.tickers
   113	        logger.info(f"Using command-line tickers: {tickers}")
   114	    elif config and 'stock_universe' in config:
   115	        tickers = config['stock_universe']
   116	        logger.info(f"Using {len(tickers)} tickers from config")
   117	    else:
   118	        logger.error("No stock universe specified")
   119	        sys.exit(1)
   120	
   121	    # Initialize engine
   122	    engine = QuantAnalysisEngine(cache_dir=args.cache_dir)
   123	
   124	    # Run screening
   125	    try:
   126	        logger.info("Starting Quant Analysis Engine...")
   127	        report = engine.run(tickers)
   128	
   129	        # Print report
   130	        print(report)
   131	
   132	        # Save to file if requested
   133	        if not args.no_save:
   134	            output_dir = config.get('output', {}).get('output_dir', './data/results')
   135	            save_results(report, output_dir)
   136	
   137	    except KeyboardInterrupt:
   138	        logger.info("\nScreening interrupted by user")
   139	        sys.exit(0)
   140	    except Exception as e:
   141	        logger.error(f"Error running engine: {e}", exc_info=True)
   142	        sys.exit(1)
   143	
   144	
   145	if __name__ == '__main__':
   146	    main()
     1	"""Stock screening module for identifying undervalued stocks at support levels.
     2	
     3	This module combines fundamental analysis (value scoring) with technical analysis
     4	(support level detection) to identify high-probability buying opportunities.
     5	"""
     6	
     7	import logging
     8	from typing import Dict, List, Optional
     9	
    10	import numpy as np
    11	import pandas as pd
    12	
    13	from src.data.storage import StockDatabase
    14	from .indicators import (
    15	    calculate_rsi,
    16	    calculate_sma,
    17	    calculate_ema,
    18	    detect_volume_spike,
    19	    find_swing_lows
    20	)
    21	
    22	# Configure logging
    23	logging.basicConfig(
    24	    level=logging.INFO,
    25	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    26	)
    27	logger = logging.getLogger(__name__)
    28	
    29	
    30	def calculate_value_score(fundamentals: Dict[str, any]) -> float:
    31	    """Calculate value score based on fundamental metrics.
    32	
    33	    The value score combines P/E ratio, P/B ratio, and FCF yield to assess
    34	    whether a stock is undervalued. Higher scores indicate better value.
    35	
    36	    Scoring criteria:
    37	    - P/E ratio: < 15 gets max points, scaled up to 30
    38	    - P/B ratio: < 1.5 gets max points, scaled up to 3.0
    39	    - FCF yield: > 5% gets max points, scaled down to 0%
    40	    - Debt/Equity: < 50% gets bonus points
    41	
    42	    Args:
    43	        fundamentals: Dictionary containing fundamental metrics with keys:
    44	                     'pe_ratio', 'pb_ratio', 'fcf_yield', 'debt_equity'.
    45	
    46	    Returns:
    47	        Float score between 0 and 100. Higher is better.
    48	        - 80-100: Excellent value
    49	        - 60-79: Good value
    50	        - 40-59: Fair value
    51	        - 0-39: Poor value
    52	
    53	    Example:
    54	        >>> fundamentals = {
    55	        ...     'pe_ratio': 12.5,
    56	        ...     'pb_ratio': 1.2,
    57	        ...     'fcf_yield': 6.5,
    58	        ...     'debt_equity': 45.0
    59	        ... }
    60	        >>> score = calculate_value_score(fundamentals)
    61	        >>> print(f"Value score: {score:.1f}")
    62	    """
    63	    score = 0.0
    64	    max_score = 100.0
    65	
    66	    # Extract metrics with defaults
    67	    pe_ratio = fundamentals.get('pe_ratio')
    68	    pb_ratio = fundamentals.get('pb_ratio')
    69	    fcf_yield = fundamentals.get('fcf_yield')
    70	    debt_equity = fundamentals.get('debt_equity')
    71	
    72	    # P/E Ratio Score (40 points max)
    73	    # Best: P/E < 15, Acceptable: P/E < 30
    74	    if pe_ratio is not None and pe_ratio > 0:
    75	        if pe_ratio <= 15:
    76	            score += 40
    77	        elif pe_ratio <= 30:
    78	            # Linear scale from 40 down to 20
    79	            score += 40 - ((pe_ratio - 15) / 15) * 20
    80	        elif pe_ratio <= 50:
    81	            # Linear scale from 20 down to 0
    82	            score += 20 - ((pe_ratio - 30) / 20) * 20
    83	        else:
    84	            score += 0
    85	    else:
    86	        logger.debug("P/E ratio missing or invalid")
    87	
    88	    # P/B Ratio Score (30 points max)
    89	    # Best: P/B < 1.5, Acceptable: P/B < 3.0
    90	    if pb_ratio is not None and pb_ratio > 0:
    91	        if pb_ratio <= 1.5:
    92	            score += 30
    93	        elif pb_ratio <= 3.0:
    94	            # Linear scale from 30 down to 10
    95	            score += 30 - ((pb_ratio - 1.5) / 1.5) * 20
    96	        elif pb_ratio <= 5.0:
    97	            # Linear scale from 10 down to 0
    98	            score += 10 - ((pb_ratio - 3.0) / 2.0) * 10
    99	        else:
   100	            score += 0
   101	    else:
   102	        logger.debug("P/B ratio missing or invalid")
   103	
   104	    # FCF Yield Score (20 points max)
   105	    # Best: FCF yield > 5%, Acceptable: FCF yield > 0%
   106	    if fcf_yield is not None:
   107	        if fcf_yield >= 5.0:
   108	            score += 20
   109	        elif fcf_yield > 0:
   110	            # Linear scale from 0 to 20
   111	            score += (fcf_yield / 5.0) * 20
   112	        else:
   113	            score += 0
   114	    else:
   115	        logger.debug("FCF yield missing")
   116	
   117	    # Debt/Equity Ratio Bonus (10 points max)
   118	    # Best: Debt/Equity < 50%, Acceptable: < 100%
   119	    if debt_equity is not None:
   120	        if debt_equity <= 50:
   121	            score += 10
   122	        elif debt_equity <= 100:
   123	            # Linear scale from 10 down to 5
   124	            score += 10 - ((debt_equity - 50) / 50) * 5
   125	        elif debt_equity <= 200:
   126	            # Linear scale from 5 down to 0
   127	            score += 5 - ((debt_equity - 100) / 100) * 5
   128	        else:
   129	            score += 0
   130	    else:
   131	        logger.debug("Debt/Equity ratio missing")
   132	
   133	    # Normalize to 0-100
   134	    score = min(max(score, 0.0), max_score)
   135	
   136	    logger.debug(
   137	        f"Value score: {score:.1f} (PE: {pe_ratio}, PB: {pb_ratio}, "
   138	        f"FCF: {fcf_yield}, D/E: {debt_equity})"
   139	    )
   140	
   141	    return round(score, 2)
   142	
   143	
   144	def detect_support_levels(price_df: pd.DataFrame) -> List[float]:
   145	    """Detect support levels from price history.
   146	
   147	    Support levels are identified using:
   148	    1. Swing lows (local minimums over 30-day window)
   149	    2. 50-day and 200-day moving averages
   150	    3. Recent significant lows
   151	
   152	    Args:
   153	        price_df: DataFrame with columns: Date, Open, High, Low, Close, Volume.
   154	                 Must have at least 200 days of data for full analysis.
   155	
   156	    Returns:
   157	        List of support price levels, sorted from lowest to highest.
   158	        Returns empty list if insufficient data or errors occur.
   159	
   160	    Example:
   161	        >>> price_df = pd.DataFrame({
   162	        ...     'Date': pd.date_range('2023-01-01', periods=250),
   163	        ...     'Close': [100 + i * 0.1 for i in range(250)],
   164	        ...     'High': [102 + i * 0.1 for i in range(250)],
   165	        ...     'Low': [98 + i * 0.1 for i in range(250)]
   166	        ... })
   167	        >>> supports = detect_support_levels(price_df)
   168	        >>> print(supports)
   169	    """
   170	    if price_df.empty:
   171	        logger.warning("Empty price DataFrame provided")
   172	        return []
   173	
   174	    required_cols = ['Close', 'High', 'Low']
   175	    missing_cols = [col for col in required_cols if col not in price_df.columns]
   176	    if missing_cols:
   177	        logger.error(f"Missing required columns: {missing_cols}")
   178	        return []
   179	
   180	    try:
   181	        support_levels = []
   182	        close_prices = price_df['Close']
   183	
   184	        # 1. Find swing lows (local minimums)
   185	        if len(close_prices) >= 61:  # Need at least 30 days on each side + 1
   186	            swing_lows = find_swing_lows(close_prices, window=30)
   187	            support_levels.extend(swing_lows)
   188	            logger.debug(f"Found {len(swing_lows)} swing lows")
   189	
   190	        # 2. Calculate 50-day moving average
   191	        if len(close_prices) >= 50:
   192	            sma_50 = calculate_sma(close_prices, period=50)
   193	            if not sma_50.isna().all():
   194	                support_levels.append(float(sma_50.iloc[-1]))
   195	                logger.debug(f"Added SMA-50: {sma_50.iloc[-1]:.2f}")
   196	
   197	        # 3. Calculate 200-day moving average
   198	        if len(close_prices) >= 200:
   199	            sma_200 = calculate_sma(close_prices, period=200)
   200	            if not sma_200.isna().all():
   201	                support_levels.append(float(sma_200.iloc[-1]))
   202	                logger.debug(f"Added SMA-200: {sma_200.iloc[-1]:.2f}")
   203	
   204	        # 4. Add significant recent lows (last 90 days)
   205	        if len(close_prices) >= 90:
   206	            recent_low = close_prices.iloc[-90:].min()
   207	            support_levels.append(float(recent_low))
   208	            logger.debug(f"Added recent low: {recent_low:.2f}")
   209	
   210	        # 5. Add 52-week low if available
   211	        if len(close_prices) >= 252:  # Trading days in a year
   212	            week_52_low = close_prices.iloc[-252:].min()
   213	            support_levels.append(float(week_52_low))
   214	            logger.debug(f"Added 52-week low: {week_52_low:.2f}")
   215	
   216	        # Remove duplicates and sort
   217	        # Group similar levels (within 0.5% of each other)
   218	        if support_levels:
   219	            support_levels = sorted(set(support_levels))
   220	            consolidated = [support_levels[0]]
   221	
   222	            for level in support_levels[1:]:
   223	                # If level is more than 0.5% different from last, add it
   224	                if abs(level - consolidated[-1]) / consolidated[-1] > 0.005:
   225	                    consolidated.append(level)
   226	
   227	            logger.info(f"Detected {len(consolidated)} support levels")
   228	            return consolidated
   229	
   230	        return []
   231	
   232	    except Exception as e:
   233	        logger.error(f"Error detecting support levels: {e}")
   234	        return []
   235	
   236	
   237	def calculate_support_score(
   238	    current_price: float,
   239	    support_levels: List[float],
   240	    rsi: Optional[float] = None,
   241	    volume_spike: bool = False,
   242	    price_history: Optional[pd.DataFrame] = None
   243	) -> float:
   244	    """Calculate support score based on technical factors.
   245	
   246	    The support score assesses how close the stock is to support levels and
   247	    whether technical indicators suggest a buying opportunity.
   248	
   249	    Scoring criteria:
   250	    - Distance from nearest support: Closer is better (max 40 points)
   251	    - RSI oversold (< 40): Bonus points (max 30 points)
   252	    - Volume spike on dip: Bonus points (20 points)
   253	    - Price at support level: Bonus points (10 points)
   254	
   255	    Args:
   256	        current_price: Current stock price.
   257	        support_levels: List of identified support price levels.
   258	        rsi: Current RSI value (0-100). Optional.
   259	        volume_spike: Whether volume is significantly elevated. Optional.
   260	        price_history: DataFrame with price data for additional analysis. Optional.
   261	
   262	    Returns:
   263	        Float score between 0 and 100. Higher indicates better technical setup.
   264	        - 80-100: Excellent technical setup
   265	        - 60-79: Good technical setup
   266	        - 40-59: Fair technical setup
   267	        - 0-39: Poor technical setup
   268	
   269	    Example:
   270	        >>> score = calculate_support_score(
   271	        ...     current_price=95.5,
   272	        ...     support_levels=[90, 95, 100],
   273	        ...     rsi=35,
   274	        ...     volume_spike=True
   275	        ... )
   276	        >>> print(f"Support score: {score:.1f}")
   277	    """
   278	    if current_price <= 0:
   279	        logger.warning("Invalid current price")
   280	        return 0.0
   281	
   282	    score = 0.0
   283	
   284	    # 1. Distance from nearest support (40 points max)
   285	    if support_levels:
   286	        # Find nearest support below current price
   287	        supports_below = [s for s in support_levels if s <= current_price]
   288	
   289	        if supports_below:
   290	            nearest_support = max(supports_below)
   291	            distance_pct = ((current_price - nearest_support) / nearest_support) * 100
   292	
   293	            if distance_pct <= 1.0:
   294	                # Within 1% of support - excellent
   295	                score += 40
   296	                logger.debug(f"At support level: {distance_pct:.2f}% away")
   297	            elif distance_pct <= 3.0:
   298	                # Within 3% of support - very good
   299	                score += 40 - ((distance_pct - 1.0) / 2.0) * 15
   300	                logger.debug(f"Near support: {distance_pct:.2f}% away")
   301	            elif distance_pct <= 5.0:
   302	                # Within 5% of support - good
   303	                score += 25 - ((distance_pct - 3.0) / 2.0) * 10
   304	                logger.debug(f"Approaching support: {distance_pct:.2f}% away")
   305	            elif distance_pct <= 10.0:
   306	                # Within 10% of support - fair
   307	                score += 15 - ((distance_pct - 5.0) / 5.0) * 15
   308	                logger.debug(f"Distant from support: {distance_pct:.2f}% away")
   309	            else:
   310	                logger.debug(f"Far from support: {distance_pct:.2f}% away")
   311	        else:
   312	            # Current price below all support levels
   313	            logger.debug("Price below all known support levels")
   314	            score += 20  # Potential new support forming
   315	
   316	    # 2. RSI Score (30 points max)
   317	    if rsi is not None:
   318	        if rsi <= 30:
   319	            # Deeply oversold - excellent buying opportunity
   320	            score += 30
   321	            logger.debug(f"Deeply oversold: RSI {rsi:.1f}")
   322	        elif rsi <= 40:
   323	            # Oversold - good buying opportunity
   324	            score += 30 - ((rsi - 30) / 10) * 10
   325	            logger.debug(f"Oversold: RSI {rsi:.1f}")
   326	        elif rsi <= 50:
   327	            # Approaching oversold
   328	            score += 20 - ((rsi - 40) / 10) * 10
   329	            logger.debug(f"Neutral RSI: {rsi:.1f}")
   330	        elif rsi >= 70:
   331	            # Overbought - negative signal
   332	            score -= 10
   333	            logger.debug(f"Overbought: RSI {rsi:.1f}")
   334	
   335	    # 3. Volume Spike Bonus (20 points)
   336	    if volume_spike:
   337	        score += 20
   338	        logger.debug("Volume spike detected - accumulation signal")
   339	
   340	    # 4. Multiple support confluence (10 points bonus)
   341	    if support_levels:
   342	        # Check if multiple support levels are clustered near current price
   343	        supports_nearby = [
   344	            s for s in support_levels
   345	            if abs(current_price - s) / current_price <= 0.03
   346	        ]
   347	        if len(supports_nearby) >= 2:
   348	            score += 10
   349	            logger.debug(f"Multiple support confluence: {len(supports_nearby)} levels")
   350	
   351	    # 5. Additional analysis with price history
   352	    if price_history is not None and not price_history.empty:
   353	        try:
   354	            # Check if price is in lower 25% of recent range
   355	            if len(price_history) >= 90:
   356	                recent_high = price_history['High'].iloc[-90:].max()
   357	                recent_low = price_history['Low'].iloc[-90:].min()
   358	                price_range = recent_high - recent_low
   359	
   360	                if price_range > 0:
   361	                    position = (current_price - recent_low) / price_range
   362	
   363	                    if position <= 0.25:
   364	                        score += 10
   365	                        logger.debug(f"Price in lower 25% of range: {position:.2%}")
   366	        except Exception as e:
   367	            logger.warning(f"Error in price range analysis: {e}")
   368	
   369	    # Normalize to 0-100
   370	    score = min(max(score, 0.0), 100.0)
   371	
   372	    logger.debug(f"Support score: {score:.1f}")
   373	    return round(score, 2)
   374	
   375	
   376	def screen_candidates(
   377	    db: StockDatabase,
   378	    tickers_list: List[str],
   379	    value_weight: float = 0.7,
   380	    support_weight: float = 0.3,
   381	    min_data_days: int = 200
   382	) -> pd.DataFrame:
   383	    """Screen stocks and rank by combined value and technical scores.
   384	
   385	    This is the main screening function that combines fundamental value analysis
   386	    with technical support analysis to identify high-probability buying opportunities.
   387	
   388	    Args:
   389	        db: StockDatabase instance for data retrieval.
   390	        tickers_list: List of stock ticker symbols to screen.
   391	        value_weight: Weight for value score in final ranking (default: 0.7).
   392	        support_weight: Weight for support score in final ranking (default: 0.3).
   393	        min_data_days: Minimum days of price data required (default: 200).
   394	
   395	    Returns:
   396	        DataFrame with columns: ticker, name, sector, current_price,
   397	        value_score, support_score, buy_signal, rsi, nearest_support.
   398	        Sorted by buy_signal descending (best opportunities first).
   399	        Returns empty DataFrame if no valid candidates found.
   400	
   401	    Example:
   402	        >>> from src.data.storage import StockDatabase
   403	        >>> db = StockDatabase()
   404	        >>> results = screen_candidates(db, ["AAPL", "MSFT", "GOOGL"])
   405	        >>> print(results.head())
   406	        >>> print(f"Top candidate: {results.iloc[0]['ticker']}")
   407	    """
   408	    if not tickers_list:
   409	        logger.warning("Empty ticker list provided")
   410	        return pd.DataFrame()
   411	
   412	    if value_weight + support_weight != 1.0:
   413	        logger.warning(f"Weights don't sum to 1.0: {value_weight} + {support_weight}")
   414	        # Normalize weights
   415	        total = value_weight + support_weight
   416	        value_weight /= total
   417	        support_weight /= total
   418	
   419	    logger.info(f"Screening {len(tickers_list)} candidates...")
   420	
   421	    results = []
   422	
   423	    for ticker in tickers_list:
   424	        try:
   425	            logger.debug(f"Processing {ticker}...")
   426	
   427	            # Get fundamental data
   428	            fundamentals = db.get_latest_fundamentals(ticker)
   429	            if not fundamentals:
   430	                logger.warning(f"No fundamentals found for {ticker}")
   431	                continue
   432	
   433	            # Get price history
   434	            from datetime import datetime, timedelta
   435	            end_date = datetime.now()
   436	            start_date = end_date - timedelta(days=min_data_days + 100)  # Extra buffer
   437	
   438	            price_history = db.get_price_history(
   439	                ticker,
   440	                start_date.strftime('%Y-%m-%d'),
   441	                end_date.strftime('%Y-%m-%d')
   442	            )
   443	
   444	            if price_history.empty or len(price_history) < min_data_days:
   445	                logger.warning(
   446	                    f"Insufficient price data for {ticker}: {len(price_history)} days"
   447	                )
   448	                continue
   449	
   450	            # Calculate value score
   451	            value_score = calculate_value_score(fundamentals)
   452	
   453	            # Detect support levels
   454	            support_levels = detect_support_levels(price_history)
   455	
   456	            # Calculate technical indicators
   457	            current_price = fundamentals.get('current_price')
   458	            if current_price is None or current_price <= 0:
   459	                logger.warning(f"Invalid current price for {ticker}")
   460	                continue
   461	
   462	            # Calculate RSI
   463	            rsi = None
   464	            if len(price_history) >= 15:
   465	                rsi_series = calculate_rsi(price_history['Close'], period=14)
   466	                if not rsi_series.isna().all():
   467	                    rsi = float(rsi_series.iloc[-1])
   468	
   469	            # Detect volume spike
   470	            volume_spike = False
   471	            if 'Volume' in price_history.columns and len(price_history) >= 20:
   472	                current_volume = price_history['Volume'].iloc[-1]
   473	                volume_spike = detect_volume_spike(
   474	                    price_history['Volume'],
   475	                    current_volume,
   476	                    threshold=1.5
   477	                )
   478	
   479	            # Calculate support score
   480	            support_score = calculate_support_score(
   481	                current_price=current_price,
   482	                support_levels=support_levels,
   483	                rsi=rsi,
   484	                volume_spike=volume_spike,
   485	                price_history=price_history
   486	            )
   487	
   488	            # Calculate combined buy signal
   489	            buy_signal = (value_score * value_weight) + (support_score * support_weight)
   490	
   491	            # Find nearest support
   492	            nearest_support = None
   493	            if support_levels:
   494	                supports_below = [s for s in support_levels if s <= current_price]
   495	                if supports_below:
   496	                    nearest_support = max(supports_below)
   497	
   498	            # Compile results
   499	            results.append({
   500	                'ticker': ticker,
   501	                'name': fundamentals.get('name', ticker),
   502	                'sector': fundamentals.get('sector', 'Unknown'),
   503	                'current_price': current_price,
   504	                'value_score': value_score,
   505	                'support_score': support_score,
   506	                'buy_signal': round(buy_signal, 2),
   507	                'rsi': round(rsi, 2) if rsi is not None else None,
   508	                'nearest_support': round(nearest_support, 2) if nearest_support else None,
   509	                'pe_ratio': fundamentals.get('pe_ratio'),
   510	                'pb_ratio': fundamentals.get('pb_ratio'),
   511	                'data_points': len(price_history)
   512	            })
   513	
   514	            logger.info(
   515	                f"{ticker}: Buy Signal={buy_signal:.1f} "
   516	                f"(Value={value_score:.1f}, Support={support_score:.1f})"
   517	            )
   518	
   519	        except Exception as e:
   520	            logger.error(f"Error screening {ticker}: {e}")
   521	            continue
   522	
   523	    if not results:
   524	        logger.warning("No valid screening results")
   525	        return pd.DataFrame()
   526	
   527	    # Create DataFrame and sort by buy signal
   528	    df = pd.DataFrame(results)
   529	    df = df.sort_values('buy_signal', ascending=False).reset_index(drop=True)
   530	
   531	    logger.info(f"Successfully screened {len(df)} candidates")
   532	
   533	    return df

exec
/bin/zsh -lc "rg --files .github scripts -g '*.yml' -g '*.yaml' -g '*.sh' | sort | xargs -I{} sh -c 'echo FILE:{}; nl -ba \"{}\"'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
FILE:.github/workflows/daily_screening_git_storage.yml
     1	name: Daily Stock Screening (Git-Based Storage)
     2	
     3	on:
     4	  schedule:
     5	    # Run at 7am EST (12:00 UTC) on weekdays
     6	    - cron: '0 12 * * 1-5'
     7	
     8	  # Allow manual triggering
     9	  workflow_dispatch:
    10	    inputs:
    11	      force_full_refresh:
    12	        description: 'Force refresh all fundamentals (ignore cache)'
    13	        required: false
    14	        type: boolean
    15	        default: false
    16	
    17	jobs:
    18	  screen-stocks:
    19	    runs-on: ubuntu-latest
    20	
    21	    permissions:
    22	      contents: write  # Required to commit fundamental cache
    23	
    24	    steps:
    25	      - name: Checkout code
    26	        uses: actions/checkout@v4
    27	        with:
    28	          fetch-depth: 1  # Shallow clone for speed
    29	
    30	      - name: Get current date
    31	        id: date
    32	        run: |
    33	          echo "date=$(date +'%Y-%m-%d')" >> $GITHUB_OUTPUT
    34	          echo "time=$(date +'%H:%M:%S')" >> $GITHUB_OUTPUT
    35	
    36	      - name: Check existing fundamental cache
    37	        id: cache-check
    38	        run: |
    39	          if [ -d "data/fundamentals_cache" ]; then
    40	            CACHE_COUNT=$(ls data/fundamentals_cache/*_fundamentals.json 2>/dev/null | wc -l | tr -d ' ')
    41	            echo "✓ Found existing fundamental cache"
    42	            echo "cached_stocks=$CACHE_COUNT" >> $GITHUB_OUTPUT
    43	            echo "  Cached stocks: $CACHE_COUNT"
    44	
    45	            # Show cache age distribution
    46	            echo "  Cache age distribution:"
    47	            find data/fundamentals_cache -name "*_fundamentals.json" -mtime -7 -type f | wc -l | xargs echo "    <7 days:"
    48	            find data/fundamentals_cache -name "*_fundamentals.json" -mtime +7 -mtime -30 -type f | wc -l | xargs echo "    7-30 days:"
    49	            find data/fundamentals_cache -name "*_fundamentals.json" -mtime +30 -mtime -90 -type f | wc -l | xargs echo "    30-90 days:"
    50	            find data/fundamentals_cache -name "*_fundamentals.json" -mtime +90 -type f | wc -l | xargs echo "    >90 days (stale):"
    51	          else
    52	            echo "⚠ No existing cache, will create"
    53	            mkdir -p data/fundamentals_cache
    54	            echo "cached_stocks=0" >> $GITHUB_OUTPUT
    55	          fi
    56	
    57	      - name: Set up Python
    58	        uses: actions/setup-python@v5
    59	        with:
    60	          python-version: '3.11'
    61	          cache: 'pip'
    62	
    63	      - name: Install dependencies
    64	        run: |
    65	          python -m pip install --upgrade pip
    66	          pip install -r requirements.txt
    67	
    68	      - name: Run optimized stock screening
    69	        env:
    70	          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
    71	          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
    72	          EMAIL_TO: ${{ secrets.EMAIL_TO }}
    73	          EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER || 'smtp.gmail.com' }}
    74	          EMAIL_SMTP_PORT: ${{ secrets.EMAIL_SMTP_PORT || '587' }}
    75	          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    76	          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
    77	          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    78	          FORCE_FULL_REFRESH: ${{ github.event.inputs.force_full_refresh || 'false' }}
    79	          CACHED_STOCKS: ${{ steps.cache-check.outputs.cached_stocks }}
    80	        run: |
    81	          echo "Starting screening with:"
    82	          echo "  - Fresh price data for all stocks (1 year history)"
    83	          echo "  - Smart fundamental refresh (earnings-aware)"
    84	          echo "  - Cached fundamentals: $CACHED_STOCKS stocks"
    85	          echo ""
    86	
    87	          # Create output directories
    88	          mkdir -p data/daily_scans
    89	          mkdir -p data/logs
    90	
    91	          # Conservative mode to avoid rate limits
    92	          # --git-storage flag enables Git-based fundamental storage
    93	          # --enable-llm-agents runs Fundamentals Auditor + Catalyst Sentiment
    94	          # (Claude API calls) and the free Congress Trades lookup on the Top 20
    95	          # pool, then filters/ranks that pool down to a Top 5 shortlist in the
    96	          # email. Fundamentals Auditor/Catalyst Sentiment no-op with a logged
    97	          # warning if ANTHROPIC_API_KEY isn't set as a repo secret.
    98	          python run_optimized_scan.py --conservative --git-storage --enable-llm-agents
    99	
   100	      - name: Show fundamental refresh stats
   101	        if: always()
   102	        run: |
   103	          echo "=== Fundamental Cache Statistics ==="
   104	          if [ -f "data/fundamentals_cache/metadata.json" ]; then
   105	            echo "Latest updates:"
   106	            python3 << 'PYTHON_SCRIPT'
   107	          import json
   108	          from datetime import datetime
   109	
   110	          try:
   111	              with open("data/fundamentals_cache/metadata.json", "r") as f:
   112	                  metadata = json.load(f)
   113	
   114	              # Show last 10 updated stocks
   115	              updates = [(ticker, data["last_updated"]) for ticker, data in metadata.items()]
   116	              updates.sort(key=lambda x: x[1], reverse=True)
   117	
   118	              print(f"Total tracked: {len(updates)} stocks")
   119	              print("\nLast 10 updates:")
   120	              for ticker, timestamp in updates[:10]:
   121	                  dt = datetime.fromisoformat(timestamp)
   122	                  formatted = dt.strftime("%Y-%m-%d %H:%M")
   123	                  print(f"  {ticker}: {formatted}")
   124	          except Exception as e:
   125	              print(f"Could not read metadata: {e}")
   126	          PYTHON_SCRIPT
   127	          else
   128	            echo "No metadata file found"
   129	          fi
   130	
   131	      - name: Commit updated fundamental cache
   132	        id: commit
   133	        run: |
   134	          git config --local user.email "github-actions[bot]@users.noreply.github.com"
   135	          git config --local user.name "github-actions[bot]"
   136	
   137	          # Add fundamental cache directory, plus the LLM agents' logged output
   138	          # (data/fundamentals_audit/, data/catalyst_sentiment/, data/congress_trades/)
   139	          # — these need to persist past this ephemeral runner so they can accumulate
   140	          # into a real point-in-time history for the walk-forward backtest to eventually use.
   141	          git add data/fundamentals_cache/
   142	          git add data/fundamentals_audit/ 2>/dev/null || true
   143	          git add data/catalyst_sentiment/ 2>/dev/null || true
   144	          git add data/congress_trades/ 2>/dev/null || true
   145	
   146	          # Also commit the day's Top 20 pool + Top 5 shortlist (top20_latest.json,
   147	          # shortlist_latest.json) and scan report — this is what actually reaches
   148	          # the local GUI dashboard (dashboard.py) after a `git pull`, so the same
   149	          # picks that went out by email are also visible there.
   150	          git add data/daily_scans/ 2>/dev/null || true
   151	
   152	          # Check if there are changes
   153	          if git diff --staged --quiet; then
   154	            echo "No fundamental cache changes to commit"
   155	            echo "has_changes=false" >> $GITHUB_OUTPUT
   156	          else
   157	            CHANGED_FILES=$(git diff --staged --name-only | wc -l)
   158	            echo "Committing $CHANGED_FILES updated fundamental files"
   159	            git commit -m "chore: update fundamental cache ($CHANGED_FILES stocks) - ${{ steps.date.outputs.date }}"
   160	            echo "has_changes=true" >> $GITHUB_OUTPUT
   161	          fi
   162	
   163	      - name: Push changes
   164	        if: steps.commit.outputs.has_changes == 'true'
   165	        uses: ad-m/github-push-action@v0.8.0
   166	        with:
   167	          github_token: ${{ secrets.GITHUB_TOKEN }}
   168	          branch: ${{ github.ref }}
   169	
   170	      - name: Upload screening results
   171	        if: always()
   172	        uses: actions/upload-artifact@v4
   173	        with:
   174	          name: screening-results-${{ steps.date.outputs.date }}
   175	          path: |
   176	            data/daily_scans/
   177	            data/logs/
   178	          if-no-files-found: warn  # Don't fail if no files found
   179	          retention-days: 90  # Keep screening results for 90 days
   180	
   181	      - name: Cache size report
   182	        if: always()
   183	        run: |
   184	          echo "=== Git Repository Impact ==="
   185	          if [ -d "data/fundamentals_cache" ]; then
   186	            CACHE_SIZE=$(du -sh data/fundamentals_cache | cut -f1)
   187	            CACHE_FILES=$(find data/fundamentals_cache -name "*.json" | wc -l | tr -d ' ')
   188	
   189	            echo "Fundamental cache directory size: $CACHE_SIZE"
   190	            echo "Total files: $CACHE_FILES"
   191	            echo ""
   192	            echo "Today's commit impact:"
   193	            if [ "${{ steps.commit.outputs.has_changes }}" == "true" ]; then
   194	              git show --stat | tail -5
   195	            else
   196	              echo "  No changes committed"
   197	            fi
   198	          fi
FILE:.github/workflows/midday_quick_scan.yml
     1	name: Midday Quick Scan
     2	
     3	on:
     4	  schedule:
     5	    # ~12pm ET on weekdays (17:00 UTC). Uses the same fixed EST-based UTC
     6	    # offset as the 7am daily scan, so both jobs drift together (~1hr late)
     7	    # during EDT months rather than independently.
     8	    - cron: '0 17 * * 1-5'
     9	
    10	  workflow_dispatch: {}
    11	
    12	jobs:
    13	  quick-scan:
    14	    runs-on: ubuntu-latest
    15	
    16	    permissions:
    17	      contents: write  # Required to commit fundamental cache
    18	
    19	    steps:
    20	      - name: Checkout code
    21	        uses: actions/checkout@v4
    22	        with:
    23	          fetch-depth: 1
    24	
    25	      - name: Set up Python
    26	        uses: actions/setup-python@v5
    27	        with:
    28	          python-version: '3.11'
    29	          cache: 'pip'
    30	
    31	      - name: Install dependencies
    32	        run: |
    33	          python -m pip install --upgrade pip
    34	          pip install -r requirements.txt
    35	
    36	      - name: Run quick test scan (100 stocks)
    37	        env:
    38	          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
    39	          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
    40	          EMAIL_TO: ${{ secrets.EMAIL_TO }}
    41	          EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER || 'smtp.gmail.com' }}
    42	          EMAIL_SMTP_PORT: ${{ secrets.EMAIL_SMTP_PORT || '587' }}
    43	          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    44	          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
    45	        run: |
    46	          mkdir -p data/daily_scans
    47	          mkdir -p data/logs
    48	          python run_optimized_scan.py --test-mode --git-storage
    49	
    50	      - name: Commit updated fundamental cache
    51	        id: commit
    52	        run: |
    53	          git config --local user.email "github-actions[bot]@users.noreply.github.com"
    54	          git config --local user.name "github-actions[bot]"
    55	
    56	          git add data/fundamentals_cache/
    57	          # Also commit the day's Top 20 pool + scan report so the local GUI
    58	          # dashboard (dashboard.py) can show it after a `git pull`.
    59	          git add data/daily_scans/ 2>/dev/null || true
    60	
    61	          if git diff --staged --quiet; then
    62	            echo "No fundamental cache changes to commit"
    63	            echo "has_changes=false" >> $GITHUB_OUTPUT
    64	          else
    65	            CHANGED_FILES=$(git diff --staged --name-only | wc -l)
    66	            git commit -m "chore: midday quick scan cache update ($CHANGED_FILES stocks) - $(date +'%Y-%m-%d %H:%M')"
    67	            echo "has_changes=true" >> $GITHUB_OUTPUT
    68	          fi
    69	
    70	      - name: Push changes
    71	        if: steps.commit.outputs.has_changes == 'true'
    72	        uses: ad-m/github-push-action@v0.8.0
    73	        with:
    74	          github_token: ${{ secrets.GITHUB_TOKEN }}
    75	          branch: ${{ github.ref }}
    76	
    77	      - name: Upload scan results
    78	        if: always()
    79	        uses: actions/upload-artifact@v4
    80	        with:
    81	          name: midday-quick-scan-${{ github.run_id }}
    82	          path: |
    83	            data/daily_scans/
    84	            data/logs/
    85	          if-no-files-found: warn
    86	          retention-days: 30
FILE:scripts/check_throttling.sh
     1	#!/bin/bash
     2	# Quick throttling detection script
     3	
     4	LOG_FILE="./data/logs/optimized_scan_$(date +%Y%m%d).log"
     5	
     6	if [ ! -f "$LOG_FILE" ]; then
     7	    echo "❌ No log file found for today"
     8	    echo "   Expected: $LOG_FILE"
     9	    exit 0
    10	fi
    11	
    12	echo ""
    13	echo "🔍 THROTTLING DETECTION REPORT"
    14	echo "================================"
    15	echo ""
    16	
    17	# Count different error types
    18	ERROR_429=$(grep -c "429\|Too Many Requests" "$LOG_FILE" 2>/dev/null || echo "0")
    19	TIMEOUTS=$(grep -c -i "timeout\|timed out" "$LOG_FILE" 2>/dev/null || echo "0")
    20	FAILED=$(grep -c "Failed to fetch" "$LOG_FILE" 2>/dev/null || echo "0")
    21	EMPTY_DATA=$(grep -c "Insufficient data (0 days)" "$LOG_FILE" 2>/dev/null || echo "0")
    22	
    23	echo "Error Breakdown:"
    24	echo "  429 'Too Many Requests': $ERROR_429"
    25	echo "  Timeouts: $TIMEOUTS"
    26	echo "  Failed Fetches: $FAILED"
    27	echo "  Empty Data Responses: $EMPTY_DATA"
    28	echo ""
    29	
    30	TOTAL_ERRORS=$((ERROR_429 + TIMEOUTS + FAILED))
    31	
    32	echo "Total Error Events: $TOTAL_ERRORS"
    33	echo ""
    34	
    35	# Determine status
    36	if [ $ERROR_429 -gt 50 ] || [ $TOTAL_ERRORS -gt 150 ]; then
    37	    echo "🚨 STATUS: BEING THROTTLED!"
    38	    echo ""
    39	    echo "   Yahoo is rate limiting your requests."
    40	    echo ""
    41	    echo "   WHAT TO DO:"
    42	    echo "   1. Stop the current scan (Ctrl+C if running)"
    43	    echo "   2. Wait 10 minutes: sleep 600"
    44	    echo "   3. Resume with: python run_optimized_scan.py --conservative --resume"
    45	    echo ""
    46	elif [ $ERROR_429 -gt 20 ] || [ $TOTAL_ERRORS -gt 75 ]; then
    47	    echo "⚠️  STATUS: APPROACHING LIMIT"
    48	    echo ""
    49	    echo "   You're getting close to Yahoo's rate limit."
    50	    echo ""
    51	    echo "   WHAT TO DO:"
    52	    echo "   1. If scan is running, let it finish"
    53	    echo "   2. Next run, use: python run_optimized_scan.py --conservative"
    54	    echo "   3. Monitor error rate closely"
    55	    echo ""
    56	elif [ $TOTAL_ERRORS -gt 20 ]; then
    57	    echo "ℹ️  STATUS: MINOR ERRORS (Normal)"
    58	    echo ""
    59	    echo "   Some errors are normal. Error rate appears acceptable."
    60	    echo ""
    61	    echo "   You're fine to continue."
    62	    echo ""
    63	else
    64	    echo "✅ STATUS: ALL GOOD!"
    65	    echo ""
    66	    echo "   Very low error rate. No throttling detected."
    67	    echo ""
    68	    echo "   You can safely continue or increase speed if desired."
    69	    echo ""
    70	fi
    71	
    72	# Check for progress file to show error rate
    73	PROGRESS_FILE="./data/batch_results/batch_progress.pkl"
    74	if [ -f "$PROGRESS_FILE" ]; then
    75	    echo "Recent Scan Statistics:"
    76	    python3 -c "
    77	import pickle
    78	try:
    79	    with open('$PROGRESS_FILE', 'rb') as f:
    80	        data = pickle.load(f)
    81	    error_rate = data.get('error_rate', 0) * 100
    82	    processed = len(data.get('processed', []))
    83	    total = data.get('total_tickers', 0)
    84	
    85	    print(f'  Processed: {processed:,}/{total:,} stocks')
    86	    print(f'  Error Rate: {error_rate:.2f}%')
    87	
    88	    if error_rate > 5:
    89	        print('  ⚠️  High error rate!')
    90	    elif error_rate > 2:
    91	        print('  ℹ️  Moderate error rate')
    92	    else:
    93	        print('  ✅ Low error rate')
    94	except Exception as e:
    95	    print(f'  Could not read progress file: {e}')
    96	" 2>/dev/null
    97	fi
    98	
    99	echo ""
   100	echo "================================"
   101	echo ""
FILE:scripts/daily_scanner.sh
     1	#!/bin/bash
     2	# Daily market scanner - runs full scan of all US stocks
     3	# Designed to run at 6:30 AM EST daily via cron
     4	
     5	# Configuration
     6	SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
     7	LOG_DIR="$SCRIPT_DIR/data/logs"
     8	LOG_FILE="$LOG_DIR/daily_scan_$(date +%Y%m%d).log"
     9	
    10	# Create log directory
    11	mkdir -p "$LOG_DIR"
    12	
    13	# Log start
    14	echo "========================================" | tee -a "$LOG_FILE"
    15	echo "Daily Market Scan Started" | tee -a "$LOG_FILE"
    16	echo "Time: $(date '+%Y-%m-%d %H:%M:%S %Z')" | tee -a "$LOG_FILE"
    17	echo "========================================" | tee -a "$LOG_FILE"
    18	
    19	# Change to script directory
    20	cd "$SCRIPT_DIR"
    21	
    22	# Activate virtual environment
    23	source venv/bin/activate
    24	
    25	# Run the scan with resume capability (in case of previous interruption)
    26	python run_full_market_scan.py --resume 2>&1 | tee -a "$LOG_FILE"
    27	
    28	# Log completion
    29	echo "========================================" | tee -a "$LOG_FILE"
    30	echo "Daily Market Scan Completed" | tee -a "$LOG_FILE"
    31	echo "Time: $(date '+%Y-%m-%d %H:%M:%S %Z')" | tee -a "$LOG_FILE"
    32	echo "========================================" | tee -a "$LOG_FILE"
    33	
    34	# Keep only last 30 days of logs
    35	find "$LOG_DIR" -name "daily_scan_*.log" -mtime +30 -delete
    36	
    37	# Deactivate virtual environment
    38	deactivate

exec
/bin/zsh -lc "nl -ba src/screening/phase_indicators.py | sed -n '250,480p'; nl -ba scripts/component_correlation_analysis.py; nl -ba scripts/compare_old_vs_new_weights.py; nl -ba scripts/backtest_critic.py" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
   250	        sma: SMA value
   251	
   252	    Returns:
   253	        Percentage distance
   254	    """
   255	    if sma == 0:
   256	        return 0.0
   257	
   258	    return ((price - sma) / sma) * 100
   259	
   260	
   261	def classify_phase(price_data: pd.DataFrame, current_price: float) -> Dict[str, any]:
   262	    """Classify current market phase (1-4) based on price action rules.
   263	
   264	    Phase 1: Base Building / Compression
   265	    - 50 SMA flat or turning up slightly
   266	    - 200 SMA flat
   267	    - Price trading tightly
   268	    - Volatility contracting
   269	    - Volume below average
   270	
   271	    Phase 2: Uptrend / Breakout
   272	    - Price > 50 SMA
   273	    - 50 SMA > 200 SMA
   274	    - Both SMAs sloping upward
   275	    - Breakout above resistance
   276	    - Volume expansion
   277	
   278	    Phase 3: Distribution / Top
   279	    - Price extended above 50 SMA
   280	    - Momentum weakening
   281	    - Flattening of 50 SMA
   282	
   283	    Phase 4: Downtrend
   284	    - Price < 50 and 200 SMA
   285	    - 50 SMA < 200 SMA
   286	    - Both slopes downward
   287	
   288	    Args:
   289	        price_data: DataFrame with OHLCV data
   290	        current_price: Current stock price
   291	
   292	    Returns:
   293	        Dict with phase info
   294	    """
   295	    if len(price_data) < 200:
   296	        return {
   297	            'phase': 0,
   298	            'phase_name': 'Insufficient Data',
   299	            'confidence': 0.0,
   300	            'reasons': ['Need at least 200 days of data']
   301	        }
   302	
   303	    close = price_data['Close']
   304	    high = price_data['High']
   305	    low = price_data['Low']
   306	    volume = price_data.get('Volume', pd.Series([]))
   307	
   308	    # Calculate SMAs (50, 150, 200 for Minervini Trend Template)
   309	    sma_50 = calculate_sma(close, 50)
   310	    sma_150 = calculate_sma(close, 150)
   311	    sma_200 = calculate_sma(close, 200)
   312	
   313	    if sma_50.isna().all() or sma_200.isna().all():
   314	        return {
   315	            'phase': 0,
   316	            'phase_name': 'Insufficient Data',
   317	            'confidence': 0.0,
   318	            'reasons': ['Cannot calculate SMAs']
   319	        }
   320	
   321	    sma_50_val = sma_50.iloc[-1]
   322	    sma_150_val = sma_150.iloc[-1] if not sma_150.isna().all() else 0
   323	    sma_200_val = sma_200.iloc[-1]
   324	
   325	    # Calculate 52-week high/low for Minervini criteria
   326	    if len(close) >= 252:  # ~1 year of trading days
   327	        week_52_high = high.iloc[-252:].max()
   328	        week_52_low = low.iloc[-252:].min()
   329	    else:
   330	        week_52_high = high.max()
   331	        week_52_low = low.min()
   332	
   333	    # Calculate slopes
   334	    slope_50 = calculate_slope(sma_50, 20)
   335	    slope_200 = calculate_slope(sma_200, 20)
   336	
   337	    # Volatility analysis
   338	    vol_data = detect_volatility_contraction(close, 20)
   339	
   340	    # Volume analysis
   341	    if len(volume) > 20:
   342	        avg_volume = volume.iloc[-20:].mean()
   343	        current_volume = volume.iloc[-1]
   344	        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
   345	    else:
   346	        volume_ratio = 1.0
   347	
   348	    reasons = []
   349	    confidence = 0.0
   350	
   351	    # Phase 4: Downtrend (check first)
   352	    if (current_price < sma_50_val and
   353	        current_price < sma_200_val and
   354	        sma_50_val < sma_200_val):
   355	
   356	        phase = 4
   357	        phase_name = 'Downtrend'
   358	        reasons.append(f'Price ({current_price:.2f}) below both 50 SMA ({sma_50_val:.2f}) and 200 SMA ({sma_200_val:.2f})')
   359	        reasons.append(f'50 SMA below 200 SMA (Death Cross)')
   360	        confidence = 70
   361	
   362	        if slope_50 < 0 and slope_200 < 0:
   363	            reasons.append('Both SMAs declining')
   364	            confidence += 20
   365	
   366	        if slope_50 < 0:
   367	            confidence += 10
   368	
   369	    # Phase 2: Uptrend / Breakout
   370	    elif (current_price > sma_50_val and
   371	          sma_50_val > sma_200_val and
   372	          slope_50 > 0):
   373	
   374	        phase = 2
   375	        phase_name = 'Uptrend/Breakout'
   376	        reasons.append(f'Price ({current_price:.2f}) above 50 SMA ({sma_50_val:.2f})')
   377	        reasons.append(f'50 SMA above 200 SMA (Golden Cross)')
   378	        reasons.append(f'50 SMA rising (slope: {slope_50:.3f}%)')
   379	        confidence = 70
   380	
   381	        if slope_200 > 0:
   382	            reasons.append(f'200 SMA also rising (slope: {slope_200:.3f}%)')
   383	            confidence += 15
   384	
   385	        if volume_ratio > 1.2:
   386	            reasons.append(f'Volume expansion ({volume_ratio:.1f}x average)')
   387	            confidence += 15
   388	
   389	    # Phase 3: Distribution / Top
   390	    elif (current_price > sma_50_val and
   391	          calculate_distance_from_sma(current_price, sma_50_val) > 25):
   392	
   393	        phase = 3
   394	        phase_name = 'Distribution/Top'
   395	        distance = calculate_distance_from_sma(current_price, sma_50_val)
   396	        reasons.append(f'Price extended {distance:.1f}% above 50 SMA')
   397	        confidence = 60
   398	
   399	        if slope_50 < 0.05:  # Flattening
   400	            reasons.append('50 SMA flattening')
   401	            confidence += 20
   402	
   403	        if abs(slope_50) < abs(slope_200) * 0.5:
   404	            reasons.append('Momentum weakening')
   405	            confidence += 20
   406	
   407	    # Phase 1: Base Building
   408	    else:
   409	        phase = 1
   410	        phase_name = 'Base Building'
   411	        reasons.append('Price in consolidation pattern')
   412	        confidence = 50
   413	
   414	        if abs(slope_50) < 0.1:
   415	            reasons.append(f'50 SMA flat (slope: {slope_50:.3f}%)')
   416	            confidence += 15
   417	
   418	        if abs(slope_200) < 0.05:
   419	            reasons.append(f'200 SMA flat (slope: {slope_200:.3f}%)')
   420	            confidence += 10
   421	
   422	        if vol_data['is_contracting']:
   423	            reasons.append(f'Volatility contracting ({vol_data["contraction_quality"]:.0f}% quality)')
   424	            confidence += 15
   425	
   426	        if volume_ratio < 1.0:
   427	            reasons.append(f'Volume below average ({volume_ratio:.1f}x)')
   428	            confidence += 10
   429	
   430	    return {
   431	        'phase': phase,
   432	        'phase_name': phase_name,
   433	        'confidence': min(confidence, 100),
   434	        'reasons': reasons,
   435	        'sma_50': round(sma_50_val, 2),
   436	        'sma_150': round(sma_150_val, 2),
   437	        'sma_200': round(sma_200_val, 2),
   438	        'slope_50': round(slope_50, 4),
   439	        'slope_200': round(slope_200, 4),
   440	        'distance_from_50sma': round(calculate_distance_from_sma(current_price, sma_50_val), 2),
   441	        'distance_from_200sma': round(calculate_distance_from_sma(current_price, sma_200_val), 2),
   442	        'week_52_high': round(week_52_high, 2),
   443	        'week_52_low': round(week_52_low, 2),
   444	        'volatility_contraction': vol_data
   445	    }
   446	
   447	
   448	def validate_minervini_trend_template(
   449	    current_price: float,
   450	    phase_info: Dict,
   451	    sma_200_series: pd.Series
   452	) -> Dict[str, any]:
   453	    """Validate Minervini Trend Template (SEPA - Specific Entry Point Analysis).
   454	
   455	    Based on Mark Minervini's methodology from "Trade Like a Stock Market Wizard"
   456	    and "Think & Trade Like a Champion".
   457	
   458	    The Trend Template identifies stocks in confirmed Stage 2 uptrends with:
   459	    1. Price > 150 SMA AND 200 SMA
   460	    2. 150 SMA > 200 SMA
   461	    3. 200 SMA trending up for at least 1 month (preferably 4-5 months)
   462	    4. 50 SMA > 150 SMA > 200 SMA (strongest configuration)
   463	    5. Price > 50 SMA
   464	    6. Price at least 30% above 52-week low
   465	    7. Price within 25% of 52-week high (the closer the better)
   466	    8. RS Rating 70+ (IBD-style, we use RS slope as proxy)
   467	
   468	    Args:
   469	        current_price: Current stock price
   470	        phase_info: Phase classification dict (must include sma_50, sma_150, sma_200, etc.)
   471	        sma_200_series: Full 200 SMA series for slope calculation
   472	
   473	    Returns:
   474	        Dict with:
   475	        - passes_template: bool
   476	        - criteria_passed: int (0-8)
   477	        - criteria_details: Dict of each criterion
   478	        - template_score: int (0-100)
   479	    """
   480	    sma_50 = phase_info.get('sma_50', 0)
     1	#!/usr/bin/env python3
     2	"""Which of the 7 scoring components actually predicts forward returns?
     3	
     4	score_buy_signal() blends 7 sub-scores into one 0-125 total: trend_score (40),
     5	fundamental_score (40), rr_score (15), rs_score (10), volume_score (10),
     6	entry_score (5), vcp_bonus (5). We already know the blended total barely
     7	correlates with returns (r ~ -0.1 to +0.12) — this checks each ingredient
     8	separately to find out which ones (if any) actually carry signal, and which
     9	are just diluting the ones that do.
    10	
    11	Tests ALL Minervini-qualified Phase 2 stocks (not just is_buy>=60), point-in-time
    12	correct (no look-ahead), so we have more data points than restricting to the
    13	final recommended pool.
    14	
    15	Usage:
    16	    python scripts/component_correlation_analysis.py --pool 400 --days 30
    17	"""
    18	
    19	import argparse
    20	import logging
    21	import random
    22	import sys
    23	from datetime import datetime, timedelta
    24	from pathlib import Path
    25	
    26	import pandas as pd
    27	import yfinance as yf
    28	
    29	sys.path.insert(0, str(Path(__file__).parent.parent))
    30	
    31	from src.data.universe_fetcher import USStockUniverseFetcher
    32	from src.screening.phase_indicators import classify_phase, calculate_relative_strength
    33	from src.screening.signal_engine import score_buy_signal
    34	
    35	logging.basicConfig(level=logging.WARNING)
    36	logger = logging.getLogger(__name__)
    37	
    38	COMPONENTS = ['trend_score', 'fundamental_score', 'rr_score', 'rs_score', 'volume_score', 'entry_score', 'vcp_bonus']
    39	
    40	
    41	def pearson(xs, ys):
    42	    n = len(xs)
    43	    if n < 5:
    44	        return None
    45	    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    46	    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    47	    std_x = (sum((x - mean_x) ** 2 for x in xs)) ** 0.5
    48	    std_y = (sum((y - mean_y) ** 2 for y in ys)) ** 0.5
    49	    if std_x == 0 or std_y == 0:
    50	        return None
    51	    return cov / (std_x * std_y)
    52	
    53	
    54	def main():
    55	    parser = argparse.ArgumentParser()
    56	    parser.add_argument('--days', type=int, default=30, help='How far back the as-of (entry) date is')
    57	    parser.add_argument('--forward-days', type=int, default=None,
    58	                         help='Forward window length; default measures to today. Set explicitly '
    59	                              'to test a fixed historical window not overlapping "today".')
    60	    parser.add_argument('--pool', type=int, default=400)
    61	    args = parser.parse_args()
    62	
    63	    as_of = (datetime.now() - timedelta(days=args.days)).date()
    64	    forward_to = (datetime.now() - timedelta(days=args.days - args.forward_days)).date() if args.forward_days else None
    65	    window_desc = f"{as_of} -> {forward_to}" if forward_to else f"{as_of} -> today"
    66	    print(f"Scoring a pool of {args.pool} tickers, entry {window_desc}...\n")
    67	
    68	    universe = USStockUniverseFetcher().fetch_universe()
    69	    pool_tickers = random.sample(universe, min(args.pool, len(universe)))
    70	
    71	    spy = yf.Ticker('SPY').history(period='2y')
    72	    spy.index = spy.index.tz_localize(None)
    73	    spy_asof = spy.loc[:pd.Timestamp(as_of)]
    74	
    75	    rows = []
    76	    for i, ticker in enumerate(pool_tickers):
    77	        try:
    78	            hist = yf.Ticker(ticker).history(period='2y')
    79	            if hist.empty:
    80	                continue
    81	            hist.index = hist.index.tz_localize(None)
    82	            asof_data = hist.loc[:pd.Timestamp(as_of)]
    83	            if len(asof_data) < 200:
    84	                continue
    85	
    86	            current_price = asof_data['Close'].iloc[-1]
    87	            phase_info = classify_phase(asof_data, current_price)
    88	            if phase_info['phase'] != 2:
    89	                continue
    90	
    91	            rs_series = calculate_relative_strength(asof_data['Close'], spy_asof['Close'], period=63)
    92	            signal = score_buy_signal(
    93	                ticker=ticker, price_data=asof_data, current_price=current_price,
    94	                phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
    95	            )
    96	
    97	            # Only stocks that passed the Minervini gate have populated component details
    98	            if not signal['details'] or 'trend_score' not in signal['details']:
    99	                continue
   100	
   101	            if forward_to:
   102	                fwd_data = hist.loc[:pd.Timestamp(forward_to)]
   103	                if fwd_data.empty:
   104	                    continue
   105	                exit_price = fwd_data['Close'].iloc[-1]
   106	            else:
   107	                exit_price = hist['Close'].iloc[-1]
   108	            return_pct = (exit_price - current_price) / current_price * 100
   109	
   110	            row = {'ticker': ticker, 'score': signal['score'], 'is_buy': signal['is_buy'], 'return_pct': return_pct}
   111	            for comp in COMPONENTS:
   112	                row[comp] = signal['details'].get(comp, 0) or 0
   113	            rows.append(row)
   114	
   115	        except Exception as e:
   116	            logger.debug(f"{ticker}: {e}")
   117	            continue
   118	
   119	        if (i + 1) % 100 == 0:
   120	            print(f"  ...{i + 1}/{len(pool_tickers)} processed, {len(rows)} qualified so far")
   121	
   122	    print(f"\n{len(rows)} Minervini-qualified Phase 2 stocks collected.\n")
   123	
   124	    if len(rows) < 20:
   125	        print("Too few data points for meaningful correlation — try a bigger --pool.")
   126	        return
   127	
   128	    is_buy_rows = [r for r in rows if r['is_buy']]
   129	
   130	    print(f"{'='*78}")
   131	    print(f"{'Component':<22}{'Range':<12}{'r (all qualified)':<20}{'r (is_buy>=60 only)'}")
   132	    print(f"{'='*78}")
   133	
   134	    total_returns = [r['return_pct'] for r in rows]
   135	    total_scores = [r['score'] for r in rows]
   136	    r_total_all = pearson(total_scores, total_returns)
   137	
   138	    for comp in ['score'] + COMPONENTS:
   139	        vals_all = [r[comp] for r in rows]
   140	        r_all = pearson(vals_all, total_returns)
   141	
   142	        vals_buy = [r[comp] for r in is_buy_rows]
   143	        returns_buy = [r['return_pct'] for r in is_buy_rows]
   144	        r_buy = pearson(vals_buy, returns_buy) if len(is_buy_rows) >= 5 else None
   145	
   146	        label = 'TOTAL SCORE' if comp == 'score' else comp
   147	        r_all_str = f"{r_all:+.3f}" if r_all is not None else "n/a"
   148	        r_buy_str = f"{r_buy:+.3f}" if r_buy is not None else "n/a"
   149	        print(f"{label:<22}{'':<12}{r_all_str:<20}{r_buy_str}")
   150	
   151	    print(f"{'='*78}")
   152	    print(f"\nSample sizes: {len(rows)} all qualified, {len(is_buy_rows)} is_buy>=60")
   153	    print("r near 0 = no predictive power. |r| > 0.2 would be a genuinely usable signal at this sample size.")
   154	    print("Negative r means higher component score correlated with WORSE forward returns.")
   155	
   156	
   157	if __name__ == '__main__':
   158	    main()
     1	#!/usr/bin/env python3
     2	"""Controlled A/B: score the SAME pool of tickers with both the OLD and NEW component
     3	weights, so any difference in outcome is actually due to the reweight, not a different
     4	random draw of the market (which confounded the earlier before/after comparison).
     5	
     6	Reconstructs the old-weight total algebraically from the new-weight component values
     7	already in `details` (each component's scaling factor is invertible), rather than
     8	re-running score_buy_signal twice — one fetch/score pass, two totals compared.
     9	"""
    10	
    11	import argparse
    12	import logging
    13	import random
    14	import sys
    15	from datetime import datetime, timedelta
    16	from pathlib import Path
    17	
    18	import pandas as pd
    19	import yfinance as yf
    20	
    21	sys.path.insert(0, str(Path(__file__).parent.parent))
    22	
    23	from src.data.universe_fetcher import USStockUniverseFetcher
    24	from src.screening.phase_indicators import classify_phase, calculate_relative_strength
    25	from src.screening.signal_engine import score_buy_signal
    26	
    27	logging.basicConfig(level=logging.WARNING)
    28	logger = logging.getLogger(__name__)
    29	
    30	# Inverse of the scaling factors applied in signal_engine.py, to reconstruct old-weight
    31	# component values from the new-weight ones already stored in `details`.
    32	OLD_SCALE = {
    33	    'trend_score': 40 / 35,
    34	    'fundamental_score': 40 / 35,
    35	    'entry_score': 1 / 5,
    36	    'rr_score': 15 / 10,
    37	    'volume_score': 10 / 5,
    38	    'rs_score': 1.0,   # unchanged
    39	}
    40	
    41	
    42	def pearson(xs, ys):
    43	    n = len(xs)
    44	    if n < 5:
    45	        return None
    46	    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    47	    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    48	    std_x = (sum((x - mean_x) ** 2 for x in xs)) ** 0.5
    49	    std_y = (sum((y - mean_y) ** 2 for y in ys)) ** 0.5
    50	    return cov / (std_x * std_y) if std_x > 0 and std_y > 0 else None
    51	
    52	
    53	def main():
    54	    parser = argparse.ArgumentParser()
    55	    parser.add_argument('--days', type=int, default=7)
    56	    parser.add_argument('--pool', type=int, default=300)
    57	    parser.add_argument('--investment', type=float, default=1000.0)
    58	    args = parser.parse_args()
    59	
    60	    as_of = (datetime.now() - timedelta(days=args.days)).date()
    61	    print(f"Scoring ONE pool of {args.pool} tickers as of {as_of} with BOTH weight schemes...\n")
    62	
    63	    universe = USStockUniverseFetcher().fetch_universe()
    64	    pool_tickers = random.sample(universe, min(args.pool, len(universe)))
    65	
    66	    spy = yf.Ticker('SPY').history(period='2y')
    67	    spy.index = spy.index.tz_localize(None)
    68	    spy_asof = spy.loc[:pd.Timestamp(as_of)]
    69	
    70	    rows = []
    71	    for ticker in pool_tickers:
    72	        try:
    73	            hist = yf.Ticker(ticker).history(period='2y')
    74	            if hist.empty:
    75	                continue
    76	            hist.index = hist.index.tz_localize(None)
    77	            asof_data = hist.loc[:pd.Timestamp(as_of)]
    78	            if len(asof_data) < 200:
    79	                continue
    80	
    81	            current_price = asof_data['Close'].iloc[-1]
    82	            phase_info = classify_phase(asof_data, current_price)
    83	            if phase_info['phase'] != 2:
    84	                continue
    85	
    86	            rs_series = calculate_relative_strength(asof_data['Close'], spy_asof['Close'], period=63)
    87	            signal = score_buy_signal(
    88	                ticker=ticker, price_data=asof_data, current_price=current_price,
    89	                phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
    90	            )
    91	            d = signal['details']
    92	            if not d or 'trend_score' not in d:
    93	                continue
    94	
    95	            old_total = sum(d.get(k, 0) * OLD_SCALE[k] for k in OLD_SCALE) + (d.get('vcp_bonus', 0) or 0)
    96	            new_total = signal['score']
    97	
    98	            today_price = hist['Close'].iloc[-1]
    99	            return_pct = (today_price - current_price) / current_price * 100
   100	
   101	            rows.append({
   102	                'ticker': ticker, 'old_score': old_total, 'new_score': new_total,
   103	                'old_is_buy': old_total >= 60, 'new_is_buy': signal['is_buy'],
   104	                'return_pct': return_pct, 'entry_price': current_price, 'today_price': today_price,
   105	            })
   106	        except Exception as e:
   107	            logger.debug(f"{ticker}: {e}")
   108	            continue
   109	
   110	    print(f"{len(rows)} Minervini-qualified Phase 2 stocks scored under both schemes.\n")
   111	
   112	    old_qual = [r for r in rows if r['old_is_buy']]
   113	    new_qual = [r for r in rows if r['new_is_buy']]
   114	
   115	    r_old = pearson([r['old_score'] for r in old_qual], [r['return_pct'] for r in old_qual])
   116	    r_new = pearson([r['new_score'] for r in new_qual], [r['return_pct'] for r in new_qual])
   117	
   118	    print(f"{'='*70}")
   119	    print(f"OLD weights: {len(old_qual)} qualified, score-vs-return r = {r_old:+.3f}" if r_old is not None else "OLD: n/a")
   120	    print(f"NEW weights: {len(new_qual)} qualified, score-vs-return r = {r_new:+.3f}" if r_new is not None else "NEW: n/a")
   121	    print(f"{'='*70}\n")
   122	
   123	    def top3_result(qualified, score_key):
   124	        top3 = sorted(qualified, key=lambda r: r[score_key], reverse=True)[:3]
   125	        if not top3:
   126	            return None
   127	        per_stock = args.investment / len(top3)
   128	        value = sum((per_stock / r['entry_price']) * r['today_price'] for r in top3)
   129	        return top3, value, value - args.investment
   130	
   131	    old_result = top3_result(old_qual, 'old_score')
   132	    new_result = top3_result(new_qual, 'new_score')
   133	
   134	    if old_result:
   135	        tickers, value, profit = old_result
   136	        print(f"OLD top 3: {[t['ticker'] for t in tickers]}")
   137	        print(f"  ${args.investment:.0f} -> ${value:.2f} (${profit:+.2f}, {profit/args.investment*100:+.2f}%)")
   138	    if new_result:
   139	        tickers, value, profit = new_result
   140	        print(f"NEW top 3: {[t['ticker'] for t in tickers]}")
   141	        print(f"  ${args.investment:.0f} -> ${value:.2f} (${profit:+.2f}, {profit/args.investment*100:+.2f}%)")
   142	
   143	
   144	if __name__ == '__main__':
   145	    main()
     1	#!/usr/bin/env python3
     2	"""Backtest Critic — compares the two most recent walk-forward runs, flags any
     3	scoring component whose correlation with real returns is drifting, flipping sign,
     4	or has notably changed, and proposes a reweighting for manual review.
     5	
     6	NEVER modifies src/screening/signal_engine.py. Every proposal is written to
     7	data/backtest_critic_proposals/ for you to read and decide on — nothing here
     8	auto-applies a weight change.
     9	
    10	Usage:
    11	    python scripts/backtest_critic.py                  # compares the 2 most recent saved runs
    12	    python scripts/backtest_critic.py --baseline data/backtest_history/walk_forward_A.json \
    13	        --current data/backtest_history/walk_forward_B.json
    14	"""
    15	
    16	import argparse
    17	import json
    18	import sys
    19	from datetime import datetime
    20	from pathlib import Path
    21	
    22	HISTORY_DIR = Path(__file__).parent.parent / "data" / "backtest_history"
    23	PROPOSALS_DIR = Path(__file__).parent.parent / "data" / "backtest_critic_proposals"
    24	
    25	COMPONENTS = ['trend_score', 'fundamental_score', 'entry_score', 'rr_score', 'rs_score', 'volume_score']
    26	
    27	# Mirrors signal_engine.py's CURRENT weights — kept here for human-readable proposals.
    28	# Must be updated by hand if signal_engine.py's weights change; this script never
    29	# reads or writes signal_engine.py itself.
    30	CURRENT_WEIGHTS = {
    31	    'trend_score': 35, 'fundamental_score': 35, 'entry_score': 25,
    32	    'rr_score': 10, 'rs_score': 10, 'volume_score': 5,
    33	}
    34	
    35	DRIFT_THRESHOLD = 0.15       # |delta r| beyond this is flagged as notable drift
    36	SIGN_FLIP_MIN_MAGNITUDE = 0.05  # ignore trivial near-zero "flips" as noise
    37	PROPOSAL_MIN_CORRELATION = 0.25  # only propose reweighting components this strong
    38	
    39	
    40	def find_two_most_recent_runs():
    41	    files = sorted(HISTORY_DIR.glob("walk_forward_*.json"))
    42	    if len(files) < 2:
    43	        return None, None
    44	    return files[-2], files[-1]
    45	
    46	
    47	def load(path):
    48	    return json.loads(Path(path).read_text())
    49	
    50	
    51	def main():
    52	    parser = argparse.ArgumentParser()
    53	    parser.add_argument('--baseline', type=str, default=None)
    54	    parser.add_argument('--current', type=str, default=None)
    55	    args = parser.parse_args()
    56	
    57	    if args.baseline and args.current:
    58	        baseline_path, current_path = Path(args.baseline), Path(args.current)
    59	    else:
    60	        baseline_path, current_path = find_two_most_recent_runs()
    61	        if baseline_path is None:
    62	            print("Need at least 2 saved walk-forward runs in data/backtest_history/ to compare.")
    63	            print("Run scripts/walk_forward_backtest.py at least twice first (e.g. before/after a code change).")
    64	            sys.exit(1)
    65	
    66	    baseline = load(baseline_path)
    67	    current = load(current_path)
    68	
    69	    print(f"Comparing baseline: {baseline_path.name}  ({baseline.get('generated', '?')})")
    70	    print(f"           against: {current_path.name}  ({current.get('generated', '?')})")
    71	    print(f"Baseline trades: {baseline['summary'].get('total_trades', 0)} | "
    72	          f"Current trades: {current['summary'].get('total_trades', 0)}\n")
    73	
    74	    findings = []
    75	
    76	    print(f"{'='*78}")
    77	    print("COMPONENT DRIFT REPORT (correlation with realized return, entry -> exit)")
    78	    print(f"{'='*78}")
    79	    print(f"{'Component':<20}{'Baseline r':<14}{'Current r':<14}{'Delta':<10}{'Flag'}")
    80	
    81	    for comp in COMPONENTS:
    82	        r_base = baseline['component_correlations'].get(comp)
    83	        r_curr = current['component_correlations'].get(comp)
    84	
    85	        if r_base is None or r_curr is None:
    86	            print(f"{comp:<20}{'n/a':<14}{'n/a':<14}{'':<10}insufficient data in one run")
    87	            continue
    88	
    89	        delta = r_curr - r_base
    90	        flag = ""
    91	        if (r_base > SIGN_FLIP_MIN_MAGNITUDE and r_curr < -SIGN_FLIP_MIN_MAGNITUDE) or \
    92	           (r_base < -SIGN_FLIP_MIN_MAGNITUDE and r_curr > SIGN_FLIP_MIN_MAGNITUDE):
    93	            flag = "SIGN FLIP"
    94	            findings.append(f"{comp}: correlation flipped sign ({r_base:+.3f} -> {r_curr:+.3f}) — unreliable, treat cautiously")
    95	        elif abs(delta) >= DRIFT_THRESHOLD:
    96	            direction = "strengthened" if delta > 0 else "weakened"
    97	            flag = f"drift ({direction})"
    98	            findings.append(f"{comp}: correlation {direction} notably ({r_base:+.3f} -> {r_curr:+.3f}, delta {delta:+.3f})")
    99	
   100	        r_base_str, r_curr_str, delta_str = f"{r_base:+.3f}", f"{r_curr:+.3f}", f"{delta:+.3f}"
   101	        print(f"{comp:<20}{r_base_str:<14}{r_curr_str:<14}{delta_str:<10}{flag}")
   102	
   103	    print(f"\n{'='*78}")
   104	    print("SUMMARY STAT COMPARISON")
   105	    print(f"{'='*78}")
   106	    for key, label in [('win_rate_pct', 'Win rate %'), ('avg_return_pct', 'Avg return %'),
   107	                        ('sharpe_like', 'Sharpe-like'), ('max_drawdown_pct', 'Max drawdown %')]:
   108	        b, c = baseline['summary'].get(key), current['summary'].get(key)
   109	        if b is not None and c is not None:
   110	            print(f"{label:<20}{b:+.2f}  ->  {c:+.2f}   (delta {c - b:+.2f})")
   111	
   112	    print(f"\n{'='*78}")
   113	    print("FINDINGS")
   114	    print(f"{'='*78}")
   115	    if findings:
   116	        for f in findings:
   117	            print(f"  - {f}")
   118	    else:
   119	        print("  No notable drift or sign flips detected — components are behaving consistently.")
   120	
   121	    print(f"\n{'='*78}")
   122	    print("PROPOSED REWEIGHTING (NOT applied — src/screening/signal_engine.py is untouched)")
   123	    print(f"{'='*78}")
   124	    proposals = []
   125	    for comp in COMPONENTS:
   126	        r_curr = current['component_correlations'].get(comp)
   127	        r_base = baseline['component_correlations'].get(comp)
   128	        if r_curr is None:
   129	            continue
   130	        consistent_direction = r_base is None or (r_curr > 0) == (r_base > 0)
   131	        if abs(r_curr) >= PROPOSAL_MIN_CORRELATION and consistent_direction:
   132	            direction = "increasing" if r_curr > 0 else "decreasing"
   133	            proposals.append({'component': comp, 'current_r': r_curr, 'suggested_direction': direction,
   134	                               'current_weight': CURRENT_WEIGHTS.get(comp)})
   135	            print(f"  - {comp}: current r={r_curr:+.3f} (weight {CURRENT_WEIGHTS.get(comp, '?')} pts) "
   136	                  f"-> consider {direction} its weight")
   137	    if not proposals:
   138	        print(f"  No component currently meets the bar (|r| >= {PROPOSAL_MIN_CORRELATION}, "
   139	              f"consistent with baseline direction) for a reweight proposal.")
   140	
   141	    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
   142	    report_path = PROPOSALS_DIR / f"critic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
   143	    report_path.write_text(json.dumps({
   144	        'generated': datetime.now().isoformat(),
   145	        'baseline_run': baseline_path.name, 'current_run': current_path.name,
   146	        'findings': findings, 'proposals': proposals, 'current_weights': CURRENT_WEIGHTS,
   147	    }, indent=2))
   148	    print(f"\nFull report saved to {report_path}")
   149	    print("This is informational only — nothing was auto-applied to the live scoring formula.")
   150	
   151	
   152	if __name__ == '__main__':
   153	    main()

exec
/bin/zsh -lc "nl -ba src/data/quality.py | sed -n '1,621p'; nl -ba scripts/fetch_news.py; nl -ba scripts/fetch_price_history.py" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Data quality validation and monitoring for stock data.
     2	
     3	This module provides comprehensive data quality checks including:
     4	- Freshness validation (detecting stale data)
     5	- Completeness validation (missing fields, gaps in data)
     6	- Anomaly detection (unrealistic values, price spikes, volume anomalies)
     7	- Quality scoring and reporting
     8	"""
     9	
    10	import logging
    11	from datetime import datetime, timedelta
    12	from typing import Dict, List, Optional, Tuple, Any
    13	from dataclasses import dataclass, field
    14	from enum import Enum
    15	
    16	import pandas as pd
    17	from sqlalchemy import func
    18	
    19	from .storage import StockDatabase
    20	
    21	
    22	logger = logging.getLogger(__name__)
    23	
    24	
    25	class IssueSeverity(Enum):
    26	    """Severity levels for data quality issues."""
    27	    CRITICAL = "critical"  # Blocks screening (missing required data)
    28	    WARNING = "warning"    # May affect accuracy (stale data, minor anomalies)
    29	    INFO = "info"          # Informational (minor completeness issues)
    30	
    31	
    32	@dataclass
    33	class DataQualityIssue:
    34	    """Represents a single data quality issue."""
    35	    ticker: str
    36	    issue_type: str
    37	    severity: IssueSeverity
    38	    description: str
    39	    detected_at: datetime = field(default_factory=datetime.now)
    40	    metadata: Dict[str, Any] = field(default_factory=dict)
    41	
    42	    def __str__(self) -> str:
    43	        """String representation of the issue."""
    44	        return f"[{self.severity.value.upper()}] {self.ticker}: {self.description}"
    45	
    46	
    47	@dataclass
    48	class TickerQualityReport:
    49	    """Quality report for a single ticker."""
    50	    ticker: str
    51	    overall_score: float = 0.0  # 0-100
    52	    issues: List[DataQualityIssue] = field(default_factory=list)
    53	    last_fundamental_update: Optional[datetime] = None
    54	    last_price_update: Optional[datetime] = None
    55	    fundamental_completeness: float = 0.0  # 0-100
    56	    price_history_days: int = 0
    57	    has_critical_issues: bool = False
    58	    needs_refresh: bool = False
    59	
    60	    def add_issue(self, issue: DataQualityIssue) -> None:
    61	        """Add an issue to the report."""
    62	        self.issues.append(issue)
    63	        if issue.severity == IssueSeverity.CRITICAL:
    64	            self.has_critical_issues = True
    65	
    66	    def get_issues_by_severity(self, severity: IssueSeverity) -> List[DataQualityIssue]:
    67	        """Get all issues of a specific severity."""
    68	        return [issue for issue in self.issues if issue.severity == severity]
    69	
    70	
    71	class DataQualityChecker:
    72	    """Validates and monitors data quality for stock data."""
    73	
    74	    # Configuration constants
    75	    FUNDAMENTAL_STALE_DAYS = 7
    76	    PRICE_STALE_DAYS = 2
    77	    MIN_HISTORY_DAYS = 180
    78	    MAX_SINGLE_DAY_CHANGE = 0.20  # 20% price change threshold
    79	    VOLUME_SPIKE_MULTIPLIER = 5.0
    80	    MAX_REASONABLE_PE = 500
    81	    MAX_REASONABLE_PB = 100
    82	    MIN_REASONABLE_PRICE = 0.01
    83	
    84	    def __init__(self, db: StockDatabase):
    85	        """Initialize the data quality checker.
    86	
    87	        Args:
    88	            db: Database instance to check
    89	        """
    90	        self.db = db
    91	        logger.info("DataQualityChecker initialized")
    92	
    93	    def check_ticker(self, ticker: str) -> TickerQualityReport:
    94	        """Run comprehensive quality checks on a single ticker.
    95	
    96	        Args:
    97	            ticker: Stock ticker symbol
    98	
    99	        Returns:
   100	            TickerQualityReport with all issues and scores
   101	        """
   102	        logger.info(f"Running quality checks for {ticker}")
   103	        report = TickerQualityReport(ticker=ticker)
   104	
   105	        # Get latest data
   106	        fundamentals = self.db.get_latest_fundamentals(ticker)
   107	        if not fundamentals:
   108	            report.add_issue(DataQualityIssue(
   109	                ticker=ticker,
   110	                issue_type="missing_fundamentals",
   111	                severity=IssueSeverity.CRITICAL,
   112	                description="No fundamental data available"
   113	            ))
   114	            report.overall_score = 0.0
   115	            report.needs_refresh = True
   116	            return report
   117	
   118	        # Get price history
   119	        end_date = datetime.now()
   120	        start_date = end_date - timedelta(days=365)
   121	        price_history = self.db.get_price_history(
   122	            ticker,
   123	            start_date.strftime('%Y-%m-%d'),
   124	            end_date.strftime('%Y-%m-%d')
   125	        )
   126	
   127	        # Update report metadata
   128	        # 'date' is the fundamental data date from the fundamentals table
   129	        fund_date = fundamentals.get('date')
   130	        if fund_date:
   131	            if isinstance(fund_date, str):
   132	                report.last_fundamental_update = datetime.fromisoformat(fund_date)
   133	            else:
   134	                report.last_fundamental_update = fund_date
   135	
   136	        if not price_history.empty:
   137	            # Price history DataFrame uses 'Date' (capital D) column
   138	            date_col = 'Date' if 'Date' in price_history.columns else 'date'
   139	            report.last_price_update = pd.to_datetime(price_history[date_col].max())
   140	            report.price_history_days = len(price_history)
   141	
   142	        # Run all validation checks
   143	        self._check_freshness(ticker, fundamentals, price_history, report)
   144	        self._check_completeness(ticker, fundamentals, price_history, report)
   145	        self._check_anomalies(ticker, fundamentals, price_history, report)
   146	
   147	        # Calculate overall quality score
   148	        report.overall_score = self._calculate_quality_score(report)
   149	
   150	        # Determine if refresh is needed
   151	        report.needs_refresh = (
   152	            report.has_critical_issues or
   153	            len(report.get_issues_by_severity(IssueSeverity.WARNING)) >= 3
   154	        )
   155	
   156	        logger.info(f"{ticker} quality score: {report.overall_score:.1f}/100, "
   157	                   f"issues: {len(report.issues)}, needs_refresh: {report.needs_refresh}")
   158	
   159	        return report
   160	
   161	    def check_all_tickers(self) -> Dict[str, TickerQualityReport]:
   162	        """Run quality checks on all tickers in the database.
   163	
   164	        Returns:
   165	            Dictionary mapping ticker to quality report
   166	        """
   167	        tickers = self.db.get_all_tickers()
   168	        logger.info(f"Running quality checks on {len(tickers)} tickers")
   169	
   170	        reports = {}
   171	        for ticker in tickers:
   172	            try:
   173	                reports[ticker] = self.check_ticker(ticker)
   174	            except Exception as e:
   175	                logger.error(f"Error checking {ticker}: {e}")
   176	                # Create error report
   177	                error_report = TickerQualityReport(ticker=ticker)
   178	                error_report.add_issue(DataQualityIssue(
   179	                    ticker=ticker,
   180	                    issue_type="check_error",
   181	                    severity=IssueSeverity.CRITICAL,
   182	                    description=f"Error during quality check: {str(e)}"
   183	                ))
   184	                error_report.overall_score = 0.0
   185	                error_report.needs_refresh = True
   186	                reports[ticker] = error_report
   187	
   188	        return reports
   189	
   190	    def _check_freshness(
   191	        self,
   192	        ticker: str,
   193	        fundamentals: Dict[str, Any],
   194	        price_history: pd.DataFrame,
   195	        report: TickerQualityReport
   196	    ) -> None:
   197	        """Check data freshness."""
   198	        now = datetime.now()
   199	
   200	        # Check fundamental data freshness
   201	        # Use 'date' field from fundamentals table
   202	        fund_date = fundamentals.get('date')
   203	        if fund_date:
   204	            if isinstance(fund_date, str):
   205	                last_updated = datetime.fromisoformat(fund_date)
   206	            else:
   207	                last_updated = fund_date
   208	
   209	            days_old = (now - last_updated).days
   210	            if days_old > self.FUNDAMENTAL_STALE_DAYS:
   211	                report.add_issue(DataQualityIssue(
   212	                    ticker=ticker,
   213	                    issue_type="stale_fundamentals",
   214	                    severity=IssueSeverity.WARNING,
   215	                    description=f"Fundamental data is {days_old} days old (threshold: {self.FUNDAMENTAL_STALE_DAYS} days)",
   216	                    metadata={"days_old": days_old, "last_updated": last_updated.isoformat()}
   217	                ))
   218	
   219	        # Check price data freshness
   220	        if not price_history.empty:
   221	            # Price history DataFrame uses 'Date' (capital D) column
   222	            date_col = 'Date' if 'Date' in price_history.columns else 'date'
   223	            last_price_date = pd.to_datetime(price_history[date_col].max())
   224	            days_old = (now - last_price_date).days
   225	
   226	            # Account for weekends - only flag if older than threshold + 2 days
   227	            effective_threshold = self.PRICE_STALE_DAYS
   228	            if now.weekday() in [0, 6]:  # Monday or Sunday
   229	                effective_threshold += 2
   230	
   231	            if days_old > effective_threshold:
   232	                report.add_issue(DataQualityIssue(
   233	                    ticker=ticker,
   234	                    issue_type="stale_prices",
   235	                    severity=IssueSeverity.WARNING,
   236	                    description=f"Price data is {days_old} days old (threshold: {effective_threshold} days)",
   237	                    metadata={"days_old": days_old, "last_price_date": last_price_date.isoformat()}
   238	                ))
   239	        else:
   240	            report.add_issue(DataQualityIssue(
   241	                ticker=ticker,
   242	                issue_type="missing_prices",
   243	                severity=IssueSeverity.CRITICAL,
   244	                description="No price history available"
   245	            ))
   246	
   247	    def _check_completeness(
   248	        self,
   249	        ticker: str,
   250	        fundamentals: Dict[str, Any],
   251	        price_history: pd.DataFrame,
   252	        report: TickerQualityReport
   253	    ) -> None:
   254	        """Check data completeness."""
   255	        # Required fundamental fields
   256	        required_fields = ['pe_ratio', 'pb_ratio', 'current_price']
   257	        optional_fields = ['fcf_yield', 'debt_equity', 'market_cap', 'dividend_yield']
   258	
   259	        missing_required = []
   260	        missing_optional = []
   261	
   262	        for field in required_fields:
   263	            value = fundamentals.get(field)
   264	            if value is None or (isinstance(value, float) and pd.isna(value)):
   265	                missing_required.append(field)
   266	
   267	        for field in optional_fields:
   268	            value = fundamentals.get(field)
   269	            if value is None or (isinstance(value, float) and pd.isna(value)):
   270	                missing_optional.append(field)
   271	
   272	        # Report missing required fields as critical
   273	        if missing_required:
   274	            report.add_issue(DataQualityIssue(
   275	                ticker=ticker,
   276	                issue_type="missing_required_fields",
   277	                severity=IssueSeverity.CRITICAL,
   278	                description=f"Missing required fields: {', '.join(missing_required)}",
   279	                metadata={"missing_fields": missing_required}
   280	            ))
   281	
   282	        # Report missing optional fields as info
   283	        if missing_optional:
   284	            report.add_issue(DataQualityIssue(
   285	                ticker=ticker,
   286	                issue_type="missing_optional_fields",
   287	                severity=IssueSeverity.INFO,
   288	                description=f"Missing optional fields: {', '.join(missing_optional)}",
   289	                metadata={"missing_fields": missing_optional}
   290	            ))
   291	
   292	        # Calculate completeness percentage
   293	        total_fields = len(required_fields) + len(optional_fields)
   294	        present_fields = total_fields - len(missing_required) - len(missing_optional)
   295	        report.fundamental_completeness = (present_fields / total_fields) * 100
   296	
   297	        # Check price history completeness
   298	        if not price_history.empty:
   299	            days_available = len(price_history)
   300	            if days_available < self.MIN_HISTORY_DAYS:
   301	                report.add_issue(DataQualityIssue(
   302	                    ticker=ticker,
   303	                    issue_type="insufficient_history",
   304	                    severity=IssueSeverity.WARNING,
   305	                    description=f"Only {days_available} days of price history (minimum: {self.MIN_HISTORY_DAYS})",
   306	                    metadata={"days_available": days_available, "days_required": self.MIN_HISTORY_DAYS}
   307	                ))
   308	
   309	            # Check for gaps in trading days
   310	            date_col = 'Date' if 'Date' in price_history.columns else 'date'
   311	            price_history = price_history.sort_values(date_col)
   312	            dates = pd.to_datetime(price_history[date_col])
   313	            date_diffs = dates.diff().dt.days
   314	
   315	            # Gaps > 7 days (accounting for weekends and holidays)
   316	            large_gaps = date_diffs[date_diffs > 7]
   317	            if not large_gaps.empty:
   318	                report.add_issue(DataQualityIssue(
   319	                    ticker=ticker,
   320	                    issue_type="price_history_gaps",
   321	                    severity=IssueSeverity.INFO,
   322	                    description=f"Found {len(large_gaps)} gaps >7 days in price history",
   323	                    metadata={"num_gaps": len(large_gaps), "max_gap_days": int(large_gaps.max())}
   324	                ))
   325	
   326	    def _check_anomalies(
   327	        self,
   328	        ticker: str,
   329	        fundamentals: Dict[str, Any],
   330	        price_history: pd.DataFrame,
   331	        report: TickerQualityReport
   332	    ) -> None:
   333	        """Check for data anomalies."""
   334	        # Check fundamental value anomalies
   335	        pe_ratio = fundamentals.get('pe_ratio')
   336	        if pe_ratio is not None and not pd.isna(pe_ratio):
   337	            if pe_ratio < 0:
   338	                # Negative P/E can be valid (losses) but flag for awareness
   339	                report.add_issue(DataQualityIssue(
   340	                    ticker=ticker,
   341	                    issue_type="negative_pe",
   342	                    severity=IssueSeverity.INFO,
   343	                    description=f"Negative P/E ratio: {pe_ratio:.2f} (company may be unprofitable)",
   344	                    metadata={"pe_ratio": pe_ratio}
   345	                ))
   346	            elif pe_ratio > self.MAX_REASONABLE_PE:
   347	                report.add_issue(DataQualityIssue(
   348	                    ticker=ticker,
   349	                    issue_type="extreme_pe",
   350	                    severity=IssueSeverity.WARNING,
   351	                    description=f"Extremely high P/E ratio: {pe_ratio:.2f} (may indicate data error)",
   352	                    metadata={"pe_ratio": pe_ratio}
   353	                ))
   354	
   355	        pb_ratio = fundamentals.get('pb_ratio')
   356	        if pb_ratio is not None and not pd.isna(pb_ratio):
   357	            if pb_ratio > self.MAX_REASONABLE_PB:
   358	                report.add_issue(DataQualityIssue(
   359	                    ticker=ticker,
   360	                    issue_type="extreme_pb",
   361	                    severity=IssueSeverity.WARNING,
   362	                    description=f"Extremely high P/B ratio: {pb_ratio:.2f} (may indicate data error)",
   363	                    metadata={"pb_ratio": pb_ratio}
   364	                ))
   365	            elif pb_ratio < 0:
   366	                report.add_issue(DataQualityIssue(
   367	                    ticker=ticker,
   368	                    issue_type="negative_pb",
   369	                    severity=IssueSeverity.WARNING,
   370	                    description=f"Negative P/B ratio: {pb_ratio:.2f} (company has negative book value)",
   371	                    metadata={"pb_ratio": pb_ratio}
   372	                ))
   373	
   374	        current_price = fundamentals.get('current_price')
   375	        if current_price is not None and not pd.isna(current_price):
   376	            if current_price < self.MIN_REASONABLE_PRICE:
   377	                report.add_issue(DataQualityIssue(
   378	                    ticker=ticker,
   379	                    issue_type="penny_stock",
   380	                    severity=IssueSeverity.INFO,
   381	                    description=f"Very low price: ${current_price:.4f} (penny stock)",
   382	                    metadata={"current_price": current_price}
   383	                ))
   384	
   385	        # Check price history anomalies
   386	        if not price_history.empty and len(price_history) > 1:
   387	            date_col = 'Date' if 'Date' in price_history.columns else 'date'
   388	            close_col = 'Close' if 'Close' in price_history.columns else 'close'
   389	            volume_col = 'Volume' if 'Volume' in price_history.columns else 'volume'
   390	
   391	            price_history = price_history.sort_values(date_col)
   392	
   393	            # Calculate daily returns
   394	            closes = price_history[close_col].values
   395	            returns = (closes[1:] - closes[:-1]) / closes[:-1]
   396	
   397	            # Flag large single-day changes (potential stock splits)
   398	            large_changes = abs(returns) > self.MAX_SINGLE_DAY_CHANGE
   399	            if large_changes.any():
   400	                num_spikes = large_changes.sum()
   401	                max_change = abs(returns).max()
   402	                report.add_issue(DataQualityIssue(
   403	                    ticker=ticker,
   404	                    issue_type="price_spike",
   405	                    severity=IssueSeverity.WARNING,
   406	                    description=f"Found {num_spikes} price spike(s) >{self.MAX_SINGLE_DAY_CHANGE*100:.0f}% "
   407	                               f"(max: {max_change*100:.1f}%) - possible stock split or data error",
   408	                    metadata={"num_spikes": int(num_spikes), "max_change_pct": float(max_change * 100)}
   409	                ))
   410	
   411	            # Check volume anomalies
   412	            volumes = price_history[volume_col].values
   413	            if len(volumes) > 20:
   414	                avg_volume = volumes.mean()
   415	                if avg_volume > 0:
   416	                    volume_ratios = volumes / avg_volume
   417	
   418	                    # Flag extreme volume spikes
   419	                    extreme_spikes = volume_ratios > self.VOLUME_SPIKE_MULTIPLIER
   420	                    if extreme_spikes.any():
   421	                        num_spikes = extreme_spikes.sum()
   422	                        max_ratio = volume_ratios.max()
   423	                        report.add_issue(DataQualityIssue(
   424	                            ticker=ticker,
   425	                            issue_type="volume_spike",
   426	                            severity=IssueSeverity.INFO,
   427	                            description=f"Found {num_spikes} volume spike(s) >{self.VOLUME_SPIKE_MULTIPLIER}x average "
   428	                                       f"(max: {max_ratio:.1f}x)",
   429	                            metadata={"num_spikes": int(num_spikes), "max_ratio": float(max_ratio)}
   430	                        ))
   431	
   432	                    # Flag zero volume days
   433	                    zero_volume_days = (volumes == 0).sum()
   434	                    if zero_volume_days > 0:
   435	                        report.add_issue(DataQualityIssue(
   436	                            ticker=ticker,
   437	                            issue_type="zero_volume",
   438	                            severity=IssueSeverity.WARNING,
   439	                            description=f"Found {zero_volume_days} day(s) with zero volume",
   440	                            metadata={"zero_volume_days": int(zero_volume_days)}
   441	                        ))
   442	
   443	    def _calculate_quality_score(self, report: TickerQualityReport) -> float:
   444	        """Calculate overall quality score (0-100).
   445	
   446	        Scoring breakdown:
   447	        - Start with 100 points
   448	        - Subtract points for each issue based on severity
   449	        - Bonus for data completeness and history length
   450	        """
   451	        score = 100.0
   452	
   453	        # Deduct points for issues
   454	        for issue in report.issues:
   455	            if issue.severity == IssueSeverity.CRITICAL:
   456	                score -= 30
   457	            elif issue.severity == IssueSeverity.WARNING:
   458	                score -= 10
   459	            elif issue.severity == IssueSeverity.INFO:
   460	                score -= 2
   461	
   462	        # Bonus for completeness (up to +10 points)
   463	        completeness_bonus = (report.fundamental_completeness / 100) * 10
   464	        score += completeness_bonus
   465	
   466	        # Bonus for sufficient history (up to +10 points)
   467	        if report.price_history_days >= self.MIN_HISTORY_DAYS:
   468	            history_bonus = min(10, (report.price_history_days / self.MIN_HISTORY_DAYS) * 5)
   469	            score += history_bonus
   470	
   471	        # Clamp to 0-100
   472	        return max(0.0, min(100.0, score))
   473	
   474	    def generate_summary_report(self, reports: Dict[str, TickerQualityReport]) -> str:
   475	        """Generate human-readable summary report.
   476	
   477	        Args:
   478	            reports: Dictionary of ticker quality reports
   479	
   480	        Returns:
   481	            Formatted report string
   482	        """
   483	        lines = []
   484	        lines.append("=" * 80)
   485	        lines.append("DATA QUALITY SUMMARY REPORT")
   486	        lines.append("=" * 80)
   487	        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
   488	        lines.append(f"Total Tickers Analyzed: {len(reports)}\n")
   489	
   490	        # Overall statistics
   491	        scores = [r.overall_score for r in reports.values()]
   492	        avg_score = sum(scores) / len(scores) if scores else 0
   493	        tickers_needing_refresh = sum(1 for r in reports.values() if r.needs_refresh)
   494	        tickers_with_critical = sum(1 for r in reports.values() if r.has_critical_issues)
   495	
   496	        lines.append("Overall Statistics:")
   497	        lines.append(f"  Average Quality Score: {avg_score:.1f}/100")
   498	        lines.append(f"  Tickers Needing Refresh: {tickers_needing_refresh} ({tickers_needing_refresh/len(reports)*100:.0f}%)")
   499	        lines.append(f"  Tickers with Critical Issues: {tickers_with_critical} ({tickers_with_critical/len(reports)*100:.0f}%)")
   500	
   501	        # Categorize tickers by quality
   502	        excellent = [t for t, r in reports.items() if r.overall_score >= 90]
   503	        good = [t for t, r in reports.items() if 70 <= r.overall_score < 90]
   504	        fair = [t for t, r in reports.items() if 50 <= r.overall_score < 70]
   505	        poor = [t for t, r in reports.items() if r.overall_score < 50]
   506	
   507	        lines.append(f"\nQuality Distribution:")
   508	        lines.append(f"  Excellent (90-100): {len(excellent)} tickers - {excellent}")
   509	        lines.append(f"  Good (70-89):       {len(good)} tickers - {good}")
   510	        lines.append(f"  Fair (50-69):       {len(fair)} tickers - {fair}")
   511	        lines.append(f"  Poor (0-49):        {len(poor)} tickers - {poor}")
   512	
   513	        # Detail section for each ticker
   514	        lines.append("\n" + "=" * 80)
   515	        lines.append("DETAILED TICKER REPORTS")
   516	        lines.append("=" * 80)
   517	
   518	        # Sort by quality score (worst first)
   519	        sorted_reports = sorted(reports.items(), key=lambda x: x[1].overall_score)
   520	
   521	        for ticker, report in sorted_reports:
   522	            lines.append(f"\n{ticker} - Quality Score: {report.overall_score:.1f}/100")
   523	            lines.append("-" * 80)
   524	
   525	            # Status
   526	            if report.overall_score >= 90:
   527	                status = "✓ EXCELLENT - Ready for screening"
   528	            elif report.overall_score >= 70:
   529	                status = "✓ GOOD - Ready for screening"
   530	            elif report.overall_score >= 50:
   531	                status = "⚠ FAIR - Usable with caution"
   532	            else:
   533	                status = "✗ POOR - Needs refresh"
   534	
   535	            lines.append(f"Status: {status}")
   536	
   537	            # Metadata
   538	            if report.last_fundamental_update:
   539	                lines.append(f"Last Fundamental Update: {report.last_fundamental_update.strftime('%Y-%m-%d')}")
   540	            if report.last_price_update:
   541	                lines.append(f"Last Price Update: {report.last_price_update.strftime('%Y-%m-%d')}")
   542	            lines.append(f"Price History Days: {report.price_history_days}")
   543	            lines.append(f"Fundamental Completeness: {report.fundamental_completeness:.0f}%")
   544	
   545	            # Issues
   546	            if report.issues:
   547	                lines.append(f"\nIssues Found ({len(report.issues)}):")
   548	                critical = report.get_issues_by_severity(IssueSeverity.CRITICAL)
   549	                warnings = report.get_issues_by_severity(IssueSeverity.WARNING)
   550	                info = report.get_issues_by_severity(IssueSeverity.INFO)
   551	
   552	                if critical:
   553	                    lines.append(f"  CRITICAL ({len(critical)}):")
   554	                    for issue in critical:
   555	                        lines.append(f"    - {issue.description}")
   556	
   557	                if warnings:
   558	                    lines.append(f"  WARNINGS ({len(warnings)}):")
   559	                    for issue in warnings:
   560	                        lines.append(f"    - {issue.description}")
   561	
   562	                if info:
   563	                    lines.append(f"  INFO ({len(info)}):")
   564	                    for issue in info:
   565	                        lines.append(f"    - {issue.description}")
   566	            else:
   567	                lines.append("\nNo issues found - Data quality is excellent!")
   568	
   569	            # Recommendation
   570	            if report.needs_refresh:
   571	                lines.append("\n⟳ RECOMMENDATION: Re-fetch data for this ticker")
   572	
   573	        # Summary recommendations
   574	        lines.append("\n" + "=" * 80)
   575	        lines.append("RECOMMENDATIONS")
   576	        lines.append("=" * 80)
   577	
   578	        if tickers_needing_refresh > 0:
   579	            refresh_list = [t for t, r in reports.items() if r.needs_refresh]
   580	            lines.append(f"\nTickers to refresh ({len(refresh_list)}):")
   581	            lines.append(f"  {', '.join(refresh_list)}")
   582	        else:
   583	            lines.append("\n✓ All tickers have acceptable data quality!")
   584	
   585	        lines.append("\n" + "=" * 80)
   586	
   587	        return "\n".join(lines)
   588	
   589	    def save_quality_log(self, reports: Dict[str, TickerQualityReport]) -> None:
   590	        """Save quality check results to database.
   591	
   592	        Args:
   593	            reports: Dictionary of ticker quality reports
   594	        """
   595	        logger.info(f"Saving quality log for {len(reports)} tickers")
   596	
   597	        from sqlalchemy import text
   598	
   599	        with self.db.engine.begin() as conn:
   600	            for ticker, report in reports.items():
   601	                # Insert quality log entry (convert booleans to int for SQLite)
   602	                conn.execute(
   603	                    text("""
   604	                        INSERT INTO data_quality_log
   605	                        (ticker, check_date, overall_score, has_critical_issues,
   606	                         needs_refresh, num_issues, issue_summary)
   607	                        VALUES (:ticker, :check_date, :score, :critical,
   608	                                :refresh, :num_issues, :summary)
   609	                    """),
   610	                    {
   611	                        "ticker": ticker,
   612	                        "check_date": datetime.now(),
   613	                        "score": report.overall_score,
   614	                        "critical": 1 if report.has_critical_issues else 0,
   615	                        "refresh": 1 if report.needs_refresh else 0,
   616	                        "num_issues": len(report.issues),
   617	                        "summary": "; ".join([issue.description for issue in report.issues[:5]])  # First 5 issues
   618	                    }
   619	                )
   620	
   621	        logger.info("Quality log saved successfully")
     1	#!/usr/bin/env python3
     2	"""Fetch real recent news headlines for a list of tickers — used by the GUI
     3	dashboard's Market tab news sections. Free/fast: reuses catalyst_sentiment.py's
     4	headline fetcher directly (yfinance), no Claude/LLM call involved here at all.
     5	
     6	Usage:
     7	    python scripts/fetch_news.py --tickers AAPL,MSFT,NVDA --json-out out.json
     8	"""
     9	import argparse
    10	import json
    11	import sys
    12	from datetime import datetime
    13	from pathlib import Path
    14	
    15	sys.path.insert(0, str(Path(__file__).parent.parent))
    16	
    17	from src.agents.catalyst_sentiment import _fetch_headlines
    18	
    19	
    20	def main():
    21	    parser = argparse.ArgumentParser()
    22	    parser.add_argument('--tickers', type=str, required=True, help='Comma-separated ticker list')
    23	    parser.add_argument('--json-out', type=str, required=True)
    24	    args = parser.parse_args()
    25	
    26	    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    27	    news = {}
    28	    for ticker in tickers:
    29	        print(f"Fetching news for {ticker}...")
    30	        news[ticker] = _fetch_headlines(ticker, limit=5)
    31	
    32	    out_path = Path(args.json_out)
    33	    out_path.parent.mkdir(parents=True, exist_ok=True)
    34	    out_path.write_text(json.dumps({
    35	        'generated': datetime.now().isoformat(),
    36	        'tickers': tickers,
    37	        'news': news,
    38	    }, indent=2, default=str))
    39	    print(f"Wrote news for {len(tickers)} tickers to {out_path}")
    40	
    41	
    42	if __name__ == '__main__':
    43	    main()
     1	#!/usr/bin/env python3
     2	"""Fetch recent daily close price history for a list of tickers — used by the
     3	GUI dashboard's Shortlist charts and the "Live" auto-refresh feature. Free/fast:
     4	yfinance only, no LLM call involved.
     5	
     6	Usage:
     7	    python scripts/fetch_price_history.py --tickers AAPL,MSFT,NVDA --json-out out.json
     8	"""
     9	import argparse
    10	import json
    11	import sys
    12	from datetime import datetime
    13	from pathlib import Path
    14	
    15	import pandas as pd
    16	import yfinance as yf
    17	
    18	
    19	def _fetch_history(ticker: str):
    20	    """Last ~180 trading days of close prices. Drops any NaN close (e.g. an
    21	    in-progress trading day with no closing print yet) — a bare NaN would
    22	    otherwise get written by json.dumps as an invalid, unparseable JSON token.
    23	    Never raises."""
    24	    try:
    25	        hist = yf.Ticker(ticker).history(period="9mo")
    26	        closes = hist["Close"].iloc[-180:]
    27	        return [
    28	            {"date": str(idx.date()) if hasattr(idx, "date") else str(idx), "close": round(float(c), 2)}
    29	            for idx, c in closes.items() if pd.notna(c)
    30	        ]
    31	    except Exception as e:
    32	        print(f"Failed to fetch price history for {ticker}: {e}")
    33	        return []
    34	
    35	
    36	def main():
    37	    parser = argparse.ArgumentParser()
    38	    parser.add_argument('--tickers', type=str, required=True, help='Comma-separated ticker list')
    39	    parser.add_argument('--json-out', type=str, required=True)
    40	    args = parser.parse_args()
    41	
    42	    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    43	    prices = {}
    44	    for ticker in tickers:
    45	        print(f"Fetching price history for {ticker}...")
    46	        prices[ticker] = _fetch_history(ticker)
    47	
    48	    out_path = Path(args.json_out)
    49	    out_path.parent.mkdir(parents=True, exist_ok=True)
    50	    out_path.write_text(json.dumps({
    51	        'generated': datetime.now().isoformat(),
    52	        'tickers': tickers,
    53	        'prices': prices,
    54	    }, indent=2, default=str), encoding="utf-8")
    55	    print(f"Wrote price history for {len(tickers)} tickers to {out_path}")
    56	
    57	
    58	if __name__ == '__main__':
    59	    main()

exec
/bin/zsh -lc "nl -ba src/notifications/scheduler.py; nl -ba automated_position_report.py | sed -n '1,360p'; nl -ba src/utils/json_safe.py; git status --short" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	"""Scheduling module for automated stock screening and notifications.
     2	
     3	Supports running screening on a schedule (daily, hourly, etc.) with
     4	automatic notifications via email and/or Slack.
     5	"""
     6	
     7	import argparse
     8	import logging
     9	import os
    10	import sys
    11	from datetime import datetime
    12	from typing import List, Optional
    13	
    14	import pandas as pd
    15	from dotenv import load_dotenv
    16	
    17	# Add parent directory to path for imports
    18	sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    19	
    20	from src.data import YahooFinanceFetcher, StockDatabase
    21	from src.screening import screen_candidates
    22	from .email_notifier import EmailNotifier
    23	from .slack_notifier import SlackNotifier
    24	
    25	# Load environment variables
    26	load_dotenv()
    27	
    28	# Configure logging
    29	logging.basicConfig(
    30	    level=logging.INFO,
    31	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    32	)
    33	logger = logging.getLogger(__name__)
    34	
    35	
    36	class ScreeningScheduler:
    37	    """Automated stock screening with notifications.
    38	
    39	    Runs screening on a schedule and sends results via email and/or Slack.
    40	
    41	    Environment Variables:
    42	        SCREENING_TICKERS: Comma-separated list of tickers to screen
    43	        SCREENING_TOP_N: Number of top results to include in notifications (default: 10)
    44	        SCREENING_MIN_SIGNAL: Minimum buy signal to include (default: 50)
    45	
    46	    Example:
    47	        >>> scheduler = ScreeningScheduler()
    48	        >>> scheduler.run_screening()  # Run once
    49	    """
    50	
    51	    def __init__(
    52	        self,
    53	        tickers: Optional[List[str]] = None,
    54	        enable_email: bool = True,
    55	        enable_slack: bool = True
    56	    ) -> None:
    57	        """Initialize the screening scheduler.
    58	
    59	        Args:
    60	            tickers: List of tickers to screen. Defaults to env SCREENING_TICKERS.
    61	            enable_email: Whether to send email notifications.
    62	            enable_slack: Whether to send Slack notifications.
    63	        """
    64	        # Load tickers
    65	        if tickers:
    66	            self.tickers = tickers
    67	        else:
    68	            tickers_env = os.getenv('SCREENING_TICKERS', '')
    69	            if tickers_env:
    70	                self.tickers = [t.strip() for t in tickers_env.split(',')]
    71	            else:
    72	                # Default ticker list
    73	                self.tickers = [
    74	                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    75	                    'JPM', 'BAC', 'WMT', 'JNJ', 'XOM'
    76	                ]
    77	                logger.warning(f"No tickers configured. Using defaults: {self.tickers}")
    78	
    79	        self.top_n = int(os.getenv('SCREENING_TOP_N', '10'))
    80	        self.min_signal = float(os.getenv('SCREENING_MIN_SIGNAL', '50'))
    81	
    82	        # Initialize components
    83	        self.fetcher = YahooFinanceFetcher()
    84	        self.db = StockDatabase()
    85	
    86	        # Initialize notifiers
    87	        self.email_notifier = EmailNotifier() if enable_email else None
    88	        self.slack_notifier = SlackNotifier() if enable_slack else None
    89	
    90	        logger.info(f"ScreeningScheduler initialized with {len(self.tickers)} tickers")
    91	        logger.info(f"Notifications: Email={enable_email}, Slack={enable_slack}")
    92	
    93	    def fetch_data(self, update_cache: bool = True) -> bool:
    94	        """Fetch latest data for all tickers.
    95	
    96	        Args:
    97	            update_cache: Whether to update cached data.
    98	
    99	        Returns:
   100	            True if data fetched successfully, False otherwise.
   101	        """
   102	        logger.info(f"Fetching data for {len(self.tickers)} tickers...")
   103	
   104	        success_count = 0
   105	        for i, ticker in enumerate(self.tickers, 1):
   106	            try:
   107	                logger.info(f"[{i}/{len(self.tickers)}] Fetching {ticker}...")
   108	
   109	                # Fetch fundamentals
   110	                fundamentals = self.fetcher.fetch_fundamentals(ticker)
   111	                if fundamentals:
   112	                    self.db.save_stock_fundamentals(ticker, fundamentals)
   113	                    logger.debug(f"✓ {ticker} fundamentals saved")
   114	
   115	                # Fetch price history
   116	                prices = self.fetcher.fetch_price_history(ticker, period="1y")
   117	                if not prices.empty:
   118	                    self.db.save_price_history(ticker, prices)
   119	                    logger.debug(f"✓ {ticker} price history saved")
   120	                    success_count += 1
   121	
   122	            except Exception as e:
   123	                logger.error(f"✗ Failed to fetch {ticker}: {e}")
   124	                continue
   125	
   126	        logger.info(f"Data fetch complete: {success_count}/{len(self.tickers)} successful")
   127	        return success_count > 0
   128	
   129	    def run_screening(self) -> Optional[pd.DataFrame]:
   130	        """Run screening on configured tickers.
   131	
   132	        Returns:
   133	            DataFrame with screening results, or None if failed.
   134	        """
   135	        logger.info("Starting screening analysis...")
   136	
   137	        try:
   138	            # Run screening
   139	            results = screen_candidates(self.db, self.tickers)
   140	
   141	            if results.empty:
   142	                logger.warning("No screening results generated")
   143	                return None
   144	
   145	            # Filter by minimum signal
   146	            results = results[results['buy_signal'] >= self.min_signal]
   147	
   148	            if results.empty:
   149	                logger.info(f"No candidates meet minimum signal threshold: {self.min_signal}")
   150	                return None
   151	
   152	            logger.info(f"Screening complete: {len(results)} candidates found")
   153	            return results
   154	
   155	        except Exception as e:
   156	            logger.error(f"Screening failed: {e}")
   157	            return None
   158	
   159	    def send_notifications(self, results: pd.DataFrame) -> bool:
   160	        """Send notifications with screening results.
   161	
   162	        Args:
   163	            results: DataFrame with screening results.
   164	
   165	        Returns:
   166	            True if at least one notification sent successfully.
   167	        """
   168	        if results.empty:
   169	            logger.warning("No results to send")
   170	            return False
   171	
   172	        success = False
   173	
   174	        # Send email
   175	        if self.email_notifier:
   176	            try:
   177	                if self.email_notifier.send_screening_results(results, self.top_n):
   178	                    logger.info("✓ Email notification sent")
   179	                    success = True
   180	                else:
   181	                    logger.warning("✗ Email notification failed")
   182	            except Exception as e:
   183	                logger.error(f"Email notification error: {e}")
   184	
   185	        # Send Slack
   186	        if self.slack_notifier:
   187	            try:
   188	                # Use fewer results for Slack (more concise)
   189	                slack_top_n = min(self.top_n, 5)
   190	                if self.slack_notifier.send_screening_results(results, slack_top_n):
   191	                    logger.info("✓ Slack notification sent")
   192	                    success = True
   193	                else:
   194	                    logger.warning("✗ Slack notification failed")
   195	            except Exception as e:
   196	                logger.error(f"Slack notification error: {e}")
   197	
   198	        return success
   199	
   200	    def run_once(self, fetch_data: bool = True) -> bool:
   201	        """Run screening once and send notifications.
   202	
   203	        Args:
   204	            fetch_data: Whether to fetch fresh data before screening.
   205	
   206	        Returns:
   207	            True if successful, False otherwise.
   208	        """
   209	        logger.info("=" * 60)
   210	        logger.info("AUTOMATED STOCK SCREENING - SINGLE RUN")
   211	        logger.info("=" * 60)
   212	        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
   213	        logger.info(f"Tickers: {len(self.tickers)}")
   214	        logger.info(f"Top N: {self.top_n}")
   215	        logger.info(f"Min Signal: {self.min_signal}")
   216	        logger.info("=" * 60)
   217	
   218	        try:
   219	            # Fetch data if needed
   220	            if fetch_data:
   221	                if not self.fetch_data():
   222	                    logger.error("Data fetch failed")
   223	                    return False
   224	
   225	            # Run screening
   226	            results = self.run_screening()
   227	            if results is None or results.empty:
   228	                logger.warning("No screening results")
   229	                return False
   230	
   231	            # Send notifications
   232	            if self.send_notifications(results):
   233	                logger.info("✓ Screening and notifications complete")
   234	                return True
   235	            else:
   236	                logger.warning("Screening complete but notifications failed")
   237	                return False
   238	
   239	        except Exception as e:
   240	            logger.error(f"Screening run failed: {e}")
   241	            return False
   242	
   243	    def test_setup(self) -> bool:
   244	        """Test configuration and connections.
   245	
   246	        Returns:
   247	            True if all tests pass, False otherwise.
   248	        """
   249	        logger.info("Testing setup...")
   250	
   251	        all_passed = True
   252	
   253	        # Test database
   254	        try:
   255	            all_tickers = self.db.get_all_tickers()
   256	            logger.info(f"✓ Database connected ({len(all_tickers)} stocks)")
   257	        except Exception as e:
   258	            logger.error(f"✗ Database error: {e}")
   259	            all_passed = False
   260	
   261	        # Test email
   262	        if self.email_notifier:
   263	            if self.email_notifier.test_connection():
   264	                logger.info("✓ Email configuration valid")
   265	            else:
   266	                logger.warning("✗ Email configuration invalid")
   267	                all_passed = False
   268	
   269	        # Test Slack
   270	        if self.slack_notifier:
   271	            if self.slack_notifier.test_connection():
   272	                logger.info("✓ Slack configuration valid")
   273	            else:
   274	                logger.warning("✗ Slack configuration invalid")
   275	                all_passed = False
   276	
   277	        return all_passed
   278	
   279	
   280	def main():
   281	    """Main entry point for command-line usage."""
   282	    parser = argparse.ArgumentParser(description='Stock Screening Scheduler')
   283	
   284	    parser.add_argument(
   285	        'command',
   286	        choices=['run', 'test', 'fetch'],
   287	        help='Command to execute'
   288	    )
   289	    parser.add_argument(
   290	        '--tickers',
   291	        type=str,
   292	        help='Comma-separated list of tickers (overrides env var)'
   293	    )
   294	    parser.add_argument(
   295	        '--top-n',
   296	        type=int,
   297	        default=10,
   298	        help='Number of top results (default: 10)'
   299	    )
   300	    parser.add_argument(
   301	        '--no-email',
   302	        action='store_true',
   303	        help='Disable email notifications'
   304	    )
   305	    parser.add_argument(
   306	        '--no-slack',
   307	        action='store_true',
   308	        help='Disable Slack notifications'
   309	    )
   310	
   311	    args = parser.parse_args()
   312	
   313	    # Parse tickers
   314	    tickers = None
   315	    if args.tickers:
   316	        tickers = [t.strip() for t in args.tickers.split(',')]
   317	
   318	    # Initialize scheduler
   319	    scheduler = ScreeningScheduler(
   320	        tickers=tickers,
   321	        enable_email=not args.no_email,
   322	        enable_slack=not args.no_slack
   323	    )
   324	
   325	    if hasattr(scheduler, 'top_n'):
   326	        scheduler.top_n = args.top_n
   327	
   328	    # Execute command
   329	    if args.command == 'test':
   330	        success = scheduler.test_setup()
   331	        sys.exit(0 if success else 1)
   332	
   333	    elif args.command == 'fetch':
   334	        success = scheduler.fetch_data()
   335	        sys.exit(0 if success else 1)
   336	
   337	    elif args.command == 'run':
   338	        success = scheduler.run_once()
   339	        sys.exit(0 if success else 1)
   340	
   341	
   342	if __name__ == "__main__":
   343	    main()
     1	#!/usr/bin/env python3
     2	"""Automated position reporting - NOT CURRENTLY SUPPORTED for Fidelity.
     3	
     4	This used to run as part of a GitHub Actions workflow, logging into Robinhood
     5	with stored credentials (via the unofficial robin_stocks library) to fetch
     6	positions headlessly. Fidelity has no equivalent unofficial API — position
     7	data now comes from a CSV you export yourself from Fidelity's website, which
     8	means it can't be fetched automatically in a headless CI run the way
     9	Robinhood's login could.
    10	
    11	For position analysis now, export your positions CSV from Fidelity
    12	(Accounts & Trade -> Positions -> Download) and run:
    13	    python manage_positions.py --csv path/to/your_export.csv
    14	
    15	This script is left in place in case a Fidelity automation path (e.g. you
    16	manually drop a fresh CSV somewhere this job can read) becomes worth wiring
    17	up later — it currently just exits without doing anything.
    18	"""
    19	
    20	import sys
    21	
    22	print("automated_position_report.py: not supported for Fidelity (no headless-fetchable API).")
    23	print("Export your positions from Fidelity's website and run:")
    24	print("  python manage_positions.py --csv path/to/your_export.csv")
    25	sys.exit(0)
     1	"""Shared helper for writing JSON that the GUI dashboard's browser-side
     2	JavaScript will actually be able to parse.
     3	
     4	Any script whose output flows into the dashboard (via --json-out) touches
     5	pandas/yfinance data at some point, which can leave a NaN behind — an SMA
     6	with not enough real history, a return-pct computed from a missing price,
     7	an average over an empty list. Python's json.dumps happily serializes NaN
     8	and Infinity as bare, non-standard tokens (NaN, Infinity) by default; the
     9	browser's JSON.parse() rejects them outright with no server-side error to
    10	point at, so the dashboard view just hangs on "Loading..." forever with no
    11	visible cause. sanitize_nan() replaces any such float with None (JSON null)
    12	right before serialization, regardless of which upstream calculation
    13	produced it.
    14	"""
    15	import math
    16	
    17	
    18	def sanitize_nan(obj):
    19	    if isinstance(obj, float):
    20	        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    21	    if isinstance(obj, dict):
    22	        return {k: sanitize_nan(v) for k, v in obj.items()}
    23	    if isinstance(obj, list):
    24	        return [sanitize_nan(v) for v in obj]
    25	    return obj
 M dashboard.py
 M data/cache/AAPL_prices_5y_1d.pkl
 M data/cache/AMZN_prices_5y_1d.pkl
 M data/cache/GOOGL_prices_5y_1d.pkl
 M data/cache/MSFT_prices_5y_1d.pkl
 M data/cache/TSLA_prices_5y_1d.pkl
 M data/daily_scans/latest_optimized_scan.txt
 M manage_positions.py
 M requirements.txt
 M scripts/backtest_top3.py
 M scripts/backtest_top3_monte_carlo.py
 M scripts/walk_forward_backtest.py
 M src/__pycache__/__init__.cpython-313.pyc
 M src/agents/catalyst_sentiment.py
 M src/analysis/position_manager.py
 M src/data/__pycache__/__init__.cpython-313.pyc
 M src/data/__pycache__/fetcher.cpython-313.pyc
 M src/data/__pycache__/storage.cpython-313.pyc
 M src/notifications/email_notifier.py
 M src/screening/__pycache__/__init__.cpython-313.pyc
 M src/screening/__pycache__/indicators.cpython-313.pyc
 M src/screening/__pycache__/screener.cpython-313.pyc
?? .claude/skills/dashboard/
?? .sprint/
?? data/catalyst_sentiment/sentiment_20260909_172815.json
?? data/congress_trades/signals_20260909_172815.json
?? data/daily_scans/optimized_scan_20260909_172815.txt
?? data/daily_scans/shortlist_latest.json
?? data/daily_scans/top20_latest.json
?? data/fundamentals_audit/audit_20260909_172331.json
?? mac_app/
?? position/
?? scripts/fetch_momentum_status.py
?? scripts/fetch_news.py
?? scripts/fetch_price_history.py
?? static/
?? templates/

exec
/bin/zsh -lc "rg -n \"def test_connection|smtplib.SMTP\" src/notifications/email_notifier.py; nl -ba src/notifications/email_notifier.py | sed -n '110,190p'; nl -ba src/notifications/email_notifier.py | sed -n '270,470p'; nl -ba .github/workflows/daily_screening_git_storage.yml | sed -n '120,175p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
297:            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
361:            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
371:        except smtplib.SMTPAuthenticationError:
374:        except smtplib.SMTPException as e:
451:            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
461:        except smtplib.SMTPAuthenticationError:
464:        except smtplib.SMTPException as e:
918:    def test_connection(self) -> bool:
935:            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
940:        except smtplib.SMTPAuthenticationError:
943:        except smtplib.SMTPException as e:
   110	                    elif val >= 65:
   111	                        color = '#f39c12'  # Orange
   112	                    else:
   113	                        color = '#95a5a6'  # Gray
   114	                    display = f'<span style="color: {color}; font-weight: bold;">{val:.1f}</span>'
   115	                elif col == 'current_price':
   116	                    display = f'${float(value):.2f}'
   117	                elif col == 'rsi':
   118	                    val = float(value)
   119	                    if val < 30:
   120	                        color = '#e74c3c'  # Red (oversold)
   121	                    elif val < 70:
   122	                        color = '#000'  # Black
   123	                    else:
   124	                        color = '#c0392b'  # Dark red (overbought)
   125	                    display = f'<span style="color: {color};">{val:.1f}</span>'
   126	                elif isinstance(value, (int, float)):
   127	                    display = f'{value:.2f}'
   128	                else:
   129	                    display = str(value)
   130	
   131	                html += f'      <td style="padding: 10px; border: 1px solid #ddd;">{display}</td>\n'
   132	
   133	            html += '    </tr>\n'
   134	
   135	        html += '  </tbody>\n</table>'
   136	        return html
   137	
   138	    def _create_html_email(
   139	        self,
   140	        results: pd.DataFrame,
   141	        top_n: int = 10,
   142	        subject_prefix: str = "[Stock Screener]"
   143	    ) -> str:
   144	        """Create HTML email body with screening results.
   145	
   146	        Args:
   147	            results: DataFrame with screening results.
   148	            top_n: Number of top candidates to include.
   149	            subject_prefix: Prefix for email subject line.
   150	
   151	        Returns:
   152	            HTML email body as string.
   153	        """
   154	        today = datetime.now().strftime('%B %d, %Y')
   155	        total_candidates = len(results)
   156	
   157	        # Get top candidates
   158	        top_results = results.head(top_n)
   159	
   160	        # Select columns for email
   161	        email_cols = [
   162	            'ticker', 'buy_signal', 'value_score', 'support_score',
   163	            'current_price', 'rsi', 'pe_ratio', 'pb_ratio'
   164	        ]
   165	        display_df = top_results[email_cols].copy()
   166	
   167	        # Rename columns for display
   168	        display_df.columns = [
   169	            'Ticker', 'Buy Signal', 'Value', 'Support',
   170	            'Price', 'RSI', 'P/E', 'P/B'
   171	        ]
   172	
   173	        html = f"""
   174	<!DOCTYPE html>
   175	<html>
   176	<head>
   177	    <meta charset="UTF-8">
   178	    <style>
   179	        body {{
   180	            font-family: Arial, sans-serif;
   181	            line-height: 1.6;
   182	            color: #333;
   183	            max-width: 900px;
   184	            margin: 0 auto;
   185	            padding: 20px;
   186	        }}
   187	        .header {{
   188	            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   189	            color: white;
   190	            padding: 30px;
   270	        return html
   271	
   272	    def send_notification(self, subject: str, message: str) -> bool:
   273	        """Send a short plain-text status notification (e.g. "scan started").
   274	
   275	        Lighter-weight than send_scan_report — no HTML, no signal tables, just a
   276	        quick heads-up. Fails silently (logs + returns False) if unconfigured,
   277	        same as every other notifier method — never raises into the caller.
   278	
   279	        Args:
   280	            subject: Email subject line.
   281	            message: Plain-text body.
   282	
   283	        Returns:
   284	            True if sent successfully, False otherwise.
   285	        """
   286	        if not self.email_from or not self.email_password or not self.email_to:
   287	            logger.warning(f"Email not configured - skipping notification: {subject}")
   288	            return False
   289	
   290	        try:
   291	            msg = MIMEMultipart('alternative')
   292	            msg['From'] = self.email_from
   293	            msg['To'] = self.email_to
   294	            msg['Subject'] = subject
   295	            msg.attach(MIMEText(message, 'plain'))
   296	
   297	            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
   298	                server.starttls()
   299	                server.login(self.email_from, self.email_password)
   300	                recipients = [r.strip() for r in self.email_to.split(',')]
   301	                server.sendmail(self.email_from, recipients, msg.as_string())
   302	
   303	            logger.info(f"✓ Notification email sent: {subject}")
   304	            return True
   305	
   306	        except Exception as e:
   307	            logger.error(f"Failed to send notification email: {e}")
   308	            return False
   309	
   310	    def send_screening_results(
   311	        self,
   312	        results: pd.DataFrame,
   313	        top_n: int = 10,
   314	        subject_prefix: str = "[Stock Screener]"
   315	    ) -> bool:
   316	        """Send screening results via email.
   317	
   318	        Args:
   319	            results: DataFrame with screening results (from screen_candidates).
   320	            top_n: Number of top candidates to include in email.
   321	            subject_prefix: Prefix for email subject line.
   322	
   323	        Returns:
   324	            True if email sent successfully, False otherwise.
   325	
   326	        Example:
   327	            >>> notifier = EmailNotifier()
   328	            >>> results = screen_candidates(db, tickers)
   329	            >>> notifier.send_screening_results(results, top_n=10)
   330	        """
   331	        if not self.email_from or not self.email_password or not self.email_to:
   332	            logger.error("Email configuration incomplete. Check environment variables.")
   333	            return False
   334	
   335	        if results.empty:
   336	            logger.warning("No screening results to send")
   337	            return False
   338	
   339	        try:
   340	            # Create message
   341	            today = datetime.now().strftime('%b %d, %Y')
   342	            subject = f"{subject_prefix} Top {top_n} Candidates - {today}"
   343	
   344	            msg = MIMEMultipart('alternative')
   345	            msg['From'] = self.email_from
   346	            msg['To'] = self.email_to
   347	            msg['Subject'] = subject
   348	
   349	            # Create HTML body
   350	            html_body = self._create_html_email(results, top_n, subject_prefix)
   351	
   352	            # Create plain text fallback
   353	            text_body = self._create_text_fallback(results, top_n)
   354	
   355	            # Attach both versions
   356	            msg.attach(MIMEText(text_body, 'plain'))
   357	            msg.attach(MIMEText(html_body, 'html'))
   358	
   359	            # Send email
   360	            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
   361	            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
   362	                server.starttls()
   363	                server.login(self.email_from, self.email_password)
   364	
   365	                recipients = [r.strip() for r in self.email_to.split(',')]
   366	                server.sendmail(self.email_from, recipients, msg.as_string())
   367	
   368	            logger.info(f"✓ Email sent successfully to {self.email_to}")
   369	            return True
   370	
   371	        except smtplib.SMTPAuthenticationError:
   372	            logger.error("SMTP authentication failed. Check email credentials.")
   373	            return False
   374	        except smtplib.SMTPException as e:
   375	            logger.error(f"SMTP error: {e}")
   376	            return False
   377	        except Exception as e:
   378	            logger.error(f"Failed to send email: {e}")
   379	            return False
   380	
   381	    def send_scan_report(
   382	        self,
   383	        buy_signals: List[Dict],
   384	        sell_signals: List[Dict],
   385	        spy_analysis: Optional[Dict] = None,
   386	        breadth: Optional[Dict] = None,
   387	        top_n: int = 15,
   388	        top20: Optional[List[Dict]] = None,
   389	        fundamentals_audits: Optional[Dict[str, Dict]] = None,
   390	        catalyst_sentiments: Optional[Dict[str, Dict]] = None,
   391	        congress_signals: Optional[Dict[str, Dict]] = None,
   392	        shortlist: Optional[List[Dict]] = None,
   393	    ) -> bool:
   394	        """Send the daily optimized full-market scan results via email.
   395	
   396	        Unlike send_screening_results (which expects a DataFrame in the older
   397	        buy_signal/value_score/pe_ratio shape), this matches the dict shape produced
   398	        by run_optimized_scan.py's score_buy_signal/score_sell_signal — the current
   399	        Minervini-based scanner. Each ticker links straight to its Fidelity trade page.
   400	
   401	        Args:
   402	            buy_signals: List of buy signal dicts (already sorted, highest score first).
   403	            sell_signals: List of sell signal dicts (already sorted, highest score first).
   404	            spy_analysis: Optional SPY trend dict (phase, trend, confidence) for context.
   405	            breadth: Optional market breadth dict.
   406	            top_n: Number of top candidates per list to include in the email.
   407	            top20: Optional pre-ranked pool from top20_ranker.build_top20() —
   408	                combined technical + Reddit-buzz score, with "why it's moving" links.
   409	            fundamentals_audits: Optional {ticker: audit-dict} from
   410	                src.agents.fundamentals_auditor.audit_candidates() — Top 20 only.
   411	            catalyst_sentiments: Optional {ticker: classification-dict} from
   412	                src.agents.catalyst_sentiment.analyze_candidates() — Top 20 only.
   413	            congress_signals: Optional {ticker: signal-dict} from
   414	                src.agents.congress_trades.get_signals_for_candidates() — Top 20 only.
   415	            shortlist: Optional Top 5 from src.agents.shortlist.build_shortlist() —
   416	                the Top 20 pool actually filtered/ranked by the three agents above.
   417	                Rendered as the primary section; top20 is shown below it for reference.
   418	
   419	        Returns:
   420	            True if email sent successfully, False otherwise.
   421	        """
   422	        if not self.email_from or not self.email_password or not self.email_to:
   423	            logger.error("Email configuration incomplete. Check environment variables.")
   424	            return False
   425	
   426	        if not buy_signals and not sell_signals:
   427	            logger.warning("No buy or sell signals to email")
   428	            return False
   429	
   430	        try:
   431	            today = datetime.now().strftime('%b %d, %Y')
   432	            subject = f"[Stock Screener] {len(buy_signals)} Buy / {len(sell_signals)} Sell - {today}"
   433	
   434	            msg = MIMEMultipart('alternative')
   435	            msg['From'] = self.email_from
   436	            msg['To'] = self.email_to
   437	            msg['Subject'] = subject
   438	
   439	            html_body = self._create_scan_html_email(
   440	                buy_signals, sell_signals, spy_analysis, breadth, top_n, top20,
   441	                fundamentals_audits, catalyst_sentiments, congress_signals, shortlist,
   442	            )
   443	            text_body = self._create_scan_text_fallback(
   444	                buy_signals, sell_signals, spy_analysis, top_n, top20, shortlist,
   445	            )
   446	
   447	            msg.attach(MIMEText(text_body, 'plain'))
   448	            msg.attach(MIMEText(html_body, 'html'))
   449	
   450	            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
   451	            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
   452	                server.starttls()
   453	                server.login(self.email_from, self.email_password)
   454	
   455	                recipients = [r.strip() for r in self.email_to.split(',')]
   456	                server.sendmail(self.email_from, recipients, msg.as_string())
   457	
   458	            logger.info(f"✓ Scan report email sent to {self.email_to}")
   459	            return True
   460	
   461	        except smtplib.SMTPAuthenticationError:
   462	            logger.error("SMTP authentication failed. Check email credentials.")
   463	            return False
   464	        except smtplib.SMTPException as e:
   465	            logger.error(f"SMTP error: {e}")
   466	            return False
   467	        except Exception as e:
   468	            logger.error(f"Failed to send scan report email: {e}")
   469	            return False
   470	
   120	              for ticker, timestamp in updates[:10]:
   121	                  dt = datetime.fromisoformat(timestamp)
   122	                  formatted = dt.strftime("%Y-%m-%d %H:%M")
   123	                  print(f"  {ticker}: {formatted}")
   124	          except Exception as e:
   125	              print(f"Could not read metadata: {e}")
   126	          PYTHON_SCRIPT
   127	          else
   128	            echo "No metadata file found"
   129	          fi
   130	
   131	      - name: Commit updated fundamental cache
   132	        id: commit
   133	        run: |
   134	          git config --local user.email "github-actions[bot]@users.noreply.github.com"
   135	          git config --local user.name "github-actions[bot]"
   136	
   137	          # Add fundamental cache directory, plus the LLM agents' logged output
   138	          # (data/fundamentals_audit/, data/catalyst_sentiment/, data/congress_trades/)
   139	          # — these need to persist past this ephemeral runner so they can accumulate
   140	          # into a real point-in-time history for the walk-forward backtest to eventually use.
   141	          git add data/fundamentals_cache/
   142	          git add data/fundamentals_audit/ 2>/dev/null || true
   143	          git add data/catalyst_sentiment/ 2>/dev/null || true
   144	          git add data/congress_trades/ 2>/dev/null || true
   145	
   146	          # Also commit the day's Top 20 pool + Top 5 shortlist (top20_latest.json,
   147	          # shortlist_latest.json) and scan report — this is what actually reaches
   148	          # the local GUI dashboard (dashboard.py) after a `git pull`, so the same
   149	          # picks that went out by email are also visible there.
   150	          git add data/daily_scans/ 2>/dev/null || true
   151	
   152	          # Check if there are changes
   153	          if git diff --staged --quiet; then
   154	            echo "No fundamental cache changes to commit"
   155	            echo "has_changes=false" >> $GITHUB_OUTPUT
   156	          else
   157	            CHANGED_FILES=$(git diff --staged --name-only | wc -l)
   158	            echo "Committing $CHANGED_FILES updated fundamental files"
   159	            git commit -m "chore: update fundamental cache ($CHANGED_FILES stocks) - ${{ steps.date.outputs.date }}"
   160	            echo "has_changes=true" >> $GITHUB_OUTPUT
   161	          fi
   162	
   163	      - name: Push changes
   164	        if: steps.commit.outputs.has_changes == 'true'
   165	        uses: ad-m/github-push-action@v0.8.0
   166	        with:
   167	          github_token: ${{ secrets.GITHUB_TOKEN }}
   168	          branch: ${{ github.ref }}
   169	
   170	      - name: Upload screening results
   171	        if: always()
   172	        uses: actions/upload-artifact@v4
   173	        with:
   174	          name: screening-results-${{ steps.date.outputs.date }}
   175	          path: |

exec
/bin/zsh -lc "nl -ba static/js/dashboard.js | sed -n '400,620p'; nl -ba static/js/dashboard.js | sed -n '830,930p'; nl -ba src/analysis/position_manager.py | sed -n '340,410p'; nl -ba scripts/daily_scanner.sh" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
   400	    const chartId = `short-chart-${s.ticker}`;
   401	    return `
   402	      <div class="pick-card ${!s.passed_filters ? 'backfilled' : ''}">
   403	        <div class="pick-rank">#${i + 1}</div>
   404	        <div class="pick-header">
   405	          <span class="ticker">${s.ticker}</span>
   406	          <span id="${chartId}-slot"></span>
   407	        </div>
   408	        <div class="pick-scores">
   409	          <div class="score-block"><div class="label">Composite</div><div class="value">${s.composite_score ?? '-'}</div></div>
   410	          <div class="score-block"><div class="label">Base Score</div><div class="value">${s.combined_score ?? s.score ?? '-'}</div></div>
   411	        </div>
   412	        <div style="margin-bottom:10px"><span id="momentum-slot-${s.ticker}"></span></div>
   413	        ${backfillNote}
   414	        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
   415	        ${fidelityLink(s.ticker, 'Buy on Fidelity', 'buy')}
   416	        <div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
   417	      </div>`;
   418	  }).join('');
   419	
   420	  content.innerHTML = `
   421	    <div class="source-note email">
   422	      <b>This is what your daily email sends.</b> Same 5 picks, same links — the email is just a snapshot of this page.
   423	    </div>
   424	    <div class="shortlist-grid">${cards}</div>
   425	    <div id="shortlistNews" style="margin-top:24px"></div>`;
   426	
   427	  loadShortlistCharts(tickers);
   428	  loadShortlistNews(tickers);
   429	  loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap));
   430	  _startLive(() => {
   431	    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
   432	    _liveGuarded('shortlist-news', () => loadShortlistNews(tickers, true));
   433	    _liveGuarded('shortlist-momentum', () => loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap)));
   434	  });
   435	}
   436	
   437	let _shortlistPrices = {};
   438	let _marketTop20Tickers = [];
   439	
   440	function _shortlistSeries(ticker) {
   441	  const h = _shortlistPrices[ticker];
   442	  return h && h.length ? { history: h, entry: null, stop: null } : null;
   443	}
   444	
   445	async function loadShortlistCharts(tickers, silent) {
   446	  if (!tickers.length) return;
   447	  await startJob('price-history', { tickers, group: 'shortlist' }, async (st) => {
   448	    if (st.status !== 'success') return;
   449	    const data = await fetchJSON('/api/price-history/shortlist');
   450	    _shortlistPrices = data.prices || {};
   451	
   452	    if (!silent) {
   453	      // First load: drop a chart button into each card that actually has history.
   454	      tickers.forEach(ticker => {
   455	        const slot = document.getElementById(`short-chart-${ticker}-slot`);
   456	        if (slot && _shortlistPrices[ticker] && _shortlistPrices[ticker].length) {
   457	          slot.innerHTML = chartToggleButtonHTML(`short-chart-${ticker}`);
   458	        }
   459	      });
   460	      wireChartToggles(content, _shortlistSeries, 'short-chart-');
   461	    } else {
   462	      // Live refresh: buttons already exist — just repaint whichever are open.
   463	      refreshOpenCharts(_shortlistSeries, 'short-chart-');
   464	    }
   465	  });
   466	}
   467	
   468	async function loadShortlistNews(tickers, silent) {
   469	  const el = document.getElementById('shortlistNews');
   470	  if (!el) return;
   471	  if (!silent) {
   472	    el.innerHTML = _newsSectionHTML('shortlist', 'News on your shortlist', 'loading');
   473	  }
   474	  await _loadNewsGroup('shortlist', tickers, 'No shortlist yet.', silent);
   475	}
   476	
   477	function renderTop20Table(top20) {
   478	  if (!top20.length) return '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan from the Full Scan page.</p></div>';
   479	  const rows = top20.map((s, i) => {
   480	    const links = (s.why_links || []).slice(0, 3).map(l =>
   481	      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
   482	    ).join('');
   483	    return `<tr>
   484	      <td>#${i + 1}</td>
   485	      <td><span class="ticker">${s.ticker}</span></td>
   486	      <td><span class="score-num">${s.combined_score ?? s.score ?? '-'}</span></td>
   487	      <td><span id="momentum-slot-${s.ticker}"></span></td>
   488	      <td>${redditCell(s.reddit_mentions_24h)}</td>
   489	      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
   490	      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
   491	    </tr>`;
   492	  }).join('');
   493	  return `
   494	    <div class="card">
   495	      <h2>Top 20 — Combined Pool</h2>
   496	      <div style="overflow-x:auto"><table class="signal-table">
   497	        <thead><tr><th>#</th><th>Ticker</th><th>Combined Score</th><th>Momentum</th><th>Reddit</th><th>Why it's moving</th><th>Trade</th></tr></thead>
   498	        <tbody>${rows}</tbody>
   499	      </table></div>
   500	    </div>`;
   501	}
   502	
   503	// --- View: Market (today's Top 20 / Buy / Sell / regime) ---------------
   504	
   505	async function renderMarketView() {
   506	  const scans = await fetchJSON('/api/scans');
   507	  if (_currentView !== 'market') return; // navigated away before this resolved
   508	  if (!scans.length) {
   509	    content.innerHTML = '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan to get started.</p></div>';
   510	    return;
   511	  }
   512	  content.innerHTML = `
   513	    <div class="source-note email">
   514	      <b>This is the full pool your email's picks are drawn from.</b> Buy/Sell Signals and the Top 20 table
   515	      here are the same lists that get emailed (capped at 15 rows there; everything's shown here) — the
   516	      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
   517	    </div>
   518	    <div style="margin-bottom:16px">
   519	      <select class="scan-select" id="scanSelect"></select>
   520	    </div>
   521	    <div id="marketBody"></div>
   522	    <div id="newsSections" style="margin-top:24px"></div>`;
   523	  const sel = document.getElementById('scanSelect');
   524	  scans.forEach(s => {
   525	    const opt = document.createElement('option');
   526	    opt.value = s.path;
   527	    opt.textContent = s.date.replace('_', ' ');
   528	    sel.appendChild(opt);
   529	  });
   530	  sel.addEventListener('change', () => loadMarketScan(sel.value));
   531	  loadMarketScan(scans[0].path);
   532	  loadMarketNews();
   533	  _startLive(() => {
   534	    _liveGuarded('market-news', () => loadMarketNews(true));
   535	    _liveGuarded('market-momentum', () => loadMomentumStatus(
   536	      _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
   537	    ));
   538	  });
   539	}
   540	
   541	async function loadMarketNews(silent) {
   542	  const el = document.getElementById('newsSections');
   543	  if (!el) return; // navigated away before this resolved
   544	  if (!silent) {
   545	    el.innerHTML = _newsSectionHTML('positions', 'News on your positions', 'loading') +
   546	                    _newsSectionHTML('buy', "News on what the scanner's telling you to buy", 'loading');
   547	  }
   548	
   549	  const [positionsData, top20Data] = await Promise.all([
   550	    fetchJSON('/api/positions'), fetchJSON('/api/top20'),
   551	  ]);
   552	  const positionTickers = (positionsData.position_analyses || []).map(a => a.ticker);
   553	  const buyTickers = (top20Data.top20 || []).slice(0, 8).map(s => s.ticker);
   554	
   555	  await Promise.all([
   556	    _loadNewsGroup('positions', positionTickers, 'Upload your positions in the Positions tab to see news for them here.', silent),
   557	    _loadNewsGroup('buy', buyTickers, 'No Top 20 pool yet — run a scan from the Full Scan tab first.', silent),
   558	  ]);
   559	}
   560	
   561	function _newsSectionHTML(group, title, bodyHTML) {
   562	  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
   563	}
   564	
   565	async function _loadNewsGroup(group, tickers, emptyMsg, silent) {
   566	  const bodyEl = document.getElementById(`news-${group}-body`);
   567	  if (!bodyEl) return; // navigated away before this resolved
   568	  if (!tickers.length) {
   569	    bodyEl.innerHTML = `<div style="color:var(--muted);font-size:13px">${emptyMsg}</div>`;
   570	    return;
   571	  }
   572	  if (!silent) {
   573	    bodyEl.innerHTML = '<div style="color:var(--muted);font-size:13px"><span class="spinner"></span> Fetching real headlines…</div>';
   574	  }
   575	
   576	  await startJob('news', { tickers, group }, async (st) => {
   577	    const el = document.getElementById(`news-${group}-body`);
   578	    if (!el) return; // navigated away mid-job
   579	    if (st.status === 'success') {
   580	      const data = await fetchJSON(`/api/news/${group}`);
   581	      el.innerHTML = _renderNewsGroupHTML(data.news || {});
   582	    } else if (!silent && (st.status === 'error' || st.status === 'stopped')) {
   583	      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
   584	    }
   585	  });
   586	}
   587	
   588	function _renderNewsGroupHTML(newsByTicker) {
   589	  const tickers = Object.keys(newsByTicker);
   590	  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
   591	  return `<div class="news-ticker-grid">${tickers.map(ticker => {
   592	    const items = newsByTicker[ticker] || [];
   593	    const list = items.length
   594	      ? items.map(h => `
   595	          <a href="${h.url || '#'}" target="_blank" rel="noopener" class="news-headline">
   596	            <div class="news-headline-title">${h.title}</div>
   597	            <div class="news-headline-meta">${h.publisher || 'Unknown source'}${h.pub_date ? ' · ' + new Date(h.pub_date).toLocaleDateString() : ''}</div>
   598	          </a>`).join('')
   599	      : '<div style="color:var(--muted);font-size:12px">No recent headlines.</div>';
   600	    return `<div class="news-ticker-block"><div class="ticker" style="margin-bottom:6px">${ticker}</div>${list}</div>`;
   601	  }).join('')}</div>`;
   602	}
   603	
   604	async function loadMarketScan(path) {
   605	  const [scan, top20] = await Promise.all([
   606	    fetchJSON('/api/scan?path=' + encodeURIComponent(path)),
   607	    fetchJSON('/api/top20'),
   608	  ]);
   609	  if (_currentView !== 'market') return; // navigated away before this resolved
   610	  if (scan.error) {
   611	    document.getElementById('marketBody').innerHTML = '<div class="no-data"><h2>No scan data</h2></div>';
   612	    return;
   613	  }
   614	  pageMeta.textContent = `${scan.scan_date} · ${scan.stats.analyzed || '?'} analyzed · ${scan.regime}`;
   615	
   616	  const buyCount = scan.stats.buy_count ?? scan.buy_signals.length;
   617	  const sellCount = scan.stats.sell_count ?? scan.sell_signals.length;
   618	  const topScore = scan.buy_signals.length ? scan.buy_signals[0].score : '-';
   619	  const regimeClass = scan.regime.includes('RISK-ON') ? 'risk-on' : scan.regime.includes('RISK-OFF') ? 'risk-off' : 'transitional';
   620	
   830	  const summary = data.summary || {};
   831	  const analyses = data.position_analyses || [];
   832	  const resultsEl = document.getElementById('pos-results');
   833	  if (!resultsEl) return;
   834	
   835	  if (!analyses.length) {
   836	    resultsEl.innerHTML = '<div class="no-data"><h2>No positions found</h2></div>';
   837	    return;
   838	  }
   839	
   840	  const cards = analyses.map(a => {
   841	    const meta = POSITION_ACTION_LABELS[a.action] || { label: a.action || 'hold', cls: 'neutral' };
   842	    const gainColor = a.current_gain_pct >= 0 ? 'var(--green)' : 'var(--red)';
   843	    const gainSign = a.current_gain_pct >= 0 ? '+' : '';
   844	
   845	    let extra = '';
   846	    if (a.recommended_stop) {
   847	      extra += `<div class="agent-badge-sub">Recommended stop: $${a.recommended_stop.toFixed(2)}</div>`;
   848	    }
   849	    if (a.add_on_signal) {
   850	      extra += `<div class="agent-badge-sub" style="color:var(--green);margin-top:6px">Add-on candidate — ${a.add_on_rationale}</div>`;
   851	    }
   852	    (a.warnings || []).forEach(w => {
   853	      extra += `<div class="agent-badge-sub" style="color:var(--yellow)">${w}</div>`;
   854	    });
   855	
   856	    const chartId = `pos-chart-${a.ticker}`;
   857	    const hasHistory = a.price_history && a.price_history.length;
   858	
   859	    return `
   860	      <div class="pick-card">
   861	        <div class="pick-header">
   862	          <span class="ticker">${a.ticker}</span>
   863	          ${hasHistory ? chartToggleButtonHTML(chartId) : ''}
   864	          <span class="badge ${meta.cls}" style="margin-left:${hasHistory ? '8px' : 'auto'}">${meta.label}</span>
   865	        </div>
   866	        <div class="pick-scores">
   867	          <div class="score-block"><div class="label">Entry</div><div class="value">$${a.entry_price.toFixed(2)}</div></div>
   868	          <div class="score-block"><div class="label">Current</div><div class="value">$${a.current_price.toFixed(2)}</div></div>
   869	          <div class="score-block"><div class="label">Gain</div><div class="value" style="color:${gainColor}">${gainSign}${a.current_gain_pct}%</div></div>
   870	        </div>
   871	        <div style="margin-bottom:10px"><span id="momentum-slot-${a.ticker}"></span></div>
   872	        ${extra}
   873	        ${hasHistory ? `<div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>` : ''}
   874	      </div>`;
   875	  }).join('');
   876	
   877	  resultsEl.innerHTML = `
   878	    <div class="stats-row">
   879	      <div class="stat-card"><div class="label">Positions</div><div class="value">${summary.total_positions || 0}</div></div>
   880	      <div class="stat-card yellow"><div class="label">Need Adjustment</div><div class="value">${summary.positions_need_adjustment || 0}</div></div>
   881	      <div class="stat-card green"><div class="label">Add-On Candidates</div><div class="value">${summary.add_on_candidates || 0}</div></div>
   882	      <div class="stat-card ${(summary.average_gain_pct || 0) >= 0 ? 'green' : 'red'}"><div class="label">Avg Gain</div><div class="value">${(summary.average_gain_pct || 0) >= 0 ? '+' : ''}${summary.average_gain_pct || 0}%</div></div>
   883	    </div>
   884	    <div class="shortlist-grid">${cards}</div>`;
   885	
   886	  wireChartToggles(resultsEl, (ticker) => {
   887	    const a = analyses.find(x => x.ticker === ticker);
   888	    return a ? { history: a.price_history, entry: a.entry_price, stop: a.recommended_stop } : null;
   889	  }, 'pos-chart-');
   890	
   891	  const posTickers = analyses.map(a => a.ticker);
   892	  loadMomentumStatus(posTickers, 'positions', (statusMap) => paintMomentumSlots(posTickers, statusMap));
   893	}
   894	
   895	// --- View: Backtests ------------------------------------------------------
   896	
   897	async function renderBacktestsView() {
   898	  const history = await fetchJSON('/api/backtest/history');
   899	  if (_currentView !== 'backtests') return; // navigated away before this resolved
   900	  content.innerHTML = `
   901	    <div class="source-note historical">
   902	      <b>This is a report card, not your email.</b> It shows how the screener's scoring would have performed
   903	      on real historical stocks and prices — win rate, returns, drawdown. It doesn't contain today's picks;
   904	      for those, see <a href="#/shortlist" style="color:var(--blue)">Shortlist</a> or
   905	      <a href="#/market" style="color:var(--blue)">Market</a>. Run a fresh one from
   906	      <a href="#/run" style="color:var(--blue)">Run Simulation</a>.
   907	    </div>
   908	    <div style="margin-bottom:16px">
   909	      <select class="scan-select" id="backtestSelect">
   910	        <option value="">Latest</option>
   911	      </select>
   912	    </div>
   913	    <div id="backtestBody"></div>`;
   914	  const sel = document.getElementById('backtestSelect');
   915	  history.forEach(h => {
   916	    const opt = document.createElement('option');
   917	    opt.value = h.path;
   918	    opt.textContent = `${h.name} (${h.generated ? new Date(h.generated).toLocaleDateString() : '?'})`;
   919	    sel.appendChild(opt);
   920	  });
   921	  sel.addEventListener('change', () => loadBacktest(sel.value));
   922	  loadBacktest('');
   923	}
   924	
   925	async function loadBacktest(path) {
   926	  const [summaryData, tradesData] = await Promise.all([
   927	    path ? fetchJSON('/api/backtest/run?path=' + encodeURIComponent(path)) : fetchJSON('/api/backtest/latest'),
   928	    fetchJSON('/api/backtest/trades' + (path ? '?path=' + encodeURIComponent(path) : '')),
   929	  ]);
   930	  if (_currentView !== 'backtests') return; // navigated away before this resolved
   340	        if not positions:
   341	            return {
   342	                'position_analyses': [],
   343	                'summary': {'total_positions': 0},
   344	                'urgent_actions': []
   345	            }
   346	
   347	        entry_dates = entry_dates or {}
   348	        analyses = []
   349	
   350	        for pos in positions:
   351	            ticker = pos['ticker']
   352	            entry_date = entry_dates.get(ticker)
   353	
   354	            logger.info(f"Analyzing {ticker}: entry=${pos['average_buy_price']:.2f}, current=${pos['current_price']:.2f}")
   355	
   356	            analysis = self.analyze_position(
   357	                ticker=ticker,
   358	                entry_price=pos['average_buy_price'],
   359	                current_price=pos['current_price'],
   360	                entry_date=entry_date
   361	            )
   362	
   363	            analysis['quantity'] = pos['quantity']
   364	            analyses.append(analysis)
   365	
   366	        # Generate summary
   367	        total_positions = len(analyses)
   368	        positions_to_adjust = sum(1 for a in analyses if a['should_adjust_stop'])
   369	        short_term_positions = sum(
   370	            1 for a in analyses if a['tax_treatment'] == 'short_term'
   371	        )
   372	        long_term_positions = sum(
   373	            1 for a in analyses if a['tax_treatment'] == 'long_term'
   374	        )
   375	
   376	        avg_gain = sum(a['current_gain_pct'] for a in analyses) / total_positions if total_positions > 0 else 0
   377	
   378	        add_on_candidates = sum(1 for a in analyses if a.get('add_on_signal'))
   379	
   380	        summary = {
   381	            'total_positions': total_positions,
   382	            'positions_need_adjustment': positions_to_adjust,
   383	            'add_on_candidates': add_on_candidates,
   384	            'short_term_positions': short_term_positions,
   385	            'long_term_positions': long_term_positions,
   386	            'average_gain_pct': round(avg_gain, 2)
   387	        }
   388	
   389	        # Urgent actions (Phase 3/4 warnings, big winners, breakdowns)
   390	        urgent = []
   391	        for analysis in analyses:
   392	            if analysis['warnings']:
   393	                urgent.append({
   394	                    'ticker': analysis['ticker'],
   395	                    'reason': analysis['warnings'],
   396	                    'current_gain': analysis['current_gain_pct']
   397	                })
   398	            elif analysis.get('action') in ['take_partial_and_trail', 'take_partial_and_trail_tight']:
   399	                urgent.append({
   400	                    'ticker': analysis['ticker'],
   401	                    'reason': 'Big winner - consider taking partial profits',
   402	                    'current_gain': analysis['current_gain_pct']
   403	                })
   404	
   405	        return {
   406	            'position_analyses': analyses,
   407	            'summary': summary,
   408	            'urgent_actions': urgent,
   409	            'timestamp': datetime.now()
   410	        }
     1	#!/bin/bash
     2	# Daily market scanner - runs full scan of all US stocks
     3	# Designed to run at 6:30 AM EST daily via cron
     4	
     5	# Configuration
     6	SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
     7	LOG_DIR="$SCRIPT_DIR/data/logs"
     8	LOG_FILE="$LOG_DIR/daily_scan_$(date +%Y%m%d).log"
     9	
    10	# Create log directory
    11	mkdir -p "$LOG_DIR"
    12	
    13	# Log start
    14	echo "========================================" | tee -a "$LOG_FILE"
    15	echo "Daily Market Scan Started" | tee -a "$LOG_FILE"
    16	echo "Time: $(date '+%Y-%m-%d %H:%M:%S %Z')" | tee -a "$LOG_FILE"
    17	echo "========================================" | tee -a "$LOG_FILE"
    18	
    19	# Change to script directory
    20	cd "$SCRIPT_DIR"
    21	
    22	# Activate virtual environment
    23	source venv/bin/activate
    24	
    25	# Run the scan with resume capability (in case of previous interruption)
    26	python run_full_market_scan.py --resume 2>&1 | tee -a "$LOG_FILE"
    27	
    28	# Log completion
    29	echo "========================================" | tee -a "$LOG_FILE"
    30	echo "Daily Market Scan Completed" | tee -a "$LOG_FILE"
    31	echo "Time: $(date '+%Y-%m-%d %H:%M:%S %Z')" | tee -a "$LOG_FILE"
    32	echo "========================================" | tee -a "$LOG_FILE"
    33	
    34	# Keep only last 30 days of logs
    35	find "$LOG_DIR" -name "daily_scan_*.log" -mtime +30 -delete
    36	
    37	# Deactivate virtual environment
    38	deactivate

exec
/bin/zsh -lc 'nl -ba requirements.txt; nl -ba mac_app/setup.py; nl -ba scripts/run_quant_engine.py; nl -ba src/data/__init__.py; nl -ba src/screening/__init__.py' in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
     1	yfinance>=0.2.66
     2	pandas>=2.2.0
     3	sqlalchemy>=2.0.20
     4	psycopg2-binary>=2.9.9
     5	python-dotenv>=1.0.0
     6	pytest>=7.4.0
     7	pytest-mock>=3.11.1
     8	requests>=2.31.0
     9	slack-sdk>=3.26.0
    10	pyyaml>=6.0
    11	numpy>=1.24.0
    12	robin-stocks>=3.0.0  # Read-only position tracking (optional)
    13	praw>=7.7.0  # Read-only Reddit ticker-mention tracking (optional)
    14	anthropic>=0.120.0  # Fundamentals Auditor + News/Catalyst Sentiment agents (optional, needs ANTHROPIC_API_KEY)
    15	flask>=3.0.0  # Local GUI dashboard (dashboard.py)
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
     1	#!/usr/bin/env python3
     2	"""Run the Quant Analysis & Execution Engine.
     3	
     4	This script loads the stock universe from config.yaml and runs the complete
     5	Phase-based screening system.
     6	
     7	Usage:
     8	    python run_quant_engine.py
     9	    python run_quant_engine.py --tickers AAPL MSFT GOOGL
    10	    python run_quant_engine.py --config custom_config.yaml
    11	"""
    12	
    13	import argparse
    14	import logging
    15	import sys
    16	from datetime import datetime
    17	from pathlib import Path
    18	
    19	import yaml
    20	
    21	from src.screening.quant_engine import QuantAnalysisEngine
    22	
    23	logging.basicConfig(
    24	    level=logging.INFO,
    25	    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    26	)
    27	logger = logging.getLogger(__name__)
    28	
    29	
    30	def load_config(config_path: str = 'config.yaml') -> dict:
    31	    """Load configuration from YAML file.
    32	
    33	    Args:
    34	        config_path: Path to config file
    35	
    36	    Returns:
    37	        Config dict
    38	    """
    39	    try:
    40	        with open(config_path, 'r') as f:
    41	            config = yaml.safe_load(f)
    42	        logger.info(f"Loaded config from {config_path}")
    43	        return config
    44	    except Exception as e:
    45	        logger.error(f"Error loading config: {e}")
    46	        return {}
    47	
    48	
    49	def save_results(report: str, output_dir: str = './data/results'):
    50	    """Save screening results to file.
    51	
    52	    Args:
    53	        report: Report string
    54	        output_dir: Output directory
    55	    """
    56	    try:
    57	        # Create output directory
    58	        Path(output_dir).mkdir(parents=True, exist_ok=True)
    59	
    60	        # Generate filename with timestamp
    61	        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    62	        filename = f"quant_screen_{timestamp}.txt"
    63	        filepath = Path(output_dir) / filename
    64	
    65	        # Save report
    66	        with open(filepath, 'w') as f:
    67	            f.write(report)
    68	
    69	        logger.info(f"Results saved to {filepath}")
    70	        return str(filepath)
    71	
    72	    except Exception as e:
    73	        logger.error(f"Error saving results: {e}")
    74	        return None
    75	
    76	
    77	def main():
    78	    """Main entry point."""
    79	    parser = argparse.ArgumentParser(
    80	        description='Run Quant Analysis & Execution Engine'
    81	    )
    82	    parser.add_argument(
    83	        '--config',
    84	        type=str,
    85	        default='config.yaml',
    86	        help='Path to config file (default: config.yaml)'
    87	    )
    88	    parser.add_argument(
    89	        '--tickers',
    90	        nargs='+',
    91	        help='Override config with specific tickers'
    92	    )
    93	    parser.add_argument(
    94	        '--no-save',
    95	        action='store_true',
    96	        help='Do not save results to file'
    97	    )
    98	    parser.add_argument(
    99	        '--cache-dir',
   100	        type=str,
   101	        default='./data/cache',
   102	        help='Cache directory (default: ./data/cache)'
   103	    )
   104	
   105	    args = parser.parse_args()
   106	
   107	    # Load config
   108	    config = load_config(args.config)
   109	
   110	    # Get stock universe
   111	    if args.tickers:
   112	        tickers = args.tickers
   113	        logger.info(f"Using command-line tickers: {tickers}")
   114	    elif config and 'stock_universe' in config:
   115	        tickers = config['stock_universe']
   116	        logger.info(f"Using {len(tickers)} tickers from config")
   117	    else:
   118	        logger.error("No stock universe specified")
   119	        sys.exit(1)
   120	
   121	    # Initialize engine
   122	    engine = QuantAnalysisEngine(cache_dir=args.cache_dir)
   123	
   124	    # Run screening
   125	    try:
   126	        logger.info("Starting Quant Analysis Engine...")
   127	        report = engine.run(tickers)
   128	
   129	        # Print report
   130	        print(report)
   131	
   132	        # Save to file if requested
   133	        if not args.no_save:
   134	            output_dir = config.get('output', {}).get('output_dir', './data/results')
   135	            save_results(report, output_dir)
   136	
   137	    except KeyboardInterrupt:
   138	        logger.info("\nScreening interrupted by user")
   139	        sys.exit(0)
   140	    except Exception as e:
   141	        logger.error(f"Error running engine: {e}", exc_info=True)
   142	        sys.exit(1)
   143	
   144	
   145	if __name__ == '__main__':
   146	    main()
     1	"""Data fetching and storage modules for stock screener."""
     2	
     3	from .fetcher import YahooFinanceFetcher
     4	from .storage import StockDatabase
     5	from .quality import DataQualityChecker, TickerQualityReport, DataQualityIssue, IssueSeverity
     6	
     7	__all__ = [
     8	    "YahooFinanceFetcher",
     9	    "StockDatabase",
    10	    "DataQualityChecker",
    11	    "TickerQualityReport",
    12	    "DataQualityIssue",
    13	    "IssueSeverity"
    14	]
     1	"""Stock screening module for identifying undervalued stocks at support levels."""
     2	
     3	from .screener import (
     4	    calculate_value_score,
     5	    detect_support_levels,
     6	    calculate_support_score,
     7	    screen_candidates
     8	)
     9	from .indicators import (
    10	    calculate_rsi,
    11	    calculate_sma,
    12	    calculate_ema,
    13	    detect_volume_spike,
    14	    find_swing_lows
    15	)
    16	
    17	__all__ = [
    18	    "calculate_value_score",
    19	    "detect_support_levels",
    20	    "calculate_support_score",
    21	    "screen_candidates",
    22	    "calculate_rsi",
    23	    "calculate_sma",
    24	    "calculate_ema",
    25	    "detect_volume_spike",
    26	    "find_swing_lows"
    27	]

exec
/bin/zsh -lc 'nl -ba mac_app/README.md; rg -n "pywebview|webview" README.md QUICK_START.md START_HERE.md requirements.txt mac_app' in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
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
mac_app/README.md:3:A standalone macOS app wrapper around `dashboard.py`. It bundles its own Python + Flask + pywebview runtime (via py2app) so it can be double-clicked from Applications/Dock/Launchpad without needing a terminal or the project's venv activated — and it opens in its own native window (via `pywebview`, using macOS's WebKit), not a browser tab.
mac_app/README.md:5:`mac_app/main.py` runs the real `dashboard.py`'s Flask app in a background thread, then opens a `pywebview` window pointed at it — no `webbrowser.open()` call in this path at all, so launching/relaunching the app never pops open your default browser.
mac_app/README.md:7:It still operates on the real project checkout on disk (`~/Desktop/stock-screener` by default, override with the `STOCK_SCREENER_ROOT` env var if you move the folder) — data files, git pull/push (the Sync button), and running backtest scripts all go through the real repo and its own `venv/bin/python`, exactly like running `python dashboard.py` normally. The app bundle itself only needs to run Flask + pywebview; the heavier dependencies (pandas, yfinance, etc.) are never bundled since `dashboard.py` shells out to scripts rather than importing them directly.
mac_app/README.md:14:venv/bin/pip install py2app pywebview   # one-time
mac_app/README.md:22:On this machine, the venv's Python is a conda-based interpreter, and several of its C extensions link against `@rpath/lib*.dylib` copies that live in `~/miniconda3/lib/` rather than a system path — py2app's dependency walker doesn't reliably follow those. Two hit so far: `ctypes` needs `libffi.8.dylib`; `ssl` (imported by `pywebview.http`) needs `libssl.3.dylib` + `libcrypto.3.dylib`. If the built app fails silently (or shows an `ImportError: ... Library not loaded` when run directly from the terminal — see Debugging below), fix each missing one the same way:
mac_app/setup.py:9:Bundles Flask + its own dependencies, plus pywebview and its macOS backend
mac_app/setup.py:31:        'webview', 'objc', 'Cocoa', 'WebKit', 'Quartz', 'Security', 'UniformTypeIdentifiers',
mac_app/main.py:5:opens it in its own native window via pywebview (no browser tabs/address bar)
mac_app/main.py:11:this .app. The bundle only carries a self-contained Python + Flask + pywebview
mac_app/main.py:20:# This process loads Cocoa/WebKit (via pywebview below), which Apple documents
mac_app/main.py:26:# set before pywebview/webview is imported.
mac_app/main.py:57:import webview  # noqa: E402
mac_app/main.py:59:webview.create_window(
mac_app/main.py:63:webview.start()

exec
/bin/zsh -lc "git diff -- dashboard.py scripts/backtest_top3.py scripts/backtest_top3_monte_carlo.py scripts/walk_forward_backtest.py src/notifications/email_notifier.py manage_positions.py src/analysis/position_manager.py src/agents/catalyst_sentiment.py requirements.txt | sed -n '1,420p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
diff --git a/dashboard.py b/dashboard.py
index 00b6b449..c66930b1 100644
--- a/dashboard.py
+++ b/dashboard.py
@@ -12,25 +12,83 @@ import argparse
 import json
 import os
 import re
+import shutil
 import subprocess
 import sys
+import threading
+import time
+import uuid
 import webbrowser
-from datetime import datetime
 from pathlib import Path
 from threading import Timer
 
-from flask import Flask, jsonify, render_template_string, request
+from flask import Flask, jsonify, render_template, request
+
+# When bundled as a standalone .app (py2app sets sys.frozen), this file lives
+# inside the bundle's Resources folder, not the real project checkout — but
+# the dashboard always needs to read/write the real repo (git pull/push via
+# /api/sync, data/ files, and it shells out to the project's own venv to run
+# scripts). So PROJECT_ROOT deliberately does NOT follow __file__ when frozen;
+# it points at the real checkout instead, overridable via STOCK_SCREENER_ROOT
+# for anyone whose folder lives somewhere other than the default.
+if getattr(sys, "frozen", False):
+    PROJECT_ROOT = Path(os.environ.get("STOCK_SCREENER_ROOT", str(Path.home() / "Desktop" / "stock-screener"))).resolve()
+else:
+    PROJECT_ROOT = Path(__file__).parent.resolve()
+
+# py2app's own bootstrap chdir's the frozen process into the .app bundle's
+# Resources folder before this module even runs — wrong for us either way, we
+# always want PROJECT_ROOT. Setting it here (rather than passing cwd= on each
+# subprocess call below) is what keeps those calls eligible for macOS's safe
+# posix_spawn() path instead of fork()+exec() — see the comment in
+# _launch_job() for why that distinction matters for the packaged .app.
+os.chdir(str(PROJECT_ROOT))
+
+app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"), static_folder=str(PROJECT_ROOT / "static"))
 
-app = Flask(__name__)
-
-PROJECT_ROOT = Path(__file__).parent.resolve()
 SCAN_DIR = PROJECT_ROOT / "data" / "daily_scans"
+BACKTEST_DIR = PROJECT_ROOT / "data" / "backtest_history"
+ADHOC_DIR = PROJECT_ROOT / "data" / "adhoc_simulations"
+POSITIONS_CSV = PROJECT_ROOT / "data" / "positions_latest.csv"
 VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"
 
 
+def _venv_python():
+    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
+
+
+# The plain "git" on PATH (/usr/bin/git) is actually a stub that shells out to
+# `xcodebuild -find git` to locate the real binary — on a machine with a
+# broken/corrupted Xcode.app (as opposed to just the separate, lighter-weight
+# Command Line Tools), that stub fails with an unrelated-looking dlopen error
+# and git (and the Sync button) stops working entirely, even though a real,
+# working git binary is usually still sitting right here. Preferring it
+# sidesteps the broken xcodebuild lookup rather than depending on it.
+_CLT_GIT = Path("/Library/Developer/CommandLineTools/usr/bin/git")
+
+
+def _git_binary():
+    if _CLT_GIT.exists():
+        return str(_CLT_GIT)
+    return shutil.which("git") or "/usr/bin/git"
+
+
+def _read_json(path, default):
+    """Load a JSON file, falling back to `default` if it's missing/unreadable
+    — every read-only route uses this so "no data yet" is always a normal 200
+    response, never a bare error."""
+    path = Path(path)
+    if not path.exists():
+        return default
+    try:
+        return json.loads(path.read_text(encoding="utf-8"))
+    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
+        return default
+
+
 def parse_scan_file(filepath):
     """Parse a scan .txt file into structured data."""
-    text = Path(filepath).read_text()
+    text = Path(filepath).read_text(encoding="utf-8")
 
     data = {
         "scan_date": "",
@@ -207,496 +265,411 @@ def get_scan_files():
     return [{"name": f.stem, "path": str(f), "date": f.stem.replace("optimized_scan_", "")} for f in files]
 
 
-DASHBOARD_HTML = """
-<!DOCTYPE html>
-<html lang="en">
-<head>
-<meta charset="UTF-8">
-<meta name="viewport" content="width=device-width, initial-scale=1.0">
-<title>Stock Screener Dashboard</title>
-<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
-<style>
-  :root {
-    --bg: #0f1117;
-    --surface: #1a1d27;
-    --border: #2a2d3a;
-    --text: #e4e6eb;
-    --muted: #8b8fa3;
-    --green: #22c55e;
-    --red: #ef4444;
-    --yellow: #eab308;
-    --blue: #3b82f6;
-    --purple: #a855f7;
-  }
-  * { margin: 0; padding: 0; box-sizing: border-box; }
-  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
-
-  .header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
-  .header h1 { font-size: 20px; font-weight: 600; }
-  .header .meta { color: var(--muted); font-size: 13px; }
-  .header .actions { display: flex; gap: 10px; }
-
-  .btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px; transition: all 0.15s; }
-  .btn:hover { border-color: var(--blue); }
-  .btn.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
-  .btn.primary:hover { opacity: 0.9; }
-  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
-
-  .container { max-width: 1400px; margin: 0 auto; padding: 24px; }
-
-  .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
-  .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
-  .stat-card .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
-  .stat-card .value { font-size: 28px; font-weight: 700; }
-  .stat-card .sub { color: var(--muted); font-size: 12px; margin-top: 4px; }
-  .stat-card.green .value { color: var(--green); }
-  .stat-card.red .value { color: var(--red); }
-  .stat-card.blue .value { color: var(--blue); }
-  .stat-card.yellow .value { color: var(--yellow); }
-
-  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
-  @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
-
-  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
-  .card h2 { font-size: 15px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
-
-  .regime-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
-  .regime-badge.risk-on { background: rgba(34,197,94,0.15); color: var(--green); }
-  .regime-badge.risk-off { background: rgba(239,68,68,0.15); color: var(--red); }
-  .regime-badge.transitional { background: rgba(234,179,8,0.15); color: var(--yellow); }
-
-  .chart-wrap { position: relative; height: 250px; }
-
-  .signal-table { width: 100%; border-collapse: collapse; }
-  .signal-table th { text-align: left; padding: 10px 12px; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
-  .signal-table td { padding: 12px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: top; }
-  .signal-table tr:hover { background: rgba(59,130,246,0.04); }
-
-  .ticker { font-weight: 700; font-size: 14px; color: var(--blue); }
-  .score-bar { height: 6px; border-radius: 3px; background: var(--border); overflow: hidden; width: 80px; display: inline-block; vertical-align: middle; margin-left: 6px; }
-  .score-bar .fill { height: 100%; border-radius: 3px; }
-  .score-num { font-weight: 600; font-size: 13px; }
-
-  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
-  .badge.good { background: rgba(34,197,94,0.15); color: var(--green); }
-  .badge.extended { background: rgba(234,179,8,0.15); color: var(--yellow); }
-  .badge.poor { background: rgba(239,68,68,0.15); color: var(--red); }
-  .badge.critical { background: rgba(239,68,68,0.25); color: var(--red); }
-  .badge.high { background: rgba(239,68,68,0.15); color: var(--red); }
-  .badge.medium { background: rgba(234,179,8,0.15); color: var(--yellow); }
-
-  .reasons-list { list-style: none; padding: 0; margin-top: 4px; }
-  .reasons-list li { font-size: 11px; color: var(--muted); padding: 1px 0; }
-
-  .expand-btn { background: none; border: none; color: var(--blue); cursor: pointer; font-size: 11px; padding: 2px 0; }
-  .expand-btn:hover { text-decoration: underline; }
-
-  .trade-link { display: inline-flex; align-items: center; gap: 4px; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; white-space: nowrap; border: 1px solid transparent; }
-  .trade-link.buy { background: rgba(34,197,94,0.15); color: var(--green); }
-  .trade-link.buy:hover { background: rgba(34,197,94,0.28); }
-  .trade-link.sell { background: rgba(239,68,68,0.15); color: var(--red); }
-  .trade-link.sell:hover { background: rgba(239,68,68,0.28); }
-
-  .no-data { text-align: center; padding: 60px 20px; color: var(--muted); }
-  .no-data h2 { font-size: 18px; margin-bottom: 8px; color: var(--text); }
-
-  .scan-select { background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 6px; font-size: 13px; }
-
-  .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid var(--border); border-top-color: var(--blue); border-radius: 50%; animation: spin 0.6s linear infinite; margin-right: 6px; vertical-align: middle; }
-  @keyframes spin { to { transform: rotate(360deg); } }
-
-  .toast { position: fixed; bottom: 24px; right: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; font-size: 13px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); z-index: 100; transition: opacity 0.3s; }
-</style>
-</head>
-<body>
-
-<div class="header">
-  <div>
-    <h1>Stock Screener</h1>
-    <div class="meta" id="headerMeta">Loading...</div>
-  </div>
-  <div class="actions">
-    <select class="scan-select" id="scanSelect" onchange="loadScan(this.value)"></select>
-    <button class="btn" onclick="runScan(false)" id="testBtn">Test Scan (100)</button>
-    <button class="btn primary" onclick="runScan(true)" id="fullBtn">Full Scan</button>
-  </div>
-</div>
-
-<div class="container" id="content">
-  <div class="no-data" id="noData" style="display:none">
-    <h2>No scan data yet</h2>
-    <p>Run a test scan to get started</p>
-  </div>
-  <div id="dashboard" style="display:none">
-
-    <div class="stats-row" id="statsRow"></div>
-
-    <div class="grid-2">
-      <div class="card">
-        <h2>Market Breadth</h2>
-        <div class="chart-wrap"><canvas id="breadthChart"></canvas></div>
-      </div>
-      <div class="card">
-        <h2>SPY Regime</h2>
-        <div id="spyInfo"></div>
-      </div>
-    </div>
-
-    <div class="card" style="margin-bottom:16px" id="top20Card">
-      <h2 style="color:#a855f7">⭐ Top 20 — Combined Shortlist</h2>
-      <div style="color:var(--muted);font-size:12px;margin-top:-8px;margin-bottom:12px">
-        Technical/fundamental score first, re-ranked by Reddit buzz. Every entry already passed the full screen.
-      </div>
-      <div style="overflow-x:auto">
-        <table class="signal-table" id="top20Table">
-          <thead>
-            <tr>
-              <th>#</th>
-              <th>Ticker</th>
-              <th>Combined Score</th>
-              <th>Reddit</th>
-              <th>Why it's moving</th>
-              <th>Trade</th>
-            </tr>
-          </thead>
-          <tbody></tbody>
-        </table>
-      </div>
-    </div>
-
-    <div class="card" style="margin-bottom:16px">
-      <h2 style="color:var(--green)">Buy Signals</h2>
-      <div style="overflow-x:auto">
-        <table class="signal-table" id="buyTable">
-          <thead>
-            <tr>
-              <th>#</th>
-              <th>Ticker</th>
-              <th>Score</th>
-              <th>Entry</th>
-              <th>Stop Loss</th>
-              <th>R:R</th>
-              <th>RS</th>
-              <th>Reddit</th>
-              <th>Key Reasons</th>
-              <th>Trade</th>
-            </tr>
-          </thead>
-          <tbody></tbody>
-        </table>
-      </div>
-    </div>
-
-    <div class="card">
-      <h2 style="color:var(--red)">Sell Signals</h2>
-      <div style="overflow-x:auto">
-        <table class="signal-table" id="sellTable">
-          <thead>
-            <tr>
-              <th>#</th>
-              <th>Ticker</th>
-              <th>Score</th>
-              <th>Severity</th>
-              <th>Breakdown</th>
-              <th>Reddit</th>
-              <th>Reasons</th>
-              <th>Trade</th>
-            </tr>
-          </thead>
-          <tbody></tbody>
-        </table>
-      </div>
-    </div>
-
-  </div>
-</div>
-
-<script>
-let breadthChartInstance = null;
-
-async function loadScanList() {
-  const res = await fetch('/api/scans');
-  const scans = await res.json();
-  const sel = document.getElementById('scanSelect');
-  sel.innerHTML = '';
-  if (scans.length === 0) {
-    sel.innerHTML = '<option>No scans</option>';
-    document.getElementById('noData').style.display = '';
-    document.getElementById('dashboard').style.display = 'none';
-    return;
-  }
-  scans.forEach((s, i) => {
-    const opt = document.createElement('option');
-    opt.value = s.path;
-    opt.textContent = s.date.replace('_', ' ');
-    sel.appendChild(opt);
-  });
-  loadScan(scans[0].path);
-}
-
-async function loadScan(path) {
-  const res = await fetch('/api/scan?path=' + encodeURIComponent(path));
-  const data = await res.json();
-  if (data.error) {
-    document.getElementById('noData').style.display = '';
-    document.getElementById('dashboard').style.display = 'none';
-    return;
-  }
-  renderDashboard(data);
-  loadTop20();
-}
-
-async function loadTop20() {
-  const res = await fetch('/api/top20');
-  const data = await res.json();
-  renderTop20(data.top20 || []);
-}
-
-function renderTop20(top20) {
-  const card = document.getElementById('top20Card');
-  const body = document.querySelector('#top20Table tbody');
-  if (!top20 || top20.length === 0) {
-    card.style.display = 'none';
-    return;
-  }
-  card.style.display = '';
-  body.innerHTML = top20.map((s, i) => {
-    const links = (s.why_links || []).slice(0, 3).map(l =>
-      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">🔗 ${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
-    ).join('');
-    return `<tr>
-      <td>#${i + 1}</td>
-      <td><span class="ticker">${s.ticker}</span></td>
-      <td><span class="score-num">${s.combined_score ?? s.score ?? '-'}</span></td>
-      <td>${redditCell(s.reddit_mentions_24h)}</td>
-      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
-      <td><a class="trade-link buy" href="https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol=${s.ticker}" target="_blank" rel="noopener">Buy on Fidelity ↗</a></td>
-    </tr>`;
-  }).join('');
-}
-
-function renderDashboard(d) {
-  document.getElementById('noData').style.display = 'none';
-  document.getElementById('dashboard').style.display = '';
-  document.getElementById('headerMeta').textContent =
-    `Scan: ${d.scan_date} | ${d.stats.analyzed || '?'} stocks analyzed | ${d.regime}`;
-
-  // Stats cards
-  const buyCount = d.stats.buy_count || d.buy_signals.length;
-  const sellCount = d.stats.sell_count || d.sell_signals.length;
-  const topScore = d.buy_signals.length > 0 ? d.buy_signals[0].score : '-';
-
-  document.getElementById('statsRow').innerHTML = `
-    <div class="stat-card green">
-      <div class="label">Buy Signals</div>
-      <div class="value">${buyCount}</div>
-      <div class="sub">Phase 2 confirmed uptrends</div>
-    </div>
-    <div class="stat-card red">
-      <div class="label">Sell Signals</div>
-      <div class="value">${sellCount}</div>
-      <div class="sub">Phase 3/4 breakdowns</div>
-    </div>
-    <div class="stat-card blue">
-      <div class="label">Top Score</div>
-      <div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div>
-      <div class="sub">${d.buy_signals.length > 0 ? d.buy_signals[0].ticker : '-'}</div>
-    </div>
-    <div class="stat-card">
-      <div class="label">Universe</div>
-      <div class="value">${(d.stats.analyzed || 0).toLocaleString()}</div>
-      <div class="sub">of ${(d.stats.total_universe || 0).toLocaleString()} | ${d.stats.processing_minutes || '?'} min</div>
-    </div>
-    <div class="stat-card ${d.spy && d.spy.phase === 2 ? 'green' : d.spy && d.spy.phase === 4 ? 'red' : 'yellow'}">
-      <div class="label">SPY Phase</div>
-      <div class="value">${d.spy.phase || '?'}</div>
-      <div class="sub">${d.spy.trend || ''} @ $${(d.spy.price || 0).toFixed(2)}</div>
-    </div>
-  `;
-
-  // Breadth chart
-  const b = d.breadth;
-  if (breadthChartInstance) breadthChartInstance.destroy();
-  const ctx = document.getElementById('breadthChart').getContext('2d');
-  breadthChartInstance = new Chart(ctx, {
-    type: 'doughnut',
-    data: {
-      labels: ['Phase 1 (Base)', 'Phase 2 (Uptrend)', 'Phase 3 (Distribution)', 'Phase 4 (Downtrend)'],
-      datasets: [{
-        data: [b.phase_1_pct || 0, b.phase_2_pct || 0, b.phase_3_pct || 0, b.phase_4_pct || 0],
-        backgroundColor: ['#eab308', '#22c55e', '#f97316', '#ef4444'],
-        borderColor: '#1a1d27',
-        borderWidth: 3
-      }]
-    },

codex
## 1. Understanding

This is a read-only audit for concrete correctness and reliability defects across the dashboard, screening/data pipeline, backtests, agents, notifications, automation, and macOS wrapper. I excluded style issues and did not re-report the already-fixed Flask threading, inherited dashboard socket, or dashboard-level job watchdog defects except where equivalent exposure still exists outside that watchdog.

I found no new defect I would rate critical in the default dashboard path, but several high-severity bugs can produce stale recommendations, silently invalid backtests, duplicate scans, or multi-hour hangs.

## 2. Files/modules inspected

I inspected:

- `dashboard.py`, `control_panel.py`, `manage_positions.py`, `run_optimized_scan.py`
- `static/js/dashboard.js`, `templates/dashboard.html`
- `mac_app/main.py`, `mac_app/setup.py`, `mac_app/README.md`
- `src/screening/`: `optimized_batch_processor.py`, `batch_processor.py`, `quant_engine.py`, `phase_indicators.py`, `signal_engine.py`, `screener.py`, `top20_ranker.py`, `benchmark.py`, `indicators.py`
- `src/data/`: `fetcher.py`, `smart_fetcher.py`, `git_storage_fetcher.py`, `storage.py`, `universe_fetcher.py`, `fundamentals_fetcher.py`, `enhanced_fundamentals.py`, `fmp_fetcher.py`, `insider_trading.py`, `earnings_risk.py`, `reddit_sentiment.py`, `apewisdom_sentiment.py`, `fidelity_positions.py`, `robinhood_positions.py`, `quality.py`
- `src/agents/`: `fundamentals_auditor.py`, `catalyst_sentiment.py`, `congress_trades.py`, `shortlist.py`, `llm_client.py`
- `src/analysis/position_manager.py`
- `src/notifications/`: `email_notifier.py`, `slack_notifier.py`, `scheduler.py`
- Backtest/data scripts under `scripts/`, especially `walk_forward_backtest.py`, `backtest_top3.py`, `backtest_top3_monte_carlo.py`, `daily_scanner.sh`, and dashboard fetch scripts
- Both GitHub Actions workflows and existing tests

I also reproduced the database duplicate-row failure against an isolated temporary SQLite database.

## 3. Confirmed bugs

### 1. “Live” position refresh never refreshes the displayed current price

**Severity: High**

The CSV’s `Last Price` is stored as `current_price` at [fidelity_positions.py:107](/Users/badripratti/Desktop/stock-screener/src/data/fidelity_positions.py:107) and [fidelity_positions.py:119](/Users/badripratti/Desktop/stock-screener/src/data/fidelity_positions.py:119). That value is passed unchanged into the analysis at [position_manager.py:354](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:354)-[359](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:359).

Although fresh price history is fetched, it is used only for technical indicators; the newest close never replaces `current_price`. The dashboard then advertises a 90-second live refresh at [dashboard.js:762](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:762) and renders the stale CSV price at [dashboard.js:868](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:868).

**Failure scenario:** Upload a morning Fidelity export, leave the dashboard open through a large intraday move, and press re-analyze or wait for live refresh. Charts may change, but displayed price, gain percentage, trailing-stop decision, and partial-sale recommendation remain based on the old CSV quote.

### 2. Resume mode reuses stale completed analyses and loses market breadth

**Severity: High**

Progress stores processed tickers and analyses at [optimized_batch_processor.py:113](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:113), but not the accumulated `phase_results`. On resume, old analyses are restored at [optimized_batch_processor.py:387](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:387), while `phase_results` is reset to an empty list at [optimized_batch_processor.py:399](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:399). Only newly processed tickers are added at [optimized_batch_processor.py:426](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:426).

The sequential processor has the same defect at [batch_processor.py:268](/Users/badripratti/Desktop/stock-screener/src/screening/batch_processor.py:268)-[283](/Users/badripratti/Desktop/stock-screener/src/screening/batch_processor.py:283).

There is also no completed marker, age check, universe fingerprint, or configuration validation.

**Failure scenario:** A completed scan leaves every ticker marked processed. Running with `--resume` the following day performs no fresh stock analysis, reuses yesterday’s prices/results, and returns empty breadth. A partial resume calculates breadth from only the remaining subset, which can change the market regime and suppress or enable signals incorrectly.

### 3. Re-saving overlapping price history always raises `IntegrityError`

**Severity: High**

`PriceHistory` has a unique `(stock_id, date)` constraint at [storage.py:140](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:140). The purported duplicate-handling block surrounds only `session.add()` at [storage.py:399](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:399)-[416](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:416), but SQLAlchemy does not issue the INSERT until flush/commit at [storage.py:417](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:417). Therefore the inner `except IntegrityError` is unreachable for ordinary duplicate rows.

I reproduced this: saving the same one-day DataFrame twice raises SQLite `UNIQUE constraint failed`.

**Failure scenario:** `ScreeningScheduler.fetch_data()` downloads a rolling one-year history on every run and calls this method at [scheduler.py:115](/Users/badripratti/Desktop/stock-screener/src/notifications/scheduler.py:115)-[120](/Users/badripratti/Desktop/stock-screener/src/notifications/scheduler.py:120). After the first run, every ticker overlaps existing dates, every save fails, `success_count` remains zero, and the scheduler reports the whole refresh failed.

### 4. Two legacy engines pass the wrong fundamentals structure into scoring

**Severity: High**

`QuantAnalysisEngine` produces both raw `quarterly_data` and reduced `fundamental_analysis` at [quant_engine.py:117](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:117)-[128](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:128), but passes the reduced structure to `score_buy_signal()` at [quant_engine.py:184](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:184)-[191](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:191).

`score_buy_signal()` expects raw fields such as `quarterly_revenue`, `revenue_yoy_change`, and `eps_yoy_change` at [signal_engine.py:267](/Users/badripratti/Desktop/stock-screener/src/screening/signal_engine.py:267)-[271](/Users/badripratti/Desktop/stock-screener/src/screening/signal_engine.py:271). The reduced dictionary contains classifications such as `revenue_trend`, so real values are ignored and mostly neutral/default scores are assigned.

`run_full_market_scan.py` repeats the mismatch at [run_full_market_scan.py:310](/Users/badripratti/Desktop/stock-screener/scripts/run_full_market_scan.py:310)-[319](/Users/badripratti/Desktop/stock-screener/scripts/run_full_market_scan.py:319).

**Failure scenario:** A company with collapsing revenue or strong EPS growth receives effectively the same fundamental component as one with missing data when these entry points are used.

### 5. A successful scan can leave yesterday’s Top 20 and shortlist in place

**Severity: High**

`top20_latest.json` is written only when `buy_signals` is nonempty at [run_optimized_scan.py:508](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:508)-[522](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:522). The shortlist is written only when agents are enabled and the Top 20 is nonempty at [run_optimized_scan.py:535](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:535)-[567](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:567). Neither path clears prior files on an empty/new non-agent run.

The dashboard always reads those fixed “latest” files at [dashboard.py:696](/Users/badripratti/Desktop/stock-screener/dashboard.py:696)-[706](/Users/badripratti/Desktop/stock-screener/dashboard.py:706).

**Failure scenario:** Today’s scan finds no buys, or a midday scan runs without agents. The current scan report is updated, but Market/Shortlist continues showing older recommendations.

### 6. Dashboard live-refresh overlap protection does not wait for jobs

**Severity: Medium**

`_liveGuarded()` removes its in-flight marker when its callback promise resolves at [dashboard.js:65](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:65)-[71](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:71). But `startJob()` launches its asynchronous polling and immediately returns the job ID at [dashboard.js:243](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:243)-[255](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:255); it does not resolve on job completion.

Consequently the guard is cleared almost immediately, despite comments claiming it prevents stacked jobs.

This combines badly with per-group shared output files, e.g. [dashboard.py:466](/Users/badripratti/Desktop/stock-screener/dashboard.py:466), [dashboard.py:478](/Users/badripratti/Desktop/stock-screener/dashboard.py:478), and [dashboard.py:490](/Users/badripratti/Desktop/stock-screener/dashboard.py:490).

**Failure scenario:** A refresh exceeds 90 seconds or a manual refresh overlaps it. Two jobs for the same group run concurrently; whichever finishes last overwrites the shared file. A callback for the newer job can therefore read output produced by the older job.

### 7. Uploading a new portfolio can race an old live analysis

**Severity: High**

All position jobs read the fixed `positions_latest.csv` and write the fixed `positions_latest.json` at [dashboard.py:455](/Users/badripratti/Desktop/stock-screener/dashboard.py:455)-[459](/Users/badripratti/Desktop/stock-screener/dashboard.py:459). Upload overwrites the CSV directly at [dashboard.py:615](/Users/badripratti/Desktop/stock-screener/dashboard.py:615)-[625](/Users/badripratti/Desktop/stock-screener/dashboard.py:625), with no coordination against live jobs.

**Failure scenario:** A live job starts using portfolio A. The user uploads portfolio B and starts analysis. If the older job finishes last, it overwrites the JSON with recommendations for portfolio A, even though `has_csv` reports that portfolio B exists.

### 8. The control panel has a check/start race that permits duplicate scans

**Severity: High**

The “already running” check at [control_panel.py:101](/Users/badripratti/Desktop/stock-screener/control_panel.py:101)-[107](/Users/badripratti/Desktop/stock-screener/control_panel.py:107) is neither locked nor atomically coupled to setting the status. Status is changed only after the new worker thread begins at [control_panel.py:64](/Users/badripratti/Desktop/stock-screener/control_panel.py:64)-[71](/Users/badripratti/Desktop/stock-screener/control_panel.py:71).

**Failure scenario:** Two near-simultaneous POSTs both observe `idle` and launch two full scans. The second process replaces `STATE[cid]["proc"]`, so Stop controls only one of them while both write the same progress/cache/latest-report files.

### 9. The control panel has no process deadline and is exposed to the LAN

**Severity: High**

Its subprocess loop at [control_panel.py:73](/Users/badripratti/Desktop/stock-screener/control_panel.py:73)-[93](/Users/badripratti/Desktop/stock-screener/control_panel.py:93) has no watchdog or timeout. This leaves all its commands exposed to the same indefinite network-read problem already addressed in `dashboard.py`.

Additionally, it binds an unauthenticated command-running application to every interface at [control_panel.py:297](/Users/badripratti/Desktop/stock-screener/control_panel.py:297)-[304](/Users/badripratti/Desktop/stock-screener/control_panel.py:304).

**Failure scenario:** A hung Yahoo/pip operation leaves the command permanently running. Any machine on the same LAN can also POST fixed commands such as environment setup or full scan without authentication.

### 10. Direct and scheduled scans still have no outer deadline

**Severity: High**

The fixed dashboard watchdog protects only jobs launched through `dashboard.py`. The actual full-scan pipeline still makes yfinance calls at [optimized_batch_processor.py:207](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:207)-[223](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:223) without a process-level deadline.

GitHub Actions runs that script directly at [daily_screening_git_storage.yml:98](/Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml:98), and no `timeout-minutes` is configured. CLI and cron runs are similarly unguarded.

**Failure scenario:** The same stalled SSL read previously observed through the dashboard can hold a scheduled job until the CI platform’s multi-hour default limit, preventing output, email, and cache commits.

### 11. Universe downloads use an unbounded FTP read

**Severity: Medium**

NASDAQ listings are loaded directly through `pandas.read_csv(ftp://...)` at [universe_fetcher.py:46](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:46)-[54](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:54) and [universe_fetcher.py:65](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:65)-[73](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:73). There is no connect/read timeout that this module controls.

**Failure scenario:** A NASDAQ FTP server accepts the connection but stops sending. Fresh-universe scans block before any ticker processing begins.

### 12. Production SMTP sends omit the timeout used by the connection test

**Severity: Medium**

All three real send paths construct `smtplib.SMTP` without a timeout at [email_notifier.py:297](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:297), [email_notifier.py:361](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:361), and [email_notifier.py:451](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:451). In contrast, `test_connection()` uses `timeout=10` at [email_notifier.py:935](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:935).

**Failure scenario:** SMTP accepts a TCP connection and then stalls during TLS, login, or delivery. A CLI/CI scan hangs after completing its expensive work and never commits or exits.

### 13. The documented cron shell script resolves every important path from the wrong directory

**Severity: High**

`SCRIPT_DIR` is the repository’s `scripts/` directory at [daily_scanner.sh:6](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:6). It consequently writes logs under `scripts/data`, changes into `scripts/`, and tries to source `scripts/venv/bin/activate` at [daily_scanner.sh:19](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:19)-[23](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:23). The actual environment is at repository-root `venv/`.

There is also no `set -e`/`pipefail`, and the script unconditionally logs “Completed” at [daily_scanner.sh:25](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:25)-[31](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:31).

**Failure scenario:** Under cron, activation fails; the system Python may then lack dependencies. The scan fails, but the pipeline’s status is masked by `tee` and the log still claims completion.

### 14. Walk-forward stop losses assume impossible fills after gap-down opens

**Severity: Medium**

When the day’s low breaches a stop, the backtest always exits exactly at the stop price at [walk_forward_backtest.py:81](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:81)-[86](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:86).

**Failure scenario:** Stop is $100, but the next session opens at $85 after bad earnings and never trades near $100. A real stop-market order fills near $85; the backtest records $100, materially overstating performance and understating downside.

### 15. Momentum “day streaks” count observations, not consecutive calendar days

**Severity: Medium**

If a ticker retains the same status, the code increments the streak by exactly one at [fetch_momentum_status.py:91](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:91)-[94](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:94), without checking whether `last_seen` was yesterday.

**Failure scenario:** A ticker is checked September 1 and next checked September 13. It is shown as Day 2 rather than either Day 13 or a reset streak. This contradicts the stated “consecutive calendar days” meaning and silently mislabels momentum age.

The shared history file is also updated through a non-atomic load/modify/write at [fetch_momentum_status.py:62](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:62)-[73](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:73), so concurrent group jobs can lose each other’s updates.

### 16. Major partial-sale recommendations are omitted from urgent actions

**Severity: Low**

The action produced for the largest winners is `take_major_partial_and_trail_tight` at [position_manager.py:266](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:266)-[268](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:268). The urgent-action filter instead checks nonexistent `take_partial_and_trail_tight` at [position_manager.py:398](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:398).

**Failure scenario:** A large winner receives the strongest trim recommendation but, absent another warning, is not included in `urgent_actions`.

### 17. Unescaped external data is inserted into dashboard HTML

**Severity: High**

Yahoo news titles, publishers, and URLs are interpolated directly into `innerHTML` at [dashboard.js:588](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:588)-[601](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:601). LLM summaries and filing-derived flags are likewise inserted at [dashboard.js:206](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:206)-[236](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:236).

**Failure scenario:** A feed title or LLM-returned string containing an element with an event handler executes JavaScript in the dashboard origin. That origin can call the unauthenticated local job, sync, upload, and arbitrary-JSON-path endpoints.

### 18. Invalid walk-forward parameters can create an infinite loop

**Severity: Medium**

The dashboard number inputs have no minimum validation at [dashboard.js:1012](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1012)-[1017](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1017), and the backend passes them straight to argparse at [dashboard.py:442](/Users/badripratti/Desktop/stock-screener/dashboard.py:442)-[453](/Users/badripratti/Desktop/stock-screener/dashboard.py:453).

`run_walk_forward()` advances dates using `d += timedelta(days=step_days)` at [walk_forward_backtest.py:172](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:172)-[178](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:178).

**Failure scenario:** An API caller supplies `step_days=0` or a negative value. The date-building loop never terminates; only the dashboard’s ten-minute watchdog eventually kills it. The CLI version has no watchdog.

## 4. Suspected but not fully verified

- **macOS startup race:** [mac_app/main.py:55](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:55)-[60](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:60) starts Flask in a background thread and immediately opens the WebView without a readiness probe. Whether WebKit retries a refused initial connection depends on pywebview/WebKit behavior, so I did not classify this as confirmed.
- **Anthropic request duration:** [llm_client.py:38](/Users/badripratti/Desktop/stock-screener/src/agents/llm_client.py:38)-[40](/Users/badripratti/Desktop/stock-screener/src/agents/llm_client.py:40) constructs the client without an explicit application timeout. The SDK may provide a version-dependent default, so I could not prove an indefinite hang from the repository alone.
- **Non-atomic latest-file reads:** many JSON/text outputs are written directly to their final path while dashboard readers accept malformed intermediate content as “no data.” A concurrent read can therefore show a transient empty page. The exact likelihood depends on filesystem write timing.
- **Packaged-app port collision:** if port 5050 is already occupied, the Flask thread can fail while the WebView still opens that port. Whether the user sees another service or an error depends on local state.

## 5. Easy-to-miss points

- The resume defect is not merely “possibly stale cache”: a normal completed run writes a progress file that makes the next `--resume` run skip every ticker, while restored analyses and breadth come from different universes.
- The positions feature fetches fresh market history successfully, which makes the stale-current-price bug hard to notice: the chart changes while the displayed price and recommendation do not.
- The duplicate database handler looks correct at first glance, but SQLAlchemy constraint errors occur during flush/commit, outside the inner `try`.
- The dashboard’s overlap guard is syntactically asynchronous but guards only job creation, not job lifetime.
- The test email path has a timeout while all real send paths do not, so a successful configuration test gives false confidence about production hang behavior.
tokens used
248,266
## 1. Understanding

This is a read-only audit for concrete correctness and reliability defects across the dashboard, screening/data pipeline, backtests, agents, notifications, automation, and macOS wrapper. I excluded style issues and did not re-report the already-fixed Flask threading, inherited dashboard socket, or dashboard-level job watchdog defects except where equivalent exposure still exists outside that watchdog.

I found no new defect I would rate critical in the default dashboard path, but several high-severity bugs can produce stale recommendations, silently invalid backtests, duplicate scans, or multi-hour hangs.

## 2. Files/modules inspected

I inspected:

- `dashboard.py`, `control_panel.py`, `manage_positions.py`, `run_optimized_scan.py`
- `static/js/dashboard.js`, `templates/dashboard.html`
- `mac_app/main.py`, `mac_app/setup.py`, `mac_app/README.md`
- `src/screening/`: `optimized_batch_processor.py`, `batch_processor.py`, `quant_engine.py`, `phase_indicators.py`, `signal_engine.py`, `screener.py`, `top20_ranker.py`, `benchmark.py`, `indicators.py`
- `src/data/`: `fetcher.py`, `smart_fetcher.py`, `git_storage_fetcher.py`, `storage.py`, `universe_fetcher.py`, `fundamentals_fetcher.py`, `enhanced_fundamentals.py`, `fmp_fetcher.py`, `insider_trading.py`, `earnings_risk.py`, `reddit_sentiment.py`, `apewisdom_sentiment.py`, `fidelity_positions.py`, `robinhood_positions.py`, `quality.py`
- `src/agents/`: `fundamentals_auditor.py`, `catalyst_sentiment.py`, `congress_trades.py`, `shortlist.py`, `llm_client.py`
- `src/analysis/position_manager.py`
- `src/notifications/`: `email_notifier.py`, `slack_notifier.py`, `scheduler.py`
- Backtest/data scripts under `scripts/`, especially `walk_forward_backtest.py`, `backtest_top3.py`, `backtest_top3_monte_carlo.py`, `daily_scanner.sh`, and dashboard fetch scripts
- Both GitHub Actions workflows and existing tests

I also reproduced the database duplicate-row failure against an isolated temporary SQLite database.

## 3. Confirmed bugs

### 1. “Live” position refresh never refreshes the displayed current price

**Severity: High**

The CSV’s `Last Price` is stored as `current_price` at [fidelity_positions.py:107](/Users/badripratti/Desktop/stock-screener/src/data/fidelity_positions.py:107) and [fidelity_positions.py:119](/Users/badripratti/Desktop/stock-screener/src/data/fidelity_positions.py:119). That value is passed unchanged into the analysis at [position_manager.py:354](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:354)-[359](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:359).

Although fresh price history is fetched, it is used only for technical indicators; the newest close never replaces `current_price`. The dashboard then advertises a 90-second live refresh at [dashboard.js:762](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:762) and renders the stale CSV price at [dashboard.js:868](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:868).

**Failure scenario:** Upload a morning Fidelity export, leave the dashboard open through a large intraday move, and press re-analyze or wait for live refresh. Charts may change, but displayed price, gain percentage, trailing-stop decision, and partial-sale recommendation remain based on the old CSV quote.

### 2. Resume mode reuses stale completed analyses and loses market breadth

**Severity: High**

Progress stores processed tickers and analyses at [optimized_batch_processor.py:113](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:113), but not the accumulated `phase_results`. On resume, old analyses are restored at [optimized_batch_processor.py:387](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:387), while `phase_results` is reset to an empty list at [optimized_batch_processor.py:399](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:399). Only newly processed tickers are added at [optimized_batch_processor.py:426](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:426).

The sequential processor has the same defect at [batch_processor.py:268](/Users/badripratti/Desktop/stock-screener/src/screening/batch_processor.py:268)-[283](/Users/badripratti/Desktop/stock-screener/src/screening/batch_processor.py:283).

There is also no completed marker, age check, universe fingerprint, or configuration validation.

**Failure scenario:** A completed scan leaves every ticker marked processed. Running with `--resume` the following day performs no fresh stock analysis, reuses yesterday’s prices/results, and returns empty breadth. A partial resume calculates breadth from only the remaining subset, which can change the market regime and suppress or enable signals incorrectly.

### 3. Re-saving overlapping price history always raises `IntegrityError`

**Severity: High**

`PriceHistory` has a unique `(stock_id, date)` constraint at [storage.py:140](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:140). The purported duplicate-handling block surrounds only `session.add()` at [storage.py:399](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:399)-[416](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:416), but SQLAlchemy does not issue the INSERT until flush/commit at [storage.py:417](/Users/badripratti/Desktop/stock-screener/src/data/storage.py:417). Therefore the inner `except IntegrityError` is unreachable for ordinary duplicate rows.

I reproduced this: saving the same one-day DataFrame twice raises SQLite `UNIQUE constraint failed`.

**Failure scenario:** `ScreeningScheduler.fetch_data()` downloads a rolling one-year history on every run and calls this method at [scheduler.py:115](/Users/badripratti/Desktop/stock-screener/src/notifications/scheduler.py:115)-[120](/Users/badripratti/Desktop/stock-screener/src/notifications/scheduler.py:120). After the first run, every ticker overlaps existing dates, every save fails, `success_count` remains zero, and the scheduler reports the whole refresh failed.

### 4. Two legacy engines pass the wrong fundamentals structure into scoring

**Severity: High**

`QuantAnalysisEngine` produces both raw `quarterly_data` and reduced `fundamental_analysis` at [quant_engine.py:117](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:117)-[128](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:128), but passes the reduced structure to `score_buy_signal()` at [quant_engine.py:184](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:184)-[191](/Users/badripratti/Desktop/stock-screener/src/screening/quant_engine.py:191).

`score_buy_signal()` expects raw fields such as `quarterly_revenue`, `revenue_yoy_change`, and `eps_yoy_change` at [signal_engine.py:267](/Users/badripratti/Desktop/stock-screener/src/screening/signal_engine.py:267)-[271](/Users/badripratti/Desktop/stock-screener/src/screening/signal_engine.py:271). The reduced dictionary contains classifications such as `revenue_trend`, so real values are ignored and mostly neutral/default scores are assigned.

`run_full_market_scan.py` repeats the mismatch at [run_full_market_scan.py:310](/Users/badripratti/Desktop/stock-screener/scripts/run_full_market_scan.py:310)-[319](/Users/badripratti/Desktop/stock-screener/scripts/run_full_market_scan.py:319).

**Failure scenario:** A company with collapsing revenue or strong EPS growth receives effectively the same fundamental component as one with missing data when these entry points are used.

### 5. A successful scan can leave yesterday’s Top 20 and shortlist in place

**Severity: High**

`top20_latest.json` is written only when `buy_signals` is nonempty at [run_optimized_scan.py:508](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:508)-[522](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:522). The shortlist is written only when agents are enabled and the Top 20 is nonempty at [run_optimized_scan.py:535](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:535)-[567](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:567). Neither path clears prior files on an empty/new non-agent run.

The dashboard always reads those fixed “latest” files at [dashboard.py:696](/Users/badripratti/Desktop/stock-screener/dashboard.py:696)-[706](/Users/badripratti/Desktop/stock-screener/dashboard.py:706).

**Failure scenario:** Today’s scan finds no buys, or a midday scan runs without agents. The current scan report is updated, but Market/Shortlist continues showing older recommendations.

### 6. Dashboard live-refresh overlap protection does not wait for jobs

**Severity: Medium**

`_liveGuarded()` removes its in-flight marker when its callback promise resolves at [dashboard.js:65](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:65)-[71](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:71). But `startJob()` launches its asynchronous polling and immediately returns the job ID at [dashboard.js:243](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:243)-[255](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:255); it does not resolve on job completion.

Consequently the guard is cleared almost immediately, despite comments claiming it prevents stacked jobs.

This combines badly with per-group shared output files, e.g. [dashboard.py:466](/Users/badripratti/Desktop/stock-screener/dashboard.py:466), [dashboard.py:478](/Users/badripratti/Desktop/stock-screener/dashboard.py:478), and [dashboard.py:490](/Users/badripratti/Desktop/stock-screener/dashboard.py:490).

**Failure scenario:** A refresh exceeds 90 seconds or a manual refresh overlaps it. Two jobs for the same group run concurrently; whichever finishes last overwrites the shared file. A callback for the newer job can therefore read output produced by the older job.

### 7. Uploading a new portfolio can race an old live analysis

**Severity: High**

All position jobs read the fixed `positions_latest.csv` and write the fixed `positions_latest.json` at [dashboard.py:455](/Users/badripratti/Desktop/stock-screener/dashboard.py:455)-[459](/Users/badripratti/Desktop/stock-screener/dashboard.py:459). Upload overwrites the CSV directly at [dashboard.py:615](/Users/badripratti/Desktop/stock-screener/dashboard.py:615)-[625](/Users/badripratti/Desktop/stock-screener/dashboard.py:625), with no coordination against live jobs.

**Failure scenario:** A live job starts using portfolio A. The user uploads portfolio B and starts analysis. If the older job finishes last, it overwrites the JSON with recommendations for portfolio A, even though `has_csv` reports that portfolio B exists.

### 8. The control panel has a check/start race that permits duplicate scans

**Severity: High**

The “already running” check at [control_panel.py:101](/Users/badripratti/Desktop/stock-screener/control_panel.py:101)-[107](/Users/badripratti/Desktop/stock-screener/control_panel.py:107) is neither locked nor atomically coupled to setting the status. Status is changed only after the new worker thread begins at [control_panel.py:64](/Users/badripratti/Desktop/stock-screener/control_panel.py:64)-[71](/Users/badripratti/Desktop/stock-screener/control_panel.py:71).

**Failure scenario:** Two near-simultaneous POSTs both observe `idle` and launch two full scans. The second process replaces `STATE[cid]["proc"]`, so Stop controls only one of them while both write the same progress/cache/latest-report files.

### 9. The control panel has no process deadline and is exposed to the LAN

**Severity: High**

Its subprocess loop at [control_panel.py:73](/Users/badripratti/Desktop/stock-screener/control_panel.py:73)-[93](/Users/badripratti/Desktop/stock-screener/control_panel.py:93) has no watchdog or timeout. This leaves all its commands exposed to the same indefinite network-read problem already addressed in `dashboard.py`.

Additionally, it binds an unauthenticated command-running application to every interface at [control_panel.py:297](/Users/badripratti/Desktop/stock-screener/control_panel.py:297)-[304](/Users/badripratti/Desktop/stock-screener/control_panel.py:304).

**Failure scenario:** A hung Yahoo/pip operation leaves the command permanently running. Any machine on the same LAN can also POST fixed commands such as environment setup or full scan without authentication.

### 10. Direct and scheduled scans still have no outer deadline

**Severity: High**

The fixed dashboard watchdog protects only jobs launched through `dashboard.py`. The actual full-scan pipeline still makes yfinance calls at [optimized_batch_processor.py:207](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:207)-[223](/Users/badripratti/Desktop/stock-screener/src/screening/optimized_batch_processor.py:223) without a process-level deadline.

GitHub Actions runs that script directly at [daily_screening_git_storage.yml:98](/Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml:98), and no `timeout-minutes` is configured. CLI and cron runs are similarly unguarded.

**Failure scenario:** The same stalled SSL read previously observed through the dashboard can hold a scheduled job until the CI platform’s multi-hour default limit, preventing output, email, and cache commits.

### 11. Universe downloads use an unbounded FTP read

**Severity: Medium**

NASDAQ listings are loaded directly through `pandas.read_csv(ftp://...)` at [universe_fetcher.py:46](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:46)-[54](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:54) and [universe_fetcher.py:65](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:65)-[73](/Users/badripratti/Desktop/stock-screener/src/data/universe_fetcher.py:73). There is no connect/read timeout that this module controls.

**Failure scenario:** A NASDAQ FTP server accepts the connection but stops sending. Fresh-universe scans block before any ticker processing begins.

### 12. Production SMTP sends omit the timeout used by the connection test

**Severity: Medium**

All three real send paths construct `smtplib.SMTP` without a timeout at [email_notifier.py:297](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:297), [email_notifier.py:361](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:361), and [email_notifier.py:451](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:451). In contrast, `test_connection()` uses `timeout=10` at [email_notifier.py:935](/Users/badripratti/Desktop/stock-screener/src/notifications/email_notifier.py:935).

**Failure scenario:** SMTP accepts a TCP connection and then stalls during TLS, login, or delivery. A CLI/CI scan hangs after completing its expensive work and never commits or exits.

### 13. The documented cron shell script resolves every important path from the wrong directory

**Severity: High**

`SCRIPT_DIR` is the repository’s `scripts/` directory at [daily_scanner.sh:6](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:6). It consequently writes logs under `scripts/data`, changes into `scripts/`, and tries to source `scripts/venv/bin/activate` at [daily_scanner.sh:19](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:19)-[23](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:23). The actual environment is at repository-root `venv/`.

There is also no `set -e`/`pipefail`, and the script unconditionally logs “Completed” at [daily_scanner.sh:25](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:25)-[31](/Users/badripratti/Desktop/stock-screener/scripts/daily_scanner.sh:31).

**Failure scenario:** Under cron, activation fails; the system Python may then lack dependencies. The scan fails, but the pipeline’s status is masked by `tee` and the log still claims completion.

### 14. Walk-forward stop losses assume impossible fills after gap-down opens

**Severity: Medium**

When the day’s low breaches a stop, the backtest always exits exactly at the stop price at [walk_forward_backtest.py:81](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:81)-[86](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:86).

**Failure scenario:** Stop is $100, but the next session opens at $85 after bad earnings and never trades near $100. A real stop-market order fills near $85; the backtest records $100, materially overstating performance and understating downside.

### 15. Momentum “day streaks” count observations, not consecutive calendar days

**Severity: Medium**

If a ticker retains the same status, the code increments the streak by exactly one at [fetch_momentum_status.py:91](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:91)-[94](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:94), without checking whether `last_seen` was yesterday.

**Failure scenario:** A ticker is checked September 1 and next checked September 13. It is shown as Day 2 rather than either Day 13 or a reset streak. This contradicts the stated “consecutive calendar days” meaning and silently mislabels momentum age.

The shared history file is also updated through a non-atomic load/modify/write at [fetch_momentum_status.py:62](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:62)-[73](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:73), so concurrent group jobs can lose each other’s updates.

### 16. Major partial-sale recommendations are omitted from urgent actions

**Severity: Low**

The action produced for the largest winners is `take_major_partial_and_trail_tight` at [position_manager.py:266](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:266)-[268](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:268). The urgent-action filter instead checks nonexistent `take_partial_and_trail_tight` at [position_manager.py:398](/Users/badripratti/Desktop/stock-screener/src/analysis/position_manager.py:398).

**Failure scenario:** A large winner receives the strongest trim recommendation but, absent another warning, is not included in `urgent_actions`.

### 17. Unescaped external data is inserted into dashboard HTML

**Severity: High**

Yahoo news titles, publishers, and URLs are interpolated directly into `innerHTML` at [dashboard.js:588](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:588)-[601](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:601). LLM summaries and filing-derived flags are likewise inserted at [dashboard.js:206](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:206)-[236](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:236).

**Failure scenario:** A feed title or LLM-returned string containing an element with an event handler executes JavaScript in the dashboard origin. That origin can call the unauthenticated local job, sync, upload, and arbitrary-JSON-path endpoints.

### 18. Invalid walk-forward parameters can create an infinite loop

**Severity: Medium**

The dashboard number inputs have no minimum validation at [dashboard.js:1012](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1012)-[1017](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1017), and the backend passes them straight to argparse at [dashboard.py:442](/Users/badripratti/Desktop/stock-screener/dashboard.py:442)-[453](/Users/badripratti/Desktop/stock-screener/dashboard.py:453).

`run_walk_forward()` advances dates using `d += timedelta(days=step_days)` at [walk_forward_backtest.py:172](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:172)-[178](/Users/badripratti/Desktop/stock-screener/scripts/walk_forward_backtest.py:178).

**Failure scenario:** An API caller supplies `step_days=0` or a negative value. The date-building loop never terminates; only the dashboard’s ten-minute watchdog eventually kills it. The CLI version has no watchdog.

## 4. Suspected but not fully verified

- **macOS startup race:** [mac_app/main.py:55](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:55)-[60](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:60) starts Flask in a background thread and immediately opens the WebView without a readiness probe. Whether WebKit retries a refused initial connection depends on pywebview/WebKit behavior, so I did not classify this as confirmed.
- **Anthropic request duration:** [llm_client.py:38](/Users/badripratti/Desktop/stock-screener/src/agents/llm_client.py:38)-[40](/Users/badripratti/Desktop/stock-screener/src/agents/llm_client.py:40) constructs the client without an explicit application timeout. The SDK may provide a version-dependent default, so I could not prove an indefinite hang from the repository alone.
- **Non-atomic latest-file reads:** many JSON/text outputs are written directly to their final path while dashboard readers accept malformed intermediate content as “no data.” A concurrent read can therefore show a transient empty page. The exact likelihood depends on filesystem write timing.
- **Packaged-app port collision:** if port 5050 is already occupied, the Flask thread can fail while the WebView still opens that port. Whether the user sees another service or an error depends on local state.

## 5. Easy-to-miss points

- The resume defect is not merely “possibly stale cache”: a normal completed run writes a progress file that makes the next `--resume` run skip every ticker, while restored analyses and breadth come from different universes.
- The positions feature fetches fresh market history successfully, which makes the stale-current-price bug hard to notice: the chart changes while the displayed price and recommendation do not.
- The duplicate database handler looks correct at first glance, but SQLAlchemy constraint errors occur during flush/commit, outside the inner `try`.
- The dashboard’s overlap guard is syntactically asynchronous but guards only job creation, not job lifetime.
- The test email path has a timeout while all real send paths do not, so a successful configuration test gives false confidence about production hang behavior.
