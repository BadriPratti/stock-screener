// The midday workflow scans a random ~100-stock sample and always writes the
// newest report, so before this fix the Market view opened on that sample
// ("Buy (10)") instead of the full-universe scan (a few hundred buys). The
// samples stay selectable and labelled, but must never be the default.
//
// Run with: node tests/js/test_market_default_scan.js

const assert = require('assert');
const path = require('path');

function fakeEscapableElement() {
  const el = { _text: '' };
  Object.defineProperty(el, 'textContent', { set(v) { el._text = v; } });
  Object.defineProperty(el, 'innerHTML', { get() { return el._text; } });
  return el;
}
global.document = { getElementById: () => ({}), querySelectorAll: () => [], createElement: fakeEscapableElement };
global.window = { addEventListener: () => {} };
global.location = { href: 'http://localhost/' };

const scan = (date, universe, isSample) => ({
  name: `optimized_scan_${date}`, path: `/x/optimized_scan_${date}.txt`, date,
  total_universe: universe, run_kind: null, is_sample: isSample,
});

async function main() {
  const marketPath = path.join(__dirname, '..', '..', 'static', 'js', 'views', 'market.js');
  const { pickDefaultScan, scanOptionLabel } = await import(`file://${marketPath}`);

  // Real shape from the repo: newest-first, every day's newest report is the midday sample.
  const scans = [
    scan('20260918_192654', 100, true),
    scan('20260918_170746', 3770, false),
    scan('20260917_200021', 100, true),
    scan('20260917_173505', 3768, false),
  ];

  assert.strictEqual(pickDefaultScan(scans).date, '20260918_170746',
    'default is the newest FULL scan, not the newest scan');
  assert.strictEqual(scans[0].date, '20260918_192654', 'the list order itself is untouched (newest first)');

  assert.strictEqual(pickDefaultScan([scan('a', 100, true), scan('b', 100, true)]).date, 'a',
    'if every scan is a sample, fall back to the newest rather than showing nothing');
  assert.strictEqual(pickDefaultScan([scan('a', 3770, false)]).date, 'a');
  assert.strictEqual(pickDefaultScan([]), undefined, 'empty list is the caller\'s empty-state, not a crash here');

  assert.strictEqual(scanOptionLabel(scans[1]), '20260918 170746', 'full scans keep their existing label');
  assert.strictEqual(scanOptionLabel(scans[0]), '20260918 192654 (100-stock sample)',
    'samples are labelled with their real universe size');

  console.log('test_market_default_scan.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.stack || e.message); process.exit(1); });
