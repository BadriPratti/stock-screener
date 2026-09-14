import { fetchJSON } from '../core/api.js';
import { startJob } from '../core/jobs.js';
import { _liveGuarded, _startLive, liveBadgeHTML } from '../core/refresh.js';
import { content, currentView, pageMeta } from '../core/state.js';
import {
  cleanEmoji,
  escapeHtml,
  fidelityLink,
  loadMomentumStatus,
  paintMomentumSlots,
  redditCell,
  renderTop20Table,
  safeHref,
} from '../core/ui-helpers.js';

let _marketTop20Tickers = [];

export async function renderMarketView() {
  const scans = await fetchJSON('/api/scans');
  if (currentView !== 'market') return; // navigated away before this resolved
  if (!scans.length) {
    content.innerHTML = '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan to get started.</p></div>';
    return;
  }
  content.innerHTML = `
    <div class="source-note email">
      <b>This is the full pool your email's picks are drawn from.</b> Buy/Sell Signals and the Top 20 table
      here are the same lists that get emailed (capped at 15 rows there; everything's shown here) — the
      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
    </div>
    <div style="margin-bottom:16px">
      <select class="scan-select" id="scanSelect"></select>
    </div>
    <div id="marketBody"></div>
    <div id="newsSections" style="margin-top:24px"></div>`;
  const sel = document.getElementById('scanSelect');
  scans.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.path;
    opt.textContent = s.date.replace('_', ' ');
    sel.appendChild(opt);
  });
  sel.addEventListener('change', () => loadMarketScan(sel.value));
  loadMarketScan(scans[0].path);
  loadMarketNews();
  _startLive(() => {
    _liveGuarded('market-news', () => loadMarketNews(true));
    _liveGuarded('market-momentum', () => loadMomentumStatus(
      _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
    ));
  });
}

async function loadMarketNews(silent) {
  const el = document.getElementById('newsSections');
  if (!el) return; // navigated away before this resolved
  if (!silent) {
    el.innerHTML = _newsSectionHTML('positions', 'News on your positions', 'loading') +
                    _newsSectionHTML('buy', "News on what the scanner's telling you to buy", 'loading');
  }

  const [positionsData, top20Data] = await Promise.all([
    fetchJSON('/api/positions'), fetchJSON('/api/top20'),
  ]);
  const positionTickers = (positionsData.position_analyses || []).map(a => a.ticker);
  const buyTickers = (top20Data.top20 || []).slice(0, 8).map(s => s.ticker);

  await Promise.all([
    _loadNewsGroup('positions', positionTickers, 'Upload your positions in the Positions tab to see news for them here.', silent),
    _loadNewsGroup('buy', buyTickers, 'No Top 20 pool yet — run a scan from the Full Scan tab first.', silent),
  ]);
}

export function _newsSectionHTML(group, title, bodyHTML) {
  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
}

export async function _loadNewsGroup(group, tickers, emptyMsg, silent) {
  const bodyEl = document.getElementById(`news-${group}-body`);
  if (!bodyEl) return; // navigated away before this resolved
  if (!tickers.length) {
    bodyEl.innerHTML = `<div style="color:var(--muted);font-size:13px">${emptyMsg}</div>`;
    return;
  }
  if (!silent) {
    bodyEl.innerHTML = '<div style="color:var(--muted);font-size:13px"><span class="spinner"></span> Fetching real headlines…</div>';
  }

  await startJob('news', { tickers, group }, async (st) => {
    const el = document.getElementById(`news-${group}-body`);
    if (!el) return; // navigated away mid-job
    if (st.status === 'success') {
      const data = await fetchJSON(`/api/news/${group}`);
      el.innerHTML = _renderNewsGroupHTML(data.news || {});
    } else if (!silent && (st.status === 'error' || st.status === 'stopped')) {
      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
    }
  });
}

function _renderNewsGroupHTML(newsByTicker) {
  const tickers = Object.keys(newsByTicker);
  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
  return `<div class="news-ticker-grid">${tickers.map(ticker => {
    const items = newsByTicker[ticker] || [];
    const list = items.length
      ? items.map(h => `
          <a href="${safeHref(h.url)}" target="_blank" rel="noopener" class="news-headline">
            <div class="news-headline-title">${escapeHtml(h.title)}</div>
            <div class="news-headline-meta">${escapeHtml(h.publisher || 'Unknown source')}${h.pub_date ? ' · ' + escapeHtml(new Date(h.pub_date).toLocaleDateString()) : ''}</div>
          </a>`).join('')
      : '<div style="color:var(--muted);font-size:12px">No recent headlines.</div>';
    return `<div class="news-ticker-block"><div class="ticker" style="margin-bottom:6px">${escapeHtml(ticker)}</div>${list}</div>`;
  }).join('')}</div>`;
}

