# Sprint: Live "Packed" Buy Opportunity Map (memory + motion + intraday refresh)

STATUS OF THIS DOCUMENT: PLAN ONLY. Nothing here has been built, committed, pushed, scheduled, or dispatched.
Three items need the user's explicit approval before the affected task runs (see "Decisions the user must make").

## Request (user's own words)

"the chart of buy opportunity should also include this like realistically that graph should be packed to the brim
because those stocks that it viewed before should still be there realistically we should do this stock scan every
2 hours and everything simultaneously moves in motion"

## Engineering Council process

HARD. Full council, all three agents investigated the SAME problem independently before any comparison:
- Claude: `.sprint/council/claude-live-chart.md` (written before reading the others)
- Codex: `.sprint/council/codex-live-chart.md`
- Antigravity: `.sprint/council/antigravity-live-chart.md`
Shared verified facts handed to both external agents: `.sprint/council/live-chart-data/FACTS.md`, `buy_signal_facts.txt`.
I then re-verified every disputed claim against the code (results below).

## What the request really needs (the finding that shapes everything)

The chart is the last 20% of the work. Three prerequisites do not exist today:

1. No stored history of buy signals. The Market chart plots `buy_signals` regex-parsed from the human text report
   (`dashboard.py:93 parse_scan_file`), and that report details only the TOP 50 buys (`run_optimized_scan.py:151`
   `buy_signals[:50]`) out of 364-479 real ones; the rest are bare tickers with no score/RS. The pick-history ledger
   deliberately stores only shortlist/top20. So "stocks it viewed before should still be there" has nothing to read.
2. The ledger's vocabulary is "one recorded session per ET day". Intraday frames need a different granularity that must
   not leak into the daily consistency badges ("N scans").
3. "Every 2 hours" is not what GitHub delivers: full scan = 3,770 tickers x 1.0 s rate-limit = 62.8 min (matches every
   report), and scheduled runs have started 4-5 h late every day since 2026-08-31 (documented in the daily workflow).

Also honest about the motion itself: the scanner scores on DAILY bars, so intraday only the partial current bar moves.
Intraday motion is real but modest (RS/volume drift, occasional threshold crossings). The dramatic motion is across
days. The replay is designed to look right with either.

## Converged decisions (all three agents agree unless noted)

1. Separate store, daily ledger untouched. New module `src/screening/market_motion.py`; `pick_history.py`, its
   `_RUN_KINDS`, `/api/pick-history`, the badges and their 74 tests do not change. 12 intraday frames can never inflate
   "N scans". (unanimous)
2. Machine-readable frames, not text parsing. Scanner writes ALL qualified buys as a slim JSON frame (never re-parse
   text at request time; parse the 5 legacy reports once for backfill only). (unanimous)
3. Two-tier cadence, NOT repeated full scans: the daily full scan stays as the discovery run; intraday runs are a light
   RE-SCORE of a tracked roster (<=500 tickers) with no LLM agents, no email, no canonical/report/ledger writes, no
   breadth/regime recomputation. (unanimous)
4. Bounded "trailing memory with visual decay", not an infinite accumulator. A stock that broke down weeks ago must not
   sit on a "Buy" map looking actionable. Current qualifiers are solid; recent dropouts are hollow, muted, dated ghosts.
   (unanimous; Antigravity and Codex most explicit)
5. Motion = custom requestAnimationFrame interpolation KEYED BY TICKER over one stable dataset, `chart.update('none')`,
   plus a small Chart.js plugin for trails/threshold/labels. Chart.js built-in animation is index-based and would
   morph unrelated tickers into each other. Slider is ordinal over RECORDED frames (weekends/holidays are gaps, not
   fake frames). Tweening is a visual transition, never evidence of an intra-gap path. (unanimous)
6. Fixed axis domain across the replay (rescaling per frame fakes motion). (unanimous)
7. Frontend has ONE writer at a time; chart-modal sprint and Market redesign never run concurrently with it.
   (unanimous)
8. `prefers-reduced-motion` is unhandled anywhere today: add CSS + JS (no autoplay, zero-duration steps, tails on
   hover only). Canvas needs a real table alternative that includes decimated points. (unanimous)

