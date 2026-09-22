// Characterization test for the shortlist.js empty-state fix: a shortlist
// API response with no data can mean "no scan has ever run" (data.generated
// is null) OR "a scan completed and legitimately found zero candidates"
// (data.result === 'no_candidates', data.generated is a real timestamp).
// Before this fix both cases showed the identical "no scan has run" banner,
// making a normal zero-candidate trading day look indistinguishable from a
// broken pipeline — and the empty state never surfaced pageMeta's generated
// timestamp at all. See .sprint/SPRINT_PLAN.md (TASK-003) for the bug report.
//
// Mocks shortlist.js's imports (fetchJSON, DOM, core/ui-helpers) and calls
// the real renderShortlistView(), matching this repo's no-framework/no-build
// testing style — same "extract/mock and eval" approach as the other files
// in this directory, just at module granularity since this function needs
// its real module-level imports resolved, not just its own function body.
//
// Run with: node tests/js/test_shortlist_empty_state.js

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');

function fakeEl() {
  return { innerHTML: '', textContent: '', style: {}, addEventListener: () => {}, querySelectorAll: () => [] };
}

async function renderScenario(scenario, responses) {
  const elements = {};
  global.document = { getElementById: (id) => (elements[id] ||= fakeEl()), querySelectorAll: () => [] };
  global.window = {};
  global.location = { href: 'http://localhost/' };
  global.fetch = async () => ({ json: async () => ({}) });

  const contentEl = fakeEl();
  const pageMetaEl = fakeEl();

  global.__mockFetchJSON = async (url) => {
    if (url === '/api/shortlist') return responses[scenario];
    if (url === '/api/top20') return { generated: responses[scenario].generated, top20: [{ ticker: 'AAPL', score: 80 }] };
    return {};
  };
  global.__mockContent = contentEl;
  global.__mockPageMeta = pageMetaEl;
  global.__mockCurrentView = 'shortlist';

  const srcPath = path.join(__dirname, '..', '..', 'static', 'js', 'views', 'shortlist.js');
  const src = fs.readFileSync(srcPath, 'utf8');

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
    .replace("import { loadNewsGroup, newsSectionHTML } from '../components/news.js';", `
      const loadNewsGroup = async () => {};
      const newsSectionHTML = () => '';
    `)
    .replace("import { loadConsistency } from '../core/pick-history.js';", 'const loadConsistency = async () => null;');

  const tmpFile = path.join(os.tmpdir(), `shortlist_patched_${scenario}.mjs`);
  fs.writeFileSync(tmpFile, patched);
  const mod = await import(`file://${tmpFile}`);
  await mod.renderShortlistView();
  fs.unlinkSync(tmpFile);

  return { pageMetaText: pageMetaEl.textContent, bannerHTML: contentEl.innerHTML };
}

async function main() {
  const responses = {
    'never-scanned': { generated: null, result: null, shortlist: [], fundamentals_audits: {}, catalyst_sentiments: {}, congress_signals: {} },
    'zero-candidates': { generated: '2026-09-14T12:00:00', result: 'no_candidates', shortlist: [], fundamentals_audits: {}, catalyst_sentiments: {}, congress_signals: {} },
  };

  const neverScanned = await renderScenario('never-scanned', responses);
  assert.strictEqual(neverScanned.pageMetaText, '', 'no-scan-ever case should show no generated timestamp');
  assert.ok(neverScanned.bannerHTML.includes('No filtered shortlist yet'),
    'no-scan-ever case should show the generic "run a scan" banner');

  const zeroCandidates = await renderScenario('zero-candidates', responses);
  assert.ok(zeroCandidates.pageMetaText.includes('Generated'),
    'zero-candidates case must surface the real generated timestamp (this was the bug: pageMeta was only set in the non-empty branch)');
  assert.ok(zeroCandidates.bannerHTML.includes('found no candidates'),
    'zero-candidates case must show a distinct message, not the generic "no scan has run" banner');
  assert.ok(!zeroCandidates.bannerHTML.includes('No filtered shortlist yet'),
    'zero-candidates case must NOT show the "run a scan" banner — a scan DID run');

  console.log('test_shortlist_empty_state.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
