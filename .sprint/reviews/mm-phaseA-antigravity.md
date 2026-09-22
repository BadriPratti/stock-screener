# Independent Code Review: Persistent Buy-Opportunity Tracker (Phase A Backend)

Engineering Council review of Phase A implementation per `.sprint/SPRINT_PLAN_LIVE_CHART.md` (Amendments 1 & 2).

---

### Prioritized Defect Findings

#### 1. [CRITICAL] Shallow clone breaks push rebase retry on concurrent remote changes
- **File & Line**: `scripts/ci_push_with_rebase.sh:17` via `.github/workflows/daily_screening_git_storage.yml:48` and `midday_quick_scan.yml:32`
- **Concrete Scenario**: Both workflows check out with `fetch-depth: 1` (shallow clone). The daily scan takes ~64 minutes. If the local app or midday scan pushes a commit to `origin/main` during this window, `ci_push_with_rebase.sh` executes `git pull --rebase --no-autostash origin "$branch"`. Because `.git/shallow` truncates ancestry, Git cannot find the merge base with `origin/main` and fails with `fatal: refusing to merge unrelated histories` or `cannot rebase onto a shallow commit`. All 4 attempts fail and exit code 1; the daily scan's committed results and fundamental cache are lost.
- **Fix**: Run `if [ -f "$(git rev-parse --git-dir)/shallow" ]; then git fetch --unshallow || git fetch --deepen=100; fi` in `scripts/ci_push_with_rebase.sh` before rebase, or set `fetch-depth: 0` in checkout steps.

#### 2. [HIGH] Frame validation crash on regime-gated buys lacking RS readings
- **File & Line**: `src/screening/intraday_rescore.py:110-115`
- **Concrete Scenario**: When SPY downtrend closes the regime gate (`should_generate_buys=False`), `_points_from_analyses` evaluates the roster. If a stock passes buy rules (`is_buy=True`) but lacks an RS reading (e.g., newly listed or <20 bars of RS data, where `details['rs_slope']` is `None`), `normalize_buy_signal` produces a point with `rs=None`. `intraday_rescore.py` directly forces `point["evaluation"] = "not_qualified"`. At line 282, `validate_frame()` enforces `("score", "rs")` on all `not_qualified` points and raises `ValueError: points[...] (not_qualified) needs a finite rs`. `run_rescore` catches this as a fatal exception, aborts, and writes no frame.
- **Fix**: Check `if point.get("rs") is not None` before marking `not_qualified`; otherwise set `evaluation="not_scored"` and `drop_reason="regime_gate"` via `outcome_point()`.

#### 3. [MEDIUM] `current_streak_frames` leaks across calendar days and includes daily scans
- **File & Line**: `src/screening/market_motion.py:644-650`
- **Concrete Scenario**: Amendment 1 specifies `current_streak_frames` as "consecutive intraday frames qualified today (secondary; shown in the tooltip only)". Line 644 iterates backwards over `non_legacy` without filtering by `f["run_kind"] == RUN_KIND_INTRADAY` or `f["session_date"] == today`. If a stock qualified yesterday and across previous daily/intraday frames, `frame_streak` counts backwards across day boundaries and daily scans, displaying e.g. "8 intraday frames today" when only 1 scan has run today.
- **Fix**: Restrict the backward frame streak loop to frames where `f["session_date"] == dates[-1]` and `f["run_kind"] == RUN_KIND_INTRADAY`.

#### 4. [MEDIUM] `_newest_daily_frame` ignores `legacy_report` frames, breaking rescore post-backfill
- **File & Line**: `src/screening/intraday_rescore.py:51-57`, `181-186`
- **Concrete Scenario**: After running `scripts/backfill_market_motion.py`, the repository contains 5 historical daily frames of kind `legacy_report` with 84 tracked tickers. If a user triggers an intraday rescore before a live 64-minute full scan runs, `_newest_daily_frame` filters only for `RUN_KIND_DAILY_FULL` and returns `None`. `run_rescore` immediately aborts with `status: failed, reason: no_completed_daily_frame`.
- **Fix**: Change filter to `frame.get("run_kind") in market_motion._DAILY_KINDS`.

