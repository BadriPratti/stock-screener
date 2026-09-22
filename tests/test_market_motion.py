"""Tests for src/screening/market_motion.py (frames + derived tracker)."""

import json
import random
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.screening import market_motion as mm

ROOT = Path(__file__).resolve().parents[1]
EMOJI = "\U0001F7E2⭐⚠✓"


def q(ticker, score=100.0, rs=0.3, **extra):
    return mm.make_point(ticker, mm.EVAL_QUALIFIED, score=score, rs=rs, phase=2, entry_quality="Good", **extra)


def nq(ticker, score=50.0, rs=0.1):
    return mm.make_point(ticker, mm.EVAL_NOT_QUALIFIED, score=score, rs=rs, phase=2, drop_reason="below_buy_threshold")


def ns(ticker, why="phase_3"):
    return mm.make_point(ticker, mm.EVAL_NOT_SCORED, phase=3, drop_reason=why)


def ne(ticker):
    return mm.make_point(ticker, mm.EVAL_NOT_EVALUATED)


def frame(day, points, kind=mm.RUN_KIND_DAILY_FULL, hour=17, minute=0, coverage=None,
          completed=True, version=mm.SCORING_VERSION):
    gen = datetime.fromisoformat(day).replace(hour=hour, minute=minute, tzinfo=timezone.utc)
    f = mm.build_frame(
        run_kind=kind, generated_at=gen, session_date=day, points=points,
        scope={"mode": "full_universe", "completed": completed},
        coverage=coverage, scoring_version=version,
    )
    return f


def days(n, start="2026-09-14"):
    d = datetime.fromisoformat(start)
    out = []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.date().isoformat())
        d += timedelta(days=1)
    return out


# --- points ---------------------------------------------------------------

def test_make_point_strips_emoji_drops_non_finite_and_never_zero_fills():
    p = mm.make_point(" lila ", mm.EVAL_QUALIFIED, score=float("nan"), rs="x", phase="2",
                      top_reason=f"{EMOJI} Good Stage 2", entry_quality=None)
    assert p["ticker"] == "LILA"
    assert "score" not in p and "rs" not in p          # missing stays missing, never 0
    assert p["phase"] == 2
    assert p["top_reason"] == "Good Stage 2"
    with pytest.raises(ValueError):
        mm.make_point("A", "nonsense")


def test_normalize_buy_signal_maps_scanner_fields():
    sig = {"ticker": "sun", "is_buy": True, "score": 112.46, "phase": 2, "entry_quality": "Good",
           "stop_loss": 70.5, "risk_reward_ratio": 5.6, "current_price": 74.12,
           "details": {"rs_slope": 0.355}, "reasons": [f"{EMOJI} Strong RS", "second"]}
    p = mm.normalize_buy_signal(sig, rank=1)
    assert p == {"ticker": "SUN", "evaluation": "qualified", "score": 112.46, "rs": 0.355, "phase": 2,
                 "entry_quality": "Good", "current_price": 74.12, "stop_loss": 70.5, "rr_ratio": 5.6,
                 "rank": 1, "top_reason": "Strong RS"}
    flat = mm.normalize_buy_signal({"ticker": "A", "score": 90, "rs": 0.1, "rr_ratio": 2.0})
    assert flat["rs"] == 0.1 and flat["rr_ratio"] == 2.0


def test_outcome_point_handles_numpy_bool_is_buy():
    # score_buy_signal's is_buy is numpy.bool_, not Python bool (it comes from
    # a numpy-typed score comparison) -- `numpy.bool_(True) is True` is False,
    # a real bug that silently misclassified every qualifying stock as
    # not_qualified. Reproduced here without a numpy dependency in this test
    # file by using a minimal stand-in with the same `is True` failure mode.
    class NumpyLikeBool:
        def __init__(self, value):
            self._value = bool(value)
        def __bool__(self):
            return self._value
        def __eq__(self, other):
            return self._value == other

    true_ish = NumpyLikeBool(True)
    assert (true_ish is True) is False, "the stand-in must reproduce the real numpy.bool_ identity failure"
    qualifies = mm.outcome_point("ET", signal={"is_buy": true_ish, "score": 107.9, "phase": 2, "details": {"rs_slope": 0.005}})
    assert qualifies["evaluation"] == "qualified" and qualifies["score"] == 107.9

    false_ish = NumpyLikeBool(False)
    below = mm.outcome_point("X", signal={"is_buy": false_ish, "score": 55.0, "phase": 2, "details": {"rs_slope": 0.1}})
    assert below["evaluation"] == "not_qualified"