## Disagreements and how they were resolved (with evidence)

| Topic | Claude | Codex | Antigravity | Decision |
|---|---|---|---|---|
| Where the 2-hourly run executes | GitHub cron (off-minute) | Local (LaunchAgent preferred) | Local in-app timer primary; 3 fixed cloud windows as fallback | LOCAL, in-app scheduler first. Claude conceded: verified GitHub 4-5 h start delay, push contention (neither workflow rebases), repo growth, and the chart is only read on this Mac. GitHub stays an explicitly separate opt-in alternative. |
| Are intraday frames committed to git | yes, prune | local by default, batch daily if ever committed | keep 10 days in git | LOCAL and gitignored. Only the once-a-day `daily_full` frame is committed by the workflow. Removes bloat/push-contention. Verified `git checkout -- data/` in `/api/sync` (dashboard.py:641) only reverts TRACKED files, so ignored local frames survive Sync. |
| Runtime of a 400-500 ticker re-score | 12-15 min | ~4 min (linear from the 100-stock sample: 0.8 min) | 1.5-2 min | Verified: time is set by the global rate limiter (`optimized_batch_processor.py:131-144`; 62.8 min = 3,770 x 1.0 s). 500 tickers = ~4 min at default pacing, ~8.3 min at `--conservative`. Use conservative pacing, SLO <= 10 min; MEASURE in build, do not promise. Antigravity's 1.5-2 min is unsupported (per-ticker 5y history fetch, no batch download). |
| Y axis | keep fixed | fixed 45-100 with threshold line at 48% | `suggestedMin: 50` | Codex is right and Antigravity's premise was wrong: the chart y-scale has no min/max today (auto-fit, `charts.js:195-199`), so it zooms INTO the top-50's 81-93% strip. Verified real buy threshold is `final_score >= 60` of 125 = 48% (`signal_engine.py:694`; the report's "Score >= 70" header is a misleading label). Fixed domain 40-100 with a drawn 48% threshold line, taken from frame metadata (`score_model`). |
| Trail policy | 3 segments, hover full | 3 segments alpha .35/.20/.10 | hidden by default, hover only | Hybrid with a hard performance gate: 1-step motion vector during playback, 3-segment tail only for hovered/selected tickers and when the plotted count <= 250; auto-suppressed by the frame-time budget before any current point is dropped. |
| Point budget | <=600 live + 600 ghosts | 750 current + 450 ghosts = 1,200 | 600 total | Codex's 1,200 default as a STARTING budget, benchmarked at 500/1,200/2,000 (median frame < 33 ms), degrade trails/labels first, never drop current points. |
| Implementation ownership for Antigravity | - | Antigravity implements backfill/scheduler/tests | Antigravity implements UI + controls | Antigravity does REVIEW/AUDIT only. Proven headless limits (no python/node/git; cannot run tests) make it unsafe as an implementer of anything that needs a test loop; it reviewed TASK-002 well last sprint. |

## New findings from the council, folded into the plan

- Exits should move to their REAL new position, not freeze (Codex): the scanner scores every phase-1/2 ticker; a name
  that drops to 57% is a real point below the 48% line. So frames record an `evaluation` state per tracked ticker:
  `qualified` | `not_qualified` (scored, real coords) | `not_scored` (phase 3/4, no score) | `error` | `not_evaluated`.
  "Absent" is never treated as "dropped".
- COVERAGE BOUNDARY (mine, extends Codex): the 5 backfilled frames are `top50_only`. The first real full frame has ~430
  points. Naively that is ~380 "new entries" blooming at once. Rule: tickers newly LOCATED across a coverage change
  are drawn without an entry bloom and are not counted as new opportunities; tickers absent from a `top50_only` frame
  are `not_evaluated`, never dropouts. Explicit acceptance test.
- The sidecar needs explicit normalization (Codex): the in-memory signal has no `max_score`; `rs` = `details['rs_slope']`
  (20-day RS slope, identical to what the report prints as "RS:"), `rr_ratio` = `risk_reward_ratio`; `max_score` = 125.
- Regime gate (mine): intraday cannot recompute breadth over a buys-only set (would read ~100% Phase 2). Daily frame
  stores `regime.should_generate_buys`; intraday frames inherit it (`regime_source_run_id`).
- Existing defects to fix on the way (all are in files this sprint already owns):
  a. `/api/scan?path=` opens ANY existing path (`dashboard.py:781-793`) - path-containment fix (scan ids / resolve under
     SCAN_DIR). Local-only Flask, but it is an arbitrary-file-read shape; do not replicate it in the new API.
  b. `loadMarketScan` guards only `currentView`, not "is this still the selected scan" (`market.js:308-318`): a slow
     older response can paint last. Fix with a request token.
  c. The Market "Live" loop never re-renders the opportunity map (`market.js:70-78`); the 5-minute auto-sync reroutes
     the whole view and would reset any replay state (`dashboard.js:61-70`). Use an in-place "data updated" event or
     retain and reseed the last frame.
  d. Not fixed here, flagged: report header says "Score >= 70" but the buy threshold is 60.
- Intraday stale-fundamentals honesty: technicals update intraday, fundamentals (35 of 125 points) come from cache.
  Frames carry `fundamentals_as_of`; UI copy says "intraday re-score, fundamentals as of <date>", never "real-time".

## Architecture

### Data store (`src/screening/market_motion.py`)
```
data/market_motion/snapshots/
  daily_full/<run_id>.json          COMMITTED (workflow stages it; whitelisted in .gitignore)
  intraday_rescore/<run_id>.json    LOCAL ONLY (gitignored)
```
run_id = `<UTC timestamp>-<kind>` (immutable; ordering is UTC; ET session date is metadata, not uniqueness).
Frame (v1): schema_version, run_id, run_kind (`daily_full` | `intraday_rescore` | `legacy_report`), generated_at,
session_date_et, scoring_version, score_model {max_score:125, buy_threshold:60, rs_metric:"rs_slope_20"},
regime {should_generate_buys, source_run_id}, fundamentals_as_of, scope {mode, requested, analyzed, failed, completed,
candidate_source_run_id}, coverage {kind: complete_for_scope | top50_only, qualified_total, located_points},
points[] of {ticker, evaluation, score, max_score, rs, phase, entry_quality, current_price, stop_loss, rr_ratio,
volume_ratio?, rank?, top_reason?(emoji stripped at write), drop_reason?, error_code?}.
Only `scope.completed == true` frames are replay endpoints. Writes: validate -> sanitize_nan -> same-dir temp -> fsync
-> os.replace (same pattern as `pick_history.write_snapshot`). Duplicate tickers normalized (upper/trim, best rank wins).
Size: ~600 rows x ~150 B = ~90 KB raw, ~20 KB gz per daily frame => ~5 MB/yr in git. Intraday local: 4/day x ~75 KB
= ~300 KB/day; local retention = last 60 sessions (max 240 frames), then thin to last-of-day.

### Roster for intraday runs
Union of the latest daily_full qualifiers and recently-qualified intraday names, capped at 500 (top 400 by score + up to
100 recent dropouts/movers), deterministic order. UI states "500 of N tracked intraday". Known limitation to tell the
user: a stock that first qualifies at 1 pm is invisible until the next daily full frame.

### Intraday command (`run_intraday_rescore.py`, new file)
Fetch price+SPY for the roster only; reuse `OptimizedBatchProcessor.process_batch_parallel(tickers)` and
`score_buy_signal`; cached fundamentals; no earnings/Reddit/insider/Congress/LLM/shortlist/email/report/canonical
writes/pick-history writes. Market-open guard: if SPY's latest bar date != today ET, exit 0 with no frame (no fake
motion; also covers holidays without an exchange calendar). Atomic frame only after the roster completes.

