# Engineering Council Second Opinion: Stock Categorization, Sector/Industry Pipeline, and UI Organization

Author: Antigravity (Independent Second Opinion)  
Date: September 22, 2026  
Scope: Medium-Hard (Data pipeline, persistent caching, CI budget, API contracts, UI views)  
Target Repository: /Users/badripratti/Desktop/stock-screener  
Target Output File: .sprint/council/antigravity-sector.md  

---

## 1. Executive Summary & Architectural Position

The user's stated requirement is unambiguous:
"I honestly want these stocks organized by category like technology, insurance, health... so on so forth like that so I know what I am getting into"

This request is fundamentally about information hierarchy, cognitive orientation, and risk comprehension. A user looking at a flat list of 20 or 50 tickers with technical scores and price targets cannot immediately assess sector concentration risk (for example, realizing that 14 of the Top 20 picks are semiconductor manufacturers or that an apparent breakout is in property and casualty insurance).

However, introducing sector and industry classifications into an existing daily scanning pipeline that operates under a strict 120-minute GitHub Actions CI budget poses specific architectural challenges:
1. CI Runtime Preservation: Naively making unthrottled live yfinance `.info` network calls for all 1,970 to 3,770 universe tickers during the daily scan would consume an additional 11 to 22 minutes of network time and trigger yfinance rate limits, dangerously eroding the 56-minute CI headroom.
2. Caching Discipline: Company sectors and industries change exceptionally rarely (effectively once per corporate lifecycle or major restructuring). A permanent or multi-month TTL cache is required.
3. Strict Signal Engine Isolation: In accordance with the findings in .sprint/SPRINT_PLAN_SCORING.md, sector and industry metadata must remain strictly an organizational, filtering, and presentation dimension. It must never feed into score_buy_signal composite calculations, the 60/125 buy qualification threshold, or technical ranking formulas.
4. Taxonomy Alignment: yfinance uses standard 11-sector GICS classifications where "Insurance" is an industry under "Financial Services", and health insurance is under "Healthcare". The user explicitly grouped "insurance" alongside "technology" and "health". A normalized category mapping is necessary to satisfy both institutional sector standards and the user's intuitive category expectations.
5. Multi-View UI Cohesion: The user asked for organization by category. A pure filter hides data; a pure grouping breaks continuous ranking. The optimal solution couples category pill badges, opt-in category section grouping, and instantaneous filter chips across Shortlist cards, the Top 20 table, and the Buy Opportunity Map.

---

## 2. Independent Verification of Codebase Facts

Before proposing architectural specifications, all facts asserted in the council brief were verified directly against repository code and runtime data:

1. Sector Data Absence in Live Scan Call Graph:
   - Grepped `sector` and `industry` across `src/data/fundamentals_fetcher.py`, `src/data/git_storage_fetcher.py`, `src/screening/optimized_batch_processor.py`, `src/screening/signal_engine.py`, and `run_optimized_scan.py`.
   - Result: Exactly zero occurrences in any active screening, scoring, or candidate assembly logic.
   - Checked `src/data/fetcher.py` (line 200) and `src/screening/screener.py` (line 502): While stale references exist in these files, `src/screening/__init__.py` confirms they belong to the legacy support-level screener that is lazily imported and never invoked by `run_optimized_scan.py`.
   - Verified that `top20_latest.json` and `shortlist_latest.json` contain no sector or industry attributes.

2. yfinance Behavior and Latency:
   - `yf.Ticker(ticker).info` reliably supplies `sector` and `industry` keys.
   - Network call latency averages ~0.30s to 0.45s per uncached ticker.
   - Note on `fast_info`: In yfinance, `fast_info` does not provide `sector` or `industry`; fetching corporate classification requires the standard `.info` endpoint.

3. Existing Fundamentals Cache Pattern:
   - Inspected `src/data/git_storage_fetcher.py` and `data/fundamentals_cache/` (2,601 files present).
   - The existing fundamentals cache focuses exclusively on quarterly financial statement metrics (`quarterly_income`, `quarterly_balance_sheet`, `quarterly_cashflow`) for Phase 1 and 2 candidates, using an earnings-season refresh policy (7 days during earnings season, 90 days otherwise).
   - Storing corporate sector data inside quarterly fundamentals JSON files is inappropriate because:
     a) Fundamentals are refetched frequently during earnings seasons, creating unnecessary `.info` calls.
     b) Non-Phase 1/2 stocks or stocks with missing SEC quarterly filings (e.g., foreign issuers, ADRs, recent IPOs) would fail to retain sector data.
     c) Sector metadata has an annual or multi-year stability horizon, unlike quarterly financial metrics.

