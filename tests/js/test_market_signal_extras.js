// Characterization test for three Market Signals additions to
// static/js/views/market.js: the "Calculated <timestamp>" line (so a user
// scrolled deep into the signals table can see data freshness without
// scrolling back to the top pageMeta), the per-row current-price cell, and
// the per-row full-screen analysis button.
//
// Needs a real-ish document.createElement stub because core/ui-helpers.js's
// escapeHtml() round-trips through a real <div>.textContent/.innerHTML —
// a plain `{}` stub (as used in test_market_scatter_points.js, which never
// calls escapeHtml) silently produces "undefined" instead of throwing,
// which is exactly the kind of false-pass this test exists to avoid.
//
// Run with: node tests/js/test_market_signal_extras.js

const assert = require('assert');
const path = require('path');

function fakeEscapableElement() {
  const el = { _text: '' };
  Object.defineProperty(el, 'textContent', { set(v) { el._text = v; } });
  Object.defineProperty(el, 'innerHTML', { get() { return el._text; } });
  return el;
}

global.document = {
  getElementById: () => ({}),
  querySelectorAll: () => [],
  createElement: fakeEscapableElement,
};
global.window = { addEventListener: () => {} };
global.location = { href: 'http://localhost/' };

async function main() {
  const marketPath = path.join(__dirname, '..', '..', 'static', 'js', 'views', 'market.js');
  const mod = await import(`file://${marketPath}`);

  const html = mod._signalTabsHTML({
    stats: { buy_count: 1, sell_count: 0 },
    generated: '2026-09-15 17:31:19',
    buy_signals: [{
      ticker: 'CNO', rank: 1, score: 104.1, max_score: 125, current_price: 21.35,
      entry_quality: 'Good', stop_loss: 53.92, rr_ratio: 9.2, rs: 0.254,
      reddit_mentions: 0, reasons: [],
    }],
    sell_signals: [],
  });

  assert.ok(html.includes('Calculated 2026-09-15 17:31:19'),
    'the signals card must show when the scan was last calculated, not just the top-of-page pageMeta');
  assert.ok(!html.includes('<th scope="col">Chart</th>'), 'the obsolete inline-chart column must be removed');
  assert.ok(html.includes('$21.35'), 'current_price must render as a formatted dollar amount');
  assert.ok(html.includes('chart-analysis-btn'), 'each row needs the shared full-screen analysis button');
  assert.ok(html.includes('aria-label="Open CNO price analysis"'), 'the action needs a ticker-specific accessible name');
  assert.ok(!html.includes('class="chart-row"'), 'the removed inline chart must not leave a hidden table row');

  console.log('test_market_signal_extras.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
