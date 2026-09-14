import { emptyStateHTML } from '../components/empty-state.js';
import { metricCardHTML } from '../components/metric-card.js';
import { fetchJSON } from '../core/api.js';
import { startJob } from '../core/jobs.js';
import { _liveGuarded, _startLive, liveBadgeHTML } from '../core/refresh.js';
import { content, currentView, pageMeta } from '../core/state.js';
import {
  chartToggleButtonHTML,
  loadMomentumStatus,
  paintMomentumSlots,
  showToast,
  wireChartToggles,
} from '../core/ui-helpers.js';

const POSITION_ACTION_LABELS = {
  hold: { label: 'hold', cls: 'neutral' },
  trail_to_breakeven: { label: 'trail to breakeven', cls: 'good' },
  trail_to_profit: { label: 'trail to profit', cls: 'good' },
  take_partial_and_trail: { label: 'consider trimming', cls: 'medium' },
  take_major_partial_and_trail_tight: { label: 'trim + trail tight', cls: 'poor' },
};

function _positionsUploadCardHTML(data, expanded) {
  const hasResults = data.position_analyses && data.position_analyses.length;
  if (hasResults && !expanded) {
    return `
      <div class="card" id="pos-upload-card" style="display:flex;align-items:center;gap:12px;padding:14px 20px">
        <span style="color:var(--muted);font-size:13px">Showing ${data.position_analyses.length} position${data.position_analyses.length === 1 ? '' : 's'} from your last upload.</span>
        <button class="btn" id="pos-expand" style="margin-left:auto">Update positions</button>
      </div>`;
  }
  return `
    <div class="card sim-card" id="pos-upload-card" style="max-width:600px">
      <h2>Upload Your Positions <span class="status-pill idle" id="pos-pill">idle</span></h2>
      <div class="sim-desc">
        Export a Positions CSV from Fidelity (Accounts &amp; Trade -&gt; Positions -&gt; Download) and upload it here.
        Nothing leaves this machine — no login, no credentials, just the file you already downloaded. Only your
        entry price and quantity are used; current prices come from cached market data, not the CSV.
      </div>
      <input type="file" id="pos-file" accept=".csv" style="margin-bottom:12px;display:block;color:var(--text);font-size:13px">
      <button class="btn primary" id="pos-analyze">${data.has_csv ? 'Re-analyze' : 'Upload &amp; Analyze'}</button>
      <div class="job-output" id="pos-output"></div>
    </div>`;
}

export async function renderPositionsView() {
  const data = await fetchJSON('/api/positions');
  if (currentView !== 'positions') return; // navigated away before this resolved
  const hasResults = data.position_analyses && data.position_analyses.length;
  content.innerHTML = `
    ${_positionsUploadCardHTML(data, false)}
    <div id="pos-results" style="margin-top:20px"></div>`;

  if (hasResults) {
    pageMeta.innerHTML = liveBadgeHTML();
    renderPositionsResults(data);
    _startLive(() => _liveGuarded('positions', refreshPositionsLive));
  }
  wirePositionsUpload(data);
}

async function refreshPositionsLive() {
  await startJob('positions', {}, async (st) => {
    if (st.status === 'success') {
      renderPositionsResults(await fetchJSON('/api/positions'));
    }
  });
}

function wirePositionsUpload(data) {
  const expandBtn = document.getElementById('pos-expand');
  if (expandBtn) {
    expandBtn.addEventListener('click', () => {
      document.getElementById('pos-upload-card').outerHTML = _positionsUploadCardHTML(data, true);
      wirePositionsUpload(data);
    });
    return;
  }

  document.getElementById('pos-analyze').addEventListener('click', async () => {
    const fileInput = document.getElementById('pos-file');
    const btn = document.getElementById('pos-analyze');
    const pill = document.getElementById('pos-pill');
    const out = document.getElementById('pos-output');
    btn.disabled = true;

    if (fileInput.files.length) {
      pill.className = 'status-pill running';
      pill.innerHTML = '<span class="spinner"></span> uploading';
      const form = new FormData();
      form.append('csv', fileInput.files[0]);
      const uploadRes = await fetch('/api/positions/upload', { method: 'POST', body: form }).then(r => r.json());
      if (!uploadRes.success) {
        showToast('Upload failed: ' + (uploadRes.error || 'unknown error'));
        btn.disabled = false;
        pill.className = 'status-pill error';
        pill.textContent = 'error';
        return;
      }
    } else if (!data.has_csv) {
      showToast('Choose a CSV file first');
      btn.disabled = false;
      return;
    }

    out.style.display = 'block';
    out.textContent = '';
    pill.className = 'status-pill running';
    pill.innerHTML = '<span class="spinner"></span> analyzing';

    await startJob('positions', {}, async (st) => {
      out.textContent = st.output.join('\n');
      out.scrollTop = out.scrollHeight;
      if (st.status === 'success' || st.status === 'error' || st.status === 'stopped') {
        btn.disabled = false;
        pill.className = `status-pill ${st.status}`;
        pill.textContent = st.status;
        if (st.status === 'success') {
          renderPositionsResults(await fetchJSON('/api/positions'));
        }
      }
    });
  });
}

