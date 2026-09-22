# TASK-006 — Consistency leaderboard

## Files changed

- `static/js/views/consistency.js` — added the Consistency route UI, pure leaderboard builders/sorters, guarded fetching, accessible controls/table, gap and warning notes, and calm empty/error handling.
- `static/js/dashboard.js` — added the Consistency view import and `VIEWS` registration.
- `templates/dashboard.html` — added the requested Consistency link inside the Analyze navigation group.
- `static/css/dashboard.css` — added only the controls, notes, table, sortable-header focus/indicator, and dropped-row styles needed by this view, adjacent to the existing pick-history rules.
- `tests/js/test_consistency_view.js` — added plain-Node coverage for ordering, all column directions, null placement, stability, formatting, escaping, empty/error states, request races, stale navigation, accessibility wiring, and route/nav registration.

The repository was already dirty with the approved earlier sprint work. Comparing the final status with the pre-task status, this task changed only those five permitted paths and this report; no chart code, `static/js/core/ui-helpers.js`, or `position/` content was touched.

## Final behavior

`#/consistency` opens with Shortlist and 5 scans selected. Either select refreshes only the live results region. A monotonic request sequence prevents an older response from repainting a newer selection, and the view also discards a response after navigation away.

The table columns are Ticker, Appearances, Current streak, Longest streak, First seen, Last seen, Best rank, Avg rank, Avg score, Score change, and Status. The initial order is appearances descending, current streak descending, average rank ascending, then ticker ascending. Every header is mouse- and keyboard-sortable; user-selected sorts are stable, and null/undefined values stay last in both directions. The initial Appearances header exposes `aria-sort="descending"`; active `aria-sort` state follows later sorts.

Rows use the API's real denominator and a rounded whole-number percentage. Score changes use an explicit `+` when positive and `-` when unavailable. Dates reuse `formatSessionDate`; the introductory copy reuses `consistencyCaptionText`. Status is always explicit text (`On latest scan` or `Dropped out`). Dropped rows use muted text without reducing the whole row's opacity.

## Judgment calls

- `buildLeaderboardRows` returns rows in the required default compound order, while `sortLeaderboardRows` handles one requested column at a time and preserves input order for equal values. This keeps both behaviors independently testable.
- Numeric display is capped at two decimal places with insignificant trailing zeroes removed. The appearance percentage is derived from appearances and the real denominator when both exist, using `appearance_rate` only as a fallback.
- Gap copy summarizes the first dated gap and reports how many additional gap records exist, keeping the line short while retaining the session-streak caveat.
- An unusable payload or failed request uses the same calm `No pick history yet` state as an empty ledger. A valid history window containing no ticker rows also degrades to that non-blank state.

## Verification

### JavaScript suite

Command:

```text
for f in tests/js/*.js; do node "$f"; done
```

Result: all 12 files passed, including `test_consistency_view.js`.

```text
test_auto_sync_form_guard.js: all assertions passed
test_consistency_view.js: all assertions passed
test_live_guard.js: all assertions passed
test_market_default_scan.js: all assertions passed
test_market_scatter_points.js: all assertions passed
test_market_signal_extras.js: all assertions passed
test_market_signal_tabs.js: all assertions passed
test_news_component.js: all assertions passed
test_pick_history_badges.js: all assertions passed
test_shortlist_consistency.js: all assertions passed
test_shortlist_empty_state.js: all assertions passed
test_start_job.js: all assertions passed
```

### Syntax, CSS, and module graph

- `node --input-type=module --check` passed for `static/js/views/consistency.js`, `static/js/dashboard.js`, and `tests/js/test_consistency_view.js`.
- CSS brace check passed: `193 pairs`.
- `git diff --check` passed for all five permitted implementation/test paths.
- A real Node ESM import of `static/js/dashboard.js` with the requested minimal DOM/fetch/browser stubs resolved successfully: `dashboard.js ESM graph loaded`.

### Real API payload through the pure builder

The payload came from:

```text
venv/bin/python
dashboard.app.test_client().get('/api/pick-history?list=shortlist&window=5').get_json()
```

It was then passed into `buildLeaderboardRows`. Default-order output:

```text
LILA   5/5 (100%)  current 5  avg rank 2.2   change -6.6   On latest scan
LILAK  4/5 (80%)   current 2  avg rank 2.25  change -4.4   On latest scan
LTC    3/5 (60%)   current 3  avg rank 2.67  change +0.8   On latest scan
NVDA   2/5 (40%)   current 1  avg rank 3     change -7.79  On latest scan
OXY    2/5 (40%)   current 1  avg rank 4.5   change -7.9   On latest scan
NGL    2/5 (40%)   current 0  avg rank 1     change +4.06  Dropped out
DVN    2/5 (40%)   current 0  avg rank 4.5   change -3.6   Dropped out
CRWD   2/5 (40%)   current 0  avg rank 5     change -1.95  Dropped out
ASND   1/5 (20%)   current 0  avg rank 2     change -      Dropped out
BP     1/5 (20%)   current 0  avg rank 4     change -      Dropped out
ET     1/5 (20%)   current 0  avg rank 5     change -      Dropped out
```

This confirms LILA is first with 5/5 appearances and a five-scan streak.

### Python regression tests

Command:

```text
venv/bin/python -m pytest tests/test_dashboard_jobs.py tests/test_pick_history_api.py -q
```

Result:

```text
19 passed in 0.59s
```

### Working-tree scope

`git status --porcelain` was run. It still shows the substantial pre-existing uncommitted work from TASK-001 through TASK-005 and other planned sprints. Relative to the status captured before implementation, TASK-006 added/changed only:

```text
 M static/css/dashboard.css
 M static/js/dashboard.js
 M templates/dashboard.html
?? static/js/views/consistency.js
?? tests/js/test_consistency_view.js
?? .sprint/results/pick-TASK-006-codex.md
```

No commit or push was run.
