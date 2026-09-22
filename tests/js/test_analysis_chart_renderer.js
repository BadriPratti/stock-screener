const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const created = [];
class FakeChart {
  constructor(context, config) {
    this.context = context;
    this.config = config;
    this.destroyed = false;
    created.push(this);
  }
  destroy() { this.destroyed = true; }
}

const canvas = { getContext: () => ({ canvas: true }) };
const context = {
  Chart: FakeChart,
  document: { documentElement: {}, getElementById: () => canvas },
  getComputedStyle: () => ({ getPropertyValue: () => '' }),
  window: {},
  console,
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', '..', 'static', 'js', 'charts.js'), 'utf8'), context);

const series = {
  history: [{ date: 'd1', close: 10 }, { date: 'd2', close: 11 }],
  sma20: [null, 10.5],
  sma50: null,
  referenceLines: [
    { label: 'Zero reference', value: 0, kind: 'entry' },
    { label: 'Invalid reference', value: NaN, kind: 'stop' },
  ],
};
context.window.StockCharts.renderAnalysisChart('priceAnalysisChart', series, { ticker: 'AAA' });
assert.strictEqual(created[0].config.data.datasets.map(dataset => dataset.label).join('|'),
  'Daily close|SMA 20|Zero reference');
assert.strictEqual(created[0].config.options.responsive, true);
assert.strictEqual(created[0].config.options.maintainAspectRatio, false);

context.window.StockCharts.renderAnalysisChart('priceAnalysisChart', series, { ticker: 'BBB' });
assert.strictEqual(created[0].destroyed, true, 'existing chart is destroyed before the fixed canvas is reused');
assert.strictEqual(created.length, 2);
context.window.StockCharts.destroyChart('priceAnalysisChart');
assert.strictEqual(created[1].destroyed, true, 'explicit close destroys the active chart');
console.log('test_analysis_chart_renderer.js: all assertions passed');
