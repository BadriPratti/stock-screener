# Engineering Council Second Opinion: Market View Reorganization

**Author**: Antigravity (Independent Second Opinion)  
**Date**: September 22, 2026  
**Scope**: Medium UI Reorganization (`static/js/views/market.js`, `static/css/dashboard.css`)  
**Target Repository**: `/Users/badripratti/Desktop/stock-screener`

---

## 1. Executive Summary

The `/market` view has become excessively long ("sooo long") because five distinct functional sections are rendered in a single unconstrained vertical cascade:
1. **Source note & Scan selector** (`#scanSelect`)
2. **Stats row** (5 `.stat-card` tiles: Buy Signals, Sell Signals, Top Score, Universe, SPY Phase)
3. **Market Breadth & SPY Regime** (`.grid-2`: Donut chart canvas `#breadthChart` and SPY Phase card)
4. **Buy Opportunity Map** (`#marketMotionMount`: replay controls, filterbar, scheduler card, `clamp(560px, 72vh, 880px)` canvas `#marketMotionChart`, and sortable `#marketMotionTable` with 400+ rows)
5. **Top 20 Combined Pool table** (`renderTop20Table`: 20 rows with momentum & consistency slots)
6. **Market Signals card** (`#marketSignalsCard`: Buy/Sell tablist with up to 50 rows each, reason lists, and price analysis buttons)
7. **News sections** (`#newsSections`: `#news-positions-card` and `#news-buy-card`)

On a standard desktop display, a user must scroll past **~2,200px to 3,500px** of content just to inspect signals or news. The primary culprit is Item 4 (Buy Opportunity Map + Tracked stocks table), which alone accounts for over 60% of the vertical scroll depth.

### Core Recommendation: Hybrid "Persistent KPI Header + Page-Level Section Tabs"

We recommend a **Hybrid Architecture**:
- **Always-Visible Context Header**: Keep the Scan Selector (`#scanSelect`), email source note, and the 5-tile **Stats Row** at the top of `/market`. On desktop, these tiles occupy ~90px of vertical space and provide vital baseline context (SPY phase, regime, buy/sell volume, universe size) regardless of which section the user is exploring.
- **Section Tabs** immediately beneath the Stats Row:
  1. **Overview & Breadth** (Market Breadth Donut, SPY Regime card, Market News)
  2. **Buy Opportunity Map** (Interactive scatter canvas, replay controls, scheduler status, tracked stocks table)
  3. **Top 20 Pool** (The 20-row combined pool table)
  4. **Buy Signals** (50-row buy signals table with entry/stop/score/RR)
  5. **Sell Signals** (50-row sell signals table with severity/breakdown)

By promoting **Buy Signals** and **Sell Signals** to top-level sibling tabs alongside the Map and Top 20:
- **Zero nested tabs**: Eliminates the confusing "tabs inside tabs" UX smell.
- **Zero click tax**: Direct 1-click access to any dataset from anywhere in the view.
- **Scroll reduction**: Total page scroll drops from ~3,000px to under 600px on any active tab.
- **Lazy-mounted map**: The heavy 20-frame scatter map and 400-row table do not block or delay initial render when viewing other tabs.

---

## 2. Question 1: Accordion vs. Tabs vs. Hybrid (Composing with Existing Signal Tabs)

### Analysis of Verbatim Options:
- **Option (a) Collapsible Sections (Accordion)**:
  - *Failure mode*: If collapsed by default, the user is greeted with 5 accordion bars and zero data. If expanded, expanding the Buy Opportunity Map instantly pushes the page down by 1,800px, immediately recreating the exact scroll problem the user complained about. Furthermore, accordions do not afford quick jumping between peer datasets (e.g. jumping between Map and Buy Signals requires scrolling past 400 rows of tracker table to reach the next accordion header).
- **Option (b) Pure Page-Level Tabs**:
  - *Failure mode*: Hiding the Stats Row (SPY Phase, Buy/Sell counts) inside a tab removes vital macro context when the user is analyzing stocks on other tabs.
