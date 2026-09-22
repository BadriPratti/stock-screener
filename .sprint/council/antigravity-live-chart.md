# Engineering Council Analysis: Live "Buy Opportunity Map" & Intraday Scanning

**Author:** Antigravity (Council Member)  
**Date:** 2026-09-20  
**Context:** Local Flask + pywebview Stock Screener (`/Users/badripratti/Desktop/stock-screener`)  
**Evaluation Target:** User Request on Live Animated Market Scatter Chart & 2-Hour Scans

---

## Executive Summary & Architectural Position

The user requested:
> *"the chart of buy opportunity should also include this like realistically that graph should be packed to the brim because those stocks that it viewed before should still be there realistically we should do this stock scan every 2 hours and everything simultaneously moves in motion"*

This proposal touches three distinct architectural tiers:
1. **Data Pipeline & Persistence**: Transitioning the scanner from a memoryless top-50 text dump to a structured multi-scan historical ledger.
2. **Frontend Motion & Visualization**: Transforming a static Chart.js 4.4.7 canvas into an interactive, time-scrubbable, 60 FPS replay engine with keyed point tweening.
3. **Execution Cadence & Scheduling**: Running automated scans at an intraday cadence without triggering platform rate limits, GitHub cron drift, or runaway API costs.

### Verdict & Crucial Reframing
- **The "Cumulative Infinite Accumulator" idea must be rejected in favor of Trailing Memory with Visual Decay**: Storing every stock ever seen without expiration would cause 2,000+ dots to accumulate within weeks, turning the canvas into an opaque blob. More dangerously, obsolete buy signals from weeks ago that have since collapsed into Stage 4 downtrends would remain plotted on the "Buy Opportunity Map", presenting toxic trade recommendations. The chart must use a **5-session trailing window with alpha/size decay**, not permanent accumulation.
- **The "Every 2 Hours Full Scan" idea must be rejected in favor of a Fast Watchpool Re-score**: A full-universe scan takes **62.8 minutes** (`FACTS.md`, line 13). Running it every 2 hours on GitHub Actions is impossible because GitHub Actions cron has an observed **4–5 hour queue delay** (`FACTS.md`, line 14; `.github/workflows/daily_screening_git_storage.yml`, lines 5–10). Furthermore, running LLM agents and sending emails every 2 hours would multiply Claude API costs by 4–6x and spam the user with 8+ emails daily. Instead, intraday runs must be **lightweight candidate re-scores (~400 stocks, <2 minutes, zero LLM calls, zero emails)** running either locally in the dashboard or via a dedicated market-hours cloud schedule.
- **Chart.js Animation Pitfall**: Chart.js 4.4.7 animates scatter points by **array index**, not ticker identity. Naively updating datasets will morph unrelated stocks into each other. Smooth simultaneous motion requires a **custom requestAnimationFrame (rAF) keyed interpolation driver** updating a single dataset via `chart.update('none')`.

---

## 1. Data Architecture: Machine-Readable Sidecars, Backfill & Axis Encoding

### Current State & Root Cause of the 50-Dot Cap
In `static/js/views/market.js` (lines 150–154):
```javascript
export function buildBuyOpportunityPoints(buySignals) {
  return (buySignals || [])
    .filter(s => Number.isFinite(s.score) && Number.isFinite(s.max_score) && s.max_score > 0 && Number.isFinite(s.rs))
    .map(s => ({ x: s.rs, y: (s.score / s.max_score) * 100, signal: s }));
}
```
Currently, `scan.buy_signals` is populated by `dashboard.py:parse_scan_file()` (lines 173–230), which uses regex to extract blocks matching `BUY #(\d+): ...` from `data/daily_scans/optimized_scan_*.txt`.

