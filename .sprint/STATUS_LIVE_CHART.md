PLAN: SPRINT_PLAN_LIVE_CHART.md  (planned 2026-09-20; NOT approved; nothing built)

MM-001 | Claude      | COMPLETE (market_motion.py + 41 tests incl. brute-force cross-check, real git check-ignore; .gitignore whitelists data/market_motion/**)
MM-002 | Codex       | COMPLETE after lead review (frame writer, workflow staging, ci_push_with_rebase.sh; lead added: -X theirs fallback from attempt 3 with tests, `bash` invocation, qualified-without-RS made valid so one bad reading cannot cost the frame, phase 1/2 unscored != downtrend)
MM-003 | Claude      | COMPLETE (5 legacy frames written under data/market_motion/snapshots/legacy_report; 8 tests incl. real-git: 84 distinct tickers, 25 in all five; rerun byte-identical)
MM-004 | Codex       | COMPLETE after lead review (run_intraday_rescore.py + src/screening/intraday_rescore.py; isolates progress/price/fundamentals cache; 132 tests green)
MM-005 | Claude      | COMPLETE (/api/market-motion, /latest, /tracker + /api/scan path containment; 13 new tests; verified on the real 5 frames)
MM-006 | Codex       | COMPLETE (publisher via git plumbing, scheduler default OFF, control API; 151 tests green; lead review pending)
MM-007 | Claude      | COMPLETE (static/js/core/market-motion.js + tests/js/test_market_motion.js; all 13 JS test files pass)
MM-008 | Codex       | COMPLETE (map, replay, filters, tracked table, scheduler card, Expand; lead browser check found and fixed a real overlay-plugin bug (vectors shape) + regression test; 23 JS files green)
MM-009 | Antigravity | Phase A review DONE and dispositioned; UI audit skipped to save cost (lead did a real browser pass instead)
MM-010 | Claude      | COMPLETE (290 Python + 23 JS files green; real browser pass on the live map with the seeded 395-buy frame; scheduler still OFF; nothing committed/pushed/dispatched)

AMENDMENT 1 applied: persistent tiered tracker (ACTIVE/WATCHING/RETIRED), per-stock streaks, bigger map + filters + tracked table.
Open user decisions: scheduler location/cadence, intraday storage local vs git, phase ordering vs chart modal, seeding scan, retention window (default 10 sessions).

AMENDMENT 2: user decisions recorded (in-app scheduler OFF by default; store on GitHub; order A -> modal -> B; seed scan yes; retention 10).

SEEDING scan DONE 2026-09-20 (local, 67.8 min): frame 20260920T225418Z-daily_full, session 2026-09-18, 395 qualified + 7 not_scored, provenance local. pick-history ledger untouched.

OUT-OF-PLAN FIX 2026-09-22: /api/sync could not recover from an UNTRACKED file blocking `git pull` (only handled the tracked-file variant). Fixed in dashboard.py (_safe_untracked_conflict_paths) + 7 tests in tests/test_sync_untracked_conflict.py, all passing. Only deletes files verified inside data/, confirmed untracked by git, never position/.
OUT-OF-PLAN FIX 2026-09-22: numpy.bool_ identity bug (`is_buy is True`) in market_motion.outcome_point + intraday_rescore._points_from_analyses silently marked every genuinely-qualifying stock as not_qualified during intraday re-scores. Fixed both sites, added regression tests using a real numpy-bool-like object, re-ran the corrected intraday rescore (348 qualified / 50 dropped / 1 not_qualified / 3 error — a sane distribution).