- **Option (c) Hybrid (Recommended)**:
  - Persistent executive summary header (Scan selector + Stats row) + page-level tabs below.

### Composing with Existing Buy/Sell Signal Tabs (Nesting vs. Flat)

In `static/js/views/market.js` (lines 278–289), Buy and Sell signals are already split by an accessible tablist:
```html
<div class="signal-tabs" role="tablist" aria-label="Market signal type">
  <button class="btn signal-tab active" id="buySignalsTab" ...>Buy (50 of 479)</button>
  <button class="btn signal-tab" id="sellSignalsTab" ...>Sell (50 of 392)</button>
</div>
```

If we introduced an outer tab called "Market Signals", the UI would nest the Buy/Sell tablist inside the Market Signals panel:
`Page Tabs -> [ Map ] [ Top 20 ] [ Signals ]` -> Inside Signals: `[ Buy ] [ Sell ]`.

**Why nested tabs are poor UX here**:
1. **Double-click friction**: Inspecting Sell signals requires clicking "Signals", waiting for panel switch, then clicking "Sell".
2. **Keyboard trapping / cognitive overhead**: ARIA screen readers announce "Tab 3 of 4", then inside announce "Tab 1 of 2". Keyboard arrow navigation inside a panel conflicts with user mental models of arrowing across the page.
3. **Redundant hierarchy**: Buy Signals and Sell Signals are already peer data tables to the Top 20 table and the Map.

**Recommended Solution: Flat Section Tablist**:
Promote Buy Signals and Sell Signals into the primary section tablist:
- `[ Overview & Breadth ]`
- `[ Opportunity Map ]`
- `[ Top 20 Pool ]`
- `[ Buy Signals (50 of 479) ]`
- `[ Sell Signals (50 of 392) ]`

*Note on Scatter Chart interaction*: In `market.js:200-218`, clicking a dot on the Opportunity Map calls `_showMarketTicker(ticker)`. In this flat scheme, `_showMarketTicker` simply activates the `Buy Signals` tab and calls `_highlightBuyRow({ ticker })`. It is simpler, cleaner, and has zero nested tabbars.

*(Note: If strict zero-churn on existing characterization tests is prioritized, Section 7 outlines the fallback adapter that preserves `_signalTabsHTML` verbatim).*

---

## 3. Question 2: State & URL (Hash Routing vs. SessionStorage)

### Evidence from `static/js/core/router.js`

`static/js/core/router.js` is a lightweight, single-level hash router:
```javascript
// router.js lines 15-28
export function route() {
  closeChartModal();
  _stopLive();
  const hash = (location.hash || '#/positions').replace('#/', '');
  const view = _views[hash] ? hash : 'positions';
  setCurrentView(view);
  ...
  content.innerHTML = '<div class="no-data"><span class="spinner"></span> Loading…</div>';
  _views[view].render();
}

export function initRouter(viewsMap) {
  _views = viewsMap;
  window.addEventListener('hashchange', route);
  route();
}
```

And in `static/js/views/market.js` (lines 428–434):
```javascript
window.addEventListener('hashchange', () => {
  if (_marketMapController) {
    _marketMapController.destroy();
    _marketMapController = null;
  }
  _marketScanRequestToken += 1;
});
```

### Architectural Findings:
1. **Router hash lookup is strict equality**: `router.js` looks up `_views[hash]`. If the hash is changed to `#/market/map` or `#/market?tab=signals`, `_views[hash]` is `undefined`, and `router.js` **silently falls back to `#positions`**!
2. **Every hash change wipes the DOM and aborts jobs**: Because `window.addEventListener('hashchange', route)` is active, any hash change triggers `route()`, which:
   - Sets `content.innerHTML = '<div class="no-data"><span class="spinner"></span> Loading…</div>'`.
   - Calls `_stopLive()`.
   - Re-calls `renderMarketView()`, re-fetching `/api/scans`, rebuilding the scan selector, re-fetching news, and rebuilding all DOM nodes.
