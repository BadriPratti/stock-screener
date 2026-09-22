const assert = require('assert');
const path = require('path');

async function main() {
  const mod = await import(`file://${path.join(__dirname, '..', '..', 'static', 'js', 'core', 'price-analysis.js')}`);

  assert.deepStrictEqual(mod.computeSMA([1, 2, 3, 4], 3), [null, null, 2, 3]);
  assert.deepStrictEqual(mod.computeSMA([1, NaN, 3, 4], 2), [null, null, null, 3.5]);
  assert.deepStrictEqual(mod.computeSMA([], 20), []);

  const history = [
    { date: '2026-01-03', close: 15 },
    { date: '2026-01-01', close: 10 },
    { date: 'bad', close: NaN },
    { date: '2026-01-02', close: 12 },
  ];
  assert.deepStrictEqual(mod.computePriceStats(history), {
    latest: 15, change: 5, changePct: 50, low: 10, high: 15,
    count: 3, startDate: '2026-01-01', endDate: '2026-01-03',
  });
  assert.deepStrictEqual(mod.computePriceStats([]), {
    latest: null, change: null, changePct: null, low: null, high: null,
    count: 0, startDate: null, endDate: null,
  });
  assert.strictEqual(mod.computePriceStats([{ date: 'x', close: 4 }]).change, null);
  assert.strictEqual(mod.computePriceStats([{ date: 'a', close: 0 }, { date: 'b', close: 1 }]).changePct, null);

  assert.deepStrictEqual(mod.sliceRange(history, 2).map(point => point.close), [12, 15]);
  assert.strictEqual(mod.sliceRange(history, 21).length, 3, 'short histories remain intact');
  assert.strictEqual(mod.sliceRange(history, null).length, 3, 'All removes invalid points without truncating');
  console.log('test_price_analysis.js: all assertions passed');
}

main().catch(error => { console.error('FAILED:', error.message); process.exit(1); });
