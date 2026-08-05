"""Earnings-event risk warning — a fundamentally different signal from the rest of this
screener: not "is this stock trending" but "is a high-uncertainty news event imminent."

Trend-following (this screener's core methodology) cannot predict discrete jumps like
earnings beats/misses — that information doesn't exist in price/volume history before the
event. This module doesn't try to predict the DIRECTION of an earnings move; it flags WHEN
one is coming and how big the options market expects it to be, via the standard "ATM
straddle" expected-move calculation options traders use. That's a risk-sizing signal
("this could gap past your stop-loss overnight"), not a buy/sell signal.

Uses yfinance's Ticker.calendar (earnings date) and Ticker.option_chain (real market IV) —
both already a dependency, no new API key needed.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Optional

import yfinance as yf

logger = logging.getLogger(__name__)

DEFAULT_LOOKAHEAD_DAYS = 14


class EarningsRiskFetcher:
    """Flags imminent earnings events and the options-implied expected move."""

    def get_earnings_risk(self, ticker: str, lookahead_days: int = DEFAULT_LOOKAHEAD_DAYS) -> Dict:
        """Check whether a ticker has earnings coming up soon, and how big a move the
        options market is pricing in around that date.

        Returns a dict that's always safe to use even on total failure:
            {'has_upcoming_earnings': False, 'earnings_date': None, 'days_until': None,
             'expected_move_pct': None, 'note': str}
        """
        empty = {
            'has_upcoming_earnings': False, 'earnings_date': None,
            'days_until': None, 'expected_move_pct': None, 'note': None,
        }

        try:
            t = yf.Ticker(ticker)
            calendar = t.calendar
            earnings_dates = calendar.get('Earnings Date') if calendar else None
            if not earnings_dates:
                return empty

            earnings_date = earnings_dates[0]
            days_until = (earnings_date - date.today()).days

            if days_until < 0 or days_until > lookahead_days:
                return empty

            expected_move_pct = self._expected_move(t, earnings_date)

            note = (
                f"Earnings in {days_until} day{'s' if days_until != 1 else ''} "
                f"({earnings_date.isoformat()})"
            )
            if expected_move_pct is not None:
                note += f" — options market pricing in ~±{expected_move_pct:.1f}% move"

            return {
                'has_upcoming_earnings': True,
                'earnings_date': earnings_date.isoformat(),
                'days_until': days_until,
                'expected_move_pct': expected_move_pct,
                'note': note,
            }

        except Exception as e:
            logger.debug(f"Earnings risk check failed for {ticker}: {e}")
            return empty

    def _expected_move(self, ticker_obj: yf.Ticker, earnings_date: date) -> Optional[float]:
        """ATM straddle price as % of stock price = the options market's implied expected
        move around the given date. Standard technique: (ATM call + ATM put) / stock price.

        Most precise for near-term earnings (within ~1-2 weeks), where a weekly options
        expiration lands close to the report date. For earnings further out, the nearest
        available expiration may be well past the report, overstating the earnings-specific
        move with several extra weeks of ordinary time value — real limitation, not hidden.
        """
        try:
            expirations = ticker_obj.options
            if not expirations:
                return None

            target_exp = None
            for exp_str in expirations:
                exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
                if exp_date >= earnings_date:
                    target_exp = exp_str
                    break
            if not target_exp:
                return None

            price = ticker_obj.history(period='1d')['Close'].iloc[-1]
            chain = ticker_obj.option_chain(target_exp)
            calls, puts = chain.calls, chain.puts
            if calls.empty or puts.empty:
                return None

            atm_strike = calls.iloc[(calls['strike'] - price).abs().argsort()[:1]]['strike'].values[0]
            atm_call = calls[calls['strike'] == atm_strike]['lastPrice']
            atm_put = puts[puts['strike'] == atm_strike]['lastPrice']
            if atm_call.empty or atm_put.empty or atm_call.values[0] == 0:
                return None

            straddle = atm_call.values[0] + atm_put.values[0]
            return float(straddle / price * 100)

        except Exception as e:
            logger.debug(f"Expected move calc failed: {e}")
            return None
