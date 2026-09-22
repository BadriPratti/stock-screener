const assert = require('assert');
const fs = require('fs');
const path = require('path');

class FakeElement {
  constructor(id = '') {
    this.id = id;
    this.value = '';
    this.textContent = '';
    this.listeners = {};
    this.attributes = {};
    this._innerHTML = '';
  }

  set innerHTML(value) {
    this._innerHTML = String(value);
    if (this.id === 'content') {
      if (value.includes('id="consistencyList"')) {
        elements.consistencyList = new FakeElement('consistencyList');
        elements.consistencyList.value = 'shortlist';
      }
      if (value.includes('id="consistencyWindow"')) {
        elements.consistencyWindow = new FakeElement('consistencyWindow');
        elements.consistencyWindow.value = '5';
      }
      if (value.includes('id="consistencyResults"')) {
        elements.consistencyResults = new FakeElement('consistencyResults');
      }
    }
  }

  get innerHTML() { return this._innerHTML; }
  addEventListener(type, handler) { this.listeners[type] = handler; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; }
  querySelectorAll() { return []; }
  querySelector() { return null; }
  dispatch(type, event = {}) { return this.listeners[type]?.(event); }
}

const elements = {
  content: new FakeElement('content'),
  pageTitle: new FakeElement('pageTitle'),
  pageMeta: new FakeElement('pageMeta'),
};

function escapableElement() {
  const element = new FakeElement();
  Object.defineProperty(element, 'textContent', {
    get() { return this._escaped || ''; },
    set(value) {
      this._escaped = String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
      this._innerHTML = this._escaped;
    },
  });
  return element;
}

global.document = {
  getElementById: id => elements[id] || null,
  querySelectorAll: () => [],
  addEventListener: () => {},
  createElement: escapableElement,
};
global.window = { addEventListener: () => {} };
global.location = { href: 'http://localhost/', hash: '#/consistency' };

const ROOT = path.join(__dirname, '..', '..');

function stat(overrides = {}) {
  return {
    appearances: 4,
    denominator: 5,
    appearance_rate: 0.8,
    current_streak: 2,
    longest_streak: 3,
    first_seen: '2026-09-14',
    last_seen: '2026-09-18',
    best_rank: 1,
    average_rank: 2.25,
    average_score: 126.075,
    score_delta: 3.5,
    is_active_today: true,
    ...overrides,
  };
}

function history(tickers, overrides = {}) {
  return {
    list: 'shortlist',
    window_requested: 5,
    sessions_available: 5,
    sessions: ['2026-09-14', '2026-09-15', '2026-09-16', '2026-09-17', '2026-09-18'],
    denominator: 5,
    latest_session_date: '2026-09-18',
    coverage_gaps: [],
    warnings: [],
    tickers,
    ...overrides,
  };
}

function response(payload) {
  return { json: async () => payload };
}

function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}

async function settle() {
  await Promise.resolve();
  await new Promise(resolve => setImmediate(resolve));
}

