"""Fidelity position loader — reads positions from a CSV you export yourself
from Fidelity's website. No login automation, no credentials handled by this
tool: Fidelity actively blocks scraping/unofficial API access, unlike
Robinhood's already-gray-area unofficial API that the old
src/data/robinhood_positions.py used.

How to export (Fidelity website):
  Accounts & Trade -> Positions -> click the download/export icon near the
  top of the positions table -> saves "Portfolio_Positions_<date>.csv".

Produces the same dict shape src/analysis/position_manager.py expects
(ticker, average_buy_price, current_price, quantity) — a drop-in replacement
for RobinhoodPositionFetcher.fetch_positions() from the caller's point of view.

If Fidelity's actual export from your account uses different column names
than expected below, share the header row and COLUMN_ALIASES can be adjusted.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Fidelity's standard Positions CSV export column names, matched
# case-insensitively. A couple of common aliases are tolerated in case the
# export format varies slightly by account type.
COLUMN_ALIASES = {
    'ticker': ['symbol'],
    'description': ['description'],
    'quantity': ['quantity', 'qty'],
    'last_price': ['last price', 'lastprice'],
    'current_value': ['current value'],
    'average_cost_basis': ['average cost basis', 'avg cost basis', 'cost basis per share'],
    'cost_basis_total': ['cost basis total', 'total cost basis'],
}

# Fidelity's export includes cash/money-market sweep lines and a trailing
# disclaimer footer that aren't real equity positions — skip these tickers.
_NON_POSITION_TICKERS = {'CASH', 'SPAXX', 'FDRXX', 'FZFXX', 'PENDING ACTIVITY'}


def _clean_money(val: Optional[str]) -> Optional[float]:
    if val is None:
        return None
    val = val.strip().replace('$', '').replace(',', '')
    if val in ('', '--', 'n/a', 'N/A'):
        return None
    negative = val.startswith('(') and val.endswith(')')
    if negative:
        val = val[1:-1]
    try:
        num = float(val)
        return -num if negative else num
    except ValueError:
        return None


def _find_column(headers: List[str], aliases: List[str]) -> Optional[str]:
    lowered = {h.strip().lower(): h for h in headers}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def load_positions(csv_path: str) -> List[Dict]:
    """Parse a Fidelity Positions CSV export into position dicts.

    Returns dicts with: ticker, average_buy_price, current_price, quantity,
    description, current_value (the last two informational only).
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.reader(f))

    if not rows:
        return []

    header = rows[0]
    col = {name: _find_column(header, aliases) for name, aliases in COLUMN_ALIASES.items()}
    if col['ticker'] is None:
        raise ValueError(
            f"Couldn't find a Symbol column in {csv_path}. Headers found: {header}. "
            "Fidelity may have changed their export format — share this header row to fix it."
        )

    idx = {name: header.index(c) for name, c in col.items() if c is not None}

    def cell(row, name):
        i = idx.get(name)
        return row[i] if i is not None and len(row) > i else None

    positions = []
    for row in rows[1:]:
        ticker = (cell(row, 'ticker') or '').strip().upper()
        if not ticker or ticker in _NON_POSITION_TICKERS:
            continue
        if not any(c.isalpha() for c in ticker):
            continue  # skips blank/disclaimer rows that slipped past the ticker check

        quantity = _clean_money(cell(row, 'quantity'))
        last_price = _clean_money(cell(row, 'last_price'))
        avg_cost = _clean_money(cell(row, 'average_cost_basis'))
        if quantity is None or last_price is None or avg_cost is None:
            logger.warning(f"Skipping {ticker}: missing quantity/price/cost-basis in CSV row")
            continue

        unrealized_pl_pct = (last_price - avg_cost) / avg_cost * 100 if avg_cost else 0.0

        positions.append({
            'ticker': ticker,
            'quantity': quantity,
            'average_buy_price': avg_cost,
            'current_price': last_price,
            'unrealized_pl_pct': unrealized_pl_pct,
            'description': (cell(row, 'description') or '').strip(),
            'current_value': _clean_money(cell(row, 'current_value')),
        })

    logger.info(f"Loaded {len(positions)} positions from {csv_path}")
    return positions


def format_positions_report(positions: List[Dict]) -> str:
    """Format positions as a readable text report (mirrors the old
    RobinhoodPositionFetcher.format_positions_report output style)."""
    if not positions:
        return "No open positions"

    from datetime import datetime

    lines = ["=" * 60, "CURRENT FIDELITY POSITIONS (from CSV export)",
              f"Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 60, ""]

    for i, pos in enumerate(positions, 1):
        lines.append(f"{i}. {pos['ticker']}")
        lines.append(f"   Shares: {pos['quantity']}")
        lines.append(f"   Entry: ${pos['average_buy_price']:.2f}")
        lines.append(f"   Current: ${pos['current_price']:.2f}")
        pl_sign = "+" if pos['unrealized_pl_pct'] >= 0 else ""
        lines.append(f"   P/L: {pl_sign}{pos['unrealized_pl_pct']:.2f}%")
        lines.append("")

    lines.append("=" * 60)
    lines.append(f"Total positions: {len(positions)}")
    lines.append("=" * 60)
    return "\n".join(lines)
