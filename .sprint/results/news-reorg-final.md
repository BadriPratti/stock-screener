# News Section Reorganization — Final Report

## What was built

A new shared, framework-free news component (`static/js/components/news.js`) replacing the flat, unbounded per-ticker headline dump the user complained about. Key behavior:

- 2 headlines per ticker by default, newest-first (missing/invalid dates sort last, stably).
- Real accessible expand control: `<button aria-expanded aria-controls>` + native `hidden` attribute, not the app's existing `toggleReasons` (which both council investigations independently flagged as missing `aria-expanded` and not correctly restoring its label on re-collapse).
- Expand/collapse state lives in a module-level `Set` keyed by `"group:ticker"`, not the DOM — the 90-second live-refresh fully replaces the news body's `innerHTML`, so anything tracked only in DOM state (an inline style, an open `<details>`) would silently collapse under the user mid-read every tick. Both agents flagged this as the critical implementation trap; it's the one thing that would have made the whole redesign feel broken in practice if missed.
- Deduplicates headlines within a ticker by canonical URL.
- Renders a headline with no safe http(s) URL as plain text, not a misleading link.
- Preserves the caller's ticker order (Shortlist's rank order), and renders an empty-state card for any ticker missing from the API response instead of letting it silently vanish (`Object.keys()` on the response used to be the only source of which tickers rendered at all).
- Added a "Jump to news ↓" button on Shortlist, since 5 pick cards with expandable price charts can push the news section far down the page — directly addresses the "constantly scrolling" half of the complaint.

Wired into `shortlist.js` (which now imports directly from the new component) and `dashboard.js` (removed the now-unnecessary `configureShortlistNews` dependency-injection wiring, which existed only because the shared implementation used to live inside `market.js`).

## Judgment calls between the two agents

Both agents converged almost completely (2-headline cap, sort-by-recency, module-state for expand tracking, dedup, extract into a shared module). Two divergences:

1. **Antigravity proposed relative-time labels ("2h ago") and title line-clamping; Codex didn't mention either.** Adopted relative-time formatting — cheap and it directly answers the user's "no way to tell what's recent" pain point. Deferred line-clamping (CSS-only polish, not core to the complaint).
2. **Antigravity proposed Market-specific treatment** (activity-first ticker sorting, a consolidated "no news for: X, Y, Z" footnote for large position lists). Not implemented — Market's news section wasn't touched at all this pass (see below), so this is now documented as explicit follow-up work for whoever migrates Market's news rendering later.

## Critical scope boundary: Market view untouched

`static/js/views/market.js` was under active, concurrent edit by a separate in-flight sprint (scatter chart, then a tabbed Buy/Sell registry) for the entire duration of this work. Both council investigations independently flagged this risk and recommended either sequencing after that sprint, or extracting into a shared module that avoids editing `market.js` at all. Took the second path: the redesign lives entirely in the new `components/news.js`; `market.js`'s own `_newsSectionHTML`/`_loadNewsGroup`/`_renderNewsGroupHTML` were never opened for editing and are unchanged. Confirmed via `git diff --stat static/js/views/market.js static/js/charts.js` showing only the other sprint's edits, none of mine.

**Consequence, stated plainly**: Shortlist's news section is fully redesigned. Market's two news sections (positions, buy) still show the old unbounded list — unchanged, not regressed, just not yet migrated. Documented as a follow-up task in `.sprint/SPRINT_PLAN_NEWS.md`.

## A real bug found in an existing test while integrating

`tests/js/test_shortlist_empty_state.js` regex-patches `shortlist.js`'s known import lines to mock them for a standalone test run. Adding the new `components/news.js` import to `shortlist.js` broke that test (it tried to resolve the real relative import from a temp directory). Fixed by adding a matching mock for the new import line, keeping that test's existing pattern intact — not a scope violation since the test itself isn't owned by the concurrent Market sprint, and leaving it broken would have been a silent regression.

## Verification

```
node --input-type=module --check on: static/js/components/news.js, static/js/views/shortlist.js, static/js/dashboard.js — all pass
CSS brace-balance check on dashboard.css: 0 (balanced)

node tests/js/test_live_guard.js            → all assertions passed
node tests/js/test_start_job.js             → all assertions passed
node tests/js/test_auto_sync_form_guard.js  → all assertions passed
node tests/js/test_shortlist_empty_state.js → all assertions passed (after the fix above)
node tests/js/test_news_component.js        → all assertions passed (new, 8 assertions covering
                                                sorting, invalid dates, cap/expand threshold, empty
                                                tickers, ticker-order preservation, dedup, unsafe URLs)

venv/bin/python -m pytest tests/test_dashboard_jobs.py -v → 8/8 passed (unaffected; sanity check)

Real ES module graph load (dashboard.js → all its imports) under Node with a DOM stub:
resolved and evaluated with zero errors, including with the Market sprint's
concurrent in-flight market.js/charts.js changes present in the same tree.

git diff --stat static/js/views/market.js static/js/charts.js → shows ONLY the
other sprint's own edits; zero lines from this work.
```

No commit or push was made. Changes are in the working tree for the coordinator to review alongside the Market View Redesign sprint's own changes.
