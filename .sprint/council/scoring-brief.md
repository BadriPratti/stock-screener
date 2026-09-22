You are participating in a full Engineering Council (HARD-classified: this changes what a live financial screening tool
recommends to a real user with real money on the line). Do NOT modify any file except the single output file named
below. Do not run any script that fetches live network data or takes more than a few minutes — read-only investigation
of the repository and its existing recorded data only, unless explicitly told otherwise below.

Repository: /Users/badripratti/Desktop/stock-screener. NEVER open, list, or reference the directory `position/` (real
brokerage account data).

## The user's request (their words, from this session)
"we need to revisit the scoring algorithm because it kind of sucks right now" — then, asked to be specific, picked
(multi-select): "Too rewarding of distance-from-SMA, not real strength" AND "Fundamentals block feels disconnected".

## Mandatory first read
.sprint/council/scoring-data/FACTS.md — verified facts, numbers, and file:line citations gathered by the sprint lead
BEFORE any of you were invoked. Read it fully. It includes real (if 7-weeks-stale) correlation data from this repo's
own backtest history, and a CONFIRMED finding that the walk-forward backtest never tests fundamentals at all
(scripts/walk_forward_backtest.py:224 passes fundamentals=None unconditionally). Then independently verify the claims
in FACTS.md against the actual code/data yourself — it is data, not something to take on faith, and if you find it
wrong, say so with evidence.

## Also read
- src/screening/signal_engine.py (full score_buy_signal, ~lines 96-711): the current formula, its weights, and the
  code comments explaining the last reweighting pass and citing correlation numbers.
- scripts/component_correlation_analysis.py: the tool used to justify the current weights (broad-pool, unrestricted
  correlation of each of the 7 top-level components vs forward returns).
- scripts/walk_forward_backtest.py and scripts/backtest_critic.py: full walk-forward simulation + before/after drift
  comparator, built specifically so a scoring change can be validated as a real improvement before trusting it.
- data/backtest_history/walk_forward_*.json (the 6 real recorded runs, all from 2026-08-04): read at least 2-3 of
  them directly yourself (jq/python), don't just trust the table in FACTS.md.
- src/screening/phase_indicators.py: where distance_from_50sma/distance_from_200sma/slope_50/slope_200 actually come
  from (phase_info), since these feed both score_buy_signal's trend_score AND, separately, the Positions view's
  add-on/trim guidance language quoted at the end of FACTS.md.
- The positions view's own add-on-candidate copy (search "Add-on candidate" / "classic continuation add point" in the
  codebase) — a apparent internal inconsistency FACTS.md flags: elsewhere in this same app, "pulled back closer to a
  rising 50 SMA without breaking it" is described as a GOOD add-on signal, while distance_component in score_buy_signal
  gives FEWER points the closer a stock sits to its 50 SMA. Reconcile or explain this, don't just note it.

## What you must actually determine (not just opine about)
1. Is the user's complaint #1 ("too rewarding of distance-from-SMA, not real strength") correct? distance_component is
   only ONE of three pieces inside trend_score (distance / slope / breakout+over-extension penalty), and no existing
   tool in this repo measures its correlation with returns SEPARATELY from the other two — only the blended trend_score
   (r=0.196 in the largest recorded sample, per FACTS.md) exists today. You cannot answer this question with existing
   data alone. Design (and if time/scope allows, actually build and run against real recent data) a finer-grained
   correlation check that isolates distance_component, slope_component, and the breakout/over-extension pieces from
   each other, so the actual predictive value of "distance from SMA" specifically can be measured, not assumed.
2. Is complaint #2 ("fundamentals block feels disconnected") correct, and why has it never been backtested? Is
   fetching real point-in-time historical fundamentals for a walk-forward test even feasible with what this repo
   already has (src/data/fundamentals_fetcher.py, src/data/git_storage_fetcher.py, data/fundamentals_cache/)? If yes,
   what would it take to actually wire real fundamentals into scripts/walk_forward_backtest.py so this 35-point block
   can finally be validated instead of assumed? If genuinely infeasible for point-in-time correctness (e.g. fundamentals
   data source has no historical/as-of capability, only "current"), say so plainly and propose the best available
   alternative (e.g. reduce the block's weight until it can be validated, or find a different proxy that IS testable).
3. Given 1 and 2, and the instability already visible in entry_score's own correlation across sample sizes (FACTS.md:
   0.37 at n=25 shrinking to 0.025 at n=200 with a 5000-stock universe, and flipping sign between two identical-params
   runs), is the CURRENT weighting (35 trend / 35 fundamental / 25 entry / 10 rr / 10 rs / 5 volume / 5 vcp) actually
   defensible right now, or should weights on untested/unstable components (fundamentals, entry_score, vcp_bonus) be
   provisionally reduced until better-validated, with the freed points redistributed to whatever the fresh, corrected
   analysis shows actually predicts returns? Do not propose a number you cannot justify from real data (existing or
   newly gathered here).
4. rs_score (r=-0.213) and volume_score (r=-0.171) show NEGATIVE correlation with forward returns in the largest
   recorded sample. Investigate WHY: mean-reversion in the specific window tested, a bucket/threshold definition
   problem in how rs_score/volume_score are computed, multicollinearity with other components, or genuine noise (n=200
   trades, one 9-month window, one specific market regime — SPY's regime during Aug 2026 matters here). Do not treat a
   negative sign as automatically meaningful without checking these alternatives.
5. Practical validation path: given the existing tooling (component_correlation_analysis.py, walk_forward_backtest.py,
   backtest_critic.py) was BUILT for exactly this kind of change, what is the concrete, lowest-risk sequence to (a) get
   a fresh, non-stale correlation reading (today's data is 7 weeks old), (b) test any proposed reweighting against a
   walk-forward simulation BEFORE it goes live, and (c) roll it out safely (e.g. log both old and new scores side by
   side for some period before switching what's actually shown/recommended, so a bad change is caught before it
   affects a real recommendation)? This is a live tool a real person is using for real trade decisions RIGHT NOW —
   treat "ship an unvalidated reweighting" as the highest-severity risk in this whole investigation.
6. Anything else you find that a careless read of "reweight some numbers" would miss — edge cases, look-ahead bias
   risks in the backtest itself, whether 200 trades over one 9-month window is even enough data to trust ANY of these
   correlations at the precision implied by weights like "25 points" vs "10 points", multicollinearity between
   components (e.g. does entry_score partially double-count what trend_score's distance_component already measures?).

## Constraints
- This is HARD/high-stakes: prioritize being RIGHT and CITING REAL EVIDENCE over being fast. If you cannot verify a
  claim with real data in the time available, say "unverified" rather than asserting it.
- Propose a plan (what to build/measure/change and in what order), not a finished reweighted formula — a real
  algorithm change needs fresh validation data this council does not yet have, and must not ship on guesses.
- No emoji. Do not modify signal_engine.py, walk_forward_backtest.py, or any other production file — investigation and
  a written plan only.
- Give a concrete task breakdown at the end (owner suggestion Claude/Codex/Antigravity, dependencies, acceptance
  criteria) for a HARD-classified /sprint-build that would actually execute this safely.

Write your full analysis to the single output file named for you below. Also print a short summary to stdout.
