# Claude independent analysis - Live packed opportunity chart (written BEFORE reading Codex/Antigravity output)

## Central finding
The request sounds like a chart change, but the chart is the last 20% of the work. Three things must exist first, and none do today:
1. There is no stored history of buy signals. `buy_signals` are regex-parsed from the human text report (`dashboard.py:parse_scan_file`), and the report only details the top 50 (`run_optimized_scan.py:151` `buy_signals[:50]`) out of 364-479. The pick-history ledger deliberately tracks only shortlist/top20. So "the stocks it viewed before should still be there" has nothing to read from.
2. The ledger's whole vocabulary is "one recorded session per ET day". Intraday frames need a different granularity that must not leak into the daily consistency badges.
3. "Every 2 hours" is not what the scanner does or what GitHub cron delivers: a full scan is ~63 min, and scheduled runs have started 4-5 hours late every day since 2026-08-31.

## What actually moves intraday (important to be honest with the user)
The scanner scores on daily bars (phase from 50/200 SMA on daily closes). Inside a trading day only the partial current bar changes, so RS vs SPY and volume-related score parts drift slightly; Phase/entry-quality flip rarely. The visible motion of a 2-hour cadence is therefore modest jitter plus occasional entries/exits at the threshold, NOT dramatic movement. The dramatic, real motion is across days (5 recorded full sessions already exist). Design for both: the time axis is "frames" (daily-close frames plus intraday frames), and the replay works well even with one frame/day.

## Recommended architecture
### Data: a new "signal frame" ledger, separate from the daily consistency ledger
- New module `src/screening/signal_frames.py` + directory `data/pick_history/signals/<ET-date>/<HHMM>Z-<kind>.json` (inside the already-whitelisted `data/pick_history/**` .gitignore rule, so no new gitignore trap). `pick_history.py` stays untouched: `_RUN_KINDS`, snapshot_path, compute_history, badge semantics, and their 74 tests do not move.
- A frame = {schema_version, frame_id, generated_at, session_date_et, kind: "full"|"focus"|"backfill", market_open: bool, scoring_version, universe_scope, points: columnar-ish list of {t: ticker, rs, sp (score % of max, 1 dp), eq (entry quality enum), ph (phase), px (price)}}. Compact keys: ~430 rows x ~55 bytes = ~25 KB/frame raw, ~6-8 KB gzipped in git.
- Full daily scan writes ALL buy signals (not just the top 50) as a `full` frame (one code path: the scanner already holds the full `buy_signals` list in memory, so no text parsing is needed going forward). Backfill: the 5 existing full reports give `backfill` frames of top-50 only (`detail_limited: true`), used as history with an honest caption.
- Chart universe rule: a ticker's point in frame f = its buy signal in f; absent = dropped out at f. "Memory" = a ticker's last-known position persists as a fading ghost for K frames after it drops, plus a short trail of its previous K positions.

### Cadence: two-tier, NOT "12 full scans a day"
- Tier 1 (existing): the daily full scan, unchanged (LLM agents, email, canonical outputs, ledger).
- Tier 2 (new): an intraday FOCUS pass every ~2 hours during market hours: re-score only the tickers that were buys in the latest full frame (~430; plus optionally top20), price-only, NO LLM agents, NO email, NO canonical report/latest files, NO breadth/regime recomputation (breadth over a buys-only set would read ~100% Phase 2 and corrupt the regime; reuse the daily regime). `process_batch_parallel(tickers, ...)` already accepts an explicit ticker list (`run_optimized_scan.py:~440`), so a `--run-kind intraday-focus --tickers-from-ledger` mode is a small, contained change. Estimated 12-15 min/run vs 63 (430/1973 of the work, no fundamentals refresh).
- Known limitation to state to the user: a stock that first qualifies at 1pm is invisible until the next full scan. (Option for later: widen the focus set to near-misses, needs the full frame to also store 55-70 scorers.)
- Runs/day: 3 intraday (e.g. 15:07, 17:07, 19:07 UTC = 11:07/13:07/15:07 EDT or 10:07/12:07/14:07 EST; off-minute avoids the top-of-hour queue that causes the 4-5 h delays; still best-effort) + 1 daily full = 4 frames/day. Cron is UTC and DST-blind: pick UTC hours that stay inside 9:30-16:00 ET in both EDT and EST.
- Public repo => runner minutes are free; the real budget is data-provider rate limits and git churn. Push contention is real (three workflows all push to main with no rebase-before-push): add `git pull --rebase` retry in the commit step of every workflow that writes, or write intraday frames on a separate data branch. Commits/day: ~4 (+ existing midday). Bytes: ~8 KB gz x 4 x 250 = ~8 MB/yr in .git. Fine. Working-tree retention: keep all `full` frames; prune `focus` frames older than 30 days to their last-of-day.
- Alternative to put to the user: a local scheduler in the Mac app. Rejected as default (only runs while the Mac is on; produces local-only frames that diverge from the repo) but the existing `/api/jobs` runner could expose a manual "Refresh focus now" button cheaply.
- Market closed/holiday: focus run checks SPY's last bar date == today ET; if not, exits 0 without writing a frame (no fake motion).

