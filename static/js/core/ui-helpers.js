import { fetchJSON } from './api.js';
import { openChartModal, refreshChartModal } from './chart-modal.js';
import { startJob } from './jobs.js';

const CHART_ICON = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 6"/><polyline points="15 6 21 6 21 12"/></svg>';

function attr(value) {
  return String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
}

export function analysisButtonHTML(ticker, contextKey = ticker, disabled = false) {
  const safeTicker = attr(ticker);
  return `<button class="chart-analysis-btn" type="button" data-ticker="${safeTicker}" data-analysis-key="${attr(contextKey)}" title="Open ${safeTicker} price analysis" aria-label="Open ${safeTicker} price analysis"${disabled ? ' disabled' : ''}>${CHART_ICON}</button>`;
}

export function wireAnalysisButtons(container, getSeries) {
  container.querySelectorAll('.chart-analysis-btn').forEach(button => {
    if (button.dataset.analysisWired === 'true') return;
    const series = getSeries(button.dataset.analysisKey);
    button.disabled = !series;
    if (!series) return;
    button.dataset.analysisWired = 'true';
    button.addEventListener('click', () => {
      const latest = getSeries(button.dataset.analysisKey);
      if (latest) openChartModal({ ...latest, ticker: button.dataset.ticker, triggerEl: button });
    });
  });
}

export function refreshAnalysisModal(getSeries) {
  refreshChartModal(getSeries);
}

const MOMENTUM_LABELS = { hot: 'HOT', stable: 'STABLE', basing: 'BASING', avoid: 'AVOID' };

function momentumBadgeHTML(entry) {
  if (!entry || !entry.status) return '';
  const label = MOMENTUM_LABELS[entry.status] || entry.status.toUpperCase();
  const dayWord = entry.days === 1 ? 'day' : 'days';
  return `<span class="momentum-badge ${entry.status}" title="${entry.label} — ${entry.days} ${dayWord}">${label}<span class="streak">Day ${entry.days}</span></span>`;
}

export async function loadMomentumStatus(tickers, group, onLoaded) {
  if (!tickers.length) return;
  await startJob('momentum-status', { tickers, group }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON(`/api/momentum-status/${group}`);
    onLoaded(data.status || {});
  });
}

export function paintMomentumSlots(tickers, statusMap) {
  tickers.forEach(ticker => {
    const slot = document.getElementById(`momentum-slot-${ticker}`);
    if (slot && statusMap[ticker]) slot.innerHTML = momentumBadgeHTML(statusMap[ticker]);
  });
}

export function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.opacity = '1';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.opacity = '0'; }, 5000);
}

export function redditCell(count) {
  if (count == null) return '<span style="color:var(--muted)">-</span>';
  if (count === 0) return '<span style="color:var(--muted)">0</span>';
  const hot = count >= 10;
  return `<span style="color:${hot ? 'var(--yellow)' : 'var(--text)'};font-weight:${hot ? 700 : 400}">${count}</span>`;
}

export function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text == null ? '' : String(text);
  return div.innerHTML;
}

export function cleanEmoji(text) {
  return (text || '').replace(/[\uD83D\uDFE2\uDD34\uDFE1\u2B50\u26A0\u2713\uDEA8]/g, '').trim();
}

// External news URLs must not be able to introduce executable schemes.
export function safeHref(url) {
  try {
    const parsed = new URL(url, location.href);
    return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '#';
  } catch {
    return '#';
  }
}

export function toggleReasons(btn) {
  const extra = btn.previousElementSibling;
  if (extra.style.display === 'none') {
    extra.style.display = '';
    btn.textContent = 'less';
  } else {
    extra.style.display = 'none';
  }
}

export function fidelityLink(ticker, label, cls) {
  return `<a class="trade-link ${cls}" href="https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol=${ticker}" target="_blank" rel="noopener">${label} ↗</a>`;
}

export function renderTop20Table(top20) {
  if (!top20.length) return '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan from the Full Scan page.</p></div>';
  const rows = top20.map((s, i) => {
    const links = (s.why_links || []).slice(0, 3).map(l =>
      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
    ).join('');
    return `<tr>
      <td>#${i + 1}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td><span class="score-num">${s.combined_score ?? s.score ?? '-'}</span></td>
      <td><span id="momentum-slot-${s.ticker}"></span></td>
      <td><span id="consistency-slot-top20-${s.ticker}"></span></td>
      <td>${redditCell(s.reddit_mentions_24h)}</td>
      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
    </tr>`;
  }).join('');
  return `
    <div class="card">
      <h2>Top 20 — Combined Pool</h2>
      <div class="consistency-caption" id="consistency-caption-top20"></div>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Combined Score</th><th scope="col">Momentum</th><th scope="col">Consistency</th><th scope="col">Reddit</th><th scope="col">Why it's moving</th><th scope="col">Trade</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;
}
