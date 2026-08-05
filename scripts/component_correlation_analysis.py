#!/usr/bin/env python3
"""Which of the 7 scoring components actually predicts forward returns?

score_buy_signal() blends 7 sub-scores into one 0-125 total: trend_score (40),
fundamental_score (40), rr_score (15), rs_score (10), volume_score (10),
entry_score (5), vcp_bonus (5). We already know the blended total barely
correlates with returns (r ~ -0.1 to +0.12) — this checks each ingredient
separately to find out which ones (if any) actually carry signal, and which
are just diluting the ones that do.

Tests ALL Minervini-qualified Phase 2 stocks (not just is_buy>=60), point-in-time
correct (no look-ahead), so we have more data points than restricting to the
final recommended pool.

Usage:
    python scripts/component_correlation_analysis.py --pool 400 --days 30
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

COMPONENTS = ['trend_score', 'fundamental_score', 'rr_score', 'rs_score', 'volume_score', 'entry_score', 'vcp_bonus']


def pearson(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = (sum((x - mean_x) ** 2 for x in xs)) ** 0.5
    std_y = (sum((y - mean_y) ** 2 for y in ys)) ** 0.5
    if std_x == 0 or std_y == 0:
        return None
    return cov / (std_x * std_y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=30, help='How far back the as-of (entry) date is')
    parser.add_argument('--forward-days', type=int, default=None,
                         help='Forward window length; default measures to today. Set explicitly '
                              'to test a fixed historical window not overlapping "today".')
    parser.add_argument('--pool', type=int, default=400)
    args = parser.parse_args()

    as_of = (datetime.now() - timedelta(days=args.days)).date()
    forward_to = (datetime.now() - timedelta(days=args.days - args.forward_days)).date() if args.forward_days else None
    window_desc = f"{as_of} -> {forward_to}" if forward_to else f"{as_of} -> today"
    print(f"Scoring a pool of {args.pool} tickers, entry {window_desc}...\n")

    universe = USStockUniverseFetcher().fetch_universe()
    pool_tickers = random.sample(universe, min(args.pool, len(universe)))

    spy = yf.Ticker('SPY').history(period='2y')
    spy.index = spy.index.tz_localize(None)
    spy_asof = spy.loc[:pd.Timestamp(as_of)]

    rows = []
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
            if phase_info['phase'] != 2:
                continue

            rs_series = calculate_relative_strength(asof_data['Close'], spy_asof['Close'], period=63)
            signal = score_buy_signal(
                ticker=ticker, price_data=asof_data, current_price=current_price,
                phase_info=phase_info, rs_series=rs_series, fundamentals=None, vcp_data=None
            )

            # Only stocks that passed the Minervini gate have populated component details
            if not signal['details'] or 'trend_score' not in signal['details']:
                continue

            if forward_to:
                fwd_data = hist.loc[:pd.Timestamp(forward_to)]
                if fwd_data.empty:
                    continue
                exit_price = fwd_data['Close'].iloc[-1]
            else:
                exit_price = hist['Close'].iloc[-1]
            return_pct = (exit_price - current_price) / current_price * 100

            row = {'ticker': ticker, 'score': signal['score'], 'is_buy': signal['is_buy'], 'return_pct': return_pct}
            for comp in COMPONENTS:
                row[comp] = signal['details'].get(comp, 0) or 0
            rows.append(row)

        except Exception as e:
            logger.debug(f"{ticker}: {e}")
            continue

        if (i + 1) % 100 == 0:
            print(f"  ...{i + 1}/{len(pool_tickers)} processed, {len(rows)} qualified so far")

    print(f"\n{len(rows)} Minervini-qualified Phase 2 stocks collected.\n")

    if len(rows) < 20:
        print("Too few data points for meaningful correlation — try a bigger --pool.")
        return

    is_buy_rows = [r for r in rows if r['is_buy']]

    print(f"{'='*78}")
    print(f"{'Component':<22}{'Range':<12}{'r (all qualified)':<20}{'r (is_buy>=60 only)'}")
    print(f"{'='*78}")

    total_returns = [r['return_pct'] for r in rows]
    total_scores = [r['score'] for r in rows]
    r_total_all = pearson(total_scores, total_returns)

    for comp in ['score'] + COMPONENTS:
        vals_all = [r[comp] for r in rows]
        r_all = pearson(vals_all, total_returns)

        vals_buy = [r[comp] for r in is_buy_rows]
        returns_buy = [r['return_pct'] for r in is_buy_rows]
        r_buy = pearson(vals_buy, returns_buy) if len(is_buy_rows) >= 5 else None

        label = 'TOTAL SCORE' if comp == 'score' else comp
        r_all_str = f"{r_all:+.3f}" if r_all is not None else "n/a"
        r_buy_str = f"{r_buy:+.3f}" if r_buy is not None else "n/a"
        print(f"{label:<22}{'':<12}{r_all_str:<20}{r_buy_str}")

    print(f"{'='*78}")
    print(f"\nSample sizes: {len(rows)} all qualified, {len(is_buy_rows)} is_buy>=60")
    print("r near 0 = no predictive power. |r| > 0.2 would be a genuinely usable signal at this sample size.")
    print("Negative r means higher component score correlated with WORSE forward returns.")


if __name__ == '__main__':
    main()