async function main() {
  global.fetch = async () => response(history({}));
  const state = await import(`file://${path.join(ROOT, 'static', 'js', 'core', 'state.js')}`);
  const view = await import(`file://${path.join(ROOT, 'static', 'js', 'views', 'consistency.js')}`);

  const ordered = view.buildLeaderboardRows(history({
    ZED: stat({ appearances: 4, current_streak: 1, average_rank: 1 }),
    BETA: stat({ appearances: 4, current_streak: 3, average_rank: 2 }),
    ALPHA: stat({ appearances: 4, current_streak: 3, average_rank: 2 }),
    FIVE: stat({ appearances: 5, current_streak: 1, average_rank: 5 }),
  }));
  assert.deepStrictEqual(ordered.map(row => row.ticker), ['FIVE', 'ALPHA', 'BETA', 'ZED'],
    'default order applies every documented tie-break');

  const sortRows = [
    { id: 'a', ticker: 'B', appearances: 2, currentStreak: 1, longestStreak: 2, firstSeen: '2026-09-15', lastSeen: '2026-09-18', bestRank: 2, averageRank: 3, averageScore: 20, scoreChange: -1, statusText: 'Dropped out' },
    { id: 'b', ticker: 'A', appearances: 1, currentStreak: 2, longestStreak: 3, firstSeen: '2026-09-14', lastSeen: '2026-09-17', bestRank: 1, averageRank: 2, averageScore: 10, scoreChange: 1, statusText: 'On latest scan' },
  ];
  const keys = ['ticker', 'appearances', 'currentStreak', 'longestStreak', 'firstSeen', 'lastSeen', 'bestRank', 'averageRank', 'averageScore', 'scoreChange', 'statusText'];
  for (const key of keys) {
    const ascending = view.sortLeaderboardRows(sortRows, key, 'ascending');
    const descending = view.sortLeaderboardRows(sortRows, key, 'descending');
    assert.notStrictEqual(ascending[0].id, descending[0].id, `${key} sorts in both directions`);
  }

  const withNull = [{ id: 'null', value: null }, { id: 'two', value: 2 }, { id: 'one', value: 1 }];
  assert.strictEqual(view.sortLeaderboardRows(withNull, 'value', 'ascending').at(-1).id, 'null');
  assert.strictEqual(view.sortLeaderboardRows(withNull, 'value', 'descending').at(-1).id, 'null');
  const stable = [{ id: 1, value: 3 }, { id: 2, value: 3 }, { id: 3, value: 3 }];
  assert.deepStrictEqual(view.sortLeaderboardRows(stable, 'value', 'descending').map(row => row.id), [1, 2, 3]);

  const formatted = view.buildLeaderboardRows(history({
    '<img src=x onerror=alert(1)>': stat(),
    OLD: stat({ appearances: 2, denominator: 5, appearance_rate: 0.4, is_active_today: false, score_delta: null }),
  }));
  const old = formatted.find(row => row.ticker === 'OLD');
  assert.strictEqual(old.appearancesText, '2/5 (40%)');
  assert.strictEqual(old.statusText, 'Dropped out');
  assert.strictEqual(old.scoreChangeText, '-');
  assert.strictEqual(formatted.find(row => row.ticker.startsWith('<')).scoreChangeText, '+3.5');

  state.setCurrentView('consistency');
  global.fetch = async () => response(history({
    '<img src=x onerror=alert(1)>': stat(),
    OLD: stat({ is_active_today: false }),
  }, {
    coverage_gaps: [{ after: '2026-09-14', before: '2026-09-17', missing_weekdays: 2 }],
    warnings: ['Skipped <bad>.json'],
  }));
  await view.renderConsistencyView();
  const rendered = elements.consistencyResults.innerHTML;
  assert.ok(rendered.includes('&lt;img src=x onerror=alert(1)&gt;') && !rendered.includes('<img src=x'),
    'hostile ticker text is escaped');
  assert.ok(rendered.includes('Dropped out') && rendered.includes('consistency-dropped'));
  assert.ok(rendered.includes('1 gap in the record: no scan between Sep 14 and Sep 17'));
  assert.ok(rendered.includes('Skipped &lt;bad&gt;.json'));
  assert.strictEqual(elements.pageMeta.textContent, 'Through 2026-09-18');
  assert.ok(elements.content.innerHTML.includes('aria-live="polite"'));

  state.setCurrentView('consistency');
  global.fetch = async () => response(history({}, { sessions_available: 0, sessions: [], denominator: 0, latest_session_date: null }));
  await view.renderConsistencyView();
  assert.ok(elements.consistencyResults.innerHTML.includes('No pick history yet'));
  assert.ok(elements.consistencyResults.innerHTML.includes('one entry per daily scan'));

  global.fetch = async () => response({ malformed: true });
  await assert.doesNotReject(() => view.renderConsistencyView());
  assert.ok(elements.consistencyResults.innerHTML.includes('No pick history yet'));
  global.fetch = async () => { throw new Error('offline'); };
  await assert.doesNotReject(() => view.renderConsistencyView());
  assert.ok(elements.consistencyResults.innerHTML.includes('No pick history yet'));

  state.setCurrentView('consistency');
  const first = deferred();
  const second = deferred();
  let fetchCount = 0;
  global.fetch = () => (++fetchCount === 1 ? first.promise : second.promise);
  const initialRender = view.renderConsistencyView();
  elements.consistencyList.value = 'top20';
  elements.consistencyList.dispatch('change');
  second.resolve(response(history({ SECOND: stat() }, { list: 'top20' })));
  await settle();
  assert.ok(elements.consistencyResults.innerHTML.includes('SECOND'));
  first.resolve(response(history({ FIRST: stat() })));
  await initialRender;
  await settle();
  assert.ok(elements.consistencyResults.innerHTML.includes('SECOND'));
  assert.ok(!elements.consistencyResults.innerHTML.includes('FIRST'), 'late earlier response is discarded');

  state.setCurrentView('consistency');
  const stale = deferred();
  global.fetch = () => stale.promise;
  const staleRender = view.renderConsistencyView();
  const beforeNavigation = elements.consistencyResults.innerHTML;
  state.setCurrentView('market');
  stale.resolve(response(history({ STALE: stat() })));
  await staleRender;
  assert.strictEqual(elements.consistencyResults.innerHTML, beforeNavigation, 'response is discarded after navigation');
  assert.ok(!elements.consistencyResults.innerHTML.includes('STALE'));

  const html = fs.readFileSync(path.join(ROOT, 'templates', 'dashboard.html'), 'utf8');
  const analyzeStart = html.indexOf('aria-label="Analyze"');
  const analyzeEnd = html.indexOf('aria-label="Run"', analyzeStart);
  const analyzeGroup = html.slice(analyzeStart, analyzeEnd);
  assert.ok(analyzeGroup.includes('href="#/consistency"') && analyzeGroup.includes('data-view="consistency"'));
  const dashboard = fs.readFileSync(path.join(ROOT, 'static', 'js', 'dashboard.js'), 'utf8');
  assert.ok(/consistency:\s*\{\s*title:\s*'Consistency',\s*render:\s*renderConsistencyView\s*\}/.test(dashboard));

  const source = fs.readFileSync(path.join(ROOT, 'static', 'js', 'views', 'consistency.js'), 'utf8');
  assert.ok(source.includes("event.key === 'Enter' || event.key === ' '") && source.includes("event.preventDefault()"));
  assert.ok(source.includes('role="button" tabindex="0" aria-sort='));

  console.log('test_consistency_view.js: all assertions passed');
}

main().catch(error => { console.error('FAILED:', error.stack || error.message); process.exit(1); });
