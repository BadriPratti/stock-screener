const assert = require('assert');
const path = require('path');

function escapableElement() {
  const element = { value: '' };
  Object.defineProperty(element, 'textContent', { set(value) {
    element.value = String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  } });
  Object.defineProperty(element, 'innerHTML', { get() { return element.value; } });
  return element;
}

class FakeElement {
  constructor(id, dataset = {}) {
    this.id = id;
    this.dataset = dataset;
    this.listeners = {};
    this.attributes = {};
    this.classList = { toggle: () => {}, add: () => {}, remove: () => {} };
    this.hidden = false;
    this.disabled = false;
    this.checked = false;
    this.value = '';
    this.textContent = '';
  }
  addEventListener(type, callback) { (this.listeners[type] ||= []).push(callback); }
  emit(type, extra = {}) {
    for (const callback of this.listeners[type] || []) callback({ target: this, preventDefault() {}, ...extra });
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  focus() { this.focused = true; }
}

function makeFrame(id, score, rs) {
  return {
    run_id: id, run_kind: 'daily_full', generated_at: `2026-09-${id === 'f1' ? '17' : id === 'f2' ? '18' : id === 'f3' ? '19' : '20'}T17:00:00Z`,
    session_date: `2026-09-${id === 'f1' ? '17' : id === 'f2' ? '18' : id === 'f3' ? '19' : '20'}`,
    scoring_version: 'v1', score_model: { max_score: 125, buy_threshold: 60 },
    coverage: { kind: 'complete_for_scope' }, fundamentals_as_of: null,
    points: [
      { ticker: 'AAA', evaluation: 'qualified', score, rs, entry_quality: 'Good' },
      { ticker: 'BBB', evaluation: 'not_qualified', score: 55, rs: -0.1, entry_quality: 'Extended' },
    ],
  };
}

function trackerFixture() {
  return {
    counts: { active: 1, watching: 1, retired: 0 }, roster: { cap: 500, active: 1, watching: 1, overflow: 0 },
    top50_only_sessions: [], tickers: {
      AAA: { tier: 'active', current_streak_days: 2, longest_streak_days: 3, sessions_qualified: 2, sessions_observed: 2,
        first_qualified: '2026-09-17', last_qualified: '2026-09-18', score_trend: 2,
        latest: { evaluation: 'qualified', entry_quality: 'Good' },
        position: { score: 92, rs: 0.3, generated_at: '2026-09-18T17:00:00Z', is_current: true } },
      BBB: { tier: 'watching', current_streak_days: 0, longest_streak_days: 1, sessions_qualified: 1, sessions_observed: 2,
        first_qualified: '2026-09-17', last_qualified: '2026-09-17', score_trend: -3,
        latest: { evaluation: 'not_qualified', entry_quality: 'Extended', drop_reason: 'below_buy_threshold' },
        position: { score: 55, rs: -0.1, generated_at: '2026-09-18T17:00:00Z', is_current: true } },
    },
  };
}

function fakeRoot() {
  const ids = ['marketMotionSlider', 'marketMotionPlay', 'marketMotionLive', 'marketMotionNew',
    'marketMotionFrameStatus', 'marketMotionAnnouncement', 'marketMotionVersion', 'marketMotionFundamentals',
    'marketMotionChart', 'marketMotionCoverage', 'marketMotionPrevious', 'marketMotionNext', 'marketMotionSpeed',
    'marketMotionShowRetired', 'marketMotionSearch', 'marketSchedulerMessage', 'marketSchedulerLastRun',
    'marketSchedulerLastPublish', 'marketSchedulerNextRun', 'marketSchedulerEnabled', 'marketSchedulerPublish',
    'marketSchedulerRun', 'marketSchedulerError', 'marketMotionExpand'];
  const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
  elements.marketMotionSpeed.value = '1';
  const tiers = ['active', 'watching', 'retired'].map(value => new FakeElement(`tier-${value}`, { tier: value }));
  const qualities = ['good', 'extended', 'poor'].map(value => new FakeElement(`quality-${value}`, { quality: value }));
  const streaks = [0, 2, 3, 5].map(value => new FakeElement(`streak-${value}`, { streak: String(value) }));
  const sorts = ['ticker', 'streak', 'score'].map(value => new FakeElement(`sort-${value}`, { marketSort: value }));
  const body = new FakeElement('tbody');
  const root = new FakeElement('root');
  root.querySelector = selector => {
    if (selector === '#marketMotionTable tbody') return body;
    return selector.startsWith('#') ? elements[selector.slice(1)] : selector === '[data-tier="retired"]' ? tiers[2] : null;
  };
  root.querySelectorAll = selector => ({
    '[data-tier]': tiers, '[data-quality]': qualities, '[data-streak]': streaks, '[data-market-sort]': sorts,
  }[selector] || []);
  return { root, elements, tiers, qualities, streaks, sorts, body };
}

global.document = {
  createElement: escapableElement, getElementById: () => ({}), querySelectorAll: () => [],
  querySelector: () => null, contains: () => false, body: { classList: { add() {}, remove() {} } },
};
global.window = { addEventListener() {}, matchMedia: () => ({ matches: false, addEventListener() {}, removeEventListener() {} }) };
global.location = { href: 'http://localhost/' };

async function settle() { await Promise.resolve(); await Promise.resolve(); await Promise.resolve(); }

async function main() {
  const componentPath = path.join(__dirname, '..', '..', 'static', 'js', 'components', 'market-map.js');
  const component = await import(`file://${componentPath}`);
  const dom = fakeRoot();
  let clock = 0;
  let nextHandle = 1;
  const pending = new Map();
  const updates = [];
  const mediaListeners = new Set();
  const media = {
    matches: false,
    addEventListener: (type, callback) => mediaListeners.add(callback),
    removeEventListener: (type, callback) => mediaListeners.delete(callback),
  };
  let cleanup;
  const chartApi = {
    renderMarketMotionChart: (id, initial, options) => {
      cleanup = options.cleanup;
      return { update: state => updates.push(state), resize() {} };
    },
    destroyChart: () => cleanup(),
  };
  let frames = [makeFrame('f1', 90, 0.2), makeFrame('f2', 92, 0.3)];
  const tracker = trackerFixture();
  const calls = [];
  const fetchJSON = async (url, options) => {
    calls.push({ url, options });
    if (url === '/api/market-motion?limit=20') return { frames };
    if (url.startsWith('/api/market-motion/tracker')) return tracker;
    if (url === '/api/market-motion/scheduler') return { enabled: options && JSON.parse(options.body).enabled, publish_to_github: true, message: 'Updated' };
    if (url === '/api/market-motion/run-now') return { started: true, reason: null };
    throw new Error(`unexpected ${url}`);
  };
  const controller = component.createMarketMapController({
    root: dom.root, frames, tracker, scheduler: { message: 'Off' }, fetchJSON, chartApi,
    requestFrame: callback => { const id = nextHandle++; pending.set(id, callback); return id; },
    cancelFrame: id => pending.delete(id), now: () => clock, matchMedia: () => media,
  });
  assert.ok(updates.at(-1).items.some(item => item.ticker === 'AAA'));

  // Filters and search repaint without reconstructing or restarting the player.
  controller.state().player.atLive && dom.elements.marketMotionPlay.emit('click');
  assert.strictEqual(controller.state().player.playing, true);
  dom.qualities[0].emit('click');
  assert.strictEqual(controller.state().player.playing, true, 'filtering does not restart or pause replay');
  dom.qualities[0].emit('click');
  dom.elements.marketMotionSearch.value = 'AAA';
  dom.elements.marketMotionSearch.emit('input');
  assert.strictEqual(controller.state().selected, 'AAA');
  assert.deepStrictEqual(updates.at(-1).items.map(item => item.ticker), ['AAA']);
  dom.sorts[0].emit('click');
  assert.strictEqual(dom.sorts[0].attributes['aria-sort'], 'ascending');
  assert.ok(dom.body.innerHTML.indexOf('AAA') < dom.body.innerHTML.indexOf('BBB'), 'ticker sort updates every table row');

  // Reduced motion disables autoplay and cancels its scheduled animation.
  media.matches = true;
  [...mediaListeners].forEach(listener => listener({ matches: true }));
  assert.strictEqual(controller.state().reducedMotion, true);
  assert.strictEqual(controller.state().player.playing, false);
  assert.strictEqual(pending.size, 0);

  // New data follows at live, but leaves a scrubbed-back player in place.
  media.matches = false;
  [...mediaListeners].forEach(listener => listener({ matches: false }));
  dom.elements.marketMotionLive.emit('click');
  clock += 800; [...pending.values()].forEach(callback => callback()); pending.clear();
  frames = [...frames, makeFrame('f3', 94, 0.4)];
  await controller.refresh();
  clock += 800; [...pending.values()].forEach(callback => callback()); pending.clear();
  assert.strictEqual(controller.state().player.atLive, true, 'live edge follows the appended frame');
  dom.elements.marketMotionSlider.value = '0'; dom.elements.marketMotionSlider.emit('input');
  frames = [...frames, makeFrame('f4', 96, 0.5)];
  await controller.refresh();
  assert.strictEqual(controller.state().player.t, 0, 'scrubbed position is not yanked to live');
  assert.strictEqual(controller.state().player.newAvailable, true);

  // Scheduler controls use the exact endpoints and JSON bodies.
  dom.elements.marketSchedulerEnabled.checked = true;
  dom.elements.marketSchedulerEnabled.emit('change');
  await settle();
  dom.elements.marketSchedulerRun.emit('click');
  await settle();
  const schedulerCall = calls.find(call => call.url === '/api/market-motion/scheduler');
  assert.strictEqual(schedulerCall.options.method, 'POST');
  assert.deepStrictEqual(JSON.parse(schedulerCall.options.body), { enabled: true });
  assert.ok(calls.some(call => call.url === '/api/market-motion/run-now' && call.options.method === 'POST'));

  controller.destroy();
  assert.strictEqual(pending.size, 0, 'destroy cancels player animation callbacks');
  assert.strictEqual(mediaListeners.size, 0, 'destroy removes the reduced-motion listener');

  // A superseded mount request must not paint after it resolves.
  const mount = { innerHTML: 'unchanged', querySelector: () => null };
  let resolveFrames;
  let current = true;
  const deferred = new Promise(resolve => { resolveFrames = resolve; });
  const mounting = component.mountMarketMap({
    mount, chartApi, fallback: () => { throw new Error('stale fallback painted'); }, onTickerClick() {},
    isCurrent: () => current,
    fetchJSON: url => url.includes('?limit=20') ? deferred : Promise.resolve(url.endsWith('scheduler') ? {} : tracker),
  });
  current = false;
  resolveFrames({ frames: [] });
  await mounting;
  assert.strictEqual(mount.innerHTML, 'unchanged', 'stale async response cannot paint');
  console.log('test_market_map_controller.js: all assertions passed');
}

main().catch(error => { console.error('FAILED:', error.stack || error.message); process.exit(1); });
