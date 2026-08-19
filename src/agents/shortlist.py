"""Builds the final Top 5 shortlist from the Top 20 pool by actually filtering on
the LLM agents' output, instead of just labeling it.

Drop rules (a candidate is filtered out of the ranked pool, not the email —
see below):
  - Fundamentals Auditor says red flags outweigh green flags
  - Catalyst Sentiment score <= -2 (a real negative catalyst, not just noise)

Survivors are ranked by composite_score = technical score + catalyst_score*2 +
congress_score*3 (congress weighted highest since it's a distinct, hard-to-fake
data source; catalyst next since it's Claude's live news read; base score is
already what got the candidate into the Top 20 pool in the first place).

If fewer than `size` candidates survive the drop rules, the list is backfilled
from the filtered-out pool (best composite_score first) so the email is never
empty on a slow-news day — those backfilled entries keep their drop_reasons so
it's visible in the email that they didn't fully clear the bar.
"""

from typing import Dict, List, Optional


def build_shortlist(
    top20: List[Dict],
    fundamentals_audits: Optional[Dict[str, Dict]] = None,
    catalyst_sentiments: Optional[Dict[str, Dict]] = None,
    congress_signals: Optional[Dict[str, Dict]] = None,
    size: int = 5,
) -> List[Dict]:
    fundamentals_audits = fundamentals_audits or {}
    catalyst_sentiments = catalyst_sentiments or {}
    congress_signals = congress_signals or {}

    scored = []
    for s in top20:
        ticker = s['ticker']
        drop_reasons = []

        audit = fundamentals_audits.get(ticker)
        if audit and audit.get('overall_assessment') == 'red_flags_outweigh':
            drop_reasons.append('Fundamentals Auditor: red flags outweigh green')

        sentiment = catalyst_sentiments.get(ticker)
        catalyst_score = sentiment.get('catalyst_score', 0) if sentiment else 0
        if sentiment and catalyst_score <= -2:
            ctype = (sentiment.get('catalyst_type') or 'other').replace('_', ' ')
            drop_reasons.append(f"Catalyst Sentiment: {ctype} ({catalyst_score:+d})")

        congress = congress_signals.get(ticker)
        congress_score = congress.get('score', 0) if congress else 0

        composite = s.get('combined_score', s.get('score', 0)) + catalyst_score * 2 + congress_score * 3

        scored.append({
            **s,
            'drop_reasons': drop_reasons,
            'passed_filters': not drop_reasons,
            'catalyst_score': catalyst_score,
            'congress_score': congress_score,
            'composite_score': round(composite, 2),
        })

    passed = sorted(
        [s for s in scored if s['passed_filters']],
        key=lambda s: s['composite_score'], reverse=True,
    )
    shortlist = passed[:size]

    if len(shortlist) < size:
        chosen_tickers = {s['ticker'] for s in shortlist}
        backfill = sorted(
            [s for s in scored if s['ticker'] not in chosen_tickers],
            key=lambda s: s['composite_score'], reverse=True,
        )
        shortlist += backfill[:size - len(shortlist)]

    return shortlist
