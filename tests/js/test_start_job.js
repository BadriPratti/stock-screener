// Characterization test for startJob — moved to static/js/core/jobs.js by
// TASK-003 (router/jobs/refresh extraction). Locks in the fix from earlier
// this session where startJob's returned promise now resolves only on job
// completion, not right after the initial POST. Every _liveGuarded caller
// depends on this to know when it's actually safe to start the next refresh
// cycle; regressing this silently defeats that guard again (it happened once
// already — see the git history for "_liveGuarded doesn't actually await job
// completion").
//
// Plain Node, no test framework/dependency. Run with: node tests/js/test_start_job.js

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(
  path.join(__dirname, '..', '..', 'static', 'js', 'core', 'jobs.js'), 'utf8'
);

function extract(fnName) {
  let start = src.indexOf(`function ${fnName}(`);
  if (start === -1) throw new Error(`${fnName} not found in dashboard.js`);
  if (src.slice(Math.max(0, start - 6), start) === 'async ') start -= 6;
  let depth = 0, i = src.indexOf('{', start);
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') { depth--; if (depth === 0) break; }
  }
  return src.slice(start, i + 1);
}

async function main() {
  // Mock fetchJSON: first call is the POST (returns job_id), subsequent
  // calls are polls returning a scripted status sequence.
  const statusSequence = ['queued', 'running', 'running', 'success'];
  let pollCount = 0;
  let postCalled = false;

  global.fetchJSON = async (url, opts) => {
    if (opts && opts.method === 'POST') {
      postCalled = true;
      return { job_id: 'test-job-1' };
    }
    const status = statusSequence[Math.min(pollCount, statusSequence.length - 1)];
    pollCount++;
    return { status, output: [] };
  };

  // startJob's internal setTimeout(poll, 1500) would make this test slow —
  // replace with immediate scheduling for the test only.
  global.setTimeout = (fn) => fn();

  eval(extract('startJob'));

  const updates = [];
  let resolvedBeforeTerminal = false;

  const jobPromise = startJob('test-kind', {}, (st) => {
    updates.push(st.status);
    if (st.status === 'running' || st.status === 'queued') {
      // If the promise has already resolved while we're still seeing
      // non-terminal statuses, the fix regressed.
    }
  });

  const resolvedJobId = await jobPromise;

  assert.strictEqual(postCalled, true, 'startJob must POST to start the job');
  assert.strictEqual(resolvedJobId, 'test-job-1', 'startJob must resolve with the job_id');
  assert.deepStrictEqual(
    updates, ['queued', 'running', 'running', 'success'],
    'onUpdate must have been called once per poll, ending with the terminal status'
  );
  // The critical regression check: the promise must not have resolved until
  // the LAST onUpdate call (the terminal one) had already fired.
  assert.strictEqual(
    updates[updates.length - 1], 'success',
    'the last onUpdate call before resolution must be the terminal status — ' +
    'if this fails, startJob is resolving early again (the exact bug fixed this session)'
  );

  console.log('test_start_job.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
