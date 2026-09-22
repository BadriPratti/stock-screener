# MR-003 implementation report

## What changed

- `static/js/components/market-map.js:110` (`marketMapHTML`): replaced the eagerly rendered tracked-stock table with a closed-by-default `.market-motion-table-disclosure` button and hidden table container. The initial count uses the default active/watching filters, and the existing tracker title ID is preserved.
- `static/js/components/market-map.js:338` (`renderTable`, `invalidateTable`, `bindSortHeaders`): added lazy table construction. No table rows or headers are built while closed. The first open builds the table once; open-table filter/sort changes update it immediately, while closed-table changes only update the visible count and mark the table dirty for its next open.
- `static/js/components/market-map.js:418` (`pollLatest`): retained the existing externally driven polling method. This file does not own or start a timer. A newer frame detected while inactive is recorded as pending and exposes the existing "New snapshot available" action instead of silently fetching and repainting the hidden map.
- `static/js/components/market-map.js:487` (`closeExpanded`): made overlay teardown lifecycle-aware so suspension closes the overlay without resizing or restoring focus into a hidden tab.
- `static/js/components/market-map.js:617` (`togglePlayback`, `setActive`): reused the Play/Pause toggle path to pause active replay during suspension. Resume performs one `chart.resize()` and one repaint at the preserved replay position, without autoplay, fetching, destroying, or recreating the chart.
- `static/js/components/market-map.js:673` (returned controller): added `setActive(bool)`, `suspend()`, and `resume()` while retaining all existing controller methods, exports, IDs, and classes.

## Decisions

- The controller remains active by default, preserving the existing single-panel behavior when no lifecycle method is called.
- The disclosure count and rows follow all current tier, entry-quality, minimum-streak, and ticker-search filters. Programmatic `selectTicker` also invalidates the table.
- Pending data discovered by polling while inactive is fetched only when the user accepts the existing new-snapshot action. A failed refresh leaves the pending state intact.
- No polling timer was found in this file. The existing lightweight `pollLatest()` method was already suitable for the `market.js` owner to call, so no additional polling API was introduced.

## Verification

Python regression command:

```text
venv/bin/python -m pytest tests/test_market_motion.py tests/test_pick_history.py tests/test_scan_run_kind.py tests/test_workflows_pick_history.py tests/test_pick_history_api.py tests/test_backfill_pick_history.py tests/test_dashboard_jobs.py tests/test_current_price_flow.py
```

Result: `124 passed in 1.57s`.

JavaScript command:

```text
node tests/js/test_market_map_controller.js; node tests/js/test_market_map_component.js; node tests/js/test_market_motion.js; node tests/js/test_market_motion_chart_renderer.js
```

Results:

- `test_market_map_controller.js`: passed.
- `test_market_motion.js`: passed.
- `test_market_motion_chart_renderer.js`: passed.
- `test_market_map_component.js`: failed on its pre-MR-003 initial-HTML assertion that sortable table headers/rows must already exist. The new contract intentionally leaves the table container empty until first open. The task's file restriction allowed only `static/js/components/market-map.js`, so I did not update that test file; MR-005 owns the planned test change.

Additional offline checks:

- `node --check static/js/components/market-map.js`: passed.
- Lazy-disclosure smoke: closed state, filtered count, hidden container, and no initial tracked rows passed.
- In-memory lifecycle harness: suspension paused replay and cleared its scheduled frame; resume did not restart, fetched nothing, resized once, repainted once, and retained one chart construction.
- In-memory overlay harness: suspension closed an open Expand overlay.
- Source emoji scan: clean.

## Risks and follow-up

- The repository's current `test_market_map_component.js` must be updated by its permitted owner to open the disclosure before asserting sortable headers and tracked rows. Until then, the requested four-file JavaScript command has one expected stale-test failure.
- A browser verification remains useful after MR-002 connects tab activation, particularly for Chart.js resize timing and focus behavior across the real tab and overlay DOM.

No implementation work was blocked, no network scan or external API was invoked, and no git-mutating command was used.
