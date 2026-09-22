# TASK-004 — Persistent Pick History API + Scan Metadata

## Changes

- Added `PICK_HISTORY_ROOT = PROJECT_ROOT / "data" / "pick_history"` and a read-only `GET /api/pick-history` route in `dashboard.py`.
- The route reads `PICK_HISTORY_ROOT` at request time, loads snapshots through `pick_history.load_snapshots`, and derives the response through `pick_history.compute_history`.
- Added safe query normalization for `list` and `window`, preserving loader warnings and returning HTTP 200 empty shapes for missing ledgers and unexpected computation failures.
- Added `SAMPLE_UNIVERSE_MAX = 150` and `_scan_report_meta(path)`, which reads at most 4096 report characters and extracts `Total Universe` and `Run Kind` without allowing unreadable reports to break `/api/scans`.
- Extended every `/api/scans` item with `total_universe`, `run_kind`, and `is_sample`. The existing `name`, `path`, `date`, glob, and reverse-sort behavior are unchanged.
- Added `tests/test_pick_history_api.py` with Flask contract coverage for empty/populated history, both lists, all requested query fallbacks, corrupt snapshots, strict JSON, Friday-to-Monday streaks, defensive degradation, scan metadata, old reports, missing headers, and an unreadable report-shaped directory.
- Did not modify `src/screening/pick_history.py`, `parse_scan_file`, or `/api/scan`.

## Final response shapes

`GET /api/pick-history` returns the exact `compute_history` object. This is a real empty-ledger response captured through `dashboard.app.test_client()`:

```json
{
  "coverage_gaps": [],
  "denominator": 0,
  "latest_session_date": null,
  "list": "shortlist",
  "run_kind": "daily_full",
  "schema_version": 1,
  "sessions": [],
  "sessions_available": 0,
  "tickers": {},
  "warnings": [],
  "window_requested": 5
}
```

A populated response has the same top-level shape, with per-symbol derived statistics under `tickers`. This `LILA` value was captured from the real ledger through the Flask test client:

```json
{
  "appearance_rate": 1.0,
  "appearances": 5,
  "average_rank": 2.2,
  "average_score": 126.48,
  "best_rank": 1,
  "current_streak": 5,
  "denominator": 5,
  "first_seen": "2026-09-14",
  "history": [
    {"date": "2026-09-14", "rank": 3, "score": 127.1},
    {"date": "2026-09-15", "rank": 3, "score": 125.6},
    {"date": "2026-09-16", "rank": 1, "score": 129.5},
    {"date": "2026-09-17", "rank": 1, "score": 128.4},
    {"date": "2026-09-18", "rank": 3, "score": 121.8}
  ],
  "is_active_today": true,
  "last_seen": "2026-09-18",
  "latest_score": 121.8,
  "longest_streak": 5,
  "score_delta": -6.6,
  "total_appearances": 5
}
```

`GET /api/scans` remains an array. A real item now has this shape:

```json
{
  "name": "optimized_scan_20260918_192654",
  "path": "/Users/badripratti/Desktop/stock-screener/data/daily_scans/optimized_scan_20260918_192654.txt",
  "date": "20260918_192654",
  "total_universe": 100,
  "run_kind": null,
  "is_sample": true
}
```

## Fallback and warning wording

- Unknown list: `Unknown list 'watchlist'; using 'shortlist'.`
- Non-integer window: `Invalid window 'abc'; using default 5.`
- Low clamp: `Window 0 was clamped to 1.`
- High clamp: `Window 999 was clamped to 60.`
- Corrupt files retain the loader's wording, for example: `Skipped 2026-09-17.json: ...`.
- Unexpected failure: `Could not compute pick history: synthetic failure` (also logged with a traceback through Flask's logger).

All of these cases return HTTP 200.

## Judgment calls

- `is_sample` is based only on a successfully parsed universe size (`<= 150`), never on `run_kind`, so old 100-stock reports remain truthfully labeled while old full-universe reports do not become samples.
- Missing or unreadable metadata returns `(None, None)` and therefore `is_sample: false`; a directory whose name matches the report glob exercises this reliably without platform-dependent `chmod` behavior.
- Loader warnings are kept if history computation subsequently fails, followed by query fallback warnings and the defensive failure warning.
- Existing uncommitted `Current Price:` parsing and `result` defaults were preserved. No unrelated dashboard code was reformatted.

## Verification

### Focused suite

```text
$ venv/bin/python -m pytest tests/test_pick_history_api.py -v
collected 11 items
11 passed in 0.63s
```

### Regression suite

```text
$ venv/bin/python -m pytest tests/test_pick_history.py tests/test_dashboard_jobs.py tests/test_current_price_flow.py -q
.................................                                        [100%]
33 passed in 0.62s
```

### Syntax

```text
$ python3 -c "import ast; ast.parse(open('dashboard.py').read())"
# exit 0
```

### Real `/api/scans` Flask-client check

HTTP 200, 17 previously returned `optimized_scan_*.txt` files, still newest first. The older real files predate TASK-002's header addition, so `run_kind` is correctly `None`; universe-based sample detection still distinguishes the midday and full runs.

```text
date              total_universe  run_kind  is_sample
20260918_192654    100             None      True
20260918_170746    3770            None      False
20260917_200021    100             None      True
20260917_173505    3768            None      False
20260916_195151    100             None      True
20260916_172610    3767            None      False
20260915_195953    100             None      True
20260915_173119    3766            None      False
20260914_231020    3766            None      False
20260914_204707    100             None      True
20260909_172815    100             None      True
20260730_225116    100             None      True
20260730_085210    3772            None      False
20260729_223608    100             None      True
20260729_223432    100             None      True
20260729_222415    100             None      True
20260729_221947    100             None      True
```

### Diff safety check

`git diff -- dashboard.py` shows only the pick-history import/constants/route, scan metadata helper and fields, plus the pre-existing `Current Price:` changes. Direct inspection also confirms both existing `"result": None` defaults remain on `/api/top20` and `/api/shortlist`.

No commit or push was run.