4. Daily CI Execution Budget and Scan Volume:
   - Inspected `data/daily_scans/optimized_scan_20260922_173646.txt`:
     Total Universe: 3,770 stocks. Analyzed: 1,984 stocks. Processing Time: 62.8 minutes at ~1.0 TPS. Buy Signals: 372. Sell Signals: 460.
   - Under the 120-minute CI timeout in `.github/workflows/daily_screening_git_storage.yml`, 62.8 minutes represents ~52% utilization (~57 minutes remaining headroom).
   - This headroom already accommodates the LLM agent step on the Top 20 (Anthropic API calls) and the market motion frame generation. Any unthrottled, un-cached daily `.info` loop across 2,000+ tickers would add ~12 minutes plus rate-limit penalties, creating unacceptable CI timeout risk.

---

## 3. Data Architecture: Fetching, Caching, and CI Budget

### 3.1 Recommended Cache Architecture: Dedicated Consolidated Sector Registry

We evaluate four structural options for storing sector data:

- Option A: Fold into `data/fundamentals_cache/<TICKER>_fundamentals.json`.
  Rejected. Couplings quarterly balance-sheet queries to corporate classification, forces sector refetches on 7-day/90-day cycles, fails on tickers without quarterly data, and bloats 2,600 files.
- Option B: Individual per-ticker files: `data/sector_cache/<TICKER>.json`.
  Viable, but creates 2,600 to 3,800 additional small files in the git tree, increasing `git status` overhead and file system fragmentation.
- Option C: SQLite table in `data/storage.py`.
  Rejected. The project deliberately transitioned from SQLite to Git-tracked JSON files for screening outputs and persistence across ephemeral GitHub Actions runners.
- Option D (Recommended): Consolidated Git-Tracked JSON Registry (`data/sector_cache/sectors.json`).
  Selected. A single JSON file storing a flat dictionary keyed by ticker symbol.
  - Size footprint: 3,800 tickers at ~120 bytes per entry equals ~456 KB uncompressed (~55 KB gzipped).
  - Git impact: Only one file modified per CI run.
  - In-memory performance: Loaded once at application or scan startup into a Python dictionary. In-memory read latency during scan loops is O(1) (~0.001 ms).
  - Concurrency safety: The scan coordinator maintains the registry in memory and commits changes atomically via `_atomic_write_json` at the conclusion of the scan, avoiding file locking across parallel worker processes.

### 3.2 Registry Schema (`data/sector_cache/sectors.json`)

```json
{
  "schema_version": 1,
  "updated_at": "2026-09-22T20:01:34Z",
  "total_tracked": 2601,
  "sectors": {
    "AAPL": {
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "category": "Technology",
      "fetched_at": "2026-09-22T14:30:00Z"
    },
    "UNH": {
      "sector": "Healthcare",
      "industry": "Healthcare Plans",
      "category": "Insurance",
      "fetched_at": "2026-09-22T14:30:00Z"
    },
    "PGR": {
      "sector": "Financial Services",
      "industry": "Insurance - Property & Casualty",
      "category": "Insurance",
      "fetched_at": "2026-09-22T14:30:00Z"
    }
  }
}
```

### 3.3 Cache Invalidation Policy

- Time-to-Live (TTL): 365 days (1 year).
- Conditional Refresh: A ticker's cached classification is only refetched if:
  1. The ticker is missing from `sectors.json`.
  2. The entry is older than 365 days.
  3. The entry is explicitly flagged as `"Uncategorized"` or `"Unknown"` (allowing automatic self-healing on subsequent runs if yfinance data becomes available).

### 3.4 When and What is Fetched: Staged Pipeline Integration

To guarantee that sector fetching never strains CI limits:
1. Universe Screening (Phase 1 to 4): No sector calls are made. Price and moving-average screening runs at maximum TPS.
2. Signal Generation: When `score_buy_signal` (and `score_sell_signal`) identifies qualifying candidates (~300 to 500 tickers), the scan coordinator extracts candidate tickers.
3. Roster Union: The set of tickers requiring sector resolution is:
   `tickers_to_resolve = buy_signal_tickers | sell_signal_tickers | market_motion_tracked_tickers`
