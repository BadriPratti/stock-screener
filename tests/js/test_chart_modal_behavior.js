const assert = require('assert');
const path = require('path');

class FakeElement {
  constructor(id) {
    this.id = id;
    this.hidden = false;
    this.disabled = false;
    this.checked = false;
    this.dataset = {};
    this.listeners = {};
    this.attributes = {};
    this.classList = { add() {}, remove() {}, toggle() {} };
    this.textContent = '';
  }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  emit(type, event = {}) { (this.listeners[type] || []).forEach(fn => fn({ target: this, preventDefault() {}, ...event })); }
  setAttribute(name, value) { this.attributes[name] = value; }
  removeAttribute(name) { delete this.attributes[name]; }
  focus() { global.document.activeElement = this; this.focused = true; }
  querySelectorAll(selector) {
    if (selector === '[data-chart-range]') return ranges;
    if (selector.startsWith('button')) return focusables;
    return [];
  }
}

const ids = ['priceAnalysisModal', 'priceAnalysisClose', 'priceAnalysisTitle', 'priceAnalysisSubtitle',
  'priceAnalysisSMA20', 'priceAnalysisSMA50', 'priceAnalysisLatest', 'priceAnalysisChange',
  'priceAnalysisLow', 'priceAnalysisHigh', 'priceAnalysisPeriod', 'pageTitle'];
const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
const ranges = ['1m', '3m', '6m', 'all'].map(value => {
  const button = new FakeElement(`range-${value}`);
  button.dataset.chartRange = value;
  return button;
});
const focusables = [elements.priceAnalysisClose, ...ranges, elements.priceAnalysisSMA20, elements.priceAnalysisSMA50];
const app = new FakeElement('app');
const fallback = new FakeElement('nav');
const body = new FakeElement('body');
let attachedTrigger = null;
global.document = {
  body,
  activeElement: null,
  getElementById: id => elements[id] || null,
  querySelector: selector => selector === '.app' ? app : selector === '.nav-item.active' ? fallback : null,
  contains: node => node === attachedTrigger,
};
const calls = [];
global.window = { StockCharts: {
  destroyChart: id => calls.push(['destroy', id]),
  renderAnalysisChart: (id, series) => calls.push(['render', id, series]),
} };
global.requestAnimationFrame = callback => { callback(); return 1; };
global.cancelAnimationFrame = () => {};

async function main() {
  const mod = await import(`file://${path.join(__dirname, '..', '..', 'static', 'js', 'core', 'chart-modal.js')}`);
  const trigger = new FakeElement('trigger');
  attachedTrigger = trigger;
  mod.openChartModal({ ticker: 'AAA', history: [{ date: '2026-01-01', close: 10 }], triggerEl: trigger });
  assert.strictEqual(elements.priceAnalysisModal.hidden, false);
  assert.strictEqual(elements.priceAnalysisModal.attributes['aria-hidden'], undefined);
  assert.strictEqual(elements.priceAnalysisClose.focused, true);
  assert.ok('inert' in app.attributes, 'background app becomes inert');
  assert.deepStrictEqual(calls.slice(0, 2).map(call => call[0]), ['destroy', 'render'], 'destroy happens before recreate');

  let prevented = false;
  document.activeElement = ranges[ranges.length - 1];
  elements.priceAnalysisModal.emit('keydown', { key: 'Tab', preventDefault: () => { prevented = true; } });
  assert.strictEqual(prevented, true);
  assert.strictEqual(document.activeElement, elements.priceAnalysisClose, 'Tab wraps to first control');
  document.activeElement = elements.priceAnalysisClose;
  elements.priceAnalysisModal.emit('keydown', { key: 'Tab', shiftKey: true });
  assert.strictEqual(document.activeElement, ranges[ranges.length - 1], 'Shift+Tab wraps to the last enabled control');

  elements.priceAnalysisModal.emit('keydown', { key: 'Escape' });
  assert.strictEqual(elements.priceAnalysisModal.hidden, true);
  assert.strictEqual(trigger.focused, true, 'focus returns to an attached trigger');

  const removedTrigger = new FakeElement('removed');
  attachedTrigger = null;
  mod.openChartModal({ ticker: 'BBB', history: [{ date: '2026-01-01', close: 20 }], triggerEl: removedTrigger });
  elements.priceAnalysisModal.emit('click', { target: elements.priceAnalysisClose });
  assert.strictEqual(elements.priceAnalysisModal.hidden, false, 'descendant click does not close the backdrop');
  elements.priceAnalysisModal.emit('click', { target: elements.priceAnalysisModal });
  assert.strictEqual(elements.priceAnalysisModal.hidden, true, 'backdrop click closes');
  assert.strictEqual(removedTrigger.focused, undefined, 'detached trigger is never focused');
  assert.strictEqual(fallback.focused, true, 'detached trigger uses a safe fallback');
  console.log('test_chart_modal_behavior.js: all assertions passed');
}

main().catch(error => { console.error('FAILED:', error.stack || error.message); process.exit(1); });
