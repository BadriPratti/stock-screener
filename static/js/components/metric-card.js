function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);

export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
  const variantClass = variants.has(variant) ? ` ${variant}` : '';
  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;

  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
}
