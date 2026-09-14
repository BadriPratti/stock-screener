# TASK-002 — Atomic shortlist data writes and explicit result state

## Implementation

- Added `_atomic_write_json(path, data)` in `run_optimized_scan.py`. It serializes the sanitized payload to `<final suffix>.tmp` in the final file's directory, flushes and `fsync`s the temporary file, then uses `os.replace()` for an atomic same-filesystem swap. Opening the fixed temporary path with mode `w` overwrites a stale temporary file from an interrupted earlier run.
- Replaced the three direct writes for `top20_latest.json` and `shortlist_latest.json` with the helper. Existing payload fields and their meanings are unchanged.
- Added `result` to the persisted payloads:
  - `success` when `top20` contains candidates, including the non-empty shortlist branch.
  - `no_candidates` when the completed scan produced an empty `top20`, including the `elif args.enable_llm_agents` shortlist-clearing branch.
- Did not add `agents_unavailable`. The agent functions do expose missing-key and call-failure reasons, but `build_shortlist()` still deterministically returns real candidates by backfilling from a non-empty `top20`. The requested result state describes candidate availability, so labeling that payload unavailable would conflate enrichment status with the presence of valid scan candidates.
- Added `result: None` to the `/api/top20` and `/api/shortlist` missing/unreadable-file fallback payloads in `dashboard.py`.

## Constraint checks

- No existing JSON field was removed, renamed, or given new semantics.
- No buy-signal, Top 20, shortlist, or agent-call logic was changed.
- No files under `static/`, `templates/`, `.github/workflows/`, or `position/` were touched by this task.
- Task code changes are limited to `run_optimized_scan.py` and `dashboard.py`; the requested report is this file. The throwaway test was placed at `/tmp/task002_atomic_write_test.py`, outside the repository.
- The worktree already contained unrelated modified and untracked files before this task, including workflow, sprint, frontend, and test changes. Final `git status --short` still reports those pre-existing changes, so repository-wide status is not clean; the scoped diff confirms this task's code footprint is the two requested Python files.
- No commit or push was run.

## Verification

Syntax checks:

```text
python3 -c "import ast; ast.parse(open('run_optimized_scan.py').read())"  PASS
python3 -c "import ast; ast.parse(open('dashboard.py').read())"           PASS
```

Standalone helper test:

```text
PYTHONPATH=. venv/bin/python /tmp/task002_atomic_write_test.py
atomic JSON fixture checks passed
```

The fixture exercised non-empty and empty Top 20 payloads plus non-empty and empty shortlist payloads. For each case it pre-created stale `.json.tmp` content, parsed the final file with `json.loads`, asserted the expected `result`, and asserted that no `.tmp` file remained after success.

Dashboard sanity suite:

```text
venv/bin/python -m pytest tests/test_dashboard_jobs.py -v
collected 8 items
8 passed in 0.10s
```

Diff/status review:

```text
git diff --stat
10 files changed, 332 insertions(+), 1196 deletions(-)
```

That repository-wide stat includes changes present before TASK-002. `git diff -- run_optimized_scan.py dashboard.py` shows only the atomic helper/call-site updates, added result fields, and route defaults described above. `git status --short` confirms both target Python files are modified and this report is untracked, alongside the pre-existing unrelated worktree changes.
