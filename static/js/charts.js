// Chart.js render helpers. Each function destroys any previous instance on
// the given canvas id before creating a new one, so views can be re-rendered
// freely (e.g. switching backtest runs) without leaking chart instances.

// Colors/fonts are read from the design-token custom properties (TASK-002,
// static/css/dashboard.css :root) rather than hardcoded here a second time,
// so a token change in the CSS automatically propagates to charts. A couple
// of values used in the original chart palette (the Phase 3 orange, the 10px
// tick size) have no equivalent semantic token yet — those stay as literals
// rather than inventing a new token from inside JS.
function _token(name, fallback) {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

const CHART_COLORS = {
  success: _token('--color-success', '#22c55e'),
  danger: _token('--color-danger', '#ef4444'),
  warning: _token('--color-warning', '#eab308'),
  accent: _token('--color-accent', '#3b82f6'),
  textSecondary: _token('--color-text-secondary', '#8b8fa3'),
  borderDefault: _token('--color-border-default', '#2a2d3a'),
  surfaceRaised: _token('--color-surface-raised', '#1a1d27'),
  phase3: '#f97316', // no semantic token for this exact orange yet
};

const CHART_FONT_FAMILY = _token('--font-family-sans', "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif");
const CHART_LABEL_SIZE = parseInt(_token('--font-size-caption', '11px'), 10) || 11;
const CHART_TICK_SIZE = 10; // no matching token below --font-size-caption (11px); kept as-is

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
        backgroundColor: [CHART_COLORS.warning, CHART_COLORS.success, CHART_COLORS.phase3, CHART_COLORS.danger],
        borderColor: CHART_COLORS.surfaceRaised,
        borderWidth: 3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: CHART_COLORS.textSecondary, font: { size: CHART_LABEL_SIZE, family: CHART_FONT_FAMILY }, padding: 12 } },
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
        borderColor: positive ? CHART_COLORS.success : CHART_COLORS.danger,
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
        x: { ticks: { color: CHART_COLORS.textSecondary, maxTicksLimit: 8, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } }, grid: { color: CHART_COLORS.borderDefault } },
        y: { ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY }, callback: (v) => '$' + v }, grid: { color: CHART_COLORS.borderDefault } },
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
  const colors = { stop_loss: CHART_COLORS.danger, max_hold: CHART_COLORS.accent, sell_signal: CHART_COLORS.warning };
  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.map(l => l.replace('_', ' ')),
      datasets: [{
        data: values,
        backgroundColor: labels.map(l => colors[l] || CHART_COLORS.textSecondary),
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_LABEL_SIZE, family: CHART_FONT_FAMILY } }, grid: { display: false } },
        y: { ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } }, grid: { color: CHART_COLORS.borderDefault } },
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
    borderColor: CHART_COLORS.accent,
    backgroundColor: 'rgba(59,130,246,0.08)',
    fill: true,
    tension: 0.15,
    pointRadius: 0,
    borderWidth: 2,
  }];
  if (entryPrice) {
    datasets.push({
      label: 'Your entry', data: labels.map(() => entryPrice),
      borderColor: CHART_COLORS.textSecondary, borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5, fill: false,
    });
  }
  if (stopLoss) {
    datasets.push({
      label: 'Recommended stop', data: labels.map(() => stopLoss),
      borderColor: CHART_COLORS.danger, borderDash: [3, 3], pointRadius: 0, borderWidth: 1.5, fill: false,
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
        legend: { display: true, position: 'top', labels: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY }, boxWidth: 12 } },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: $${c.parsed.y.toFixed(2)}` } },
      },
      scales: {
        x: { ticks: { color: CHART_COLORS.textSecondary, maxTicksLimit: 6, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } }, grid: { color: CHART_COLORS.borderDefault } },
        y: { ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY }, callback: (v) => '$' + v }, grid: { color: CHART_COLORS.borderDefault } },
      },
    },
  });
}