def test_outcome_point_states():
    below = mm.outcome_point("A", signal={"is_buy": False, "score": 57.2, "phase": 2, "details": {"rs_slope": 0.02}})
    assert below["evaluation"] == "not_qualified" and below["score"] == 57.2 and below["rs"] == 0.02
    unscored = mm.outcome_point("B", signal={"is_buy": False, "score": 0, "reason": "Not in Phase 2 (currently Phase 3)", "details": {}}, phase=3)
    assert unscored["evaluation"] == "not_scored" and "score" not in unscored and unscored["phase"] == 3
    assert mm.outcome_point("C", error="price_data_unavailable")["evaluation"] == "error"
    assert mm.outcome_point("D")["evaluation"] == "not_evaluated"
    assert mm.outcome_point("E", phase=4)["drop_reason"] == "phase_4"
    buy = mm.outcome_point("F", signal={"is_buy": True, "score": 80, "phase": 2, "details": {"rs_slope": 0.2}})
    assert buy["evaluation"] == "qualified"


def test_qualified_buy_without_an_rs_reading_is_valid_but_has_no_position():
    no_rs = mm.normalize_buy_signal({"ticker": "NORS", "is_buy": True, "score": 90, "phase": 2, "details": {"rs_slope": None}})
    assert "rs" not in no_rs and no_rs["evaluation"] == "qualified"
    d = days(2)
    f1 = frame(d[0], [q("A"), no_rs])
    mm.validate_frame(f1)                                # one bad reading must not cost the whole frame
    t = mm.compute_tracker([f1, frame(d[1], [q("A"), no_rs])])
    r = t["tickers"]["NORS"]
    assert r["current_streak_days"] == 2 and r["position"] is None and r["latest"]["score"] == 90


def test_phase_only_outcomes_do_not_call_phase_1_or_2_a_downtrend():
    assert mm.outcome_point("E", phase=4)["drop_reason"] == "phase_4"
    assert mm.outcome_point("F", phase=2)["drop_reason"] == "not_scored"
    assert mm.outcome_point("G", phase=1)["drop_reason"] == "not_scored"


def test_dedupe_keeps_first_order_and_best_information():
    pts = mm.dedupe_points([ne("A"), q("B", score=70, rank=5), q("A", score=90, rank=2), q("B", score=99, rank=1), {"ticker": ""}])
    assert [p["ticker"] for p in pts] == ["A", "B"]
    assert pts[0]["evaluation"] == "qualified"
    assert pts[1]["rank"] == 1


# --- frames / store -------------------------------------------------------

def test_build_frame_shape_and_validation(tmp_path):
    f = frame("2026-09-18", [q("AAA"), nq("BBB"), ns("CCC")])
    assert f["run_id"] == "20260918T170000Z-daily_full"
    assert f["score_model"] == {"max_score": 125, "buy_threshold": 60, "rs_metric": "rs_slope_20"}
    assert f["coverage"]["kind"] == "complete_for_scope" and f["coverage"]["qualified_total"] == 1
    mm.validate_frame(f)
    path = mm.write_frame(f, tmp_path)
    assert path == tmp_path / "snapshots" / "daily_full" / "20260918T170000Z-daily_full.json"
    assert json.loads(path.read_text())["points"][0]["ticker"] == "AAA"
    assert not list(path.parent.glob(".*.tmp"))


@pytest.mark.parametrize("mutate,msg", [
    (lambda f: f.update(schema_version=2), "schema_version"),
    (lambda f: f.update(run_kind="x"), "run_kind"),
    (lambda f: f.update(session_date="2026-13-01"), "session_date"),
    (lambda f: f.update(run_id="bad"), "run_id"),
    (lambda f: f["scope"].update(completed="yes"), "completed"),
    (lambda f: f["coverage"].update(kind="???"), "coverage"),
    (lambda f: f["points"].append(dict(f["points"][0])), "duplicate"),
    (lambda f: f["points"][0].pop("score"), "finite score"),
    (lambda f: f["points"].__setitem__(0, mm.make_point("AAA", mm.EVAL_NOT_QUALIFIED, score=50)), "finite rs"),
    (lambda f: f["points"][0].update(rs=float("nan")), "rs must be finite"),
    (lambda f: f["points"][0].update(ticker="not a ticker"), "ticker"),
    (lambda f: f["points"][0].update(evaluation="maybe"), "evaluation"),
])
def test_validation_rejects_bad_frames(mutate, msg):
    f = frame("2026-09-18", [q("AAA")])
    mutate(f)
    with pytest.raises(ValueError, match=msg):
        mm.validate_frame(f)


