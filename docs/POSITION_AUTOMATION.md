# Position Management Automation

## Overview

This used to support two modes — manual (interactive Robinhood login) and
automated (GitHub Actions with stored Robinhood credentials). Since migrating
to Fidelity, only manual mode is available: **Fidelity has no supported
unofficial API**, so there's no credential-based automation path to build a
CI equivalent around. `automated_position_report.py` still exists but is now
just a stub that explains this and exits — it's not wired into any workflow.

### Manual Mode (On Your Local Machine)

```bash
python manage_positions.py --csv ~/Downloads/Portfolio_Positions.csv
```

**When to use:**
- When you have 5-10 minutes in the morning
- Whenever you want to check stop losses manually
- For full control and review before taking action

**What happens:**
- Reads positions from a CSV you export yourself from Fidelity's website
  (Accounts & Trade → Positions → Download) — no login, no credentials
  touched by this tool at all
- Analyzes using cached market data (no extra API calls)
- Shows recommendations in terminal
- Optional: Export to file

**Security:**
- No credentials of any kind are involved
- The CSV itself contains real account data — don't commit it to Git

---

## Why Cache Data?

The position manager uses cached market data from your daily scan:
- ✓ No additional API calls to yfinance
- ✓ Lightning fast analysis
- ✓ Consistent with daily screening
- ✓ Zero impact on rate limits

### How It Works

```
Daily Scan (run_optimized_scan.py)
├─ Fetches 1 year price history for 3800+ stocks
├─ Caches all price data (1 year × 3800 = ~14MB)
└─ Caches fundamentals in Git

Position Analysis (manage_positions.py --csv <file>)
├─ Reads positions from your Fidelity CSV export
├─ Looks up cached price data for each position
├─ Calculates Phase, SMA, swing lows
└─ Generates recommendations
```

No extra yfinance calls! Everything is cached from the daily scan — only
your positions (quantity + entry price) come from the CSV.

---

## Troubleshooting

### "Couldn't find a Symbol column"

You either downloaded a different Fidelity report than the Positions CSV, or
Fidelity changed their export format. Open the CSV and check the header row —
see `docs/FIDELITY_SETUP.md` for how to fix column matching if needed.

### "Insufficient price data for analysis"

Position was added after the daily scan ran. It will be analyzed once the
next scan's cache includes it.

### "Invalid entry price (zero or negative)"

A row in the CSV has a corrupted or missing average-cost-basis value —
the loader skips it and logs a warning rather than passing bad data through.

---

## If Automated Reporting Becomes Worth Building Later

There's no clean way to auto-fetch a fresh Fidelity CSV in a headless GitHub
Actions run today. If this becomes worth solving, the realistic options are:

1. You manually download+commit a fresh CSV to a private location the
   workflow can read (still a manual step, just decoupled from running
   `manage_positions.py` yourself).
2. A future Fidelity-supported API (Fidelity has talked about broader
   developer API access at times — worth rechecking periodically).

Neither is implemented here — this is a note for future reference, not a
current feature.

---

## Privacy & Security

### What's Stored?

**Nothing.** No credentials, no tokens, no login state. The only sensitive
artifact is the CSV file itself, which you control entirely — it never
leaves your machine unless you choose to move it somewhere.

### What's NOT Stored?

- ✗ Account balance
- ✗ Cash available
- ✗ Portfolio value
- ✗ Order history
- ✗ Any login credentials

The integration is **READ-ONLY**, offline, and CSV-based.

---

## Next Steps

1. **Export your positions from Fidelity's website** (Accounts & Trade → Positions → Download)

2. **Run manual mode:**
   ```bash
   python manage_positions.py --csv ~/Downloads/Portfolio_Positions.csv
   ```

3. **Review reports:**
   - Check `data/position_reports/` for generated reports
   - Verify recommendations make sense
   - Manually adjust stops on Fidelity
