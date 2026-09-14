// Characterization test for _liveGuarded — moved to static/js/core/refresh.js
// by TASK-003 (router/jobs/refresh extraction). Locks in the dedup behavior
// from before that extraction; a failure here means the move changed real
// behavior, not just relocated code.
//
// Plain Node, no test framework/dependency — matches this repo's "no build
// step" frontend. Run with: node tests/js/test_live_guard.js

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(
  path.join(__dirname, '..', '..', 'static', 'js', 'core', 'refresh.js'), 'utf8'
);

function extract(fnName) {
  let start = src.indexOf(`function ${fnName}(`);
  if (start === -1) throw new Error(`${fnName} not found in dashboard.js`);
  // Include a leading "async " if present — dropping it silently turns a
  // valid async function into a syntax error at its own `await` calls.
  if (src.slice(Math.max(0, start - 6), start) === 'async ') start -= 6;
  let depth = 0, i = src.indexOf('{', start);
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') { depth--; if (depth === 0) break; }
  }
  return src.slice(start, i + 1);
}

// eslint-disable-next-line no-eval
eval('const _liveInFlight = new Set();\n' + extract('_liveGuarded'));

async function main() {
  // Test 1: sequential calls with the same key both run (no false-positive dedup)
  let runs = 0;
  await _liveGuarded('a', async () => { runs++; });
  await _liveGuarded('a', async () => { runs++; });
  assert.strictEqual(runs, 2, 'sequential calls with the same key should both execute');

  // Test 2: a call that's still in-flight blocks a concurrent call with the SAME key
  let concurrentRuns = 0;
  let resolveFirst;
  const firstCall = _liveGuarded('b', () => new Promise(r => { resolveFirst = r; })
    .then(() => { concurrentRuns++; }));
  // second call fires while the first is still pending
  await _liveGuarded('b', async () => { concurrentRuns++; });
  assert.strictEqual(concurrentRuns, 0, 'overlapping call with the same key must be skipped, not queued');
  resolveFirst();
  await firstCall;
  assert.strictEqual(concurrentRuns, 1, 'only the first in-flight call should have run');

  // Test 3: different keys never block each other
  let cRuns = 0, dRuns = 0;
  let resolveC;
  const cCall = _liveGuarded('c', () => new Promise(r => { resolveC = r; }).then(() => { cRuns++; }));
  await _liveGuarded('d', async () => { dRuns++; });
  assert.strictEqual(dRuns, 1, 'a different key must not be blocked by an in-flight call under another key');
  resolveC();
  await cCall;
  assert.strictEqual(cRuns, 1);

  // Test 4: the guard clears after completion, allowing a later call through
  let eRuns = 0;
  await _liveGuarded('e', async () => { eRuns++; });
  await _liveGuarded('e', async () => { eRuns++; });
  assert.strictEqual(eRuns, 2, 'the in-flight marker must be released after the guarded call resolves');

  console.log('test_live_guard.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
