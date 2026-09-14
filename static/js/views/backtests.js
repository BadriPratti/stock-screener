import { fetchJSON } from '../core/api.js';
import { content, currentView, pageMeta } from '../core/state.js';

export async function renderBacktestsView() {
  const history = await fetchJSON('/api/backtest/history');
  if (currentView !== 'backtests') return; // navigated away before this resolved
  content.innerHTML = `
    <div class="source-note historical">
      <b>This is a report card, not your email.</b> It shows how the screener's scoring would have performed
      on real historical stocks and prices — win rate, returns, drawdown. It doesn't contain today's picks;
      for those, see <a href="#/shortlist" style="color:var(--blue)">Shortlist</a> or
      <a href="#/market" style="color:var(--blue)">Market</a>. Run a fresh one from
      <a href="#/run" style="color:var(--blue)">Run Simulation</a>.
    </div>
    <div style="margin-bottom:16px">
      <select class="scan-select" id="backtestSelect">
        <option value="">Latest</option>
      </select>
    </div>
    <div id="backtestBody"></div>`;
  const sel = document.getElementById('backtestSelect');
  history.forEach(h => {
    const opt = document.createElement('option');
    opt.value = h.path;
    opt.textContent = `${h.name} (${h.generated ? new Date(h.generated).toLocaleDateString() : '?'})`;
    sel.appendChild(opt);
  });
  sel.addEventListener('change', () => loadBacktest(sel.value));
  loadBacktest('');
}

async function loadBacktest(path) {
  const [summaryData, tradesData] = await Promise.all([
    path ? fetchJSON('/api/backtest/run?path=' + encodeURIComponent(path)) : fetchJSON('/api/backtest/latest'),
    fetchJSON('/api/backtest/trades' + (path ? '?path=' + encodeURIComponent(path) : '')),
  ]);
  if (currentView !== 'backtests') return; // navigated away before this resolved
  const summary = summaryData.summary || {};
  const trades = tradesData.trades || [];

  if (!summary.total_trades) {
    document.getElementById('backtestBody').innerHTML = `
      <div class="no-data"><h2>No backtest history yet</h2><p>Run a Walk-Forward simulation from the Run Simulation page.</p></div>`;
    return;
  }
  pageMeta.textContent = summaryData.generated ? `Generated ${new Date(summaryData.generated).toLocaleString()}` : '';

  document.getElementById('backtestBody').innerHTML = `
    <div class="stats-row">
      <div class="stat-card ${summary.win_rate_pct >= 40 ? 'green' : 'yellow'}"><div class="label">Win Rate</div><div class="value">${(summary.win_rate_pct || 0).toFixed(1)}%</div><div class="sub">${summary.total_trades} trades</div></div>
      <div class="stat-card ${summary.avg_return_pct >= 0 ? 'green' : 'red'}"><div class="label">Avg Return</div><div class="value">${(summary.avg_return_pct || 0).toFixed(2)}%</div><div class="sub">median ${(summary.median_return_pct || 0).toFixed(2)}%</div></div>
      <div class="stat-card blue"><div class="label">Sharpe-like</div><div class="value">${(summary.sharpe_like || 0).toFixed(2)}</div><div class="sub">avg win ${(summary.avg_win_pct || 0).toFixed(1)}% / loss ${(summary.avg_loss_pct || 0).toFixed(1)}%</div></div>
      <div class="stat-card red"><div class="label">Max Drawdown</div><div class="value">${(summary.max_drawdown_pct || 0).toFixed(1)}%</div><div class="sub">$${(summary.max_drawdown_dollars || 0).toFixed(0)}</div></div>
      <div class="stat-card purple"><div class="label">Avg Days Held</div><div class="value">${(summary.avg_days_held || 0).toFixed(1)}</div><div class="sub">${summary.total_periods || '?'} periods</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Cumulative P&amp;L (by exit date)</h2><div class="chart-wrap"><canvas id="equityChart"></canvas></div></div>
      <div class="card"><h2>Exit Reasons</h2><div class="chart-wrap"><canvas id="exitChart"></canvas></div></div>
    </div>
    <div class="card">
      <h2>Trades <span style="font-weight:400;color:var(--muted);font-size:12px">(click a column to sort)</span></h2>
      <div style="overflow-x:auto"><table class="signal-table" id="tradesTable">
        <thead><tr>
          <th scope="col" data-key="ticker" role="button" tabindex="0" aria-sort="none">Ticker</th><th scope="col" data-key="period" role="button" tabindex="0" aria-sort="none">Entry Date</th><th scope="col" data-key="score" role="button" tabindex="0" aria-sort="none">Score</th>
          <th scope="col" data-key="exit_reason" role="button" tabindex="0" aria-sort="none">Exit Reason</th><th scope="col" data-key="days_held" role="button" tabindex="0" aria-sort="none">Days Held</th><th scope="col" data-key="return_pct" role="button" tabindex="0" aria-sort="none">Return %</th><th scope="col" data-key="dollar_pnl" role="button" tabindex="0" aria-sort="none">$ P&amp;L</th>
        </tr></thead>
        <tbody>${renderTradeRows(trades)}</tbody>
      </table></div>
    </div>`;

  renderEquityCurveChart('equityChart', tradesData.equity_curve || []);
  renderExitReasonChart('exitChart', summary.exit_reasons || {});

  let sortKey = null, sortDir = 1;
  const headers = document.querySelectorAll('#tradesTable th[data-key]');
  const applySort = (th) => {
    const key = th.dataset.key;
    sortDir = sortKey === key ? -sortDir : 1;
    sortKey = key;
    const sorted = [...trades].sort((a, b) => {
      const av = a[key], bv = b[key];
      if (typeof av === 'string') return sortDir * String(av).localeCompare(String(bv));
      return sortDir * ((av || 0) - (bv || 0));
    });
    document.querySelector('#tradesTable tbody').innerHTML = renderTradeRows(sorted);
    headers.forEach(h => h.setAttribute('aria-sort', h === th ? (sortDir === 1 ? 'ascending' : 'descending') : 'none'));
  };
  headers.forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => applySort(th));
    th.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); applySort(th); }
    });
  });
}

function renderTradeRows(trades) {
  return trades.map(t => `<tr>
    <td><span class="ticker">${t.ticker}</span></td>
    <td>${t.period || '-'}</td>
    <td>${t.score ?? '-'}</td>
    <td><span class="badge ${t.exit_reason === 'stop_loss' ? 'poor' : t.exit_reason === 'sell_signal' ? 'medium' : 'good'}">${(t.exit_reason || '-').replace('_', ' ')}</span></td>
    <td>${t.days_held ?? '-'}</td>
    <td style="color:${(t.return_pct || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">${(t.return_pct || 0).toFixed(2)}%</td>
    <td style="color:${(t.dollar_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">$${(t.dollar_pnl || 0).toFixed(2)}</td>
  </tr>`).join('');
}
