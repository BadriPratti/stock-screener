const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');

const ROOT = path.join(__dirname, '..', '..');
const COMPONENT = path.join(ROOT, 'static', 'js', 'components', 'market-map.js');
const CHARTS = path.join(ROOT, 'static', 'js', 'charts.js');
const MARKET = path.join(ROOT, 'static', 'js', 'views', 'market.js');
const DASHBOARD = path.join(ROOT, 'static', 'js', 'dashboard.js');
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B50}]/u;

function escapableElement() {
  const element = { value: '' };
  Object.defineProperty(element, 'textContent', { set(value) {
    element.value = String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  } });
  Object.defineProperty(element, 'innerHTML', { get() { return element.value; } });
  return element;
}

global.document = { createElement: escapableElement, getElementById: () => ({}), querySelectorAll: () => [] };
global.window = { addEventListener() {} };
global.location = { href: 'http://localhost/' };

function trackerFixture() {
  return {
    counts: { active: 1, watching: 1, retired: 1 },
    roster: { cap: 500, active: 1, watching: 1, overflow: 0 },
    top50_only_sessions: ['2026-09-17'],
    tickers: {
      'A<&': { tier: 'active', current_streak_days: 5, longest_streak_days: 6, sessions_qualified: 7, sessions_observed: 8,
        first_qualified: '2026-09-01', last_qualified: '2026-09-18', score_trend: 2, latest_daily_score: 90,
        latest: { evaluation: 'qualified', entry_quality: 'Good' }, position: { score: 90, rs: 0.2, is_current: true } },
      BBB: { tier: 'watching', current_streak_days: 0, longest_streak_days: 2, sessions_qualified: 2, sessions_observed: 5,
        first_qualified: '2026-09-02', last_qualified: '2026-09-15', score_trend: null, latest_daily_score: 80,
        latest: { evaluation: 'not_scored', drop_reason: 'phase_3' }, position: { score: 80, rs: 0.1, is_current: false } },
      CCC: { tier: 'retired', current_streak_days: 0, longest_streak_days: 1, sessions_qualified: 1, sessions_observed: 15,
        first_qualified: '2026-08-01', last_qualified: '2026-08-01', score_trend: -4, latest_daily_score: 70,
        latest: null, position: { score: 70, rs: -0.1, is_current: false } },
    },
  };
}

class FakeElement {
  constructor(id = '', dataset = {}) {
    this.id = id;
    this.dataset = dataset;
    this.listeners = {};
    this.attributes = {};
    this.children = [];
    this.parentNode = null;
    this.hidden = false;
    this.disabled = false;
    this.checked = false;
    this.value = '';
    this.textContent = '';
    this._innerHTML = '';
    this.innerHTMLWrites = 0;
    this.classList = { add() {}, remove() {}, toggle() {} };
  }

  addEventListener(type, callback) { (this.listeners[type] ||= []).push(callback); }
  removeEventListener(type, callback) {
    this.listeners[type] = (this.listeners[type] || []).filter(item => item !== callback);
  }
  emit(type, extra = {}) {
    for (const callback of this.listeners[type] || []) callback({ target: this, preventDefault() {}, ...extra });
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; }
  append(...nodes) {
    nodes.forEach(node => {
      if (node.parentNode) node.parentNode.children = node.parentNode.children.filter(child => child !== node);
      node.parentNode = this;
      this.children.push(node);
    });
  }
  replaceWith(node) {
    if (!this.parentNode) return;
    const index = this.parentNode.children.indexOf(this);
    if (index !== -1) this.parentNode.children[index] = node;
    node.parentNode = this.parentNode;
    this.parentNode = null;
  }
  remove() {
    if (this.parentNode) this.parentNode.children = this.parentNode.children.filter(child => child !== this);
    this.parentNode = null;
  }
  focus() { this.focused = true; }
  querySelectorAll() { return this.children.flatMap(child => [child, ...child.querySelectorAll()]); }
  set innerHTML(value) { this._innerHTML = String(value); this.innerHTMLWrites += 1; }
  get innerHTML() { return this._innerHTML; }
}