async function loadMarketScan(path) {
  const [scan, top20] = await Promise.all([
    fetchJSON('/api/scan?path=' + encodeURIComponent(path)),
    fetchJSON('/api/top20'),
  ]);
  if (currentView !== 'market') return; // navigated away before this resolved
  if (scan.error) {
    document.getElementById('marketBody').innerHTML = '<div class="no-data"><h2>No scan data</h2></div>';
    return;
  }
  pageMeta.textContent = `${scan.scan_date} · ${scan.stats.analyzed || '?'} analyzed · ${scan.regime}`;

  const buyCount = scan.stats.buy_count ?? scan.buy_signals.length;
  const sellCount = scan.stats.sell_count ?? scan.sell_signals.length;
  const topScore = scan.buy_signals.length ? scan.buy_signals[0].score : '-';
  const regimeClass = scan.regime.includes('RISK-ON') ? 'risk-on' : scan.regime.includes('RISK-OFF') ? 'risk-off' : 'transitional';

  document.getElementById('marketBody').innerHTML = `
    <div class="stats-row">
      <div class="stat-card green"><div class="label">Buy Signals</div><div class="value">${buyCount}</div><div class="sub">Phase 2 confirmed uptrends</div></div>
      <div class="stat-card red"><div class="label">Sell Signals</div><div class="value">${sellCount}</div><div class="sub">Phase 3/4 breakdowns</div></div>
      <div class="stat-card blue"><div class="label">Top Score</div><div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div><div class="sub">${scan.buy_signals.length ? scan.buy_signals[0].ticker : '-'}</div></div>
      <div class="stat-card"><div class="label">Universe</div><div class="value">${(scan.stats.analyzed || 0).toLocaleString()}</div><div class="sub">of ${(scan.stats.total_universe || 0).toLocaleString()} | ${scan.stats.processing_minutes || '?'} min</div></div>
      <div class="stat-card ${scan.spy.phase === 2 ? 'green' : scan.spy.phase === 4 ? 'red' : 'yellow'}"><div class="label">SPY Phase</div><div class="value">${scan.spy.phase || '?'}</div><div class="sub">${scan.spy.trend || ''} @ $${(scan.spy.price || 0).toFixed(2)}</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Market Breadth</h2><div class="chart-wrap"><canvas id="breadthChart"></canvas></div></div>
      <div class="card">
        <h2>SPY Regime</h2>
        <span class="regime-badge ${regimeClass}">${scan.regime}</span>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px">
          <div><div style="color:var(--muted);font-size:11px">Phase</div><div style="font-size:18px;font-weight:700">${scan.spy.phase} - ${scan.spy.phase_name || ''}</div></div>
          <div><div style="color:var(--muted);font-size:11px">Confidence</div><div style="font-size:18px;font-weight:700">${scan.spy.confidence || '?'}%</div></div>
        </div>
      </div>
    </div>
    ${renderTop20Table(top20.top20 || [])}
    <div class="card">
      <h2 style="color:var(--green)">Buy Signals</h2>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Score</th><th scope="col">Entry</th><th scope="col">Stop Loss</th><th scope="col">R:R</th><th scope="col">RS</th><th scope="col">Reddit</th><th scope="col">Key Reasons</th><th scope="col">Trade</th></tr></thead>
        <tbody>${renderBuyRows(scan.buy_signals)}</tbody>
      </table></div>
    </div>
    <div class="card">
      <h2 style="color:var(--red)">Sell Signals</h2>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Score</th><th scope="col">Severity</th><th scope="col">Breakdown</th><th scope="col">Reddit</th><th scope="col">Reasons</th><th scope="col">Trade</th></tr></thead>
        <tbody>${renderSellRows(scan.sell_signals)}</tbody>
      </table></div>
    </div>`;

  renderBreadthChart('breadthChart', scan.breadth);

  // The live-refresh closure must always read the current scan selection.
  _marketTop20Tickers = (top20.top20 || []).map(s => s.ticker);
  loadMomentumStatus(_marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap));
}

function renderBuyRows(signals) {
  if (!signals.length) return '<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
  return signals.map(s => {
    const pct = (s.score / (s.max_score || 125)) * 100;
    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
    const entryClass = (s.entry_quality || '').toLowerCase();
    const topReasons = (s.reasons || []).slice(0, 3).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    const extra = (s.reasons || []).slice(3);
    const extraHTML = extra.length
      ? `<div class="extra-reasons" style="display:none">${extra.map(r => `<li>${cleanEmoji(r)}</li>`).join('')}</div><button class="expand-btn" onclick="toggleReasons(this)">+${extra.length} more</button>`
      : '';
    return `<tr>
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td><span class="score-num">${s.score}</span><div class="score-bar"><div class="fill" style="width:${pct}%;background:${barColor}"></div></div></td>
      <td><span class="badge ${entryClass}">${s.entry_quality || '-'}</span></td>
      <td>${s.stop_loss ? '$' + s.stop_loss.toFixed(2) : '-'}</td>
      <td style="color:${(s.rr_ratio || 0) >= 3 ? 'var(--green)' : (s.rr_ratio || 0) >= 2 ? 'var(--text)' : 'var(--yellow)'}">${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : '-'}</td>
      <td style="color:${(s.rs || 0) > 0.1 ? 'var(--green)' : (s.rs || 0) > 0 ? 'var(--text)' : 'var(--red)'}">${s.rs != null ? s.rs.toFixed(3) : '-'}</td>
      <td>${redditCell(s.reddit_mentions)}</td>
      <td><ul class="reasons-list">${topReasons}</ul>${extraHTML}</td>
      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
    </tr>`;
  }).join('');
}

function renderSellRows(signals) {
  if (!signals.length) return '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
  return signals.map(s => {
    const sevClass = (s.severity || 'medium').toLowerCase();
    const reasons = (s.reasons || []).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    return `<tr>
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td><span class="score-num">${s.score}</span></td>
      <td><span class="badge ${sevClass}">${(s.severity || '?').toUpperCase()}</span></td>
      <td>${s.breakdown_level ? '$' + s.breakdown_level.toFixed(2) : '-'}</td>
      <td>${redditCell(s.reddit_mentions)}</td>
      <td><ul class="reasons-list">${reasons}</ul></td>
      <td>${fidelityLink(s.ticker, 'Sell', 'sell')}</td>
    </tr>`;
  }).join('');
}
