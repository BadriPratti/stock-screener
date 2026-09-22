# Engineering Council analysis: scoring algorithm

Date: 2026-09-22  
Classification: HARD; live financial recommendation path  
Scope: offline, read-only investigation of repository code and recorded data. No production code was changed and no network-backed analysis was run.

## Executive conclusion

The current weights are not defensible as an evidence-based allocation. That does **not** justify shipping a guessed replacement.

The first complaint is directionally correct about current behavior: inside the ordinary Stage 2 range, the composite still rewards being farther above the 50- and 200-day averages, even though its entry-timing subscore partly rewards the opposite. A controlled pullback can therefore lower the total while the trend remains intact. However, the historical artifacts do not contain the raw trend subcomponents, so there is no existing evidence that distance itself predicts returns. The correct conclusion is “behavior confirmed, predictive value unverified,” not “distance has been disproven.”

The second complaint is stronger. The walk-forward test always passes `fundamentals=None` and `vcp_data=None` (`scripts/walk_forward_backtest.py:221-225`). Every recorded trade consequently has the same 17.5-point fundamental value, and VCP is not even included in the walk-forward component schema (`scripts/walk_forward_backtest.py:58`). Thus the live formula reserves nominal weights of 35 and 5 points for blocks that this validation path has never tested. There are also defects in the stated fundamental weight: the implemented subparts can total 50 raw points, then are multiplied by 35/40, so the alleged 35-point block can actually contribute 43.75 points. The final 125 cap hides this over-allocation rather than fixing it.

The largest recorded run's negative Pearson correlations for RS and volume are real calculations but are not robust evidence of harmful predictors. On the saved 200 rows, RS/return is -0.213 and volume/return is -0.171. After 5/95 winsorizing returns they shrink to -0.062 and -0.070; Spearman correlations are -0.073 and -0.006; correlations with simply winning are +0.022 and +0.003. A 219.7% winner with RS score 4.03 and volume score 0 is one obvious source of leverage. The safest interpretation is “unstable magnitude association in a heavy-tailed, selected sample,” not established mean reversion.

Recommendation: freeze the displayed production formula, add behavior-neutral diagnostic logging, make the datasets reproducible and point-in-time correct, run a pre-registered component study plus nested walk-forward comparison, and only then choose weights. Candidate reductions for fundamentals, entry, and VCP should be evaluated in shadow mode as a grid; this council does not have evidence to select a new numeric weight.

## 1. Independent verification of FACTS.md

### Confirmed

- The advertised formula and comments are present at `src/screening/signal_engine.py:109-125`; the actual implementations are trend at `:171-253`, fundamentals at `:255-388`, volume at `:390-450`, RS at `:452-491`, risk/reward at `:499-561`, entry at `:563-644`, and VCP at `:646-688`.
- Trend's raw pieces are distance up to 15 (`signal_engine.py:188-194`), slope up to 15 (`:205-211`), breakout +10 (`:227-238`), and an extension penalty of -5/-10 (`:240-246`), followed by a 35/40 scale (`:248-253`). Only the aggregate is written to `details`.
- `classify_phase` calculates slopes from rolling SMAs and emits the two distances (`src/screening/phase_indicators.py:430-444`). The distance is current price relative to the SMA (`phase_indicators.py:224-236`).
- The broad-pool script measures only seven top-level components and passes no fundamentals or VCP (`scripts/component_correlation_analysis.py:38, 91-95`). It uses all Minervini-qualified rows and separately reports the >=60 subset (`:97-113, 128-152`). It cannot answer which trend subpart matters.
- The walk-forward call unconditionally passes both optional blocks as `None` (`scripts/walk_forward_backtest.py:221-225`). Saved trades all contain fundamental score 17.5; their fundamental correlations are null. This follows from the no-data raw score of 20 and the 35/40 scaling (`signal_engine.py:378-388`).
- The five substantive recorded correlations cited in FACTS.md match the JSON. The two earliest files are exact-result duplicates, and all six were generated on 2026-08-04.
- The largest recorded run has 200 trades, 20 entry dates, 179 unique tickers, score r=0.061, trend r=0.196, entry r=0.025, RS r=-0.213, and volume r=-0.171 (`data/backtest_history/walk_forward_20260804_225921.json`, `summary` and `component_correlations`).
- The add-on logic explicitly identifies a Phase 2 stock between the 50 SMA and 3% above it as a favorable continuation add point (`src/analysis/position_manager.py:195-210`).

