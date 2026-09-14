#!/usr/bin/env python3
"""Fetch real recent news headlines for a list of tickers — used by the GUI
dashboard's Market tab news sections. Free/fast: reuses catalyst_sentiment.py's
headline fetcher directly (yfinance), no Claude/LLM call involved here at all.

Usage:
    python scripts/fetch_news.py --tickers AAPL,MSFT,NVDA --json-out out.json
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.catalyst_sentiment import _fetch_headlines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', type=str, required=True, help='Comma-separated ticker list')
    parser.add_argument('--json-out', type=str, required=True)
    args = parser.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    news = {}
    for ticker in tickers:
        print(f"Fetching news for {ticker}...")
        news[ticker] = _fetch_headlines(ticker, limit=5)

    out_path = Path(args.json_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        'generated': datetime.now().isoformat(),
        'tickers': tickers,
        'news': news,
    }, indent=2, default=str))
    print(f"Wrote news for {len(tickers)} tickers to {out_path}")


if __name__ == '__main__':
    main()
