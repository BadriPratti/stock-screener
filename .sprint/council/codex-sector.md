# Engineering Council: sector and industry organization

## Recommendation

Add a small, durable company-profile cache and enrich only the already-selected result set. The daily scanner must never call `Ticker.info` for the full analyzed universe. Rank and qualify stocks exactly as today, then attach classification metadata to the Top 20, the remaining qualified buy signals, sell signals, and the already-tracked market-motion roster. Use the classification only for labels, grouped presentation, and filters.

The user-facing default should be literal category groups where the list is small and rank-oriented (Shortlist and Top 20), plus category filters where the population is large and exploratory (the Buy Opportunity Map). Every item retains its original numeric rank. Nothing in this feature enters `score_buy_signal`, `is_buy`, the score threshold, `combined_score`, `composite_score`, or any ranking sort.

## Independent findings

- The live path has no `sector` or `industry` reference in `src/data/fundamentals_fetcher.py`, `src/data/git_storage_fetcher.py`, `src/screening/optimized_batch_processor.py`, `src/screening/signal_engine.py`, or `run_optimized_scan.py`.
- The only current scanner-side references are in the old `src/data/fetcher.py` and `src/screening/screener.py` path. `src/screening/__init__.py` exposes that screener lazily, while `run_optimized_scan.py` directly uses `OptimizedBatchProcessor`; the old fields do not reach the daily outputs.
- `OptimizedBatchProcessor` fetches quarterly fundamentals only for Phase 1/2 stocks, but those cache records contain quarterly metrics and a `fetched_at`; they contain no profile classification.
- There are 2,601 `*_fundamentals.json` records in `data/fundamentals_cache/` in this checkout.
- The full reports present in this checkout show roughly 1,971-1,994 analyzed stocks and 62.8-67.8 minutes processing time. The council brief reports that the operational range can reach about 3,770, so the design must remain bounded at either scale. The workflow timeout is 120 minutes.
- `build_top20` copies qualified signal dictionaries, ranks them using existing score/Reddit/insider inputs, and only then adds news. `build_shortlist` spreads those Top 20 dictionaries into its results. Enriching after `build_top20` therefore cleanly preserves ranking and can be propagated to both lists.
- `/api/top20` and `/api/shortlist` return the canonical JSON files without transforming their rows. `/api/scan` reparses the text report. Pick-history deliberately slims rows, and market-motion deliberately normalizes signals into frame points, so both stores need explicit optional-field propagation.
- The Map already has tier, entry-quality, streak, and ticker filters in `.market-motion-filterbar`, plus a sortable tracked-stock table. Its color already encodes entry quality; sector must not take over that encoding.
- The market-reorganization sprint is not merely planned now: MR-001 through MR-004 are marked complete, MR-005 is running, and MR-006 is pending. Sector UI work must wait for MR-006 and its browser verification rather than editing `market.js`, `market-map.js`, `dashboard.css`, or their tests concurrently.

## 1. Fetch and cache design

### Use a separate profile cache

Create `data/company_profiles/`, with one tracked JSON file per normalized ticker, for example `data/company_profiles/AAPL.json`. Do not fold the values into `data/fundamentals_cache/AAPL_fundamentals.json`:

- Quarterly fundamentals deliberately refresh every 7 or 90 days. Company classification should not inherit that network cadence.
- A separate, tiny record can be read without loading or rewriting a large quarterly payload.
- It avoids a one-time rewrite of 2,601 existing fundamentals files and reduces git conflicts/noise.
- Raw provider values can be retained while the display taxonomy evolves locally without another Yahoo request.

Proposed record:

```json
{
  "schema_version": 1,
  "ticker": "AAPL",
  "source": "yfinance.info",
  "fetched_at": "2026-09-22T20:15:00Z",
  "status": "ok",
  "raw": {
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "quote_type": "EQUITY"
  }
}
```