4. Cache Lookup: For this pool, check `sectors.json`.
   - Steady-State Daily Operation: 98% to 99% of these tickers will already exist in the cache. Only genuinely new IPOs, newly qualified penny stocks crossing volume thresholds, or newly listed tickers (typically 5 to 20 tickers per run) will be missing.
   - Steady-State Cost: 10 new tickers x 0.35s = ~3.5 seconds total runtime.
   - Steady-State Headroom Impact: Less than 0.1% of CI time.
5. First-Run Backfill Strategy:
   - Cold-start problem: If the daily scan started with an empty `sectors.json` and attempted to fetch 2,600 tickers sequentially, it would take ~15 minutes at single-thread speed.
   - Resolution: Do NOT backfill 2,600 tickers during the live daily screening CI run.
   - Provide a dedicated, standalone offline backfill script: `scripts/backfill_sectors.py`.
   - Run this script once locally or via an explicit `workflow_dispatch` GitHub Actions job with 5 parallel workers (paged at 0.1s delay = 10 TPS). 2,600 tickers backfilled at 10 TPS completes in 260 seconds (4.3 minutes) and commits `data/sector_cache/sectors.json` into the repository.
   - From that point onward, the daily scan operates strictly in steady-state mode.

---

## 4. Data Shape, Taxonomy, and Normalization

### 4.1 Resolving the Category Ambiguity

The user stated: "organized by category like technology, insurance, health... so on so forth".

In standard corporate taxonomies (GICS / Refinitiv / yfinance):
- "Technology" is a Sector (`sector: "Technology"`).
- "Health" is a Sector (`sector: "Healthcare"`).
- "Insurance" is NOT a sector. It is an Industry Group under `sector: "Financial Services"`, and managed care insurance (like UnitedHealth Group, Humana, Cigna) is an Industry under `sector: "Healthcare"`.

If the system organized stocks strictly by raw yfinance `sector`:
- UnitedHealth (`UNH`) would be grouped under "Healthcare".
- Progressive (`PGR`) and Travelers (`TRV`) would be grouped under "Financial Services".
- There would be NO "Insurance" group, directly violating the user's explicit expectation.

Conversely, if the system grouped stocks strictly by yfinance `industry`:
- There would be over 120 granular sub-industries ("Software - Infrastructure", "Software - Application", "Semiconductors", "Computer Hardware"), fragmenting 20 stocks into 15 micro-groups with 1 stock each.

### 4.2 Two-Tier Normalized Taxonomy: `sector` and `category`

We define two distinct, complementary fields attached to every candidate:
1. `sector`: The normalized macro sector (11 standard sectors + "ETF/Fund" + "Uncategorized").
2. `category`: An intuitive display category that elevates prominent industry clusters (such as Insurance, Biotech, and Cybersecurity) while grouping generalist companies into standard macro sectors.

#### Normalization Mapping Rules:

| yfinance Sector | yfinance Industry Pattern | Normalized `sector` | User-Facing `category` |
|---|---|---|---|
| Financial Services | `*Insurance*` | Financial Services | Insurance |
| Healthcare | `*Healthcare Plans*` | Healthcare | Insurance |
| Technology | `*Semiconductor*` | Technology | Technology |
| Technology | `*Software*` | Technology | Technology |
| Healthcare | `*Biotechnology*` | Healthcare | Healthcare |
| Healthcare | Any other Healthcare | Healthcare | Healthcare |
| Financial Services | Non-insurance | Financial Services | Financial Services |
| Consumer Cyclical | Any | Consumer Cyclical | Consumer Discretionary |
| Consumer Defensive | Any | Consumer Defensive | Consumer Staples |
| Industrials | Any | Industrials | Industrials |
| Energy | Any | Energy | Energy |
| Utilities | Any | Utilities | Utilities |
| Real Estate | Any | Real Estate | Real Estate |
| Basic Materials | Any | Basic Materials | Basic Materials |
| Communication Services | Any | Communication Services | Communication Services |