### Corrections and qualifications

1. **The “placeholder 10” is not the missing-fundamentals fallback.** The +10 at `signal_engine.py:374-376` is a fixed profit-margin placeholder applied when a fundamentals dictionary exists. When the whole dictionary is absent, raw fundamental score is 20 and final score is 17.5 (`:378-388`). This distinction matters: 8.75 final points are constant even in the supposedly data-driven live block, while historical walk-forward rows get a different 17.5 constant.

2. **The two 250-universe runs do not have identical parameters.** They share universe size, period, top-N, and holding rules, but seeds are 42 and 43. Their sign disagreement is still evidence of universe-sample instability, but it is not a nondeterministic rerun of the same sample. The 222245 and 222257 files are the actual same-seed duplicate (`seed=7`) and have identical results.

3. **VCP is worse than a null-variance column in the current walk-forward report.** It is passed as `None`, excluded from `COMPONENTS`, and absent from saved trade objects (`walk_forward_backtest.py:58, 221-245`). The backtest critic also omits it (`scripts/backtest_critic.py:22-29`). It has no recorded correlation at all.

4. **The code's “two independent historical windows” evidence is not reproducible from saved artifacts.** `component_correlation_analysis.py` selects a new random pool without a seed (`:68-70`), saves neither rows nor output, and chooses a single as-of date per invocation (`:63-66`). The +0.40/+0.48 entry claims in `signal_engine.py:637-641` may have come from two console runs, but there is no repository artifact from which to audit samples, windows, or uncertainty.

5. **The broad-pool script's “point-in-time correct” claim is incomplete.** Price inputs are sliced at the as-of date, but it samples today's universe (`component_correlation_analysis.py:68-83`), creating survivorship/constituent bias for historical dates. It also relies on current provider history and does not persist the fetched dataset.

## 2. Complaint 1: distance from SMA versus real strength

### What the formula actually does

For a qualified Phase 2 stock, raw distance points are:

`min(15, max(0, distance50 / 15 * 10 + distance200 / 20 * 5))`

After the trend scale, the maximum contribution is 13.125 points. Within the uncapped region, each extra percentage point above the 50 SMA adds about 0.583 final points and each extra point above the 200 SMA adds about 0.219. Because a price move changes both distances, their effects are not independent.

Entry quality pushes partly the other way. Its SMA portion falls from 2 raw points near the 50 SMA to 1 at 20% above it, then is multiplied by five (`signal_engine.py:602-615, 637-644`). Holding other features fixed, that subtracts 0.25 final points per additional percentage point through the 0-20% range. The net local effect is nevertheless generally positive because the two trend distance terms outweigh it. The 52-week-high portion of entry quality also tends to reward a price that has already advanced (`:570-600`). This is why a pullback can lose total points even while earning a better entry-timing score.

There are discontinuities: moving from just above 20% to 20% or below removes the 4.375-point scaled extension penalty, and moving below 30% removes the larger 8.75-point penalty (`signal_engine.py:240-251`). The total relationship is therefore rising, capped, and discontinuously penalized—not a coherent “closer is better” or “farther is better” model.

### Reconciliation with add-on guidance

Initial breakout selection and adding to an existing profitable position are genuinely different decisions. A stock near a high may demonstrate leadership for an initial momentum screen, while a later low-volume pullback toward a rising average can offer a better add-on risk point. The contradiction is not that both concepts exist; it is that one unlabeled total score mixes:

- trend maturity/leadership (farther above averages, near a 52-week high),
- entry efficiency (closer to the 50 SMA and not extended), and
- breakout state,

then the UI treats the scalar as general buy quality. The add-on path makes the intended trade stage explicit; the main score does not. The safe design is to keep structural strength and setup/timing as separate displayed dimensions, or explicitly select an “initial breakout” versus “pullback/add-on” setup before ranking.

