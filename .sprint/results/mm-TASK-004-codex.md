# MM-004 implementation report

## What changed

- `run_intraday_rescore.py`
  - Added the thin CLI for `--cap`, `--workers`, `--delay`, `--root`, `--dry-run`, and `--force`.
  - Constructs the production processor with git-backed fundamentals enabled and emits the required final `MARKET_MOTION_RESULT` JSON line.
  - Returns exit code 0 for written/skipped runs and 1 for failed runs.
- `src/screening/intraday_rescore.py`
  - Added `run_rescore`, the dependency-injected orchestration core.
  - Loads the tracker, builds the deterministic capped roster, records explicit overflow rows, inherits the newest completed `daily_full` regime and fundamentals date, checks the last SPY bar, runs only the tracked roster, and writes one complete intraday frame only after all analysis succeeds.
  - Added `_score_analysis` with the same `score_buy_signal` argument shape used by `run_optimized_scan.main`.
  - Added point conversion for qualified, below-threshold, unscored, missing-analysis, roster-overflow, and regime-gated outcomes.
  - Isolated `batch_progress.pkl` and the ordinary price cache in a temporary directory. The git fundamentals cache is copied into that temporary directory before processing, so existing cached fundamentals are used while refresh writes cannot modify shared scan state.
  - Added stable scheduler result formatting.
- `tests/test_intraday_rescore.py`
  - Added deterministic offline coverage for closed-market skip, force override, no roster, ordering/cap/overflow, all outcome states, scorer call parity, regime gating, zero analyses, mid-run exception, dry-run, single-file persistence, tracker motion/streak behavior, SPY failure, and CLI result/exit-code behavior.

## Decisions

- A dry run reports `status: "skipped"`, `reason: "dry_run"`, and a null `run_id`, because no immutable frame was written.
- Missing analyses count as failures and are represented by `error_code: "not_analyzed"`; capped overflow does not count as requested or failed and is represented as `not_evaluated`.
- The inherited regime gates only would-be buys. When false, the point becomes `not_qualified` with `drop_reason: "regime_gate"` and retains score, RS, price, and the other normalized coordinates.
- The newest completed frame used for regime provenance must be `daily_full`, not a legacy backfill or an intraday frame.

## Could not do

- No real runtime measurement was performed because this task prohibits real market/network scans. The pacing defaults remain 2 workers and a 1.0 second global delay, which bounds a 500-ticker roster to the intended conservative range plus provider/analysis overhead.

## Verification

Exact command:

```text
venv/bin/python -m pytest -q tests/test_market_motion.py tests/test_pick_history.py tests/test_scan_run_kind.py tests/test_workflows_pick_history.py tests/test_pick_history_api.py tests/test_backfill_pick_history.py tests/test_dashboard_jobs.py tests/test_current_price_flow.py tests/test_intraday_rescore.py
```

Result: `132 passed in 1.70s`.

Additional checks:

- `venv/bin/python -m pytest -q tests/test_intraday_rescore.py tests/test_market_motion.py` -> `54 passed in 0.88s`.
- `venv/bin/python run_intraday_rescore.py --help` succeeded and displayed all required options.
- The three added code/test files contain no emoji in added text.

## Lead review risks

- `_score_analysis` deliberately duplicates the small full-scan scoring call shape because importing `run_optimized_scan.py` has unrelated side effects. Add a parity test or shared side-effect-free helper when ownership of the full-scan file permits it.
- The real processor calls `fetch_spy_data` internally from `process_batch_parallel`, so production currently performs a second small SPY fetch after the explicit guard fetch. This follows the fixed processor API without editing it, but a later processor option to reuse already-loaded SPY data would remove the duplicate request.
