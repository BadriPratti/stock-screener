"""Reddit ticker-mention fetcher via ApeWisdom's free public API — no Reddit API
app, no credentials, no setup at all.

ApeWisdom (https://apewisdom.io) already scrapes r/wallstreetbets and other
finance subreddits and publishes ranked ticker-mention counts as a public JSON
API, updated continuously. This is the zero-setup alternative to
src/data/reddit_sentiment.py (which needs a Reddit "script" app's client_id/
secret) — same output shape, so it's a drop-in replacement at the call site.

Trade-off: you don't control which subreddits/timeframe get scraped (that's
ApeWisdom's own pipeline, not configurable per-request beyond their filter
options), and there's no official uptime/rate-limit guarantee since it's a
free community-run API, not something either of us operates.
"""

import logging
from typing import Dict, Optional, Set

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}"
MAX_PAGES = 8  # covers ApeWisdom's full ranked list (~700-800 tickers)
REQUEST_TIMEOUT = 15


class ApeWisdomSentimentFetcher:
    """Free, no-credential Reddit mention-count fetcher via apewisdom.io."""

    @property
    def available(self) -> bool:
        return True  # no credentials required

    def fetch_mentions(
        self,
        valid_tickers: Set[str],
        filter_name: str = "all-stocks",
        max_pages: int = MAX_PAGES,
    ) -> Dict[str, Dict]:
        """Fetch current Reddit mention counts for tickers in valid_tickers.

        Args:
            valid_tickers: Known-good ticker symbols to match against (filters noise).
            filter_name: ApeWisdom filter — "all-stocks", "wallstreetbets",
                "stocks", "options", etc. (their supported subreddit filters).
            max_pages: Safety cap on how many pages to walk.

        Returns:
            Dict of ticker -> {'count': int, 'top_post_title': None,
            'top_post_url': "https://apewisdom.io/stocks/<ticker>/"} — same
            shape as RedditSentimentFetcher.fetch_mentions() so callers don't
            need to branch on which source is active. top_post_title is None
            since ApeWisdom doesn't expose individual post links, only the
            aggregate mention count.
        """
        mentions: Dict[str, Dict] = {}

        for page in range(1, max_pages + 1):
            url = BASE_URL.format(filter=filter_name, page=page)
            try:
                resp = requests.get(url, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.warning(f"ApeWisdom fetch failed on page {page}: {e}")
                break

            results = data.get('results') or []
            if not results:
                break

            for row in results:
                ticker = (row.get('ticker') or '').upper()
                if ticker not in valid_tickers:
                    continue
                mentions[ticker] = {
                    'count': row.get('mentions', 0),
                    'top_post_title': None,
                    'top_post_url': f"https://apewisdom.io/stocks/{ticker}/",
                }

            if page >= data.get('pages', page):
                break

        return mentions