### An additional defect in the breakout term

`find_base_high` and `find_pivot_high` take maxima over windows that include the current close (`phase_indicators.py:189-218`). `detect_breakout` then requires `current_price > base_high` or `> pivot_high` (`:860-900`). Because callers pass the same latest close as `current_price`, those comparisons cannot be true. With VCP absent in both existing analyses, the only reachable breakout is the recent 50-SMA cross at `:902-908`. Thus the historical “breakout component” is not testing base/pivot breakout strength as its comments imply.

### Determination

The user's behavioral complaint is correct. The causal/predictive claim remains unverified. The saved trades contain only blended `trend_score`, not distances, slopes, breakout flags, or penalties, so the existing runs cannot be decomposed after the fact. A fresh data pull was also out of scope for this offline council review.

### Finer-grained correlation study to build

First add behavior-neutral diagnostics—without changing the score—to both qualified-universe rows and walk-forward rows:

- raw `distance_50`, `distance_200`, distance component before and after scale;
- raw `slope_50`, `slope_200`, slope component;
- base/pivot/50-SMA/VCP breakout flags, breakout volume confirmation, and separate breakout points;
- extension penalty as a separate signed field;
- 52-week-high entry portion and 50-SMA entry portion separately;
- score saturation/cap flags and the setup type being evaluated.

Then measure, on frozen inputs:

1. Fixed 10/20/40/60-trading-day raw and SPY-excess returns, not a variable “until today” outcome.
2. Pearson, Spearman, winsorized Pearson, win probability, downside/tail outcomes, and monotonic binned plots. Distance should be allowed to be nonlinear; bands or splines are more appropriate than assuming a straight line.
3. Marginal and conditional effects: regress/regularize return on distance, slopes, breakout, entry subparts, volatility, sector, market cap, and entry-date effects. Report variance inflation and component correlations.
4. Both all-qualified and selected top-N populations. The latter is necessary for strategy performance; the former avoids the restriction-of-range created by selecting on the score itself.
5. Clustered bootstrap confidence intervals by entry date, with a second clustering/sensitivity check by ticker. Use non-overlapping forward cohorts for the primary analysis.
6. Prespecified market regimes based on benchmark trend, forward benchmark return, and volatility. Do not infer regime after seeing component outcomes.
7. A direct comparison of initial-breakout and pullback/add-on cohorts. The question is likely an interaction—distance may mean different things in the two setups—not one universal coefficient.

The acceptance result is not “one correlation is positive.” It is a stable direction and useful rank separation across held-out time windows, robust estimators, and setup types, with uncertainty narrow enough to distinguish it from zero.

## 3. Complaint 2: the fundamentals block

### Why it feels disconnected

The complaint is supported by implementation evidence:

- No walk-forward trade has ever varied the production fundamental score.
- A fundamentals-present record receives a fixed raw +10 for an unimplemented margin feature (`signal_engine.py:374-376`), equal to 8.75 final points.
- Missing EPS receives 7.5 raw neutral points and missing inventory receives 5 (`:331-371`). Missingness therefore looks like quality rather than uncertainty.
- Revenue quality is based on the average of three sequential QoQ changes (`:276-329`). This is strongly seasonal for many businesses, yet the formula does not seasonally adjust or prefer YoY comparisons when four quarters are available. `revenue_qoq_change` is read at `:269` but never used directly.
- Inventory change is scored with one universal scale (`:349-371`) despite very different sector economics.
- The block is not capped at its advertised raw 40. Revenue 15 + EPS 15 + inventory 10 + placeholder 10 = 50; after scaling it can contribute 43.75.
- Negative fundamental values are possible because the recent-revenue penalty is not followed by a lower clamp.

I emulated the exact implemented fundamental arithmetic over the 2,600 current cache files, without fetching anything. This is a coverage/shape audit, not a return test. The resulting final-score distribution was min -4.38, median 23.31, mean 22.92, 90th percentile 35.51, max 43.75; 280 files (10.8%) exceeded the advertised 35-point maximum. EPS YoY was present in 95.2% and inventory change in only 55.7%. This confirms that the documented weight and actual contribution differ materially.

