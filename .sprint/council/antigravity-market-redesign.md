Here is an independent Engineering Council investigation and design proposal for the requested Market view redesign.

---

# Engineering Council Design Proposal: Market View Interactive Dot-Plot & Tabbed Signals

## 1. Understanding of the Requests & Dot-Plot Arrangement

### The User’s Core Needs
1. **Interactive Dot Plot ("Huge interact chart like a dot plot... buy or momentum kind of deal... keep market breadth")**:
   The user wants an expansive, bird's-eye visual landscape of all candidate stocks instead of immediately confronting hundreds of tabular rows. Hovering over any dot must identify the stock, while keeping the high-level macro context (Market Breadth donut and SPY regime).
2. **Tabbed Signal Lists ("Don't want constantly scrolling down for buy and sell... create a button Buy and Sell")**:
   Presently, `market.js` stacks the entire Buy Signals table and the entire Sell Signals table vertically. In a typical scan (e.g., the latest scan in the repo), there are **479 buy signals** and **392 sell signals** — a total of **871 table rows**. Users must scroll past hundreds of rows to reach the sell signals or news. The user wants a clean button/tab toggle between Buy and Sell signals in a single unified view.

---

### Chart Arrangement & Axis Selection

Given the fields actually available in `buy_signals` (`score` 0–125, `rs` Relative Strength vs. SPY, `rr_ratio`, `entry_quality`, `volume_ratio`, `stop_loss`, `rank`):

| Dimension | Metric | Rationale & Domain Semantics |
| :--- | :--- | :--- |
| **X-Axis** | **Relative Strength (`rs`)** | **The "Momentum" Axis**. In Stage Analysis & CANSLIM, Relative Strength is *the* momentum indicator. Centered around `0.0` (outperforming SPY to the right, underperforming to the left). A subtle vertical dashed reference line at `x = 0` splits market leaders from laggards. |
| **Y-Axis** | **Screener Score (`score`)** | **The "Buy Setup Quality" Axis**. Typically ranges from 70 to 125. Higher values represent higher conviction technical + fundamental setups. |
| **Dot Color** | **`entry_quality`** | Encodes actionable timing: **Green** (`var(--color-success)`) for `Good`, **Yellow** (`var(--color-warning)`) for `Extended`, **Red** (`var(--color-danger)`) for `Poor`. |
| **Dot Size / Opacity** | **Fixed Radius (5.5px) + 0.65 Alpha** | Semi-transparent fills (`rgba(..., 0.65)`) with a 1px solid stroke allow overlapping clusters of stocks to show natural density without visual clutter. |

#### Quadrant Semantics:
```
                 High Score (Quality)
                          ▲
    Top-Left:             │    Top-Right: PRIME BUY SETUPS
    Solid Base / Coiling  │    ★ High RS Momentum + High Setup Score
    (Awaiting breakout)   │    (Focus of breakout trading)
                          │
  ────────────────────────┼────────────────────────► RS (Momentum)
  RS < 0 (Lagging SPY)    │    RS > 0 (Leading SPY)
                          │
    Bottom-Left:          │    Bottom-Right:
    Marginal / Watchlist  │    Extended Runners / Speculative
                          │
```

---

## 2. Visual Hierarchy & Placement in the View

The user explicitly requested: *"keep the the market breadth and stuff like that"*. The macro breadth context must remain prominent.

### Proposed Page Layout (Top to Bottom):
1. **Source Note & Scan Selector** (`#scanSelect` dropdown).
2. **Stats Row** (5 cards: Buy Signals Count, Sell Signals Count, Top Score, Universe Analyzed, SPY Phase).
3. **Macro Market Grid (`.grid-2`)**:
   - **Market Breadth Donut Chart** (Phase 1–4 distribution).
   - **SPY Regime Card** (Phase, Trend, Confidence %).
4. **NEW: Buy Opportunity Landscape (Full-Width Card, 420px height)**:
   - Full-width card housing the interactive Chart.js scatter plot.
   - Placed directly below the Macro Grid and directly above the Top 20 table.
   - *Why here?* It follows the natural trading decision funnel: **Macro Market Health (Breadth) $\rightarrow$ Visual Opportunity Landscape (Scatter Plot) $\rightarrow$ Top 20 Shortlist $\rightarrow$ Full Tabbed Signal Registry**.
