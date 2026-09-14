# Sprint: Fix Shortlist Not Updating

## Problem

User report: "The Shortlist view is not updating to the latest data."

## Engineering Council process

HARD-classified (spans CI/CD scheduling, Python data-generation logic, git-based
sync architecture, and a recently-refactored frontend — genuinely could have been
any of these). Full council run: Claude and Codex independently investigated the
same problem with no shared conclusions beforehand. (Antigravity's headless CLI
mode remains a known, previously-exhausted tooling gap in this environment —
excluded per established precedent from this session's earlier sprint, not
re-attempted.)

Findings converged strongly, and Codex surfaced one critical fact Claude's own
pass missed. Full investigation transcript: `.sprint/council/codex-shortlist-investigation.md`.

## Root cause (evidence-based, both agents + direct verification agree)

**1. CRITICAL — an active regression, introduced by Claude earlier in this same
session, currently blocks every future scheduled run:**

`.github/workflows/daily_screening_git_storage.yml` had `timeout-minutes: 60`
added to its `screen-stocks` job in commit `377523cf` (pushed today,
2026-09-13 22:47 EDT), as part of an earlier bug-fix sprint this session —
intended to guard against a hung scan (a real incident that happened once,
locally). Verified via `gh run list --json startedAt,updatedAt` against the
last 10 scheduled runs: **every single one, going back to 2026-08-31, took
consistently 63–64 minutes** (63m18s to 64m9s, no exceptions). A 60-minute
timeout will therefore kill every future run 3–4 minutes before it reaches
its git-commit/push step — permanently blocking the shortlist/top20 pipeline
from ever publishing again, not just explaining past staleness. This must be
fixed before the next scheduled run completes (or is killed).

**2. Already partially fixed this session, but unverified by any real run:**
Before today's earlier fix (also in `377523cf`), `run_optimized_scan.py` only
wrote `top20_latest.json`/`shortlist_latest.json` when `buy_signals`/`top20`
were non-empty. Verified via full git history (`git log --all -- data/daily_scans/shortlist_latest.json`):
**not one of the ~40+ successful automated workflow runs since at least
2026-08-31 ever actually committed to these two files** — the only commit
touching them in the entire repo history is a manual local commit made
earlier today from a stale (2026-09-09) local snapshot. This is consistent
with buy_signals legitimately being empty on most/all scan days (plausible
for a strict Minervini-style screener) under the old silently-skip-on-empty
code. The fix (unconditional writes, including an explicit empty payload) is
already in place but has never been exercised by a real scheduled run.

**3. Current state:** the data backing the dashboard's Positions/Shortlist/
Market views right now is that stale manually-committed local snapshot. The
dashboard's own "Sync latest" / 5-minute auto-sync is working exactly as
designed — `git pull` correctly reports "already up to date" because there
genuinely is nothing newer on `origin/main`. **This is not a frontend or sync
bug**, despite the recent large UI refactor — independently confirmed by both
investigations (the extracted `shortlist.js` view fetches `/api/shortlist`
and rerenders on sync exactly as the pre-refactor code did).

**4. Secondary, real UI-truthfulness bug (Codex's find):** `shortlist.js`'s
empty state can't distinguish "no data has ever loaded" from "today's scan
legitimately found zero candidates," and doesn't surface the shortlist's own
`generated` timestamp on an empty render (it's set after the empty-check
branch). Once the pipeline above is fixed, a legitimate empty-shortlist day
would look identical to a broken one — undermining trust in the fix.

**5. Not a bug, just worth knowing:** scheduled trigger times have
consistently started ~4–4.5 hours after the 12:00 UTC cron fire (actual
starts: 16:11–17:39 UTC every day, not 12:00 UTC) — a documented GitHub
Actions platform limitation for scheduled workflows, not something to code
around. The workflow's own comment ("Run at 7am EST") is now misleading
about when picks actually land.

## Tasks

- TASK-001 | Claude | **Urgent**: fix the workflow timeout regression (raise `timeout-minutes`, add safety margin above observed runtime) | no deps
- TASK-002 | Codex | Atomic JSON writes + explicit result state (`success`/`no_candidates`) in `run_optimized_scan.py`'s output, so "legitimately empty" is distinguishable from "broken" | no deps
- TASK-003 | Claude | Fix `shortlist.js` empty-state: show `generated` timestamp always, distinguish "no data yet" vs "zero candidates today" | deps: 002 (consumes the result-state field)
- TASK-004 | Claude | Surface data freshness (shortlist's own `generated` date) near the Sync button, so this exact confusion — "sync says up to date" vs "data looks old" — is legible to the user going forward | deps: 003
- TASK-005 | Claude | Verification: after TASK-001 lands on `main`, manually trigger the workflow (`gh workflow run` / `workflow_dispatch`) and confirm end-to-end — completes within the new timeout, writes fresh data, commits, pushes, dashboard picks it up — without waiting for tomorrow's cron | deps: 001, 002, 003, 004

## Explicitly out of scope for this sprint

- Reducing the scan's actual ~63-minute runtime (Codex flagged this as worth
  profiling long-term; not blocking, not part of this fix).
- Rebuilding the sync mechanism around commit SHAs instead of `git pull`
  output-string parsing (Codex's suggestion — a good idea, bigger than this
  bug fix warrants right now).
- A full run-status manifest / observability system (Codex's fuller proposal;
  TASK-002 covers the minimal version actually needed to fix the reported bug).
- Migrating off git-based storage to a database/object store (architecturally
  cleaner per Codex, but far more than this fix needs).