In `run_optimized_scan.py:save_report()` (lines 151, 249–255):
```python
if buy_signals:
    for i, signal in enumerate(buy_signals[:50], 1):
        ...
    if len(buy_signals) > 50:
        output.append(f"\nADDITIONAL BUYS ({len(buy_signals)-50} more)")
        remaining = [s['ticker'] for s in buy_signals[50:]]
        for i in range(0, len(remaining), 10):
            output.append(", ".join(remaining[i:i+10]))
```
The text report details **only the top 50 buy signals**. The remaining 314–429 qualified buy signals (`buy_signal_facts.txt`, lines 1–5) are dumped as bare comma-separated ticker strings without score, RS, price, or entry quality. Thus, the text report physically lacks the data needed to plot more than 50 points.

### Source of Truth: Where Data Must Come From
We evaluate three options:
1. **Extend `src/screening/pick_history.py` (Rejected)**:
   In `pick_history.py` (lines 23–24, 112–115), `LIST_NAMES = ("shortlist", "top20")`. Adding 450 buy signals per scan would expand daily snapshot size from ~2 KB to ~60 KB. Crucially, `pick_history.py` enforces a single snapshot per calendar date (`session_date_et()`, line 58; `_validate_session_date()`, lines 134–143). Injecting intraday snapshots directly into `daily_full` breaks the daily consistency ledger and streak counters locked in by 100+ tests.
2. **Re-parse Historical Text Reports (Partial Backfill Only)**:
   The 5 recorded full scans (`optimized_scan_20260914_231020.txt` through `...20260918_170746.txt`) contain detailed numerical metrics for **only 50 stocks each** (84 unique tickers total, `buy_signal_facts.txt`, line 6). We cannot invent historical score/RS numbers that were never computed or logged.
3. **Machine-Readable Sidecar Files (Adopted)**:
   `run_optimized_scan.py` must write a structured sidecar alongside the text report:
   `data/daily_scans/buy_signals_{timestamp}.json` (and `buy_signals_latest.json`).
   Each record uses a compact schema:
   ```json
   {
     "ticker": "SUN",
     "rank": 1,
     "score": 112.5,
     "max_score": 125,
     "rs": 0.355,
     "entry_quality": "Good",
     "current_price": 74.12,
     "stop_loss": 70.50,
     "rr_ratio": 5.6,
     "phase": 2
   }
   ```
   At ~130 bytes per signal across 450 signals, the uncompressed JSON payload is **~58 KB per scan** (negligible disk footprint, fast HTTP delivery).

### Historical Backfill Strategy
A one-time script (`scripts/backfill_buy_opportunity_history.py`) will parse the 5 existing git reports. For those 5 scans, the historical dataset will contain the verified 50 detailed buy signals per scan. Going forward, every full scan and intraday scan will record the complete qualified buy pool into structured JSON sidecars.

### Honest Handling of "Dropped Out" Stocks
When stock $S$ was present at scan $T-1$ but is absent at scan $T$:
- **Root Cause of Dropout**: Either the stock fell below the minimum score threshold ($\text{Score} < 70$), broke support/stop, RS deteriorated vs SPY, or it was not rescanned.
- **Deception Risk**: Freezing an expired stock at its last known position with full opacity implies it remains an active buy recommendation.
- **Honest Policy**:
  - Classify each point with a lifecycle state: `active` (present in latest snapshot), `decaying` (absent from latest snapshot, but present in one of the previous $W=3$ snapshots), or `expired` (absent for $>3$ snapshots; dropped from canvas).
  - Decaying stocks are rendered with distinct styling: hollow border, desaturated gray stroke (`#8b8fa3`), reduced radius (3px), and alpha fading inversely with age.
  - Tooltip explicitly states: `Status: Inactive / Dropped Out (Last active: 2026-09-17)`.

### Y-Axis Compression & Encoding Reality
Data verified from `buy_signal_facts.txt` (lines 1–5):
- Top 50 Buy Signals: Score as % of max ranges exclusively from **81.2% to 93.4%**.
- Across all 450 Buy Signals: Minimum score is 70/125 = **56.0%**.
- RS ranges from **-0.145 to +1.344**.