function renderPositionsResults(data) {
  const summary = data.summary || {};
  const analyses = data.position_analyses || [];
  const resultsEl = document.getElementById('pos-results');
  if (!resultsEl) return;

  if (!analyses.length) {
    resultsEl.innerHTML = emptyStateHTML({ title: 'No positions found' });
    return;
  }

  const cards = analyses.map(a => {
    const meta = POSITION_ACTION_LABELS[a.action] || { label: a.action || 'hold', cls: 'neutral' };
    const gainColor = a.current_gain_pct >= 0 ? 'var(--green)' : 'var(--red)';
    const gainSign = a.current_gain_pct >= 0 ? '+' : '';

    let extra = '';
    if (a.recommended_stop) {
      extra += `<div class="agent-badge-sub">Recommended stop: $${a.recommended_stop.toFixed(2)}</div>`;
    }
    if (a.add_on_signal) {
      extra += `<div class="agent-badge-sub" style="color:var(--green);margin-top:6px">Add-on candidate — ${a.add_on_rationale}</div>`;
    }
    (a.warnings || []).forEach(w => {
      extra += `<div class="agent-badge-sub" style="color:var(--yellow)">${w}</div>`;
    });

    const chartId = `pos-chart-${a.ticker}`;
    const hasHistory = a.price_history && a.price_history.length;

    return `
      <div class="pick-card">
        <div class="pick-header">
          <span class="ticker">${a.ticker}</span>
          ${hasHistory ? chartToggleButtonHTML(chartId) : ''}
          <span class="badge ${meta.cls}" style="margin-left:${hasHistory ? '8px' : 'auto'}">${meta.label}</span>
        </div>
        <div class="pick-scores">
          <div class="score-block"><div class="label">Entry</div><div class="value">$${a.entry_price.toFixed(2)}</div></div>
          <div class="score-block"><div class="label">Current</div><div class="value">$${a.current_price.toFixed(2)}</div></div>
          <div class="score-block"><div class="label">Gain</div><div class="value" style="color:${gainColor}">${gainSign}${a.current_gain_pct}%</div></div>
        </div>
        <div style="margin-bottom:10px"><span id="momentum-slot-${a.ticker}"></span></div>
        ${extra}
        ${hasHistory ? `<div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>` : ''}
      </div>`;
  }).join('');

  const averageGain = summary.average_gain_pct || 0;
  resultsEl.innerHTML = `
    <div class="stats-row">
      ${metricCardHTML({ label: 'Positions', value: summary.total_positions || 0 })}
      ${metricCardHTML({ label: 'Need Adjustment', value: summary.positions_need_adjustment || 0, variant: 'yellow' })}
      ${metricCardHTML({ label: 'Add-On Candidates', value: summary.add_on_candidates || 0, variant: 'green' })}
      ${metricCardHTML({ label: 'Avg Gain', value: `${averageGain >= 0 ? '+' : ''}${averageGain}%`, variant: averageGain >= 0 ? 'green' : 'red' })}
    </div>
    <div class="shortlist-grid">${cards}</div>`;

  wireChartToggles(resultsEl, (ticker) => {
    const a = analyses.find(x => x.ticker === ticker);
    return a ? { history: a.price_history, entry: a.entry_price, stop: a.recommended_stop } : null;
  }, 'pos-chart-');

  const posTickers = analyses.map(a => a.ticker);
  loadMomentumStatus(posTickers, 'positions', (statusMap) => paintMomentumSlots(posTickers, statusMap));
}
