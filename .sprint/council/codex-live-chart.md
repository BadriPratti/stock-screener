# Engineering Council: Live Buy Opportunity Map

## Executive decision

The interpretation is directionally right, but two parts need reframing.

First, “keep every stock seen” should mean **retain a real, timestamped state history and show recent dropped-out stocks as clearly stale ghosts**, not leave every old dot looking like a current buy forever. An absent ticker is not automatically a failed opportunity: it may have fallen below the buy threshold, failed a hard eligibility gate, not been evaluated because a run was partial, or not have belonged to a light scan's candidate set. The data contract must preserve those distinctions.

Second, “every two hours” should not mean four more full-universe scans. A full scan currently takes about 63 minutes, so four intraday full scans would consume about 252 scan-minutes per trading day before the existing daily run, hammer data providers, and still arrive unpredictably on GitHub's delayed cron. The right architecture is:

1. Keep the existing daily full-universe scan as the discovery/seed run.
2. Persist a new slim, machine-readable market-motion snapshot containing every qualified buy, not just the report's top 50.
3. During market hours, re-score a bounded rolling candidate roster locally four times per day, with no LLM agents and no email.
4. Drive a time-scrubbable chart from those immutable snapshots. Animate only between recorded states; never synthesize market observations.
5. Leave the daily pick-history ledger and all of its “N scans” semantics unchanged.

This should be approved as two decisions: the data/chart feature, and separately the scheduler/cadence. Scheduling must not be enabled without the user's explicit approval.

## Repository diagnosis

### What the chart actually shows today

`buildBuyOpportunityPoints()` maps one report's parsed `buy_signals` to `x = rs` and `y = score / max_score * 100`, dropping non-finite inputs (`static/js/views/market.js:144-154`). The card then constructs one canvas and immediately calls the global `renderMarketScatterChart()` with only those points (`static/js/views/market.js:156-175`). The renderer destroys any prior chart, builds one scatter dataset, colors it by entry quality, and fixes every radius at 5.5 (`static/js/charts.js:129-176`). It has no history or update controller.

The source is lossy. `parse_scan_file()` regex-parses the human report (`dashboard.py:93-106`, `dashboard.py:172-229`). `save_report()` serializes details for only `buy_signals[:50]`, then writes all remaining buys as ticker symbols with no score or RS (`run_optimized_scan.py:144-164`, `run_optimized_scan.py:249-255`). The five verified full scans contain 364-479 buys apiece, but only 50 plottable rows each; the five top-50 lists contain just 84 distinct tickers, with 25 present in every scan (`.sprint/council/live-chart-data/FACTS.md:3-8`; `.sprint/council/live-chart-data/buy_signal_facts.txt:1-10`). Therefore no frontend-only change can make this chart both full and historically honest.

The current “Live” loop also does not update the opportunity map. It refreshes Market news, momentum, and per-row price histories, but never reloads scan data or calls the scatter renderer (`static/js/views/market.js:70-78`). The shared live timer is polling every 90 seconds (`static/js/core/refresh.js:1-18`), while the app-wide sync pulls Git every five minutes and can reroute/re-render the whole view (`static/js/dashboard.js:57-70`, `static/js/dashboard.js:97-103`). A new scan currently causes a replacement, not point motion.

There is also a race to fix: `loadMarketScan(path)` starts two requests and checks only that the current view is still Market; it does not confirm that the response still belongs to the latest selected path (`static/js/views/market.js:308-318`). Quickly changing the dropdown can let an older response paint last.

### The score axis is not intrinsically broken

The observed 81-93% Y range is a **top-50 selection artifact**, not evidence that normalized scanner score is useless. The buy engine's real threshold is 60 and its maximum is 125 (`src/screening/signal_engine.py:690-710`), so the full qualifying population can in principle span 48-100% of maximum. The report parser supplies `max_score` from the printed `Score: n/max` text (`dashboard.py:172-185`), but the in-memory buy-signal object itself does not return `max_score`; it returns `score`, `risk_reward_ratio`, and `details.rs_slope` under different names (`src/screening/signal_engine.py:699-711`). A sidecar writer must normalize those names explicitly instead of dumping objects and hoping the UI schema matches.

## 1. Data design

### Recommended source of truth

Add a **separate market-motion snapshot store**, not a `buy_signals` member on the daily pick-history ledger and not runtime re-parsing of text files.

Suggested layout:

```text
data/market_motion/
  snapshots/
    daily_full/
      2026-09-18T170746Z.json
    intraday_rescore/
      2026-09-18T133500Z.json
      2026-09-18T153500Z.json
```

The stored unit is one ticker's state at one completed run. One possible v1 shape is:

