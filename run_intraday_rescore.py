#!/usr/bin/env python3
"""Re-score the market-motion tracked roster without full-scan outputs."""

from __future__ import annotations

import argparse
import logging

from src.screening import market_motion
from src.screening.intraday_rescore import format_result, run_rescore
from src.screening.optimized_batch_processor import OptimizedBatchProcessor
from src.screening.signal_engine import score_buy_signal


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=int, default=500)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--root", default=str(market_motion.DEFAULT_ROOT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    if args.force:
        logging.getLogger(__name__).warning(
            "FORCE MODE REQUESTED: market-open guard will be skipped"
        )
    result = run_rescore(
        OptimizedBatchProcessor,
        score_buy_signal,
        args.root,
        args.cap,
        None,
        args.force,
        args.dry_run,
        workers=args.workers,
        delay=args.delay,
    )
    print(format_result(result))
    return 1 if result["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