In `static/js/charts.js` (lines 195–199), the Y-axis currently defaults to auto-scale or 0–100%. If scaled 0–100%, **the bottom 56% of the chart is completely empty**, and the top 50 stocks compress into a paper-thin horizontal strip between 81% and 93%.
Furthermore, RS is an explicit input into the scoring formula (`src/screening/signal_engine.py`), creating a positive mathematical correlation between X and Y that packs points along a diagonal band.

**Recommended Axis Fix**:
1. Configure Chart.js Y-axis options with `suggestedMin: 50` and `suggestedMax: 100` (`static/js/charts.js`, line 195). This doubles the vertical visual separation of points without clipping outliers.
2. Provide a user toggle on the card header:
   - **Default**: Momentum vs. Conviction ($X = \text{RS vs SPY}$, $Y = \text{Score \% of Max}$).
   - **Alternative**: Momentum vs. Asymmetry ($X = \text{RS vs SPY}$, $Y = \text{Risk/Reward Ratio}$, spanning 1.5:1 to 8.0:1), which spreads points across a completely independent fundamental/technical axis.

---

## 2. Visual Design: Density Management & Readability

Plotting 400–600 points (active + decaying) on an HTML5 canvas requires strict visual hierarchy to prevent dense overlapping from becoming illegible.

```
                      BUY OPPORTUNITY MAP (DENSITY DESIGN)
       100% +---------------------------------------------------------+
            |                                         (Active: Solid) |
            |                          O [SUN] 93%         O          |
            |                     O               O                   |
    Score % |               o (Decaying: Faded)       O               |
     of Max |             . .                      O                  |
            |           . [Trail]                                     |
            |         O                                               |
            |                                                         |
        50% +-----------------------------+---------------------------+
            -0.2 (Underperforming SPY)   0.0   +1.5 (Outperforming SPY)
                               RS vs SPY
```

### 1. Point Budget & Canvas Performance
Chart.js 4.4.7 renders scatter charts on a single `<canvas>` element.
- **Budget**: At 500–800 points, 2D canvas context renders at a smooth 60 FPS on macOS Retina displays (backing store $2\times$ pixel ratio).
- **Decimation**: Hard limit total plotted points to **600**. Priority order: (1) Active Top 20/Shortlist, (2) Active Buy Signals sorted by Score, (3) Decaying points sorted by recency. Points older than 3 snapshots are pruned entirely.

### 2. Alpha Decay & Size Curve
Points scale in opacity and size based on snapshot recency:
- **Current Snapshot ($T$)**: Radius $5.5\text{px}$, Fill Alpha $0.75$, Border Alpha $1.0$.
- **Snapshot $T-1$**: Radius $4.5\text{px}$, Fill Alpha $0.40$, Border Alpha $0.60$.
- **Snapshot $T-2$**: Radius $3.5\text{px}$, Fill Alpha $0.20$, Border Alpha $0.35$.
- **Snapshot $T-3$ (Dropped)**: Radius $3.0\text{px}$, Fill Alpha $0.00$ (hollow), Border Alpha $0.20$ (`#8b8fa3`).

### 3. Motion Trails (Tails) Policy
Drawing line trails for all 400 dots simultaneously creates an unreadable "spaghetti bowl" / hairball.
- **Static State**: Trails are **hidden by default**.
- **Interactive Hover**: Hovering over any dot immediately renders its trailing spline path across the previous 3 snapshots with directional arrow heads.
- **Scrub / Playback State**: During active timeline scrubbing or playback, short motion vectors (length: displacement between $T-1$ and $T$) are drawn with 30% opacity, fading out 800ms after motion stops.