Normalization should happen on read through one shared pure function, producing `category`, `sector`, and `industry`. Store a `taxonomy_version` in emitted data or expose it from the normalizer, not as a reason to refetch raw data. A successful record is effectively permanent: refresh only by an explicit maintenance command, after a known corporate change, or through an optional background refresh when older than 12 months. A 12-month refresh must be staggered and budgeted; never let a same-day anniversary cause a cache-expiry herd in the daily scan.

Negative caching is essential. A successful Yahoo response with no usable classification should be stored as `status: "unclassified"` and normalized to `Uncategorized`, so ETFs or sparse foreign listings are not queried every day. A transient request failure should leave the signal labeled `Uncategorized` for that run and record a short `retry_after` (for example seven days), without failing the scan.

Writes should use the repository's existing atomic-write approach, validate ticker-derived filenames, use UTC timestamps, and return a total fallback object rather than raising into scan delivery.

### Fetch only after selection

The daily order should be:

1. Run the existing price, phase, fundamentals, and scoring pipeline unchanged.
2. Build and rank Top 20 exactly as today, without classification.
3. Resolve profiles cache-first in this priority order: Top 20; other qualified buy signals needed by the Map; sell signals shown in the Signals view; previously tracked active/watching tickers missing a cache record.
4. Fetch only cache misses, with a per-run cap (recommended 50) and conservative pacing. Attach fallback `Uncategorized` immediately to entries beyond the cap; they can fill on later runs.
5. Attach the same normalized fields to `top20`, `buy_signals`, and `sell_signals`. Shortlist entries inherit them from Top 20. Only then write `top20_latest.json`, `shortlist_latest.json`, the report, pick-history snapshot, and market-motion frame.

No API request and no intraday re-score should initiate a Yahoo profile fetch. Those paths are cache-only. This prevents page loads or the two-hour Map scheduler from creating an unbounded external dependency.

Fetching only Top 20 would cover two views but leave much of the persistent tracker permanently unclassified. Fetching the displayed signal population plus tracked roster is the better boundary: it is still dramatically narrower than roughly 2,000-3,770 analyzed names and covers every UI named in the request.

### Time-budget estimate

- Full optional backfill: `2,601 x 0.35 seconds = 910.35 seconds`, about 15 minutes 10 seconds of ideal serial request time. With deliberate pacing, retries, and throttling, plan operationally for roughly 20-45 minutes and allow safe resume. This must be a separate manual/maintenance job, not part of the 120-minute daily workflow.
- Day-one without a bulk backfill: at most the capped 50 misses, about 17.5 seconds of raw provider latency, while guaranteeing that the Top 20 is attempted first. This is a bounded migration cost.
- Steady state: normally zero calls. If the universe introduces, for example, 1-10 genuinely new selected/tracked tickers, raw latency is about 0.35-3.5 seconds, plus pacing. Record hit/miss/fetch/failure counts and elapsed time so this assumption is observable.

The optional 2,601-file backfill is useful for immediate historical labeling and avoiding gradual fill, but it is not a day-one dependency.

## 2. Data shape and normalization

Emit these optional fields on a candidate or stored point:

```json
{
  "category": "Insurance",
  "sector": "Financials",
  "industry": "Insurance - Property & Casualty",
  "classification_status": "classified"
}
```

`category` is the stable, user-facing grouping key. `sector` is a normalized broad sector. `industry` is a cleaned provider description and is detail, not a grouping key. This separation lets the UI honor the user's explicit “insurance” example without pretending insurance is a separate standard broad sector.

Recommended deterministic taxonomy:

| Yahoo raw sector/metadata | Normalized sector | User category |
|---|---|---|
| Technology | Technology | Technology |
| Healthcare | Healthcare | Healthcare |
| Financial Services + industry contains insurance/reinsurance | Financials | Insurance |
| Financial Services, otherwise | Financials | Financials |
| Consumer Cyclical | Consumer Discretionary | Consumer Discretionary |
| Consumer Defensive | Consumer Staples | Consumer Staples |
| Industrials | Industrials | Industrials |
| Energy | Energy | Energy |
| Basic Materials | Materials | Materials |
| Real Estate | Real Estate | Real Estate |
| Utilities | Utilities | Utilities |
| Communication Services | Communication Services | Communication Services |
| ETF/mutual-fund quote type | Funds & ETFs | Funds & ETFs |
| missing, blank, or unknown value | Uncategorized | Uncategorized |

