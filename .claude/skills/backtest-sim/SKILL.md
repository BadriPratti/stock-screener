---
name: backtest-sim
description: Run a point-in-time backtest simulating $1,000 invested in the top 3 buy-signal picks from N days ago (default 7), tracked to today with real historical prices. Use when the user says "run a simulation," "backtest," "how much would I have made," or wants to test the screener against real past data. Supports running multiple times to see variance across different random samples.
---

Run `scripts/backtest_top3.py` from the project root — this is a genuine point-in-time backtest (feeds the real scoring engine only price data available as of the entry date, no look-ahead bias), not a hindsight-biased "today's picks pretended to be from last week."

## Running once

```
venv/bin/python scripts/backtest_top3.py --days 7 --investment 1000
```

- `--days`: how many days back the entry date is (default 7)
- `--sample`: random ticker sample size from the universe (default 150)
- `--investment`: total $ invested, split evenly across the top 3 (default 1000)

Each run uses a **different random 150-ticker sample** of the ~3,800-stock universe, so results vary run to run — this is expected, not a bug. Report each run's picks, entry/exit prices, and profit/loss clearly.

## Running multiple times ("do it N times")

Run the command N times in sequence (a shell loop is fine, e.g. `for i in $(seq 1 5); do venv/bin/python scripts/backtest_top3.py --days 7 --investment 1000; done`). After all runs, present:
1. A table of all N runs (picks + result each)
2. Win rate (how many were profitable)
3. Average and median result across all N runs

## Important framing to include every time

- This is a **statistical illustration**, not investment advice or a guarantee of future results.
- Each run's small ticker sample means results are noisy — don't over-interpret a single run or even a handful of runs as proof the system does/doesn't work. See `scripts/backtest_top3_monte_carlo.py` and `scripts/component_correlation_analysis.py` for more statistically robust versions (100-iteration Monte Carlo, correlation analysis) if the user wants a deeper read than "run it a few times."
