# Sprint: Reorganize the Market view (tabs, not one long scroll)

STATUS: PLAN ONLY. Nothing built, committed, or pushed.

## Request (user's own words)
"we need to have better way to organize this because the market thing is sooo long and I am scrolling down a lot
we need better way to organize we can create button that then drops down the list or have tabs"

## Council process
MEDIUM task, second-opinion council (not full 3-way, to control cost per the user's own stated token concern today):
Codex (`.sprint/council/codex-market-reorg.md`) + Antigravity (`.sprint/council/antigravity-market-reorg.md`),
both independent, both given the same brief (`.sprint/council/market-reorg-brief.md`). I verified their key
factual claims against the actual CSS/JS before adopting them (below).

## Why the page is this long today
`static/js/views/market.js` (480 lines) renders, top to bottom, in one scroll: source note + scan picker -> 5 stat
tiles -> Market Breadth donut + SPY Regime card -> the new Buy Opportunity Map (replay controls, filter chips,
scheduler card, a `clamp(560px, 72vh, 880px)` canvas, and a sortable table that can list 400+ tracked stocks) ->
the Top 20 table -> Buy/Sell signal tabs (up to 50 rows each) -> news. Item 3 (the map, added earlier today) is by
far the biggest contributor.

## Converged decisions (Codex and Antigravity independently agreed)
1. **Tabs, not an accordion.** An accordion either buries everything by default or, once the map section is
   expanded, reproduces the exact scroll problem (the map alone is 1,000+px). Tabs guarantee only one heavy
   section is on screen at a time.
2. **Lazy-mount the map; never destroy it on tab switch.** Hiding a section with `hidden`/`display:none` does
   NOT stop fetches, the Chart.js instance, or the replay animation loop — confirmed in code
   (`static/js/views/market.js` always calls `mountMarketMap()` today; `static/js/charts.js:308`'s
   `renderMarketMotionChart` is exactly the function that throws "Canvas is already in use" if torn down and
   rebuilt carelessly). Policy: mount the map only the first time its tab is actually opened; once mounted, keep
   its DOM/controller alive across tab switches (don't refetch/rebuild); pause its requestAnimationFrame replay
   loop when its tab isn't active; call `chart.resize()` on reactivation (the map's own Expand overlay already
   does exactly this pattern — reuse it). The existing 90-second Live poll keeps running for ALL sections
   regardless of which tab is open, so the "New snapshot available" badge and scheduler status stay honest even
   while looking at Top 20 or Signals — only the heavy full-frame/table refresh is deferred to reactivation.
3. **Reuse the existing accessible tab pattern, don't invent a new one.** `market.js:278-289` already has a
   correct `role="tablist"`/`role="tab"`/`role="tabpanel"`, `aria-selected`, roving-tabindex, arrow-key
   implementation for Buy/Sell. The new page-level tabs copy this pattern exactly (verified against
   `dashboard.css`'s existing focus-ring and reduced-motion rules — nothing new needed there).
4. **Keep every existing DOM id/export.** `_signalTabsHTML`, `_activateSignalTab`, `_wireSignalTabs`,
   `_showBuySignal`, `buildBuyOpportunityPoints`, `marketMotionMount`/`marketMotionChart`/`marketMotionTable`, etc.
   all stay as-is; the reorg wraps existing render output in new tab panels rather than rewriting it. This is
   what keeps `tests/js/test_market_signal_tabs.js`, `test_market_signal_extras.js`, `test_market_scatter_points.js`,
   `test_market_motion*.js`, and `test_market_map_controller.js` passing with little or no change (both agents
   independently audited all `tests/js/test_market_*.js` files against this constraint).

## Disagreements, and how I resolved them (with evidence I checked myself)

### 1. Where do Market Breadth + SPY Regime go?
Codex: leave them in the always-visible header ("cheap enough to render with the scan").
Antigravity: move them into a tab, with real arithmetic: on the app's documented 900x600 minimum window, the
`.chart-wrap` donut is a fixed `height: 250px` (verified, `dashboard.css:162`) and `.grid-2` collapses to a single
column under 900px (verified, `dashboard.css:146`) — meaning Breadth and Regime would stack, not sit side by side,
consuming roughly 400+px combined, on top of the topbar/padding/stats-row already used. That alone would push the
tab bar itself off the bottom of the window on the app's own minimum supported size.
**Decision: Antigravity is right, verified independently.** Only the scan picker, source note, and the compact
5-tile stats row stay always-visible above the tabs. Market Breadth + SPY Regime move into the default
"Overview" tab, alongside the news sections (which were part of the scroll problem too and neither agent's
original brief scope called out but both correctly flagged as belonging in the reorg).

### 2. Nest Buy/Sell under a "Signals" tab, or promote them to two separate top-level tabs?
Codex: keep them nested one level inside a single "Signals" tab — reuses the existing, tested tablist verbatim,
represents a real parent/child relationship (two views of the same signal data), and is the lower-risk, less-churn
option.
Antigravity: promote Buy and Sell to their own top-level tabs — avoids "tabs inside tabs" and one extra click.
**Decision: Codex's nested approach.** The user's complaint was about vertical scrolling, not click depth, and
one level of nesting for two genuinely related sub-views (not three unrelated ones) isn't the "tabs inside tabs
inside an accordion" smell that's actually worth avoiding. It also means zero changes to
`static/js/views/market.js:278-289` and zero risk to its existing tests. Antigravity's flat alternative is cheap
to switch to later if this turns out to annoy in practice — noted, not built.

### 3. How is the active tab remembered — URL hash sub-route, or session state?
Codex: extend `router.js` to parse `#/market/map` etc., using `history.replaceState` (not a direct hash
assignment, which would fire `market.js`'s own `hashchange` listener and `router.js`'s `route()`, tearing
everything down) — deep-linkable and shareable.
Antigravity: don't touch the URL or `router.js` at all; keep the active tab in a module variable backed by
`sessionStorage` (`market:section`), restored on return to the view, reset on a fresh app launch.
**Decision: Antigravity's simpler approach.** This is a single-user local desktop app, not a multi-user web app —
shareable Market-tab URLs have little real value here, while Codex's own analysis correctly identifies that its
approach requires touching `router.js` (currently a single, simple hash-to-view lookup used by every view) and
getting a subtle replaceState-vs-hashchange distinction exactly right. Lower blast radius wins. `router.js` is
NOT modified by this sprint.

## Structure (final)

Always visible (above the tabs): source note, scan selector, stats row (Buy/Sell counts, top score, universe,
SPY phase).

Tabs, in this order:
1. **Buy Opportunity Map** (default) — the persistent tracker map exactly as it exists today: replay, filters,
   scheduler card, canvas, tracked-stocks table.
2. **Overview** — Market Breadth donut + SPY Regime card + the news sections.
3. **Top 20** — the combined-pool table.
4. **Signals** — the existing Buy/Sell tablist, unchanged.

Sub-detail on the map's own tracked-stocks table: Codex additionally recommends putting the 400+-row table behind
a closed-by-default disclosure (`<button aria-expanded>` or native `<details>`) inside the Map tab, building its
rows only on first expansion, rather than always rendering all of them the moment the tab opens. Adopted — this
is a real, additional, low-risk win on top of lazy-mounting the tab itself, and composes cleanly with tab-level
lazy mount (mounting the tab fetches data and shows the chart + count; opening the disclosure is what actually
builds several hundred table rows).

## Tasks

- MR-001 | Claude | `static/css/dashboard.css`: `.market-section-tabs`/`.market-section-tab` (mirrors
  `.signal-tabs` styling, horizontal-scroll at the 760px defensive breakpoint per both agents' CSS, no wrapping),
  `.market-section-panel[hidden]`, tracked-table disclosure styles. No template/sidebar changes — this stays a
  single view. Deps: none.
- MR-002 | Codex | `static/js/views/market.js`: wrap existing render output into the 4 panels above (move
  Breadth/Regime/news into "Overview", nothing else moves); add `_activateMarketSection(id)` (module state +
  sessionStorage, roving-tabindex/arrow-key wiring copied from `_wireSignalTabs`'s pattern); lazy-call
  `mountMarketMap()` only when the Map tab is first activated; keep the existing 90s Live poll running
  unconditionally for all sections. Deps: MR-001.
- MR-003 | Codex | `static/js/components/market-map.js`: add `setActive(bool)`/`suspend()`/`resume()` to the
  controller — pause the replay rAF and close any open Expand overlay on suspend; call `chart.resize()` and
  repaint once on resume; never destroy/recreate the Chart.js instance on a tab switch. Add the closed-by-default
  disclosure for the tracked-stocks table (count shown while closed; rows built on first expansion only). Deps:
  none (can run in parallel with MR-002; touches a different file).
- MR-004 | Claude | `_showMarketTicker`/the map's click-to-row handler: activate the Signals tab (and the Buy
  sub-tab) before scrolling/highlighting a row, since the row now lives inside a hidden panel until its tab is
  active. Deps: MR-002, MR-003.
- MR-005 | Codex | Tests: new `tests/js/test_market_sections.js` (tab switching, ARIA roles/roving tabindex,
  arrow/Home/End keys, sessionStorage restore, single lazy mount of the map, disclosure open-builds-rows-once).
  Update `test_market_map_component.js` only where it currently asserts every tracked row exists in the initial
  HTML (change to: count + closed disclosure initially, rows present after opening it). Run the FULL
  `tests/js/*.js` suite and confirm zero regressions in `test_market_signal_tabs.js`, `test_market_signal_extras.js`,
  `test_market_scatter_points.js`, `test_market_motion*.js`, `test_market_map_controller.js`,
  `test_market_default_scan.js` (both agents' test audits agree these should need no changes if MR-002/003 keep
  every existing id/export). Deps: MR-002, MR-003, MR-004.
- MR-006 | Claude | Verification: full JS suite + Python suite unaffected check, real ES-module graph load, and a
  real browser pass (the map's rAF-pause/resume and the "Canvas is already in use" risk specifically need eyes on
  a real Chart.js instance, not just Node DOM stubs). Deps: MR-005.

## Guardrails
No emoji. Never touch `position/`. `router.js` is explicitly OUT OF SCOPE for this sprint (see disagreement #3).
No two tasks touch `static/js/views/market.js` concurrently — MR-002 owns it alone; MR-003/MR-004/MR-005 wait on
it or touch different files. No commit/push without the user's go-ahead, matching every other sprint this session.
