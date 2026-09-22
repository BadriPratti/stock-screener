// Characterization tests for static/js/core/pick-history.js (the consistency
// badges on the Shortlist cards and the Top 20 table) and for the Consistency
// column the shared renderTop20Table now emits.
//
// The rules locked in here are the ones that would silently mislead a user if
// they regressed: the denominator is always the number of scans actually
// recorded (a short ledger must never read as a long window); a slow response
// for one list can never paint badges into another list's slots; and a failed
// or malformed history request degrades to "no badges" without throwing.
//
// Run with: node tests/js/test_pick_history_badges.js

const assert = require('assert');
const path = require('path');

function fakeEscapableElement() {
  const el = { _text: '' };
  Object.defineProperty(el, 'textContent', { set(v) { el._text = v; }, get() { return el._text; } });
  Object.defineProperty(el, 'innerHTML', { get() { return el._text; }, set(v) { el._text = v; } });
  return el;
}

const slots = {};
function fakeSlot(id) {
  slots[id] = { innerHTML: '', textContent: '' };
  return slots[id];
}

global.document = {
  getElementById: (id) => slots[id] || null,
  querySelectorAll: () => [],
  createElement: fakeEscapableElement,
};
global.window = { addEventListener: () => {} };
global.location = { href: 'http://localhost/' };

const ROOT = path.join(__dirname, '..', '..', 'static', 'js');
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B50}]/u;

function stat(overrides = {}) {
  return {
    appearances: 4, denominator: 5, appearance_rate: 0.8, current_streak: 2, longest_streak: 2,
    total_appearances: 4, first_seen: '2026-09-14', last_seen: '2026-09-18', is_active_today: true,
    best_rank: 1, average_rank: 2.25, average_score: 126.075, latest_score: 123.6, score_delta: -4.4,
    history: [
      { date: '2026-09-14', rank: 4, score: 127.5 },
      { date: '2026-09-15', rank: 2, score: 125.0 },
      { date: '2026-09-17', rank: 2, score: 128.0 },
      { date: '2026-09-18', rank: 1, score: 123.6 },
    ],
    ...overrides,
  };
}

function history(overrides = {}) {
  return {
    schema_version: 1, list: 'shortlist', run_kind: 'daily_full', window_requested: 5,
    sessions_available: 5, sessions: ['2026-09-14', '2026-09-15', '2026-09-16', '2026-09-17', '2026-09-18'],
    denominator: 5, latest_session_date: '2026-09-18', coverage_gaps: [], warnings: [],
    tickers: { LILAK: stat() },
    ...overrides,
  };
}