### Scheduler (approval-gated; default OFF)
In-app scheduler (`src/screening/motion_scheduler.py`, started from dashboard.py) at ~09:35, 11:35, 13:35, 15:35 ET
on weekdays while the app is open; on app launch, if the market is open and the newest frame is older than ~2 h, run
once (catch-up). "Run now" + status (last success, next intended, roster size, duration, last error) exposed via API and
shown in the UI, so silence is visible when the Mac sleeps. Uses the existing job runner (subprocess, watchdog 45 min
vs a <=10 min run). Setting default OFF until the user flips it. A macOS LaunchAgent (runs while Mac is awake, app
closed) is a documented phase-2 option requiring approval because it installs system configuration.

### API (additive; existing contracts unchanged)
`GET /api/market-motion?limit=20&before=<run_id>` (ordered frames + warnings for skipped/corrupt files + `latest_run_id`
+ `has_more`; default 20, cap 60; opaque validated ids, no filesystem paths), `GET /api/market-motion/latest`,
scheduler status/run-now endpoints. `/api/scan` path-containment fix. `/api/scans`, `/api/pick-history` shapes untouched.

### Frontend
- `static/js/core/market-motion.js` (new, pure, unit-tested): ticker-keyed tracks, interpolate(t) with enter/exit/stale/
  coverage-boundary handling, fixed domain, deterministic decimation, tail construction, scoring-version divider,
  injected clock/rAF for tests.
