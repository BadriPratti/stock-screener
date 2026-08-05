#!/usr/bin/env python3
"""Point-in-time backtest: what would the top-3 buy signals have been N days ago,
and what would $1000 split across them be worth today?

Critically, this feeds the real scoring engine only price data available THROUGH
the as-of date (no look-ahead) — it does not just take today's picks and pretend
they were made earlier, which would be look-ahead bias (today's picks are selected
because they look good NOW; a week ago the algorithm may not have flagged them
at all). Runs against a random sample of the universe, same approach as --test-mode.

Usage:
    python scripts/backtest_top3.py
    python scripts/backtest_top3.py --days 7 --sample 150 --investment 1000
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
    parser.add_argument('--days', type=int, default=7, help='Lookback days for the as-of date')
    parser.add_argument('--sample', type=int, default=150, help='Random ticker sample size')
    parser.add_argument('--investment', type=float, default=1000.0, help='Total $ invested, split evenly')
    args = parser.parse_args()

    as_of = (datetime.now() - timedelta(days=args.days)).date()
    print(f"Backtesting: what would the top-3 buy signals have been as of {as_of}?")
    print(f"Using ONLY price data through {as_of} (no look-ahead) — random {args.sample}-ticker sample\n")

    universe = USStockUniverseFetcher().fetch_universe()
    sample = random.sample(universe, min(args.sample, len(universe)))

    spy = yf.Ticker('SPY').history(period='2y')
    spy.index = spy.index.tz_localize(None)
    spy_asof = spy.loc[:pd.Timestamp(as_of)]

    candidates = []
    scanned, errors = 0, 0
    for ticker in sample:
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
                candidates.append(signal)

            scanned += 1
        except Exception as e:
            errors += 1
            logger.debug(f"{ticker}: {e}")
            continue

    candidates.sort(key=lambda s: s['score'], reverse=True)
    top3 = candidates[:3]

    print(f"Scanned {scanned}/{len(sample)} tickers ({errors} errors/skipped).")
    print(f"Found {len(candidates)} qualifying buy signals as of {as_of}.\n")

    if not top3:
        print("No qualifying buy signals found in this sample — try a larger --sample size.")
        return

    print(f"{'='*70}\nTOP 3 (as they would have been recommended on {as_of})\n{'='*70}\n")
    per_stock = args.investment / len(top3)
    total_value = 0.0

    for i, s in enumerate(top3, 1):
        shares = per_stock / s['entry_price_asof']
        value_today = shares * s['current_price_today']
        profit = value_today - per_stock
        total_value += value_today

        print(f"#{i} {s['ticker']} — score {s['score']}/125")
        print(f"    Entry ({as_of}): ${s['entry_price_asof']:.2f}  ->  Today: ${s['current_price_today']:.2f}  ({s['return_pct']:+.2f}%)")
        print(f"    ${per_stock:.2f} invested -> {shares:.4f} shares -> worth ${value_today:.2f} today (${profit:+.2f})")
        print()

    total_profit = total_value - args.investment
    print(f"{'='*70}")
    print(f"TOTAL: ${args.investment:.2f} invested -> ${total_value:.2f} today")
    print(f"PROFIT/LOSS: ${total_profit:+.2f} ({total_profit/args.investment*100:+.2f}%)")
    print(f"{'='*70}")
    print("\nNote: small random sample of the universe, not the full ~3,800-stock scan —")
    print("results will vary between runs. Not financial advice.")


if __name__ == '__main__':
    main()
