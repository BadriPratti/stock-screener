// Stock Screener dashboard — vanilla JS single-page app. Hash-based routing
// (no router library), fetch() for data, Chart.js (via charts.js) for charts.

const content = document.getElementById('content');
const pageTitle = document.getElementById('pageTitle');
const pageMeta = document.getElementById('pageMeta');

const VIEWS = {
  positions: { title: 'Positions', render: renderPositionsView },
  shortlist: { title: 'Shortlist', render: renderShortlistView },
  market: { title: 'Market', render: renderMarketView },
  backtests: { title: 'Backtests', render: renderBacktestsView },
  run: { title: 'Run Simulation', render: renderRunView },
  scan: { title: 'Full Scan', render: renderScanView },
};

// Tracks which view is actually on screen right now. View render functions
// are async — if you navigate away while one is still awaiting its first
// fetch, that stale call resolves later and, without this check, would paint
// its (now-irrelevant) content over whatever view you've since navigated to.
// Every render function checks `_currentView === '<its own name>'` right
// after each await, before touching pageMeta/content, and bails out silently
// if it's lost the race.
let _currentView = null;

function route() {
  _stopLive();
  const hash = (location.hash || '#/positions').replace('#/', '');
  const view = VIEWS[hash] ? hash : 'positions';
  _currentView = view;
  document.querySelectorAll('.nav-item').forEach(a => {
    a.classList.toggle('active', a.dataset.view === view);
  });
  pageTitle.textContent = VIEWS[view].title;
  pageMeta.innerHTML = '';
  content.innerHTML = '<div class="no-data"><span class="spinner"></span> Loading…</div>';
  VIEWS[view].render();
}
window.addEventListener('hashchange', route);

// --- "Live" auto-refresh -------------------------------------------------
// This is a local, single-user Flask app with no push/streaming layer, so
// "live" here means: while a view that supports it is open, quietly re-pull
// fresh data on a timer and patch it into the DOM. Stopped on every route
// change so a background view never keeps polling once you've navigated away.

const LIVE_INTERVAL_MS = 90 * 1000; // 90 seconds — cheap yfinance-only pulls, no LLM cost
let _liveTimer = null;

function _stopLive() {
  if (_liveTimer) { clearInterval(_liveTimer); _liveTimer = null; }
}
function _startLive(fn) {
  _stopLive();
  _liveTimer = setInterval(fn, LIVE_INTERVAL_MS);
}
function liveBadgeHTML() {
  return '<span class="live-badge"><span class="live-dot"></span>Live — updates every 90s</span>';
}

// If a live-refresh tick's job hasn't finished by the time the next tick
// fires (e.g. yfinance is slow), skip that tick instead of stacking another
// overlapping job on top — the next one will pick up fresh data anyway.
const _liveInFlight = new Set();
async function _liveGuarded(key, fn) {
  if (_liveInFlight.has(key)) return;
  _liveInFlight.add(key);
  try {
    await fn();
  } finally {
    _liveInFlight.delete(key);
  }
}

// Chart toggle buttons (Positions + Shortlist share this). Open/closed state
// persists in this module-level set across re-renders and silent refreshes,
// keyed by the canvas element id, so a chart you had open stays open through
// a live refresh instead of collapsing every cycle.
const CHART_ICON = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 6"/><polyline points="15 6 21 6 21 12"/></svg>';
const _openCharts = new Set();

function chartToggleButtonHTML(chartId) {
  return `<button class="chart-toggle-btn" data-chart-id="${chartId}" title="Price history">${CHART_ICON}</button>`;
}

// getSeries(ticker) -> {history, entry, stop} | null. Attaches click handlers
// (call once per DOM render) and immediately re-opens any chart that was
// already open before this render (e.g. across a live refresh).
function wireChartToggles(container, getSeries, idPrefix) {
  container.querySelectorAll('.chart-toggle-btn').forEach(btn => {
    const chartId = btn.dataset.chartId;
    const wrap = document.getElementById(`${chartId}-wrap`);
    if (!wrap) return;
    const ticker = chartId.slice(idPrefix.length);

    if (_openCharts.has(chartId)) {
      wrap.style.display = 'block';
      btn.classList.add('active');
      const series = getSeries(ticker);
      if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
    }

    btn.addEventListener('click', () => {
      const nowVisible = wrap.style.display !== 'block';
      wrap.style.display = nowVisible ? 'block' : 'none';
      btn.classList.toggle('active', nowVisible);
      if (nowVisible) {
        _openCharts.add(chartId);
        const series = getSeries(ticker);
        if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
      } else {
        _openCharts.delete(chartId);
      }
    });
  });
}

// For a silent live refresh where the cards themselves aren't re-rendered
// (Shortlist) — just repaint whichever charts are currently open with fresh data.
function refreshOpenCharts(getSeries, idPrefix) {
  _openCharts.forEach(chartId => {
    if (!chartId.startsWith(idPrefix)) return;
    if (!document.getElementById(`${chartId}-wrap`)) return; // stale id from a different view
    const ticker = chartId.slice(idPrefix.length);
    const series = getSeries(ticker);
    if (series) renderPositionChart(chartId, series.history, series.entry, series.stop);
  });
}

// --- Momentum status (hot / stable / basing / avoid) + day-streak --------
// Shared across Shortlist, Positions, and Market — same classification the
// screening engine itself uses (Phase + distance from the 50-day average),
// so a badge here always means the same thing it means in a scan report.

const MOMENTUM_LABELS = { hot: 'HOT', stable: 'STABLE', basing: 'BASING', avoid: 'AVOID' };

function momentumBadgeHTML(entry) {
  if (!entry || !entry.status) return '';
  const label = MOMENTUM_LABELS[entry.status] || entry.status.toUpperCase();
  const dayWord = entry.days === 1 ? 'day' : 'days';
  return `<span class="momentum-badge ${entry.status}" title="${entry.label} — ${entry.days} ${dayWord}">${label}<span class="streak">Day ${entry.days}</span></span>`;
}

