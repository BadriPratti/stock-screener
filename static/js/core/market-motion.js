// Pure model for the Market tab's persistent "Buy Opportunity Map": frames in,
// render items out. No DOM, no Chart.js, no timers of its own (the player takes
// an injected clock and frame scheduler), so everything here is unit-testable in
// plain Node (tests/js/test_market_motion.js).
//
// Data contract (see src/screening/market_motion.py and /api/market-motion):
//   frame   = { run_id, run_kind, generated_at, session_date, scoring_version,
//               coverage: { kind }, points: [point] }        (oldest -> newest)
//   point   = { ticker, evaluation, score?, rs?, phase?, entry_quality?, drop_reason?, ... }
//   evaluation: qualified | not_qualified | not_scored | error | not_evaluated
//   tracker = { tickers: { T: { tier, current_streak_days, ... } }, ... }
//
// Honesty rules encoded here (each has a test):
//  * A point only ever moves between two REAL observations; nothing is invented.
//  * not_scored / error / not_evaluated / absent have no coordinates: the dot is
//    held at its last real position and marked stale, never sent to (0,0).
//  * A ticker that is newly LOCATED because coverage changed (a top-50-only
//    frame followed by a complete one) appears without an "entry" bloom, since it
//    is not a new opportunity, only a newly visible one.
//  * No tweening across a scoring_version change: the map snaps.

export const DEFAULT_MAX_SCORE = 125;
export const DEFAULT_THRESHOLD = 60;
export const Y_DOMAIN_MIN = 40;
export const Y_DOMAIN_MAX = 100;
export const DEFAULT_POINT_BUDGET = 1200;

const POSITIONED = new Set(['qualified', 'not_qualified']);
const ALPHA = { active: 1, watching: 0.85, stale: 0.45 };

function finite(v) {
  return typeof v === 'number' && Number.isFinite(v);
}

export function scorePct(point, maxScore = DEFAULT_MAX_SCORE) {
  if (!point || !finite(point.score) || !(maxScore > 0)) return null;
  return (point.score / maxScore) * 100;
}

function isPositioned(point) {
  return !!point && POSITIONED.has(point.evaluation) && finite(point.score) && finite(point.rs);
}

// --- tracks ----------------------------------------------------------------

// tickers -> { ticker, firstQualified: frameIndex, obs: [point|null per frame] }
// Only tickers that qualified at least once are tracked (matches the tracker).
export function buildTracks(frames) {
  const index = new Map();
  frames.forEach((frame, i) => {
    for (const p of frame.points || []) {
      if (!index.has(p.ticker)) index.set(p.ticker, new Array(frames.length).fill(null));
      index.get(p.ticker)[i] = p;
    }
  });
  const tracks = new Map();
  for (const [ticker, obs] of index) {
    const firstQualified = obs.findIndex(p => p && p.evaluation === 'qualified');
    if (firstQualified === -1) continue;
    tracks.set(ticker, { ticker, firstQualified, obs });
  }
  return tracks;
}

function stateAt(track, i) {
  if (i < track.firstQualified) return 'X';
  const p = track.obs[i];
  if (!p) return 'U';
  if (p.evaluation === 'qualified') return 'Q';
  if (p.evaluation === 'not_qualified') return 'N';
  if (p.evaluation === 'not_scored') return 'S';
  return 'U';
}

// Last real coordinates at or before frame i (carry-forward for stale points).
function positionAtOrBefore(track, i, maxScore) {
  for (let k = Math.min(i, track.obs.length - 1); k >= track.firstQualified; k--) {
    const p = track.obs[k];
    if (isPositioned(p)) return { x: p.rs, y: scorePct(p, maxScore), from: k, point: p };
  }
  return null;
}

const CATEGORY = { Q: 'active', N: 'watching', S: 'stale', U: 'stale' };

// --- interpolation -----------------------------------------------------------

function newlyLocated(frames, a, b, track) {
  // Coverage widened between the two frames and the ticker was simply not in the
  // narrower frame: it is newly visible, not a new opportunity.
  const fa = frames[a];
  const fb = frames[b];
  const narrow = fa && fa.coverage && fa.coverage.kind === 'top50_only';
  const wide = fb && fb.coverage && fb.coverage.kind !== 'top50_only';
  return narrow && wide && !track.obs[a];
}

export function easeInOutCubic(p) {
  return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
}

/**
 * Render items for fractional frame position t in [0, frames.length - 1].
 * options: { maxScore, isVisible(ticker) -> bool, easing }
 */
