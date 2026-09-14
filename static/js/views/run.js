import { jobPanelHTML } from '../components/job-panel.js';
import { fetchJSON } from '../core/api.js';
import { wireJobCard } from '../core/jobs.js';
import { content, currentView } from '../core/state.js';

export function renderRunView() {
  if (currentView !== 'run') return;
  content.innerHTML = `
    <div class="grid-3">
      ${jobPanelHTML({
        id: 'top3',
        title: 'Quick Backtest (Top 3)',
        description: 'What would the top-3 buy signals have been N days ago, held to today?',
        paramsHTML: `
          <label>Days back<input type="number" id="top3-days" value="7"></label>
          <label>Sample size<input type="number" id="top3-sample" value="150"></label>
          <label>Investment $<input type="number" id="top3-investment" value="1000"></label>
        `,
      })}
      ${jobPanelHTML({
        id: 'mc',
        title: 'Monte Carlo',
        description: 'Re-samples many top-3 portfolios from one fetched pool — win rate distribution, not one basket.',
        paramsHTML: `
          <label>Days back<input type="number" id="mc-days" value="7"></label>
          <label>Pool size<input type="number" id="mc-pool" value="300"></label>
          <label>Sample size<input type="number" id="mc-sample" value="150"></label>
          <label>Iterations<input type="number" id="mc-iterations" value="100"></label>
        `,
      })}
      ${jobPanelHTML({
        id: 'wf',
        title: 'Full Walk-Forward',
        description: 'Rigorous multi-period backtest — walks a fixed universe through many historical dates. Slow (minutes+).',
        paramsHTML: `
          <label>Universe size<input type="number" id="wf-universe_size" value="250"></label>
          <label>Lookback (mo)<input type="number" id="wf-lookback_months" value="9"></label>
          <label>Top N/period<input type="number" id="wf-top_n" value="10"></label>
          <label>Max hold (days)<input type="number" id="wf-max_hold_days" value="60"></label>
        `,
      })}
    </div>`;

  wireJobCard('top3', 'backtest-top3', () => ({
    days: +document.getElementById('top3-days').value,
    sample: +document.getElementById('top3-sample').value,
    investment: +document.getElementById('top3-investment').value,
  }), async (st, resultEl) => {
    if (!st.result_path) return;
    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
    if (res.error) return;
    resultEl.innerHTML = `<div style="font-size:13px">
      <strong style="color:${res.total_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.total_profit.toFixed(2)} (${res.total_return_pct.toFixed(2)}%)</strong>
      — ${res.picks.map(p => p.ticker).join(', ')}</div>`;
  });

  wireJobCard('mc', 'backtest-monte-carlo', () => ({
    days: +document.getElementById('mc-days').value,
    pool: +document.getElementById('mc-pool').value,
    sample: +document.getElementById('mc-sample').value,
    iterations: +document.getElementById('mc-iterations').value,
  }), async (st, resultEl) => {
    if (!st.result_path) return;
    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
    if (res.error || !res.iterations_run) { resultEl.innerHTML = '<div style="color:var(--muted);font-size:13px">Not enough qualifiers found.</div>'; return; }
    resultEl.innerHTML = `<div style="font-size:13px">
      Win rate <strong>${res.win_rate.toFixed(1)}%</strong> · avg <strong style="color:${res.avg_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.avg_profit.toFixed(2)} (${res.avg_pct.toFixed(2)}%)</strong>
      over ${res.iterations_run} iterations${res.score_return_correlation != null ? ` · score/return correlation r=${res.score_return_correlation.toFixed(3)}` : ''}</div>`;
  });

  wireJobCard('wf', 'walk-forward', () => ({
    universe_size: +document.getElementById('wf-universe_size').value,
    lookback_months: +document.getElementById('wf-lookback_months').value,
    top_n: +document.getElementById('wf-top_n').value,
    max_hold_days: +document.getElementById('wf-max_hold_days').value,
  }), async (st, resultEl) => {
    resultEl.innerHTML = '<a href="#/backtests" class="btn primary">View results →</a>';
  });
}