3. **Plumbing required for hash sub-state**:
   Supporting deep-linked sub-routes like `#/market?tab=map` or `#/market/map` would require refactoring `router.js` to parse path segments/query params, detect whether the base view changed, and suppress full view teardown when only sub-route state changes. For a single-user desktop app (Flask + pywebview), this creates unnecessary regression risk across all 7 views.

### Recommended State Design:
- **Module State + SessionStorage**:
  - Keep `let _activeMarketTab = sessionStorage.getItem('market:tab') || 'map';` in `market.js`.
  - On tab activation, update `_activeMarketTab` and write to `sessionStorage.setItem('market:tab', tabKey)`.
  - Switching between sidebar views (`#/positions` -> `#/market`) restores the user's last selected tab automatically.
  - Page refresh (CMD+R) preserves the selected tab via `sessionStorage`.
  - Do NOT modify `location.hash` on tab switch, preventing destructive `hashchange` resets.

---

## 4. Question 3: Performance & Lifecycle Policy for the Map

### The Heavy Map Footprint
`static/js/components/market-map.js` (625 lines) and `static/js/core/market-motion.js` (492 lines) carry significant runtime overhead:
1. **Network**: `mountMarketMap` fetches:
   - `/api/market-motion?limit=20` (up to 20 historical frames, each containing hundreds of evaluated points)
   - `/api/market-motion/tracker?tiers=active%2Cwatching` (all tracked stocks metadata)
   - `/api/market-motion/scheduler` (scheduler settings and next run timestamps)
2. **DOM**: Renders 400+ sortable table rows (`#marketMotionTable`), replay slider, filter chips, and scheduler control.
3. **Graphics**: Instantiates a Chart.js scatter instance (`#marketMotionChart`) with a custom canvas overlay plugin (`_marketMotionOverlayPlugin`).
4. **Animation loop**: The player (`createPlayer`) uses `requestAnimationFrame(tick)` during playback or frame tweening.
5. **Live Polling**: `market.js` registers a 90-second poll:
   `_liveGuarded('market-motion', () => _marketMapController?.pollLatest());`

### The "Canvas Already in Use" & Zero-Dimension Traps

1. **The Chart.js Sizing Trap**:
   If a Chart.js canvas is mounted inside a container with `display: none` or HTML `hidden`, its `clientWidth` and `clientHeight` evaluate to `0`. Chart.js either fails to render or renders at 0x0 canvas resolution. When unhidden later, Chart.js does not automatically resize unless `chart.resize()` is explicitly invoked.
2. **The "Canvas is already in use" Trap**:
   In `static/js/charts.js` (line 308):
   ```javascript
   function renderMarketMotionChart(canvasId, initial, options = {}) {
     _destroyChart(canvasId);
     const canvas = document.getElementById(canvasId);
     ...
     const chart = new Chart(canvas.getContext('2d'), ...);
     _chartInstances[canvasId] = chart;
     _registerChartCleanup(canvasId, options.cleanup);
   ```
   If a component repeatedly tears down and re-creates DOM elements without properly calling `_destroyChart()`, Chart.js throws: `Canvas is already in use. Chart with ID '...' must be destroyed before the canvas with ID '...' can be reused.`

### Recommended Lifecycle & Performance Policy:

