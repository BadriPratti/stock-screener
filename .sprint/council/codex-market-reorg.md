# Engineering Council second opinion: Market view reorganization

## Recommendation

Use a **hybrid**: keep a compact market-context header visible, put the data-heavy work areas behind primary tabs, and make the map's 400+ row tracker a collapsed disclosure inside its tab.

Recommended order:

1. Always visible: source note, scan selector, five stats, then Market Breadth + SPY Regime.
2. **Opportunity Map** (default primary tab).
3. **Top 20**.
4. **Signals** (retain the existing Buy/Sell tablist inside this panel).
5. **News** (the current `newsSections` is also part of the page length even though it was omitted from the problem inventory).

Inside Opportunity Map, keep filters, replay, chart, scheduler, and Expand together; put **Tracked stocks (N)** behind a closed-by-default disclosure and create its rows on first expansion. The existing full-screen Expand behavior complements this structure but does not solve the long inline table by itself.

This is preferable to a page-wide accordion: stats/regime are glanceable context, while Map/Top 20/Signals/News are peer workflows where tabs give clearer location and guarantee only one long region is visible. The one nested tablist is acceptable because it expresses a real hierarchy (Market section -> signal side) and reuses the already accessible, tested Buy/Sell control. Do not add another accordion around Signals. Promoting Buy and Sell to separate primary tabs would remove nesting but causes more churn and weakens the useful “Signals” grouping.

## Repository evidence and design details

### State and URL

Use `#/market/map`, `#/market/top20`, `#/market/signals`, and `#/market/news`; bare `#/market` resolves to `map`. Do **not** persist the primary tab in `localStorage`: the URL already survives refresh and is shareable, while a remembered hidden section can make a later visit feel surprising. Map filters/replay state may remain in memory for the current Market-view lifetime only. The tracker disclosure should reset closed on a fresh view/scan.

`static/js/core/router.js` does not support this today: it removes `#/` and looks up the entire remainder in `VIEWS`, so `#/market/map` falls back to `positions`. Add small route parsing that separates the top-level view from an optional section. Tab clicks should update the hash with `history.replaceState` (not assign `location.hash`) so changing section does not invoke `route()`, `_stopLive()`, clear `content`, destroy the map, and refetch the whole view. Direct loads and normal navigation still go through `route()`. If section changes should participate in Back/Forward, use `pushState` plus a `popstate` handler; for this desktop dashboard, replace-state is the lower-risk default.

Reject unknown Market sections to `map` and canonicalize the URL. Keep `currentView === 'market'`, so existing live guards and sidebar highlighting continue to work.

### Map lifecycle and performance

`hidden`/`display:none` only removes layout and paint; it does not undo fetches, the Chart.js instance, event listeners, table construction, or replay callbacks. Today `loadMarketScan()` always calls `mountMarketMap()`, which immediately fetches frames, tracker, and scheduler, emits every tracker row, creates the Chart.js canvas, and constructs the player. Therefore CSS-only tabs do not provide meaningful work avoidance.

Policy:

- Lazy-mount the map only on the first activation of Opportunity Map. A direct Top 20/Signals/News link must not fetch map data or create its canvas.
- Mount once per selected scan and keep the controller/DOM while switching primary tabs, preserving filters and replay position. Never construct a second controller for the same `marketMotionChart` canvas.
- Add an explicit controller `setActive(active)` (or `suspend`/`resume`). On deactivation: pause playback/cancel its rAF, close the expanded overlay, and stop rendering/resizing. On activation: refresh dirty data, resize the chart, then repaint once. The player only schedules rAF while animating today, but explicit suspension prevents a replay or step tween from continuing after the panel is hidden.
- Keep the existing Market-view 90-second timer while any Market section is open. Once the map has mounted, inactive-map ticks should make only lightweight `/api/market-motion/latest` and scheduler-status checks. If a new run exists, mark the controller dirty/new; do not fetch full frames/tracker or update the hidden chart/table until activation. This keeps scheduler status and “New snapshot available” honest without hidden rendering. If the map has never mounted, its first mount's three fetches establish fresh state, so no background map poll is required.
- Render the tracker table shell/count initially but create the full row HTML only when its disclosure first opens. Subsequent sorting/filter refreshes may update it only while expanded, or mark it dirty while closed.
- Destroy the existing controller **before** replacing `marketBody` on a scan change or leaving Market. The current scan-load order assigns `marketBody.innerHTML` before destroying the old controller; reorganizing is a good time to fix that ordering. `charts.js` already registers/destroys charts by canvas id, and `market-map.js` cleanup destroys the player and media-query listener; retain that path to avoid the prior “Canvas is already in use” class of failure.

