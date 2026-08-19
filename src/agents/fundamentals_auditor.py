"""Fundamentals Auditor — Part 3. For each Phase 2 candidate, pulls the company's
most recent 10-Q or 10-K from SEC EDGAR, extracts the MD&A section, and asks Claude
to flag qualitative red/green flags a pure numbers score would miss (margin
compression explained away as "one-time," guidance cuts, earnings quality issues,
etc.) — things visible in the prose but invisible to signal_engine.py's line-item math.

Never modifies src/screening/signal_engine.py. Every flag is logged to
data/fundamentals_audit/ for manual review and eventual backtesting once enough
history accumulates (that wiring is walk_forward_backtest.py's job, not this module's).
"""

import json
import logging
import os
import pickle
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Literal, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from src.agents.llm_client import MODEL, get_client

logger = logging.getLogger(__name__)

# Same fair-access User-Agent convention as insider_trading.py — SEC's bot-detection
# rejects "AppName/1.0 (description)"-shaped strings, so keep this a plain name+email.
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "stock-screener-personal-use contact@example.com")
REQUEST_DELAY = 0.15
CIK_MAP_CACHE_DAYS = 7
MAX_FILING_CHARS = 60000  # ~15-20K tokens — controls cost regardless of model choice

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "fundamentals_audit"


class FundamentalFlag(BaseModel):
    flag: str = Field(description="Short label, e.g. 'Margin compression from one-time restructuring costs'")
    category: Literal[
        "margin", "revenue_quality", "guidance", "balance_sheet",
        "cash_flow", "earnings_quality", "customer_concentration", "other",
    ]
    severity: Literal["minor", "moderate", "major"]
    evidence: str = Field(description="The specific language or figure from the filing that supports this flag")


class FundamentalsAudit(BaseModel):
    red_flags: List[FundamentalFlag]
    green_flags: List[FundamentalFlag]
    overall_assessment: Literal["red_flags_outweigh", "green_flags_outweigh", "mixed", "no_notable_flags"]
    summary: str = Field(description="2-3 sentence plain-English summary of the qualitative picture")


AUDIT_SYSTEM_PROMPT = """You are a skeptical equity research analyst auditing a company's most \
recent SEC filing (10-Q or 10-K). Your job is to catch qualitative issues a pure numbers-based \
screen would miss, such as:
- Margin compression explained away as "one-time" that isn't really one-time
- Revenue growth propped up by a single large customer, acquisition, or one-time item
- Guidance cuts, softened language, or hedged forward-looking statements
- Earnings quality concerns (divergence between GAAP and non-GAAP, unusual adjustments)
- Balance sheet or cash flow deterioration not obvious from headline numbers

Also note genuine green flags: real margin expansion, clean guidance raises, strengthening \
balance sheet, diversifying revenue.

Base every flag ONLY on the filing text provided. If the filing is thin or you find nothing \
notable, use overall_assessment='no_notable_flags' rather than inventing flags."""