Use case-insensitive aliases for common variants, trim whitespace, and never accept provider text as HTML. Do not guess from the ticker or company name. Unknown values should log a normalization counter and render as `Uncategorized`; they must remain in every list and denominator. Preserve raw strings in the cache so a taxonomy correction is a local migration, not a refetch.

## 3. UI behavior by view

### Shortlist: grouped and labeled, no filter

Five cards are too few to justify a filter. Render category sections ordered by the first ranked stock in each category, and preserve the original global rank badge inside each card. Put a category pill beside the ticker and the industry as muted text beneath it. The sections organize the choices while `#1` through `#5` still communicate the scanner's unchanged ordering.

### Top 20: grouping plus multi-select filter

This is the primary category browser. Default to all categories, grouped into table bodies ordered by each category's best original rank; rows inside each group retain original rank. Add an `All` control and category chips above the table. Chips may select one or several categories; zero selected should resolve to `All`, avoiding an unexplained empty screen. Add a Category column containing the category pill and smaller industry text.

Markup sketch:

```html
<section class="card top20-by-category" aria-labelledby="top20-title">
  <h2 id="top20-title">Top 20 by category</h2>
  <div class="market-motion-filterbar" aria-label="Filter Top 20 by category">
    <div class="market-motion-chips" role="group" aria-label="Categories">
      <button class="market-motion-chip active" data-category="all" aria-pressed="true">All</button>
      <button class="market-motion-chip active" data-category="technology" aria-pressed="true">Technology (4)</button>
      <button class="market-motion-chip active" data-category="insurance" aria-pressed="true">Insurance (2)</button>
    </div>
  </div>
  <table class="signal-table">
    <thead><tr><th>#</th><th>Ticker</th><th>Category</th><th>Combined score</th><!-- existing columns --></tr></thead>
    <tbody data-category-group="technology">
      <tr class="category-heading"><th colspan="9" scope="rowgroup">Technology <span>4 stocks</span></th></tr>
      <tr data-category="technology"><td>#1</td><td>...</td><td><span class="category-chip">Technology</span><small>Consumer Electronics</small></td></tr>
    </tbody>
  </table>
</section>
```

Reuse the existing filter-bar/chip visual language but give the Top 20 component its own data attributes and event wiring. `renderTop20Table` is shared by the Market Top 20 tab and the Shortlist fallback, so the behavior must work in both mounts and avoid global duplicate IDs.

### Buy Opportunity Map: filter and label, not grouped rows

Add category chips or a compact multi-select to the existing `.market-motion-filterbar`, alongside tier, entry quality, streak, and ticker search. Category becomes another predicate in `filterTickers`; it filters both plotted points and tracked-table rows. Do not change dot color, score axes, tier, or sort. Add a sortable Category column to the tracked table, with industry as small secondary text or an accessible title.

Literal category row groups are inappropriate here: the table can exceed 400 rows, is lazy behind a disclosure, and already promises arbitrary column sorting. Group headers would fight the current sort model. Filtering plus a visible Category column provides organization without breaking tracker analysis.

Markup sketch:

```html
<div class="market-motion-filterbar" aria-label="Map filters">
  <!-- existing tier, quality, and streak controls -->
  <div class="market-motion-chips" role="group" aria-label="Categories">
    <button class="market-motion-chip active" data-sector="technology" aria-pressed="true">Technology</button>
    <button class="market-motion-chip active" data-sector="insurance" aria-pressed="true">Insurance</button>
    <button class="market-motion-chip active" data-sector="uncategorized" aria-pressed="true">Uncategorized</button>
  </div>
  <!-- existing ticker search -->
</div>
<table id="marketMotionTable">
  <thead><tr><th>Ticker</th><th>Category</th><!-- existing sortable columns --></tr></thead>
  <tbody><tr data-category="insurance"><td>RDN</td><td><span class="category-chip">Insurance</span><small>Mortgage Insurance</small></td></tr></tbody>
</table>
```

