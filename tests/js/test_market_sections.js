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
  constructor(section, panel = false) {
    this.dataset = panel ? { marketSectionPanel: section } : { marketSection: section };
    this.hidden = panel && section !== 'map';
    this.attributes = {};
    this.listeners = {};
    this.tabIndex = section === 'map' ? 0 : -1;
    this.focused = false;
    this.classList = {
      active: section === 'map',
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

function harness(storedSection) {
  const ids = ['map', 'overview', 'top20', 'signals'];
  const tabs = ids.map(id => new FakeElement(id));
  const panels = ids.map(id => new FakeElement(id, true));
  const storage = new Map();
  if (storedSection !== undefined) storage.set('market:section', storedSection);
  global.sessionStorage = {
    getItem: key => storage.has(key) ? storage.get(key) : null,
    setItem: (key, value) => storage.set(key, value),
  };
  global.document = {
    querySelectorAll: selector => {
      if (selector === '[role="tab"][data-market-section]') return tabs;
      if (selector === '.market-section-panel') return panels;
      return [];
    },
  };

  const tested = eval(`
    const MARKET_SECTION_IDS = ['map', 'overview', 'top20', 'signals'];
    let _marketSection = 'map';
    let _marketMapController = null;
    let _marketMapMountPromise = null;
    let mountCount = 0;
    const activeCalls = [];
    let _marketMapMount = async () => {
      mountCount += 1;
      _marketMapController = { setActive: active => activeCalls.push(active) };
      _marketMapController.setActive(_marketSection === 'map');
      return _marketMapController;
    };
    ${extract('_normaliseMarketSection')}
    ${extract('_readMarketSection')}
    ${extract('_activateMarketSection')}
    ${extract('_wireMarketSectionTabs')}
    ${extract('_restoreMarketSection')}
    _restoreMarketSection();
    ({
      activate: _activateMarketSection,
      tabs,
      panels,
      stored: () => sessionStorage.getItem('market:section'),
      mountCount: () => mountCount,
      activeCalls,
    });
  `);
  return tested;
}

async function settle() {
  await Promise.resolve();
  await Promise.resolve();
}

async function main() {
  assert.match(src, /id="marketSectionPanel-map"[^>]*data-market-section-panel="map"/);
  assert.match(src, /id="marketSectionPanel-overview"[^>]*data-market-section-panel="overview"[^>]*hidden/);
  assert.match(src, /id="marketSectionPanel-top20"[^>]*data-market-section-panel="top20"[^>]*hidden/);
  assert.match(src, /id="marketSectionPanel-signals"[^>]*data-market-section-panel="signals"[^>]*hidden/);

  const defaults = harness(undefined);
  await settle();
  assert.strictEqual(defaults.tabs[0].getAttribute('aria-selected'), 'true');
  assert.strictEqual(defaults.panels[0].hidden, false);
  assert.strictEqual(defaults.panels[1].hidden, true);
  assert.strictEqual(defaults.mountCount(), 1, 'the default Map section mounts immediately');

  defaults.tabs[1].listeners.click();
  defaults.tabs[0].listeners.click();
  defaults.tabs[1].listeners.click();
  defaults.tabs[0].listeners.click();
  await settle();
  assert.strictEqual(defaults.mountCount(), 1, 'returning to Map must reuse its controller');
  assert.strictEqual(defaults.stored(), 'map');
  assert.ok(defaults.activeCalls.includes(false), 'leaving Map suspends its controller');

  const restored = harness('overview');
  await settle();
  assert.strictEqual(restored.tabs[1].getAttribute('aria-selected'), 'true');
  assert.strictEqual(restored.tabs[1].tabIndex, 0);
  assert.strictEqual(restored.panels[1].hidden, false);
  assert.strictEqual(restored.panels[0].hidden, true);
  assert.strictEqual(restored.mountCount(), 0, 'a restored non-Map section must not fetch or build the map');
  restored.tabs[0].listeners.click();
  await settle();
  assert.strictEqual(restored.mountCount(), 1);
  assert.strictEqual(restored.stored(), 'map');

  const invalid = harness('unknown');
  await settle();
  assert.strictEqual(invalid.tabs[0].getAttribute('aria-selected'), 'true');
  assert.strictEqual(invalid.stored(), 'map', 'an invalid stored section is corrected to Map');
  assert.strictEqual(invalid.mountCount(), 1);

  const keyboard = harness('map');
  await settle();
  let prevented = false;
  keyboard.tabs[0].listeners.keydown({ key: 'ArrowRight', preventDefault: () => { prevented = true; } });
  assert.strictEqual(prevented, true);
  assert.strictEqual(keyboard.tabs[1].focused, true);
  assert.strictEqual(keyboard.panels[1].hidden, false);
  keyboard.tabs[1].listeners.keydown({ key: 'ArrowLeft', preventDefault() {} });
  assert.strictEqual(keyboard.tabs[0].focused, true);
  keyboard.tabs[0].listeners.keydown({ key: 'End', preventDefault() {} });
  assert.strictEqual(keyboard.tabs[3].focused, true);
  assert.strictEqual(keyboard.panels[3].hidden, false);
  keyboard.tabs[3].listeners.keydown({ key: 'Home', preventDefault() {} });
  assert.strictEqual(keyboard.tabs[0].focused, true);
  assert.strictEqual(keyboard.panels[0].hidden, false);

  console.log('test_market_sections.js: all assertions passed');
}

main().catch(error => { console.error('FAILED:', error.stack || error.message); process.exit(1); });
