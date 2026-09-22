"""Offline tests for the tracked-roster intraday re-score command."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import run_intraday_rescore as command
from src.screening import market_motion as mm
from src.screening.intraday_rescore import format_result, run_rescore


FRIDAY = datetime(2026, 9, 18, 20, tzinfo=timezone.utc)
SUNDAY = datetime(2026, 9, 20, 16, tzinfo=timezone.utc)


def qualified(ticker: str, score: float = 90, rs: float = 0.2):
    return mm.make_point(ticker, mm.EVAL_QUALIFIED, score=score, rs=rs, phase=2)


def seed_daily(root: Path, points, *, regime=True, generated_at=FRIDAY):
    frame = mm.build_frame(
        run_kind=mm.RUN_KIND_DAILY_FULL,
        generated_at=generated_at,
        session_date="2026-09-18",
        provenance="live",
        points=points,
        regime={"should_generate_buys": regime, "source_run_id": None},
        scope={"mode": "full_universe", "completed": True},
    )
    mm.write_frame(frame, root)
    return frame


def analysis(ticker: str, phase: int = 2, price: float = 25.0):
    return {
        "ticker": ticker,
        "price_data": object(),
        "current_price": price,
        "phase_info": {"phase": phase},
        "rs_series": object(),
        "quarterly_data": {"revenue": {}},
        "vcp_data": {"quality": 70},
    }


def signal(ticker: str, *, is_buy=True, score=80.0, rs=0.25, reason=None):
    result = {
        "ticker": ticker,
        "is_buy": is_buy,
        "score": score,
        "phase": 2,
        "details": {"rs_slope": rs},
        "reasons": ["Strong setup"],
        "entry_quality": "Good",
        "risk_reward_ratio": 3.0,
    }
    if reason:
        result["reason"] = reason
    return result


class StubProcessor:
    def __init__(self, analyses, bar=FRIDAY, *, spy_ok=True, batch_error=None):
        self._analyses = analyses
        self._bar = bar
        self._spy_ok = spy_ok
        self._batch_error = batch_error
        self.spy_data = None
        self.calls = []

    def fetch_spy_data(self):
        self.calls.append(("spy",))
        if self._spy_ok:
            self.spy_data = type("Spy", (), {"index": [self._bar]})()
        return self._spy_ok

    def process_batch_parallel(self, tickers, **kwargs):
        self.calls.append(("batch", list(tickers), kwargs))
        if self._batch_error:
            return {"error": self._batch_error}
        return {"analyses": self._analyses}


def factory_for(processor, captured=None):
    def factory(**kwargs):
        if captured is not None:
            captured.update(kwargs)
        return processor

    return factory


def score_from(mapping):
    def scorer(**kwargs):
        ticker = kwargs["ticker"]
        value = mapping[ticker]
        return value() if callable(value) else dict(value)

    return scorer


def intraday_files(root: Path):
    directory = root / "snapshots" / mm.RUN_KIND_INTRADAY
    return sorted(directory.glob("*.json")) if directory.exists() else []


def test_no_tracked_stocks_skips_without_constructing_processor(tmp_path):
    called = False

    def factory(**kwargs):
        nonlocal called
        called = True
        raise AssertionError("processor should not be constructed")

    result = run_rescore(factory, lambda **kwargs: {}, tmp_path, 500, FRIDAY, False, False)
    assert result["status"] == "skipped"
    assert result["reason"] == "no_tracked_stocks (run a full scan first)"
    assert result["run_id"] is None and called is False
    assert intraday_files(tmp_path) == []


def test_weekend_bar_guard_skips_before_processing(tmp_path):
    seed_daily(tmp_path, [qualified("AAA")])
    processor = StubProcessor([analysis("AAA")])
    result = run_rescore(
        factory_for(processor), score_from({"AAA": signal("AAA")}),
        tmp_path, 500, SUNDAY, False, False,
    )
    assert result["status"] == "skipped"
    assert result["reason"] == "market_closed_or_no_bar_today"
    assert processor.calls == [("spy",)]
    assert intraday_files(tmp_path) == []


def test_force_overrides_guard_and_uses_isolated_processor_state(tmp_path, caplog):
    seed_daily(tmp_path, [qualified("AAA")])
    processor = StubProcessor([analysis("AAA")])
    factory_kwargs = {}
    result = run_rescore(
        factory_for(processor, factory_kwargs), score_from({"AAA": signal("AAA")}),
        tmp_path, 500, SUNDAY, True, False,
    )
    assert result["status"] == "written"
    assert "FORCE enabled" in caplog.text
    assert factory_kwargs["use_git_storage"] is True
    assert factory_kwargs["max_workers"] == 2
    assert factory_kwargs["rate_limit_delay"] == 1.0
    assert Path(factory_kwargs["results_dir"]).name == "results"
    assert processor.calls[1] == (
        "batch", ["AAA"],
        {"resume": False, "min_price": 5.0, "min_volume": 100000},
    )


def test_roster_order_cap_overflow_ranks_and_scope(tmp_path):
    daily = seed_daily(
        tmp_path,
        [qualified("LOW", 70), qualified("TOP", 100), qualified("MID", 85)],
    )
    processor = StubProcessor([analysis("LOW"), analysis("TOP")])
    scores = {"TOP": signal("TOP", score=75), "LOW": signal("LOW", score=95)}
    result = run_rescore(
        factory_for(processor), score_from(scores), tmp_path, 2, FRIDAY, False, False,
    )
    assert result["status"] == "written"
    assert processor.calls[1][1] == ["TOP", "MID"]
    frame = mm.load_frames(tmp_path, run_kinds=(mm.RUN_KIND_INTRADAY,))[0][0]
    assert [point["ticker"] for point in frame["points"]] == ["TOP", "MID", "LOW"]
    assert frame["points"][0]["rank"] == 1
    assert frame["points"][1] == {
        "ticker": "MID", "evaluation": "error", "error_code": "not_analyzed"
    }
    assert frame["points"][2] == {"ticker": "LOW", "evaluation": "not_evaluated"}
    assert frame["scope"] == {
        "mode": "tracked_roster",
        "requested": 2,
        "analyzed": 1,
        "failed": 1,
        "completed": True,
        "roster_cap": 2,
        "overflow": 1,
        "candidate_source_run_id": daily["run_id"],
    }
    assert frame["coverage"]["kind"] == mm.COVERAGE_COMPLETE
    assert frame["regime"] == {"should_generate_buys": True, "source_run_id": daily["run_id"]}
    assert frame["fundamentals_as_of"] == "2026-09-18"


def test_each_analysis_outcome_state_and_scoring_call_shape(tmp_path):
    tickers = ["BUY", "BELOW", "TEMPLATE", "PHASE3", "MISSING"]
    seed_daily(tmp_path, [qualified(ticker, 100 - index) for index, ticker in enumerate(tickers)])
    analyses = [
        analysis("BUY"), analysis("BELOW"), analysis("TEMPLATE", phase=1), analysis("PHASE3", phase=3)
    ]
    calls = []

    def scorer(**kwargs):
        calls.append(kwargs)
        ticker = kwargs["ticker"]
        if ticker == "BUY":
            return signal(ticker, score=90)
        if ticker == "BELOW":
            return signal(ticker, is_buy=False, score=55, rs=0.1)
        return signal(ticker, is_buy=False, score=0, rs=None, reason="Fails Minervini trend template")

    result = run_rescore(factory_for(StubProcessor(analyses)), scorer, tmp_path, 500, FRIDAY, False, False)
    assert result["status"] == "written" and result["analyzed"] == 4
    frame = mm.load_frames(tmp_path, run_kinds=(mm.RUN_KIND_INTRADAY,))[0][0]
    points = {point["ticker"]: point for point in frame["points"]}
    assert points["BUY"]["evaluation"] == "qualified"
    assert points["BELOW"]["evaluation"] == "not_qualified"
    assert points["TEMPLATE"]["evaluation"] == "not_scored"
    assert points["PHASE3"]["evaluation"] == "not_scored"
    assert points["MISSING"]["evaluation"] == "error"
    assert {call["ticker"] for call in calls} == {"BUY", "BELOW", "TEMPLATE"}
    assert set(calls[0]) == {
        "ticker", "price_data", "current_price", "phase_info", "rs_series",
        "fundamentals", "vcp_data",
    }


def test_is_buy_as_numpy_style_bool_still_qualifies(tmp_path):
    # Regression for the exact production bug: signal_engine.score_buy_signal's
    # is_buy is numpy.bool_, and `if signal.get("is_buy") is True:` silently
    # treats every real numpy-typed True as False, recording a genuinely
    # qualifying stock as not_qualified. Reproduced with a real numpy bool
    # when numpy is available, otherwise an object with the same identity trap.
    try:
        import numpy as np
        true_ish = np.bool_(True)
    except ImportError:
        class NumpyLikeBool:
            def __bool__(self):
                return True
        true_ish = NumpyLikeBool()
    assert (true_ish is True) is False

    seed_daily(tmp_path, [qualified("AAA")])
    sig = signal("AAA", score=107.9, rs=0.005)
    sig["is_buy"] = true_ish
    result = run_rescore(
        factory_for(StubProcessor([analysis("AAA")])), score_from({"AAA": sig}),
        tmp_path, 500, FRIDAY, False, False,
    )
    assert result["status"] == "written", result
    point = mm.load_frames(tmp_path, run_kinds=(mm.RUN_KIND_INTRADAY,))[0][0]["points"][0]
    assert point["evaluation"] == "qualified", point
    assert point["score"] == 107.9


def test_regime_gate_downgrades_buy_but_keeps_coordinates(tmp_path):
    seed_daily(tmp_path, [qualified("AAA")], regime=False)
    result = run_rescore(
        factory_for(StubProcessor([analysis("AAA", price=41.5)])),
        score_from({"AAA": signal("AAA", score=92, rs=0.44)}),
        tmp_path, 500, FRIDAY, False, False,
    )
    assert result["status"] == "written"
    point = mm.load_frames(tmp_path, run_kinds=(mm.RUN_KIND_INTRADAY,))[0][0]["points"][0]
    assert point["evaluation"] == "not_qualified"
    assert point["drop_reason"] == "regime_gate"
    assert (point["score"], point["rs"], point["current_price"]) == (92.0, 0.44, 41.5)
    assert "rank" not in point


@pytest.mark.parametrize("mode", ["none_analyzed", "exception"])
def test_broken_run_writes_no_frame(tmp_path, mode):
    seed_daily(tmp_path, [qualified("AAA")])
    if mode == "none_analyzed":
        processor = StubProcessor([])
        scorer = score_from({})
    else:
        processor = StubProcessor([analysis("AAA")])

        def scorer(**kwargs):
            raise RuntimeError("scoring exploded")

    result = run_rescore(factory_for(processor), scorer, tmp_path, 500, FRIDAY, False, False)
    assert result["status"] == "failed"
    assert intraday_files(tmp_path) == []


def test_dry_run_computes_but_writes_nothing(tmp_path):
    seed_daily(tmp_path, [qualified("AAA")])
    result = run_rescore(
        factory_for(StubProcessor([analysis("AAA")])),
        score_from({"AAA": signal("AAA")}), tmp_path, 500, FRIDAY, False, True,
    )
    assert result["status"] == "skipped" and result["reason"] == "dry_run"
    assert result["analyzed"] == 1 and result["run_id"] is None
    assert intraday_files(tmp_path) == []


def test_success_adds_only_one_file_and_tracker_moves_without_daily_streak_change(tmp_path):
    seed_daily(tmp_path, [qualified("AAA", 80, 0.1)])
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}
    result = run_rescore(
        factory_for(StubProcessor([analysis("AAA")])),
        score_from({"AAA": signal("AAA", score=96, rs=0.5)}),
        tmp_path, 500, FRIDAY.replace(hour=21), False, False,
    )
    after = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}
    assert len(after - before) == 1
    assert after - before == {
        Path("snapshots/intraday_rescore") / f"{result['run_id']}.json"
    }
    frames, warnings = mm.load_frames(tmp_path)
    assert warnings == []
    record = mm.compute_tracker(frames)["tickers"]["AAA"]
    assert record["position"]["score"] == 96
    assert record["current_streak_days"] == 1
    assert record["current_streak_frames"] == 2


def test_spy_failure_has_clear_result_and_no_frame(tmp_path):
    seed_daily(tmp_path, [qualified("AAA")])
    result = run_rescore(
        factory_for(StubProcessor([], spy_ok=False)), lambda **kwargs: {},
        tmp_path, 500, FRIDAY, False, False,
    )
    assert result["status"] == "failed" and result["reason"] == "spy_data_unavailable"
    assert intraday_files(tmp_path) == []


def test_result_line_and_cli_exit_code(monkeypatch, capsys):
    expected = {
        "status": "written", "reason": "frame_written", "run_id": "run-1",
        "session_date": "2026-09-18", "roster": 3, "analyzed": 2, "elapsed_seconds": 0.5,
    }
    monkeypatch.setattr(command, "run_rescore", lambda *args, **kwargs: expected)
    assert command.main(["--dry-run"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[-1].startswith("MARKET_MOTION_RESULT ")
    assert json.loads(lines[-1].removeprefix("MARKET_MOTION_RESULT ")) == expected
    assert format_result(expected) == lines[-1]


def test_cli_failed_result_returns_one(monkeypatch, capsys):
    failed = {
        "status": "failed", "reason": "boom", "run_id": None,
        "session_date": None, "roster": 0, "analyzed": 0, "elapsed_seconds": 0.0,
    }
    monkeypatch.setattr(command, "run_rescore", lambda *args, **kwargs: failed)
    assert command.main([]) == 1
    assert capsys.readouterr().out.splitlines()[-1] == format_result(failed)


def test_regime_gated_buy_without_an_rs_reading_becomes_not_scored_not_a_failed_frame(tmp_path):
    seed_daily(tmp_path, [qualified("AAA"), qualified("BBB")], regime=False)
    no_rs = signal("AAA", score=92)
    no_rs["details"] = {"rs_slope": None}
    result = run_rescore(
        factory_for(StubProcessor([analysis("AAA"), analysis("BBB")])),
        score_from({"AAA": no_rs, "BBB": signal("BBB", score=90, rs=0.3)}),
        tmp_path, 500, FRIDAY, False, False,
    )
    assert result["status"] == "written", result
    points = {p["ticker"]: p for p in mm.load_frames(tmp_path, run_kinds=(mm.RUN_KIND_INTRADAY,))[0][0]["points"]}
    assert points["AAA"]["evaluation"] == "not_scored" and points["AAA"]["drop_reason"] == "regime_gate"
    assert points["BBB"]["evaluation"] == "not_qualified"


def test_legacy_only_history_can_seed_a_rescore(tmp_path):
    legacy = mm.build_frame(
        run_kind=mm.RUN_KIND_LEGACY, generated_at=FRIDAY, session_date="2026-09-18", provenance="backfill",
        points=[qualified("AAA")], scope={"mode": "legacy_report", "completed": True},
        coverage={"kind": mm.COVERAGE_TOP50, "qualified_total": 300, "located_points": 1},
    )
    mm.write_frame(legacy, tmp_path)
    result = run_rescore(
        factory_for(StubProcessor([analysis("AAA")])), score_from({"AAA": signal("AAA")}),
        tmp_path, 500, FRIDAY, False, False,
    )
    assert result["status"] == "written", result
    frame = mm.load_frames(tmp_path, run_kinds=(mm.RUN_KIND_INTRADAY,))[0][0]
    assert frame["scope"]["candidate_source_run_id"] == legacy["run_id"]


def test_a_mostly_failed_run_is_not_recorded_as_an_observation(tmp_path):
    seed_daily(tmp_path, [qualified(t) for t in ("A1", "A2", "A3", "A4")])
    result = run_rescore(
        factory_for(StubProcessor([analysis("A1")])), score_from({"A1": signal("A1")}),
        tmp_path, 500, FRIDAY, False, False,
    )
    assert result["status"] == "failed" and "too_many_failures" in result["reason"]
    assert intraday_files(tmp_path) == []
