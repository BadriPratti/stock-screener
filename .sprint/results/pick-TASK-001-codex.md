# TASK-001 Result: Persistent Pick-History Core

## Outcome

Implemented the dependency-free version-one pick-history ledger in `src/screening/pick_history.py` and its focused test suite in `tests/test_pick_history.py`. The module creates slim per-session snapshots, validates and atomically replaces them, skips bad ledger files with visible warnings, and derives deterministic windowed and full-ledger consistency statistics.

No existing project file was modified for this task. The only paths created are:

- `src/screening/pick_history.py`
- `tests/test_pick_history.py`
- `.sprint/results/pick-TASK-001-codex.md`

## Public API implemented

Constants:

```python
SCHEMA_VERSION = 1
SCORING_VERSION = "v1"
RUN_KIND_DAILY_FULL = "daily_full"
DEFAULT_LEDGER_ROOT = Path(__file__).resolve().parents[2] / "data" / "pick_history"
LIST_NAMES = ("shortlist", "top20")
```

Functions (annotations shown as implemented):

```python
session_date_et(dt: datetime | str | None = None) -> str

build_snapshot(
    *,
    session_date: str,
    generated_at: datetime | str,
    provenance: str,
    scope: dict[str, Any],
    shortlist: list[dict[str, Any]] | None,
    top20: list[dict[str, Any]] | None,
    run_kind: str = RUN_KIND_DAILY_FULL,
    source: dict[str, Any] | None = None,
) -> dict[str, Any]

validate_snapshot(snapshot: Any) -> None

snapshot_path(
    session_date: str,
    run_kind: str = RUN_KIND_DAILY_FULL,
    root: str | os.PathLike[str] | None = None,
) -> Path

write_snapshot(
    snapshot: dict[str, Any],
    root: str | os.PathLike[str] | None = None,
) -> Path

record_scan(
    *,
    shortlist: list[dict[str, Any]] | None,
    top20: list[dict[str, Any]] | None,
    scope: dict[str, Any],
    generated_at: datetime | str | None = None,
    source: dict[str, Any] | None = None,
    root: str | os.PathLike[str] | None = None,
    provenance: str = "live",
) -> Path

load_snapshots(
    root: str | os.PathLike[str] | None = None,
    run_kind: str = RUN_KIND_DAILY_FULL,
) -> tuple[list[dict[str, Any]], list[str]]

compute_history(
    snapshots: list[dict[str, Any]],
    list_name: str = "shortlist",
    window: int = 5,
    warnings: list[str] | None = None,
    run_kind: str = RUN_KIND_DAILY_FULL,
) -> dict[str, Any]
```

## Judgment calls

- Coverage gaps are calculated from all recorded snapshots, not only sessions where the requested list is non-null. A snapshot where one list was not produced is still a recorded scan, so treating that date as a missing scan would create a false coverage warning. The null list remains excluded from that list's denominator and streak observations.
- Raw scanner NaN and infinity values are converted to `None` while `build_snapshot` creates slim rows. This permits the required strict-JSON output. `validate_snapshot` still rejects a non-finite score placed directly into an already-built snapshot, satisfying the validation contract rather than silently repairing arbitrary external snapshots.
- `latest_score` and `score_delta` refer to the latest ticker appearance in the selected window, even when the ticker is absent from the latest session. This follows the contract's phrase "latest window appearance"; current membership is represented separately by `is_active_today` and `current_streak`.
- Coverage gaps count weekdays strictly between consecutive recorded dates. Thus Friday-to-Monday has zero missing weekdays, while Thursday-to-Monday reports Friday as one missing weekday. Gaps remain informational and never alter streaks.
- Snapshot validation requires both list keys to be present explicitly, even though either value may be `None`. This prevents a malformed or older shape from being silently interpreted as a deliberately unproduced list.

## Contract risks noted

- Same-date retries intentionally use latest-writer-wins replacement. Atomic filesystem replacement prevents partial files but does not resolve semantic races between two writers; TASK-002's shared workflow concurrency is still important.
- `run_kind` validation currently recognizes only `daily_full`, as specified by the sole public run-kind constant. Adding another ledger series requires explicitly extending the accepted run-kind set.
- `zoneinfo.ZoneInfo("America/New_York")` depends on timezone data being present in the deployment environment, matching the sprint plan's existing risk note.
- Score comparison depends on a session-wide `scoring_version`. If only one list's scoring formula changes later, the version must still be bumped so incompatible deltas are suppressed.

## Tests implemented

The 23 focused pytest cases cover:

- Public constants and project-root-derived default path.
- ET/UTC date boundaries, including naive datetimes interpreted as UTC.
- Exact snapshot shape, UTC timestamp conversion, slim rows, ticker normalization, and blank-ticker removal.
- Friday-to-Monday streak continuity.
- Zero-candidate results and streak breaks.
- Null-list exclusion versus empty-list observation semantics.
- Missing-weekday coverage gaps without streak breaks.
- Same-date replacement, one-file idempotency, and byte-identical rewrites.
- Preservation of an existing file and temporary-file cleanup after validation failure.
- Windows larger and smaller than available history.
- Window-only appearances/ranks/scores with full-ledger first-seen and streak statistics.
- Corrupt JSON, invalid schema, and filename/date mismatch skipping with warnings.
- Missing ledger directory behavior.
- Duplicate ticker, non-consecutive rank, both-lists-null, and direct non-finite score rejection.
- Scanner NaN sanitization and strict JSON parsing.
- Score-delta suppression across scoring versions.
- Hand-computed shortlist and Top 20 rank/score fallback math.
- The Sep 14-18 LILA 5/5 and LTC final-3 fixture.
- JSON serializability, float rounding, warning order, determinism, empty history, window flooring, unknown list rejection, path construction, and `record_scan` integration.

## Verification

```text
$ venv/bin/python -m pytest tests/test_pick_history.py -v
collected 23 items
23 passed in 0.56s

$ venv/bin/python -m pytest tests/test_dashboard_jobs.py tests/test_current_price_flow.py -q
..........                                                               [100%]
10 passed in 0.61s

$ python3 -c "import ast; ast.parse(open('src/screening/pick_history.py').read())"
(exit 0)

$ venv/bin/python -c "import runpy; ns=runpy.run_path('src/screening/pick_history.py'); assert ns['SCHEMA_VERSION'] == 1; print('standalone module import check: PASS')"
standalone module import check: PASS
```

The running import check executes the module directly, avoiding `src.screening.__init__`, which independently imports the repository's pre-existing scientific stack. Inspection of the module's import statements confirms only Python standard-library modules and `src.utils.json_safe` are imported.

The final `git status --porcelain` audit showed the three paths above as the only task-created paths. All other reported modifications and untracked paths matched the pre-task working-tree inventory and were left untouched.
