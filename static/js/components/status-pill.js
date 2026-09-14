function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

const statuses = new Set(['idle', 'running', 'success', 'error']);

export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
  const normalizedStatus = statuses.has(status) ? status : 'idle';
  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';

  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
}
