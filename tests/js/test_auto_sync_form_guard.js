const assert = require('assert');
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(
  path.join(__dirname, '..', '..', 'static', 'js', 'dashboard.js'), 'utf8'
);

function extract(fnName) {
  let start = src.indexOf(`function ${fnName}(`);
  if (start === -1) throw new Error(`${fnName} not found in dashboard.js`);
  if (src.slice(Math.max(0, start - 6), start) === 'async ') start -= 6;
  let depth = 0;
  let i = src.indexOf('{', start);
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') {
      depth--;
      if (depth === 0) break;
    }
  }
  return src.slice(start, i + 1);
}

async function main() {
  let currentView;
  let routeCalls = 0;
  const toastMessages = [];
  const fetchJSON = async () => ({ success: true, output: 'Pulled new data' });
  const route = () => { routeCalls++; };
  const events = [];
  const window = { dispatchEvent: event => events.push(event) };
  const CustomEvent = class { constructor(type, options) { this.type = type; this.detail = options.detail; } };
  const showToast = (message) => { toastMessages.push(message); };
  // doSync also calls this (added alongside the data-freshness indicator,
  // see test_shortlist_empty_state.js's sibling bug fix) — it's irrelevant
  // to what this test is about, so just no-op it like the other collaborators.
  const refreshDataFreshness = () => {};

  eval(extract('doSync'));

  currentView = 'run';
  await doSync(true);
  assert.strictEqual(routeCalls, 0, 'silent sync must preserve Run form state');

  currentView = 'market';
  await doSync(true);
  assert.strictEqual(routeCalls, 0, 'Market updates in place so its replay position is preserved');

  currentView = 'run';
  await doSync(false);
  assert.strictEqual(routeCalls, 1, 'manual sync must refresh Run after a successful pull');

  currentView = 'scan';
  await doSync(false);
  assert.strictEqual(routeCalls, 2, 'manual sync must refresh Scan after a successful pull');
  assert.strictEqual(toastMessages.length, 4, 'successful pulls must retain their toast notification');
  assert.strictEqual(events.length, 4, 'each successful pull dispatches an in-place data event');
  assert.ok(events.every(event => event.type === 'stock-data-updated'));

  console.log('test_auto_sync_form_guard.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