All categories start enabled, including `Uncategorized`, so adding this feature can never silently hide a stock. On small windows the category control should horizontally scroll or collapse into a native multi-select rather than wrap the already-dense filter bar into a very tall panel.

## 4. API and persistence changes

All changes are additive optional fields. Existing consumers that ignore them continue to work, and existing fixtures without them remain valid.

| Endpoint | Change |
|---|---|
| `/api/top20` | No envelope change. Each `top20[]` row may include `category`, `sector`, `industry`, and `classification_status`; these are written by the scanner. |
| `/api/shortlist` | Same optional fields on `shortlist[]`, inherited from Top 20. No envelope change. |
| `/api/scan` | Add the optional fields to parsed `buy_signals[]` and `sell_signals[]`. Write `Category: ...`, `Sector: ...`, and `Industry: ...` lines in new reports and teach the parser to accept them. For old reports, enrich cache-only by ticker or return `Uncategorized`; never fetch from this route. |
| `/api/market-motion` | Future frame points may carry the optional fields. The endpoint may cache-enrich old in-memory response points so historical replay can filter immediately; do not rewrite files during GET. `/latest` needs no change because it contains no ticker rows. |
| `/api/market-motion/tracker` | Each `tickers[TICKER]` record should expose top-level optional classification fields derived from its newest available point, with cache-only fallback. Preserve the existing `filters` object and add `categories` only if server-side category filtering is implemented; client filtering is sufficient for the initial capped roster. |
| `/api/pick-history` | Store optional fields in future slim rows, carry the latest known classification into each derived `tickers[TICKER]` record, and cache-enrich older snapshots on read. The history/streak denominator remains entirely unchanged. |

`market_motion.make_point`/normalization and validation must explicitly permit the new strings; `compute_tracker` should lift them to the ticker record rather than forcing the client to search old points. `pick_history._slim_rows` and `compute_history` need the corresponding explicit pass-through. Keep schema version 1 if validators already permit unknown/additive fields; if the implementation makes the fields required, that would be a breaking mistake and would force an unnecessary schema migration.

## 5. Historical data

Day one does not require destructive rewrites of pick-history or market-motion files. New snapshots should persist classification going forward, while GET responses may enrich older rows from the current profile cache. This provides useful category browsing across old sessions immediately after a cache backfill while honestly treating the label as current company metadata, not proof of the company's historical sector on that date.

A later idempotent backfill is a nice-to-have. It should support dry-run, resume, an explicit root, atomic replacement, and a manifest of changed files. It should only add fields; ranks, scores, evaluations, dates, and provenance must compare equal before and after. If historical-as-of classification ever matters, that is a different dataset and should not be inferred from today's Yahoo value.

## 6. Sequencing and file ownership

Data-layer work can start independently, but reserve `run_optimized_scan.py` while the scoring sprint has work planned there. It must not touch `src/screening/signal_engine.py`. The scoring sprint may instrument or later correct score components; the sector sprint only decorates finalized signals after ranking.

Do not start sector UI work until market-reorganization MR-005 and MR-006 are complete. That sprint currently owns or verifies `static/js/views/market.js`, `static/js/components/market-map.js`, `static/css/dashboard.css`, and the market tests. After it lands, build sector UI on its four-tab layout: Top 20 changes belong inside the Top 20 panel and Map controls belong inside the existing Map filter bar. Do not introduce another Market navigation layer.

## Concrete task breakdown