#### Handling Unclassifiable or Missing Tickers:
- Foreign issuers, ADRs, Pink Sheet uplists, or obscure holding companies may return `sector: null` or empty string in yfinance.
- ETFs (such as SPY, QQQ, XLK) may have `quoteType: "ETF"` and no sector.
- Strict Policy: NEVER drop, filter out, or reject an unclassifiable stock from Top 20, Shortlist, or scan reports.
- If `quoteType == 'ETF'` -> `sector: "ETF / Fund"`, `category: "ETF / Fund"`.
- If missing or unmapped -> `sector: "Uncategorized"`, `industry: "Unknown"`, `category: "Uncategorized"`.
- This ensures full transparency without breaking sort or filter pipelines.

---

## 5. UI Design & User Experience Specification

The user asks for stocks to be "organized by category... so I know what I am getting into".
In desktop information design, "organized" can mean three distinct mechanisms:
1. Card/row labeling (badges showing the category on every entity).
2. Filtering (selecting one or more categories to narrow down the view).
3. Section grouping (visual headings grouping items by category).

We analyze how each view should behave:

### 5.1 View 1: Shortlist View (`static/js/views/shortlist.js`)

- Context: The Shortlist view displays exactly 5 curated cards (`.pick-card`).
- UX Evaluation: Grouping 5 cards into 3 or 4 separate section headings adds visual noise, vertical scroll, and uneven layout (e.g. three sections with 1 card, one section with 2 cards).
- Design Specification:
  - Add a prominent, color-coded category badge directly into `.pick-header` adjacent to the ticker symbol.
  - Markup sketch:
    ```html
    <div class="pick-header">
      <span class="ticker">${s.ticker}</span>
      <span class="category-badge category-${slug(s.category)}">${escapeHtml(s.category)}</span>
      <span class="industry-sub">${escapeHtml(s.industry || '')}</span>
      <span class="pick-price">$${s.current_price.toFixed(2)}</span>
      <span id="${chartId}-slot"></span>
    </div>
    ```
  - Benefit: Immediate comprehension of what kind of company the pick is, zero additional scroll depth.

### 5.2 View 2: Top 20 Table (`static/js/core/ui-helpers.js` -> `renderTop20Table`)

- Context: Displays 20 ranked candidates in a single table with momentum and consistency slots.
- The Dilemma: If the table is permanently grouped into category sections, the linear #1 to #20 ranking order becomes fragmented and difficult to compare. If it is only a flat table, the user cannot see categorized clusters.
- Solution: A Hybrid Presentation featuring:
  1. A dedicated `Category` column in the table with distinct pill styling.
  2. A `Category Filter Bar` above the table: `[All (20)]`, `[Technology (8)]`, `[Healthcare (4)]`, `[Insurance (3)]`, `[Financials (3)]`, `[Other (2)]`.
  3. A View Mode Toggle: `[Ranked List]` (default) vs. `[Grouped by Category]`.

#### Markup Sketch for Top 20 Controls & Grouped Table:

```html
<div class="card top20-card">
  <div class="top20-header-row">
    <div>
      <h2>Top 20 — Combined Pool</h2>
      <div class="card-sub">Ranked buy candidates with technical, Reddit buzz, and insider scores</div>
    </div>
    <div class="view-mode-toggle" role="group" aria-label="Top 20 view mode">
      <button class="btn btn-sm active" id="top20ViewRanked" type="button" aria-pressed="true">Ranked</button>
      <button class="btn btn-sm" id="top20ViewGrouped" type="button" aria-pressed="false">Grouped</button>
    </div>
  </div>

  <!-- Filter chips bar -->
  <div class="top20-filterbar" id="top20FilterBar" aria-label="Category filters">
    <button class="top20-chip active" data-category="all" type="button">All (20)</button>
    <!-- Dynamically rendered chips for present categories -->
    <button class="top20-chip" data-category="Technology" type="button">Technology (8)</button>
    <button class="top20-chip" data-category="Insurance" type="button">Insurance (3)</button>
    <button class="top20-chip" data-category="Healthcare" type="button">Healthcare (4)</button>
  </div>

  <div class="consistency-caption" id="consistency-caption-top20"></div>

  <div style="overflow-x:auto">
    <table class="signal-table top20-table">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Ticker</th>
          <th scope="col">Category</th>
          <th scope="col">Combined Score</th>
          <th scope="col">Momentum</th>
          <th scope="col">Consistency</th>
          <th scope="col">Reddit</th>
          <th scope="col">Why it's moving</th>
          <th scope="col">Trade</th>
        </tr>
      </thead>
      <tbody>
        <!-- When in Grouped mode: -->
        <tr class="table-group-header">
          <td colspan="9"><b>Technology</b> <span class="group-count">(8 stocks)</span></td>
        </tr>
        <tr>
          <td>#1</td>
          <td><span class="ticker">NSIT</span></td>
          <td><span class="badge-pill badge-tech">Technology</span><div class="table-sub">IT Services</div></td>
          <td><span class="score-num">107.8</span></td>
          ...
        </tr>
        <tr class="table-group-header">
          <td colspan="9"><b>Insurance</b> <span class="group-count">(3 stocks)</span></td>
        </tr>
        <tr>
          <td>#3</td>
          <td><span class="ticker">PGR</span></td>
          <td><span class="badge-pill badge-ins">Insurance</span><div class="table-sub">Property & Casualty</div></td>
          <td><span class="score-num">98.2</span></td>
          ...
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

### 5.3 View 3: Buy Opportunity Map (`static/js/components/market-map.js`)

- Context: The Buy Opportunity Map tracks ~400 stocks across frames, rendering a 2D scatter canvas (RS slope vs. Buy Score) and a sortable table (`#marketMotionTable`).
- Existing Pattern: The map already implements a sophisticated filter-chip UI in `.market-motion-filterbar` (Tier: Active/Watching/Retired; Entry Quality: Good/Extended/Poor; Streak: >=0, >=2, >=3, >=5; Search: Ticker).
- Design Specification:
  1. Add a Category Filter to `.market-motion-filterbar`.
     Because there can be 10 to 12 active categories among 400 tracked stocks, placing 12 additional button chips would double the filterbar's vertical footprint. Instead, implement a compact category selector dropdown (`<select id="marketMotionCategory" class="market-motion-select">`) styled identically to the replay speed select, or a responsive scrollable chip strip.
  2. Canvas Interaction:
     When a category filter is selected, `filterTickers()` in `static/js/core/market-motion.js` filters the visible universe. Non-matching stocks fade or are excluded from the canvas, allowing the user to isolate "Technology" or "Insurance" trajectory clusters on the map.
  3. Canvas Tooltip:
     Add `Category: ${item.category} (${item.industry})` to the canvas hover tooltip and the selected ticker detail box.
  4. Tracked Stocks Table (`#marketMotionTable`):
     - Add `category` to `TABLE_COLUMNS` in `market-map.js`:
       `['category', 'Category']`
     - Enable column sorting by category.

---

## 6. API Design & Data Contracts (Additive, Non-Breaking)

All API adjustments in `dashboard.py` and downstream data files are strictly additive. No existing fields are removed, renamed, or modified in type. Existing unit tests and consumers require zero modifications.

### 6.1 Endpoint Details:

1. `GET /api/top20`
   - Source: `data/daily_scans/top20_latest.json`.
   - Contract Addition: Each candidate object in the `top20` array receives:
     ```json
     {
       "ticker": "AAPL",
       "score": 95.5,
       "combined_score": 102.1,
       "sector": "Technology",
       "industry": "Consumer Electronics",
       "category": "Technology"
     }
     ```

2. `GET /api/shortlist`
   - Source: `data/daily_scans/shortlist_latest.json`.
   - Contract Addition: Each candidate object in `shortlist` receives `sector`, `industry`, `category`.

3. `GET /api/scan?path=...`
   - Source: Parsed from `optimized_scan_*.txt` via `parse_scan_file(filepath)`.
   - Contract Addition: The text report format in `run_optimized_scan.py` (`save_report`) will include a new line per signal:
     `Category: Technology | Industry: Consumer Electronics`
   - `parse_scan_file` adds regex extraction to populate `signal["sector"]`, `signal["industry"]`, and `signal["category"]`.

4. `GET /api/market-motion/tracker`
   - Source: Derived by `compute_tracker(frames)`.
   - Contract Addition: Each record in `tracker["tickers"][ticker]` receives `category`, `sector`, and `industry`.
   - In addition, `tracker["categories"]` is returned at the root level with ticker counts (e.g. `{"Technology": 142, "Insurance": 28, ...}`) to allow instant population of client-side filter controls without re-scanning the entire ticker map.

