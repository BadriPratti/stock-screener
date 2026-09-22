# Engineering Council Analysis: Reassessing the Buy Scoring Algorithm

**Date:** 2026-09-22  
**Council Participant:** Antigravity  
**Classification:** HARD (Affects Live Financial Recommendations for Real Capital)  
**Scope:** Read-Only Investigation of Repository Architecture, Historical Backtest Data, and Empirical Evidence  
**Target File:** `.sprint/council/antigravity-scoring.md`

---

## Executive Summary

The user's two complaints regarding `score_buy_signal()` are:
1. *"Too rewarding of distance-from-SMA, not real strength"* (observed live: ET score dropped ~5 points and CF dropped ~2-6 points purely from `distance_from_50sma` shrinking while remaining in confirmed Phase 2).
2. *"Fundamentals block feels disconnected"* (suspicion that the 35-point fundamental sub-score does not correlate with forward returns).

### Primary Findings

1. **Complaint 1 is fully confirmed in mechanism, but unmeasured in sub-component predictive return correlation.**
   The current scoring formula in `src/screening/signal_engine.py:188-204` linearly increases `trend_score` points as price moves from 0% to 15% above the 50 SMA (up to 8.75 final points) and 0% to 20% above the 200 SMA (up to 4.375 final points). A stock executing a low-risk pullback to its rising 50 SMA loses up to 8.75 points and is labeled "Weak Stage 2: 0.5% above 50 SMA" (`signal_engine.py:201`), directly contradicting the Positions view (`src/analysis/position_manager.py:204-210`), which explicitly designates price within 0-3% of the 50 SMA as a "classic continuation add point." Furthermore, `entry_score` (`signal_engine.py:602-615`) attempts to reward proximity to the 50 SMA, creating an internal tug-of-war on the exact same variable (`distance_50`), where the trend distance reward (+8.75 pts) overpowers the entry proximity reward (-3.75 pts), resulting in a net penalty for testing moving average support.

2. **Complaint 2 is fully confirmed: the 35-point fundamentals block has never been backtested.**
   In `scripts/walk_forward_backtest.py:224` and `scripts/component_correlation_analysis.py:94`, `score_buy_signal` is called with `fundamentals=None` unconditionally across all historical trades. Every recorded backtest trade receives an identical fallback score of 17.5 points (`signal_engine.py:380, 386`). Pearson correlation is identically `None` (zero variance) across all 6 recorded walk-forward runs. Furthermore, point-in-time historical reconstruction is structurally blocked: yfinance provides only 4-5 quarters of financial statements indexed by fiscal quarter end date (not SEC filing date), creating severe look-ahead bias if used historically and insufficient history (<4 quarters) for dates prior to early 2026.

3. **The previous reweighting (which boosted `entry_score` from 5 to 25 points) was based on small-sample noise that collapsed in larger samples.**
   The justification in `signal_engine.py:113-114` ("BY FAR the strongest predictor found, +0.40/+0.48 correlation") derived from an unseeded, unsaved run on an unrestricted pool. In the recorded walk-forward simulations, `entry_score` correlation degraded from r = +0.369 at n=25 (`seed=99`) to r = +0.101 at n=200 (`seed=42`), flipped negative to r = -0.038 at n=200 (`seed=43`), and shrank to r = +0.025 at n=200 on the 5,000-ticker universe. At n=200, r = +0.025 has a t-statistic of 0.35 (p = 0.73), which is pure statistical noise.

4. **The current 125-point weighting is indefensible.**
   Over 50% of the scoring weight (35 pts fundamental + 25 pts entry + 5 pts VCP = 65/125, or 52.0%) is either completely unvalidated or empirically demonstrated to be statistical noise in walk-forward testing. However, replacing it with guessed numbers without empirical measurement would violate sound quantitative engineering.

---

## 1. Independent Verification of FACTS.md and Repository Artifacts

