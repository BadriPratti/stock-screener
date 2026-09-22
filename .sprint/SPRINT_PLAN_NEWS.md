# Sprint: News Section Reorganization (parallel to the Market View Redesign sprint)

## Request (user's own words)

"I am tired of scrolling down constantly in the shortlist trying to look at the news section and stuff and the news section is organized at all like its just bunch of news articles I honestly want you to organize these news articles much better please"

## Engineering Council process

MEDIUM-classified UI refactor. Claude + Codex + Antigravity all independently investigated (transcripts: `.sprint/council/codex-news-redesign.md`, `.sprint/council/antigravity-news-redesign.md`). This sprint ran fully in parallel with the concurrent Market View Redesign sprint (`.sprint/SPRINT_PLAN.md`) — hence separate plan/status files, to avoid two sprints stomping one shared `.sprint/SPRINT_PLAN.md`.

## Converged decisions

- Default cap: 2 headlines per ticker, sorted newest-first (missing/invalid `pub_date` sort last, stable).
- Real `<button aria-expanded aria-controls>` + native `hidden` attribute for "+N more" / "Show less", not the existing `toggleReasons` pattern (which both agents independently flagged as missing `aria-expanded` and mis-restoring its collapsed label).
- Expand/collapse state tracked in a module-level `Set` keyed by `"group:ticker"`, NOT in the DOM — required because the 90-second live-refresh does a full `innerHTML` replacement of the news body; both agents independently identified this as the critical implementation trap.
- Preserve the caller's requested ticker order (not `Object.keys(newsByTicker)`), so a ticker missing from the API response still gets an empty-state card instead of silently vanishing, and Shortlist's rank order isn't alphabetized.
- Deduplicate headlines within a ticker by canonical URL (fallback: normalized title).
- A headline with no safe http(s) URL renders as non-clickable text, not a misleading `<a href="#">`.
- A "Jump to news ↓" button on Shortlist, since 5 pick cards (with expandable charts) can push news far down the page.

## Divergence between agents, and the call made

Antigravity additionally proposed relative-time formatting ("2h ago") and title line-clamping; Codex didn't address either. Relative-time formatting was adopted (cheap, directly addresses "no way to tell what's recent" from the user's complaint) via `_relativeTime()` in the new component. Title line-clamping (CSS `-webkit-line-clamp`) was deferred — lower priority, not part of the core complaint, can be a follow-up.

Antigravity also proposed Market-specific treatment (activity-first ticker sorting, consolidated footnote for empty ETF tickers). Not implemented in this pass — see scope note below.

## Critical scope constraint: Market view was NOT touched

Both agents independently flagged that `static/js/views/market.js` was under active concurrent edit by the Market View Redesign sprint (scatter chart wiring, then a tabbed Buy/Sell registry) and recommended landing this sprint either after that one finishes, or by extracting the news functions into a new shared module that doesn't require editing `market.js` at all. **The second option was taken**: `_newsSectionHTML`/`_loadNewsGroup`/`_renderNewsGroupHTML` were NOT removed from `market.js` (that file was never opened for editing) — instead, a new `static/js/components/news.js` was created with the full redesign, and only `static/js/views/shortlist.js` and `static/js/dashboard.js` were wired to use it.

**Consequence**: Shortlist's news section has the full redesign. Market's two news sections (`positions`, `buy`) still use the original, unredesigned `_newsSectionHTML`/`_loadNewsGroup`/`_renderNewsGroupHTML` inside `market.js`, unchanged. This is a deliberate, documented scope boundary, not an oversight.

## Follow-up task (not done here, tracked for later)

Once the Market View Redesign sprint's `market.js` work is fully merged and stable, migrate `loadMarketNews` (in `market.js`) to import `loadNewsGroup`/`newsSectionHTML` from `static/js/components/news.js` instead of its own local `_loadNewsGroup`/`_newsSectionHTML`/`_renderNewsGroupHTML`, then delete the now-dead local copies from `market.js`. At that point also implement Antigravity's Market-specific suggestions (activity-first ticker sort, consolidated empty-ticker footnote, `tickerLimit` for large position lists) since `loadNewsGroup`'s signature was left open to accept a future `options` parameter for this.

## Files changed

- New: `static/js/components/news.js` (the redesigned shared component)
- New: `tests/js/test_news_component.js`
- Modified: `static/js/views/shortlist.js` (import from the new component instead of the `configureShortlistNews` injection pattern; added the "Jump to news" button)
- Modified: `static/js/dashboard.js` (removed the now-obsolete `configureShortlistNews` wiring and its import)
- Modified: `static/css/dashboard.css` (additive: `.news-headline-nolink`, `.news-extra:not([hidden])`, `.news-jump-btn`; renamed a section comment)
- Modified: `tests/js/test_shortlist_empty_state.js` (added a mock for the new `components/news.js` import shortlist.js now has, matching its existing mock-and-import pattern for every other import)

## Verification

- `node --input-type=module --check` on every touched/new JS file: pass.
- CSS brace-balance check: 0 (balanced).
- Full existing JS suite (`test_live_guard.js`, `test_start_job.js`, `test_auto_sync_form_guard.js`, `test_shortlist_empty_state.js`) + new `test_news_component.js`: all pass.
- `venv/bin/python -m pytest tests/test_dashboard_jobs.py -v`: 8/8 pass (unaffected, sanity check only).
- Real ES module graph load (`import('./static/js/dashboard.js')` under Node with a DOM stub): resolves and evaluates with no errors, even with the Market sprint's concurrent in-flight edits to `market.js`/`charts.js` present.
- `git status`/`git diff --stat` confirmed zero edits to `static/js/views/market.js`, `static/js/charts.js`, or the Market sprint's specific CSS additions (`.scatter-chart-wrap`, `.row-highlight-pulse`, `.signal-tabs*`).