5. **Top 20 Table** (Curated top 20 with live momentum status badges and news links).
6. **Unified Signal Registry Card** (Button-toggled Buy vs. Sell table, described in Section 4).
7. **News Sections** (Positions news & Buy picks news).

---

## 3. Hover & Click Interactions

### Hover Interaction (Custom Chart.js Tooltip)
Chart.js canvas tooltips are styled to match the dark dashboard theme (`surfaceRaised`, `borderDefault`, `font-family-sans`):

```
┌──────────────────────────────────────────────┐
│ NVDA  •  Good Entry                          │
├──────────────────────────────────────────────┤
│ Rank: #2  |  Score: 114.0 / 125              │
│ Relative Strength (RS): +0.570 (vs SPY)      │
│ Risk/Reward: 4.5:1 (Stop: $10.58)            │
│ Reddit Mentions (24h): 14                    │
│ Key Driver: Strong Stage 2 breakout over 50D │
└──────────────────────────────────────────────┘
```
- **Tooltip Title**: `${ticker} · ${entry_quality} Entry`
- **Body Items**: Score & Rank, RS with sign prefix (`+`), Risk/Reward ratio and stop-loss price, Reddit 24h count, and the primary setup reason (`cleanEmoji(reasons[0])`).

### Click Interaction: Jump & Highlight Table Row
- **Action**: Clicking a dot smoothly scrolls the page to that ticker's row in the table below and triggers a 2-second glowing row-pulse animation (`.row-highlight-pulse`).
- **Tab Auto-Switch**: If the user is currently viewing the "Sell Signals" tab when clicking a dot, the view automatically activates the "Buy Signals" tab first, then scrolls to and highlights the row.
- **Why NOT open the Fidelity link directly on click?**
  In a dense scatter plot with 400+ dots, accidental clicks during hover/inspection are frequent. Spawning external broker windows without confirmation is jarring and disruptive. Jumping to the row allows the user to inspect the full breakdown (all 7 reasons, fundamental snapshot, stop loss) and intentionally click the Fidelity trade button.
- **Hint**: A small subtitle below the chart title: *"Tip: Hover to preview setup details • Click any dot to locate in the table below"*.

---

## 4. Implementation of the Buy/Sell Button-Toggled List

### Segmented Control / Tab UI Pattern
Replace the two stacked cards (`<div class="card"><h2>Buy Signals</h2>...</div>` and `<div class="card"><h2>Sell Signals</h2>...</div>`) with a single **Signal Registry** card featuring a segmented button group in the header:

```html
<div class="card signal-registry-card">
  <div class="signal-header-row">
    <h2>Market Signals</h2>
    <div class="tab-group" role="tablist" aria-label="Signal Type">
      <button role="tab" id="tabBtnBuy" class="tab-btn active buy" aria-selected="true" aria-controls="panelBuySignals">
        Buy Signals <span class="tab-count-badge">${buyCount}</span>
      </button>
      <button role="tab" id="tabBtnSell" class="tab-btn sell" aria-selected="false" aria-controls="panelSellSignals">
        Sell Signals <span class="tab-count-badge">${sellCount}</span>
      </button>
    </div>
  </div>
  
  <div id="panelBuySignals" role="tabpanel" aria-labelledby="tabBtnBuy">
    <!-- Buy table HTML -->
  </div>
  <div id="panelSellSignals" role="tabpanel" aria-labelledby="tabBtnSell" hidden>
    <!-- Sell table HTML -->
  </div>
</div>
```

### DOM Rendering Strategy: Up-Front Render + DOM Visibility Toggle
- **Both tables are rendered into the DOM during scan load**, with `#panelSellSignals` hidden via `hidden` (or `display: none`).
- **Rationale**:
  1. All data is already fetched in one single `/api/scan` response.
  2. Tab switching is instantaneous (0ms layout reflow, no string serialization or innerHTML repainting).
  3. Clicking a dot on the scatter chart can immediately find `document.getElementById(`row-buy-${ticker}`)` without waiting for an asynchronous render cycle.
  4. Preserves user interaction state (e.g., expanded reasons rows stay expanded when switching tabs).