### 4. Label Policy
Rendering 400 permanent text labels will cover 100% of the canvas in text collisions.
- **Permanent Labels**: Reserved exclusively for the **Top 5 Shortlist** tickers (using a 10px bold sans-serif tag offset $+8\text{px}$ above the dot).
- **Dynamic Labels**: Displayed on hover via the Chart.js tooltip plugin.
- **Collision Mitigation**: Tooltip interaction mode set to `interaction: { mode: 'nearest', intersect: true }` (`static/js/charts.js`, line 181) with hover radius expanded to $8\text{px}$.

---

## 3. Motion Architecture: Keyed Interpolation & Playback Engine

### The Chart.js 4.4.7 Animation Trap
Chart.js default animations (`options.animation`) operate strictly on **array indices**.
If Snapshot A has:
- Index 0: `SUN` at $(0.35, 90)$
- Index 1: `NVDA` at $(0.80, 88)$

And Snapshot B has:
- Index 0: `AAPL` at $(0.10, 85)$
- Index 1: `SUN` at $(0.40, 91)$

Chart.js will animate Index 0 from `SUN`'s coordinates to `AAPL`'s coordinates, and Index 1 from `NVDA` to `SUN`. **Points will cross-morph between unrelated stocks.** This completely destroys the illusion of continuous market motion.

### Custom rAF Tweening Engine
To achieve authentic simultaneous motion, we bypass Chart.js internal transition animations and drive canvas updates using an external `requestAnimationFrame` loop.

```
                           KEYED TWEENING ARCHITECTURE
+----------------------+     +----------------------+     +----------------------+
| Snapshot T-1 (Map)   |     | Interpolator (rAF)   |     | Chart.js Canvas      |
| SUN: (0.35, 90)      | --> | Keyed by Ticker      | --> | Single Dataset       |
| NVDA: (0.80, 88)     |     | Progress p: 0.0->1.0 |     | chart.update('none') |
+----------------------+     | Enter/Exit Easing    |     +----------------------+
| Snapshot T (Map)     | --> +----------------------+
| SUN: (0.40, 91)      |
| AAPL: (0.10, 85)     |
+----------------------+
```

1. **State Structure**: Build a Map of `ticker -> { from: {x, y, r, a}, to: {x, y, r, a} }`.
   - **Persistent Tickers** ($T-1 \cap T$): Linear or cubic easing from $(x_0, y_0)$ to $(x_1, y_1)$.
   - **Entering Tickers** ($T \setminus T-1$): Position fixed at $(x_1, y_1)$; radius animates $0 \to 5.5\text{px}$; opacity animates $0 \to 0.75$.
   - **Exiting Tickers** ($T-1 \setminus T$): Position fixed at $(x_0, y_0)$; radius animates $5.5 \to 3.0\text{px}$; opacity animates to dropped-out ghost styling.
2. **Execution**:
   At each frame, compute interpolated values and invoke:
   ```javascript
   chart.data.datasets[0].data = interpolatedData;
   chart.update('none'); // Bypasses internal animation; instantaneous 16ms repaint
   ```
3. **Timeline Scrubber**:
   A range slider `<input type="range" min="0" max="N-1" step="0.01">` lets the user scrub continuously between snapshots. For slider value $v = 2.4$, the engine interpolates between Snapshot 2 and Snapshot 3 at progress $p = 0.4$. This delivers seamless, deterministic scrubbing without timer lag.

### `prefers-reduced-motion` Compliance
Repository check: `prefers-reduced-motion` is currently **completely absent** from `static/css/dashboard.css`.
- In CSS (`static/css/dashboard.css`):
  ```css
  @media (prefers-reduced-motion: reduce) {
    .row-highlight-pulse { animation: none !important; }
    .timeline-play-btn { display: none !important; }
  }
  ```
- In JavaScript (`static/js/charts.js`):
  ```javascript
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) {
    // Jump directly to target snapshot without rAF animation
    chart.data.datasets[0].data = targetPoints;
    chart.update('none');
    return;
  }
  ```

