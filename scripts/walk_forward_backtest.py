#!/usr/bin/env python3
"""Walk-forward backtest: the rigorous version.

Fixes the weaknesses of scripts/backtest_top3*.py (single/few time windows, top-3
concentration, fixed-N-day snapshot exits, fresh random samples each run):

1. Walks a FIXED ticker universe through MANY historical entry dates (not one),
   spanning real bull/correction/choppy stretches, not one arbitrary week.
2. Takes the top N (default 10) picks per period, not top 3.
3. Each ticker's full price history is fetched ONCE and reused across every
   walk-forward date (in-memory slicing) — network cost stays bounded to the
   universe size regardless of how many periods are tested.
4. Trades exit on REAL rules — stop-loss breach (intraday low), a Phase 3/4
   breakdown (re-running the actual phase classifier day-by-day going forward),
   or a max holding period cap, whichever comes first.
5. Reports win rate, avg win/loss, max drawdown, and a Sharpe-like consistency
   ratio across ALL trades — not one dollar figure from one basket.
6. --seed makes runs REPRODUCIBLE (same universe sample every time) — the
   previous version resampled randomly on every invocation, so "rerun the same
   command" silently tested different stocks. Default seed is fixed; pass
   --seed 0 (or any int) explicitly to compare specific runs, or omit --seed
   entirely for a fresh random draw when you want that instead.
7. Tracks each trade's individual scoring COMPONENTS (trend/fundamental/entry/
   R:R/RS/volume) at entry time, and reports each component's correlation with
   realized return — this is what scripts/backtest_critic.py compares between
   runs to detect drift.
8. Saves full structured results to data/backtest_history/ as JSON, so future
   runs have a baseline to compare against.

Usage:
    python scripts/walk_forward_backtest.py
    python scripts/walk_forward_backtest.py --universe-size 3800 --lookback-months 12 \
        --step-days 14 --top-n 15 --max-hold-days 60 --seed 42
"""

import argparse
import json
import logging
import random
import statistics
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.universe_fetcher import USStockUniverseFetcher
from src.screening.phase_indicators import classify_phase, calculate_relative_strength
from src.screening.signal_engine import score_buy_signal

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

COMPONENTS = ['trend_score', 'fundamental_score', 'entry_score', 'rr_score', 'rs_score', 'volume_score']
HISTORY_DIR = Path(__file__).parent.parent / "data" / "backtest_history"


