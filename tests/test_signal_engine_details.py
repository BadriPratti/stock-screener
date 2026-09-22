"""Regression tests for behavior-neutral buy-signal instrumentation."""

import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from src.screening import phase_indicators, signal_engine


NEW_DETAIL_KEYS = {
    'score_version',
    'distance_component_raw',
    'distance_component',
    'slope_component_raw',
    'slope_component',
    'stage2_quality',
    'breakout_fired',
    'breakout_type',
    'breakout_bonus',
    'extension_penalty',
    'fundamentals_branch',
    'fundamentals_missing',
    'fundamental_revenue_score_raw',
    'fundamental_eps_score_raw',
    'fundamental_inventory_score_raw',
    'fundamental_margin_placeholder_raw',
    'volume_score_raw',
    'vol_ratio',
    'rs_score_raw',
    'rr_score_raw',
    'entry_high_proximity_score_raw',
    'entry_high_proximity_score_scaled',
    'entry_sma_score_raw',
    'entry_sma_score_scaled',
    'vcp_bonus_raw',
}


GOLDEN_LEGACY_OUTPUT_HASHES = {
    'phase1': 'b24b337d1cb9b294ac12459eb034858f7f3bcf0473be40ea9c3857cf941d0024',
    'template_fail': '55aeb45f0d825cac646cf56c7f9e899f63afcacfc0e21c6756a97d950f756f59',
    'balanced_none': 'c381dfc94fb23a172268e111de2857e3849e31812eabbec9cc78eadf352c0d42',
    'empty_dict': 'd92d665b087eb8976d2350163626883da48e0af05bef13a18ba68c5104cc7926',
    'breakout_real': '3b6820a9cc0e19a6d542932ae65c554e774f59b71887d331ec4647ce92b81a71',
    'overextended_partial': 'a3780940fa83a24ac9eb1a4eacf319270dfcc74a14621fe8edf2adde804e3cd9',
}


@pytest.fixture
def scoring_environment(monkeypatch):
    def fake_template(current_price, phase_info, sma_200):
        passed = not phase_info.get('force_fail', False)
        return {
            'passes_template': passed,
            'criteria_passed': 8 if passed else 6,
            'template_score': 100 if passed else 75,
            'criteria': {'price_above_150_200': passed},
        }

    def fake_breakout(price_data, current_price, phase_info, vcp_data):
        fired = phase_info.get('force_breakout', False)
        return {
            'is_breakout': fired,
            'breakout_type': (
                phase_info.get('breakout_type', '50 SMA Cross') if fired else None
            ),
            'breakout_level': 99.5 if fired else None,
            'volume_confirmed': phase_info.get('volume_confirmed', False),
        }

    monkeypatch.setattr(
        signal_engine, 'validate_minervini_trend_template', fake_template
    )
    monkeypatch.setattr(signal_engine, 'detect_breakout', fake_breakout)
    monkeypatch.setattr(
        signal_engine,
        'calculate_rs_slope',
        lambda series, periods: float(series.iloc[-1]),
    )

    index = pd.date_range('2025-01-01', periods=220, freq='B')
    close = np.linspace(70.0, 100.0, 220)
    close[-6:] = [95, 97, 96, 99, 98, 100]
    price_data = pd.DataFrame(
        {
            'Open': close - 0.5,
            'High': close + 2,
            'Low': close - 3,
            'Close': close,
            'Volume': np.r_[
                np.full(215, 1_000_000),
                [2_000_000, 500_000, 2_000_000, 500_000, 2_000_000],
            ],
        },
        index=index,
    )
    return price_data


def _phase(**overrides):
    phase_info = {
        'phase': 2,
        'sma_50': 90.0,
        'sma_200': 75.0,
        'slope_50': 0.04,
        'slope_200': 0.02,
        'distance_from_50sma': 10.0,
        'distance_from_200sma': 25.0,
        'week_52_high': 105.0,
    }
    phase_info.update(overrides)
    return phase_info