Every claim in `.sprint/council/scoring-data/FACTS.md` was verified against repository source code and recorded run artifacts in `data/backtest_history/`.

### Table 1: Independent Audit of Recorded Walk-Forward Backtests (2026-08-04)

| Run File Timestamp | Universe Size | Lookback (Mos) | Top N | Total Trades | `score` r | `trend_score` r | `entry_score` r | `rr_score` r | `rs_score` r | `volume_score` r | `fundamental_score` r |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `222245` (seed 7) | 40 | 2 | 5 | 25 | +0.289 | -0.142 | +0.326 | +0.365 | +0.170 | -0.068 | `null` |
| `222257` (seed 7) | 40 | 2 | 5 | 25 | +0.289 | -0.142 | +0.326 | +0.365 | +0.170 | -0.068 | `null` |
| `222412` (seed 99) | 40 | 2 | 5 | 25 | -0.227 | -0.473 | +0.369 | +0.418 | -0.390 | +0.037 | `null` |
| `225018` (seed 42) | 250 | 9 | 10 | 200 | -0.024 | -0.014 | +0.101 | +0.002 | -0.133 | +0.019 | `null` |
| `225131` (seed 43) | 250 | 9 | 10 | 200 | +0.099 | +0.193 | -0.038 | -0.127 | -0.027 | -0.028 | `null` |
| `225921` (seed 42) | 5000 | 9 | 10 | 200 | +0.061 | +0.196 | +0.025 | +0.023 | -0.213 | -0.171 | `null` |

### Audit Corrections and Clarifications to FACTS.md

1. **Distinction between missing-data fallback and active margin placeholder:**
   FACTS.md notes line 376 (`score += 10 # Placeholder - assume neutral`). In `src/screening/signal_engine.py:374-388`, line 376 is a placeholder for profit margin expansion inside the active branch (`if fundamentals:`). When the dictionary is omitted (`fundamentals=None`), execution falls into lines 379-381:
   ```python
   else:
       fundamental_score = 20  # Half of 40
   ```
   This raw score of 20 is scaled at line 386 by `35 / 40`, yielding `17.5` points flat. Every single trade in all 6 backtest runs had `fundamental_score = 17.5`, producing variance = 0, which makes Pearson correlation mathematically undefined (`null`).

2. **Theoretical Point Leakage in Fundamentals:**
   The docstring at `signal_engine.py:112` advertises Fundamentals as 35 points (was 40). However, the active sub-pieces inside `if fundamentals:` allow:
   - Revenue QoQ/YoY: 15 pts max (`signal_engine.py:299`)
   - EPS YoY: 15 pts max (`signal_engine.py:335`)
   - Inventory: 10 pts max (`signal_engine.py:357`)
   - Margins placeholder: 10 pts flat (`signal_engine.py:376`)
   Raw total possible = 50 points. Scaled by `35 / 40` (`line 386`), `50 * (35 / 40) = 43.75` points. The fundamentals block can contribute 43.75 points toward the total score, not 35 points. The global clamp `max(0, min(score, 125))` at line 691 masks this point inflation.

3. **Parameter Discrepancy between Runs 225018 and 225131:**
   FACTS.md characterizes these runs as having "IDENTICAL params." Verification of the parameter blocks shows they differ in `seed`: Run 225018 used `seed: 42`, while Run 225131 used `seed: 43`. This demonstrates that holding universe size (250), lookback (9 months), step (14 days), and top_n (10) constant, a different random universe draw flips `entry_score` from +0.101 to -0.038 and `rr_score` from +0.002 to -0.127.

4. **Total Omission of `vcp_bonus` from Walk-Forward Infrastructure:**
   In `scripts/walk_forward_backtest.py:58`, `COMPONENTS` is defined as:
   ```python
   COMPONENTS = ['trend_score', 'fundamental_score', 'entry_score', 'rr_score', 'rs_score', 'volume_score']
   ```
   `vcp_bonus` is entirely absent from `COMPONENTS`, absent from the saved trade dictionaries (`line 244-245`), and absent from `scripts/backtest_critic.py:25`. Even if `vcp_data` were supplied, the walk-forward harness would not track or evaluate its correlation.

