# TASK-003 — Extract router/jobs/refresh/api into core modules (Claude)

## Files created

- `static/js/core/api.js` — `fetchJSON`.
- `static/js/core/state.js` — `content`/`pageTitle`/`pageMeta` DOM refs, `currentView` (live-binding export) + `setCurrentView`.
- `static/js/core/refresh.js` — `LIVE_INTERVAL_MS`, `_stopLive`, `_startLive`, `liveBadgeHTML`, `_liveGuarded`. Exact code covered by `tests/js/test_live_guard.js`, only relocated.
- `static/js/core/jobs.js` — `startJob` (the FIX-001 promise-resolves-on-completion version), `jobCardHTML`, `_activeJobs`, `_watchingJobIds`, `watchJob`, `wireJobCard`.
- `static/js/core/router.js` — `route()` + `initRouter(viewsMap)`. `VIEWS` itself stays in `dashboard.js` (it references the view render functions, which still live there) and is passed in via `initRouter(VIEWS)`.

## Files modified

- `static/js/dashboard.js` — removed the five blocks above (225 lines net removed), added the five `import` lines, renamed `_currentView` → `currentView` at all 8 call sites (now an imported live binding from `state.js`, written only by `router.js`), replaced the trailing `route();` bootstrap call with `initRouter(VIEWS)`, added `window.toggleReasons = toggleReasons;` (see judgment call below).
- `templates/dashboard.html` — `dashboard.js`'s `<script>` tag now has `type="module"` (required to use `import`). `charts.js`'s tag is untouched (still a classic script, still exposes its render functions as globals, which `dashboard.js` continues to call as bare identifiers — module scripts still see pre-existing globals).
- `tests/js/test_live_guard.js`, `tests/js/test_start_job.js` — updated `fs.readFileSync` path to point at `core/refresh.js` / `core/jobs.js` respectively. No assertions changed. `extract()` itself needed no changes: it locates `function <name>(`, so the `export ` keyword (which sits before `async `/`function`) is simply left outside the match, same as it already handled a leading `async `.

## Judgment calls

1. **`jobCardHTML` kept, not swapped for TASK-002's `components/job-panel.js`.** TASK-002 built a more general `jobPanelHTML` that could replace it, but doing so means editing `renderRunView`/`renderScanView`'s call sites — explicitly out of scope for TASK-003 (view-rendering functions are TASK-004/005/006 territory). Moved `jobCardHTML` as-is into `core/jobs.js` since it's tightly coupled to `watchJob`/`wireJobCard`'s DOM id convention. **Flagging for TASK-006** (owns the Run/Scan views): switch `renderRunView`/`renderScanView` to `jobPanelHTML` from `components/job-panel.js` and delete `jobCardHTML` from `core/jobs.js` at that point.
2. **`doSync`/`AUTO_SYNC_INTERVAL_MS` left in `dashboard.js`**, not moved to `refresh.js`. It's thematically "refresh" but is really app-bootstrap wiring — it directly grabs `syncBtn` from the DOM and calls `route()` from router.js, and moving it would touch bootstrap sequencing for no behavioral gain. Left as-is; can revisit in TASK-010 (final integration) if the module boundary still feels wrong once every view is migrated.
3. **`currentView` naming**: dropped the leading underscore now that it's a real cross-module export (`state.js`) rather than a same-file private convention. Every read site in `dashboard.js` was mechanically renamed; no logic changed.
4. **`window.toggleReasons = toggleReasons`**: required because `renderBuyRows` generates `onclick="toggleReasons(this)"` in a template literal, and module scripts don't leak declarations onto `window` the way the old classic `<script>` did. This is the only such inline handler in the codebase (checked via `grep -n "onclick=" static/js/dashboard.js` and confirmed no `onclick=` attributes exist in `templates/dashboard.html` itself).

## Verification

- `node --input-type=module --check` on all 5 new core files and on `dashboard.js`: all pass.
- Full module graph resolution test (Node, stubbed `document`/`window`/`fetch`): `import('./dashboard.js')` resolves with no errors — confirms every `import` path across `dashboard.js` → `core/*` → `core/*` is correct, not just syntactically valid in isolation.
- Live end-to-end check: started `dashboard.py --port 5099` (a fresh instance — a stale pre-existing process from earlier in the session already held :5050), confirmed via `curl` that `dashboard.js` is served with `type="module"` and all 5 `core/*.js` files return 200, then did a headless-Chrome DOM dump of the page. The Positions view (default route) rendered fully — real data (5 positions), `pageTitle` set to "Positions", nav item marked `active` — proving `initRouter(VIEWS)` → `route()` → `renderPositionsView()` → `fetchJSON`/`startJob` all executed correctly through the new module boundaries. No JS errors in Chrome's stderr (only unrelated macOS headless-Chrome display/process-policy noise).
- `node tests/js/test_live_guard.js && node tests/js/test_start_job.js`: both pass, 0 assertion changes.
- `venv/bin/python -m pytest tests/test_dashboard_jobs.py -v`: 8/8 pass (unaffected by this JS-only refactor; run as a sanity check per instructions — also fixed one incorrect test assumption in this same session, see the `test_read_json_*` tests, unrelated to TASK-003 itself).
- `git diff --stat` for this task's own changes: only `static/js/dashboard.js`, `templates/dashboard.html`, plus the two `tests/js/*.js` path updates and 5 new files under `static/js/core/`. No view-rendering function (`renderShortlistView`, `renderMarketView`, `renderPositionsView`, `renderBacktestsView`, `renderRunView`, `renderScanView`, or their private helpers) had its body altered beyond the mechanical `currentView` rename.

All changes are unstaged in the working tree, nothing committed, nothing under `position/` touched.