### Scatter Chart vs. Tab Interaction
- **The Scatter Chart is dedicated to Buy Signals**:
  In `dashboard.py` (lines 238–256), `rs`, `entry_quality`, and `rr_ratio` are **only parsed for Buy Signals**. Sell signals in the backend do not have `rs` or entry qualities parsed. Furthermore, sells are breakdown risk events (Phase 4), whereas the user explicitly asked for a *"buy or momentum kind of deal"*.
- **Independence**: The scatter plot remains visible as the Buy Opportunity Landscape regardless of which tab is selected below. If the user clicks a dot while the Sell tab is open, it auto-switches the tab back to Buy and focuses the row.

---

## 5. Relevant Files & Modules to Touch

| File | Purpose of Change |
| :--- | :--- |
| `static/js/charts.js` | Add `renderMarketScatterChart(canvasId, buySignals, onDotClick)`. Manage Chart.js instance destruction via `_destroyChart(canvasId)`. Follow existing design-token pattern (`_token`). |
| `static/js/views/market.js` | Update `loadMarketScan()` DOM template: insert scatter chart container, replace stacked cards with tabbed header + two tab panels, attach tab switching listeners, and attach row IDs (`row-buy-${s.ticker}`). |
| `static/css/dashboard.css` | Add `.scatter-chart-wrap` (height 420px), `.signal-header-row`, `.tab-group`, `.tab-btn`, `.tab-btn.active`, and `@keyframes row-highlight-pulse`. |

*(Note: No backend Python changes are required; all required fields exist in `/api/scan`).*

---

## 6. Recommended Concrete Implementation Approach