| Task | Suggested owner | Depends on | File boundary | Acceptance criteria |
|---|---|---|---|---|
| SEC-001 Profile cache and taxonomy | Codex | None | New `src/data/company_profiles.py`; focused Python tests | Cache hit performs no Yahoo call; successful, unclassified, transient-failure, ticker validation, atomic write, aliases, Insurance carve-out, Funds & ETFs, and Uncategorized cases pass. No score module imported. |
| SEC-002 Scanner enrichment | Codex | SEC-001; coordinate with scoring owner for `run_optimized_scan.py` | `run_optimized_scan.py` only | Classification runs after Top 20 ranking; priority and 50-miss cap are tested; Top 20/buy/sell receive fields; score/order/is_buy are byte-for-byte unchanged in regression fixtures; profile failures cannot fail report delivery. |
| SEC-003 Stored-shape propagation | Claude | SEC-001, SEC-002 | `src/screening/market_motion.py`, `src/screening/pick_history.py` and their Python tests | New frames/snapshots retain optional fields; old fixtures still validate/load; tracker/history expose classification; streaks, ranks, scores, and denominators are unchanged. |
| SEC-004 API compatibility | Claude | SEC-001, SEC-003 | `dashboard.py`, report writer/parser tests and API tests | All named endpoints return their old envelopes; candidate/ticker rows gain optional fields; old report/snapshot fixtures return safely; GET routes make zero network calls; malformed cache data yields Uncategorized, not 500. |
| SEC-005 Resumable profile backfill utility | Codex | SEC-001 | New script and focused tests; no daily-workflow edit | Dry-run/resume/cap/retry work; reports totals and elapsed time; cannot run as an accidental import; no requirement to execute the full backfill for launch. |
| SEC-006 Shared Top 20 grouping/filter UI | Codex | SEC-004; market reorg MR-006 complete | `static/js/core/ui-helpers.js`, dedicated UI tests; CSS coordinated with SEC-008 | Both Market Top 20 and Shortlist fallback group by category, keep original ranks, support accessible multi-select filtering, include Uncategorized, escape provider strings, and do not rely on unique global IDs. |
| SEC-007 Shortlist card groups | Claude | SEC-004; market reorg MR-006 complete | `static/js/views/shortlist.js` and its tests | Category headings ordered by best original rank; all cards appear exactly once; global rank and existing live/news/chart behavior remain; industry/category labels have safe fallbacks. |
| SEC-008 Map category filter and column | Codex | SEC-003, SEC-004; market reorg MR-006 complete | `static/js/core/market-motion.js`, `static/js/components/market-map.js`, `static/css/dashboard.css`, map tests | Category composes with tier/quality/streak/search; all categories initially enabled; Uncategorized visible; chart and lazy table show the same filtered ticker set; Category sorts; entry-quality colors and replay/suspend/resume behavior are unchanged. |
| SEC-009 Independent audit | Antigravity | SEC-001 through SEC-008 | Review report only | Audit verifies no classification input reaches scoring/ranking, no full-universe `.info` loop exists, APIs remain additive, old fixtures remain readable, and UI never drops Uncategorized. Antigravity does not implement or run tests. |
| SEC-010 Integrated verification | Claude | SEC-006 through SEC-009 | Test execution and browser review; fixes assigned back to file owner | Full Python and JS suites pass; cold-cache run respects cap and timeout; warm-cache run makes zero provider calls; browser check covers 900x600 layout, keyboard chips, Top 20 grouping, Shortlist grouping, Map filter/table/replay, and market tabs. |

## Release gates

1. A test must prove identical candidate membership, scores, buy/no-buy decisions, and rank order with classification enabled versus disabled.
2. A warm-cache daily run must make zero profile calls. A cold run must never exceed the configured miss cap.
3. Missing classification must render `Uncategorized` everywhere and never remove a row or point.
4. Existing historical files and API fixtures without classification must load unchanged.
5. Market-reorganization MR-006 must be complete before any sector UI file is edited.

This delivers the requested organization while keeping sector/industry strictly descriptive. It spends network time only on stocks the product actually shows or tracks and converts that cost into a durable one-time lookup.
