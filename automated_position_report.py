#!/usr/bin/env python3
"""Automated position reporting - NOT CURRENTLY SUPPORTED for Fidelity.

This used to run as part of a GitHub Actions workflow, logging into Robinhood
with stored credentials (via the unofficial robin_stocks library) to fetch
positions headlessly. Fidelity has no equivalent unofficial API — position
data now comes from a CSV you export yourself from Fidelity's website, which
means it can't be fetched automatically in a headless CI run the way
Robinhood's login could.

For position analysis now, export your positions CSV from Fidelity
(Accounts & Trade -> Positions -> Download) and run:
    python manage_positions.py --csv path/to/your_export.csv

This script is left in place in case a Fidelity automation path (e.g. you
manually drop a fresh CSV somewhere this job can read) becomes worth wiring
up later — it currently just exits without doing anything.
"""

import sys

print("automated_position_report.py: not supported for Fidelity (no headless-fetchable API).")
print("Export your positions from Fidelity's website and run:")
print("  python manage_positions.py --csv path/to/your_export.csv")
sys.exit(0)
