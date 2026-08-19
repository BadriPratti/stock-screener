#!/usr/bin/env python3
"""Run the Fundamentals Auditor (Part 3) against specific tickers, or by default
against the most recent Top 20 shortlist.

Usage:
    python scripts/run_fundamentals_auditor.py                    # audits data/daily_scans/top20_latest.json
    python scripts/run_fundamentals_auditor.py --tickers AAPL,MSFT,NVDA
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.fundamentals_auditor import audit_candidates

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TOP20_PATH = Path(__file__).parent.parent / "data" / "daily_scans" / "top20_latest.json"


def _tickers_from_top20() -> list:
    if not TOP20_PATH.exists():
        return []
    data = json.loads(TOP20_PATH.read_text())
    return [entry["ticker"] for entry in data.get("top20", [])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", type=str, default=None, help="Comma-separated tickers (default: latest Top 20)")
    args = parser.parse_args()

    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    else:
        tickers = _tickers_from_top20()
        if not tickers:
            logger.error(f"No --tickers given and no shortlist found at {TOP20_PATH}. Run a scan first or pass --tickers.")
            sys.exit(1)
        logger.info(f"Auditing latest Top 20 shortlist: {len(tickers)} tickers")

    results = audit_candidates(tickers)

    print("\n" + "=" * 78)
    print("FUNDAMENTALS AUDIT SUMMARY")
    print("=" * 78)
    for r in results:
        if not r["audited"]:
            print(f"{r['ticker']:<8} SKIPPED ({r['reason']})")
            continue
        audit = r["audit"]
        print(f"\n{r['ticker']:<8} {r['filing_type']} ({r['filing_date']}) — {audit['overall_assessment']}")
        for flag in audit["red_flags"]:
            print(f"  🔴 [{flag['severity']}] {flag['flag']}")
        for flag in audit["green_flags"]:
            print(f"  🟢 [{flag['severity']}] {flag['flag']}")
        print(f"  Summary: {audit['summary']}")

    print(f"\nFull results saved to data/fundamentals_audit/latest.json")


if __name__ == "__main__":
    main()
