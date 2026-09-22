# Verified facts for the "revisit the scoring algorithm" investigation (extracted by the sprint lead; treat as data)

## User's specific complaints (their own words, from a clarifying question)
1. "Too rewarding of distance-from-SMA, not real strength" — a stock's score can drop several points just from pulling
   back toward its 50-day average even though nothing about the underlying trend broke (observed live today: ET's score
   dropped ~5 points and CF's dropped ~2-6 points purely from `distance_from_50sma` shrinking, both still Phase 2).
2. "Fundamentals block feels disconnected" — suspects the 35-point fundamentals sub-score doesn't actually relate to how
   a stock performs afterward.

## Current formula (src/screening/signal_engine.py:96-711, score_buy_signal, 125 pts total)
- trend_score: 35 pts (was 40). Sub-pieces: distance_component (up to 15, linear in %-above-50/200-SMA, capped at
  15%/20%), slope_component (up to 15, linear in 50/200-SMA slope), breakout bonus (+10, from detect_breakout), an
  OVER-EXTENSION PENALTY (-10 if >30% above 50SMA, -5 if >20%). NOT reported as a single number anywhere except the
  aggregate trend_score — no sub-component correlation data exists for distance vs slope vs breakout individually.
- fundamental_score: 35 pts (was 40). revenue trend (15) + EPS trend (15) + inventory (10; capped), OR falls back to a
  flat "score += 10 # Placeholder - assume neutral" (signal_engine.py ~line 376) when fundamentals data is missing/absent.
- entry_score: 25 pts (was 5 — the single largest reweight of any component).
- rr_score: 10 pts (was 15). rs_score: 10 pts (unchanged). volume_score: 5 pts (was 10). vcp_bonus: 5 pts (unchanged).
- Comment at signal_engine.py:109-115 justifies these weights by citing scripts/component_correlation_analysis.py
  "2 independent historical windows... entry_score +0.40/+0.48 correlation... BY FAR the strongest predictor found".

## What the actual recorded backtest data shows (data/backtest_history/walk_forward_*.json, all dated 2026-08-04,
## now 7 weeks stale) — READ BY THE LEAD DIRECTLY, verify independently before trusting
| file (time) | universe_size | months | top_n | trades | entry_score r | fundamental_score r |
|---|---|---|---|---|---|---|
| 222245/222257 | 40 | 2 | 5 | 25 | 0.326 | None |
| 222412 | 40 | 2 | 5 | 25 | 0.369 | None |
| 225018 | 250 | 9 | 10 | 200 | 0.101 | None |
| 225131 | 250 | 9 | 10 | 200 | -0.038 | None |
| 225921 | 5000 | 9 | 10 | 200 | 0.025 | None |

Observations (mine, verify independently — do not just trust these):
- entry_score's own correlation SHRINKS TOWARD ZERO (and once flips negative) as universe size / sample size grows: the
  strongest reading (0.37, cited-ish by the code comment) comes from the SMALLEST, noisiest test (25 trades, a
  40-stock universe, 2-month window) — a classic small-sample overfitting shape. The two 250-universe runs with
  IDENTICAL params (250/9/10) disagree in SIGN (0.10 vs -0.04), which by itself says the true signal is within noise
  at that sample size. None of the 6 real runs reproduces the code comment's cited "+0.40/+0.48 across both windows" —
  that number likely comes from component_correlation_analysis.py's own separate methodology (it tests ALL
  Minervini-qualified Phase 2 stocks in a ~400 pool over 30 days, not the walk-forward's actual smaller traded set),
  not from these walk_forward_backtest.py runs. This discrepancy between the two measurement methods is unresolved
  and worth reconciling — they may not be measuring the same thing (component_correlation_analysis.py: unrestricted
  population; walk_forward's own component_correlations: only the already-selected top_n trades, i.e. a
  restriction-of-range sample that will mechanically show weaker/noisier correlations for anything that also
  influenced selection — so the two are not simply comparable, but neither is a fabricated number).
- fundamental_score's correlation is `None` in EVERY recorded run, with no exception. `pearson()` returning None means
  zero/undefined variance in the sample. The scanner's own fallback code (signal_engine.py ~376: "score += 10 —
  Placeholder - assume neutral") suggests the walk-forward backtest may never be supplying real point-in-time
  fundamentals data at all, so every trade gets the SAME placeholder fundamental_score — meaning the 35-point
  fundamentals block has literally never been backtested with real, varying data. This directly supports the user's
  suspicion: not "disproven to matter" but "never actually tested."
- `component_correlation_analysis.py`'s own docstring (lines 5-10) already states, BEFORE any of this reweighting:
  "We already know the blended total barely correlates with returns (r ~ -0.1 to +0.12)" — i.e. even the CURRENT
  post-reweighting composite score's real-world predictive power is acknowledged, in this repo's own comments, to be
  weak. The most recent full-composite reading: `score` r = 0.061 (225921 run, largest/most representative sample).
- rs_score (10 pts, relative strength vs SPY — literally the x-axis of the new Buy Opportunity Map) shows a NEGATIVE
  correlation with forward returns in the largest sample: r = -0.213. volume_score also negative: r = -0.171. Neither
  was flagged or reweighted based on this; both deserve scrutiny (sign might mean mean-reversion, or a scoring-bucket
  definition problem, or genuine noise — needs investigation, not assumption).
- All six recorded runs are from a single day (2026-08-04), all exploratory/tuning runs, none since. Today is
  2026-09-22 (~7 weeks later); market conditions have moved (SPY was $759-773 across the frames we've seen this week).
  Any conclusion should be re-validated on FRESH data, not solely the stale Aug 4 numbers above.

## Adjacent, already-built infrastructure relevant to this investigation
- scripts/component_correlation_analysis.py: per-component correlation across a broad (default 400-stock) pool over N
  days (default 30), independent of the walk-forward trade-selection process — the right tool to re-run fresh, and to
  EXTEND to break trend_score into its sub-pieces (distance/slope/breakout/over-extension) since that's exactly where
  the user's "distance-from-SMA" complaint lives and no existing tool measures it at that granularity.
- scripts/walk_forward_backtest.py + scripts/backtest_critic.py: full walk-forward simulation + before/after drift
  comparator (reads two walk_forward_*.json files, diffs component_correlations) — built specifically to validate a
  scoring change is a real improvement, not a regression, before trusting it. USE THIS to validate any proposed change.
- src/screening/market_motion.py (today's sprint): the persistent tracker map/leaderboard is a live, growing dataset
  of real qualified/dropped/re-qualified stocks with dated scores/RS per ticker — a second, independent, forward-
  looking source of ground truth that will accumulate real outcomes over the coming weeks, complementary to the
  historical walk-forward backtest.
- The Positions view already surfaces real add-on/trim guidance derived from phase_info distance-from-SMA
  ("Add-on candidate — Pulled back to the rising 50 SMA... without breaking it, still in a confirmed Phase 2 uptrend
  and not yet an extended winner... a classic continuation add point") — i.e. elsewhere in this SAME codebase, "closer
  to the 50 SMA after a pullback" is treated as a BUY-MORE signal (continuation entry), the opposite of how
  score_buy_signal's distance_component treats it (closer to the SMA = fewer points, further above = more points, up
  to a penalty past 20-30%). These two are not necessarily contradictory (initial entry vs. add-on timing are
  different decisions) but the inconsistency is worth the council explicitly reconciling or explaining.

## CONFIRMED: the walk-forward backtest never tests fundamentals at all
scripts/walk_forward_backtest.py:224 calls:
    score_buy_signal(..., fundamentals=None, vcp_data=None)
literally, unconditionally, for every single historical trade. This is not a data-availability edge case — it is the
walk-forward backtest's permanent behavior. So `fundamental_score` and `vcp_bonus` are two more 0-pt-variance columns
in every recorded run (fundamental_score confirmed None above; vcp_bonus likely the same, verify). The 35-point
fundamentals block and the 5-point VCP bonus — 40 of 125 total points, 32% of the score — have NEVER been backtested
with real data by this repo's own validation tooling. Any defense of their current weight is untested, not proven.
