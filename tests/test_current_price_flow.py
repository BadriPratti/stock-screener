import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.screening.top20_ranker import build_top20
import dashboard


def test_build_top20_preserves_current_price():
    buy_signal = {
        'ticker': 'TEST',
        'score': 80,
        'current_price': 123.45,
    }

    with patch('src.screening.top20_ranker._fetch_news_links', return_value=[]):
        top20 = build_top20([buy_signal], reddit_mentions={}, insider_signals={})

    assert top20[0]['current_price'] == 123.45


def test_parse_scan_file_extracts_current_price(tmp_path):
    # Market's Buy/Sell tables read from the human-readable .txt report (via
    # parse_scan_file), a completely separate serialization path from
    # top20_latest.json/shortlist_latest.json's direct JSON dump — a value
    # present on the in-memory signal dict does not automatically appear here
    # unless save_report() (run_optimized_scan.py) also writes it into the
    # text format and this parser extracts it back out. This locks in that
    # round-trip for both buy and sell signals.
    report = (
        "################################################################################\n"
        "BUY #1: AAPL | Score: 95.0/125\n"
        "################################################################################\n"
        "Current Price: $182.50\n"
        "Phase: 2\n"
        "Entry Quality: Good\n"
        "Stop Loss: $175.00\n"
        "\n"
        "################################################################################\n"
        "SELL #1: XYZ | Score: 85.0/110\n"
        "################################################################################\n"
        "Current Price: $42.10\n"
        "Phase: 4 | Severity: CRITICAL\n"
        "Breakdown: $40.00\n"
    )
    report_file = tmp_path / "scan.txt"
    report_file.write_text(report, encoding="utf-8")

    data = dashboard.parse_scan_file(str(report_file))

    assert data['buy_signals'][0]['current_price'] == 182.50
    assert data['sell_signals'][0]['current_price'] == 42.10