def test_failed_validation_leaves_existing_file_intact(tmp_path):
    f = frame("2026-09-18", [q("AAA")])
    path = mm.write_frame(f, tmp_path)
    before = path.read_bytes()
    bad = json.loads(json.dumps(f))
    bad["points"][0]["score"] = float("nan")
    with pytest.raises(ValueError):
        mm.write_frame(bad, tmp_path)
    assert path.read_bytes() == before
    assert not list(path.parent.glob(".*.tmp"))


def test_same_run_id_replaces_but_new_time_is_a_new_observation(tmp_path):
    a = frame("2026-09-18", [q("AAA", score=90)], kind=mm.RUN_KIND_INTRADAY, hour=15)
    mm.write_frame(a, tmp_path)
    mm.write_frame(frame("2026-09-18", [q("AAA", score=95)], kind=mm.RUN_KIND_INTRADAY, hour=15), tmp_path)
    mm.write_frame(frame("2026-09-18", [q("AAA", score=99)], kind=mm.RUN_KIND_INTRADAY, hour=17), tmp_path)
    frames, warnings = mm.load_frames(tmp_path)
    assert warnings == []
    assert [f["points"][0]["score"] for f in frames] == [95, 99]


def test_load_frames_skips_corrupt_incomplete_and_misnamed(tmp_path):
    mm.write_frame(frame("2026-09-17", [q("AAA")]), tmp_path)
    mm.write_frame(frame("2026-09-18", [q("AAA")], completed=False), tmp_path)
    d = tmp_path / "snapshots" / "daily_full"
    (d / "20260916T170000Z-daily_full.json").write_text("{not json")
    good = frame("2026-09-15", [q("AAA")])
    (d / "20260915T999999Z-daily_full.json").write_text(json.dumps(good))
    (d / ".hidden.json").write_text("{}")
    frames, warnings = mm.load_frames(tmp_path)
    assert [f["session_date"] for f in frames] == ["2026-09-17"]
    assert len(warnings) == 2 and all(w.startswith("Skipped daily_full/") for w in warnings)
    frames_all, _ = mm.load_frames(tmp_path, completed_only=False)
    assert len(frames_all) == 2


def test_thin_intraday_keeps_last_of_day_beyond_retention(tmp_path):
    for i, d in enumerate(days(4)):
        for h in (14, 16, 18):
            mm.write_frame(frame(d, [q("A")], kind=mm.RUN_KIND_INTRADAY, hour=h), tmp_path)
    removed = mm.thin_intraday(tmp_path, keep_full_sessions=2)
    assert len(removed) == 4                      # 2 old dates x 2 dropped frames
    frames, _ = mm.load_frames(tmp_path)
    per_day = {}
    for f in frames:
        per_day.setdefault(f["session_date"], []).append(f["generated_at"][11:13])
    assert per_day[days(4)[0]] == ["18"] and per_day[days(4)[1]] == ["18"]
    assert per_day[days(4)[2]] == ["14", "16", "18"]


# --- daily session selection ----------------------------------------------

def test_full_live_frame_beats_top50_legacy_for_the_same_date():
    legacy = frame("2026-09-18", [q("AAA")], kind=mm.RUN_KIND_LEGACY, coverage={"kind": "top50_only"})
    live = frame("2026-09-18", [q("AAA"), q("BBB")], hour=18)
    later_legacy = frame("2026-09-18", [q("AAA")], kind=mm.RUN_KIND_LEGACY, hour=23, coverage={"kind": "top50_only"})
    chosen = mm.select_daily_sessions([legacy, later_legacy, live])
    assert len(chosen) == 1 and chosen[0]["run_kind"] == "daily_full"
    intraday = frame("2026-09-19", [q("AAA")], kind=mm.RUN_KIND_INTRADAY)
    assert mm.select_daily_sessions([intraday]) == []          # intraday is never a session record