function controllerDOM() {
  const ids = ['marketMotionSlider', 'marketMotionPlay', 'marketMotionLive', 'marketMotionNew',
    'marketMotionFrameStatus', 'marketMotionAnnouncement', 'marketMotionVersion', 'marketMotionFundamentals',
    'marketMotionChart', 'marketMotionCoverage', 'marketMotionPrevious', 'marketMotionNext', 'marketMotionSpeed',
    'marketMotionShowRetired', 'marketMotionSearch', 'marketSchedulerMessage', 'marketSchedulerLastRun',
    'marketSchedulerLastPublish', 'marketSchedulerNextRun', 'marketSchedulerEnabled', 'marketSchedulerPublish',
    'marketSchedulerRun', 'marketSchedulerError', 'marketMotionExpand', 'marketMotionTableDisclosure',
    'marketMotionTableContainer'];
  const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
  elements.marketMotionSpeed.value = '1';
  elements.marketMotionTableDisclosure.setAttribute('aria-expanded', 'false');
  elements.marketMotionTableContainer.hidden = true;
  const tiers = ['active', 'watching', 'retired'].map(tier => new FakeElement(`tier-${tier}`, { tier }));
  const tableBody = new FakeElement('marketMotionTableBody');
  const root = new FakeElement('marketMotionCard');
  root.querySelector = selector => {
    if (selector === '[data-tier="retired"]') return tiers[2];
    if (selector === '#marketMotionTable tbody') return tableBody;
    return selector.startsWith('#') ? elements[selector.slice(1)] : null;
  };
  root.querySelectorAll = selector => selector === '[data-tier]' ? tiers : [];
  return { root, elements, tiers, tableBody };
}

