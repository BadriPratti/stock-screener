import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import run_optimized_scan as scanner
from src.screening import pick_history


@pytest.mark.parametrize(
    ("run_kind", "test_mode", "record_motion", "expected"),
    [
        ("midday-sample", False, False, {"write_canonical_latest": False, "record_history": False, "record_market_motion": False}),
        ("midday-sample", False, True, {"write_canonical_latest": False, "record_history": False, "record_market_motion": False}),
        ("midday-sample", True, True, {"write_canonical_latest": False, "record_history": False, "record_market_motion": False}),
        ("daily-full", False, False, {"write_canonical_latest": True, "record_history": True, "record_market_motion": True}),
        ("daily-full", False, True, {"write_canonical_latest": True, "record_history": True, "record_market_motion": True}),
        ("daily-full", True, True, {"write_canonical_latest": True, "record_history": False, "record_market_motion": False}),
        ("local", False, False, {"write_canonical_latest": True, "record_history": False, "record_market_motion": False}),
        ("local", False, True, {"write_canonical_latest": True, "record_history": False, "record_market_motion": True}),
        ("local", True, True, {"write_canonical_latest": True, "record_history": False, "record_market_motion": False}),
    ],
)
def test_resolve_output_policy_truth_table(run_kind, test_mode, record_motion, expected):
    assert scanner.resolve_output_policy(run_kind, test_mode, record_motion) == expected


def test_resolve_output_policy_rejects_unknown_kind():
    with pytest.raises(ValueError, match="Unknown run kind"):
        scanner.resolve_output_policy("surprise", False)


def _minimal_results():
    return {
        "total_processed": 100,
        "total_analyzed": 50,
        "processing_time_seconds": 60,
        "actual_tps": 1.25,
        "error_rate": 0,
    }


def test_save_report_skips_latest_but_writes_dated_report_and_run_kind(tmp_path, monkeypatch):
    latest = tmp_path / "latest_optimized_scan.txt"
    original = b"canonical morning report\n"
    latest.write_bytes(original)
    monkeypatch.setattr(scanner, "format_benchmark_summary", lambda *_: "Benchmark summary")

    dated = scanner.save_report(
        _minimal_results(), [], [], {}, {}, output_dir=tmp_path,
        write_latest=False, run_kind="midday-sample",
    )

    assert dated.exists()
    assert dated.name.startswith("optimized_scan_")
    assert latest.read_bytes() == original
    lines = dated.read_text(encoding="utf-8").splitlines()
    generated_index = next(i for i, line in enumerate(lines) if line.startswith("Generated:"))
    assert lines[generated_index + 1] == "Run Kind: midday-sample"


def test_save_report_write_latest_default_behaviour_is_preserved(tmp_path, monkeypatch):
    monkeypatch.setattr(scanner, "format_benchmark_summary", lambda *_: "Benchmark summary")

    dated = scanner.save_report(
        _minimal_results(), [], [], {}, {}, output_dir=tmp_path, run_kind="daily-full",
    )

    latest = tmp_path / "latest_optimized_scan.txt"
    assert latest.read_bytes() == dated.read_bytes()
    lines = latest.read_text(encoding="utf-8").splitlines()
    generated_index = next(i for i, line in enumerate(lines) if line.startswith("Generated:"))
    assert lines[generated_index + 1] == "Run Kind: daily-full"


def test_run_kind_parser_default_and_invalid_choice():
    defaults = scanner.build_arg_parser().parse_args([])
    assert defaults.run_kind == "local"
    assert defaults.record_market_motion is False
    assert scanner.build_arg_parser().parse_args(["--record-market-motion"]).record_market_motion is True
    with pytest.raises(SystemExit):
        scanner.build_arg_parser().parse_args(["--run-kind", "invalid"])


def test_record_pick_history_fails_soft_and_emits_annotation(monkeypatch, caplog, capsys):
    def fail(**_kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(pick_history, "record_scan", fail)
    with caplog.at_level(logging.ERROR):
        result = scanner.record_pick_history(
            shortlist=[], top20=[],
            scope={"total_universe": 100, "analyzed": 50, "completed": True},
            source={},
        )

    assert result is None
    assert "Pick history ledger write failed: disk unavailable" in caplog.text
    assert (
        "::warning title=pick-history::ledger write failed: disk unavailable"
        in capsys.readouterr().out
    )