### Lifecycle & Memory Leaks in `charts.js`
`static/js/charts.js` is loaded as a classic `<script>` providing globals, managed via `_destroyChart(canvasId)` (lines 33–38).
If a rAF playback loop continues running after the user navigates away from the Market tab, the loop will invoke `chart.update()` on a destroyed or detached context, causing browser memory leaks and console errors.
- **Contract**: Store active animation handles in `_chartAnimationHandles[canvasId] = { rafId: null, timerId: null }`.
- **Destruction Hook**:
  ```javascript
  function _destroyChart(canvasId) {
    if (_chartAnimationHandles[canvasId]) {
      cancelAnimationFrame(_chartAnimationHandles[canvasId].rafId);
      clearTimeout(_chartAnimationHandles[canvasId].timerId);
      delete _chartAnimationHandles[canvasId];
    }
    if (_chartInstances[canvasId]) {
      _chartInstances[canvasId].destroy();
      delete _chartInstances[canvasId];
    }
  }
  ```

### Live Update Animation
When the dashboard's background 5-minute auto-sync (`static/js/dashboard.js`, lines 97–106) pulls a new scan during an open session:
Instead of destroying and recreating the chart (which flashes white), the view triggers an automated 800ms tween from current coordinates to the new snapshot, smoothly gliding points into their new positions.

---

## 4. Intraday Ledger Design & Isolation

### Preventing Regression of Daily Consistency Semantics
The pick-history ledger built in `src/screening/pick_history.py` relies on strict invariants:
1. One snapshot per America/New_York date: `snapshot_path(session_date)` maps to `data/pick_history/snapshots/daily_full/YYYY-MM-DD.json` (line 218).
2. Date format strictly validated: `_validate_session_date()` enforces `^\d{4}-\d{2}-\d{2}$` (lines 134–143).
3. "Session" = 1 market day: Consecutive trading days form streaks; `denominator = len(window_sessions)` (lines 400–401).
4. Badges in Shortlist and Top 20 display `"4/5 days"` or `"3-scan streak"`.

**If intraday scans wrote to `daily_full`:**
- Same-date executions would overwrite earlier scans, losing the intraday timeline.
- Adding timestamp suffixes (`YYYY-MM-DD_HHMMSS.json`) would immediately fail `_validate_session_date()`.
- If accepted, 4 intraday scans per day would inflate the session count by $4\times$, breaking consistency badges (e.g. showing "4/20 scans" instead of "4/5 days") and invalidating the 100+ tests in `tests/test_pick_history.py`.

### The Dual-Directory Ledger Architecture
We isolate daily consistency from intraday motion via separate directory trees and run kinds:

```
data/pick_history/snapshots/
├── daily_full/                 <-- CANONICAL DAILY LEDGER (Untouched)
│   ├── 2026-09-14.json         <-- 1 file per market date (Shortlist + Top 20)
│   └── 2026-09-18.json         <-- Consumed by Consistency view & badges
└── intraday/                   <-- INTRADAY OPPORTUNITY MAP SERIES
    ├── 2026-09-18_103000.json  <-- Timestamped snapshots
    ├── 2026-09-18_123000.json  <-- Stores compact buy_signals pool
    └── 2026-09-18_143000.json  <-- Consumed exclusively by Market Opportunity Map
```

### Intraday Snapshot Schema (`RUN_KIND_INTRADAY = "intraday"`)
```json
{
  "schema_version": 1,
  "run_kind": "intraday",
  "session_date": "2026-09-18",
  "generated_at": "2026-09-18T18:30:00Z",
  "scan_time_et": "14:30:00",
  "universe_scope": "watchpool",
  "tracked_count": 420,
  "buy_signals": [
    {
      "ticker": "SUN",
      "rank": 1,
      "score": 112.5,
      "max_score": 125,
      "rs": 0.355,
      "entry_quality": "Good",
      "current_price": 74.12,
      "stop_loss": 70.50,
      "rr_ratio": 5.6,
      "phase": 2
    }
  ]
}
```

