const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const created = [];
class FakeChart {
  constructor(context, config) {
    this.context = context;
    this.config = config;
    this.data = config.data;
    this.scales = {};
    this.updateModes = [];
    created.push(this);
  }
  update(mode) { this.updateModes.push(mode); }
  resize() { this.resized = true; }
  destroy() { this.destroyed = true; }
}

const canvas = { getContext: () => ({}) };
const context = {
  Chart: FakeChart,
  document: { documentElement: {}, getElementById: () => canvas },
  getComputedStyle: () => ({ getPropertyValue: () => '' }),
  window: {},
  console,
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', '..', 'static', 'js', 'charts.js'), 'utf8'), context);

let cleaned = 0;
const renderer = context.window.StockCharts.renderMarketMotionChart('marketMotionChart', {
  domain: { xMin: -1, xMax: 1, yMin: 40, yMax: 100, thresholdY: 48 },
  thresholdY: 48,
  items: [{ ticker: 'AAA', x: 0.2, y: 80, radius: 5, alpha: 1, color: '#22c55e' }],
}, { cleanup: () => { cleaned++; }, tooltipLines: () => ['line'] });
assert.strictEqual(created.length, 1, 'one Chart instance is created for the canvas');
renderer.update({
  thresholdY: 48, playing: true, labels: ['AAA'], tails: [], vectors: [],
  items: [{ ticker: 'AAA', x: 0.3, y: 82, radius: 6, alpha: 1, color: '#22c55e' }],
});
assert.strictEqual(created.length, 1, 'frame updates mutate the existing Chart');
assert.ok(created[0].updateModes.every(mode => mode === 'none'), 'all frame updates disable Chart.js animation');
assert.strictEqual(created[0].data.datasets[0].data[0].x, 0.3);
// The overlay plugin must accept the vector/tail objects the controller actually produces
// ({ticker, points}), not just bare arrays: a shape mismatch here threw on every animation frame.
const strokes = [];
const fakeCtx = new Proxy({}, { get: (t, k) => (k === 'stroke' ? () => strokes.push('stroke') : () => {}), set: () => true });
const scale = { min: -1, max: 1, getPixelForValue: (v) => v * 100 };
const overlay = created[0].config.plugins[0];
renderer.update({
  thresholdY: 48, playing: true, labels: ['AAA'],
  tails: [{ ticker: 'AAA', points: [{ x: 0.1, y: 70 }, { x: 0.2, y: 80 }, { x: 0.3, y: 82 }] }],
  vectors: [{ ticker: 'AAA', points: [{ x: 0.2, y: 80 }, { x: 0.3, y: 82 }] }, { ticker: 'BBB', points: [] }],
  items: [{ ticker: 'AAA', x: 0.3, y: 82, radius: 6, alpha: 1, color: '#22c55e' }],
});
const strokesBefore = strokes.length;
assert.doesNotThrow(() => overlay.afterDatasetsDraw({
  ctx: fakeCtx, chartArea: { left: 0, right: 100, top: 0, bottom: 100 }, scales: { x: scale, y: scale },
  $marketMotion: created[0].$marketMotion,
}), 'plugin draws {ticker, points} vectors and tails without throwing');
assert.ok(strokes.length - strokesBefore >= 4, 'threshold, zero line, one vector and one tail are stroked');
assert.doesNotThrow(() => overlay.afterDatasetsDraw({
  ctx: fakeCtx, chartArea: { left: 0, right: 100, top: 0, bottom: 100 }, scales: { x: scale, y: scale },
  $marketMotion: { ...created[0].$marketMotion, vectors: [[{ x: 0, y: 1 }, { x: 1, y: 2 }], null, {}] },
}), 'malformed vectors are skipped, never thrown');
context.window.StockCharts.destroyChart('marketMotionChart');
assert.strictEqual(cleaned, 1, 'registered cleanup runs exactly once');
assert.strictEqual(created[0].destroyed, true, 'cleanup runs before the Chart is destroyed');
console.log('test_market_motion_chart_renderer.js: all assertions passed');
