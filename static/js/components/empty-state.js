function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';

  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
}