class FundamentalsAuditor:
    """Pulls a ticker's most recent 10-Q/10-K from SEC EDGAR and audits it with Claude."""

    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": SEC_USER_AGENT})
        self._cik_map: Optional[Dict[str, str]] = None
        self._last_request_time = 0.0
        self.client = get_client()

    @property
    def available(self) -> bool:
        return self.client is not None

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()

    def _get(self, url: str) -> Optional[requests.Response]:
        self._rate_limit()
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.debug(f"SEC request failed for {url}: {e}")
            return None

    def _load_cik_map(self) -> Dict[str, str]:
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

    def _recent_10q_10k_filings(self, cik: str, count: int = 40) -> List[Dict]:
        """Recent 10-Q/10-K filings (form type, date, index page URL), newest first."""
        url = (
            "https://www.sec.gov/cgi-bin/browse-edgar"
            f"?action=getcompany&CIK={cik}&type=10-&dateb=&owner=include"
            f"&count={count}&output=atom"
        )
        resp = self._get(url)
        if resp is None:
            return []

        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError:
            return []

        ns = {"a": "http://www.w3.org/2005/Atom"}
        filings = []
        for entry in root.findall("a:entry", ns):
            category = entry.find("a:category", ns)
            form_type = category.get("term") if category is not None else None
            if form_type not in ("10-Q", "10-K"):
                continue
            content = entry.find("a:content", ns)
            if content is None:
                continue
            href_el = content.find("a:filing-href", ns)
            date_el = content.find("a:filing-date", ns)
            if href_el is None or date_el is None:
                continue
            filings.append({
                "form_type": form_type,
                "filing_date": date_el.text,
                "index_url": href_el.text,
            })
        return filings

    def _latest_filing_index_url(self, cik: str) -> Optional[Dict]:
        """Most recent 10-Q or 10-K filing: form type, date, and index page URL."""
        filings = self._recent_10q_10k_filings(cik, count=10)
        return filings[0] if filings else None

    def _filing_index_url_asof(self, cik: str, as_of_date) -> Optional[Dict]:
        """Most recent 10-Q/10-K filed strictly BEFORE as_of_date — the filing that
        would actually have been public knowledge as of a historical trade's entry
        date. This is what makes a "backtest" of this agent honest rather than
        look-ahead-biased; unlike news (no historical archive), SEC filings carry
        real filing dates we can filter on."""
        as_of_str = as_of_date.isoformat() if hasattr(as_of_date, "isoformat") else str(as_of_date)
        filings = self._recent_10q_10k_filings(cik, count=40)
        eligible = [f for f in filings if f["filing_date"] < as_of_str]
        return eligible[0] if eligible else None

    def _find_primary_doc_url(self, index_url: str) -> Optional[str]:
        """Largest .htm in the filing directory is reliably the primary document —
        exhibits and press-release attachments are consistently much smaller. Same
        SEC structured JSON directory index trick as insider_trading.py uses for
        Form 4 XML (the HTML listing renders as one unparseable line)."""
        directory_url = index_url.rsplit("/", 1)[0] + "/"
        resp = self._get(directory_url + "index.json")
        if resp is None:
            return None
        try:
            items = resp.json().get("directory", {}).get("item", [])
        except ValueError:
            return None

        htm_items = [i for i in items if i.get("name", "").lower().endswith(".htm")]
        if not htm_items:
            return None
        largest = max(htm_items, key=lambda i: int(i.get("size", 0) or 0))
        return directory_url + largest["name"]

    def _extract_filing_text(self, html: str) -> str:
        """Strip HTML to plain text, then bias toward the MD&A section (the part of
        a filing that actually contains qualitative narrative) if we can find it,
        falling back to the start of the document body otherwise."""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        text = "\n".join(lines)

        # The phrase "Management's Discussion and Analysis" appears once in the table
        # of contents (short line, followed by a page number) and again as the real
        # section header (followed by actual prose) — take the LAST match, since the
        # TOC entry always comes first and the real section is what we want to audit.
        lower = text.lower()
        matches = [
            m.start() for m in re.finditer(r"management.s discussion and analysis", lower)
        ]
        if matches:
            text = text[matches[-1]:]

        return text[:MAX_FILING_CHARS]

    def _audit_filing(self, ticker: str, filing: Optional[Dict], not_found_reason: str) -> Dict:
        """Shared fetch -> extract -> LLM-audit pipeline, given an already-resolved filing.

        Returns a dict that's always safe to use even on total failure:
            {'ticker', 'audited': bool, 'reason': str|None, 'filing_type': str|None,
             'filing_date': str|None, 'audit': FundamentalsAudit-shaped dict|None}
        """
        empty = {
            "ticker": ticker, "audited": False, "reason": None,
            "filing_type": None, "filing_date": None, "audit": None,
        }

        if not self.available:
            return {**empty, "reason": "ANTHROPIC_API_KEY not set"}

        if not filing:
            return {**empty, "reason": not_found_reason}

        doc_url = self._find_primary_doc_url(filing["index_url"])
        if not doc_url:
            return {**empty, "reason": "could not locate primary filing document"}

        resp = self._get(doc_url)
        if resp is None:
            return {**empty, "reason": "failed to fetch filing document"}

        filing_text = self._extract_filing_text(resp.text)
        if len(filing_text) < 500:
            return {**empty, "reason": "extracted filing text too short to audit"}

        try:
            response = self.client.messages.parse(
                model=MODEL,
                max_tokens=8192,
                system=AUDIT_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Ticker: {ticker}\n"
                        f"Filing: {filing['form_type']} filed {filing['filing_date']}\n\n"
                        f"--- FILING TEXT (MD&A-biased excerpt) ---\n{filing_text}"
                    ),
                }],
                output_format=FundamentalsAudit,
            )
            audit_result = response.parsed_output
        except Exception as e:
            logger.warning(f"Fundamentals audit failed for {ticker}: {e}")
            return {**empty, "reason": f"LLM call failed: {e}"}

        return {
            "ticker": ticker,
            "audited": True,
            "reason": None,
            "filing_type": filing["form_type"],
            "filing_date": filing["filing_date"],
            "filing_url": doc_url,
            "audit": audit_result.model_dump(),
        }

    def audit(self, ticker: str) -> Dict:
        """Audit a ticker's MOST RECENT 10-Q/10-K — for live/current scans."""
        if not self.available:
            return self._audit_filing(ticker, None, "ANTHROPIC_API_KEY not set")
        cik = self._get_cik(ticker)
        if not cik:
            return self._audit_filing(ticker, None, "ticker not found in SEC CIK map")
        filing = self._latest_filing_index_url(cik)
        return self._audit_filing(ticker, filing, "no recent 10-Q/10-K found")

    def audit_asof(self, ticker: str, as_of_date) -> Dict:
        """Audit the filing that was actually public AS OF a historical date — for
        point-in-time backtesting (walk_forward_backtest.py's --audit-fundamentals).
        as_of_date can be a date/datetime or an ISO date string."""
        if not self.available:
            return self._audit_filing(ticker, None, "ANTHROPIC_API_KEY not set")
        cik = self._get_cik(ticker)
        if not cik:
            return self._audit_filing(ticker, None, "ticker not found in SEC CIK map")
        filing = self._filing_index_url_asof(cik, as_of_date)
        return self._audit_filing(ticker, filing, "no 10-Q/10-K filed before as_of_date")


