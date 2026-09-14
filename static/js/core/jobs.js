import { fetchJSON } from './api.js';

// --- Background job runner (Run Simulation / Full Scan views) ----------

// Resolves only once the job reaches a terminal state (success/error/stopped),
// not right after it starts — every caller does `await startJob(...)` expecting
// that to mean "the job is done," and several (via _liveGuarded) depend on it
// to know when it's safe to start the next refresh cycle. It used to resolve
// as soon as the initial POST came back, which silently defeated that guard.
export async function startJob(kind, body, onUpdate) {
  const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  return new Promise((resolve) => {
    const poll = async () => {
      const st = await fetchJSON(`/api/jobs/${job_id}`);
      onUpdate(st);
      if (st.status === 'running' || st.status === 'queued') {
        setTimeout(poll, 1500);
      } else {
        resolve(job_id);
      }
    };
    poll();
  });
}

// Job cards (Run Simulation, Full Scan) kick off long-running background jobs
// (a real detached subprocess on the server — it was never actually stopped by
// navigating away). What used to break on navigation was the UI side: the
// click handler closed over the specific DOM nodes present at click-time, so
// leaving the page and coming back re-rendered a fresh "idle" card with no
// memory of the job still running (or just finished) underneath it. _activeJobs
// tracks job_id per card id at module scope — outside any view's DOM — so it
// survives a route change, and wireJobCard reconnects to it on every render.
const _activeJobs = {}; // cardId -> most recent job_id for that card (running OR finished), survives across renders
const _watchingJobIds = {}; // cardId -> job_id an active setTimeout poll loop is already chasing

export function watchJob(id, jobId, onResult) {
  _activeJobs[id] = jobId;
  // Reconnecting to a job you're already polling (e.g. navigating back and
  // forth while it runs) would otherwise stack up a duplicate setTimeout
  // chain each time — same end state, just wasted polling. The next tick of
  // the existing loop repaints the freshly-mounted card within ~1.5s anyway.
  if (_watchingJobIds[id] === jobId) return;
  _watchingJobIds[id] = jobId;

  const poll = async () => {
    const st = await fetchJSON(`/api/jobs/${jobId}`);
    if (st.error) {
      // The server prunes finished jobs after a while — if you reconnect to
      // one long after it ended, just drop back to idle instead of crashing
      // on the missing `output` field.
      if (_activeJobs[id] === jobId) delete _activeJobs[id];
      if (_watchingJobIds[id] === jobId) delete _watchingJobIds[id];
      return;
    }
    const btn = document.getElementById(`${id}-run`);
    const pill = document.getElementById(`${id}-pill`);
    const out = document.getElementById(`${id}-output`);
    // Paint only if this card is actually on screen right now — if you've
    // navigated elsewhere these are null and we just skip rendering. The job
    // itself keeps running server-side regardless; we'll catch up next poll,
    // or immediately via this same function when you navigate back.
    if (btn && pill && out) {
      out.style.display = 'block';
      out.textContent = st.output.join('\n');
      out.scrollTop = out.scrollHeight;
      if (st.status === 'running' || st.status === 'queued') {
        btn.disabled = true;
        pill.className = 'status-pill running';
        pill.innerHTML = '<span class="spinner"></span> running';
      } else {
        btn.disabled = false;
        pill.className = `status-pill ${st.status}`;
        pill.textContent = st.status;
      }
    }

    if (st.status === 'running' || st.status === 'queued') {
      setTimeout(poll, 1500);
    } else {
      // Deliberately NOT clearing _activeJobs[id] here — it's what lets
      // wireJobCard reconnect and show the finished result if the job
      // completed while you were on a different page (the common case for
      // anything that finishes in under a minute or two). It's only replaced
      // when this card starts a new job, never otherwise.
      if (_watchingJobIds[id] === jobId) delete _watchingJobIds[id];
      if (st.status === 'success' && onResult) {
        const resultEl = document.getElementById(`${id}-result`);
        if (resultEl) await onResult(st, resultEl);
      }
    }
  };
  poll();
}

export function wireJobCard(id, kind, getParams, onResult) {
  // Reconnect to a job started before navigating away and back.
  if (_activeJobs[id]) {
    watchJob(id, _activeJobs[id], onResult);
  }

  document.getElementById(`${id}-run`).addEventListener('click', async () => {
    const btn = document.getElementById(`${id}-run`);
    const pill = document.getElementById(`${id}-pill`);
    const out = document.getElementById(`${id}-output`);
    const resultEl = document.getElementById(`${id}-result`);
    // Disable synchronously, before the POST round-trip, so a rapid double
    // click can't start two overlapping jobs for the same card.
    btn.disabled = true;
    pill.className = 'status-pill running';
    pill.innerHTML = '<span class="spinner"></span> running';
    out.style.display = 'block';
    out.textContent = '';
    if (resultEl) resultEl.innerHTML = '';

    const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(getParams()),
    });
    watchJob(id, job_id, onResult);
  });
}
