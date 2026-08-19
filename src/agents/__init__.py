"""LLM-powered analysis agents (Fundamentals Auditor, News/Catalyst Sentiment).

"Agent" here means an automated pipeline module wired into run_optimized_scan.py,
not a standalone autonomous loop. Each one reads data already available in (or
easily reachable from) the pipeline, calls Claude for qualitative judgment a pure
numbers score would miss, and logs a structured result for future backtesting.

None of these modules ever modify src/screening/signal_engine.py — every score or
flag they produce is additive/logged, for manual review.
"""
