function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function normalizeHeader(header, index) {
  if (typeof header === 'string') {
    return { key: header, label: header, sortable: true, index };
  }

  return {
    ...header,
    key: header.key ?? index,
    label: header.label ?? header.key ?? '',
    sortable: header.sortable !== false,
    index,
  };
}

function cellValue(row, header) {
  if (typeof header.value === 'function') return header.value(row);
  return row?.[header.key];
}

function compareValues(left, right) {
  if (left == null && right == null) return 0;
  if (left == null) return 1;
  if (right == null) return -1;
  if (typeof left === 'number' && typeof right === 'number') return left - right;
  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
}

export function dataTableHTML({
  headers = [],
  rows = [],
  id = '',
  caption = '',
  sortBy = null,
  sortDirection = 'asc',
  emptyMessage = 'No data yet',
  rowClass = null,
} = {}) {
  const columns = headers.map(normalizeHeader);
  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
  const sortedRows = [...rows];

  if (sortColumn) {
    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
    const multiplier = direction === 'desc' ? -1 : 1;
    sortedRows.sort((left, right) => multiplier * compare(
      cellValue(left, sortColumn),
      cellValue(right, sortColumn),
      left,
      right,
    ));
  }

  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
  const sortAttributes = sortColumn
    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
    : '';
  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
  const headerHTML = columns.map(column => {
    const sortableAttributes = column.sortable
      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
      : '';
    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
    return `<th scope="col"${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
  }).join('');
  const rowsHTML = sortedRows.map((row, rowIndex) => {
    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
    const cells = columns.map(column => {
      const value = cellValue(row, column);
      const content = typeof column.render === 'function'
        ? column.render(value, row, rowIndex)
        : escapeHtml(value);
      return `<td>${content ?? ''}</td>`;
    }).join('');
    return `<tr${classAttribute}>${cells}</tr>`;
  }).join('');
  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;

  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
}
