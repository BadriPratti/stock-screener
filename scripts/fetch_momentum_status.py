#!/usr/bin/env python3
"""Classifies each ticker into a momentum "status" — hot / stable / basing /
avoid — using the same Phase + distance-from-50-SMA logic the real screening
engine (src/screening/signal_engine.py) already scores buy signals with, and
tracks how many consecutive calendar days a ticker has held its current
status (a running "day N of this trend" streak, persisted across runs).

Status buckets:
  hot    - Phase 2 uptrend, but stock is stretched >20% above its 50 SMA.
           Real momentum, but the entry-quality math in signal_engine.py
           penalizes chasing this — high risk/reward is already spent.
  stable - Phase 2 uptrend, healthy distance from the 50 SMA (<=20%) and the
           SMA is still rising. This is the "good entry zone."
  basing - Phase 1 (base building), or a Phase 2 stock whose 50 SMA has gone
           flat/rolling over — momentum stalling, not yet a downtrend.
  avoid  - Phase 3 (distribution) or Phase 4 (downtrend). Not a buy.

Usage:
    python scripts/fetch_momentum_status.py --tickers GKOS,NVDA --group shortlist --json-out out.json
"""
import argparse
import fcntl
import json
from datetime import date, datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf

from src.screening.phase_indicators import classify_phase
from src.utils.json_safe import sanitize_nan

HISTORY_PATH = Path(__file__).parent.parent / "data" / "momentum_status" / "history.json"
LOCK_PATH = HISTORY_PATH.parent / "history.lock"

STATUS_LABELS = {
    'hot': 'Hot — extended',
    'stable': 'Stable uptrend',
    'basing': 'Basing / cooling',
    'avoid': 'Avoid — downtrend',
}


def classify_status(phase_info: dict) -> str:
    phase = phase_info.get('phase', 0)
    distance_50 = phase_info.get('distance_from_50sma', 0)
    slope_50 = phase_info.get('slope_50', 0)

    if phase in (3, 4):
        return 'avoid'
    if phase == 1:
        return 'basing'
    if phase == 2:
        if distance_50 > 20:
            return 'hot'
        if slope_50 <= 0:
            return 'basing'
        return 'stable'
    return 'basing'  # phase 0 / insufficient data — treat as neutral, not a buy


def _load_history() -> dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return {}
    return {}


def _save_history(history: dict):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(sanitize_nan(history), indent=2), encoding="utf-8")


def update_streak(history: dict, ticker: str, status: str, today_str: str) -> dict:
    """Advances (or resets) the day-streak for one ticker. Safe to call many
    times on the same calendar day (idempotent) — the streak count only
    changes on an actual day-to-day transition.

    "days" counts CONSECUTIVE calendar days, not observations: if the ticker
    wasn't checked yesterday (e.g. the app was closed, or a fetch failed),
    the streak restarts from 1 today rather than pretending the gap didn't
    happen — a status observed on Sept 1 and next observed on Sept 13 is not
    a real 2-day streak, that would silently misstate how long the trend has
    actually held.
    """
    existing = history.get(ticker)
    today = date.fromisoformat(today_str)

    if existing and existing.get('last_seen') == today_str:
        if existing['status'] != status:
            # Flipped status within the same day — restart the streak from today.
            existing['status'] = status
            existing['since'] = today_str
            existing['days'] = 1
        # else: same status, same day — nothing to advance.
        return existing

    if existing and existing['status'] == status:
        last_seen = date.fromisoformat(existing['last_seen'])
        gap_days = (today - last_seen).days
        if gap_days == 1:
            existing['days'] = existing.get('days', 1) + 1
        else:
            # A gap of more than a day breaks the streak, even though the
            # status matches — we don't actually know it held continuously
            # through the days we didn't check.
            existing['since'] = today_str
            existing['days'] = 1
        existing['last_seen'] = today_str
        return existing

    record = {'status': status, 'since': today_str, 'days': 1, 'last_seen': today_str}
    history[ticker] = record
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', type=str, required=True)
    parser.add_argument('--group', type=str, default='misc')
    parser.add_argument('--json-out', type=str, required=True)
    args = parser.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    today_str = date.today().isoformat()

    # Fetch + classify (slow, network-bound) happens BEFORE the shared-file
    # lock is taken — a lock should only ever guard the fast in-memory
    # update, never be held across a network call.
    classified = {}  # ticker -> (status, phase_info)
    for ticker in tickers:
        print(f"Classifying momentum status for {ticker}...")
        try:
            price_data = yf.Ticker(ticker).history(period="1y", interval="1d")
            if price_data.empty or len(price_data) < 200:
                print(f"  {ticker}: insufficient price history, skipping")
                continue
            current_price = float(price_data['Close'].iloc[-1])
            phase_info = classify_phase(price_data, current_price)
            classified[ticker] = (classify_status(phase_info), phase_info)
        except Exception as e:
            print(f"  {ticker}: failed ({e})")

    # Multiple dashboard views can each kick off their own momentum-status
    # job around the same time, all sharing this one history file — an
    # unlocked load-modify-save here would let whichever job saves last
    # silently discard another job's ticker updates. Holding an exclusive
    # file lock for this whole read-modify-write section serializes them:
    # the second job blocks until the first finishes, then reads the
    # already-updated state instead of overwriting it.
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {}
    with open(LOCK_PATH, 'w') as lockfile:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        try:
            history = _load_history()
            for ticker, (status, phase_info) in classified.items():
                record = update_streak(history, ticker, status, today_str)
                snapshot[ticker] = {
                    'status': status,
                    'label': STATUS_LABELS[status],
                    'days': record['days'],
                    'since': record['since'],
                    'phase': phase_info.get('phase'),
                    'distance_from_50sma': phase_info.get('distance_from_50sma'),
                }
            _save_history(history)
        finally:
            fcntl.flock(lockfile, fcntl.LOCK_UN)

    out_path = Path(args.json_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sanitize_nan({
        'generated': datetime.now().isoformat(),
        'group': args.group,
        'tickers': tickers,
        'status': snapshot,
    }), indent=2), encoding="utf-8")
    print(f"Wrote momentum status for {len(snapshot)} tickers to {out_path}")


if __name__ == '__main__':
    main()
