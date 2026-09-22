# MM-008 Persistent Tracker Map

## Changed
- `static/js/components/market-map.js`: added the persistent-map DOM/controller, replay wiring, filters/search, full tracker table, scheduler controls, live refresh, reduced-motion handling, fallback, and expanded focus-trapped overlay.
- `static/js/charts.js`: added the classic-script `renderMarketMotionChart`, one-instance in-place dataset updates, buy/zero lines, vectors/tails/labels plugin, per-point encodings/tooltips, and cleanup registration before Chart destruction.
- `static/js/views/market.js`: mounted the controller, retained `buildBuyOpportunityPoints`, added report request-token protection, in-place live polling, row navigation, and route teardown.
- `static/js/dashboard.js`: dispatches `stock-data-updated` after successful sync and preserves the Market replay instead of rerouting it; other views retain rerouting behavior.
- `static/css/dashboard.css`: added full-width clamp-sized map, controls, scheduler/table, expanded overlay, responsive, focus, and reduced-motion styles.
- `tests/js/test_auto_sync_form_guard.js`: updated the auto-sync contract for Market's in-place event.
- Added `tests/js/test_market_map_component.js`, `test_market_map_controller.js`, and `test_market_motion_chart_renderer.js`.

## Decisions
- Kept the chart canvas mounted during Expand and called Chart resize, avoiding a second Chart instance and canvas ownership races.
- Kept table construction independent of chart decimation so every tracker API record remains available to keyboard and screen-reader users.
- Applied degradation in the required order: tails first, then labels; active points remain protected by the fixed model contract.
- Treated scheduler status as optional/fail-soft so a scheduler error cannot replace valid persistent frame data with the fallback chart.
- Preserved replay position on `stock-data-updated`; live-edge players follow appended frames, while scrubbed players show the new-snapshot control.

## Could not do
- No browser/pywebview visual pass was available in this task environment. Automated tests cover structure, state, lifecycle, and rendering configuration.

## Verification
- `for f in tests/js/*.js; do node "$f" || exit 1; done` -> 23 files passed.
- 2,000-point `itemsAt` + `decimate` smoke average: 0.361 ms locally; generous non-flaky bound passed.
- ES-module graph load command importing `static/js/dashboard.js` with repository-style DOM/fetch/timer stubs -> `dashboard module graph loaded`.
- `venv/bin/python -m pytest -q tests/test_market_motion.py tests/test_pick_history.py tests/test_scan_run_kind.py tests/test_workflows_pick_history.py tests/test_pick_history_api.py tests/test_backfill_pick_history.py tests/test_dashboard_jobs.py tests/test_current_price_flow.py` -> 123 passed in 2.41s.
- `git diff --check -- <allowed tracked frontend/test files>` plus newline checks for new files -> clean.

## Lead review risk
- Please visually verify dense labels, tooltip legibility, focus behavior, and canvas resizing in the real pywebview/WebKit window; these are the remaining platform-specific risks.
