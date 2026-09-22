# MM-002 implementation report

## Changes

- `run_optimized_scan.py`
  - Extended `resolve_output_policy` with the `record_market_motion` gate while preserving the existing canonical-output and pick-history gates.
  - Added `--record-market-motion` to `build_arg_parser`.
  - Added `build_market_motion_points`, which includes every ranked buy signal and one deduplicated outcome for each previously tracked non-buy ticker.
  - Retained scored non-buy results during the existing signal loop so outcome points do not re-run scoring.
  - Added fail-soft `record_market_motion`, including broken-run and missing-SPY guards, SPY-bar session dating, complete scope/regime/source metadata, prior-frame tracking, and atomic writing through the fixed market-motion API.
  - Called market-motion recording after report/pick-history output and before email delivery. Local opt-in runs use `local` provenance; daily full runs use `live` provenance.
- `.github/workflows/daily_screening_git_storage.yml`
  - Added fail-visible market-motion staging before the commit.
  - Added market-motion data to uploaded artifacts.
  - Replaced the push action with the bounded rebase/push helper while preserving timeout, concurrency, condition, and write permission.
- `.github/workflows/midday_quick_scan.yml`
  - Replaced the push action with the same bounded rebase/push helper while preserving concurrency, condition, and write permission.
- `scripts/ci_push_with_rebase.sh`
  - Added a strict-mode, bounded pull-with-rebase and push retry loop with configurable retry delay, rebase abort on pull failure, Actions error annotation, and no force push.
- `tests/test_scan_run_kind.py`
  - Expanded the output-policy truth table and parser coverage for the new flag.
- `tests/test_market_motion_scan.py`
  - Added offline coverage for 120 buys, deduplication, all required tracked dropout states, valid zero-buy recording, broken/missing-data skips, fail-soft writing, and local opt-in isolation from pick history.
- `tests/test_ci_push_with_rebase.py`
  - Added real temporary bare-repository and depth-one clone tests for clean push, non-conflicting remote advance/rebase, permanent rejection, bounded failure, and absence of force push.
- `tests/test_workflows_pick_history.py`
  - Added assertions for market-motion staging/artifacts and both workflows' rebase helper, YAML parsing, concurrency, conditions, and permissions.

## Decisions

- Used `git pull --rebase --no-autostash` because Git rejects the spelling `--autostash=false` with `option 'autostash' takes no value`. `--no-autostash` is the supported equivalent and was verified in depth-one clone tests.
- Sorted tracked-only outcomes by normalized ticker for deterministic frames while leaving qualified buys in their existing score-descending rank order.
- Treated a previously tracked ticker absent from current analyses as `error` with `error_code: not_analyzed`, matching the fixed `outcome_point` contract.
- Logged corrupt prior-frame warnings but continued with valid loaded frames; any actual frame construction or write failure remains fail-soft and cannot block email.

## Could not do

- Nothing required by MM-002 remains incomplete.
- No real scan, network market call, workflow dispatch, email, external API, commit, push, or index mutation was performed.

## Verification

Exact command:

```text
venv/bin/python -m pytest -q tests/test_market_motion.py tests/test_pick_history.py tests/test_scan_run_kind.py tests/test_workflows_pick_history.py tests/test_pick_history_api.py tests/test_backfill_pick_history.py tests/test_dashboard_jobs.py tests/test_current_price_flow.py tests/test_market_motion_scan.py tests/test_ci_push_with_rebase.py
```

Result: `128 passed in 3.52s`.

Additional checks: focused MM-002 suite `28 passed in 2.71s`; Python compilation, `bash -n`, executable-bit check, and `git diff --check` all passed.

## Lead review risk

- Please note the intentional `--no-autostash` spelling described above. It is semantically the requested behavior and is required for compatibility with the Git binary used by the tests and GitHub-hosted runners.