def pearson(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = (sum((x - mean_x) ** 2 for x in xs)) ** 0.5
    std_y = (sum((y - mean_y) ** 2 for y in ys)) ** 0.5
    return cov / (std_x * std_y) if std_x > 0 and std_y > 0 else None


def simulate_trade(hist: pd.DataFrame, entry_date: pd.Timestamp, entry_price: float,
                    stop_loss: float, max_hold_days: int) -> dict:
    """Walk forward day-by-day using REAL subsequent price data already in memory.
    Exits on stop-loss breach, a Phase 3/4 breakdown, or max_hold_days — first wins."""
    future = hist.loc[hist.index > entry_date].iloc[:max_hold_days]
    if future.empty:
        return None

    for i in range(len(future)):
        day = future.index[i]
        row = future.iloc[i]

        if stop_loss and row['Low'] <= stop_loss:
            return {'exit_price': stop_loss, 'exit_reason': 'stop_loss', 'days_held': i + 1, 'exit_date': day}

        if i > 0 and i % 3 == 0:
            data_through_today = hist.loc[:day]
            if len(data_through_today) >= 200:
                phase_info = classify_phase(data_through_today, row['Close'])
                if phase_info['phase'] in [3, 4]:
                    return {'exit_price': row['Close'], 'exit_reason': 'sell_signal', 'days_held': i + 1, 'exit_date': day}

    last = future.iloc[-1]
    return {'exit_price': last['Close'], 'exit_reason': 'max_hold', 'days_held': len(future), 'exit_date': future.index[-1]}


def compute_max_drawdown(trades: list, investment_per_trade: float) -> dict:
    """Builds a cumulative P&L curve ordered by EXIT date (when P&L is realized)
    and finds the largest peak-to-trough decline.

    Simplifying assumption, stated plainly: this treats every trade as an
    independent $investment_per_trade position (not a single compounding
    account), and orders by exit date even though trades can overlap in time
    (a new batch can open while an earlier one is still held). It's an
    approximation of "how much could you be down at once," not a literal
    portfolio equity curve — good enough to catch a strategy that has ugly
    losing streaks, not precise enough to use for real position sizing.
    """
    if not trades:
        return {'max_drawdown_pct': 0, 'max_drawdown_dollars': 0}

    ordered = sorted(trades, key=lambda t: t['exit_date'])
    cumulative = 0.0
    peak = 0.0
    max_dd_dollars = 0.0
    for t in ordered:
        cumulative += t['dollar_pnl']
        peak = max(peak, cumulative)
        max_dd_dollars = max(max_dd_dollars, peak - cumulative)

    total_invested = len(trades) * investment_per_trade
    return {
        'max_drawdown_pct': (max_dd_dollars / total_invested * 100) if total_invested else 0,
        'max_drawdown_dollars': max_dd_dollars,
    }


def audit_fundamentals_for_trades(all_trades: list, sample_size: int, seed: int) -> None:
    """Point-in-time Fundamentals Auditor pass over a (sampled) subset of trades —
    mutates each sampled trade in place with a 'fundamentals_audit_score' field.

    This is genuinely point-in-time (not look-ahead-biased): audit_asof() only
    considers SEC filings that were actually filed before that trade's entry date.
    Catalyst Sentiment can't get the same treatment — yfinance's news feed has no
    historical archive, so scoring today's news against an old trade would be
    look-ahead bias. That agent instead just logs going forward (see
    src/agents/catalyst_sentiment.py + the daily email wiring) until enough real
    point-in-time history accumulates on its own.

    Real Claude API calls + SEC fetches, one per sampled trade — slow (each audit
    took ~15-50s in testing) and not free (~$0.05-0.15/call on claude-opus-5), which
    is why this is capped to `sample_size` trades by default rather than all of them.
    """
    from src.agents.fundamentals_auditor import FundamentalsAuditor, flags_to_score

    auditor = FundamentalsAuditor()
    if not auditor.available:
        print("\n--audit-fundamentals requested but ANTHROPIC_API_KEY isn't set — skipping.")
        return

    rng = random.Random(seed)
    sampled = all_trades if sample_size >= len(all_trades) else rng.sample(all_trades, sample_size)

    print(f"\nAuditing fundamentals (point-in-time) for {len(sampled)}/{len(all_trades)} trades "
          f"— this makes real Claude API calls, expect it to be slow...")
    for i, trade in enumerate(sampled):
        entry_date = date.fromisoformat(trade['period'])
        result = auditor.audit_asof(trade['ticker'], entry_date)
        trade['fundamentals_audit_score'] = flags_to_score(result['audit']) if result['audited'] else None
        if (i + 1) % 10 == 0:
            print(f"  ...{i + 1}/{len(sampled)} audited")


def run_walk_forward(universe_size: int, lookback_months: int, step_days: int, top_n: int,
                      max_hold_days: int, investment_per_trade: float, seed: int,
                      audit_fundamentals: bool = False, audit_sample_size: int = 40) -> dict:
    if seed is not None:
        random.seed(seed)

    latest_entry = date.today() - timedelta(days=max_hold_days)
    earliest_entry = latest_entry - timedelta(days=lookback_months * 30)
    entry_dates = []
    d = earliest_entry
    while d <= latest_entry:
        entry_dates.append(d)
        d += timedelta(days=step_days)

    print(f"Walk-forward backtest: {len(entry_dates)} entry dates from {earliest_entry} to {latest_entry}")
    print(f"Universe size: {universe_size} (seed={seed}), top {top_n} picks/date, max {max_hold_days}-day hold\n")

    universe = USStockUniverseFetcher().fetch_universe()
    sample = universe if universe_size >= len(universe) else random.sample(universe, universe_size)

    spy = yf.Ticker('SPY').history(period='2y')
    spy.index = spy.index.tz_localize(None)

    print(f"Fetching price history for {len(sample)} tickers (one-time cost — this is the slow part)...")
    histories = {}
    for i, ticker in enumerate(sample):
        try:
            h = yf.Ticker(ticker).history(period='2y')
            if h.empty or len(h) < 200:
                continue
            h.index = h.index.tz_localize(None)
            histories[ticker] = h
        except Exception as e:
            logger.debug(f"{ticker}: {e}")
        if (i + 1) % 100 == 0:
            print(f"  ...{i + 1}/{len(sample)} fetched, {len(histories)} usable")

    print(f"\n{len(histories)} tickers usable. Walking forward through {len(entry_dates)} dates...\n")

    all_trades = []
    for period_i, entry_date_d in enumerate(entry_dates):
        entry_ts = pd.Timestamp(entry_date_d)
        spy_asof = spy.loc[:entry_ts]
        if len(spy_asof) < 63:
            continue

        candidates = []
        for ticker, hist in histories.items():
            asof_data = hist.loc[:entry_ts]
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
            if signal['is_buy']:
                candidates.append((signal, current_price, hist))

        candidates.sort(key=lambda c: c[0]['score'], reverse=True)
        picks = candidates[:top_n]

        for signal, entry_price, hist in picks:
            result = simulate_trade(hist, entry_ts, entry_price, signal.get('stop_loss'), max_hold_days)
            if result is None:
                continue
            return_pct = (result['exit_price'] - entry_price) / entry_price * 100
            trade = {
                'period': entry_date_d.isoformat(), 'ticker': signal['ticker'], 'score': signal['score'],
                'entry_price': entry_price, 'exit_price': result['exit_price'],
                'exit_reason': result['exit_reason'], 'days_held': result['days_held'],
                'exit_date': result['exit_date'], 'return_pct': return_pct,
                'dollar_pnl': investment_per_trade * (return_pct / 100),
            }
            for comp in COMPONENTS:
                trade[comp] = (signal.get('details') or {}).get(comp, 0) or 0
            all_trades.append(trade)

        if (period_i + 1) % 5 == 0:
            print(f"  ...{period_i + 1}/{len(entry_dates)} periods walked, {len(all_trades)} trades so far")

    if audit_fundamentals and all_trades:
        audit_fundamentals_for_trades(all_trades, audit_sample_size, seed or 0)

    # Component correlations (needed by backtest_critic.py to detect drift between runs)
    component_correlations = {}
    if len(all_trades) >= 5:
        returns = [t['return_pct'] for t in all_trades]
        for comp in ['score'] + COMPONENTS:
            vals = [t[comp] for t in all_trades]
            component_correlations[comp] = pearson(vals, returns)

        audited = [t for t in all_trades if t.get('fundamentals_audit_score') is not None]
        if len(audited) >= 5:
            component_correlations['fundamentals_audit_score'] = pearson(
                [t['fundamentals_audit_score'] for t in audited],
                [t['return_pct'] for t in audited],
            )

    drawdown = compute_max_drawdown(all_trades, investment_per_trade)

    summary = {}
    if all_trades:
        returns = [t['return_pct'] for t in all_trades]
        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r <= 0]
        std_return = statistics.stdev(returns) if len(returns) > 1 else 0
        exit_reasons = {}
        for t in all_trades:
            exit_reasons[t['exit_reason']] = exit_reasons.get(t['exit_reason'], 0) + 1

        summary = {
            'total_trades': len(all_trades),
            'total_periods': len(entry_dates),
            'win_rate_pct': len(wins) / len(returns) * 100,
            'avg_return_pct': statistics.mean(returns),
            'median_return_pct': statistics.median(returns),
            'avg_win_pct': statistics.mean(wins) if wins else None,
            'avg_loss_pct': statistics.mean(losses) if losses else None,
            'std_return_pct': std_return,
            'sharpe_like': (statistics.mean(returns) / std_return) if std_return > 0 else 0,
            'avg_days_held': statistics.mean(t['days_held'] for t in all_trades),
            'exit_reasons': exit_reasons,
            **drawdown,
        }

    # exit_date isn't JSON-serializable (Timestamp) — stringify before saving/returning
    for t in all_trades:
        t['exit_date'] = str(t['exit_date'])

    return {
        'generated': datetime.now().isoformat(),
        'params': {
            'universe_size': universe_size, 'lookback_months': lookback_months,
            'step_days': step_days, 'top_n': top_n, 'max_hold_days': max_hold_days,
            'investment_per_trade': investment_per_trade, 'seed': seed,
        },
        'summary': summary,
        'component_correlations': component_correlations,
        'trades': all_trades,
    }