### Chart: replay, not redraw
- New ES module `static/js/components/signal-map.js` owns its own Chart instance/lifecycle using the global `Chart` (charts.js is a classic script, but a module can read its globals); minimal edits to `market.js` (swap `_renderBuyOpportunityChart`). Keeps charts.js/ui-helpers.js/dashboard.css contention with the unbuilt chart-modal sprint to a few lines.
- Pure math in `static/js/core/signal-frames.js` (unit-testable in plain Node): `buildTracks(frames)` -> per-ticker ordered positions; `interpolate(track, t)` with enter/exit (radius/alpha ramp) and ghost handling; `pickWindow(frames, n)`; `easing`.
- Rendering: one dataset of interpolated current positions mutated in place per requestAnimationFrame with `chart.update('none')`, plus a custom Chart.js plugin drawing (a) a faded trail per ticker limited to the last K=3 positions and only full-length for hovered/pinned tickers, (b) hollow ghost markers for dropped-out tickers. Chart.js built-in per-point animations are avoided: they allocate per-property animators and get janky past ~1k points. Budget: <= ~600 live points + <= ~600 ghosts + <= ~1,800 trail segments per frame, all canvas primitives; fine at 60 fps.
- Controls: play/pause, step +/-, scrub slider labelled with the frame's ET timestamp and kind ("Sep 18 close" vs "Sep 18 13:07"), speed 1x/2x/4x, "Live" jumps to the latest frame. On a new frame arriving while viewing the newest frame, animate the transition; if the user scrubbed back, do not yank them.
- `prefers-reduced-motion: reduce` (unhandled anywhere today): no auto-play, transitions become instant frame steps, trails on hover only.
- Accessibility: canvas gets `role="img"` + aria-label summary; a visually-adjacent "Table view" toggle lists the current frame's points (the existing Buy Signals table already does this for the top 50; extend to the frame).
- Encodings: color = entry quality (existing palette), size = volume_ratio or score, alpha = recency, ghost = hollow. Axis: Y currently spans 81-93% for the top 50; with all buys it spans ~56-93%, which is better; keep axes fixed across frames (autoscale during playback makes everything appear to jump) and set from the union of the window.

## Tasks (proposed)
- T1 Claude/Codex: `signal_frames.py` (schema, atomic write, load, retention) + tests (mirrors pick_history.py rigor).
- T2 Codex: scanner wiring: full scan emits a full frame (all buys) fail-soft; `--run-kind intraday-focus` with ticker-list input, no LLM/email/canonical/breadth; market-open guard; tests.
- T3 Claude: backfill from the 5 git-history reports as `backfill` frames (reuse scripts/backfill_pick_history.py machinery), idempotent.
- T4 Codex: `/api/signal-frames?window=` compact payload + `/api/scans` untouched; warnings for skipped files.
- T5 Codex: workflow `intraday_focus.yml` (own concurrency group, off-minute cron, rebase-before-push retry, artifact) + hardening of the two existing commit steps. DO NOT dispatch without user approval.
- T6 Claude: `core/signal-frames.js` pure math + tests.
- T7 Antigravity/Claude: `components/signal-map.js` + CSS + controls + reduced-motion + a11y table; wire into market.js.
- T8 Claude: verification, visual check plan, final report.
Sequencing: T1-T6 touch no file the chart-modal plan touches (Python, workflows, new JS files). T7 edits market.js/dashboard.css and must run AFTER the chart-modal frontend lands (or before it starts) - never concurrently.

## Risks
partial/failed runs (fail-soft, never block email), duplicate tickers, scoring_version changes between frames (mixed-version frames must not be interpolated as continuity), NaN/None rs, two frames within the same minute (frame_id collision -> same-id replace), DST cron drift, weekend/holiday empty frames (skip), 2k-point hit-testing cost, stale fetch races (token guard), payload growth (window cap + last-of-day thinning beyond 5 sessions), and the user expectation gap (modest intraday motion).