---

## 2. Determination 1: Complaint #1 ("Too Rewarding of Distance-From-SMA, Not Real Strength")

### Analysis of the Scoring Mechanics

In `src/screening/signal_engine.py:188-253`, `trend_score` is computed as:
```python
distance_component = min(15, max(0,
    (distance_50 / 15.0 * 10) +  # 0-15% -> 0-10 pts
    (distance_200 / 20.0 * 5)    # 0-20% -> 0-5 pts
))
stage2_quality += distance_component
# ... slope_component added (0-15 pts) ...
# ... breakout_bonus added (+10 pts) ...
# ... over-extension penalty (-5 at >20%, -10 at >30%) ...
trend_score_final = min(trend_score, 40) * (35 / 40)
```

Within the typical Stage 2 operating range (0% to 20% above 50 SMA):
- A stock at 0% above 50 SMA receives 0 points from the 50 SMA term.
- A stock at 15% above 50 SMA receives the maximum 10 points (scaled to 8.75 final points).
- Marginal reward: +0.583 final points per 1.0% distance above 50 SMA.
- Marginal reward: +0.219 final points per 1.0% distance above 200 SMA.

### The Internal Architectural Contradiction

Three independent sections of the codebase treat `distance_from_50sma` with mutually contradictory logic:

1. **`signal_engine.py:196-204` (Trend Structure):**
   - Treats distance < 3% as "Weak Stage 2" or "Very weak Stage 2."
   - Penalizes proximity to the 50 SMA.

2. **`src/analysis/position_manager.py:204-210` (Positions Management):**
   - Explicitly checks: `phase == 2 and sma_50 > 0 and sma_50 <= current_price <= sma_50 * 1.03 and gain_pct < 15`.
   - Generates the user-facing signal: *"Pulled back to the rising 50 SMA without breaking it, still in a confirmed Phase 2 uptrend... a classic continuation add point if you want to size up."*

3. **`signal_engine.py:602-615` (Entry Quality):**
   - Evaluates:
     ```python
     if distance_50 > 0 and distance_50 <= 20:
         sma_score = 2 - (distance_50 / 20.0) * 1
     ```
   - Multiplied by 5 (`entry_score_final = entry_score * 5` at line 642).
   - At distance_50 = 0%, awards 2.0 * 5 = 10.0 points.
   - At distance_50 = 20%, awards 1.0 * 5 = 5.0 points.
   - Marginal penalty: -0.25 final points per 1.0% distance above 50 SMA.

### Net Effect on Pullback

When a stock pulls back from 15% above 50 SMA to 1% above 50 SMA:
- `trend_score` distance component drops from 10.0 to 0.67 raw points ($\Delta = -9.33$ raw, or $-8.16$ final points).
- `entry_score` SMA component rises from 1.25 to 1.95 raw points ($\Delta = +0.70$ raw, multiplied by 5 = $+3.50$ final points).
- Assuming slope, RS, and fundamentals remain steady, the stock loses:
  $$\Delta_{\text{net}} = -8.16 + 3.50 = -4.66 \text{ points}$$
- If distance from 200 SMA also compressed slightly, the total drop is 5 to 6 points.

This matches the user's direct observations on ET (~5 pt drop) and CF (~2-6 pt drop). The screener penalizes low-risk continuation setups because the upward slope of the trend distance formula outweighs the downward slope of the entry proximity formula.

### Discontinuous Penalty Cliffs

At `signal_engine.py:241-246`:
- `distance_50 > 20`: -5 raw points (-4.375 final points).
- `distance_50 > 30`: -10 raw points (-8.75 final points).
A stock moving from 19.9% to 20.1% distance experiences an instantaneous 4.375-point drop. Step functions create artificial score volatility near boundaries.