### What the existing sources can and cannot support

`fetch_quarterly_financials` has no as-of parameter. It asks yfinance for the current quarterly frames and stamps the current fetch time (`src/data/fundamentals_fetcher.py:35-59`). Quarter keys are fiscal period ends, not public filing dates (`:61-114`). Simply taking rows whose quarter end precedes a historical trade would leak information released after that trade and possibly later restatements.

`GitStorageFetcher` stores one file per ticker with `data` and `fetched_at`, overwriting the working-tree copy on refresh (`src/data/git_storage_fetcher.py:78-134`). The working tree alone is not a historical database. However, the repository's Git history preserves a useful sequence of observed snapshots. For AAPL, cache commits exist from 2026-01-15 through 2026-08-14; inspected snapshots had fetch timestamps matching the snapshot period. Repository-wide cache coverage was 2,161 files at the 2026-02-13 commit, 2,354 at 2026-05-11, 2,442 at 2026-07-15, and 2,477 at 2026-08-14.

Therefore, point-in-time use is **partially feasible** with current recorded data:

- For an entry date, select the latest immutable cache blob whose own `fetched_at` is no later than the decision cutoff. Never use a later blob and truncate by quarter date.
- Record snapshot commit, file fetch timestamp, coverage/missingness, and a deterministic score calculated with the exact historical formula version.
- Treat absence as missing, not as proof of neutral quality, and compare a missingness indicator.
- Limit conclusions to periods/tickers with genuine prior snapshots. The nine-month saved walk-forward begins 2025-09-08, while the cache history was only introduced in December 2025. The early part cannot be reconstructed correctly from these files.

For broader history, current yfinance fetchers are insufficient. The best available repo path is the point-in-time SEC-based fundamentals auditor already referenced in `walk_forward_backtest.py:130-164`, but it produces a different audit score and uses costly model calls. A production-grade alternative is a deterministic SEC XBRL/filing loader keyed by accepted/filing timestamp, taxonomy concept, fiscal period, and accession, with immutable raw responses. That can score only facts public before each entry and can handle amended filings explicitly. Until that exists, a cache-snapshot test can validate recent cohorts but cannot establish long-horizon generality.

### Wiring needed in walk-forward

1. Define a `FundamentalsAsOfProvider` interface returning data, availability timestamp, source snapshot/accession, coverage flags, and formula version.
2. Implement the Git-history snapshot provider first; fail closed if no valid pre-entry snapshot exists.
3. Split the output into current production fundamental subparts (revenue, EPS, inventory, constant placeholder, missingness) and store all of them per candidate, not only selected trades.
4. Run two analyses: complete-case predictive validity and realistic operational validity with missing data. Never silently equate absent data with 17.5 points.
5. Add the SEC filing-backed provider for dates without Git snapshots and reconcile a sample manually against filings.
6. Pass the returned as-of dictionary to `score_buy_signal` only after an automated assertion proves `available_at <= entry cutoff`.

## 4. Are the current weights defensible?

No—not as empirically validated weights.

- Fundamentals and VCP account for a nominal 40/125 points but are untested by the walk-forward tool. The actual fundamentals maximum is larger than advertised.
- Entry was increased fivefold based on unsaved, non-reproducible broad-pool runs. In recorded walk-forward tests its correlation is 0.326/0.326/0.369 at n=25, then 0.101/-0.038/0.025 at n=200. The duplicate first two are not independent evidence.
- Trend is the best-looking component in the largest run at r=0.196, but its distance, slope, and breakout meanings are blended; its robust association has not been established, and breakout logic is defective.
- Risk/reward saturates: 87% of the largest run's selected trades score the maximum 10, leaving little ranking information.
- The total score's largest-run correlation is only 0.061.

There is meaningful multicollinearity. In the largest saved run, component correlations include trend/entry -0.432, trend/RS -0.558, and trend/volume -0.547. The negative trend/entry relationship is consistent with the formula rewarding extension in one block and proximity in another. A weight chosen from one-variable correlations ignores those interactions.

