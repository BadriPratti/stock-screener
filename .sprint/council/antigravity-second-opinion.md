# Engineering Council Analysis: Incorporating Codex and Antigravity Second Opinions

**Date:** 2026-09-22  
**Council Participant:** Antigravity  
**Classification:** HARD (Adds to Live Financial Recommendation Pipeline)  
**Target File:** `.sprint/council/antigravity-second-opinion.md`  

---

## Executive Summary

The user requests incorporating Codex and Antigravity into the stock analysis pipeline before picks reach the app and daily email:
> "we also need to incorporate codex and antigravity to also do these stock analysis before going into the app... they need a say of their own before going [into the app]"

Through direct user clarifications, the design constraints are established:
1. **Zero New API Keys**: No direct OpenAI or Google Gemini API keys. Invocations must use the existing `codex exec` and `agy -p` CLI tools already installed on the developer workstation.
2. **Advisory Only**: Contributes lightly to final shortlist ranking (similar to Catalyst Sentiment), but possesses strictly **no drop power** (cannot disqualify a candidate, unlike the Fundamentals Auditor).
3. **Strict Reliability and Time Budget**: The daily GitHub Actions scan takes ~64 minutes against a 120-minute hard timeout (~56 minutes headroom). The solution must run boundedly, parallelized where possible, and degrade seamlessly to zero contribution if either or both CLI tools fail, crash, or time out.

### Key Architectural Determinations

1. **Call Shape: 1 Batched Parallel Call per Agent for the Entire Top 20 Universe.**  
   Invoking CLI agents once per ticker (40 invocations total) is disqualified: cold-start process overhead, workspace indexing, and tool execution latencies observed in this session (1 to 10+ minutes per session) would consume 40 to 120+ minutes and crash system resources. Small batches (4 batches of 5) quadruple process startup overhead and complicate state reconciliation. A single batched invocation containing all 20 candidates is ~5,000 input tokens and produces ~1,200 output tokens. Both CLI agents can be dispatched concurrently via Python subprocesses with a **180-second hard timeout**.
2. **Strict Tool Suppression in Prompts.**  
   Session logs (`.sprint/logs/agy-scoring.log`) prove that headless `agy -p` crashes outright when tool permissions are requested (`jetski: no output produced — a tool required the "command" permission that headless mode cannot prompt for`). Codex sessions (`.sprint/logs/codex-second-opinion.log`) balloon to 10+ minutes when allowed to browse files and run shell commands. Prompts must be 100% self-contained, explicitly forbidding tool invocation, and CLI invocations must pass `--dangerously-skip-permissions` (for Antigravity) and `-s read-only --ephemeral` (for Codex).
3. **Resilient 3-Tier Parsing Fallback.**  
   CLI agents lack API-level JSON mode guarantees. A three-tier parsing pipeline (Direct JSON -> Fenced Markdown Block -> Per-Ticker Regex Scanner) ensures partial or malformed responses still extract valid ticker verdicts. Any unparseable ticker or complete CLI failure defaults to score `0` (neutral pass), never crashing the scan.
4. **Ranking Mechanism: Bounded Additive Term with Explicit Dissent Surfacing.**  
   Each agent provides a discrete opinion score in `[-2, +2]`. In `src/agents/shortlist.py`, `composite_score` adds `(codex_score * 1.0) + (antigravity_score * 1.0)`, shifting ranking by at most +/-4.0 points on an 80-110 point base score. Instead of silently averaging disagreement, the UI surfaces an **AI Council Consensus Badge** (e.g. "3/4 Bullish; Codex Dissent: Extended Valuation"), giving the user high-signal divergence context without card bloat.
5. **CI Reality Check: Graceful Auto-Detection.**  
   Standard GitHub Actions `ubuntu-latest` runners do not have `codex` or `agy` binaries installed or authenticated. The execution harness must check binary availability via `shutil.which()`. In CI or unauthenticated environments, the runner logs an informational notice and returns empty opinion sets instantly, preserving full pipeline compatibility.

---

## 1. Call Shape, Batching, and Parsing Reliability

### 1.1 Comparative Analysis of Execution Granularities

