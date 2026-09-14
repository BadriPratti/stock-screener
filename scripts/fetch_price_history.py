#!/usr/bin/env python3
"""Fetch recent daily close price history for a list of tickers — used by the
GUI dashboard's Shortlist charts and the "Live" auto-refresh feature. Free/fast:
yfinance only, no LLM call involved.

Usage:
    python scripts/fetch_price_history.py --tickers AAPL,MSFT,NVDA --json-out out.json
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf


def _fetch_history(ticker: str):
    """Last ~180 trading days of close prices. Drops any NaN close (e.g. an
    in-progress trading day with no closing print yet) — a bare NaN would
    otherwise get written by json.dumps as an invalid, unparseable JSON token.
    Never raises."""
    try:
        hist = yf.Ticker(ticker).history(period="9mo")
        closes = hist["Close"].iloc[-180:]
        return [
            {"date": str(idx.date()) if hasattr(idx, "date") else str(idx), "close": round(float(c), 2)}
            for idx, c in closes.items() if pd.notna(c)
        ]
    except Exception as e:
        print(f"Failed to fetch price history for {ticker}: {e}")
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', type=str, required=True, help='Comma-separated ticker list')
    parser.add_argument('--json-out', type=str, required=True)
    args = parser.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    prices = {}
    for ticker in tickers:
        print(f"Fetching price history for {ticker}...")
        prices[ticker] = _fetch_history(ticker)

    out_path = Path(args.json_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        'generated': datetime.now().isoformat(),
        'tickers': tickers,
        'prices': prices,
    }, indent=2, default=str), encoding="utf-8")
    print(f"Wrote price history for {len(tickers)} tickers to {out_path}")


if __name__ == '__main__':
    main()
