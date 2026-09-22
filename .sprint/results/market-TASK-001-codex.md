# TASK-001 Result: Persist current price

## Files changed

- `run_optimized_scan.py`: attaches `analysis['current_price']` to qualified buy and sell signal dictionaries before they are appended and persisted.
- `tests/test_current_price_flow.py`: adds a deterministic regression test proving `build_top20()` preserves `current_price`; the news fetch is stubbed so the test has no network dependency.
- `.sprint/results/market-TASK-001-codex.md`: records this implementation and its verification.

No production change was needed in `src/screening/top20_ranker.py`: `build_top20()` uses `entry = dict(signal)`, which preserves `current_price`.

No production change was needed in `src/agents/shortlist.py`: `build_shortlist()` constructs each result with `{**s, ...}`, preserving every Top 20 field, including `current_price`. There is no explicit allowlist.

No production change was needed in `dashboard.py`: `_read_json()` returns the decoded JSON object directly, and both `/api/top20` and `/api/shortlist` pass that object directly to `jsonify()`. There is no field reconstruction or allowlist.

## Constraint checks

- Did not modify `quant_engine.py`, `src/screening/signal_engine.py`, `src/screening/top20_ranker.py`, `src/agents/shortlist.py`, or `dashboard.py`.
- Did not modify anything under `static/js/`, `static/css/`, `templates/`, or `position/`.
- Did not change any existing output field or unrelated output shape.
- Did not run `git commit` or `git push`.
- Pre-existing/parallel changes in `.sprint/SPRINT_PLAN.md`, `.sprint/STATUS.md`, `.sprint/council/`, `static/css/dashboard.css`, and `static/js/charts.js` were left untouched.

## Verification

- `python3 -c "import ast; ast.parse(open('run_optimized_scan.py').read())"`: passed.
- `python3 -c "import ast; ast.parse(open('tests/test_current_price_flow.py').read())"`: passed.
- `venv/bin/python -m pytest tests/test_current_price_flow.py -v`: passed, 1 test.
- `venv/bin/python -m pytest tests/test_dashboard_jobs.py -v`: passed, 8 tests.
- Requested command `venv/bin/python -m pytest tests/ -v -k "current_price or top20 or shortlist"`: could not execute selected tests because collection imports the pre-existing `tests/test_email_full.py`, which performs a live five-stock fetch at module import and calls `exit(1)` when the fetch returns no data. In this environment it reported `No data fetched!`; pytest exited with code 3 before applying the `-k` filter. The unrelated test was not modified.
- Equivalent filtered run with the collection blocker excluded, `venv/bin/python -m pytest tests/ -v -k "current_price or top20 or shortlist" --ignore=tests/test_email_full.py`: passed, 1 selected test and 97 deselected.
- `git diff --stat`: the task source diff is `run_optimized_scan.py | 2 ++`; the command also listed concurrent changes in `.sprint/SPRINT_PLAN.md`, `.sprint/STATUS.md`, `static/css/dashboard.css`, and `static/js/charts.js`. Untracked test/report files are listed by `git status --short` but are not included by plain `git diff --stat`.
- `git status --short`: task-owned paths are modified `run_optimized_scan.py` and untracked `tests/test_current_price_flow.py` plus this report. Other listed sprint and frontend files were pre-existing or parallel work.