| Architecture | Total CLI Calls | Cold-Start Overhead | Concurrency Risk | Failure Blast Radius | Estimated Latency | Council Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Per-Ticker (1x20 each)** | 40 separate calls | Extreme (40 boots of Node/Go/Python runtimes) | High (OOM / CPU thrashing if parallel; serialized hangs) | Isolated (1 ticker lost per fail) | 40 - 120+ minutes | **Disqualified**: Exceeds CI timeout, unmanageable process thrashing |
| **Micro-Batches (4x5 each)** | 8 separate calls | High (8 cold starts, 8 workspace scans) | Moderate | Moderate (5 tickers lost per fail) | 12 - 25 minutes | **Suboptimal**: High latency, complex reconciliation |
| **Single Batched Call (1x20 each)** | 2 parallel calls | Minimal (1 boot per agent engine) | Low (bounded to 2 worker threads) | High without parsing fallbacks; Negligible with tier-3 parser | 1.5 - 3.0 minutes | **Recommended**: Fits time budget, lowest overhead, parallel execution |

### 1.2 Quantitative Token and Latency Estimation

- **Input Prompt Payload for 20 Tickers**:
  - Each ticker payload contains: Ticker symbol, current price, technical score, phase, entry quality, relative strength, distance to 50/200 SMA, 52-week range, valuation snapshot (P/E, Debt/Equity, FCF Yield), Claude Fundamentals flags, and Claude Catalyst classification.
  - Payload per ticker: ~220 tokens.
  - Total prompt payload for 20 tickers: ~4,400 tokens + ~600 tokens system instructions = **~5,000 tokens**.
  - Modern LLM context windows (Codex `gpt-5.6-sol`, Antigravity `gemini-2.0-flash` / `gemini-1.5-pro`) easily process 128k to 1M tokens. 5,000 tokens is processed in a single forward pass.
- **Output Response Payload**:
  - 20 JSON objects containing `{ "ticker": str, "opinion_score": int [-2..2], "stance": str, "summary": str, "key_risk": str }`.
  - Output per ticker: ~50-60 tokens.
  - Total output payload: **~1,000 - 1,200 tokens**.
  - Generation time for 1,200 tokens: 25 to 45 seconds under typical API/agent load.
- **Observed CLI Latency in This Session**:
  - From `.sprint/logs/`:
    - `codex-market-reorg.log`: 4 minutes (interactive tool use).
    - `codex-live-chart.log`: 7 minutes (file exploration, test running).
    - `agy-market-reorg.log`: ~2.5 minutes (prompt turn with language server overhead).
  - The dominant latency driver in recorded sessions was **tool invocation** (running `grep`, reading files, executing `pytest`). When instructed strictly as an in-memory generation task with zero tool calls, process overhead drops to:
    - CLI boot and language server startup: ~5-10 seconds.
    - Generation: ~30-50 seconds.
    - Total expected wall-clock runtime per agent: **60 to 90 seconds**.

### 1.3 Headless Execution Flags and Tool Suppression

Session logs demonstrate two failure modes that must be proactively engineered out:
1. **Headless Permission Deadlock**: In `.sprint/logs/agy-scoring.log`, `agy -p` exited with code 1:
   `jetski: no output produced — a tool required the "command" permission that headless mode cannot prompt for, so it was auto-denied.`
2. **Agentic Wandering**: In `.sprint/logs/codex-second-opinion.log`, Codex spawned shell sub-processes to inspect `data/fundamentals_cache/metadata.json` and git status, delaying response generation by minutes.

**Mandatory CLI Invocation Configurations**:
- **Antigravity CLI**:
  ```bash
  agy -p --dangerously-skip-permissions --disable-slash-commands --print-timeout 180s "<PROMPT>"
  ```
  Passing `--dangerously-skip-permissions` ensures that if an internal tool is triggered, it does not deadlock headless execution. Passing `--disable-slash-commands` prevents unwanted skill expansions.
- **Codex CLI**:
  ```bash
  codex exec -s read-only --ephemeral --skip-git-repo-check -o <OUTPUT_FILE> "<PROMPT>"
  ```
  Passing `-s read-only` prevents workspace mutation; `--ephemeral` avoids cluttering `~/.codex/sessions`; `-o <OUTPUT_FILE>` ensures the final model response is cleanly captured even if stdout contains terminal formatting codes.

### 1.4 Hard Per-Call Timeout and Process Tree Termination