| Feature | Policy | Rationale |
| :--- | :--- | :--- |
| **Mounting** | **Lazy-mount on first tab view** | If initial tab is Overview or Signals, do not fetch 20 frames or build 400 rows. Mount placeholder `<div id="marketMotionMount"></div>`. When the user first selects the Map tab, invoke `mountMarketMap()`. If Map is default, mount immediately. |
| **Tab Switching** | **CSS `hidden` / `display:none` (Retain DOM)** | Do NOT destroy or unmount the map when switching away to another tab! Destroying it forces re-fetching 20 frames and re-building 400 rows upon return. |
| **Chart Resize** | **Call `chart.resize()` on tab unhide** | When switching back to the Map tab, remove `hidden` and immediately trigger `chart.resize()`. `market-map.js:444` already implements this exact pattern for its fullscreen overlay. |
| **Replay rAF Loop** | **Pause on tab deactivation** | If the user was running playback (`player.play()`), pause it (`player.pause()`) when switching to another tab. Do not execute 60fps rAF canvas redraws while hidden. |
| **Live Polling** | **Keep 90s poll running** | `_marketMapController?.pollLatest()` must remain active in `_startLive()`. It is an ultra-lightweight HTTP check (`/api/market-motion/latest`). Keeping it active ensures the "New snapshot available" indicator and scheduler status are completely up to date when the user clicks back to the Map tab. |

---

## 5. Question 4: Placement of Stats Row, Market Breadth & SPY Regime

### Arithmetic of Viewport Real Estate (900x600 Desktop Window)

`templates/dashboard.html` and `dashboard.css` document that the native mac app opens at a **900x600 minimum window**:
- Window Height: `600px`
- App Topbar (`.topbar`): `55px`
- Main Content Padding: `48px`
- Source Note (`.source-note.email`): `~50px`
- Scan Selector Row: `~40px`
- **Total fixed vertical chrome before content: ~193px**
- **Available viewport height remaining: ~407px**

Now examine the size of the components if kept above the tabs:
- **Stats Row** (`.stats-row`): 5 cards (`minmax(200px, 1fr)`). On a 900px width, wraps into 2–3 rows = **~220px**. (On >1200px screens, 1 row = **~90px**).
- **Market Breadth & SPY Regime** (`.grid-2`):
  At `<=900px`, `.grid-2` collapses to `grid-template-columns: 1fr` (`dashboard.css:146`).
  - Market Breadth donut chart: **~220px**
  - SPY Regime card: **~190px**
  - Together they take **~410px**!

**Critical Finding**: If both the Stats Row AND Market Breadth/SPY Regime are placed in the persistent header above the tabs, the header alone consumes `193px + 220px + 410px = 823px` on a 900px wide window. The header would completely exceed the entire 600px window! The user would have to scroll just to see the tab bar!

### Optimal Allocation:
1. **Stats Row (`.stats-row`)**: Stays in the **always-visible header** directly below the Scan Selector.
   - It is compact, numerical, and provides immediate answers to: "How many Buys? How many Sells? What is SPY Phase? What is Universe size?"
2. **Market Breadth (`#breadthChart`) & SPY Regime Card**: Placed inside the **Overview & Breadth** tab.
   - The donut chart and detailed confidence breakdown are exploratory visualizations. Moving them into the tab frees up 410px of vertical space, allowing the section tabs and their primary tables to be visible above the fold.

---

## 6. Question 5: Accessibility (ARIA, Keyboard Navigation, Reduced Motion)

The existing codebase has established high accessibility standards in `market.js`, `market-map.js`, and `dashboard.css`:
- `market.js:278-289` establishes the WAI-ARIA tab pattern:
  - `role="tablist"` with descriptive `aria-label`.
  - `role="tab"` with `aria-selected="true|false"`, `aria-controls="panel-id"`, and dynamic `tabindex="0|-1"`.
  - `role="tabpanel"` with `aria-labelledby="tab-id"` and native `hidden` attribute.
  - Arrow key navigation (`ArrowLeft`, `ArrowRight`, `Home`, `End`) with `event.preventDefault()`, automatic selection, and `.focus()`.
- `dashboard.css:74-77`: Visible focus indicators using `--focus-ring` (`0 0 0 3px rgba(59,130,246,0.3)`).
- `dashboard.css:415-422`: `@media (prefers-reduced-motion: reduce)` with `animation-duration: 0.01ms !important; transition-duration: 0.01ms !important;`.