5. `GET /api/pick-history`
   - Source: Derived by `compute_history(snapshots)`.
   - Contract Addition: `_slim_rows` in `src/screening/pick_history.py` optionally retains `sector` and `category` when available.

---

## 7. Historical Data Strategy & Backfill Policy

### 7.1 Immutability of Recorded Files

The repository stores historical snapshots in:
- `data/pick_history/daily_full_*.json` (daily scan ledger snapshots)
- `data/market_motion/frame_*.json` (recorded intraday/daily frames)

Key Question: Should these historical JSON files be modified on disk to backfill sector fields?

Recommendation: NO. Do not rewrite historical files.
Rationale:
1. Immutability: Historical frames and ledger records represent exact snapshots of the pipeline state at execution time. Mutating dozens of historical files violates ledger integrity and bloats git diff history.
2. Zero Necessity: In this architecture, corporate classification is ticker-level metadata that does not vary from hour to hour.
3. Dynamic On-Read Resolution:
   Both `market_motion.py` (`compute_tracker`) and `pick_history.py` (`compute_history`) derive their view models dynamically on read.
   By allowing `compute_tracker` and `compute_history` to query `SectorCache.get(ticker)` in-memory during view computation, 100% of historical sessions automatically display the correct category badges and enable category filtering retroactively, without touching a single byte of historical JSON files on disk.
4. Optional Tooling: If external consumers ever require enriched past files, a dedicated script `scripts/backfill_sectors.py --rewrite-history` can be provided as an optional offline utility, but it is explicitly excluded from the critical path.

---

## 8. Integration & Sequencing with In-Flight Sprints

Today's development environment contains two other active sprints:
1. `SPRINT_PLAN_MARKET_REORG.md` (reorganizing `/market` into tabs, lazy-mounting the map, modifying `static/js/views/market.js` and `static/css/dashboard.css`). Currently in progress (MR-005 dispatched, MR-006 pending).
2. `SPRINT_PLAN_SCORING.md` (instrumenting walk-forward backtest inputs and testing score correlations in `src/backtesting/frozen_inputs.py` and `signal_engine.py`).

### 8.1 File Contention Matrix & Blast Radius

| File | Market Reorg | Scoring Sprint | Sector Sprint | Conflict Risk | Sequencing Policy |
|---|---|---|---|---|---|
| `src/data/sector_cache.py` | No | No | CREATE | Zero | Can build immediately |
| `scripts/backfill_sectors.py` | No | No | CREATE | Zero | Can build immediately |
| `src/screening/top20_ranker.py` | No | No | Modify | Zero | Can build immediately |
| `src/agents/shortlist.py` | No | No | Modify | Zero | Can build immediately |
| `run_optimized_scan.py` | No | No | Modify | Zero | Can build immediately |
| `src/screening/market_motion.py`| No | No | Modify | Zero | Can build immediately |
| `dashboard.py` (API routes) | No | No | Modify | Zero | Can build immediately |
| `static/js/core/ui-helpers.js` | No | No | Modify | Zero | Can build immediately |
| `static/js/views/shortlist.js` | No | No | Modify | Zero | Can build immediately |
| `static/js/components/market-map.js` | Touched | No | Modify | Moderate | MUST wait for MR-006 to land |
| `static/js/views/market.js` | Heavily Touched| No | No | High | DO NOT TOUCH (handled by MR) |
| `static/css/dashboard.css` | Heavily Touched| No | Modify | Moderate | MUST wait for MR-006 to land |

### 8.2 Three-Stage Execution Sequence

- Stage 1: Data, Cache, and Scanner Pipeline (Backend Only)
  - Build `src/data/sector_cache.py`.
  - Populate `data/sector_cache/sectors.json` via `scripts/backfill_sectors.py`.
  - Connect `run_optimized_scan.py`, `top20_ranker.py`, and `shortlist.py`.
  - This stage touches zero UI files and zero scoring logic. It can execute concurrently with any ongoing UI sprint.
- Stage 2: API and In-Memory Resolution
  - Update `dashboard.py` endpoints (`/api/top20`, `/api/shortlist`, `/api/scan`).
  - Update `src/screening/market_motion.py` to resolve sectors dynamically on read.