export function itemsAt(frames, tracks, t, options = {}) {
  const n = frames.length;
  if (!n) return [];
  const clamped = Math.min(Math.max(t, 0), n - 1);
  const a = Math.floor(clamped);
  const b = Math.min(a + 1, n - 1);
  const raw = a === b ? 0 : clamped - a;
  const maxScore = options.maxScore || DEFAULT_MAX_SCORE;
  const ease = options.easing || easeInOutCubic;
  const p = ease(raw);
  const versionBreak = frames[a].scoring_version !== frames[b].scoring_version;
  const items = [];

  for (const track of tracks.values()) {
    if (options.isVisible && !options.isVisible(track.ticker)) continue;
    const sa = stateAt(track, a);
    const sb = stateAt(track, b);
    if (sa === 'X' && sb === 'X') continue;

    const posB = sb === 'X' ? null : positionAtOrBefore(track, b, maxScore);
    const posA = sa === 'X' ? null : positionAtOrBefore(track, a, maxScore);
    let x;
    let y;
    let alpha;
    let scale = 1;
    let entering = false;
    let bloom = false;
    let category;
    let source;

    if (sa === 'X') {
      // first appears in b
      if (!posB) continue;
      x = posB.x; y = posB.y;
      entering = raw > 0;
      bloom = !newlyLocated(frames, a, b, track);
      category = CATEGORY[sb];
      alpha = bloom ? p * ALPHA[category] : ALPHA[category];
      scale = bloom ? p : 1;
      if (raw === 0) continue; // exactly at frame a it does not exist yet
      source = b;
    } else if (versionBreak) {
      const useB = raw >= 0.5;
      const pos = useB ? posB : posA;
      if (!pos) continue;
      x = pos.x; y = pos.y;
      category = CATEGORY[useB ? sb : sa];
      alpha = ALPHA[category];
      source = useB ? b : a;
    } else if (posA && posB) {
      x = posA.x + (posB.x - posA.x) * p;
      y = posA.y + (posB.y - posA.y) * p;
      const catA = CATEGORY[sa];
      const catB = CATEGORY[sb];
      category = raw < 0.5 ? catA : catB;
      alpha = ALPHA[catA] + (ALPHA[catB] - ALPHA[catA]) * p;
      source = raw < 0.5 ? a : b;
    } else {
      continue;
    }

    const src = track.obs[source] || track.obs[Math.max(track.firstQualified, source)] || null;
    const latestPoint = (posB && posB.point) || (posA && posA.point) || null;
    items.push({
      ticker: track.ticker,
      x,
      y,
      category,
      alpha,
      scale,
      entering,
      bloom,
      exiting: sa === 'Q' && sb !== 'Q' && sb !== 'X' && raw > 0,
      stale: category === 'stale',
      evaluation: src ? src.evaluation : 'not_evaluated',
      dropReason: src && src.drop_reason ? src.drop_reason : null,
      entryQuality: (latestPoint && latestPoint.entry_quality) || null,
      phase: (src && src.phase) || (latestPoint && latestPoint.phase) || null,
      score: latestPoint ? latestPoint.score : null,
      rs: latestPoint ? latestPoint.rs : null,
      positionFrame: (posB || posA) ? (posB || posA).from : null,
    });
  }
  return items;
}

/** The last `maxSegments` real positions (older first) up to frame floor(t). */
export function trailPoints(frames, tracks, ticker, t, maxSegments = 3, maxScore = DEFAULT_MAX_SCORE) {
  const track = tracks.get(ticker);
  if (!track) return [];
  const upTo = Math.min(Math.floor(t), frames.length - 1);
  const pts = [];
  for (let k = upTo; k >= track.firstQualified && pts.length < maxSegments + 1; k--) {
    const p = track.obs[k];
    if (isPositioned(p)) {
      const last = pts[pts.length - 1];
      if (!last || last.x !== p.rs || last.y !== scorePct(p, maxScore)) {
        pts.push({ x: p.rs, y: scorePct(p, maxScore), frame: k });
      }
    }
  }
  return pts.reverse();
}

/**
 * Keep every active item; fill the rest of the budget with watching, then stale,
 * most recently observed first. Returns { items, dropped } - the table still
 * lists every record, decimation is only a rendering concern.
 */
export function decimate(items, budget = DEFAULT_POINT_BUDGET) {
  if (items.length <= budget) return { items, dropped: 0 };
  const rank = { active: 0, watching: 1, stale: 2 };
  const active = items.filter(i => i.category === 'active');
  const rest = items
    .filter(i => i.category !== 'active')
    .sort((p, q) => rank[p.category] - rank[q.category]
      || (q.positionFrame ?? -1) - (p.positionFrame ?? -1)
      || (p.ticker < q.ticker ? -1 : 1));
  const room = Math.max(0, budget - active.length);
  const kept = active.concat(rest.slice(0, room));
  return { items: kept, dropped: items.length - kept.length };
}

// --- encodings ---------------------------------------------------------------

