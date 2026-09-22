# SC-001: Backtest experiment manifest and frozen-input runner

## What was built

- Added `src/backtesting/frozen_inputs.py`, which defines manifest schema version 1, strict schema validation,
  capture/load helpers, SHA-256 verification, path-traversal protection, row-count checks, and clear
  `ManifestError` failures.
- Added opt-in capture and replay modes to `scripts/walk_forward_backtest.py`.
- Capture freezes the exact sampled universe, the full SPY frame, every successfully returned ticker frame
  (including frames rejected as too short), fetch failures, the complete date grid, the random seed, all
  backtest CLI parameters, the repository commit when available, and a UTC creation timestamp.
- Replay loads its parameters and date grid from the manifest, verifies every frozen file before analysis,
  and performs no universe or yfinance history fetches. It never falls back to live data.
- Manifest-backed results use the manifest creation timestamp, so repeated replay JSON is deterministic rather
  than changing because of `datetime.now()`.
- Existing no-flag behavior remains live-fetch/no-capture and retains the original defaults.
- Capture/replay explicitly reject `--audit-fundamentals`, because that option makes external SEC/Claude calls
  whose inputs are not frozen by this task. Allowing it would falsely claim an offline deterministic replay.
- `component_correlation_analysis.py` was not wired in this task. Its frozen-input support was a stretch goal;
  the complete walk-forward acceptance path was prioritized without restructuring the second working tool.

No live scoring weights, thresholds, scanner behavior, or dashboard behavior were changed.

## Storage decision

The store defaults to `data/backtest_manifests/<manifest_id>/`, with `manifest.json`, `spy.csv`, and numbered
files under `histories/`. CSV was chosen because `pyarrow` is not installed in the project virtual environment
or declared in `requirements.txt`. Frames are written with ISO timestamps and 17 significant digits for floats,
which preserves IEEE-754 float round trips without adding a dependency. Every CSV has a SHA-256, byte count,
and row count in the manifest. Existing manifest directories are never overwritten.

## CLI usage

Capture with an automatically generated id:

```bash
venv/bin/python scripts/walk_forward_backtest.py --capture-manifest
```

Capture with a stable id and any normal backtest parameters:

```bash
venv/bin/python scripts/walk_forward_backtest.py \
  --universe-size 250 --lookback-months 9 --step-days 14 \
  --top-n 10 --max-hold-days 60 --seed 42 \
  --capture-manifest baseline-2026-09-22
```

Replay by id. Frozen parameters and the frozen date grid are used; current CLI defaults do not replace them:

```bash
venv/bin/python scripts/walk_forward_backtest.py --replay-manifest baseline-2026-09-22
```

An explicit manifest directory or `manifest.json` path can also be supplied for replay. An explicit directory
can be supplied for capture.

With neither flag, the original live-fetch behavior remains:

```bash
venv/bin/python scripts/walk_forward_backtest.py
```

## Tests

Focused acceptance suite:

```text
venv/bin/python -m pytest -q tests/test_frozen_backtest_manifest.py
6 passed in 1.23s
```

The tests cover schema validation, inconsistent seed rejection, one-byte tamper/hash rejection,
capture-followed-by-two byte-identical replay results, non-empty trades/metrics/correlations, zero replay network
calls, missing-manifest failure without fallback, frozen frame loading, and unchanged default fetch behavior.

Broader repository suite excluding an existing collection-breaking integration module:

```text
venv/bin/python -m pytest -q tests --ignore=tests/test_email_full.py
305 passed, 1 failed in 23.41s
```

The remaining failure is pre-existing and outside this task: `tests/test_fetcher.py::TestFetchPriceHistory::
test_fetch_price_history_success` expects a `Date` column, while its mocked returned DataFrame has `Date` only
as its index and the production fetcher returns that frame unchanged.

The unfiltered repository command could not collect tests:

```text
venv/bin/python -m pytest -q
INTERNALERROR during collection: tests/test_email_full.py performs a live fetch and raises SystemExit(1)
when no data is fetched; no tests ran.
```