### Diagnostic Tooling Design to Isolate Trend Sub-Components

Existing tooling evaluates only composite `trend_score`. To measure whether distance adds value or merely noise, the correlation harness must isolate the 4 underlying components:

```python
# Proposed diagnostic breakdown for signal_engine details
details['trend_subcomponents'] = {
    'dist_50_pts': round(distance_50_pts, 2),
    'dist_200_pts': round(distance_200_pts, 2),
    'slope_50_pts': round(slope_50_pts, 2),
    'slope_200_pts': round(slope_200_pts, 2),
    'breakout_bonus_pts': round(breakout_bonus, 2),
    'extension_penalty_pts': round(extension_penalty, 2),
}
```

By instrumenting `scripts/component_correlation_analysis.py` to record these fields alongside realized forward returns (14-day, 30-day, 60-day), we can calculate:
1. Univariate Pearson $r$ and Spearman $\rho$ for `dist_50` vs. returns.
2. Multivariate OLS regression:
   $$\text{Return} = \beta_0 + \beta_1(\text{dist\_50}) + \beta_2(\text{slope\_50}) + \beta_3(\text{breakout}) + \epsilon$$
This will determine whether $\beta_1$ is positive, zero, or negative when controlling for slope.

---

## 3. Determination 2: Complaint #2 ("Fundamentals Block Feels Disconnected") & Historical Feasibility

### Verification of Omission

`scripts/walk_forward_backtest.py:221-225`:
```python
signal = score_buy_signal(
    ticker=ticker, price_data=asof_data, current_price=current_price,
    phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
)
```
Fundamentals were omitted intentionally during initial development because point-in-time financial statements are non-trivial to reconstruct without look-ahead bias.

### Technical Feasibility Analysis of Point-In-Time Historical Fundamentals

| Asset / Source | Current State | Historical Depth | Point-in-Time Correctness | Feasibility for Walk-Forward |
| :--- | :--- | :--- | :--- | :--- |
| `data/fundamentals_cache/` (2,600 files) | Single snapshot fetched ~2026-08-14 | Latest 5 fiscal quarters | None (Fetched at single fixed date) | **Infeasible** (Severe look-ahead bias for 2025 trades) |
| `src/data/fundamentals_fetcher.py` (yfinance) | Live API calls to `quarterly_financials` | 4-5 quarters max | Poor (Keys are period end dates, not SEC filing dates) | **Infeasible** (Look-ahead on filing lag; insufficient depth) |
| `src/data/fmp_fetcher.py` (Financial Modeling Prep) | API client implemented | Multi-year historical statements | Moderate (Has filing dates, but requires key) | **Infeasible on Free Tier** (250 calls/day limit vs. 200 trades * 4 calls = 800 calls/run) |
| `src/agents/fundamentals_auditor.py` (EDGAR + LLM) | Full text SEC parser via EDGAR | Unlimited historical filings | High (Uses actual acceptance timestamp) | **Infeasible for Bulk Screening** (15-50s and $0.05-$0.15 per trade) |

### Why yfinance Cannot Support Historical Walk-Forward Testing

1. **Look-Ahead Bias via Filing Date Lag:**
   `quarterly_income` columns represent fiscal period end dates (e.g., `2025-09-30`), not public disclosure dates. A company whose quarter ends September 30 typically files its Form 10-Q 40 to 45 days later (mid-November). If a backtest evaluates a trade on October 15 using statements indexed to September 30, it trades on information that was not public.
2. **Insufficient Historical Depth:**
   `signal_engine.py:276` requires at least 4 quarters of revenue to compute 3 quarters of QoQ growth:
   ```python
   if quarterly_revenue and len(quarterly_revenue) >= 4:
   ```
   Because yfinance only provides 4 to 5 quarters total, any simulation date older than 3 to 6 months before today will have fewer than 4 prior quarters, causing the calculation to fail and drop into fallback mode.

### Recommendation on Fundamentals

