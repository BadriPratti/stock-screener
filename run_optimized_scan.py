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
from datetime import datetime, timezone
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


def resolve_output_policy(run_kind, test_mode, record_market_motion=False):
    """Return output gates for a scan invocation without causing side effects."""
    if run_kind == 'midday-sample':
        return {
            'write_canonical_latest': False,
            'record_history': False,
            'record_market_motion': False,
        }
    if run_kind == 'daily-full':
        return {
            'write_canonical_latest': True,
            'record_history': not test_mode,
            'record_market_motion': not test_mode,
        }
    if run_kind == 'local':
        return {
            'write_canonical_latest': True,
            'record_history': False,
            'record_market_motion': bool(record_market_motion) and not test_mode,
        }
    raise ValueError(f"Unknown run kind: {run_kind}")


def record_pick_history(*, shortlist, top20, scope, source):
    """Record the canonical scan ledger without making it a publishing dependency."""
    try:
        from src.screening import pick_history

        return pick_history.record_scan(
            shortlist=shortlist,
            top20=top20,
            scope=scope,
            source=source,
        )
    except Exception as exc:
        logger.error("Pick history ledger write failed: %s", exc)
        print(f"::warning title=pick-history::ledger write failed: {exc}")
        return None


def build_market_motion_points(buy_signals, analyses, scored_signals, tracked):
    """Build one outcome per current buy or previously tracked ticker."""
    from src.screening import market_motion

    points = [
        market_motion.normalize_buy_signal(signal, rank=rank)
        for rank, signal in enumerate(buy_signals, 1)
    ]
    buy_tickers = {
        market_motion.normalise_ticker(signal.get('ticker'))
        for signal in buy_signals
    }
    analyses_by_ticker = {
        market_motion.normalise_ticker(analysis.get('ticker')): analysis
        for analysis in analyses
        if market_motion.normalise_ticker(analysis.get('ticker'))
    }
    scored_by_ticker = {
        market_motion.normalise_ticker(ticker): signal
        for ticker, signal in scored_signals.items()
        if market_motion.normalise_ticker(ticker)
    }

    for ticker in sorted(market_motion.normalise_ticker(value) for value in tracked):
        if not ticker or ticker in buy_tickers:
            continue
        analysis = analyses_by_ticker.get(ticker)
        phase = (analysis.get('phase_info') or {}).get('phase') if analysis else None
        if ticker in scored_by_ticker:
            points.append(market_motion.outcome_point(
                ticker, signal=scored_by_ticker[ticker], phase=phase,
            ))
        elif analysis is not None:
            points.append(market_motion.outcome_point(ticker, phase=phase))
        else:
            points.append(market_motion.outcome_point(ticker, error='not_analyzed'))
    return market_motion.dedupe_points(points)


def record_market_motion(*, buy_signals, analyses, scored_signals, tickers,
                         total_analyzed, spy_data, should_generate_buys,
                         source, provenance, root=None, generated_at=None):
    """Record a complete market-motion frame without blocking scan delivery."""
    if not isinstance(total_analyzed, (int, float)) or total_analyzed <= 0:
        reason = "scan analyzed no stocks"
        logger.warning("Market motion frame skipped: %s", reason)
        print(f"::warning title=market-motion::frame skipped: {reason}")
        return None
    try:
        if spy_data is None or getattr(spy_data, 'empty', False) or len(spy_data) == 0:
            reason = "SPY data is missing or empty"
            logger.warning("Market motion frame skipped: %s", reason)
            print(f"::warning title=market-motion::frame skipped: {reason}")
            return None

        from src.screening import market_motion

        frames, warnings = market_motion.load_frames(root=root)
        for warning in warnings:
            logger.warning("Market motion history: %s", warning)
        points = build_market_motion_points(
            buy_signals,
            analyses,
            scored_signals,
            market_motion.tracked_tickers(frames),
        )
        timestamp = generated_at or datetime.now(timezone.utc)
        frame = market_motion.build_frame(
            run_kind=market_motion.RUN_KIND_DAILY_FULL,
            generated_at=timestamp,
            session_date=market_motion.session_date_from_bar(spy_data.index[-1]),
            points=points,
            scope={
                'mode': 'full_universe',
                'requested': len(tickers),
                'analyzed': total_analyzed,
                'completed': True,
            },
            coverage={'kind': market_motion.COVERAGE_COMPLETE},
            regime={
                'should_generate_buys': should_generate_buys,
                'source_run_id': None,
            },
            provenance=provenance,
            source=source,
        )
        return market_motion.write_frame(frame, root=root)
    except Exception as exc:
        logger.error("Market motion frame write failed: %s", exc)
        print(f"::warning title=market-motion::frame write failed: {exc}")
        return None


