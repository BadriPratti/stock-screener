# SC-002 Result: Scoring sub-component instrumentation

Implemented behavior-neutral instrumentation in `src/screening/signal_engine.py` and added focused regression coverage in `tests/test_signal_engine_details.py`.

## New `details` keys

- `score_version`
- `distance_component_raw`
- `distance_component`
- `slope_component_raw`
- `slope_component`
- `stage2_quality`
- `breakout_fired`
- `breakout_type`
- `breakout_bonus`
- `extension_penalty`
- `fundamentals_branch`
- `fundamentals_missing`
- `fundamental_revenue_score_raw`
- `fundamental_eps_score_raw`
- `fundamental_inventory_score_raw`
- `fundamental_margin_placeholder_raw`
- `volume_score_raw`
- `vol_ratio`
- `rs_score_raw`
- `rr_score_raw`
- `entry_high_proximity_score_raw`
- `entry_high_proximity_score_scaled`
- `entry_sma_score_raw`
- `entry_sma_score_scaled`
- `vcp_bonus_raw`

`score_version` is also present in the `details` mapping returned by the Phase and Minervini-template early exits.

## Behavior-neutral verification

`test_golden_batch_preserves_every_legacy_output_field` freezes the complete legacy output after removing only the enumerated new detail keys. It covers six cases: Phase 1 rejection, Minervini-template rejection, ordinary Phase 2 with no fundamentals, empty fundamentals, real fundamentals with a breakout and VCP bonus, and an over-extended signal with partial fundamentals. The frozen output includes every legacy top-level field, every legacy `details` field, and the complete reasons list.

The following tests verify the new data reconstructs the existing parent scores without changing them:

- `test_trend_components_are_signed_clamped_and_sum_to_parent`
- `test_breakout_entry_and_scaled_components_sum_to_parents`
- `test_raw_trend_components_expose_lower_clamp`
- `test_fundamentals_none_and_empty_dict_are_observably_distinct`
- `test_present_partial_fundamentals_expose_each_raw_subcomponent`

The fundamentals distinction test confirms `fundamentals=None` and `fundamentals={}` both retain the existing `fundamental_score` of `17.5`, while `fundamentals_missing` distinguishes the inputs.

No score formula, threshold, cliff, branch condition, existing detail value, or existing returned top-level value was changed.

## Test results

Focused instrumentation suite:

```text
./venv/bin/python -m pytest -q tests/test_signal_engine_details.py
8 passed in 0.33s
```

All Python test files found by searching `tests/` for `from src.screening.signal_engine import`, `import src.screening.signal_engine`, or `score_buy_signal`, together with the new instrumentation suite:

```text
./venv/bin/python -m pytest -q tests/test_signal_engine_details.py tests/test_frozen_backtest_manifest.py tests/test_intraday_rescore.py tests/test_market_motion.py
77 passed in 1.64s
```

The repository-local `./venv/bin/python` was used as requested. It currently reports Python `3.13.5`, rather than Python 3.11.