### Git History Growth & Retention Limits
- **File Generation Rate**: 3 intraday runs/day $\times$ 252 trading days = **756 files/year**.
- **Storage Impact**: At ~55 KB per snapshot, raw generation is **~41 MB/year**.
- **Git Bloat Mitigation**:
  - Keep active intraday snapshots in git storage for a **rolling window of 10 trading days** (~30 files, ~1.6 MB).
  - Older intraday snapshots are pruned automatically by the daily workflow cleanup step. The permanent archive remains in `daily_full/` and GitHub release artifacts.
  - This keeps repo clones fast and prevents repository size explosion.

---

## 5. Scheduling & Execution Reality: "Every 2 Hours"

### Repository Evidence vs. User Expectations
The user's vision of running full scans every 2 hours must be reconciled with hard repository data:

| Dimension | Daily Full Scan (Current) | User's "Full Scan Every 2h" | Council Recommended Intraday Rescore |
|---|---|---|---|
| **Universe Scope** | 3,770 processed, ~1,970 analyzed | 3,770 processed, ~1,970 analyzed | **~400–500 candidate watchpool** |
| **Execution Time** | **62.8 minutes** (`FACTS.md`, line 13) | 62.8 minutes | **~1.5 – 2.0 minutes** |
| **Cadence Feasibility** | Once daily | **Impossible** (63 min run + 4h queue delay) | **Feasible** (Runs in 90 seconds) |
| **GitHub Cron Latency** | Scheduled 12:00 UTC, starts 16:11–17:39 UTC | Scheduled every 2h, starts with 4h jitter | N/A (Local scheduler) or 3 fixed cloud windows |
| **LLM Agent Calls** | 20 tickers $\times$ 2 Claude calls = 40/day | 40 $\times$ 4 = 160 calls/day ($$$ cost) | **0 calls** (LLM disabled on intraday) |
| **Email Volume** | 2 emails/day (start + report) | **8–12 emails/day** (inbox spam) | **0 emails** (notifications disabled) |
| **Data Provider Load** | 1,970 tickers @ 2 TPS | High risk of HTTP 429 rate limits | 400 tickers batch-downloaded safely |

### Scheduling Options: Local Mac Dashboard vs. GitHub Actions

#### Option A: Local Mac Dashboard Scheduler (Primary Recommendation)
`dashboard.py` already includes an internal background job launcher (`/api/jobs/scan`, lines 455–462, 567–586) running within a desktop Flask + pywebview application.
- **Mechanism**: A lightweight background timer thread in `dashboard.py` triggers an intraday watchpool re-score every 2 hours while the app is running during market hours (9:30 AM – 4:00 PM ET).
- **Pros**: Zero GitHub cron delay, zero git push collisions, instant UI refresh, no runner timeouts.
- **Cons**: Only runs while the user's Mac is awake with the dashboard open.

#### Option B: Cloud Workflow via GitHub Actions
If cloud execution is required when the Mac is offline:
- **Do NOT schedule a generic `0 */2 * * 1-5` cron**: GitHub Actions cron will bunch runs together due to queue latency.
- **Define 3 discrete market-hours workflows**:
  1. `10:30 AM ET` (14:30 UTC): Morning Momentum Shift.
  2. `1:00 PM ET` (17:00 UTC): Midday Trend Check (replaces the existing 100-stock `midday_quick_scan.yml`).
  3. `3:30 PM ET` (19:30 UTC): Power Hour Close Positioning.
- **Concurrency & Push Hardening**:
  - Workflow concurrency group: `screening-intraday`, `cancel-in-progress: true`.
  - Workflow timeout: `timeout-minutes: 15`.
  - Push step must execute `git pull --rebase` before pushing to avoid push rejection against concurrent daily runs.

---

## 6. Sequencing & Cross-Sprint Conflict Management

