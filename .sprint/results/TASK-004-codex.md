# TASK-004 Result

## Outcome

Migrated the Positions and Shortlist views from `static/js/dashboard.js` into standalone ES modules without changing their data sources, DOM contracts, or interactions.

## Files

- Created `static/js/views/positions.js` with `renderPositionsView`, `POSITION_ACTION_LABELS`, `_positionsUploadCardHTML`, `refreshPositionsLive`, `wirePositionsUpload`, and `renderPositionsResults`.
- Created `static/js/views/shortlist.js` with `renderShortlistView`, `_shortlistPrices`, `_shortlistSeries`, `loadShortlistCharts`, `loadShortlistNews`, and the Shortlist-only agent badge helpers.
- Created `static/js/core/ui-helpers.js`. The name reflects that these are reusable HTML/DOM helpers shared across view modules, rather than application state or routing infrastructure.
- Updated `static/js/dashboard.js` to import both view renderers and the shared helpers, while leaving Market, Backtests, Run Simulation, Full Scan, news, and sync implementations in place.

## Helper boundaries

`ui-helpers.js` contains `CHART_ICON`, `_openCharts`, `chartToggleButtonHTML`, `wireChartToggles`, `refreshOpenCharts`, `MOMENTUM_LABELS`, `momentumBadgeHTML`, `loadMomentumStatus`, `paintMomentumSlots`, `showToast`, `redditCell`, `escapeHtml`, `fidelityLink`, and `renderTop20Table`. The constants and directly internal renderers stay unexported; the functions consumed by views are exported. `renderTop20Table` is shared by Shortlist fallback and Market, so it could not remain private to Shortlist.

Shortlist-only `catalystBadgeHTML`, `congressBadgeHTML`, and `fundamentalsFlagsHTML` remain local to `views/shortlist.js`. Market-only `cleanEmoji`, `safeHref`, and `toggleReasons` remain in `dashboard.js`; the existing `window.toggleReasons = toggleReasons` assignment is unchanged. `_marketTop20Tickers` also remains in `dashboard.js` because grep confirmed it is read and written only by the still-unmigrated Market view.

The protected `_newsSectionHTML`, `_loadNewsGroup`, and `_renderNewsGroupHTML` bodies remain untouched in `dashboard.js`. `configureShortlistNews` injects the first two into the Shortlist module at bootstrap, avoiding a circular import while respecting the TASK-005 boundary.

## Component adoption

Positions uses `emptyStateHTML` for its matching no-results block and `metricCardHTML` for the four simple summary cards. Their generated class and element structure matches the prior markup. The upload panel and Top 20 table stayed hand-built because their specialized DOM IDs, upload controls, and column markup do not cleanly fit the generic components without risking behavior or layout changes.

## Constraint checks

- Preserved both exact stale-render guards: `currentView !== 'positions'` and both `currentView !== 'shortlist'` checks.
- Did not edit `static/js/charts.js`, `static/css/dashboard.css`, `dashboard.py`, the five TASK-003 core modules, tests, or anything under `position/`.
- Did not change the bodies of `renderMarketView`, `renderBacktestsView`, `renderRunView`, `renderScanView`, `loadMarketNews`, `loadMarketScan`, `renderBuyRows`, `renderSellRows`, `_newsSectionHTML`, `_loadNewsGroup`, `_renderNewsGroupHTML`, or `doSync`; `AUTO_SYNC_INTERVAL_MS` remains `5 * 60 * 1000`.
- No git commit or push was run.

The repository was already dirty at task start from TASK-002/TASK-003 and sprint bookkeeping. The task-local implementation touched only `static/js/dashboard.js` and created `static/js/views/positions.js`, `static/js/views/shortlist.js`, and `static/js/core/ui-helpers.js`; this report is the only additional task file. Final `git status --short` still lists the pre-existing sprint files, CSS/template changes, test files, and Python cache recorded at task start, plus the new `static/js/views/` directory.

## Verification

Syntax and whitespace:

```text
$ for f in static/js/dashboard.js static/js/core/ui-helpers.js static/js/views/positions.js static/js/views/shortlist.js; do node --input-type=module --check < "$f" || exit 1; done
syntax checks passed

$ git diff --check
[no output]
```

JavaScript characterization tests:

```text
$ node tests/js/test_live_guard.js && node tests/js/test_start_job.js
test_live_guard.js: all assertions passed
test_start_job.js: all assertions passed
```

Python sanity tests:

```text
$ venv/bin/python -m pytest tests/test_dashboard_jobs.py -v
collected 8 items
tests/test_dashboard_jobs.py::test_unknown_job_returns_404 PASSED
tests/test_dashboard_jobs.py::test_prune_old_jobs_keeps_running_and_recent_jobs PASSED
tests/test_dashboard_jobs.py::test_momentum_status_empty_shape_not_error PASSED
tests/test_dashboard_jobs.py::test_news_empty_shape_not_error PASSED
tests/test_dashboard_jobs.py::test_price_history_empty_shape_not_error PASSED
tests/test_dashboard_jobs.py::test_read_json_parses_literal_nan_without_raising PASSED
tests/test_dashboard_jobs.py::test_read_json_falls_back_on_malformed_json PASSED
tests/test_dashboard_jobs.py::test_read_json_falls_back_on_missing_file PASSED
============================== 8 passed in 0.10s ===============================
```

Flask route and MIME verification:

```text
$ venv/bin/python dashboard.py --port 5098 --no-browser
Dashboard running at http://localhost:5098
* Serving Flask app 'dashboard'
* Debug mode: off
Operation not permitted
```

The managed sandbox prohibits binding a TCP listener, so the scratch server exited with status 1 and no process remained to kill. The same routes were then exercised through Flask's in-process HTTP test client, which uses the application's actual static-file routing and MIME resolution:

```text
/ 200 text/html; charset=utf-8
/static/js/dashboard.js 200 text/javascript; charset=utf-8
/static/js/views/positions.js 200 text/javascript; charset=utf-8
/static/js/views/shortlist.js 200 text/javascript; charset=utf-8
/static/js/core/ui-helpers.js 200 text/javascript; charset=utf-8
```

Repository inspection:

```text
$ git diff --stat
 .sprint/SPRINT_PLAN.md                     |  32 +-
 .sprint/STATUS.md                          |  18 +-
 static/css/dashboard.css                   |  53 +++
 static/js/dashboard.js                     | 707 ++---------------------------
 templates/dashboard.html                   |   2 +-
 tests/__pycache__/__init__.cpython-313.pyc | Bin 201 -> 201 bytes
 6 files changed, 112 insertions(+), 700 deletions(-)
```

Git does not include untracked files in `git diff --stat`; `git status --short` confirms the new `static/js/views/` files and `static/js/core/ui-helpers.js` under the already-untracked TASK-003 `static/js/core/` directory. The other listed changes match the dirty-worktree baseline captured before TASK-004 began.