- `static/js/charts.js`: plain global `renderMarketMotionChart(...)` (classic script; no `export`); `_destroyChart`
  extended to run registered cleanup (cancel rAF, remove matchMedia listener) then destroy. Create once, update in place.
- `static/js/views/market.js`: replay controls (Play/Pause, Prev, Next, range slider over recorded frames with ET labels
  and elapsed gap, speed 0.5/1/2x, "Live"/"Return to live"), status line, scheduler status, request-token fix,
  in-place live update: at the live edge tween all points 800 ms; if scrubbed into history do NOT yank, show
  "New snapshot available". The report dropdown and the replay clock are separate and labelled as such.
- `static/css/dashboard.css` + `dashboard.js`: controls styling, `@media (prefers-reduced-motion: reduce)`, in-place
  data-updated event. Encodings: color = entry quality (existing palette), solid vs hollow = current vs ghost, alpha
  `max(0.10, exp(-0.55*age))` for ghosts, no size-for-score (Y already encodes it), labels only for selected/hovered/
  top-10 score/top-10 movers (cap 20). Plain text/CSS only, no emoji.
- Accessible table: sortable (ticker, status, score, RS, entry quality, first/last seen, change) containing every record,
  including decimated ghosts; `aria-live="polite"` updated only when the selected frame changes.

## Tasks (approved-on-approval ordering; NOTHING STARTS until the user says /sprint-build)

Owners chosen for testability: Claude and Codex implement (both can run python/node); Antigravity reviews.

### Phase A - data + backend (no shared frontend file; may run BEFORE or alongside the chart-modal sprint)
- MM-001 | Claude | `src/screening/market_motion.py` (schema, validation, normalization helper `normalize_buy_signal`,
  atomic timestamped write, completed-only loader with warnings, evaluation states, coverage kinds, retention selector,
  ET labels) + `tests/test_market_motion.py` + `.gitignore` (whitelist `daily_full`, ignore `intraday_rescore`) with
  real `git check-ignore` tests. Deps: none. Files: new + `.gitignore`.
- MM-002 | Codex | Full-scan sidecar in `run_optimized_scan.py` (sole writer): every qualified buy + outcomes for tracked names,
  only for `daily-full` and not test-mode, fail-soft (warning annotation, never blocks email), written before email;
  daily workflow stages `data/market_motion/snapshots/daily_full/` (mirror the pick-history staging step: no `|| true`
  swallowing, `::warning`), artifact path added. Tests. Deps: MM-001. Files: `run_optimized_scan.py`,
  `.github/workflows/daily_screening_git_storage.yml`, tests.
- MM-003 | Claude | `scripts/backfill_market_motion.py` from the same 5 accepted reports as the pick-history backfill:
  `legacy_report`, `coverage.kind=top50_only`, no invented coordinates, two-phase, idempotent byte-identical rerun,
  refuses live overwrite. Deps: MM-001. Files: new script + tests.
- MM-004 | Codex | `run_intraday_rescore.py` (+ small helper module) per the spec above; roster builder; market-open guard;
  measured runtime recorded; tests with a stubbed processor. Deps: MM-001. Files: new only (disjoint from MM-002, so
  MM-002 and MM-004 may run in parallel).