The 200 rows are also not 200 independent experiments: there are only 20 entry dates, picks within a date share the same market outcome, holding periods overlap, and selection is top-N. Under an unrealistic iid assumption, a correlation's Fisher-z standard error is already about 0.071 at n=200 and 0.213 at n=25; clustering makes effective precision worse. The data cannot support the apparent precision of point allocations such as 25 versus 10.

Untested/unstable blocks should be candidates for reduced influence, but no replacement numeric allocation is justified by the current evidence. Changing live weights now would exchange one assumption for another and alter both the >=60 gate and top-N selection. Keep the production score frozen while testing prespecified challenger grids in shadow. Select a challenger only by locked, held-out performance and risk criteria—not by maximizing the same correlations used to invent it.

## 5. Why RS and volume are negative in the largest run

### Offline diagnostics performed

For the three 200-trade runs, raw correlations were:

| Universe/seed | RS | Volume | Trend |
|---|---:|---:|---:|
| 250 / 42 | -0.133 | +0.019 | -0.014 |
| 250 / 43 | -0.027 | -0.028 | +0.193 |
| 5000 / 42 | -0.213 | -0.171 | +0.196 |

On the 5,000-universe run:

- removing entry-date means left RS at -0.201 and volume at -0.247, so an across-date market regime alone does not explain the signs;
- a standardized multivariable fit including trend, entry, risk/reward, RS, and volume left coefficients of -0.152 for RS and -0.112 for volume, so simple sign reversal from those measured components is not the whole story;
- but Spearman was only -0.073/-0.006, 5/95 winsorized Pearson -0.062/-0.070, and win-indicator correlation +0.022/+0.003;
- leave-one-entry-date-out Pearson ranges remained negative (-0.257 to -0.095 RS, -0.214 to -0.059 volume), but that does not address the outsized-return leverage spread across dates;
- 69.5% of trades had the maximum RS score and 40% the maximum volume score. Severe caps compress most candidates into ties.

These results make four explanations distinguishable:

1. **Mean reversion:** plausible but unproven. If true, the negative relationship should persist for rank returns and multiple forward horizons. It does not persist strongly in rank or winsorized results here.
2. **Definition/cap problem:** supported. RS is clipped to 0-10 (`signal_engine.py:461-474`). Volume uses only five sessions, compares mean absolute volume on up versus down days, and clips the result (`:395-428`). The calculated 25-day baseline volume at `:399` is never used. A no-down-day window is forced to ratio 1.0 rather than recognized as a special case.
3. **Multicollinearity:** present but not sufficient. Trend is substantially negatively correlated with both, yet the multivariable signs stay negative. A proper regularized held-out model is still needed because this selected sample is small.
4. **Noise/heavy tails:** strongly supported. The negative Pearson magnitudes mostly disappear with robust/rank outcomes, and the signs/magnitudes vary across same-design universe samples.

The SPY-regime explanation is **unverified**. The JSON saves entry-time RS scores but no benchmark levels, forward SPY returns, volatility, or regime label. The tested trades enter from 2025-09-08 through 2026-06-01 and can exit through the August run date, so attributing the result to “August 2026” alone would also be inaccurate. A rerun must persist benchmark return over each exact trade interval and report both raw and excess return.

## 6. Lowest-risk validation and rollout path

### Phase A: freeze and make experiments reproducible

1. Do not change the displayed score or buy threshold.
2. Persist an immutable experiment manifest: code commit, formula version, universe membership as-of source/date, raw price/benchmark snapshot hash, corporate-action settings, fundamental snapshot IDs, seed, date grid, and all parameters.
3. Make baseline and challenger consume the same frozen candidate rows. The current critic compares separately generated run files; fresh provider data or universe changes can otherwise masquerade as scoring drift.
4. Correct behavior-neutral defects before evaluating weights: expose all subcomponents, include VCP in the schema, and repair breakout resistance windows to exclude the current bar. Version these changes because even a “bug fix” changes candidate scores.

### Phase B: fresh correlation reading

