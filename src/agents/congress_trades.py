"""Congress Trades agent — surfaces recent US House stock-trade disclosures for a ticker.

Data source: TattooedHead/house-stock-watcher-data on GitHub — free, actively
maintained (scrapes the official House Clerk PTR disclosure filings). This is
House only: the old Senate/House Stock Watcher S3 buckets that used to serve
Senate data are dead (AccessDenied, domains no longer resolve), and the only
maintained Senate alternative found is Quiver Quant's paid API. Revisit if
Senate coverage becomes worth paying for.

No LLM call here — this is a deterministic lookup/aggregation over structured
disclosure data, not a Claude-based classifier like the other two agents.
Never modifies src/screening/signal_engine.py.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

DATA_URL = "https://raw.githubusercontent.com/TattooedHead/house-stock-watcher-data/main/data/all_transactions.json"
CACHE_PATH = Path("./data/congress_trades_cache/all_transactions.json")
CACHE_MAX_AGE_HOURS = 20
LOOKBACK_DAYS = 45  # STOCK Act filing deadline — catches trades recently made public


def _load_all_transactions() -> List[Dict]:
    """Fetch the full House disclosure dataset, cached locally for CACHE_MAX_AGE_HOURS."""
    if CACHE_PATH.exists():
        age_hours = (datetime.now().timestamp() - CACHE_PATH.stat().st_mtime) / 3600
        if age_hours < CACHE_MAX_AGE_HOURS:
            try:
                with open(CACHE_PATH) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

    try:
        resp = requests.get(DATA_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        transactions = resp.json()
    except Exception as e:
        logger.warning(f"Congress trades fetch failed: {e}")
        if CACHE_PATH.exists():
            with open(CACHE_PATH) as f:
                return json.load(f)
        return []

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, 'w') as f:
        json.dump(transactions, f)
    return transactions


def _parse_date(s: str) -> Optional[datetime]:
    try:
        return datetime.strptime(s, "%m/%d/%Y")
    except (ValueError, TypeError):
        return None


def get_congress_signal(
    ticker: str,
    all_transactions: Optional[List[Dict]] = None,
    as_of: Optional[datetime] = None,
) -> Dict:
    """Aggregate House trade disclosures made public in the LOOKBACK_DAYS before `as_of`
    (defaults to now) for one ticker.

    score is a dollar-weighted net direction capped to +-5 (same scale as
    Catalyst Sentiment): positive = net buying by members of Congress,
    negative = net selling.

    Passing `as_of` makes this genuinely point-in-time (for backtesting): only
    disclosures with disclosure_date before `as_of` are considered, so it reflects
    what would have actually been public knowledge at that historical moment —
    unlike Catalyst Sentiment, this data source does have a real historical archive.
    """
    if all_transactions is None:
        all_transactions = _load_all_transactions()

    reference = as_of or datetime.now()
    cutoff = reference - timedelta(days=LOOKBACK_DAYS)
    matches = []
    for t in all_transactions:
        if t.get('ticker') != ticker:
            continue
        d = _parse_date(t.get('disclosure_date', ''))
        if d is None or d < cutoff or d > reference:
            continue
        matches.append(t)

    if not matches:
        return {
            'ticker': ticker, 'has_data': False,
            'num_purchases': 0, 'num_sales': 0, 'net_amount_mid': 0,
            'politicians': [], 'score': 0.0,
            'summary': 'No House trade disclosures in the last 45 days.',
        }

    purchases = [t for t in matches if t.get('type') == 'Purchase']
    sales = [t for t in matches if t.get('type') == 'Sale']
    buy_value = sum(t.get('amount_mid', 0) for t in purchases)
    sell_value = sum(t.get('amount_mid', 0) for t in sales)
    net = buy_value - sell_value
    politicians = sorted({t['representative'] for t in matches if t.get('representative')})

    if net > 0:
        score = min(5.0, 1.0 + net / 50000)
    elif net < 0:
        score = max(-5.0, -1.0 + net / 50000)
    else:
        score = 0.0

    direction = "net buying" if net > 0 else ("net selling" if net < 0 else "mixed, net-flat")
    who = ', '.join(politicians[:3]) + ('...' if len(politicians) > 3 else '')
    summary = f"{len(matches)} House disclosure(s) in last {LOOKBACK_DAYS}d ({direction}): {who}"

    return {
        'ticker': ticker, 'has_data': True,
        'num_purchases': len(purchases), 'num_sales': len(sales),
        'net_amount_mid': net, 'politicians': politicians,
        'score': round(score, 2), 'summary': summary,
    }


def get_signals_for_candidates(tickers: List[str]) -> Dict[str, Dict]:
    """Batch congress-trade lookup for a candidate list, logged like the other agents."""
    all_transactions = _load_all_transactions()
    if not all_transactions:
        logger.warning("Congress trades data unavailable this run — skipping.")
        return {}

    signals = {t: get_congress_signal(t, all_transactions) for t in tickers}

    out_dir = Path("./data/congress_trades")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        'generated': datetime.now().isoformat(),
        'source': 'house-stock-watcher-data (House only, no free Senate source available)',
        'signals': signals,
    }
    with open(out_dir / f"signals_{ts}.json", 'w') as f:
        json.dump(payload, f, indent=2, default=str)
    with open(out_dir / "latest.json", 'w') as f:
        json.dump(payload, f, indent=2, default=str)

    return signals
