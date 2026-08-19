#!/usr/bin/env python3
"""Backtest Critic — compares the two most recent walk-forward runs, flags any
scoring component whose correlation with real returns is drifting, flipping sign,
or has notably changed, and proposes a reweighting for manual review.

NEVER modifies src/screening/signal_engine.py. Every proposal is written to
data/backtest_critic_proposals/ for you to read and decide on — nothing here
auto-applies a weight change.

Usage:
    python scripts/backtest_critic.py                  # compares the 2 most recent saved runs
    python scripts/backtest_critic.py --baseline data/backtest_history/walk_forward_A.json \
        --current data/backtest_history/walk_forward_B.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path(__file__).parent.parent / "data" / "backtest_history"
PROPOSALS_DIR = Path(__file__).parent.parent / "data" / "backtest_critic_proposals"

COMPONENTS = ['trend_score', 'fundamental_score', 'entry_score', 'rr_score', 'rs_score', 'volume_score']

# Mirrors signal_engine.py's CURRENT weights — kept here for human-readable proposals.
# Must be updated by hand if signal_engine.py's weights change; this script never
# reads or writes signal_engine.py itself.
CURRENT_WEIGHTS = {
    'trend_score': 35, 'fundamental_score': 35, 'entry_score': 25,
    'rr_score': 10, 'rs_score': 10, 'volume_score': 5,
}

DRIFT_THRESHOLD = 0.15       # |delta r| beyond this is flagged as notable drift
SIGN_FLIP_MIN_MAGNITUDE = 0.05  # ignore trivial near-zero "flips" as noise
PROPOSAL_MIN_CORRELATION = 0.25  # only propose reweighting components this strong


def find_two_most_recent_runs():
    files = sorted(HISTORY_DIR.glob("walk_forward_*.json"))
    if len(files) < 2:
        return None, None
    return files[-2], files[-1]


def load(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=str, default=None)
    parser.add_argument('--current', type=str, default=None)
    args = parser.parse_args()

    if args.baseline and args.current:
        baseline_path, current_path = Path(args.baseline), Path(args.current)
    else:
        baseline_path, current_path = find_two_most_recent_runs()
        if baseline_path is None:
            print("Need at least 2 saved walk-forward runs in data/backtest_history/ to compare.")
            print("Run scripts/walk_forward_backtest.py at least twice first (e.g. before/after a code change).")
            sys.exit(1)

    baseline = load(baseline_path)
    current = load(current_path)

    print(f"Comparing baseline: {baseline_path.name}  ({baseline.get('generated', '?')})")
    print(f"           against: {current_path.name}  ({current.get('generated', '?')})")
    print(f"Baseline trades: {baseline['summary'].get('total_trades', 0)} | "
          f"Current trades: {current['summary'].get('total_trades', 0)}\n")

    findings = []

    print(f"{'='*78}")
    print("COMPONENT DRIFT REPORT (correlation with realized return, entry -> exit)")
    print(f"{'='*78}")
    print(f"{'Component':<20}{'Baseline r':<14}{'Current r':<14}{'Delta':<10}{'Flag'}")

    for comp in COMPONENTS:
        r_base = baseline['component_correlations'].get(comp)
        r_curr = current['component_correlations'].get(comp)

        if r_base is None or r_curr is None:
            print(f"{comp:<20}{'n/a':<14}{'n/a':<14}{'':<10}insufficient data in one run")
            continue

        delta = r_curr - r_base
        flag = ""
        if (r_base > SIGN_FLIP_MIN_MAGNITUDE and r_curr < -SIGN_FLIP_MIN_MAGNITUDE) or \
           (r_base < -SIGN_FLIP_MIN_MAGNITUDE and r_curr > SIGN_FLIP_MIN_MAGNITUDE):
            flag = "SIGN FLIP"
            findings.append(f"{comp}: correlation flipped sign ({r_base:+.3f} -> {r_curr:+.3f}) — unreliable, treat cautiously")
        elif abs(delta) >= DRIFT_THRESHOLD:
            direction = "strengthened" if delta > 0 else "weakened"
            flag = f"drift ({direction})"
            findings.append(f"{comp}: correlation {direction} notably ({r_base:+.3f} -> {r_curr:+.3f}, delta {delta:+.3f})")

        r_base_str, r_curr_str, delta_str = f"{r_base:+.3f}", f"{r_curr:+.3f}", f"{delta:+.3f}"
        print(f"{comp:<20}{r_base_str:<14}{r_curr_str:<14}{delta_str:<10}{flag}")

    print(f"\n{'='*78}")
    print("SUMMARY STAT COMPARISON")
    print(f"{'='*78}")
    for key, label in [('win_rate_pct', 'Win rate %'), ('avg_return_pct', 'Avg return %'),
                        ('sharpe_like', 'Sharpe-like'), ('max_drawdown_pct', 'Max drawdown %')]:
        b, c = baseline['summary'].get(key), current['summary'].get(key)
        if b is not None and c is not None:
            print(f"{label:<20}{b:+.2f}  ->  {c:+.2f}   (delta {c - b:+.2f})")

    print(f"\n{'='*78}")
    print("FINDINGS")
    print(f"{'='*78}")
    if findings:
        for f in findings:
            print(f"  - {f}")
    else:
        print("  No notable drift or sign flips detected — components are behaving consistently.")

    print(f"\n{'='*78}")
    print("PROPOSED REWEIGHTING (NOT applied — src/screening/signal_engine.py is untouched)")
    print(f"{'='*78}")
    proposals = []
    for comp in COMPONENTS:
        r_curr = current['component_correlations'].get(comp)
        r_base = baseline['component_correlations'].get(comp)
        if r_curr is None:
            continue
        consistent_direction = r_base is None or (r_curr > 0) == (r_base > 0)
        if abs(r_curr) >= PROPOSAL_MIN_CORRELATION and consistent_direction:
            direction = "increasing" if r_curr > 0 else "decreasing"
            proposals.append({'component': comp, 'current_r': r_curr, 'suggested_direction': direction,
                               'current_weight': CURRENT_WEIGHTS.get(comp)})
            print(f"  - {comp}: current r={r_curr:+.3f} (weight {CURRENT_WEIGHTS.get(comp, '?')} pts) "
                  f"-> consider {direction} its weight")
    if not proposals:
        print(f"  No component currently meets the bar (|r| >= {PROPOSAL_MIN_CORRELATION}, "
              f"consistent with baseline direction) for a reweight proposal.")

    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROPOSALS_DIR / f"critic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps({
        'generated': datetime.now().isoformat(),
        'baseline_run': baseline_path.name, 'current_run': current_path.name,
        'findings': findings, 'proposals': proposals, 'current_weights': CURRENT_WEIGHTS,
    }, indent=2))
    print(f"\nFull report saved to {report_path}")
    print("This is informational only — nothing was auto-applied to the live scoring formula.")


if __name__ == '__main__':
    main()
