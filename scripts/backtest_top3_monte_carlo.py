#!/usr/bin/env python3
"""Monte Carlo version of backtest_top3.py: fetch + score a pool of tickers ONCE
(point-in-time, no look-ahead, same as backtest_top3.py), then re-sample many
different "top 3" portfolios from that same pool without re-fetching data.

Scoring a ticker doesn't depend on which other tickers are in the sample (only on
its own price history + SPY), so this is equivalent to running the single-shot
backtest many times over fresh random draws, at a fraction of the network cost.

Tradeoff: all iterations draw from the same fixed pool rather than fresh random
tickers from the full universe each time, so iterations aren't fully independent
of each other (less externally valid than truly independent draws) — but it's the
only way to run this many iterations without hammering Yahoo Finance for an hour+.

Usage:
    python scripts/backtest_top3_monte_carlo.py --iterations 100 --pool 300 --sample 150
"""

import argparse
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.universe_fetcher import USStockUniverseFetcher
from src.screening.phase_indicators import classify_phase, calculate_relative_strength
from src.screening.signal_engine import score_buy_signal

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--pool', type=int, default=300, help='Tickers to fetch+score once')
    parser.add_argument('--sample', type=int, default=150, help='Tickers drawn per iteration')
    parser.add_argument('--iterations', type=int, default=100)
    parser.add_argument('--investment', type=float, default=1000.0)
    args = parser.parse_args()

    as_of = (datetime.now() - timedelta(days=args.days)).date()
    print(f"Pre-fetching + scoring a pool of {args.pool} tickers as of {as_of} (one-time cost)...")

    universe = USStockUniverseFetcher().fetch_universe()
    pool_tickers = random.sample(universe, min(args.pool, len(universe)))

    spy = yf.Ticker('SPY').history(period='2y')
    spy.index = spy.index.tz_localize(None)
    spy_asof = spy.loc[:pd.Timestamp(as_of)]

    qualifiers = []  # tickers that were real buy signals as of as_of, with real forward return
    for i, ticker in enumerate(pool_tickers):
        try:
            hist = yf.Ticker(ticker).history(period='2y')
            if hist.empty:
                continue
            hist.index = hist.index.tz_localize(None)
            asof_data = hist.loc[:pd.Timestamp(as_of)]
            if len(asof_data) < 200:
                continue

            current_price = asof_data['Close'].iloc[-1]
            phase_info = classify_phase(asof_data, current_price)
            if phase_info['phase'] not in [1, 2]:
                continue

            rs_series = calculate_relative_strength(asof_data['Close'], spy_asof['Close'], period=63)
            signal = score_buy_signal(
                ticker=ticker, price_data=asof_data, current_price=current_price,
                phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
            )
            if signal['is_buy']:
                today_price = hist['Close'].iloc[-1]
                signal['entry_price_asof'] = float(current_price)
                signal['current_price_today'] = float(today_price)
                signal['return_pct'] = (today_price - current_price) / current_price * 100
                qualifiers.append(signal)
        except Exception as e:
            logger.debug(f"{ticker}: {e}")
            continue

        if (i + 1) % 100 == 0:
            print(f"  ...{i + 1}/{len(pool_tickers)} scored")

    print(f"\nPool scored: {len(qualifiers)} qualifying buy signals out of {len(pool_tickers)} tickers.\n")

    # Does the score actually predict forward return? Pearson correlation.
    if len(qualifiers) >= 5:
        scores = [s['score'] for s in qualifiers]
        returns = [s['return_pct'] for s in qualifiers]
        n = len(scores)
        mean_s, mean_r = sum(scores) / n, sum(returns) / n
        cov = sum((s - mean_s) * (r - mean_r) for s, r in zip(scores, returns))
        std_s = (sum((s - mean_s) ** 2 for s in scores)) ** 0.5
        std_r = (sum((r - mean_r) ** 2 for r in returns)) ** 0.5
        corr = cov / (std_s * std_r) if std_s > 0 and std_r > 0 else 0.0
        print(f"Score-vs-{args.days}-day-forward-return correlation among qualifiers: r = {corr:+.3f}")
        print("(1.0 = score perfectly predicts return, 0 = no relationship, negative = higher score did worse)\n")

    if len(qualifiers) < 3:
        print("Not enough qualifiers in this pool to run iterations — try a bigger --pool.")
        return

    qualifier_tickers = {s['ticker'] for s in qualifiers}
    qualifiers_by_ticker = {s['ticker']: s for s in qualifiers}

    print(f"Running {args.iterations} Monte Carlo draws of {args.sample} tickers each from the {args.pool}-ticker pool...\n")

    results = []
    for _ in range(args.iterations):
        drawn = set(random.sample(pool_tickers, min(args.sample, len(pool_tickers))))
        present_qualifiers = [qualifiers_by_ticker[t] for t in drawn if t in qualifier_tickers]
        if not present_qualifiers:
            continue
        present_qualifiers.sort(key=lambda s: s['score'], reverse=True)
        top3 = present_qualifiers[:3]

        per_stock = args.investment / len(top3)
        total_value = sum(
            (per_stock / s['entry_price_asof']) * s['current_price_today'] for s in top3
        )
        profit = total_value - args.investment
        results.append({
            'tickers': [s['ticker'] for s in top3],
            'total_value': total_value,
            'profit': profit,
            'profit_pct': profit / args.investment * 100,
        })

    if not results:
        print("No iteration drew any qualifying tickers — try a bigger --sample or --pool.")
        return

    profits = [r['profit'] for r in results]
    profit_pcts = [r['profit_pct'] for r in results]
    wins = sum(1 for p in profits if p > 0)
    losses = sum(1 for p in profits if p < 0)

    avg_profit = sum(profits) / len(profits)
    avg_pct = sum(profit_pcts) / len(profit_pcts)
    best = max(results, key=lambda r: r['profit'])
    worst = min(results, key=lambda r: r['profit'])
    sorted_pcts = sorted(profit_pcts)
    median_pct = sorted_pcts[len(sorted_pcts) // 2]

    print(f"{'='*70}")
    print(f"RESULTS: {len(results)} valid iterations (as of {as_of}, {args.days} days ago)")
    print(f"{'='*70}")
    print(f"Win rate:        {wins}/{len(results)} ({wins/len(results)*100:.1f}%) profitable, {losses} losses")
    print(f"Average result:  ${avg_profit:+.2f} ({avg_pct:+.2f}%) per $1,000")
    print(f"Median result:   {median_pct:+.2f}%")
    print(f"Best run:        {', '.join(best['tickers'])} -> ${best['profit']:+.2f} ({best['profit_pct']:+.2f}%)")
    print(f"Worst run:       {', '.join(worst['tickers'])} -> ${worst['profit']:+.2f} ({worst['profit_pct']:+.2f}%)")
    print(f"{'='*70}")
    print("\nNote: iterations draw from a shared fixed pool (not fully independent),")
    print("and this is a statistical illustration, not investment advice.")


if __name__ == '__main__':
    main()