async function main() {
  const ph = await import(`file://${path.join(ROOT, 'core', 'pick-history.js')}`);

  // --- date formatting ---------------------------------------------------
  assert.strictEqual(ph.formatSessionDate('2026-09-18'), 'Sep 18');
  assert.strictEqual(ph.formatSessionDate('2026-01-05'), 'Jan 5');
  assert.strictEqual(ph.formatSessionDate('not-a-date'), 'not-a-date', 'unparseable input passes through');
  assert.strictEqual(ph.formatSessionDate(null), '');

  // --- badges ------------------------------------------------------------
  assert.strictEqual(ph.consistencyBadgeHTML(stat(), history({ sessions_available: 0 })), '',
    'an empty ledger renders no badge at all');
  assert.strictEqual(ph.consistencyBadgeHTML(stat(), null), '');

  const badge = ph.consistencyBadgeHTML(stat(), history());
  assert.ok(badge.includes('4/5 scans'), 'frequency badge shows appearances/denominator');
  assert.ok(badge.includes('2-scan streak'), 'a 2-scan current streak gets a streak badge');
  assert.ok(!badge.includes('new-pick'), 'a stock seen 4 times is not "New"');
  assert.ok(badge.includes('Best rank #1') && badge.includes('Sep 14 #4'),
    'the tooltip carries best rank and the per-scan rank history');
  assert.ok(badge.includes('the Shortlist'), 'the tooltip names which list this is about');
  assert.ok(!EMOJI.test(badge), 'no emoji anywhere in the UI (project rule)');

  assert.ok(!ph.consistencyBadgeHTML(stat({ current_streak: 1 }), history()).includes('badge streak'),
    'a streak of 1 is not worth a streak badge (the tooltip may still mention it)');
  assert.ok(ph.consistencyBadgeHTML(stat({ current_streak: 2 }), history()).includes('badge streak'));
  const fresh = ph.consistencyBadgeHTML(stat({ appearances: 1, total_appearances: 1, current_streak: 1 }), history());
  assert.ok(fresh.includes('new-pick') && fresh.includes('>New<'), 'first-ever appearance today is marked New');
  assert.ok(!ph.consistencyBadgeHTML(stat({ total_appearances: 1, is_active_today: false }), history()).includes('new-pick'),
    'New only applies to a stock that is on today\'s list');

  const absent = ph.consistencyBadgeHTML(undefined, history());
  assert.ok(absent.includes('Not on record'), 'a ticker with no history entry is shown neutrally, not as a fake stat');
  assert.ok(!/\d+\/\d+/.test(absent), 'and never with an invented fraction');

  // Short ledger, long requested window: the badge must use the REAL denominator.
  const shortLedger = ph.consistencyBadgeHTML(
    stat({ appearances: 2, denominator: 3 }),
    history({ window_requested: 20, sessions_available: 3, denominator: 3 }),
  );
  assert.ok(shortLedger.includes('2/3 scans') && !shortLedger.includes('/20'),
    'a 3-scan ledger viewed with window=20 still says 2/3, never x/20');

  // Untrusted-looking text in a tooltip attribute must not break out of it.
  const hostile = ph.consistencyBadgeHTML(
    stat({ history: [{ date: '2026-09-18"><img src=x onerror=alert(1)>', rank: 1, score: 1 }] }), history());
  assert.ok(!hostile.includes('"><img'), 'tooltip attribute content is HTML-escaped');

  // --- caption -----------------------------------------------------------
  assert.strictEqual(
    ph.consistencyCaptionText(history()),
    'Consistency: last 5 recorded scans (Sep 14 - Sep 18), through 2026-09-18.',
  );
  const shortCaption = ph.consistencyCaptionText(history({
    window_requested: 20, sessions_available: 5, denominator: 5,
  }));
  assert.ok(shortCaption.includes('Only 5 scans on record so far.'),
    'asking for 20 but having 5 must be stated plainly');
  assert.ok(ph.consistencyCaptionText(history({ sessions: ['2026-09-18'], sessions_available: 1, denominator: 1, window_requested: 5 }))
    .includes('last 1 recorded scan (Sep 18)'), 'singular wording for one scan');
  assert.ok(ph.consistencyCaptionText(history({ sessions_available: 0 })).includes('starts after the first recorded'));
  assert.ok(ph.consistencyCaptionText(history({ warnings: ["Skipped 2026-09-16.json: bad"] })).includes('1 history file skipped'),
    'a skipped/corrupt history file is surfaced, not hidden');

  // --- painting: list-scoped slot ids -------------------------------------
  for (const k of Object.keys(slots)) delete slots[k];
  const shortlistSlot = fakeSlot('consistency-slot-shortlist-LILAK');
  const top20Slot = fakeSlot('consistency-slot-top20-LILAK');
  const shortlistCaption = fakeSlot('consistency-caption-shortlist');
  const top20Caption = fakeSlot('consistency-caption-top20');

  ph.paintConsistencySlots(['LILAK'], history({ list: 'shortlist' }));
  assert.ok(shortlistSlot.innerHTML.includes('4/5 scans'), 'shortlist history paints the shortlist slot');
  assert.strictEqual(top20Slot.innerHTML, '', 'and must NOT touch the Top 20 slot for the same ticker');
  assert.ok(shortlistCaption.textContent.startsWith('Consistency:'));
  assert.strictEqual(top20Caption.textContent, '', 'nor the other list\'s caption');

  // --- loading -------------------------------------------------------------
  const calls = [];
  const respondWith = (payload) => { global.fetch = async (url) => { calls.push(url); return { json: async () => payload }; }; };

  for (const k of Object.keys(slots)) delete slots[k];
  const slot = fakeSlot('consistency-slot-shortlist-LILAK');
  respondWith(history({ list: 'shortlist' }));
  const loaded = await ph.loadConsistency(['LILAK'], 'shortlist', 5);
  assert.ok(loaded && loaded.list === 'shortlist');
  assert.strictEqual(calls[0], '/api/pick-history?list=shortlist&window=5', 'requests the right list and window');
  assert.ok(slot.innerHTML.includes('4/5 scans'));

  slot.innerHTML = '';
  respondWith(history({ list: 'top20' }));
  assert.strictEqual(await ph.loadConsistency(['LILAK'], 'shortlist', 5), null,
    'a response for a different list than requested is discarded');
  assert.strictEqual(slot.innerHTML, '', 'and nothing is painted from it');

  respondWith({ error: 'boom' });
  assert.strictEqual(await ph.loadConsistency(['LILAK'], 'shortlist'), null, 'malformed payload -> null, no throw');

  global.fetch = async () => { throw new Error('network down'); };
  assert.strictEqual(await ph.loadConsistency(['LILAK'], 'shortlist'), null, 'network failure -> null, no throw');

  calls.length = 0;
  respondWith(history());
  assert.strictEqual(await ph.loadConsistency([], 'shortlist'), null);
  assert.strictEqual(calls.length, 0, 'no tickers means no request at all');

  // --- the shared Top 20 table's new column --------------------------------
  const ui = await import(`file://${path.join(ROOT, 'core', 'ui-helpers.js')}`);
  const table = ui.renderTop20Table([{ ticker: 'AAA', combined_score: 100, why_links: [] }]);
  assert.ok(table.includes('<th scope="col">Consistency</th>'), 'Top 20 table has a Consistency column header');
  assert.ok(table.includes('id="consistency-slot-top20-AAA"'), 'each row has a top20-scoped slot');
  assert.ok(table.includes('id="consistency-caption-top20"'), 'and the table has a caption slot');
  assert.ok(table.indexOf('Momentum') < table.indexOf('Consistency') && table.indexOf('Consistency') < table.indexOf('Reddit'),
    'column sits between Momentum and Reddit');

  console.log('test_pick_history_badges.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.stack || e.message); process.exit(1); });
