# Sprint: Organize stocks by category (sector/industry)

STATUS: PLAN ONLY. Nothing built, committed, or pushed.

## Request (user's own words)
"I honestly want these stocks organized by category like technology, insurance, health... so on so forth like
that so I know what I am getting into"

## Council process
Full council, Codex + Antigravity, both independent (`.sprint/council/codex-sector.md`,
`.sprint/council/antigravity-sector.md`). Both converged on nearly everything; one real disagreement, resolved
below.

## Verified starting facts
Sector/industry data is not fetched, cached, or present anywhere in the live scan pipeline today — confirmed by
both agents independently grepping `src/data/fundamentals_fetcher.py`, `src/data/git_storage_fetcher.py`,
`src/screening/optimized_batch_processor.py`, `src/screening/signal_engine.py`, and `run_optimized_scan.py`: zero
hits. (Older, unused `src/data/fetcher.py`/`src/screening/screener.py` have stale sector code that never reaches
the real daily scan.) yfinance provides it for free (`sector`, `industry` on `.info`, confirmed live: ~0.35s/call).

## Converged decisions
1. **Never feed sector/industry into scoring.** It's purely organizational/display — doesn't touch
   `score_buy_signal`, the buy threshold, or ranking order. Kept deliberately separate from the concurrent scoring
   investigation.
2. **Fetch only for stocks the app actually shows or tracks** (Top 20 + sell signals shown in Signals + the
   market-motion tracked roster, capped per run, e.g. 50 misses/day) — never the full ~2,000-3,770-ticker analyzed
   universe. This keeps steady-state cost to a handful of seconds/day.
3. **Cache effectively permanently** (proposed 12-month TTL with self-healing retry for anything that came back
   "Uncategorized") — sector rarely changes, so this is a one-time cost per ticker, not recurring.
4. **A one-time offline backfill script**, run manually/via `workflow_dispatch`, NOT part of the daily CI run — the
   full ~2,600-3,800-ticker backfill would eat 15+ minutes if done inline; kept fully separate.
5. **Two-tier taxonomy: `sector` (standard macro sector) + `category` (a friendlier display grouping).** Both
   agents independently identified and solved the exact same problem the user's own example raises: "Insurance"
   is not a real yfinance sector — it's an industry that spans two different sectors (Financial Services AND
   Healthcare, for managed-care insurers). A pure-sector grouping would never produce an "Insurance" bucket at
   all; a pure-industry grouping would fragment into 100+ tiny groups. `category` is derived by matching industry
   text (e.g. `*Insurance*`) on top of the normalized sector, specifically so "insurance" works exactly as the
   user described it.
6. **Never drop or hide an unclassifiable stock.** Missing/odd data becomes `Uncategorized`, always shown, never
   filtered out silently.
7. **UI split by view**: Shortlist (5 cards) gets simple grouped sections, no filter needed at that size. Top 20
   gets both grouping and a category-chip filter (the primary browsing view). The Buy Opportunity Map gets a
   category filter added to its existing tier/entry-quality/streak filter bar plus a sortable column — NOT grouped
   rows, since its table can be 400+ rows and already has its own sort model; a filter fits that shape better than
   forcing literal group headers into it.
8. **All API changes are additive optional fields** — no endpoint's existing shape breaks, no existing fixture/
   test needs to change to keep passing.
9. **Sequencing**: the data/cache/scanner layer (no UI files) can start immediately. All sector UI work is
   explicitly blocked until the market-reorg sprint's MR-006 lands (it does now — see below), so nothing edits
   `market.js`/`market-map.js`/`dashboard.css` while that sprint is mid-flight.

## The one real disagreement, and how I resolved it
**Where sector data is stored.** Codex recommends one JSON file per ticker (`data/company_profiles/AAPL.json`),
mirroring the existing `data/fundamentals_cache/` pattern exactly. Antigravity recommends one consolidated
registry file (`data/sector_cache/sectors.json`) holding every ticker, citing fewer files in the git tree and O(1)
in-memory lookup.

**Decision: per-ticker files, matching Codex's proposal.** `data/fundamentals_cache/` already holds 2,601
per-ticker files in this exact repository today, proving the "too many small files" concern Antigravity raises is
not actually a practical problem here — the established pattern already works at this scale. Consistency with
that existing, working convention outweighs Antigravity's theoretical efficiency argument, especially since
sector data is only ever fetched/read for a small, bounded roster per run (tens to low hundreds of tickers, not
the full universe), where the read-cost difference between "open N small files" and "load one big dict" is
negligible either way.

