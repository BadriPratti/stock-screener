You are participating in an Engineering Council (one independent second opinion, not the full 3-agent council — this is a MEDIUM-scoped UI reorganization, not an architecture change). Do NOT modify any file except the single output file named below. Do not run git commands that mutate anything, no python/node execution beyond reading.

Repository: /Users/badripratti/Desktop/stock-screener (Flask + pywebview dashboard; native ES modules, no build step; Chart.js). NEVER open/reference `position/`.

## The user's request (their words)
"we need to have better way to organize this because the market thing is sooo long and I am scrolling down a lot we need better way to organize we can create button that then drops down the list or have tabs that those section"

## Why the page got this long (context you need)
static/js/views/market.js (480 lines) currently renders, top to bottom, ALL of:
1. Stats row (Buy/Sell signal counts, top score, universe size, SPY phase)
2. Market Breadth donut chart + SPY Regime card (side by side)
3. THE BUY OPPORTUNITY MAP — a persistent tracked-stock scatter chart (static/js/components/market-map.js, 624 lines) that a same-day sprint just added: replay controls (play/pause/scrub/speed/live), filter chips (tier/entry-quality/streak/search), a scheduler status card (auto-refresh toggle, publish toggle, run-now), a big canvas, AND a full sortable "Tracked stocks" table listing every record (can be 400+ rows) underneath it
4. The Top 20 Combined Pool table (renderTop20Table, from ui-helpers.js, shared with Shortlist)
5. Buy/Sell Signal tabs (already tabbed internally, role="tablist" — see market.js:278-289) each listing up to 50 rows with expandable reasons and a per-row "price analysis" button (opens the new full-screen chart modal)

So today, on one scroll, a user passes: 5 stat tiles -> 2 charts -> an entire second data-dense sub-app (map+table, easily 400+ tracked rows) -> a 20-row table -> up to 50 more rows. That's the "sooo long" complaint, and it just got much worse today because of item 3.

## Existing patterns already in this codebase (reuse, don't reinvent)
- Accessible tabs already exist: market.js:278-289 (role="tablist"/"tab"/"tabpanel", aria-selected, arrow-key navigation wired in `_wireSignalTabs`) — the Buy/Sell split already uses this.
- static/js/views/consistency.js (297 lines) is a full separate VIEW/nav-item pattern (sidebar item, its own route) — an alternative to in-page tabs is a separate page.
- static/js/core/router.js is a simple hash router (`#/market`, `#/consistency`, etc.) already supports sub-state? Check whether it supports a second-level hash segment (e.g. `#/market/map`) for deep-linking a section, or only top-level views.
- static/css/dashboard.css (522 lines) has the design tokens/spacing to match (read its `:root` variables and existing `.card`, `.signal-tabs` styles before proposing new components).
- The full-screen chart modal (static/js/core/chart-modal.js, just built) is a precedent for "let something be big in an overlay rather than always inline" — could the map's "Expand" behavior (it already exists: static/js/components/market-map.js has an Expand button per SPRINT_PLAN_LIVE_CHART.md) be leveraged instead of, or alongside, collapsing sections?

## Two structural options the user floated, verbatim
(a) "a button that then drops down the list" — collapsible/expandable sections (accordion), collapsed by default or remembering state.
(b) "tabs that those section[s]" — page-level tabs so only one section is visible/rendered at a time (e.g. Overview / Buy Opportunity Map / Top 20 / Buy Signals / Sell Signals).

## Questions to answer with repository evidence
1. Which of (a) accordion or (b) tabs — or a hybrid — fits this data best? Consider: some sections (stats row, regime) are things a user wants to glance at every visit (arguably should NOT be hidden behind a click); the map+table is the heaviest, most scroll-inducing block and a natural first tab; Buy/Sell already has internal tabs — nesting tabs inside tabs is a known UX smell, so how does the top-level scheme compose with the EXISTING Buy/Sell tablist without becoming "tabs inside tabs inside an accordion"?
2. State and URL: should the selected section be reflected in the URL hash (deep-linkable, survives refresh, shareable) — check router.js for whether this is easy or requires new plumbing. Should it persist across visits (localStorage) or always reset?
3. Performance: does hiding a section with CSS (`hidden`/`display:none`) avoid doing the section's own work (Chart.js render, fetches, the map's rAF animation loop) while inactive, or does it need to actually not-mount/lazy-mount to avoid wasted work and the "Canvas is already in use" trap this repo has hit before? The map has a live requestAnimationFrame loop and a 90s "Live" poll — what MUST keep running even when its tab isn't active (so the live badge / new-snapshot notice is still honest), and what should pause?
4. Where do the stats row and the Market Breadth/SPY Regime cards belong — always-visible header, their own tab, or folded into an "Overview" default tab?
5. Accessibility: keyboard navigation, ARIA roles, and reduced-motion consistent with what's already established in this codebase (see market.js's existing tablist wiring and dashboard.css's reduced-motion rules from the chart-modal/market-map sprints).
6. Migration risk: existing plain-Node characterization tests reference DOM ids/classes in market.js and market-map.js (tests/js/test_market_*.js) — what's the least-churn way to restructure without breaking every existing test's selectors, vs. where updating tests is unavoidable and worth it.
7. Mobile/narrow-window behavior: this is a desktop app with a documented 760px defensive breakpoint (not primary mobile target) — do tabs remain usable at that width, or do they need to collapse to a select/accordion below it?

Give a recommended structure (name the sections/tabs explicitly, in order), a concrete state/URL design, a performance/lazy-mount policy for the map specifically, and a task breakdown (files touched, dependencies, test impact). Be concise — this is a MEDIUM-scoped UI task, not a research paper. Write your analysis to .sprint/council/codex-market-reorg.md (this is the only file you may create). Also print a short summary to stdout.
