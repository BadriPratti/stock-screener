"""Shared helper for writing JSON that the GUI dashboard's browser-side
JavaScript will actually be able to parse.

Any script whose output flows into the dashboard (via --json-out) touches
pandas/yfinance data at some point, which can leave a NaN behind — an SMA
with not enough real history, a return-pct computed from a missing price,
an average over an empty list. Python's json.dumps happily serializes NaN
and Infinity as bare, non-standard tokens (NaN, Infinity) by default; the
browser's JSON.parse() rejects them outright with no server-side error to
point at, so the dashboard view just hangs on "Loading..." forever with no
visible cause. sanitize_nan() replaces any such float with None (JSON null)
right before serialization, regardless of which upstream calculation
produced it.
"""
import math


def sanitize_nan(obj):
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: sanitize_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_nan(v) for v in obj]
    return obj
