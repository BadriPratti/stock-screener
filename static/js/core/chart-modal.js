import { computePriceStats, computeSMA, sliceRange } from './price-analysis.js';

const CANVAS_ID = 'priceAnalysisChart';
const RANGE_SESSIONS = { '1m': 21, '3m': 63, '6m': 126, all: null };
let _bound = false;
let _renderToken = 0;
let _frame = null;
let _state = null;
let _range = 'all';
let _showSMA20 = true;
let _showSMA50 = false;

function el(id) {
  return document.getElementById(id);
}

function money(value) {
  return Number.isFinite(value) ? `$${value.toFixed(2)}` : '-';
}

function normalizedReferences(entry, stop, meta = {}) {
  const lines = Array.isArray(meta.referenceLines) ? [...meta.referenceLines] : [];
  if (Number.isFinite(entry)) lines.push({ label: meta.entryLabel || 'Your entry', value: entry, kind: 'entry' });
  if (Number.isFinite(stop)) lines.push({ label: meta.stopLabel || 'Recommended stop', value: stop, kind: 'stop' });
  return lines.filter(line => line && Number.isFinite(line.value));
}

function updateStats(history) {
  const stats = computePriceStats(history);
  el('priceAnalysisLatest').textContent = money(stats.latest);
  const sign = stats.change > 0 ? '+' : '';
  el('priceAnalysisChange').textContent = stats.change == null || stats.changePct == null
    ? '-'
    : `${sign}${money(stats.change)} (${sign}${stats.changePct.toFixed(2)}%)`;
  el('priceAnalysisLow').textContent = money(stats.low);
  el('priceAnalysisHigh').textContent = money(stats.high);
  el('priceAnalysisPeriod').textContent = stats.count
    ? `${stats.count} closes · ${stats.startDate} to ${stats.endDate}`
    : 'No valid daily closes';
}

function render() {
  if (!_state) return;
  const token = ++_renderToken;
  if (_frame != null && typeof cancelAnimationFrame === 'function') cancelAnimationFrame(_frame);
  const schedule = typeof requestAnimationFrame === 'function' ? requestAnimationFrame : callback => callback();
  _frame = schedule(() => {
    _frame = null;
    if (!_state || token !== _renderToken) return;
    const fullHistory = sliceRange(_state.history, null);
    const visible = sliceRange(fullHistory, RANGE_SESSIONS[_range]);
    const offset = fullHistory.length - visible.length;
    const closes = fullHistory.map(point => point.close);
    const sma20 = computeSMA(closes, 20).slice(offset);
    const sma50 = computeSMA(closes, 50).slice(offset);
    updateStats(visible);
    window.StockCharts.renderAnalysisChart(CANVAS_ID, {
      history: visible,
      sma20: _showSMA20 && sma20.some(Number.isFinite) ? sma20 : null,
      sma50: _showSMA50 && sma50.some(Number.isFinite) ? sma50 : null,
      referenceLines: _state.referenceLines,
    }, { ticker: _state.ticker });
  });
}

function focusableElements(modal) {
  return [...modal.querySelectorAll('button, input, select, [href], [tabindex]:not([tabindex="-1"])')]
    .filter(node => !node.disabled && !node.hidden);
}

function handleKeydown(event) {
  if (!_state) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    closeChartModal();
    return;
  }
  if (event.key !== 'Tab') return;
  const nodes = focusableElements(el('priceAnalysisModal'));
  if (!nodes.length) return;
  const first = nodes[0];
  const last = nodes[nodes.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function bindModal() {
  if (_bound) return;
  const modal = el('priceAnalysisModal');
  if (!modal) return;
  _bound = true;
  el('priceAnalysisClose').addEventListener('click', closeChartModal);
  modal.addEventListener('keydown', handleKeydown);
  modal.addEventListener('click', event => {
    if (event.target === modal) closeChartModal();
  });
  modal.querySelectorAll('[data-chart-range]').forEach(button => {
    button.addEventListener('click', () => {
      _range = button.dataset.chartRange;
      modal.querySelectorAll('[data-chart-range]').forEach(candidate => {
        const selected = candidate === button;
        candidate.classList.toggle('active', selected);
        candidate.setAttribute('aria-pressed', String(selected));
      });
      render();
    });
  });
  el('priceAnalysisSMA20').addEventListener('change', event => { _showSMA20 = event.target.checked; render(); });
  el('priceAnalysisSMA50').addEventListener('change', event => { _showSMA50 = event.target.checked; render(); });
}

export function openChartModal({ ticker, history, entry, stop, meta = {}, triggerEl = null }) {
  bindModal();
  const modal = el('priceAnalysisModal');
  if (!modal) return;
  window.StockCharts.destroyChart(CANVAS_ID);
  _state = {
    ticker,
    history: Array.isArray(history) ? history : [],
    referenceLines: normalizedReferences(entry, stop, meta),
    contextKey: meta.contextKey || ticker,
    triggerEl,
  };
  el('priceAnalysisTitle').textContent = `${ticker} price analysis`;
  el('priceAnalysisSubtitle').textContent = meta.subtitle || 'Daily close · up to 180 trading sessions';
  el('priceAnalysisSMA20').checked = _showSMA20;
  el('priceAnalysisSMA50').checked = _showSMA50;
  const validHistoryLength = sliceRange(_state.history, null).length;
  el('priceAnalysisSMA20').disabled = validHistoryLength < 20;
  el('priceAnalysisSMA50').disabled = validHistoryLength < 50;
  modal.hidden = false;
  document.body.classList.add('chart-modal-open');
  const app = document.querySelector('.app');
  if (app) app.setAttribute('inert', '');
  render();
  el('priceAnalysisClose').focus();
}

export function closeChartModal() {
  const modal = el('priceAnalysisModal');
  if (!modal || !_state) return;
  const trigger = _state.triggerEl;
  _state = null;
  _renderToken++;
  if (_frame != null && typeof cancelAnimationFrame === 'function') cancelAnimationFrame(_frame);
  _frame = null;
  window.StockCharts?.destroyChart(CANVAS_ID);
  modal.hidden = true;
  document.body.classList.remove('chart-modal-open');
  const app = document.querySelector('.app');
  if (app) app.removeAttribute('inert');
  if (trigger && document.contains(trigger)) {
    trigger.focus();
  } else {
    const fallback = document.querySelector('.nav-item.active') || el('pageTitle');
    if (fallback && typeof fallback.focus === 'function') {
      if (fallback === el('pageTitle')) fallback.setAttribute('tabindex', '-1');
      fallback.focus();
    }
  }
}

export function refreshChartModal(getSeries) {
  if (!_state || typeof getSeries !== 'function') return;
  const series = getSeries(_state.contextKey);
  if (!series || !Array.isArray(series.history)) return;
  _state.history = series.history;
  _state.referenceLines = normalizedReferences(series.entry, series.stop, series.meta || {});
  render();
}