### The File Conflict Surface
Two major plans touch overlapping frontend files:
1. `SPRINT_PLAN_CHART_MODAL.md` (unbuilt): Touches `market.js`, `charts.js`, `dashboard.css`, `ui-helpers.js`, `dashboard.html`, `router.js`.
2. **Live Opportunity Map Sprint**: Touches `market.js`, `charts.js`, `dashboard.css`, `dashboard.py`, `run_optimized_scan.py`, `src/screening/`.

Shared files: `static/js/views/market.js`, `static/js/charts.js`, `static/css/dashboard.css`.

### Strict Task Sequencing Strategy
To ensure no two engineers touch the same file concurrently, work must be partitioned across 3 strict sequential phases:

```
[Phase 1: Backend Data & Sidecars] (Python)
  - run_optimized_scan.py (JSON sidecar)
  - scripts/rescore_candidates.py
  - dashboard.py (/api/market/opportunity-history)
           │
           ▼
[Phase 2: Chart Modal Sprint OR Live Chart Foundation] (JS/CSS)
  - Execute SPRINT_PLAN_CHART_MODAL.md to completion FIRST, OR
  - Lock `charts.js` API contracts before editing `market.js`
           │
           ▼
[Phase 3: Market View UI & Timeline Controls] (ES Modules / CSS)
  - static/js/views/market.js (Timeline slider, replay controller)
  - static/css/dashboard.css (Slider styling, reduced-motion)
```

**Council Recommendation**: Build Phase 1 immediately. If the Chart Modal sprint is scheduled, build it next, as it simplifies `market.js` (removes inline toggle charts). Then layer the Live Opportunity Map replay controls onto `market.js` without risking code clobbering.

---

## 7. Risks, Edge Cases & Verification Suite

### Edge Cases & Defensive Safeguards
1. **Weekend & Holiday Gaps**:
   The playback slider must step over **discrete recorded snapshots** ($S_0, S_1, S_2, \dots$), NOT linear elapsed calendar time. Stepping over linear time would cause the animation to stall over 48 hours of weekend inactivity.
2. **Partial or Aborted Scans**:
   If an intraday scan is aborted or encounters network timeouts, it must not write a corrupted sidecar. All writes must use atomic temporary files (`tempfile.NamedTemporaryFile` + `os.replace`), matching `pick_history.py:write_snapshot()` (lines 232–246).
3. **Duplicate Tickers**:
   Upstream batch quirks must not inject duplicate ticker entries into the snapshot. The scanner must deduplicate by ticker symbol, retaining the higher score.
4. **Scoring Version Incompatibilities**:
   If scoring weights change (`SCORING_VERSION`), delta calculations and motion vectors across different scoring regimes must be suppressed to avoid misleading visual jumps.
5. **NaN / Infinite Values**:
   All metrics must pass through `sanitize_nan` on serialization. Frontend `buildBuyOpportunityPoints` must continue rejecting non-finite values (`Number.isFinite(s.score) && Number.isFinite(s.rs)`).
6. **Accessibility (Canvas Fallback)**:
   Canvas elements cannot be parsed by screen readers. A visually hidden text alternative (`<div class="sr-only" role="region" aria-live="polite">`) must summarize point counts, active leaders, and status changes for assistive technologies.
7. **Strict No-Emoji Policy**:
   Repository guidelines strictly prohibit unicode emojis in UI text. All UI controls, badges, and timeline indicators must use plain typography, SVG icons, or CSS status dots.

---

## 8. Critical Review: What Others Will Miss & Request Critique

### 1. The "Packed to the Brim" Accumulation Trap
Other engineers may take the user's words literally and store an unbounded accumulation of past tickers.
- **Why this fails**: In trend-following, stocks break down. If a stock was a buy 3 weeks ago, broke its 50 SMA, and plunged 30%, keeping it on the Buy Opportunity Map presents an active hazard to the trader.
- **Correction**: The map must represent **active and recent opportunities**, using a 5-session decaying memory window.

