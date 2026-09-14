// Chart.js render helpers. Each function destroys any previous instance on
// the given canvas id before creating a new one, so views can be re-rendered
// freely (e.g. switching backtest runs) without leaking chart instances.

const _chartInstances = {};

function _destroyChart(canvasId) {
  if (_chartInstances[canvasId]) {
    _chartInstances[canvasId].destroy();
    delete _chartInstances[canvasId];
  }
}

function renderBreadthChart(canvasId, breadth) {
  _destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Phase 1 (Base)', 'Phase 2 (Uptrend)', 'Phase 3 (Distribution)', 'Phase 4 (Downtrend)'],
      datasets: [{
        data: [breadth.phase_1_pct || 0, breadth.phase_2_pct || 0, breadth.phase_3_pct || 0, breadth.phase_4_pct || 0],
        backgroundColor: ['#eab308', '#22c55e', '#f97316', '#ef4444'],
        borderColor: '#1a1d27',
        borderWidth: 3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: '#8b8fa3', font: { size: 11 }, padding: 12 } },
        tooltip: { callbacks: { label: (c) => `${c.label}: ${c.parsed}% (${breadth[`phase_${c.dataIndex + 1}_count`] || 0} stocks)` } },
      },
    },
  });
}

function renderEquityCurveChart(canvasId, equityCurve) {
  _destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  const labels = equityCurve.map(p => p.date.slice(0, 10));
  const values = equityCurve.map(p => p.cumulative_pnl);
  const positive = values.length && values[values.length - 1] >= 0;
  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Cumulative P&L ($)',
        data: values,
        borderColor: positive ? '#22c55e' : '#ef4444',
        backgroundColor: positive ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
        fill: true,
        tension: 0.15,
        pointRadius: 0,
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: '#8b8fa3', maxTicksLimit: 8, font: { size: 10 } }, grid: { color: '#2a2d3a' } },
        y: { ticks: { color: '#8b8fa3', font: { size: 10 }, callback: (v) => '$' + v }, grid: { color: '#2a2d3a' } },
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => `Cumulative: $${c.parsed.y.toFixed(2)}` } },
      },
    },
  });
}

function renderExitReasonChart(canvasId, exitReasons) {
  _destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  const labels = Object.keys(exitReasons || {});
  const values = labels.map(l => exitReasons[l]);
  const colors = { stop_loss: '#ef4444', max_hold: '#3b82f6', sell_signal: '#eab308' };
  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.map(l => l.replace('_', ' ')),
      datasets: [{
        data: values,
        backgroundColor: labels.map(l => colors[l] || '#8b8fa3'),
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#8b8fa3', font: { size: 11 } }, grid: { display: false } },
        y: { ticks: { color: '#8b8fa3', font: { size: 10 } }, grid: { color: '#2a2d3a' } },
      },
    },
  });
}

// Real historical price chart for one position — NOT a forecast/projection
// (no future data exists to plot honestly). entryPrice/stopLoss are drawn as
// flat reference lines so you can see where the current price sits relative
// to your cost basis and the recommended stop, over real price history.
function renderPositionChart(canvasId, priceHistory, entryPrice, stopLoss) {
  _destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  const labels = priceHistory.map(p => p.date);
  const closes = priceHistory.map(p => p.close);
  const datasets = [{
    label: 'Price',
    data: closes,
    borderColor: '#3b82f6',
    backgroundColor: 'rgba(59,130,246,0.08)',
    fill: true,
    tension: 0.15,
    pointRadius: 0,
    borderWidth: 2,
  }];
  if (entryPrice) {
    datasets.push({
      label: 'Your entry', data: labels.map(() => entryPrice),
      borderColor: '#8b8fa3', borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5, fill: false,
    });
  }
  if (stopLoss) {
    datasets.push({
      label: 'Recommended stop', data: labels.map(() => stopLoss),
      borderColor: '#ef4444', borderDash: [3, 3], pointRadius: 0, borderWidth: 1.5, fill: false,
    });
  }
  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: true, position: 'top', labels: { color: '#8b8fa3', font: { size: 10 }, boxWidth: 12 } },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: $${c.parsed.y.toFixed(2)}` } },
      },
      scales: {
        x: { ticks: { color: '#8b8fa3', maxTicksLimit: 6, font: { size: 10 } }, grid: { color: '#2a2d3a' } },
        y: { ticks: { color: '#8b8fa3', font: { size: 10 }, callback: (v) => '$' + v }, grid: { color: '#2a2d3a' } },
      },
    },
  });
}