# --- tracker --------------------------------------------------------------

def test_friday_to_monday_is_consecutive_and_streak_ends_at_latest():
    fs = [frame("2026-09-17", [q("A")]), frame("2026-09-18", [q("A")]), frame("2026-09-21", [q("A")])]
    t = mm.compute_tracker(fs)
    r = t["tickers"]["A"]
    assert (r["current_streak_days"], r["longest_streak_days"], r["tier"]) == (3, 3, "active")
    assert t["sessions"] == ["2026-09-17", "2026-09-18", "2026-09-21"]
    assert (r["sessions_qualified"], r["sessions_observed"]) == (3, 3)


def test_not_qualified_breaks_streak_and_counts_in_denominator():
    fs = [frame(d, p) for d, p in zip(days(4), [[q("A")], [q("A")], [nq("A")], [q("A")]])]
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert (r["current_streak_days"], r["longest_streak_days"]) == (1, 2)
    assert (r["sessions_qualified"], r["sessions_observed"]) == (3, 4)


def test_unknown_session_breaks_streak_but_is_excluded_from_denominator():
    d = days(4)
    fs = [frame(d[0], [q("A")]), frame(d[1], [q("A")]), frame(d[2], [ne("A")]), frame(d[3], [q("A")])]
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert r["current_streak_days"] == 1               # cannot claim it was good across the gap
    assert r["longest_streak_days"] == 2
    assert (r["sessions_qualified"], r["sessions_observed"], r["unknown_sessions"]) == (3, 3, 1)
    # absent from a frame entirely is the same as unknown, never a miss
    fs2 = [frame(d[0], [q("A")]), frame(d[1], [q("B")]), frame(d[2], [q("A")])]
    r2 = mm.compute_tracker(fs2)["tickers"]["A"]
    assert (r2["sessions_qualified"], r2["sessions_observed"], r2["unknown_sessions"]) == (2, 2, 1)


def test_top50_only_sessions_are_unknown_for_unlocated_tickers_and_reported():
    d = days(3)
    legacy = coverage = {"kind": "top50_only", "qualified_total": 479}
    fs = [frame(d[0], [q("A")], kind=mm.RUN_KIND_LEGACY, coverage=legacy),
          frame(d[1], [q("A")], kind=mm.RUN_KIND_LEGACY, coverage=coverage),
          frame(d[2], [q("A"), q("Z")])]
    t = mm.compute_tracker(fs)
    assert t["top50_only_sessions"] == d[:2]
    z = t["tickers"]["Z"]
    assert (z["current_streak_days"], z["sessions_observed"], z["unknown_sessions"]) == (1, 1, 2)
    assert t["tickers"]["A"]["current_streak_days"] == 3


def test_zero_qualifier_session_is_an_observation_that_breaks_streaks():
    d = days(3)
    fs = [frame(d[0], [q("A")]), frame(d[1], [nq("A")]), frame(d[2], [q("A")])]
    assert mm.compute_tracker(fs)["tickers"]["A"]["current_streak_days"] == 1


def test_tiers_watching_then_retired_then_repromoted():
    d = days(14)
    fs = [frame(d[0], [q("A")])] + [frame(x, [q("B"), nq("A")]) for x in d[1:11]]      # 10 sessions since A qualified
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert (r["sessions_since_qualified"], r["tier"], r["current_streak_days"]) == (10, "watching", 0)
    fs.append(frame(d[11], [q("B"), nq("A")]))                                        # 11 -> retired
    assert mm.compute_tracker(fs)["tickers"]["A"]["tier"] == "retired"
    fs.append(frame(d[12], [q("A"), q("B")]))
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert (r["tier"], r["current_streak_days"], r["longest_streak_days"]) == ("active", 1, 1)
    assert mm.compute_tracker(fs)["counts"] == {"active": 2, "watching": 0, "retired": 0}


def test_window_limits_denominator_but_not_streak_or_tier():
    d = days(6)
    fs = [frame(x, [q("A")]) for x in d]
    r = mm.compute_tracker(fs, window=3)["tickers"]["A"]
    assert (r["sessions_qualified"], r["sessions_observed"]) == (3, 3)
    assert r["current_streak_days"] == 6
    t = mm.compute_tracker(fs, window=99)
    assert t["denominator_sessions"] == 6 and t["sessions_available"] == 6


