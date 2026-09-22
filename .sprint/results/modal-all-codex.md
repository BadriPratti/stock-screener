# Full-Screen Chart Analysis Modal

## Files changed
- `static/js/core/price-analysis.js`: added pure history normalization, SMA, range, and statistics helpers.
- `static/js/core/chart-modal.js`: added singleton modal controller, controls, rendering, focus trap, safe focus return, backdrop/Escape close, refresh, and chart teardown.
- `static/js/charts.js`: added classic-script `renderAnalysisChart` plus explicit `window.StockCharts` render/destroy boundary.
- `static/js/core/ui-helpers.js`: replaced inline toggle state with one accessible analysis-button helper and modal wiring/refresh helpers.
- `static/js/core/router.js`: closes the modal before every route transition.
- `static/js/views/positions.js`: opens analysis with real entry and recommended-stop references; refreshes an open modal after live rerender.
- `static/js/views/shortlist.js`: opens analysis with no fabricated references and refreshes current modal data.
- `static/js/views/market.js`: opens buy charts with `Scanner stop`, sell charts with `Breakdown level`, removes inline chart rows/column, and preserves the opportunity scatter and jump handler.
- `templates/dashboard.html`: added the persistent modal/ARIA shell outside `#content`.
- `static/css/dashboard.css`: added full-viewport responsive modal styling, explicit chart height, toast layer 1100, and reduced-motion handling.
- `tests/js/test_market_signal_extras.js`: updated the obsolete inline-chart assertions to require the replacement modal action.
- `tests/js/test_market_signal_tabs.js`, `test_shortlist_empty_state.js`, `test_shortlist_consistency.js`: updated helper mocks for the renamed analysis API.
- Added `tests/js/test_price_analysis.js`, `test_chart_modal_template.js`, `test_chart_modal_behavior.js`, `test_chart_reference_wiring.js`, `test_router_closes_chart_modal.js`, `test_charts_classic_boundary.js`, and `test_analysis_chart_renderer.js`.

## Decisions
- Reused one fixed canvas and always destroyed its Chart.js instance before recreation and on close.
- Computed SMAs from full normalized history before slicing the selected display range.
- Preserved 1M/3M/6M/All and SMA preferences across ticker changes; SMA controls disable for insufficient valid closes.
- Treated every reference as optional with `Number.isFinite`, including valid zero values.
- Kept the existing Market Buy Opportunity Map and its click-to-row behavior unchanged.

## Deviations
- None from the sprint plan. The Market inline-chart characterization test was updated because that assertion was explicitly obsolete after replacement.

## Verification
- `for f in tests/js/*.js; do node "$f"; done` -> 20 files passed.
- `venv/bin/python -m pytest tests/test_dashboard_jobs.py -q` -> 8 passed in 1.02s.
- `node --input-type=module -e "...await import('./static/js/dashboard.js')..."` with repository-style DOM/fetch/timer stubs -> `dashboard module graph loaded`.
- `git diff --check -- <allowed frontend and tests paths>` -> clean.

## Risks
- Automated tests validate structure, lifecycle, math, wiring, and keyboard logic; final visual sizing, native WebKit focus behavior, canvas sharpness, and resize behavior still require a pywebview manual pass.
