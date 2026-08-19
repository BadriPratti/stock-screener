"""News & Catalyst Sentiment — Part 4. For each Phase 2 candidate, reads recent news
headlines (yfinance) and SEC Form 4 insider-buying data already available in the
pipeline (insider_trading.py) and asks Claude to classify "why is this stock moving"
into a catalyst type, scored numerically (-5 to +5) as a new scoring component — not
just a text bullet.

Never modifies src/screening/signal_engine.py. Every score is logged to
data/catalyst_sentiment/ for manual review and eventual backtesting via
walk_forward_backtest.py.

Note on "press releases": Yahoo's news feed already aggregates company press releases
alongside third-party articles, so no separate press-release-only source is wired in
here — a genuinely distinct source would need a new paid API, out of scope for now.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal

import yfinance as yf
from pydantic import BaseModel, Field

from src.agents.llm_client import MODEL, get_client
from src.data.insider_trading import InsiderTradingFetcher

logger = logging.getLogger(__name__)

MAX_HEADLINES = 8
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "catalyst_sentiment"


class CatalystClassification(BaseModel):
    catalyst_type: Literal[
        "earnings_beat", "earnings_miss", "guidance_raise", "guidance_cut",
        "insider_buying", "insider_selling", "analyst_upgrade", "analyst_downgrade",
        "merger_acquisition", "product_news", "regulatory", "sector_momentum",
        "pure_momentum_no_catalyst", "other",
    ]
    catalyst_score: int = Field(
        ge=-5, le=5,
        description="-5 (strongly bearish catalyst) to +5 (strongly bullish catalyst); 0 if no real catalyst",
    )
    confidence: Literal["low", "medium", "high"]
    summary: str = Field(description="1-2 sentence plain-English explanation of why the stock is moving")


CATALYST_SYSTEM_PROMPT = """You classify WHY a stock is moving right now, using the recent \
news headlines and SEC Form 4 insider-buying data provided. Pick the single best-fitting \
catalyst_type and score how bullish or bearish that catalyst is on a -5 (strongly bearish) to \
+5 (strongly bullish) scale, where 0 means no real catalyst (pure price/volume momentum with \
no identifiable news driver).

Be skeptical of hype-y headlines with no substance. If the headlines are generic or stale and \
there's no insider buying signal, classify as 'pure_momentum_no_catalyst' with a score near 0 \
rather than inventing a catalyst."""


def _fetch_headlines(ticker: str, limit: int = MAX_HEADLINES) -> List[Dict]:
    """Recent news headlines via yfinance. Never raises."""
    try:
        news = yf.Ticker(ticker).news or []
    except Exception as e:
        logger.debug(f"News fetch failed for {ticker}: {e}")
        return []

    headlines = []
    for item in news[:limit]:
        content = item.get("content", {})
        title = content.get("title")
        publisher = (content.get("provider") or {}).get("displayName")
        pub_date = content.get("pubDate")
        if title:
            headlines.append({"title": title, "publisher": publisher, "pub_date": pub_date})
    return headlines


class CatalystSentimentAgent:
    """Classifies why a stock is moving using news + insider-buying data + Claude."""

    def __init__(self):
        self.client = get_client()
        self.insider_fetcher = InsiderTradingFetcher()

    @property
    def available(self) -> bool:
        return self.client is not None

    def analyze(self, ticker: str) -> Dict:
        """Returns a dict always safe to use even on total failure:
            {'ticker', 'analyzed': bool, 'reason': str|None, 'headlines_used': int,
             'insider_purchases_90d': int, 'classification': dict|None}
        """
        empty = {
            "ticker": ticker, "analyzed": False, "reason": None,
            "headlines_used": 0, "insider_purchases_90d": 0, "classification": None,
        }

        if not self.available:
            return {**empty, "reason": "ANTHROPIC_API_KEY not set"}

        headlines = _fetch_headlines(ticker)
        insider_signal = self.insider_fetcher.get_insider_signal(ticker)

        if not headlines and insider_signal["purchases_90d"] == 0:
            return {**empty, "reason": "no news or insider activity found"}

        headline_text = "\n".join(
            f'- "{h["title"]}" ({h.get("publisher") or "unknown source"}, {h.get("pub_date") or "date unknown"})'
            for h in headlines
        ) or "(no recent headlines found)"

        if insider_signal["purchases_90d"] > 0:
            insider_text = (
                f"{insider_signal['purchases_90d']} open-market insider purchase(s) in the last 90 days, "
                f"totaling ${insider_signal['total_buy_value']:,.0f}."
            )
        else:
            insider_text = "No open-market insider purchases in the last 90 days."

        try:
            response = self.client.messages.parse(
                model=MODEL,
                max_tokens=1024,
                system=CATALYST_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Ticker: {ticker}\n\n"
                        f"Recent headlines:\n{headline_text}\n\n"
                        f"Insider buying (SEC Form 4): {insider_text}"
                    ),
                }],
                output_format=CatalystClassification,
            )
            classification = response.parsed_output
        except Exception as e:
            logger.warning(f"Catalyst sentiment failed for {ticker}: {e}")
            return {**empty, "reason": f"LLM call failed: {e}"}

        return {
            "ticker": ticker,
            "analyzed": True,
            "reason": None,
            "headlines_used": len(headlines),
            "insider_purchases_90d": insider_signal["purchases_90d"],
            "classification": classification.model_dump(),
        }


def analyze_candidates(tickers: List[str]) -> List[Dict]:
    """Analyze a list of tickers, saving one timestamped run to data/catalyst_sentiment/."""
    agent = CatalystSentimentAgent()
    results = []
    for ticker in tickers:
        logger.info(f"Catalyst sentiment: {ticker}...")
        results.append(agent.analyze(ticker))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {"generated": datetime.now().isoformat(), "results": results}

    (OUTPUT_DIR / f"sentiment_{timestamp}.json").write_text(json.dumps(payload, indent=2))
    (OUTPUT_DIR / "latest.json").write_text(json.dumps(payload, indent=2))

    return results