/** Dot radius in px: 4 at a 1-day streak growing to 10 at 10+ days; 3 with no streak. */
export function radiusForStreak(days) {
  if (!finite(days) || days < 1) return 3;
  return 4 + 6 * Math.min(1, (days - 1) / 9);
}

/** Fixed axis domain over every frame in the replay (no per-frame rescaling). */
export function chartDomain(frames, options = {}) {
  const maxScore = options.maxScore || DEFAULT_MAX_SCORE;
  let minX = 0;
  let maxX = 0;
  let minY = Y_DOMAIN_MIN;
  for (const f of frames) {
    for (const p of f.points || []) {
      if (!isPositioned(p)) continue;
      minX = Math.min(minX, p.rs);
      maxX = Math.max(maxX, p.rs);
      minY = Math.min(minY, scorePct(p, maxScore));
    }
  }
  const pad = Math.max(0.05, (maxX - minX) * 0.05);
  return {
    xMin: Math.floor((minX - pad) * 20) / 20,
    xMax: Math.ceil((maxX + pad) * 20) / 20,
    yMin: Math.floor(minY / 5) * 5,
    yMax: Y_DOMAIN_MAX,
    thresholdY: ((options.threshold ?? DEFAULT_THRESHOLD) / maxScore) * 100,
  };
}

// --- labels ------------------------------------------------------------------

const ET_PARTS = typeof Intl !== 'undefined'
  ? new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hourCycle: 'h23',
  })
  : null;

export function frameLabel(frame) {
  if (!frame) return '';
  const [y, m, d] = String(frame.session_date || '').split('-').map(Number);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const day = (m >= 1 && m <= 12 && d) ? `${months[m - 1]} ${d}` : String(frame.session_date || '');
  if (frame.run_kind === 'intraday_rescore' && ET_PARTS) {
    const parts = Object.fromEntries(ET_PARTS.formatToParts(new Date(frame.generated_at)).map(p => [p.type, p.value]));
    return `${day} ${parts.hour}:${parts.minute} ET (intraday)`;
  }
  if (frame.run_kind === 'legacy_report') return `${day} (daily scan, top 50 only)`;
  return `${day} (daily scan)`;
}

export function dropReasonLabel(reason) {
  if (!reason) return '';
  if (reason === 'below_buy_threshold') return 'Below the buy line';
  if (reason === 'regime_gate') return 'Market regime gate';
  if (reason === 'not_scored') return 'Not scored this run';
  const phase = /^phase_(\d)$/.exec(reason);
  if (phase) return `Phase ${phase[1]} (not an uptrend)`;
  if (/^Not in Phase (\d)/i.test(reason)) return `Phase ${/^Not in Phase \d \(currently Phase (\d)/i.exec(reason)?.[1] || '?'} (not an uptrend)`;
  if (/minervini/i.test(reason)) return 'Fails the trend template';
  return String(reason);
}

export function stateLabel(latest) {
  if (!latest) return 'Unknown';
  switch (latest.evaluation) {
    case 'qualified': return 'Qualified';
    case 'not_qualified': return 'Below the buy line';
    case 'not_scored': return dropReasonLabel(latest.drop_reason) || 'Not scored';
    case 'error': return 'Could not be evaluated';
    default: return 'Not re-scored this run';
  }
}

// --- tracker table / filters ---------------------------------------------------

export function buildTrackerRows(tracker) {
  const rows = [];
  for (const [ticker, r] of Object.entries((tracker && tracker.tickers) || {})) {
    const latest = r.latest || null;
    const pos = r.position || null;
    rows.push({
      ticker,
      tier: r.tier,
      streak: r.current_streak_days,
      longest: r.longest_streak_days,
      qualified: r.sessions_qualified,
      observed: r.sessions_observed,
      sessionsText: `${r.sessions_qualified} of ${r.sessions_observed}`,
      score: pos ? pos.score : (r.latest_daily_score ?? null),
      rs: pos ? pos.rs : null,
      entryQuality: (latest && latest.entry_quality) || null,
      firstQualified: r.first_qualified,
      lastQualified: r.last_qualified,
      trend: r.score_trend,
      state: stateLabel(latest),
      stale: !!(pos && !pos.is_current),
    });
  }
  return rows;
}

const TIER_ORDER = { active: 0, watching: 1, retired: 2 };

export function sortRows(rows, key = 'streak', direction = 'descending') {
  const dir = direction === 'ascending' ? 1 : -1;
  const value = (row) => (key === 'tier' ? TIER_ORDER[row.tier] : row[key]);
  return [...rows].sort((a, b) => {
    const va = value(a);
    const vb = value(b);
    const aMissing = va === null || va === undefined;
    const bMissing = vb === null || vb === undefined;
    if (aMissing !== bMissing) return aMissing ? 1 : -1;          // missing always last
    if (!aMissing && va !== vb) return (va < vb ? -1 : 1) * dir;
    return a.ticker < b.ticker ? -1 : 1;
  });
}