- MM-005 | Claude | dashboard.py: `/api/market-motion`, `/api/market-motion/latest`, `/api/scan` path containment; tests;
  existing API tests unchanged. Deps: MM-001, MM-003. Files: `dashboard.py`, new tests.
- MM-006 | Codex | Scheduler + status/run-now endpoints (default OFF). **BLOCKED on user approval of decision 1.**
  Deps: MM-004, MM-005. Files: `dashboard.py` (after MM-005), new scheduler module, tests.
- MM-007 | Claude | `static/js/core/market-motion.js` + `tests/js/test_market_motion.js` (new files only; may run in
  parallel with Phase A and even with the modal sprint). Deps: frame schema from MM-001.
- Antigravity review gate after MM-002/004 (workflow + scanner-output policy; same procedure as last sprint).

### Phase B - frontend integration (single writer chain; BLOCKED until the chart-modal sprint is merged or explicitly deferred)
- MM-008 | Codex (sole writer of `market.js`, `charts.js`, `dashboard.css`, `dashboard.js`; `ui-helpers.js` only if
  the merged modal API requires it). Deps: MM-005, MM-007, modal sprint done/deferred.
- MM-009 | Antigravity | Read-only audit of MM-008: ARIA/keyboard, lifecycle leaks, emoji, reduced-motion, table completeness.
  Findings go back to the MM-008 owner; no concurrent edits.
- MM-010 | Claude | Verification: full pytest + all JS tests, real ES-module graph, real frames (the 5 backfilled) through the
  real model, 500/1,200/2,000-point frame-time benchmark, browser visual check with the Chrome tools if the extension
  connects (also closes the still-open "never eyeballed in a browser" gap for the pick-history UI), confirm no workflow
  was dispatched and no scheduler enabled without approval.

## Decisions the user must make (I will not assume any of these)

1. SCHEDULER: where "every 2 hours" runs. Recommended: in-app scheduler on this Mac, 4 runs per trading day (~9:35,
   11:35, 13:35, 15:35 ET), no LLM, no email, ~8-10 min each at conservative pacing (~35 min/day of scanning), only
   while the dashboard is open, ships with the switch OFF. Alternatives: (b) macOS LaunchAgent (works with the app
   closed; installs system config), (c) GitHub Actions (rejected as default: 4-5 h start delay, push contention).
   The existing 100-stock midday workflow is unchanged either way.
2. STORAGE: intraday frames local-only (recommended) vs committed to GitHub (cross-machine, more commits/repo growth).
3. ORDER: Phase A (invisible backend) can start immediately without touching any file the modal sprint needs.
   Phase B needs the modal sprint (`SPRINT_PLAN_CHART_MODAL.md`) built first or deferred. Recommended: A now, then the
   modal, then B.
4. SEEDING: the map only becomes "packed" (~430 dots) after the first new-format full scan writes a frame. Until then
   it shows the 5 backfilled top-50 frames (84 distinct tickers). Optional: run one full scan locally right after the
   build (~63 min, real data-provider calls, writes canonical files) instead of waiting for the next GitHub run.

## Out of scope
Real-time (sub-minute) quotes; a tick chart; intraday fundamentals; catching stocks that first qualify intraday (needs
near-miss storage); instrument-id alias reconciliation; the momentum "Day N" calendar-day bug; editing the report's
"Score >= 70" label; the LaunchAgent (phase 2, needs approval).

## Guardrails (carry into every task prompt)
Never read/reference/stage `position/`. No emoji in UI/code/frames. No commit/push without asking. No live
`workflow_dispatch`, no enabling of any schedule, no real email, without explicit user confirmation. Do not
overwrite the user's large uncommitted work (patch backup: `.sprint/logs/preflight-uncommitted-tracked.patch`).
Never two writers on one file. Working git: `export PATH="/Library/Developer/CommandLineTools/usr/bin:$PATH"`;
`gh` always with `--repo BadriPratti/stock-screener`.

---

# AMENDMENT 1 (2026-09-20) - user clarification: a persistent per-stock TRACKER, not a 3-frame fade

## What the user said (their words)
"the graph I am seeing right now is pretty small and very few [options]... only from the last scan but the graph should have
stocks from [options] all around from previous we should really keep track of those stocks meaning we should have a separate
agent keeping track of each one of those stocks and see how they are doing and run the algorithm through those stocks and
once we keep count on how many times in a row that stock is good like we have been doing"

