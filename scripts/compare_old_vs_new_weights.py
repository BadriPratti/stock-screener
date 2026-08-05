#!/usr/bin/env python3
"""Controlled A/B: score the SAME pool of tickers with both the OLD and NEW component
weights, so any difference in outcome is actually due to the reweight, not a different
random draw of the market (which confounded the earlier before/after comparison).

Reconstructs the old-weight total algebraically from the new-weight component values
already in `details` (each component's scaling factor is invertible), rather than
re-running score_buy_signal twice — one fetch/score pass, two totals compared.
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

# Inverse of the scaling factors applied in signal_engine.py, to reconstruct old-weight
# component values from the new-weight ones already stored in `details`.
OLD_SCALE = {
    'trend_score': 40 / 35,
    'fundamental_score': 40 / 35,
    'entry_score': 1 / 5,
    'rr_score': 15 / 10,
    'volume_score': 10 / 5,
    'rs_score': 1.0,   # unchanged
}


def pearson(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = (sum((x - mean_x) ** 2 for x in xs)) ** 0.5
    std_y = (sum((y - mean_y) ** 2 for y in ys)) ** 0.5
    return cov / (std_x * std_y) if std_x > 0 and std_y > 0 else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--pool', type=int, default=300)
    parser.add_argument('--investment', type=float, default=1000.0)
    args = parser.parse_args()

    as_of = (datetime.now() - timedelta(days=args.days)).date()
    print(f"Scoring ONE pool of {args.pool} tickers as of {as_of} with BOTH weight schemes...\n")

    universe = USStockUniverseFetcher().fetch_universe()
    pool_tickers = random.sample(universe, min(args.pool, len(universe)))

    spy = yf.Ticker('SPY').history(period='2y')
    spy.index = spy.index.tz_localize(None)
    spy_asof = spy.loc[:pd.Timestamp(as_of)]

    rows = []
    for ticker in pool_tickers:
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
            d = signal['details']
            if not d or 'trend_score' not in d:
                continue

            old_total = sum(d.get(k, 0) * OLD_SCALE[k] for k in OLD_SCALE) + (d.get('vcp_bonus', 0) or 0)
            new_total = signal['score']

            today_price = hist['Close'].iloc[-1]
            return_pct = (today_price - current_price) / current_price * 100

            rows.append({
                'ticker': ticker, 'old_score': old_total, 'new_score': new_total,
                'old_is_buy': old_total >= 60, 'new_is_buy': signal['is_buy'],
                'return_pct': return_pct, 'entry_price': current_price, 'today_price': today_price,
            })
        except Exception as e:
            logger.debug(f"{ticker}: {e}")
            continue

    print(f"{len(rows)} Minervini-qualified Phase 2 stocks scored under both schemes.\n")

    old_qual = [r for r in rows if r['old_is_buy']]
    new_qual = [r for r in rows if r['new_is_buy']]

    r_old = pearson([r['old_score'] for r in old_qual], [r['return_pct'] for r in old_qual])
    r_new = pearson([r['new_score'] for r in new_qual], [r['return_pct'] for r in new_qual])

    print(f"{'='*70}")
    print(f"OLD weights: {len(old_qual)} qualified, score-vs-return r = {r_old:+.3f}" if r_old is not None else "OLD: n/a")
    print(f"NEW weights: {len(new_qual)} qualified, score-vs-return r = {r_new:+.3f}" if r_new is not None else "NEW: n/a")
    print(f"{'='*70}\n")

    def top3_result(qualified, score_key):
        top3 = sorted(qualified, key=lambda r: r[score_key], reverse=True)[:3]
        if not top3:
            return None
        per_stock = args.investment / len(top3)
        value = sum((per_stock / r['entry_price']) * r['today_price'] for r in top3)
        return top3, value, value - args.investment

    old_result = top3_result(old_qual, 'old_score')
    new_result = top3_result(new_qual, 'new_score')

    if old_result:
        tickers, value, profit = old_result
        print(f"OLD top 3: {[t['ticker'] for t in tickers]}")
        print(f"  ${args.investment:.0f} -> ${value:.2f} (${profit:+.2f}, {profit/args.investment*100:+.2f}%)")
    if new_result:
        tickers, value, profit = new_result
        print(f"NEW top 3: {[t['ticker'] for t in tickers]}")
        print(f"  ${args.investment:.0f} -> ${value:.2f} (${profit:+.2f}, {profit/args.investment*100:+.2f}%)")


if __name__ == '__main__':
    main()