def print_report(result: dict):
    summary = result['summary']
    if not summary:
        print("No trades generated — try a bigger --universe-size or longer --lookback-months.")
        return

    print(f"\n{'='*78}")
    print(f"RESULTS: {summary['total_trades']} total trades across {summary['total_periods']} periods")
    print(f"{'='*78}\n")
    print(f"Win rate:              {summary['win_rate_pct']:.1f}%")
    print(f"Average return/trade:  {summary['avg_return_pct']:+.2f}%")
    print(f"Median return/trade:   {summary['median_return_pct']:+.2f}%")
    print(f"Avg win:               {summary['avg_win_pct']:+.2f}%" if summary['avg_win_pct'] is not None else "Avg win: n/a")
    print(f"Avg loss:              {summary['avg_loss_pct']:+.2f}%" if summary['avg_loss_pct'] is not None else "Avg loss: n/a")
    print(f"Return std dev:        {summary['std_return_pct']:.2f}%")
    print(f"Sharpe-like ratio:     {summary['sharpe_like']:.3f}")
    print(f"Max drawdown:          {summary['max_drawdown_pct']:.2f}% (${summary['max_drawdown_dollars']:,.2f})")
    print(f"Avg days held:         {summary['avg_days_held']:.1f}")
    print(f"Exit reasons:          {summary['exit_reasons']}")

    print(f"\n{'='*78}")
    print("COMPONENT CORRELATIONS (each component's value at entry vs. realized return)")
    print(f"{'='*78}")
    for comp, r in result['component_correlations'].items():
        r_str = f"{r:+.3f}" if r is not None else "n/a"
        print(f"  {comp:<20} r = {r_str}")