```json
{
  "schema_version": 1,
  "run_id": "2026-09-18T153500Z-intraday-rescore",
  "run_kind": "intraday_rescore",
  "generated_at": "2026-09-18T15:35:00Z",
  "session_date_et": "2026-09-18",
  "scoring_version": "v1",
  "score_model": {"max_score": 125, "buy_threshold": 60, "rs_metric": "rs_slope_20"},
  "scope": {
    "mode": "rolling_candidates",
    "requested": 500,
    "analyzed": 493,
    "failed": 7,
    "completed": true,
    "candidate_source_run_ids": ["..."]
  },
  "coverage": {"kind": "complete_for_scope"},
  "points": [
    {
      "ticker": "SUN",
      "evaluation": "qualified",
      "score": 112.5,
      "max_score": 125,
      "rs": 0.355,
      "phase": 2,
      "entry_quality": "Good",
      "current_price": 78.34,
      "stop_loss": 74.12,
      "rr_ratio": 5.6,
      "volume_ratio": 2.31,
      "rank": 1,
      "top_reason": "Good Stage 2: 4.6% above 50 SMA"
    },
    {
      "ticker": "XYZ",
      "evaluation": "not_qualified",
      "score": 57.2,
      "max_score": 125,
      "rs": 0.018,
      "drop_reason": "below_buy_threshold"
    },
    {
      "ticker": "ABC",
      "evaluation": "error",
      "error_code": "price_data_unavailable"
    }
  ]
}
```

The schema should store slim chart/tooltip fields only. Do not persist full `details`, all reasons, fundamentals, Reddit payloads, or agent output in every intraday snapshot. The full scanner already enriches every signal with earnings and social/insider lookups before building the Top 20 (`run_optimized_scan.py:518-579`); repeating and persisting those payloads is unrelated to chart motion.

The daily full run should emit `daily_full` market-motion data from the in-memory `buy_signals` after sorting (`run_optimized_scan.py:467-491`). That sidecar contains every qualified buy. It must also write an outcome for previously tracked names that were analyzed but no longer qualify. For a completed full-universe scan, absence from the qualified list can be treated as a dropout only if the scanner confirms that ticker was actually analyzed. For a partial or light run, an unobserved ticker is `not_evaluated`, never `not_qualified`.

This is why merely storing an array of buys is insufficient: it can remember entrances but cannot honestly explain exits.

### Why the daily pick ledger must stay separate

The existing ledger has a deliberately narrow contract:

- Only `shortlist` and `top20` are valid list names, and only `daily_full` is an accepted run kind (`src/screening/pick_history.py:19-25`).
- Its canonical key is `snapshots/<run_kind>/<session_date>.json`, so a same-date write replaces the same file (`src/screening/pick_history.py:211-245`).
- Same-day downgrade protection assumes a later empty run is probably broken rather than a real market change (`src/screening/pick_history.py:256-295`).
- Streaks, appearances, and denominators are computed over recorded daily sessions (`src/screening/pick_history.py:365-425`, `src/screening/pick_history.py:464-496`).

Putting 4-12 intraday runs into that store would either overwrite all but one run or silently redefine “5 scans” from five market sessions to roughly one day. That would break the semantics the approved pick-history plan explicitly locked down: daily full only, Friday-to-Monday consecutive, and denominator equal to actual recorded sessions (`.sprint/SPRINT_PLAN.md:32-42`, `.sprint/SPRINT_PLAN.md:77-85`).

Use a separate module, proposed as `src/screening/market_motion.py`, with timestamp keys and its own validator. Do not add `intraday_rescore` to `pick_history._RUN_KINDS`. Existing `/api/pick-history` responses and tests remain byte-for-byte semantically compatible.

### Backfill of the five existing full scans

Backfill exactly the five named full reports in `buy_signal_facts.txt`. A one-time script should call the existing text parser or a purpose-built strict parser, normalize the 50 detailed rows, and write five `daily_full` motion snapshots with:

```json
"provenance": "legacy_report",
"coverage": {
  "kind": "top50_only",
  "qualified_total": 479,
  "located_points": 50,
  "unlocated_qualified": 429
}
```

The additional bare tickers may be retained as `qualified_unlocated` records for a text/table count, but they must not receive invented coordinates and must not be placed at `(0, 0)`. The existing frontend already correctly omits rows with missing/non-finite score or RS (`static/js/views/market.js:144-153`); backfill should preserve that honesty.

Do not reparse old reports on every API request. Parsing is appropriate once for migration; future snapshots should be JSON written atomically by the scanner. The text report is a human presentation whose cap and labels can change.

### API and compatibility

Add new endpoints rather than changing `/api/scan`:

```text
GET /api/market-motion?limit=20&before=<run_id>
GET /api/market-motion/latest
```

The series response should include ordered snapshot summaries plus points, warnings for skipped/corrupt files, `latest_run_id`, and `has_more`. Default to 20 snapshots; cap at 60. Keep `/api/scans`, `/api/scan`, and `/api/pick-history` shapes unchanged so current consumers continue to work.

The new API should accept opaque validated run IDs, not arbitrary filesystem paths. The current `/api/scan` accepts any existing `path` and passes it to `parse_scan_file()` (`dashboard.py:780-793`); this is an existing local-file disclosure risk in the Flask surface. Do not copy that pattern. As a separate hardening item, constrain `/api/scan` to files resolved beneath `SCAN_DIR` or use scan IDs from `/api/scans`.

## 2. Visual design: dense but legible

The chart should show two meanings, not one undifferentiated cloud:

- **Current qualified points:** solid fill, 5 px radius, 1 px categorical border.
- **Recently dropped points:** hollow muted ring at the last valid coordinate, 3 px radius, with tooltip text “Last qualified <timestamp>; latest result <reason>.” Never count these in the visible “current opportunities” total.
- **Not evaluated/error:** do not visually mark as dropped. Keep the last point with a small stale/error indicator in its tooltip and accessible table.

Recommended encoding:

- X remains RS slope versus SPY. Always include zero and retain the existing zero-line concept (`static/js/charts.js:135-154`).
- Y remains normalized score, but use the whole model domain, initially 45-100%, with a visible threshold line at 48% (60/125). Do not auto-zoom to 81-93%. If a future model changes max or threshold, take both from snapshot metadata.
- Color remains entry quality (`Good`, `Extended`, `Poor`), because that is already the chart's established categorical meaning (`static/js/charts.js:129-133`, `static/js/charts.js:168-175`). Dropped points are neutral gray; color must not imply a stale point is currently Good.
- Do not use size for score; Y already encodes score. Reserve radius changes for active/ghost/selected state.
- Fix scale bounds across all snapshots loaded into the current replay, including zero plus 5% padding on X. Axes that rescale every frame make stationary data appear to move.

Concrete density budget:

- Persist all valid rows; decimation is a rendering concern, not data loss.
- Render all current qualifiers while the current count is at or below 750. The observed 364-479 full-scan range fits comfortably.
- Allow at most 450 recent ghosts, for a hard default of 1,200 dot elements. If more exist, retain all current points, then choose ghosts deterministically by recency and most recent score. The accessible table still exposes every stored record.
- Draw a maximum of three trail segments per currently qualified ticker. Tail alpha newest-to-oldest: 0.35, 0.20, 0.10; line width 1 px. Do not turn every historical observation into a separate permanent dot.
- Age fade for ghost snapshots: `alpha = max(0.10, exp(-0.55 * age_in_snapshots))`, giving approximately 0.58, 0.33, 0.19, and 0.11 after one through four observations.
- Labels: selected ticker, hovered ticker, top 10 scores, and top 10 largest moves since the prior snapshot, deduplicated and capped at 20. Everything else is tooltip/table discoverable. Hundreds of always-on ticker labels would defeat “packed” readability.

The 1,200-dot/three-tail budget is a starting performance contract, not a claim already proven by this repository. Benchmark it on the target Mac at 500, 1,200, and 2,000 points. Acceptance should be median frame time below 33 ms during a 30 fps tween at the default budget, with automatic trail/label suppression before dropping current points. A 2,000-point fixture is required as a degradation test even though the normal renderer will decimate ghosts.

The current click behavior assumes every point has a row in the current Buy table; `_highlightBuyRow()` silently returns when it cannot find one (`static/js/views/market.js:177-193`). A ghost or replayed historical point usually will not have such a row. Clicking it should open/focus the chart's accessible detail row, while clicking a currently selected report's active point may retain the table jump.

## 3. Motion and replay

### Rendering approach

Use **requestAnimationFrame interpolation over one stable, ticker-keyed dataset**, with a small custom Chart.js plugin only for trails, threshold/zero lines, and capped labels.

Do not rely solely on Chart.js built-in transitions. Built-in point animation is index-oriented; entering, exiting, filtering, and reordering hundreds of tickers can animate one ticker from another ticker's prior index. A keyed controller should build the union of the two adjacent snapshots and interpolate by ticker:

```text
qualified -> qualified: interpolate x and y
enter:                  stay at target x/y; radius/alpha 0 -> active
exit:                   stay at last real x/y; active -> hollow ghost
error/not_evaluated:    hold last real x/y; mark stale, do not call it exit
```