## Reading of the request (and where I am NOT following it literally)
1. Every stock that has ever been flagged stays TRACKED and keeps being run through the same algorithm - not shown for a
   few frames and then forgotten. THIS SUPERSEDES converged decision 4 ("bounded trailing memory, ~3 frames") and the
   "Roster for intraday runs" section: the memory is now a persistent tracker with tiers, not a fading window.
2. Each tracked stock keeps its own running record, including "how many times in a row it has been good" - the same
   consecutive-streak idea as the Shortlist/Top 20 consistency badges, now for the whole buy universe.
3. "A separate agent per stock": NOT one LLM agent per stock. That would be 500+ Claude calls per run, 4 runs/day, cost and
   latency that cannot be justified, and the numbers are produced by the deterministic scoring code anyway. The tracker IS the
   "agent": one deterministic process re-scores every tracked stock and updates that stock's record. The existing LLM
   agents (Fundamentals Auditor, Catalyst Sentiment) keep running only on the daily Top 20 as today; extending them to the
   top of the tracker leaderboard is a separate, cost-gated option, not part of this sprint.
4. The graph itself is too small: today it is a fixed `height: 480px` (`dashboard.css:167`) inside a `max-width: 1300px`
   content column, with one un-filterable dataset. It needs a much larger canvas and real controls (below). The full-screen
   analysis modal (SPRINT_PLAN_CHART_MODAL) is the per-ticker price chart; this map gets its own large layout.

## Tiered tracking (keeps cost bounded while never forgetting a stock)
| Tier | Definition | Re-scored | Shown on map |
|---|---|---|---|
| ACTIVE | qualified (buy, score >= 60) in the latest frame | every intraday run + daily full scan | solid, full colour |
| WATCHING | qualified within the last 10 recorded daily sessions but not in the latest frame | every intraday run (ranked after ACTIVE) + daily full scan | hollow, at its REAL current position (below the 48% line if it scored lower; last position with a stale marker if it is now Phase 3/4 and unscored) |
| RETIRED | not qualified for > 10 consecutive daily sessions | daily full scan only (free: the full scan already analyses ~1,970 tickers) | hidden by default; "Show retired" toggle; re-promotes to ACTIVE the moment it qualifies again |
- Retention numbers (10 sessions) are a starting default in one constant, chosen so a stock that pauses for a week or two
  stays visible; tune from real data once full frames exist. Tickers are never deleted from history, only tiered.
- Intraday cost stays bounded: roster = ACTIVE first, then WATCHING by most-recent-qualified, cap 500 (configurable),
  ~8-10 min at conservative pacing. The map states "tracking N stocks, re-scored intraday: 500". Honest limit: if
  ACTIVE+WATCHING exceeds the cap, the overflow is refreshed on the daily full scan only and labelled "as of <date>".
- The daily full scan writes an outcome row for EVERY tracked ticker (any tier), not just qualifiers, so a stock's record
  never has a hole and "absent" never means "dropped" (the evaluation-state rule from the main plan).

## Per-stock tracker record (DERIVED ON READ from frames, like the pick-history ledger - no mutable counters)
`compute_tracker(frames)` in `market_motion.py`, one entry per ticker:
- `tier`, `first_qualified` (date), `last_qualified` (date), `latest_state` (evaluation) and `latest_score/rs/phase/entry_quality`
- `current_streak_days`: consecutive recorded DAILY sessions the stock has been qualified, ending at the latest session
  (0 if not qualified now); `longest_streak_days`; `sessions_qualified / sessions_observed` (honest denominator, same
  rules as pick-history: a session where the stock was not evaluated is excluded, not counted against it)
- `current_streak_frames`: consecutive intraday frames qualified today (secondary; shown in the tooltip only). Intraday
  frames never inflate the primary day-based streak, so the numbers stay comparable with the Shortlist/Top 20 badges.
- `score_trend`: latest score minus the score at the previous session (only within the same `scoring_version`),
  `best_score`, `avg_score`, per-session sparkline data (date, score, rs, state).