The Breadth chart belongs in the always-visible context and is cheap enough to render with the scan. Signal price-history and news refreshes can remain as-is for this medium task; they are not animation loops and changing them would broaden scope.

### Accessibility and narrow windows

Mirror `_wireSignalTabs`: `role="tablist"`, buttons with `role="tab"`, `aria-selected`, `aria-controls`, roving `tabindex`, and Left/Right/Home/End. Each controlled panel uses `role="tabpanel"`, `aria-labelledby`, and `hidden`. Use distinct `data-market-section` selectors so the primary wiring cannot accidentally capture `[data-signal-tab]`. On keyboard activation, move focus to the selected tab; mouse activation should not unexpectedly move focus.

The tracker disclosure should be a real `<button aria-expanded aria-controls>` (or native `<details>/<summary>` if styling permits), with the count in its accessible name. When a map point targets a Buy row, activate the primary Signals panel, activate Buy, then find/scroll/highlight the row. Honor `prefers-reduced-motion` for this programmatic scroll (`auto`, not `smooth`); the map player already disables animation through `matchMedia`, and CSS already suppresses overlay/highlight animations.

At the defensive 760px breakpoint, keep the same tab semantics. Make the primary tablist horizontally scrollable with single-line labels and a visible focus ring; do not change it into a select/accordion, which would introduce a second interaction model at a non-primary width. The existing Buy/Sell buttons already become full-width at 760px, and the map controls already stack there.

## Migration plan and test impact

1. **`static/js/core/router.js`** — parse the optional Market section and expose/pass it without changing the top-level `currentView`; support direct deep links. Dependency: none.
2. **`static/js/views/market.js`** — add the primary tab shell/controller; keep existing IDs (`marketBody`, `marketMotionMount`, `marketSignalsCard`, signal tab/panel/body IDs, `breadthChart`) and existing rendered table/card helpers. Move `newsSections` into its panel without renaming its child IDs. Lazy-call `mountMarketMap`, destroy-before-replace, and make `_showMarketTicker` activate Signals/Buy before scrolling. Dependency: router section parsing and map lifecycle API.
3. **`static/js/components/market-map.js`** — add suspend/resume/dirty lifecycle, lightweight inactive polling behavior, and lazy tracker-row disclosure. Preserve all public control/canvas/table IDs. Dependency: none; controller behavior can be characterized independently.
4. **`static/css/dashboard.css`** — add primary-tab and disclosure styles using existing tokens (`--space-*`, surfaces, borders, accent, focus ring), horizontal overflow at 760px, and reduced-motion behavior. No template/sidebar or separate view is needed.
5. **Tests** — add `tests/js/test_market_sections.js` for default/invalid route section, ARIA/keyboard behavior, URL replacement, single lazy mount, and section switching. Extend `test_market_map_controller.js` for suspend/resume, no hidden repaint, dirty refresh, and cleanup. Update `test_market_map_component.js` where it currently requires every tracker record to appear in the initial HTML; replace that with assertions that the disclosure/count exists and rows render once on expansion. Existing signal-tab tests should remain valid if their IDs/functions and `data-signal-tab` selector are preserved. The pure scatter, motion model, renderer, and default-scan tests should not need changes.

This avoids a new sidebar route (`consistency.js` shows that pattern, but Map/Top 20/Signals share the same scan selection and context), preserves nearly all established selectors, and confines unavoidable test churn to the deliberately lazy tracker table and new primary navigation lifecycle.