// Injects a badge into a per-ticker slot element (id="momentum-slot-<ticker>")
// once the classification job completes. Call after slots exist in the DOM.
async function loadMomentumStatus(tickers, group, onLoaded) {
  if (!tickers.length) return;
  await startJob('momentum-status', { tickers, group }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON(`/api/momentum-status/${group}`);
    onLoaded(data.status || {});
  });
}

function paintMomentumSlots(tickers, statusMap) {
  tickers.forEach(ticker => {
    const slot = document.getElementById(`momentum-slot-${ticker}`);
    if (slot && statusMap[ticker]) slot.innerHTML = momentumBadgeHTML(statusMap[ticker]);
  });
}

// --- Shared helpers -----------------------------------------------------

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  return res.json();
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.opacity = '1';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.opacity = '0'; }, 5000);
}

function redditCell(count) {
  if (count == null) return '<span style="color:var(--muted)">-</span>';
  if (count === 0) return '<span style="color:var(--muted)">0</span>';
  const hot = count >= 10;
  return `<span style="color:${hot ? 'var(--yellow)' : 'var(--text)'};font-weight:${hot ? 700 : 400}">${count}</span>`;
}

function cleanEmoji(text) {
  return (text || '').replace(/[🟢🔴🟡⭐⚠✓🚨]/g, '').trim();
}

// Escapes free text before it's interpolated into innerHTML. Needed anywhere
// the string didn't originate from this codebase — news headlines/publishers
// (raw Yahoo Finance feed data), and LLM-generated summaries/flags (ultimately
// derived from external filings/press) — a crafted string containing HTML
// could otherwise execute JS in the dashboard's own origin, which has several
// unauthenticated routes (sync, scan, positions upload).
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text == null ? '' : String(text);
  return div.innerHTML;
}

// Only allow http(s) URLs as link targets — a "javascript:" (or other
// executable) scheme in externally-sourced data (e.g. a news item's URL)
// would otherwise run when clicked, same class of risk as the innerHTML issue.
function safeHref(url) {
  try {
    const parsed = new URL(url, location.href);
    return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '#';
  } catch {
    return '#';
  }
}

function toggleReasons(btn) {
  const extra = btn.previousElementSibling;
  if (extra.style.display === 'none') {
    extra.style.display = '';
    btn.textContent = 'less';
  } else {
    extra.style.display = 'none';
  }
}

function fidelityLink(ticker, label, cls) {
  return `<a class="trade-link ${cls}" href="https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry?symbol=${ticker}" target="_blank" rel="noopener">${label} ↗</a>`;
}

// Agent badges — same color logic as src/notifications/email_notifier.py
// (_catalyst_badge_html / _congress_badge_html / _fundamentals_flags_html) so
// the dashboard and the email read consistently.

function catalystBadgeHTML(sentiment) {
  if (!sentiment) return '';
  const score = sentiment.catalyst_score || 0;
  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
  const ctype = (sentiment.catalyst_type || 'other').replace(/_/g, ' ');
  const sign = score > 0 ? '+' : '';
  return `<div><span class="agent-badge ${cls}">Catalyst ${sign}${score} — ${escapeHtml(ctype)}</span>
    <div class="agent-badge-sub">${escapeHtml(sentiment.summary)}</div></div>`;
}

function congressBadgeHTML(signal) {
  if (!signal || !signal.has_data) return '';
  const score = signal.score || 0;
  const cls = score > 0 ? 'pos' : score < 0 ? 'neg' : 'neu';
  const sign = score > 0 ? '+' : '';
  return `<div><span class="agent-badge ${cls}">Congress ${sign}${score.toFixed(1)}</span>
    <div class="agent-badge-sub">${escapeHtml(signal.summary)}</div></div>`;
}

