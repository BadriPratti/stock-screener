"""Reddit ticker-mention fetcher for cross-referencing stock buzz with screener signals.

Uses PRAW (the official Reddit API wrapper) in read-only mode against PUBLIC subreddits.
Never authenticates as a user account, posts, votes, or comments — read-only API access
with an app-only OAuth token, same as any legitimate third-party Reddit client.
"""

import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

DEFAULT_SUBREDDITS = ['wallstreetbets', 'stocks', 'StockMarket', 'pennystocks']

# Common short English words/abbreviations that are also valid ticker symbols.
# A bare mention of these (no $ prefix) is almost always the word, not the stock.
COMMON_WORD_BLOCKLIST = {
    'A', 'I', 'ALL', 'ARE', 'FOR', 'ON', 'IT', 'GO', 'SO', 'OR', 'AT', 'BE',
    'DD', 'CEO', 'IPO', 'USA', 'NOW', 'NEW', 'ONE', 'CAN', 'GOOD', 'REAL',
    'PLAY', 'BIG', 'LOVE', 'NEXT', 'OPEN', 'HIGH', 'LOW', 'YOLO', 'EDIT',
    'ANY', 'THE', 'AND', 'BUT', 'NOT', 'YOU', 'SEE', 'WAY', 'DAY', 'GET',
    'FREE', 'HOLD', 'MOON', 'FUD', 'IMO', 'ATH', 'ATM', 'RIP', 'IRA', 'CEO',
    'US', 'UK', 'EU', 'OK', 'PM', 'AM', 'ETF', 'SEC', 'FDA', 'FOMO',
}

CASHTAG_RE = re.compile(r'\$([A-Z]{1,5})\b')
BARE_TICKER_RE = re.compile(r'\b([A-Z]{2,5})\b')


class RedditSentimentFetcher:
    """Read-only fetcher for stock ticker mention counts across public subreddits.

    Environment Variables:
        REDDIT_CLIENT_ID: From a Reddit "script" app at reddit.com/prefs/apps
        REDDIT_CLIENT_SECRET: Same app
        REDDIT_USER_AGENT: Optional, defaults to a descriptive string Reddit requires
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or os.getenv('REDDIT_USER_AGENT', 'stock-screener-bot/1.0 (read-only)')
        self.reddit = None

        if not PRAW_AVAILABLE:
            logger.warning("praw not installed - Reddit sentiment disabled. pip install praw")
            return

        if not self.client_id or not self.client_secret:
            logger.warning("Reddit credentials not configured (REDDIT_CLIENT_ID/SECRET) - Reddit sentiment disabled")
            return

        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )
        self.reddit.read_only = True

    @property
    def available(self) -> bool:
        return self.reddit is not None

    def fetch_mentions(
        self,
        valid_tickers: Set[str],
        subreddits: Optional[List[str]] = None,
        hours: int = 24,
        post_limit: int = 150,
    ) -> Dict[str, Dict]:
        """Scan recent post titles/bodies in the given subreddits for ticker mentions.

        Args:
            valid_tickers: Known-good ticker symbols to match against (filters noise).
            subreddits: Subreddit names without "r/". Defaults to DEFAULT_SUBREDDITS.
            hours: Only count posts newer than this many hours.
            post_limit: Max newest posts to scan per subreddit.

        Returns:
            Dict of ticker -> {'count': int, 'top_post_title': str, 'top_post_url': str},
            where the "top post" is the highest-scoring (most-upvoted) post that
            mentioned this ticker — used as the "why is this being talked about" link.
        """
        if not self.available:
            return {}

        subreddits = subreddits or DEFAULT_SUBREDDITS
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        mentions: Dict[str, Dict] = {}

        for sub_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                for post in subreddit.new(limit=post_limit):
                    post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    if post_time < cutoff:
                        break  # .new() is newest-first, safe to stop scanning this subreddit

                    text = f"{post.title} {post.selftext or ''}"
                    for ticker in self._extract_tickers(text, valid_tickers):
                        entry = mentions.setdefault(
                            ticker, {'count': 0, 'top_post_title': None, 'top_post_url': None, '_top_post_score': -1}
                        )
                        entry['count'] += 1
                        if post.score > entry['_top_post_score']:
                            entry['_top_post_score'] = post.score
                            entry['top_post_title'] = post.title
                            entry['top_post_url'] = f"https://reddit.com{post.permalink}"

            except Exception as e:
                logger.warning(f"Reddit fetch failed for r/{sub_name}: {e}")

        for entry in mentions.values():
            entry.pop('_top_post_score', None)

        return mentions

    def _extract_tickers(self, text: str, valid_tickers: Set[str]) -> Set[str]:
        """Extract likely ticker mentions from one post's text, deduped per-post."""
        found = set()

        # High confidence: $TICKER cashtags
        for match in CASHTAG_RE.findall(text):
            if match in valid_tickers:
                found.add(match)

        # Lower confidence: bare uppercase words — must be a real ticker AND not a common word
        for match in BARE_TICKER_RE.findall(text):
            if match in valid_tickers and match not in COMMON_WORD_BLOCKLIST:
                found.add(match)

        return found