#### 5. [MEDIUM] Degraded runs with high failure rates are marked `completed: True`
- **File & Line**: `src/screening/intraday_rescore.py:258-278`
- **Concrete Scenario**: If rate limits or network dropouts cause 198 out of 200 roster stocks to fail during batch processing, `analyzed == 0` is false (`analyzed == 2`). The frame is written with `scope.completed = True`. Because `scope.completed` is true, `load_frames()` permanently treats this heavily degraded run as a valid replay endpoint, recording 198 stocks as `error` and corrupting tracker streak continuity.
- **Fix**: Require `failed / max(1, roster_count) < 0.5` (or similar completion threshold) before setting `scope.completed = True`.

#### 6. [LOW] Scoring loop parity mismatch under closed regime gate
- **File & Line**: `run_optimized_scan.py:579-601` vs `src/screening/intraday_rescore.py:105-117`
- **Concrete Scenario**: When `should_generate_buys=False`, `run_optimized_scan.py` skips the buy scoring loop entirely (`scored_non_buys` remains empty), emitting tracked stocks as `not_scored` with no coordinates. In contrast, `intraday_rescore.py` scores them anyway and records them as `not_qualified` with coordinates retained. The same stock on the same day receives different evaluation schemas between daily and intraday frames.
- **Fix**: Align behavior so both either preserve coordinates or emit `not_scored` when regime suppresses buys.

#### 7. [LOW] Query parameter mismatch (`tier` vs `tiers`)
- **File & Line**: `dashboard.py:938`
- **Concrete Scenario**: Plan task MM-005 specifies `GET /api/market-motion/tracker?tier=&min_streak=`. Line 938 only checks `request.args.get("tiers")`. A client requesting `?tier=active` has the parameter ignored and falls back to `"active,watching"`.
- **Fix**: Check `request.args.get("tier") or request.args.get("tiers", "active,watching")`.

---

### Verdicts per File

- `src/screening/market_motion.py`: PASS with fix needed (clean schema, pure tracker, but `current_streak_frames` leaks across dates).
- `src/screening/intraday_rescore.py`: FAIL (must fix regime-gated missing-RS crash and `legacy_report` detection post-backfill).
- `run_intraday_rescore.py`: PASS (clean entrypoint, CLI options, and exit code propagation).
- `run_optimized_scan.py`: PASS (robust fail-soft sidecar, O(N) builder, zero scanning/email delivery risk).
- `scripts/ci_push_with_rebase.sh`: FAIL (shallow clone `fetch-depth: 1` causes `git pull --rebase` to fail on push contention).
- `.github/workflows/daily_screening_git_storage.yml`: PASS with fix needed (staging is correct, but shallow clone breaks push rebase).
- `.github/workflows/midday_quick_scan.yml`: PASS with fix needed (staging is correct, but shallow clone breaks push rebase).
- `dashboard.py`: PASS (strict JSON, clean clamping, robust path containment; minor `tier` query param alias needed).
- `scripts/backfill_market_motion.py`: PASS (deterministic, idempotent, strictly validates against schema and git history).

---
## Lead disposition (2026-09-20)
1 CRITICAL shallow-clone rebase: DISPROVED by test (tests/test_ci_push_with_rebase.py rebases a --depth 1 clone after a remote advance and passes). No change.
2 regime-gated buy without RS: FIXED (not_scored/regime_gate) + test.   3 frame streak across dates: FIXED (newest session only) + test.
4 legacy-only history blocks rescore: FIXED + test.   5 mostly-failed run marked completed: FIXED (>50% failures => failed, no frame) + test.
6 regime-gate scoring parity: ACCEPTED as-is (intraday keeps coordinates, which is more informative; documented).
7 `tier` query alias: applied after MM-006 finishes editing dashboard.py.
