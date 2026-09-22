# Sprint: Revisit the scoring algorithm

STATUS: PLAN ONLY. Nothing built, committed, or pushed. HARD classification — this changes what a live tool
recommends with real money. **The plan's own conclusion is: do not reweight yet.** Read the whole thing before
deciding whether to build anything.

## Request (user's own words)
"we need to revisit the scoring algorithm because it kind of sucks right now" — asked to be specific:
"Too rewarding of distance-from-SMA, not real strength" + "Fundamentals block feels disconnected".

## Council process
Full HARD council. Codex's independent, read-only investigation (`.sprint/council/codex-scoring.md`, 254 lines) is
the backbone of this plan — it went well beyond my own `.sprint/council/scoring-data/FACTS.md` groundwork,
independently re-verifying my numbers, correcting two of them, and finding several NEW concrete defects by
actually reading `signal_engine.py`'s arithmetic line by line and emulating it against the real 2,600-file
fundamentals cache. Antigravity's independent pass is still running (relaunched once after a headless
permission failure); I'll fold in anything material it adds. Given the quality and depth of Codex's analysis, I'm
not waiting on Antigravity to report the core findings to the user.

## Executive conclusion (from the investigation, not a guess)
**The current point weights (35 trend / 35 fundamental / 25 entry / 10 R:R / 10 RS / 5 volume / 5 VCP) are not
defensible as empirically validated — but neither is any specific replacement number.** The honest next step is
to build proper measurement infrastructure and validate a change in shadow mode before it ever affects a real
recommendation, not to guess a new set of weights right now.

## What's actually true about the two complaints

**"Too rewarded for distance from SMA" — confirmed as a real behavior, not confirmed as wrong.** The formula does
give more points the farther a stock sits above its 50/200-day average (up to a cap, then a penalty past 20-30%),
while a *different* part of the same score (entry quality) gives slightly more credit for being close to the 50
SMA. So yes, a stock can lose total points from a pullback even though nothing about its trend broke — verified
directly in the arithmetic (`signal_engine.py:188-253`) and matches what we watched happen live today with ET and
CF. But no test in this repo has ever isolated "distance from SMA" from the other things bundled into the same
sub-score (trend slope, breakout detection) to check whether distance itself predicts anything. So the mechanism
is real; whether it's actually *wrong* is unverified either way.

**"Fundamentals block feels disconnected" — confirmed, and worse than suspected.** The walk-forward backtest that
was used to justify the current weights literally never passes real fundamentals data to the scorer
(`scripts/walk_forward_backtest.py:221-225` — hardcoded `fundamentals=None`). Every historical trade got the exact
same placeholder value. The 35-point fundamentals block has never been tested with real, varying data. On top of
that, Codex found the block can silently exceed its own advertised cap — emulating the real formula against all
2,600 files in `data/fundamentals_cache/` showed 10.8% of tickers would score *above* 35 points (up to 43.75),
because the component math doesn't match the stated maximum.

## New, concrete bugs found (not part of the original complaint, found by reading the code)
1. **The breakout detector may never actually fire as intended.** `detect_breakout` checks `current_price >
   base_high`/`pivot_high`, but those highs are computed over a window that includes the current price itself —
   so that comparison can structurally never be true. The only breakout path that can actually trigger is a
   simpler 50-SMA cross. The "breakout" component's comments don't match what it tests.
2. **The old code comment citing "+0.40/+0.48 correlation" for entry_score can't be reproduced or audited.** The
   script that supposedly produced it doesn't save its inputs, doesn't use a fixed random seed, and samples a
   different pool every run. There's no artifact in this repo proving that number was ever real in the form cited.
3. **Sample size doesn't support the current precision.** With correct statistics (accounting for the fact that
   200 "trades" really come from only 20 distinct entry dates, not 200 independent events), the underlying
   evidence can't reliably tell a 25-point weight apart from a 10-point weight. The current weights imply more
   precision than the data backing them can support.
4. **RS and volume showing negative correlation with returns is probably not what it looks like.** Deep diagnostics
   (rank correlation, trimming outliers, controlling for other factors) show the negative signal mostly disappears
   once a single 220%-return outlier trade is handled properly — it looks much more like noise and a scoring-cap
   problem (RS is clipped 0-10; volume only looks at 5 sessions) than genuine evidence that momentum hurts.
5. Several backtest-methodology issues that would make ANY reweighting untrustworthy until fixed: the historical
   universe is today's stock list applied to past dates (survivorship bias), trades are filled at the same closing
   price the signal was computed from (look-ahead), and stop-losses fill at the exact stop price even on a gap
   down (unrealistically optimistic).

## Recommended path (phased; do not skip ahead to "just change the numbers")
- **Phase A — Freeze & instrument.** Don't touch the live weights yet. Add logging that records every
  sub-component (distance, slope, breakout, entry subparts, fundamentals subparts) separately, without changing
  what the score shows. Fix the breakout-window bug and the fundamentals cap-overflow bug as behavior-neutral
  fixes, versioned separately from any weight change.