- Stage 3: UI Integration (Strictly Blocked by Market Reorg)
  - Prerequisite: `SPRINT_PLAN_MARKET_REORG.md` MR-006 completes and passes all automated browser and unit tests.
  - Implement Shortlist badges in `static/js/views/shortlist.js`.
  - Implement Top 20 category column, filter chips, and grouping toggle in `static/js/core/ui-helpers.js`.
  - Implement Market Map category filter in `static/js/components/market-map.js`.
  - Add category pill styling in `static/css/dashboard.css`.

---

## 9. Concrete Task Breakdown & Council Recommendations

Per council policy, Antigravity is assigned review and architectural audit tasks only. Implementation, execution, and test-running tasks are assigned to Claude or Codex.

| Task ID | Component | Description | Owner | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|
| SEC-001 | Data Layer | Create `src/data/sector_cache.py` with `SectorCache` class, in-memory lookup, 365-day TTL, atomic file writing, and category normalization taxonomy | Codex | None | Unit tests pass; handles nulls/ETFs gracefully as "Uncategorized" |
| SEC-002 | Tooling | Create `scripts/backfill_sectors.py` to backfill `data/sector_cache/sectors.json` for existing 2,600 cached fundamentals tickers using thread pool (paged at 10 TPS) | Claude | SEC-001 | Generates valid `sectors.json` (<500 KB); zero failed unhandled exceptions |
| SEC-003 | Architecture Audit | Independent audit of `SectorCache` implementation, taxonomy mappings, and backfilled `sectors.json` integrity | Antigravity | SEC-001, SEC-002 | Verify zero score contamination, verify memory consumption <10 MB, confirm no emoji in stored data |
| SEC-004 | Pipeline Integration | Integrate `SectorCache` into `src/screening/top20_ranker.py`, `src/agents/shortlist.py`, and `run_optimized_scan.py` (`save_report`) | Codex | SEC-001 | `top20_latest.json`, `shortlist_latest.json`, and scan report include `sector`, `industry`, `category` |
| SEC-005 | API & Backend | Update `dashboard.py` (`/api/top20`, `/api/shortlist`, `parse_scan_file`) and `src/screening/market_motion.py` (`compute_tracker`) | Claude | SEC-004 | API endpoints return additive sector fields without breaking existing schema contracts |
| SEC-006 | API Verification | Audit API contracts and test suite for backward compatibility | Antigravity | SEC-005 | Confirm all existing Python API tests pass; verify zero regressions on legacy clients |
| SEC-007 | UI: Shortlist & Top 20 | Update `static/js/views/shortlist.js` (card badges) and `static/js/core/ui-helpers.js` (`renderTop20Table` category column, filter chips, and grouped toggle) | Claude | SEC-005, MR-006 | Shortlist cards show category badges; Top 20 supports category filtering and section grouping |
| SEC-008 | UI: Market Map | Update `static/js/components/market-map.js` (category filter in filterbar, category column in tracked table, tooltip update) and `static/css/dashboard.css` | Codex | SEC-005, MR-006 | Category filter narrows canvas points and tracked table rows; matches existing design language |
| SEC-009 | End-to-End Audit | Final full-system verification: CI runtime impact, browser visual pass, keyboard navigation, responsive layout | Antigravity | SEC-007, SEC-008 | Complete system verified; verify daily scan adds <10s overhead; all JS/Python test suites clean |

---

## 10. Summary for the Lead

1. Caching Strategy: Single consolidated file `data/sector_cache/sectors.json` loaded into memory at startup. Steady-state daily cost is under 10 seconds, preserving the 56-minute CI headroom.
2. Taxonomy: Two-tier `sector` (macro standard) and `category` (elevating user-requested clusters like "Insurance"). Tickers with missing data are labeled "Uncategorized" and never dropped.
3. Isolation: Strict adherence to scoring isolation. Sector metadata is purely organizational and never enters `score_buy_signal` or ranking calculations.
4. UI Delivery: Category pill badges on Shortlist cards; filter chips plus grouped view toggle on the Top 20 table; category filter and table column on the Buy Opportunity Map.
5. Sprint Harmony: Data/pipeline tasks (SEC-001 through SEC-006) can execute immediately; UI tasks (SEC-007, SEC-008) must sequence after the Market Reorg sprint (MR-006) completes.
