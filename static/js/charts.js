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
const _chartCleanups = {};

function _destroyChart(canvasId) {
  if (_chartCleanups[canvasId]) {
    const cleanup = _chartCleanups[canvasId];
    delete _chartCleanups[canvasId];
    cleanup();
  }
  if (_chartInstances[canvasId]) {
    _chartInstances[canvasId].destroy();
    delete _chartInstances[canvasId];
  }
}

function _registerChartCleanup(canvasId, cleanup) {
  if (typeof cleanup === 'function') _chartCleanups[canvasId] = cleanup;
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

const ENTRY_QUALITY_COLORS = {
  good: CHART_COLORS.success,
  extended: CHART_COLORS.warning,
  poor: CHART_COLORS.danger,
};

// Draws a dashed vertical line at x=0 (RS vs. SPY) so "outperforming vs.
// underperforming the market" reads at a glance, without a second dataset.
const _rsZeroLinePlugin = {
  id: 'rsZeroLine',
  afterDraw(chart) {
    const xScale = chart.scales.x;
    if (!xScale || xScale.min > 0 || xScale.max < 0) return;
    const { ctx, chartArea: { top, bottom } } = chart;
    const xPixel = xScale.getPixelForValue(0);
    ctx.save();
    ctx.strokeStyle = CHART_COLORS.borderDefault;
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(xPixel, top);
    ctx.lineTo(xPixel, bottom);
    ctx.stroke();
    ctx.restore();
  },
};

// points: [{ x: rs, y: scorePct, signal: <original buy_signal object> }, ...]
// onPointClick(signal): called when a dot is clicked — this module only
// renders and reports the click; navigation/tab-switching policy belongs to
// the caller (market.js), not here.
function renderMarketScatterChart(canvasId, points, onPointClick) {
  _destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        data: points.map(p => ({ x: p.x, y: p.y })),
        backgroundColor: points.map(p => {
          const color = ENTRY_QUALITY_COLORS[(p.signal.entry_quality || '').toLowerCase()] || CHART_COLORS.textSecondary;
          return color + 'a6'; // ~65% alpha fill, per-point translucency for overlap density
        }),
        borderColor: points.map(p => ENTRY_QUALITY_COLORS[(p.signal.entry_quality || '').toLowerCase()] || CHART_COLORS.textSecondary),
        borderWidth: 1,
        radius: 5.5,
        hoverRadius: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'nearest', intersect: true },
      onClick: (event, elements) => {
        if (!elements.length || !onPointClick) return;
        onPointClick(points[elements[0].index].signal);
      },
      onHover: (event, elements) => {
        event.native.target.style.cursor = elements.length ? 'pointer' : 'default';
      },
      scales: {
        x: {
          title: { display: true, text: 'Relative Strength vs. SPY (momentum)', color: CHART_COLORS.textSecondary, font: { size: CHART_LABEL_SIZE, family: CHART_FONT_FAMILY } },
          ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } },
          grid: { color: CHART_COLORS.borderDefault },
        },
        y: {
          title: { display: true, text: 'Scanner score (% of max)', color: CHART_COLORS.textSecondary, font: { size: CHART_LABEL_SIZE, family: CHART_FONT_FAMILY } },
          ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY }, callback: (v) => v + '%' },
          grid: { color: CHART_COLORS.borderDefault },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => {
              const s = points[items[0].dataIndex].signal;
              return `${s.ticker} · ${s.entry_quality || 'Unknown'} entry`;
            },
            label: (item) => {
              const s = points[item.dataIndex].signal;
              const rr = s.rr_ratio ? `${s.rr_ratio.toFixed(1)}:1` : '-';
              const stop = s.stop_loss ? `$${s.stop_loss.toFixed(2)}` : '-';
              const rsSign = (s.rs || 0) > 0 ? '+' : '';
              const topReason = (s.reasons || [])[0] || '';
              return [
                `Score: ${s.score ?? '-'} / ${s.max_score ?? 125}`,
                `RS vs SPY: ${rsSign}${s.rs != null ? s.rs.toFixed(3) : '-'}`,
                `R:R ${rr} · Stop ${stop}`,
                `Reddit (24h): ${s.reddit_mentions ?? 0}`,
                topReason ? `${topReason}` : '',
              ].filter(Boolean);
            },
          },
        },
      },
    },
    plugins: [_rsZeroLinePlugin],
  });
}