function fundamentalsFlagsHTML(audit) {
  if (!audit) return '';
  const red = audit.red_flags || [];
  const green = audit.green_flags || [];
  let html = '';
  if (red.length) {
    const more = red.length > 1 ? ` (+${red.length - 1} more)` : '';
    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${escapeHtml(red[0].flag)}${more}</div>`;
  }
  if (green.length) {
    const more = green.length > 1 ? ` (+${green.length - 1} more)` : '';
    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
  }
  return html;
}

// --- Background job runner (Run Simulation / Full Scan views) ----------

// Resolves only once the job reaches a terminal state (success/error/stopped),
// not right after it starts — every caller does `await startJob(...)` expecting
// that to mean "the job is done," and several (via _liveGuarded) depend on it
// to know when it's safe to start the next refresh cycle. It used to resolve
// as soon as the initial POST came back, which silently defeated that guard.
async function startJob(kind, body, onUpdate) {
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

function jobCardHTML(id, title, desc, paramsHTML) {
  return `
    <div class="card sim-card">
      <h2>${title} <span class="status-pill idle" id="${id}-pill">idle</span></h2>
      <div class="sim-desc">${desc}</div>
      <div class="sim-params">${paramsHTML}</div>
      <button class="btn primary" id="${id}-run">Run</button>
      <div class="job-output" id="${id}-output"></div>
      <div id="${id}-result" style="margin-top:12px"></div>
    </div>`;
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

function watchJob(id, jobId, onResult) {
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

function wireJobCard(id, kind, getParams, onResult) {
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

// --- View: Shortlist (default landing view) -----------------------------

async function renderShortlistView() {
  const data = await fetchJSON('/api/shortlist');
  if (_currentView !== 'shortlist') return; // navigated away before this resolved
  if (!data.shortlist || data.shortlist.length === 0) {
    const top20 = await fetchJSON('/api/top20');
    if (_currentView !== 'shortlist') return;
    content.innerHTML = `
      <div class="banner">
        No filtered shortlist yet — run a scan with AI agents enabled from the
        <a href="#/scan">Full Scan</a> page to get a Top 5 filtered by fundamentals,
        news sentiment, and congressional trading. Showing the raw Top 20 pool below instead.
      </div>
      ${renderTop20Table(top20.top20 || [])}
    `;
    const fallbackTickers = (top20.top20 || []).map(s => s.ticker);
    loadMomentumStatus(fallbackTickers, 'shortlist-fallback', (statusMap) => paintMomentumSlots(fallbackTickers, statusMap));
    return;
  }
  pageMeta.textContent = data.generated ? `Generated ${new Date(data.generated).toLocaleString()}` : '';

  const tickers = data.shortlist.map(s => s.ticker);

  const cards = data.shortlist.map((s, i) => {
    const badges = [
      catalystBadgeHTML(data.catalyst_sentiments[s.ticker]),
      congressBadgeHTML(data.congress_signals[s.ticker]),
      fundamentalsFlagsHTML(data.fundamentals_audits[s.ticker]),
    ].filter(Boolean).join('');
    const backfillNote = !s.passed_filters
      ? `<div class="backfill-note">Backfilled — didn't clear filters: ${(s.drop_reasons || []).join('; ') || 'below filter bar'}</div>`
      : '';
    const chartId = `short-chart-${s.ticker}`;
    return `
      <div class="pick-card ${!s.passed_filters ? 'backfilled' : ''}">
        <div class="pick-rank">#${i + 1}</div>
        <div class="pick-header">
          <span class="ticker">${s.ticker}</span>
          <span id="${chartId}-slot"></span>
        </div>
        <div class="pick-scores">
          <div class="score-block"><div class="label">Composite</div><div class="value">${s.composite_score ?? '-'}</div></div>
          <div class="score-block"><div class="label">Base Score</div><div class="value">${s.combined_score ?? s.score ?? '-'}</div></div>
        </div>
        <div style="margin-bottom:10px"><span id="momentum-slot-${s.ticker}"></span></div>
        ${backfillNote}
        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
        ${fidelityLink(s.ticker, 'Buy on Fidelity', 'buy')}
        <div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>
      </div>`;
  }).join('');

  content.innerHTML = `
    <div class="source-note email">
      <b>This is what your daily email sends.</b> Same 5 picks, same links — the email is just a snapshot of this page.
    </div>
    <div class="shortlist-grid">${cards}</div>
    <div id="shortlistNews" style="margin-top:24px"></div>`;

  loadShortlistCharts(tickers);
  loadShortlistNews(tickers);
  loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap));
  _startLive(() => {
    _liveGuarded('shortlist-charts', () => loadShortlistCharts(tickers, true));
    _liveGuarded('shortlist-news', () => loadShortlistNews(tickers, true));
    _liveGuarded('shortlist-momentum', () => loadMomentumStatus(tickers, 'shortlist', (statusMap) => paintMomentumSlots(tickers, statusMap)));
  });
}

let _shortlistPrices = {};
let _marketTop20Tickers = [];

function _shortlistSeries(ticker) {
  const h = _shortlistPrices[ticker];
  return h && h.length ? { history: h, entry: null, stop: null } : null;
}

async function loadShortlistCharts(tickers, silent) {
  if (!tickers.length) return;
  await startJob('price-history', { tickers, group: 'shortlist' }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON('/api/price-history/shortlist');
    _shortlistPrices = data.prices || {};

    if (!silent) {
      // First load: drop a chart button into each card that actually has history.
      tickers.forEach(ticker => {
        const slot = document.getElementById(`short-chart-${ticker}-slot`);
        if (slot && _shortlistPrices[ticker] && _shortlistPrices[ticker].length) {
          slot.innerHTML = chartToggleButtonHTML(`short-chart-${ticker}`);
        }
      });
      wireChartToggles(content, _shortlistSeries, 'short-chart-');
    } else {
      // Live refresh: buttons already exist — just repaint whichever are open.
      refreshOpenCharts(_shortlistSeries, 'short-chart-');
    }
  });
}

async function loadShortlistNews(tickers, silent) {
  const el = document.getElementById('shortlistNews');
  if (!el) return;
  if (!silent) {
    el.innerHTML = _newsSectionHTML('shortlist', 'News on your shortlist', 'loading');
  }
  await _loadNewsGroup('shortlist', tickers, 'No shortlist yet.', silent);
}

