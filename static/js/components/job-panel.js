function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

const statuses = new Set(['idle', 'running', 'success', 'error']);

export function jobPanelHTML({
  id,
  title,
  description = '',
  paramsHTML = '',
  runLabel = 'Run',
  status = 'idle',
  statusLabel = null,
  outputHTML = '',
  resultHTML = '',
} = {}) {
  if (!id) throw new TypeError('jobPanelHTML requires an id');

  const safeId = escapeHtml(id);
  const normalizedStatus = statuses.has(status) ? status : 'idle';

  return `
    <div class="card sim-card">
      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill" role="status" aria-live="polite">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
      <div class="sim-desc">${escapeHtml(description)}</div>
      <div class="sim-params">${paramsHTML}</div>
      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
    </div>`;
}