_SEVERITY_WEIGHT = {"minor": 1, "moderate": 2, "major": 3}


def flags_to_score(audit: Dict) -> float:
    """Collapse a FundamentalsAudit's red/green flags into one signed number, for
    correlating against realized returns in the walk-forward backtest — the same
    treatment as signal_engine.py's other numeric components (trend_score, etc).
    Positive = green-flag-weighted, negative = red-flag-weighted, 0 = a wash or
    no notable flags either way."""
    green = sum(_SEVERITY_WEIGHT.get(f["severity"], 0) for f in (audit.get("green_flags") or []))
    red = sum(_SEVERITY_WEIGHT.get(f["severity"], 0) for f in (audit.get("red_flags") or []))
    return float(green - red)


def audit_candidates(tickers: List[str]) -> List[Dict]:
    """Audit a list of tickers, saving one timestamped run to data/fundamentals_audit/."""
    auditor = FundamentalsAuditor()
    results = []
    for ticker in tickers:
        logger.info(f"Fundamentals audit: {ticker}...")
        results.append(auditor.audit(ticker))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {"generated": datetime.now().isoformat(), "results": results}

    (OUTPUT_DIR / f"audit_{timestamp}.json").write_text(json.dumps(payload, indent=2))
    (OUTPUT_DIR / "latest.json").write_text(json.dumps(payload, indent=2))

    return results