def save_report(results, buy_signals, sell_signals, spy_analysis, breadth,
                output_dir="./data/daily_scans", write_latest=True, run_kind='local'):
    """Save comprehensive report."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')

    output = []
    output.append("="*80)
    output.append("OPTIMIZED FULL MARKET SCAN - ALL US STOCKS")
    output.append(f"Scan Date: {date_str}")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Run Kind: {run_kind}")
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

    if write_latest:
        latest_path = Path(output_dir) / "latest_optimized_scan.txt"
        with open(latest_path, 'w') as f:
            f.write(report_text)

    logger.info(f"Report saved: {filepath}")
    print(report_text)

    return filepath


def build_arg_parser():
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
    parser.add_argument('--run-kind', choices=('daily-full', 'midday-sample', 'local'), default='local',
                        help='Scan output scope (default: local)')
    parser.add_argument('--record-market-motion', action='store_true',
                        help='Record a full-universe market-motion frame')
    parser.add_argument('--enable-llm-agents', action='store_true',
                         help='Run the Fundamentals Auditor + Catalyst Sentiment agents (Claude API calls) '
                              'on the Top 20 shortlist. Needs ANTHROPIC_API_KEY set; no-ops with a warning otherwise.')
    return parser


def main():
    parser = build_arg_parser()

    args = parser.parse_args()
    output_policy = resolve_output_policy(
        args.run_kind, args.test_mode, args.record_market_motion,
    )
    logger.info(
        "Run kind %s: canonical latest outputs=%s, pick history ledger=%s",
        args.run_kind,
        'write' if output_policy['write_canonical_latest'] else 'skip',
        'write' if output_policy['record_history'] else 'skip',
    )
    if args.run_kind == 'daily-full' and args.test_mode:
        logger.warning(
            "daily-full was requested with --test-mode; pick history will not be recorded "
            "because a sample is not a canonical full-universe session."
        )

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
        scored_non_buys = {}
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
                    else:
                        scored_non_buys[analysis['ticker']] = signal

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
        if buy_signals:
            logger.info("Building Top 20 shortlist...")
            top20 = build_top20(buy_signals, reddit_mentions, insider_signals)
        # For runs allowed to publish canonical latest outputs, write
        # top20_latest.json even when empty — otherwise a scan that finds zero
        # buy signals leaves a stale prior day's Top 20 in place with no
        # indication it's stale (the dashboard's Market/Shortlist views read
        # this file directly and would show yesterday's picks as if fresh).
        # sanitize_nan: this feeds the dashboard's Market/Shortlist views
        # directly — a stray NaN in a technical score would otherwise
        # serialize as an invalid JSON token the browser can't parse.
        if output_policy['write_canonical_latest']:
            top20_path.parent.mkdir(parents=True, exist_ok=True)
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
            if output_policy['write_canonical_latest']:
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
            if output_policy['write_canonical_latest']:
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
        save_report(
            results, buy_signals, sell_signals, spy_analysis, breadth,
            write_latest=output_policy['write_canonical_latest'], run_kind=args.run_kind,
        )

        # Record only after all primary latest/report outputs have been published.
        # A ledger failure is intentionally auxiliary and cannot block email delivery.
        source = {
            key: value for key, value in {
                'git_sha': os.environ.get('GITHUB_SHA'),
                'github_run_id': os.environ.get('GITHUB_RUN_ID'),
                'workflow': os.environ.get('GITHUB_WORKFLOW'),
            }.items() if value
        }
        if output_policy['record_history']:
            total_universe = results.get('total_processed')
            record_pick_history(
                shortlist=shortlist if args.enable_llm_agents else None,
                top20=top20,
                scope={
                    'total_universe': total_universe if isinstance(total_universe, int) else None,
                    'analyzed': results.get('total_analyzed'),
                    'completed': True,
                },
                source=source,
            )

        if output_policy['record_market_motion']:
            record_market_motion(
                buy_signals=buy_signals,
                analyses=results['analyses'],
                scored_signals=scored_non_buys,
                tickers=tickers,
                total_analyzed=results.get('total_analyzed'),
                spy_data=processor.spy_data,
                should_generate_buys=signal_rec['should_generate_buys'],
                source=source,
                provenance='live' if args.run_kind == 'daily-full' else 'local',
            )

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