function renderTop20Table(top20) {
  if (!top20.length) return '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan from the Full Scan page.</p></div>';
  const rows = top20.map((s, i) => {
    const links = (s.why_links || []).slice(0, 3).map(l =>
      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
    ).join('');
    return `<tr>
      <td>#${i + 1}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td><span class="score-num">${s.combined_score ?? s.score ?? '-'}</span></td>
      <td><span id="momentum-slot-${s.ticker}"></span></td>
      <td>${redditCell(s.reddit_mentions_24h)}</td>
      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
    </tr>`;
  }).join('');
  return `
    <div class="card">
      <h2>Top 20 — Combined Pool</h2>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th>#</th><th>Ticker</th><th>Combined Score</th><th>Momentum</th><th>Reddit</th><th>Why it's moving</th><th>Trade</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;
}

// --- View: Market (today's Top 20 / Buy / Sell / regime) ---------------

async function renderMarketView() {
  const scans = await fetchJSON('/api/scans');
  if (_currentView !== 'market') return; // navigated away before this resolved
  if (!scans.length) {
    content.innerHTML = '<div class="no-data"><h2>No scan data yet</h2><p>Run a scan to get started.</p></div>';
    return;
  }
  content.innerHTML = `
    <div class="source-note email">
      <b>This is the full pool your email's picks are drawn from.</b> Buy/Sell Signals and the Top 20 table
      here are the same lists that get emailed (capped at 15 rows there; everything's shown here) — the
      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
    </div>
    <div style="margin-bottom:16px">
      <select class="scan-select" id="scanSelect"></select>
    </div>
    <div id="marketBody"></div>
    <div id="newsSections" style="margin-top:24px"></div>`;
  const sel = document.getElementById('scanSelect');
  scans.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.path;
    opt.textContent = s.date.replace('_', ' ');
    sel.appendChild(opt);
  });
  sel.addEventListener('change', () => loadMarketScan(sel.value));
  loadMarketScan(scans[0].path);
  loadMarketNews();
  _startLive(() => {
    _liveGuarded('market-news', () => loadMarketNews(true));
    _liveGuarded('market-momentum', () => loadMomentumStatus(
      _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
    ));
  });
}

async function loadMarketNews(silent) {
  const el = document.getElementById('newsSections');
  if (!el) return; // navigated away before this resolved
  if (!silent) {
    el.innerHTML = _newsSectionHTML('positions', 'News on your positions', 'loading') +
                    _newsSectionHTML('buy', "News on what the scanner's telling you to buy", 'loading');
  }

  const [positionsData, top20Data] = await Promise.all([
    fetchJSON('/api/positions'), fetchJSON('/api/top20'),
  ]);
  const positionTickers = (positionsData.position_analyses || []).map(a => a.ticker);
  const buyTickers = (top20Data.top20 || []).slice(0, 8).map(s => s.ticker);

  await Promise.all([
    _loadNewsGroup('positions', positionTickers, 'Upload your positions in the Positions tab to see news for them here.', silent),
    _loadNewsGroup('buy', buyTickers, 'No Top 20 pool yet — run a scan from the Full Scan tab first.', silent),
  ]);
}

function _newsSectionHTML(group, title, bodyHTML) {
  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
}

async function _loadNewsGroup(group, tickers, emptyMsg, silent) {
  const bodyEl = document.getElementById(`news-${group}-body`);
  if (!bodyEl) return; // navigated away before this resolved
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
      el.innerHTML = _renderNewsGroupHTML(data.news || {});
    } else if (!silent && (st.status === 'error' || st.status === 'stopped')) {
      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
    }
  });
}

function _renderNewsGroupHTML(newsByTicker) {
  const tickers = Object.keys(newsByTicker);
  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
  return `<div class="news-ticker-grid">${tickers.map(ticker => {
    const items = newsByTicker[ticker] || [];
    const list = items.length
      ? items.map(h => `
          <a href="${safeHref(h.url)}" target="_blank" rel="noopener" class="news-headline">
            <div class="news-headline-title">${escapeHtml(h.title)}</div>
            <div class="news-headline-meta">${escapeHtml(h.publisher || 'Unknown source')}${h.pub_date ? ' · ' + escapeHtml(new Date(h.pub_date).toLocaleDateString()) : ''}</div>
          </a>`).join('')
      : '<div style="color:var(--muted);font-size:12px">No recent headlines.</div>';
    return `<div class="news-ticker-block"><div class="ticker" style="margin-bottom:6px">${escapeHtml(ticker)}</div>${list}</div>`;
  }).join('')}</div>`;
}

async function loadMarketScan(path) {
  const [scan, top20] = await Promise.all([
    fetchJSON('/api/scan?path=' + encodeURIComponent(path)),
    fetchJSON('/api/top20'),
  ]);
  if (_currentView !== 'market') return; // navigated away before this resolved
  if (scan.error) {
    document.getElementById('marketBody').innerHTML = '<div class="no-data"><h2>No scan data</h2></div>';
    return;
  }
  pageMeta.textContent = `${scan.scan_date} · ${scan.stats.analyzed || '?'} analyzed · ${scan.regime}`;

  const buyCount = scan.stats.buy_count ?? scan.buy_signals.length;
  const sellCount = scan.stats.sell_count ?? scan.sell_signals.length;
  const topScore = scan.buy_signals.length ? scan.buy_signals[0].score : '-';
  const regimeClass = scan.regime.includes('RISK-ON') ? 'risk-on' : scan.regime.includes('RISK-OFF') ? 'risk-off' : 'transitional';

  document.getElementById('marketBody').innerHTML = `
    <div class="stats-row">
      <div class="stat-card green"><div class="label">Buy Signals</div><div class="value">${buyCount}</div><div class="sub">Phase 2 confirmed uptrends</div></div>
      <div class="stat-card red"><div class="label">Sell Signals</div><div class="value">${sellCount}</div><div class="sub">Phase 3/4 breakdowns</div></div>
      <div class="stat-card blue"><div class="label">Top Score</div><div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div><div class="sub">${scan.buy_signals.length ? scan.buy_signals[0].ticker : '-'}</div></div>
      <div class="stat-card"><div class="label">Universe</div><div class="value">${(scan.stats.analyzed || 0).toLocaleString()}</div><div class="sub">of ${(scan.stats.total_universe || 0).toLocaleString()} | ${scan.stats.processing_minutes || '?'} min</div></div>
      <div class="stat-card ${scan.spy.phase === 2 ? 'green' : scan.spy.phase === 4 ? 'red' : 'yellow'}"><div class="label">SPY Phase</div><div class="value">${scan.spy.phase || '?'}</div><div class="sub">${scan.spy.trend || ''} @ $${(scan.spy.price || 0).toFixed(2)}</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Market Breadth</h2><div class="chart-wrap"><canvas id="breadthChart"></canvas></div></div>
      <div class="card">
        <h2>SPY Regime</h2>
        <span class="regime-badge ${regimeClass}">${scan.regime}</span>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px">
          <div><div style="color:var(--muted);font-size:11px">Phase</div><div style="font-size:18px;font-weight:700">${scan.spy.phase} - ${scan.spy.phase_name || ''}</div></div>
          <div><div style="color:var(--muted);font-size:11px">Confidence</div><div style="font-size:18px;font-weight:700">${scan.spy.confidence || '?'}%</div></div>
        </div>
      </div>
    </div>
    ${renderTop20Table(top20.top20 || [])}
    <div class="card">
      <h2 style="color:var(--green)">Buy Signals</h2>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th>#</th><th>Ticker</th><th>Score</th><th>Entry</th><th>Stop Loss</th><th>R:R</th><th>RS</th><th>Reddit</th><th>Key Reasons</th><th>Trade</th></tr></thead>
        <tbody>${renderBuyRows(scan.buy_signals)}</tbody>
      </table></div>
    </div>
    <div class="card">
      <h2 style="color:var(--red)">Sell Signals</h2>
      <div style="overflow-x:auto"><table class="signal-table">
        <thead><tr><th>#</th><th>Ticker</th><th>Score</th><th>Severity</th><th>Breakdown</th><th>Reddit</th><th>Reasons</th><th>Trade</th></tr></thead>
        <tbody>${renderSellRows(scan.sell_signals)}</tbody>
      </table></div>
    </div>`;

  renderBreadthChart('breadthChart', scan.breadth);

  // Stashed at module scope (not a local var) so the live-refresh closure set
  // up in renderMarketView — which persists across scan-selector changes —
  // always reads the CURRENT Top 20 list rather than whatever it was when
  // the interval was first created.
  _marketTop20Tickers = (top20.top20 || []).map(s => s.ticker);
  loadMomentumStatus(_marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap));
}

function renderBuyRows(signals) {
  if (!signals.length) return '<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
  return signals.map(s => {
    const pct = (s.score / (s.max_score || 125)) * 100;
    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
    const entryClass = (s.entry_quality || '').toLowerCase();
    const topReasons = (s.reasons || []).slice(0, 3).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    const extra = (s.reasons || []).slice(3);
    const extraHTML = extra.length
      ? `<div class="extra-reasons" style="display:none">${extra.map(r => `<li>${cleanEmoji(r)}</li>`).join('')}</div><button class="expand-btn" onclick="toggleReasons(this)">+${extra.length} more</button>`
      : '';
    return `<tr>
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td><span class="score-num">${s.score}</span><div class="score-bar"><div class="fill" style="width:${pct}%;background:${barColor}"></div></div></td>
      <td><span class="badge ${entryClass}">${s.entry_quality || '-'}</span></td>
      <td>${s.stop_loss ? '$' + s.stop_loss.toFixed(2) : '-'}</td>
      <td style="color:${(s.rr_ratio || 0) >= 3 ? 'var(--green)' : (s.rr_ratio || 0) >= 2 ? 'var(--text)' : 'var(--yellow)'}">${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : '-'}</td>
      <td style="color:${(s.rs || 0) > 0.1 ? 'var(--green)' : (s.rs || 0) > 0 ? 'var(--text)' : 'var(--red)'}">${s.rs != null ? s.rs.toFixed(3) : '-'}</td>
      <td>${redditCell(s.reddit_mentions)}</td>
      <td><ul class="reasons-list">${topReasons}</ul>${extraHTML}</td>
      <td>${fidelityLink(s.ticker, 'Buy', 'buy')}</td>
    </tr>`;
  }).join('');
}

function renderSellRows(signals) {
  if (!signals.length) return '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
  return signals.map(s => {
    const sevClass = (s.severity || 'medium').toLowerCase();
    const reasons = (s.reasons || []).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    return `<tr>
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span></td>
      <td><span class="score-num">${s.score}</span></td>
      <td><span class="badge ${sevClass}">${(s.severity || '?').toUpperCase()}</span></td>
      <td>${s.breakdown_level ? '$' + s.breakdown_level.toFixed(2) : '-'}</td>
      <td>${redditCell(s.reddit_mentions)}</td>
      <td><ul class="reasons-list">${reasons}</ul></td>
      <td>${fidelityLink(s.ticker, 'Sell', 'sell')}</td>
    </tr>`;
  }).join('');
}

// --- View: Positions (upload a Fidelity CSV, get hold/trim/add recommendations) --

const POSITION_ACTION_LABELS = {
  hold: { label: 'hold', cls: 'neutral' },
  trail_to_breakeven: { label: 'trail to breakeven', cls: 'good' },
  trail_to_profit: { label: 'trail to profit', cls: 'good' },
  take_partial_and_trail: { label: 'consider trimming', cls: 'medium' },
  take_major_partial_and_trail_tight: { label: 'trim + trail tight', cls: 'poor' },
};

function _positionsUploadCardHTML(data, expanded) {
  const hasResults = data.position_analyses && data.position_analyses.length;
  // Once you have results, the big upload form is just noise — collapse it to
  // a one-line bar with an "Update positions" toggle instead of always
  // showing the full form front and center.
  if (hasResults && !expanded) {
    return `
      <div class="card" id="pos-upload-card" style="display:flex;align-items:center;gap:12px;padding:14px 20px">
        <span style="color:var(--muted);font-size:13px">Showing ${data.position_analyses.length} position${data.position_analyses.length === 1 ? '' : 's'} from your last upload.</span>
        <button class="btn" id="pos-expand" style="margin-left:auto">Update positions</button>
      </div>`;
  }
  return `
    <div class="card sim-card" id="pos-upload-card" style="max-width:600px">
      <h2>Upload Your Positions <span class="status-pill idle" id="pos-pill">idle</span></h2>
      <div class="sim-desc">
        Export a Positions CSV from Fidelity (Accounts &amp; Trade -&gt; Positions -&gt; Download) and upload it here.
        Nothing leaves this machine — no login, no credentials, just the file you already downloaded. Only your
        entry price and quantity are used; current prices come from cached market data, not the CSV.
      </div>
      <input type="file" id="pos-file" accept=".csv" style="margin-bottom:12px;display:block;color:var(--text);font-size:13px">
      <button class="btn primary" id="pos-analyze">${data.has_csv ? 'Re-analyze' : 'Upload &amp; Analyze'}</button>
      <div class="job-output" id="pos-output"></div>
    </div>`;
}

async function renderPositionsView() {
  const data = await fetchJSON('/api/positions');
  if (_currentView !== 'positions') return; // navigated away before this resolved
  const hasResults = data.position_analyses && data.position_analyses.length;
  content.innerHTML = `
    ${_positionsUploadCardHTML(data, false)}
    <div id="pos-results" style="margin-top:20px"></div>`;

  if (hasResults) {
    pageMeta.innerHTML = liveBadgeHTML();
    renderPositionsResults(data);
    _startLive(() => _liveGuarded('positions', refreshPositionsLive));
  }
  wirePositionsUpload(data);
}

// Silent live refresh: re-runs the (cheap, yfinance-only) positions analysis
// in the background and patches fresh prices/gains/charts in without touching
// the upload card or showing a loading spinner.
async function refreshPositionsLive() {
  await startJob('positions', {}, async (st) => {
    if (st.status === 'success') {
      renderPositionsResults(await fetchJSON('/api/positions'));
    }
  });
}

function wirePositionsUpload(data) {
  const expandBtn = document.getElementById('pos-expand');
  if (expandBtn) {
    expandBtn.addEventListener('click', () => {
      document.getElementById('pos-upload-card').outerHTML = _positionsUploadCardHTML(data, true);
      wirePositionsUpload(data);
    });
    return; // collapsed state has no analyze button yet
  }

  document.getElementById('pos-analyze').addEventListener('click', async () => {
    const fileInput = document.getElementById('pos-file');
    const btn = document.getElementById('pos-analyze');
    const pill = document.getElementById('pos-pill');
    const out = document.getElementById('pos-output');
    btn.disabled = true;

    if (fileInput.files.length) {
      pill.className = 'status-pill running';
      pill.innerHTML = '<span class="spinner"></span> uploading';
      const form = new FormData();
      form.append('csv', fileInput.files[0]);
      const uploadRes = await fetch('/api/positions/upload', { method: 'POST', body: form }).then(r => r.json());
      if (!uploadRes.success) {
        showToast('Upload failed: ' + (uploadRes.error || 'unknown error'));
        btn.disabled = false;
        pill.className = 'status-pill error';
        pill.textContent = 'error';
        return;
      }
    } else if (!data.has_csv) {
      showToast('Choose a CSV file first');
      btn.disabled = false;
      return;
    }

    out.style.display = 'block';
    out.textContent = '';
    pill.className = 'status-pill running';
    pill.innerHTML = '<span class="spinner"></span> analyzing';

    await startJob('positions', {}, async (st) => {
      out.textContent = st.output.join('\n');
      out.scrollTop = out.scrollHeight;
      if (st.status === 'success' || st.status === 'error' || st.status === 'stopped') {
        btn.disabled = false;
        pill.className = `status-pill ${st.status}`;
        pill.textContent = st.status;
        if (st.status === 'success') {
          renderPositionsResults(await fetchJSON('/api/positions'));
        }
      }
    });
  });
}

function renderPositionsResults(data) {
  const summary = data.summary || {};
  const analyses = data.position_analyses || [];
  const resultsEl = document.getElementById('pos-results');
  if (!resultsEl) return;

  if (!analyses.length) {
    resultsEl.innerHTML = '<div class="no-data"><h2>No positions found</h2></div>';
    return;
  }

  const cards = analyses.map(a => {
    const meta = POSITION_ACTION_LABELS[a.action] || { label: a.action || 'hold', cls: 'neutral' };
    const gainColor = a.current_gain_pct >= 0 ? 'var(--green)' : 'var(--red)';
    const gainSign = a.current_gain_pct >= 0 ? '+' : '';

    let extra = '';
    if (a.recommended_stop) {
      extra += `<div class="agent-badge-sub">Recommended stop: $${a.recommended_stop.toFixed(2)}</div>`;
    }
    if (a.add_on_signal) {
      extra += `<div class="agent-badge-sub" style="color:var(--green);margin-top:6px">Add-on candidate — ${a.add_on_rationale}</div>`;
    }
    (a.warnings || []).forEach(w => {
      extra += `<div class="agent-badge-sub" style="color:var(--yellow)">${w}</div>`;
    });

    const chartId = `pos-chart-${a.ticker}`;
    const hasHistory = a.price_history && a.price_history.length;

    return `
      <div class="pick-card">
        <div class="pick-header">
          <span class="ticker">${a.ticker}</span>
          ${hasHistory ? chartToggleButtonHTML(chartId) : ''}
          <span class="badge ${meta.cls}" style="margin-left:${hasHistory ? '8px' : 'auto'}">${meta.label}</span>
        </div>
        <div class="pick-scores">
          <div class="score-block"><div class="label">Entry</div><div class="value">$${a.entry_price.toFixed(2)}</div></div>
          <div class="score-block"><div class="label">Current</div><div class="value">$${a.current_price.toFixed(2)}</div></div>
          <div class="score-block"><div class="label">Gain</div><div class="value" style="color:${gainColor}">${gainSign}${a.current_gain_pct}%</div></div>
        </div>
        <div style="margin-bottom:10px"><span id="momentum-slot-${a.ticker}"></span></div>
        ${extra}
        ${hasHistory ? `<div class="position-chart-wrap" id="${chartId}-wrap" style="display:none"><canvas id="${chartId}"></canvas></div>` : ''}
      </div>`;
  }).join('');

  resultsEl.innerHTML = `
    <div class="stats-row">
      <div class="stat-card"><div class="label">Positions</div><div class="value">${summary.total_positions || 0}</div></div>
      <div class="stat-card yellow"><div class="label">Need Adjustment</div><div class="value">${summary.positions_need_adjustment || 0}</div></div>
      <div class="stat-card green"><div class="label">Add-On Candidates</div><div class="value">${summary.add_on_candidates || 0}</div></div>
      <div class="stat-card ${(summary.average_gain_pct || 0) >= 0 ? 'green' : 'red'}"><div class="label">Avg Gain</div><div class="value">${(summary.average_gain_pct || 0) >= 0 ? '+' : ''}${summary.average_gain_pct || 0}%</div></div>
    </div>
    <div class="shortlist-grid">${cards}</div>`;

  wireChartToggles(resultsEl, (ticker) => {
    const a = analyses.find(x => x.ticker === ticker);
    return a ? { history: a.price_history, entry: a.entry_price, stop: a.recommended_stop } : null;
  }, 'pos-chart-');

  const posTickers = analyses.map(a => a.ticker);
  loadMomentumStatus(posTickers, 'positions', (statusMap) => paintMomentumSlots(posTickers, statusMap));
}

// --- View: Backtests ------------------------------------------------------

async function renderBacktestsView() {
  const history = await fetchJSON('/api/backtest/history');
  if (_currentView !== 'backtests') return; // navigated away before this resolved
  content.innerHTML = `
    <div class="source-note historical">
      <b>This is a report card, not your email.</b> It shows how the screener's scoring would have performed
      on real historical stocks and prices — win rate, returns, drawdown. It doesn't contain today's picks;
      for those, see <a href="#/shortlist" style="color:var(--blue)">Shortlist</a> or
      <a href="#/market" style="color:var(--blue)">Market</a>. Run a fresh one from
      <a href="#/run" style="color:var(--blue)">Run Simulation</a>.
    </div>
    <div style="margin-bottom:16px">
      <select class="scan-select" id="backtestSelect">
        <option value="">Latest</option>
      </select>
    </div>
    <div id="backtestBody"></div>`;
  const sel = document.getElementById('backtestSelect');
  history.forEach(h => {
    const opt = document.createElement('option');
    opt.value = h.path;
    opt.textContent = `${h.name} (${h.generated ? new Date(h.generated).toLocaleDateString() : '?'})`;
    sel.appendChild(opt);
  });
  sel.addEventListener('change', () => loadBacktest(sel.value));
  loadBacktest('');
}

async function loadBacktest(path) {
  const [summaryData, tradesData] = await Promise.all([
    path ? fetchJSON('/api/backtest/run?path=' + encodeURIComponent(path)) : fetchJSON('/api/backtest/latest'),
    fetchJSON('/api/backtest/trades' + (path ? '?path=' + encodeURIComponent(path) : '')),
  ]);
  if (_currentView !== 'backtests') return; // navigated away before this resolved
  const summary = summaryData.summary || {};
  const trades = tradesData.trades || [];

  if (!summary.total_trades) {
    document.getElementById('backtestBody').innerHTML = `
      <div class="no-data"><h2>No backtest history yet</h2><p>Run a Walk-Forward simulation from the Run Simulation page.</p></div>`;
    return;
  }
  pageMeta.textContent = summaryData.generated ? `Generated ${new Date(summaryData.generated).toLocaleString()}` : '';

  document.getElementById('backtestBody').innerHTML = `
    <div class="stats-row">
      <div class="stat-card ${summary.win_rate_pct >= 40 ? 'green' : 'yellow'}"><div class="label">Win Rate</div><div class="value">${(summary.win_rate_pct || 0).toFixed(1)}%</div><div class="sub">${summary.total_trades} trades</div></div>
      <div class="stat-card ${summary.avg_return_pct >= 0 ? 'green' : 'red'}"><div class="label">Avg Return</div><div class="value">${(summary.avg_return_pct || 0).toFixed(2)}%</div><div class="sub">median ${(summary.median_return_pct || 0).toFixed(2)}%</div></div>
      <div class="stat-card blue"><div class="label">Sharpe-like</div><div class="value">${(summary.sharpe_like || 0).toFixed(2)}</div><div class="sub">avg win ${(summary.avg_win_pct || 0).toFixed(1)}% / loss ${(summary.avg_loss_pct || 0).toFixed(1)}%</div></div>
      <div class="stat-card red"><div class="label">Max Drawdown</div><div class="value">${(summary.max_drawdown_pct || 0).toFixed(1)}%</div><div class="sub">$${(summary.max_drawdown_dollars || 0).toFixed(0)}</div></div>
      <div class="stat-card purple"><div class="label">Avg Days Held</div><div class="value">${(summary.avg_days_held || 0).toFixed(1)}</div><div class="sub">${summary.total_periods || '?'} periods</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Cumulative P&amp;L (by exit date)</h2><div class="chart-wrap"><canvas id="equityChart"></canvas></div></div>
      <div class="card"><h2>Exit Reasons</h2><div class="chart-wrap"><canvas id="exitChart"></canvas></div></div>
    </div>
    <div class="card">
      <h2>Trades <span style="font-weight:400;color:var(--muted);font-size:12px">(click a column to sort)</span></h2>
      <div style="overflow-x:auto"><table class="signal-table" id="tradesTable">
        <thead><tr>
          <th data-key="ticker">Ticker</th><th data-key="period">Entry Date</th><th data-key="score">Score</th>
          <th data-key="exit_reason">Exit Reason</th><th data-key="days_held">Days Held</th><th data-key="return_pct">Return %</th><th data-key="dollar_pnl">$ P&amp;L</th>
        </tr></thead>
        <tbody>${renderTradeRows(trades)}</tbody>
      </table></div>
    </div>`;

  renderEquityCurveChart('equityChart', tradesData.equity_curve || []);
  renderExitReasonChart('exitChart', summary.exit_reasons || {});

  let sortKey = null, sortDir = 1;
  document.querySelectorAll('#tradesTable th[data-key]').forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      sortDir = sortKey === key ? -sortDir : 1;
      sortKey = key;
      const sorted = [...trades].sort((a, b) => {
        const av = a[key], bv = b[key];
        if (typeof av === 'string') return sortDir * String(av).localeCompare(String(bv));
        return sortDir * ((av || 0) - (bv || 0));
      });
      document.querySelector('#tradesTable tbody').innerHTML = renderTradeRows(sorted);
    });
  });
}

function renderTradeRows(trades) {
  return trades.map(t => `<tr>
    <td><span class="ticker">${t.ticker}</span></td>
    <td>${t.period || '-'}</td>
    <td>${t.score ?? '-'}</td>
    <td><span class="badge ${t.exit_reason === 'stop_loss' ? 'poor' : t.exit_reason === 'sell_signal' ? 'medium' : 'good'}">${(t.exit_reason || '-').replace('_', ' ')}</span></td>
    <td>${t.days_held ?? '-'}</td>
    <td style="color:${(t.return_pct || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">${(t.return_pct || 0).toFixed(2)}%</td>
    <td style="color:${(t.dollar_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">$${(t.dollar_pnl || 0).toFixed(2)}</td>
  </tr>`).join('');
}

// --- View: Run Simulation --------------------------------------------------

function renderRunView() {
  content.innerHTML = `
    <div class="grid-3">
      ${jobCardHTML('top3', 'Quick Backtest (Top 3)', 'What would the top-3 buy signals have been N days ago, held to today?', `
        <label>Days back<input type="number" id="top3-days" value="7"></label>
        <label>Sample size<input type="number" id="top3-sample" value="150"></label>
        <label>Investment $<input type="number" id="top3-investment" value="1000"></label>
      `)}
      ${jobCardHTML('mc', 'Monte Carlo', 'Re-samples many top-3 portfolios from one fetched pool — win rate distribution, not one basket.', `
        <label>Days back<input type="number" id="mc-days" value="7"></label>
        <label>Pool size<input type="number" id="mc-pool" value="300"></label>
        <label>Sample size<input type="number" id="mc-sample" value="150"></label>
        <label>Iterations<input type="number" id="mc-iterations" value="100"></label>
      `)}
      ${jobCardHTML('wf', 'Full Walk-Forward', 'Rigorous multi-period backtest — walks a fixed universe through many historical dates. Slow (minutes+).', `
        <label>Universe size<input type="number" id="wf-universe_size" value="250"></label>
        <label>Lookback (mo)<input type="number" id="wf-lookback_months" value="9"></label>
        <label>Top N/period<input type="number" id="wf-top_n" value="10"></label>
        <label>Max hold (days)<input type="number" id="wf-max_hold_days" value="60"></label>
      `)}
    </div>`;

  wireJobCard('top3', 'backtest-top3', () => ({
    days: +document.getElementById('top3-days').value,
    sample: +document.getElementById('top3-sample').value,
    investment: +document.getElementById('top3-investment').value,
  }), async (st, resultEl) => {
    if (!st.result_path) return;
    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
    if (res.error) return;
    resultEl.innerHTML = `<div style="font-size:13px">
      <strong style="color:${res.total_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.total_profit.toFixed(2)} (${res.total_return_pct.toFixed(2)}%)</strong>
      — ${res.picks.map(p => p.ticker).join(', ')}</div>`;
  });

  wireJobCard('mc', 'backtest-monte-carlo', () => ({
    days: +document.getElementById('mc-days').value,
    pool: +document.getElementById('mc-pool').value,
    sample: +document.getElementById('mc-sample').value,
    iterations: +document.getElementById('mc-iterations').value,
  }), async (st, resultEl) => {
    if (!st.result_path) return;
    const res = await fetchJSON('/api/backtest/run?path=' + encodeURIComponent(st.result_path));
    if (res.error || !res.iterations_run) { resultEl.innerHTML = '<div style="color:var(--muted);font-size:13px">Not enough qualifiers found.</div>'; return; }
    resultEl.innerHTML = `<div style="font-size:13px">
      Win rate <strong>${res.win_rate.toFixed(1)}%</strong> · avg <strong style="color:${res.avg_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.avg_profit.toFixed(2)} (${res.avg_pct.toFixed(2)}%)</strong>
      over ${res.iterations_run} iterations${res.score_return_correlation != null ? ` · score/return correlation r=${res.score_return_correlation.toFixed(3)}` : ''}</div>`;
  });

  wireJobCard('wf', 'walk-forward', () => ({
    universe_size: +document.getElementById('wf-universe_size').value,
    lookback_months: +document.getElementById('wf-lookback_months').value,
    top_n: +document.getElementById('wf-top_n').value,
    max_hold_days: +document.getElementById('wf-max_hold_days').value,
  }), async (st, resultEl) => {
    resultEl.innerHTML = `<a href="#/backtests" class="btn primary">View results →</a>`;
  });
}

// --- View: Full Scan --------------------------------------------------------

function renderScanView() {
  content.innerHTML = `
    <div class="card sim-card" style="max-width:520px">
      <h2>Run a Scan <span class="status-pill idle" id="scan-pill">idle</span></h2>
      <div class="sim-desc">Test scan covers ~100 stocks (~1 min). Full scan covers the ~3,800-stock universe (15-30 min).</div>
      <div class="sim-params" style="align-items:center">
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-full" style="width:auto"> Full scan (unchecked = quick test scan)</label>
      </div>
      <div class="sim-params" style="align-items:center">
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-agents" style="width:auto"> Enable AI agents (Fundamentals/Catalyst/Congress → Top 5 shortlist, needs ANTHROPIC_API_KEY)</label>
      </div>
      <button class="btn primary" id="scan-run">Run</button>
      <div class="job-output" id="scan-output"></div>
      <div id="scan-result" style="margin-top:12px"></div>
    </div>`;

  wireJobCard('scan', 'scan', () => ({
    full: document.getElementById('scan-full').checked,
    enable_llm_agents: document.getElementById('scan-agents').checked,
  }), async (st, resultEl) => {
    resultEl.innerHTML = `<a href="#/market" class="btn primary">View Market →</a> <a href="#/shortlist" class="btn">View Shortlist →</a>`;
  });
}

// silent=true (used by auto-sync): stays quiet unless it actually pulls new
// data, so a background sync every few minutes doesn't spam toasts for
// "already up to date" or for a transient failure — the manual button still
// surfaces both of those explicitly when you click it yourself.
async function doSync(silent) {
  try {
    const res = await fetchJSON('/api/sync', { method: 'POST' });
    if (res.success) {
      if (!res.output.includes('Already up to date')) {
        showToast('Pulled latest data — refreshing…');
        route();
      } else if (!silent) {
        showToast('Already up to date.');
      }
    } else if (!silent) {
      showToast('Sync failed: ' + (res.output || 'unknown error').slice(0, 200));
    }
    return res;
  } catch (e) {
    if (!silent) showToast('Sync error: ' + e.message);
    return { success: false };
  }
}

document.getElementById('syncBtn').addEventListener('click', async () => {
  const btn = document.getElementById('syncBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Syncing…';
  await doSync(false);
  btn.disabled = false;
  btn.innerHTML = 'Sync latest';
});

// Auto-sync: pulls in the background every few minutes so today's emailed
// picks show up here without you having to click Sync — runs app-wide (not
// tied to the current view, unlike the per-view "Live" refresh) since new
// data can land at any time regardless of what page you're on.
const AUTO_SYNC_INTERVAL_MS = 5 * 60 * 1000;
setInterval(() => doSync(true), AUTO_SYNC_INTERVAL_MS);
doSync(true); // also try once right away, in case new data landed since last time the app was open

route();