Because historical point-in-time fundamentals cannot be reconstructed cleanly with the repository's current free data sources:
- Do not attempt to synthesize unverified historical fundamental data.
- **Provisionally reduce `fundamental_score` weight:** Lower nominal weight from 35 points to 10-15 points, or reframe it as a qualifying filter / penalty modifier rather than a 28% additive component.
- **Forward Point-in-Time Collection:** `src/screening/market_motion.py` and daily scan snapshots already record daily fundamental snapshots. Allow this genuine point-in-time dataset to accumulate forward for 6 months before recalibrating a high-weight fundamental block.

---

## 4. Determination 3: Defensibility of Current Weights & `entry_score` Instability

### Empirical Evidence of Instability

`signal_engine.py:109-114` states:
> *"Entry quality: 25 points (was 5 — BY FAR the strongest predictor found, +0.40/+0.48 correlation across both windows, stronger than the blended total score itself)"*

Comparing that justification to the recorded walk-forward runs:
- **Run 222412** ($N=25$, universe 40, lookback 2m): `entry_score` $r = +0.369$.
- **Run 225018** ($N=200$, universe 250, lookback 9m, seed 42): `entry_score` $r = +0.101$.
- **Run 225131** ($N=200$, universe 250, lookback 9m, seed 43): `entry_score` $r = -0.038$.
- **Run 225921** ($N=200$, universe 5000, lookback 9m, seed 42): `entry_score` $r = +0.025$.

### Statistical Power and Standard Error

The standard error of Pearson's correlation coefficient is:
$$SE_r \approx \frac{1 - r^2}{\sqrt{N - 2}}$$

- For $N = 25$ ($r \approx 0$): $SE \approx \frac{1}{\sqrt{23}} \approx 0.209$. The 95% confidence interval is $\pm 1.96 \times 0.209 \approx \pm 0.409$. An observed correlation of $+0.37$ on 25 trades is not statistically distinguishable from zero at the 95% confidence level ($p > 0.05$).
- For $N = 200$ ($r \approx 0$): $SE \approx \frac{1}{\sqrt{198}} \approx 0.071$. The 95% confidence interval is $\pm 0.139$.
  - In Run 225921, `entry_score` $r = +0.025 \implies t = \frac{0.025}{0.071} = 0.35$ ($p = 0.73$).
  - In Run 225921, `trend_score` $r = +0.196 \implies t = \frac{0.196}{0.069} = 2.84$ ($p = 0.005$).

### The Reweighting Error

In the 2026-08-04 reweighting pass:
1. `entry_score` was boosted by 500% (from 5 to 25 points) based on a small-sample correlation that was within normal sampling noise.
2. `trend_score` was trimmed from 40 to 35 points, despite being the **only** component that demonstrated statistically significant positive correlation ($r = +0.196, p = 0.005$) in the largest, most representative simulation (Run 225921).
3. `fundamental_score` was trimmed by only 5 points (40 to 35) on "general principle," leaving 28% of the score tied to a variable with zero empirical validation.

### Defensibility Verdict

The current weighting scheme is indefensible. 52% of the score is allocated to components that are either completely untested in walk-forward backtests (fundamentals, VCP) or demonstrated to collapse to noise at scale (entry score). 

However, this council **must not** guess replacement weights. We propose a provisional testing matrix to be evaluated through fresh walk-forward runs:

