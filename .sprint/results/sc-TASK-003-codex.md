# SC-003: Verified scoring bug fixes

## Production changes

Only the three requested score behaviors changed.

1. `find_base_high()` and `find_pivot_high()` now require the current bar plus a complete prior lookback window
   and calculate resistance from `prices.iloc[-window-1:-1]`. The current bar is excluded. `detect_breakout()`
   retains its strict `current_price > resistance` condition, so equality is not a breakout, consistently with
   the existing 50-SMA branch's strict comparison.
2. The scaled fundamentals score is now exactly
   `min(fundamental_score, 40) * (35 / 40)`, capping the block at its advertised 35 points. There is intentionally
   no lower clamp: the existing recent-revenue-decline subtraction is a penalty and must still reduce the total
   signal score. The final total-score clamp remains the last protection against a negative returned score.
3. The extension penalty is now
   `-min(10, max(0, distance_50 - 20))`. It is 0 through 20%, falls continuously by one raw trend point for each
   percentage point from 20% to 30%, and is capped at -10 from 30% onward. After the existing 35/40 trend scale,
   a one-percentage-point movement changes this contribution by at most 0.875 total-score points.

The scoring version recorded in `details` is now `v2-sc003`, including both early exits. SC-002's instrumentation
remains present. In particular, `extension_penalty` records the new continuous value; `breakout_fired` and
`breakout_type` expose newly reachable base/pivot breakouts; `fundamental_score` records the capped scaled value;
and the four raw fundamentals component fields remain uncapped audit inputs.

The 52-week-high entry-quality formula was reviewed and not changed. Its adjoining branches agree exactly at
the boundaries: both sides produce 2 raw points at -15% and 1 raw point at -25%.

## Tests

New tests in `tests/test_signal_engine_details.py`:

- `test_breakout_levels_use_exact_prior_window_and_require_strict_new_high`
- `test_pivot_breakout_uses_prior_20_bars_below_longer_base_high`
- `test_base_breakout_updates_buy_signal_instrumentation`
- `test_fundamental_score_is_capped_at_advertised_35_points`
- `test_fundamental_revenue_penalty_is_not_floored_at_subscore`

The existing parameterized trend-component test was extended to cover 20.0, 20.1, 25.0, 29.9, 30.0, and
35.0 percent, proving the continuous values and exact endpoints. The SC-002 parent-sum assertion was updated to
reconstruct the now-capped fundamentals score. The SC-002 golden test was renamed for the intentional SC-003
behavior and only its `breakout_real` hash changed, from
`5fffd6f9f206427ae94218ea7958a680b31e855277b545bef87f53bafd4735a7` to
`3b6820a9cc0e19a6d542932ae65c554e774f59b71887d331ec4647ce92b81a71`; that fixture's raw fundamentals exceed
40, so the old hash asserted the bug.

Focused result:

```text
venv/bin/python -m pytest tests/test_signal_engine_details.py -q
16 passed in 0.46s
```

Compilation and whitespace validation also passed:

```text
venv/bin/python -m py_compile src/screening/signal_engine.py src/screening/phase_indicators.py tests/test_signal_engine_details.py
git diff --check -- src/screening/signal_engine.py src/screening/phase_indicators.py tests/test_signal_engine_details.py
```

## Measured real-data impact

The comparison was offline and deterministic over the repository's current cache: 3,766
`data/cache/*_prices_5y_1d.pkl` histories and 2,600 `data/fundamentals_cache/*_fundamentals.json` records. Of
those histories, 867 latest observations classified as Phase 2 and ran through the complete buy scorer without
an error. Each variant used the same price frame, phase classification, matching cached fundamentals, no VCP
override, and the same neutral RS series. The pre-fix implementation was reconstructed by reversing only these
three expressions in an in-memory module; each fix was also isolated independently. Deltas below use the
scorer's returned one-decimal score.

| Variant versus pre-fix | Tickers changed | Minimum | Median | Maximum |
|---|---:|---:|---:|---:|
| Breakout window only | 92 | +8.7 | +8.7 | +8.8 |
| Fundamentals cap only | 110 | -8.8 | -4.15 | -0.2 |
| Continuous extension only | 46 | -4.2 | +1.75 | +4.3 |
| All three fixes | 199 | -9.5 | +2.5 | +13.0 |

The fixed detector classified 87 real candidates as `Base Breakout` and 6 as `Pivot Breakout`; 93 breakout
types changed, while 92 returned scores changed because one signal was already at the total score cap. Before
the fix, none of those base/pivot paths could fire. A separate read-only search of all 23 historical files in
`data/daily_scans/*.txt` found zero occurrences of either `Base Breakout` or `Pivot Breakout`, consistent with
the structural bug.

The combined change caused two buy-threshold flips. The aggregate buy count remained 741 because one candidate
moved above the threshold and one moved below it.

## Full-suite result

Command required by the task:

```text
venv/bin/python -m pytest tests --ignore=tests/test_email_full.py -q
321 passed, 1 failed in 22.48s
```

The sole failure is the pre-existing, unrelated
`tests/test_fetcher.py::TestFetchPriceHistory::test_fetch_price_history_success`: the test expects a `Date`
column although its mock supplies `Date` as the index and the fetcher returns the frame unchanged. SC-001's
result already recorded the same failure. It does not exercise either changed scoring module, and it was not
modified because `tests/test_fetcher.py` is outside this task's file scope.

The mandated repository interpreter was used throughout. `venv/bin/python --version` reports Python 3.13.5,
not the stated Python 3.11.