def save_result(result: dict) -> Path:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = HISTORY_DIR / f"walk_forward_{timestamp}.json"
    with open(path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    latest_path = HISTORY_DIR / "latest.json"
    with open(latest_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--universe-size', type=int, default=250,
                         help='Ticker sample size. Set to 3800+ (or any value >= universe size) for the full universe.')
    parser.add_argument('--lookback-months', type=int, default=9)
    parser.add_argument('--step-days', type=int, default=14)
    parser.add_argument('--top-n', type=int, default=10)
    parser.add_argument('--max-hold-days', type=int, default=60)
    parser.add_argument('--investment-per-trade', type=float, default=1000.0)
    parser.add_argument('--seed', type=int, default=42,
                         help='Fixed by default so reruns are reproducible. Omit for a fresh random draw.')
    parser.add_argument('--no-seed', action='store_true', help='Disable the fixed seed for a fresh random draw.')
    parser.add_argument('--audit-fundamentals', action='store_true',
                         help='Run the point-in-time Fundamentals Auditor (real Claude API calls) against a '
                              'sample of the resulting trades and report its correlation with realized return. '
                              'Needs ANTHROPIC_API_KEY; slow (~15-50s/trade) and not free — see --audit-sample-size.')
    parser.add_argument('--audit-sample-size', type=int, default=40,
                         help='Max trades to run through --audit-fundamentals (default 40, randomly sampled). '
                              'Set >= total trade count to audit all of them (slow/costly at full scale).')
    args = parser.parse_args()

    result = run_walk_forward(
        universe_size=args.universe_size, lookback_months=args.lookback_months,
        step_days=args.step_days, top_n=args.top_n, max_hold_days=args.max_hold_days,
        investment_per_trade=args.investment_per_trade, seed=None if args.no_seed else args.seed,
        audit_fundamentals=args.audit_fundamentals, audit_sample_size=args.audit_sample_size,
    )

    print_report(result)
    path = save_result(result)
    print(f"\nFull results + component correlations saved to {path}")
    print("(also copied to data/backtest_history/latest.json for backtest_critic.py to compare against)")


if __name__ == '__main__':
    main()
