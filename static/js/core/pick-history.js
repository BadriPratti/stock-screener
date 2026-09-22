import { fetchJSON } from './api.js';

const LIST_NOUN = { shortlist: 'the Shortlist', top20: 'the Top 20' };
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function esc(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function plural(n, word) {
  return `${n} ${word}${n === 1 ? '' : 's'}`;
}

// Parsed from the string, not via Date, so a YYYY-MM-DD session date can never
// shift a day under the viewer's timezone.
export function formatSessionDate(iso) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso ?? ''));
  if (!match) return String(iso ?? '');
  return `${MONTHS[Number(match[2]) - 1]} ${Number(match[3])}`;
}

export function consistencyTooltip(stat, history) {
  const noun = LIST_NOUN[history.list] || 'this list';
  const parts = [
    `On ${noun} in ${stat.appearances} of the last ${plural(stat.denominator, 'recorded scan')}.`,
  ];
  if (stat.current_streak >= 1) parts.push(`Current streak: ${plural(stat.current_streak, 'scan')}.`);
  parts.push(`Best rank #${stat.best_rank}.`);
  if (stat.history && stat.history.length) {
    parts.push(stat.history.map(h => `${formatSessionDate(h.date)} #${h.rank}`).join(' · '));
  }
  return parts.join(' ');
}

export function consistencyBadgeHTML(stat, history) {
  if (!history || !history.sessions_available) return '';
  if (!stat) {
    return `<span class="consistency-badges"><span class="badge neutral" title="${esc(absentTooltip(history))}">Not on record</span></span>`;
  }
  const badges = [
    `<span class="badge frequency">${stat.appearances}/${stat.denominator} scans</span>`,
  ];
  if (stat.current_streak >= 2) {
    badges.push(`<span class="badge streak">${stat.current_streak}-scan streak</span>`);
  }
  if (stat.total_appearances === 1 && stat.is_active_today) {
    badges.push('<span class="badge new-pick">New</span>');
  }
  return `<span class="consistency-badges" title="${esc(consistencyTooltip(stat, history))}">${badges.join('')}</span>`;
}

function absentTooltip(history) {
  const noun = LIST_NOUN[history.list] || 'this list';
  return `Not on ${noun} in the last ${plural(history.denominator, 'recorded scan')}, or the history is behind the latest scan.`;
}

// The denominator is always the number of scans actually recorded, never the
// requested window: with a short ledger a "last 20" view must not read as 20.
export function consistencyCaptionText(history) {
  if (!history || !history.sessions_available) {
    return 'Consistency history starts after the first recorded daily scan.';
  }
  const sessions = history.sessions || [];
  const span = sessions.length > 1
    ? `${formatSessionDate(sessions[0])} - ${formatSessionDate(sessions[sessions.length - 1])}`
    : formatSessionDate(sessions[0]);
  let text = `Consistency: last ${plural(history.denominator, 'recorded scan')} (${span}), through ${history.latest_session_date}.`;
  if (history.denominator < history.window_requested) {
    text += ` Only ${plural(history.sessions_available, 'scan')} on record so far.`;
  }
  const skipped = (history.warnings || []).filter(w => String(w).startsWith('Skipped')).length;
  if (skipped) text += ` ${plural(skipped, 'history file')} skipped as unreadable.`;
  return text;
}

export function paintConsistencySlots(tickers, history) {
  if (!history || !history.tickers) return;
  tickers.forEach(ticker => {
    const slot = document.getElementById(`consistency-slot-${history.list}-${ticker}`);
    if (slot) slot.innerHTML = consistencyBadgeHTML(history.tickers[ticker], history);
  });
  const caption = document.getElementById(`consistency-caption-${history.list}`);
  if (caption) caption.textContent = consistencyCaptionText(history);
}

// Non-critical enhancement: a failed or missing history must never affect the
// view that asked for it, so every failure resolves to null instead of throwing.
export async function loadConsistency(tickers, list, window = 5) {
  if (!tickers.length) return null;
  try {
    const history = await fetchJSON(`/api/pick-history?list=${encodeURIComponent(list)}&window=${window}`);
    if (!history || !history.tickers || history.list !== list) return null;
    paintConsistencySlots(tickers, history);
    return history;
  } catch {
    return null;
  }
}