“Fresh” has two meanings. Use the latest fully matured historical cohorts for 20/40/60-day outcomes; today's cohort cannot have a future return. Separately begin prospective logging today for future maturation.

Run the enhanced broad-pool study on multiple fixed as-of dates across the full feasible universe, not one unseeded random date. Save candidate-level rows. Produce the robust statistics, conditional models, benchmark-relative outcomes, regime segments, and clustered confidence intervals specified above. Reconcile the prior +0.40/+0.48 entry claim; if its original rows cannot be reproduced, retire it from code comments.

### Phase C: point-in-time walk-forward

Use frozen price/universe data and as-of fundamentals. Run baseline and a small, predeclared challenger grid through identical entry dates. Use nested time splits: earlier folds select among candidates; the final later fold is untouched until one challenger is locked. Include all candidates for ranking diagnostics and execute top-N for portfolio diagnostics.

Primary evaluation should include rank IC, top-N excess return, median and tail return, win rate, turnover, stop frequency, exposure/concentration, and a real overlapping-position equity simulation. Weight selection must account for uncertainty and multiple candidates; it must not optimize one noisy Pearson coefficient.

### Phase D: critic gate

`backtest_critic.py` is useful as a report formatter, not a release authority. It compares only two runs, uses raw correlation thresholds, lacks confidence intervals, and can suggest “decreasing” a negatively correlated component (`scripts/backtest_critic.py:31-35, 65-112`). Extend it to reject incomparable manifests, show robust and clustered intervals, compare baseline/challenger on the same rows, and never auto-propose weights from one run.

### Phase E: shadow rollout

Log old and locked challenger scores side by side for every eligible ticker, including subcomponents, data freshness, score-version ID, rank, threshold crossing, and eventual outcomes. The UI continues to recommend from baseline only. Review rank churn and cases where the challenger changes a recommendation; manually audit the highest-impact disagreements.

Switch only after all prespecified cohorts mature and acceptance criteria pass. Roll out behind a version flag with an immediate fallback, retain both scores in logs, and initially present the challenger as an explicitly labeled experimental comparison. A failed data-freshness or as-of check must fall back to baseline, not silently impute a favorable score.

## 7. Additional risks a number-only reweight would miss

- **Survivorship bias:** both analysis scripts use the current fetched universe for historical dates (`component_correlation_analysis.py:68-70`; `walk_forward_backtest.py:183-197`).
- **Selection/collider bias:** walk-forward correlations are calculated only after the >=60 gate and top-N sorting (`walk_forward_backtest.py:226-260`). Changing weights changes the sampled population itself.
- **Execution look-ahead:** entries use the as-of closing price; a signal computed from that close cannot generally be filled at the same close. Sell-phase checks similarly observe a close and exit at that close (`walk_forward_backtest.py:88-96`). Test next-session execution.
- **Optimistic stops:** if a day's low breaches a stop, simulation fills exactly at the stop even if the market gaps below it (`:81-86`).
- **Censoring/horizon mismatch:** `max_hold_days` slices trading rows, while the latest entry is chosen by calendar days (`:73-77, 172-178`). Recent entries may not have the requested number of sessions yet but are labeled max-hold exits at the last available row.
- **Overlapping dependence:** batches every 14 calendar days can hold for 60 trading days. The “Sharpe-like” value treats trade returns as if independent, and documented drawdown is explicitly not a portfolio equity curve (`:99-127`).
- **Provider reproducibility:** price histories and universe are fetched anew and not saved, so a fixed seed alone does not make a run reproducible.
- **Corporate actions:** provider-adjusted historical prices can be revised. The chosen adjustment policy must be frozen and documented.
- **Total-score cap interaction:** fundamentals can exceed its advertised maximum; the final 125 cap (`signal_engine.py:690-694`) can erase distinctions among other components for high-fundamental names.
- **Gate mismatch in trend template:** the documentation calls criterion 8 an RS requirement, but implementation uses Phase 2 again (`phase_indicators.py:453-467, 555-565`). RS is therefore not actually part of the seven-of-eight gate.
- **Regime and sector confounding:** the saved rows have neither sector nor benchmark-forward fields, preventing direct checks.

