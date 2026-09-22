const assert = require('assert');
const path = require('path');

global.document = { getElementById: () => ({}), querySelectorAll: () => [], createElement: () => ({}) };
global.window = { addEventListener() {} };
global.location = { href: 'http://localhost/' };

async function main() {
  const base = path.join(__dirname, '..', '..', 'static', 'js', 'views');
  const [{ positionAnalysisSeries }, { shortlistAnalysisSeries }, { marketSignalAnalysisSeries }] = await Promise.all([
    import(`file://${path.join(base, 'positions.js')}`),
    import(`file://${path.join(base, 'shortlist.js')}`),
    import(`file://${path.join(base, 'market.js')}`),
  ]);
  const history = [{ date: '2026-01-01', close: 10 }];
  const position = positionAnalysisSeries({ price_history: history, entry_price: 9, recommended_stop: 8 });
  assert.strictEqual(position.entry, 9);
  assert.strictEqual(position.stop, 8);
  assert.strictEqual(position.meta.entryLabel, 'Your entry');
  assert.strictEqual(position.meta.stopLabel, 'Recommended stop');

  const buy = marketSignalAnalysisSeries({ ticker: 'BUY', stop_loss: 7 }, 'buy', history, 'buy:BUY');
  assert.strictEqual(buy.stop, 7);
  assert.strictEqual(buy.meta.stopLabel, 'Scanner stop');
  const sell = marketSignalAnalysisSeries({ ticker: 'SELL', breakdown_level: 6 }, 'sell', history, 'sell:SELL');
  assert.strictEqual(sell.stop, 6);
  assert.strictEqual(sell.meta.stopLabel, 'Breakdown level');

  const shortlist = shortlistAnalysisSeries(history);
  assert.strictEqual(shortlist.entry, null);
  assert.strictEqual(shortlist.stop, null);
  assert.deepStrictEqual(shortlist.meta.referenceLines, []);
  console.log('test_chart_reference_wiring.js: all assertions passed');
}

main().catch(error => { console.error('FAILED:', error.message); process.exit(1); });
