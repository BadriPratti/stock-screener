# Sprint: Persistent Pick History + Consistency Tracking

> Sibling plan awaiting approval: `.sprint/SPRINT_PLAN_CHART_MODAL.md` (full-screen chart modal).
> The two sprints edit some of the same frontend files (see "Sequencing" below) — do not build them concurrently.

## Request (user's own words)

"Are we keeping track of the stocks we said before? I feel like we are re-doing our calculation fresh every time — we need a way to keep track of the stocks we said so that I know what stocks have been consistently well over time."

## Engineering Council process

HARD-classified (new data subsystem + CI workflow changes + UI). Full council: Claude, Codex and Antigravity investigated independently.
Transcripts: `.sprint/council/codex-pick-history.md`, `.sprint/council/antigravity-pick-history.md`.
Historic snapshots both agents worked from (extracted from git): `.sprint/council/pick-history-data/` (planning artifact only — the real backfill script must read git directly, not this folder).

**Antigravity note:** its first run hit the headless permission wall again (it was told to use `git log`/`git show`; the allowlist doesn't match git-with-arguments) and its second launch exited silently. Fixed by pre-extracting the git snapshots to plain files, restricting it to `cat/grep/rg/find/ls`, and launching with `--log-file` so a failure is diagnosable. It then produced a full independent analysis. Recipe now proven twice: `--mode accept-edits`, `--print-timeout 25m`, no git/python/node in the prompt, pre-extract any data it needs.

## Diagnosis (verified against the repo, not just reported by the agents)

The app is **memoryless**: every run overwrites `shortlist_latest.json` / `top20_latest.json`. Only accidental git history exists. Real automated, comparable history starts **2026-09-14** (5 daily full-universe runs: commits `25b3fc3f`, `40b6d251`, `3b798ef7`, `9d9fe4ee`, `919bf881`).

### Existing bugs found while planning (they directly corrupt any history, so they are prerequisites, not extras)

1. **Midday test scan overwrites the canonical Top 20 every afternoon.** `midday_quick_scan.yml` runs `run_optimized_scan.py --test-mode` on a **random 100-stock sample** (~50 analyzed, 8–14 buys) and writes the same `top20_latest.json` as the daily full-universe run (~3,770 stocks, 360–480 buys). Verified: today's `top20_latest.json` has 11 entries from the midday run while `shortlist_latest.json` is from the morning full scan — they are out of sync.
2. **Market view's default scan is that midday sample.** `get_scan_files()` sorts `optimized_scan_*.txt` newest-first and the view loads `scans[0]`; the midday report is always newest. This is why Market showed "Buy (10) / Sell (9)" instead of a few hundred.
3. **Momentum "Day N" is not a consistency measure** (deliberately not used here, and not fixed in this sprint): `scripts/fetch_momentum_status.py` breaks a streak on any calendar-day gap >1 (my FIX-008 earlier in this session over-corrected — a weekend resets it), and `data/momentum_status/history.json` is **gitignored / local-only**, so "Day N" only reflects days the local app happened to check. See "Out of scope".

### Build trap (verified)

`.gitignore` has `data/*` with an explicit whitelist. A new `data/pick_history/` would be **silently ignored**, and both workflows use `git add … 2>/dev/null || true`, so CI would report success and never persist the ledger. Needs a `.gitignore` negation **and** a test that fails if the ledger path is ignored.

## Converged decisions (both agents agreed independently)

- **Event log is the source of truth; aggregates are derived on read.** No mutable per-ticker counters (they drift and can't be audited/corrected). JSON files — not SQLite (binary diffs/merge conflicts), not JSONL, not mining `git log` at runtime (CI uses `fetch-depth: 1`; fragile in the packaged app).
- **A "day" = a recorded scan session, not a calendar day.** Streaks run over consecutive *recorded sessions*, so Friday→Monday is consecutive. Explicitly do **not** copy the momentum script's calendar-gap logic.
- **Only the full-universe daily scan enters the ledger.** Midday/test/local runs never do.
- **Zero-candidate day = a recorded session with empty lists** (breaks every active streak). **Failed/missing run = no session** (a visible coverage gap, never a false "disappeared").
- Session date key = **America/New_York market date**; re-running the same date **replaces** that session (idempotent), never double counts.
- **Backfill exactly the 5 automated daily runs above**, with an explicit accepted-commit manifest; mark `provenance: "backfill"`. Exclude: Sep 9 (manual 100-stock test), Sep 12/13 manual local commit `c741acb0`, Jul 29–30 reports, and every midday commit.
- Read-only API following the repo's "empty shape, not error" contract; UI = Shortlist badges + a Consistency column in the shared Top 20 table.
- Use the real `ticker` field (in-memory lists), never the text-report regex. Pass everything through `sanitize_nan`.
- **Local runs must not write the canonical ledger** — `dashboard.py`'s Sync runs `git checkout -- data/` on conflict and would wipe it.

## Disagreements — resolved

| Topic | Codex | Antigravity | Decision |
|---|---|---|---|
| Storage layout | One file per session under `data/pick_history/snapshots/daily_full/DATE.json` | One `data/daily_scans/pick_history.json` with a `scans[]` array, read-modify-write under `fcntl` | **Per-session files (Codex).** Idempotency = overwrite one file; no read-modify-write of a growing shared file; a bad write loses one day, not the history; tiny diffs; trivially byte-identical backfill. `fcntl` only protects processes on one machine, not CI runners. Cost = the `.gitignore` negation above. |
| What to track | shortlist + top20 + buy_signals | shortlist + top20 only | **shortlist + top20.** These are "the stocks we said" (emailed/shown). Buy signals are 350–650 rows/day (~25× the data), the report only keeps the top 50 so they can't be backfilled with scores, and they dilute the meaning. `lists` is a dict so it can be added later without migration. |
| Isolating midday | `--run-kind` flag; only `daily-full` writes canonical latest files | Just drop `git add data/daily_scans/` from the midday workflow | **`--run-kind` (Codex), default `local` so local behaviour is unchanged.** Only `midday-sample` is barred from overwriting canonical files; only `daily-full` records the ledger. Removing the `git add` alone would leave the scanner unaware of its scope and wouldn't fix the Market default-scan problem. |
| Ledger write fails | Fail the whole workflow | (silent on this) | **Fail soft.** The shortlist/Top 20 publish is the primary product; an auxiliary ledger bug must not block it (lesson from this week's timeout regression). Log loudly + emit a `::warning::`; the API reports a coverage gap; the repair/backfill script can rebuild the day idempotently. |
| Concurrency | Shared `concurrency` group in **both** workflows; no auto-rebase | Group in daily only **plus** `git pull --rebase` before push | **(SUPERSEDED — see "Amendments after independent review": each workflow now has its own group.)** Originally: shared group in both (a group in one workflow serializes nothing against the other). **Rebase-before-push deferred** — it is not caused by this feature, and with `fetch-depth: 1` a rebase is a known-flaky operation on the primary publishing path; don't risk the pipeline again without a way to verify it. |
| Leaderboard view | In scope | Deferred | **In scope, minimal, and last** (so it can be cut without affecting badges). Badges only describe today's picks; "which stocks have been most consistent?" — the user's literal question — needs a page that also shows stocks that dropped out. |
| Score trend | Suppress across incompatible score definitions (store version) | Plain delta | **Store a `scoring_version` per session; compute trend only within one version.** Cheap now, painful to retrofit. |

## Snapshot schema (v1) — one file per recorded session

```
data/pick_history/snapshots/daily_full/YYYY-MM-DD.json
{
  "schema_version": 1,
  "run_kind": "daily_full",
  "provenance": "live" | "backfill",
  "session_date": "2026-09-18",            // America/New_York
  "generated_at": "2026-09-18T17:07:46Z",  // UTC
  "scoring_version": "v1",
  "source": { "git_sha": "...", "github_run_id": "...", "source_commit": "919bf881" (backfill only) },
  "scope": { "total_universe": 3770, "analyzed": 1973, "completed": true },
  "result": "success" | "no_candidates",
  "lists": {
    "shortlist": [ { "ticker", "rank", "score", "composite_score", "passed_filters" } ],  // null if not produced this run
    "top20":     [ { "ticker", "rank", "score", "combined_score" } ]
  }
}
```

A list that is `null` (not produced) is excluded from that list's denominator; an empty list `[]` counts as an observation.

## Derived stats (per ticker, per list, over a window of N recorded sessions)

appearances / denominator (denominator = `min(N, sessions_available)` — **always show the real denominator**; only 5 sessions exist at launch, so a "last 20" view must not read as 20), appearance rate, current streak (0 if absent from the latest session), longest streak, first/last seen, best & average rank, latest/average score, score delta (same `scoring_version` only), compact per-session history for tooltips. Response also carries `sessions`, `sessions_available`, `coverage_gaps`, `warnings` (e.g. skipped corrupt snapshot), and `latest_session_date` so the UI can say "history through DATE".

## API

`GET /api/pick-history?list=shortlist|top20&window=5` — window clamped 1–60, unknown values fall back to defaults, never a 500; empty ledger → 200 with an empty shape. Also `/api/scans` gains `run_kind` (parsed from a new `Run Kind:` report header; older reports inferred as `sample` when `Total Universe` ≤ 150).

## Tasks

- TASK-001 | Codex | `src/screening/pick_history.py` + `tests/test_pick_history.py`: schema constants, validation (dup tickers, bad shapes), atomic per-session writer, ledger reader that skips corrupt files with a warning, aggregation (session-based streaks, windows, coverage gaps, null-vs-empty lists, versioned trend). Must include tests for: Fri→Mon streak continues; zero-candidate session breaks streaks; missing session ≠ disappearance; same-date rewrite is idempotent; window larger than available sessions; corrupt file skipped; NaN sanitized; ET date-key boundary. Claude independently re-derives streak math on adversarial fixtures before accepting. | no deps
- TASK-002 | Codex | Scanner + CI wiring: `--run-kind {daily-full,midday-sample,local}` (default `local`); `midday-sample` never overwrites canonical `top20_latest.json`/`latest_optimized_scan.txt`; `daily-full` records the ledger (fail-soft, loud warning); report gets a machine-readable `Run Kind:` header; both workflows pass `--run-kind`, share one `concurrency` group (`cancel-in-progress: false`), and explicitly `git add data/pick_history/` (not silently swallowed); `.gitignore` negation + a pytest asserting the ledger path is **not** ignored. Nothing else in the workflows changes. | deps: 001
- TASK-003 | Claude | `scripts/backfill_pick_history.py`: explicit manifest of the 5 accepted commits; reads `git show <hash>:…` directly; cross-checks each against its dated report header (Generated/Universe/Analyzed); marks `provenance: "backfill"`; run twice → byte-identical; commit the 5 snapshot files. | deps: 001
- TASK-004 | Codex | `dashboard.py`: `/api/pick-history` and `run_kind` on `/api/scans`; Flask contract tests (empty ledger, populated, bad query params, corrupt snapshot → warning not error). | deps: 001
- TASK-005 | Claude | Frontend part 1: Consistency badge on each Shortlist card (plain text badges — **no emoji**, this project forbids them: e.g. "4/5 days", "3-scan streak", "New"), Consistency column in the shared `renderTop20Table` (covers Shortlist fallback + Market), Market default-scan fix (default to newest non-sample scan; label samples "(100-stock sample)"), "history through DATE" caption, CSS, plain-Node tests. | deps: 004, 003 (real data), sequencing constraint below
- TASK-006 | Codex | Frontend part 2: minimal Consistency leaderboard view (`static/js/views/consistency.js`, nav entry under Analyze, route registration, list + window selectors, sortable table incl. stocks not present today, actual denominators shown) + tests. | deps: 005 (sequenced — shares `ui-helpers.js`/`dashboard.css`)
- TASK-007 | Claude | Verification: full Python + JS suites, module-graph load, Flask checks, `.gitignore` assertion, YAML validity. Live checks via `workflow_dispatch` — (a) midday first (cheap): confirm it leaves canonical `top20_latest.json` alone and writes no ledger file; (b) daily (~96 min, real API calls + a real email — **needs explicit user confirmation before triggering**): exactly one `daily_full/DATE.json` committed, a same-day re-dispatch replaces rather than adds, dashboard Sync shows badges. | deps: all

Order: 001 → (002 ∥ 003 ∥ 004) → 005 → 006 → 007. Tasks 002/003/004 touch disjoint files.

## Sequencing constraint vs the chart-modal sprint

TASK-005/006 and the chart-modal sprint both edit `ui-helpers.js`, `shortlist.js`, `market.js` and `dashboard.css`. Backend tasks 001–004 have no overlap and can start any time. Build the frontend halves **one sprint at a time** (recommend: pick-history frontend first — smaller, and it fixes the misleading Market default view — then the chart modal), to avoid the concurrent-edit clobbering seen earlier in this project.

## Out of scope (deliberate)

- Tracking all buy signals; a `midday_sample` history series.
- Charts, heatmaps, per-ticker timeline pages.
- Fixing the momentum "Day N" streak (weekday-aware logic + a CI-derived source) — flagged, not done.
- `git pull --rebase` before push (shallow-clone caveat; separate hardening task).
- Ticker-symbol alias/rename reconciliation (symbols treated as distinct identities for now).
- Consistency badges on historical (non-latest) Market scan selections — present-day history on past buy rows would be temporally misleading.

## Risks to watch

- Workflow edits are on the primary publishing path — keep them minimal, validate YAML, and verify with `workflow_dispatch` (the earlier 60-minute-timeout regression is the cautionary tale).
- A same-day manual re-dispatch replaces the scheduled run's snapshot (latest wins) — acceptable, documented.
- Only 5 sessions at launch: every stat must print its true denominator.
- `zoneinfo` needs tzdata on the runner/app — verify in CI and in the packaged app.

## Amendments after independent review (TASK-002 CI review by Antigravity + my own end-to-end checks)

Findings and how each was dispositioned. Source: `.sprint/reviews/pick-TASK-002-antigravity.md`.

| ID | Finding | Decision |
|---|---|---|
| SEC-01 | A concurrency group shared by both workflows lets a third run cancel a PENDING run (GitHub keeps one pending run per group) — a midday run or manual dispatch could silently cancel a pending **daily** scan. | **Adopted, and this reverses the "shared group in both" row of the disagreements table.** Each workflow now serializes only with itself (`screening-daily`, `screening-midday`). The suggested alternative (move the daily cron to 07:00 UTC) was **declined**: the scan was designed as a pre-market run and GitHub's ~4–5 h queue delay is what makes it a midday run today; changing the cron would change what the scan measures, and is a separate decision. |
| SEC-02 | `results['total_analyzed']` was indexed outside the fail-soft wrapper. | **Adopted** (`.get`). |
| SEC-03 | Move `git add data/pick_history/ 2>/dev/null \|\| true` into the commit step so a failed staging step can't leave the ledger behind silently. | **Declined as specified** — swallowing errors is the exact silent-failure trap found earlier (an ignored path + `\|\| true` = green CI, no ledger). **Adopted the underlying concern differently:** the staging step now emits an explicit `::warning` annotation on failure (still non-blocking), and a test forbids `\|\| true` / `2>/dev/null` there. |
| SEC-04 | A later same-day run finding zero candidates would overwrite a good morning snapshot and reset every streak. | **Adopted.** `record_scan` refuses to replace a same-day `success` session with `no_candidates` (override: `allow_downgrade=True`). A genuine zero-candidate day on a fresh date is still recorded. |
| SEC-05 | Ledger snapshots were missing from the 90-day run artifacts, so a failed push loses the day. | **Adopted.** `data/pick_history/` added to the artifact upload. |
| SEC-06 | Duplicate tickers from upstream would make validation drop the whole day. | **Adopted.** `build_snapshot` de-duplicates (first occurrence keeps the better rank); the validator still rejects duplicates in hand-built snapshots. |

Deferred (unchanged, still out of scope): `git pull --rebase` before push (a push racing an unrelated commit to `main` still loses the day's push; the artifacts now retain the ledger snapshot so it is recoverable).

Other reviewer fix during TASK-001: the America/New_York zone lookup is now lazy so the read-only dashboard API can never be broken at import time by missing tz data.
