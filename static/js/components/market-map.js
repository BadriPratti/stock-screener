import {
  DEFAULT_POINT_BUDGET,
  buildTrackerRows,
  buildTracks,
  chartDomain,
  createPlayer,
  decimate,
  dropReasonLabel,
  filterTickers,
  frameLabel,
  itemsAt,
  radiusForStreak,
  sortRows,
  stateLabel,
  trailPoints,
} from '../core/market-motion.js';
import { escapeHtml } from '../core/ui-helpers.js';

const CANVAS_ID = 'marketMotionChart';
const QUALITY_COLORS = { good: '#22c55e', extended: '#eab308', poor: '#ef4444' };
const TABLE_COLUMNS = [
  ['ticker', 'Ticker'], ['tier', 'Tier'], ['streak', 'Streak'], ['longest', 'Longest'],
  ['qualified', 'Qualified of observed'], ['score', 'Score'], ['rs', 'RS'],
  ['entryQuality', 'Entry quality'], ['firstQualified', 'First qualified'],
  ['trend', 'Score trend'], ['state', 'State'],
];

function finite(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

function formatNumber(value, digits = 2) {
  if (!finite(value)) return '-';
  return String(Number(value.toFixed(digits)));
}

function dateTime(value) {
  if (!value) return 'Never';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
}

function elapsedLabel(frames, index) {
  if (index <= 0 || !frames[index - 1]) return 'first recorded frame';
  const gap = new Date(frames[index].generated_at) - new Date(frames[index - 1].generated_at);
  if (!Number.isFinite(gap) || gap < 0) return 'recorded gap unknown';
  const hours = gap / 36e5;
  if (hours < 1) return `${Math.max(1, Math.round(gap / 60000))} min after previous frame`;
  if (hours < 48) return `${Number(hours.toFixed(1))}h after previous frame`;
  return `${Number((hours / 24).toFixed(1))} days after previous frame`;
}

function schedulerDetail(status) {
  const lastRun = status.last_run
    ? `${status.last_run.status || 'unknown'} at ${dateTime(status.last_run.finished_at)}`
    : 'Never';
  const lastPublish = status.last_publish
    ? `${status.last_publish.status || 'unknown'} at ${dateTime(status.last_publish.at)}`
    : 'Never';
  return { lastRun, lastPublish, nextRun: dateTime(status.next_run_at) };
}

export function schedulerCardHTML(status = {}) {
  const detail = schedulerDetail(status);
  return `<section class="market-motion-scheduler" aria-labelledby="marketMotionSchedulerTitle">
    <div>
      <h3 id="marketMotionSchedulerTitle">Tracked-stock refresh</h3>
      <div id="marketSchedulerMessage" class="market-motion-status">${escapeHtml(status.message || 'Off')}</div>
      <div class="market-motion-scheduler-times">
        <span>Last run: <b id="marketSchedulerLastRun">${escapeHtml(detail.lastRun)}</b></span>
        <span>Last publish: <b id="marketSchedulerLastPublish">${escapeHtml(detail.lastPublish)}</b></span>
        <span>Next run: <b id="marketSchedulerNextRun">${escapeHtml(detail.nextRun)}</b></span>
      </div>
      <div class="market-motion-off-note">Off by default. Nothing runs unless auto-refresh is turned on or Run now is selected.</div>
    </div>
    <div class="market-motion-scheduler-actions">
      <label><input id="marketSchedulerEnabled" type="checkbox"${status.enabled ? ' checked' : ''}> Auto-refresh every 2 hours while this app is open</label>
      <label><input id="marketSchedulerPublish" type="checkbox"${status.publish_to_github ? ' checked' : ''}> Publish frames to GitHub</label>
      <button class="btn" id="marketSchedulerRun" type="button"${status.running ? ' disabled' : ''}>${status.running ? 'Running' : 'Run now'}</button>
      <div class="market-motion-error" id="marketSchedulerError" role="status">${escapeHtml(status.error || '')}</div>
    </div>
  </section>`;
}

function tableRowsHTML(rows) {
  return rows.map(row => {
    const trend = finite(row.trend) ? `${row.trend > 0 ? '+' : ''}${formatNumber(row.trend)}` : '-';
    return `<tr id="trackedTicker-${escapeHtml(row.ticker)}" data-tracked-ticker="${escapeHtml(row.ticker)}" tabindex="-1" class="${row.stale ? 'market-motion-stale-row' : ''}">
      <td><span class="ticker">${escapeHtml(row.ticker)}</span></td>
      <td>${escapeHtml(row.tier || '-')}</td><td>${escapeHtml(row.streak ?? '-')}</td>
      <td>${escapeHtml(row.longest ?? '-')}</td><td>${escapeHtml(row.sessionsText)}</td>
      <td>${escapeHtml(formatNumber(row.score))}</td><td>${escapeHtml(formatNumber(row.rs, 3))}</td>
      <td>${escapeHtml(row.entryQuality || '-')}</td><td>${escapeHtml(row.firstQualified || '-')}</td>
      <td>${escapeHtml(trend)}</td><td>${escapeHtml(row.state || '-')}</td>
    </tr>`;
  }).join('');
}

export function trackerTableHTML(rows, sort = { key: 'streak', direction: 'descending' }) {
  const headers = TABLE_COLUMNS.map(([key, label]) => {
    const active = sort.key === key;
    return `<th scope="col" role="button" tabindex="0" data-market-sort="${key}" aria-sort="${active ? sort.direction : 'none'}">${label}</th>`;
  }).join('');
  return `<div class="market-motion-table-wrap"><table class="signal-table market-motion-table" id="marketMotionTable">
    <caption>Every tracked stock returned by the tracker, including points omitted from the chart</caption>
    <thead><tr>${headers}</tr></thead><tbody>${tableRowsHTML(rows)}</tbody>
  </table></div>`;
}

export function marketMapHTML(tracker, scheduler = {}) {
  const counts = tracker.counts || {};
  const total = (counts.active || 0) + (counts.watching || 0) + (counts.retired || 0);
  const intraday = Math.min((tracker.roster && tracker.roster.cap) || 0,
    ((tracker.roster && tracker.roster.active) || 0) + ((tracker.roster && tracker.roster.watching) || 0));
  const visible = filterTickers(tracker);
  const rows = sortRows(buildTrackerRows(tracker).filter(row => visible.has(row.ticker)), 'streak', 'descending');
  return `<div class="card market-motion-card" id="marketMotionCard">
    <div class="market-motion-heading">
      <div><h2>Buy Opportunity Map</h2>
        <div class="card-sub" id="marketMotionSubtitle">Tracking ${total} stocks (${counts.active || 0} active, ${counts.watching || 0} watching). Intraday re-score: ${intraday} of ${total}.</div>
      </div>
      <button class="btn" id="marketMotionExpand" type="button" aria-label="Expand Buy Opportunity Map">Expand</button>
    </div>
    <div class="market-motion-filterbar" aria-label="Map filters">
      <div class="market-motion-chips" role="group" aria-label="Tracking tier">
        <button class="market-motion-chip active" type="button" data-tier="active" aria-pressed="true">Active</button>
        <button class="market-motion-chip active" type="button" data-tier="watching" aria-pressed="true">Watching</button>
        <button class="market-motion-chip" type="button" data-tier="retired" aria-pressed="false">Retired</button>
      </div>
      <label class="market-motion-toggle"><input id="marketMotionShowRetired" type="checkbox"> Show retired</label>
      <div class="market-motion-chips" role="group" aria-label="Entry quality">
        ${['Good', 'Extended', 'Poor'].map(value => `<button class="market-motion-chip active" type="button" data-quality="${value.toLowerCase()}" aria-pressed="true">${value}</button>`).join('')}
      </div>
      <div class="market-motion-chips" role="group" aria-label="Minimum streak">
        <button class="market-motion-chip active" type="button" data-streak="0" aria-pressed="true">Any streak</button>
        ${[2, 3, 5].map(value => `<button class="market-motion-chip" type="button" data-streak="${value}" aria-pressed="false">Streak &gt;= ${value}</button>`).join('')}
      </div>
      <label class="market-motion-search">Ticker <input id="marketMotionSearch" type="search" autocomplete="off" aria-label="Search tracked ticker"></label>
    </div>
    <div class="market-motion-player" aria-label="Replay controls">
      <button class="btn" id="marketMotionPlay" type="button" aria-label="Play replay">Play</button>
      <button class="btn" id="marketMotionPrevious" type="button" aria-label="Previous recorded frame">Previous</button>
      <button class="btn" id="marketMotionNext" type="button" aria-label="Next recorded frame">Next</button>
      <label class="market-motion-slider-label">Recorded frame <input id="marketMotionSlider" type="range" min="0" max="0" step="0.01" value="0" aria-label="Recorded frame replay position"></label>
      <label>Speed <select id="marketMotionSpeed" aria-label="Replay speed"><option value="0.5">0.5x</option><option value="1" selected>1x</option><option value="2">2x</option></select></label>
      <button class="btn" id="marketMotionLive" type="button" aria-label="Return to latest frame">Live</button>
    </div>
    <div class="market-motion-status-row"><span id="marketMotionFrameStatus"></span><button id="marketMotionNew" class="market-motion-new" type="button" hidden>New snapshot available</button></div>
    <div id="marketMotionAnnouncement" class="visually-hidden" aria-live="polite"></div>
    <div id="marketMotionCoverage" class="market-motion-note"></div>
    <div id="marketMotionVersion" class="market-motion-divider" hidden></div>
    <div id="marketMotionFundamentals" class="market-motion-note"></div>
    <div class="market-motion-chart-wrap"><canvas id="${CANVAS_ID}" role="img" aria-label="Buy Opportunity Map loading"></canvas></div>
    <div class="market-motion-legend">Color shows entry quality. Solid points are active; hollow points are watching; muted diamonds are stale at their last real position. Dot size shows the daily qualification streak.</div>
    ${schedulerCardHTML(scheduler)}
    <section class="market-motion-tracker" aria-labelledby="marketMotionTrackerTitle">
      <h3 id="marketMotionTrackerTitle" class="visually-hidden">Tracked stocks</h3>
      <button class="market-motion-table-disclosure" id="marketMotionTableDisclosure" type="button" aria-expanded="false" aria-controls="marketMotionTableContainer">Tracked stocks (${rows.length})<span class="chevron" aria-hidden="true">&gt;</span></button>
      <div id="marketMotionTableContainer" hidden></div>
    </section>
  </div>`;
}

export function fallbackMapHTML(message) {
  return `<div class="card market-motion-card market-motion-fallback">
    <h2>Buy Opportunity Map</h2>
    <div class="card-sub">${escapeHtml(message)}</div>
    <div class="scatter-chart-wrap"><canvas id="marketScatterChart" role="img" aria-label="Current scan Buy Opportunity Map"></canvas></div>
  </div>`;
}

function median(values) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

function mergeFrames(existing, incoming) {
  const byId = new Map(existing.map(frame => [frame.run_id, frame]));
  incoming.forEach(frame => byId.set(frame.run_id, frame));
  return [...byId.values()].sort((a, b) => String(a.generated_at).localeCompare(String(b.generated_at)) || String(a.run_id).localeCompare(String(b.run_id)));
}

function focusableElements(root) {
  return [...root.querySelectorAll('button, input, select, [href], [tabindex]:not([tabindex="-1"])')]
    .filter(node => !node.disabled && !node.hidden);
}

export function createMarketMapController({
  root,
  frames: initialFrames,
  tracker: initialTracker,
  scheduler: initialScheduler = {},
  fetchJSON,
  chartApi,
  onTickerClick = () => {},
  requestFrame = callback => requestAnimationFrame(callback),
  cancelFrame = handle => cancelAnimationFrame(handle),
  now = () => performance.now(),
  matchMedia = query => window.matchMedia(query),
}) {
  let frames = initialFrames;
  let tracker = initialTracker;
  let tracks = buildTracks(frames);
  let chart = null;
  let player = null;
  let speed = 1;
  let selected = null;
  let hovered = null;
  let sort = { key: 'streak', direction: 'descending' };
  let requestToken = 0;
  let destroyed = false;
  let expanded = null;
  let active = true;
  let pendingLatestRunId = null;
  let lastAnnounced = -1;
  let frameTimes = [];
  let degradeLevel = 0;
  const filters = {
    tiers: new Set(['active', 'watching']),
    entryQualities: new Set(['good', 'extended', 'poor']),
    minStreak: 0,
    search: '',
  };
  const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');
  let reducedMotion = !!motionQuery.matches;

  const element = id => root.querySelector(`#${id}`);
  const hasTableDisclosure = !!element('marketMotionTableDisclosure');
  let tableOpen = !hasTableDisclosure;
  let tableBuilt = false;
  let tableDirty = true;
  const currentFrameIndex = state => Math.min(frames.length - 1, Math.max(0, Math.round(state.t)));

  function visibleTickers() {
    const effective = filters.entryQualities.size === 3
      ? { ...filters, entryQualities: new Set() }
      : filters;
    return filterTickers(tracker, effective);
  }

  function labelTickers(items) {
    if (degradeLevel >= 2) return selected || hovered ? [selected || hovered] : [];
    const candidates = new Set([selected, hovered].filter(Boolean));
    [...items].sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, 10).forEach(item => candidates.add(item.ticker));
    [...items].sort((a, b) => Math.abs(b.trend || 0) - Math.abs(a.trend || 0)).slice(0, 10).forEach(item => candidates.add(item.ticker));
    return [...candidates].slice(0, 20);
  }

  function enrich(item) {
    const record = tracker.tickers[item.ticker] || {};
    const latest = record.latest || null;
    const position = record.position || null;
    const quality = String((latest && latest.entry_quality) || item.entryQuality || '').toLowerCase();
    return {
      ...item,
      radius: radiusForStreak(record.current_streak_days) * item.scale,
      color: QUALITY_COLORS[quality] || '#8b8fa3',
      hollow: item.category !== 'active',
      selected: item.ticker === selected,
      streak: record.current_streak_days || 0,
      longest: record.longest_streak_days || 0,
      qualified: record.sessions_qualified || 0,
      observed: record.sessions_observed || 0,
      firstQualified: record.first_qualified || null,
      trend: record.score_trend,
      stateText: stateLabel(latest),
      dropText: dropReasonLabel(latest && latest.drop_reason),
      lastRealDate: position && position.generated_at,
    };
  }

  function renderState(state) {
    if (destroyed || !frames.length) return;
    if (!active) return;
    const started = now();
    const raw = itemsAt(frames, tracks, state.t, { isVisible: ticker => visibleTickers().has(ticker) });
    const plotted = decimate(raw, DEFAULT_POINT_BUDGET).items.map(enrich);
    const tailTickers = reducedMotion
      ? [hovered].filter(Boolean)
      : plotted.length <= 250 && degradeLevel < 1
        ? plotted.map(item => item.ticker)
        : [selected, hovered].filter(Boolean);
    const tails = [...new Set(tailTickers)].map(ticker => ({ ticker, points: trailPoints(frames, tracks, ticker, state.t, 3) }));
    const vectors = state.playing && !reducedMotion
      ? plotted.map(item => ({ ticker: item.ticker, points: trailPoints(frames, tracks, item.ticker, Math.ceil(state.t), 1) }))
      : [];
    chart.update({
      items: plotted,
      thresholdY: chartDomain(frames).thresholdY,
      labels: reducedMotion ? [hovered].filter(Boolean) : labelTickers(plotted),
      tails,
      vectors,
      playing: state.playing,
    });
    const index = currentFrameIndex(state);
    const shown = frames[index];
    element('marketMotionSlider').max = Math.max(0, frames.length - 1);
    element('marketMotionSlider').value = state.t;
    element('marketMotionPlay').textContent = state.playing ? 'Pause' : 'Play';
    element('marketMotionLive').textContent = state.atLive ? 'Live' : 'Return to live';
    element('marketMotionNew').hidden = !(state.newAvailable || pendingLatestRunId);
    element('marketMotionFrameStatus').textContent = `${frameLabel(shown)}; ${elapsedLabel(frames, index)}`;
    if (index !== lastAnnounced) {
      lastAnnounced = index;
      element('marketMotionAnnouncement').textContent = `Showing ${frameLabel(shown)}`;
    }
    const prior = index > 0 ? frames[index - 1] : null;
    const versionChanged = prior && prior.scoring_version !== shown.scoring_version;
    element('marketMotionVersion').hidden = !versionChanged;
    element('marketMotionVersion').textContent = versionChanged
      ? `Scoring model changed from ${prior.scoring_version} to ${shown.scoring_version}; positions snap at this divider.` : '';
    element('marketMotionFundamentals').textContent = shown.run_kind === 'intraday_rescore'
      ? `Intraday re-score, fundamentals as of ${shown.fundamentals_as_of || 'unknown'}.` : '';
    const counts = plotted.reduce((out, item) => { out[item.category] = (out[item.category] || 0) + 1; return out; }, {});
    element(CANVAS_ID).setAttribute('aria-label', `${counts.active || 0} active, ${counts.watching || 0} watching, ${counts.stale || 0} stale. ${frameLabel(shown)}`);
    frameTimes.push(now() - started);
    if (frameTimes.length > 30) frameTimes.shift();
    if (frameTimes.length === 30 && median(frameTimes) > 33 && degradeLevel < 2) {
      degradeLevel += 1;
      frameTimes = [];
    }
  }

  function makePlayer(position, wasPlaying = false) {
    if (player) player.destroy();
    player = createPlayer({
      frameCount: frames.length,
      stepDurationMs: 800 / speed,
      now, requestFrame, cancelFrame, reducedMotion,
      onUpdate: renderState,
    });
    if (finite(position)) player.scrub(position);
    else renderState(player.state());
    if (wasPlaying) player.play();
  }

  function renderTable() {
    const visible = visibleTickers();
    const allRows = buildTrackerRows(tracker);
    const rows = sortRows(hasTableDisclosure ? allRows.filter(row => visible.has(row.ticker)) : allRows,
      sort.key, sort.direction);
    const disclosure = element('marketMotionTableDisclosure');
    if (disclosure) disclosure.innerHTML = `Tracked stocks (${rows.length})<span class="chevron" aria-hidden="true">&gt;</span>`;
    if (!tableOpen) {
      tableDirty = true;
      return;
    }
    if (tableBuilt && !tableDirty) return;
    const container = element('marketMotionTableContainer');
    if (!tableBuilt && container) {
      container.innerHTML = trackerTableHTML(rows, sort);
      tableBuilt = true;
      tableDirty = false;
      bindSortHeaders();
      return;
    }
    const body = root.querySelector('#marketMotionTable tbody');
    if (body) {
      body.innerHTML = tableRowsHTML(rows);
      tableBuilt = true;
      tableDirty = false;
    }
  }

  function invalidateTable() {
    tableDirty = true;
    renderTable();
  }

  function applySort(header) {
    const key = header.dataset.marketSort;
    sort = { key, direction: sort.key === key && sort.direction === 'ascending' ? 'descending' : 'ascending' };
    invalidateTable();
    root.querySelectorAll('[data-market-sort]').forEach(item => item.setAttribute('aria-sort', item.dataset.marketSort === key ? sort.direction : 'none'));
  }

  function bindSortHeaders() {
    root.querySelectorAll('[data-market-sort]').forEach(header => {
      if (header.dataset.marketSortBound) return;
      header.dataset.marketSortBound = 'true';
      header.addEventListener('click', () => applySort(header));
      header.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); applySort(header); }
      });
    });
  }

  async function refetchTracker(includeRetired) {
    const token = ++requestToken;
    const tiers = includeRetired ? 'active,watching,retired' : 'active,watching';
    try {
      const next = await fetchJSON(`/api/market-motion/tracker?tiers=${encodeURIComponent(tiers)}`);
      if (destroyed || token !== requestToken) return false;
      tracker = next;
      invalidateTable();
      renderState(player.state());
      return true;
    } catch {
      if (!destroyed && token === requestToken) element('marketMotionCoverage').textContent = 'Could not refresh the tracked-stock list.';
      return false;
    }
  }

  async function refreshFrames() {
    const token = ++requestToken;
    try {
      const data = await fetchJSON('/api/market-motion?limit=20');
      if (destroyed || token !== requestToken || !Array.isArray(data.frames)) return false;
      const oldCount = frames.length;
      frames = mergeFrames(frames, data.frames);
      tracks = buildTracks(frames);
      await refetchTracker(filters.tiers.has('retired'));
      if (destroyed || token > requestToken) return false;
      if (frames.length !== oldCount) player.setFrameCount(frames.length);
      else renderState(player.state());
      return true;
    } catch {
      return false;
    }
  }

  async function pollLatest() {
    try {
      const latest = await fetchJSON('/api/market-motion/latest');
      if (!destroyed && latest.latest_run_id && !frames.some(frame => frame.run_id === latest.latest_run_id)) {
        if (active) await refreshFrames();
        else {
          pendingLatestRunId = latest.latest_run_id;
          element('marketMotionNew').hidden = false;
        }
      }
    } catch {
      // Live polling is fail-soft; the next interval tries again.
    }
    try {
      const scheduler = await fetchJSON('/api/market-motion/scheduler');
      if (!destroyed) updateScheduler(scheduler);
    } catch {
      if (!destroyed) element('marketSchedulerError').textContent = 'Could not refresh scheduler status.';
    }
  }

  function updateScheduler(status) {
    const detail = schedulerDetail(status);
    element('marketSchedulerMessage').textContent = status.message || 'Off';
    element('marketSchedulerLastRun').textContent = detail.lastRun;
    element('marketSchedulerLastPublish').textContent = detail.lastPublish;
    element('marketSchedulerNextRun').textContent = detail.nextRun;
    element('marketSchedulerEnabled').checked = !!status.enabled;
    element('marketSchedulerPublish').checked = !!status.publish_to_github;
    element('marketSchedulerRun').disabled = !!status.running;
    element('marketSchedulerRun').textContent = status.running ? 'Running' : 'Run now';
  }

  async function schedulerPost(body) {
    element('marketSchedulerError').textContent = '';
    try {
      const status = await fetchJSON('/api/market-motion/scheduler', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      });
      if (status.error) throw new Error(status.error);
      if (!destroyed) updateScheduler(status);
    } catch (error) {
      if (!destroyed) element('marketSchedulerError').textContent = `Could not update scheduler: ${error.message}`;
    }
  }

  async function runNow() {
    const button = element('marketSchedulerRun');
    button.disabled = true;
    button.textContent = 'Starting';
    element('marketSchedulerError').textContent = '';
    try {
      const result = await fetchJSON('/api/market-motion/run-now', { method: 'POST' });
      if (!result.started) throw new Error(result.reason || 'Run was not started');
      button.textContent = 'Running';
    } catch (error) {
      if (!destroyed) {
        button.disabled = false;
        button.textContent = 'Run now';
        element('marketSchedulerError').textContent = `Could not start: ${error.message}`;
      }
    }
  }

  function closeExpanded() {
    if (!expanded) return;
    const { overlay, placeholder, trigger, keydown } = expanded;
    overlay.removeEventListener('keydown', keydown);
    placeholder.replaceWith(root);
    overlay.remove();
    document.body.classList.remove('market-map-open');
    const app = document.querySelector('.app');
    if (app) app.removeAttribute('inert');
    expanded = null;
    if (!destroyed && active) chart.resize();
    if (active && document.contains(trigger)) trigger.focus();
  }

  function openExpanded() {
    if (expanded) return;
    const trigger = element('marketMotionExpand');
    const placeholder = document.createElement('div');
    root.replaceWith(placeholder);
    const overlay = document.createElement('div');
    overlay.className = 'market-map-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Expanded Buy Opportunity Map');
    const panel = document.createElement('section');
    panel.className = 'market-map-overlay-panel';
    const close = document.createElement('button');
    close.className = 'btn market-map-overlay-close';
    close.type = 'button';
    close.textContent = 'Close';
    close.setAttribute('aria-label', 'Close expanded Buy Opportunity Map');
    panel.append(close, root);
    overlay.append(panel);
    document.body.append(overlay);
    document.body.classList.add('market-map-open');
    const app = document.querySelector('.app');
    if (app) app.setAttribute('inert', '');
    const keydown = event => {
      if (event.key === 'Escape') { event.preventDefault(); closeExpanded(); return; }
      if (event.key !== 'Tab') return;
      const nodes = focusableElements(overlay);
      if (!nodes.length) return;
      if (event.shiftKey && document.activeElement === nodes[0]) { event.preventDefault(); nodes[nodes.length - 1].focus(); }
      else if (!event.shiftKey && document.activeElement === nodes[nodes.length - 1]) { event.preventDefault(); nodes[0].focus(); }
    };
    overlay.addEventListener('keydown', keydown);
    overlay.addEventListener('click', event => { if (event.target === overlay) closeExpanded(); });
    close.addEventListener('click', closeExpanded);
    expanded = { overlay, placeholder, trigger, keydown };
    chart.resize();
    close.focus();
  }

  function bind() {
    element('marketMotionPlay').addEventListener('click', togglePlayback);
    element('marketMotionPrevious').addEventListener('click', () => player.step(-1));
    element('marketMotionNext').addEventListener('click', () => player.step(1));
    element('marketMotionLive').addEventListener('click', () => player.toLive());
    element('marketMotionNew').addEventListener('click', async () => {
      if (pendingLatestRunId) {
        const refreshed = await refreshFrames();
        if (!refreshed) return;
        pendingLatestRunId = null;
      }
      player.toLive();
    });
    element('marketMotionSlider').addEventListener('input', event => player.scrub(Number(event.target.value)));
    element('marketMotionSpeed').addEventListener('change', event => {
      const old = player.state();
      speed = Number(event.target.value) || 1;
      makePlayer(old.t, old.playing);
    });
    root.querySelectorAll('[data-tier]').forEach(button => button.addEventListener('click', async () => {
      const tier = button.dataset.tier;
      const enable = !filters.tiers.has(tier);
      if (enable) filters.tiers.add(tier); else filters.tiers.delete(tier);
      button.classList.toggle('active', enable); button.setAttribute('aria-pressed', String(enable));
      if (tier === 'retired') {
        element('marketMotionShowRetired').checked = enable;
        invalidateTable();
        await refetchTracker(enable);
      } else {
        invalidateTable();
        renderState(player.state());
      }
    }));
    element('marketMotionShowRetired').addEventListener('change', async event => {
      const button = root.querySelector('[data-tier="retired"]');
      if (event.target.checked) filters.tiers.add('retired'); else filters.tiers.delete('retired');
      button.classList.toggle('active', event.target.checked); button.setAttribute('aria-pressed', String(event.target.checked));
      invalidateTable();
      await refetchTracker(event.target.checked);
    });
    root.querySelectorAll('[data-quality]').forEach(button => button.addEventListener('click', () => {
      const quality = button.dataset.quality;
      const enable = !filters.entryQualities.has(quality);
      if (enable) filters.entryQualities.add(quality); else filters.entryQualities.delete(quality);
      button.classList.toggle('active', enable); button.setAttribute('aria-pressed', String(enable));
      invalidateTable();
      renderState(player.state());
    }));
    root.querySelectorAll('[data-streak]').forEach(button => button.addEventListener('click', () => {
      filters.minStreak = Number(button.dataset.streak);
      root.querySelectorAll('[data-streak]').forEach(item => {
        const active = item === button; item.classList.toggle('active', active); item.setAttribute('aria-pressed', String(active));
      });
      invalidateTable();
      renderState(player.state());
    }));
    element('marketMotionSearch').addEventListener('input', event => {
      filters.search = event.target.value;
      const matches = filterTickers(tracker, filters);
      selected = matches.size === 1 ? [...matches][0] : null;
      invalidateTable();
      renderState(player.state());
    });
    bindSortHeaders();
    element('marketSchedulerEnabled').addEventListener('change', event => schedulerPost({ enabled: event.target.checked }));
    element('marketSchedulerPublish').addEventListener('change', event => schedulerPost({ publish_to_github: event.target.checked }));
    element('marketSchedulerRun').addEventListener('click', runNow);
    element('marketMotionExpand').addEventListener('click', openExpanded);
    const disclosure = element('marketMotionTableDisclosure');
    if (disclosure) disclosure.addEventListener('click', () => {
      tableOpen = !tableOpen;
      disclosure.setAttribute('aria-expanded', String(tableOpen));
      element('marketMotionTableContainer').hidden = !tableOpen;
      if (tableOpen) renderTable();
    });
  }

  function togglePlayback() {
    if (player.state().playing) player.pause();
    else player.play();
  }

  function setActive(isActive) {
    if (destroyed) return;
    active = !!isActive;
    if (!active) {
      if (player.state().playing) togglePlayback();
      closeExpanded();
      return;
    }
    chart.resize();
    renderState(player.state());
  }

  const motionChange = event => { reducedMotion = event.matches; player.setReducedMotion(reducedMotion); };
  const cleanup = () => {
    destroyed = true;
    requestToken += 1;
    if (player) player.destroy();
    if (motionQuery.removeEventListener) motionQuery.removeEventListener('change', motionChange);
    else if (motionQuery.removeListener) motionQuery.removeListener(motionChange);
    closeExpanded();
  };

  const domain = chartDomain(frames);
  chart = chartApi.renderMarketMotionChart(CANVAS_ID, { items: [], domain, thresholdY: domain.thresholdY }, {
    cleanup,
    onPointClick: item => {
      selected = item.ticker;
      renderState(player.state());
      onTickerClick(item.ticker);
    },
    onHover: ticker => { hovered = ticker; if (reducedMotion || frames.length <= 250) renderState(player.state()); },
    tooltipLines: item => [
      `${item.streak} days in a row (longest ${item.longest})`,
      `qualified ${item.qualified} of ${item.observed} sessions`,
      `first qualified: ${item.firstQualified || '-'}`,
      `score: ${formatNumber(item.score)}`,
      `RS: ${formatNumber(item.rs, 3)}`,
      `entry quality: ${item.entryQuality || '-'}`,
      `state: ${item.stateText}${item.dropText && item.dropText !== item.stateText ? ` (${item.dropText})` : ''}`,
      ...(item.stale ? [`last real position: ${item.lastRealDate ? dateTime(item.lastRealDate) : 'unknown'}`] : []),
    ],
  });
  bind();
  makePlayer();
  renderTable();
  const coverage = (tracker.top50_only_sessions || []);
  element('marketMotionCoverage').textContent = coverage.length
    ? `Sessions ${coverage.join(', ')} recorded only the top 50 buys; other stocks are unknown for those days, not dropped.` : '';
  if (motionQuery.addEventListener) motionQuery.addEventListener('change', motionChange);
  else if (motionQuery.addListener) motionQuery.addListener(motionChange);

  return {
    state: () => ({
      filters, selected, reducedMotion, requestToken, frames: [...frames], player: player.state(),
      active, expanded: !!expanded, tableOpen, tableBuilt, tableDirty, pendingLatestRunId,
    }),
    pollLatest,
    refresh: refreshFrames,
    setActive,
    suspend: () => setActive(false),
    resume: () => setActive(true),
    destroy: () => chartApi.destroyChart(CANVAS_ID),
    selectTicker(ticker) {
      selected = ticker;
      filters.search = ticker;
      element('marketMotionSearch').value = ticker;
      invalidateTable();
      renderState(player.state());
    },
  };
}