def test_score_trend_only_within_a_scoring_version():
    d = days(3)
    same = mm.compute_tracker([frame(d[0], [q("A", 90)]), frame(d[1], [q("A", 100)])])["tickers"]["A"]
    assert same["score_trend"] == 10
    crossed = mm.compute_tracker([frame(d[0], [q("A", 90)], version="v1"), frame(d[1], [q("A", 100)], version="v2")])["tickers"]["A"]
    assert crossed["score_trend"] is None
    unscored = mm.compute_tracker([frame(d[0], [q("A", 90)]), frame(d[1], [ns("A")])])["tickers"]["A"]
    assert unscored["score_trend"] is None and unscored["latest_daily_score"] == 90


def test_position_holds_last_real_coordinates_and_flags_staleness():
    d = days(2)
    fs = [frame(d[0], [q("A", score=100, rs=0.4)]), frame(d[1], [ns("A", "Fails Minervini trend template")])]
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert r["position"]["score"] == 100 and r["position"]["rs"] == 0.4
    assert r["position"]["is_current"] is False          # newer frame exists but had no coordinates
    assert r["latest"]["evaluation"] == "not_scored" and r["latest"]["drop_reason"].startswith("Fails Minervini")
    fs.append(frame(d[1], [nq("A", 55, 0.05)], hour=20))
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert (r["position"]["score"], r["position"]["is_current"]) == (55, True)


def test_intraday_frames_move_position_and_frame_streak_but_never_the_day_streak():
    d = "2026-09-18"
    fs = [frame(d, [q("A", 90)], hour=13)]
    fs += [frame(d, [q("A", 90 + i)], kind=mm.RUN_KIND_INTRADAY, hour=14 + 2 * i) for i in range(4)]
    t = mm.compute_tracker(fs)
    r = t["tickers"]["A"]
    assert r["current_streak_days"] == 1 and t["sessions_available"] == 1
    assert r["current_streak_frames"] == 5
    assert r["position"]["score"] == 93 and r["latest"]["run_kind"] == "intraday_rescore"
    fs.append(frame(d, [nq("A", 55, 0.0)], kind=mm.RUN_KIND_INTRADAY, hour=23))
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert r["current_streak_frames"] == 0 and r["current_streak_days"] == 1


def test_frame_streak_never_crosses_session_dates():
    d = days(2)
    fs = [frame(d[0], [q("A")]), frame(d[1], [q("A")], hour=13),
          frame(d[1], [q("A")], kind=mm.RUN_KIND_INTRADAY, hour=15)]
    r = mm.compute_tracker(fs)["tickers"]["A"]
    assert r["current_streak_days"] == 2
    assert r["current_streak_frames"] == 2        # today's daily + intraday only, not yesterday's


def test_history_is_capped_and_marks_unknown():
    d = days(5)
    fs = [frame(d[0], [q("A")]), frame(d[1], [q("B")]), frame(d[2], [nq("A", 50, 0.1)])]
    h = mm.compute_tracker(fs, history_cap=2)["tickers"]["A"]["history"]
    assert [e["state"] for e in h] == ["unknown", "not_qualified"]
    assert h[1]["score"] == 50


def test_tracked_set_and_roster_order_cap_and_overflow():
    d = days(4)
    fs = [frame(d[0], [q("W1", 80), q("R", 70)]),
          frame(d[1], [q("W2", 85), q("W1", 80)]),
          frame(d[2], [q("W2", 85)]),
          frame(d[3], [q("A1", 95), q("A2", 105), q("W2", 85), nq("W1", 50, 0.0)])]
    assert mm.tracked_tickers(fs) == {"W1", "R", "W2", "A1", "A2"}
    t = mm.compute_tracker(fs, retire_after=1)
    tiers = {k: v["tier"] for k, v in t["tickers"].items()}
    assert tiers == {"A1": "active", "A2": "active", "W2": "active", "W1": "retired", "R": "retired"}
    roster = mm.build_roster(t, cap=2)
    assert roster["tickers"] == ["A2", "A1"] and roster["overflow"] == 1 and roster["active"] == 3
    t = mm.compute_tracker(fs, retire_after=5)
    roster = mm.build_roster(t, cap=500)
    assert roster["tickers"][:3] == ["A2", "A1", "W2"]                 # active by score desc
    assert roster["tickers"][3:] == ["W1", "R"]                        # watching by recency (W1 1 session, R 3)
    assert mm.build_roster(t, cap=0)["tickers"] == []


