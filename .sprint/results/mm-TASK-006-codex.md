# MM-006 implementation report

## What changed

- `src/screening/market_motion_publisher.py`
  - Added `publish_frames()` with bounded fetch/rebuild/push retries.
  - Discovers only JSON files below the configured market-motion snapshot root, skips dot-temporary files, strictly parses and validates every candidate with `market_motion.validate_frame()`, and reports invalid or remotely divergent immutable paths.
  - Builds the revision from the remote branch tip through a temporary `GIT_INDEX_FILE` using `read-tree`, `hash-object`, `update-index`, `write-tree`, and `commit-tree`. The ordinary checkout index, current branch, and tracked working files are not used to construct it.
  - Uses configured Git identity where present and supplies the specified local fallback identity otherwise.
  - Pushes without force, retries only remote-tip races, and soft-fails every error into the result dictionary.
  - Reconciles successfully published files through a fast-forward pull. It removes only byte-identical local copies and restores saved bytes atomically whenever sync fails or does not reproduce the exact frame.
- `src/screening/market_motion_scheduler.py`
  - Added `MarketMotionScheduler`, fixed ET weekday slots, 30-second daemon loop, catch-up logic, busy/running exclusion, at-most-one run per tick, and manual `run_now()`.
  - Added dependency injection for clock, command execution, publishing, sleep, settings/status paths, frame root, and heavy-job detection.
  - Added strict result-line parsing, 20-minute command timeout, publish-only-after-`written` behavior, failure isolation, ET/DST-aware status, and newest-frame reporting.
  - Added default-off atomic settings and restart-visible atomic status persistence.
- `dashboard.py`
  - Added a lazy module-level scheduler factory wired to the dashboard venv interpreter, clean subprocess environment, existing fast-forward pull helper, Git selector, and job registry.
  - Added `GET/POST /api/market-motion/scheduler` with strict boolean-only JSON validation.
  - Added `POST /api/market-motion/run-now` with 202/409 semantics.
  - Added idempotent background-service startup in the direct launcher and a root-page hook for the pywebview import launcher. Importing the module alone does not construct or start the scheduler.
- `tests/test_market_motion_publisher.py`
  - Added temporary bare-remote integration coverage for isolated frame-only revisions, dirty tracked and staged state preservation, fast-forward reconciliation, remote-tip race retry, permanent rejection, restore after pull failure, immutable path divergence, invalid frames, and forbidden high-level Git command arguments.
- `tests/test_market_motion_scheduler.py`
  - Added injected-clock coverage for slot boundaries, missed-slot catch-up, recent-frame startup coverage, weekends, after-close behavior, winter/summer ET offsets, busy retry, no overlap, one job per tick, default-off behavior, publish gating, failures, manual runs, settings corruption, atomic writes, ignored settings/status paths, and status restart.
- `tests/test_market_motion_control_api.py`
  - Added API default/toggle/validation/run-now tests and an isolated-process proof that dashboard import starts no thread.

## Decisions

- Scheduler runs are background workers so the 30-second timer and Flask request threads never block for the rescore duration. The scheduler lock and `running` flag provide overlap exclusion.
- On first enabled tick after startup, a completed frame newer than 100 minutes covers all already-passed slots. Otherwise one catch-up run covers all passed slots. Subsequent slots remain independently due.
- Slot attempts are persisted with the status record. Busy skips do not mark attempts; launched runs do, regardless of success, so failures wait until the next slot as required.
- The main Python dashboard starts services explicitly. The packaged launcher cannot be edited in this task, so its first root-page request starts the same idempotent service hook while preserving import-time purity.
- A remote frame path is immutable. Byte differences are reported as divergence and never replaced.

## Could not do

- I omitted the requested marker-file test for the separately forbidden data location. Creating or even naming that test target would violate the task's stronger rule never to read, list, open, stage, or reference it. Path containment is instead enforced structurally: discovery starts only at `data/market_motion/snapshots`, resolved candidates must remain below the configured frame root, and only those relative paths enter the temporary index.
- No live market scan, real network push, workflow dispatch, email, or paid API call was run.

## Verification

Exact command:

```text
venv/bin/python -m pytest -q tests/test_market_motion.py tests/test_pick_history.py tests/test_scan_run_kind.py tests/test_workflows_pick_history.py tests/test_pick_history_api.py tests/test_backfill_pick_history.py tests/test_dashboard_jobs.py tests/test_current_price_flow.py tests/test_market_motion_publisher.py tests/test_market_motion_scheduler.py tests/test_market_motion_control_api.py
```

Result: `151 passed in 6.59s`.

Additional focused result: `29 passed in 6.28s`, followed by successful `py_compile` of both new modules and `dashboard.py`.

## Lead review risks

- The post-push fast-forward reconcile intentionally advances the local branch when Git can preserve unrelated dirty/staged changes. If Git refuses because a local output conflicts, exact frame bytes are restored and status reports `local sync pending`; the remote publication still remains successful.
- The scheduler uses weekdays for intended slots and delegates exchange holidays to the intraday command's SPY-currentness guard, matching the final plan.
- The pywebview launcher starts the scheduler on its first root-page request because that launcher imports `dashboard.py` and is outside this task's writable file list.