## Task breakdown (reconciled from both agents' proposals; Antigravity stays review-only per established policy)

| Task | Owner | Depends on | File boundary | Acceptance criteria |
|---|---|---|---|---|
| SEC-001 Profile cache + taxonomy | Codex | None | New `src/data/company_profiles.py`; focused tests | Cache hit makes zero yfinance calls; handles ok/unclassified/transient-failure/ETF cases; Insurance carve-out and every taxonomy row tested; never imports anything from `src/screening/signal_engine.py` |
| SEC-002 Scanner enrichment | Codex | SEC-001 | `run_optimized_scan.py` only | Classification runs AFTER Top 20 ranking, never before; priority order and the per-run miss cap are tested; score/order/is_buy are byte-for-byte unchanged with classification on vs off; a profile fetch failure can never fail report/email delivery |
| SEC-003 Resumable offline backfill | Codex | SEC-001 | New `scripts/backfill_sectors.py`; tests | Dry-run/resume/cap/retry all work; reports totals + elapsed time; never runs as a side effect of importing it; not part of the daily workflow |
| SEC-004 Stored-shape propagation | Claude | SEC-001, SEC-002 | `src/screening/market_motion.py`, `src/screening/pick_history.py` + tests | New frames/snapshots carry the optional fields; old fixtures still load; tracker/history expose classification; every existing streak/rank/score/denominator is provably unchanged |
| SEC-005 API compatibility | Claude | SEC-001, SEC-004 | `dashboard.py` + API tests | Every named endpoint's existing envelope is unchanged; new fields are additive only; GET routes never make a network call; malformed cache data returns "Uncategorized," never a 500 |
| SEC-006 Independent audit of SEC-001/002/003 | Antigravity | SEC-001, SEC-002, SEC-003 | Review only | Confirms zero classification input reaches scoring/ranking, no full-universe `.info` loop exists anywhere, no emoji in stored data |
| SEC-007 Shared Top 20 grouping + filter UI | Codex | SEC-005, **market-reorg MR-006 (DONE)** | `static/js/core/ui-helpers.js` + new UI tests | Groups by category (best-rank-first ordering), keeps every original rank visible, accessible multi-select filter, `Uncategorized` always included, works in both its Market-tab and Shortlist-fallback mounts without duplicate global ids |
| SEC-008 Shortlist card groups | Claude | SEC-005, MR-006 (DONE) | `static/js/views/shortlist.js` + tests | Category-headed sections ordered by each group's best rank; every card appears exactly once; existing live/news/chart-modal behavior untouched |
| SEC-009 Map category filter + column | Codex | SEC-004, SEC-005, MR-006 (DONE) | `static/js/components/market-motion.js`, `static/js/components/market-map.js`, `static/css/dashboard.css` + tests | Composes cleanly with the existing tier/entry-quality/streak/search filters; all categories start enabled including Uncategorized; sortable Category column; replay/suspend/resume behavior from the market-reorg sprint is untouched |
| SEC-010 Independent audit of the UI work | Antigravity | SEC-007, SEC-008, SEC-009 | Review only | Confirms accessible markup, no dropped/hidden stocks, consistent with the map's established filter-chip visual language |
| SEC-011 Integrated verification | Claude | SEC-006, SEC-010 | Full test run + real browser pass | Full Python + JS suites green; a cold-cache scan respects the miss cap and stays within the CI time budget; a warm-cache scan makes zero profile calls; browser check covers Top 20 grouping/filter, Shortlist grouping, and the Map's new filter/column |

## Release gates
1. A test proves identical candidate membership, scores, buy/no-buy decisions, and rank order with
   classification on vs. off.
2. A warm-cache daily run makes zero profile-fetch calls; a cold run never exceeds the configured miss cap.
3. Missing classification always renders "Uncategorized" and never removes a stock from any list.
4. Every existing historical file/API fixture without classification still loads unchanged.

## Guardrails
No emoji. Never touch `position/`. No commit/push without the user's go-ahead. Sector UI tasks (SEC-007/008/009)
may now proceed — the market-reorg sprint they were waiting on (MR-001 through MR-006) is fully complete and
verified in a real browser as of this session.
