PLAN: SPRINT_PLAN_SCORING.md (planned 2026-09-22; NOT approved; nothing built; recommends AGAINST reweighting yet)

Council: Codex full analysis DONE (.sprint/council/codex-scoring.md, 254 lines, very high quality — new bugs found:
breakout-window logic can never trigger as intended; fundamentals block silently exceeds its 35pt cap for 10.8% of
real cache files; old "+0.40/+0.48" correlation claim is unreproducible; sample size can't support current weight
precision; RS/volume negative correlations look like noise/outlier-driven, not real harm).
Antigravity: 1st attempt failed (headless auto-denied python3 command execution). Relaunched with corrected
read-only tool constraints (pid tracked in session) — pending.

SC-001 | Codex | COMPLETE (src/backtesting/frozen_inputs.py: manifest schema, capture/replay modes on walk_forward_backtest.py; CSV storage, sha256-verified; 6/6 tests, 305/306 broader suite (1 pre-existing unrelated failure); zero live-weight changes)
SC-002 | Codex | COMPLETE (25 new details fields exposed; lead independently verified the diff is 57 insertions, 2 deletions, purely additive - only 2 lines removed and both are the exact same dict with score_version added; 8/8 new tests, full suite green)
SC-003 | Codex | COMPLETE (lead independently verified: diffs match spec exactly, +an off-by-one edge-case fix Codex caught that wasn't even specified; 16/16 new tests, 321/322 full suite (1 pre-existing unrelated failure); measured real impact on 867 real Phase-2 tickers: 199 scores changed, 2 buy-threshold flips, 93 previously-unreachable Base/Pivot breakouts now fire, confirmed zero occurrences in 23 historical reports before the fix)
SC-004..009 | all PENDING

AMENDMENT 1: Antigravity's independent pass completed (3rd attempt, after 2 environment failures) and folded in. Numbers spot-checked against raw data, match exactly. One real disagreement (RS/volume negative correlation - real vs noise) resolved in favor of the more rigorous outlier-robust analysis. Task table updated: Antigravity moved to review-only role per established policy.
