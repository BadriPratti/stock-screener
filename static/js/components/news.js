import { startJob } from '../core/jobs.js';
import { fetchJSON } from '../core/api.js';
import { liveBadgeHTML } from '../core/refresh.js';
import { escapeHtml, safeHref } from '../core/ui-helpers.js';

// Per-ticker expand/collapse state lives here, keyed by "group:ticker" — NOT
// in the DOM (a `hidden` attribute or inline style) or as function args,
// because the 90-second live-refresh tick fully replaces each group's
// innerHTML. Anything the user has expanded would silently collapse under
// them mid-read on every tick without this being tracked outside the DOM.
const _expandedTickers = new Set();
const HEADLINE_LIMIT = 2;

function _parsedTime(pubDate) {
  const t = pubDate ? Date.parse(pubDate) : NaN;
  return Number.isNaN(t) ? null : t;
}

// Newest-first; missing/invalid dates sort after every valid date but keep
// their original relative order among themselves and each other (a plain
// `(a,b) => timeB - timeA` would push nulls to NaN-driven arbitrary
// positions instead).
function _sortByRecency(headlines) {
  const withIndex = headlines.map((h, i) => ({ h, i, t: _parsedTime(h.pub_date) }));
  withIndex.sort((a, b) => {
    if (a.t == null && b.t == null) return a.i - b.i;
    if (a.t == null) return 1;
    if (b.t == null) return -1;
    return b.t - a.t;
  });
  return withIndex.map(x => x.h);
}

// Drops obviously-malformed entries and de-duplicates by canonical URL
// (falling back to a normalized title when a URL is missing) — Yahoo's feed
// occasionally repeats the same story under a syndicated title variant.
function _dedupeHeadlines(headlines) {
  const seen = new Set();
  const out = [];
  for (const h of headlines) {
    if (!h || !h.title) continue;
    const key = h.url || h.title.trim().toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(h);
  }
  return out;
}

function _relativeTime(pubDate) {
  const t = _parsedTime(pubDate);
  if (t == null) return null;
  const diffMs = Date.now() - t;
  const hours = diffMs / 36e5;
  if (hours < 1) return 'just now';
  if (hours < 24) return `${Math.round(hours)}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(t).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function _headlineRowHTML(h) {
  const isSafe = safeHref(h.url) !== '#';
  const meta = [escapeHtml(h.publisher || 'Unknown source'), _relativeTime(h.pub_date)].filter(Boolean).join(' · ');
  const title = `<div class="news-headline-title">${escapeHtml(h.title)}</div><div class="news-headline-meta">${meta}</div>`;
  return isSafe
    ? `<a href="${safeHref(h.url)}" target="_blank" rel="noopener" class="news-headline">${title}</a>`
    : `<div class="news-headline news-headline-nolink">${title}</div>`;
}

function _tickerCardHTML(group, ticker, headlines) {
  const key = `${group}:${ticker}`;
  const cleaned = _sortByRecency(_dedupeHeadlines(headlines || []));
  if (!cleaned.length) {
    return `<div class="news-ticker-block"><div class="ticker" style="margin-bottom:6px">${escapeHtml(ticker)}</div>
      <div style="color:var(--muted);font-size:12px">No recent headlines.</div></div>`;
  }
  const visible = cleaned.slice(0, HEADLINE_LIMIT);
  const extra = cleaned.slice(HEADLINE_LIMIT);
  const expanded = _expandedTickers.has(key);
  const extraHTML = extra.length
    ? `<div class="news-extra" ${expanded ? '' : 'hidden'} id="news-extra-${escapeHtml(key)}">${extra.map(_headlineRowHTML).join('')}</div>
       <button type="button" class="expand-btn" data-news-toggle="${escapeHtml(key)}" data-extra-count="${extra.length}"
         aria-expanded="${expanded}" aria-controls="news-extra-${escapeHtml(key)}">${expanded ? 'Show less' : `+${extra.length} more`}</button>`
    : '';
  return `<div class="news-ticker-block"><div class="ticker" style="margin-bottom:6px">${escapeHtml(ticker)}</div>
    ${visible.map(_headlineRowHTML).join('')}${extraHTML}</div>`;
}

// tickers (not just Object.keys(newsByTicker)) drives which cards render and
// in what order — a ticker the API omitted from its response still gets an
// empty-state card instead of silently vanishing, and Shortlist's rank order
// is preserved rather than however the API happened to key its object.
export function renderNewsGroupHTML(group, tickers, newsByTicker) {
  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
  return `<div class="news-ticker-grid">${tickers.map(ticker =>
    _tickerCardHTML(group, ticker, (newsByTicker || {})[ticker])
  ).join('')}</div>`;
}

export function newsSectionHTML(group, title, bodyHTML) {
  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
}

// One delegated listener per group body — the expand/collapse buttons are
// re-created on every render (job success, or a silent refresh), so binding
// directly to them would leak listeners and miss ones added after a refresh.
const _wiredGroups = new Set();
function _wireToggleDelegation(group) {
  if (_wiredGroups.has(group)) return;
  _wiredGroups.add(group);
  const el = document.getElementById(`news-${group}-body`);
  if (!el) { _wiredGroups.delete(group); return; }
  el.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-news-toggle]');
    if (!btn) return;
    const key = btn.dataset.newsToggle;
    const extraEl = document.getElementById(`news-extra-${key}`);
    const nowExpanded = !_expandedTickers.has(key);
    if (nowExpanded) _expandedTickers.add(key); else _expandedTickers.delete(key);
    if (extraEl) extraEl.hidden = !nowExpanded;
    btn.setAttribute('aria-expanded', String(nowExpanded));
    btn.textContent = nowExpanded ? 'Show less' : `+${btn.dataset.extraCount} more`;
  });
}

export async function loadNewsGroup(group, tickers, emptyMsg, silent) {
  const bodyEl = document.getElementById(`news-${group}-body`);
  if (!bodyEl) return; // navigated away before this resolved
  if (!silent) {
    // A fresh (non-silent) view load starts every ticker collapsed — carrying
    // expand state across an intentional full reload (as opposed to the
    // background 90s tick) would be surprising, not helpful.
    for (const key of Array.from(_expandedTickers)) {
      if (key.startsWith(`${group}:`)) _expandedTickers.delete(key);
    }
  }
  if (!tickers.length) {
    bodyEl.innerHTML = `<div style="color:var(--muted);font-size:13px">${emptyMsg}</div>`;
    return;
  }
  if (!silent) {
    bodyEl.innerHTML = '<div style="color:var(--muted);font-size:13px"><span class="spinner"></span> Fetching real headlines…</div>';
  }

  await startJob('news', { tickers, group }, async (st) => {
    const el = document.getElementById(`news-${group}-body`);
    if (!el) return; // navigated away mid-job
    if (st.status === 'success') {
      const data = await fetchJSON(`/api/news/${group}`);
      el.innerHTML = renderNewsGroupHTML(group, tickers, data.news || {});
      _wireToggleDelegation(group);
    } else if (!silent && (st.status === 'error' || st.status === 'stopped')) {
      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
    }
  });
}