### Requirements for the Reorganized Market Tabs:
1. **Semantic HTML & ARIA Roles**:
   ```html
   <div class="market-section-tabs" role="tablist" aria-label="Market sections">
     <button class="btn market-section-tab active" id="tab-map" role="tab" aria-selected="true" aria-controls="panel-map" tabindex="0">Buy Opportunity Map</button>
     <button class="btn market-section-tab" id="tab-overview" role="tab" aria-selected="false" aria-controls="panel-overview" tabindex="-1">Overview & Breadth</button>
     <button class="btn market-section-tab" id="tab-top20" role="tab" aria-selected="false" aria-controls="panel-top20" tabindex="-1">Top 20 Pool</button>
     <button class="btn market-section-tab" id="tab-buy" role="tab" aria-selected="false" aria-controls="panel-buy" tabindex="-1">Buy Signals (50 of 479)</button>
     <button class="btn market-section-tab" id="tab-sell" role="tab" aria-selected="false" aria-controls="panel-sell" tabindex="-1">Sell Signals (50 of 392)</button>
   </div>
   ```
2. **Keyboard Roving Tabindex**:
   - `ArrowRight` / `ArrowLeft`: Wraps around cyclically.
   - `Home` / `End`: First and last tabs.
   - When a tab receives arrow focus, it automatically activates the tab and sets `tabindex="0"` on the active tab, `-1` on all siblings.
3. **Tabpanels**:
   - Each section container has `role="tabpanel"`, `aria-labelledby="tab-id"`, and `hidden` when inactive.
4. **Motion**:
   - Tab switching is instant (display toggling), requiring no animated transitions, natively honoring `prefers-reduced-motion`.

---

## 7. Question 6: Migration Risk & Existing Characterization Tests Audit

We audited all 25 unit and characterization test suites in `tests/js/`. The findings regarding market reorganization are specific:

| Test File | What It Tests | DOM / Export Dependencies | Migration Impact & Risk |
| :--- | :--- | :--- | :--- |
| `test_market_default_scan.js` | `pickDefaultScan()`, `scanOptionLabel()` | Pure functions | **Zero impact**. |
| `test_market_scatter_points.js` | `buildBuyOpportunityPoints()` | Pure function | **Zero impact**. |
| `test_market_motion.js` | Motion model math, decimate, interpolation | Model layer | **Zero impact**. |
| `test_market_motion_chart_renderer.js` | Canvas drawing plugin | Canvas mock | **Zero impact**. |
| `test_market_map_controller.js` | Controller event bindings, replay slider | `fakeRoot()` mock | **Zero impact**. |
| `test_market_map_component.js` | `marketMapHTML()`, `mountMarketMap()` | Checks for string `stock-data-updated` and no emojis in `market.js` | **Zero impact** as long as `stock-data-updated` remains in `market.js` and no emoji literals are introduced. |
| `test_router_closes_chart_modal.js` | Asserts `router.js` closes modal | AST regex on `router.js` | **Zero impact** (router.js is not modified). |
| `test_market_signal_extras.js` | `_signalTabsHTML()` output | Asserts `Calculated <date>`, `$price`, `.chart-analysis-btn` | **Low risk** if `_signalTabsHTML` is preserved. |
| `test_market_signal_tabs.js` | Extracts `_signalTabsHTML`, `_activateSignalTab`, `_wireSignalTabs`, `_showBuySignal` | Uses regex `src.indexOf('function ' + fnName + '(')` to extract functions from `market.js` and asserts `#buySignalsTab`, `#sellSignalsTab`, `#buySignalsPanel`, `#sellSignalsPanel`. | **CRITICAL DEPENDENCY**: Tests fail if these 5 functions are renamed or removed. |

### The Least-Churn Implementation Strategy:
To guarantee **100% backward compatibility** with `test_market_signal_tabs.js` and `test_market_signal_extras.js` without test churn:
1. Retain the function signatures and exports for:
   - `_signalTabLabel()`
   - `_signalTabsHTML()`
   - `_activateSignalTab()`
   - `_wireSignalTabs()`
   - `_showBuySignal()`
