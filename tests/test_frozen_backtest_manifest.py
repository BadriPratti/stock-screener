import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import scripts.walk_forward_backtest as walk_forward
from src.backtesting.frozen_inputs import ManifestError, load_manifest, validate_manifest


def _history(offset=0.0):
    index = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=320)
    close = np.linspace(50.0 + offset, 90.0 + offset, len(index))
    return pd.DataFrame(
        {
            "Open": close - 0.2,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.arange(len(index), dtype=float) + 100_000,
        },
        index=index,
    )


@pytest.fixture
def fake_market(monkeypatch):
    frames = {"SPY": _history(100), "AAA": _history(0), "BBB": _history(10)}
    calls = []

    class FakeTicker:
        def __init__(self, ticker):
            self.ticker = ticker

        def history(self, period, **kwargs):
            calls.append((self.ticker, period, kwargs))
            return frames[self.ticker].copy()

    monkeypatch.setattr(walk_forward.yf, "Ticker", FakeTicker)
    monkeypatch.setattr(
        walk_forward.USStockUniverseFetcher,
        "fetch_universe",
        lambda self: ["AAA", "BBB"],
    )
    monkeypatch.setattr(walk_forward, "classify_phase", lambda data, price: {"phase": 2})
    monkeypatch.setattr(
        walk_forward,
        "calculate_relative_strength",
        lambda stock, benchmark, period: pd.Series(1.0, index=stock.index),
    )

    def fake_score(ticker, price_data, current_price, **kwargs):
        ticker_bonus = 2 if ticker == "BBB" else 1
        score = float(current_price / 2 + ticker_bonus)
        return {
            "ticker": ticker,
            "score": score,
            "is_buy": True,
            "stop_loss": None,
            "details": {
                "trend_score": score / 2,
                "fundamental_score": 10,
                "entry_score": ticker_bonus,
                "rr_score": 5,
                "rs_score": 4,
                "volume_score": 3,
            },
        }

    monkeypatch.setattr(walk_forward, "score_buy_signal", fake_score)
    return calls


def _run(store, **kwargs):
    params = {
        "universe_size": 2,
        "lookback_months": 1,
        "step_days": 7,
        "top_n": 2,
        "max_hold_days": 10,
        "investment_per_trade": 1000.0,
        "seed": 17,
        "manifest_store": store,
    }
    params.update(kwargs)
    return walk_forward.run_walk_forward(**params)


def test_manifest_schema_validation_rejects_missing_and_inconsistent_fields(tmp_path, fake_market):
    _run(tmp_path, capture_manifest_ref="schema-test")
    manifest_path = tmp_path / "schema-test" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    validate_manifest(manifest)

    missing = copy.deepcopy(manifest)
    del missing["parameters"]["top_n"]
    with pytest.raises(ManifestError, match="parameters are missing: top_n"):
        validate_manifest(missing)

    inconsistent = copy.deepcopy(manifest)
    inconsistent["random_seed"] = 999
    with pytest.raises(ManifestError, match="random_seed"):
        validate_manifest(inconsistent)


def test_replay_rejects_one_byte_tampering(tmp_path, fake_market):
    _run(tmp_path, capture_manifest_ref="tamper-test")
    manifest_path = tmp_path / "tamper-test" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    frozen_path = manifest_path.parent / manifest["price_histories"]["AAA"]["path"]
    contents = bytearray(frozen_path.read_bytes())
    offset = contents.index(b"5")
    contents[offset] = ord("6")
    frozen_path.write_bytes(contents)

    with pytest.raises(ManifestError, match="hash mismatch"):
        _run(tmp_path, replay_manifest_ref="tamper-test")


def test_capture_then_two_replays_are_byte_identical_and_offline(tmp_path, fake_market, monkeypatch):
    captured = _run(tmp_path, capture_manifest_ref="deterministic")
    assert captured["manifest_id"] == "deterministic"
    manifest = json.loads((tmp_path / "deterministic" / "manifest.json").read_text())
    assert manifest["universe"] == ["AAA", "BBB"]
    assert manifest["random_seed"] == 17
    assert manifest["parameters"]["max_hold_days"] == 10
    assert manifest["data_settings"]["history_arguments"] == {
        "period": "2y", "auto_adjust": True, "actions": True,
    }
    assert set(manifest["price_histories"]) == {"AAA", "BBB"}

    def network_forbidden(*args, **kwargs):
        raise AssertionError("network-backed fetcher was called during replay")

    monkeypatch.setattr(walk_forward.yf, "Ticker", network_forbidden)
    monkeypatch.setattr(walk_forward.USStockUniverseFetcher, "fetch_universe", network_forbidden)

    first = _run(tmp_path, replay_manifest_ref="deterministic")
    second = _run(tmp_path, replay_manifest_ref="deterministic")
    first_bytes = json.dumps(first, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    second_bytes = json.dumps(second, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    assert first_bytes == second_bytes
    assert first["trades"]
    assert first["summary"]
    assert first["component_correlations"]


def test_default_mode_still_fetches_live_without_writing_a_manifest(tmp_path, fake_market):
    result = _run(tmp_path)
    assert "manifest_id" not in result
    assert fake_market == [("SPY", "2y", {}), ("AAA", "2y", {}), ("BBB", "2y", {})]
    assert not list(tmp_path.iterdir())


def test_missing_manifest_fails_without_fetching(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("replay fell back to live fetching")

    monkeypatch.setattr(walk_forward.yf, "Ticker", forbidden)
    monkeypatch.setattr(walk_forward.USStockUniverseFetcher, "fetch_universe", forbidden)
    with pytest.raises(ManifestError, match="does not exist"):
        _run(tmp_path, replay_manifest_ref="missing")


def test_load_manifest_returns_only_histories_marked_usable(tmp_path, fake_market):
    _run(tmp_path, capture_manifest_ref="load-test")
    manifest, spy, histories, path = load_manifest("load-test", store_root=tmp_path)
    assert path == tmp_path / "load-test" / "manifest.json"
    assert not spy.empty
    assert list(histories) == manifest["universe"]
