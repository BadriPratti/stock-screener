# TASK-002 — Persistent Pick History + Consistency Tracking

## Changed files

- `run_optimized_scan.py` — added run-kind parsing and output policy, protected canonical latest files from midday samples, added the report header, and wired the fail-soft daily ledger write.
- `.github/workflows/daily_screening_git_storage.yml` — marked the scan `daily-full`, serialized it with midday, and visibly staged pick history before the existing commit step.
- `.github/workflows/midday_quick_scan.yml` — marked the scan `midday-sample` and added the shared serialization group.
- `.gitignore` — allowed canonical pick-history snapshots while continuing to ignore atomic-write temp files.
- `tests/test_scan_run_kind.py` — covers the policy matrix, parser contract, report latest-file gating/header, and fail-soft ledger behavior.
- `tests/test_workflows_pick_history.py` — covers YAML validity/configuration, workflow commands and step ordering, timeout preservation, absence of midday ledger references, and real `git check-ignore` behavior.
- `.sprint/results/pick-TASK-002-codex.md` — records implementation decisions and verification evidence for this task.

No changes were made to `src/screening/pick_history.py`, `dashboard.py`, the backfill script, snapshot data, or anything under `position/`.

## `resolve_output_policy` truth table

| run_kind | test_mode | write_canonical_latest | record_history |
|---|---:|---:|---:|
| `daily-full` | false | true | true |
| `daily-full` | true | true | false |
| `midday-sample` | false | false | false |
| `midday-sample` | true | false | false |
| `local` | false | true | false |
| `local` | true | true | false |

A `daily-full --test-mode` invocation additionally logs a warning explaining that sample data cannot enter the canonical ledger.

## Ledger placement and fail-soft behavior

The ledger step is in `main()` immediately after `save_report(...)` and before email notification. At that point the Top 20 and optional LLM shortlist have their final values, all permitted canonical JSON outputs and the text report have already been written, and a ledger problem therefore cannot prevent the primary artifacts from being published. Keeping it before email also leaves the existing email/commit path able to proceed after any ledger failure.

`record_pick_history(...)` wraps the entire ledger operation, including `from src.screening import pick_history`, in `try/except Exception`. Failure logs `Pick history ledger write failed: ...`, prints `::warning title=pick-history::ledger write failed: <message>` to stdout, returns `None`, and does not raise or alter the scan exit status.

The ledger receives:

- final `top20` in all recorded runs;
- final `shortlist` only when `--enable-llm-agents` was requested, otherwise `None`;
- scope from `results['total_processed']` when it is an integer, `results['total_analyzed']`, and `completed: true`;
- only non-empty `GITHUB_SHA`, `GITHUB_RUN_ID`, and `GITHUB_WORKFLOW` source values.

## Judgment calls

- Used `results['total_processed']` as `scope.total_universe`, because it is the scan-result value already emitted as `Total Universe` in the report; a missing/non-integer value becomes `None` as requested.
- Kept `save_report` backward-compatible by defaulting `write_latest=True` and `run_kind='local'`.
- Continued computing Top 20/shortlist in memory regardless of publishing policy; the policy gates only canonical latest writes, so the dated report and email behavior remain available.
- Preserved the zero-candidate staleness behavior for every run kind allowed to publish canonical latest outputs.
- Did not run a real scan because the task explicitly excludes network/end-to-end execution in this sandbox.

## Verification

Command:

```text
venv/bin/python -m pytest tests/test_scan_run_kind.py tests/test_workflows_pick_history.py -v
```

Result: `15 passed in 0.69s`.

Command:

```text
venv/bin/python -m pytest tests/test_pick_history.py tests/test_dashboard_jobs.py tests/test_current_price_flow.py -q
```

Result: `33 passed in 0.59s`.

Syntax/YAML checks:

```text
python3 -c "import ast; ast.parse(open('run_optimized_scan.py').read())"
venv/bin/python -c "import yaml; [yaml.safe_load(open(f)) for f in ('.github/workflows/daily_screening_git_storage.yml','.github/workflows/midday_quick_scan.yml')]; print('yaml ok')"
```

Result: AST parse exited 0; YAML check printed `yaml ok`.

Diff checks:

- `git diff --check` exited 0.
- `git diff run_optimized_scan.py` confirms the earlier `current_price` report/signal lines, `_atomic_write_json`, and JSON `result` fields remain present.
- `git diff .github/workflows .gitignore` contains only the requested run-kind commands, shared concurrency blocks, daily history-staging step, and pick-history ignore rules; daily `timeout-minutes: 120` and all unrelated workflow content remain unchanged.
- No commit or push was performed.
