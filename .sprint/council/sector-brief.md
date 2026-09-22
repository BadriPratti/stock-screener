You are participating in a full Engineering Council (MEDIUM-HARD: touches the live scanner's data pipeline, its
cache layer, the daily CI time budget, the API, and several UI views). Do NOT modify any file except the single
output file named for you below.

Repository: /Users/badripratti/Desktop/stock-screener (Flask + pywebview stock screener; native ES modules, no
build step). NEVER open/reference `position/`.

## The user's request (their words)
"I honestly want these stocks organized by category like technology, insurance, health... so on so forth like
that so I know what I am getting into"

## Verified facts (gathered by the lead before dispatching you - verify independently, don't just trust this)
- Sector/industry data is NOT fetched, cached, or present ANYWHERE in the current live scan pipeline. Grepped
  `sector`/`industry` across `src/data/fundamentals_fetcher.py`, `src/data/git_storage_fetcher.py`,
  `src/screening/optimized_batch_processor.py`, `src/screening/signal_engine.py`, `run_optimized_scan.py` - zero
  hits in all of them. (There ARE stale `sector` references in `src/data/fetcher.py` and `src/screening/screener.py`
  - these are an OLDER/unused module path, lazily imported per `src/screening/__init__.py`, not part of the real
  daily scan's call graph - verify this yourself before assuming they're reachable.)
- yfinance DOES provide it easily: `yf.Ticker('AAPL').info` returns `sector: 'Technology'`,
  `industry: 'Consumer Electronics'`. One live call measured at ~0.35s.
- The existing fundamentals cache (`src/data/git_storage_fetcher.py`, `GitStorageFetcher.fetch_fundamentals_smart`)
  already has exactly the right pattern to copy: cache a ticker's fetched data as a JSON file with a `fetched_at`
  timestamp, only refetch if stale (`days_old` check). Sector/industry change far less often than quarterly
  financials - essentially never for a stable company - so a much longer/effectively-permanent cache TTL is
  appropriate, meaning this should be a ONE-TIME cost per ticker ever, not a recurring one, if designed right.
