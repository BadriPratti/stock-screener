# MR-005 — Market reorg test reconciliation

## Changed

- Updated `tests/js/test_market_map_component.js` for the lazy tracked-stock disclosure.
- The initial HTML assertions now require `aria-expanded="false"`, the visible `Tracked stocks (2)` count, and a hidden, empty table container with no eager headers or rows.
- The test opens the disclosure through the controller's click listener before asserting sortable headers, escaped ticker content, and all two currently visible tracked rows; enabling retired stocks then verifies all three tracker records remain covered.
- Added a close/reopen assertion proving the table is built only once.

## Acceptance-criteria audit

- `test_market_sections.js` already covers tab/panel ARIA state, roving `tabIndex`, ArrowLeft/ArrowRight/Home/End navigation, session restoration, invalid-value fallback, and a single lazy map mount reused across tab switches.
- The lifecycle gap was controller behavior. Added assertions that deactivation pauses replay and closes the Expand overlay, while reactivation resizes and repaints the existing chart without a fetch.
- No new test file was needed; the controller-backed coverage fits the existing component characterization test.

## Verification

- `for f in tests/js/*.js; do node "$f" || echo "FAIL $f"; done` — 24 of 24 test files passed; zero `FAIL` lines.
- `venv/bin/python -m pytest tests/test_dashboard_jobs.py -q` — 8 passed in 0.12s.
- Repository-style `node --input-type=module -e "...await import('./static/js/dashboard.js')..."` DOM/fetch/timer-stub graph load — passed and printed `dashboard module graph loaded`.
- `git diff --check -- tests/js/test_market_map_component.js` — clean.

## MR-006 browser-pass risk

- Verify the real Chart.js canvas visibly resizes after leaving and returning to Map in pywebview/WebKit, without a second data request or canvas-reuse error.
- Verify suspending Map closes the expanded dialog, restores the card to the correct panel, and leaves focus in a sensible place when that panel is hidden.
- Verify the disclosure count, chevron state, table sizing, and keyboard-sort focus behavior in the real browser after first open and reopen.