- **Phase B — Fresh, reproducible measurement.** Re-run the correlation analysis with fixed seeds, saved inputs,
  and the sub-components broken apart (so "distance from SMA" can finally be measured on its own, not blended into
  trend_score). Today's data is 7 weeks stale; get a current reading.
- **Phase C — Real fundamentals in the backtest.** This turns out to be partially possible: this repo's own git
  history has fundamentals-cache snapshots going back months, which can be used to reconstruct what was actually
  known at each past date (never using a snapshot from after the fact). Wire that into the walk-forward backtest
  so the fundamentals block can finally be validated instead of assumed.
- **Phase D — Point-in-time walk-forward with a locked test set**, using proper statistics (not a single raw
  correlation number) to compare the current formula against any candidate change.
- **Phase E — Shadow mode before it ever ships.** Compute both the old and any new score side by side for a
  while, visible only as a labeled comparison, never switching what's actually recommended, until it's proven
  better on data it wasn't tuned on.

## Tasks (for a future /sprint-build — NOT started)
| Task | Owner | Depends on | Done when |
|---|---|---|---|
| SC-001 Experiment manifest + frozen-input runner | Codex | — | Two baseline runs from the same frozen inputs produce identical results |
| SC-002 Log every sub-component separately (no behavior change) | Codex | SC-001 | Distance/slope/breakout/entry/fundamentals all individually recorded and sum back to today's score |
| SC-003 Fix the breakout-window bug and the fundamentals-cap bug | Codex | SC-002 | Each has a unit test; versioned as a behavior change, kept separate from any weight change |
| SC-004 Point-in-time fundamentals from git history | Codex | SC-001 | Automated check rejects any data dated after the decision point; coverage report by ticker/date |
| SC-005 Statistical plan, locked BEFORE looking at results | Claude | SC-002 | Time windows, metrics, and thresholds for "did it work" are written down before any test runs |
| SC-006 Fresh component-level correlation study | Codex | SC-002, SC-005 | Saved, reproducible data; distance-from-SMA finally measured on its own |
| SC-007 Point-in-time walk-forward, baseline vs. any candidate | Codex | SC-003, SC-004, SC-006 | Uses a locked, untouched final time period never used to pick the candidate |
| SC-008 Shadow-mode logging in the live app (no effect on real recommendations) | Antigravity | SC-007 | Both scores visible side by side; the real Shortlist/Top20 still uses only the current formula |
| SC-009 Review + go/no-go | Claude | SC-008, matured shadow data | Written sign-off against the criteria from SC-005, not "one number went up" |

## Guardrails
Nothing here changes `signal_engine.py`'s live weights or the buy threshold. No commit/push without your go-ahead.
This plan explicitly recommends AGAINST shipping a reweighted formula based on guesses, even well-informed ones.

---

## Amendment 1 (2026-09-22) — Antigravity's independent pass folded in

Antigravity completed its own full read-only investigation (`.sprint/council/antigravity-scoring.md`, 406
lines) after two earlier failed attempts (a headless permission denial, then a silent process death — both
environment issues, not analysis issues; the third attempt completed cleanly). I spot-checked its numeric table
against the raw backtest JSON directly — it matches exactly, so its transcription is trustworthy.

It independently reached the same two core conclusions as Codex (both complaints are real; current weights
aren't defensible; don't ship a guessed reweight) via a mostly-separate line of analysis. What it adds:

- **Quantified the pullback penalty precisely.** A stock moving from 15% to 1% above its 50-day average loses
  ~8.16 points from the trend block and gains back only ~3.50 from the entry-quality block — a net loss of about
  4.66 points, which matches almost exactly what we watched happen live to ET (~5 points) and CF (2-6 points)
  today. This turns the earlier "confirmed behavior" finding into an exact, reproducible number.
- **A fundamentals-data feasibility matrix** across every data source this repo has (the fundamentals cache,
  yfinance, Financial Modeling Prep's free tier, the SEC-filing auditor) — each is infeasible for point-in-time
  historical backtesting for a different concrete reason (look-ahead bias via filing-date lag, insufficient
  quarters of history, free-tier rate limits too low for 200 trades x 4 calls, or too slow/costly at $0.05-0.15
  per trade). Its verdict is more pessimistic than Codex's git-history-snapshot approach (see reconciliation
  below), but sharpens exactly which shortcuts are NOT available.
- **A concrete, illustrative weight-testing matrix** (e.g. trend 45-50, fundamentals 10-15, entry 10-15,
  explicitly labeled "provisional proposal for TESTING," not a ship-it number) — a useful starting grid for
  Phase B/C rather than starting from nothing.
- **A new structural defect**: several score components use hard step-function cliffs (e.g. the extension penalty
  jumps by 5 points exactly at 20% and by another 5 at 30%) that can make two nearly-identical stocks land on
  opposite sides of a 5-10 point jump from a fraction of a percent of price movement. Worth smoothing into
  continuous functions alongside the other behavior-neutral fixes in Phase A.
- **Quantified why 200 recorded trades isn't enough**: they come from only ~18-20 independent entry-date cycles
  within one 9-month window (one market regime), and recommends at least ~500 trades spanning multiple regimes
  (bull/bear/sideways) before trusting any weight to the precision the current numbers imply.

