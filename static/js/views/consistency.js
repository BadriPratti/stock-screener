import { emptyStateHTML } from '../components/empty-state.js';
import { fetchJSON } from '../core/api.js';
import { consistencyCaptionText, formatSessionDate } from '../core/pick-history.js';
import { content, currentView, pageMeta } from '../core/state.js';
import { escapeHtml } from '../core/ui-helpers.js';

const COLUMNS = [
  ['ticker', 'Ticker'],
  ['appearances', 'Appearances'],
  ['currentStreak', 'Current streak'],
  ['longestStreak', 'Longest streak'],
  ['firstSeen', 'First seen'],
  ['lastSeen', 'Last seen'],
  ['bestRank', 'Best rank'],
  ['averageRank', 'Avg rank'],
  ['averageScore', 'Avg score'],
  ['scoreChange', 'Score change'],
  ['statusText', 'Status'],
];

const EMPTY_MESSAGE = 'History builds up one entry per daily scan.';
let requestSequence = 0;
let displayedSort = { key: 'appearances', direction: 'descending' };

function finiteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function roundedPercent(appearances, denominator, appearanceRate) {
  if (appearances !== null && denominator !== null && denominator > 0) {
    return Math.round((appearances / denominator) * 100);
  }
  const rate = finiteNumber(appearanceRate);
  return rate === null ? null : Math.round(rate * 100);
}

function formattedNumber(value) {
  return value === null ? '-' : String(Number(value.toFixed(2)));
}

function formattedScoreChange(value) {
  if (value === null) return '-';
  const formatted = formattedNumber(value);
  return value > 0 ? `+${formatted}` : formatted;
}

export function buildLeaderboardRows(history) {
  if (!historyIsUsable(history)) return [];

  const rows = Object.entries(history.tickers).map(([ticker, stat]) => {
    const safeStat = stat && typeof stat === 'object' ? stat : {};
    const appearances = finiteNumber(safeStat.appearances);
    const denominator = finiteNumber(safeStat.denominator) ?? finiteNumber(history.denominator);
    const percent = roundedPercent(appearances, denominator, safeStat.appearance_rate);
    const currentStreak = finiteNumber(safeStat.current_streak);
    const longestStreak = finiteNumber(safeStat.longest_streak);
    const bestRank = finiteNumber(safeStat.best_rank);
    const averageRank = finiteNumber(safeStat.average_rank);
    const averageScore = finiteNumber(safeStat.average_score);
    const scoreChange = finiteNumber(safeStat.score_delta);
    const firstSeen = typeof safeStat.first_seen === 'string' ? safeStat.first_seen : null;
    const lastSeen = typeof safeStat.last_seen === 'string' ? safeStat.last_seen : null;
    const isActiveToday = safeStat.is_active_today === true;

    return {
      ticker: String(ticker),
      appearances,
      denominator,
      percent,
      appearancesText: appearances === null || denominator === null || percent === null
        ? '-'
        : `${appearances}/${denominator} (${percent}%)`,
      currentStreak,
      longestStreak,
      firstSeen,
      firstSeenText: firstSeen ? formatSessionDate(firstSeen) : '-',
      lastSeen,
      lastSeenText: lastSeen ? formatSessionDate(lastSeen) : '-',
      bestRank,
      bestRankText: bestRank === null ? '-' : `#${bestRank}`,
      averageRank,
      averageRankText: formattedNumber(averageRank),
      averageScore,
      averageScoreText: formattedNumber(averageScore),
      scoreChange,
      scoreChangeText: formattedScoreChange(scoreChange),
      isActiveToday,
      statusText: isActiveToday ? 'On latest scan' : 'Dropped out',
    };
  });
  return defaultLeaderboardOrder(rows);
}

