"""Combine technical/fundamental buy signals with Reddit buzz and insider buying into
a ranked top-20 shortlist, with links explaining why each stock is moving.

Ranking rule: a stock must already be a qualified buy signal (passed the full
Minervini technical/fundamental screen in signal_engine.py) to be eligible here —
Reddit mentions and insider buying only re-rank and enrich within that already-
qualified pool, they never substitute for it. This module adds no new tickers.
"""

import logging
import math
from typing import Dict, List, Optional

import yfinance as yf

logger = logging.getLogger(__name__)

REDDIT_MENTION_WEIGHT = 5.0  # bonus points per log(1 + mentions); diminishing returns
INSIDER_BUY_WEIGHT = 3.0  # bonus points per log(1 + $thousands bought); diminishing returns
NEWS_ITEMS_PER_TICKER = 2


def _fetch_news_links(ticker: str, limit: int = NEWS_ITEMS_PER_TICKER) -> List[Dict]:
    """Best-effort recent news headlines for a ticker via yfinance. Never raises."""
    try:
        news = yf.Ticker(ticker).news or []
    except Exception as e:
        logger.debug(f"News fetch failed for {ticker}: {e}")
        return []

    links = []
    for item in news[:limit]:
        content = item.get('content', {})
        title = content.get('title')
        url = (
            (content.get('canonicalUrl') or {}).get('url')
            or (content.get('clickThroughUrl') or {}).get('url')
        )
        if title and url:
            links.append({'title': title, 'url': url})
    return links


def build_top20(
    buy_signals: List[Dict],
    reddit_mentions: Optional[Dict[str, Dict]] = None,
    insider_signals: Optional[Dict[str, Dict]] = None,
    limit: int = 20,
) -> List[Dict]:
    """Rank qualified buy signals by combined technical + Reddit-buzz + insider-buying score.

    News links are only fetched for the final top N (not the whole buy_signals pool),
    since each lookup is a network call — ranking happens first on score alone, then
    news links are attached to just the finalists. Reddit and insider "why" links come
    for free from data already fetched for the whole pool (needed for scoring anyway).

    Args:
        buy_signals: Already-scored, already-qualified buy signals.
        reddit_mentions: Optional {ticker: {'count', 'top_post_title', 'top_post_url'}}
            from RedditSentimentFetcher.fetch_mentions(). Missing/empty is fine —
            ranking then falls back to pure technical score.
        insider_signals: Optional {ticker: {'purchases_90d', 'total_buy_value', 'buyers',
            'top_buy_url'}} from InsiderTradingFetcher.get_insider_signal().
        limit: Max entries to return.

    Returns:
        List of signal dicts (+ combined_score, reddit_mentions_24h, insider_buy_value,
        why_links), sorted best-first, length <= limit.
    """
    reddit_mentions = reddit_mentions or {}
    insider_signals = insider_signals or {}
    ranked = []

    for signal in buy_signals:
        ticker = signal['ticker']
        reddit_info = reddit_mentions.get(ticker, {})
        mention_count = reddit_info.get('count', 0)
        reddit_boost = math.log1p(mention_count) * REDDIT_MENTION_WEIGHT

        insider_info = insider_signals.get(ticker, {})
        buy_value = insider_info.get('total_buy_value', 0)
        insider_boost = math.log1p(buy_value / 1000) * INSIDER_BUY_WEIGHT

        entry = dict(signal)
        entry['reddit_mentions_24h'] = mention_count
        entry['insider_buy_value_90d'] = buy_value
        entry['combined_score'] = round(signal['score'] + reddit_boost + insider_boost, 2)
        entry['_reddit_info'] = reddit_info
        entry['_insider_info'] = insider_info
        ranked.append(entry)

    ranked.sort(key=lambda s: s['combined_score'], reverse=True)
    top = ranked[:limit]

    for entry in top:
        reddit_info = entry.pop('_reddit_info', {})
        insider_info = entry.pop('_insider_info', {})
        why_links = []

        # Earnings risk is a WARNING, not a bullish reason — shown first, distinct label.
        earnings_risk = entry.get('earnings_risk')
        if earnings_risk and earnings_risk.get('has_upcoming_earnings'):
            why_links.append({
                'label': '⚠️ Earnings Risk',
                'title': earnings_risk['note'],
                'url': f"https://finance.yahoo.com/calendar/earnings?symbol={entry['ticker']}",
            })

        if insider_info.get('top_buy_url'):
            top_buyer = (insider_info.get('buyers') or [{}])[0]
            buyer_desc = top_buyer.get('officer_title') or ('Director' if top_buyer.get('is_director') else 'Insider')
            why_links.append({
                'label': f"Insider Buy (${entry['insider_buy_value_90d']:,.0f}/90d)",
                'title': f"{top_buyer.get('owner_name', 'Insider')} ({buyer_desc}) bought {top_buyer.get('shares', 0):.0f} shares @ ${top_buyer.get('price', 0):.2f}",
                'url': insider_info['top_buy_url'],
            })

        if reddit_info.get('top_post_url'):
            why_links.append({
                'label': f"Reddit ({entry['reddit_mentions_24h']} mentions/24h)",
                'title': reddit_info.get('top_post_title'),
                'url': reddit_info['top_post_url'],
            })

        for news_item in _fetch_news_links(entry['ticker']):
            why_links.append({'label': 'News', 'title': news_item['title'], 'url': news_item['url']})

        entry['why_links'] = why_links

    return top
