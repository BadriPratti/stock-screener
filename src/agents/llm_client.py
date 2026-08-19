"""Shared Claude client setup for the LLM-powered agents.

Mirrors the optional-integration pattern already used for Reddit (reddit_sentiment.py)
and FMP (fmp_fetcher.py): missing credentials mean the feature no-ops with a logged
warning, not a crash — a scan should never fail just because an optional agent's
API key isn't configured.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# claude-opus-5 by default: this skill's guidance is to never silently downgrade
# for cost — that's the user's call, not an automatic optimization. Confirmed with
# the user (2026-08-04) for both the Fundamentals Auditor and Catalyst Sentiment agents.
MODEL = "claude-opus-5"


def get_client():
    """Return an anthropic.Anthropic client, or None if ANTHROPIC_API_KEY isn't set.

    Callers should treat None as "agent unavailable this run" and no-op, same as
    RedditSentimentFetcher.available / EnhancedFundamentalsFetcher.fmp_available.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning(
            "ANTHROPIC_API_KEY not set — LLM agent disabled for this run. "
            "Set it in .env to enable."
        )
        return None

    import anthropic

    return anthropic.Anthropic(api_key=api_key)