function _rgba(hex, alpha) {
  const value = String(hex || '').replace('#', '');
  if (!/^[0-9a-f]{6}$/i.test(value)) return `rgba(139,143,163,${alpha})`;
  const n = parseInt(value, 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${alpha})`;
}

// Kept as a plain classic-script plugin so charts.js remains usable before the
// ES-module graph loads. Per-frame drawing state lives on chart.$marketMotion.
const _marketMotionOverlayPlugin = {
  id: 'marketMotionOverlay',
  afterDatasetsDraw(chart) {
    const state = chart.$marketMotion;
    if (!state) return;
    const { ctx, chartArea, scales } = chart;
    const xScale = scales.x;
    const yScale = scales.y;
    if (!xScale || !yScale || !chartArea) return;

    ctx.save();
    if (xScale.min <= 0 && xScale.max >= 0) {
      const x = xScale.getPixelForValue(0);
      ctx.strokeStyle = CHART_COLORS.borderDefault;
      ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(x, chartArea.top); ctx.lineTo(x, chartArea.bottom); ctx.stroke();
    }
    const threshold = yScale.getPixelForValue(state.thresholdY);
    ctx.strokeStyle = CHART_COLORS.success;
    ctx.setLineDash([6, 4]);
    ctx.beginPath(); ctx.moveTo(chartArea.left, threshold); ctx.lineTo(chartArea.right, threshold); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = CHART_COLORS.success;
    ctx.font = `${CHART_LABEL_SIZE}px ${CHART_FONT_FAMILY}`;
    ctx.fillText('Buy line', chartArea.left + 6, threshold - 5);

    const byTicker = new Map((state.items || []).map(item => [item.ticker, item]));
    const drawPath = (points, alpha, dashed) => {
      if (!Array.isArray(points) || points.length < 2) return;
      ctx.strokeStyle = _rgba(CHART_COLORS.accent, alpha);
      ctx.setLineDash(dashed ? [3, 3] : []);
      ctx.beginPath();
      points.forEach((point, index) => {
        const x = xScale.getPixelForValue(point.x);
        const y = yScale.getPixelForValue(point.y);
        if (index) ctx.lineTo(x, y); else ctx.moveTo(x, y);
      });
      ctx.stroke();
    };
    if (state.playing) {
      for (const vector of state.vectors || []) drawPath(Array.isArray(vector) ? vector : vector && vector.points, 0.38, true);
    }
    for (const tail of state.tails || []) drawPath(tail.points, tail.alpha || 0.28, false);

    ctx.setLineDash([]);
    ctx.fillStyle = CHART_COLORS.textSecondary;
    ctx.font = `${CHART_LABEL_SIZE}px ${CHART_FONT_FAMILY}`;
    for (const ticker of state.labels || []) {
      const item = byTicker.get(ticker);
      if (!item) continue;
      ctx.fillText(ticker, xScale.getPixelForValue(item.x) + item.radius + 2,
        yScale.getPixelForValue(item.y) - item.radius - 1);
    }
    ctx.restore();
  },
};

function renderMarketMotionChart(canvasId, initial, options = {}) {
  _destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const state = {
    items: [], thresholdY: initial.domain.thresholdY, labels: [], tails: [], vectors: [], playing: false,
  };
  const dataset = {
    data: [],
    backgroundColor: [],
    borderColor: [],
    borderWidth: [],
    pointStyle: [],
    radius: [],
    hoverRadius: [],
  };
  const chart = new Chart(canvas.getContext('2d'), {
    type: 'scatter',
    data: { datasets: [dataset] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      parsing: false,
      interaction: { mode: 'nearest', intersect: true },
      onClick: (event, elements) => {
        if (elements.length && options.onPointClick) options.onPointClick(state.items[elements[0].index]);
      },
      onHover: (event, elements) => {
        state.hovered = elements.length ? state.items[elements[0].index]?.ticker : null;
        if (event.native && event.native.target) event.native.target.style.cursor = elements.length ? 'pointer' : 'default';
        if (options.onHover) options.onHover(state.hovered);
      },
      scales: {
        x: {
          min: initial.domain.xMin, max: initial.domain.xMax,
          title: { display: true, text: 'Relative Strength vs. SPY (momentum)', color: CHART_COLORS.textSecondary, font: { size: CHART_LABEL_SIZE, family: CHART_FONT_FAMILY } },
          ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } },
          grid: { color: CHART_COLORS.borderDefault },
        },
        y: {
          min: initial.domain.yMin, max: initial.domain.yMax,
          title: { display: true, text: 'Scanner score (% of max)', color: CHART_COLORS.textSecondary, font: { size: CHART_LABEL_SIZE, family: CHART_FONT_FAMILY } },
          ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY }, callback: value => value + '%' },
          grid: { color: CHART_COLORS.borderDefault },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: contexts => state.items[contexts[0].dataIndex]?.ticker || '',
            label: context => options.tooltipLines ? options.tooltipLines(state.items[context.dataIndex]) : [],
          },
        },
      },
    },
    plugins: [_marketMotionOverlayPlugin],
  });
  chart.$marketMotion = state;
  _chartInstances[canvasId] = chart;
  _registerChartCleanup(canvasId, options.cleanup);

  const update = (next) => {
    state.items = next.items || [];
    state.thresholdY = next.thresholdY;
    state.labels = next.labels || [];
    state.tails = next.tails || [];
    state.vectors = next.vectors || [];
    state.playing = !!next.playing;
    dataset.data = state.items.map(item => ({ x: item.x, y: item.y }));
    dataset.backgroundColor = state.items.map(item => item.hollow
      ? _rgba(CHART_COLORS.surfaceRaised, item.alpha)
      : _rgba(item.color, item.alpha));
    dataset.borderColor = state.items.map(item => _rgba(item.color, item.stale ? 0.5 : item.alpha));
    dataset.borderWidth = state.items.map(item => item.selected ? 3 : item.hollow ? 2 : 1);
    dataset.pointStyle = state.items.map(item => item.stale ? 'rectRot' : 'circle');
    dataset.radius = state.items.map(item => item.radius);
    dataset.hoverRadius = state.items.map(item => item.radius + 3);
    chart.update('none');
  };
  update(initial);
  return { chart, update, resize: () => chart.resize() };
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

function renderAnalysisChart(canvasId, series, options) {
  _destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  const history = Array.isArray(series.history) ? series.history : [];
  const labels = history.map(point => point.date);
  const datasets = [{
    label: 'Daily close',
    data: history.map(point => point.close),
    borderColor: CHART_COLORS.accent,
    backgroundColor: 'rgba(59,130,246,0.08)',
    fill: true,
    tension: 0.15,
    pointRadius: history.length === 1 ? 3 : 0,
    borderWidth: 2,
  }];
  if (Array.isArray(series.sma20) && series.sma20.some(Number.isFinite)) {
    datasets.push({ label: 'SMA 20', data: series.sma20, borderColor: CHART_COLORS.success, pointRadius: 0, borderWidth: 1.5, fill: false });
  }
  if (Array.isArray(series.sma50) && series.sma50.some(Number.isFinite)) {
    datasets.push({ label: 'SMA 50', data: series.sma50, borderColor: CHART_COLORS.warning, pointRadius: 0, borderWidth: 1.5, fill: false });
  }
  (series.referenceLines || []).filter(line => Number.isFinite(line.value)).forEach(line => {
    datasets.push({
      label: line.label,
      data: labels.map(() => line.value),
      borderColor: line.kind === 'entry' ? CHART_COLORS.textSecondary : CHART_COLORS.danger,
      borderDash: line.kind === 'entry' ? [5, 4] : [3, 3],
      pointRadius: 0,
      borderWidth: 1.5,
      fill: false,
    });
  });
  _chartInstances[canvasId] = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: true, position: 'top', labels: { color: CHART_COLORS.textSecondary, font: { size: CHART_LABEL_SIZE, family: CHART_FONT_FAMILY }, boxWidth: 12 } },
        tooltip: { callbacks: { label: context => `${context.dataset.label}: $${context.parsed.y.toFixed(2)}` } },
        title: { display: false, text: options?.ticker || '' },
      },
      scales: {
        x: { ticks: { color: CHART_COLORS.textSecondary, maxTicksLimit: 12, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY } }, grid: { color: CHART_COLORS.borderDefault } },
        y: { ticks: { color: CHART_COLORS.textSecondary, font: { size: CHART_TICK_SIZE, family: CHART_FONT_FAMILY }, callback: value => '$' + value }, grid: { color: CHART_COLORS.borderDefault } },
      },
    },
  });
  return _chartInstances[canvasId];
}

function destroyChart(canvasId) {
  _destroyChart(canvasId);
}

window.StockCharts = {
  renderAnalysisChart,
  renderMarketMotionChart,
  renderMarketScatterChart,
  destroyChart,
};