- Coverage rule carried over: sessions from `top50_only` frames count as "observed" only for tickers that were located in
  them; absence there is `not_evaluated`, not a miss.
Streak counting follows the existing convention exactly (Friday -> Monday consecutive; a zero-candidate session is an
observation that breaks streaks; a missing run is a coverage gap, not a break).

## Chart changes that follow from this
- Bigger: full content width, height `clamp(560px, 72vh, 880px)`, plus an "Expand" control that takes the map to a
  near-full-viewport overlay for analysis (reuses the modal sprint's overlay/z-index/focus-trap pattern if that has
  landed; otherwise a local one). All within Phase B's single-writer rule.
- Packed: ALL ACTIVE + WATCHING stocks are plotted (one interactive dot per ticker at the selected time), not just the last
  scan's top 50. Retired is opt-in. Point budget/decimation from the main plan still applies with a degradation order
  (labels, tails, oldest WATCHING) that never drops ACTIVE points.
- Streak is the main visual encoding (replaces "no size-for-score"): dot radius = f(current_streak_days) (e.g. 4px at 1 day,
  growing to ~10px at 10+ days), so long-lived leaders are visibly big and one-day pops are small. Colour stays entry
  quality; hollow = WATCHING. Tooltip: "N days in a row (longest M), qualified S of D sessions, first qualified <date>".
- Real options to slice it: filter chips (Active / Watching / Retired; Entry quality Good/Extended/Poor; Streak >= 2 / >= 3 /
  >= 5), ticker search that highlights and pans focus to a dot, and a "Tracked stocks" sortable table under the chart (same
  data, ticker / tier / streak / longest / qualified-of-observed / latest score / RS / entry quality / first qualified /
  score trend). Table also serves as the accessible alternative and includes every record even when dots are decimated.
- Replay/scrubber, keyed motion, reduced-motion, fixed 40-100 domain, threshold line: unchanged from the main plan.

## Task changes
- MM-001 (Claude): schema gains tracker fields on rows (`tier` is derived, NOT stored; rows store evaluation + numbers), the
  "every tracked ticker gets an outcome row" rule, and `compute_tracker()` + tests (streak edge cases: Fri->Mon, zero-candidate
  session, not_evaluated exclusion, top50_only coverage, scoring-version boundary, retire/re-promote after 10 sessions, dedupe).
  Property test against a brute-force reference like the pick-history fuzz check.
- MM-002 (Codex): daily sidecar writes outcome rows for all tracked tickers (tracked set = union of tickers ever qualified in
  prior daily frames, read from the store) in addition to every qualified buy.
- MM-004 (Codex): roster builder = ACTIVE, then WATCHING (most recently qualified first), cap 500; reports overflow count.
- MM-005 (Claude): `GET /api/market-motion/tracker?tier=&min_streak=` derived on read (default: active+watching), plus the
  frames endpoint; honest `sessions_available`/denominator fields like `/api/pick-history`.