Fabricating a starting coordinate for a new ticker would imply movement that was never observed, so entry should bloom in place. Similarly, an exit should fade at its last valid observation, not fly to a made-up edge.

The controller should target 30 fps and an 800 ms default tween. On each frame, mutate the stable data array and call `chart.update('none')`; benchmark whether this remains within the 33 ms budget. If it does not, reduce ghosts/trails first. The plugin can use the current scales to draw three-segment tails without multiplying interactive datasets.

The replay controls are Play/Pause, Previous, Next, an `<input type="range">`, current timestamp, “Live” state, and playback speed 0.5x/1x/2x. The slider is ordinal over **recorded snapshots**, not wall-clock hours. A Friday close to Monday open or a holiday gap advances to the next real observation without synthesizing weekend frames. Display the actual elapsed gap beside the timestamp.

### Classic-script lifecycle

`charts.js` is deliberately a classic script with globals, while Market is a native ES module (`.sprint/SPRINT_PLAN_CHART_MODAL.md:20-24`; `static/js/views/market.js:1-18`). Keep that boundary:

- `static/js/charts.js` exposes a plain global `renderMarketMotionChart(...)`, never `export`.
- A new ES module such as `static/js/core/market-motion.js` owns snapshot normalization, keyed interpolation, replay state, and fetch sequencing.
- `market.js` owns view policy and controls.
- The Chart.js renderer owns only canvas behavior and reports point selections back to the module.

Extend `_destroyChart(canvasId)` so it first calls any registered motion-controller cleanup: cancel the active animation frame, remove media-query listeners, clear pointer state, then destroy the Chart instance (`static/js/charts.js:31-38`). Do not destroy/recreate the chart on every replay frame. Create once, update in place, and destroy only on view teardown or a genuine canvas replacement. This also preserves the full-screen modal plan's destroy-before-recreate invariant (`.sprint/SPRINT_PLAN_CHART_MODAL.md:21-27`).

### Reduced motion

