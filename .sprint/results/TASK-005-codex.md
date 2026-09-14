# TASK-005 Result

## Outcome

Market and Backtests were migrated from `static/js/dashboard.js` into dedicated ES modules without changing their rendering, refresh, sorting, or stale-render behavior.

## Files

- Created `static/js/views/market.js` with `renderMarketView`, all Market-only helpers, and Market's `_marketTop20Tickers` module state.
- Created `static/js/views/backtests.js` with `renderBacktestsView`, `loadBacktest`, and `renderTradeRows`.
- Updated `static/js/dashboard.js` to import the two render functions and remove the migrated implementations.
- Added `cleanEmoji`, `safeHref`, and `toggleReasons` exports to `static/js/core/ui-helpers.js`.
- Created this report at `.sprint/results/TASK-005-codex.md`.

## Shortlist news injection

`_newsSectionHTML` and `_loadNewsGroup` are exported from `views/market.js` because Shortlist needs them at runtime. `dashboard.js` imports both and continues to call:

```js
configureShortlistNews({ newsSectionHTML: _newsSectionHTML, loadNewsGroup: _loadNewsGroup });
```

`views/shortlist.js` was not changed and does not import `views/market.js`, preserving the existing dependency-injection boundary.

## Helper placement

Grep confirmed that Market uses `cleanEmoji`, `safeHref`, and `toggleReasons`; Backtests uses none. The helpers were added to `core/ui-helpers.js` to avoid a dashboard-to-view circular import and keep pure UI helpers in the established shared location. `dashboard.js` imports `toggleReasons` and retains the one-time `window.toggleReasons = toggleReasons` assignment required by the existing inline handler. The emoji-matching expression uses Unicode escapes so the source contains no emoji characters while preserving the same matches.

## Component adoption

No additional components were adopted. The existing Market metrics include nested value markup, its signal-table empty rows have specific colspan and styling, and Backtests has custom click sorting and column semantics. Replacing these with the generic components would risk changing rendered structure, styling, or sorting behavior, so the original markup was preserved.

## Constraint checks

- Preserved both Market and both Backtests `currentView` stale-render guards exactly.
- Did not change `views/positions.js` or `views/shortlist.js`.
- Added exports to `core/ui-helpers.js` without modifying its existing exports.
- Did not change `renderRunView`, `renderScanView`, `doSync`, or `AUTO_SYNC_INTERVAL_MS` while removing the preceding views.
- Did not change `static/js/charts.js`, `static/css/dashboard.css`, or `core/api.js`, `core/state.js`, `core/router.js`, `core/jobs.js`, or `core/refresh.js`.
- Did not touch anything under `position/`.
- `git diff --check` passed for all TASK-005 JavaScript files.
- No commit or push was run.

## Verification

Syntax checks, run as `node --input-type=module --check < file`:

- `static/js/dashboard.js`: passed
- `static/js/core/ui-helpers.js`: passed
- `static/js/views/market.js`: passed
- `static/js/views/backtests.js`: passed

JavaScript tests:

```text
test_live_guard.js: all assertions passed
test_start_job.js: all assertions passed
```

Python tests:

```text
tests/test_dashboard_jobs.py: 8 passed in 0.10s
```

Flask in-process test client:

```text
/ 200 text/html; charset=utf-8
/static/js/dashboard.js 200 text/javascript; charset=utf-8
/static/js/views/market.js 200 text/javascript; charset=utf-8
/static/js/views/backtests.js 200 text/javascript; charset=utf-8
```

Final `git diff --stat`:

```text
 .sprint/SPRINT_PLAN.md                     |   32 +-
 .sprint/STATUS.md                          |   18 +-
 static/css/dashboard.css                   |   53 ++
 static/js/dashboard.js                     | 1027 +---------------------------
 templates/dashboard.html                   |    2 +-
 tests/__pycache__/__init__.cpython-313.pyc |  Bin 201 -> 201 bytes
 6 files changed, 99 insertions(+), 1033 deletions(-)
```

Final `git status --short`:

```text
 M .sprint/SPRINT_PLAN.md
 M .sprint/STATUS.md
 M static/css/dashboard.css
 M static/js/dashboard.js
 M templates/dashboard.html
 M tests/__pycache__/__init__.cpython-313.pyc
?? .sprint/council/
?? .sprint/results/TASK-002-codex.md
?? .sprint/results/TASK-003-claude.md
?? .sprint/results/TASK-004-codex.md
?? .sprint/results/TASK-005-codex.md
?? static/js/components/
?? static/js/core/
?? static/js/views/
?? tests/js/
?? tests/test_dashboard_jobs.py
```

The worktree was already dirty at task start with every status entry above, including the TASK-005 report path and the untracked parent directories. Comparing the initial and final scope, TASK-005 changed only `static/js/dashboard.js`, `static/js/core/ui-helpers.js`, `static/js/views/market.js`, `static/js/views/backtests.js`, and this report. The broad untracked directory entries prevent Git's short status from listing the new view files individually; no other pre-existing worktree changes were modified.