def test_empty_input_is_a_valid_empty_tracker():
    t = mm.compute_tracker([])
    assert t["sessions_available"] == 0 and t["tickers"] == {} and t["newest_frame"] is None
    assert mm.build_roster(t)["tickers"] == []


def test_session_date_comes_from_the_data_not_the_wall_clock():
    import pandas as pd
    assert mm.session_date_from_bar(pd.Timestamp("2026-09-18")) == "2026-09-18"
    assert mm.session_date_from_bar(pd.Timestamp("2026-09-18", tz="America/New_York")) == "2026-09-18"
    # 03:00 UTC on the 19th is still the evening of the 18th in New York
    assert mm.session_date_from_bar(datetime(2026, 9, 19, 3, 0, tzinfo=timezone.utc)) == "2026-09-18"
    assert mm.session_date_from_bar("2026-09-18T00:00:00") == "2026-09-18"
    with pytest.raises(ValueError):
        mm.session_date_from_bar(12345)
    sunday = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)
    assert mm.is_data_current("2026-09-18", now=sunday) is False      # weekend run holds Friday data
    monday = datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc)
    assert mm.is_data_current("2026-09-21", now=monday) is True
    assert mm.is_data_current("2026-09-18", now=monday) is False      # holiday / no bar yet


# --- brute-force cross-check ---------------------------------------------

def _reference(states):
    """Independent streak / denominator reference over 'Q','N','U' strings."""
    longest = run = 0
    for s in states:
        run = run + 1 if s == "Q" else 0
        longest = max(longest, run)
    cur = 0
    for s in reversed(states):
        if s != "Q":
            break
        cur += 1
    return cur, longest, states.count("Q"), sum(1 for s in states if s != "U")


def test_random_sessions_match_a_reference_implementation():
    rng = random.Random(20260920)
    for _ in range(150):
        n = rng.randint(1, 14)
        d = days(n)
        states = ["Q"] + [rng.choice("QQNU") for _ in range(n - 1)]
        rng.shuffle(states)
        if "Q" not in states:
            states[0] = "Q"
        fs = []
        for day, s in zip(d, states):
            pts = [q("ANCHOR")]
            pts.append({"Q": q("T"), "N": nq("T"), "U": ne("T")}[s])
            if s == "U" and rng.random() < 0.5:
                pts = [p for p in pts if p["ticker"] != "T"]
            fs.append(frame(day, pts))
        r = mm.compute_tracker(fs)["tickers"]["T"]
        cur, longest, qn, obs = _reference(states)
        assert (r["current_streak_days"], r["longest_streak_days"], r["sessions_qualified"], r["sessions_observed"]) == (cur, longest, qn, obs), states


# --- repository hygiene ---------------------------------------------------

def _git():
    """First git that actually runs (macOS's /usr/bin/git shim can be broken)."""
    for candidate in (shutil.which("git"), "/Library/Developer/CommandLineTools/usr/bin/git"):
        if candidate and subprocess.run([candidate, "--version"], capture_output=True).returncode == 0:
            return candidate
    pytest.skip("no usable git binary")


@pytest.mark.parametrize("rel,ignored", [
    ("data/market_motion/snapshots/daily_full/20260918T170000Z-daily_full.json", False),
    ("data/market_motion/snapshots/intraday_rescore/20260918T173500Z-intraday_rescore.json", False),
    ("data/market_motion/snapshots/legacy_report/20260918T170746Z-legacy_report.json", False),
    ("data/market_motion/snapshots/daily_full/.20260918T170000Z-daily_full.json.abc123.tmp", True),
])
def test_gitignore_tracks_frames_but_not_temp_files(rel, ignored):
    res = subprocess.run([_git(), "check-ignore", "-q", rel], cwd=ROOT)
    assert (res.returncode == 0) is ignored


def test_position_directory_is_still_ignored():
    assert subprocess.run([_git(), "check-ignore", "-q", "position/anything.csv"], cwd=ROOT).returncode == 0
