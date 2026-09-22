# Sprint: Full-Screen Chart Analysis Modal

## Request (user's own words)

"i want to add the graph function and also the graph that pops up is too small I want it to a massive kind of window that I can do other analysis on"

## Engineering Council process

HARD-classified (a genuinely new UI subsystem — no existing modal/expand precedent in the codebase). Full council: Claude + Codex + Antigravity all independently investigated. Full transcripts: `.sprint/council/codex-chart-modal.md`, `.sprint/council/antigravity-chart-modal.md`.

## Converged decisions (both agents agreed independently)

- **Pattern**: a full-viewport in-page modal overlay (`role="dialog"`, `aria-modal="true"`), NOT a second pywebview OS window (the app launches exactly one native window with no multi-window/IPC support — both agents independently rejected this as disproportionate), NOT a dedicated hash route (would tear down the current view's scroll/sort/tab state), NOT an iframe (duplicates the whole app, breaks offline/local guarantees for a third-party embed option Antigravity also explicitly rejected).
- **Scope for "other analysis," using zero new backend data**: the existing price-history data is daily-close-only (~180 sessions, confirmed in `scripts/fetch_price_history.py`) with no OHLC/volume, and Chart.js core has no candlestick support. Both agents independently concluded the right scope for *this* sprint is client-side-derived analytics from data already fetched:
  - Range selector: 1M / 3M / 6M / All (21/63/126/180 trading sessions, sliced client-side, no network call).
  - Optional 20-day and 50-day SMA overlays, computed client-side from the existing close series.
  - A stats strip: latest price, period change (abs + %), period low/high.
  - Reference lines carried through per view: Positions' real entry/stop, Market buy's `stop_loss` (labeled "Scanner stop," not "recommended stop" — these mean different things), Market sell's `breakdown_level` (its own distinct label), Shortlist has none (no entry/stop data exists there — do not fabricate one).
- **Explicitly deferred** (both agents agreed, for the same reason: it's real, separate backend work, not needed to solve the actual complaint): OHLCV/candlesticks, volume histogram, RSI/MACD, drawing tools, saved layouts. Vendoring a Chart.js financial plugin is a distinct future sprint.
- **Critical technical constraint** (both agents flagged identically): `static/js/charts.js` is a classic `<script>`, not an ES module (confirmed: loaded in `templates/dashboard.html` before the `type="module"` entry point specifically so its functions are globals). The new chart-rendering function must be a plain global `function`, not `export function`.
- **Shared risks both agents flagged in detail** (must all be handled, not just "keep in mind"):
  - Toast is currently `z-index: 100` — must be raised above the modal's z-index or sync/job notifications become invisible while the modal is open.
  - Chart.js throws a hard error ("Canvas is already in use") if a new instance isn't created after destroying the previous one on the *same* canvas id — the modal must always destroy-then-recreate on every open/ticker-switch/close, reusing one fixed canvas id, matching the existing `_destroyChart` convention.
  - The modal's chart container needs an explicit height (not a percentage) — Chart.js's `maintainAspectRatio:false` collapses to 0px otherwise (already documented in `dashboard.css` from an earlier sprint's scatter-chart work).
  - Reference lines (entry/stop/breakdown) must be treated as strictly optional per view (`Number.isFinite`, not truthiness) — Shortlist legitimately has none; don't plot a flat zero line.
  - A user reads by the same trigger element after 90+ seconds inside the modal, background live-refresh may have re-rendered/removed the original card underneath (already true for Positions' live refresh) — focus-return-on-close must check the trigger element is still attached to the document before calling `.focus()` on it, falling back safely otherwise.
  - The modal element must live outside `#content` (e.g. a sibling in `templates/dashboard.html`) so a view's own re-render never wipes it out from under an open modal.

## One real disagreement — resolved

**Codex**: remove the small inline chart entirely; the existing toggle button becomes the single action that opens the big modal directly. Simpler state (one chart lifecycle, not two), and it matches what the user actually asked for — they didn't ask to keep a small preview *and* get a big one, they said the current one is too small.

**Antigravity**: keep the small inline chart for quick glanceability across multiple cards, and add a *second*, separate "expand" icon next to it that opens the modal.

**Decision: go with Codex's simpler approach — replace, don't add.** The user's own words ("I want it to a massive kind of window") describe a replacement, not a supplement. A second icon/control on every row is exactly the kind of scope creep this project has been actively trimming (see the recent Buy/Sell tabbing work, done specifically to reduce UI clutter). If glanceability across many cards turns out to be missed later, that's a cheap, separable follow-up — reintroducing one icon is far easier than un-shipping two competing chart affordances now.

## Tasks

- TASK-001 | Claude | `static/js/core/price-analysis.js` — pure functions: `computeSMA(closes, period)`, `computePriceStats(history)`, `sliceRange(history, sessions)`. No DOM, no Chart.js — the easily-unit-tested foundation everything else builds on. | no deps
- TASK-002 | Codex | Modal markup (`templates/dashboard.html`) + CSS (`static/css/dashboard.css`): overlay/dialog/header/toolbar/canvas-wrap, the z-index fix for `.toast`, the 760px responsive rule for the modal, explicit non-collapsing chart-container height. | no deps (touches different files than TASK-001; safe to run in parallel)
- TASK-003 | Claude | `renderAnalysisChart(canvasId, series, options)` in `static/js/charts.js` (plain global function, classic-script convention) — multi-dataset chart: price line, optional SMA20/SMA50, optional labeled reference lines, matching the existing `_destroyChart` lifecycle pattern. | deps: 001, 002
- TASK-004 | Claude | `static/js/core/chart-modal.js` — the modal controller: `openChartModal({ ticker, history, entry, stop, meta, triggerEl })` / `closeChartModal()`, focus trap + Escape + backdrop-click-to-close, timeframe pill wiring, SMA toggle wiring, focus-restore-with-attached-check on close. Orchestrates TASK-001's math and TASK-003's renderer. | deps: 001, 002, 003
- TASK-005 | Codex | Wire all three views to the new modal, replacing the inline chart entirely: `static/js/core/ui-helpers.js` (replace `chartToggleButtonHTML`/`wireChartToggles`/`refreshOpenCharts` with a single open-analysis button/wiring helper), `static/js/views/positions.js` (real entry/stop), `static/js/views/shortlist.js` (no reference lines), `static/js/views/market.js` (`stop_loss` labeled "Scanner stop" for buys, `breakdown_level` labeled distinctly for sells; remove `_signalChartRowHTML` and the inline chart-toggle column entirely). | deps: 004 (sequenced, not parallel — these files are exactly where TASK-004's public API must already be stable; running this concurrently with 004 risks the same kind of file-clobber this project has hit before)
- TASK-006 | Claude | `static/js/core/router.js`: close the modal at the start of `route()` so it can't outlive the view it was opened from. Tests (pure math functions, DOM/ARIA structure, per-view reference-line correctness) + full-suite regression + module-graph/Flask verification, matching every prior sprint's rigor. | deps: 005

## Explicitly out of scope for this sprint

- OHLCV/candlestick charts, volume histograms, RSI/MACD, or any indicator needing more than the existing daily-close series — a separate backend + vendoring sprint (`scripts/fetch_price_history.py` would need to fetch and cache OHLCV, `dashboard.py`'s price-history route would need a schema version, and Chart.js would need a financial-charts plugin it doesn't currently have).
- A second small "expand" icon alongside a retained inline chart (Antigravity's alternative — deliberately not taken; see disagreement resolution above).
- User-drawn annotations, saved chart layouts, or comparison-to-SPY overlays.