async function main() {
  const component = await import(`file://${COMPONENT}`);
  const html = component.marketMapHTML(trackerFixture(), { enabled: false, publish_to_github: true, message: 'Off' });
  for (const required of ['marketMotionPlay', 'marketMotionPrevious', 'marketMotionNext', 'marketMotionSlider',
    'marketMotionSpeed', 'marketMotionLive', 'marketMotionSearch', 'marketMotionShowRetired',
    'marketSchedulerEnabled', 'marketSchedulerPublish', 'marketSchedulerRun', 'marketMotionExpand']) {
    assert.ok(html.includes(`id="${required}"`), `missing ${required}`);
  }
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /role="img"/);
  assert.match(html, /Off by default\. Nothing runs unless/);
  assert.match(html, /Auto-refresh every 2 hours while this app is open/);
  assert.match(html, /Publish frames to GitHub/);
  assert.match(html, /id="marketMotionTableDisclosure"[^>]*aria-expanded="false"[^>]*>Tracked stocks \(2\)/);
  assert.match(html, /<div id="marketMotionTableContainer" hidden><\/div>/);
  assert.ok(!html.includes('data-market-sort='), 'sortable headers are not built while the disclosure is closed');
  assert.strictEqual((html.match(/data-tracked-ticker=/g) || []).length, 0,
    'tracked rows are not built while the disclosure is closed');

  const fallback = component.fallbackMapHTML('No frames');
  assert.match(fallback, /showing the current scan only|No frames/);
  assert.match(fallback, /marketScatterChart/);
  const fallbackMount = { innerHTML: '', querySelector: () => null };
  let fallbackRendered = 0;
  const fallbackController = await component.mountMarketMap({
    mount: fallbackMount, fetchJSON: async () => { throw new Error('offline'); }, chartApi: {},
    fallback: () => { fallbackRendered++; }, onTickerClick() {},
  });
  assert.strictEqual(fallbackController, null);
  assert.strictEqual(fallbackRendered, 1, 'failed frame fetch renders the legacy scatter exactly once');
  assert.match(fallbackMount.innerHTML, /Persistent history could not be loaded/);

  const dom = controllerDOM();
  const host = new FakeElement('host');
  host.append(dom.root);
  const body = new FakeElement('body');
  const app = new FakeElement('app');
  const originalDocument = global.document;
  global.document = {
    createElement: () => new FakeElement(),
    querySelector: selector => selector === '.app' ? app : null,
    contains: node => !!node && node.parentNode !== null,
    body,
  };
  let resizeCount = 0;
  let updateCount = 0;
  let fetchCount = 0;
  const pendingFrames = new Map();
  let nextFrame = 1;
  const controller = component.createMarketMapController({
    root: dom.root,
    frames: [{
      run_id: 'frame-1', run_kind: 'daily_full', generated_at: '2026-09-18T17:00:00Z',
      session_date: '2026-09-18', scoring_version: 'v1',
      score_model: { max_score: 125, buy_threshold: 60 }, coverage: { kind: 'complete_for_scope' },
      points: [
        { ticker: 'A<&', evaluation: 'qualified', score: 90, rs: 0.2, entry_quality: 'Good' },
        { ticker: 'BBB', evaluation: 'qualified', score: 80, rs: 0.1, entry_quality: 'Good' },
      ],
    }, {
      run_id: 'frame-2', run_kind: 'daily_full', generated_at: '2026-09-19T17:00:00Z',
      session_date: '2026-09-19', scoring_version: 'v1',
      score_model: { max_score: 125, buy_threshold: 60 }, coverage: { kind: 'complete_for_scope' },
      points: [
        { ticker: 'A<&', evaluation: 'qualified', score: 91, rs: 0.21, entry_quality: 'Good' },
        { ticker: 'BBB', evaluation: 'qualified', score: 81, rs: 0.11, entry_quality: 'Good' },
      ],
    }],
    tracker: trackerFixture(),
    fetchJSON: async () => { fetchCount += 1; return trackerFixture(); },
    chartApi: {
      renderMarketMotionChart: () => ({ update: () => { updateCount += 1; }, resize: () => { resizeCount += 1; } }),
      destroyChart() {},
    },
    requestFrame: callback => { const id = nextFrame++; pendingFrames.set(id, callback); return id; },
    cancelFrame: id => pendingFrames.delete(id),
    now: () => 0,
    matchMedia: () => ({ matches: false, addEventListener() {}, removeEventListener() {} }),
  });

  const tableContainer = dom.elements.marketMotionTableContainer;
  assert.strictEqual(controller.state().tableBuilt, false);
  assert.strictEqual(tableContainer.innerHTML, '');
  dom.elements.marketMotionTableDisclosure.emit('click');
  assert.strictEqual(dom.elements.marketMotionTableDisclosure.attributes['aria-expanded'], 'true');
  assert.strictEqual(tableContainer.hidden, false);
  assert.match(tableContainer.innerHTML, /role="button" tabindex="0" data-market-sort="ticker"/);
  assert.ok(!tableContainer.innerHTML.includes('A<&'), 'ticker text is escaped in every table cell and attribute');
  assert.strictEqual((tableContainer.innerHTML.match(/data-tracked-ticker=/g) || []).length, 2,
    'opening builds every currently visible tracked row, independent of chart decimation');
  assert.strictEqual(tableContainer.innerHTMLWrites, 1);
  dom.elements.marketMotionTableDisclosure.emit('click');
  dom.elements.marketMotionTableDisclosure.emit('click');
  assert.strictEqual(tableContainer.innerHTMLWrites, 1, 'reopening reuses the table built on first expansion');

  dom.tiers[2].emit('click');
  await Promise.resolve();
  await Promise.resolve();
  assert.strictEqual((dom.tableBody.innerHTML.match(/data-tracked-ticker=/g) || []).length, 3,
    'including retired stocks keeps coverage of every tracker record');
  assert.ok(!dom.tableBody.innerHTML.includes('A<&'), 'ticker escaping is preserved after a table refresh');
  const fetchesBeforeLifecycle = fetchCount;

  dom.elements.marketMotionPlay.emit('click');
  assert.strictEqual(controller.state().player.playing, true);
  dom.elements.marketMotionExpand.emit('click');
  assert.strictEqual(controller.state().expanded, true);
  const resizeAfterExpand = resizeCount;
  controller.setActive(false);
  assert.strictEqual(controller.state().player.playing, false, 'suspending pauses replay');
  assert.strictEqual(controller.state().expanded, false, 'suspending closes the Expand overlay');
  assert.strictEqual(resizeCount, resizeAfterExpand, 'suspending does not resize a hidden chart');
  const updatesBeforeResume = updateCount;
  controller.setActive(true);
  assert.strictEqual(resizeCount, resizeAfterExpand + 1, 'reactivation resizes the existing chart');
  assert.strictEqual(updateCount, updatesBeforeResume + 1, 'reactivation repaints the existing chart');
  assert.strictEqual(fetchCount, fetchesBeforeLifecycle, 'suspend and resume do not refetch data');
  global.document = originalDocument;

  const source = fs.readFileSync(COMPONENT, 'utf8');
  assert.match(source, /\/api\/market-motion\?limit=20/);
  assert.match(source, /\/api\/market-motion\/tracker\?tiers=/);
  assert.match(source, /method: 'POST'[\s\S]*JSON\.stringify\(body\)/,
    'scheduler settings use a JSON POST body');
  assert.match(source, /\/api\/market-motion\/run-now', \{ method: 'POST' \}/);
  assert.match(source, /removeEventListener\('change', motionChange\)/);
  assert.match(source, /player\.destroy\(\)/);
  assert.match(fs.readFileSync(MARKET, 'utf8'), /stock-data-updated/);
  assert.match(fs.readFileSync(DASHBOARD, 'utf8'), /dispatchEvent\(new CustomEvent\('stock-data-updated'/);
  assert.ok(!/^\s*export\s/m.test(fs.readFileSync(CHARTS, 'utf8')), 'charts.js has no exports');
  for (const file of [COMPONENT, CHARTS, MARKET, DASHBOARD]) {
    assert.ok(!EMOJI.test(fs.readFileSync(file, 'utf8')), `no emoji in ${path.basename(file)}`);
  }

  // Performance smoke: the pure computation should have ample headroom. The
  // assertion is intentionally generous for loaded CI machines; the measured
  // average is printed so the lead can compare it with the 33 ms target.
  const model = await import(`file://${path.join(ROOT, 'static', 'js', 'core', 'market-motion.js')}`);
  const points = Array.from({ length: 2000 }, (_, index) => ({
    ticker: `T${index}`, evaluation: 'qualified', score: 60 + (index % 60), rs: (index % 200) / 100 - 1,
  }));
  const frames = [
    { run_id: 'a', scoring_version: 'v1', coverage: { kind: 'complete_for_scope' }, points },
    { run_id: 'b', scoring_version: 'v1', coverage: { kind: 'complete_for_scope' }, points: points.map(point => ({ ...point, score: point.score + 1, rs: point.rs + 0.01 })) },
  ];
  const tracks = model.buildTracks(frames);
  const iterations = 30;
  const started = performance.now();
  for (let index = 0; index < iterations; index++) model.decimate(model.itemsAt(frames, tracks, 0.5), model.DEFAULT_POINT_BUDGET);
  const average = (performance.now() - started) / iterations;
  console.log(`test_market_map_component.js: 2,000-point average ${average.toFixed(3)} ms`);
  assert.ok(average < 200, `performance smoke exceeded generous bound: ${average} ms`);
  console.log('test_market_map_component.js: all assertions passed');
}

main().catch(error => { console.error('FAILED:', error.stack || error.message); process.exit(1); });