def _score(price_data, name, phase_info, fundamentals=None, vcp_data=None, rs=0.0):
    return signal_engine.score_buy_signal(
        ticker=name.upper(),
        price_data=price_data.copy(),
        current_price=100.0,
        phase_info=phase_info,
        rs_series=pd.Series([rs] * 25),
        fundamentals=fundamentals,
        vcp_data=vcp_data,
    )


def _golden_cases():
    return {
        'phase1': (_phase(phase=1), None, None, 0.0),
        'template_fail': (_phase(force_fail=True), None, None, 0.0),
        'balanced_none': (_phase(), None, None, 0.05),
        'empty_dict': (
            _phase(
                distance_from_50sma=1.0,
                distance_from_200sma=5.0,
                slope_50=0.01,
                slope_200=0.005,
            ),
            {},
            None,
            -0.08,
        ),
        'breakout_real': (
            _phase(
                distance_from_50sma=5.0,
                distance_from_200sma=18.0,
                slope_50=0.07,
                slope_200=0.04,
                force_breakout=True,
                breakout_type='VCP Breakout',
                volume_confirmed=True,
            ),
            {
                'quarterly_revenue': {
                    '2024Q1': 100,
                    '2024Q2': 108,
                    '2024Q3': 118,
                    '2024Q4': 132,
                },
                'eps_yoy_change': 40.0,
                'inventory_qoq_change': -10.0,
            },
            {
                'is_vcp': True,
                'vcp_quality': 85,
                'pattern_details': '3 contractions',
                'contraction_count': 3,
                'base_length_weeks': 9,
                'breakout_volume_ratio': 1.8,
                'quality_factors': ['tightness'],
            },
            0.2,
        ),
        'overextended_partial': (
            _phase(
                distance_from_50sma=35.0,
                distance_from_200sma=50.0,
                slope_50=0.10,
                slope_200=0.08,
                week_52_high=140,
            ),
            {'ticker': 'OVER'},
            {
                'is_vcp': False,
                'contraction_count': 2,
                'vcp_quality': 45,
                'pattern_details': 'partial',
            },
            -0.2,
        ),
    }