export async function mountMarketMap({ mount, fetchJSON, chartApi, fallback, onTickerClick, isCurrent = () => true, dependencies = {} }) {
  let framesData;
  let tracker;
  let scheduler;
  try {
    [framesData, tracker, scheduler] = await Promise.all([
      fetchJSON('/api/market-motion?limit=20'),
      fetchJSON('/api/market-motion/tracker?tiers=active%2Cwatching'),
      fetchJSON('/api/market-motion/scheduler').catch(() => ({
        enabled: false, publish_to_github: true, message: 'Status unavailable',
        error: 'Could not load scheduler status.',
      })),
    ]);
  } catch {
    if (!isCurrent()) return null;
    mount.innerHTML = fallbackMapHTML('Persistent history could not be loaded; showing the current scan only.');
    fallback();
    return null;
  }
  if (!isCurrent()) return null;
  if (!Array.isArray(framesData.frames) || !framesData.frames.length) {
    mount.innerHTML = fallbackMapHTML('No persistent frames are recorded yet; showing the current scan only.');
    fallback();
    return null;
  }
  mount.innerHTML = marketMapHTML(tracker, scheduler);
  return createMarketMapController({
    root: mount.querySelector('#marketMotionCard'), frames: framesData.frames, tracker, scheduler,
    fetchJSON, chartApi, onTickerClick, ...dependencies,
  });
}