### Step 1: Chart Helper in `static/js/charts.js`
Add `renderMarketScatterChart` using Chart.js's native `'scatter'` type:
```javascript
function renderMarketScatterChart(canvasId, signals, onDotClick) {
  _destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  // Filter out any signals with missing numeric coordinates
  const valid = (signals || []).filter(s => typeof s.score === 'number' && typeof s.rs === 'number');
  if (!valid.length) return;

  const ctx = canvas.getContext('2d');
  
  // Map points to Chart.js scatter format {x, y} with custom metadata
  const points = valid.map(s => ({
    x: s.rs,
    y: s.score,
    signal: s,
  }));

  // Color by entry quality using token fallbacks
  const colorMap = {
    good: 'rgba(34, 197, 94, 0.75)',     // var(--color-success)
    extended: 'rgba(234, 179, 8, 0.75)', // var(--color-warning)
    poor: 'rgba(239, 68, 68, 0.75)',     // var(--color-danger)
  };
  const borderMap = {
    good: CHART_COLORS.success,
    extended: CHART_COLORS.warning,
    poor: CHART_COLORS.danger,
  };

  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Buy Signals',
        data: points,
        backgroundColor: points.map(p => colorMap[(p.signal.entry_quality || '').toLowerCase()] || 'rgba(59, 130, 246, 0.75)'),
        borderColor: points.map(p => borderMap[(p.signal.entry_quality || '').toLowerCase()] || CHART_COLORS.accent),
        borderWidth: 1.5,
        pointRadius: 5.5,
        pointHoverRadius: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (e, elements) => {
        if (elements.length && onDotClick) {
          const item = points[elements[0].index];
          onDotClick(item.signal);
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Relative Strength (RS vs SPY) ➔ Momentum', color: CHART_COLORS.textSecondary, font: { family: CHART_FONT_FAMILY, size: CHART_LABEL_SIZE } },
          ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } },
          grid: { color: (ctx) => ctx.tick.value === 0 ? 'rgba(255, 255, 255, 0.3)' : CHART_COLORS.borderDefault, lineWidth: (ctx) => ctx.tick.value === 0 ? 1.5 : 1 },
        },
        y: {
          title: { display: true, text: 'Screener Score ➔ Conviction', color: CHART_COLORS.textSecondary, font: { family: CHART_FONT_FAMILY, size: CHART_LABEL_SIZE } },
          ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } },
          grid: { color: CHART_COLORS.borderDefault },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => {
              const s = items[0].raw.signal;
              return `${s.ticker} · ${s.entry_quality || 'Neutral'} Entry`;
            },
            label: (item) => {
              const s = item.raw.signal;
              return [
                `Score: ${s.score}/${s.max_score || 125} (Rank #${s.rank})`,
                `RS: ${s.rs > 0 ? '+' : ''}${s.rs.toFixed(3)} | R:R: ${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : 'N/A'}`,
                `Stop Loss: $${s.stop_loss ? s.stop_loss.toFixed(2) : '-'} | Reddit: ${s.reddit_mentions || 0}`,
                s.reasons && s.reasons[0] ? `Key: ${s.reasons[0]}` : '',
              ].filter(Boolean);
            },
          },
        },
      },
    },
  });
}
```

### Step 2: Tab Logic & Dot Click Handler in `static/js/views/market.js`
1. Tag each row with an ID in `renderBuyRows`: `<tr id="row-buy-${s.ticker}">`.
2. Connect dot click to row highlight:
```javascript
function focusBuyRow(ticker) {
  // Ensure Buy tab is active
  switchSignalTab('buy');
  const row = document.getElementById(`row-buy-${ticker}`);
  if (row) {
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    row.classList.remove('row-highlight-pulse');
    void row.offsetWidth; // trigger DOM reflow for re-animation
    row.classList.add('row-highlight-pulse');
  }
}
```
3. Wire tab button clicks (`switchSignalTab('buy' | 'sell')`) updating `aria-selected`, CSS classes, and toggling `hidden` on the two panels.

### Step 3: CSS Styles in `static/css/dashboard.css`
```css
.scatter-chart-wrap { position: relative; height: 420px; }
.signal-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.tab-group { display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 3px; gap: 4px; }
.tab-btn {
  background: transparent; border: none; color: var(--muted); padding: 6px 14px;
  border-radius: var(--radius-md); font-size: 13px; font-weight: 600; cursor: pointer;
  display: inline-flex; align-items: center; gap: 8px; transition: all 0.15s ease;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active.buy { background: rgba(34, 197, 94, 0.18); color: var(--green); }
.tab-btn.active.sell { background: rgba(239, 68, 68, 0.18); color: var(--red); }
.tab-count-badge { background: rgba(0, 0, 0, 0.3); padding: 1px 6px; border-radius: var(--radius-pill); font-size: 11px; }

@keyframes row-highlight-pulse {
  0% { background-color: rgba(59, 130, 246, 0.35); }
  100% { background-color: transparent; }
}
.row-highlight-pulse { animation: row-highlight-pulse 2s ease-out; }
```

---

## 7. Alternative Approaches Considered & Why Rejected

| Alternative | What It Entails | Why Rejected |
| :--- | :--- | :--- |
| **Bubble Chart (sizing by R:R)** | Varying dot radius by `rr_ratio` or volume. | With 400+ dots, varying radii creates massive overlapping blobs that obscure neighboring stocks. Fixed 5.5px dots with alpha transparency provide a cleaner, readable distribution. |
| **Treemap / Heatmap** | Hierarchical rectangular tiles. | Requires external Chart.js plugins (`chartjs-chart-treemap`), violating the hard constraint that no external charting libraries may be added. |
| **X: Rank vs Y: Score** | Plotting rank along X and score along Y. | Rank is a direct 1:1 sort of Score. This produces a trivial downward-sloping monotonic curve with zero exploratory utility. |
| **Collapsible Accordions** | Keeping both tables stacked but collapsible. | If both are expanded, the user is right back to the long scrolling problem. A segmented tab strictly enforces one list in view at a time. |
| **Dropdown Select Filter** | A `<select>` dropdown to pick "Buy" or "Sell". | Requires an extra click to view options and hides the signal counts from view. Segmented tabs surface both counts simultaneously. |

---

## 8. Risks & Mitigation Strategies

1. **Performance with Large Signal Counts (400–600 points)**:
   - *Risk*: Laggy canvas hover hit-testing or slow initial animation.
   - *Mitigation*: Chart.js 2D canvas easily handles up to 1,000 points at 60 FPS. Set `animation: false` or a quick initial fade, and use `interaction: { mode: 'nearest', intersect: true }` to keep hover calculations lightweight.
2. **Overlapping Dots at Common Scores**:
   - *Risk*: Scores often cluster around identical numbers (e.g., 90.0, 95.0, 100.0).
   - *Mitigation*: Semi-transparent point backgrounds (`0.75` alpha) make overlapping clusters visually darker, signaling setup density. Chart.js's `nearest` hit test selects the closest point accurately.
3. **Re-Render Lifecycle on Scan Selection (`#scanSelect`)**:
   - *Risk*: Switching scans leaks Chart.js instances and attaches duplicate canvas listeners.
   - *Mitigation*: Calling `_destroyChart(canvasId)` at the start of `renderMarketScatterChart` destroys the existing instance and releases event handlers cleanly.
4. **Accessibility (Canvas is an inaccessible black box)**:
   - *Risk*: Regressing the accessibility work done in the prior sprint.
   - *Mitigation*: 
     - Canvas is given `role="img"` and `aria-label="Scatter plot showing Buy Signals by Relative Strength and Screener Score"`.
     - The underlying table below remains 100% accessible, containing all data points in standard accessible markup.
     - Segmented buttons adhere to WAI-ARIA tab semantics (`role="tablist"`, `role="tab"`, `aria-selected`, `aria-controls`, and `focus-visible` styling).

---

## 9. Edge Cases & Handling

- **Zero Buy Signals**: Render a styled empty placeholder inside the card (`<div class="no-data" style="padding:40px"><h2>No buy signals in this scan</h2></div>`) instead of empty canvas axes.
- **Zero Sell Signals**: Sell tab button displays `Sell Signals (0)`; activating the tab displays the existing `<tr><td colspan="8">No sell signals</td></tr>`.
- **Missing or Non-Numeric RS/Score**: Filter candidate signals using `typeof s.score === 'number' && typeof s.rs === 'number'` prior to passing data to Chart.js.
- **Async Navigation Away**: If the user clicks another navigation link while `fetchJSON('/api/scan')` is in-flight, `if (currentView !== 'market') return;` (already present in `market.js`) cleanly aborts DOM rendering and chart creation.

---

## 10. Testing Strategy

Following the repository's plain Node test harness (`tests/js/test_*.js`):

### Realistically Testable in Headless Node:
1. **Scatter Data Transformation Unit Test**:
   - Create a pure helper `prepareScatterData(signals)` (or test it via extract-and-eval).
   - Verify it maps `{ x: s.rs, y: s.score, signal: s }`.
   - Verify null/undefined/NaN scores and RS values are safely filtered out.
   - Verify color assignment matches `entry_quality` ('good', 'extended', 'poor').
2. **Tab Switching & ARIA State Characterization Test**:
   - Test tab toggle logic using a simulated DOM (`fakeEl` as seen in `test_shortlist_empty_state.js`).
   - Verify initial state: Buy tab active, Buy panel visible, Sell panel hidden.
   - Verify clicking Sell tab flips `aria-selected`, swaps `active` classes, and swaps panel `hidden` states.
3. **Chart Lifecycle Test**:
   - Verify calling the render function destroys any existing chart on that canvas ID before creating a new instance.

### What is NOT Testable in Headless Node (Requires Manual / Browser Inspection):
- Real 2D canvas pixel rendering and Chart.js hover hit-testing.
- CSS smooth-scrolling (`scrollIntoView`) and keyframe animations.

---

## 11. Subtle Nuances & Traps Another Engineer Might Miss

1. **`charts.js` is NOT an ES Module!**
   In `templates/dashboard.html` (line 68), `charts.js` is loaded as a classic script:
   `<script src="{{ url_for('static', filename='js/charts.js') }}"></script>`
   All functions in `charts.js` are global window functions. If an engineer adds `export function renderMarketScatterChart` in `charts.js` and imports it in `market.js`, the browser throws a syntax error. It must be declared as a top-level function `function renderMarketScatterChart(...)` matching `renderBreadthChart`.
2. **`dashboard.py` Does Not Parse `rs` for Sell Signals**:
   A developer might assume "let's plot both Buy and Sell signals on the scatter plot". However, `dashboard.py` lines 238–256 omit `rs` from `sell_signals`. All sell signals would map to `x = undefined` (NaN) and crash or collapse the chart.
3. **Chart.js Container Height Collapse**:
   Chart.js with `maintainAspectRatio: false` inside a flex/grid container will collapse to 0px height unless its parent wrapper has an explicit pixel height or `min-height`. The `.scatter-chart-wrap` must explicitly define `height: 420px; position: relative;`.
4. **Preserving Design Tokens**:
   `charts.js` uses `_token('--color-success', '#22c55e')` to read CSS variables from `:root`. Colors for the scatter plot must use `_token` or reference `CHART_COLORS` so future theme updates remain synchronized.