- The real daily scan analyzes ~1,970-3,770 tickers per run (`data/daily_scans/*.txt` "Analyzed:" figures from
  today's real reports) within a ~64-minute run against a 120-minute CI timeout (~56 min headroom, already shared
  with the LLM-agent step on the Top 20 and, per today's other in-flight sprint, a market-motion frame write).
  Naively adding a fresh `.info` call for EVERY analyzed ticker every day (not just new/uncached ones) would add
  roughly 1,970 x 0.35s ≈ 11-plus minutes even before considering yfinance rate-limiting under the existing
  conservative pacing - eating meaningfully into that headroom. This must be designed to avoid that, not just
  measured and accepted.

## Also read
- `src/agents/shortlist.py`, `src/screening/top20_ranker.py` (`build_top20`) - where the final ranked lists get
  assembled, to see the cleanest point to attach a sector field per candidate.
- `static/js/components/market-map.js` - the persistent tracker map ALREADY has a working filter-chip UI pattern
  (tier / entry-quality / streak / ticker-search - `.market-motion-filterbar` in `dashboard.css`) that a sector
  filter/group could extend, rather than inventing a new UI language.
- `static/js/core/ui-helpers.js` `renderTop20Table` (shared by Top 20 and, via consistency badges, elsewhere) and
  `static/js/views/shortlist.js` - where a sector label/grouping would need to appear on cards/rows.
- `.sprint/SPRINT_PLAN_MARKET_REORG.md` (a same-day sprint reorganizing the Market view into tabs - IN PROGRESS,
  not yet fully merged/verified) - whatever you design must not conflict with or duplicate that work; note where
  your plan's UI changes and that one's overlap (likely the Top 20 tab and the map's own filter bar) and how they
  should sequence, not run concurrently on the same files.
- `.sprint/SPRINT_PLAN_SCORING.md` - a same-day investigation into whether the numeric SCORE itself is trustworthy,
  which concluded "don't add new weighted signals without validating them first." Sector/industry as a pure
  ORGANIZATIONAL/filtering dimension (not a new scoring input that changes ranking or who qualifies) avoids that
  concern entirely - confirm your design does NOT feed sector into `score_buy_signal`'s composite score or the
  buy/no-buy threshold; it's about how results are grouped/labeled/filtered for the user, not about re-scoring.

## What you must design
1. **Where sector/industry is fetched and cached.** Recommend fetching it only once per ticker ever (or on a very
   long TTL, e.g. 6-12 months), mirroring `GitStorageFetcher`'s existing cache-file-with-fetched_at pattern -
   propose the concrete file location/format (a new cache directory? folded into the existing fundamentals cache
   file, adding two fields?) and exactly WHEN it's fetched: only for tickers that reach some narrowed stage (e.g.
   only Phase 1/2 candidates that get scored at all, or only the Top 20/tracked roster, similar to how fundamentals
   and the LLM agents are already scoped to the Top 20 rather than the full analyzed universe) rather than every
   one of ~2,000 analyzed tickers every run. Give a concrete estimate of first-run cost (backfilling the ~2,600
   tickers already in `data/fundamentals_cache/` once) versus steady-state daily cost (only genuinely new tickers).
2. **Data shape and normalization.** yfinance's raw `sector`/`industry` strings can be inconsistent/missing for
   some tickers (ETFs, foreign issuers, etc.) - design a normalized category taxonomy (the user named
   "technology, insurance, health" as examples - map yfinance's broader GICS-like sectors sensibly, and decide
   what an unclassifiable ticker (missing/odd sector) is labeled as - never silently drop it from a list, label it
   honestly e.g. "Uncategorized").
3. **Where it surfaces in the UI**, concretely, per view: Shortlist cards, the Top 20 table (a new column? a
   filter above the table?), the persistent Buy Opportunity Map's tracked-stocks table and its existing filter
   chips (a sector filter/multi-select alongside tier/entry-quality/streak fits naturally there), and whether the
   user wants literal GROUPED SECTIONS (a "Technology" heading with its stocks under it, then "Healthcare", etc.)
   versus a FILTER (pick one/several sectors, list narrows) versus both. The user's exact words ("organized by
   category... so I know what I am getting into") suggest grouped/labeled sections are the primary want, with
   filtering as a natural complement - propose which views get grouping, which get filtering, and which get both,
   with a concrete markup sketch for at least the Top 20 table and the tracker map.
4. **API changes needed** - does `dashboard.py`'s `/api/top20`, `/api/scan`, `/api/market-motion*`,
   `/api/pick-history` need a `sector` field added to their existing response shapes? Design this additively (new
   optional field, not a breaking shape change) so existing tests/consumers don't need to change unless they
   specifically test the new field.
5. **Historical data**: the pick-history ledger and market-motion frames already store past sessions - should
   sector be backfillable onto already-recorded historical snapshots (nice-to-have, not required for day one), or
   is it acceptable that only newly-recorded sessions going forward carry a sector label?
6. **Sequencing with the two other in-flight sprints today** (market reorg, scoring investigation) - propose task
   ownership and file-touch boundaries so nothing conflicts. Sector data-layer work (scanner/cache/API) can likely
   proceed independently right now; UI work should probably wait for the market-reorg sprint to fully land first,
   same file-contention discipline used all day.

## Constraints
- Do not make sector/industry feed into `score_buy_signal`'s composite score, the buy threshold, or ranking order
  - this is an organizational/display feature, not a new scoring signal (see the scoring-investigation context
  above for why that boundary matters right now).
- No emoji. This is a plan only - do not implement anything.
- Give a concrete task breakdown at the end (owner suggestion Claude/Codex, dependencies, acceptance criteria).
  Per this session's established policy, Antigravity should be assigned review/audit tasks only in the task
  breakdown, not implementation or test-running tasks, given its proven headless unreliability today.

Write your full analysis to the file named for you below. Also print a short summary to stdout.
