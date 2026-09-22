Here is the independent code review for **TASK-002** and the persistent pick history workflow wiring.

---

### Prioritized Findings Summary

| Severity | ID | File & Line | Summary |
|---|---|---|---|
| **SHOULD-FIX** | **SEC-01** | [daily_screening_git_storage.yml#L21-L23](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml#L21-L23), [midday_quick_scan.yml#L12-L14](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/midday_quick_scan.yml#L12-L14) | Shared concurrency group with pending queue depth = 1 can silently drop/cancel runs |
| **SHOULD-FIX** | **SEC-02** | [run_optimized_scan.py#L685](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L685) | `results['total_analyzed']` raw key lookup outside `record_pick_history()` fail-soft wrapper |
| **SHOULD-FIX** | **SEC-03** | [daily_screening_git_storage.yml#L148-L173](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml#L148-L173) | Split-step staging: `git add data/pick_history/` isolated from commit step |
| **NOTE** | **SEC-04** | [src/screening/pick_history.py#L217-L249](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L217-L249) | Same-day manual rerun can clobber a valid morning `success` snapshot with `no_candidates` |
| **NOTE** | **SEC-05** | [daily_screening_git_storage.yml#L192-L202](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml#L192-L202) | `data/pick_history/` omitted from `upload-artifact` retention step |
| **NOTE** | **SEC-06** | [src/screening/pick_history.py#L192-L194](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L192-L194) | Unhandled duplicate ticker in upstream signals causes fail-soft ledger drop |

---

### Detailed Findings

#### [SHOULD-FIX] SEC-01: Shared Concurrency Group Silently Cancels Pending Runs
- **File**: [.github/workflows/daily_screening_git_storage.yml#L21-L23](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml#L21-L23), [.github/workflows/midday_quick_scan.yml#L12-L14](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/midday_quick_scan.yml#L12-L14)
- **Concrete Scenario**:
  GitHub Actions concurrency groups with `cancel-in-progress: false` protect the *currently running* job, but **GitHub Actions maintains a pending queue depth of exactly 1**. When Run 1 is running and Run 2 is pending, any newly arriving Run 3 in that concurrency group immediately cancels Run 2.
  - Daily scan is scheduled for 12:00 UTC, but platform dispatch delay has consistently pushed start times to 16:11–17:39 UTC (taking ~64–96 minutes).
  - Midday quick scan cron triggers at 17:00 UTC.
  - On almost every weekday, Midday will queue while Daily is actively running (or vice-versa). While one is pending in the queue, if anyone manually triggers either workflow via `workflow_dispatch` (e.g. testing midday or re-running daily), the pending workflow is **silently canceled without running**. If Daily is the pending run, the entire day's canonical screening run and email are lost.
- **Recommended Action**: Desynchronize the schedules so their real execution windows never overlap (e.g., schedule Daily cron at 07:00 UTC so that even with a 4–5 hour platform delay, it finishes before 13:00 UTC / 9:00 AM ET, hours before Midday at 17:00 UTC).

#### [SHOULD-FIX] SEC-02: Direct Key Indexing on Publishing Path Outside Fail-Soft Wrapper
- **File**: [run_optimized_scan.py#L679-L688](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L679-L688)
- **Concrete Scenario**:
  While [`record_pick_history()`](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L77-L92) has an internal `try...except Exception`, the dictionary arguments passed to it are evaluated in [`main()`](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L685) *before* the function call:
  ```python
  total_universe = results.get('total_processed')  # Safe
  record_pick_history(
      shortlist=shortlist if args.enable_llm_agents else None,
      top20=top20,
      scope={
          'total_universe': total_universe if isinstance(total_universe, int) else None,
          'analyzed': results['total_analyzed'],  # <-- Raw key indexing outside try/except
          'completed': True,
      },
      source=source,
  )
  ```
  Notice the asymmetry: `total_processed` uses `.get()`, but `total_analyzed` uses direct dictionary lookup. If `results` ever lacks `'total_analyzed'` (e.g. mock/test harness, future refactor of `OptimizedBatchProcessor`, or edge-case processing failure), a `KeyError` is raised in `main()`. This escapes directly to `except Exception as e: sys.exit(1)` at [line 722](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L722), aborting the process **before** sending the email notification ([line 693](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L693)) and before git commit.
- **Recommended Action**: Use `results.get('total_analyzed', 0)` or move the scope/source preparation inside `record_pick_history()`.

#### [SHOULD-FIX] SEC-03: Staging Step Isolation Creates Uncommitted Ledger Risk
- **File**: [.github/workflows/daily_screening_git_storage.yml#L148-L173](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml#L148-L173)
- **Concrete Scenario**:
  Staging pick history was split into its own step with `continue-on-error: true`:
  ```yaml
  - name: Stage pick history
    continue-on-error: true
    run: |
      if [ -d data/pick_history ]; then git add data/pick_history/; fi
  ```
  However, in the subsequent step `Commit updated fundamental cache`, `data/pick_history/` is **omitted** from the `git add` list (which only stages `fundamentals_cache`, `fundamentals_audit`, `catalyst_sentiment`, `congress_trades`, and `daily_scans`).
  If step "Stage pick history" fails, is skipped, or is altered by future edits, `continue-on-error` masks the issue. The commit step then stages and commits all *other* artifacts and pushes cleanly. CI reports green, but the ledger file is silently left behind in runner storage.
- **Recommended Action**: Move `git add data/pick_history/ 2>/dev/null || true` directly inside the `Commit updated fundamental cache` step alongside `data/daily_scans/`.

#### [NOTE] SEC-04: Same-Day Rerun Can Clobber Valid Morning Streaks
- **File**: [src/screening/pick_history.py#L207-L249](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L207-L249), [run_optimized_scan.py#L70-L71](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L70-L71)
- **Concrete Scenario**:
  The morning scheduled run executes normally, finding valid picks and recording `2026-09-20.json` with `result: "success"`. Later in the day, an operator triggers a manual `workflow_dispatch` (e.g. testing `force_full_refresh` after market close or during network throttling). If that afternoon run produces 0 buy signals, it produces a snapshot with `result: "no_candidates"` and empty lists. Under "latest writer wins", the atomic overwrite clobbers the morning snapshot. In [`compute_history()`](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L416), a `no_candidates` session resets `current_streak` to 0 for **all** tickers.
- **Recommended Action**: In [`write_snapshot()`](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L217), if an existing snapshot on the same date already has `result: "success"` and non-empty candidate lists, do not overwrite it with `result: "no_candidates"` unless an explicit override flag is passed.

#### [NOTE] SEC-05: Pick History Snapshots Missing from Workflow Artifacts
- **File**: [.github/workflows/daily_screening_git_storage.yml#L192-L202](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml#L192-L202)
- **Concrete Scenario**:
  `Upload screening results` (`if: always()`) archives `data/daily_scans/` and `data/logs/`. If the `Push changes` step fails (e.g. non-fast-forward git push conflict caused by a concurrent developer commit), the scan report and latest JSON files are preserved in the GitHub Actions 90-day artifact archive, but `data/pick_history/` is not. The day's ledger snapshot is permanently lost and cannot be recovered from the run artifacts.
- **Recommended Action**: Add `data/pick_history/` to the `path` list in `Upload screening results`.

#### [NOTE] SEC-06: Strict Duplicate Ticker Validation in Fail-Soft Loop
- **File**: [src/screening/pick_history.py#L192-L194](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L192-L194)
- **Concrete Scenario**:
  [`validate_snapshot()`](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L192) raises `ValueError(f"duplicate ticker {ticker!r} in {list_name}")`. If upstream signal generators ever yield duplicate tickers (e.g. dual share classes or unsorted batch merges), [`_slim_rows()`](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L67-L94) does not deduplicate them. The validation error is caught by `record_pick_history()`, emitting a warning annotation and returning `None`. CI finishes successfully with exit code 0, but the day's ledger snapshot is silently dropped.
- **Recommended Action**: Add deduplication inside `_slim_rows()` using a `seen` set before computing consecutive ranks.

---

### Direct Answers to Specific Review Questions

#### 1. Concurrency Semantics and Silent Drop/Cancellation
- **Semantics**: In GitHub Actions, concurrency groups with `cancel-in-progress: false` do not queue multiple pending runs. The concurrency group has 1 active slot and at most 1 pending slot. If Run 1 is running and Run 2 is pending, arrival of Run 3 immediately **cancels Run 2**.
- **Realistic Scenario**: With Daily delayed to ~16:30 UTC (running ~96 min) and Midday scheduled for 17:00 UTC, one is almost always pending while the other runs. If a user manually dispatches a workflow during this window:
  - If Midday is running and Daily is pending: **Daily is canceled** (the entire full-universe scan is dropped for that day).
  - If Daily is running and Midday is pending: Midday is canceled.
- **Rating**: Likelihood is **Low-Medium** on hands-off days, but **High** during active development or testing. Severity is **High** (loss of daily scan and email).
- **Design Change**: Yes. Shift Daily cron earlier (e.g., `0 7 * * 1-5` UTC) so its delayed window finishes before market open and well before Midday at 17:00 UTC.

#### 2. Interaction of "Stage pick history" with Commit and Push Steps
- **Normal Day with Changes**: `Stage pick history` stages the new snapshot; `git diff --staged --quiet` detects changes and sets `has_changes=true`; files are committed and pushed.
- **Days with No Ledger Change**: If no new snapshot is written (or content is byte-identical), `git diff --staged --quiet` relies on changes in `data/daily_scans/` (e.g. the dated scan report) and fundamental cache. If truly no files changed across all staged paths, `has_changes=false` and commit/push are cleanly skipped.
- **When Ledger Write Fails**: `record_pick_history()` catches the exception and returns `None`. No file is created in `data/pick_history/`. `Stage pick history` stages nothing. The commit step proceeds to stage and commit `daily_scans` and fundamental cache. Primary publishing continues uninterrupted.
- **Failure Risk**: Because `data/pick_history/` is not listed in the commit step's own `git add` list, any failure in the staging step causes the commit step to silently commit only the other directories.

#### 3. First Run After Merge (Directory Existence)
- **If `data/pick_history/` exists**: Normal checkout, snapshot written to `data/pick_history/snapshots/daily_full/`, staged, committed, and pushed.
- **If `data/pick_history/` does NOT exist**: In [`pick_history.write_snapshot()`](file:///Users/badripratti/Desktop/stock-screener/src/screening/pick_history.py#L224), `final_path.parent.mkdir(parents=True, exist_ok=True)` automatically creates `data/pick_history/snapshots/daily_full/` on disk before writing. When the workflow reaches `if [ -d data/pick_history ]; then git add data/pick_history/; fi`, the condition evaluates to true and git stages the new directory and files. If the scan failed before writing, the condition evaluates to false and skips staging without error.

#### 4. Variable Construction and Exception Escapes in `main()`
- **Exception Escapes**: As highlighted in **SEC-02**, line 685 calls `'analyzed': results['total_analyzed']` with raw dictionary lookup outside the `try...except` block in `record_pick_history()`. A `KeyError` here would bypass the fail-soft protection, trigger `sys.exit(1)`, and abort before sending emails or committing.
- **Definition of `shortlist` and `top20`**:
  - `top20` is explicitly initialized as `top20 = []` at [line 575](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L575).
  - `shortlist` is explicitly initialized as `shortlist = []` at [line 607](file:///Users/badripratti/Desktop/stock-screener/run_optimized_scan.py#L607).
  - Both are unconditionally bound before branching. When there are zero buy signals: `top20` remains `[]`, `shortlist` remains `[]`, and `shortlist if args.enable_llm_agents else None` safely evaluates to `[]` (or `None` if agents were disabled). Validation passes with `result: "no_candidates"`.

#### 5. Positional/Legacy Arguments to `run_optimized_scan.py`
- `build_arg_parser()` has never accepted positional arguments; all options are flag-based (`--conservative`, `--test-mode`, `--workers`, etc.).
- In [dashboard.py#L456](file:///Users/badripratti/Desktop/stock-screener/dashboard.py#L456) and [dashboard.py#L868](file:///Users/badripratti/Desktop/stock-screener/dashboard.py#L868), local scans are launched via:
  ```python
  cmd = [python, str(PROJECT_ROOT / "run_optimized_scan.py")]
  ```
  Omission of `--run-kind` cleanly defaults to `--run-kind local`. Under policy `local`, `resolve_output_policy()` returns `write_canonical_latest=True, record_history=False`. This matches existing local GUI behavior and prevents local sync wipes from touching the canonical ledger.

#### 6. Same-Day Rerun Replacing Snapshot ("Latest Writer Wins")
- Under normal circumstances, overwriting the same date key (`YYYY-MM-DD.json`) is the intended idempotent design (avoiding duplicate sessions and allowing re-runs to fix interrupted runs).
- However, as documented in **SEC-04**, an afternoon manual test run that produces `no_candidates` will overwrite a good morning snapshot, resetting all active streaks.
- **Recommended Mitigation**: Prevent overwriting an existing `result: "success"` snapshot with a `result: "no_candidates"` snapshot on the same date unless forced.

#### 7. Silent Ledger Loss and Primary Publish Failures
- **Silent Ledger Loss**: If `record_scan()` fails validation (e.g. duplicate tickers or disk write error), `record_pick_history()` logs an error, prints a warning annotation, and returns `None`. CI finishes with exit code 0 and reports green, while the ledger is silently skipped.
- **Primary Publish Failure**: If a commit is pushed to `main` while the 96-minute daily scan is running, `Push changes` ([line 187](file:///Users/badripratti/Desktop/stock-screener/.github/workflows/daily_screening_git_storage.yml#L187)) will fail with a non-fast-forward push rejection. Because `data/pick_history/` is also omitted from `Upload screening results`, the day's ledger snapshot is permanently lost from the runner.