### 2. The Chart.js Index-Morphing Bug
Engineers unfamiliar with Chart.js 4.4.7 internals will assume calling `chart.update()` will animate points between scans correctly.
- **Why this fails**: Chart.js interpolates by array index. Ticker A will morph into Ticker B unless driven by a custom keyed interpolator.

### 3. The GitHub Actions Cron Myth
Engineers may schedule `0 */2 * * 1-5` on GitHub Actions and assume scans will run every 2 hours.
- **Why this fails**: Verified repository facts show GitHub Actions cron runs with 4–5 hours of latency. A 2-hour cron will bunch up, skip, and fail. Intraday scanning belongs in a fast local rescore or fixed cloud windows.

### 4. Y-Axis Visual Smear
Leaving the Y-axis at default 0–100% compresses all meaningful buy signals into a narrow horizontal band between 81% and 93%.
- **Correction**: Set `suggestedMin: 50` to spread conviction scores across the full vertical canvas.

---

## 9. Recommended Task Breakdown & Implementation Plan

| Task ID | Component | Description & Acceptance Criteria | Owner | Dependencies | Files Touched |
|---|---|---|---|---|---|
| **TASK-001** | Backend Data | **Full Buy Signals Sidecar Writer**: Update `run_optimized_scan.py` to write `buy_signals_{timestamp}.json` containing all qualified buy signals (not just top 50). Sanitize NaNs, atomic write. | Codex | None | `run_optimized_scan.py` |
| **TASK-002** | Backend Data | **Historical Backfill Script**: Create `scripts/backfill_buy_opportunity_history.py` parsing the 5 existing git reports into historical JSON sidecars (50 points each). Idempotent execution. | Claude | TASK-001 | `scripts/backfill_buy_opportunity_history.py` |
| **TASK-003** | Intraday Engine | **Light Watchpool Rescorer**: Create `src/screening/watchpool_rescore.py` to rescore ~400 candidates (price + RS + score) in <2 min. Zero LLM calls, zero emails. CLI flag `--intraday`. | Codex | TASK-001 | `src/screening/watchpool_rescore.py`, `run_optimized_scan.py` |
| **TASK-004** | API Layer | **Opportunity History Route**: Add `GET /api/market/opportunity-history` in `dashboard.py`. Returns chronological array of snapshots with `session_date`, `scan_time`, and slim buy points. Empty-safe contract. | Codex | TASK-001, 002 | `dashboard.py`, `tests/test_market_history_api.py` |
| **TASK-005** | Chart Motion Engine | **Keyed rAF Interpolation Driver**: In `static/js/charts.js`, implement `renderMarketReplayScatterChart` with keyed ticker tweening, enter/exit easing, and `_destroyChart` cleanup. Respects `prefers-reduced-motion`. | Claude | TASK-004 | `static/js/charts.js` |
| **TASK-006** | UI & Controls | **Timeline Scrubber & Density Styling**: Add time slider, play/pause controls, active/decaying point styling, and suggestedMin:50 scale to Market tab. Full keyboard accessibility. No emojis. | Antigravity | TASK-005 | `static/js/views/market.js`, `static/css/dashboard.css` |
| **TASK-007** | Scheduler Wiring | **Local & Cloud Trigger**: Add 2-hour local timer option to `dashboard.py` background runner; add market-hours workflow dispatch for cloud runs with `git pull --rebase`. | Codex | TASK-003, 004 | `dashboard.py`, `.github/workflows/intraday_scan.yml` |
| **TASK-008** | Verification | **End-to-End Test Suite**: Pytest for rescorer and API; plain-Node tests for point interpolation, alpha decay, and timeline state transitions. | Claude | All | `tests/test_intraday_scan.py`, `tests/js/test_market_scatter_motion.js` |

---
*Report compiled and verified against repository ground truth.*