function compareValues(a, b, direction) {
  const aMissing = a === null || a === undefined;
  const bMissing = b === null || b === undefined;
  if (aMissing || bMissing) {
    if (aMissing && bMissing) return 0;
    return aMissing ? 1 : -1;
  }
  const comparison = typeof a === 'string' || typeof b === 'string'
    ? String(a).localeCompare(String(b))
    : a - b;
  return direction === 'descending' || direction === 'desc' || direction === -1
    ? -comparison
    : comparison;
}

export function sortLeaderboardRows(rows, key, direction = 'ascending') {
  const safeRows = Array.isArray(rows) ? rows : [];
  return safeRows
    .map((row, index) => ({ row, index }))
    .sort((left, right) => {
      const comparison = compareValues(left.row?.[key], right.row?.[key], direction);
      return comparison || left.index - right.index;
    })
    .map(entry => entry.row);
}

function defaultLeaderboardOrder(rows) {
  return [...rows].sort((a, b) =>
    compareValues(a.appearances, b.appearances, 'descending')
    || compareValues(a.currentStreak, b.currentStreak, 'descending')
    || compareValues(a.averageRank, b.averageRank, 'ascending')
    || compareValues(a.ticker, b.ticker, 'ascending'));
}

function emptyHistoryHTML() {
  return emptyStateHTML({ title: 'No pick history yet', message: EMPTY_MESSAGE });
}

function historyIsUsable(history) {
  const validRoot = history
    && typeof history === 'object'
    && (history.list === 'shortlist' || history.list === 'top20')
    && Number.isInteger(history.sessions_available)
    && history.sessions_available >= 0
    && Array.isArray(history.sessions)
    && Number.isInteger(history.denominator)
    && history.denominator >= 0
    && history.tickers
    && typeof history.tickers === 'object'
    && !Array.isArray(history.tickers);
  if (!validRoot) return false;
  return Object.values(history.tickers).every(stat => stat
    && typeof stat === 'object'
    && finiteNumber(stat.appearances) !== null
    && finiteNumber(stat.denominator) !== null
    && finiteNumber(stat.current_streak) !== null
    && finiteNumber(stat.longest_streak) !== null
    && typeof stat.first_seen === 'string'
    && typeof stat.last_seen === 'string'
    && typeof stat.is_active_today === 'boolean');
}

function notesHTML(history) {
  const lines = [];
  const gaps = Array.isArray(history.coverage_gaps) ? history.coverage_gaps : [];
  if (gaps.length) {
    const first = gaps[0] || {};
    const gapWord = gaps.length === 1 ? 'gap' : 'gaps';
    let detail = '';
    if (first.after && first.before) {
      detail = `: no scan between ${formatSessionDate(first.after)} and ${formatSessionDate(first.before)}`;
    }
    const more = gaps.length > 1 ? `; ${gaps.length - 1} more` : '';
    lines.push(`${gaps.length} ${gapWord} in the record${detail}${more} (missing weekdays are informational, streaks are not affected)`);
  }
  if (Array.isArray(history.warnings)) lines.push(...history.warnings.map(String));
  return lines.map(line => `<div class="consistency-note">${escapeHtml(line)}</div>`).join('');
}

function tableHTML(rows) {
  const headers = COLUMNS.map(([key, label]) => {
    const active = key === displayedSort.key;
    const ariaSort = active ? displayedSort.direction : 'none';
    return `<th scope="col" data-key="${key}" role="button" tabindex="0" aria-sort="${ariaSort}">${label}</th>`;
  }).join('');
  return `<div class="consistency-table-wrap"><table class="signal-table consistency-table" id="consistencyTable">
    <caption>Stock consistency leaderboard</caption>
    <thead><tr>${headers}</tr></thead>
    <tbody>${tableRowsHTML(rows)}</tbody>
  </table></div>`;
}

