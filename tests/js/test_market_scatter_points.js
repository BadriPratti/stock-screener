// Characterization test for buildBuyOpportunityPoints (static/js/views/market.js)
// — the pure data-prep function behind the Market view's "Buy Opportunity Map"
// scatter chart (X = Relative Strength, Y = score as % of max). Locks in the
// filtering rule: a signal with a non-finite score, a non-positive max_score,
// or a non-finite rs must be OMITTED rather than plotted as (0,0)/NaN, which
// would silently misrepresent it instead of just leaving it off the chart.
//
// Mocks the DOM globals static/js/core/state.js touches at module-load time
// (this repo's views are real ES modules with real imports, so this uses the
// mock-and-import style already established in tests/js/test_shortlist_empty_state.js,
// rather than the extract-and-eval style used for single standalone functions).
//
// Run with: node tests/js/test_market_scatter_points.js

const assert = require('assert');
const path = require('path');

global.document = { getElementById: () => ({}), querySelectorAll: () => [] };
global.window = { addEventListener: () => {} };
global.location = { href: 'http://localhost/' };

async function main() {
  const marketPath = path.join(__dirname, '..', '..', 'static', 'js', 'views', 'market.js');
  const mod = await import(`file://${marketPath}`);
  const { buildBuyOpportunityPoints } = mod;

  const points = buildBuyOpportunityPoints([
    { ticker: 'AAA', score: 100, max_score: 125, rs: 0.2 },
    { ticker: 'BBB', score: 90, max_score: 125, rs: -0.1 },
    { ticker: 'CCC', score: 80, max_score: 0, rs: 0.1 },      // zero max_score: division-by-zero guard
    { ticker: 'DDD', score: null, max_score: 125, rs: 0.1 },  // missing score
    { ticker: 'EEE', score: 70, max_score: 125, rs: null },   // missing rs
    { ticker: 'FFF', score: 62.5, max_score: 125, rs: 0 },    // rs === 0 is a valid value, not "missing"
  ]);

  assert.strictEqual(points.length, 3, 'only AAA, BBB, and FFF have all three plottable fields');
  assert.deepStrictEqual(points.map(p => p.signal.ticker), ['AAA', 'BBB', 'FFF']);

  const aaa = points.find(p => p.signal.ticker === 'AAA');
  assert.strictEqual(aaa.x, 0.2, 'x must be the raw rs value');
  assert.strictEqual(aaa.y, 80, 'y must be score-as-percentage-of-max (100/125*100)');

  const fff = points.find(p => p.signal.ticker === 'FFF');
  assert.strictEqual(fff.x, 0, 'rs === 0 must be plotted, not treated as missing');

  assert.strictEqual(buildBuyOpportunityPoints([]).length, 0, 'empty input yields no points');
  assert.strictEqual(buildBuyOpportunityPoints(null).length, 0, 'null/undefined input must not throw');

  console.log('test_market_scatter_points.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
