import { fetchJSON } from '../core/api.js';
import { startJob } from '../core/jobs.js';
import { _liveGuarded, _startLive } from '../core/refresh.js';
import { content, currentView, pageMeta } from '../core/state.js';
import {
  chartToggleButtonHTML,
  escapeHtml,
  fidelityLink,
  loadMomentumStatus,
  paintMomentumSlots,
  refreshOpenCharts,
  renderTop20Table,
  wireChartToggles,
} from '../core/ui-helpers.js';

let _shortlistPrices = {};
let _newsSectionHTML;
let _loadNewsGroup;

export function configureShortlistNews({ newsSectionHTML, loadNewsGroup }) {
  _newsSectionHTML = newsSectionHTML;
  _loadNewsGroup = loadNewsGroup;
}

function catalystBadgeHTML(sentiment) {
  if (!sentiment) return '';
  const score = sentiment.catalyst_score || 0;
  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
  const ctype = (sentiment.catalyst_type || 'other').replace(/_/g, ' ');
  const sign = score > 0 ? '+' : '';
  return `<div><span class="agent-badge ${cls}">Catalyst ${sign}${score} — ${escapeHtml(ctype)}</span>
    <div class="agent-badge-sub">${escapeHtml(sentiment.summary)}</div></div>`;
}

function congressBadgeHTML(signal) {
  if (!signal || !signal.has_data) return '';
  const score = signal.score || 0;
  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
  const sign = score > 0 ? '+' : '';
  return `<div><span class="agent-badge ${cls}">Congress ${sign}${score.toFixed(1)}</span>
    <div class="agent-badge-sub">${escapeHtml(signal.summary)}</div></div>`;
}

function fundamentalsFlagsHTML(audit) {
  if (!audit) return '';
  const red = audit.red_flags || [];
  const green = audit.green_flags || [];
  let html = '';
  if (red.length) {
    const more = red.length > 1 ? ` (+${red.length - 1} more)` : '';
    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${escapeHtml(red[0].flag)}${more}</div>`;
  }
  if (green.length) {
    const more = green.length > 1 ? ` (+${green.length - 1} more)` : '';
    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
  }
  return html;
}

export async function renderShortlistView() {
  const data = await fetchJSON('/api/shortlist');
  if (currentView !== 'shortlist') return; // navigated away before this resolved
  // Set regardless of which branch below renders — a scan that legitimately
  // found zero candidates still has a real `generated` timestamp, and the
  // empty-state banner needs it to distinguish "no scan has ever run" from
  // "today's scan ran and found nothing" (see the two banner messages below).
  pageMeta.textContent = data.generated ? `Generated ${new Date(data.generated).toLocaleString()}` : '';
  if (!data.shortlist || data.shortlist.length === 0) {
    const top20 = await fetchJSON('/api/top20');
    if (currentView !== 'shortlist') return;
    // `result` (added alongside `generated`) distinguishes "no scan has run
    // yet" (data.generated is null) from "a scan ran and legitimately found
    // zero qualifying candidates" (data.result === 'no_candidates') — without
    // this, both looked identical and a normal empty trading day read as if
    // the pipeline were broken.
    const banner = !data.generated
      ? `No filtered shortlist yet — run a scan with AI agents enabled from the
         <a href="#/scan">Full Scan</a> page to get a Top 5 filtered by fundamentals,
         news sentiment, and congressional trading. Showing the raw Top 20 pool below instead.`
      : `Today's scan (generated ${new Date(data.generated).toLocaleString()}) found no candidates that
         passed screening criteria — this can happen on a normal trading day. Showing the raw Top 20
         pool below instead.`;
    content.innerHTML = `
      <div class="banner">${banner}</div>
      ${renderTop20Table(top20.top20 || [])}
    `;
    const fallbackTickers = (top20.top20 || []).map(s => s.ticker);
    loadMomentumStatus(fallbackTickers, 'shortlist-fallback', (statusMap) => paintMomentumSlots(fallbackTickers, statusMap));
    return;
  }

  const tickers = data.shortlist.map(s => s.ticker);

  const cards = data.shortlist.map((s, i) => {
    const badges = [
      catalystBadgeHTML(data.catalyst_sentiments[s.ticker]),
      congressBadgeHTML(data.congress_signals[s.ticker]),
      fundamentalsFlagsHTML(data.fundamentals_audits[s.ticker]),
    ].filter(Boolean).join('');
    const backfillNote = !s.passed_filters
      ? `<div class="backfill-note">Backfilled — didn't clear filters: ${(s.drop_reasons || []).join('; ') || 'below filter bar'}</div>`
      : '';
    const chartId = `short-chart-${s.ticker}`;
    return `
      <div class="pick-card ${!s.passed_filters ? 'backfilled' : ''}">
        <div class="pick-rank">#${i + 1}</div>
        <div class="pick-header">
          <span class="ticker">${s.ticker}</span>
          <span id="${chartId}-slot"></span>
        </div>
        <div class="pick-scores">
          <div class="score-block"><div class="label">Composite</div><div class="value">${s.composite_score ?? '-'}</div></div>
          <div class="score-block"><div class="label">Base Score</div><div class="value">${s.combined_score ?? s.score ?? '-'}</div></div>
        </div>
        <div style="margin-bottom:10px"><span id="momentum-slot-${s.ticker}"></span></div>
        ${backfillNote}
        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
        ${fidelityLink(s.ticker, 'Buy on Fidelity', 'buy')}
        <div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
      </div>`;
  }).join('');

  content.innerHTML = `
    <div class="source-note email">
      <b>This is what your daily email sends.</b> Same 5 picks, same links — the email is just a snapshot of this page.
    </div>
    <div class="shortlist-grid">${cards}</div>
    <div id="shortlistNews" style="margin-top:24px"></div>`;

  loadShortlistCharts(tickers);
  loadShortlistNews(tickers);
  loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap));
  _startLive(() => {
    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
    _liveGuarded('shortlist-news', () => loadShortlistNews(tickers, true));
    _liveGuarded('shortlist-momentum', () => loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap)));
  });
}

function _shortlistSeries(ticker) {
  const h = _shortlistPrices[ticker];
  return h && h.length ? { history: h, entry: null, stop: null } : null;
}

async function loadShortlistCharts(tickers, silent) {
  if (!tickers.length) return;
  await startJob('price-history', { tickers, group: 'shortlist' }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON('/api/price-history/shortlist');
    _shortlistPrices = data.prices || {};

    if (!silent) {
      tickers.forEach(ticker => {
        const slot = document.getElementById(`short-chart-${ticker}-slot`);
        if (slot && _shortlistPrices[ticker] && _shortlistPrices[ticker].length) {
          slot.innerHTML = chartToggleButtonHTML(`short-chart-${ticker}`);
        }
      });
      wireChartToggles(content, _shortlistSeries, 'short-chart-');
    } else {
      refreshOpenCharts(_shortlistSeries, 'short-chart-');
    }
  });
}

async function loadShortlistNews(tickers, silent) {
  const el = document.getElementById('shortlistNews');
  if (!el) return;
  if (!silent) {
    el.innerHTML = _newsSectionHTML('shortlist', 'News on your shortlist', 'loading');
  }
  await _loadNewsGroup('shortlist', tickers, 'No shortlist yet.', silent);
}