/** filters: { tiers:Set, entryQualities:Set, minStreak:number, search:string } -> Set of tickers */
export function filterTickers(tracker, filters = {}) {
  const tiers = filters.tiers || new Set(['active', 'watching']);
  const query = String(filters.search || '').trim().toUpperCase();
  const out = new Set();
  for (const [ticker, r] of Object.entries((tracker && tracker.tickers) || {})) {
    if (!tiers.has(r.tier)) continue;
    if (filters.entryQualities && filters.entryQualities.size) {
      const q = ((r.latest && r.latest.entry_quality) || '').toLowerCase();
      if (!filters.entryQualities.has(q)) continue;
    }
    if (finite(filters.minStreak) && r.current_streak_days < filters.minStreak) continue;
    if (query && !ticker.includes(query)) continue;
    out.add(ticker);
  }
  return out;
}

// --- player ------------------------------------------------------------------

/**
 * Deterministic replay controller. All time comes from the injected `now()` and
 * `requestFrame(cb)`/`cancelFrame(id)`, so tests advance it by hand.
 * State: t (fractional frame position), playing, live edge, newAvailable.
 */
export function createPlayer({
  frameCount = 0, stepDurationMs = 800, now, requestFrame, cancelFrame, onUpdate = () => {},
  reducedMotion = false,
}) {
  let count = frameCount;
  let t = Math.max(0, count - 1);
  let playing = false;
  let anim = null;                 // { from, to, start, duration, resolve }
  let handle = null;
  let newAvailable = false;

  const state = () => ({
    t, playing, frameCount: count, index: Math.round(t),
    atLive: count > 0 && Math.abs(t - (count - 1)) < 1e-9 && !anim,
    newAvailable,
  });

  const emit = () => onUpdate(state());

  function stopFrames() {
    if (handle !== null) { cancelFrame(handle); handle = null; }
  }

  function tick() {
    handle = null;
    if (!anim) return;
    const elapsed = now() - anim.start;
    const progress = anim.duration <= 0 ? 1 : Math.min(1, elapsed / anim.duration);
    t = anim.from + (anim.to - anim.from) * progress;
    if (progress >= 1) {
      t = anim.to;
      const done = anim;
      anim = null;
      emit();
      done.after && done.after();
      return;
    }
    emit();
    handle = requestFrame(tick);
  }

  function animateTo(target, after) {
    stopFrames();
    const to = Math.min(Math.max(target, 0), Math.max(0, count - 1));
    if (reducedMotion || Math.abs(to - t) < 1e-9) {
      anim = null;
      t = to;
      emit();
      after && after();
      return;
    }
    // Speed is constant per frame step, so a long jump is not slower than a short one.
    const duration = stepDurationMs * Math.min(Math.abs(to - t), 1);
    anim = { from: t, to, start: now(), duration, after };
    handle = requestFrame(tick);
  }

  function advance() {
    if (!playing) return;
    const next = Math.floor(t + 1e-9) + 1;
    if (next > count - 1) { playing = false; emit(); return; }
    animateTo(next, advance);
  }

  return {
    state,
    play() {
      if (reducedMotion || count < 2) return;        // no autoplay under reduced motion
      if (t >= count - 1 - 1e-9) t = 0;
      playing = true;
      emit();
      advance();
    },
    pause() {
      playing = false;
      stopFrames();
      if (anim) { anim = null; }
      emit();
    },
    seek(index) {
      playing = false;
      stopFrames();
      anim = null;
      t = Math.min(Math.max(Math.round(index), 0), Math.max(0, count - 1));
      emit();
    },
    scrub(position) {                                 // continuous slider value
      playing = false;
      stopFrames();
      anim = null;
      t = Math.min(Math.max(position, 0), Math.max(0, count - 1));
      emit();
    },
    step(delta) {
      playing = false;
      animateTo(Math.round(t) + delta);
    },
    toLive() {
      playing = false;
      newAvailable = false;
      animateTo(count - 1);
    },
    setReducedMotion(value) {
      reducedMotion = !!value;
      if (reducedMotion) { playing = false; stopFrames(); if (anim) { t = anim.to; anim = null; } emit(); }
    },
    /** A newer frame arrived. At the live edge follow it with a tween; when scrubbed back, do not move. */
    setFrameCount(nextCount) {
      const wasLive = state().atLive;
      const grew = nextCount > count;
      count = nextCount;
      if (grew && wasLive) { animateTo(count - 1); }
      else if (grew) { newAvailable = true; emit(); }
      else { t = Math.min(t, Math.max(0, count - 1)); emit(); }
    },
    destroy() { playing = false; stopFrames(); anim = null; },
  };
}
