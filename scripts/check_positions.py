#!/usr/bin/env python3
"""Quick script to check your current Fidelity positions from a CSV export.

Usage:
    python scripts/check_positions.py --csv path/to/your_export.csv

This script:
- Reads tickers, quantities, entry prices from a Fidelity Positions CSV
- Does NOT read account balances
- Does NOT execute any trades
- Does NOT touch your Fidelity login at all — no credentials involved

How to get the CSV: Fidelity website -> Accounts & Trade -> Positions ->
click the download/export icon near the top of the positions table.
"""

import argparse
import logging
import sys
from datetime import datetime

sys.path.insert(0, '.')
from src.data.fidelity_positions import load_positions, format_positions_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Fidelity position checker (read-only, CSV-based)')
    parser.add_argument('--csv', type=str, required=True,
                         help='Path to a Fidelity Positions CSV export')
    args = parser.parse_args()

    print("\n" + "="*60)
    print("FIDELITY POSITION CHECKER (Read-Only, from CSV)")
    print("="*60)
    print("\nThis will:")
    print("  ✓ Read tickers, quantities and entry prices from the CSV")
    print("  ✗ NOT read account balance or portfolio value")
    print("  ✗ NOT execute any trades or modifications")
    print("\n" + "="*60 + "\n")

    try:
        positions = load_positions(args.csv)
    except (FileNotFoundError, ValueError) as e:
        print(f"\nERROR: {e}\n")
        sys.exit(1)

    if not positions:
        print("="*60)
        print("No open positions found in the CSV")
        print("="*60)
        return

    report = format_positions_report(positions)
    print(report)

    export = input("\nExport to file? (y/n): ").strip().lower()
    if export == 'y':
        filename = f"fidelity_positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        print(f"\n✓ Exported to: {filename}")


if __name__ == '__main__':
    main()