| Component | Current Weight | Stated Evidence | Walk-Forward Evidence (N=200) | Provisional Proposal for Testing |
| :--- | :--- | :--- | :--- | :--- |
| `trend_score` | 35 pts | Modest correlation cited | **$r = +0.196$ ($p=0.005$)** (Strongest positive) | 45 - 50 pts (after distance fix) |
| `fundamental_score` | 35 pts | Untested | **$r = \text{null}$** (Zero variance) | 10 - 15 pts (or qualitative gate) |
| `entry_score` | 25 pts | +0.40/+0.48 cited (unverified) | **$r = +0.025$ ($p=0.73$)** (Statistical noise) | 10 - 15 pts |
| `rr_score` | 10 pts | Inconsistent (+0.04/+0.26) | $r = +0.023$ ($p=0.75$) | 10 pts |
| `rs_score` | 10 pts | Flipped sign (+0.16/-0.21) | $r = -0.213$ ($p=0.002$) | 10 - 15 pts (with slope smoothing) |
| `volume_score` | 5 pts | Negative (-0.02/-0.18) | $r = -0.171$ ($p=0.016$) | 5 pts |
| `vcp_bonus` | 5 pts | Untested | Not tracked | 5 pts |

---

## 5. Determination 4: Negative Correlations of `rs_score` (-0.213) and `volume_score` (-0.171)

In Run 225921 ($N=200$, 5000 universe, 9-month lookback), both `rs_score` ($r = -0.213$) and `volume_score` ($r = -0.171$) exhibited statistically significant negative correlations with forward returns.

Four competing hypotheses were evaluated:

### Hypothesis A: Short-Term Climax vs. Intermediate Holding Period (Mean-Reversion)

1. **`rs_score` mechanics (`signal_engine.py:462-474`):**
   Scored on a 20-day RS slope vs. SPY. An extreme RS slope over 20 trading days indicates a steep, near-vertical relative surge. In growth stock swing trading, stocks that have doubled their distance from index moving averages over 15-20 days are often short-term extended. Entering at peak slope without base consolidation frequently leads to immediate 2-4 week consolidations or pullbacks, dragging down 30-60 day trade returns.
2. **`volume_score` mechanics (`signal_engine.py:397-428`):**
   Calculates ratio of up-day volume to down-day volume over **only the last 5 trading days**. A 5-day window is prone to capturing volume blow-offs or climactic exhaustion bars. Stocks with extreme 5-day volume ratios are often at the tail end of an impulse move rather than the low-risk start of a base breakout.

### Hypothesis B: Heavy-Tailed Return Outliers (Leverage Points)

In swing trading distributions, a few outsized winning trades (e.g., +50% to +200%) exert substantial leverage on Pearson correlation coefficients.
If a major winner broke out from a quiet, low-volume base with a flat 20-day RS slope (modest initial `rs_score` of 4-5 and neutral `volume_score` of 5) and subsequently trended upward for 60 days, that single trade will pull Pearson correlation negative for both metrics.

To test this without running unauthorized commands, the recorded trades in `data/backtest_history/walk_forward_20260804_225921.json` were inspected. The summary reports:
- Win rate: 29.0%
- Average win: +33.87%
- Average loss: -5.39%
- Max return: Several large positive outliers (>50%).
When win rate is 29% and average win is 6x the average loss, Pearson $r$ is dominated by the feature values of the top 5-10 winning trades. A flat base breakout (low initial 5-day volume ratio, low initial 20-day RS slope) that produces a massive trend will mechanically generate negative Pearson correlation against short-term momentum indicators.

### Hypothesis C: Multicollinearity and Range Restriction

All trades evaluated in `walk_forward_backtest.py` have already passed:
1. Phase 2 classification (`phase_indicators.py:370-380`).
2. Minervini Trend Template (at least 7 of 8 criteria, `signal_engine.py:158`).
3. Total score $\ge 60$, ranked in the top 10 candidates for that period (`walk_forward_backtest.py:226-230`).

Within this pre-selected, highly restricted range of market leaders, variations in short-term RS slope do not measure "is this a leader?" (the Minervini filter already answered yes); they measure "how fast did it move in the last 15 days?" Fast recent moves within a Stage 2 population are subject to mean reversion over the subsequent 30-60 days.

### Hypothesis D: Macro Market Regime (Nov 2025 - Aug 2026)

During choppy or rotating market regimes, high-beta momentum stocks experience sharp pullbacks as institutional rotation punishes recent high-fliers. If the 9-month test window coincided with sector rotation, chasing 20-day RS strength would underperform buying quiet bases.

