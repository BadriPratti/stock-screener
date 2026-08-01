"""SEC Form 4 insider-buying tracker.

Uses SEC EDGAR's fully public, free API — no account, no API key, no OAuth app.
SEC's only requirement is a descriptive User-Agent header identifying the requester
(their fair-use policy, not a credential). Rate-limited client-side to stay well
under SEC's 10 req/sec cap.

Only "P" (open market or private purchase) transactions count as a bullish signal.
Most Form 4 filings are routine compensation events (RSU vesting = "M", tax
withholding = "F", grants = "A") that carry no real signal — those are filtered out.
Insider selling ("S") is common for mundane reasons (diversification, taxes) and is
far less predictive than buying, so it's tracked for context but not scored.
"""

import logging
import os
import pickle
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# SEC's fair-access policy requires a descriptive User-Agent (name + contact), and
# their bot-detection specifically rejects "AppName/1.0 (description)"-shaped strings
# (looks like a generic bot signature) — a plain "name email" string works reliably.
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "stock-screener-personal-use contact@example.com")
REQUEST_DELAY = 0.15  # stays well under SEC's 10 req/sec limit
CIK_MAP_CACHE_DAYS = 7


class InsiderTradingFetcher:
    """Fetch and analyze SEC Form 4 insider-purchase filings for a ticker."""

    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": SEC_USER_AGENT})
        self._cik_map: Optional[Dict[str, str]] = None
        self._last_request_time = 0.0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()

    def _get(self, url: str) -> Optional[requests.Response]:
        self._rate_limit()
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.debug(f"SEC request failed for {url}: {e}")
            return None

    def _load_cik_map(self) -> Dict[str, str]:
        """Ticker -> zero-padded 10-digit CIK, cached to disk for a week."""
        if self._cik_map is not None:
            return self._cik_map

        cache_file = self.cache_dir / "sec_ticker_cik_map.pkl"
        if cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if age < timedelta(days=CIK_MAP_CACHE_DAYS):
                with open(cache_file, "rb") as f:
                    self._cik_map = pickle.load(f)
                    return self._cik_map

        resp = self._get("https://www.sec.gov/files/company_tickers.json")
        if resp is None:
            self._cik_map = {}
            return self._cik_map

        data = resp.json()
        cik_map = {
            entry["ticker"].upper(): f"{entry['cik_str']:010d}"
            for entry in data.values()
        }
        with open(cache_file, "wb") as f:
            pickle.dump(cik_map, f)
        self._cik_map = cik_map
        return cik_map

    def _get_cik(self, ticker: str) -> Optional[str]:
        return self._load_cik_map().get(ticker.upper())

    def _recent_form4_filing_urls(self, cik: str, days: int, limit: int) -> List[Dict]:
        """Return [{accession, filing_date, index_url}] for recent Form 4s."""
        url = (
            "https://www.sec.gov/cgi-bin/browse-edgar"
            f"?action=getcompany&CIK={cik}&type=4&dateb=&owner=include"
            f"&count={limit}&output=atom"
        )
        resp = self._get(url)
        if resp is None:
            return []

        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError:
            return []

        ns = {"a": "http://www.w3.org/2005/Atom"}
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date()
        filings = []
        for entry in root.findall("a:entry", ns):
            content = entry.find("a:content", ns)
            if content is None:
                continue
            filing_date_el = content.find("a:filing-date", ns)
            href_el = content.find("a:filing-href", ns)
            if filing_date_el is None or href_el is None:
                continue
            try:
                filing_date = datetime.strptime(filing_date_el.text, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
            if filing_date < cutoff:
                continue
            filings.append({"filing_date": filing_date_el.text, "index_url": href_el.text})

        return filings

    def _find_xml_doc_url(self, index_url: str) -> Optional[str]:
        """Use SEC's structured JSON directory index to find the Form 4 XML doc.

        (The HTML directory listing page renders as a single minified line with
        multiple hrefs per line, so naive HTML link-scraping picks up the wrong
        link — the JSON index avoids that entirely.)
        """
        directory_url = index_url.rsplit("/", 1)[0] + "/"
        resp = self._get(directory_url + "index.json")
        if resp is None:
            return None
        try:
            items = resp.json().get("directory", {}).get("item", [])
        except ValueError:
            return None

        for item in items:
            name = item.get("name", "")
            if name.lower().endswith(".xml") and "form4" in name.lower():
                return directory_url + name
        return None

    def _parse_form4_purchases(self, xml_text: str, filing_url: str) -> List[Dict]:
        """Extract only open-market purchase ("P") transactions from a Form 4."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        owner_el = root.find("reportingOwner")
        owner_name, is_officer, officer_title, is_director = None, False, None, False
        if owner_el is not None:
            name_el = owner_el.find("reportingOwnerId/rptOwnerName")
            owner_name = name_el.text if name_el is not None else None
            rel_el = owner_el.find("reportingOwnerRelationship")
            if rel_el is not None:
                is_officer = (rel_el.findtext("isOfficer") or "").lower() == "true"
                officer_title = rel_el.findtext("officerTitle")
                is_director = (rel_el.findtext("isDirector") or "").lower() == "true"

        purchases = []
        for txn in root.findall(".//nonDerivativeTransaction"):
            code = txn.findtext("transactionCoding/transactionCode")
            if code != "P":
                continue

            shares_text = txn.findtext("transactionAmounts/transactionShares/value")
            price_text = txn.findtext("transactionAmounts/transactionPricePerShare/value")
            date_text = txn.findtext("transactionDate/value")

            try:
                shares = float(shares_text) if shares_text else 0.0
                price = float(price_text) if price_text else 0.0
            except ValueError:
                shares, price = 0.0, 0.0

            purchases.append({
                "owner_name": owner_name,
                "is_officer": is_officer,
                "officer_title": officer_title,
                "is_director": is_director,
                "shares": shares,
                "price": price,
                "value": shares * price,
                "date": date_text,
                "filing_url": filing_url,
            })

        return purchases

    def get_insider_signal(self, ticker: str, days: int = 90, max_filings: int = 15) -> Dict:
        """Aggregate recent open-market insider purchases for a ticker.

        Returns a dict that's always safe to use even on total failure:
            {'purchases_90d': int, 'total_buy_value': float, 'buyers': [...], 'top_buy_url': str|None}
        """
        empty = {"purchases_90d": 0, "total_buy_value": 0.0, "buyers": [], "top_buy_url": None}

        cik = self._get_cik(ticker)
        if not cik:
            return empty

        filings = self._recent_form4_filing_urls(cik, days=days, limit=max_filings)
        all_purchases = []
        for filing in filings:
            xml_url = self._find_xml_doc_url(filing["index_url"])
            if not xml_url:
                continue
            resp = self._get(xml_url)
            if resp is None:
                continue
            all_purchases.extend(self._parse_form4_purchases(resp.text, filing["index_url"]))

        if not all_purchases:
            return empty

        all_purchases.sort(key=lambda p: p["value"], reverse=True)
        total_value = sum(p["value"] for p in all_purchases)

        return {
            "purchases_90d": len(all_purchases),
            "total_buy_value": total_value,
            "buyers": all_purchases[:5],
            "top_buy_url": all_purchases[0]["filing_url"],
        }