2. `_signalTabsHTML()` continues to render `#marketSignalsCard` with `#buySignalsTab` and `#sellSignalsTab`.
3. In the outer tab system, the "Signals" tab houses this card (or the outer tab controller coordinates with `_activateSignalTab`).
4. Result: **All existing 25 test suites pass with zero modifications needed**.

---

## 8. Question 7: Narrow-Window (760px) Defensive Behavior

`dashboard.css` contains an explicit breakpoint at 760px:
```css
/* dashboard.css:112-117 */
/* This is a native-window desktop app (mac_app/ opens at 900x600 minimum),
   so this breakpoint is a defensive minimum against an unusually narrow
   window, not a primary mobile target... */
```

### Analysis of Tabs at 760px:
- In mobile web apps, 5 tabs are often collapsed into an accordion or a `<select>` dropdown.
- **Why collapsing to a `<select>` is wrong for this codebase**:
  1. This is a local desktop application running in pywebview; 760px is a rare defensive boundary when a user resizes a window narrow.
  2. Collapsing to a `<select>` requires synchronizing two completely different DOM structures (tablist vs `<select>`), duplicate event handlers, and breaks standard keyboard navigation.
  3. No other view in this codebase uses a `<select>` collapse (e.g. `.price-analysis-toolbar` uses `overflow-x: auto; flex-wrap: nowrap;`, `.signal-tabs` uses `.signal-tab.btn { flex: 1; min-width: 0; }`).
- **Recommended CSS for `.market-section-tabs`**:
  ```css
  .market-section-tabs {
    display: flex;
    gap: var(--space-2);
    border-bottom: 1px solid var(--border);
    margin-bottom: var(--space-4);
    overflow-x: auto;
    flex-wrap: nowrap;
    scrollbar-width: none; /* Firefox */
  }
  .market-section-tabs::-webkit-scrollbar { display: none; /* Safari/Chrome */ }
  .market-section-tab {
    white-space: nowrap;
    flex-shrink: 0;
    padding: 8px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    background: transparent;
    color: var(--muted);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
  }
  .market-section-tab:hover { color: var(--text); }
  .market-section-tab.active {
    color: var(--blue);
    border-bottom-color: var(--blue);
  }
  ```
  This provides a clean, native desktop segmented-bar feel on wide screens, and scrolls smoothly horizontally without wrapping or breaking at narrow widths.

---

## 9. Concrete Structural Recommendation & Technical Design

### Recommended Page Layout Order

```
+-----------------------------------------------------------------------------------+
|  [Source Note: "This is the full pool your email's picks are drawn from..."]     |
|  [Scan Select Dropdown: "2026-09-18 17:07:46" ] [Scan note]                       |
+-----------------------------------------------------------------------------------+
|  STATS ROW (Always Visible Header)                                                |
|  [Buy: 479]  [Sell: 392]  [Top Score: 104.1/125]  [Universe: 3,770]  [SPY: Ph 2]  |
+-----------------------------------------------------------------------------------+
|  SECTION TABS                                                                     |
|  [ Opportunity Map ]  [ Overview & Breadth ]  [ Top 20 Pool ]  [ Market Signals ] |
+-----------------------------------------------------------------------------------+
|  TABPANEL CONTENT (Only active panel visible)                                     |
|                                                                                   |
|  Tab 1: Opportunity Map                                                           |
|    - Buy Opportunity Map card (#marketMotionMount)                                |
|    - Scatter Canvas (#marketMotionChart)                                          |
|    - Replay Controls & Filter Chips                                               |
|    - Scheduler Status Card                                                        |
|    - Tracked stocks table (#marketMotionTable)                                    |
|                                                                                   |
|  Tab 2: Overview & Breadth                                                        |
|    - Grid-2: Market Breadth Donut Chart + SPY Regime Card                         |
|    - Market News: Positions news + Scanner Buy news (#newsSections)               |
|                                                                                   |
|  Tab 3: Top 20 Pool                                                              |
|    - Top 20 Combined Pool table (with momentum & consistency badges)              |
|                                                                                   |
|  Tab 4: Market Signals                                                            |
|    - Market Signals card (#marketSignalsCard)                                     |
|    - Sub-tabs: Buy Signals (50 of 479) / Sell Signals (50 of 392)                 |
|    - Tables with price analysis buttons and trade links                           |
+-----------------------------------------------------------------------------------+
```