### Conclusion on RS and Volume

Neither `rs_score` nor `volume_score` should be inverted or eliminated based on these negative signs alone. The negative correlations are an artifact of pairing **short-term momentum indicators** (5-day volume ratio, 20-day RS slope) with **longer-term holding periods** (up to 60 days) on a pre-filtered population of Stage 2 stocks, distorted by heavy-tailed outlier returns.

**Design adjustments to test:**
- Expand the RS measurement period from 20 days to 63 days (3 months) to measure intermediate-term leadership rather than short-term extension.
- Expand the volume ratio period from 5 days to 20 or 50 days to measure genuine institutional accumulation rather than single-week volume spikes.

---

## 6. Determination 5: Concrete, Lowest-Risk Validation and Rollout Sequence

This tool affects real capital. Shipping an unvalidated reweighting carries unacceptable financial risk. The validation and rollout process must follow a strict, gated sequence:

```
[Phase 1: Instrumentation]
       │ (Export trend subcomponents & add scoring version metadata)
       ▼
[Phase 2: Fresh Diagnostic Correlation Analysis]
       │ (Measure decomposed components on current Sept 2026 data)
       ▼
[Phase 3: Formula Candidate Formulation & Simulation]
       │ (Test candidates via walk_forward_backtest & backtest_critic)
       ▼
[Phase 4: Side-by-Side Shadow Mode (10 Trading Days)]
       │ (Log v1 vs v2 without changing displayed recommendations)
       ▼
[Phase 5: Production Cutover & Monitoring]
```

### Phase 1: Diagnostic Instrumentation (Zero Behavior Change)
- In `src/screening/signal_engine.py`, unpack `trend_score` in the returned `details` dictionary to expose:
  - `distance_50_score`
  - `distance_200_score`
  - `slope_50_score`
  - `slope_200_score`
  - `breakout_score`
  - `extension_penalty`
- Expose `entry_subcomponents` (`high_proximity_score`, `sma_proximity_score`).
- Ensure no change to `score`, `is_buy`, or existing return keys.

### Phase 2: Fresh Diagnostic Run (7 Weeks Post-August 4)
- Update `scripts/component_correlation_analysis.py` to:
  - Read the unpacked sub-components.
  - Calculate both Pearson $r$ and Spearman rank correlation $\rho$.
  - Calculate winsorized correlations (clamping top/bottom 5% returns) to eliminate single-trade leverage.
- Run against a 500-stock pool across 30-day and 60-day forward windows on current market data (September 2026).

### Phase 3: Walk-Forward Backtest Verification
- Test proposed formula adjustments (e.g., smoothing the distance curve, reducing fundamental weight) using:
  ```bash
  python scripts/walk_forward_backtest.py --universe-size 250 --lookback-months 9 --seed 42
  ```
- Run `scripts/backtest_critic.py` against the August 4 baseline (`walk_forward_20260804_225018.json`).
- **Hard Acceptance Gate:** The new formula must show:
  1. No decrease in win rate ($> 30\%$).
  2. Increase in Sharpe-like ratio ($\ge 0.25$).
  3. Positive correlation for `trend_score` ($r \ge +0.15$).
  4. Non-negative correlation for composite `score` ($r \ge +0.10$).

### Phase 4: Side-by-Side Shadow Mode
- In `src/screening/market_motion.py` and `run_optimized_scan.py`:
  - Calculate `score_v1` (current live formula) and `score_v2_candidate`.
  - Store both in daily scan outputs and frame metadata.
  - Render the UI, shortlist, and email notifications using `score_v1` exclusively.
- Maintain shadow mode for 10 consecutive trading sessions.
- Audit specific behavior: Verify that healthy Stage 2 pullbacks (like ET and CF) maintain stable scores in `v2` rather than dropping 5 points.

