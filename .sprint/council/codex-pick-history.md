Reading additional input from stdin...
OpenAI Codex v0.154.0
--------
workdir: /Users/badripratti/Desktop/stock-screener
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: medium
reasoning summaries: none
session id: 01a0bf2e-9c3b-7751-ad4c-481846618c8e
--------
user
You are participating in an Engineering Council (full council — HARD-classified: new data subsystem + CI workflow changes + UI).

Do NOT modify any files. Investigation and design proposal only.

Repository: /Users/badripratti/Desktop/stock-screener

User's request (verbatim): "Are we keeping track of the stocks we said before? I feel like we are re-doing our calculation fresh every time — we need a way to keep track of the stocks we said so that I know what stocks have been consistently well over time."

Problem: each scan run overwrites data/daily_scans/shortlist_latest.json (Top 5 shortlist) and top20_latest.json (Top 20 pool) with a fresh calculation. Nothing persists which tickers were picked on prior days, so the user can't see which stocks are consistently strong over time (e.g. "on the shortlist 4 of the last 5 scan days", "3-day streak", "first seen 9/14, avg score 118"). Design a persistent pick-history ledger + aggregate consistency stats, backfilled from existing history where reliable, kept current by the automated GitHub Actions workflows, and surfaced in the dashboard.

Read these before proposing anything:
- run_optimized_scan.py (where top20_latest.json / shortlist_latest.json are written, _atomic_write_json, save_report, the buy_signals list, main())
- .github/workflows/daily_screening_git_storage.yml and .github/workflows/midday_quick_scan.yml (what each runs, with which flags, what each `git add`s and commits, timing/cron, and whether either does any pull/rebase before push)
- scripts/fetch_momentum_status.py and data/momentum_status/history.json (an existing per-ticker history+streak precedent, including its fcntl file locking and how it counts "consecutive days") and how dashboard.py exposes it (/api/momentum-status/<group>) and how static/js/core/ui-helpers.js paints it onto the UI (loadMomentumStatus / paintMomentumSlots)
- dashboard.py (parse_scan_file, /api/shortlist, /api/top20, /api/scan, get_scan_files, sync)
- static/js/views/shortlist.js, static/js/views/market.js, static/js/core/router.js and templates/dashboard.html (nav groups) to understand where history could be surfaced
- The data you would backfill from: `git log --format='%h %ci %s' -- data/daily_scans/shortlist_latest.json` and the same for top20_latest.json (use `git show <hash>:<path>` to read historic versions — read-only git commands are fine), and the dated data/daily_scans/optimized_scan_*.txt reports. Verify for yourself how reliable/comparable each source is: which snapshots came from the daily full-universe run versus the midday run, what universe size each scanned (check the "Analyzed:"/"Total Universe:" header lines in the .txt reports and the workflow flags), which are real automated runs versus manual local commits, and what the earliest trustworthy date is.

Independently investigate and propose:

1. Your understanding of the problem, and what "consistently well over time" should concretely mean as measurable stats (appearances in last N scan days, consecutive-scan streak, first/last seen, average/trend of score, best rank...). Define "a day" precisely — calendar day vs. trading-day scan, weekends/holidays, days with two scans, days with no scan — and say which streak definition you'd use and why. Note that the existing momentum streak logic breaks a streak on any gap of more than 1 calendar day; think about what that does over a weekend and whether the new ledger should copy it.
2. What exactly to track: shortlist only, Top 20, all buy signals (the report only persists top 50), or several separate "lists" keyed by source — and the data-integrity implications of the daily and midday workflows producing differently-scoped lists into the same output file.
3. Storage design: file format/location/schema (append-only event log of daily snapshots vs. per-ticker aggregate vs. both; JSON vs. JSONL vs. SQLite), size growth, and whether aggregates should be stored or derived on read.
4. Who writes it and when: inside run_optimized_scan.py's process, a separate post-scan script step in the workflow, or derived on demand from committed snapshots. Address idempotency (re-running the same day must not double count), the two workflows, concurrent pushes to main (does the current commit/push step tolerate two workflows racing on the same file?), and what happens when the local dashboard also runs scans (the Full Scan view runs run_optimized_scan.py locally).
5. Backfill: exactly what can be reconstructed reliably from git history / dated reports, what should be excluded and why, how to mark backfilled vs. live entries, and a concrete one-time backfill procedure.
6. Backend/API surface (new route(s), shape of response, how the dashboard picks it up after `git pull`).
7. UI surfaces: badges on Shortlist cards, a column on Market's Top 20/Buy tables, a dedicated leaderboard/consistency view, or some combination — recommend a concrete scope for this sprint and what to defer. Note existing patterns to reuse (momentum badge slot painting) and this app's constraints (native ES modules, no framework/build step; charts.js is a classic script).
8. Relevant files to touch and a suggested task breakdown/ordering (mark which pieces are independent and which share files).
9. Alternatives considered and rejected.
10. Risks and edge cases (ticker symbol changes/delistings, a scan that fails or produces zero candidates, a day with only a midday scan, timezone/date-key boundaries, schema evolution, corrupt/partial ledger file, the ledger growing stale if the laptop app isn't synced).
11. Testing strategy consistent with this repo (pytest for Python — see tests/test_dashboard_jobs.py and tests/test_current_price_flow.py; plain-Node scripts for JS under tests/js/) and a way to verify the live workflow change without waiting for the next cron (workflow_dispatch exists).
12. Anything another engineer might easily miss.

Do not assume Claude's conclusion is correct — you have not been told what Claude proposed. Ground everything in the actual repository code and the actual historical data, not assumptions.
codex
I’ll audit the specified code, workflows, and historical commits/reports read-only, then return a concrete design with explicit reliability boundaries and implementation sequencing. No files will be changed.
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g '"'!node_modules'"' -g '"'!venv'"' -g '"'!env'"' | head -50 && git status --short && rg -n \"top20_latest|shortlist_latest|_atomic_write_json|def save_report|buy_signals|def main\" run_optimized_scan.py && sed -n '1,260p' .github/workflows/daily_screening_git_storage.yml && sed -n '1,260p' .github/workflows/midday_quick_scan.yml" in /Users/badripratti/Desktop/stock-screener
 succeeded in 8ms:
56:def _atomic_write_json(path, data):
66:def save_report(results, buy_signals, sell_signals, spy_analysis, breadth, output_dir="./data/daily_scans"):
99:    if len(buy_signals) > 0:
100:        output.append(f"🟢 Buy Signals: {len(buy_signals)}")
102:        output.append(f"Buy Signals: {len(buy_signals)}")
116:    output.append(f"🟢 TOP BUY SIGNALS (Score >= 70) - {len(buy_signals)} Total")
120:    if buy_signals:
121:        for i, signal in enumerate(buy_signals[:50], 1):
219:        if len(buy_signals) > 50:
221:            output.append(f"ADDITIONAL BUYS ({len(buy_signals)-50} more)")
223:            remaining = [s['ticker'] for s in buy_signals[50:]]
315:def main():
418:        buy_signals = []
439:                        buy_signals.append(signal)
441:        buy_signals = sorted(buy_signals, key=lambda x: x['score'], reverse=True)
471:        tickers_of_interest = {s['ticker'] for s in buy_signals} | {s['ticker'] for s in sell_signals}
476:            for signal in buy_signals + sell_signals:
502:                for signal in buy_signals:
512:        buy_tickers = {s['ticker'] for s in buy_signals}
526:        top20_path = Path("./data/daily_scans/top20_latest.json")
528:        if buy_signals:
530:            top20 = build_top20(buy_signals, reddit_mentions, insider_signals)
531:        # Always write top20_latest.json, even when empty — otherwise a scan
539:        _atomic_write_json(top20_path, {
548:        # Only run on the Top 20 shortlist, not the full buy_signals pool, to keep
576:            # Persist alongside top20_latest.json so the local GUI dashboard can
579:            shortlist_path = Path("./data/daily_scans/shortlist_latest.json")
581:            _atomic_write_json(shortlist_path, {
591:            # Same staleness issue as top20_latest.json above: a daily run
598:            shortlist_path = Path("./data/daily_scans/shortlist_latest.json")
600:            _atomic_write_json(shortlist_path, {
611:        save_report(results, buy_signals, sell_signals, spy_analysis, breadth)
616:            buy_signals, sell_signals, spy_analysis, breadth, top20=top20,
637:        logger.info(f"Buy signals: {len(buy_signals)}")
name: Daily Stock Screening (Git-Based Storage)

on:
  schedule:
    # Scheduled for 12:00 UTC on weekdays, but GitHub Actions has consistently
    # delayed the actual start by ~4-5 hours (observed 16:11-17:39 UTC across
    # every run since 2026-08-31) — a documented platform limitation for
    # scheduled workflows, not something this repo controls. Don't rely on
    # "7am EST" as when today's picks actually land.
    - cron: '0 12 * * 1-5'

  # Allow manual triggering
  workflow_dispatch:
    inputs:
      force_full_refresh:
        description: 'Force refresh all fundamentals (ignore cache)'
        required: false
        type: boolean
        default: false

jobs:
  screen-stocks:
    runs-on: ubuntu-latest
    # A hung network call (e.g. a stalled SSL read to a data provider that
    # never times out on its own — this has happened for real, locally) would
    # otherwise run until GitHub's own multi-hour default limit, blocking the
    # day's email, commit, and dashboard data the whole time. 120 min gives
    # ~2x headroom over the observed real runtime (every run since
    # 2026-08-31 has taken 63-64 min, consistently — a 60 min timeout was
    # killing every run a few minutes before it reached the commit/push
    # step, which is why the dashboard's daily_scans data stopped updating).
    timeout-minutes: 120

    permissions:
      contents: write  # Required to commit fundamental cache

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 1  # Shallow clone for speed

      - name: Get current date
        id: date
        run: |
          echo "date=$(date +'%Y-%m-%d')" >> $GITHUB_OUTPUT
          echo "time=$(date +'%H:%M:%S')" >> $GITHUB_OUTPUT

      - name: Check existing fundamental cache
        id: cache-check
        run: |
          if [ -d "data/fundamentals_cache" ]; then
            CACHE_COUNT=$(ls data/fundamentals_cache/*_fundamentals.json 2>/dev/null | wc -l | tr -d ' ')
            echo "✓ Found existing fundamental cache"
            echo "cached_stocks=$CACHE_COUNT" >> $GITHUB_OUTPUT
            echo "  Cached stocks: $CACHE_COUNT"

            # Show cache age distribution
            echo "  Cache age distribution:"
            find data/fundamentals_cache -name "*_fundamentals.json" -mtime -7 -type f | wc -l | xargs echo "    <7 days:"
            find data/fundamentals_cache -name "*_fundamentals.json" -mtime +7 -mtime -30 -type f | wc -l | xargs echo "    7-30 days:"
            find data/fundamentals_cache -name "*_fundamentals.json" -mtime +30 -mtime -90 -type f | wc -l | xargs echo "    30-90 days:"
            find data/fundamentals_cache -name "*_fundamentals.json" -mtime +90 -type f | wc -l | xargs echo "    >90 days (stale):"
          else
            echo "⚠ No existing cache, will create"
            mkdir -p data/fundamentals_cache
            echo "cached_stocks=0" >> $GITHUB_OUTPUT
          fi

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run optimized stock screening
        env:
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER || 'smtp.gmail.com' }}
          EMAIL_SMTP_PORT: ${{ secrets.EMAIL_SMTP_PORT || '587' }}
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          FORCE_FULL_REFRESH: ${{ github.event.inputs.force_full_refresh || 'false' }}
          CACHED_STOCKS: ${{ steps.cache-check.outputs.cached_stocks }}
        run: |
          echo "Starting screening with:"
          echo "  - Fresh price data for all stocks (1 year history)"
          echo "  - Smart fundamental refresh (earnings-aware)"
          echo "  - Cached fundamentals: $CACHED_STOCKS stocks"
          echo ""

          # Create output directories
          mkdir -p data/daily_scans
          mkdir -p data/logs

          # Conservative mode to avoid rate limits
          # --git-storage flag enables Git-based fundamental storage
          # --enable-llm-agents runs Fundamentals Auditor + Catalyst Sentiment
          # (Claude API calls) and the free Congress Trades lookup on the Top 20
          # pool, then filters/ranks that pool down to a Top 5 shortlist in the
          # email. Fundamentals Auditor/Catalyst Sentiment no-op with a logged
          # warning if ANTHROPIC_API_KEY isn't set as a repo secret.
          python run_optimized_scan.py --conservative --git-storage --enable-llm-agents

      - name: Show fundamental refresh stats
        if: always()
        run: |
          echo "=== Fundamental Cache Statistics ==="
          if [ -f "data/fundamentals_cache/metadata.json" ]; then
            echo "Latest updates:"
            python3 << 'PYTHON_SCRIPT'
          import json
          from datetime import datetime

          try:
              with open("data/fundamentals_cache/metadata.json", "r") as f:
                  metadata = json.load(f)

              # Show last 10 updated stocks
              updates = [(ticker, data["last_updated"]) for ticker, data in metadata.items()]
              updates.sort(key=lambda x: x[1], reverse=True)

              print(f"Total tracked: {len(updates)} stocks")
              print("\nLast 10 updates:")
              for ticker, timestamp in updates[:10]:
                  dt = datetime.fromisoformat(timestamp)
                  formatted = dt.strftime("%Y-%m-%d %H:%M")
                  print(f"  {ticker}: {formatted}")
          except Exception as e:
              print(f"Could not read metadata: {e}")
          PYTHON_SCRIPT
          else
            echo "No metadata file found"
          fi

      - name: Commit updated fundamental cache
        id: commit
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"

          # Add fundamental cache directory, plus the LLM agents' logged output
          # (data/fundamentals_audit/, data/catalyst_sentiment/, data/congress_trades/)
          # — these need to persist past this ephemeral runner so they can accumulate
          # into a real point-in-time history for the walk-forward backtest to eventually use.
          git add data/fundamentals_cache/
          git add data/fundamentals_audit/ 2>/dev/null || true
          git add data/catalyst_sentiment/ 2>/dev/null || true
          git add data/congress_trades/ 2>/dev/null || true

          # Also commit the day's Top 20 pool + Top 5 shortlist (top20_latest.json,
          # shortlist_latest.json) and scan report — this is what actually reaches
          # the local GUI dashboard (dashboard.py) after a `git pull`, so the same
          # picks that went out by email are also visible there.
          git add data/daily_scans/ 2>/dev/null || true

          # Check if there are changes
          if git diff --staged --quiet; then
            echo "No fundamental cache changes to commit"
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            CHANGED_FILES=$(git diff --staged --name-only | wc -l)
            echo "Committing $CHANGED_FILES updated fundamental files"
            git commit -m "chore: update fundamental cache ($CHANGED_FILES stocks) - ${{ steps.date.outputs.date }}"
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi

      - name: Push changes
        if: steps.commit.outputs.has_changes == 'true'
        uses: ad-m/github-push-action@v0.8.0
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: ${{ github.ref }}

      - name: Upload screening results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: screening-results-${{ steps.date.outputs.date }}
          path: |
            data/daily_scans/
            data/logs/
          if-no-files-found: warn  # Don't fail if no files found
          retention-days: 90  # Keep screening results for 90 days

      - name: Cache size report
        if: always()
        run: |
          echo "=== Git Repository Impact ==="
          if [ -d "data/fundamentals_cache" ]; then
            CACHE_SIZE=$(du -sh data/fundamentals_cache | cut -f1)
            CACHE_FILES=$(find data/fundamentals_cache -name "*.json" | wc -l | tr -d ' ')

            echo "Fundamental cache directory size: $CACHE_SIZE"
            echo "Total files: $CACHE_FILES"
            echo ""
            echo "Today's commit impact:"
            if [ "${{ steps.commit.outputs.has_changes }}" == "true" ]; then
              git show --stat | tail -5
            else
              echo "  No changes committed"
            fi
          fi
name: Midday Quick Scan

on:
  schedule:
    # ~12pm ET on weekdays (17:00 UTC). Uses the same fixed EST-based UTC
    # offset as the 7am daily scan, so both jobs drift together (~1hr late)
    # during EDT months rather than independently.
    - cron: '0 17 * * 1-5'

  workflow_dispatch: {}

jobs:
  quick-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    permissions:
      contents: write  # Required to commit fundamental cache

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run quick test scan (100 stocks)
        env:
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER || 'smtp.gmail.com' }}
          EMAIL_SMTP_PORT: ${{ secrets.EMAIL_SMTP_PORT || '587' }}
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
        run: |
          mkdir -p data/daily_scans
          mkdir -p data/logs
          python run_optimized_scan.py --test-mode --git-storage

      - name: Commit updated fundamental cache
        id: commit
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"

          git add data/fundamentals_cache/
          # Also commit the day's Top 20 pool + scan report so the local GUI
          # dashboard (dashboard.py) can show it after a `git pull`.
          git add data/daily_scans/ 2>/dev/null || true

          if git diff --staged --quiet; then
            echo "No fundamental cache changes to commit"
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            CHANGED_FILES=$(git diff --staged --name-only | wc -l)
            git commit -m "chore: midday quick scan cache update ($CHANGED_FILES stocks) - $(date +'%Y-%m-%d %H:%M')"
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi

      - name: Push changes
        if: steps.commit.outputs.has_changes == 'true'
        uses: ad-m/github-push-action@v0.8.0
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: ${{ github.ref }}

      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: midday-quick-scan-${{ github.run_id }}
          path: |
            data/daily_scans/
            data/logs/
          if-no-files-found: warn
          retention-days: 30

codex
The first important finding is confirmed: both workflows write and commit the same `*_latest.json` paths, but the midday job scans only 100 stocks and does not enable the LLM shortlist agents. I’m now separating trustworthy full-universe history from those incomparable snapshots and checking race behavior and dashboard conventions.
exec
/bin/zsh -lc "sed -n '1,720p' run_optimized_scan.py && sed -n '1,320p' scripts/fetch_momentum_status.py && sed -n '1,220p' data/momentum_status/history.json" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
#!/usr/bin/env python3
"""Optimized full market scanner with parallel processing.

This version uses parallel workers to achieve 10-25 TPS safely while
avoiding rate limits through:
- Thread pool with 5 workers
- Per-worker rate limiting (0.2s = 5 TPS each)
- Adaptive backoff on errors
- Session pooling

Expected runtime: 15-30 minutes for 3,800+ stocks

Usage:
    python run_optimized_scan.py
    python run_optimized_scan.py --workers 10  # Faster but riskier
    python run_optimized_scan.py --conservative  # Slower but safer (3 workers)
"""

import argparse
import json
import logging
import os
import random
import sys
from datetime import datetime
from pathlib import Path

from src.data.universe_fetcher import USStockUniverseFetcher
from src.screening.optimized_batch_processor import OptimizedBatchProcessor
from src.screening.benchmark import (
    analyze_spy_trend,
    calculate_market_breadth,
    format_benchmark_summary,
    should_generate_signals
)
from src.screening.signal_engine import score_buy_signal, score_sell_signal
from src.data.enhanced_fundamentals import EnhancedFundamentalsFetcher
from src.data.reddit_sentiment import RedditSentimentFetcher
from src.data.apewisdom_sentiment import ApeWisdomSentimentFetcher
from src.data.insider_trading import InsiderTradingFetcher
from src.data.earnings_risk import EarningsRiskFetcher
from src.screening.top20_ranker import build_top20
from src.agents.fundamentals_auditor import audit_candidates
from src.agents.catalyst_sentiment import analyze_candidates
from src.agents.congress_trades import get_signals_for_candidates as get_congress_signals
from src.agents.shortlist import build_shortlist
from src.utils.json_safe import sanitize_nan

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _atomic_write_json(path, data):
    path = Path(path)
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    with open(tmp_path, 'w') as f:
        json.dump(sanitize_nan(data), f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def save_report(results, buy_signals, sell_signals, spy_analysis, breadth, output_dir="./data/daily_scans"):
    """Save comprehensive report."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')

    output = []
    output.append("="*80)
    output.append("OPTIMIZED FULL MARKET SCAN - ALL US STOCKS")
    output.append(f"Scan Date: {date_str}")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("="*80)
    output.append("")

    # Stats
    output.append("SCANNING STATISTICS")
    output.append("-"*80)
    output.append(f"Total Universe: {results['total_processed']:,} stocks")
    output.append(f"Analyzed: {results['total_analyzed']:,} stocks")
    output.append(f"Processing Time: {results['processing_time_seconds']/60:.1f} minutes")
    output.append(f"Actual TPS: {results['actual_tps']:.2f}")

    error_rate = results['error_rate'] * 100
    if error_rate < 1:
        error_emoji = "🟢"
    elif error_rate < 5:
        error_emoji = "🟡"
    else:
        error_emoji = "🔴"
    output.append(f"{error_emoji} Error Rate: {error_rate:.2f}%")

    # Buy/Sell signal counts with emoji
    if len(buy_signals) > 0:
        output.append(f"🟢 Buy Signals: {len(buy_signals)}")
    else:
        output.append(f"Buy Signals: {len(buy_signals)}")

    if len(sell_signals) > 0:
        output.append(f"🔴 Sell Signals: {len(sell_signals)}")
    else:
        output.append(f"Sell Signals: {len(sell_signals)}")
    output.append("")

    # Benchmark
    output.append(format_benchmark_summary(spy_analysis, breadth))
    output.append("")

    # Buy signals
    output.append("="*80)
    output.append(f"🟢 TOP BUY SIGNALS (Score >= 70) - {len(buy_signals)} Total")
    output.append("="*80)
    output.append("")

    if buy_signals:
        for i, signal in enumerate(buy_signals[:50], 1):
            score = signal['score']
            # Score-based emoji (green/yellow with star for exceptional)
            if score >= 90:
                score_emoji = "⭐"  # Exceptional - star
            elif score >= 80:
                score_emoji = "🟢"  # Very good - green
            elif score >= 70:
                score_emoji = "🟢"  # Good - green
            else:
                score_emoji = "🟡"  # Borderline - yellow

            output.append(f"\n{'#'*80}")
            output.append(f"{score_emoji} BUY #{i}: {signal['ticker']} | Score: {signal['score']}/125")
            output.append(f"{'#'*80}")
            if signal.get('current_price') is not None:
                output.append(f"Current Price: ${signal['current_price']:.2f}")
            output.append(f"Phase: {signal['phase']}")

            # Entry quality with emoji
            entry_quality = signal.get('entry_quality', 'Unknown')
            if entry_quality == 'Good':
                output.append(f"🟢 Entry Quality: {entry_quality}")
            elif entry_quality == 'Extended':
                output.append(f"🟡 Entry Quality: {entry_quality}")
            else:
                output.append(f"🔴 Entry Quality: {entry_quality}")

            # CRITICAL: Stop loss and R/R ratio
            if signal.get('stop_loss'):
                output.append(f"Stop Loss: ${signal['stop_loss']:.2f}")
                details = signal.get('details', {})
                risk_amt = details.get('risk_amount', 0)
                reward_amt = details.get('reward_amount', 0)
                rr_ratio = signal.get('risk_reward_ratio', 0)
                # R/R ratio emoji
                if rr_ratio >= 3:
                    rr_emoji = "🟢"  # Excellent R/R
                elif rr_ratio >= 2:
                    rr_emoji = "🟢"  # Good R/R
                else:
                    rr_emoji = "🟡"  # Poor R/R
                output.append(f"{rr_emoji} Risk/Reward: {rr_ratio:.1f}:1 (Risk ${risk_amt:.2f}, Reward ${reward_amt:.2f})")

            if signal.get('breakout_price'):
                output.append(f"Breakout: ${signal['breakout_price']:.2f}")

            details = signal.get('details', {})
            if 'rs_slope' in details:
                rs_slope = details['rs_slope']
                # RS emoji (green = good, yellow = ok, red = bad)
                if rs_slope > 0.5:
                    rs_emoji = "🟢"  # Strong RS
                elif rs_slope > 0:
                    rs_emoji = "🟡"  # Positive RS
                else:
                    rs_emoji = "🔴"  # Weak RS
                output.append(f"{rs_emoji} RS: {rs_slope:.3f}")
            if 'volume_ratio' in details:
                vol_ratio = details['volume_ratio']
                # Volume emoji
                if vol_ratio > 1.5:
                    vol_emoji = "🟢"  # High volume
                elif vol_ratio > 1.0:
                    vol_emoji = "🟡"  # Above average
                else:
                    vol_emoji = "🔴"  # Low volume
                output.append(f"{vol_emoji} Volume: {vol_ratio:.1f}x")

            # VCP pattern details if detected
            vcp_data = details.get('vcp_data')
            if vcp_data:
                vcp_quality = vcp_data.get('quality', 0)
                contractions = vcp_data.get('contractions', 0)
                pattern = vcp_data.get('pattern', 'N/A')

                if vcp_quality >= 80:
                    vcp_emoji = "⭐"  # Exceptional VCP
                elif vcp_quality >= 60:
                    vcp_emoji = "🟢"  # Good VCP
                elif vcp_quality >= 50:
                    vcp_emoji = "🟡"  # Marginal VCP
                else:
                    vcp_emoji = "🟡"  # Partial pattern

                if vcp_quality >= 50:
                    output.append(f"{vcp_emoji} VCP: {pattern} (quality: {vcp_quality:.0f}/100)")

            if signal.get('reddit_mentions_24h') is not None:
                output.append(f"💬 Reddit Mentions (24h): {signal['reddit_mentions_24h']}")

            output.append("\nKey Reasons:")
            for reason in signal['reasons'][:7]:  # Show 7 instead of 5
                output.append(f"  • {reason}")

            if signal.get('fundamental_snapshot'):
                output.append(signal['fundamental_snapshot'])

        if len(buy_signals) > 50:
            output.append(f"\n{'='*80}")
            output.append(f"ADDITIONAL BUYS ({len(buy_signals)-50} more)")
            output.append(f"{'='*80}\n")
            remaining = [s['ticker'] for s in buy_signals[50:]]
            for i in range(0, len(remaining), 10):
                output.append(", ".join(remaining[i:i+10]))
    else:
        output.append("✗ NO BUY SIGNALS TODAY")

    # Sell signals
    output.append(f"\n\n{'='*80}")
    output.append(f"🔴 TOP SELL SIGNALS (Score >= 60) - {len(sell_signals)} Total")
    output.append(f"{'='*80}")
    output.append("")

    if sell_signals:
        for i, signal in enumerate(sell_signals[:30], 1):
            score = signal['score']
            severity = signal['severity']

            # Severity emoji (red/yellow with alarm for critical)
            if severity == 'critical':
                severity_emoji = "🚨"  # Critical - alarm
            elif severity == 'high':
                severity_emoji = "🔴"  # High - red
            else:
                severity_emoji = "🟡"  # Moderate - yellow

            # Score emoji (higher score = more urgent to sell)
            if score >= 80:
                score_emoji = "🚨"  # Very urgent - alarm
            elif score >= 70:
                score_emoji = "🔴"  # Urgent - red
            else:
                score_emoji = "🟡"  # Warning - yellow

            output.append(f"\n{'#'*80}")
            output.append(f"{score_emoji} SELL #{i}: {signal['ticker']} | Score: {signal['score']}/110")
            output.append(f"{'#'*80}")
            if signal.get('current_price') is not None:
                output.append(f"Current Price: ${signal['current_price']:.2f}")
            output.append(f"Phase: {signal['phase']} | {severity_emoji} Severity: {severity.upper()}")
            if signal.get('breakdown_level'):
                output.append(f"Breakdown: ${signal['breakdown_level']:.2f}")
            details = signal.get('details', {})
            if 'rs_slope' in details:
                rs_slope = details['rs_slope']
                # RS emoji for sell signals (negative is expected)
                if rs_slope < -0.5:
                    rs_emoji = "🔴"  # Very weak RS
                elif rs_slope < 0:
                    rs_emoji = "🟡"  # Weak RS
                else:
                    rs_emoji = "🟢"  # Still positive RS (unusual for sell)
                output.append(f"{rs_emoji} RS: {rs_slope:.3f}")
            if signal.get('reddit_mentions_24h') is not None:
                output.append(f"💬 Reddit Mentions (24h): {signal['reddit_mentions_24h']}")
            output.append("\nSell Reasons:")
            for reason in signal['reasons'][:5]:
                output.append(f"  • {reason}")

            if signal.get('fundamental_snapshot'):
                output.append(signal['fundamental_snapshot'])

        if len(sell_signals) > 30:
            output.append(f"\n{'='*80}")
            output.append(f"ADDITIONAL SELLS ({len(sell_signals)-30} more)")
            output.append(f"{'='*80}\n")
            remaining = [s['ticker'] for s in sell_signals[30:]]
            for i in range(0, len(remaining), 10):
                output.append(", ".join(remaining[i:i+10]))
    else:
        output.append("✗ NO SELL SIGNALS TODAY")

    output.append(f"\n\n{'='*80}")
    output.append("END OF SCAN")
    output.append(f"{'='*80}\n")

    report_text = "\n".join(output)

    # Save
    filepath = Path(output_dir) / f"optimized_scan_{timestamp}.txt"
    with open(filepath, 'w') as f:
        f.write(report_text)

    latest_path = Path(output_dir) / "latest_optimized_scan.txt"
    with open(latest_path, 'w') as f:
        f.write(report_text)

    logger.info(f"Report saved: {filepath}")
    print(report_text)

    return filepath


def main():
    parser = argparse.ArgumentParser(description='Optimized Full Market Scanner')
    parser.add_argument('--workers', type=int, default=3, help='Parallel workers (default: 3)')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay per worker (default: 0.5s)')
    parser.add_argument('--conservative', action='store_true', help='Ultra-conservative mode (2 workers, 1.0s delay)')
    parser.add_argument('--aggressive', action='store_true', help='Faster mode (5 workers, 0.3s delay) - MAY HIT RATE LIMITS!')
    parser.add_argument('--resume', action='store_true', help='Resume from progress')
    parser.add_argument('--clear-progress', action='store_true', help='Clear progress')
    parser.add_argument('--test-mode', action='store_true', help='Test with 100 stocks')
    parser.add_argument('--min-price', type=float, default=5.0, help='Min price')
    parser.add_argument('--min-volume', type=int, default=100000, help='Min volume')
    parser.add_argument('--use-fmp', action='store_true', help='Use FMP for enhanced fundamentals on buy signals')
    parser.add_argument('--git-storage', action='store_true', help='Use Git-based storage for fundamentals (recommended)')
    parser.add_argument('--enable-llm-agents', action='store_true',
                         help='Run the Fundamentals Auditor + Catalyst Sentiment agents (Claude API calls) '
                              'on the Top 20 shortlist. Needs ANTHROPIC_API_KEY set; no-ops with a warning otherwise.')

    args = parser.parse_args()

    # Presets
    if args.conservative:
        args.workers = 2
        args.delay = 1.0
        logger.info("Ultra-conservative mode: 2 workers, 1.0s delay (~2 TPS)")
    elif args.aggressive:
        args.workers = 5
        args.delay = 0.3
        logger.warning("Aggressive mode: 5 workers, 0.3s delay (~17 TPS) - MAY HIT RATE LIMITS!")

    effective_tps = args.workers / args.delay
    logger.info(f"Configuration: {args.workers} workers × {1/args.delay:.1f} TPS = ~{effective_tps:.1f} TPS effective")

    # "Hard search activated" notification — fires immediately on scan start, not
    # at the end, so a manual/scheduled trigger is confirmed without waiting 15-30 min.
    if not args.test_mode:
        from src.notifications.email_notifier import EmailNotifier
        EmailNotifier().send_notification(
            subject="[Stock Screener] Hard Search Activated 🚀",
            message=(
                "Your full market scan (3,800+ stocks) just started.\n\n"
                f"Workers: {args.workers} | Effective rate: ~{effective_tps:.1f} TPS\n"
                "Expected runtime: 15-30 minutes.\n\n"
                "You'll get a second email with the buy/sell signals when it finishes."
            ),
        )

    # Initialize enhanced fundamentals fetcher
    fundamentals_fetcher = EnhancedFundamentalsFetcher()
    if args.use_fmp and fundamentals_fetcher.fmp_available:
        logger.info("FMP enabled - will use for buy signal fundamentals")
    elif args.use_fmp:
        logger.warning("--use-fmp specified but FMP_API_KEY not set. Using yfinance only.")

    try:
        # Fetch universe
        universe_fetcher = USStockUniverseFetcher()
        logger.info("Fetching stock universe...")
        tickers = universe_fetcher.fetch_universe()

        if not tickers:
            logger.error("Failed to fetch universe")
            sys.exit(1)

        logger.info(f"Universe: {len(tickers):,} stocks")

        if args.test_mode:
            # universe_fetcher sorts alphabetically, so tickers[:100] would always be
            # the same ~100 "A" names every run — random sample instead for real coverage.
            tickers = random.sample(tickers, min(100, len(tickers)))
            logger.info(f"TEST MODE: {len(tickers)} random stocks")

        # Initialize processor
        processor = OptimizedBatchProcessor(
            max_workers=args.workers,
            rate_limit_delay=args.delay,
            use_git_storage=args.git_storage
        )

        if args.git_storage:
            logger.info("Git-based fundamental storage enabled - 74% API call reduction!")

        if args.clear_progress:
            processor.clear_progress()

        # Process
        results = processor.process_batch_parallel(
            tickers,
            resume=args.resume,
            min_price=args.min_price,
            min_volume=args.min_volume
        )

        if 'error' in results:
            logger.error(results['error'])
            sys.exit(1)

        # Analysis
        logger.info("Generating signals...")
        spy_analysis = analyze_spy_trend(processor.spy_data, processor.spy_price)
        breadth = calculate_market_breadth(results['phase_results'])
        signal_rec = should_generate_signals(spy_analysis, breadth)

        # Buy signals
        buy_signals = []
        if signal_rec['should_generate_buys']:
            for analysis in results['analyses']:
                if analysis['phase_info']['phase'] in [1, 2]:
                    signal = score_buy_signal(
                        ticker=analysis['ticker'],
                        price_data=analysis['price_data'],
                        current_price=analysis['current_price'],
                        phase_info=analysis['phase_info'],
                        rs_series=analysis['rs_series'],
                        fundamentals=analysis.get('quarterly_data'),  # Pass raw quarterly data, not analyzed
                        vcp_data=analysis.get('vcp_data')  # Added VCP data
                    )
                    if signal['is_buy']:
                        signal['current_price'] = analysis['current_price']
                        # Use FMP for enhanced snapshot if requested and available
                        signal['fundamental_snapshot'] = fundamentals_fetcher.create_snapshot(
                            analysis['ticker'],
                            quarterly_data=analysis.get('quarterly_data', {}),
                            use_fmp=args.use_fmp
                        )
                        buy_signals.append(signal)

        buy_signals = sorted(buy_signals, key=lambda x: x['score'], reverse=True)

        # Sell signals
        sell_signals = []
        if signal_rec['should_generate_sells']:
            for analysis in results['analyses']:
                if analysis['phase_info']['phase'] in [3, 4]:
                    signal = score_sell_signal(
                        ticker=analysis['ticker'],
                        price_data=analysis['price_data'],
                        current_price=analysis['current_price'],
                        phase_info=analysis['phase_info'],
                        rs_series=analysis['rs_series'],
                        fundamentals=analysis.get('quarterly_data')  # Pass raw quarterly data, not analyzed
                    )
                    if signal['is_sell']:
                        signal['current_price'] = analysis['current_price']
                        # Add fundamental snapshot
                        signal['fundamental_snapshot'] = fundamentals_fetcher.create_snapshot(
                            analysis['ticker'],
                            quarterly_data=analysis.get('quarterly_data', {}),
                            use_fmp=args.use_fmp
                        )
                        sell_signals.append(signal)

        sell_signals = sorted(sell_signals, key=lambda x: x['score'], reverse=True)

        # Earnings risk warning — NOT a bullish/bearish signal, just a heads-up that a
        # high-uncertainty event (which trend-following can't predict) is imminent. No
        # credentials needed, always available, applies to both buy and sell signals.
        tickers_of_interest = {s['ticker'] for s in buy_signals} | {s['ticker'] for s in sell_signals}
        if tickers_of_interest:
            logger.info(f"Checking earnings risk for {len(tickers_of_interest)} signal tickers...")
            earnings_fetcher = EarningsRiskFetcher()
            flagged = 0
            for signal in buy_signals + sell_signals:
                risk = earnings_fetcher.get_earnings_risk(signal['ticker'])
                if risk['has_upcoming_earnings']:
                    signal['earnings_risk'] = risk
                    # Inserted into `reasons` (not a separate field) so it flows through
                    # the existing text report / email "top reason" / dashboard bullet
                    # rendering automatically, without needing parallel display code.
                    signal['reasons'].insert(0, f"⚠️ {risk['note']}")
                    flagged += 1
            logger.info(f"Earnings risk: {flagged} tickers have earnings within 14 days")

        # Reddit mentions. Prefers the official PRAW-based fetcher if
        # REDDIT_CLIENT_ID/SECRET are set (configurable subreddit list, real-time);
        # otherwise falls back to ApeWisdom's free public API (no credentials,
        # no setup, but their subreddit/timeframe choices aren't configurable).
        reddit_mentions = {}
        if tickers_of_interest:
            reddit_fetcher = RedditSentimentFetcher()
            if reddit_fetcher.available:
                logger.info(f"Checking Reddit mentions for {len(tickers_of_interest)} signal tickers (PRAW)...")
                reddit_mentions = reddit_fetcher.fetch_mentions(tickers_of_interest)
            else:
                logger.info(f"Checking Reddit mentions for {len(tickers_of_interest)} signal tickers (ApeWisdom, no credentials)...")
                reddit_mentions = ApeWisdomSentimentFetcher().fetch_mentions(tickers_of_interest)

            if reddit_mentions:
                for signal in buy_signals:
                    signal['reddit_mentions_24h'] = reddit_mentions.get(signal['ticker'], {}).get('count', 0)
                for signal in sell_signals:
                    signal['reddit_mentions_24h'] = reddit_mentions.get(signal['ticker'], {}).get('count', 0)
                total_mentions = sum(v['count'] for v in reddit_mentions.values())
                logger.info(f"Reddit: {total_mentions} mentions found across {len(reddit_mentions)} tickers")

        # Insider buying (SEC Form 4, "P" open-market purchases only) — no credentials
        # needed, always available, so no gating check like Reddit/FMP.
        insider_signals = {}
        buy_tickers = {s['ticker'] for s in buy_signals}
        if buy_tickers:
            logger.info(f"Checking insider buying (SEC Form 4) for {len(buy_tickers)} buy signal tickers...")
            insider_fetcher = InsiderTradingFetcher()
            for ticker in buy_tickers:
                signal = insider_fetcher.get_insider_signal(ticker)
                if signal['purchases_90d'] > 0:
                    insider_signals[ticker] = signal
            total_insider_value = sum(v['total_buy_value'] for v in insider_signals.values())
            logger.info(f"Insider buying: ${total_insider_value:,.0f} across {len(insider_signals)} tickers")

        # Top 20: combined technical + Reddit-buzz + insider-buying ranking of the
        # qualified buy pool, with "why is this moving" links
        top20 = []
        top20_path = Path("./data/daily_scans/top20_latest.json")
        top20_path.parent.mkdir(parents=True, exist_ok=True)
        if buy_signals:
            logger.info("Building Top 20 shortlist...")
            top20 = build_top20(buy_signals, reddit_mentions, insider_signals)
        # Always write top20_latest.json, even when empty — otherwise a scan
        # that finds zero buy signals leaves a stale prior day's Top 20 in
        # place with no indication it's stale (the dashboard's Market/
        # Shortlist views read this file directly and would show yesterday's
        # picks as if they were fresh).
        # sanitize_nan: this feeds the dashboard's Market/Shortlist views
        # directly — a stray NaN in a technical score would otherwise
        # serialize as an invalid JSON token the browser can't parse.
        _atomic_write_json(top20_path, {
            'generated': datetime.now().isoformat(),
            'result': 'success' if top20 else 'no_candidates',
            'top20': top20,
        })
        logger.info(f"Top 20 saved: {top20_path} ({len(top20)} tickers)")

        # LLM agents (Fundamentals Auditor, Catalyst Sentiment) + free Congress Trades
        # lookup — opt-in since the first two are real Claude API calls per ticker.
        # Only run on the Top 20 shortlist, not the full buy_signals pool, to keep
        # cost bounded. None of these ever modify src/screening/signal_engine.py;
        # results are logged under data/fundamentals_audit/, data/catalyst_sentiment/,
        # data/congress_trades/. Their output actually filters/ranks the final Top 5
        # (see src/agents/shortlist.py) — it's not just informational anymore.
        fundamentals_audits = {}
        catalyst_sentiments = {}
        congress_signals = {}
        shortlist = []
        if args.enable_llm_agents and top20:
            top20_tickers = [s['ticker'] for s in top20]
            logger.info(f"Running Fundamentals Auditor on {len(top20_tickers)} Top 20 tickers...")
            audit_results = audit_candidates(top20_tickers)
            fundamentals_audits = {r['ticker']: r['audit'] for r in audit_results if r['audited']}
            logger.info(f"Running Catalyst Sentiment on {len(top20_tickers)} Top 20 tickers...")
            sentiment_results = analyze_candidates(top20_tickers)
            catalyst_sentiments = {r['ticker']: r['classification'] for r in sentiment_results if r['analyzed']}
            logger.info(f"Running Congress Trades lookup on {len(top20_tickers)} Top 20 tickers...")
            congress_signals = get_congress_signals(top20_tickers)
            shortlist = build_shortlist(
                top20, fundamentals_audits, catalyst_sentiments, congress_signals, size=5,
            )
            logger.info(
                f"Top 5 shortlist: {[s['ticker'] for s in shortlist]} "
                f"({sum(1 for s in shortlist if s['passed_filters'])} passed filters, "
                f"{sum(1 for s in shortlist if not s['passed_filters'])} backfilled)"
            )

            # Persist alongside top20_latest.json so the local GUI dashboard can
            # show the actual filtered Top 5 (today this only reaches the user
            # via email otherwise).
            shortlist_path = Path("./data/daily_scans/shortlist_latest.json")
            shortlist_path.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_json(shortlist_path, {
                'generated': datetime.now().isoformat(),
                'result': 'success',
                'shortlist': shortlist,
                'fundamentals_audits': fundamentals_audits,
                'catalyst_sentiments': catalyst_sentiments,
                'congress_signals': congress_signals,
            })
            logger.info(f"Shortlist saved: {shortlist_path}")
        elif args.enable_llm_agents:
            # Same staleness issue as top20_latest.json above: a daily run
            # that explicitly asked for a shortlist but found zero buy
            # signals must not leave yesterday's real shortlist looking
            # current. Only reached when agents were requested — a run
            # without --enable-llm-agents (e.g. the midday scan) correctly
            # leaves the once-a-day shortlist file untouched.
            logger.info("LLM agents skipped: no Top 20 shortlist was built this run.")
            shortlist_path = Path("./data/daily_scans/shortlist_latest.json")
            shortlist_path.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_json(shortlist_path, {
                'generated': datetime.now().isoformat(),
                'result': 'no_candidates',
                'shortlist': [],
                'fundamentals_audits': {},
                'catalyst_sentiments': {},
                'congress_signals': {},
            })
            logger.info(f"Shortlist cleared (no candidates today): {shortlist_path}")

        # Report
        save_report(results, buy_signals, sell_signals, spy_analysis, breadth)

        # Email notification (no-ops with a logged warning if EMAIL_* env vars aren't set)
        from src.notifications.email_notifier import EmailNotifier
        EmailNotifier().send_scan_report(
            buy_signals, sell_signals, spy_analysis, breadth, top20=top20,
            fundamentals_audits=fundamentals_audits, catalyst_sentiments=catalyst_sentiments,
            congress_signals=congress_signals, shortlist=shortlist,
        )

        # Show FMP usage if enabled
        if args.use_fmp:
            usage = fundamentals_fetcher.get_api_usage()
            logger.info("="*60)
            logger.info("FMP API USAGE")
            logger.info(f"Calls used: {usage['fmp_calls_used']}/{usage['fmp_daily_limit']}")
            logger.info(f"Calls remaining: {usage['fmp_calls_remaining']}")
            if 'bandwidth_used_mb' in usage:
                logger.info(f"Bandwidth used: {usage['bandwidth_used_mb']:.1f} MB / {usage['bandwidth_limit_gb']:.1f} GB ({usage['bandwidth_pct_used']:.1f}%)")
                logger.info(f"Earnings season: {'Yes' if usage['is_earnings_season'] else 'No'} (cache: {usage['cache_hours']}h)")
            logger.info("="*60)

        logger.info("="*60)
        logger.info("SCAN COMPLETE")
        logger.info(f"Time: {results['processing_time_seconds']/60:.1f} minutes")
        logger.info(f"Actual TPS: {results['actual_tps']:.2f}")
        logger.info(f"Buy signals: {len(buy_signals)}")
        logger.info(f"Sell signals: {len(sell_signals)}")
        logger.info("="*60)

    except KeyboardInterrupt:
        logger.info("\nInterrupted - progress saved")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
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
{
  "OXY": {
    "status": "stable",
    "since": "2026-09-20",
    "days": 1,
    "last_seen": "2026-09-20"
  },
  "KRO": {
    "status": "basing",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "GKOS": {
    "status": "basing",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "CAKE": {
    "status": "basing",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "MUFG": {
    "status": "basing",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "ELBM": {
    "status": "avoid",
    "since": "2026-09-18",
    "days": 3,
    "last_seen": "2026-09-20"
  },
  "NVDA": {
    "status": "stable",
    "since": "2026-09-18",
    "days": 3,
    "last_seen": "2026-09-20"
  },
  "VOO": {
    "status": "stable",
    "since": "2026-09-18",
    "days": 3,
    "last_seen": "2026-09-20"
  },
  "VTI": {
    "status": "stable",
    "since": "2026-09-18",
    "days": 3,
    "last_seen": "2026-09-20"
  },
  "FRBUX": {
    "status": "stable",
    "since": "2026-09-17",
    "days": 4,
    "last_seen": "2026-09-20"
  },
  "NGL": {
    "status": "basing",
    "since": "2026-09-17",
    "days": 1,
    "last_seen": "2026-09-17"
  },
  "ASND": {
    "status": "basing",
    "since": "2026-09-15",
    "days": 1,
    "last_seen": "2026-09-15"
  },
  "LILA": {
    "status": "stable",
    "since": "2026-09-20",
    "days": 1,
    "last_seen": "2026-09-20"
  },
  "LILAK": {
    "status": "stable",
    "since": "2026-09-20",
    "days": 1,
    "last_seen": "2026-09-20"
  },
  "LTC": {
    "status": "stable",
    "since": "2026-09-20",
    "days": 1,
    "last_seen": "2026-09-20"
  },
  "COP": {
    "status": "stable",
    "since": "2026-09-16",
    "days": 1,
    "last_seen": "2026-09-16"
  },
  "WES": {
    "status": "stable",
    "since": "2026-09-13",
    "days": 2,
    "last_seen": "2026-09-14"
  },
  "CVX": {
    "status": "stable",
    "since": "2026-09-16",
    "days": 2,
    "last_seen": "2026-09-17"
  },
  "PSX": {
    "status": "hot",
    "since": "2026-09-17",
    "days": 1,
    "last_seen": "2026-09-17"
  },
  "SM": {
    "status": "stable",
    "since": "2026-09-17",
    "days": 1,
    "last_seen": "2026-09-17"
  },
  "JPM": {
    "status": "stable",
    "since": "2026-09-13",
    "days": 2,
    "last_seen": "2026-09-14"
  },
  "MFG": {
    "status": "stable",
    "since": "2026-09-16",
    "days": 1,
    "last_seen": "2026-09-16"
  },
  "ACOG": {
    "status": "stable",
    "since": "2026-09-13",
    "days": 2,
    "last_seen": "2026-09-14"
  },
  "MPC": {
    "status": "hot",
    "since": "2026-09-17",
    "days": 1,
    "last_seen": "2026-09-17"
  },
  "EGY": {
    "status": "stable",
    "since": "2026-09-13",
    "days": 2,
    "last_seen": "2026-09-14"
  },
  "BP": {
    "status": "stable",
    "since": "2026-09-20",
    "days": 1,
    "last_seen": "2026-09-20"
  },
  "ET": {
    "status": "stable",
    "since": "2026-09-16",
    "days": 1,
    "last_seen": "2026-09-16"
  },
  "SLDE": {
    "status": "stable",
    "since": "2026-09-17",
    "days": 1,
    "last_seen": "2026-09-17"
  },
  "TALO": {
    "status": "stable",
    "since": "2026-09-16",
    "days": 2,
    "last_seen": "2026-09-17"
  },
  "HRTG": {
    "status": "stable",
    "since": "2026-09-15",
    "days": 2,
    "last_seen": "2026-09-16"
  },
  "PUBM": {
    "status": "stable",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "KRT": {
    "status": "stable",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "WHD": {
    "status": "stable",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "SAIC": {
    "status": "stable",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "BCAL": {
    "status": "stable",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "CLMT": {
    "status": "hot",
    "since": "2026-09-14",
    "days": 1,
    "last_seen": "2026-09-14"
  },
  "SATA": {
    "status": "stable",
    "since": "2026-09-17",

exec
/bin/zsh -lc "rg -n \"momentum-status|parse_scan_file|api/shortlist|api/top20|api/scan|get_scan_files|def sync|git pull|run_optimized_scan\" dashboard.py && sed -n '1,360p' static/js/core/ui-helpers.js && sed -n '1,360p' static/js/views/shortlist.js && sed -n '1,420p' static/js/views/market.js && sed -n '1,260p' static/js/core/router.js && rg -n \"nav|shortlist|market|Full Scan|full-scan\" templates/dashboard.html" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
29:# the dashboard always needs to read/write the real repo (git pull/push via
89:def parse_scan_file(filepath):
268:def get_scan_files():
421:        cmd = [python, str(PROJECT_ROOT / "run_optimized_scan.py")]
493:    elif kind == "momentum-status":
591:    """git pull the repo so today's committed scan/shortlist/backtest data
667:@app.route("/api/momentum-status/<group>")
683:@app.route("/api/scans")
685:    return jsonify(get_scan_files())
688:@app.route("/api/scan")
701:    return jsonify(parse_scan_file(path))
704:@app.route("/api/top20")
709:@app.route("/api/shortlist")
776:        cmd = [_venv_python(), str(PROJECT_ROOT / "run_optimized_scan.py")]
786:    # (including git pull, running scans/backtests, and reading arbitrary
import { fetchJSON } from './api.js';
import { startJob } from './jobs.js';

const CHART_ICON = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 6"/><polyline points="15 6 21 6 21 12"/></svg>';
const _openCharts = new Set();

export function chartToggleButtonHTML(chartId) {
  return `<button class="chart-toggle-btn" data-chart-id="${chartId}" title="Price history">${CHART_ICON}</button>`;
}

export function wireChartToggles(container, getSeries, idPrefix) {
  container.querySelectorAll('.chart-toggle-btn').forEach(btn => {
    const chartId = btn.dataset.chartId;
    const wrap = document.getElementById(`${chartId}-wrap`);
    if (!wrap) return;
    const ticker = chartId.slice(idPrefix.length);

    if (_openCharts.has(chartId)) {
      wrap.style.display = 'block';
      btn.classList.add('active');
      const series = getSeries(ticker);
      if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
    }

    btn.addEventListener('click', () => {
      const nowVisible = wrap.style.display !== 'block';
      wrap.style.display = nowVisible ? 'block' : 'none';
      btn.classList.toggle('active', nowVisible);
      if (nowVisible) {
        _openCharts.add(chartId);
        const series = getSeries(ticker);
        if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
      } else {
        _openCharts.delete(chartId);
      }
    });
  });
}

export function refreshOpenCharts(getSeries, idPrefix) {
  _openCharts.forEach(chartId => {
    if (!chartId.startsWith(idPrefix)) return;
    if (!document.getElementById(`${chartId}-wrap`)) return;
    const ticker = chartId.slice(idPrefix.length);
    const series = getSeries(ticker);
    if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
  });
}

const MOMENTUM_LABELS = { hot: 'HOT', stable: 'STABLE', basing: 'BASING', avoid: 'AVOID' };

function momentumBadgeHTML(entry) {
  if (!entry || !entry.status) return '';
  const label = MOMENTUM_LABELS[entry.status] || entry.status.toUpperCase();
  const dayWord = entry.days === 1 ? 'day' : 'days';
  return `<span class="momentum-badge ${entry.status}" title="${entry.label} — ${entry.days} ${dayWord}">${label}<span class="streak">Day ${entry.days}</span></span>`;
}

export async function loadMomentumStatus(tickers, group, onLoaded) {
  if (!tickers.length) return;
  await startJob('momentum-status', { tickers, group }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON(`/api/momentum-status/${group}`);
    onLoaded(data.status || {});
  });
}

export function paintMomentumSlots(tickers, statusMap) {
  tickers.forEach(ticker => {
    const slot = document.getElementById(`momentum-slot-${ticker}`);
    if (slot && statusMap[ticker]) slot.innerHTML = momentumBadgeHTML(statusMap[ticker]);
  });
}

export function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.opacity = '1';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.opacity = '0'; }, 5000);
}

export function redditCell(count) {
  if (count == null) return '<span style="color:var(--muted)">-</span>';
  if (count === 0) return '<span style="color:var(--muted)">0</span>';
  const hot = count >= 10;
  return `<span style="color:${hot ? 'var(--yellow)' : 'var(--text)'};font-weight:${hot ? 700 : 400}">${count}</span>`;
}

export function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text == null ? '' : String(text);
  return div.innerHTML;
}

export function cleanEmoji(text) {
  return (text || '').replace(/[\uD83D\uDFE2\uDD34\uDFE1\u2B50\u26A0\u2713\uDEA8]/g, '').trim();
}

// External news URLs must not be able to introduce executable schemes.
export function safeHref(url) {
  try {
    const parsed = new URL(url, location.href);
    return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '#';
  } catch {
    return '#';
  }
}

export function toggleReasons(btn) {
  const extra = btn.previousElementSibling;
  if (extra.style.display === 'none') {
    extra.style.display = '';
    btn.textContent = 'less';
  } else {
    extra.style.display = 'none';
  }
}

export function fidelityLink(ticker, label, cls) {
  return `<a class="trade-link ${cls}" href="https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol=${ticker}" target="_blank" rel="noopener">${label} ↗</a>`;
}

export function renderTop20Table(top20) {
  if (!top20.length) return '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan from the Full Scan page.</p></div>';
  const rows = top20.map((s, i) => {
    const links = (s.why_links || []).slice(0, 3).map(l =>
      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
    ).join('');
    return `<tr>
      <td>#${i + 1}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td><span class="score-num">${s.combined_score ?? s.score ?? '-'}</span></td>
      <td><span id="momentum-slot-${s.ticker}"></span></td>
      <td>${redditCell(s.reddit_mentions_24h)}</td>
      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
    </tr>`;
  }).join('');
  return `
    <div class="card">
      <h2>Top 20 — Combined Pool</h2>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Combined Score</th><th scope="col">Momentum</th><th scope="col">Reddit</th><th scope="col">Why it's moving</th><th scope="col">Trade</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;
}
import { fetchJSON } from '../core/api.js';
import { startJob } from '../core/jobs.js';
import { _liveGuarded, _startLive } from '../core/refresh.js';
import { content, currentView, pageMeta } from '../core/state.js';
import {
  chartToggleButtonHTML,
  escapeHtml,
  fidelityLink,
  loadMomentumStatus,
  paintMomentumSlots,
  refreshOpenCharts,
  renderTop20Table,
  wireChartToggles,
} from '../core/ui-helpers.js';
import { loadNewsGroup, newsSectionHTML } from '../components/news.js';

let _shortlistPrices = {};

function catalystBadgeHTML(sentiment) {
  if (!sentiment) return '';
  const score = sentiment.catalyst_score || 0;
  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
  const ctype = (sentiment.catalyst_type || 'other').replace(/_/g, ' ');
  const sign = score > 0 ? '+' : '';
  return `<div><span class="agent-badge ${cls}">Catalyst ${sign}${score} — ${escapeHtml(ctype)}</span>
    <div class="agent-badge-sub">${escapeHtml(sentiment.summary)}</div></div>`;
}

function congressBadgeHTML(signal) {
  if (!signal || !signal.has_data) return '';
  const score = signal.score || 0;
  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
  const sign = score > 0 ? '+' : '';
  return `<div><span class="agent-badge ${cls}">Congress ${sign}${score.toFixed(1)}</span>
    <div class="agent-badge-sub">${escapeHtml(signal.summary)}</div></div>`;
}

function fundamentalsFlagsHTML(audit) {
  if (!audit) return '';
  const red = audit.red_flags || [];
  const green = audit.green_flags || [];
  let html = '';
  if (red.length) {
    const more = red.length > 1 ? ` (+${red.length - 1} more)` : '';
    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${escapeHtml(red[0].flag)}${more}</div>`;
  }
  if (green.length) {
    const more = green.length > 1 ? ` (+${green.length - 1} more)` : '';
    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
  }
  return html;
}

export async function renderShortlistView() {
  const data = await fetchJSON('/api/shortlist');
  if (currentView !== 'shortlist') return; // navigated away before this resolved
  // Set regardless of which branch below renders — a scan that legitimately
  // found zero candidates still has a real `generated` timestamp, and the
  // empty-state banner needs it to distinguish "no scan has ever run" from
  // "today's scan ran and found nothing" (see the two banner messages below).
  pageMeta.textContent = data.generated ? `Generated ${new Date(data.generated).toLocaleString()}` : '';
  if (!data.shortlist || data.shortlist.length === 0) {
    const top20 = await fetchJSON('/api/top20');
    if (currentView !== 'shortlist') return;
    // `result` (added alongside `generated`) distinguishes "no scan has run
    // yet" (data.generated is null) from "a scan ran and legitimately found
    // zero qualifying candidates" (data.result === 'no_candidates') — without
    // this, both looked identical and a normal empty trading day read as if
    // the pipeline were broken.
    const banner = !data.generated
      ? `No filtered shortlist yet — run a scan with AI agents enabled from the
         <a href="#/scan">Full Scan</a> page to get a Top 5 filtered by fundamentals,
         news sentiment, and congressional trading. Showing the raw Top 20 pool below instead.`
      : `Today's scan (generated ${new Date(data.generated).toLocaleString()}) found no candidates that
         passed screening criteria — this can happen on a normal trading day. Showing the raw Top 20
         pool below instead.`;
    content.innerHTML = `
      <div class="banner">${banner}</div>
      ${renderTop20Table(top20.top20 || [])}
    `;
    const fallbackTickers = (top20.top20 || []).map(s => s.ticker);
    loadMomentumStatus(fallbackTickers, 'shortlist-fallback', (statusMap) => paintMomentumSlots(fallbackTickers, statusMap));
    return;
  }

  const tickers = data.shortlist.map(s => s.ticker);

  const cards = data.shortlist.map((s, i) => {
    const badges = [
      catalystBadgeHTML(data.catalyst_sentiments[s.ticker]),
      congressBadgeHTML(data.congress_signals[s.ticker]),
      fundamentalsFlagsHTML(data.fundamentals_audits[s.ticker]),
    ].filter(Boolean).join('');
    const backfillNote = !s.passed_filters
      ? `<div class="backfill-note">Backfilled — didn't clear filters: ${(s.drop_reasons || []).join('; ') || 'below filter bar'}</div>`
      : '';
    const chartId = `short-chart-${s.ticker}`;
    return `
      <div class="pick-card ${!s.passed_filters ? 'backfilled' : ''}">
        <div class="pick-rank">#${i + 1}</div>
        <div class="pick-header">
          <span class="ticker">${s.ticker}</span>
          ${s.current_price != null ? `<span class="pick-price">$${s.current_price.toFixed(2)}</span>` : ''}
          <span id="${chartId}-slot"></span>
        </div>
        <div class="pick-scores">
          <div class="score-block"><div class="label">Composite</div><div class="value">${s.composite_score ?? '-'}</div></div>
          <div class="score-block"><div class="label">Base Score</div><div class="value">${s.combined_score ?? s.score ?? '-'}</div></div>
        </div>
        <div style="margin-bottom:10px"><span id="momentum-slot-${s.ticker}"></span></div>
        ${backfillNote}
        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
        ${fidelityLink(s.ticker, 'Buy on Fidelity', 'buy')}
        <div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
      </div>`;
  }).join('');

  content.innerHTML = `
    <div class="source-note email">
      <b>This is what your daily email sends.</b> Same 5 picks, same links — the email is just a snapshot of this page.
      <button type="button" class="news-jump-btn" onclick="document.getElementById('shortlistNews').scrollIntoView({behavior:'smooth'})">Jump to news ↓</button>
    </div>
    <div class="shortlist-grid">${cards}</div>
    <div id="shortlistNews" style="margin-top:24px"></div>`;

  loadShortlistCharts(tickers);
  loadShortlistNews(tickers);
  loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap));
  _startLive(() => {
    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
    _liveGuarded('shortlist-news', () => loadShortlistNews(tickers, true));
    _liveGuarded('shortlist-momentum', () => loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap)));
  });
}

function _shortlistSeries(ticker) {
  const h = _shortlistPrices[ticker];
  return h && h.length ? { history: h, entry: null, stop: null } : null;
}

async function loadShortlistCharts(tickers, silent) {
  if (!tickers.length) return;
  await startJob('price-history', { tickers, group: 'shortlist' }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON('/api/price-history/shortlist');
    _shortlistPrices = data.prices || {};

    if (!silent) {
      tickers.forEach(ticker => {
        const slot = document.getElementById(`short-chart-${ticker}-slot`);
        if (slot && _shortlistPrices[ticker] && _shortlistPrices[ticker].length) {
          slot.innerHTML = chartToggleButtonHTML(`short-chart-${ticker}`);
        }
      });
      wireChartToggles(content, _shortlistSeries, 'short-chart-');
    } else {
      refreshOpenCharts(_shortlistSeries, 'short-chart-');
    }
  });
}

async function loadShortlistNews(tickers, silent) {
  const el = document.getElementById('shortlistNews');
  if (!el) return;
  if (!silent) {
    el.innerHTML = newsSectionHTML('shortlist', 'News on your shortlist', 'loading');
  }
  await loadNewsGroup('shortlist', tickers, 'No shortlist yet.', silent);
}
import { fetchJSON } from '../core/api.js';
import { startJob } from '../core/jobs.js';
import { _liveGuarded, _startLive, liveBadgeHTML } from '../core/refresh.js';
import { content, currentView, pageMeta } from '../core/state.js';
import {
  chartToggleButtonHTML,
  cleanEmoji,
  escapeHtml,
  fidelityLink,
  loadMomentumStatus,
  paintMomentumSlots,
  redditCell,
  refreshOpenCharts,
  renderTop20Table,
  safeHref,
  wireChartToggles,
} from '../core/ui-helpers.js';

let _marketTop20Tickers = [];
let _marketSignalPrices = {};
let _marketSignalTickers = [];
const MARKET_CHART_PREFIX = 'market-sig-chart-';

export async function renderMarketView() {
  const scans = await fetchJSON('/api/scans');
  if (currentView !== 'market') return; // navigated away before this resolved
  if (!scans.length) {
    content.innerHTML = '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan to get started.</p></div>';
    return;
  }
  content.innerHTML = `
    <div class="source-note email">
      <b>This is the full pool your email's picks are drawn from.</b> Buy/Sell Signals and the Top 20 table
      here are the same lists that get emailed (capped at 15 rows there; everything's shown here) — the
      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
    </div>
    <div style="margin-bottom:16px">
      <select class="scan-select" id="scanSelect"></select>
    </div>
    <div id="marketBody"></div>
    <div id="newsSections" style="margin-top:24px"></div>`;
  const sel = document.getElementById('scanSelect');
  scans.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.path;
    opt.textContent = s.date.replace('_', ' ');
    sel.appendChild(opt);
  });
  sel.addEventListener('change', () => loadMarketScan(sel.value));
  loadMarketScan(scans[0].path);
  loadMarketNews();
  _startLive(() => {
    _liveGuarded('market-news', () => loadMarketNews(true));
    _liveGuarded('market-momentum', () => loadMomentumStatus(
      _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
    ));
    _liveGuarded('market-signal-charts', () => loadMarketSignalCharts(_marketSignalTickers, true));
  });
}

async function loadMarketNews(silent) {
  const el = document.getElementById('newsSections');
  if (!el) return; // navigated away before this resolved
  if (!silent) {
    el.innerHTML = _newsSectionHTML('positions', 'News on your positions', 'loading') +
                    _newsSectionHTML('buy', "News on what the scanner's telling you to buy", 'loading');
  }

  const [positionsData, top20Data] = await Promise.all([
    fetchJSON('/api/positions'), fetchJSON('/api/top20'),
  ]);
  const positionTickers = (positionsData.position_analyses || []).map(a => a.ticker);
  const buyTickers = (top20Data.top20 || []).slice(0, 8).map(s => s.ticker);

  await Promise.all([
    _loadNewsGroup('positions', positionTickers, 'Upload your positions in the Positions tab to see news for them here.', silent),
    _loadNewsGroup('buy', buyTickers, 'No Top 20 pool yet — run a scan from the Full Scan tab first.', silent),
  ]);
}

export function _newsSectionHTML(group, title, bodyHTML) {
  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
}

export async function _loadNewsGroup(group, tickers, emptyMsg, silent) {
  const bodyEl = document.getElementById(`news-${group}-body`);
  if (!bodyEl) return; // navigated away before this resolved
  if (!tickers.length) {
    bodyEl.innerHTML = `<div style="color:var(--muted);font-size:13px">${emptyMsg}</div>`;
    return;
  }
  if (!silent) {
    bodyEl.innerHTML = '<div style="color:var(--muted);font-size:13px"><span class="spinner"></span> Fetching real headlines…</div>';
  }

  await startJob('news', { tickers, group }, async (st) => {
    const el = document.getElementById(`news-${group}-body`);
    if (!el) return; // navigated away mid-job
    if (st.status === 'success') {
      const data = await fetchJSON(`/api/news/${group}`);
      el.innerHTML = _renderNewsGroupHTML(data.news || {});
    } else if (!silent && (st.status === 'error' || st.status === 'stopped')) {
      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
    }
  });
}

function _renderNewsGroupHTML(newsByTicker) {
  const tickers = Object.keys(newsByTicker);
  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
  return `<div class="news-ticker-grid">${tickers.map(ticker => {
    const items = newsByTicker[ticker] || [];
    const list = items.length
      ? items.map(h => `
          <a href="${safeHref(h.url)}" target="_blank" rel="noopener" class="news-headline">
            <div class="news-headline-title">${escapeHtml(h.title)}</div>
            <div class="news-headline-meta">${escapeHtml(h.publisher || 'Unknown source')}${h.pub_date ? ' · ' + escapeHtml(new Date(h.pub_date).toLocaleDateString()) : ''}</div>
          </a>`).join('')
      : '<div style="color:var(--muted);font-size:12px">No recent headlines.</div>';
    return `<div class="news-ticker-block"><div class="ticker" style="margin-bottom:6px">${escapeHtml(ticker)}</div>${list}</div>`;
  }).join('')}</div>`;
}

// Pure by design (exported for tests/js characterization coverage): maps
// buy_signals to {x, y, signal} scatter points. Only keeps signals with a
// finite score, a positive max_score, and a finite rs — a missing/null field
// on any of these would otherwise plot as (0,0) or NaN, silently misleading
// rather than just being omitted. Y is score-as-percentage-of-max rather
// than the raw score, since max_score isn't always the same fixed number.
export function buildBuyOpportunityPoints(buySignals) {
  return (buySignals || [])
    .filter(s => Number.isFinite(s.score) && Number.isFinite(s.max_score) && s.max_score > 0 && Number.isFinite(s.rs))
    .map(s => ({ x: s.rs, y: (s.score / s.max_score) * 100, signal: s }));
}

function _buyOpportunityChartCardHTML(buySignals) {
  const plotted = buildBuyOpportunityPoints(buySignals).length;
  const total = (buySignals || []).length;
  const omitted = total - plotted;
  const omittedNote = omitted > 0
    ? ` (${omitted} signal${omitted === 1 ? '' : 's'} without a plottable score/RS not shown)`
    : '';
  return `
    <div class="card">
      <h2>Buy Opportunity Map</h2>
      <div class="card-sub">Right = stronger relative momentum · Up = higher scanner conviction${omittedNote}</div>
      <div class="scatter-chart-wrap"><canvas id="marketScatterChart"></canvas></div>
      <div style="color:var(--muted);font-size:11px;margin-top:8px">Hover a dot for details, click to jump to it in the Buy Signals table below.</div>
    </div>`;
}

function _renderBuyOpportunityChart(buySignals) {
  const points = buildBuyOpportunityPoints(buySignals);
  renderMarketScatterChart('marketScatterChart', points, _showBuySignal);
}

export function _showBuySignal(signal) {
  _activateSignalTab('buy');
  _highlightBuyRow(signal);
}

// Scrolls to and briefly pulses a ticker's row in the Buy Signals table —
// used as the scatter chart's click handler. Does not open the Fidelity
// trade link directly: a dense chart is easy to mis-click, and jumping to
// the row (rather than an outbound broker link) lets the user confirm the
// full breakdown before intentionally clicking Trade themselves.
function _highlightBuyRow(signal) {
  const row = document.querySelector(`#buySignalsBody tr[data-ticker="${signal.ticker}"]`);
  if (!row) return;
  row.scrollIntoView({ behavior: 'smooth', block: 'center' });
  row.classList.add('row-highlight-pulse');
  setTimeout(() => row.classList.remove('row-highlight-pulse'), 2000);
}

function _marketSignalSeries(ticker) {
  const h = _marketSignalPrices[ticker];
  return h && h.length ? { history: h, entry: null, stop: null } : null;
}

// Fetches price history for every ticker shown in the Buy/Sell tables (both,
// regardless of which tab is active — the chart-toggle button on a sell row
// works even if the sell panel hasn't been the visible tab yet since the
// tickers/prices are fetched once up front, not per-tab). Reuses the same
// batched price-history job Shortlist/Positions use — one job, not one
// request per ticker.
async function loadMarketSignalCharts(tickers, silent) {
  if (!tickers.length) return;
  await startJob('price-history', { tickers, group: 'market-signals' }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON('/api/price-history/market-signals');
    _marketSignalPrices = data.prices || {};
    if (silent) {
      refreshOpenCharts(_marketSignalSeries, MARKET_CHART_PREFIX);
    } else {
      const card = document.getElementById('marketSignalsCard');
      if (card) wireChartToggles(card, _marketSignalSeries, MARKET_CHART_PREFIX);
    }
  });
}

function _signalTabLabel(label, shownCount, totalCount) {
  return totalCount !== shownCount
    ? `${label} (${shownCount} of ${totalCount})`
    : `${label} (${shownCount})`;
}

export function _signalTabsHTML(scan) {
  const buyTotal = scan.stats.buy_count ?? scan.buy_signals.length;
  const sellTotal = scan.stats.sell_count ?? scan.sell_signals.length;
  return `
    <div class="card" id="marketSignalsCard">
      <div class="signal-tabs-header">
        <div>
          <h2 style="margin-bottom:2px">Market Signals</h2>
          <div class="card-sub" style="margin:0">Calculated ${escapeHtml(scan.generated || scan.scan_date || 'unknown')}</div>
        </div>
        <div class="signal-tabs" role="tablist" aria-label="Market signal type">
          <button class="btn signal-tab active" id="buySignalsTab" type="button" role="tab" data-signal-tab="buy" aria-selected="true" aria-controls="buySignalsPanel" tabindex="0">${_signalTabLabel('Buy', scan.buy_signals.length, buyTotal)}</button>
          <button class="btn signal-tab" id="sellSignalsTab" type="button" role="tab" data-signal-tab="sell" aria-selected="false" aria-controls="sellSignalsPanel" tabindex="-1">${_signalTabLabel('Sell', scan.sell_signals.length, sellTotal)}</button>
        </div>
      </div>
      <div id="buySignalsPanel" role="tabpanel" aria-labelledby="buySignalsTab">
        <div style="overflow-x:auto"><table class="signal-table">
          <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Price</th><th scope="col">Chart</th><th scope="col">Score</th><th scope="col">Entry</th><th scope="col">Stop Loss</th><th scope="col">R:R</th><th scope="col">RS</th><th scope="col">Reddit</th><th scope="col">Key Reasons</th><th scope="col">Trade</th></tr></thead>
          <tbody id="buySignalsBody">${renderBuyRows(scan.buy_signals)}</tbody>
        </table></div>
      </div>
      <div id="sellSignalsPanel" role="tabpanel" aria-labelledby="sellSignalsTab" hidden>
        <div style="overflow-x:auto"><table class="signal-table">
          <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Price</th><th scope="col">Chart</th><th scope="col">Score</th><th scope="col">Severity</th><th scope="col">Breakdown</th><th scope="col">Reddit</th><th scope="col">Reasons</th><th scope="col">Trade</th></tr></thead>
          <tbody id="sellSignalsBody"></tbody>
        </table></div>
      </div>
    </div>`;
}

export function _activateSignalTab(name, sellSignals = []) {
  const buyTab = document.getElementById('buySignalsTab');
  const sellTab = document.getElementById('sellSignalsTab');
  const buyPanel = document.getElementById('buySignalsPanel');
  const sellPanel = document.getElementById('sellSignalsPanel');
  if (!buyTab || !sellTab || !buyPanel || !sellPanel) return;

  const showBuy = name === 'buy';
  if (!showBuy) {
    const sellBody = document.getElementById('sellSignalsBody');
    if (sellBody && sellBody.dataset.rendered !== 'true') {
      sellBody.innerHTML = renderSellRows(sellSignals);
      sellBody.dataset.rendered = 'true';
      // Sell rows' chart-toggle buttons don't exist until this lazy render,
      // so they must be wired here rather than only at initial page load —
      // the same reason the Buy panel's toggles are wired separately, right
      // after loadMarketSignalCharts's price fetch resolves.
      const card = document.getElementById('marketSignalsCard');
      if (card) wireChartToggles(card, _marketSignalSeries, MARKET_CHART_PREFIX);
    }
  }

  buyTab.setAttribute('aria-selected', String(showBuy));
  sellTab.setAttribute('aria-selected', String(!showBuy));
  buyTab.tabIndex = showBuy ? 0 : -1;
  sellTab.tabIndex = showBuy ? -1 : 0;
  buyTab.classList.toggle('active', showBuy);
  sellTab.classList.toggle('active', !showBuy);
  buyPanel.hidden = !showBuy;
  sellPanel.hidden = showBuy;
}

export function _wireSignalTabs(sellSignals) {
  const tabs = [...document.querySelectorAll('[role="tab"][data-signal-tab]')];
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => _activateSignalTab(tab.dataset.signalTab, sellSignals));
    tab.addEventListener('keydown', (event) => {
      let nextIndex;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = tabs.length - 1;
      if (nextIndex === undefined) return;
      event.preventDefault();
      const nextTab = tabs[nextIndex];
      _activateSignalTab(nextTab.dataset.signalTab, sellSignals);
      nextTab.focus();
    });
  });
}

async function loadMarketScan(path) {
  const [scan, top20] = await Promise.all([
    fetchJSON('/api/scan?path=' + encodeURIComponent(path)),
    fetchJSON('/api/top20'),
  ]);
  if (currentView !== 'market') return; // navigated away before this resolved
  if (scan.error) {
    document.getElementById('marketBody').innerHTML = '<div class="no-data"><h2>No scan data</h2></div>';
    return;
  }
  pageMeta.textContent = `${scan.scan_date} · ${scan.stats.analyzed || '?'} analyzed · ${scan.regime}`;

  const buyCount = scan.stats.buy_count ?? scan.buy_signals.length;
  const sellCount = scan.stats.sell_count ?? scan.sell_signals.length;
  const topScore = scan.buy_signals.length ? scan.buy_signals[0].score : '-';
  const regimeClass = scan.regime.includes('RISK-ON') ? 'risk-on' : scan.regime.includes('RISK-OFF') ? 'risk-off' : 'transitional';

  document.getElementById('marketBody').innerHTML = `
    <div class="stats-row">
      <div class="stat-card green"><div class="label">Buy Signals</div><div class="value">${buyCount}</div><div class="sub">Phase 2 confirmed uptrends</div></div>
      <div class="stat-card red"><div class="label">Sell Signals</div><div class="value">${sellCount}</div><div class="sub">Phase 3/4 breakdowns</div></div>
      <div class="stat-card blue"><div class="label">Top Score</div><div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div><div class="sub">${scan.buy_signals.length ? scan.buy_signals[0].ticker : '-'}</div></div>
      <div class="stat-card"><div class="label">Universe</div><div class="value">${(scan.stats.analyzed || 0).toLocaleString()}</div><div class="sub">of ${(scan.stats.total_universe || 0).toLocaleString()} | ${scan.stats.processing_minutes || '?'} min</div></div>
      <div class="stat-card ${scan.spy.phase === 2 ? 'green' : scan.spy.phase === 4 ? 'red' : 'yellow'}"><div class="label">SPY Phase</div><div class="value">${scan.spy.phase || '?'}</div><div class="sub">${scan.spy.trend || ''} @ $${(scan.spy.price || 0).toFixed(2)}</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Market Breadth</h2><div class="chart-wrap"><canvas id="breadthChart"></canvas></div></div>
      <div class="card">
        <h2>SPY Regime</h2>
        <span class="regime-badge ${regimeClass}">${scan.regime}</span>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px">
          <div><div style="color:var(--muted);font-size:11px">Phase</div><div style="font-size:18px;font-weight:700">${scan.spy.phase} - ${scan.spy.phase_name || ''}</div></div>
          <div><div style="color:var(--muted);font-size:11px">Confidence</div><div style="font-size:18px;font-weight:700">${scan.spy.confidence || '?'}%</div></div>
        </div>
      </div>
    </div>
    ${_buyOpportunityChartCardHTML(scan.buy_signals)}
    ${renderTop20Table(top20.top20 || [])}
    ${_signalTabsHTML(scan)}`;

  renderBreadthChart('breadthChart', scan.breadth);
  _wireSignalTabs(scan.sell_signals);
  _renderBuyOpportunityChart(scan.buy_signals);

  // The live-refresh closure must always read the current scan selection.
  _marketTop20Tickers = (top20.top20 || []).map(s => s.ticker);
  loadMomentumStatus(_marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap));

  // Union of both tabs' tickers, fetched once regardless of which tab is
  // active — a chart toggle on a lazily-rendered Sell row still needs its
  // price data to already be present the moment that row exists.
  _marketSignalTickers = [...scan.buy_signals, ...scan.sell_signals].map(s => s.ticker);
  loadMarketSignalCharts(_marketSignalTickers);
}

function _signalChartRowHTML(ticker, colspan) {
  const chartId = `${MARKET_CHART_PREFIX}${ticker}`;
  return `<tr class="chart-row"><td colspan="${colspan}">
    <div class="position-chart-wrap signal-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
  </td></tr>`;
}

function renderBuyRows(signals) {
  if (!signals.length) return '<tr><td colspan="12" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
  return signals.map(s => {
    const pct = (s.score / (s.max_score || 125)) * 100;
    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
    const entryClass = (s.entry_quality || '').toLowerCase();
    const topReasons = (s.reasons || []).slice(0, 3).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    const extra = (s.reasons || []).slice(3);
    const extraHTML = extra.length
      ? `<div class="extra-reasons" style="display:none">${extra.map(r => `<li>${cleanEmoji(r)}</li>`).join('')}</div><button class="expand-btn" onclick="toggleReasons(this)">+${extra.length} more</button>`
      : '';
    return `<tr data-ticker="${s.ticker}">
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td>${s.current_price != null ? '$' + s.current_price.toFixed(2) : '-'}</td>
      <td>${chartToggleButtonHTML(`${MARKET_CHART_PREFIX}${s.ticker}`)}</td>
      <td><span class="score-num">${s.score}</span><div class="score-bar"><div class="fill" style="width:${pct}%;background:${barColor}"></div></div></td>
      <td><span class="badge ${entryClass}">${s.entry_quality || '-'}</span></td>
      <td>${s.stop_loss ? '$' + s.stop_loss.toFixed(2) : '-'}</td>
      <td style="color:${(s.rr_ratio || 0) >= 3 ? 'var(--green)' : (s.rr_ratio || 0) >= 2 ? 'var(--text)' : 'var(--yellow)'}">${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : '-'}</td>
      <td style="color:${(s.rs || 0) > 0.1 ? 'var(--green)' : (s.rs || 0) > 0 ? 'var(--text)' : 'var(--red)'}">${s.rs != null ? s.rs.toFixed(3) : '-'}</td>
      <td>${redditCell(s.reddit_mentions)}</td>
      <td><ul class="reasons-list">${topReasons}</ul>${extraHTML}</td>
      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
    </tr>${_signalChartRowHTML(s.ticker, 12)}`;
  }).join('');
}

function renderSellRows(signals) {
  if (!signals.length) return '<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
  return signals.map(s => {
    const sevClass = (s.severity || 'medium').toLowerCase();
    const reasons = (s.reasons || []).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    return `<tr data-ticker="${s.ticker}">
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td>${s.current_price != null ? '$' + s.current_price.toFixed(2) : '-'}</td>
      <td>${chartToggleButtonHTML(`${MARKET_CHART_PREFIX}${s.ticker}`)}</td>
      <td><span class="score-num">${s.score}</span></td>
      <td><span class="badge ${sevClass}">${(s.severity || '?').toUpperCase()}</span></td>
      <td>${s.breakdown_level ? '$' + s.breakdown_level.toFixed(2) : '-'}</td>
      <td>${redditCell(s.reddit_mentions)}</td>
      <td><ul class="reasons-list">${reasons}</ul></td>
      <td>${fidelityLink(s.ticker, 'Sell', 'sell')}</td>
    </tr>${_signalChartRowHTML(s.ticker, 10)}`;
  }).join('');
}
import { content, pageTitle, pageMeta, setCurrentView } from './state.js';
import { _stopLive } from './refresh.js';

// Populated by initRouter with the VIEWS map from dashboard.js. Kept as
// module state rather than an import to avoid a circular dependency —
// dashboard.js defines the view render functions and imports route()/
// initRouter() from here, so router.js can't import VIEWS back from
// dashboard.js at module-evaluation time.
let _views = {};

export function route() {
  _stopLive();
  const hash = (location.hash || '#/positions').replace('#/', '');
  const view = _views[hash] ? hash : 'positions';
  setCurrentView(view);
  document.querySelectorAll('.nav-item').forEach(a => {
    const isActive = a.dataset.view === view;
    a.classList.toggle('active', isActive);
    if (isActive) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  pageTitle.textContent = _views[view].title;
  pageMeta.innerHTML = '';
  content.innerHTML = '<div class="no-data"><span class="spinner"></span> Loading…</div>';
  _views[view].render();
}

export function initRouter(viewsMap) {
  _views = viewsMap;
  window.addEventListener('hashchange', route);
  route();
}
13:  <nav class="sidebar" aria-label="Primary">
16:    <div class="nav-group" role="group" aria-label="Monitor">
17:      <div class="nav-group-label">Monitor</div>
18:      <a href="#/positions" class="nav-item" data-view="positions">
19:        <span class="nav-item-title">Positions</span>
20:        <span class="nav-item-sub">Your portfolio</span>
22:      <a href="#/shortlist" class="nav-item" data-view="shortlist">
23:        <span class="nav-item-title">Shortlist</span>
24:        <span class="nav-item-sub">Today's email picks</span>
26:      <a href="#/market" class="nav-item" data-view="market">
27:        <span class="nav-item-title">Market</span>
28:        <span class="nav-item-sub">Full scan, all signals</span>
32:    <div class="nav-group" role="group" aria-label="Analyze">
33:      <div class="nav-group-label">Analyze</div>
34:      <a href="#/backtests" class="nav-item" data-view="backtests">
35:        <span class="nav-item-title">Backtests</span>
36:        <span class="nav-item-sub">Past performance, not email</span>
40:    <div class="nav-group" role="group" aria-label="Run">
41:      <div class="nav-group-label">Run</div>
42:      <a href="#/run" class="nav-item" data-view="run">
43:        <span class="nav-item-title">Run Simulation</span>
44:        <span class="nav-item-sub">Test a strategy</span>
46:      <a href="#/scan" class="nav-item" data-view="scan">
47:        <span class="nav-item-title">Full Scan</span>
48:        <span class="nav-item-sub">Trigger a new scan</span>
53:  </nav>

exec
/bin/zsh -lc "sed -n '1,180p' dashboard.py; sed -n '250,330p' dashboard.py; sed -n '380,535p' dashboard.py; sed -n '570,730p' dashboard.py; sed -n '750,815p' dashboard.py; sed -n '1,140p' static/js/dashboard.js; sed -n '1,100p' templates/dashboard.html; sed -n '1,280p' tests/test_dashboard_jobs.py; sed -n '1,260p' tests/test_current_price_flow.py; rg --files tests/js | sort" in /Users/badripratti/Desktop/stock-screener
 succeeded in 0ms:
#!/usr/bin/env python3
"""Interactive web dashboard for Stock Screener results.

Usage:
    python dashboard.py                    # Start dashboard on port 5050
    python dashboard.py --port 8080        # Custom port
    python dashboard.py --scan             # Run test scan first, then launch
    python dashboard.py --scan --full      # Run full scan first, then launch
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, render_template, request

# When bundled as a standalone .app (py2app sets sys.frozen), this file lives
# inside the bundle's Resources folder, not the real project checkout — but
# the dashboard always needs to read/write the real repo (git pull/push via
# /api/sync, data/ files, and it shells out to the project's own venv to run
# scripts). So PROJECT_ROOT deliberately does NOT follow __file__ when frozen;
# it points at the real checkout instead, overridable via STOCK_SCREENER_ROOT
# for anyone whose folder lives somewhere other than the default.
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(os.environ.get("STOCK_SCREENER_ROOT", str(Path.home() / "Desktop" / "stock-screener"))).resolve()
else:
    PROJECT_ROOT = Path(__file__).parent.resolve()

# py2app's own bootstrap chdir's the frozen process into the .app bundle's
# Resources folder before this module even runs — wrong for us either way, we
# always want PROJECT_ROOT. Setting it here (rather than passing cwd= on each
# subprocess call below) is what keeps those calls eligible for macOS's safe
# posix_spawn() path instead of fork()+exec() — see the comment in
# _launch_job() for why that distinction matters for the packaged .app.
os.chdir(str(PROJECT_ROOT))

app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"), static_folder=str(PROJECT_ROOT / "static"))

SCAN_DIR = PROJECT_ROOT / "data" / "daily_scans"
BACKTEST_DIR = PROJECT_ROOT / "data" / "backtest_history"
ADHOC_DIR = PROJECT_ROOT / "data" / "adhoc_simulations"
POSITIONS_CSV = PROJECT_ROOT / "data" / "positions_latest.csv"
VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"


def _venv_python():
    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


# The plain "git" on PATH (/usr/bin/git) is actually a stub that shells out to
# `xcodebuild -find git` to locate the real binary — on a machine with a
# broken/corrupted Xcode.app (as opposed to just the separate, lighter-weight
# Command Line Tools), that stub fails with an unrelated-looking dlopen error
# and git (and the Sync button) stops working entirely, even though a real,
# working git binary is usually still sitting right here. Preferring it
# sidesteps the broken xcodebuild lookup rather than depending on it.
_CLT_GIT = Path("/Library/Developer/CommandLineTools/usr/bin/git")


def _git_binary():
    if _CLT_GIT.exists():
        return str(_CLT_GIT)
    return shutil.which("git") or "/usr/bin/git"


def _read_json(path, default):
    """Load a JSON file, falling back to `default` if it's missing/unreadable
    — every read-only route uses this so "no data yet" is always a normal 200
    response, never a bare error."""
    path = Path(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return default


def parse_scan_file(filepath):
    """Parse a scan .txt file into structured data."""
    text = Path(filepath).read_text(encoding="utf-8")

    data = {
        "scan_date": "",
        "generated": "",
        "stats": {},
        "spy": {},
        "breadth": {},
        "regime": "",
        "buy_signals": [],
        "sell_signals": [],
    }

    # Header stats
    m = re.search(r"Scan Date:\s*(.+)", text)
    if m:
        data["scan_date"] = m.group(1).strip()

    m = re.search(r"Generated:\s*(.+)", text)
    if m:
        data["generated"] = m.group(1).strip()

    m = re.search(r"Total Universe:\s*([\d,]+)", text)
    if m:
        data["stats"]["total_universe"] = int(m.group(1).replace(",", ""))

    m = re.search(r"Analyzed:\s*([\d,]+)", text)
    if m:
        data["stats"]["analyzed"] = int(m.group(1).replace(",", ""))

    m = re.search(r"Processing Time:\s*([\d.]+)", text)
    if m:
        data["stats"]["processing_minutes"] = float(m.group(1))

    m = re.search(r"Error Rate:\s*([\d.]+)%", text)
    if m:
        data["stats"]["error_rate"] = float(m.group(1))

    m = re.search(r"Buy Signals:\s*(\d+)", text)
    if m:
        data["stats"]["buy_count"] = int(m.group(1))

    m = re.search(r"Sell Signals:\s*(\d+)", text)
    if m:
        data["stats"]["sell_count"] = int(m.group(1))

    # SPY
    m = re.search(r"Phase:\s*(\d)\s*-\s*(.+)", text)
    if m:
        data["spy"]["phase"] = int(m.group(1))
        data["spy"]["phase_name"] = m.group(2).strip()

    m = re.search(r"Trend:\s*(\w+)", text)
    if m:
        data["spy"]["trend"] = m.group(1).strip()

    m = re.search(r"Current Price:\s*\$([\d.]+)", text)
    if m:
        data["spy"]["price"] = float(m.group(1))

    m = re.search(r"Confidence:\s*(\d+)%", text)
    if m:
        data["spy"]["confidence"] = int(m.group(1))

    # Breadth
    for phase_num, label in [(1, "phase_1"), (2, "phase_2"), (3, "phase_3"), (4, "phase_4")]:
        m = re.search(
            rf"Phase {phase_num} \([^)]+\):\s*(\d+)\s*stocks\s*\(([\d.]+)%\)", text
        )
        if m:
            data["breadth"][f"{label}_count"] = int(m.group(1))
            data["breadth"][f"{label}_pct"] = float(m.group(2))

    m = re.search(r"Market Regime:\s*(.+)", text)
    if m:
        data["regime"] = m.group(1).strip()

    # Buy signals — extract each signal as header+details block
    buy_pattern = re.compile(
        r"BUY #(\d+):\s*(\w+)\s*\|\s*Score:\s*([\d.]+)/(\d+)"
        r".*?(?=BUY #\d+:|SELL #\d+:|={50,}.*(?:TOP SELL|END OF|ADDITIONAL)|\Z)",
        re.DOTALL,
    )
    for bm in buy_pattern.finditer(text):
        block = bm.group(0)
        signal = {
            "rank": int(bm.group(1)),
            "ticker": bm.group(2),
            "score": float(bm.group(3)),
            "max_score": int(bm.group(4)),
            signal["severity"] = m.group(2)

        m = re.search(r"Breakdown:\s*\$([\d.]+)", block)
        if m:
            signal["breakdown_level"] = float(m.group(1))

        m = re.search(r"Reddit Mentions \(24h\):\s*(\d+)", block)
        if m:
            signal["reddit_mentions"] = int(m.group(1))

        reasons = re.findall(r"[•]\s*(.+)", block)
        signal["reasons"] = [r.strip() for r in reasons[:5]]

        data["sell_signals"].append(signal)

    return data


def get_scan_files():
    """Get list of available scan files, newest first."""
    if not SCAN_DIR.exists():
        return []
    files = sorted(SCAN_DIR.glob("optimized_scan_*.txt"), reverse=True)
    return [{"name": f.stem, "path": str(f), "date": f.stem.replace("optimized_scan_", "")} for f in files]


def get_backtest_files():
    """Get list of walk-forward backtest history files, newest first."""
    if not BACKTEST_DIR.exists():
        return []
    files = sorted(BACKTEST_DIR.glob("walk_forward_*.json"), reverse=True)
    out = []
    for f in files:
        data = _read_json(f, {})
        out.append({"name": f.stem, "path": str(f), "generated": data.get("generated")})
    return out


# ---------------------------------------------------------------------------
# Background job runner — generalized version of control_panel.py's
# STATE-dict + subprocess.Popen + polling pattern, keyed by a generated job_id
# (instead of a fixed command id) so multiple differently-configured
# simulations can run/be polled independently in one session.
# ---------------------------------------------------------------------------

JOBS = {}
JOBS_LOCK = threading.Lock()


def _clean_subprocess_env():
    """A copy of the current environment with PYTHONHOME/PYTHONPATH stripped —
    see the comment in _launch_job() for why those two specifically break a
    venv/bin/python subprocess when this process is the packaged .app. Also
    forces unbuffered child stdout: Python fully block-buffers stdout when
    it's a pipe (not a terminal), so without this every print() in the child
    script sits in a buffer until the process exits and flushes everything at
    once — the live output panel would show nothing the whole run, then the
    entire report appears all at once right as the job finishes, which reads
    exactly like it's stuck rather than actually working."""
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env["PYTHONUNBUFFERED"] = "1"
    return env


# How long a job is allowed to run before the dashboard force-kills it. Needed
# because a hung network call somewhere deep in a third-party library (a scan
# hit this: yfinance/urllib3 claims a 10s timeout on price history, but a real
# run still blocked forever in an SSL socket read to a Yahoo Finance host that
# had already dropped the connection — the retry/timeout logic just never
# kicked in) can otherwise sit forever, holding the job "running" and, via the
# close_fds=False tradeoff above, an inherited copy of the Flask listening
# socket — which is what took the whole dashboard offline last time this
# happened, not just the one job.
JOB_TIMEOUT_SECONDS = {"scan": 45 * 60}
DEFAULT_JOB_TIMEOUT_SECONDS = 10 * 60


def _kill_hung_job(job_id, proc):
    if proc.poll() is not None:
        # ASCII character in the child's output (e.g. the em-dashes/bullets in
        # position_manager.py's rationale text).
        proc = subprocess.Popen(
            cmd, env=_clean_subprocess_env(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding="utf-8", errors="replace", bufsize=1, close_fds=False,
        )
        with JOBS_LOCK:
            JOBS[job_id]["proc"] = proc

        timeout_seconds = JOB_TIMEOUT_SECONDS.get(kind, DEFAULT_JOB_TIMEOUT_SECONDS)
        watchdog = threading.Timer(timeout_seconds, _kill_hung_job, args=(job_id, proc))
        watchdog.daemon = True
        watchdog.start()
        try:
            for line in proc.stdout:
                with JOBS_LOCK:
                    JOBS[job_id]["output"].append(line.rstrip("\n"))
            proc.wait()
        finally:
            watchdog.cancel()

        with JOBS_LOCK:
            JOBS[job_id]["returncode"] = proc.returncode
            JOBS[job_id]["status"] = "success" if proc.returncode == 0 else "error"
            JOBS[job_id]["proc"] = None
            JOBS[job_id]["result_path"] = result_path
    except Exception as exc:
        with JOBS_LOCK:
            JOBS[job_id]["output"].append(f"[dashboard] failed to launch: {exc}")
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["proc"] = None


def _build_job(kind, body):
    """Build (cmd, result_path) for a job kind from a request body, using each
    underlying script's own argparse defaults when a param is omitted."""
    python = _venv_python()
    job_id = uuid.uuid4().hex[:12]

    if kind == "scan":
        cmd = [python, str(PROJECT_ROOT / "run_optimized_scan.py")]
        if not body.get("full"):
            cmd.append("--test-mode")
        if body.get("enable_llm_agents"):
            cmd.append("--enable-llm-agents")
        result_path = str(SCAN_DIR / "shortlist_latest.json")

    elif kind == "backtest-top3":
        result_path = str(ADHOC_DIR / f"backtest_top3_{job_id}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "backtest_top3.py"),
            "--days", str(body.get("days", 7)),
            "--sample", str(body.get("sample", 150)),
            "--investment", str(body.get("investment", 1000)),
            "--json-out", result_path,
        ]

    elif kind == "backtest-monte-carlo":
        result_path = str(ADHOC_DIR / f"monte_carlo_{job_id}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "backtest_top3_monte_carlo.py"),
            "--days", str(body.get("days", 7)),
            "--pool", str(body.get("pool", 300)),
            "--sample", str(body.get("sample", 150)),
            "--iterations", str(body.get("iterations", 100)),
            "--investment", str(body.get("investment", 1000)),
            "--json-out", result_path,
        ]

    elif kind == "walk-forward":
        result_path = str(BACKTEST_DIR / "latest.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "walk_forward_backtest.py"),
            "--universe-size", str(body.get("universe_size", 250)),
            "--lookback-months", str(body.get("lookback_months", 9)),
            "--step-days", str(body.get("step_days", 14)),
            "--top-n", str(body.get("top_n", 10)),
            "--max-hold-days", str(body.get("max_hold_days", 60)),
            "--investment-per-trade", str(body.get("investment_per_trade", 1000)),
            "--seed", str(body.get("seed", 42)),
        ]

    elif kind == "positions":
        if not POSITIONS_CSV.exists():
            return None, None, None
        result_path = str(ADHOC_DIR / "positions_latest.json")
        cmd = [python, str(PROJECT_ROOT / "manage_positions.py"), "--csv", str(POSITIONS_CSV), "--json-out", result_path]

    elif kind == "news":
        tickers = body.get("tickers") or []
        group = body.get("group", "misc")
        if not tickers:
            return None, None, None
        result_path = str(ADHOC_DIR / f"news_{group}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "fetch_news.py"),
            "--tickers", ",".join(tickers),
            "--json-out", result_path,
        ]

    elif kind == "price-history":
        tickers = body.get("tickers") or []
        group = body.get("group", "misc")
        if not tickers:
            return None, None, None
        result_path = str(ADHOC_DIR / f"price_history_{group}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "fetch_price_history.py"),
            "--tickers", ",".join(tickers),
            "--json-out", result_path,
        ]

    elif kind == "momentum-status":
        tickers = body.get("tickers") or []
        group = body.get("group", "misc")
        if not tickers:
            return None, None, None
        result_path = str(ADHOC_DIR / f"momentum_status_{group}.json")
        cmd = [
            python, str(PROJECT_ROOT / "scripts" / "fetch_momentum_status.py"),
            "--tickers", ",".join(tickers),
            "--group", group,
            "--json-out", result_path,
        ]

    else:
        return None, None, None

    return job_id, cmd, result_path


JOB_RETENTION_SECONDS = 15 * 60  # how long a finished job stays pollable after completion


def _prune_old_jobs():
    """Drop finished jobs older than JOB_RETENTION_SECONDS. Without this, JOBS
    grows without bound — the dashboard's own "Live" auto-refresh (every 90s,
    across positions/news/price-history) now starts a job on every tick for as
    long as the app stays open, so an all-day session could otherwise pile up
    thousands of entries (each holding its full output line list) in memory.
    Called opportunistically on every new job start rather than on a timer."""
    now = time.time()
    with JOBS_LOCK:
        stale = [
            jid for jid, job in JOBS.items()
            if job["status"] not in ("queued", "running") and (now - job["started"]) > JOB_RETENTION_SECONDS
        ]
        for jid in stale:
            del JOBS[jid]


@app.route("/api/jobs/<kind>", methods=["POST"])
def api_start_job(kind):
    if kind == "positions" and not POSITIONS_CSV.exists():
        return jsonify({"error": "no positions CSV uploaded yet"}), 400
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "unknown job"}), 404
        proc = job["proc"]
    if proc and proc.poll() is None:
        proc.terminate()
        with JOBS_LOCK:
            job["status"] = "stopped"
        return jsonify({"ok": True})
    return jsonify({"error": "not running"}), 409


def _git_pull():
    return subprocess.run(
        [_git_binary(), "pull", "--ff-only"],
        capture_output=True, encoding="utf-8", errors="replace", timeout=60, close_fds=False,
    )


@app.route("/api/sync", methods=["POST"])
def api_sync():
    """git pull the repo so today's committed scan/shortlist/backtest data
    (from the scheduled GitHub Actions runs that send the email) shows up
    here too, without the user having to leave the dashboard to do it."""
    try:
        # Absolute git path (not the bare "git", which posix_spawn eligibility
        # requires — see the comment in _launch_job()) and no cwd= (process cwd
        # is already PROJECT_ROOT, set once at startup).
        result = _git_pull()

        # A local job run (Full Scan / Positions / etc., all launched from
        # this same dashboard) writes into the same data/ paths the automated
        # workflow commits to — if you've run anything locally since the last
        # sync, those two can diverge and block a fast-forward pull. Since
        # data/ is always regenerable output (never something hand-authored),
        # the automated commit is the one that actually matters here: discard
        # the local modifications and retry once rather than surfacing a git
        # merge error for what's really just stale scan output.
        if result.returncode != 0 and "overwritten by merge" in (result.stdout + result.stderr):
            subprocess.run(
                [_git_binary(), "checkout", "--", "data/"],
                capture_output=True, encoding="utf-8", errors="replace", timeout=30, close_fds=False,
            )
            result = _git_pull()

        return jsonify({
            "success": result.returncode == 0,
            "output": (result.stdout + result.stderr).strip(),
        })
    except Exception as e:
        return jsonify({"success": False, "output": str(e)})


@app.route("/api/positions/upload", methods=["POST"])
def api_positions_upload():
    """Save a Fidelity Positions CSV export uploaded from the browser. Never
    leaves this machine — no credentials, no login, just the file you already
    downloaded yourself. Overwrites the previous upload (single "current
    portfolio" file, not a history)."""
    f = request.files.get("csv")
    if not f or not f.filename:
        return jsonify({"success": False, "error": "no file uploaded"}), 400
    POSITIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
    f.save(str(POSITIONS_CSV))
    return jsonify({"success": True})


@app.route("/api/positions")
def api_positions():
    """Last computed position analysis, if any. Empty/`reason` shape (not an
    error) when nothing's been uploaded or analyzed yet, matching the other
    read-only routes."""
    has_csv = POSITIONS_CSV.exists()
    data = _read_json(ADHOC_DIR / "positions_latest.json", None)
    if data is None:
        return jsonify({
            "has_csv": has_csv,
            "position_analyses": [], "summary": {"total_positions": 0}, "urgent_actions": [],
        })
    data["has_csv"] = has_csv
    return jsonify(data)


@app.route("/api/news/<group>")
def api_news(group):
    """Last fetched news batch for a group ("positions" or "buy"). Empty shape
    (not an error) when nothing's been fetched yet."""
    return jsonify(_read_json(ADHOC_DIR / f"news_{group}.json", {"generated": None, "tickers": [], "news": {}}))


@app.route("/api/price-history/<group>")
def api_price_history(group):
    """Last fetched price-history batch for a group (e.g. "shortlist"). Empty
    shape (not an error) when nothing's been fetched yet."""
    return jsonify(_read_json(ADHOC_DIR / f"price_history_{group}.json", {"generated": None, "tickers": [], "prices": {}}))


@app.route("/api/momentum-status/<group>")
def api_momentum_status(group):
    """Last computed hot/stable/basing/avoid classification (+ day-streak) for
    a group. Empty shape (not an error) when nothing's been fetched yet."""
    return jsonify(_read_json(ADHOC_DIR / f"momentum_status_{group}.json", {"generated": None, "tickers": [], "status": {}}))


# ---------------------------------------------------------------------------
# Read-only data routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/scans")
def api_scans():
    return jsonify(get_scan_files())


@app.route("/api/scan")
def api_scan():
    path = request.args.get("path", "")
    if not path:
        latest = SCAN_DIR / "latest_optimized_scan.txt"
        if latest.exists():
            path = str(latest)
        else:
            return jsonify({"error": "No scan data"})

    if not Path(path).exists():
        return jsonify({"error": "File not found"})

    return jsonify(parse_scan_file(path))


@app.route("/api/top20")
def api_top20():
    return jsonify(_read_json(SCAN_DIR / "top20_latest.json", {"generated": None, "result": None, "top20": []}))


@app.route("/api/shortlist")
def api_shortlist():
    return jsonify(_read_json(SCAN_DIR / "shortlist_latest.json", {
        "generated": None, "result": None, "shortlist": [],
        "fundamentals_audits": {}, "catalyst_sentiments": {}, "congress_signals": {},
    }))


@app.route("/api/backtest/latest")
def api_backtest_latest():
    data = _read_json(BACKTEST_DIR / "latest.json", None)
    if data is None:
        return jsonify({"generated": None, "params": {}, "summary": {}, "component_correlations": {}, "trade_count": 0})
    return jsonify({
        "generated": data.get("generated"),
        "params": data.get("params", {}),
        "summary": data.get("summary", {}),
        "component_correlations": data.get("component_correlations", {}),
        "trade_count": len(data.get("trades", [])),
    })


def api_backtest_history():
    return jsonify(get_backtest_files())


@app.route("/api/backtest/run")
def api_backtest_run():
    path = request.args.get("path", "")
    if not path or not Path(path).exists():
        return jsonify({"error": "File not found"}), 404
    return jsonify(_read_json(path, {}))


def open_browser(port):
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Screener Dashboard")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--scan", action="store_true", help="Run a test scan before launching")
    parser.add_argument("--full", action="store_true", help="With --scan, run full scan instead of test")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    if args.scan:
        print("Running scan before dashboard launch...")
        cmd = [_venv_python(), str(PROJECT_ROOT / "run_optimized_scan.py")]
        if not args.full:
            cmd.append("--test-mode")
        subprocess.run(cmd)

    if not args.no_browser:
        Timer(1.5, open_browser, [args.port]).start()

    print(f"\n  Dashboard running at http://localhost:{args.port}\n")
    # 127.0.0.1, not 0.0.0.0: this app has zero authentication — every route
    # (including git pull, running scans/backtests, and reading arbitrary
    # local JSON files via the backtest ?path= params) is reachable by anyone
    # who can open the URL. 0.0.0.0 would expose all of that to the whole
    # LAN/WiFi, not just this machine. Matches mac_app/main.py, which already
    # binds 127.0.0.1 for the packaged .app that most people actually run.
    # threaded=True — see the matching comment in mac_app/main.py.
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True)
// Stock Screener dashboard — vanilla JS single-page app. Hash-based routing
// (no router library), fetch() for data, Chart.js (via charts.js) for charts.

import { fetchJSON } from './core/api.js';
import { route, initRouter } from './core/router.js';
import { currentView } from './core/state.js';
import { showToast, toggleReasons } from './core/ui-helpers.js';
import { renderBacktestsView } from './views/backtests.js';
import { renderMarketView } from './views/market.js';
import { renderPositionsView } from './views/positions.js';
import { renderRunView } from './views/run.js';
import { renderScanView } from './views/scan.js';
import { renderShortlistView } from './views/shortlist.js';

const VIEWS = {
  positions: { title: 'Positions', render: renderPositionsView },
  shortlist: { title: 'Shortlist', render: renderShortlistView },
  market: { title: 'Market', render: renderMarketView },
  backtests: { title: 'Backtests', render: renderBacktestsView },
  run: { title: 'Run Simulation', render: renderRunView },
  scan: { title: 'Full Scan', render: renderScanView },
};

// Inline handlers need an explicit global now that dashboard.js is a module.
window.toggleReasons = toggleReasons;

// "Sync latest" reports a GIT fact (did `git pull` fetch new commits) which
// is a different question from "is the data actually recent" — the daily
// scan is a separate scheduled job that can go a while without producing a
// new commit (weekends, a workflow failure, zero qualifying candidates) even
// though `git pull` correctly and truthfully says "already up to date" every
// time. This surfaces the shortlist's own `generated` timestamp next to the
// button so that gap is visible instead of silently confusing.
const dataFreshnessEl = document.getElementById('dataFreshness');
function _relativeAge(isoString) {
  const then = new Date(isoString);
  const hours = (Date.now() - then.getTime()) / 36e5;
  if (hours < 1) return 'less than an hour ago';
  if (hours < 24) return `${Math.round(hours)}h ago`;
  const days = Math.round(hours / 24);
  return `${days} day${days === 1 ? '' : 's'} ago`;
}
async function refreshDataFreshness() {
  try {
    const data = await fetchJSON('/api/shortlist');
    dataFreshnessEl.textContent = data.generated
      ? `Latest scan: ${_relativeAge(data.generated)}`
      : 'Latest scan: never run';
  } catch {
    // Freshness is a nice-to-have status readout — a failed fetch here
    // shouldn't interrupt anything else on the page.
  }
}

// silent=true (used by auto-sync): stays quiet unless it actually pulls new
// data, so a background sync every few minutes doesn't spam toasts for
// "already up to date" or for a transient failure — the manual button still
// surfaces both of those explicitly when you click it yourself.
async function doSync(silent) {
  let res;
  try {
    res = await fetchJSON('/api/sync', { method: 'POST' });
    if (res.success) {
      if (!res.output.includes('Already up to date')) {
        const formInUse = silent && (currentView === 'run' || currentView === 'scan');
        showToast(formInUse ? 'Pulled latest data — will show on your next visit to this page.' : 'Pulled latest data — refreshing…');
        if (!formInUse) route();
      } else if (!silent) {
        showToast('Already up to date.');
      }
    } else if (!silent) {
      showToast('Sync failed: ' + (res.output || 'unknown error').slice(0, 200));
    }
  } catch (e) {
    if (!silent) showToast('Sync error: ' + e.message);
    res = { success: false };
  }
  // Outside the try/catch above on purpose: this reflects the daily scan's
  // own data age, a separate concern from whether this particular git pull
  // succeeded — refreshDataFreshness() has its own internal error handling,
  // so it must never surface as a (misleading) "Sync error" toast.
  refreshDataFreshness();
  return res;
}

document.getElementById('syncBtn').addEventListener('click', async () => {
  const btn = document.getElementById('syncBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Syncing…';
  await doSync(false);
  btn.disabled = false;
  btn.innerHTML = 'Sync latest';
});

// Auto-sync: pulls in the background every few minutes so today's emailed
// picks show up here without you having to click Sync — runs app-wide (not
// tied to the current view, unlike the per-view "Live" refresh) since new
// data can land at any time regardless of what page you're on.
const AUTO_SYNC_INTERVAL_MS = 5 * 60 * 1000;
setInterval(() => doSync(true), AUTO_SYNC_INTERVAL_MS);
doSync(true); // also try once right away, in case new data landed since last time the app was open

initRouter(VIEWS);
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stock Screener</title>
<script src="{{ url_for('static', filename='js/vendor/chart.umd.min.js') }}"></script>
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
</head>
<body>

<div class="app">
  <nav class="sidebar" aria-label="Primary">
    <div class="brand">Stock Screener</div>

    <div class="nav-group" role="group" aria-label="Monitor">
      <div class="nav-group-label">Monitor</div>
      <a href="#/positions" class="nav-item" data-view="positions">
        <span class="nav-item-title">Positions</span>
        <span class="nav-item-sub">Your portfolio</span>
      </a>
      <a href="#/shortlist" class="nav-item" data-view="shortlist">
        <span class="nav-item-title">Shortlist</span>
        <span class="nav-item-sub">Today's email picks</span>
      </a>
      <a href="#/market" class="nav-item" data-view="market">
        <span class="nav-item-title">Market</span>
        <span class="nav-item-sub">Full scan, all signals</span>
      </a>
    </div>

    <div class="nav-group" role="group" aria-label="Analyze">
      <div class="nav-group-label">Analyze</div>
      <a href="#/backtests" class="nav-item" data-view="backtests">
        <span class="nav-item-title">Backtests</span>
        <span class="nav-item-sub">Past performance, not email</span>
      </a>
    </div>

    <div class="nav-group" role="group" aria-label="Run">
      <div class="nav-group-label">Run</div>
      <a href="#/run" class="nav-item" data-view="run">
        <span class="nav-item-title">Run Simulation</span>
        <span class="nav-item-sub">Test a strategy</span>
      </a>
      <a href="#/scan" class="nav-item" data-view="scan">
        <span class="nav-item-title">Full Scan</span>
        <span class="nav-item-sub">Trigger a new scan</span>
      </a>
    </div>

    <div class="sidebar-footer">Not financial advice.</div>
  </nav>

  <main class="main">
    <header class="topbar">
      <h1 id="pageTitle">Positions</h1>
      <div id="pageMeta" class="page-meta"></div>
      <div id="dataFreshness" class="page-meta" style="margin-left:auto" title="When the daily scan behind Shortlist/Top 20 last actually ran — separate from whether 'Sync latest' has anything new to pull"></div>
      <button class="btn" id="syncBtn" title="git pull to fetch today's emailed picks">Sync latest</button>
    </header>
    <div class="content" id="content"></div>
  </main>
</div>

<div class="toast" id="toast" style="opacity:0" role="status" aria-live="polite"></div>

<script src="{{ url_for('static', filename='js/charts.js') }}"></script>
<script type="module" src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
</body>
</html>
"""Characterization tests for dashboard.py's job registry and read-only
"empty shape, not error" routes — written before the UI modernization sprint
(TASK-003) extracts/touches the frontend code that depends on this backend
contract. These lock in behavior found and fixed earlier this session:
unbounded JOBS growth, and routes that must return 200 with an empty shape
rather than an error when no data exists yet.

No network calls — these test the job registry and route contracts
directly, not real scans/fetches.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import dashboard


def _client():
    dashboard.app.config["TESTING"] = True
    return dashboard.app.test_client()


def test_unknown_job_returns_404():
    client = _client()
    resp = client.get("/api/jobs/does-not-exist")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "unknown job"


def test_prune_old_jobs_keeps_running_and_recent_jobs():
    with dashboard.JOBS_LOCK:
        dashboard.JOBS.clear()
        now = time.time()
        dashboard.JOBS["old-finished"] = {
            "kind": "news", "status": "success", "output": [],
            "returncode": 0, "started": now - dashboard.JOB_RETENTION_SECONDS - 60,
            "proc": None, "result_path": None,
        }
        dashboard.JOBS["recent-finished"] = {
            "kind": "news", "status": "success", "output": [],
            "returncode": 0, "started": now - 5,
            "proc": None, "result_path": None,
        }
        dashboard.JOBS["still-running"] = {
            "kind": "scan", "status": "running", "output": [],
            "returncode": None, "started": now - dashboard.JOB_RETENTION_SECONDS - 60,
            "proc": None, "result_path": None,
        }

    dashboard._prune_old_jobs()

    with dashboard.JOBS_LOCK:
        assert "old-finished" not in dashboard.JOBS, "a long-finished job must be pruned"
        assert "recent-finished" in dashboard.JOBS, "a recently-finished job must survive the retention window"
        assert "still-running" in dashboard.JOBS, "a running job must never be pruned, regardless of age"
        dashboard.JOBS.clear()


def test_momentum_status_empty_shape_not_error():
    client = _client()
    resp = client.get("/api/momentum-status/__nonexistent_group__")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == {}
    assert body["generated"] is None


def test_news_empty_shape_not_error():
    client = _client()
    resp = client.get("/api/news/__nonexistent_group__")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["news"] == {}


def test_price_history_empty_shape_not_error():
    client = _client()
    resp = client.get("/api/price-history/__nonexistent_group__")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["prices"] == {}


def test_read_json_parses_literal_nan_without_raising(tmp_path):
    # Python's json.loads accepts a literal NaN token (a non-standard
    # extension) rather than raising JSONDecodeError, so _read_json parses it
    # through as float('nan') instead of falling back to `default`. This
    # characterizes actual behavior — sanitize_nan() elsewhere is what turns
    # NaN into null before writing, not _read_json on the way back in.
    bad_file = tmp_path / "bad.json"
    bad_file.write_text('{"value": NaN}', encoding="utf-8")
    result = dashboard._read_json(bad_file, {"fallback": True})
    assert result != {"fallback": True}, "a literal NaN token must not trigger the default fallback"
    assert result["value"] != result["value"], "the parsed value should be float('nan') (nan != nan)"


def test_read_json_falls_back_on_malformed_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text('{"value": ', encoding="utf-8")
    result = dashboard._read_json(bad_file, {"fallback": True})
    assert result == {"fallback": True}


def test_read_json_falls_back_on_missing_file(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    result = dashboard._read_json(missing, {"fallback": True})
    assert result == {"fallback": True}


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.screening.top20_ranker import build_top20
import dashboard


def test_build_top20_preserves_current_price():
    buy_signal = {
        'ticker': 'TEST',
        'score': 80,
        'current_price': 123.45,
    }

    with patch('src.screening.top20_ranker._fetch_news_links', return_value=[]):
        top20 = build_top20([buy_signal], reddit_mentions={}, insider_signals={})

    assert top20[0]['current_price'] == 123.45


def test_parse_scan_file_extracts_current_price(tmp_path):
    # Market's Buy/Sell tables read from the human-readable .txt report (via
    # parse_scan_file), a completely separate serialization path from
    # top20_latest.json/shortlist_latest.json's direct JSON dump — a value
    # present on the in-memory signal dict does not automatically appear here
    # unless save_report() (run_optimized_scan.py) also writes it into the
    # text format and this parser extracts it back out. This locks in that
    # round-trip for both buy and sell signals.
    report = (
        "################################################################################\n"
        "BUY #1: AAPL | Score: 95.0/125\n"
        "################################################################################\n"
        "Current Price: $182.50\n"
        "Phase: 2\n"
        "Entry Quality: Good\n"
        "Stop Loss: $175.00\n"
        "\n"
        "################################################################################\n"
        "SELL #1: XYZ | Score: 85.0/110\n"
        "################################################################################\n"
        "Current Price: $42.10\n"
        "Phase: 4 | Severity: CRITICAL\n"
        "Breakdown: $40.00\n"
    )
    report_file = tmp_path / "scan.txt"
    report_file.write_text(report, encoding="utf-8")

    data = dashboard.parse_scan_file(str(report_file))

    assert data['buy_signals'][0]['current_price'] == 182.50
    assert data['sell_signals'][0]['current_price'] == 42.10
tests/js/test_auto_sync_form_guard.js
tests/js/test_live_guard.js
tests/js/test_market_scatter_points.js
tests/js/test_market_signal_extras.js
tests/js/test_market_signal_tabs.js
tests/js/test_news_component.js
tests/js/test_shortlist_empty_state.js
tests/js/test_start_job.js

exec
/bin/zsh -lc "git log --format='%h %ci %s' -- data/daily_scans/shortlist_latest.json; git log --format='%h %ci %s' -- data/daily_scans/top20_latest.json; find data/daily_scans -maxdepth 1 -name 'optimized_scan_*.txt' -print | sort; for f in "'$(find data/daily_scans -maxdepth 1 -name '"'optimized_scan_*.txt' -print | sort); do printf '%s|' \""'$f"; rg -m1 '"'Scan Date:|Generated:|Total Universe:|Analyzed:|Buy Signals:' \""'$f" | tr '"'\\n' '|'; printf '\\n'; done" in /Users/badripratti/Desktop/stock-screener
 succeeded in 117ms:
229bed5d 2026-09-18 19:26:56 +0000 chore: midday quick scan cache update (3 stocks) - 2026-09-18 19:26
919bf881 2026-09-18 17:07:48 +0000 chore: update fundamental cache (12 stocks) - 2026-09-18
cf458768 2026-09-17 20:00:24 +0000 chore: midday quick scan cache update (3 stocks) - 2026-09-17 20:00
9d9fe4ee 2026-09-17 17:35:07 +0000 chore: update fundamental cache (10 stocks) - 2026-09-17
1299573c 2026-09-16 19:51:53 +0000 chore: midday quick scan cache update (3 stocks) - 2026-09-16 19:51
3b798ef7 2026-09-16 17:26:12 +0000 chore: update fundamental cache (12 stocks) - 2026-09-16
a2502beb 2026-09-15 19:59:56 +0000 chore: midday quick scan cache update (3 stocks) - 2026-09-15 19:59
40b6d251 2026-09-15 17:31:21 +0000 chore: update fundamental cache (10 stocks) - 2026-09-15
25b3fc3f 2026-09-14 23:10:22 +0000 chore: update fundamental cache (13 stocks) - 2026-09-14
4c93346b 2026-09-14 20:47:09 +0000 chore: midday quick scan cache update (3 stocks) - 2026-09-14 20:47
c741acb0 2026-09-13 22:47:57 -0400 Local scan data snapshots + sprint planning artifacts from this session
data/daily_scans/optimized_scan_20260729_221947.txt
data/daily_scans/optimized_scan_20260729_222415.txt
data/daily_scans/optimized_scan_20260729_223432.txt
data/daily_scans/optimized_scan_20260729_223608.txt
data/daily_scans/optimized_scan_20260730_085210.txt
data/daily_scans/optimized_scan_20260730_225116.txt
data/daily_scans/optimized_scan_20260909_172815.txt
data/daily_scans/optimized_scan_20260914_204707.txt
data/daily_scans/optimized_scan_20260914_231020.txt
data/daily_scans/optimized_scan_20260915_173119.txt
data/daily_scans/optimized_scan_20260915_195953.txt
data/daily_scans/optimized_scan_20260916_172610.txt
data/daily_scans/optimized_scan_20260916_195151.txt
data/daily_scans/optimized_scan_20260917_173505.txt
data/daily_scans/optimized_scan_20260917_200021.txt
data/daily_scans/optimized_scan_20260918_170746.txt
data/daily_scans/optimized_scan_20260918_192654.txt
data/daily_scans/optimized_scan_20260729_221947.txt|Scan Date: 2026-07-29|
data/daily_scans/optimized_scan_20260729_222415.txt|Scan Date: 2026-07-29|
data/daily_scans/optimized_scan_20260729_223432.txt|Scan Date: 2026-07-29|
data/daily_scans/optimized_scan_20260729_223608.txt|Scan Date: 2026-07-29|
data/daily_scans/optimized_scan_20260730_085210.txt|Scan Date: 2026-07-30|
data/daily_scans/optimized_scan_20260730_225116.txt|Scan Date: 2026-07-30|
data/daily_scans/optimized_scan_20260909_172815.txt|Scan Date: 2026-09-09|
data/daily_scans/optimized_scan_20260914_204707.txt|Scan Date: 2026-09-14|
data/daily_scans/optimized_scan_20260914_231020.txt|Scan Date: 2026-09-14|
data/daily_scans/optimized_scan_20260915_173119.txt|Scan Date: 2026-09-15|
data/daily_scans/optimized_scan_20260915_195953.txt|Scan Date: 2026-09-15|
data/daily_scans/optimized_scan_20260916_172610.txt|Scan Date: 2026-09-16|
data/daily_scans/optimized_scan_20260916_195151.txt|Scan Date: 2026-09-16|
data/daily_scans/optimized_scan_20260917_173505.txt|Scan Date: 2026-09-17|
data/daily_scans/optimized_scan_20260917_200021.txt|Scan Date: 2026-09-17|
data/daily_scans/optimized_scan_20260918_170746.txt|Scan Date: 2026-09-18|
data/daily_scans/optimized_scan_20260918_192654.txt|Scan Date: 2026-09-18|

exec
/bin/zsh -lc "for f in data/daily_scans/optimized_scan_*.txt; do printf '%s\\t' \""'$(basename "$f")"; sed -n '"'/"'^Generated:/p;/''^Total Universe:/p;/''^Analyzed:/p;/Buy Signals:/p'"' \""'$f" | head -4 | paste -sd '"'|' -; done | sort; printf '\\nSHORTLIST HISTORY\\n'; for h in "'$(git log --format='"'%h' -- data/daily_scans/shortlist_latest.json); do printf '%s\\t' \""'$h"; git show "$h:data/daily_scans/shortlist_latest.json" | jq -r '"'[.generated,.result,([.shortlist[]?.ticker]|join(\",\"))]|@tsv'; done; printf '\\nTOP20 HISTORY\\n'; for h in "'$(git log --format='"'%h' -- data/daily_scans/top20_latest.json); do printf '%s\\t' \""'$h"; git show "$h:data/daily_scans/top20_latest.json" | jq -r '"'[.generated,.result,([.top20[]?.ticker]|join(\",\"))]|@tsv'; done" in /Users/badripratti/Desktop/stock-screener
 succeeded in 394ms:
optimized_scan_20260729_221947.txt	Generated: 2026-07-29 22:19:47|Total Universe: 100 stocks|Analyzed: 45 stocks|🟢 Buy Signals: 13
optimized_scan_20260729_222415.txt	Generated: 2026-07-29 22:24:15|Total Universe: 100 stocks|Analyzed: 45 stocks|🟢 Buy Signals: 13
optimized_scan_20260729_223432.txt	Generated: 2026-07-29 22:34:32|Total Universe: 100 stocks|Analyzed: 50 stocks|🟢 Buy Signals: 14
optimized_scan_20260729_223608.txt	Generated: 2026-07-29 22:36:08|Total Universe: 100 stocks|Analyzed: 50 stocks|🟢 Buy Signals: 14
optimized_scan_20260730_085210.txt	Generated: 2026-07-30 08:52:10|Total Universe: 3,772 stocks|Analyzed: 1,979 stocks|🟢 Buy Signals: 630
optimized_scan_20260730_225116.txt	Generated: 2026-07-30 22:51:16|Total Universe: 100 stocks|Analyzed: 51 stocks|🟢 Buy Signals: 16
optimized_scan_20260909_172815.txt	Generated: 2026-09-09 17:28:15|Total Universe: 100 stocks|Analyzed: 59 stocks|🟢 Buy Signals: 15
optimized_scan_20260914_204707.txt	Generated: 2026-09-14 20:47:07|Total Universe: 100 stocks|Analyzed: 54 stocks|🟢 Buy Signals: 14
optimized_scan_20260914_231020.txt	Generated: 2026-09-14 23:10:20|Total Universe: 3,766 stocks|Analyzed: 1,982 stocks|🟢 Buy Signals: 479
optimized_scan_20260915_173119.txt	Generated: 2026-09-15 17:31:19|Total Universe: 3,766 stocks|Analyzed: 1,971 stocks|🟢 Buy Signals: 436
optimized_scan_20260915_195953.txt	Generated: 2026-09-15 19:59:53|Total Universe: 100 stocks|Analyzed: 49 stocks|🟢 Buy Signals: 11
optimized_scan_20260916_172610.txt	Generated: 2026-09-16 17:26:10|Total Universe: 3,767 stocks|Analyzed: 1,971 stocks|🟢 Buy Signals: 461
optimized_scan_20260916_195151.txt	Generated: 2026-09-16 19:51:51|Total Universe: 100 stocks|Analyzed: 51 stocks|🟢 Buy Signals: 8
optimized_scan_20260917_173505.txt	Generated: 2026-09-17 17:35:05|Total Universe: 3,768 stocks|Analyzed: 1,973 stocks|🟢 Buy Signals: 429
optimized_scan_20260917_200021.txt	Generated: 2026-09-17 20:00:21|Total Universe: 100 stocks|Analyzed: 48 stocks|🟢 Buy Signals: 10
optimized_scan_20260918_170746.txt	Generated: 2026-09-18 17:07:46|Total Universe: 3,770 stocks|Analyzed: 1,973 stocks|🟢 Buy Signals: 364
optimized_scan_20260918_192654.txt	Generated: 2026-09-18 19:26:54|Total Universe: 100 stocks|Analyzed: 55 stocks|🟢 Buy Signals: 11

SHORTLIST HISTORY
919bf881	2026-09-18T17:07:46.930276	success	LILAK,LTC,LILA,NVDA,OXY
9d9fe4ee	2026-09-17T17:35:05.525757	success	LILA,LILAK,LTC,BP,DVN
3b798ef7	2026-09-16T17:26:10.610096	success	LILA,NVDA,LTC,DVN,ET
40b6d251	2026-09-15T17:31:19.360454	success	NGL,LILAK,LILA,OXY,CRWD
25b3fc3f	2026-09-14T23:10:20.556302	success	NGL,ASND,LILA,LILAK,CRWD
c741acb0	2026-09-09T17:28:15.811583		OXY,KRO,GKOS,CAKE,MUFG

TOP20 HISTORY
229bed5d	2026-09-18T19:26:54.789687	success	BP,CVBF,CGON,BFH,ZBRA,WEAV,E,PLUS,EHC,QRVO,CBZ
919bf881	2026-09-18T17:07:46.332217	success	LILAK,LTC,LILA,CVX,OXY,ET,SHIP,BP,NVDA,CNQ,SUN,VLO,ASC,DELL,PSX,COP,ZETA,CVE,HALO,EOG
cf458768	2026-09-17T20:00:21.975072	success	SUN,SHIP,EXPD,ETON,ARLP,OVV,INVX,JNJ,SLP,CVLT
9d9fe4ee	2026-09-17T17:35:04.930210	success	LILA,LILAK,LTC,BP,DVN,NGL,OXY,CVX,CRWD,NVDA,SM,NUE,SUN,PSX,SLDE,TALO,RS,SATA,CVE,MPC
1299573c	2026-09-16T19:51:51.379441	success	USPH,HCC,IOSP,BZH,KELYA,EWTX,NTNX,IFF
3b798ef7	2026-09-16T17:26:10.061789	success	LILA,LTC,DVN,ET,KRNY,NVDA,TALO,BP,COP,CVX,PSX,SUN,CRWD,PAA,MFG,CF,NUE,XOM,SHIP,CNQ
a2502beb	2026-09-15T19:59:53.834570	success	LILAK,CCNE,CNO,TXO,AAPL,HRTG,BIO,AVPT,ICFI,RGEN,INTA
40b6d251	2026-09-15T17:31:18.449890	success	NGL,LILAK,LILA,OXY,LTC,DVN,KRNY,CRWD,ET,CVX,COP,BP,PSX,ASC,HOG,PAA,MFG,AVT,NSIT,SHIP
25b3fc3f	2026-09-14T23:10:19.347430	success	NGL,ASND,LILA,LILAK,OXY,LTC,CRWD,KRNY,CVBF,COP,ET,DK,CVX,PSX,FTNT,MFG,VLO,SM,DELL,HOG
4c93346b	2026-09-14T20:47:07.484176	success	CVX,HRTG,PUBM,KRT,WHD,SAIC,BCAL,CLMT,SATA,BWIN,BCH,LNC,RIO,FDS
c741acb0	2026-09-12T16:23:49.379374		NGL,ASND,LILA,LILAK,LTC,COP,WES,CVX,PSX,SM,JPM,MFG,ACOG,MPC,EGY,BP,ET,SLDE,TALO,NVDA

exec
/bin/zsh -lc "git log --format='%h %ci %an <%ae> %s' -- data/daily_scans/optimized_scan_*.txt; printf '\\nPER REPORT INTRO COMMIT\\n'; for f in data/daily_scans/optimized_scan_*.txt; do printf '%s\\t' \""'$(basename "$f")"; git log --diff-filter=A -1 --format='"'%h|%ci|%an|%s' -- \""'$f"; done | sort; printf '"'\\nRELEVANT GRAPH\\n'; git log --graph --decorate --oneline --all -35 -- .github/workflows/daily_screening_git_storage.yml .github/workflows/midday_quick_scan.yml data/daily_scans" in /Users/badripratti/Desktop/stock-screener
 succeeded in 337ms:
optimized_scan_20260729_221947.txt	f49f4b1a|2026-08-18 22:22:26 -0400|Badri Prati|Add LLM agents (Fundamentals Auditor, Catalyst Sentiment, Congress Trades) with a real Top 5 filter, and migrate trade links/position management from Robinhood to Fidelity
optimized_scan_20260729_222415.txt	f49f4b1a|2026-08-18 22:22:26 -0400|Badri Prati|Add LLM agents (Fundamentals Auditor, Catalyst Sentiment, Congress Trades) with a real Top 5 filter, and migrate trade links/position management from Robinhood to Fidelity
optimized_scan_20260729_223432.txt	f49f4b1a|2026-08-18 22:22:26 -0400|Badri Prati|Add LLM agents (Fundamentals Auditor, Catalyst Sentiment, Congress Trades) with a real Top 5 filter, and migrate trade links/position management from Robinhood to Fidelity
optimized_scan_20260729_223608.txt	f49f4b1a|2026-08-18 22:22:26 -0400|Badri Prati|Add LLM agents (Fundamentals Auditor, Catalyst Sentiment, Congress Trades) with a real Top 5 filter, and migrate trade links/position management from Robinhood to Fidelity
optimized_scan_20260730_085210.txt	f49f4b1a|2026-08-18 22:22:26 -0400|Badri Prati|Add LLM agents (Fundamentals Auditor, Catalyst Sentiment, Congress Trades) with a real Top 5 filter, and migrate trade links/position management from Robinhood to Fidelity
optimized_scan_20260730_225116.txt	f49f4b1a|2026-08-18 22:22:26 -0400|Badri Prati|Add LLM agents (Fundamentals Auditor, Catalyst Sentiment, Congress Trades) with a real Top 5 filter, and migrate trade links/position management from Robinhood to Fidelity
optimized_scan_20260909_172815.txt	c741acb0|2026-09-13 22:47:57 -0400|Badri Prati|Local scan data snapshots + sprint planning artifacts from this session
optimized_scan_20260914_204707.txt	4c93346b|2026-09-14 20:47:09 +0000|github-actions[bot]|chore: midday quick scan cache update (3 stocks) - 2026-09-14 20:47
optimized_scan_20260914_231020.txt	25b3fc3f|2026-09-14 23:10:22 +0000|github-actions[bot]|chore: update fundamental cache (13 stocks) - 2026-09-14
optimized_scan_20260915_173119.txt	40b6d251|2026-09-15 17:31:21 +0000|github-actions[bot]|chore: update fundamental cache (10 stocks) - 2026-09-15
optimized_scan_20260915_195953.txt	a2502beb|2026-09-15 19:59:56 +0000|github-actions[bot]|chore: midday quick scan cache update (3 stocks) - 2026-09-15 19:59
optimized_scan_20260916_172610.txt	3b798ef7|2026-09-16 17:26:12 +0000|github-actions[bot]|chore: update fundamental cache (12 stocks) - 2026-09-16
optimized_scan_20260916_195151.txt	1299573c|2026-09-16 19:51:53 +0000|github-actions[bot]|chore: midday quick scan cache update (3 stocks) - 2026-09-16 19:51
optimized_scan_20260917_173505.txt	9d9fe4ee|2026-09-17 17:35:07 +0000|github-actions[bot]|chore: update fundamental cache (10 stocks) - 2026-09-17
optimized_scan_20260917_200021.txt	cf458768|2026-09-17 20:00:24 +0000|github-actions[bot]|chore: midday quick scan cache update (3 stocks) - 2026-09-17 20:00
optimized_scan_20260918_170746.txt	919bf881|2026-09-18 17:07:48 +0000|github-actions[bot]|chore: update fundamental cache (12 stocks) - 2026-09-18
optimized_scan_20260918_192654.txt	229bed5d|2026-09-18 19:26:56 +0000|github-actions[bot]|chore: midday quick scan cache update (3 stocks) - 2026-09-18 19:26

RELEVANT GRAPH
* 229bed5d (HEAD -> main, origin/main, origin/HEAD) chore: midday quick scan cache update (3 stocks) - 2026-09-18 19:26
* 919bf881 chore: update fundamental cache (12 stocks) - 2026-09-18
* cf458768 chore: midday quick scan cache update (3 stocks) - 2026-09-17 20:00
* 9d9fe4ee chore: update fundamental cache (10 stocks) - 2026-09-17
* 1299573c chore: midday quick scan cache update (3 stocks) - 2026-09-16 19:51
* 3b798ef7 chore: update fundamental cache (12 stocks) - 2026-09-16
* a2502beb chore: midday quick scan cache update (3 stocks) - 2026-09-15 19:59
* 40b6d251 chore: update fundamental cache (10 stocks) - 2026-09-15
* 25b3fc3f chore: update fundamental cache (13 stocks) - 2026-09-14
* 4c93346b chore: midday quick scan cache update (3 stocks) - 2026-09-14 20:47
* f9b08abf Fix Shortlist never updating: workflow timeout regression + never-verified data pipeline
* c741acb0 Local scan data snapshots + sprint planning artifacts from this session
* 377523cf Fix real bugs from a full-repo audit: data mismatch, races, security, hangs
* a5efce7a Commit daily_scans/ data (Top 20 + shortlist) from the automated workflows
* f49f4b1a Add LLM agents (Fundamentals Auditor, Catalyst Sentiment, Congress Trades) with a real Top 5 filter, and migrate trade links/position management from Robinhood to Fidelity
* 0f7ed692 Add Reddit ticker-mention tracking and combined Top 20 shortlist
* ebd6edd1 Add midday quick scan workflow (~12pm ET weekdays)
* 1c12b4b9 Add fundamental snapshots to sell signals and update scan schedule
* b150ef6b chore: remove duplicate workflows - use Git-based storage only
* d86a4992 Clean up github actions failure
* fb52477c Add cache and tiered storage to enable rate limit safety

codex
The historical boundary is now clear. The only comparable automated full-universe series is five weekday runs from September 14–18, 2026 (about 3,766–3,770 universe; 1,971–1,982 analyzed). The same dates also contain 100-stock random midday scans, while older checked-in artifacts are manual commits or test-mode outputs and cannot support an honest “last N scan days” baseline.
exec
/bin/zsh -lc 'for h in 25b3fc3f 40b6d251 3b798ef7 9d9fe4ee 919bf881; do git show "$h:data/daily_scans/shortlist_latest.json" | jq -r --arg h "$h" '"'.generated as "'$g | .shortlist[] | [$h,$g,.ticker,.composite_score,.combined_score,.score,.passed_filters]|@tsv'"'; done; printf '\\nTOP20 FIELDS\\n'; git show 919bf881:data/daily_scans/top20_latest.json | jq '.top20[0]'; printf '\\nSHORTLIST FIELDS\\n'; git show 919bf881:data/daily_scans/shortlist_latest.json | jq '.shortlist[0]'; printf '\\nWORKFLOW HISTORY KEY COMMITS\\n'; for h in ebd6edd1 a5efce7a f9b08abf; do echo \""'$h $(git show -s --format='"'%ci %s' "'$h)"; git show "$h:.github/workflows/daily_screening_git_storage.yml" 2>/dev/null | rg -n "cron:|run_optimized_scan|git add data/daily_scans|fetch-depth|pull|rebase" || true; git show "$h:.github/workflows/midday_quick_scan.yml" 2>/dev/null | rg -n "cron:|run_optimized_scan|git add data/daily_scans|fetch-depth|pull|rebase" || true; done' in /Users/badripratti/Desktop/stock-screener
 succeeded in 270ms:
3b798ef7	2026-09-16T17:26:10.610096	LILA	129.5	129.5	100.7	true
3b798ef7	2026-09-16T17:26:10.610096	NVDA	124.51	120.55	100.0	true
3b798ef7	2026-09-16T17:26:10.610096	LTC	123.31	123.31	108.2	true
3b798ef7	2026-09-16T17:26:10.610096	DVN	122.17	122.17	102.8	true
3b798ef7	2026-09-16T17:26:10.610096	ET	121.06	121.06	112.1	true
9d9fe4ee	2026-09-17T17:35:05.525757	LILA	128.4	128.4	99.6	true
9d9fe4ee	2026-09-17T17:35:05.525757	LILAK	128.0	128.0	99.2	true
9d9fe4ee	2026-09-17T17:35:05.525757	LTC	121.31	121.31	106.2	true
9d9fe4ee	2026-09-17T17:35:05.525757	BP	118.93	118.93	109.2	true
9d9fe4ee	2026-09-17T17:35:05.525757	DVN	118.57	118.57	99.2	true
919bf881	2026-09-18T17:07:46.930276	LILAK	123.6	123.6	94.8	true
919bf881	2026-09-18T17:07:46.930276	LTC	122.11	122.11	107.0	true
919bf881	2026-09-18T17:07:46.930276	LILA	121.8	121.8	93.0	true
919bf881	2026-09-18T17:07:46.930276	NVDA	116.72	112.76	93.1	true
919bf881	2026-09-18T17:07:46.930276	OXY	116.14	116.14	96.1	true

TOP20 FIELDS
{
  "ticker": "LILAK",
  "is_buy": "True",
  "score": 94.8,
  "phase": 2,
  "minervini_template_score": 100,
  "minervini_criteria_passed": 8,
  "breakout_price": null,
  "stop_loss": 8.18,
  "risk_reward_ratio": 10.0,
  "entry_quality": "Good",
  "reasons": [
    "Weak Stage 2: 2.8% above 50 SMA",
    "SMAs rising strongly (50:0.517, 200:0.244)",
    "🔴 Revenue: 3Q avg -0.2% QoQ (4.2% → -6.6% → 1.8%)",
    "🟢 EPS: +94% YoY (strong earnings)",
    "Volume pattern neutral (ratio 1.09)",
    "✓ Strong RS: 0.242 (outperforming SPY)",
    "🟢 Outstanding R/R: 10.0:1 ($2.53 upside, $0.25 risk)",
    "🟢 Near 52W high: 5.4% from high"
  ],
  "details": {
    "trend_score": 22.44,
    "fundamental_score": 26.25,
    "avg_vol_up": 1013100.0,
    "avg_vol_down": 926489.0,
    "volume_score": 2.97,
    "rs_slope": 0.242,
    "rs_score": 9.03,
    "stop_loss": 8.177100296020507,
    "risk_reward_ratio": 10.0,
    "risk_amount": 0.25,
    "reward_amount": 2.53,
    "reward_target": 10.96,
    "rr_score": 10.0,
    "entry_score": 24.1,
    "vcp_bonus": 0,
    "minervini_template": {
      "passes_template": true,
      "criteria_passed": 8,
      "criteria_total": 8,
      "template_score": 100,
      "criteria_details": {
        "price_above_150_200": "True",
        "sma_150_above_200": "True",
        "sma_200_rising": "True",
        "sma_50_above_150": "True",
        "price_above_50": "True",
        "price_30pct_above_52w_low": "True",
        "distance_from_52w_low_pct": 82.9,
        "price_near_52w_high": "True",
        "distance_from_52w_high_pct": 5.4,
        "confirmed_stage_2": true
      }
    }
  },
  "fundamental_snapshot": "\n============================================================\nFUNDAMENTAL SNAPSHOT - LILAK\n============================================================\n• Revenue: Modest growth (YoY: +1.5%, QoQ: +1.8%)\n  QoQ Trend (last 4Q): +2.4% → +4.2% → -6.6% → +1.8%\n✓ EPS: STRONG growth (YoY: +93.9%, QoQ: -18.2%)\n  QoQ Trend (last 4Q): +100.9% → N/A → N/A → -18.2%\n• Margins: Stable/slightly up (68.4%, +1.0pp QoQ)\n\nOverall Assessment:\n✓ Fundamentals SUPPORT technical breakout\n",
  "reddit_mentions_24h": 0,
  "insider_buy_value_90d": 14766042.485499999,
  "combined_score": 123.6,
  "why_links": [
    {
      "label": "Insider Buy ($14,766,042/90d)",
      "title": "DE ANGOITIA ALFONSO (Insider) bought 313104 shares @ $20.95",
      "url": "https://www.sec.gov/Archives/edgar/data/1712184/000172451926000010/0001724519-26-000010-index.htm"
    },
    {
      "label": "News",
      "title": "Liberty Latin America Director De Angoitia Buys $10 Million Shares. What Does This Large Purchase Mean for Investors?",
      "url": "https://www.fool.com/coverage/filings/2026/09/08/liberty-latin-america-director-de-angoitia-buys-usd10-million-shares-what-does-this-large-purchase-mean-for-investors/"
    },
    {
      "label": "News",
      "title": "Billionaire Media Titan John Malone Buys 121,000 Liberty Latin America Shares. Should Investors Be Buyers Too?",
      "url": "https://www.fool.com/coverage/filings/2026/09/03/billionaire-media-titan-john-malone-buys-121-000-liberty-latin-america-shares-should-investors-be-buyers-too/"
    }
  ]
}

SHORTLIST FIELDS
{
  "ticker": "LILAK",
  "is_buy": "True",
  "score": 94.8,
  "phase": 2,
  "minervini_template_score": 100,
  "minervini_criteria_passed": 8,
  "breakout_price": null,
  "stop_loss": 8.18,
  "risk_reward_ratio": 10.0,
  "entry_quality": "Good",
  "reasons": [
    "Weak Stage 2: 2.8% above 50 SMA",
    "SMAs rising strongly (50:0.517, 200:0.244)",
    "🔴 Revenue: 3Q avg -0.2% QoQ (4.2% → -6.6% → 1.8%)",
    "🟢 EPS: +94% YoY (strong earnings)",
    "Volume pattern neutral (ratio 1.09)",
    "✓ Strong RS: 0.242 (outperforming SPY)",
    "🟢 Outstanding R/R: 10.0:1 ($2.53 upside, $0.25 risk)",
    "🟢 Near 52W high: 5.4% from high"
  ],
  "details": {
    "trend_score": 22.44,
    "fundamental_score": 26.25,
    "avg_vol_up": 1013100.0,
    "avg_vol_down": 926489.0,
    "volume_score": 2.97,
    "rs_slope": 0.242,
    "rs_score": 9.03,
    "stop_loss": 8.177100296020507,
    "risk_reward_ratio": 10.0,
    "risk_amount": 0.25,
    "reward_amount": 2.53,
    "reward_target": 10.96,
    "rr_score": 10.0,
    "entry_score": 24.1,
    "vcp_bonus": 0,
    "minervini_template": {
      "passes_template": true,
      "criteria_passed": 8,
      "criteria_total": 8,
      "template_score": 100,
      "criteria_details": {
        "price_above_150_200": "True",
        "sma_150_above_200": "True",
        "sma_200_rising": "True",
        "sma_50_above_150": "True",
        "price_above_50": "True",
        "price_30pct_above_52w_low": "True",
        "distance_from_52w_low_pct": 82.9,
        "price_near_52w_high": "True",
        "distance_from_52w_high_pct": 5.4,
        "confirmed_stage_2": true
      }
    }
  },
  "fundamental_snapshot": "\n============================================================\nFUNDAMENTAL SNAPSHOT - LILAK\n============================================================\n• Revenue: Modest growth (YoY: +1.5%, QoQ: +1.8%)\n  QoQ Trend (last 4Q): +2.4% → +4.2% → -6.6% → +1.8%\n✓ EPS: STRONG growth (YoY: +93.9%, QoQ: -18.2%)\n  QoQ Trend (last 4Q): +100.9% → N/A → N/A → -18.2%\n• Margins: Stable/slightly up (68.4%, +1.0pp QoQ)\n\nOverall Assessment:\n✓ Fundamentals SUPPORT technical breakout\n",
  "reddit_mentions_24h": 0,
  "insider_buy_value_90d": 14766042.485499999,
  "combined_score": 123.6,
  "why_links": [
    {
      "label": "Insider Buy ($14,766,042/90d)",
      "title": "DE ANGOITIA ALFONSO (Insider) bought 313104 shares @ $20.95",
      "url": "https://www.sec.gov/Archives/edgar/data/1712184/000172451926000010/0001724519-26-000010-index.htm"
    },
    {
      "label": "News",
      "title": "Liberty Latin America Director De Angoitia Buys $10 Million Shares. What Does This Large Purchase Mean for Investors?",
      "url": "https://www.fool.com/coverage/filings/2026/09/08/liberty-latin-america-director-de-angoitia-buys-usd10-million-shares-what-does-this-large-purchase-mean-for-investors/"
    },
    {
      "label": "News",
      "title": "Billionaire Media Titan John Malone Buys 121,000 Liberty Latin America Shares. Should Investors Be Buyers Too?",
      "url": "https://www.fool.com/coverage/filings/2026/09/03/billionaire-media-titan-john-malone-buys-121-000-liberty-latin-america-shares-should-investors-be-buyers-too/"
    }
  ],
  "drop_reasons": [],
  "passed_filters": true,
  "catalyst_score": 0,
  "congress_score": 0.0,
  "composite_score": 123.6
}

WORKFLOW HISTORY KEY COMMITS
ebd6edd1 2026-07-31 18:03:44 -0400 Add midday quick scan workflow (~12pm ET weekdays)
6:    - cron: '0 12 * * 1-5'
28:          fetch-depth: 1  # Shallow clone for speed
90:          python run_optimized_scan.py --conservative --git-storage
8:    - cron: '0 17 * * 1-5'
23:          fetch-depth: 1
48:          python run_optimized_scan.py --test-mode --git-storage
a5efce7a 2026-09-11 17:15:43 -0400 Commit daily_scans/ data (Top 20 + shortlist) from the automated workflows
6:    - cron: '0 12 * * 1-5'
28:          fetch-depth: 1  # Shallow clone for speed
98:          python run_optimized_scan.py --conservative --git-storage --enable-llm-agents
148:          # the local GUI dashboard (dashboard.py) after a `git pull`, so the same
150:          git add data/daily_scans/ 2>/dev/null || true
8:    - cron: '0 17 * * 1-5'
23:          fetch-depth: 1
48:          python run_optimized_scan.py --test-mode --git-storage
58:          # dashboard (dashboard.py) can show it after a `git pull`.
59:          git add data/daily_scans/ 2>/dev/null || true
f9b08abf 2026-09-14 16:18:03 -0400 Fix Shortlist never updating: workflow timeout regression + never-verified data pipeline
10:    - cron: '0 12 * * 1-5'
41:          fetch-depth: 1  # Shallow clone for speed
111:          python run_optimized_scan.py --conservative --git-storage --enable-llm-agents
161:          # the local GUI dashboard (dashboard.py) after a `git pull`, so the same
163:          git add data/daily_scans/ 2>/dev/null || true
8:    - cron: '0 17 * * 1-5'
24:          fetch-depth: 1
49:          python run_optimized_scan.py --test-mode --git-storage
59:          # dashboard (dashboard.py) can show it after a `git pull`.
60:          git add data/daily_scans/ 2>/dev/null || true

exec
/bin/zsh -lc "cat package.json 2>/dev/null || true; for f in tests/js/test_start_job.js tests/js/test_shortlist_empty_state.js; do sed -n '1,240p' \""'$f"; done; rg -n "pytest|node tests/js|test_dashboard_jobs|test_current_price" README.md Makefile pyproject.toml setup.cfg .github/workflows 2>/dev/null | head -100; git diff -- run_optimized_scan.py dashboard.py static/js/views/shortlist.js static/js/views/market.js | sed -n '"'1,260p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 23ms:
diff --git a/dashboard.py b/dashboard.py
index 02e107c0..36322bc1 100644
--- a/dashboard.py
+++ b/dashboard.py
@@ -181,6 +181,10 @@ def parse_scan_file(filepath):
             "reasons": [],
         }
 
+        m = re.search(r"Current Price:\s*\$([\d.]+)", block)
+        if m:
+            signal["current_price"] = float(m.group(1))
+
         m = re.search(r"Phase:\s*(\d)", block)
         if m:
             signal["phase"] = int(m.group(1))
@@ -236,6 +240,10 @@ def parse_scan_file(filepath):
             "reasons": [],
         }
 
+        m = re.search(r"Current Price:\s*\$([\d.]+)", block)
+        if m:
+            signal["current_price"] = float(m.group(1))
+
         m = re.search(r"Phase:\s*(\d)\s*\|\s*.*Severity:\s*(\w+)", block)
         if m:
             signal["phase"] = int(m.group(1))
diff --git a/run_optimized_scan.py b/run_optimized_scan.py
index 69af0ee5..aa671758 100755
--- a/run_optimized_scan.py
+++ b/run_optimized_scan.py
@@ -133,6 +133,8 @@ def save_report(results, buy_signals, sell_signals, spy_analysis, breadth, outpu
             output.append(f"\n{'#'*80}")
             output.append(f"{score_emoji} BUY #{i}: {signal['ticker']} | Score: {signal['score']}/125")
             output.append(f"{'#'*80}")
+            if signal.get('current_price') is not None:
+                output.append(f"Current Price: ${signal['current_price']:.2f}")
             output.append(f"Phase: {signal['phase']}")
 
             # Entry quality with emoji
@@ -254,6 +256,8 @@ def save_report(results, buy_signals, sell_signals, spy_analysis, breadth, outpu
             output.append(f"\n{'#'*80}")
             output.append(f"{score_emoji} SELL #{i}: {signal['ticker']} | Score: {signal['score']}/110")
             output.append(f"{'#'*80}")
+            if signal.get('current_price') is not None:
+                output.append(f"Current Price: ${signal['current_price']:.2f}")
             output.append(f"Phase: {signal['phase']} | {severity_emoji} Severity: {severity.upper()}")
             if signal.get('breakdown_level'):
                 output.append(f"Breakdown: ${signal['breakdown_level']:.2f}")
@@ -425,6 +429,7 @@ def main():
                         vcp_data=analysis.get('vcp_data')  # Added VCP data
                     )
                     if signal['is_buy']:
+                        signal['current_price'] = analysis['current_price']
                         # Use FMP for enhanced snapshot if requested and available
                         signal['fundamental_snapshot'] = fundamentals_fetcher.create_snapshot(
                             analysis['ticker'],
@@ -449,6 +454,7 @@ def main():
                         fundamentals=analysis.get('quarterly_data')  # Pass raw quarterly data, not analyzed
                     )
                     if signal['is_sell']:
+                        signal['current_price'] = analysis['current_price']
                         # Add fundamental snapshot
                         signal['fundamental_snapshot'] = fundamentals_fetcher.create_snapshot(
                             analysis['ticker'],
diff --git a/static/js/views/market.js b/static/js/views/market.js
index 08ae0e73..2d0f08e0 100644
--- a/static/js/views/market.js
+++ b/static/js/views/market.js
@@ -3,17 +3,23 @@ import { startJob } from '../core/jobs.js';
 import { _liveGuarded, _startLive, liveBadgeHTML } from '../core/refresh.js';
 import { content, currentView, pageMeta } from '../core/state.js';
 import {
+  chartToggleButtonHTML,
   cleanEmoji,
   escapeHtml,
   fidelityLink,
   loadMomentumStatus,
   paintMomentumSlots,
   redditCell,
+  refreshOpenCharts,
   renderTop20Table,
   safeHref,
+  wireChartToggles,
 } from '../core/ui-helpers.js';
 
 let _marketTop20Tickers = [];
+let _marketSignalPrices = {};
+let _marketSignalTickers = [];
+const MARKET_CHART_PREFIX = 'market-sig-chart-';
 
 export async function renderMarketView() {
   const scans = await fetchJSON('/api/scans');
@@ -48,6 +54,7 @@ export async function renderMarketView() {
     _liveGuarded('market-momentum', () => loadMomentumStatus(
       _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
     ));
+    _liveGuarded('market-signal-charts', () => loadMarketSignalCharts(_marketSignalTickers, true));
   });
 }
 
@@ -114,6 +121,170 @@ function _renderNewsGroupHTML(newsByTicker) {
   }).join('')}</div>`;
 }
 
+// Pure by design (exported for tests/js characterization coverage): maps
+// buy_signals to {x, y, signal} scatter points. Only keeps signals with a
+// finite score, a positive max_score, and a finite rs — a missing/null field
+// on any of these would otherwise plot as (0,0) or NaN, silently misleading
+// rather than just being omitted. Y is score-as-percentage-of-max rather
+// than the raw score, since max_score isn't always the same fixed number.
+export function buildBuyOpportunityPoints(buySignals) {
+  return (buySignals || [])
+    .filter(s => Number.isFinite(s.score) && Number.isFinite(s.max_score) && s.max_score > 0 && Number.isFinite(s.rs))
+    .map(s => ({ x: s.rs, y: (s.score / s.max_score) * 100, signal: s }));
+}
+
+function _buyOpportunityChartCardHTML(buySignals) {
+  const plotted = buildBuyOpportunityPoints(buySignals).length;
+  const total = (buySignals || []).length;
+  const omitted = total - plotted;
+  const omittedNote = omitted > 0
+    ? ` (${omitted} signal${omitted === 1 ? '' : 's'} without a plottable score/RS not shown)`
+    : '';
+  return `
+    <div class="card">
+      <h2>Buy Opportunity Map</h2>
+      <div class="card-sub">Right = stronger relative momentum · Up = higher scanner conviction${omittedNote}</div>
+      <div class="scatter-chart-wrap"><canvas id="marketScatterChart"></canvas></div>
+      <div style="color:var(--muted);font-size:11px;margin-top:8px">Hover a dot for details, click to jump to it in the Buy Signals table below.</div>
+    </div>`;
+}
+
+function _renderBuyOpportunityChart(buySignals) {
+  const points = buildBuyOpportunityPoints(buySignals);
+  renderMarketScatterChart('marketScatterChart', points, _showBuySignal);
+}
+
+export function _showBuySignal(signal) {
+  _activateSignalTab('buy');
+  _highlightBuyRow(signal);
+}
+
+// Scrolls to and briefly pulses a ticker's row in the Buy Signals table —
+// used as the scatter chart's click handler. Does not open the Fidelity
+// trade link directly: a dense chart is easy to mis-click, and jumping to
+// the row (rather than an outbound broker link) lets the user confirm the
+// full breakdown before intentionally clicking Trade themselves.
+function _highlightBuyRow(signal) {
+  const row = document.querySelector(`#buySignalsBody tr[data-ticker="${signal.ticker}"]`);
+  if (!row) return;
+  row.scrollIntoView({ behavior: 'smooth', block: 'center' });
+  row.classList.add('row-highlight-pulse');
+  setTimeout(() => row.classList.remove('row-highlight-pulse'), 2000);
+}
+
+function _marketSignalSeries(ticker) {
+  const h = _marketSignalPrices[ticker];
+  return h && h.length ? { history: h, entry: null, stop: null } : null;
+}
+
+// Fetches price history for every ticker shown in the Buy/Sell tables (both,
+// regardless of which tab is active — the chart-toggle button on a sell row
+// works even if the sell panel hasn't been the visible tab yet since the
+// tickers/prices are fetched once up front, not per-tab). Reuses the same
+// batched price-history job Shortlist/Positions use — one job, not one
+// request per ticker.
+async function loadMarketSignalCharts(tickers, silent) {
+  if (!tickers.length) return;
+  await startJob('price-history', { tickers, group: 'market-signals' }, async (st) => {
+    if (st.status !== 'success') return;
+    const data = await fetchJSON('/api/price-history/market-signals');
+    _marketSignalPrices = data.prices || {};
+    if (silent) {
+      refreshOpenCharts(_marketSignalSeries, MARKET_CHART_PREFIX);
+    } else {
+      const card = document.getElementById('marketSignalsCard');
+      if (card) wireChartToggles(card, _marketSignalSeries, MARKET_CHART_PREFIX);
+    }
+  });
+}
+
+function _signalTabLabel(label, shownCount, totalCount) {
+  return totalCount !== shownCount
+    ? `${label} (${shownCount} of ${totalCount})`
+    : `${label} (${shownCount})`;
+}
+
+export function _signalTabsHTML(scan) {
+  const buyTotal = scan.stats.buy_count ?? scan.buy_signals.length;
+  const sellTotal = scan.stats.sell_count ?? scan.sell_signals.length;
+  return `
+    <div class="card" id="marketSignalsCard">
+      <div class="signal-tabs-header">
+        <div>
+          <h2 style="margin-bottom:2px">Market Signals</h2>
+          <div class="card-sub" style="margin:0">Calculated ${escapeHtml(scan.generated || scan.scan_date || 'unknown')}</div>
+        </div>
+        <div class="signal-tabs" role="tablist" aria-label="Market signal type">
+          <button class="btn signal-tab active" id="buySignalsTab" type="button" role="tab" data-signal-tab="buy" aria-selected="true" aria-controls="buySignalsPanel" tabindex="0">${_signalTabLabel('Buy', scan.buy_signals.length, buyTotal)}</button>
+          <button class="btn signal-tab" id="sellSignalsTab" type="button" role="tab" data-signal-tab="sell" aria-selected="false" aria-controls="sellSignalsPanel" tabindex="-1">${_signalTabLabel('Sell', scan.sell_signals.length, sellTotal)}</button>
+        </div>
+      </div>
+      <div id="buySignalsPanel" role="tabpanel" aria-labelledby="buySignalsTab">
+        <div style="overflow-x:auto"><table class="signal-table">
+          <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Price</th><th scope="col">Chart</th><th scope="col">Score</th><th scope="col">Entry</th><th scope="col">Stop Loss</th><th scope="col">R:R</th><th scope="col">RS</th><th scope="col">Reddit</th><th scope="col">Key Reasons</th><th scope="col">Trade</th></tr></thead>
+          <tbody id="buySignalsBody">${renderBuyRows(scan.buy_signals)}</tbody>
+        </table></div>
+      </div>
+      <div id="sellSignalsPanel" role="tabpanel" aria-labelledby="sellSignalsTab" hidden>
+        <div style="overflow-x:auto"><table class="signal-table">
+          <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Price</th><th scope="col">Chart</th><th scope="col">Score</th><th scope="col">Severity</th><th scope="col">Breakdown</th><th scope="col">Reddit</th><th scope="col">Reasons</th><th scope="col">Trade</th></tr></thead>
+          <tbody id="sellSignalsBody"></tbody>
+        </table></div>
+      </div>
+    </div>`;
+}
+
+export function _activateSignalTab(name, sellSignals = []) {
+  const buyTab = document.getElementById('buySignalsTab');
+  const sellTab = document.getElementById('sellSignalsTab');
+  const buyPanel = document.getElementById('buySignalsPanel');
+  const sellPanel = document.getElementById('sellSignalsPanel');
+  if (!buyTab || !sellTab || !buyPanel || !sellPanel) return;
+
+  const showBuy = name === 'buy';
+  if (!showBuy) {
+    const sellBody = document.getElementById('sellSignalsBody');
+    if (sellBody && sellBody.dataset.rendered !== 'true') {
+      sellBody.innerHTML = renderSellRows(sellSignals);
+      sellBody.dataset.rendered = 'true';
+      // Sell rows' chart-toggle buttons don't exist until this lazy render,
+      // so they must be wired here rather than only at initial page load —
+      // the same reason the Buy panel's toggles are wired separately, right
+      // after loadMarketSignalCharts's price fetch resolves.
+      const card = document.getElementById('marketSignalsCard');
+      if (card) wireChartToggles(card, _marketSignalSeries, MARKET_CHART_PREFIX);
+    }
+  }
+
+  buyTab.setAttribute('aria-selected', String(showBuy));
+  sellTab.setAttribute('aria-selected', String(!showBuy));
+  buyTab.tabIndex = showBuy ? 0 : -1;
+  sellTab.tabIndex = showBuy ? -1 : 0;
+  buyTab.classList.toggle('active', showBuy);
+  sellTab.classList.toggle('active', !showBuy);
+  buyPanel.hidden = !showBuy;
+  sellPanel.hidden = showBuy;
+}
+
+export function _wireSignalTabs(sellSignals) {
+  const tabs = [...document.querySelectorAll('[role="tab"][data-signal-tab]')];
+  tabs.forEach((tab, index) => {
+    tab.addEventListener('click', () => _activateSignalTab(tab.dataset.signalTab, sellSignals));
+    tab.addEventListener('keydown', (event) => {
+      let nextIndex;
+      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
+      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
+      if (event.key === 'Home') nextIndex = 0;
+      if (event.key === 'End') nextIndex = tabs.length - 1;
+      if (nextIndex === undefined) return;

exec
/bin/zsh -lc "nl -ba run_optimized_scan.py | sed -n '45,145p;315,455p;510,625p'; nl -ba .github/workflows/daily_screening_git_storage.yml | sed -n '1,190p'; nl -ba .github/workflows/midday_quick_scan.yml | sed -n '1,100p'; nl -ba scripts/fetch_momentum_status.py | sed -n '35,175p'; nl -ba dashboard.py | sed -n '80,110p;260,285p;410,435p;585,720p'; nl -ba static/js/core/ui-helpers.js | sed -n '35,115p'; nl -ba static/js/views/shortlist.js | sed -n '35,135p'; nl -ba static/js/views/market.js | sed -n '20,65p;275,365p'; nl -ba static/js/dashboard.js | sed -n '1,35p'; nl -ba templates/dashboard.html | sed -n '12,55p'" in /Users/badripratti/Desktop/stock-screener
 succeeded in 23ms:
    35	HISTORY_PATH = Path(__file__).parent.parent / "data" / "momentum_status" / "history.json"
    36	LOCK_PATH = HISTORY_PATH.parent / "history.lock"
    37	
    38	STATUS_LABELS = {
    39	    'hot': 'Hot — extended',
    40	    'stable': 'Stable uptrend',
    41	    'basing': 'Basing / cooling',
    42	    'avoid': 'Avoid — downtrend',
    43	}
    44	
    45	
    46	def classify_status(phase_info: dict) -> str:
    47	    phase = phase_info.get('phase', 0)
    48	    distance_50 = phase_info.get('distance_from_50sma', 0)
    49	    slope_50 = phase_info.get('slope_50', 0)
    50	
    51	    if phase in (3, 4):
    52	        return 'avoid'
    53	    if phase == 1:
    54	        return 'basing'
    55	    if phase == 2:
    56	        if distance_50 > 20:
    57	            return 'hot'
    58	        if slope_50 <= 0:
    59	            return 'basing'
    60	        return 'stable'
    61	    return 'basing'  # phase 0 / insufficient data — treat as neutral, not a buy
    62	
    63	
    64	def _load_history() -> dict:
    65	    if HISTORY_PATH.exists():
    66	        try:
    67	            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    68	        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
    69	            return {}
    70	    return {}
    71	
    72	
    73	def _save_history(history: dict):
    74	    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    75	    HISTORY_PATH.write_text(json.dumps(sanitize_nan(history), indent=2), encoding="utf-8")
    76	
    77	
    78	def update_streak(history: dict, ticker: str, status: str, today_str: str) -> dict:
    79	    """Advances (or resets) the day-streak for one ticker. Safe to call many
    80	    times on the same calendar day (idempotent) — the streak count only
    81	    changes on an actual day-to-day transition.
    82	
    83	    "days" counts CONSECUTIVE calendar days, not observations: if the ticker
    84	    wasn't checked yesterday (e.g. the app was closed, or a fetch failed),
    85	    the streak restarts from 1 today rather than pretending the gap didn't
    86	    happen — a status observed on Sept 1 and next observed on Sept 13 is not
    87	    a real 2-day streak, that would silently misstate how long the trend has
    88	    actually held.
    89	    """
    90	    existing = history.get(ticker)
    91	    today = date.fromisoformat(today_str)
    92	
    93	    if existing and existing.get('last_seen') == today_str:
    94	        if existing['status'] != status:
    95	            # Flipped status within the same day — restart the streak from today.
    96	            existing['status'] = status
    97	            existing['since'] = today_str
    98	            existing['days'] = 1
    99	        # else: same status, same day — nothing to advance.
   100	        return existing
   101	
   102	    if existing and existing['status'] == status:
   103	        last_seen = date.fromisoformat(existing['last_seen'])
   104	        gap_days = (today - last_seen).days
   105	        if gap_days == 1:
   106	            existing['days'] = existing.get('days', 1) + 1
   107	        else:
   108	            # A gap of more than a day breaks the streak, even though the
   109	            # status matches — we don't actually know it held continuously
   110	            # through the days we didn't check.
   111	            existing['since'] = today_str
   112	            existing['days'] = 1
   113	        existing['last_seen'] = today_str
   114	        return existing
   115	
   116	    record = {'status': status, 'since': today_str, 'days': 1, 'last_seen': today_str}
   117	    history[ticker] = record
   118	    return record
   119	
   120	
   121	def main():
   122	    parser = argparse.ArgumentParser()
   123	    parser.add_argument('--tickers', type=str, required=True)
   124	    parser.add_argument('--group', type=str, default='misc')
   125	    parser.add_argument('--json-out', type=str, required=True)
   126	    args = parser.parse_args()
   127	
   128	    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
   129	    today_str = date.today().isoformat()
   130	
   131	    # Fetch + classify (slow, network-bound) happens BEFORE the shared-file
   132	    # lock is taken — a lock should only ever guard the fast in-memory
   133	    # update, never be held across a network call.
   134	    classified = {}  # ticker -> (status, phase_info)
   135	    for ticker in tickers:
   136	        print(f"Classifying momentum status for {ticker}...")
   137	        try:
   138	            price_data = yf.Ticker(ticker).history(period="1y", interval="1d")
   139	            if price_data.empty or len(price_data) < 200:
   140	                print(f"  {ticker}: insufficient price history, skipping")
   141	                continue
   142	            current_price = float(price_data['Close'].iloc[-1])
   143	            phase_info = classify_phase(price_data, current_price)
   144	            classified[ticker] = (classify_status(phase_info), phase_info)
   145	        except Exception as e:
   146	            print(f"  {ticker}: failed ({e})")
   147	
   148	    # Multiple dashboard views can each kick off their own momentum-status
   149	    # job around the same time, all sharing this one history file — an
   150	    # unlocked load-modify-save here would let whichever job saves last
   151	    # silently discard another job's ticker updates. Holding an exclusive
   152	    # file lock for this whole read-modify-write section serializes them:
   153	    # the second job blocks until the first finishes, then reads the
   154	    # already-updated state instead of overwriting it.
   155	    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
   156	    snapshot = {}
   157	    with open(LOCK_PATH, 'w') as lockfile:
   158	        fcntl.flock(lockfile, fcntl.LOCK_EX)
   159	        try:
   160	            history = _load_history()
   161	            for ticker, (status, phase_info) in classified.items():
   162	                record = update_streak(history, ticker, status, today_str)
   163	                snapshot[ticker] = {
   164	                    'status': status,
   165	                    'label': STATUS_LABELS[status],
   166	                    'days': record['days'],
   167	                    'since': record['since'],
   168	                    'phase': phase_info.get('phase'),
   169	                    'distance_from_50sma': phase_info.get('distance_from_50sma'),
   170	                }
   171	            _save_history(history)
   172	        finally:
   173	            fcntl.flock(lockfile, fcntl.LOCK_UN)
   174	
   175	    out_path = Path(args.json_out)
    80	    path = Path(path)
    81	    if not path.exists():
    82	        return default
    83	    try:
    84	        return json.loads(path.read_text(encoding="utf-8"))
    85	    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
    86	        return default
    87	
    88	
    89	def parse_scan_file(filepath):
    90	    """Parse a scan .txt file into structured data."""
    91	    text = Path(filepath).read_text(encoding="utf-8")
    92	
    93	    data = {
    94	        "scan_date": "",
    95	        "generated": "",
    96	        "stats": {},
    97	        "spy": {},
    98	        "breadth": {},
    99	        "regime": "",
   100	        "buy_signals": [],
   101	        "sell_signals": [],
   102	    }
   103	
   104	    # Header stats
   105	    m = re.search(r"Scan Date:\s*(.+)", text)
   106	    if m:
   107	        data["scan_date"] = m.group(1).strip()
   108	
   109	    m = re.search(r"Generated:\s*(.+)", text)
   110	    if m:
   260	        reasons = re.findall(r"[•]\s*(.+)", block)
   261	        signal["reasons"] = [r.strip() for r in reasons[:5]]
   262	
   263	        data["sell_signals"].append(signal)
   264	
   265	    return data
   266	
   267	
   268	def get_scan_files():
   269	    """Get list of available scan files, newest first."""
   270	    if not SCAN_DIR.exists():
   271	        return []
   272	    files = sorted(SCAN_DIR.glob("optimized_scan_*.txt"), reverse=True)
   273	    return [{"name": f.stem, "path": str(f), "date": f.stem.replace("optimized_scan_", "")} for f in files]
   274	
   275	
   276	def get_backtest_files():
   277	    """Get list of walk-forward backtest history files, newest first."""
   278	    if not BACKTEST_DIR.exists():
   279	        return []
   280	    files = sorted(BACKTEST_DIR.glob("walk_forward_*.json"), reverse=True)
   281	    out = []
   282	    for f in files:
   283	        data = _read_json(f, {})
   284	        out.append({"name": f.stem, "path": str(f), "generated": data.get("generated")})
   285	    return out
   410	            JOBS[job_id]["status"] = "error"
   411	            JOBS[job_id]["proc"] = None
   412	
   413	
   414	def _build_job(kind, body):
   415	    """Build (cmd, result_path) for a job kind from a request body, using each
   416	    underlying script's own argparse defaults when a param is omitted."""
   417	    python = _venv_python()
   418	    job_id = uuid.uuid4().hex[:12]
   419	
   420	    if kind == "scan":
   421	        cmd = [python, str(PROJECT_ROOT / "run_optimized_scan.py")]
   422	        if not body.get("full"):
   423	            cmd.append("--test-mode")
   424	        if body.get("enable_llm_agents"):
   425	            cmd.append("--enable-llm-agents")
   426	        result_path = str(SCAN_DIR / "shortlist_latest.json")
   427	
   428	    elif kind == "backtest-top3":
   429	        result_path = str(ADHOC_DIR / f"backtest_top3_{job_id}.json")
   430	        cmd = [
   431	            python, str(PROJECT_ROOT / "scripts" / "backtest_top3.py"),
   432	            "--days", str(body.get("days", 7)),
   433	            "--sample", str(body.get("sample", 150)),
   434	            "--investment", str(body.get("investment", 1000)),
   435	            "--json-out", result_path,
   585	        capture_output=True, encoding="utf-8", errors="replace", timeout=60, close_fds=False,
   586	    )
   587	
   588	
   589	@app.route("/api/sync", methods=["POST"])
   590	def api_sync():
   591	    """git pull the repo so today's committed scan/shortlist/backtest data
   592	    (from the scheduled GitHub Actions runs that send the email) shows up
   593	    here too, without the user having to leave the dashboard to do it."""
   594	    try:
   595	        # Absolute git path (not the bare "git", which posix_spawn eligibility
   596	        # requires — see the comment in _launch_job()) and no cwd= (process cwd
   597	        # is already PROJECT_ROOT, set once at startup).
   598	        result = _git_pull()
   599	
   600	        # A local job run (Full Scan / Positions / etc., all launched from
   601	        # this same dashboard) writes into the same data/ paths the automated
   602	        # workflow commits to — if you've run anything locally since the last
   603	        # sync, those two can diverge and block a fast-forward pull. Since
   604	        # data/ is always regenerable output (never something hand-authored),
   605	        # the automated commit is the one that actually matters here: discard
   606	        # the local modifications and retry once rather than surfacing a git
   607	        # merge error for what's really just stale scan output.
   608	        if result.returncode != 0 and "overwritten by merge" in (result.stdout + result.stderr):
   609	            subprocess.run(
   610	                [_git_binary(), "checkout", "--", "data/"],
   611	                capture_output=True, encoding="utf-8", errors="replace", timeout=30, close_fds=False,
   612	            )
   613	            result = _git_pull()
   614	
   615	        return jsonify({
   616	            "success": result.returncode == 0,
   617	            "output": (result.stdout + result.stderr).strip(),
   618	        })
   619	    except Exception as e:
   620	        return jsonify({"success": False, "output": str(e)})
   621	
   622	
   623	@app.route("/api/positions/upload", methods=["POST"])
   624	def api_positions_upload():
   625	    """Save a Fidelity Positions CSV export uploaded from the browser. Never
   626	    leaves this machine — no credentials, no login, just the file you already
   627	    downloaded yourself. Overwrites the previous upload (single "current
   628	    portfolio" file, not a history)."""
   629	    f = request.files.get("csv")
   630	    if not f or not f.filename:
   631	        return jsonify({"success": False, "error": "no file uploaded"}), 400
   632	    POSITIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
   633	    f.save(str(POSITIONS_CSV))
   634	    return jsonify({"success": True})
   635	
   636	
   637	@app.route("/api/positions")
   638	def api_positions():
   639	    """Last computed position analysis, if any. Empty/`reason` shape (not an
   640	    error) when nothing's been uploaded or analyzed yet, matching the other
   641	    read-only routes."""
   642	    has_csv = POSITIONS_CSV.exists()
   643	    data = _read_json(ADHOC_DIR / "positions_latest.json", None)
   644	    if data is None:
   645	        return jsonify({
   646	            "has_csv": has_csv,
   647	            "position_analyses": [], "summary": {"total_positions": 0}, "urgent_actions": [],
   648	        })
   649	    data["has_csv"] = has_csv
   650	    return jsonify(data)
   651	
   652	
   653	@app.route("/api/news/<group>")
   654	def api_news(group):
   655	    """Last fetched news batch for a group ("positions" or "buy"). Empty shape
   656	    (not an error) when nothing's been fetched yet."""
   657	    return jsonify(_read_json(ADHOC_DIR / f"news_{group}.json", {"generated": None, "tickers": [], "news": {}}))
   658	
   659	
   660	@app.route("/api/price-history/<group>")
   661	def api_price_history(group):
   662	    """Last fetched price-history batch for a group (e.g. "shortlist"). Empty
   663	    shape (not an error) when nothing's been fetched yet."""
   664	    return jsonify(_read_json(ADHOC_DIR / f"price_history_{group}.json", {"generated": None, "tickers": [], "prices": {}}))
   665	
   666	
   667	@app.route("/api/momentum-status/<group>")
   668	def api_momentum_status(group):
   669	    """Last computed hot/stable/basing/avoid classification (+ day-streak) for
   670	    a group. Empty shape (not an error) when nothing's been fetched yet."""
   671	    return jsonify(_read_json(ADHOC_DIR / f"momentum_status_{group}.json", {"generated": None, "tickers": [], "status": {}}))
   672	
   673	
   674	# ---------------------------------------------------------------------------
   675	# Read-only data routes
   676	# ---------------------------------------------------------------------------
   677	
   678	@app.route("/")
   679	def index():
   680	    return render_template("dashboard.html")
   681	
   682	
   683	@app.route("/api/scans")
   684	def api_scans():
   685	    return jsonify(get_scan_files())
   686	
   687	
   688	@app.route("/api/scan")
   689	def api_scan():
   690	    path = request.args.get("path", "")
   691	    if not path:
   692	        latest = SCAN_DIR / "latest_optimized_scan.txt"
   693	        if latest.exists():
   694	            path = str(latest)
   695	        else:
   696	            return jsonify({"error": "No scan data"})
   697	
   698	    if not Path(path).exists():
   699	        return jsonify({"error": "File not found"})
   700	
   701	    return jsonify(parse_scan_file(path))
   702	
   703	
   704	@app.route("/api/top20")
   705	def api_top20():
   706	    return jsonify(_read_json(SCAN_DIR / "top20_latest.json", {"generated": None, "result": None, "top20": []}))
   707	
   708	
   709	@app.route("/api/shortlist")
   710	def api_shortlist():
   711	    return jsonify(_read_json(SCAN_DIR / "shortlist_latest.json", {
   712	        "generated": None, "result": None, "shortlist": [],
   713	        "fundamentals_audits": {}, "catalyst_sentiments": {}, "congress_signals": {},
   714	    }))
   715	
   716	
   717	@app.route("/api/backtest/latest")
   718	def api_backtest_latest():
   719	    data = _read_json(BACKTEST_DIR / "latest.json", None)
   720	    if data is None:
    35	      }
    36	    });
    37	  });
    38	}
    39	
    40	export function refreshOpenCharts(getSeries, idPrefix) {
    41	  _openCharts.forEach(chartId => {
    42	    if (!chartId.startsWith(idPrefix)) return;
    43	    if (!document.getElementById(`${chartId}-wrap`)) return;
    44	    const ticker = chartId.slice(idPrefix.length);
    45	    const series = getSeries(ticker);
    46	    if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
    47	  });
    48	}
    49	
    50	const MOMENTUM_LABELS = { hot: 'HOT', stable: 'STABLE', basing: 'BASING', avoid: 'AVOID' };
    51	
    52	function momentumBadgeHTML(entry) {
    53	  if (!entry || !entry.status) return '';
    54	  const label = MOMENTUM_LABELS[entry.status] || entry.status.toUpperCase();
    55	  const dayWord = entry.days === 1 ? 'day' : 'days';
    56	  return `<span class="momentum-badge ${entry.status}" title="${entry.label} — ${entry.days} ${dayWord}">${label}<span class="streak">Day ${entry.days}</span></span>`;
    57	}
    58	
    59	export async function loadMomentumStatus(tickers, group, onLoaded) {
    60	  if (!tickers.length) return;
    61	  await startJob('momentum-status', { tickers, group }, async (st) => {
    62	    if (st.status !== 'success') return;
    63	    const data = await fetchJSON(`/api/momentum-status/${group}`);
    64	    onLoaded(data.status || {});
    65	  });
    66	}
    67	
    68	export function paintMomentumSlots(tickers, statusMap) {
    69	  tickers.forEach(ticker => {
    70	    const slot = document.getElementById(`momentum-slot-${ticker}`);
    71	    if (slot && statusMap[ticker]) slot.innerHTML = momentumBadgeHTML(statusMap[ticker]);
    72	  });
    73	}
    74	
    75	export function showToast(msg) {
    76	  const t = document.getElementById('toast');
    77	  t.textContent = msg;
    78	  t.style.opacity = '1';
    79	  clearTimeout(t._timer);
    80	  t._timer = setTimeout(() => { t.style.opacity = '0'; }, 5000);
    81	}
    82	
    83	export function redditCell(count) {
    84	  if (count == null) return '<span style="color:var(--muted)">-</span>';
    85	  if (count === 0) return '<span style="color:var(--muted)">0</span>';
    86	  const hot = count >= 10;
    87	  return `<span style="color:${hot ? 'var(--yellow)' : 'var(--text)'};font-weight:${hot ? 700 : 400}">${count}</span>`;
    88	}
    89	
    90	export function escapeHtml(text) {
    91	  const div = document.createElement('div');
    92	  div.textContent = text == null ? '' : String(text);
    93	  return div.innerHTML;
    94	}
    95	
    96	export function cleanEmoji(text) {
    97	  return (text || '').replace(/[\uD83D\uDFE2\uDD34\uDFE1\u2B50\u26A0\u2713\uDEA8]/g, '').trim();
    98	}
    99	
   100	// External news URLs must not be able to introduce executable schemes.
   101	export function safeHref(url) {
   102	  try {
   103	    const parsed = new URL(url, location.href);
   104	    return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '#';
   105	  } catch {
   106	    return '#';
   107	  }
   108	}
   109	
   110	export function toggleReasons(btn) {
   111	  const extra = btn.previousElementSibling;
   112	  if (extra.style.display === 'none') {
   113	    extra.style.display = '';
   114	    btn.textContent = 'less';
   115	  } else {
    35	    <div class="agent-badge-sub">${escapeHtml(signal.summary)}</div></div>`;
    36	}
    37	
    38	function fundamentalsFlagsHTML(audit) {
    39	  if (!audit) return '';
    40	  const red = audit.red_flags || [];
    41	  const green = audit.green_flags || [];
    42	  let html = '';
    43	  if (red.length) {
    44	    const more = red.length > 1 ? ` (+${red.length - 1} more)` : '';
    45	    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${escapeHtml(red[0].flag)}${more}</div>`;
    46	  }
    47	  if (green.length) {
    48	    const more = green.length > 1 ? ` (+${green.length - 1} more)` : '';
    49	    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
    50	  }
    51	  return html;
    52	}
    53	
    54	export async function renderShortlistView() {
    55	  const data = await fetchJSON('/api/shortlist');
    56	  if (currentView !== 'shortlist') return; // navigated away before this resolved
    57	  // Set regardless of which branch below renders — a scan that legitimately
    58	  // found zero candidates still has a real `generated` timestamp, and the
    59	  // empty-state banner needs it to distinguish "no scan has ever run" from
    60	  // "today's scan ran and found nothing" (see the two banner messages below).
    61	  pageMeta.textContent = data.generated ? `Generated ${new Date(data.generated).toLocaleString()}` : '';
    62	  if (!data.shortlist || data.shortlist.length === 0) {
    63	    const top20 = await fetchJSON('/api/top20');
    64	    if (currentView !== 'shortlist') return;
    65	    // `result` (added alongside `generated`) distinguishes "no scan has run
    66	    // yet" (data.generated is null) from "a scan ran and legitimately found
    67	    // zero qualifying candidates" (data.result === 'no_candidates') — without
    68	    // this, both looked identical and a normal empty trading day read as if
    69	    // the pipeline were broken.
    70	    const banner = !data.generated
    71	      ? `No filtered shortlist yet — run a scan with AI agents enabled from the
    72	         <a href="#/scan">Full Scan</a> page to get a Top 5 filtered by fundamentals,
    73	         news sentiment, and congressional trading. Showing the raw Top 20 pool below instead.`
    74	      : `Today's scan (generated ${new Date(data.generated).toLocaleString()}) found no candidates that
    75	         passed screening criteria — this can happen on a normal trading day. Showing the raw Top 20
    76	         pool below instead.`;
    77	    content.innerHTML = `
    78	      <div class="banner">${banner}</div>
    79	      ${renderTop20Table(top20.top20 || [])}
    80	    `;
    81	    const fallbackTickers = (top20.top20 || []).map(s => s.ticker);
    82	    loadMomentumStatus(fallbackTickers, 'shortlist-fallback', (statusMap) => paintMomentumSlots(fallbackTickers, statusMap));
    83	    return;
    84	  }
    85	
    86	  const tickers = data.shortlist.map(s => s.ticker);
    87	
    88	  const cards = data.shortlist.map((s, i) => {
    89	    const badges = [
    90	      catalystBadgeHTML(data.catalyst_sentiments[s.ticker]),
    91	      congressBadgeHTML(data.congress_signals[s.ticker]),
    92	      fundamentalsFlagsHTML(data.fundamentals_audits[s.ticker]),
    93	    ].filter(Boolean).join('');
    94	    const backfillNote = !s.passed_filters
    95	      ? `<div class="backfill-note">Backfilled — didn't clear filters: ${(s.drop_reasons || []).join('; ') || 'below filter bar'}</div>`
    96	      : '';
    97	    const chartId = `short-chart-${s.ticker}`;
    98	    return `
    99	      <div class="pick-card ${!s.passed_filters ? 'backfilled' : ''}">
   100	        <div class="pick-rank">#${i + 1}</div>
   101	        <div class="pick-header">
   102	          <span class="ticker">${s.ticker}</span>
   103	          ${s.current_price != null ? `<span class="pick-price">$${s.current_price.toFixed(2)}</span>` : ''}
   104	          <span id="${chartId}-slot"></span>
   105	        </div>
   106	        <div class="pick-scores">
   107	          <div class="score-block"><div class="label">Composite</div><div class="value">${s.composite_score ?? '-'}</div></div>
   108	          <div class="score-block"><div class="label">Base Score</div><div class="value">${s.combined_score ?? s.score ?? '-'}</div></div>
   109	        </div>
   110	        <div style="margin-bottom:10px"><span id="momentum-slot-${s.ticker}"></span></div>
   111	        ${backfillNote}
   112	        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
   113	        ${fidelityLink(s.ticker, 'Buy on Fidelity', 'buy')}
   114	        <div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
   115	      </div>`;
   116	  }).join('');
   117	
   118	  content.innerHTML = `
   119	    <div class="source-note email">
   120	      <b>This is what your daily email sends.</b> Same 5 picks, same links — the email is just a snapshot of this page.
   121	      <button type="button" class="news-jump-btn" onclick="document.getElementById('shortlistNews').scrollIntoView({behavior:'smooth'})">Jump to news ↓</button>
   122	    </div>
   123	    <div class="shortlist-grid">${cards}</div>
   124	    <div id="shortlistNews" style="margin-top:24px"></div>`;
   125	
   126	  loadShortlistCharts(tickers);
   127	  loadShortlistNews(tickers);
   128	  loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap));
   129	  _startLive(() => {
   130	    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
   131	    _liveGuarded('shortlist-news', () => loadShortlistNews(tickers, true));
   132	    _liveGuarded('shortlist-momentum', () => loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap)));
   133	  });
   134	}
   135	
    20	let _marketSignalPrices = {};
    21	let _marketSignalTickers = [];
    22	const MARKET_CHART_PREFIX = 'market-sig-chart-';
    23	
    24	export async function renderMarketView() {
    25	  const scans = await fetchJSON('/api/scans');
    26	  if (currentView !== 'market') return; // navigated away before this resolved
    27	  if (!scans.length) {
    28	    content.innerHTML = '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan to get started.</p></div>';
    29	    return;
    30	  }
    31	  content.innerHTML = `
    32	    <div class="source-note email">
    33	      <b>This is the full pool your email's picks are drawn from.</b> Buy/Sell Signals and the Top 20 table
    34	      here are the same lists that get emailed (capped at 15 rows there; everything's shown here) — the
    35	      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
    36	    </div>
    37	    <div style="margin-bottom:16px">
    38	      <select class="scan-select" id="scanSelect"></select>
    39	    </div>
    40	    <div id="marketBody"></div>
    41	    <div id="newsSections" style="margin-top:24px"></div>`;
    42	  const sel = document.getElementById('scanSelect');
    43	  scans.forEach(s => {
    44	    const opt = document.createElement('option');
    45	    opt.value = s.path;
    46	    opt.textContent = s.date.replace('_', ' ');
    47	    sel.appendChild(opt);
    48	  });
    49	  sel.addEventListener('change', () => loadMarketScan(sel.value));
    50	  loadMarketScan(scans[0].path);
    51	  loadMarketNews();
    52	  _startLive(() => {
    53	    _liveGuarded('market-news', () => loadMarketNews(true));
    54	    _liveGuarded('market-momentum', () => loadMomentumStatus(
    55	      _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
    56	    ));
    57	    _liveGuarded('market-signal-charts', () => loadMarketSignalCharts(_marketSignalTickers, true));
    58	  });
    59	}
    60	
    61	async function loadMarketNews(silent) {
    62	  const el = document.getElementById('newsSections');
    63	  if (!el) return; // navigated away before this resolved
    64	  if (!silent) {
    65	    el.innerHTML = _newsSectionHTML('positions', 'News on your positions', 'loading') +
   275	      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
   276	      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
   277	      if (event.key === 'Home') nextIndex = 0;
   278	      if (event.key === 'End') nextIndex = tabs.length - 1;
   279	      if (nextIndex === undefined) return;
   280	      event.preventDefault();
   281	      const nextTab = tabs[nextIndex];
   282	      _activateSignalTab(nextTab.dataset.signalTab, sellSignals);
   283	      nextTab.focus();
   284	    });
   285	  });
   286	}
   287	
   288	async function loadMarketScan(path) {
   289	  const [scan, top20] = await Promise.all([
   290	    fetchJSON('/api/scan?path=' + encodeURIComponent(path)),
   291	    fetchJSON('/api/top20'),
   292	  ]);
   293	  if (currentView !== 'market') return; // navigated away before this resolved
   294	  if (scan.error) {
   295	    document.getElementById('marketBody').innerHTML = '<div class="no-data"><h2>No scan data</h2></div>';
   296	    return;
   297	  }
   298	  pageMeta.textContent = `${scan.scan_date} · ${scan.stats.analyzed || '?'} analyzed · ${scan.regime}`;
   299	
   300	  const buyCount = scan.stats.buy_count ?? scan.buy_signals.length;
   301	  const sellCount = scan.stats.sell_count ?? scan.sell_signals.length;
   302	  const topScore = scan.buy_signals.length ? scan.buy_signals[0].score : '-';
   303	  const regimeClass = scan.regime.includes('RISK-ON') ? 'risk-on' : scan.regime.includes('RISK-OFF') ? 'risk-off' : 'transitional';
   304	
   305	  document.getElementById('marketBody').innerHTML = `
   306	    <div class="stats-row">
   307	      <div class="stat-card green"><div class="label">Buy Signals</div><div class="value">${buyCount}</div><div class="sub">Phase 2 confirmed uptrends</div></div>
   308	      <div class="stat-card red"><div class="label">Sell Signals</div><div class="value">${sellCount}</div><div class="sub">Phase 3/4 breakdowns</div></div>
   309	      <div class="stat-card blue"><div class="label">Top Score</div><div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div><div class="sub">${scan.buy_signals.length ? scan.buy_signals[0].ticker : '-'}</div></div>
   310	      <div class="stat-card"><div class="label">Universe</div><div class="value">${(scan.stats.analyzed || 0).toLocaleString()}</div><div class="sub">of ${(scan.stats.total_universe || 0).toLocaleString()} | ${scan.stats.processing_minutes || '?'} min</div></div>
   311	      <div class="stat-card ${scan.spy.phase === 2 ? 'green' : scan.spy.phase === 4 ? 'red' : 'yellow'}"><div class="label">SPY Phase</div><div class="value">${scan.spy.phase || '?'}</div><div class="sub">${scan.spy.trend || ''} @ $${(scan.spy.price || 0).toFixed(2)}</div></div>
   312	    </div>
   313	    <div class="grid-2">
   314	      <div class="card"><h2>Market Breadth</h2><div class="chart-wrap"><canvas id="breadthChart"></canvas></div></div>
   315	      <div class="card">
   316	        <h2>SPY Regime</h2>
   317	        <span class="regime-badge ${regimeClass}">${scan.regime}</span>
   318	        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px">
   319	          <div><div style="color:var(--muted);font-size:11px">Phase</div><div style="font-size:18px;font-weight:700">${scan.spy.phase} - ${scan.spy.phase_name || ''}</div></div>
   320	          <div><div style="color:var(--muted);font-size:11px">Confidence</div><div style="font-size:18px;font-weight:700">${scan.spy.confidence || '?'}%</div></div>
   321	        </div>
   322	      </div>
   323	    </div>
   324	    ${_buyOpportunityChartCardHTML(scan.buy_signals)}
   325	    ${renderTop20Table(top20.top20 || [])}
   326	    ${_signalTabsHTML(scan)}`;
   327	
   328	  renderBreadthChart('breadthChart', scan.breadth);
   329	  _wireSignalTabs(scan.sell_signals);
   330	  _renderBuyOpportunityChart(scan.buy_signals);
   331	
   332	  // The live-refresh closure must always read the current scan selection.
   333	  _marketTop20Tickers = (top20.top20 || []).map(s => s.ticker);
   334	  loadMomentumStatus(_marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap));
   335	
   336	  // Union of both tabs' tickers, fetched once regardless of which tab is
   337	  // active — a chart toggle on a lazily-rendered Sell row still needs its
   338	  // price data to already be present the moment that row exists.
   339	  _marketSignalTickers = [...scan.buy_signals, ...scan.sell_signals].map(s => s.ticker);
   340	  loadMarketSignalCharts(_marketSignalTickers);
   341	}
   342	
   343	function _signalChartRowHTML(ticker, colspan) {
   344	  const chartId = `${MARKET_CHART_PREFIX}${ticker}`;
   345	  return `<tr class="chart-row"><td colspan="${colspan}">
   346	    <div class="position-chart-wrap signal-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
   347	  </td></tr>`;
   348	}
   349	
   350	function renderBuyRows(signals) {
   351	  if (!signals.length) return '<tr><td colspan="12" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
   352	  return signals.map(s => {
   353	    const pct = (s.score / (s.max_score || 125)) * 100;
   354	    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
   355	    const entryClass = (s.entry_quality || '').toLowerCase();
   356	    const topReasons = (s.reasons || []).slice(0, 3).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
   357	    const extra = (s.reasons || []).slice(3);
   358	    const extraHTML = extra.length
   359	      ? `<div class="extra-reasons" style="display:none">${extra.map(r => `<li>${cleanEmoji(r)}</li>`).join('')}</div><button class="expand-btn" onclick="toggleReasons(this)">+${extra.length} more</button>`
   360	      : '';
   361	    return `<tr data-ticker="${s.ticker}">
   362	      <td>${s.rank}</td>
   363	      <td><span class="ticker">${s.ticker}</span></td>
   364	      <td>${s.current_price != null ? '$' + s.current_price.toFixed(2) : '-'}</td>
   365	      <td>${chartToggleButtonHTML(`${MARKET_CHART_PREFIX}${s.ticker}`)}</td>
     1	// Stock Screener dashboard — vanilla JS single-page app. Hash-based routing
     2	// (no router library), fetch() for data, Chart.js (via charts.js) for charts.
     3	
     4	import { fetchJSON } from './core/api.js';
     5	import { route, initRouter } from './core/router.js';
     6	import { currentView } from './core/state.js';
     7	import { showToast, toggleReasons } from './core/ui-helpers.js';
     8	import { renderBacktestsView } from './views/backtests.js';
     9	import { renderMarketView } from './views/market.js';
    10	import { renderPositionsView } from './views/positions.js';
    11	import { renderRunView } from './views/run.js';
    12	import { renderScanView } from './views/scan.js';
    13	import { renderShortlistView } from './views/shortlist.js';
    14	
    15	const VIEWS = {
    16	  positions: { title: 'Positions', render: renderPositionsView },
    17	  shortlist: { title: 'Shortlist', render: renderShortlistView },
    18	  market: { title: 'Market', render: renderMarketView },
    19	  backtests: { title: 'Backtests', render: renderBacktestsView },
    20	  run: { title: 'Run Simulation', render: renderRunView },
    21	  scan: { title: 'Full Scan', render: renderScanView },
    22	};
    23	
    24	// Inline handlers need an explicit global now that dashboard.js is a module.
    25	window.toggleReasons = toggleReasons;
    26	
    27	// "Sync latest" reports a GIT fact (did `git pull` fetch new commits) which
    28	// is a different question from "is the data actually recent" — the daily
    29	// scan is a separate scheduled job that can go a while without producing a
    30	// new commit (weekends, a workflow failure, zero qualifying candidates) even
    31	// though `git pull` correctly and truthfully says "already up to date" every
    32	// time. This surfaces the shortlist's own `generated` timestamp next to the
    33	// button so that gap is visible instead of silently confusing.
    34	const dataFreshnessEl = document.getElementById('dataFreshness');
    35	function _relativeAge(isoString) {
    12	<div class="app">
    13	  <nav class="sidebar" aria-label="Primary">
    14	    <div class="brand">Stock Screener</div>
    15	
    16	    <div class="nav-group" role="group" aria-label="Monitor">
    17	      <div class="nav-group-label">Monitor</div>
    18	      <a href="#/positions" class="nav-item" data-view="positions">
    19	        <span class="nav-item-title">Positions</span>
    20	        <span class="nav-item-sub">Your portfolio</span>
    21	      </a>
    22	      <a href="#/shortlist" class="nav-item" data-view="shortlist">
    23	        <span class="nav-item-title">Shortlist</span>
    24	        <span class="nav-item-sub">Today's email picks</span>
    25	      </a>
    26	      <a href="#/market" class="nav-item" data-view="market">
    27	        <span class="nav-item-title">Market</span>
    28	        <span class="nav-item-sub">Full scan, all signals</span>
    29	      </a>
    30	    </div>
    31	
    32	    <div class="nav-group" role="group" aria-label="Analyze">
    33	      <div class="nav-group-label">Analyze</div>
    34	      <a href="#/backtests" class="nav-item" data-view="backtests">
    35	        <span class="nav-item-title">Backtests</span>
    36	        <span class="nav-item-sub">Past performance, not email</span>
    37	      </a>
    38	    </div>
    39	
    40	    <div class="nav-group" role="group" aria-label="Run">
    41	      <div class="nav-group-label">Run</div>
    42	      <a href="#/run" class="nav-item" data-view="run">
    43	        <span class="nav-item-title">Run Simulation</span>
    44	        <span class="nav-item-sub">Test a strategy</span>
    45	      </a>
    46	      <a href="#/scan" class="nav-item" data-view="scan">
    47	        <span class="nav-item-title">Full Scan</span>
    48	        <span class="nav-item-sub">Trigger a new scan</span>
    49	      </a>
    50	    </div>
    51	
    52	    <div class="sidebar-footer">Not financial advice.</div>
    53	  </nav>
    54	
    55	  <main class="main">

codex
No files were modified. The repository currently does not retain a dependable longitudinal record: `shortlist_latest.json`, `top20_latest.json`, and `latest_optimized_scan.txt` are mutable snapshots, and the midday workflow can overwrite the Top 20/full-report view with a random 100-stock sample.

## Recommendation

Create a versioned, Git-committed snapshot ledger containing one slim, self-describing record per scan session. Treat the automated full-universe daily scan as the canonical consistency series. Keep midday samples and local scans in separate namespaces so they never affect claims such as “4 of the last 5 scans.”

Derive aggregates from snapshots at API-read time. Do not store mutable per-ticker counters as the source of truth.

## 1. Meaning of “consistently well”

For each list—`shortlist`, `top20`, and `buy_signals`—calculate:

- Appearances in the last 5, 10, and 20 canonical scans.
- Appearance percentage, with the actual denominator shown.
- Current consecutive-scan streak.
- Longest streak.
- First and last seen.
- Best and average rank.
- Current, average, and previous score.
- Score change and short trend, only when the score definition is comparable.
- Total qualifying scan sessions and data coverage warnings.

Use “scan session,” not calendar-day streak:

- A scan session is one successfully completed canonical `daily_full` observation.
- Weekends and holidays with no scan do not break a streak.
- A failed or missing run creates no observation and does not assert that the ticker disappeared. The API should flag the coverage gap.
- A completed zero-candidate scan is an observation with empty lists. It counts in the denominator and breaks every active appearance streak.
- Multiple executions on the same America/New_York date and source slot resolve to one canonical snapshot; a retry replaces that date’s snapshot rather than incrementing counts.
- Midday and local runs are separate series, regardless of date.

This differs intentionally from [`fetch_momentum_status.py`](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:65), which breaks status streaks after any gap greater than one calendar day. That logic causes Friday-to-Monday observations to restart. For picks, “3-scan streak” is more honest and useful than pretending weekends were observations or breaking every Monday.

Score trend should use scan ordinal, not elapsed calendar days. It must be suppressed across incompatible scoring revisions. Store the scoring-field name and code revision with every snapshot.

The five trustworthy shortlist runs already illustrate the result:

- `LILA`: 5/5 appearances, five-scan streak, best rank 1, average composite 126.48.
- `LILAK`: 4/5, current two-scan streak, average composite 126.08.
- `LTC`: 3/5, current three-scan streak, best rank 2.

## 2. Lists to track

Track three separate membership lists inside each snapshot:

1. `shortlist`: the strongest user-facing claim—the five picks actually sent after agent filtering.
2. `top20`: the pool from which the shortlist is selected.
3. `buy_signals`: every technical buy signal from the completed run.

Never blend these into one “picked” statistic. A label must read, for example, “Shortlist 4/5” or “Top 20 8/10.”

For future live scans, the scanner has the complete in-memory `buy_signals` collection at [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:417), so persisting slim rows for all signals is inexpensive.

The text report writes full details only for the first 50 at [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:120). One subtlety: it subsequently writes all remaining ticker symbols in sorted order, so historical membership and implied rank can technically be reconstructed beyond 50, but scores and details cannot. Backfilled entries should expose that reduced score coverage rather than pretend they are equivalent to live events.

The current daily/midday integrity problem must be fixed first:

- Daily: full universe, `--enable-llm-agents`, canonical Top 20 and shortlist.
- Midday: random 100-stock sample, no LLM agents.
- Both currently write `top20_latest.json` and scan reports.
- Midday leaves `shortlist_latest.json` alone, creating a possible daily shortlist paired with a later, unrelated midday Top 20.

Give the scanner an explicit run identity such as:

```text
--run-kind daily-full
--run-kind midday-sample
--run-kind local-full
--run-kind local-test
```

Only `daily-full` should update the canonical `top20_latest.json` and `latest_optimized_scan.txt`. Midday should write distinct `top20_midday_latest.json` and source-labelled reports.

## 3. Storage

Recommended layout:

```text
data/pick_history/
  snapshots/
    daily_full/
      2026-09-14.json
      2026-09-15.json
    midday_sample/
      2026-09-14.json
  README.json
```

Example snapshot:

```json
{
  "schema_version": 1,
  "session_id": "daily_full:2026-09-18",
  "session_date": "2026-09-18",
  "generated_at": "2026-09-18T17:07:46Z",
  "timezone": "America/New_York",
  "run_kind": "daily_full",
  "provenance": "live",
  "source": {
    "workflow": "daily_screening_git_storage",
    "github_run_id": "…",
    "git_sha": "…",
    "attempt": 1
  },
  "scope": {
    "mode": "full_universe",
    "total_universe": 3770,
    "analyzed": 1973,
    "completed": true
  },
  "score_definitions": {
    "buy_signals": "technical_score_v1",
    "top20": "combined_score_v1",
    "shortlist": "composite_score_v1"
  },
  "lists": {
    "shortlist": [
      {"ticker": "LILAK", "rank": 1, "score": 123.6, "passed_filters": true}
    ],
    "top20": [
      {"ticker": "LILAK", "rank": 1, "score": 123.6}
    ],
    "buy_signals": [
      {"ticker": "LILAK", "rank": 1, "score": 94.8}
    ]
  }
}
```

Snapshots should contain only fields needed for longitudinal analysis, not full reasons, news links, audits, or fundamental text.

At roughly 400 slim buy-signal rows × 260 runs, growth is modest—on the order of several megabytes per year. Deriving aggregates across a few hundred JSON files is acceptable. A process cache keyed by file names/mtimes can be added later.

Why not other formats:

- JSONL: one shared append target creates Git merge conflicts and awkward replacement/idempotency.
- Aggregate-only JSON: cannot audit or correct historical calculations.
- SQLite: poor Git diffs, binary merge conflicts, and unnecessary deployment complexity.
- Git history as the runtime database: workflows use shallow clones, history can be rewritten/pruned, and reading hundreds of `git show` objects per API call is fragile.

## 4. Writer, idempotency, and workflow concurrency

The snapshot should be assembled inside `run_optimized_scan.py`, where all three exact in-memory lists and scan statistics coexist. A post-scan parser is vulnerable to mixing a fresh midday Top 20 with yesterday’s shortlist.

Recommended sequence:

1. Finish scoring and shortlist construction.
2. Write the normal latest outputs.
3. Write the text report.
4. Validate and atomically write the single history snapshot.
5. Send email.
6. Let the workflow commit all outputs together.

If canonical history writing fails, the workflow should fail rather than commit a latest snapshot without its history counterpart.

Use the existing atomic-write pattern at [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:56), enhanced with:

- A unique temporary filename.
- An `fcntl` lock around same-date read/replace for local concurrent processes.
- Schema/count/duplicate-ticker validation before replacement.

`fcntl`, as used by momentum history, only protects processes sharing one filesystem. It does not solve races between GitHub runners.

The current workflows have:

- No shared `concurrency` group.
- Shallow checkout.
- No pull, fetch/rebase, or push retry before pushing.
- Both commit overlapping `data/daily_scans/` and fundamental-cache paths.

Therefore overlapping workflows can produce a non-fast-forward push failure. Add the same workflow-level concurrency group to both files, with `cancel-in-progress: false`, so checkout and execution are serialized across daily and midday jobs. A rejected push caused by an unrelated concurrent main update should fail visibly; silently auto-resolving generated-data conflicts risks choosing the wrong scan.

Local dashboard scans currently invoke the same scanner at [`dashboard.py`](/Users/badripratti/Desktop/stock-screener/dashboard.py:421). They should be labelled `local-full` or `local-test` and must not modify canonical history. Optionally retain them under a local/adhoc namespace, but do not commit or include them in the default leaderboard.

## 5. Backfill findings and procedure

The earliest trustworthy canonical daily history is September 14, 2026.

| Dates | Source | Universe / analyzed | Decision |
|---|---|---:|---|
| Sep 14–18 | Automated daily commits | 3,766–3,770 / 1,971–1,982 | Canonical backfill |
| Sep 14–18 | Automated midday commits | 100 / 48–55 | Optional `midday_sample` backfill only |
| Sep 9 | Manual commit, test scan | 100 / 59 | Exclude |
| Sep 12 Top 20 | Manually committed snapshot, no matching report | Unknown | Exclude |
| Jul 29 | Test reports | 100 / 45–50 | Exclude |
| Jul 30 08:52 | Full report, manually added weeks later | 3,772 / 1,979 | Exclude from continuous canonical series |
| Jul 30 22:51 | Test report | 100 / 51 | Exclude |

Canonical commit pairs are:

- `25b3fc3f` — September 14
- `40b6d251` — September 15
- `3b798ef7` — September 16
- `9d9fe4ee` — September 17
- `919bf881` — September 18

Backfill procedure:

1. Add a deterministic `scripts/backfill_pick_history.py`.
2. Require an explicit manifest of accepted commit/date/run-kind tuples; do not infer trust from commit-message text alone.
3. Use `git show <hash>:data/daily_scans/{shortlist,top20}_latest.json`.
4. Pair each with the dated full report whose `Generated`, `Total Universe`, and `Analyzed` headers match.
5. Reconstruct buy-signal membership/rank; set missing scores after rank 50 to `null` and record `score_coverage: "top_50_only"`.
6. Mark every generated snapshot `provenance: "backfill"` with source commit and report path.
7. Validate list counts, timestamps, universe size, unique tickers, and Top 20/shortlist containment.
8. Run twice and assert byte-identical output.
9. Commit the five canonical daily files and, if desired, the separately namespaced midday files.

## 6. API

Add a read-only endpoint such as:

```text
GET /api/pick-history?list=shortlist&window=5&source=daily_full
```

Response:

```json
{
  "schema_version": 1,
  "list": "shortlist",
  "source": "daily_full",
  "window_requested": 5,
  "sessions_available": 5,
  "sessions": ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"],
  "coverage_gaps": [],
  "tickers": {
    "LILA": {
      "appearances": 5,
      "appearance_rate": 1.0,
      "current_streak": 5,
      "longest_streak": 5,
      "first_seen": "2026-09-14",
      "last_seen": "2026-09-18",
      "best_rank": 1,
      "average_rank": 2.2,
      "average_score": 126.48,
      "latest_score": 121.8,
      "score_delta": -6.6,
      "score_comparable": true
    }
  }
}
```

A second ticker timeline endpoint can be deferred. The dashboard already pulls committed data through `/api/sync`; after `git pull`, the route will discover the new snapshot files automatically. It should return a normal empty shape plus warnings when no valid ledger exists, following the current `_read_json` route convention.

## 7. UI scope

For this sprint:

- Add a compact badge to each Shortlist card: `5/5 · streak 5`.
- Add a “Consistency” column to the shared Top 20 table renderer. Because [`renderTop20Table`](/Users/badripratti/Desktop/stock-screener/static/js/core/ui-helpers.js:120) is reused, this covers both Shortlist fallback and Market Top 20.
- Add a dedicated “Consistency” view under the Analyze nav group, with list and window selectors and a sortable leaderboard.
- Reuse the asynchronous slot-painting pattern from `loadMomentumStatus`/`paintMomentumSlots`, but history is a direct API fetch, not a background network job.

Defer:

- Charts and per-ticker timelines.
- Buy-table consistency columns. Market can display a historical report selected from the dropdown while currently fetching the latest Top 20 at [`market.js`](/Users/badripratti/Desktop/stock-screener/static/js/views/market.js:288); adding present-day history to historical buy rows would be temporally misleading.
- Midday-vs-daily comparison UI.
- Symbol-change reconciliation UI.

The dedicated page matters: badges answer “is this recurring?” at a glance; the leaderboard answers “which stocks have been most consistent?” across stocks not present today.

## 8. Files and task order

Foundation, sequential:

1. New `src/history/pick_history.py`: schema, validation, atomic writer, aggregation.
2. New `tests/test_pick_history.py`.
3. Add run-kind/source metadata and snapshot writing to [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:315).
4. Separate daily and midday latest outputs.
5. Modify both workflow files to pass run kind, commit `data/pick_history/`, and share a concurrency group.
6. Add and run the deterministic backfill script.

After the schema/API contract is fixed, these can proceed mostly independently:

- Backend: [`dashboard.py`](/Users/badripratti/Desktop/stock-screener/dashboard.py:667) and Flask tests.
- Shared badges/table: `static/js/core/ui-helpers.js`, `shortlist.js`, and relevant CSS.
- Dedicated view: new `static/js/views/consistency.js`, [`dashboard.js`](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:15), [`dashboard.html`](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:32), and CSS.
- Plain-Node UI tests.

Several of these files already have uncommitted user changes, so implementation must preserve and integrate with that work rather than replacing it.

## 9. Risks and edge cases

- Symbol changes/delistings: initially treat ticker symbols as distinct identities. Store exchange/CIK when available, but only merge identities through an explicit alias map.
- Empty successful scan: persist it; it is meaningful negative evidence.
- Failed scan: do not create an event; expose a coverage gap.
- Midday-only day: visible only in the midday series, never canonical daily statistics.
- Time zones: emit timezone-aware timestamps and derive the session date explicitly in America/New_York. Current timestamps are naive.
- Scoring changes: version each score definition and do not average across incompatible versions.
- Corrupt snapshot: skip it, return a warning, and never silently count it as an empty scan.
- Schema evolution: require `schema_version` and migration readers.
- Duplicate ticker rows: reject the snapshot.
- Partial writes: atomic replacement plus validation.
- Stale laptop: show “history through DATE” near badges/leaderboard. Auto-sync helps, but offline/stuck Git state must remain visible.
- Momentum-history copying: its calendar-gap semantics and mutable per-ticker aggregate are both unsuitable here.
- Local sync currently may discard local `data/` changes after a pull conflict. Keeping canonical history CI-only prevents local scan history from being unexpectedly erased.
- The report heading always says “FULL MARKET” even for test mode. Add explicit machine-readable run-kind/universe headers; do not infer scope from that heading.
- The existing report parser’s `\w+` ticker regex can mishandle symbols containing punctuation. Ledger capture should use the actual ticker field, not report regexes.

## 10. Testing and rollout verification

Python/pytest:

- Snapshot validation and serialization.
- Same source/date rerun is idempotent.
- Daily and midday on the same date remain independent.
- Zero-candidate session breaks streaks.
- Missing session creates a coverage warning but not a false disappearance.
- Weekend gap does not break a consecutive-scan streak.
- Window denominators with fewer than N available sessions.
- Rank/score averages and trend.
- Score-version incompatibility.
- Malformed/corrupt files.
- Duplicate ticker rejection.
- Backfill fixture tests for the five accepted commits.
- Flask empty, normal, invalid-query, and corrupt-ledger response contracts.

Plain Node under `tests/js/`:

- Badge formatting and empty state.
- Shared Top 20 column rendering.
- Leaderboard sorting/filtering.
- Escaping ticker/API content.
- Navigation registration.
- Stale/partial-data warning rendering.

Workflow verification:

1. Validate YAML and run all local Python/Node tests.
2. Merge the change.
3. Trigger `workflow_dispatch` for the daily workflow rather than waiting for cron.
4. Confirm exactly one `daily_full/YYYY-MM-DD.json` is committed with full-universe metadata.
5. Re-run the same dispatch/date and confirm the session count does not increase.
6. Trigger midday manually and confirm it writes only `midday_sample`, does not replace canonical Top 20/history, and does not alter shortlist history.
7. Pull through the dashboard Sync button and confirm badges and leaderboard update.

The highest-priority corrective work is separating daily and midday outputs. Without that, a history ledger could faithfully preserve data while still presenting statistically incomparable scans as one series.
tokens used
84,256
No files were modified. The repository currently does not retain a dependable longitudinal record: `shortlist_latest.json`, `top20_latest.json`, and `latest_optimized_scan.txt` are mutable snapshots, and the midday workflow can overwrite the Top 20/full-report view with a random 100-stock sample.

## Recommendation

Create a versioned, Git-committed snapshot ledger containing one slim, self-describing record per scan session. Treat the automated full-universe daily scan as the canonical consistency series. Keep midday samples and local scans in separate namespaces so they never affect claims such as “4 of the last 5 scans.”

Derive aggregates from snapshots at API-read time. Do not store mutable per-ticker counters as the source of truth.

## 1. Meaning of “consistently well”

For each list—`shortlist`, `top20`, and `buy_signals`—calculate:

- Appearances in the last 5, 10, and 20 canonical scans.
- Appearance percentage, with the actual denominator shown.
- Current consecutive-scan streak.
- Longest streak.
- First and last seen.
- Best and average rank.
- Current, average, and previous score.
- Score change and short trend, only when the score definition is comparable.
- Total qualifying scan sessions and data coverage warnings.

Use “scan session,” not calendar-day streak:

- A scan session is one successfully completed canonical `daily_full` observation.
- Weekends and holidays with no scan do not break a streak.
- A failed or missing run creates no observation and does not assert that the ticker disappeared. The API should flag the coverage gap.
- A completed zero-candidate scan is an observation with empty lists. It counts in the denominator and breaks every active appearance streak.
- Multiple executions on the same America/New_York date and source slot resolve to one canonical snapshot; a retry replaces that date’s snapshot rather than incrementing counts.
- Midday and local runs are separate series, regardless of date.

This differs intentionally from [`fetch_momentum_status.py`](/Users/badripratti/Desktop/stock-screener/scripts/fetch_momentum_status.py:65), which breaks status streaks after any gap greater than one calendar day. That logic causes Friday-to-Monday observations to restart. For picks, “3-scan streak” is more honest and useful than pretending weekends were observations or breaking every Monday.

Score trend should use scan ordinal, not elapsed calendar days. It must be suppressed across incompatible scoring revisions. Store the scoring-field name and code revision with every snapshot.

The five trustworthy shortlist runs already illustrate the result:

- `LILA`: 5/5 appearances, five-scan streak, best rank 1, average composite 126.48.
- `LILAK`: 4/5, current two-scan streak, average composite 126.08.
- `LTC`: 3/5, current three-scan streak, best rank 2.

## 2. Lists to track

Track three separate membership lists inside each snapshot:

1. `shortlist`: the strongest user-facing claim—the five picks actually sent after agent filtering.
2. `top20`: the pool from which the shortlist is selected.
3. `buy_signals`: every technical buy signal from the completed run.

Never blend these into one “picked” statistic. A label must read, for example, “Shortlist 4/5” or “Top 20 8/10.”

For future live scans, the scanner has the complete in-memory `buy_signals` collection at [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:417), so persisting slim rows for all signals is inexpensive.

The text report writes full details only for the first 50 at [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:120). One subtlety: it subsequently writes all remaining ticker symbols in sorted order, so historical membership and implied rank can technically be reconstructed beyond 50, but scores and details cannot. Backfilled entries should expose that reduced score coverage rather than pretend they are equivalent to live events.

The current daily/midday integrity problem must be fixed first:

- Daily: full universe, `--enable-llm-agents`, canonical Top 20 and shortlist.
- Midday: random 100-stock sample, no LLM agents.
- Both currently write `top20_latest.json` and scan reports.
- Midday leaves `shortlist_latest.json` alone, creating a possible daily shortlist paired with a later, unrelated midday Top 20.

Give the scanner an explicit run identity such as:

```text
--run-kind daily-full
--run-kind midday-sample
--run-kind local-full
--run-kind local-test
```

Only `daily-full` should update the canonical `top20_latest.json` and `latest_optimized_scan.txt`. Midday should write distinct `top20_midday_latest.json` and source-labelled reports.

## 3. Storage

Recommended layout:

```text
data/pick_history/
  snapshots/
    daily_full/
      2026-09-14.json
      2026-09-15.json
    midday_sample/
      2026-09-14.json
  README.json
```

Example snapshot:

```json
{
  "schema_version": 1,
  "session_id": "daily_full:2026-09-18",
  "session_date": "2026-09-18",
  "generated_at": "2026-09-18T17:07:46Z",
  "timezone": "America/New_York",
  "run_kind": "daily_full",
  "provenance": "live",
  "source": {
    "workflow": "daily_screening_git_storage",
    "github_run_id": "…",
    "git_sha": "…",
    "attempt": 1
  },
  "scope": {
    "mode": "full_universe",
    "total_universe": 3770,
    "analyzed": 1973,
    "completed": true
  },
  "score_definitions": {
    "buy_signals": "technical_score_v1",
    "top20": "combined_score_v1",
    "shortlist": "composite_score_v1"
  },
  "lists": {
    "shortlist": [
      {"ticker": "LILAK", "rank": 1, "score": 123.6, "passed_filters": true}
    ],
    "top20": [
      {"ticker": "LILAK", "rank": 1, "score": 123.6}
    ],
    "buy_signals": [
      {"ticker": "LILAK", "rank": 1, "score": 94.8}
    ]
  }
}
```

Snapshots should contain only fields needed for longitudinal analysis, not full reasons, news links, audits, or fundamental text.

At roughly 400 slim buy-signal rows × 260 runs, growth is modest—on the order of several megabytes per year. Deriving aggregates across a few hundred JSON files is acceptable. A process cache keyed by file names/mtimes can be added later.

Why not other formats:

- JSONL: one shared append target creates Git merge conflicts and awkward replacement/idempotency.
- Aggregate-only JSON: cannot audit or correct historical calculations.
- SQLite: poor Git diffs, binary merge conflicts, and unnecessary deployment complexity.
- Git history as the runtime database: workflows use shallow clones, history can be rewritten/pruned, and reading hundreds of `git show` objects per API call is fragile.

## 4. Writer, idempotency, and workflow concurrency

The snapshot should be assembled inside `run_optimized_scan.py`, where all three exact in-memory lists and scan statistics coexist. A post-scan parser is vulnerable to mixing a fresh midday Top 20 with yesterday’s shortlist.

Recommended sequence:

1. Finish scoring and shortlist construction.
2. Write the normal latest outputs.
3. Write the text report.
4. Validate and atomically write the single history snapshot.
5. Send email.
6. Let the workflow commit all outputs together.

If canonical history writing fails, the workflow should fail rather than commit a latest snapshot without its history counterpart.

Use the existing atomic-write pattern at [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:56), enhanced with:

- A unique temporary filename.
- An `fcntl` lock around same-date read/replace for local concurrent processes.
- Schema/count/duplicate-ticker validation before replacement.

`fcntl`, as used by momentum history, only protects processes sharing one filesystem. It does not solve races between GitHub runners.

The current workflows have:

- No shared `concurrency` group.
- Shallow checkout.
- No pull, fetch/rebase, or push retry before pushing.
- Both commit overlapping `data/daily_scans/` and fundamental-cache paths.

Therefore overlapping workflows can produce a non-fast-forward push failure. Add the same workflow-level concurrency group to both files, with `cancel-in-progress: false`, so checkout and execution are serialized across daily and midday jobs. A rejected push caused by an unrelated concurrent main update should fail visibly; silently auto-resolving generated-data conflicts risks choosing the wrong scan.

Local dashboard scans currently invoke the same scanner at [`dashboard.py`](/Users/badripratti/Desktop/stock-screener/dashboard.py:421). They should be labelled `local-full` or `local-test` and must not modify canonical history. Optionally retain them under a local/adhoc namespace, but do not commit or include them in the default leaderboard.

## 5. Backfill findings and procedure

The earliest trustworthy canonical daily history is September 14, 2026.

| Dates | Source | Universe / analyzed | Decision |
|---|---|---:|---|
| Sep 14–18 | Automated daily commits | 3,766–3,770 / 1,971–1,982 | Canonical backfill |
| Sep 14–18 | Automated midday commits | 100 / 48–55 | Optional `midday_sample` backfill only |
| Sep 9 | Manual commit, test scan | 100 / 59 | Exclude |
| Sep 12 Top 20 | Manually committed snapshot, no matching report | Unknown | Exclude |
| Jul 29 | Test reports | 100 / 45–50 | Exclude |
| Jul 30 08:52 | Full report, manually added weeks later | 3,772 / 1,979 | Exclude from continuous canonical series |
| Jul 30 22:51 | Test report | 100 / 51 | Exclude |

Canonical commit pairs are:

- `25b3fc3f` — September 14
- `40b6d251` — September 15
- `3b798ef7` — September 16
- `9d9fe4ee` — September 17
- `919bf881` — September 18

Backfill procedure:

1. Add a deterministic `scripts/backfill_pick_history.py`.
2. Require an explicit manifest of accepted commit/date/run-kind tuples; do not infer trust from commit-message text alone.
3. Use `git show <hash>:data/daily_scans/{shortlist,top20}_latest.json`.
4. Pair each with the dated full report whose `Generated`, `Total Universe`, and `Analyzed` headers match.
5. Reconstruct buy-signal membership/rank; set missing scores after rank 50 to `null` and record `score_coverage: "top_50_only"`.
6. Mark every generated snapshot `provenance: "backfill"` with source commit and report path.
7. Validate list counts, timestamps, universe size, unique tickers, and Top 20/shortlist containment.
8. Run twice and assert byte-identical output.
9. Commit the five canonical daily files and, if desired, the separately namespaced midday files.

## 6. API

Add a read-only endpoint such as:

```text
GET /api/pick-history?list=shortlist&window=5&source=daily_full
```

Response:

```json
{
  "schema_version": 1,
  "list": "shortlist",
  "source": "daily_full",
  "window_requested": 5,
  "sessions_available": 5,
  "sessions": ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"],
  "coverage_gaps": [],
  "tickers": {
    "LILA": {
      "appearances": 5,
      "appearance_rate": 1.0,
      "current_streak": 5,
      "longest_streak": 5,
      "first_seen": "2026-09-14",
      "last_seen": "2026-09-18",
      "best_rank": 1,
      "average_rank": 2.2,
      "average_score": 126.48,
      "latest_score": 121.8,
      "score_delta": -6.6,
      "score_comparable": true
    }
  }
}
```

A second ticker timeline endpoint can be deferred. The dashboard already pulls committed data through `/api/sync`; after `git pull`, the route will discover the new snapshot files automatically. It should return a normal empty shape plus warnings when no valid ledger exists, following the current `_read_json` route convention.

## 7. UI scope

For this sprint:

- Add a compact badge to each Shortlist card: `5/5 · streak 5`.
- Add a “Consistency” column to the shared Top 20 table renderer. Because [`renderTop20Table`](/Users/badripratti/Desktop/stock-screener/static/js/core/ui-helpers.js:120) is reused, this covers both Shortlist fallback and Market Top 20.
- Add a dedicated “Consistency” view under the Analyze nav group, with list and window selectors and a sortable leaderboard.
- Reuse the asynchronous slot-painting pattern from `loadMomentumStatus`/`paintMomentumSlots`, but history is a direct API fetch, not a background network job.

Defer:

- Charts and per-ticker timelines.
- Buy-table consistency columns. Market can display a historical report selected from the dropdown while currently fetching the latest Top 20 at [`market.js`](/Users/badripratti/Desktop/stock-screener/static/js/views/market.js:288); adding present-day history to historical buy rows would be temporally misleading.
- Midday-vs-daily comparison UI.
- Symbol-change reconciliation UI.

The dedicated page matters: badges answer “is this recurring?” at a glance; the leaderboard answers “which stocks have been most consistent?” across stocks not present today.

## 8. Files and task order

Foundation, sequential:

1. New `src/history/pick_history.py`: schema, validation, atomic writer, aggregation.
2. New `tests/test_pick_history.py`.
3. Add run-kind/source metadata and snapshot writing to [`run_optimized_scan.py`](/Users/badripratti/Desktop/stock-screener/run_optimized_scan.py:315).
4. Separate daily and midday latest outputs.
5. Modify both workflow files to pass run kind, commit `data/pick_history/`, and share a concurrency group.
6. Add and run the deterministic backfill script.

After the schema/API contract is fixed, these can proceed mostly independently:

- Backend: [`dashboard.py`](/Users/badripratti/Desktop/stock-screener/dashboard.py:667) and Flask tests.
- Shared badges/table: `static/js/core/ui-helpers.js`, `shortlist.js`, and relevant CSS.
- Dedicated view: new `static/js/views/consistency.js`, [`dashboard.js`](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:15), [`dashboard.html`](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:32), and CSS.
- Plain-Node UI tests.

Several of these files already have uncommitted user changes, so implementation must preserve and integrate with that work rather than replacing it.

## 9. Risks and edge cases

- Symbol changes/delistings: initially treat ticker symbols as distinct identities. Store exchange/CIK when available, but only merge identities through an explicit alias map.
- Empty successful scan: persist it; it is meaningful negative evidence.
- Failed scan: do not create an event; expose a coverage gap.
- Midday-only day: visible only in the midday series, never canonical daily statistics.
- Time zones: emit timezone-aware timestamps and derive the session date explicitly in America/New_York. Current timestamps are naive.
- Scoring changes: version each score definition and do not average across incompatible versions.
- Corrupt snapshot: skip it, return a warning, and never silently count it as an empty scan.
- Schema evolution: require `schema_version` and migration readers.
- Duplicate ticker rows: reject the snapshot.
- Partial writes: atomic replacement plus validation.
- Stale laptop: show “history through DATE” near badges/leaderboard. Auto-sync helps, but offline/stuck Git state must remain visible.
- Momentum-history copying: its calendar-gap semantics and mutable per-ticker aggregate are both unsuitable here.
- Local sync currently may discard local `data/` changes after a pull conflict. Keeping canonical history CI-only prevents local scan history from being unexpectedly erased.
- The report heading always says “FULL MARKET” even for test mode. Add explicit machine-readable run-kind/universe headers; do not infer scope from that heading.
- The existing report parser’s `\w+` ticker regex can mishandle symbols containing punctuation. Ledger capture should use the actual ticker field, not report regexes.

## 10. Testing and rollout verification

Python/pytest:

- Snapshot validation and serialization.
- Same source/date rerun is idempotent.
- Daily and midday on the same date remain independent.
- Zero-candidate session breaks streaks.
- Missing session creates a coverage warning but not a false disappearance.
- Weekend gap does not break a consecutive-scan streak.
- Window denominators with fewer than N available sessions.
- Rank/score averages and trend.
- Score-version incompatibility.
- Malformed/corrupt files.
- Duplicate ticker rejection.
- Backfill fixture tests for the five accepted commits.
- Flask empty, normal, invalid-query, and corrupt-ledger response contracts.

Plain Node under `tests/js/`:

- Badge formatting and empty state.
- Shared Top 20 column rendering.
- Leaderboard sorting/filtering.
- Escaping ticker/API content.
- Navigation registration.
- Stale/partial-data warning rendering.

Workflow verification:

1. Validate YAML and run all local Python/Node tests.
2. Merge the change.
3. Trigger `workflow_dispatch` for the daily workflow rather than waiting for cron.
4. Confirm exactly one `daily_full/YYYY-MM-DD.json` is committed with full-universe metadata.
5. Re-run the same dispatch/date and confirm the session count does not increase.
6. Trigger midday manually and confirm it writes only `midday_sample`, does not replace canonical Top 20/history, and does not alter shortlist history.
7. Pull through the dashboard Sync button and confirm badges and leaderboard update.

The highest-priority corrective work is separating daily and midday outputs. Without that, a history ledger could faithfully preserve data while still presenting statistically incomparable scans as one series.
