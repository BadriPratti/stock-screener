You are participating in a full Engineering Council (HARD-classified: this adds to a live financial recommendation
pipeline). Do NOT modify any file except the single output file named for you below.

Repository: /Users/badripratti/Desktop/stock-screener (Flask + pywebview stock screener). NEVER open/reference
`position/`.

## The user's request (their words)
"we also need to incorporate codex and antigravity to also do these stock analysis before going into the app...
they need a say of their own before going [into the app]"

Clarified via direct questions to the user:
- No new API keys will be obtained (no OpenAI/Google Gemini keys) - this must use the `codex exec` and `agy -p`
  CLI tools this session has been using all day for engineering work, NOT a lightweight direct model API call.
- Advisory only at first: contributes LIGHTLY to ranking (like the existing Catalyst Sentiment signal does), but
  must NOT be able to drop a stock from the shortlist outright (unlike the existing Fundamentals Auditor, which can).

## Mandatory context: how this app already does exactly this pattern with Claude
`src/agents/shortlist.py` `build_shortlist()` combines independent signals into the final Top 5:
- `fundamentals_audits` (from `src/agents/fundamentals_auditor.py`) - CAN drop a candidate outright
  (`overall_assessment == 'red_flags_outweigh'`).
- `catalyst_sentiments` (from `src/agents/catalyst_sentiment.py`) - contributes `catalyst_score * 2` to
  `composite_score`; also drops a candidate if `catalyst_score <= -2`.
- `congress_signals` - contributes `congress_score * 3`.
Both `fundamentals_auditor.py` and `catalyst_sentiment.py` call Claude directly via the Anthropic SDK
(`src/agents/llm_client.py`, `model = "claude-opus-5"`) - ONE fast API call per ticker, not an agentic CLI session.
This is run today ONLY on the Top 20 pool (`run_optimized_scan.py`, guarded by `--enable-llm-agents`), never on
the full ~2,000-stock analyzed universe, specifically to keep cost/time bounded.

## The real constraint you must design around: `codex exec`/`agy -p` are slow, heavyweight, unreliable CLI AGENTS
This is NOT the same as calling a model API directly. Observed today, in this very session: single `codex exec`
investigation calls took anywhere from under a minute to 10+ minutes; `agy -p` calls were similarly variable and
FAILED OUTRIGHT THREE TIMES on pure read-only investigation tasks (once an explicit headless permission denial,
twice a silent process death with no output and no error, requiring relaunch). These are coding/tool-use agents,
not designed for a quick structured per-item judgment call. Calling either CLI once PER TICKER (20 separate calls
each, 40 total) is very likely infeasible within the daily scan's time budget and reliability bar.

The existing daily GitHub Actions scan already runs ~64 minutes against a 120-minute hard timeout (~56 min of
real headroom) that also must fit the LLM-agent Fundamentals Auditor + Catalyst Sentiment step, email delivery,
and git commit/push. Whatever you design must fit inside that remaining headroom AND be safe to fail (per the
user's "advisory only" decision, a Codex/Antigravity failure must never block or delay the real shortlist/email).

## What you must design (not just discuss abstractly)
1. **Call shape**: one BATCHED call per agent (Codex, Antigravity) analyzing the whole Top 20 pool together in a
   single invocation, returning structured per-ticker output - is this actually reliable? CLI agents like these
   aren't built with an API's JSON-mode guarantee; investigate how reliably you can get them to return
   machine-parseable structured output (e.g. a fenced JSON block at the end of their response) versus prose that
   needs a second parsing pass, and design a robust parser with a sane fallback (a ticker with unparseable output
   contributes nothing, doesn't crash the run). Consider whether one call per agent covering all 20 tickers, or a
   small number of batches (e.g. 4 batches of 5), is more reliable/faster - you have real data from this session's
   own `.sprint/logs/` to estimate a single call's real-world latency for a comparably-sized prompt; look at it.
   Recommend a hard per-call timeout and what happens on timeout (kill it, log a warning, proceed without that
   agent's contribution for that day - never retry-loop indefinitely in a scheduled workflow).
2. **What data to give them**: the same real data the existing agents get access to (ticker, current price,
   technical score/phase/entry-quality/RS from `signal_engine.py`'s output, the fundamentals snapshot, recent
   price history, the Fundamentals Auditor's and Catalyst Sentiment's own verdicts if available) so their opinion
   is grounded, not a guess from stale training-data knowledge of the ticker. Design the actual prompt shape.
3. **The look-ahead/training-data-leakage problem** (the user was warned about this, take it seriously): unlike a
   pure numeric formula, an LLM's opinion about TICKER X on DATE Y might be influenced by what the model already
   "knows" happened to that ticker from its training data, not genuine forward-looking analysis. This makes any
   future backtesting of "did Codex's/Antigravity's opinion predict returns" unreliable in the same rigorous way
   `.sprint/SPRINT_PLAN_SCORING.md` just validated the numeric formula. Propose how to detect or at least document
   this risk (e.g. logging model/training-cutoff metadata if obtainable, being explicit in the UI that this is an
   unvalidated qualitative signal, not something with the same evidentiary weight as the backtested numeric score).
4. **How it plugs into `build_shortlist()`**: given "advisory, light ranking influence, no drop power," propose the
   exact mechanism - e.g. a small additive term to `composite_score` mirroring `catalyst_score * 2`, with a small
   coefficient, explicitly logged/labeled as experimental. Should the two agents' opinions be combined (averaged,
   require agreement) or kept as two separate, individually-visible signals? What happens if they disagree with
   each other or with the existing Claude-based agents - should that disagreement itself be surfaced to the user
   as interesting information (e.g. "3 of 4 AI reviewers like this pick, 1 disagrees: <reason>") rather than just
   averaged away silently?
5. **Storage and UI**: where does the output persist (mirror `data/fundamentals_audit/`, `data/catalyst_sentiment/`
   pattern?) and how does it surface - the Shortlist view already shows Fundamentals/Catalyst/Congress reasoning
   per card; design how a third and fourth opinion fit there without making the cards enormous (collapsed/
   expandable? a compact per-agent badge with the full reasoning on click/expand, matching this repo's existing
   preference for collapsed detail with an expand affordance - e.g. the Buy/Sell reasons list already does this).
6. **Failure/degraded-mode behavior**: given Antigravity's proven unreliability today, the pipeline must produce a
   complete, correct shortlist even if Antigravity fails outright every single day. Codex is more reliable but
   still not guaranteed. Design this as N-of-N optional signals, never required.
7. **Cost/time budget estimate**: give real numbers - how many extra minutes does this likely add to the daily
   ~64-minute run (worst case and typical case), and is it safe within the 120-minute CI timeout alongside
   everything else already in that job.
8. Anything else you think the other engineers or the user is likely to miss.

## Constraints
- Do not propose weakening the "advisory only, no drop power" decision - that's final, decided by the user.
- Do not propose adding new API keys/providers - decided, use the existing CLI tools only.
- No emoji. This is a plan only - do not implement anything.
- Give a concrete task breakdown at the end (owner suggestion Claude/Codex, dependencies, acceptance criteria) for
  a future HARD-classified /sprint-build. Per this session's established policy, Antigravity should NOT be
  assigned implementation/test-running tasks in your task breakdown (review-only), given its proven headless
  unreliability - even though it may end up being one of the two "opinion" agents the FEATURE itself calls, that
  is a very different thing from Antigravity being relied on to BUILD the feature correctly during this sprint.

Write your full analysis to the file named for you below. Also print a short summary to stdout.
