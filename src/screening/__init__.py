"""Stock screening module for identifying undervalued stocks at support levels.

Deliberately does NOT eagerly import .screener/.indicators here (they pull in
numpy/pandas): the packaged desktop app (mac_app/, built by py2app) bundles
only Flask + pywebview — dashboard.py shells out to the project's real venv
for anything numpy/pandas-based rather than importing it directly — but
`from src.screening import pick_history` (and market_motion) still runs this
file first, since Python always executes a package's __init__ before any of
its submodules. An eager import here made every such import require numpy/
pandas too, which broke the packaged app's launch
(ModuleNotFoundError: No module named 'numpy') even though dashboard.py
itself never touches numpy. screen_candidates/calculate_value_score/etc. are
still available at their real path, `from src.screening.screener import ...`.
"""

__all__ = [
    "calculate_value_score",
    "detect_support_levels",
    "calculate_support_score",
    "screen_candidates",
    "calculate_rsi",
    "calculate_sma",
    "calculate_ema",
    "detect_volume_spike",
    "find_swing_lows",
]


def __getattr__(name):
    # Lazy: only pays numpy/pandas's import cost for callers that actually
    # touch the screener/indicators functions, matching the historical
    # `from src.screening import screen_candidates` usage exactly.
    if name in __all__:
        from . import screener, indicators

        return getattr(screener, name, None) or getattr(indicators, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