## 8. HARD-classified sprint-build task breakdown

| Work item | Suggested owner | Dependencies | Acceptance criteria |
|---|---|---|---|
| Experiment manifest and frozen-data runner | Codex | None | Two baseline runs from the same manifest produce identical candidate rows, trades, and metrics byte-for-byte; mismatched manifests cannot be compared. |
| Behavior-neutral component instrumentation | Codex | Manifest schema | Every qualified candidate records distance, slope, breakout type/points, extension penalty, entry subparts, VCP, caps, missingness, and score version; recomposed total equals production total within rounding. |
| Breakout/VCP test repair | Codex | Instrumentation | Unit fixtures prove current bar is excluded from resistance, each breakout type is reachable, and VCP is populated and saved; baseline behavior change is versioned, never smuggled into a weight comparison. |
| Point-in-time fundamentals provider from Git snapshots | Codex | Manifest; cache-history inventory | Automated checks reject any blob with `fetched_at` after entry; coverage report by date/ticker; hand audit of a stratified sample agrees with the selected historical blob and score arithmetic. |
| SEC filing-time provider design and semantic review | Claude | As-of interface | Written mapping of concepts, filing/acceptance cutoffs, amendments, fiscal periods, sector exceptions, and missing-data policy; sample outputs trace every value to accession and public timestamp. |
| Statistical analysis specification | Claude | Instrument fields finalized | Before outcomes are inspected: locked horizons, primary metrics, clustering, winsorization, regime definitions, multiplicity handling, train/validation/test dates, and noninferiority/risk tolerances approved by the council. |
| Enhanced broad-pool component study | Codex | Frozen inputs; statistical spec | Saved candidate-level artifact; raw/robust/conditional results with intervals for each trend subpart and setup type; prior entry claim either reproduced or formally retired. |
| Nested walk-forward baseline/challenger study | Codex | Fundamentals provider; broad-pool results | Same frozen candidates for all formulas; untouched final time fold; realistic next-session fills, gap stops, complete horizons, benchmark excess returns, clustered uncertainty, and portfolio exposure metrics. No challenger chosen on test data. |
| Shadow-score storage and UI | Antigravity | Locked challenger and schema | Baseline remains sole recommendation source; both versions, ranks, explanations, data freshness, and disagreements are inspectable; telemetry never overwrites historical versions. |
| Recommendation-disagreement review | Claude | Shadow outcomes matured | All threshold/rank-changing cases sampled by impact; false positives, missing-data cases, and setup-type mismatches documented; council sign-off references the prespecified criteria. |
| Release flag, fallback, and monitoring | Antigravity | Council approval | One-step fallback to baseline; alerts for stale/as-of failures and distribution drift; post-release logs retain both versions; rollback drill passes before exposure. |

Release is blocked until the final held-out walk-forward and shadow gates pass. “Correlation improved in one run” is explicitly not an acceptance criterion.

## Final answer to the six questions

1. Distance is indeed over-rewarded relative to pullback entry quality in current arithmetic, but its predictive value is unverified. Build the isolated study before changing it.
2. Fundamentals are disconnected because they have never varied in walk-forward, include large fixed/missing-data points, use seasonally fragile features, and can exceed their advertised cap. Git history enables a partial recent as-of test; full history requires filing-time data.
3. Current weights are not defensible, but no alternative numbers are defensible yet. Freeze production and select among shadow challengers with held-out evidence.
4. RS/volume negatives are mostly a heavy-tail/saturation result in this sample; definition problems and multicollinearity exist, while mean reversion and SPY-regime causation remain unverified.
5. The lowest-risk path is reproducible frozen inputs, fine-grained fresh analysis, point-in-time nested walk-forward, an upgraded critic gate, then side-by-side shadowing and a flagged rollout.
6. The major hidden risks are an overstated fundamental maximum, unreachable base/pivot breakout branches, survivorship and selection bias, non-independent trades, execution optimism, incomplete horizons, provider non-reproducibility, and mixed trade-stage semantics.
