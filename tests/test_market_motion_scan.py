from datetime import datetime, timezone
import sys

from src.screening import market_motion as mm
import run_optimized_scan as scanner


class SpyData:
    def __init__(self, values):
        self.index = values
        self.empty = not values

    def __len__(self):
        return len(self.index)


def buy(ticker, score):
    return {
        "ticker": ticker,
        "is_buy": True,
        "score": score,
        "phase": 2,
        "details": {"rs_slope": score / 1000},
        "reasons": ["Strong setup"],
    }


def analysis(ticker, phase):
    return {"ticker": ticker, "phase_info": {"phase": phase}}


def prior_frame(day, points):
    return mm.build_frame(
        run_kind=mm.RUN_KIND_DAILY_FULL,
        generated_at=f"{day}T20:00:00Z",
        session_date=day,
        points=points,
        scope={"mode": "full_universe", "requested": 10, "analyzed": 10, "completed": True},
    )


def test_point_builder_keeps_all_buys_and_each_tracked_outcome_state():
    buys = [buy(f"B{i:03d}", 200 - i) for i in range(120)]
    buys.append(dict(buys[0]))
    tracked = {"B000", "LOW", "PHASE3", "MISSING"}
    scored = {
        "LOW": {
            "ticker": "LOW",
            "is_buy": False,
            "score": 55,
            "phase": 2,
            "details": {"rs_slope": 0.05},
        },
    }

    points = scanner.build_market_motion_points(
        buys,
        [analysis("LOW", 2), analysis("PHASE3", 3)],
        scored,
        tracked,
    )
    by_ticker = {point["ticker"]: point for point in points}

    assert len([point for point in points if point["evaluation"] == "qualified"]) == 120
    assert len(points) == 123
    assert by_ticker["B000"]["rank"] == 1
    assert by_ticker["LOW"]["evaluation"] == "not_qualified"
    assert by_ticker["PHASE3"] == {
        "ticker": "PHASE3", "evaluation": "not_scored", "phase": 3,
        "drop_reason": "phase_3",
    }
    assert by_ticker["MISSING"] == {
        "ticker": "MISSING", "evaluation": "error", "error_code": "not_analyzed",
    }


def test_zero_buy_run_with_analysis_records_a_complete_frame(tmp_path):
    mm.write_frame(prior_frame("2026-09-17", [mm.normalize_buy_signal(buy("OLD", 90), rank=1)]), tmp_path)

    path = scanner.record_market_motion(
        buy_signals=[],
        analyses=[analysis("OLD", 3)],
        scored_signals={},
        tickers=["OLD", "NEW"],
        total_analyzed=1,
        spy_data=SpyData(["2026-09-18"]),
        should_generate_buys=False,
        source={"git_sha": "abc"},
        provenance="live",
        root=tmp_path,
        generated_at=datetime(2026, 9, 18, 20, tzinfo=timezone.utc),
    )

    assert path is not None
    frames, warnings = mm.load_frames(tmp_path)
    assert warnings == []
    current = frames[-1]
    assert current["coverage"]["qualified_total"] == 0
    assert current["points"][0]["ticker"] == "OLD"
    assert current["points"][0]["evaluation"] == "not_scored"
    assert current["scope"] == {
        "mode": "full_universe", "requested": 2, "analyzed": 1, "completed": True,
    }
    assert current["regime"] == {"should_generate_buys": False, "source_run_id": None}
    assert current["source"] == {"git_sha": "abc"}


def test_broken_or_missing_spy_observation_is_skipped(tmp_path, capsys):
    common = {
        "buy_signals": [], "analyses": [], "scored_signals": {}, "tickers": ["A"],
        "should_generate_buys": True, "source": {}, "provenance": "local", "root": tmp_path,
    }
    assert scanner.record_market_motion(
        **common, total_analyzed=0, spy_data=SpyData(["2026-09-18"]),
    ) is None
    assert scanner.record_market_motion(
        **common, total_analyzed=1, spy_data=SpyData([]),
    ) is None
    assert list(tmp_path.rglob("*.json")) == []
    output = capsys.readouterr().out
    assert output.count("::warning title=market-motion::frame skipped:") == 2


def test_frame_writer_failure_is_soft(monkeypatch, tmp_path, capsys):
    def fail(*_args, **_kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(mm, "write_frame", fail)
    result = scanner.record_market_motion(
        buy_signals=[buy("A", 80)], analyses=[analysis("A", 2)], scored_signals={},
        tickers=["A"], total_analyzed=1, spy_data=SpyData(["2026-09-18"]),
        should_generate_buys=True, source={}, provenance="local", root=tmp_path,
    )
    assert result is None
    assert "::warning title=market-motion::frame write failed: disk unavailable" in capsys.readouterr().out


def test_local_flag_records_local_frame_without_pick_history(monkeypatch, tmp_path):
    calls = {"motion": [], "history": []}

    class Universe:
        def fetch_universe(self):
            return ["AAA"]

    class Processor:
        spy_data = SpyData(["2026-09-18"])
        spy_price = 500

        def __init__(self, **_kwargs):
            pass

        def process_batch_parallel(self, *_args, **_kwargs):
            return {
                "analyses": [analysis("AAA", 3)],
                "phase_results": [{"ticker": "AAA", "phase": 3}],
                "total_processed": 1,
                "total_analyzed": 1,
                "processing_time_seconds": 1,
                "actual_tps": 1,
                "error_rate": 0,
            }

    class Fundamentals:
        fmp_available = False

    class Notifier:
        def send_notification(self, **_kwargs):
            return None

        def send_scan_report(self, *_args, **_kwargs):
            return None

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "USStockUniverseFetcher", Universe)
    monkeypatch.setattr(scanner, "OptimizedBatchProcessor", Processor)
    monkeypatch.setattr(scanner, "EnhancedFundamentalsFetcher", Fundamentals)
    monkeypatch.setattr(scanner, "analyze_spy_trend", lambda *_: {})
    monkeypatch.setattr(scanner, "calculate_market_breadth", lambda *_: {})
    monkeypatch.setattr(scanner, "should_generate_signals", lambda *_: {
        "should_generate_buys": False, "should_generate_sells": False,
    })
    monkeypatch.setattr(scanner, "save_report", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(scanner, "record_market_motion", lambda **kwargs: calls["motion"].append(kwargs))
    monkeypatch.setattr(scanner, "record_pick_history", lambda **kwargs: calls["history"].append(kwargs))
    monkeypatch.setattr("src.notifications.email_notifier.EmailNotifier", Notifier)
    monkeypatch.setattr(sys, "argv", ["run_optimized_scan.py", "--run-kind", "local", "--record-market-motion"])

    scanner.main()

    assert len(calls["motion"]) == 1
    assert calls["motion"][0]["provenance"] == "local"
    assert calls["history"] == []
