"""Email notification module for sending screening alerts.

Supports Gmail, Outlook, and custom SMTP servers with HTML email formatting.
"""

import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

FIDELITY_TRADE_URL = "https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol={ticker}"


class EmailNotifier:
    """Send screening results via email with HTML formatting.

    Supports Gmail, Outlook, and custom SMTP servers. Uses environment
    variables for configuration.

    Environment Variables:
        EMAIL_FROM: Sender email address
        EMAIL_PASSWORD: Sender email password or app-specific password
        EMAIL_TO: Recipient email address (comma-separated for multiple)
        SMTP_SERVER: SMTP server (default: smtp.gmail.com for Gmail)
        SMTP_PORT: SMTP port (default: 587)

    Example:
        >>> notifier = EmailNotifier()
        >>> notifier.send_screening_results(results_df, top_n=10)
    """

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        email_from: Optional[str] = None,
        email_password: Optional[str] = None,
        email_to: Optional[str] = None
    ) -> None:
        """Initialize the email notifier.

        Args:
            smtp_server: SMTP server address. Defaults to env EMAIL_SMTP_SERVER or smtp.gmail.com.
            smtp_port: SMTP port. Defaults to env EMAIL_SMTP_PORT or 587.
            email_from: Sender email. Defaults to env EMAIL_FROM.
            email_password: Sender password. Defaults to env EMAIL_PASSWORD.
            email_to: Recipient email(s). Defaults to env EMAIL_TO.
        """
        self.smtp_server = smtp_server or os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_from = email_from or os.getenv('EMAIL_FROM')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        self.email_to = email_to or os.getenv('EMAIL_TO')

        if not self.email_from or not self.email_password:
            logger.warning("Email credentials not configured. Set EMAIL_FROM and EMAIL_PASSWORD.")

        logger.info(f"EmailNotifier initialized (SMTP: {self.smtp_server}:{self.smtp_port})")

    def _format_html_table(self, df: pd.DataFrame) -> str:
        """Format DataFrame as HTML table with styling.

        Args:
            df: DataFrame to format.

        Returns:
            HTML string with styled table.
        """
        html = '<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">\n'

        # Header
        html += '  <thead>\n    <tr style="background-color: #2c3e50; color: white;">\n'
        for col in df.columns:
            html += f'      <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">{col}</th>\n'
        html += '    </tr>\n  </thead>\n'

        # Body
        html += '  <tbody>\n'
        for idx, row in df.iterrows():
            bg_color = '#f9f9f9' if idx % 2 == 0 else 'white'
            html += f'    <tr style="background-color: {bg_color};">\n'

            for col in df.columns:
                value = row[col]

                # Format based on column type
                if pd.isna(value):
                    display = 'N/A'
                elif col in ['buy_signal', 'value_score', 'support_score']:
                    # Color code scores
                    val = float(value)
                    if val >= 80:
                        color = '#27ae60'  # Green
                    elif val >= 65:
                        color = '#f39c12'  # Orange
                    else:
                        color = '#95a5a6'  # Gray
                    display = f'<span style="color: {color}; font-weight: bold;">{val:.1f}</span>'
                elif col == 'current_price':
                    display = f'${float(value):.2f}'
                elif col == 'rsi':
                    val = float(value)
                    if val < 30:
                        color = '#e74c3c'  # Red (oversold)
                    elif val < 70:
                        color = '#000'  # Black
                    else:
                        color = '#c0392b'  # Dark red (overbought)
                    display = f'<span style="color: {color};">{val:.1f}</span>'
                elif isinstance(value, (int, float)):
                    display = f'{value:.2f}'
                else:
                    display = str(value)

                html += f'      <td style="padding: 10px; border: 1px solid #ddd;">{display}</td>\n'

            html += '    </tr>\n'

        html += '  </tbody>\n</table>'
        return html

    def _create_html_email(
        self,
        results: pd.DataFrame,
        top_n: int = 10,
        subject_prefix: str = "[Stock Screener]"
    ) -> str:
        """Create HTML email body with screening results.

        Args:
            results: DataFrame with screening results.
            top_n: Number of top candidates to include.
            subject_prefix: Prefix for email subject line.

        Returns:
            HTML email body as string.
        """
        today = datetime.now().strftime('%B %d, %Y')
        total_candidates = len(results)

        # Get top candidates
        top_results = results.head(top_n)

        # Select columns for email
        email_cols = [
            'ticker', 'buy_signal', 'value_score', 'support_score',
            'current_price', 'rsi', 'pe_ratio', 'pb_ratio'
        ]
        display_df = top_results[email_cols].copy()

        # Rename columns for display
        display_df.columns = [
            'Ticker', 'Buy Signal', 'Value', 'Support',
            'Price', 'RSI', 'P/E', 'P/B'
        ]

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }}
        .legend {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            font-size: 12px;
            color: #666;
        }}
        .signal-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }}
        .strong-buy {{ background-color: #d4edda; color: #155724; }}
        .buy {{ background-color: #fff3cd; color: #856404; }}
        .consider {{ background-color: #d1ecf1; color: #0c5460; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Daily Stock Screening Results</h1>
        <p style="margin: 10px 0 0 0; font-size: 16px;">{today}</p>
    </div>

    <div class="summary">
        <h2 style="margin-top: 0;">Summary</h2>
        <p><strong>{total_candidates}</strong> stocks screened today. Showing top <strong>{len(top_results)}</strong> candidates.</p>
        <p>
            <span class="signal-badge strong-buy">🔥 STRONG BUY (80+)</span>
            <span class="signal-badge buy">✅ BUY (65-79)</span>
            <span class="signal-badge consider">⚡ CONSIDER (50-64)</span>
        </p>
    </div>

    <h2>Top {len(top_results)} Candidates</h2>

    {self._format_html_table(display_df)}

    <div class="legend">
        <h3 style="margin-top: 0;">📈 What These Scores Mean</h3>
        <ul style="margin: 10px 0;">
            <li><strong>Buy Signal:</strong> Combined score (70+ is actionable)</li>
            <li><strong>Value Score:</strong> Fundamental valuation (80+ is excellent)</li>
            <li><strong>Support Score:</strong> Technical setup (80+ is ready to buy)</li>
            <li><strong>RSI:</strong> <30 = Oversold (buy opportunity), >70 = Overbought</li>
        </ul>
    </div>

    <div class="footer">
        <p><strong>Automated Stock Screener</strong></p>
        <p>This email was automatically generated by your stock screening system.</p>
        <p>⚠️ This is not financial advice. Always do your own research before investing.</p>
    </div>
</body>
</html>
"""
        return html

    def send_notification(self, subject: str, message: str) -> bool:
        """Send a short plain-text status notification (e.g. "scan started").

        Lighter-weight than send_scan_report — no HTML, no signal tables, just a
        quick heads-up. Fails silently (logs + returns False) if unconfigured,
        same as every other notifier method — never raises into the caller.

        Args:
            subject: Email subject line.
            message: Plain-text body.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.email_from or not self.email_password or not self.email_to:
            logger.warning(f"Email not configured - skipping notification: {subject}")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                recipients = [r.strip() for r in self.email_to.split(',')]
                server.sendmail(self.email_from, recipients, msg.as_string())

            logger.info(f"✓ Notification email sent: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")
            return False

    def send_screening_results(
        self,
        results: pd.DataFrame,
        top_n: int = 10,
        subject_prefix: str = "[Stock Screener]"
    ) -> bool:
        """Send screening results via email.

        Args:
            results: DataFrame with screening results (from screen_candidates).
            top_n: Number of top candidates to include in email.
            subject_prefix: Prefix for email subject line.

        Returns:
            True if email sent successfully, False otherwise.

        Example:
            >>> notifier = EmailNotifier()
            >>> results = screen_candidates(db, tickers)
            >>> notifier.send_screening_results(results, top_n=10)
        """
        if not self.email_from or not self.email_password or not self.email_to:
            logger.error("Email configuration incomplete. Check environment variables.")
            return False

        if results.empty:
            logger.warning("No screening results to send")
            return False

        try:
            # Create message
            today = datetime.now().strftime('%b %d, %Y')
            subject = f"{subject_prefix} Top {top_n} Candidates - {today}"

            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject

            # Create HTML body
            html_body = self._create_html_email(results, top_n, subject_prefix)

            # Create plain text fallback
            text_body = self._create_text_fallback(results, top_n)

            # Attach both versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)

                recipients = [r.strip() for r in self.email_to.split(',')]
                server.sendmail(self.email_from, recipients, msg.as_string())

            logger.info(f"✓ Email sent successfully to {self.email_to}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_scan_report(
        self,
        buy_signals: List[Dict],
        sell_signals: List[Dict],
        spy_analysis: Optional[Dict] = None,
        breadth: Optional[Dict] = None,
        top_n: int = 15,
        top20: Optional[List[Dict]] = None,
        fundamentals_audits: Optional[Dict[str, Dict]] = None,
        catalyst_sentiments: Optional[Dict[str, Dict]] = None,
        congress_signals: Optional[Dict[str, Dict]] = None,
        shortlist: Optional[List[Dict]] = None,
    ) -> bool:
        """Send the daily optimized full-market scan results via email.

        Unlike send_screening_results (which expects a DataFrame in the older
        buy_signal/value_score/pe_ratio shape), this matches the dict shape produced
        by run_optimized_scan.py's score_buy_signal/score_sell_signal — the current
        Minervini-based scanner. Each ticker links straight to its Fidelity trade page.

        Args:
            buy_signals: List of buy signal dicts (already sorted, highest score first).
            sell_signals: List of sell signal dicts (already sorted, highest score first).
            spy_analysis: Optional SPY trend dict (phase, trend, confidence) for context.
            breadth: Optional market breadth dict.
            top_n: Number of top candidates per list to include in the email.
            top20: Optional pre-ranked pool from top20_ranker.build_top20() —
                combined technical + Reddit-buzz score, with "why it's moving" links.
            fundamentals_audits: Optional {ticker: audit-dict} from
                src.agents.fundamentals_auditor.audit_candidates() — Top 20 only.
            catalyst_sentiments: Optional {ticker: classification-dict} from
                src.agents.catalyst_sentiment.analyze_candidates() — Top 20 only.
            congress_signals: Optional {ticker: signal-dict} from
                src.agents.congress_trades.get_signals_for_candidates() — Top 20 only.
            shortlist: Optional Top 5 from src.agents.shortlist.build_shortlist() —
                the Top 20 pool actually filtered/ranked by the three agents above.
                Rendered as the primary section; top20 is shown below it for reference.

        Returns:
            True if email sent successfully, False otherwise.
        """
        if not self.email_from or not self.email_password or not self.email_to:
            logger.error("Email configuration incomplete. Check environment variables.")
            return False

        if not buy_signals and not sell_signals:
            logger.warning("No buy or sell signals to email")
            return False

        try:
            today = datetime.now().strftime('%b %d, %Y')
            subject = f"[Stock Screener] {len(buy_signals)} Buy / {len(sell_signals)} Sell - {today}"

            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject

            html_body = self._create_scan_html_email(
                buy_signals, sell_signals, spy_analysis, breadth, top_n, top20,
                fundamentals_audits, catalyst_sentiments, congress_signals, shortlist,
            )
            text_body = self._create_scan_text_fallback(
                buy_signals, sell_signals, spy_analysis, top_n, top20, shortlist,
            )

            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)

                recipients = [r.strip() for r in self.email_to.split(',')]
                server.sendmail(self.email_from, recipients, msg.as_string())

            logger.info(f"✓ Scan report email sent to {self.email_to}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send scan report email: {e}")
            return False

    def _scan_row_html(self, ticker: str, cells: List[str], bg: str) -> str:
        """Render one <tr> for the scan report table, with the ticker linked to Fidelity."""
        link = (
            f'<a href="{FIDELITY_TRADE_URL.format(ticker=ticker)}" '
            f'style="color:#1a73e8;text-decoration:none;font-weight:bold;">{ticker} ↗</a>'
        )
        row = f'    <tr style="background-color: {bg};">\n'
        row += f'      <td style="padding: 10px; border: 1px solid #ddd;">{link}</td>\n'
        for cell in cells:
            row += f'      <td style="padding: 10px; border: 1px solid #ddd;">{cell}</td>\n'
        row += '    </tr>\n'
        return row

    def _reddit_cell(self, count: Optional[int]) -> str:
        """Render a Reddit mention count with hot-ticker styling for the email table."""
        if count is None:
            return '-'
        if count == 0:
            return '0'
        if count >= 10:
            return f'<strong style="color:#e67e22;">🔥 {count}</strong>'
        return f'💬 {count}'

    def _catalyst_badge_html(self, classification: Optional[Dict]) -> str:
        """Render the Catalyst Sentiment agent's -5..+5 score as a compact colored badge."""
        if not classification:
            return ""
        score = classification.get('catalyst_score', 0)
        ctype = (classification.get('catalyst_type') or 'other').replace('_', ' ')
        if score > 0:
            color, bg = '#155724', '#d4edda'
        elif score < 0:
            color, bg = '#721c24', '#f8d7da'
        else:
            color, bg = '#555', '#eee'
        summary = classification.get('summary', '')
        return (
            f'<div style="margin-top:6px;">'
            f'<span style="background:{bg};color:{color};padding:2px 6px;border-radius:4px;'
            f'font-size:11px;font-weight:bold;">🎯 Catalyst {score:+d}: {ctype}</span>'
            f'<div style="font-size:11px;color:#666;margin-top:2px;">{summary}</div>'
            f'</div>'
        )

    def _congress_badge_html(self, signal: Optional[Dict]) -> str:
        """Render the Congress Trades agent's net buy/sell signal as a compact colored badge.

        House disclosures only (see src/agents/congress_trades.py for why).
        """
        if not signal or not signal.get('has_data'):
            return ""
        score = signal.get('score', 0)
        if score > 0:
            color, bg = '#155724', '#d4edda'
        elif score < 0:
            color, bg = '#721c24', '#f8d7da'
        else:
            color, bg = '#555', '#eee'
        summary = signal.get('summary', '')
        return (
            f'<div style="margin-top:6px;">'
            f'<span style="background:{bg};color:{color};padding:2px 6px;border-radius:4px;'
            f'font-size:11px;font-weight:bold;">🏛️ Congress {score:+.1f}</span>'
            f'<div style="font-size:11px;color:#666;margin-top:2px;">{summary}</div>'
            f'</div>'
        )

    def _fundamentals_flags_html(self, audit: Optional[Dict]) -> str:
        """Render the Fundamentals Auditor agent's top red/green flags, compact."""
        if not audit:
            return ""
        red = audit.get('red_flags') or []
        green = audit.get('green_flags') or []
        parts = []
        if red:
            more = f' (+{len(red) - 1} more)' if len(red) > 1 else ''
            parts.append(
                f'<div style="font-size:11px;color:#c0392b;margin-top:3px;">🔴 {red[0]["flag"]}{more}</div>'
            )
        if green:
            more = f' (+{len(green) - 1} more)' if len(green) > 1 else ''
            parts.append(
                f'<div style="font-size:11px;color:#27ae60;margin-top:2px;">🟢 {green[0]["flag"]}{more}</div>'
            )
        return "".join(parts)

    def _create_shortlist_html(
        self,
        shortlist: List[Dict],
        fundamentals_audits: Optional[Dict[str, Dict]] = None,
        catalyst_sentiments: Optional[Dict[str, Dict]] = None,
        congress_signals: Optional[Dict[str, Dict]] = None,
    ) -> str:
        """Render the Top 5 shortlist — the Top 20 pool actually filtered/ranked by the
        three agents (src/agents/shortlist.py), not just labeled. This is the primary,
        prominent section; the full Top 20 pool is shown below it for reference.
        """
        if not shortlist:
            return ""

        fundamentals_audits = fundamentals_audits or {}
        catalyst_sentiments = catalyst_sentiments or {}
        congress_signals = congress_signals or {}

        cards = ""
        for i, s in enumerate(shortlist, 1):
            ticker = s['ticker']
            badges = self._catalyst_badge_html(catalyst_sentiments.get(ticker))
            badges += self._congress_badge_html(congress_signals.get(ticker))
            badges += self._fundamentals_flags_html(fundamentals_audits.get(ticker))
            if not s.get('passed_filters', True):
                reasons = '; '.join(s.get('drop_reasons') or []) or 'below filter bar'
                badges += (
                    f'<div style="font-size:11px;color:#8a6d3b;margin-top:4px;">'
                    f"⚠️ Backfilled — didn't clear filters: {reasons}</div>"
                )
            if not badges:
                badges = '<span style="font-size:11px;color:#999;">No agent data</span>'

            cards += f"""
    <tr style="background-color: {'#f9f9f9' if i % 2 == 0 else 'white'};">
      <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">#{i}</td>
      <td style="padding:10px;border:1px solid #ddd;">
        <a href="{FIDELITY_TRADE_URL.format(ticker=ticker)}" style="color:#1a73e8;text-decoration:none;font-weight:bold;" target="_blank">{ticker} ↗</a>
      </td>
      <td style="padding:10px;border:1px solid #ddd;">{s.get('composite_score', '-')}</td>
      <td style="padding:10px;border:1px solid #ddd;">{s.get('combined_score', s.get('score', '-'))}</td>
      <td style="padding:10px;border:1px solid #ddd;">{badges}</td>
    </tr>"""

        return f"""
    <h2 style="color:#764ba2;">🎯 Top 5 — Filtered Shortlist</h2>
    <p style="color:#666;font-size:13px;margin-top:-8px;">
        Ranked from the Top 20 pool below by composite score = base score + Catalyst
        Sentiment×2 + Congress Trades×3. Candidates where fundamentals red flags outweigh
        green, or Catalyst Sentiment reads a clear negative catalyst (≤ -2), are dropped —
        only backfilled (⚠️ flagged) if fewer than 5 survive.
    </p>
    <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
      <thead>
        <tr style="background-color: #764ba2; color: white;">
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">#</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Ticker</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Composite</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Base Score</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Agent Signals</th>
        </tr>
      </thead>
      <tbody>{cards}</tbody>
    </table>"""

    def _create_top20_html(
        self,
        top20: List[Dict],
        fundamentals_audits: Optional[Dict[str, Dict]] = None,
        catalyst_sentiments: Optional[Dict[str, Dict]] = None,
        congress_signals: Optional[Dict[str, Dict]] = None,
    ) -> str:
        """Render the full Top 20 candidate pool the Top 5 shortlist above was drawn from.

        fundamentals_audits / catalyst_sentiments / congress_signals are optional
        {ticker: agent-result-dict} maps from src/agents/ — shown here for reference;
        they only actually change ranking in the Top 5 shortlist above, not this pool.
        """
        if not top20:
            return ""

        fundamentals_audits = fundamentals_audits or {}
        catalyst_sentiments = catalyst_sentiments or {}
        congress_signals = congress_signals or {}

        cards = ""
        for i, s in enumerate(top20, 1):
            links_html = ""
            for link in (s.get('why_links') or [])[:3]:
                title = (link.get('title') or link['label'])[:70]
                links_html += (
                    f'<a href="{link["url"]}" style="display:block;font-size:11px;color:#3b82f6;'
                    f'text-decoration:none;margin-top:3px;" target="_blank">'
                    f'🔗 {link["label"]}: {title}</a>'
                )
            if not links_html:
                links_html = '<span style="font-size:11px;color:#999;">No linked source yet</span>'

            links_html += self._catalyst_badge_html(catalyst_sentiments.get(s['ticker']))
            links_html += self._congress_badge_html(congress_signals.get(s['ticker']))
            links_html += self._fundamentals_flags_html(fundamentals_audits.get(s['ticker']))

            cards += f"""
    <tr style="background-color: {'#f9f9f9' if i % 2 == 0 else 'white'};">
      <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">#{i}</td>
      <td style="padding:10px;border:1px solid #ddd;">
        <a href="{FIDELITY_TRADE_URL.format(ticker=s['ticker'])}" style="color:#1a73e8;text-decoration:none;font-weight:bold;" target="_blank">{s['ticker']} ↗</a>
      </td>
      <td style="padding:10px;border:1px solid #ddd;">{s.get('combined_score', s.get('score', '-'))}</td>
      <td style="padding:10px;border:1px solid #ddd;">{self._reddit_cell(s.get('reddit_mentions_24h'))}</td>
      <td style="padding:10px;border:1px solid #ddd;">{links_html}</td>
    </tr>"""

        return f"""
    <h2 style="color:#999;font-size:18px;">Full Candidate Pool (Top 20)</h2>
    <p style="color:#666;font-size:13px;margin-top:-8px;">
        Technical/fundamental score first, re-ranked by Reddit buzz — the Top 5 shortlist
        above was filtered and ranked from this pool. Shown for reference; badges here
        don't re-rank this list, only the Top 5 above.
    </p>
    <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
      <thead>
        <tr style="background-color: #764ba2; color: white;">
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">#</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Ticker</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Combined Score</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Reddit</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Why it's moving</th>
        </tr>
      </thead>
      <tbody>{cards}</tbody>
    </table>"""

    def _create_scan_html_email(
        self,
        buy_signals: List[Dict],
        sell_signals: List[Dict],
        spy_analysis: Optional[Dict],
        breadth: Optional[Dict],
        top_n: int,
        top20: Optional[List[Dict]] = None,
        fundamentals_audits: Optional[Dict[str, Dict]] = None,
        catalyst_sentiments: Optional[Dict[str, Dict]] = None,
        congress_signals: Optional[Dict[str, Dict]] = None,
        shortlist: Optional[List[Dict]] = None,
    ) -> str:
        """Build the HTML body for a Minervini-scan report email."""
        today = datetime.now().strftime('%B %d, %Y')

        regime_html = ""
        if spy_analysis:
            regime_html = f"""
    <div class="summary">
        <h2 style="margin-top: 0;">Market Regime</h2>
        <p><strong>SPY:</strong> Phase {spy_analysis.get('phase', '?')} ({spy_analysis.get('trend', 'Unknown')})
           at ${spy_analysis.get('current_price', 0):.2f} · Confidence {spy_analysis.get('confidence', 0)}%</p>
        {f"<p><strong>Breadth:</strong> {breadth.get('phase2_pct', 0):.1f}% of stocks in Phase 2 (uptrend)</p>" if breadth else ""}
    </div>"""

        shortlist_html = self._create_shortlist_html(
            shortlist, fundamentals_audits, catalyst_sentiments, congress_signals
        ) if shortlist else ""
        top20_html = self._create_top20_html(
            top20, fundamentals_audits, catalyst_sentiments, congress_signals
        ) if top20 else ""

        buy_rows = ""
        for i, s in enumerate(buy_signals[:top_n]):
            details = s.get('details', {})
            rs_slope = details.get('rs_slope')
            buy_rows += self._scan_row_html(
                s['ticker'],
                [
                    f"<strong>{s['score']}</strong>/125",
                    s.get('entry_quality', '-'),
                    f"${s['stop_loss']:.2f}" if s.get('stop_loss') else '-',
                    f"{s['risk_reward_ratio']:.1f}:1" if s.get('risk_reward_ratio') else '-',
                    f"{rs_slope:.2f}" if rs_slope is not None else '-',
                    self._reddit_cell(s.get('reddit_mentions_24h')),
                    (s.get('reasons') or ['-'])[0],
                ],
                '#f9f9f9' if i % 2 == 0 else 'white',
            )
        buy_table = f"""
    <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
      <thead>
        <tr style="background-color: #27ae60; color: white;">
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Ticker</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Score</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Entry</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Stop Loss</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">R:R</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">RS</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Reddit</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Top Reason</th>
        </tr>
      </thead>
      <tbody>{buy_rows if buy_rows else '<tr><td colspan="8" style="padding:12px;text-align:center;color:#888;">No buy signals today</td></tr>'}</tbody>
    </table>"""

        sell_rows = ""
        for i, s in enumerate(sell_signals[:top_n]):
            sell_rows += self._scan_row_html(
                s['ticker'],
                [
                    f"<strong>{s['score']}</strong>/110",
                    (s.get('severity', '-') or '-').upper(),
                    f"${s['breakdown_level']:.2f}" if s.get('breakdown_level') else '-',
                    self._reddit_cell(s.get('reddit_mentions_24h')),
                    (s.get('reasons') or ['-'])[0],
                ],
                '#f9f9f9' if i % 2 == 0 else 'white',
            )
        sell_table = f"""
    <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
      <thead>
        <tr style="background-color: #e74c3c; color: white;">
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Ticker</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Score</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Severity</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Breakdown</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Reddit</th>
          <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Top Reason</th>
        </tr>
      </thead>
      <tbody>{sell_rows if sell_rows else '<tr><td colspan="6" style="padding:12px;text-align:center;color:#888;">No sell signals today</td></tr>'}</tbody>
    </table>"""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 26px; }}
        .summary {{ background-color: #f8f9fa; padding: 16px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Daily Stock Screener</h1>
        <p style="margin: 10px 0 0 0; font-size: 15px;">{today}</p>
    </div>
    {regime_html}
    {shortlist_html}
    {top20_html}
    <h2 style="color:#27ae60;">🟢 Buy Signals ({len(buy_signals)})</h2>
    {buy_table}
    <h2 style="color:#e74c3c; margin-top:30px;">🔴 Sell Signals ({len(sell_signals)})</h2>
    {sell_table}
    <div class="footer">
        <p><strong>Automated Stock Screener</strong> — tap any ticker to open its Fidelity trade page. You still decide and execute every trade yourself.</p>
        <p>⚠️ This is not financial advice. Always do your own research before investing.</p>
    </div>
</body>
</html>
"""

    def _create_scan_text_fallback(
        self,
        buy_signals: List[Dict],
        sell_signals: List[Dict],
        spy_analysis: Optional[Dict],
        top_n: int,
        top20: Optional[List[Dict]] = None,
        shortlist: Optional[List[Dict]] = None,
    ) -> str:
        """Plain-text fallback for the scan report email."""
        today = datetime.now().strftime('%B %d, %Y')
        text = f"DAILY STOCK SCREENER - {today}\n" + "=" * 60 + "\n\n"

        if spy_analysis:
            text += f"SPY: Phase {spy_analysis.get('phase', '?')} ({spy_analysis.get('trend', 'Unknown')})\n\n"

        if shortlist:
            text += "TOP 5 - FILTERED SHORTLIST:\n" + "-" * 60 + "\n"
            for i, s in enumerate(shortlist, 1):
                flag = "" if s.get('passed_filters', True) else "  [BACKFILLED - didn't clear filters]"
                text += (
                    f"#{i:<3} {s['ticker']:<6} composite {s.get('composite_score', '-')}  "
                    f"base {s.get('combined_score', s.get('score', '-'))}{flag}\n"
                )
            text += "\n"

        if top20:
            text += "FULL CANDIDATE POOL (TOP 20):\n" + "-" * 60 + "\n"
            for i, s in enumerate(top20, 1):
                text += f"#{i:<3} {s['ticker']:<6} combined {s.get('combined_score', '-')}  reddit {s.get('reddit_mentions_24h', 0)}\n"
                for link in (s.get('why_links') or [])[:2]:
                    text += f"      -> {link['label']}: {link['url']}\n"
            text += "\n"

        text += f"BUY SIGNALS ({len(buy_signals)}):\n" + "-" * 60 + "\n"
        if buy_signals:
            for s in buy_signals[:top_n]:
                reddit = s.get('reddit_mentions_24h')
                text += (
                    f"{s['ticker']:<6} score {s['score']}/125  "
                    f"stop ${s.get('stop_loss', 0):.2f}  "
                    f"reddit {reddit if reddit is not None else '-'}  "
                    f"{FIDELITY_TRADE_URL.format(ticker=s['ticker'])}\n"
                )
        else:
            text += "No buy signals today\n"

        text += f"\nSELL SIGNALS ({len(sell_signals)}):\n" + "-" * 60 + "\n"
        if sell_signals:
            for s in sell_signals[:top_n]:
                text += (
                    f"{s['ticker']:<6} score {s['score']}/110  "
                    f"severity {s.get('severity', '?')}  "
                    f"{FIDELITY_TRADE_URL.format(ticker=s['ticker'])}\n"
                )
        else:
            text += "No sell signals today\n"

        text += "\n" + "=" * 60 + "\n⚠️ Not financial advice. Do your own research.\n"
        return text

    def _create_text_fallback(self, results: pd.DataFrame, top_n: int) -> str:
        """Create plain text version of email for clients that don't support HTML.

        Args:
            results: DataFrame with screening results.
            top_n: Number of top candidates.

        Returns:
            Plain text email body.
        """
        today = datetime.now().strftime('%B %d, %Y')
        text = f"DAILY STOCK SCREENING RESULTS - {today}\n"
        text += "=" * 60 + "\n\n"

        text += f"Found {len(results)} candidates. Top {top_n} below:\n\n"

        # Format as table
        top_results = results.head(top_n)
        text += f"{'Ticker':<8} {'Buy Signal':<12} {'Value':<8} {'Support':<10} {'Price':<10}\n"
        text += "-" * 60 + "\n"

        for _, row in top_results.iterrows():
            text += f"{row['ticker']:<8} "
            text += f"{row['buy_signal']:<12.1f} "
            text += f"{row['value_score']:<8.1f} "
            text += f"{row['support_score']:<10.1f} "
            text += f"${row['current_price']:<9.2f}\n"

        text += "\n" + "=" * 60 + "\n"
        text += "\nLegend:\n"
        text += "- Buy Signal: Combined score (70+ is actionable)\n"
        text += "- Value Score: Fundamental valuation (80+ is excellent)\n"
        text += "- Support Score: Technical setup (80+ is ready to buy)\n"

        text += "\n" + "=" * 60 + "\n"
        text += "\n⚠️ This is not financial advice. Always do your own research.\n"

        return text

    def test_connection(self) -> bool:
        """Test SMTP connection and authentication.

        Returns:
            True if connection successful, False otherwise.

        Example:
            >>> notifier = EmailNotifier()
            >>> if notifier.test_connection():
            ...     print("Email configuration is valid!")
        """
        if not self.email_from or not self.email_password:
            logger.error("Email credentials not configured")
            return False

        try:
            logger.info(f"Testing connection to {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                logger.info("✓ SMTP connection successful")
                return True
        except smtplib.SMTPAuthenticationError:
            logger.error("✗ Authentication failed. Check email and password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"✗ SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            return False
