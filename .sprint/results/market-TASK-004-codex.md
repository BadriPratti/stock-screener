# TASK-004 — Market Buy/Sell signal tabs

## Implementation

- Replaced the separately stacked Buy Signals and Sell Signals cards with one Market Signals card.
- Added a real ARIA tablist with Buy and Sell `role="tab"` buttons, reciprocal `aria-controls` / `aria-labelledby` relationships, roving `tabindex`, and native `hidden` state on the inactive `role="tabpanel"`.
- Buy is active and rendered immediately. The Sell panel and `#sellSignalsBody` exist initially, but the body is empty until Sell is first activated. Its rendered DOM is retained on later switches.
- Tabs auto-activate on click, Left/Right arrow navigation, and Home/End navigation. Enter and Space retain native button activation through the click handler.
- Preserved `#buySignalsBody` and `#sellSignalsBody`, all table columns, current-price cells, ticker row attributes, reason expansion, Fidelity links, Reddit cells, badges, and score bars.
- Added responsive tab styling beside the existing Market signal-table rules using the existing `.btn` class and design tokens only.

## Scatter-chart interaction

`_renderBuyOpportunityChart` now passes `_showBuySignal` as the dot-click callback. That thin wrapper calls `_activateSignalTab('buy')` before calling the unchanged `_highlightBuyRow(signal)`, so a click while Sell is active reveals the Buy panel before the existing smooth scroll and pulse. The chart data remains Buy-only and independent of tab state.

## Count wording

Tab labels use the persisted array length as the shown count. When the corresponding scan statistic differs, the wording is `Buy (50 of 479)` or `Sell (30 of 392)`; when it matches, the shorter `Buy (50)` / `Sell (30)` form is used.

## Constraint checks

- Did not change `static/js/charts.js`.
- Did not change `buildBuyOpportunityPoints`, `_buyOpportunityChartCardHTML`, or `_highlightBuyRow`'s body. The only permitted `_renderBuyOpportunityChart` change is its callback argument.
- Did not change Market Breadth, SPY Regime, Top 20, stats, news, other views, or `static/js/core/` as part of TASK-004.
- Did not touch `position/`, commit, or push.
- TASK-004 implementation files: `static/js/views/market.js`, `static/css/dashboard.css`, and `tests/js/test_market_signal_tabs.js`; this report is the separately required result artifact. Other modified/untracked paths in repository status belong to prior sprint tasks or concurrent news work.

## Verification

```text
node --input-type=module --check < static/js/views/market.js
PASS (no output)

node tests/js/test_market_signal_tabs.js
test_market_signal_tabs.js: all assertions passed

CSS brace balance
CSS braces: 170 opening, 170 closing

node tests/js/test_live_guard.js && node tests/js/test_start_job.js && node tests/js/test_auto_sync_form_guard.js && node tests/js/test_shortlist_empty_state.js && node tests/js/test_market_signal_tabs.js
test_live_guard.js: all assertions passed
test_start_job.js: all assertions passed
test_auto_sync_form_guard.js: all assertions passed
test_shortlist_empty_state.js: all assertions passed
test_market_signal_tabs.js: all assertions passed

venv/bin/python -m pytest tests/test_dashboard_jobs.py -v
8 passed in 0.07s

git diff --check -- static/js/views/market.js static/css/dashboard.css tests/js/test_market_signal_tabs.js
PASS (no output)
```