def _native(value):
    if isinstance(value, dict):
        return {key: _native(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_native(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def _legacy_output_hash(result):
    legacy_result = dict(result)
    legacy_result['details'] = {
        key: value
        for key, value in result['details'].items()
        if key not in NEW_DETAIL_KEYS
    }
    payload = json.dumps(
        _native(legacy_result),
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def test_golden_batch_matches_sc003_outputs(scoring_environment):
    for name, (phase_info, fundamentals, vcp_data, rs) in _golden_cases().items():
        result = _score(
            scoring_environment,
            name,
            phase_info,
            fundamentals=fundamentals,
            vcp_data=vcp_data,
            rs=rs,
        )
        assert result['details']['score_version'] == 'v2-sc003'
        assert _legacy_output_hash(result) == GOLDEN_LEGACY_OUTPUT_HASHES[name]


@pytest.mark.parametrize(
    ('distance_50', 'expected_penalty'),
    [
        (20.0, 0),
        (20.1, -0.1),
        (25.0, -5),
        (29.9, -9.9),
        (30.0, -10),
        (35.0, -10),
    ],
)
def test_trend_components_are_signed_clamped_and_sum_to_parent(
    scoring_environment, distance_50, expected_penalty
):
    result = _score(
        scoring_environment,
        'trend',
        _phase(
            distance_from_50sma=distance_50,
            distance_from_200sma=50.0,
            slope_50=0.10,
            slope_200=0.08,
        ),
    )
    details = result['details']

    assert details['distance_component_raw'] > details['distance_component']
    assert details['distance_component'] == 15
    assert details['slope_component_raw'] > details['slope_component']
    assert details['slope_component'] == 15
    assert details['stage2_quality'] == 30
    assert details['breakout_fired'] is False
    assert details['breakout_type'] is None
    assert details['breakout_bonus'] == 0
    assert details['extension_penalty'] == pytest.approx(expected_penalty)
    raw_trend = (
        details['distance_component']
        + details['slope_component']
        + details['breakout_bonus']
        + details['extension_penalty']
    )
    assert round(raw_trend * (35 / 40), 2) == details['trend_score']


def test_breakout_entry_and_scaled_components_sum_to_parents(scoring_environment):
    phase_info, fundamentals, vcp_data, rs = _golden_cases()['breakout_real']
    result = _score(
        scoring_environment,
        'breakout_real',
        phase_info,
        fundamentals=fundamentals,
        vcp_data=vcp_data,
        rs=rs,
    )
    details = result['details']

    assert details['breakout_fired'] is True
    assert details['breakout_type'] == 'VCP Breakout'
    assert details['breakout_bonus'] == 10
    raw_trend = (
        details['stage2_quality']
        + details['breakout_bonus']
        + details['extension_penalty']
    )
    assert round(raw_trend * (35 / 40), 2) == details['trend_score']

    assert details['entry_high_proximity_score_scaled'] == (
        details['entry_high_proximity_score_raw'] * 5
    )
    assert details['entry_sma_score_scaled'] == details['entry_sma_score_raw'] * 5
    assert round(
        details['entry_high_proximity_score_scaled']
        + details['entry_sma_score_scaled'],
        2,
    ) == details['entry_score']

    raw_fundamentals = (
        details['fundamental_revenue_score_raw']
        + details['fundamental_eps_score_raw']
        + details['fundamental_inventory_score_raw']
        + details['fundamental_margin_placeholder_raw']
    )
    assert round(min(raw_fundamentals, 40) * (35 / 40), 2) == details['fundamental_score']
    assert round(details['volume_score_raw'] * 0.5, 2) == details['volume_score']
    assert details['vol_ratio'] == 4.0
    assert round(details['rs_score_raw'], 2) == details['rs_score']
    assert round(details['rr_score_raw'] * (10 / 15), 2) == details['rr_score']
    assert round(details['vcp_bonus_raw'], 2) == details['vcp_bonus']
    assert details['score_version'] == 'v2-sc003'


def test_raw_trend_components_expose_lower_clamp(scoring_environment):
    result = _score(
        scoring_environment,
        'lower_clamp',
        _phase(
            distance_from_50sma=-10.0,
            distance_from_200sma=-20.0,
            slope_50=-0.08,
            slope_200=-0.05,
        ),
    )
    details = result['details']

    assert details['distance_component_raw'] < 0
    assert details['distance_component'] == 0
    assert details['slope_component_raw'] < 0
    assert details['slope_component'] == 0
    assert details['stage2_quality'] == 0


def test_fundamentals_none_and_empty_dict_are_observably_distinct(
    scoring_environment,
):
    missing = _score(scoring_environment, 'missing', _phase(), fundamentals=None)
    empty = _score(scoring_environment, 'empty', _phase(), fundamentals={})

    assert missing['details']['fundamental_score'] == 17.5
    assert empty['details']['fundamental_score'] == 17.5
    assert missing['details']['fundamentals_branch'] == 'flat_neutral'
    assert empty['details']['fundamentals_branch'] == 'flat_neutral'
    assert missing['details']['fundamentals_missing'] is True
    assert empty['details']['fundamentals_missing'] is False


def test_present_partial_fundamentals_expose_each_raw_subcomponent(
    scoring_environment,
):
    result = _score(
        scoring_environment,
        'partial',
        _phase(),
        fundamentals={'ticker': 'PARTIAL'},
    )
    details = result['details']

    assert details['fundamentals_branch'] == 'real_data'
    assert details['fundamentals_missing'] is False
    assert details['fundamental_revenue_score_raw'] == 0
    assert details['fundamental_eps_score_raw'] == 7.5
    assert details['fundamental_inventory_score_raw'] == 5
    assert details['fundamental_margin_placeholder_raw'] == 10
    assert details['fundamental_score'] == 19.69


def test_breakout_levels_use_exact_prior_window_and_require_strict_new_high():
    prior = pd.Series(np.r_[np.full(59, 90.0), 100.0])

    assert phase_indicators.find_base_high(pd.concat([prior, pd.Series([101.0])])) == 100
    assert phase_indicators.find_base_high(pd.concat([prior, pd.Series([100.0])])) == 100
    assert phase_indicators.find_base_high(prior) is None

    phase_info = {'phase': 2, 'sma_50': 80.0}
    for current_price, expected in [(101.0, True), (100.0, False), (99.0, False)]:
        close = pd.concat([prior, pd.Series([current_price])], ignore_index=True)
        price_data = pd.DataFrame(
            {'Close': close, 'Volume': np.full(len(close), 1_000_000)}
        )
        breakout = phase_indicators.detect_breakout(
            price_data, current_price, phase_info
        )
        assert breakout['is_breakout'] is expected
        assert breakout['breakout_type'] == ('Base Breakout' if expected else None)


def test_pivot_breakout_uses_prior_20_bars_below_longer_base_high():
    close = pd.Series(np.r_[110.0, np.full(39, 90.0), np.full(20, 100.0), 101.0])
    price_data = pd.DataFrame(
        {'Close': close, 'Volume': np.full(len(close), 1_000_000)}
    )

    breakout = phase_indicators.detect_breakout(
        price_data, 101.0, {'phase': 2, 'sma_50': 80.0}
    )

    assert breakout['is_breakout'] is True
    assert breakout['breakout_type'] == 'Pivot Breakout'
    assert breakout['breakout_level'] == 100.0


def test_base_breakout_updates_buy_signal_instrumentation(
    scoring_environment, monkeypatch
):
    monkeypatch.setattr(
        signal_engine, 'detect_breakout', phase_indicators.detect_breakout
    )
    price_data = scoring_environment.copy()
    price_data.loc[price_data.index[-61:-1], 'Close'] = 99.0
    price_data.loc[price_data.index[-1], 'Close'] = 101.0

    result = signal_engine.score_buy_signal(
        ticker='BREAKOUT',
        price_data=price_data,
        current_price=101.0,
        phase_info=_phase(sma_50=80.0),
        rs_series=pd.Series([0.0] * 25),
    )

    assert bool(result['is_buy']) is True
    assert result['details']['breakout_fired'] is True
    assert result['details']['breakout_type'] == 'Base Breakout'
    assert result['details']['breakout_bonus'] == 10


def test_fundamental_score_is_capped_at_advertised_35_points(
    scoring_environment,
):
    result = _score(
        scoring_environment,
        'fundamental_cap',
        _phase(),
        fundamentals={
            'quarterly_revenue': {
                '2024Q1': 100,
                '2024Q2': 120,
                '2024Q3': 144,
                '2024Q4': 173,
            },
            'eps_yoy_change': 80.0,
            'inventory_qoq_change': -20.0,
        },
    )
    details = result['details']
    raw_fundamentals = (
        details['fundamental_revenue_score_raw']
        + details['fundamental_eps_score_raw']
        + details['fundamental_inventory_score_raw']
        + details['fundamental_margin_placeholder_raw']
    )

    assert raw_fundamentals == 50
    assert details['fundamental_score'] == 35


def test_fundamental_revenue_penalty_is_not_floored_at_subscore(
    scoring_environment,
):
    result = _score(
        scoring_environment,
        'fundamental_penalty',
        _phase(),
        fundamentals={
            'quarterly_revenue': {
                '2024Q1': 100,
                '2024Q2': 100,
                '2024Q3': 100,
                '2024Q4': 90,
            },
            'eps_yoy_change': -20.0,
            'inventory_qoq_change': 20.0,
        },
    )

    assert result['details']['fundamental_revenue_score_raw'] == -15
    assert result['details']['fundamental_score'] == -4.38
    assert result['score'] >= 0