CLI processes can spawn background worker daemons (such as Antigravity's `jetski` language server on localhost gRPC port `50558`, or Codex child runners).
- **Hard Timeout**: **180 seconds (3.0 minutes)** per agent.
- **Process Group Termination**: Python `subprocess.Popen` must be created with `start_new_session=True`. On timeout:
  ```python
  try:
      stdout, stderr = proc.communicate(timeout=180)
  except subprocess.TimeoutExpired:
      logger.warning(f"{agent_name} second-opinion timed out after 180s; killing process tree.")
      os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
      time.sleep(2)
      try:
          os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
      except ProcessLookupError:
          pass
      return {}
  ```
  Killing the entire process group (`os.killpg`) guarantees no orphaned language servers or python workers linger to consume CPU or leak memory.
- **Timeout Policy**: If an agent times out, log a warning, record `status: "timeout"`, and return an empty dictionary. The pipeline proceeds immediately without retry loops.

### 1.5 Robust Three-Tier Parsing Pipeline

Because CLI tools do not guarantee clean API JSON formatting, output may contain preamble (`"Here is the evaluation for the Top 20:"`), ANSI color codes, or markdown fences.

The response parser operates in three sequential fallback tiers:
1. **Tier 1 (Direct JSON Parse)**: Strip whitespace and attempt `json.loads(text)`.
2. **Tier 2 (Fenced Block Extraction)**: Search for fenced blocks ````json ... ```` or find the outer bounds between the first `[` and last `]`.
3. **Tier 3 (Per-Ticker Regex Extraction)**: If the JSON array syntax is truncated or corrupted, scan the text using regex for individual ticker blocks:
   ```python
   pattern = r'\{\s*"ticker"\s*:\s*"([A-Z]+)"\s*,\s*"opinion_score"\s*:\s*(-?[0-2])\s*,\s*"stance"\s*:\s*"([^"]+)"\s*,\s*"summary"\s*:\s*"([^"]+)"'
   ```
   Extract valid records individually.
4. **Validation and Clamping**:
   - Every extracted `opinion_score` must be an integer clamped to `[-2, +2]`.
   - Any ticker missing from the parsed payload defaults to `{ "opinion_score": 0, "stance": "neutral", "summary": "No consensus opinion provided" }`.
   - Under no circumstances does a parsing error raise an uncaught exception.

---

## 2. Grounding Data and Prompt Shape

### 2.1 Grounding Data Assembly

CLI agents must evaluate candidates based strictly on objective, current data provided in-context, avoiding stale training-data hallucinations or blind momentum guesses.

For each of the Top 20 candidates, the pipeline extracts and formats:
1. **Core Market Identifiers**: Ticker, company name, sector, current price.
2. **Signal Engine Metrics (from `signal_engine.py`)**:
   - `score`: Base composite technical score (0-125).
   - `phase`: Stage analysis phase (Phase 1 Base / Phase 2 Confirmed Uptrend).
   - `entry_quality`: Entry rating ('Good', 'Extended', 'Poor').
   - `rs_rating`: Relative Strength percentile vs S&P 500.
   - `sma_structure`: Distance to 50 SMA (%), distance to 200 SMA (%).
   - `range_52w`: Position within 52-week range (current price vs 52w high/low).
   - `volume_surge`: Volume ratio vs 50-day average volume.
3. **Fundamental Snapshot**:
   - Trailing P/E, Forward P/E, Debt-to-Equity, FCF Yield, Market Cap.
   - Revenue QoQ / YoY growth rates, Earnings growth.
4. **Existing Claude & Congress Signals (Context Grounding)**:
   - Fundamentals Auditor: `overall_assessment` (`green_flags_outweigh`, `mixed`, `no_notable_flags`, `red_flags_outweigh`), top red flag, top green flag.
   - Catalyst Sentiment: `catalyst_type` (`earnings_beat`, `analyst_upgrade`, `pure_momentum_no_catalyst`), `catalyst_score` (-5 to +5), 1-sentence catalyst summary.
   - Congress Trading Signal: Net 90-day transactions and score (-3 to +3).

### 2.2 Structured Prompt Template

The prompt is constructed as follows:

```text
You are an expert Senior Quantitative & Technical Portfolio Analyst participating in an automated Daily Stock Selection Council.

You are evaluating a pre-screened pool of the Top 20 momentum breakout candidates for today's market session.
Your role is to provide an INDEPENDENT SECOND OPINION on each candidate's breakout sustainability and risk/reward profile.

RULES:
1. DO NOT USE ANY TOOLS. Do not read files, do not run shell commands, do not query the web. All necessary data is provided below.
2. Evaluate each candidate strictly on the provided technicals, fundamentals, and catalyst evidence.
3. For each candidate, assign an integer `opinion_score` from -2 to +2:
   +2: High Conviction Bullish (Clean base, rising moving averages, solid fundamentals/catalyst, high probability continuation)
   +1: Moderate Bullish (Favorable trend, acceptable entry, minor risks noted)
    0: Neutral / Pass (Mixed evidence, fair setup but lacks distinctive edge)
   -1: Cautious / Skeptical (Extended entry, decelerating metrics, or unconvincing catalyst)
   -2: High Risk / Divergence (Dangerous extension, fragile balance sheet, severe divergence from market trend)
4. Provide a 1-sentence analytical synthesis (`summary`) and note the single primary risk (`key_risk`).
5. Return ONLY a single valid JSON array containing evaluations for all 20 tickers. No markdown chatter before or after.

CANDIDATES TO EVALUATE:
[
  {
    "ticker": "CRWD",
    "price": 312.40,
    "technical": {
      "base_score": 94.5,
      "phase": "Phase 2 (Uptrend)",
      "entry_quality": "Good",
      "distance_50sma_pct": 2.4,
      "distance_200sma_pct": 14.1,
      "rs_percentile": 92.4,
      "volume_surge": 1.45
    },
    "fundamentals": {
      "trailing_pe": 68.2,
      "forward_pe": 44.1,
      "debt_equity": 0.32,
      "fcf_yield_pct": 3.1,
      "rev_growth_yoy_pct": 31.5
    },
    "claude_audits": {
      "fundamentals_audit": "green_flags_outweigh (Operating cash flow +34%, net retention strong)",
      "catalyst_sentiment": "+3 earnings_beat (Q2 ARR beat and guidance raised)",
      "congress_signal": "0 (No transactions in 90 days)"
    }
  },
  ... (remaining 19 candidates)
]

JSON RESPONSE FORMAT:
[
  {
    "ticker": "CRWD",
    "opinion_score": 2,
    "stance": "bullish",
    "summary": "Tight consolidation within 2.5% of 50 SMA backed by 31% revenue growth provides an asymmetric continuation setup.",
    "key_risk": "High multiple leaves little room for guidance execution errors."
  }
]
```

---

## 3. The Look-Ahead / Training-Data-Leakage Problem

### 3.1 Quantitative vs LLM Historical Reliability

In `.sprint/council/antigravity-scoring.md` and `.sprint/SPRINT_PLAN_SCORING.md`, this council audited the mathematical formulas of `signal_engine.py` across historical walk-forward backtests. A numeric formula evaluated on historical OHLCV data has **zero look-ahead bias** when fed point-in-time price bars.

In stark contrast, an LLM CLI agent carries profound, invisible training-data leakage risks:
1. **Hindsight Contamination**: If asked to evaluate a historical setup from October 2023 for a stock like NVDA or SMCI, the underlying model (`gpt-5.6-sol`, Gemini, Claude) already possesses latent weights shaped by post-2023 price explosions. Even if instructed to "pretend it is 2023," neural representations cannot selectively purge subsequent market history.
2. **Survival Bias**: Models are intrinsically more familiar with historical winners that generated high volumes of post-event news and financial commentary.
3. **Invalidity for Historical Backtesting**: While `fundamentals_auditor.py` solves look-ahead bias by querying SEC EDGAR filings strictly filed before `as_of_date` via `_filing_index_url_asof()`, CLI agent reasoning on general stock setups cannot be honestly backtested against historical dates preceding the model's training cutoff.

### 3.2 Detection, Metadata Logging, and Mitigation Strategy

To maintain rigorous quantitative integrity, the architecture enforces three safeguards:

1. **Explicit Metadata Logging**:
   Every recorded opinion file in `data/agent_opinions/` must record model and engine provenance:
   ```json
   {
     "agent": "codex",
     "cli_version": "codex-v0.154.0",
     "underlying_model": "gpt-5.6-sol",
     "evaluation_timestamp": "2026-09-22T16:30:00Z",
     "model_cutoff_date": "2025-06-01",
     "is_forward_evaluation": true
   }
   ```
2. **Backtest Harness Exclusion**:
   In `scripts/walk_forward_backtest.py`, the Codex and Antigravity CLI agents **must be excluded** from historical simulation runs. Walk-forward backtests simulate years of historical step data; invoking CLI agents historically would be both economically prohibitive, prohibitively slow, and scientifically fraudulent due to look-ahead bias.
3. **Forward-Only Empirical Validation**:
   Validation of Codex and Antigravity second opinions must follow an honest **out-of-sample forward tracking** methodology:
   - Log daily opinions live starting from deployment date.
   - Correlate recorded opinion scores against 10-day, 20-day, and 60-day realized forward returns only for trades executed strictly after the deployment date.
4. **UI Disclaimer**:
   On the GUI Shortlist view and in daily emails, opinions are visually segregated. The Base Score is labeled as the "Audited Quantitative Signal," while Codex and Antigravity badges are explicitly tagged as "Experimental Qualitative Peer Review."

---

## 4. Shortlist Integration Mechanics (`build_shortlist`)

### 4.1 Ranking Formula and Weight Calibration

Per the user's explicit mandate:
- **Advisory only**: Contributes lightly to ranking.
- **Strictly no drop power**: Cannot disqualify candidates or append to `drop_reasons`.

Existing composite score formula in `src/agents/shortlist.py:52`:
```python
composite = s.get('combined_score', s.get('score', 0)) + catalyst_score * 2 + congress_score * 3
```

- Base score (`score`): Typically ranges between `80.0` and `105.0` for Top 20 candidates.
- `catalyst_score`: Integer `[-5..+5]`, scaled by `2` -> contribution `[-10.0..+10.0]`.
- `congress_score`: Float `[-3.0..+3.0]`, scaled by `3` -> contribution `[-9.0..+9.0]`.

**Proposed Second Opinion Integration**:
- `codex_score`: Integer in `[-2..+2]`, coefficient `1.0` -> contribution `[-2.0..+2.0]`.
- `antigravity_score`: Integer in `[-2..+2]`, coefficient `1.0` -> contribution `[-2.0..+2.0]`.
- Total Second Opinion contribution: `[-4.0..+4.0]`.

Updated composite formula:
```python
codex_score = codex_opinions.get(ticker, {}).get('opinion_score', 0)
agy_score = antigravity_opinions.get(ticker, {}).get('opinion_score', 0)

composite = (
    base_score
    + (catalyst_score * 2.0)
    + (congress_score * 3.0)
    + (codex_score * 1.0)
    + (agy_score * 1.0)
)
```

**Sensitivity and Impact**:
- In typical daily scans, the score separation between candidate #4, #5, #6, and #7 is often between 0.5 and 2.5 points.
- A candidate with unanimous bullish agreement (+2 from Codex, +2 from Antigravity = +4.0 points) will vault over closely clustered peers into the Top 5.
- A candidate with unanimous skepticism (-2 from Codex, -2 from Antigravity = -4.0 points) will slip below cleaner peers.
- However, a high-scoring candidate with a base score of 102 and strong catalyst (+3) will never be dropped solely because a CLI agent gave it -1 or -2. It remains eligible for the Top 5, fulfilling the requirement of advisory ranking influence without veto power.

### 4.2 Consensus vs Dissent Surfacing

Silently averaging divergent scores discards the most valuable qualitative insight. If Claude is bullish, Codex is bullish, but Antigravity issues a sharp dissent warning of decelerating gross margins or customer concentration, that dissent is high-value intelligence for the user.

The pipeline computes a structured **Consensus Classification** for each candidate:
- **Consensus State**:
  - `Unanimous Bullish`: All available AI reviewers have positive scores.
  - `Consensus Bullish (with Dissent)`: 2 or 3 positive, 1 negative.
  - `Split Opinion`: Equal balance of positive and negative reviews.
  - `Consensus Bearish / Cautious`: Majority negative reviews.
  - `Neutral / Indifferent`: All scores are 0.
- **Dissent Highlighting**:
  - When an agent deviates by >= 2 points from the prevailing consensus, the pipeline extracts that agent's `key_risk` and flags it as a `dissent_note`.
  - Example: `Consensus: Bullish (3/4) | Antigravity Dissent: "P/E 75 and decelerating QoQ billings."`

---

## 5. Storage Architecture and UI Design

### 5.1 Storage Layout

Following the established repository pattern in `data/fundamentals_audit/` and `data/catalyst_sentiment/`:

1. **Dedicated Council Output Directory**:
   `data/agent_opinions/`
   - Timestamped run files: `opinion_YYYYMMDD_HHMMSS.json`
   - Latest canonical file: `latest.json`
2. **Payload Structure**:
   ```json
   {
     "generated": "2026-09-22T16:30:00.000000",
     "scan_kind": "daily-full",
     "agent_metadata": {
       "codex": { "available": true, "version": "v0.154.0", "status": "ok", "latency_s": 74.2 },
       "antigravity": { "available": true, "version": "v1.2.8", "status": "ok", "latency_s": 51.8 }
     },
     "evaluations": {
       "CRWD": {
         "codex": { "score": 2, "stance": "bullish", "summary": "Clean Stage 2 continuation above 50 SMA.", "key_risk": "High multiple." },
         "antigravity": { "score": 1, "stance": "bullish", "summary": "Solid RS, watch earnings date.", "key_risk": "Upcoming earnings." },
         "consensus": "Unanimous Bullish (+3)"
       }
     }
   }
   ```
3. **Integration into `shortlist_latest.json`**:
   `data/daily_scans/shortlist_latest.json` is updated to include:
   - `codex_opinions`: Mapping of ticker -> evaluation dict.
   - `antigravity_opinions`: Mapping of ticker -> evaluation dict.
   - Each item in `shortlist` array records `codex_score`, `antigravity_score`, and `ai_consensus`.

### 5.2 UI Design on Shortlist View (`static/js/views/shortlist.js`)

The Shortlist card currently renders:
- Header: Rank, Ticker, Current Price, Mini Sparkline Chart
- Scores: Composite Score, Base Score
- Momentum slot, Consistency row, Backfill indicator
- Badges: Catalyst badge, Congress badge, Fundamentals flags
- Buy on Fidelity link

#### Problem: Card Bloat
Adding full paragraph verdicts from two more AI agents directly to the card would double card height, breaking grid layout and overwhelming the user with text.

#### Solution: Compact Badges with Collapsible Council Accordion
1. **Top-Level Micro-Badges**:
   In `.pick-badges`, render compact, styled badges:
   ```html
   <div class="council-badge-row">
     <span class="agent-badge pos">Codex +2</span>
     <span class="agent-badge pos">Antigravity +1</span>
     <span class="consensus-tag bullish">3/4 Bullish Consensus</span>
   </div>
   ```
   If an agent dissents (negative score while overall consensus is positive), render an amber/red warning pill:
   `<span class="agent-badge neg">Antigravity Dissent -1</span>`
2. **Expandable Detail Accordion (Matching Existing Repo Patterns)**:
   Below the badges, render a collapsed toggle matching the existing reasons expander:
   ```html
   <details class="council-details">
     <summary class="council-summary-btn">AI Council Opinions (4 Reviews) [v]</summary>
     <div class="council-tray">
       <div class="opinion-item"><b>Claude Fundamentals:</b> Green flags outweigh (Cash flow +34%)</div>
       <div class="opinion-item"><b>Claude Catalyst:</b> +3 Earnings beat</div>
       <div class="opinion-item"><b>Codex:</b> +2 Clean continuation base; key risk: high multiple</div>
       <div class="opinion-item"><b>Antigravity:</b> +1 Solid relative strength; key risk: upcoming earnings</div>
     </div>
   </details>
   ```
3. **Email Formatting**:
   In `src/notifications/email_notifier.py`, shortlist email tables include a single concise line per stock:
   `AI Council: 3/4 Bullish (Codex +2, Antigravity +1, Catalyst +3) | Risk: High multiple`

---

## 6. Failure and Degraded-Mode Behavior

### 6.1 Fault Isolation Axioms

Given that Antigravity failed three times in this session (headless auto-denials and process exits) and Codex calls can encounter network stalls, the pipeline must adhere to strict resilience axioms:

1. **Non-Blocking Execution**: An agent failure, process crash, non-zero return code, or timeout **never aborts the scan** and never raises an unhandled exception.
2. **N-of-N Optionality**: Both Codex and Antigravity are strictly optional peer signals. If Antigravity fails, the shortlist computes from Claude + Congress + Codex. If Codex also fails, it computes from Claude + Congress. If Claude agents are disabled, it computes purely from the Base Score.
3. **Neutral Missing Value (`0`)**: Any missing evaluation assigns `score = 0` (neutral effect on ranking).
4. **Transparent Degradation Logging**: When an agent fails, the failure reason is recorded in `data/logs/` and noted in `latest.json`:
   ```json
   "agent_metadata": {
     "antigravity": { "available": false, "status": "error", "error": "jetski headless permission auto-denied" }
   }
   ```
   The UI displays `[Antigravity: Skipped/Offline]` without broken markup.

---

## 7. Cost and Time Budget Estimation

### 7.1 GitHub Actions Workflow Constraints

- Workflow: `.github/workflows/daily_screening_git.yml`
- Scheduled runner limit: 120 minutes hard timeout.
- Baseline screening runtime: ~64 minutes (consistently observed across runs).
- Available Headroom: **~56 minutes**.

### 7.2 Latency Modeling for Second Opinion Step

| Scenario | Execution Mode | Codex Latency | Antigravity Latency | Total Additional Wall-Clock Time | Total Scan Duration | Headroom Remaining | CI Safety Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Typical Case** | Parallel (2 workers) | 60 - 90s | 45 - 60s | **~1.5 minutes (90s)** | ~65.5 min | ~54.5 min | Highly Safe |
| **Degraded (1 Hang)**| Parallel (2 workers) | 75s | 180s (timeout) | **3.0 minutes (180s)** | ~67.0 min | ~53.0 min | Highly Safe |
| **Worst Case (2 Hangs)**| Parallel (2 workers) | 180s (timeout)| 180s (timeout) | **3.0 minutes (180s)** | ~67.0 min | ~53.0 min | Highly Safe |
| **Sequential Fallback** | Serial (1 worker) | 90s | 60s | **~2.5 minutes (150s)**| ~66.5 min | ~53.5 min | Highly Safe |
| **Worst-Case Serial** | Serial (1 worker) | 180s (timeout)| 180s (timeout) | **6.0 minutes (360s)** | ~70.0 min | ~50.0 min | Highly Safe |

**Conclusion**: Under any scenario, whether executing smoothly, partially failing, or completely timing out, the maximum time added to the screening pipeline is strictly capped at **3.0 minutes in parallel mode** (or 6.0 minutes in serial mode). This consumes less than 6% of the remaining 56-minute CI headroom.

---

## 8. Critical Engineering Details Frequently Missed

### 8.1 The CI Runner Environment Reality Check
A major trap in this design is assuming that because `codex` and `agy` run on the user's local Mac workstation, they will automatically run inside GitHub Actions.
- GitHub Actions runs on clean, ephemeral `ubuntu-latest` virtual machines.
- `codex` and `agy` are proprietary CLI binaries. They are **not installed by default** on Ubuntu runners, nor are user session credentials (`~/.codex/config.toml`, `~/.gemini/antigravity-cli`) present unless explicitly injected via repository secrets or installed in workflow setup steps.
- **Harness Requirement**:
  The orchestrator must implement an explicit pre-flight check:
  ```python
  def is_agent_available(binary_name: str) -> bool:
      path = shutil.which(binary_name)
      if not path:
          logger.info(f"CLI agent '{binary_name}' not found on PATH; skipping.")
          return False
      return True
  ```
  If `shutil.which('codex')` or `shutil.which('agy')` returns `None`, the module marks that agent as unavailable, skips execution instantly with 0ms overhead, and proceeds. This guarantees that **CI continues running without breaking**, while local manual scans or dedicated self-hosted runners execute the full council analysis!

### 8.2 Subprocess Memory and Descriptor Leaks
Running CLI agents via Python `subprocess.run()` without piping can cause standard output buffers to fill, deadlocking child processes if output exceeds 64KB.
- Standard output and error must be routed to temporary files or captured via `subprocess.Popen.communicate()` with explicit buffer handling.
- Process groups must be closed and file descriptors released properly.

### 8.3 Cache and Idempotency
If a user reruns `run_optimized_scan.py` with `--rescore-only` or `--test-mode`, re-invoking CLI agents every time wastes minutes.
- Opinion results must be cached by date and ticker hash in `data/agent_opinions/`.
- If an opinion file for the current date and candidate list already exists within 12 hours, reload the cached opinions instead of spawning fresh CLI sessions.

---

## 9. Concrete Task Breakdown for Future Sprint

Per session governance rules:
- Antigravity is assigned **review-only** duties and must not be assigned implementation or test-running tasks.
- Implementation and test tasks are allocated between **Claude** and **Codex**.

### Task sc-TASK-001: CLI Subprocess Harness & Parsing Engine
- **Owner**: Codex  
- **Dependencies**: None  
- **Scope**: Create `src/agents/cli_agent_runner.py`.
- **Deliverables**:
  - `CLIAgentRunner` class with binary discovery (`shutil.which`).
  - Isolated subprocess execution using `start_new_session=True` and `os.killpg` on timeout.
  - Hard timeouts (180s) and error logging.
  - Three-tier resilient parser (Direct JSON -> Fenced Block -> Regex item extractor).
- **Acceptance Criteria**:
  - Unit tests covering: clean JSON array, markdown-fenced JSON, preamble text followed by JSON, truncated JSON, and process timeout.
  - Zero uncaught exceptions on malformed output or CLI death.

### Task sc-TASK-002: Prompt Formatter & Opinion Council Orchestrator
- **Owner**: Claude  
- **Dependencies**: sc-TASK-001  
- **Scope**: Create `src/agents/opinion_council.py`.
- **Deliverables**:
  - `OpinionCouncil` orchestrator extracting top 20 candidate summaries.
  - Prompt construction grounding candidates with signal engine metrics, fundamental snapshots, and Claude audit verdicts.
  - Concurrent dispatch of Codex and Antigravity runners via `concurrent.futures.ThreadPoolExecutor(max_workers=2)`.
  - Persistence to `data/agent_opinions/opinion_<timestamp>.json` and `latest.json`.
- **Acceptance Criteria**:
  - Correct formatting of 20-candidate payload.
  - Concurrent execution verified: total wall-clock runtime equals `max(T_codex, T_agy)`, not sum.
  - Empty dict returned on agent unavailability without raising errors.

### Task sc-TASK-003: Shortlist Integration & Ranking Logic
- **Owner**: Claude  
- **Dependencies**: sc-TASK-002  
- **Scope**: Modify `src/agents/shortlist.py` and `run_optimized_scan.py`.
- **Deliverables**:
  - Extend `build_shortlist()` signature to accept `codex_opinions` and `antigravity_opinions`.
  - Add additive terms: `+(codex_score * 1.0) + (antigravity_score * 1.0)` to `composite_score`.
  - Guard: Confirm that neither opinion can add to `drop_reasons` or affect `passed_filters`.
  - Compute `consensus_state` and detect individual agent dissents.
  - Persist council fields into `data/daily_scans/shortlist_latest.json`.
- **Acceptance Criteria**:
  - `build_shortlist` tests verify that candidate ranking adjusts by +/-4.0 points maximum.
  - Negative scores never drop a candidate from the shortlist.
  - Complete backwards compatibility when council dictionaries are `None` or `{}`.

### Task sc-TASK-004: Dashboard Web UI & Expandable Council Cards
- **Owner**: Codex  
- **Dependencies**: sc-TASK-003  
- **Scope**: Update `static/js/views/shortlist.js` and `static/css/dashboard.css`.
- **Deliverables**:
  - Render compact council micro-badges (`[Codex +1]`, `[Antigravity +2]`, `[Dissent Alert]`).
  - Add `<details class="council-details">` collapsible tray revealing detailed agent summaries and identified key risks.
  - Maintain existing card height when accordion is closed.
- **Acceptance Criteria**:
  - UI renders cleanly with 0, 1, or 2 CLI opinions present.
  - Layout matches existing dark-theme styling and does not overflow on mobile or desktop viewports.

### Task sc-TASK-005: End-to-End Degraded-Mode & CI Safety Suite
- **Owner**: Claude  
- **Dependencies**: sc-TASK-001 through sc-TASK-004  
- **Scope**: Integration testing and GitHub Actions workflow compatibility.
- **Deliverables**:
  - Comprehensive test suite in `tests/test_opinion_council.py` testing mock timeouts, mock process crashes, and missing binary scenarios.
  - Verify `run_optimized_scan.py --test-mode` executes without failure when CLI tools are absent.
- **Acceptance Criteria**:
  - 100% pass rate on test suite.
  - Full pipeline completes cleanly in under 5 minutes in test mode without CLI tools installed.

---

## 10. Summary and Recommendations for Council Vote

1. **Vote Recommendation**: **APPROVE WITH ARCHITECTURAL SAFEGUARDS**.
2. Incorporating Codex and Antigravity as peer reviewers provides valuable multi-perspective validation for the user's live capital allocation.
3. The design strictly preserves user mandates: **zero new API keys**, **advisory ranking influence only**, and **strictly no drop power**.
4. By utilizing **1 batched parallel call**, **headless permission auto-skip**, **strict tool suppression**, and **a 180-second hard process-group timeout**, the feature safely operates within a ~1.5 to 3.0 minute runtime footprint, fully protecting the 56-minute CI headroom.
5. With pre-flight binary discovery and 3-tier parsing, the system is completely resilient against tool crashes and environment differences.
