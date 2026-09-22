# Engineering Council: Independent Assessment & Design Proposal
**Topic:** News Section Redesign (Shortlist & Market Views)  
**Complexity:** MEDIUM UI Refactor  
**Status:** Investigation & Architectural Proposal Only (No files modified)

---

## 1. Understanding of the Actual Problem

Grounding the user's complaint in the codebase and actual adhoc simulation data (`news_shortlist.json`, `news_buy.json`, `news_positions.json`), the user's frustration stems from **three compounding UX failures**, not just sheer headline volume:

### A. Vertical Page Bloat & Physical Scroll Exhaustion
- On the **Shortlist view**, the news section is appended to the bottom (`<div id="shortlistNews">`) below 5 large pick cards (which include composite scores, momentum slots, backfill alerts, agent badges, fidelity links, and expandable chart canvases). 
- In [`market.js`](file:///Users/badripratti/Desktop/stock-screener/static/js/views/market.js#L101-L115), `_renderNewsGroupHTML` renders a CSS grid (`.news-ticker-grid`, auto-fit min 240px) displaying **every single headline** returned by the backend.
- While [`scripts/fetch_news.py:30`](file:///Users/badripratti/Desktop/stock-screener/scripts/fetch_news.py#L30) limits Yahoo Finance queries to 5 headlines per ticker (`limit=5`), 5 tickers on Shortlist produce up to 25 full headline blocks. On smaller laptop viewports, the grid wraps into 2–3 rows of tall cards, extending the page by 600–900px of scrolling.
- On the **Market view**, two news cards are rendered (`#news-positions-card` and `#news-buy-card`). With up to 20 user positions and 8 buy tickers, this dumps up to **140 headlines** below the already massive Top 20 and Buy/Sell signal tables.

### B. Lack of Recency Intelligence & Visual Hierarchy
Each headline object from `fetch_news.py` / `catalyst_sentiment.py` has the shape:
```json
{
  "title": "Implied Volatility Surging for NGL Energy Partners Stock Options",
  "publisher": "Zacks",
  "pub_date": "2026-09-09T14:22:00Z",
  "url": "https://finance.yahoo.com/..."
}
```
In [`_renderNewsGroupHTML`](file:///Users/badripratti/Desktop/stock-screener/static/js/views/market.js#L107-L111):
- **Headlines are not sorted chronologically:** Yahoo Finance results are rendered in raw API order without sorting by `pub_date`.
- **Dates are unhelpful strings:** Dates are formatted via `toLocaleDateString()` (e.g., `8/11/2026` or `2/3/2026`). In active trading, an article from 2 hours ago is critical; an article from 6 weeks ago is stale background noise.
- **Stale syndication spam shares equal weight with breaking news:** In `news_buy.json` for `KRNY`, an article from February 2026 (7 months old) and syndicated listicles ("5 R2K Leaders With Dividends") take up the identical visual weight and column height as breaking earnings news published 2 hours ago for `CRWD`.

### C. Rigid Per-Ticker Silos Without High-Level Scannability
- Grouping exclusively into per-ticker columns forces users to scan down column 1, scroll up, scan down column 2, scroll up, etc. The user cannot quickly answer: *"Did any breaking news happen today across my watchlist?"*

---

## 2. Concrete Redesign Proposal

We recommend a **Capped Progressive Disclosure Model with Recency Intelligence**:

```
+-------------------------------------------------------------------------------+
| News on your shortlist                           [Live — updates every 90s]   |
| Quick Jump: [NGL] [ASND] [LILA] [LILAK] [CRWD]                                |
+-------------------------------------------------------------------------------+
| +-------------------------+ +-------------------------+ +-------------------+ |
| | NGL                     | | CRWD                    | | ASND              | |
| |                         | |                         | |                   | |
| | • Implied Volatility... | | • Tech pulls back on... | | • BioMarin Shares | |
| |   Zacks · 5d ago        | |   Yahoo · 2h ago  [TODAY]| |   Insider · 2d ago| |
| |                         | |                         | |                   | |
| | • Great Momentum Stock? | | • Cybersecurity get...  | | • Growth Drug...  | |
| |   Zacks · Aug 21        | |   Yahoo · 6h ago  [TODAY]| |   Benzinga · 4d ago| |
| |                         | |                         | |                   | |
| | [+3 more]               | | [+3 more]               | | [+3 more]         | |
| +-------------------------+ +-------------------------+ +-------------------+ |
+-------------------------------------------------------------------------------+
```

1. **Default Cap of 2 Headlines per Ticker:**
   - Showing 2 headlines guarantees that if the first headline is an automated quantitative rating (e.g. Zacks rank change), the second headline still captures real company events (earnings, M&A, FDA news).
   - Reduces the initial vertical footprint across 5 shortlist tickers by **60%** (10 items maximum vs 25).
2. **In-Place Progressive Disclosure (`+N more` / `Show less`):**
   - If a ticker has $> 2$ headlines, the remaining items are wrapped in `<div class="news-extra" style="display:none">`.
   - Underneath, render `<button class="expand-btn news-expand-btn" data-ticker="${ticker}" aria-expanded="false">+${extra.length} more</button>`.
   - Clicking expands smoothly in place and flips text to `Show less` (matching the existing `.expand-btn` pattern in `dashboard.css`).
3. **Chronological Sorting & Smart Relative Timestamps:**
   - Sort headlines within each ticker descending by `pub_date` (null/missing dates placed at the end).
   - Format timestamps compactly:
     - $< 1\text{ hr}$: `"45m ago"`
     - $< 24\text{ hrs}$: `"${h}h ago"` + subtle green accent pill/dot (`[Today]`)
     - $< 7\text{ days}$: `"${d}d ago"`
     - $\ge 7\text{ days}$: `"MMM D"` (e.g. `"Aug 15"`)
4. **Headline Title Clamping:**
   - Multi-line titles currently cause jagged, uneven column heights. Apply CSS `-webkit-line-clamp: 2` to `.news-headline-title` with full text stored in `title="${escapeHtml(h.title)}"`.
5. **Shortlist Quick-Jump Link:**
   - Add a subtle shortcut in the Shortlist source note or header: `Jump to News ↓` (smooth scroll to `#shortlistNews`) so the user doesn't have to scroll past 5 pick cards when their primary objective is reading news.

---

## 3. Shortlist View vs. Market View

**Verdict:** The underlying data engine should be shared, but the layout presentation must adapt to ticker volume.

| Dimension | Shortlist View | Market View |
| :--- | :--- | :--- |
| **Ticker Count** | Exactly 5 picks | Up to 20+ positions, 8 buy picks |
| **Layout Strategy** | **5-Column Capped Grid** (`minmax(200px, 1fr)`) | **Density-Optimized Grid + Empty Filtering** |
| **Empty Ticker Handling** | Show block with `"No recent headlines"` (so user knows pick #5 was checked) | **Consolidated Footnote** (`"No recent headlines for: VOO, FRBUX, VTI"`) — avoids wasting 10 grid slots on empty ETFs |
| **Ticker Ordering** | Strict Rank Order (`#1` to `#5`) matching the cards above | **Activity-First Sorting**: Tickers with headlines in the last 48 hours float first; quiet/stale tickers sink to bottom |
| **Default Display** | 2 headlines + expander | 2 headlines + expander |

---

## 4. Relevant Files and Modules to Touch

1. [`static/js/views/market.js`](file:///Users/badripratti/Desktop/stock-screener/static/js/views/market.js):
   - Refactor `_renderNewsGroupHTML(newsByTicker, groupKey, options)`: add sorting, 2-item capping, `.news-extra` wrapper, relative date formatting, and state-aware expansion.
   - Refactor `_loadNewsGroup`: preserve expanded state across silent live-refreshes.
   - Update `loadMarketNews(silent)` to pass `filterEmpty: true` and activity-sort options.
2. [`static/js/views/shortlist.js`](file:///Users/badripratti/Desktop/stock-screener/static/js/views/shortlist.js):
   - In `loadShortlistNews`: pass `filterEmpty: false` and preserve shortlist order.
   - Add `Jump to News ↓` anchor in `renderShortlistView`.
3. [`static/css/dashboard.css`](file:///Users/badripratti/Desktop/stock-screener/static/css/dashboard.css#L231-L239):
   - Refine `.news-ticker-grid` and `.news-ticker-block` styling.
   - Add `.news-extra` collapsible container rules.
   - Add `.news-fresh-badge` (`var(--green)`) for articles $< 24\text{h}$.
   - Add 2-line clamping for `.news-headline-title`.
4. [`static/js/core/ui-helpers.js`](file:///Users/badripratti/Desktop/stock-screener/static/js/core/ui-helpers.js):
   - Add helper `formatNewsDate(isoString)` or `relativeTime(isoString)`.
   - Export news toggle handler or attach event delegation.
5. [`tests/js/test_news_render.js`](file:///Users/badripratti/Desktop/stock-screener/tests/js/):
   - New characterization and unit test suite matching repo conventions.

---

## 5. Implementation Approach & Live-Refresh State Preservation

### The Critical Trap: Silent Live-Refresh Re-renders
In [`static/js/core/refresh.js`](file:///Users/badripratti/Desktop/stock-screener/static/js/core/refresh.js#L7), a 90-second timer triggers `loadMarketNews(true)` and `loadShortlistNews(tickers, true)`.  
In [`market.js:94`](file:///Users/badripratti/Desktop/stock-screener/static/js/views/market.js#L94), on job completion:
```javascript
el.innerHTML = _renderNewsGroupHTML(data.news || {});
```
A naive markup/CSS solution (or HTML `<details>`) will **blow away DOM state every 90 seconds**. If a user clicks `+3 more` on `ASND` and is reading the 4th headline, the 90-second tick will replace `innerHTML` with default collapsed HTML, collapsing the card under the user's cursor.

### Recommended Solution: Explicit Module State + DOM Sync
Track expanded states in a module-level `Set`:
```javascript
const _expandedNewsKeys = new Set(); // Stores e.g. "shortlist:ASND", "positions:AAPL"
```
1. When generating HTML in `_renderNewsGroupHTML(newsByTicker, groupKey)`:
   ```javascript
   const key = `${groupKey}:${ticker}`;
   const isExpanded = _expandedNewsKeys.has(key);
   const extraStyle = isExpanded ? '' : 'style="display:none"';
   const btnText = isExpanded ? 'Show less' : `+${extra.length} more`;
   const ariaExp = isExpanded ? 'true' : 'false';
   ```
2. When the user clicks the expand button:
   ```javascript
   export function toggleNewsBlock(btn) {
     const key = btn.dataset.newsKey;
     const extraEl = btn.previousElementSibling;
     const isExpanded = _expandedNewsKeys.has(key);
     if (isExpanded) {
       _expandedNewsKeys.delete(key);
       extraEl.style.display = 'none';
       btn.textContent = `+${btn.dataset.extraCount} more`;
       btn.setAttribute('aria-expanded', 'false');
     } else {
       _expandedNewsKeys.add(key);
       extraEl.style.display = '';
       btn.textContent = 'Show less';
       btn.setAttribute('aria-expanded', 'true');
     }
   }
   ```
3. Attach listener via **event delegation** on `#newsSections` and `#shortlistNews` or expose `window.toggleNewsBlock = toggleNewsBlock;` matching the existing `window.toggleReasons = toggleReasons;` in [`dashboard.js:25`](file:///Users/badripratti/Desktop/stock-screener/static/js/dashboard.js#L25).

---

## 6. Alternative Approaches Considered and Rejected

1. **Alternative: Unified Flat Chronological Feed (Timeline)**
   - *Rejected:* On the Shortlist, the user's workflow is per-pick evaluation ("What is the story on pick #2 vs pick #3?"). A flat timeline mixes tickers together. Mega-caps with daily news (e.g. CRWD) would completely drown out lower-volume tickers (e.g. NGL, LILA), hiding their news entirely unless filtered.
2. **Alternative: Modal or Slide-out Drawer**
   - *Rejected:* High friction. Modals trap focus, block comparisons across tickers, and violate the app's established design language of in-place inline expansion (e.g. `toggleReasons`, `wireChartToggles`).
3. **Alternative: Ticker Tabs / Segmented Control**
   - *Rejected:* For 5 shortlist picks, tabs require 5 distinct clicks to check news instead of scanning all 5 at a glance. For Market (20 positions), a 20-tab bar overflows and breaks responsive design.
4. **Alternative: Pure CSS `<details>` / `<summary>`**
   - *Rejected:* Replaced `innerHTML` on the 90s live-refresh tick resets the `open` attribute of `<details>` back to closed unless managed by JS state anyway.

---

## 7. Risks and Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **Live-Refresh Collapse** | User loses expanded reading position every 90s | Track open keys in `_expandedNewsKeys` Set; render restored display state on tick. |
| **Jagged Grid from Long Titles** | 4-line titles distort grid rows | CSS 2-line clamp (`-webkit-line-clamp: 2`) with full title on native `title=""` tooltip. |
| **Screen Reader Inaccessibility** | Screen reader users unaware of hidden content | Use real `<button>` with dynamic `aria-expanded` and `aria-controls`. |
| **Missing / Invalid `pub_date`** | Date parsing errors or NaN timestamps | Date helper checks `isNaN(Date.parse(pub_date))`; sort comparator places null/invalid dates at the end. |

---

## 8. Edge Cases Handled

1. **Zero headlines for a ticker (`items.length === 0`):**
   - *Shortlist:* Render compact single-line `"No recent headlines."` (no button).
   - *Market:* Suppress the block; list ticker in consolidated footnote.
2. **Exactly 1 or 2 headlines (`items.length <= 2`):**
   - Render the 1 or 2 items directly. **Do not** render an expand button.
3. **Duplicate headlines across tickers:**
   - Macro market articles mentioning multiple tickers are deduplicated within any single ticker block by canonical URL.
4. **Missing publisher or URL:**
   - Fallback publisher to `'Unknown source'`; wrap all URLs in [`safeHref(h.url)`](file:///Users/badripratti/Desktop/stock-screener/static/js/core/ui-helpers.js#L101-L107) to prevent script injection schemes.

---

## 9. Testing Strategy

Following the repo's zero-build, plain Node testing architecture (as seen in [`tests/js/test_shortlist_empty_state.js`](file:///Users/badripratti/Desktop/stock-screener/tests/js/test_shortlist_empty_state.js) and [`tests/js/test_live_guard.js`](file:///Users/badripratti/Desktop/stock-screener/tests/js/test_live_guard.js)):

Create `tests/js/test_news_render.js` covering:
1. **Chronological Sorting:**
   - Fixture with 4 articles: `[Yesterday, 2 hours ago, 3 weeks ago, null]`.
   - Assert rendered DOM order has `2 hours ago` first, `Yesterday` second, `3 weeks ago` third, `null` last.
2. **Capping & Button Thresholds:**
   - 0 items: No expand button, displays empty text.
   - 2 items: 2 rendered, no expand button.
   - 5 items: 2 rendered visibly, 3 enclosed in `.news-extra` with `style="display:none"`, button text `"+3 more"`.
3. **Live Refresh State Retention:**
   - Simulate user expanding ticker `CRWD`.
   - Re-execute `_renderNewsGroupHTML` with fresh payload.
   - Assert `CRWD`'s `.news-extra` has `style=""` (visible) and button text `"Show less"`.
4. **Relative Date Formatter:**
   - Test boundaries: 30 minutes, 5 hours, 3 days, 14 days, invalid string, null.

---

## 10. Critical Context: In-Flight Sprint Sequence Alignment

### Beware Concurrent Edits to `market.js`
In [`.sprint/SPRINT_PLAN.md`](file:///Users/badripratti/Desktop/stock-screener/.sprint/SPRINT_PLAN.md) and [`.sprint/STATUS.md`](file:///Users/badripratti/Desktop/stock-screener/.sprint/STATUS.md), an active sprint is currently in flight:
- **TASK-001** (Codex) & **TASK-002** (Claude): Scatter chart preparation.
- **TASK-003** (Claude) & **TASK-004** (Codex): **Both touch `static/js/views/market.js`** to wire the scatter chart and replace buy/sell tables with an ARIA-tabbed registry.
- `.sprint/SPRINT_PLAN.md:39` specifically warns: `"(same file — sequential, not parallel, per the lesson from the last sprint about concurrent edits to one file)"`.

### Implementation Coordination
- The news section functions in `market.js` live at lines 54–115, while the chart and signal tables live at lines 117–218.
- However, to avoid git merge conflicts or disrupting the in-flight council tasks, **this news refactor should either land sequentially after TASK-004 completes, or isolate its rendering functions into a dedicated `static/js/core/news.js` module** that both `market.js` and `shortlist.js` import cleanly.

### Precedent: `toggleReasons` Bug Fix
The existing `toggleReasons` function in [`ui-helpers.js:110`](file:///Users/badripratti/Desktop/stock-screener/static/js/core/ui-helpers.js#L110) contains a known issue: when collapsing, it sets `display: none` but forgets to restore `btn.textContent = '+N more'`. Our news toggle implementation explicitly tracks state and toggles bidirectionally between `+N more` and `Show less`.