The stylesheet currently animates the row pulse, live dot, spinner, and toast transition with no `prefers-reduced-motion` override (`static/css/dashboard.css:203-208`, `static/css/dashboard.css:353-359`, `static/css/dashboard.css:380-383`). Add both layers:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
```

In JavaScript, check `matchMedia('(prefers-reduced-motion: reduce)')`. When true, set tween duration to zero, disable autoplay and tails, and make step/scrub updates immediate. Listen for preference changes while the view is open and unregister that listener during `_destroyChart` cleanup.

### New live snapshots

Poll only `/api/market-motion/latest` from the existing guarded 90-second Market loop. Use an `AbortController` or monotonically increasing request generation so stale responses cannot paint. If `latest_run_id` changes:

- If the user is at the live edge, append the snapshot and tween all points together over 800 ms.
- If the user has scrubbed into history, do not yank the slider forward. Show “New snapshot available” and let Return to live perform the transition.
- If the new snapshot is incomplete/invalid, show a warning and retain the last completed frame.

The app-wide five-minute Git sync currently reroutes the view after a pull (`static/js/dashboard.js:61-70`, `static/js/dashboard.js:97-103`). To preserve motion state, either dispatch a `stock-data-updated` event that Market handles in place or retain the last rendered frame in the motion controller and seed a recreated chart from it. The event approach is cleaner, but it means `static/js/dashboard.js` joins the shared-file sequence.

## 4. Intraday ledger without breaking daily consistency

The new series should have these semantics:

- `run_kind = daily_full` is a discovery snapshot emitted once by the existing full scan.
- `run_kind = intraday_rescore` evaluates only the rolling tracked roster.
- Filename key is an immutable UTC timestamp/run ID, not ET date.
- ET session date is metadata used for grouping/display, not uniqueness.
- A retry produces a new run ID unless it is explicitly resuming the same atomic run. Never silently replace an earlier real observation.
- Only `scope.completed = true` snapshots become replay endpoints. Failed jobs may write a small failure manifest/log, but not a false empty market frame.

The candidate roster should be the union of the latest daily full buy set and recently qualified intraday names, deduplicated by normalized ticker and capped at 500 for the first release. When the daily seed has more than 500 buys, keep every daily signal in the `daily_full` snapshot but choose the intraday roster deterministically: top 400 by current score plus up to 100 recent dropouts/movers. Surface “500 of N tracked intraday” in the UI.

Daily consistency remains defined only by `data/pick_history/snapshots/daily_full/YYYY-MM-DD.json`. Twelve intraday observations neither increase `sessions_available` nor alter a “4/5 scans” badge. The current aggregation already uses the produced daily snapshot list as its denominator (`src/screening/pick_history.py:393-425`) and suppresses score deltas across different scoring versions (`src/screening/pick_history.py:442-453`). Market motion should adopt the latter rule too: place a divider at a scoring-version change and do not tween score across it.

Retention recommendation:

- Default replay API: last 20 snapshots, approximately five trading days at four per day.
- Local raw retention: 60 trading sessions, at most 240 intraday snapshots.
- Long-term: retain one daily close/discovery snapshot per trading day; prune older raw intraday snapshots locally.
- Never describe a missing snapshot as a dropout. Show a coverage gap.

The existing daily coverage helper counts missing weekdays and therefore treats market holidays as missing (`src/screening/pick_history.py:341-345`). Do not reuse that function for intraday coverage. Until an exchange calendar is added, report elapsed time and explicit run failures, but do not claim a holiday was a failed run.

### Storage and Git-growth estimate

A compact 500-row motion snapshot budgeted at 150-200 bytes per row is roughly 75-100 KB plus small metadata. At four runs per trading day that is about 300-400 KB/day and 76-101 MB per 252-session year. Git compression may help repeated keys, but Git history does not shrink when old files are deleted.

By contrast, the current human report includes up to seven reasons and fundamental text for each detailed signal (`run_optimized_scan.py:163-247`). Scaling that rich format from 50 to roughly 500 records would be on the order of ten times a full report and is the wrong persistence format.

Recommended policy: raw intraday snapshots are local data by default and not committed to `main`. If cross-machine Git persistence is explicitly desired, batch the day's four immutable files into one end-of-day commit: one intraday commit/day, about 252/year, instead of four commits/day, about 1,008/year. This changes commit count, not blob bytes. An external artifact/object store would be more appropriate for indefinite high-frequency retention, but none exists in the current repository.

Also account for the current sync conflict behavior: on a blocked fast-forward it can discard changes under `data/` before retrying (`dashboard.py:624-648`). Local motion storage must be excluded from that cleanup or placed in an app-data location outside the Git-managed output tree. Otherwise the scheduler could create history that Sync later destroys.

## 5. Scheduling recommendation, pending user approval

### Recommended cadence

Use four regular-session snapshots at approximately 09:35, 11:35, 13:35, and 15:35 America/New_York on trading days. This is “about every two hours,” gives an opening and near-close state, and is a clear four-runs/day contract. Do not run overnight or on weekends. A holiday-aware calendar is preferable; without one, a no-market-data result must be a skipped run, not an empty snapshot.

Each intraday run should:

1. Load the latest candidate roster, maximum 500.
2. Fetch fresh price/benchmark data and re-run the deterministic technical/buy scoring needed for score, RS, phase, entry quality, and risk fields.
3. Reuse cached daily fundamentals where the model requires them; record their `as_of` age.
4. Skip earnings, Reddit, insider, Congress, fundamentals-auditor, catalyst-sentiment, shortlist construction, and all email notifications.
5. Atomically publish one slim snapshot only after the scoped roster finishes.

This needs a dedicated command such as `run_intraday_rescore.py`, not `run_optimized_scan.py --test-mode`. Test mode samples 100 random universe names (`run_optimized_scan.py:430-434`), so consecutive samples are not a coherent moving population. The existing midday workflow is correspondingly a random sample and is excluded from canonical history (`.sprint/council/live-chart-data/FACTS.md:15`).

The light-run duration must be benchmarked. The existing 100-stock sample takes about 0.8 minute (`.sprint/council/live-chart-data/FACTS.md:15`), so a rough linear estimate for 500 is about four minutes; budget an SLO of at most ten minutes, or 16-40 compute-minutes/day for four runs. This is an estimate, not a measured promise. Four full scans would be 252 minutes/day; adding the existing 63-minute daily scan yields 315 minutes/day, or 26.25 runner-hours per five-day week. That is wasteful even though public-repository hosted minutes are currently unmetered; provider rate limits and agent/API costs remain real (`.sprint/council/live-chart-data/FACTS.md:11-18`).

### Local versus GitHub scheduler

Prefer a local macOS scheduler for this feature, with the dashboard displaying scheduler state. A LaunchAgent is more reliable than an interval owned only by the browser/webview process, but it runs only while the Mac is awake and logged in. The dashboard already has a subprocess job framework (`dashboard.py:323-361`, `dashboard.py:379-445`) and scan job entry point (`dashboard.py:449-461`), so it can expose Run now/status without inventing another process-control system. The current scan watchdog is 45 minutes (`dashboard.py:351-361`), ample for a ten-minute rescore.

GitHub cron is a poor source of two-hour motion here. The daily schedule documents consistent 4-5 hour delays (`.github/workflows/daily_screening_git_storage.yml:3-10`), and the verified runs demonstrate the same (`.sprint/council/live-chart-data/FACTS.md:13-17`). Delayed jobs can bunch or skip and make nominal timestamps misleading.

If the user nevertheless chooses GitHub:

- Use a separate `screening-intraday` concurrency group with `cancel-in-progress: true`; the freshest light run matters more than queued stale ones. Do not share the daily group, because GitHub retains only one pending run and a light run could displace a pending daily run (`.sprint/council/live-chart-data/FACTS.md:16`).
- Keep `screening-daily` unchanged and give it priority. Add a preflight that skips intraday work while daily is active rather than letting both hit providers.
- Add `workflow_dispatch` for testing and manual recovery.
- GitHub cron has no reliable ET timezone behavior. Either maintain separate EDT/EST UTC schedules with an ET guard, or trigger hourly in a safe UTC envelope and let the script run only at the four intended ET slots. The current midday file already acknowledges the fixed-UTC one-hour DST drift (`.github/workflows/midday_quick_scan.yml:3-8`).
- No `ANTHROPIC_API_KEY`, email credentials, or email calls in the intraday command. The full command currently sends a start email for every non-test run and a report email at the end (`run_optimized_scan.py:397-409`, `run_optimized_scan.py:691-697`), so merely adding a run kind without gating notifications would spam users.
- Batch one day's files into one push where possible. Both current workflows independently push to `main` without rebase (`.github/workflows/daily_screening_git_storage.yml:158-195`; `.github/workflows/midday_quick_scan.yml:55-80`), and repository facts confirm a collision can reject one push (`.sprint/council/live-chart-data/FACTS.md:16-17`). For an intraday data-only commit, fetch current `main`, rebase the data commit, retry a bounded number of times, and retain an artifact on failure. Do not retrofit that riskier push path into the daily publishing workflow in the same task.

Approval prompt should be explicit: “Enable four local market-hours re-scores per trading day, no LLM and no email, retaining 60 sessions locally?” GitHub scheduling should be a separate alternative, not silently enabled.

## 6. Sequencing and file ownership

The full-screen chart modal plan is unbuilt and touches `charts.js`, `market.js`, `dashboard.css`, and `ui-helpers.js` among other files (`.sprint/SPRINT_PLAN_CHART_MODAL.md:37-44`). The earlier pick-history plan already warns that shared frontend sprints must be built one at a time (`.sprint/SPRINT_PLAN.md:99-101`). The live chart adds the same collision plus potentially `dashboard.js`.

Recommended order:

1. Finish and merge the full-screen chart modal, or explicitly defer it. Do not leave it half-built while starting this frontend.
2. Build market-motion schema, scanner output, backfill, and API; these can proceed without touching modal frontend files.
3. Freeze the Market redesign while one owner implements the entire live-chart frontend stack.
4. Resume broader Market redesign only after the live-chart frontend and tests land.

No two tasks below assign the same production file concurrently. New files can proceed in parallel only where dependencies permit; shared files have one sequential owner.

## 7. Risks, edge cases, and required tests

### Data correctness

- **Duplicate tickers:** normalize uppercase/trim, first/best rank wins, and reject duplicates after normalization. The daily ledger already uses this defensive approach (`src/screening/pick_history.py:61-97`).
- **NaN/Infinity/None:** sanitize before JSON, validate finite coordinates, and preserve `null` rather than coercing to zero. The chart's current finite checks are the correct baseline (`static/js/views/market.js:144-153`).
- **Partial run:** publish no replay endpoint unless `scope.completed` is true. Preserve the prior state as stale, not dropped.
- **Same timestamp/retry:** use an explicit run ID and atomic replace only for a retry of that same run; otherwise retain both ordered observations.
- **Scoring version:** no score tween/delta across versions. Show a divider and reset trails.
- **Ticker changes/aliases:** v1 treats symbols as identities, matching the existing plan's explicit limitation (`.sprint/SPRINT_PLAN.md:103-110`). Store an optional future `instrument_id` field so alias reconciliation can be added later.
- **Corporate actions:** RS/score may jump after splits or bad adjusted data. Mark unusually large moves and retain source timestamps; do not smooth them away.
- **Stale fundamentals:** intraday technical motion using cached fundamentals must expose `fundamentals_as_of`; otherwise apparent real-time conviction is overstated.

### Time and sessions

- Slider positions are recorded observations, so weekends and holidays create gaps, not empty frames.
- Use UTC for ordering and ET for market-session labels.
- Test DST spring/fall dates and duplicate local clock labels.
- Do not use naive weekday-gap logic for holiday failure detection.

### Frontend and performance

- Abort/generation-guard all scan-series and latest-snapshot fetches; test out-of-order completion.
- Cancel requestAnimationFrame on route change, canvas replacement, and chart destroy.
- Keep fixed replay-domain scales to avoid fake motion from rescaling.
- Benchmark 500, 1,200, and 2,000 records; verify deterministic decimation and that all active points survive it.
- A new snapshot while paused in history must not move the scrubber.
- A new snapshot at live edge must animate from the exact displayed state.
- Resize during a tween and repeated route entry/exit must not produce “Canvas is already in use.”
- Reduced-motion mode must perform zero-duration updates and no autoplay.

### Accessibility

A canvas alone is not an accessible data view. Add:

- A real heading and concise current/ghost/coverage summary.
- Keyboard-operable Play/Pause, step buttons, range slider, and speed control.
- An `aria-live="polite"` timestamp/status updated only when the selected snapshot changes, not every animation frame.
- A sortable text table containing ticker, current status, score, RS, entry quality, first/last seen, and latest change. It must include records omitted by visual decimation.
- Non-color distinctions: solid versus hollow, labels, and textual legend.
- No emoji in UI copy, snapshots, labels, tests, or status badges. Existing reports contain emoji, but the frontend already has a `cleanEmoji` path for reasons (`static/js/views/market.js:371-380`); the new sidecar's `top_reason` should be normalized at write time.

### Test style

Follow current repository conventions:

- Pytest unit tests for schema validation, atomic writes, retention, backfill coverage, API empty/corrupt/partial behavior, and scheduler output policy. Existing scan run-kind tests already use a small truth table and temporary directories (`tests/test_scan_run_kind.py:13-30`, `tests/test_scan_run_kind.py:43-79`).
- Flask contract tests for pagination, opaque ID validation, path containment, and backwards-compatible `/api/scan` and `/api/scans` responses. Existing API tests assert response keys and sort order (`tests/test_pick_history_api.py:192-214`).
- Plain Node tests for pure interpolation, enter/exit states, decimation, version boundaries, stale-response guards, reduced-motion, labels, and HTML/ARIA. The current scatter characterization test uses mocked globals plus dynamic module import (`tests/js/test_market_scatter_points.js:1-49`).
- Static/source tests for the classic-script/global boundary and `_destroyChart` cleanup.
- Do not make wall-clock animation tests timing-fragile: inject a clock/requestAnimationFrame adapter and advance deterministic timestamps.

## 8. Likely misses and challenges to the request

1. **More dots are not automatically more information.** Showing 2,000 old observations as peers of 400 current opportunities would make stale names look actionable. The meaningful “packed” design is all current signals plus bounded, visibly aged memory and short trails.
2. **A point is a ticker state, not an observation cloud.** At a selected time there should be at most one interactive dot per normalized ticker. Historical observations belong in its tail/replay, not as unrelated overlapping dots.
3. **Movement can be misleading if inputs are stale.** If fundamentals update daily but technicals update intraday, the UI should say so. “Real-time score” is inaccurate; “intraday re-score using fundamentals as of <time>” is honest.
4. **The selected report and replay time can diverge.** Give the opportunity map its own timestamp controls and show “Return to live.” If selecting an old report pins the chart to the nearest snapshot, state that explicitly; do not silently show today's moving chart over an old report's tables.
5. **Current auto-sync can destroy local state.** The five-minute reroute and `data/` conflict cleanup need deliberate integration, not just a polling endpoint.
6. **The current scan API path contract should not be replicated.** New history work is an opportunity to use safe IDs and add containment to the old route.
7. **A local schedule is operational state.** Show last success, next intended run, candidate count, duration, and last error. Otherwise “every two hours” will silently stop when the Mac sleeps.
8. **Do not infer causality from interpolated frames.** Tweening is a visual transition between measurements, not evidence of the path a stock took during the two-hour gap. The UI should label snapshots and avoid a continuously advancing market clock.

## Recommended task breakdown

### DATA-001 — Market-motion schema and store

- **Owner:** Claude
- **Files:** new `src/screening/market_motion.py`, new `tests/test_market_motion.py`
- **Dependencies:** none
- **Acceptance:** validates schema/run kinds/evaluation statuses; normalizes duplicate tickers; rejects non-finite values; atomic timestamped writes; corrupt files skipped with warnings; completed-only reader; UTC ordering and ET labels; retention selection; daily pick-history tests unchanged.

### DATA-002 — Full-scan sidecar writer

- **Owner:** Codex
- **Files:** `run_optimized_scan.py`, new focused scanner tests or `tests/test_scan_run_kind.py`
- **Dependencies:** DATA-001
- **Acceptance:** every in-memory qualified buy is written, not top 50; canonical field normalization maps `details.rs_slope` to `rs`, `risk_reward_ratio` to `rr_ratio`, and supplies model max/threshold; prior tracked names receive qualified/not-qualified/error outcomes; atomic write occurs only after a completed scan; daily pick ledger behavior and email output remain unchanged.

### DATA-003 — Legacy five-scan backfill

- **Owner:** Antigravity
- **Files:** new `scripts/backfill_market_motion.py`, new `tests/test_backfill_market_motion.py`, five generated `data/market_motion/snapshots/daily_full/*.json` files
- **Dependencies:** DATA-001
- **Acceptance:** explicit five-report manifest; 50 located points per snapshot; verified header totals 364-479; coverage marked `top50_only`; no invented coordinates; rerun is byte-identical; midday/sample reports excluded.

### DATA-004 — Read API and route hardening

- **Owner:** Claude
- **Files:** `dashboard.py`, new `tests/test_market_motion_api.py`, focused additions to current scan API tests
- **Dependencies:** DATA-001, DATA-003
- **Acceptance:** paginated empty-shape API; latest endpoint; corrupt/partial snapshot warnings; opaque ID/path containment; additive behavior only; existing `/api/scans`, `/api/scan`, and `/api/pick-history` contracts pass unchanged.

### RUN-001 — Intraday re-score command

- **Owner:** Codex
- **Files:** new `run_intraday_rescore.py`, new tests; minimal shared helpers extracted only if necessary
- **Dependencies:** DATA-001, DATA-002
- **Acceptance:** deterministic rolling roster capped at 500; all requested names get qualified/not-qualified/error/not-evaluated outcomes; no LLM, social, insider, Congress, shortlist, start email, or report email; no canonical daily latest or pick-history writes; atomic completed snapshot; measured runtime recorded.

### RUN-002 — Scheduler choice and implementation

- **Owner:** Antigravity
- **Files:** only after approval: local scheduler/LaunchAgent integration and status UI backend, or new `.github/workflows/intraday_rescore.yml`; tests appropriate to selected option
- **Dependencies:** RUN-001; **blocked on explicit user approval**
- **Acceptance:** four intended ET slots; market-day/no-data guard; Run now; last/next/status; no overlap with daily provider work; no email/LLM secrets; recoverable failure; exact run/commit/storage budget documented. If GitHub is chosen, DST guard, concurrency, bounded rebase/retry, and artifact retention are tested.

### UI-001 — Pure replay model

- **Owner:** Claude
- **Files:** new `static/js/core/market-motion.js`, new `tests/js/test_market_motion.js`
- **Dependencies:** DATA-004
- **Acceptance:** ticker-keyed interpolation; honest enter/exit/error states; fixed-domain calculation; three-tail construction; deterministic 1,200-point budget; scoring-version boundary; injected clock; reduced-motion zero-duration behavior; stale-response suppression.

### UI-002 — Shared frontend integration

- **Owner:** Codex, as the sole writer for this task
- **Files:** `static/js/views/market.js`, `static/js/charts.js`, `static/css/dashboard.css`, `static/js/dashboard.js`; touch `static/js/core/ui-helpers.js` only if the merged modal API requires it
- **Dependencies:** UI-001, DATA-004, and the chart-modal sprint either fully merged or explicitly deferred
- **Acceptance:** one persistent chart instance per canvas; play/pause/step/scrub/live controls; 800 ms live tween; ghost/trail/label policy; current report versus replay timestamp clearly separated; auto-sync updates in place; `_destroyChart` cancels all resources; reduced-motion CSS and JS; no emoji; no stale row-jump behavior.

### UI-003 — Accessible table and performance verification

- **Owner:** Antigravity
- **Files:** new frontend tests and benchmark fixtures only; production-file findings return to UI-002 owner rather than concurrent edits
- **Dependencies:** UI-002
- **Acceptance:** keyboard/ARIA audit; table includes all records including decimated ghosts; 500/1,200/2,000 fixtures; default median frame below 33 ms on target Mac or documented lower automatic budget; canvas lifecycle stress test; full plain-Node and pytest suites pass.

### RELEASE-001 — End-to-end council gate

- **Owner:** Claude
- **Files:** tests/docs only unless a defect is handed back to the owning task
- **Dependencies:** all approved tasks
- **Acceptance:** one daily discovery plus four light local re-scores observed on a market day; incomplete run does not create a false dropout; new live snapshot animates at live edge and waits while scrubbed back; pick-history denominator and streak badges are unchanged; no workflow/email/LLM activation occurred without user approval.

The frontend ownership rule is absolute: chart modal, live chart, and Market redesign do not have concurrent writers in `market.js`, `charts.js`, `dashboard.css`, `ui-helpers.js`, or `dashboard.js`.
