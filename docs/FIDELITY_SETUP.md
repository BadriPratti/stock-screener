# Fidelity Position Loader - READ ONLY, CSV-Based

This integration reads your current stock positions from a CSV you export yourself from Fidelity's website. There is no login automation and no credentials are ever entered into this tool — Fidelity actively blocks unofficial API access, so this is a manual export/import step, not a live integration.

## What It Does ✓

- Reads tickers of stocks you currently own
- Shows entry prices (average cost basis)
- Shows current prices and unrealized P/L %
- Shows number of shares

## What It Does NOT Do ✗

- Does NOT log into your Fidelity account
- Does NOT read account balance, portfolio value, buying power, or cash
- Does NOT execute any trades
- Does NOT modify any positions
- Does NOT place any orders

**This is READ-ONLY, and entirely offline once you have the CSV.**

---

## Setup

### 1. Export Your Positions From Fidelity

On Fidelity's website: **Accounts & Trade → Positions →** click the download/export icon near the top of the positions table. This saves a CSV (e.g. `Portfolio_Positions_Aug-18-2026.csv`) to your Downloads folder.

No environment variables or credentials are needed — just the file.

**Security note**: Don't commit your exported CSV to Git (it contains real account data). Keep it outside the repo or add its filename pattern to `.gitignore` if you save it inside the project folder.

---

## Usage

### Quick Check - See Your Positions

```bash
python scripts/check_positions.py --csv ~/Downloads/Portfolio_Positions.csv
```

This will:
1. Parse the CSV (skips cash/money-market sweep lines and Fidelity's footer disclaimer automatically)
2. Display formatted report:
   - Ticker
   - Number of shares
   - Entry price (average cost basis)
   - Current price (last price at export time)
   - Unrealized P/L %
3. Option to export to text file

### Example Output

```
============================================================
CURRENT FIDELITY POSITIONS (from CSV export)
Loaded: 2026-08-18 10:30:15
============================================================

1. AAPL
   Shares: 50
   Entry: $175.50
   Current: $182.30
   P/L: +3.87%

2. MSFT
   Shares: 25
   Entry: $380.00
   Current: $385.50
   P/L: +1.45%

3. NVDA
   Shares: 30
   Entry: $495.00
   Current: $489.20
   P/L: -1.17%

============================================================
Total positions: 3
============================================================
```

**Note**: unlike the old Robinhood live-fetch, "Current price" here is a snapshot from whenever you downloaded the CSV, not real-time. `manage_positions.py` re-fetches current market prices itself (via cached yfinance data) rather than relying on the CSV's price column, so its recommendations stay fresh even if the CSV is a day or two old — only quantity and entry price actually need to come from the CSV.

---

## Use Cases

### 1. Check Before Scanner Runs

See what you already own so you don't get duplicate buy signals:

```python
from src.data.fidelity_positions import load_positions

positions = load_positions("path/to/your_export.csv")
owned_tickers = [p['ticker'] for p in positions]
print(f"Currently own: {owned_tickers}")
```

### 2. Compare Scanner Signals to Current Holdings

```python
current_positions = load_positions("path/to/your_export.csv")
owned = {p['ticker'] for p in current_positions}

buy_signals = [...]  # From scanner
new_opportunities = [s for s in buy_signals if s['ticker'] not in owned]
```

### 3. Auto-Update Trade Tracker

Load your positions and compare to your spreadsheet to find:
- Positions you forgot to log
- Exit prices when you've sold
- Current unrealized P/L

---

## Troubleshooting

### "Couldn't find a Symbol column"

Fidelity may have changed their export format, or you downloaded a different report than the Positions CSV. Open the CSV and check the header row — if it doesn't have a `Symbol` column, share the header row and `COLUMN_ALIASES` in `src/data/fidelity_positions.py` can be updated to match.

### A position is missing from the output

The loader skips any row without a usable Quantity/Last Price/Average Cost Basis (logged as a warning), and skips cash/money-market sweep lines (SPAXX, FDRXX, etc.) and Fidelity's trailing disclaimer text — these aren't real equity positions.

---

## Position Management - Stop Loss Recommendations

### Overview

`manage_positions.py` reads your Fidelity positions from the CSV and analyzes each one to recommend:
- When to trail your stop losses up
- Exact new stop loss levels with detailed rationale
- When to take partial profits (25-50%)
- Warnings for Phase 3/4 transitions

**Important**: Only analyzes **SHORT-TERM** positions (held <1 year). Long-term positions are excluded to preserve favorable capital gains tax treatment.

### Usage

```bash
python manage_positions.py --csv ~/Downloads/Portfolio_Positions.csv
```

With entry dates for tax treatment filtering:
```bash
python manage_positions.py --csv ~/Downloads/Portfolio_Positions.csv --entry-dates entry_dates.json
```

Export report to file:
```bash
python manage_positions.py --csv ~/Downloads/Portfolio_Positions.csv --export
```

### What It Recommends

**5-10% Gain**: Trail to Breakeven
- Moves stop to entry price (risk-free position)
- "If it pulls back, exit at breakeven with no loss"

**10-20% Gain**: Trail to +5% Profit or 50 SMA
- Locks in minimum 5% profit
- Trails to 50 SMA if it's higher
- "Let winner run while protecting gains"

**20-30% Gain**: Take Partial + Trail Remainder
- Recommends selling 25-30% at current price
- Trail remaining 70-75% with stop at +10% profit
- "Lock in some gains, let runners go"

**30%+ Gain**: Take 50% + Trail Tight
- Recommends selling 50% at current price
- Trail remaining 50% very tight (near 50 SMA)
- "Major winner - secure profits, give last piece tight room"

### Entry Dates JSON Format

Create an `entry_dates.json` file to track when you entered each position:

```json
{
  "AAPL": "2024-10-18T00:00:00",
  "MSFT": "2023-05-10T00:00:00",
  "NVDA": "2024-11-13T00:00:00"
}
```

**Why this matters**:
- Positions held 365+ days = Long-term capital gains (15-20% tax)
- Positions held <365 days = Short-term capital gains (ordinary income rate)
- The tool WON'T recommend adjusting stops for long-term positions to avoid triggering early sale

### Technical Analysis Used

Each position is analyzed for:
- Current Phase (1-4 stage analysis)
- 50-day SMA (key support level)
- 200-day SMA (major trend indicator)
- Recent swing lows (last 10 days)
- Distance from entry price

Stop recommendations use:
- Breakeven stops for small winners
- Profit-based stops for medium winners
- SMA-based trailing stops when above 50 SMA
- Tight trailing for big winners (30%+)

---

## Manual Trading Only

This tool is for **information only**. You still:
- Manually review buy signals
- Manually review stop loss recommendations
- Manually place orders on Fidelity
- Manually adjust stop losses on the platform
- Manually exit positions

The integration provides **recommendations** - you make all trading decisions.
