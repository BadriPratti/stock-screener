# TASK-006 Result

## Outcome

TASK-006 is implemented and verified.

Created:

- `static/js/views/run.js`
- `static/js/views/scan.js`
- `tests/js/test_auto_sync_form_guard.js`

Modified:

- `static/js/dashboard.js`
- `static/js/core/jobs.js`

The Run Simulation and Full Scan renderers now live in their own view modules. `dashboard.js` imports both renderers and retains only application composition, sync handling, global inline-handler setup, and router initialization.

Both new synchronous renderers use the shared `currentView` guard before mounting their DOM. There is no async gap today, but retaining the guard keeps their route ownership explicit and matches the convention used by the other view modules if either renderer later gains an initial await.

## Job panel decision

All three Run Simulation cards and the Full Scan card now use `jobPanelHTML` from `static/js/components/job-panel.js`. This is behavior-compatible with `wireJobCard` and `watchJob`: the component emits the same `${id}-pill`, `${id}-run`, `${id}-output`, and `${id}-result` IDs those functions query.

The Scan panel keeps its 520px maximum width through a wrapper, and each checkbox label occupies its own row. Job kinds, request payloads, default input values, result rendering, and job reconnection behavior are unchanged.

After the migration, `rg -n "jobCardHTML" static/js` returned no matches. `jobCardHTML` was therefore dead code and was removed from `static/js/core/jobs.js`; there are no remaining imports or exports to update.

## Auto-sync form-state fix

On a successful sync that pulled new data, `doSync(silent)` now calls `route()` only when the action was manual or the current view is neither `run` nor `scan`:

```js
if (!silent || (currentView !== 'run' && currentView !== 'scan')) route();
```

Both views are protected because each contains unsaved editable controls. Protecting Scan's checkboxes as well as Run's numeric inputs is consistent and has no additional data-staleness cost.

The sync POST, success and "Already up to date" detection, existing toast behavior, error behavior, and normal rerender behavior on all other views are unchanged. A manual Sync latest action still rerenders every view. When a background sync pulls data while Run or Scan is open, the server-side data is updated and the success toast is shown without replacing the form DOM; the next user navigation renders the newly synced data normally. This focused route guard avoids introducing form persistence state and its synchronization complexity.

## Constraint checks

- Did not modify `static/js/views/positions.js`, `shortlist.js`, `market.js`, or `backtests.js`.
- Did not modify `static/js/core/ui-helpers.js` or any of its exports.
- Did not modify `static/js/charts.js`, `static/css/dashboard.css`, or `static/js/core/api.js`, `state.js`, or `router.js` as part of TASK-006.
- Did not touch anything under `position/`.
- Did not run `git commit` or `git push`.
- `git diff --check` passed with no output.
- No `jobCardHTML` references remain under `static/js`.

The worktree already contained the approved, uncommitted TASK-002 through TASK-005 changes before this task began. Those pre-existing paths remain visible in the repository-level Git output below. An untracked `.sprint/results/TASK-008-codex.md` also appeared during this turn from another process and was not touched. TASK-006 itself touched only the six files listed above plus this report.

## Verification output

### Module syntax

Command:

```text
for f in static/js/dashboard.js static/js/core/jobs.js static/js/views/run.js static/js/views/scan.js tests/js/test_auto_sync_form_guard.js; do node --input-type=module --check < "$f" || exit 1; echo "$f: syntax ok"; done
```

Output:

```text
static/js/dashboard.js: syntax ok
static/js/core/jobs.js: syntax ok
static/js/views/run.js: syntax ok
static/js/views/scan.js: syntax ok
tests/js/test_auto_sync_form_guard.js: syntax ok
```

### Auto-sync form guard characterization

Command:

```text
node tests/js/test_auto_sync_form_guard.js
```

Output:

```text
(node:78515) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
test_auto_sync_form_guard.js: all assertions passed
```

The test proves:

- a successful silent sync on `run` does not call `route()`;
- a successful silent sync on `market` does call `route()`;
- successful manual syncs call `route()` on both protected views.

### Existing Node characterizations

Command:

```text
node tests/js/test_live_guard.js && node tests/js/test_start_job.js
```

Output:

```text
(node:78516) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
test_live_guard.js: all assertions passed
(node:78509) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
test_start_job.js: all assertions passed
```

### Dashboard job tests

Command:

```text
venv/bin/python -m pytest tests/test_dashboard_jobs.py -v
```

Output:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- /Users/badripratti/Desktop/stock-screener/venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/badripratti/Desktop/stock-screener
plugins: mock-3.15.1, anyio-4.14.2
collecting ... collected 8 items

tests/test_dashboard_jobs.py::test_unknown_job_returns_404 PASSED        [ 12%]
tests/test_dashboard_jobs.py::test_prune_old_jobs_keeps_running_and_recent_jobs PASSED [ 25%]
tests/test_dashboard_jobs.py::test_momentum_status_empty_shape_not_error PASSED [ 37%]
tests/test_dashboard_jobs.py::test_news_empty_shape_not_error PASSED     [ 50%]
tests/test_dashboard_jobs.py::test_price_history_empty_shape_not_error PASSED [ 62%]
tests/test_dashboard_jobs.py::test_read_json_parses_literal_nan_without_raising PASSED [ 75%]
tests/test_dashboard_jobs.py::test_read_json_falls_back_on_malformed_json PASSED [ 87%]
tests/test_dashboard_jobs.py::test_read_json_falls_back_on_missing_file PASSED [100%]

============================== 8 passed in 0.28s ===============================
```

### Flask route and content-type checks

Used `dashboard.app.test_client()` and asserted status 200 for every route plus a JavaScript mimetype for every `.js` route.

Output:

```text
/ status=200 content_type=text/html; charset=utf-8
/static/js/dashboard.js status=200 content_type=text/javascript; charset=utf-8
/static/js/views/run.js status=200 content_type=text/javascript; charset=utf-8
/static/js/views/scan.js status=200 content_type=text/javascript; charset=utf-8
```

### Git diff and status

`git diff --stat` output:

```text
 .sprint/SPRINT_PLAN.md                     |   32 +-
 .sprint/STATUS.md                          |   18 +-
 static/css/dashboard.css                   |   53 ++
 static/js/dashboard.js                     | 1117 +---------------------------
 templates/dashboard.html                   |    2 +-
 tests/__pycache__/__init__.cpython-313.pyc |  Bin 201 -> 201 bytes
 6 files changed, 101 insertions(+), 1121 deletions(-)
```

Git does not include untracked files in `git diff --stat`. Final `git status --short` output:

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
?? .sprint/results/TASK-006-codex.md
?? .sprint/results/TASK-008-codex.md
?? static/js/components/
?? static/js/core/
?? static/js/views/
?? tests/js/
?? tests/test_dashboard_jobs.py
```