- MM-007 (Claude): pure model adds tier/streak-radius mapping, filter predicates, search, table-row builder, sort.
- MM-008 (Codex, Phase B, sole writer): larger canvas + Expand, filter chips, search, tracked table, streak-sized dots.
- New MM-011 (Claude, small, after MM-005): a "Tracker" badge line reused on Shortlist/Top 20 cards ("qualified 6 of 8
  sessions as a buy signal") ONLY if the user wants it - listed as optional, not scheduled.
- Everything else in the main plan stands, including all approval gates and the four decisions. New sub-decision below.

## One more decision for the user
5. RETENTION: is "stays tracked and visible for 10 sessions after it last qualified, then hidden-but-still-recorded" the right
   default? Alternatives: shorter (5), longer (20), or never hide (the map grows without bound as new names accumulate; the
   real size is unknown until full frames exist - the 5 backfilled top-50 frames alone contain 84 distinct tickers).

---

# AMENDMENT 2 (2026-09-20) - user decisions recorded at /sprint-build, and what they change

## Decisions received ("1: Good  2: Store it on github  3: yes  yes for all")
1. Scheduler = in-app on this Mac, ~09:35/11:35/13:35/15:35 ET weekdays, no LLM, no email. Ships with the master switch OFF
   (one click in the UI to turn on; I will not turn it on for the user).
2. Storage = GitHub. Intraday frames are COMMITTED (supersedes "local-only" in the main plan). `.gitignore` whitelists all of
   `data/market_motion/**` (done in MM-001; check-ignore tests pass).
3. Order = Phase A, then the chart-modal sprint, then Phase B.
4. Seeding scan = yes: one local full scan after the build (real provider calls, ~63 min). It must NOT write the pick-history
   ledger (a Sunday/off-schedule session would pollute the Fri->Mon consecutive-session semantics). See MM-002 flag below.
5. Retention = 10 sessions (constant `RETIRE_AFTER_SESSIONS`, already in market_motion.py).

## New findings that change tasks
- `score_buy_signal` returns score 0 / no details for Phase != 2 and for Minervini-template failures. So `not_qualified`
  (real coordinates) exists only for Phase-2 stocks that pass the template but score < 60; everything else that drops is
  `not_scored` and has NO honest coordinates: the map holds it at its last real position with a stale marker and the reason
  (e.g. "Phase 3", "Fails Minervini trend template"). (Corrects the "glide to a real position" wording in Amendment 1 for that case.)
- Frame `session_date` = date of SPY's newest daily bar (`market_motion.session_date_from_bar`), NOT wall-clock. A weekend
  seeding run is therefore labelled Friday 2026-09-18 and supersedes the top-50 legacy frame for that date
  (`select_daily_sessions` prefers a complete live frame). `market_motion.is_data_current(bar)` is the market-open guard for
  intraday runs (weekends/holidays => no frame).
- GitHub storage + a dirty working tree + concurrent workflows means a naive `git pull --rebase && git push` from the app is
  unsafe (the tree has ~60 uncommitted files; rebase-pull refuses; merge-pull makes messy merges). MM-006 therefore publishes
  with git PLUMBING that never touches the user's index, branch, or working tree:
    a. `git fetch origin main`; list local frame files not present in `origin/main` (`git ls-tree`).
    b. Build a temp index (`GIT_INDEX_FILE`), `read-tree origin/main`, `hash-object -w` + `update-index --add --cacheinfo` for
       ONLY those files, `write-tree`, `commit-tree -p origin/main`, `git push origin <sha>:refs/heads/main`.
       Rejected push => refetch and retry, bounded (3). Explicit pathspec `data/market_motion/` only; never `position/`.
    c. Reconcile: for each published file whose local bytes equal the pushed blob, remove the local untracked copy and
       fast-forward via the existing pull path; if the pull fails, WRITE THE FILES BACK from memory (no frame may be lost).
  Failure of any step is soft: frames stay local, status shows "not published: <reason>", retried on the next run.
- The daily workflow's own push has no rebase, and the app will now push to `main` during its ~64 min window. A rejected
  push would silently lose the day's committed scan. So the daily AND midday workflow commit steps get a bounded
  `git pull --rebase` retry (was "deferred hardening"; now required, in MM-002). Tested against a local bare repo.

## Task deltas
- MM-002 (Codex): add `--record-market-motion` (orthogonal to `--run-kind`): writes a `daily_full` frame with provenance
  `live` (CI, when `--run-kind daily-full`) or `local` (any other run); `--run-kind daily-full` implies it. It does NOT
  touch pick-history unless `--run-kind daily-full` (existing behaviour). Frame rows = every qualified buy (rank order) +
  an outcome row for every ticker in `tracked_tickers(load_frames())` that is not qualified this run (`outcome_point`).
  Session date from SPY's last bar. Fail-soft, before the email. Workflow: stage `data/market_motion/`, add artifact path,
  and rebase-retry push for BOTH workflows. Files: run_optimized_scan.py, both workflows, tests.
- MM-004 (Codex): as specified, plus session date from SPY, `is_data_current` guard, no push (publishing is MM-006).
- MM-006 (Codex): publisher (plumbing algorithm above) + scheduler + settings (`data/market_motion_settings.json`, gitignored,
  master switch default OFF, `publish_to_github` default ON) + status/run-now endpoints. Approval gate satisfied for
  building it; enabling remains the user's click.
- MM-003 (Claude): backfill now also targets `data/market_motion/snapshots/legacy_report/`.
