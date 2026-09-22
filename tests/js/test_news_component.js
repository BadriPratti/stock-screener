// Characterization tests for the shared news component
// (static/js/components/news.js), extracted from static/js/views/market.js
// during the news-reorganization sprint. Covers: recency sorting with
// missing/invalid dates, deduplication, the 2-headline default cap with
// expand-state tracked outside the DOM (so it survives the 90s live-refresh
// full innerHTML replacement), and preserving the caller's requested ticker
// order rather than the API response's key order.
//
// Mocks this module's imports (core/jobs, core/api, core/refresh,
// core/ui-helpers) and imports the real module, matching the mock-and-import
// style already used by tests/js/test_shortlist_empty_state.js.
//
// Run with: node tests/js/test_news_component.js

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');

function fakeEl() {
  return {
    innerHTML: '', textContent: '',
    addEventListener: () => {}, querySelectorAll: () => [],
    _listeners: {},
  };
}

async function loadModule() {
  global.document = { getElementById: () => fakeEl(), querySelectorAll: () => [] };

  const srcPath = path.join(__dirname, '..', '..', 'static', 'js', 'components', 'news.js');
  const src = fs.readFileSync(srcPath, 'utf8');
  const patched = src
    .replace("import { startJob } from '../core/jobs.js';", 'const startJob = async () => {};')
    .replace("import { fetchJSON } from '../core/api.js';", 'const fetchJSON = async () => ({});')
    .replace("import { liveBadgeHTML } from '../core/refresh.js';", "const liveBadgeHTML = () => '<span class=\"live-badge\"></span>';")
    .replace("import { escapeHtml, safeHref } from '../core/ui-helpers.js';", `
      const escapeHtml = (s) => String(s ?? '');
      const safeHref = (url) => {
        try {
          const u = new URL(url, 'http://localhost/');
          return (u.protocol === 'http:' || u.protocol === 'https:') ? u.href : '#';
        } catch { return '#'; }
      };
    `);

  const tmpFile = path.join(os.tmpdir(), `news_component_patched_${Date.now()}_${Math.random()}.mjs`);
  fs.writeFileSync(tmpFile, patched);
  const mod = await import(`file://${tmpFile}`);
  fs.unlinkSync(tmpFile);
  return mod;
}

async function main() {
  const { renderNewsGroupHTML } = await loadModule();

  // --- Recency sorting ---
  const now = Date.now();
  const hoursAgo = (h) => new Date(now - h * 3600 * 1000).toISOString();
  const newsByTicker = {
    AAPL: [
      { title: 'Yesterday story', publisher: 'A', pub_date: hoursAgo(26), url: 'https://x.com/1' },
      { title: 'Two hours ago story', publisher: 'B', pub_date: hoursAgo(2), url: 'https://x.com/2' },
      { title: 'No date story', publisher: 'C', pub_date: null, url: 'https://x.com/3' },
      { title: 'Three weeks ago story', publisher: 'D', pub_date: hoursAgo(21 * 24), url: 'https://x.com/4' },
    ],
  };
  const html = renderNewsGroupHTML('test1', ['AAPL'], newsByTicker);
  const titleOrder = [...html.matchAll(/news-headline-title">([^<]+)</g)].map(m => m[1]);
  // Only 2 shown by default; the 2 most recent must be first, in recency order.
  assert.deepStrictEqual(titleOrder.slice(0, 2), ['Two hours ago story', 'Yesterday story'],
    'headlines must be sorted newest-first, with the top 2 visible by default');
  assert.ok(html.includes('+2 more'), 'must show a "+N more" button for the remaining headlines');

  // --- Missing/invalid dates sort last, not crash ---
  const badDates = {
    BBB: [
      { title: 'Valid', publisher: 'A', pub_date: hoursAgo(1), url: 'https://x.com/5' },
      { title: 'Invalid date string', publisher: 'B', pub_date: 'not-a-date', url: 'https://x.com/6' },
    ],
  };
  const html2 = renderNewsGroupHTML('test2', ['BBB'], badDates);
  assert.ok(html2.indexOf('Valid') < html2.indexOf('Invalid date string'),
    'a valid date must sort before an invalid/unparseable one');

  // --- Zero, one, two headlines: no expand button ---
  const fewHeadlines = { CCC: [{ title: 'Only one', publisher: 'A', pub_date: hoursAgo(1), url: 'https://x.com/7' }] };
  const html3 = renderNewsGroupHTML('test3', ['CCC'], fewHeadlines);
  assert.ok(!html3.includes('more'), 'a single headline must not render an expand button');

  // --- Zero headlines for a ticker: still renders a card, doesn't vanish ---
  const html4 = renderNewsGroupHTML('test4', ['DDD'], {});
  assert.ok(html4.includes('DDD'), 'a ticker missing from the API response must still render its own card');
  assert.ok(html4.includes('No recent headlines'), 'a ticker with no headlines shows an explicit empty message');

  // --- Ticker order preserved (not alphabetized / not API key order) ---
  const outOfOrder = { ZZZ: [{ title: 'z', publisher: 'A', pub_date: hoursAgo(1), url: 'https://x.com/8' }], AAA: [{ title: 'a', publisher: 'A', pub_date: hoursAgo(1), url: 'https://x.com/9' }] };
  const html5 = renderNewsGroupHTML('test5', ['ZZZ', 'AAA'], outOfOrder);
  assert.ok(html5.indexOf('ZZZ') < html5.indexOf('AAA'),
    'ticker cards must render in the order the caller requested, not alphabetically or by API key order');

  // --- Deduplication by URL ---
  const dupes = { EEE: [
    { title: 'Same story v1', publisher: 'A', pub_date: hoursAgo(1), url: 'https://x.com/dup' },
    { title: 'Same story v1', publisher: 'A', pub_date: hoursAgo(1), url: 'https://x.com/dup' },
    { title: 'Different story', publisher: 'B', pub_date: hoursAgo(2), url: 'https://x.com/unique' },
  ] };
  const html6 = renderNewsGroupHTML('test6', ['EEE'], dupes);
  assert.strictEqual((html6.match(/Same story v1/g) || []).length, 1, 'an exact URL duplicate must only render once');

  // --- Unsafe/missing URL renders as non-clickable text, not a misleading link ---
  const badUrl = { FFF: [{ title: 'Sketchy link', publisher: 'A', pub_date: hoursAgo(1), url: 'javascript:alert(1)' }] };
  const html7 = renderNewsGroupHTML('test7', ['FFF'], badUrl);
  assert.ok(html7.includes('news-headline-nolink'), 'an unsafe URL must render as non-clickable text, not an <a> link');
  assert.ok(!html7.includes('<a href="javascript'), 'must never emit an anchor pointing at a non-http(s) scheme');

  console.log('test_news_component.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message, e.stack); process.exit(1); });
