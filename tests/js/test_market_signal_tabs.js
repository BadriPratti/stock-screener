const assert = require('assert');
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(
  path.join(__dirname, '..', '..', 'static', 'js', 'views', 'market.js'), 'utf8'
);

function extract(fnName) {
  const start = src.indexOf(`function ${fnName}(`);
  if (start === -1) throw new Error(`${fnName} not found in market.js`);
  let depth = 0;
  let index = src.indexOf('{', start);
  for (; index < src.length; index++) {
    if (src[index] === '{') depth++;
    if (src[index] === '}') {
      depth--;
      if (depth === 0) break;
    }
  }
  return src.slice(start, index + 1);
}

class FakeElement {
  constructor({ attributes = {}, hidden = false, innerHTML = '', signalTab = null } = {}) {
    this.attributes = { ...attributes };
    this.hidden = hidden;
    this.innerHTML = innerHTML;
    this.dataset = signalTab ? { signalTab } : {};
    this.listeners = {};
    this.tabIndex = Number(attributes.tabindex ?? 0);
    this.focused = false;
    this.classList = {
      active: attributes.class?.split(' ').includes('active') || false,
      toggle: (name, force) => {
        if (name === 'active') this.classList.active = force;
      },
    };
  }

  addEventListener(type, listener) {
    this.listeners[type] = listener;
  }

  setAttribute(name, value) {
    this.attributes[name] = value;
  }

  getAttribute(name) {
    return this.attributes[name];
  }

  focus() {
    this.focused = true;
  }
}

function buildFixture() {
  const elements = {
    buySignalsTab: new FakeElement({
      attributes: { 'aria-selected': 'true', class: 'btn signal-tab active', tabindex: '0' },
      signalTab: 'buy',
    }),
    sellSignalsTab: new FakeElement({
      attributes: { 'aria-selected': 'false', class: 'btn signal-tab', tabindex: '-1' },
      signalTab: 'sell',
    }),
    buySignalsPanel: new FakeElement(),
    sellSignalsPanel: new FakeElement({ hidden: true }),
    sellSignalsBody: new FakeElement(),
  };
  global.document = {
    getElementById: id => elements[id] || null,
    querySelectorAll: selector => selector === '[role="tab"][data-signal-tab]'
      ? [elements.buySignalsTab, elements.sellSignalsTab]
      : [],
  };
  return elements;
}

let highlightedSignal = null;
let activatedSection = null;
const tested = eval(`
  const renderBuyRows = signals => '<tr data-buy-count="' + signals.length + '"></tr>';
  const renderSellRows = signals => '<tr data-sell-count="' + signals.length + '"></tr>';
  const _highlightBuyRow = signal => { highlightedSignal = signal; };
  const _activateMarketSection = section => { activatedSection = section; };
  const escapeHtml = s => s;
  const wireAnalysisButtons = () => {};
  const _marketSignalSeries = () => null;
  ${extract('_signalTabLabel')}
  ${extract('_signalTabsHTML')}
  ${extract('_activateSignalTab')}
  ${extract('_wireSignalTabs')}
  ${extract('_showBuySignal')}
  ({ _signalTabsHTML, _activateSignalTab, _wireSignalTabs, _showBuySignal });
`);

function main() {
  const scan = {
    stats: { buy_count: 479, sell_count: 392 },
    buy_signals: [{ ticker: 'BUY' }],
    sell_signals: [{ ticker: 'SELL' }, { ticker: 'EXIT' }],
  };
  const html = tested._signalTabsHTML(scan);

  assert.match(html, /role="tablist"/);
  assert.match(html, /id="buySignalsTab"[^>]*aria-selected="true"[^>]*aria-controls="buySignalsPanel"/);
  assert.match(html, /id="sellSignalsTab"[^>]*aria-selected="false"[^>]*aria-controls="sellSignalsPanel"/);
  assert.match(html, /id="buySignalsPanel" role="tabpanel" aria-labelledby="buySignalsTab">/,
    'Buy panel should be visible initially');
  assert.match(html, /id="sellSignalsPanel" role="tabpanel" aria-labelledby="sellSignalsTab" hidden>/,
    'Sell panel should have the native hidden attribute initially');
  assert.match(html, /Buy \(1 of 479\)/);
  assert.match(html, /Sell \(2 of 392\)/);
  assert.match(html, /<tbody id="sellSignalsBody"><\/tbody>/,
    'Sell table body should be empty before first activation');

  const elements = buildFixture();
  tested._wireSignalTabs(scan.sell_signals);
  elements.sellSignalsTab.listeners.click();

  assert.strictEqual(elements.buySignalsPanel.hidden, true);
  assert.strictEqual(elements.sellSignalsPanel.hidden, false);
  assert.strictEqual(elements.buySignalsTab.getAttribute('aria-selected'), 'false');
  assert.strictEqual(elements.sellSignalsTab.getAttribute('aria-selected'), 'true');
  assert.match(elements.sellSignalsBody.innerHTML, /data-sell-count="2"/,
    'Sell rows should render on first activation');

  const renderedSellHTML = elements.sellSignalsBody.innerHTML;
  elements.buySignalsTab.listeners.click();
  elements.sellSignalsTab.listeners.click();
  assert.strictEqual(elements.sellSignalsBody.innerHTML, renderedSellHTML,
    'Sell DOM should be retained across tab switches');

  let prevented = false;
  elements.sellSignalsTab.listeners.keydown({ key: 'ArrowLeft', preventDefault: () => { prevented = true; } });
  assert.strictEqual(prevented, true);
  assert.strictEqual(elements.buySignalsTab.focused, true);
  assert.strictEqual(elements.buySignalsPanel.hidden, false,
    'Arrow-key navigation should automatically activate the focused tab');

  elements.sellSignalsTab.listeners.click();
  const chartSignal = { ticker: 'BUY' };
  tested._showBuySignal(chartSignal);
  assert.strictEqual(elements.buySignalsPanel.hidden, false,
    'Chart click callback should activate Buy when Sell was active');
  assert.strictEqual(elements.sellSignalsPanel.hidden, true);
  assert.strictEqual(highlightedSignal, chartSignal,
    'Chart click callback should still pass the signal to the row highlighter');
  assert.strictEqual(activatedSection, 'signals',
    'Chart click callback must activate the outer Signals section tab, or the row it scrolls to may be hidden');
  assert.match(src, /renderMarketScatterChart\('marketScatterChart', points, _showBuySignal\)/,
    'Scatter chart must use the Buy-tab-aware callback');

  console.log('test_market_signal_tabs.js: all assertions passed');
}

try {
  main();
} catch (error) {
  console.error('FAILED:', error.message);
  process.exit(1);
}
