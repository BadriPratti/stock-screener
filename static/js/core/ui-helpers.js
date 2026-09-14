import { fetchJSON } from './api.js';
import { startJob } from './jobs.js';

const CHART_ICON = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 6"/><polyline points="15 6 21 6 21 12"/></svg>';
const _openCharts = new Set();

export function chartToggleButtonHTML(chartId) {
  return `<button class="chart-toggle-btn" data-chart-id="${chartId}" title="Price history">${CHART_ICON}</button>`;
}

export function wireChartToggles(container, getSeries, idPrefix) {
  container.querySelectorAll('.chart-toggle-btn').forEach(btn => {
    const chartId = btn.dataset.chartId;
    const wrap = document.getElementById(`${chartId}-wrap`);
    if (!wrap) return;
    const ticker = chartId.slice(idPrefix.length);

    if (_openCharts.has(chartId)) {
      wrap.style.display = 'block';
      btn.classList.add('active');
      const series = getSeries(ticker);
      if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
    }

    btn.addEventListener('click', () => {
      const nowVisible = wrap.style.display !== 'block';
      wrap.style.display = nowVisible ? 'block' : 'none';
      btn.classList.toggle('active', nowVisible);
      if (nowVisible) {
        _openCharts.add(chartId);
        const series = getSeries(ticker);
        if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
      } else {
        _openCharts.delete(chartId);
      }
    });
  });
}

export function refreshOpenCharts(getSeries, idPrefix) {
  _openCharts.forEach(chartId => {
    if (!chartId.startsWith(idPrefix)) return;
    if (!document.getElementById(`${chartId}-wrap`)) return;
    const ticker = chartId.slice(idPrefix.length);
    const series = getSeries(ticker);
    if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
  });
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
      <td>${redditCell(s.reddit_mentions_24h)}</td>
      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
    </tr>`;
  }).join('');
  return `
    <div class="card">
      <h2>Top 20 — Combined Pool</h2>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Combined Score</th><th scope="col">Momentum</th><th scope="col">Reddit</th><th scope="col">Why it's moving</th><th scope="col">Trade</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;
}
