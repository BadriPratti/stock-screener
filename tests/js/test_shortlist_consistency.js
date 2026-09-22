// View-level wiring for the consistency badges on the Shortlist view: each
// pick card gets a shortlist-scoped slot, the view gets a caption slot, and
// the right list is requested for each render path (the Shortlist itself vs.
// the Top 20 fallback shown when no shortlist exists). Mock-import style, same
// as test_shortlist_empty_state.js.
//
// Run with: node tests/js/test_shortlist_consistency.js

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

function fakeEl() {
  return { innerHTML: '', textContent: '', style: {}, addEventListener: () => {}, querySelectorAll: () => [] };
}

async function render(shortlistPayload, top20Payload) {
  const elements = {};
  global.document = { getElementById: (id) => (elements[id] ||= fakeEl()), querySelectorAll: () => [] };
  global.window = {};
  global.location = { href: 'http://localhost/' };

  const contentEl = fakeEl();
  const calls = [];
  global.__mockFetchJSON = async (url) => (url === '/api/shortlist' ? shortlistPayload : top20Payload);
  global.__mockContent = contentEl;
  global.__mockPageMeta = fakeEl();
  global.__mockCurrentView = 'shortlist';
  global.__consistencyCalls = calls;

  const src = fs.readFileSync(path.join(__dirname, '..', '..', 'static', 'js', 'views', 'shortlist.js'), 'utf8');
  const patched = src
    .replace("import { fetchJSON } from '../core/api.js';", 'const fetchJSON = global.__mockFetchJSON;')
    .replace("import { startJob } from '../core/jobs.js';", 'const startJob = async () => {};')
    .replace("import { _liveGuarded, _startLive } from '../core/refresh.js';", 'const _liveGuarded = async () => {}; const _startLive = () => {};')
    .replace("import { content, currentView, pageMeta } from '../core/state.js';", 'const content = global.__mockContent; const currentView = global.__mockCurrentView; const pageMeta = global.__mockPageMeta;')
    .replace(/import \{[\s\S]*?\} from '..\/core\/ui-helpers.js';/, `
      const analysisButtonHTML = () => '';
      const escapeHtml = (s) => s;
      const fidelityLink = () => '';
      const loadMomentumStatus = () => {};
      const paintMomentumSlots = () => {};
      const refreshAnalysisModal = () => {};
      const renderTop20Table = (top20) => '<table data-top20-count="' + top20.length + '"></table>';
      const wireAnalysisButtons = () => {};
    `)
    .replace("import { loadNewsGroup, newsSectionHTML } from '../components/news.js';", 'const loadNewsGroup = async () => {}; const newsSectionHTML = () => "";')
    .replace("import { loadConsistency } from '../core/pick-history.js';", 'const loadConsistency = async (t, l, w) => { global.__consistencyCalls.push([t, l, w]); return null; };');

  const tmp = path.join(os.tmpdir(), `shortlist_consistency_${Date.now()}_${Math.random().toString(36).slice(2)}.mjs`);
  fs.writeFileSync(tmp, patched);
  const mod = await import(`file://${tmp}`);
  await mod.renderShortlistView();
  fs.unlinkSync(tmp);
  return { html: contentEl.innerHTML, calls };
}

async function main() {
  const populated = await render({
    generated: '2026-09-18T17:07:46',
    shortlist: [
      { ticker: 'LILAK', composite_score: 123.6, passed_filters: true },
      { ticker: 'LTC', composite_score: 122.1, passed_filters: true },
    ],
    fundamentals_audits: {}, catalyst_sentiments: {}, congress_signals: {},
  }, { top20: [] });

  assert.ok(populated.html.includes('id="consistency-slot-shortlist-LILAK"'), 'each pick card has a shortlist-scoped slot');
  assert.ok(populated.html.includes('id="consistency-slot-shortlist-LTC"'));
  assert.ok(populated.html.includes('id="consistency-caption-shortlist"'), 'the view has a caption slot');
  assert.deepStrictEqual(populated.calls, [[['LILAK', 'LTC'], 'shortlist', undefined]],
    'requests the SHORTLIST history for exactly the displayed tickers, once');

  const fallback = await render(
    { generated: '2026-09-18T17:07:46', shortlist: [] },
    { top20: [{ ticker: 'AAA' }, { ticker: 'BBB' }] },
  );
  assert.deepStrictEqual(fallback.calls, [[['AAA', 'BBB'], 'top20', undefined]],
    'the Top 20 fallback requests the TOP 20 history, never the shortlist one');

  console.log('test_shortlist_consistency.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.stack || e.message); process.exit(1); });