function tableRowsHTML(rows) {
  return rows.map(row => `<tr class="${row.isActiveToday ? '' : 'consistency-dropped'}">
    <td><span class="ticker">${escapeHtml(row.ticker)}</span></td>
    <td>${escapeHtml(row.appearancesText)}</td>
    <td>${escapeHtml(row.currentStreak ?? '-')}</td>
    <td>${escapeHtml(row.longestStreak ?? '-')}</td>
    <td>${escapeHtml(row.firstSeenText)}</td>
    <td>${escapeHtml(row.lastSeenText)}</td>
    <td>${escapeHtml(row.bestRankText)}</td>
    <td>${escapeHtml(row.averageRankText)}</td>
    <td>${escapeHtml(row.averageScoreText)}</td>
    <td>${escapeHtml(row.scoreChangeText)}</td>
    <td>${escapeHtml(row.statusText)}</td>
  </tr>`).join('');
}

function wireSorting(rows) {
  const table = document.getElementById('consistencyTable');
  if (!table) return;
  const headers = table.querySelectorAll('th[data-key]');
  const applySort = (header) => {
    const key = header.dataset.key;
    const direction = displayedSort.key === key && displayedSort.direction === 'ascending'
      ? 'descending'
      : 'ascending';
    displayedSort = { key, direction };
    const sorted = sortLeaderboardRows(rows, key, direction);
    const body = table.querySelector('tbody');
    if (body) body.innerHTML = tableRowsHTML(sorted);
    headers.forEach(item => item.setAttribute(
      'aria-sort',
      item === header ? direction : 'none',
    ));
  };

  headers.forEach(header => {
    header.addEventListener('click', () => applySort(header));
    header.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        applySort(header);
      }
    });
  });
}

function renderHistory(history, results) {
  if (!historyIsUsable(history) || history.sessions_available === 0) {
    pageMeta.textContent = '';
    results.innerHTML = emptyHistoryHTML();
    return;
  }

  const rows = buildLeaderboardRows(history);
  if (!rows.length) {
    pageMeta.textContent = history.latest_session_date ? `Through ${history.latest_session_date}` : '';
    results.innerHTML = emptyHistoryHTML();
    return;
  }

  displayedSort = { key: 'appearances', direction: 'descending' };
  const sorted = rows;
  pageMeta.textContent = history.latest_session_date ? `Through ${history.latest_session_date}` : '';
  results.innerHTML = `
    <div class="consistency-caption">${escapeHtml(consistencyCaptionText(history))}</div>
    ${notesHTML(history)}
    ${tableHTML(sorted)}`;
  wireSorting(rows);
}

async function loadLeaderboard() {
  const sequence = ++requestSequence;
  const list = document.getElementById('consistencyList')?.value || 'shortlist';
  const windowSize = document.getElementById('consistencyWindow')?.value || '5';
  const results = document.getElementById('consistencyResults');
  if (!results) return;
  results.setAttribute('aria-busy', 'true');

  try {
    const history = await fetchJSON(`/api/pick-history?list=${encodeURIComponent(list)}&window=${encodeURIComponent(windowSize)}`);
    if (currentView !== 'consistency' || sequence !== requestSequence) return;
    results.removeAttribute('aria-busy');
    renderHistory(history, results);
  } catch {
    if (currentView !== 'consistency' || sequence !== requestSequence) return;
    results.removeAttribute('aria-busy');
    pageMeta.textContent = '';
    results.innerHTML = emptyHistoryHTML();
  }
}

export async function renderConsistencyView() {
  content.innerHTML = `
    <div class="consistency-controls">
      <label for="consistencyList">List</label>
      <select class="scan-select" id="consistencyList">
        <option value="shortlist">Shortlist</option>
        <option value="top20">Top 20</option>
      </select>
      <label for="consistencyWindow">Window</label>
      <select class="scan-select" id="consistencyWindow">
        <option value="5">5 scans</option>
        <option value="10">10 scans</option>
        <option value="20">20 scans</option>
      </select>
    </div>
    <div id="consistencyResults" aria-live="polite"></div>`;

  document.getElementById('consistencyList').addEventListener('change', loadLeaderboard);
  document.getElementById('consistencyWindow').addEventListener('change', loadLeaderboard);
  await loadLeaderboard();
}
