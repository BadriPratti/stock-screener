#!/usr/bin/env python3
"""Position management tool - integrates Fidelity positions with stop loss recommendations.

Reads your current Fidelity positions from a CSV you export yourself and
analyzes each one to recommend:
- When to trail stops up
- Exact new stop loss levels
- When to take partial profits
- Warnings for Phase 3/4 transitions

ONLY analyzes SHORT-TERM positions (held <1 year) to avoid disrupting long-term tax treatment.

How to get the CSV: Fidelity website -> Accounts & Trade -> Positions ->
click the download/export icon near the top of the positions table.

Usage:
    python manage_positions.py --csv ~/Downloads/Portfolio_Positions.csv
    python manage_positions.py --csv positions.csv --export  # Save report to file
"""

import json
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

from src.data.fidelity_positions import load_positions
from src.analysis.position_manager import PositionManager
from src.utils.json_safe import sanitize_nan

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Position Management with Stop Loss Recommendations')
    parser.add_argument('--csv', type=str, required=True,
                         help='Path to a Fidelity Positions CSV export (Accounts & Trade -> Positions -> Download)')
    parser.add_argument('--export', action='store_true', help='Export report to file')
    parser.add_argument('--entry-dates', type=str, help='JSON file with entry dates (optional)')
    parser.add_argument('--json-out', type=str, default=None,
                         help='Optional path to also write structured JSON results (used by the GUI dashboard)')
    args = parser.parse_args()

    print("\n" + "="*80)
    print("POSITION MANAGEMENT - STOP LOSS RECOMMENDATIONS")
    print("="*80)
    print("\nThis tool will:")
    print("  - Read your current Fidelity positions from the CSV you exported")
    print("  - Analyze each position's technical structure")
    print("  - Recommend stop loss adjustments for SHORT-TERM holdings")
    print("  - Identify when to take partial profits, and good add-on points")
    print("  - LONG-TERM positions (1+ years) are EXCLUDED")
    print("      (to preserve favorable capital gains tax treatment)")
    print("\n" + "="*80 + "\n")

    try:
        print(f"Reading positions from {args.csv}...")
        positions = load_positions(args.csv)
    except (FileNotFoundError, ValueError) as e:
        print(f"\nERROR: {e}\n")
        sys.exit(1)

    if not positions:
        print("="*80)
        print("No open positions found in the CSV")
        print("="*80)
        if args.json_out:
            _write_json_out(args, {'position_analyses': [], 'summary': {'total_positions': 0}, 'urgent_actions': []})
        return

    print(f"Found {len(positions)} positions\n")

    # Load entry dates if provided
    entry_dates = None
    if args.entry_dates:
        try:
            with open(args.entry_dates, 'r') as f:
                dates_data = json.load(f)
                from datetime import datetime as dt
                entry_dates = {
                    ticker: dt.fromisoformat(date_str)
                    for ticker, date_str in dates_data.items()
                }
            print(f"Loaded entry dates for {len(entry_dates)} tickers\n")
        except Exception as e:
            print(f"Could not load entry dates: {e}")
            print("Proceeding without entry date data (will not filter by tax treatment)\n")

    # Analyze positions
    print("Analyzing positions and calculating stop recommendations...\n")
    manager = PositionManager()
    analysis = manager.analyze_portfolio(positions, entry_dates)

    # Generate report
    report = manager.format_portfolio_report(analysis)
    print(report)

    # Export if requested
    if args.export:
        output_dir = Path("./data/position_reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = output_dir / f"position_management_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write(report)

        print(f"\nReport exported to: {filename}")

    if args.json_out:
        _write_json_out(args, analysis)


def _write_json_out(args, analysis):
    """Optional structured JSON alongside the printed report — used by the GUI
    dashboard's Positions view. Never affects stdout output or the CLI usage."""
    out_path = Path(args.json_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sanitize_nan(analysis), indent=2, default=str))


if __name__ == '__main__':
    main()