### Phase 5: Production Cutover
- Increment `SCORING_VERSION = "v2"` in `src/screening/market_motion.py:43` and `src/screening/pick_history.py:20`.
- Flip production output to `v2`.

---

## 7. Additional Structural & Quantitative Findings

### 1. Multicollinearity Between Trend and Entry
`trend_score` and `entry_score` both consume `distance_from_50sma`. 
- `trend_score` rewards large distance ($0 \to 15\%$).
- `entry_score` rewards small distance ($0 \to 20\%$).
Evaluating the same physical market variable in two separate components with opposing signs creates artificial parameter sensitivity and obfuscates what the screener is actually optimizing for.

### 2. Discontinuous Step Functions Create Jitter
- Entry quality near 52-week high (`signal_engine.py:581-598`):
  - $\ge -5\%$: 3.0 pts
  - $-5\%$ to $-15\%$: Linear interpolation
  - $-15\%$ to $-25\%$: Linear interpolation
  - $< -25\%$: 0.0 pts
- Trend extension penalty (`signal_engine.py:241-246`):
  - $> 20\%$: -5 pts
  - $> 30\%$: -10 pts
Step cliffs cause tickers to jump 5 to 10 points on fractional price fluctuations. All penalties and boundaries should be converted to continuous sigmoid or piecewise linear functions.

### 3. Inadequacy of 200 Trades Across 9 Months
A backtest of 200 trades across one 9-month window represents approximately 18 to 20 entry decision cycles. Because market cycles rotate between momentum, value, consolidation, and contraction, a single 9-month window captures only one dominant market regime. Calibrating weights to the tenth of a point based on 200 trades over-fits the algorithm to that specific regime. Minimum sample size for setting 7 independent weights should be at least 500 trades across multiple market regimes (bull, bear, sideways).

---

## 8. Actionable Task Breakdown for /sprint-build

The following task breakdown is structured for a HARD-classified `/sprint-build`:

| Task ID | Task Description | Owner | Dependencies | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TASK-1** | **Instrument Sub-Component Diagnostics in Signal Engine** | Antigravity | None | `score_buy_signal` outputs `trend_subcomponents` and `entry_subcomponents` in `details`. All existing tests pass. Zero changes to final `score` or `is_buy`. |
| **TASK-2** | **Extend Component Correlation Analysis with Robust Metrics** | Codex | TASK-1 | `component_correlation_analysis.py` evaluates all sub-components, calculates Spearman $\rho$ and winsorized Pearson $r$, accepts `--seed`, and saves output JSON to `data/correlation_reports/`. |
| **TASK-3** | **Execute Fresh Correlation Run on Current Market Data** | Antigravity | TASK-2 | Run on $N \ge 400$ pool across 30d and 60d windows on current data. Produces verified report documenting the empirical predictive value of `distance_50` vs `slope_50`. |
| **TASK-4** | **Reconcile Distance-from-SMA Formula & Rebalance Weights** | Codex | TASK-3 | Revise `distance_component` in `signal_engine.py` to remove penalty on 0-3% pullbacks; eliminate opposing sign conflict with `entry_score`; provisionally adjust weights per empirical findings from TASK-3. |
| **TASK-5** | **Walk-Forward Validation & Critic Diff Run** | Antigravity | TASK-4 | Execute `walk_forward_backtest.py` on 250 universe / 9 months with seed 42. Compare against baseline with `backtest_critic.py`. Must pass hard gates (win rate $\ge 30\%$, Sharpe $\ge 0.25$, positive trend correlation). |
| **TASK-6** | **Implement 10-Day Shadow Mode in Batch Scanner & UI** | Claude | TASK-5 | Daily scans calculate both `v1` and `v2_candidate`. Side-by-side comparison view in dev logs. Real user recommendations remain locked to `v1`. |
| **TASK-7** | **Final Production Cutover and Documentation** | Antigravity | TASK-6 | After 10-day shadow audit confirms stability, flip production to `v2`, increment `SCORING_VERSION`, and update documentation. |

---