### One real disagreement between the two agents, and how I resolved it
Antigravity's Phase-4 table treats `rs_score`'s -0.213 correlation as likely statistically real (naive p=0.002
from the standard Pearson formula) and proposes tuning it (e.g. "with slope smoothing"). Codex went further and
actually re-ran the same relationship through rank correlation and outlier-trimmed statistics, and found the
signal collapses toward zero once a single extreme winning trade is handled properly (winsorized r=-0.062,
Spearman rho=-0.073). Antigravity's OWN later qualitative section (its "Hypothesis B: Heavy-Tailed Return
Outliers") independently arrives at essentially the same place Codex did once it works through the actual win/loss
distribution — it just didn't go back and correct its earlier table's naive p-value framing to match. **I'm
siding with the more rigorous, outlier-robust analysis (Codex's, which Antigravity's own later reasoning
effectively agrees with): treat RS/volume's negative sign as likely noise/definition-artifact until a fresh study
using rank and winsorized statistics from the start says otherwise — not as an established, real negative
predictor.** This is exactly why SC-006 must compute Spearman and winsorized correlations as first-class outputs,
not an afterthought.

### Reconciling the fundamentals-feasibility disagreement
Antigravity assessed the on-disk fundamentals cache as one fixed current-day snapshot (correctly infeasible on
its own for historical testing). Codex found something more specific: this repo's GIT HISTORY holds many dated
commits of that same cache directory going back months, effectively giving a real (if partial, recent-only)
sequence of point-in-time snapshots that can be walked commit-by-commit. These aren't actually contradictory —
Codex's technique is more sophisticated than what Antigravity evaluated, and is worth trying for SC-004, with
Antigravity's broader infeasibility findings kept as the honest fallback if git-history coverage turns out too
sparse to be useful once someone actually tries it.

### Task ownership correction
Antigravity's own task breakdown assigns itself several implementation/test-execution tasks. Per this session's
established, hard-learned pattern (Antigravity's headless mode cannot reliably run python/tests and has now
failed outright twice on this very topic), **Antigravity stays in a review/audit role only** for the actual
build — the task table below overrides its self-assignment. Codex and Claude do all code/test/run work; Antigravity
reviews the diagnostic instrumentation (SC-002) and the fresh correlation results (SC-006) for statistical
soundness before they're trusted, which is exactly the kind of task it's proven good at (this document and its
predecessor).

Updated task table (supersedes the table in the base plan above — SC-001 is unchanged, already dispatched):

| Task | Owner | Depends on | Done when |
|---|---|---|---|
| SC-001 Experiment manifest + frozen-input runner | Codex | — | *(dispatched; in progress)* |
| SC-002 Log every sub-component separately (genuinely behavior-neutral: score/is_buy unchanged, proven by regression test) | Codex | SC-001 | Distance/slope/breakout/entry/fundamentals all individually recorded in `details`; today's live score is bit-for-bit unchanged for every existing test case |
| SC-002-REVIEW Antigravity audits SC-002's instrumentation for correctness/completeness | Antigravity | SC-002 | Written sign-off or findings list; review only, no code changes by Antigravity |
| SC-003 Fix the breakout-window bug, the fundamentals-cap bug, AND smooth the discontinuous step-function cliffs (Antigravity's jitter finding) — all real, intentional behavior changes | Codex | SC-002 | Each has a unit test; every changed score is logged/diffed against the pre-fix formula; versioned separately from any weight reallocation (corrected from Amendment 1, which mislabeled cliff-smoothing as behavior-neutral — it isn't) |
| SC-004 Point-in-time fundamentals: try Codex's git-history-snapshot approach first | Codex | SC-001 | Coverage report by ticker/date; explicit go/no-go on whether coverage is dense enough to use, with Antigravity's feasibility matrix as the documented fallback if not |
| SC-005 Statistical plan, locked BEFORE looking at results (must specify Spearman + winsorized correlation as primary, not just raw Pearson, given the RS/volume disagreement above) | Claude | SC-002 | Time windows, metrics, and thresholds written down before any test runs |
| SC-006 Fresh component-level correlation study (>=400 stocks, current data, both raw and robust statistics) | Codex | SC-002, SC-005 | Reproducible saved data; distance-from-SMA finally measured on its own; resolves the RS/volume disagreement with real numbers instead of two agents' competing guesses |
| SC-006-REVIEW Antigravity audits SC-006's results for statistical soundness | Antigravity | SC-006 | Written sign-off; flags any remaining naive-Pearson-only conclusions |
| SC-007 Point-in-time walk-forward, baseline vs. any candidate (using Antigravity's provisional weight grid as a starting set of candidates to test, not a foregone conclusion) | Codex | SC-003, SC-004, SC-006 | Locked, untouched final time period never used to pick the candidate; hard acceptance gates written down in SC-005 |
| SC-008 Shadow-mode logging in the live app (no effect on real recommendations) | Claude | SC-007 | Both scores visible side by side; real Shortlist/Top20 still uses only the current formula |
| SC-009 Review + go/no-go | Claude | SC-008, matured shadow data | Written sign-off against SC-005's criteria, not "one number went up" |
