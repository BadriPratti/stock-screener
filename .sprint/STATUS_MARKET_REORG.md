PLAN: SPRINT_PLAN_MARKET_REORG.md (planned 2026-09-22; NOT approved; nothing built)

MR-001 | Claude | COMPLETE (dashboard.css: .market-section-tabs/.market-section-tab, panel[hidden], tracked-table disclosure, 760px + reduced-motion rules)
MR-002 | Codex  | COMPLETE (4 panels, section tabs, sessionStorage, lazy mount; 1 expected cross-task test failure noted)
MR-003 | Codex  | COMPLETE (setActive/suspend/resume, lazy disclosure; same 1 expected cross-task test failure noted)
MR-004 | Claude | COMPLETE (_showMarketTicker/_showBuySignal now activate the Signals section before jumping to a row; tracker-row path now uses the map controller's own selectTicker API instead of reaching into its DOM; fixed a real regression in test_market_signal_tabs.js caused by the same change, added an assertion for it)
MR-005 | Codex  | COMPLETE (test_market_map_component.js reconciled + lifecycle assertions added; 24/24 JS files, 8/8 Python, ES-module graph loads)
MR-006 | Claude | COMPLETE (real browser pass: tab switch works, map suspends/resumes with zero extra fetches, canvas resizes correctly to 1171x620, no console errors, tracked-table disclosure opens/builds 402 rows on demand). MARKET REORG SPRINT DONE - nothing committed/pushed.

Council: Codex + Antigravity independent second opinions, both converged on tabs + lazy-mount + reuse existing
a11y pattern. Lead adjudicated 3 disagreements (Breadth/Regime placement -> Antigravity's math, verified;
Buy/Sell nesting -> Codex's lower-risk reuse; tab-state persistence -> Antigravity's sessionStorage over
Codex's router.js hash-subroute, to keep router.js untouched).