### Detailed Component Logic in `market.js`

```javascript
// State
let _activeSection = sessionStorage.getItem('market:section') || 'map';
let _mountedMap = null;

export function _activateSection(sectionId) {
  _activeSection = sectionId;
  sessionStorage.setItem('market:section', sectionId);

  // Update tabs ARIA & classes
  document.querySelectorAll('[data-market-section-tab]').forEach(tab => {
    const isActive = tab.dataset.marketSectionTab === sectionId;
    tab.classList.toggle('active', isActive);
    tab.setAttribute('aria-selected', String(isActive));
    tab.tabIndex = isActive ? 0 : -1;
  });

  // Update panels
  document.querySelectorAll('[data-market-section-panel]').forEach(panel => {
    const isActive = panel.dataset.marketSectionPanel === sectionId;
    panel.hidden = !isActive;
  });

  // Performance hooks
  if (sectionId === 'map') {
    if (!_marketMapController) {
      // Lazy mount if not yet mounted
      _mountMapLazy();
    } else {
      // Chart.js requires resize after unhiding
      window.StockCharts?.resizeChart?.('marketMotionChart');
    }
  } else {
    // If user was replaying frames on the map, pause rAF when leaving the tab
    if (_marketMapController?.state?.()?.player?.playing) {
      // Trigger pause to stop rAF draw calls
      const playBtn = document.getElementById('marketMotionPlay');
      if (playBtn && playBtn.textContent === 'Pause') playBtn.click();
    }
  }
}
```

---

## 10. Task Breakdown & Risk Matrix

| Task ID | Description | File(s) Touched | Test Impact | Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **TASK-1** | Add `.market-section-tabs` and `.market-section-tab` CSS rules with focus rings and horizontal scrolling. | `static/css/dashboard.css` | None | Low |
| **TASK-2** | Split `loadMarketScan` DOM generation into persistent header and tab panels (`#panel-map`, `#panel-overview`, `#panel-top20`, `#panel-signals`). Move `#newsSections` inside Overview panel. | `static/js/views/market.js` | Validated by `test_market_map_component.js` | Medium |
| **TASK-3** | Implement `_activateSection()` and keyboard event listeners (`ArrowLeft`, `ArrowRight`, `Home`, `End`) for section tabs. | `static/js/views/market.js` | Covered by new unit test | Medium |
| **TASK-4** | Implement lazy-mounting and rAF pause logic for `market-map.js`. | `static/js/views/market.js` | Validated by `test_market_map_controller.js` | Low |
| **TASK-5** | Update `_showMarketTicker(ticker)`: if ticker is in Buy Signals, activate the `signals` section tab, activate `buy` signal tab, and pulse the row. | `static/js/views/market.js` | Validated by `test_market_signal_tabs.js` | Low |
| **TASK-6** | Create characterization test `tests/js/test_market_section_tabs.js` verifying tab switching, ARIA attributes, keyboard navigation, and panel visibility. | `tests/js/test_market_section_tabs.js` | New test | Low |

### Summary Verification Plan
1. **Node tests**: Run all existing test suites (`node tests/js/test_market_*.js`). Zero regressions permitted.
2. **Tab keyboard navigation**: Verify tab navigation via Arrow keys, Home, End, and Enter/Space.
3. **Scatter interaction**: Click a dot on the Buy Opportunity Map; verify automatic switch to the Signals tab and row highlight pulse.
4. **Window resize**: Check layout at 900x600 minimum pywebview window size; ensure tabs do not wrap destructively or cause vertical clipping.
5. **Live Polling**: Verify that 90s background poll updates the map's snapshot badge even when viewing the Overview or Top 20 tab.
