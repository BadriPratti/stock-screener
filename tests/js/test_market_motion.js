// Characterization tests for static/js/core/market-motion.js, the pure model behind
// the Market tab's persistent Buy Opportunity Map (frames -> render items, filters,
// tracker table rows, and the replay player).
//
// The rules locked in here are the ones that would silently mislead if they
// regressed: points only move between two REAL observations, a point with no
// honest coordinates is held (never sent to 0,0), a newly *located* ticker is not
// shown as a new opportunity, and nothing tweens across a scoring-version change.
//
// Run with: node tests/js/test_market_motion.js

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const MODULE = path.join(__dirname, '..', '..', 'static', 'js', 'core', 'market-motion.js');
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B50}]/u;
const linear = (p) => p;

function q(ticker, score, rs, extra = {}) {
  return { ticker, evaluation: 'qualified', score, rs, phase: 2, entry_quality: 'Good', ...extra };
}
function nq(ticker, score, rs) {
  return { ticker, evaluation: 'not_qualified', score, rs, phase: 2, drop_reason: 'below_buy_threshold' };
}
function ns(ticker, reason = 'phase_3') {
  return { ticker, evaluation: 'not_scored', phase: 3, drop_reason: reason };
}
function frame(date, points, extra = {}) {
  return {
    run_id: `${date}-x`, run_kind: 'daily_full', session_date: date, generated_at: `${date}T17:00:00Z`,
    scoring_version: 'v1', coverage: { kind: 'complete_for_scope' }, points, ...extra,
  };
}
const byTicker = (items) => Object.fromEntries(items.map(i => [i.ticker, i]));
const near = (a, b, msg) => assert.ok(Math.abs(a - b) < 1e-9, `${msg}: ${a} vs ${b}`);

async function main() {
  const m = await import(`file://${MODULE}`);
  const opts = { easing: linear };

  // --- tracks ---------------------------------------------------------------
  const frames = [
    frame('2026-09-14', [q('A', 100, 0.2), nq('N', 50, 0.0)]),
    frame('2026-09-15', [q('A', 110, 0.4), q('N', 90, 0.1)]),
    frame('2026-09-16', [ns('A'), q('N', 95, 0.3)]),
  ];
  const tracks = m.buildTracks(frames);
  assert.deepStrictEqual([...tracks.keys()].sort(), ['A', 'N']);
  assert.strictEqual(tracks.get('N').firstQualified, 1, 'a ticker is tracked only from its first qualified frame');

  // --- integer positions: categories, coordinates, carry-forward -------------
  let at = byTicker(m.itemsAt(frames, tracks, 0, opts));
  assert.deepStrictEqual(Object.keys(at), ['A'], 'N is not tracked yet at frame 0 (its earlier not_qualified row is pre-history)');
  assert.strictEqual(at.A.category, 'active');
  near(at.A.x, 0.2, 'x = rs'); near(at.A.y, 80, 'y = score / 125 * 100');

  at = byTicker(m.itemsAt(frames, tracks, 2, opts));
  assert.strictEqual(at.A.category, 'stale', 'not_scored is stale');
  near(at.A.x, 0.4, 'stale dot is held at its LAST REAL x'); near(at.A.y, 88, 'and last real y');
  assert.ok(at.A.x !== 0 || at.A.y !== 0, 'never sent to the origin');
  assert.strictEqual(at.A.dropReason, 'phase_3');
  assert.strictEqual(at.A.stale, true);
  assert.strictEqual(at.N.category, 'active');

  // --- interpolation between two real observations ----------------------------
  const mid = byTicker(m.itemsAt(frames, tracks, 0.5, opts));
  near(mid.A.x, 0.3, 'midpoint x'); near(mid.A.y, 84, 'midpoint y (80 -> 88)');
  assert.strictEqual(mid.N.entering, true, 'N first qualifies in frame 1');
  assert.strictEqual(mid.N.bloom, true, 'a genuinely new opportunity blooms in');
  near(mid.N.scale, 0.5, 'bloom scale follows progress'); near(mid.N.alpha, 0.5, 'bloom alpha follows progress');
  assert.ok(!byTicker(m.itemsAt(frames, tracks, 0, opts)).N, 'and it is absent exactly at the frame before it exists');

  // exit: qualified -> not_scored holds position and flips to a stale ghost at the midpoint
  const exit1 = byTicker(m.itemsAt(frames, tracks, 1.25, opts)).A;
  assert.strictEqual(exit1.exiting, true); assert.strictEqual(exit1.category, 'active');
  const exit2 = byTicker(m.itemsAt(frames, tracks, 1.75, opts)).A;
  assert.strictEqual(exit2.category, 'stale');
  near(exit2.x, 0.4, 'exit does not fly anywhere: no coordinates exist to fly to');

  // default easing is monotonic and hits the endpoints
  assert.strictEqual(m.easeInOutCubic(0), 0); assert.strictEqual(m.easeInOutCubic(1), 1);
  assert.ok(m.easeInOutCubic(0.25) < 0.25 && m.easeInOutCubic(0.75) > 0.75);

  // not_qualified keeps real coordinates and is "watching" (hollow) at the real new position
  const drop = [frame('d1', [q('W', 100, 0.3)]), frame('d2', [nq('W', 57.5, 0.05)])];
  const dTracks = m.buildTracks(drop);
  const w = byTicker(m.itemsAt(drop, dTracks, 1, opts)).W;
  assert.strictEqual(w.category, 'watching'); near(w.y, 46, '57.5 / 125'); near(w.x, 0.05, 'real x');

  // --- coverage boundary: newly LOCATED is not a new opportunity ----------------
  const cov = [
    frame('c1', [q('A', 100, 0.2)], { run_kind: 'legacy_report', coverage: { kind: 'top50_only' } }),
    frame('c2', [q('A', 101, 0.2), q('Z', 90, 0.5)]),                        // Z absent from the narrow frame
    frame('c3', [q('A', 102, 0.2), q('Z', 91, 0.5), q('NEW', 80, 0.1)]),
  ];
  const cTracks = m.buildTracks(cov);
  const located = byTicker(m.itemsAt(cov, cTracks, 0.5, opts)).Z;
  assert.strictEqual(located.bloom, false, 'no entry bloom for a ticker that only became visible');
  near(located.scale, 1, 'drawn at full size'); near(located.alpha, 1, 'and full opacity');
  const genuinelyNew = byTicker(m.itemsAt(cov, cTracks, 1.5, opts)).NEW;
  assert.strictEqual(genuinelyNew.bloom, true, 'a new ticker between two complete frames still blooms');

  // --- scoring-version boundary: snap, never tween ------------------------------
  const ver = [frame('v1', [q('A', 100, 0.2)]), frame('v2', [q('A', 110, 0.6)], { scoring_version: 'v2' })];
  const vTracks = m.buildTracks(ver);
  const before = byTicker(m.itemsAt(ver, vTracks, 0.4, opts)).A;
  const after = byTicker(m.itemsAt(ver, vTracks, 0.6, opts)).A;
  near(before.x, 0.2, 'before the midpoint it stays on the old model'); near(after.x, 0.6, 'after it snaps to the new one');

  // --- visibility filter, decimation, trails -------------------------------------
  const only = m.itemsAt(frames, tracks, 1, { ...opts, isVisible: (t) => t === 'N' });
  assert.deepStrictEqual(only.map(i => i.ticker), ['N']);

  const many = [];
  for (let i = 0; i < 10; i++) many.push({ ticker: `A${i}`, category: 'active', positionFrame: 1 });
  for (let i = 0; i < 10; i++) many.push({ ticker: `W${i}`, category: 'watching', positionFrame: i });
  for (let i = 0; i < 10; i++) many.push({ ticker: `S${i}`, category: 'stale', positionFrame: i });
  let d = m.decimate(many, 15);
  assert.strictEqual(d.items.length, 15); assert.strictEqual(d.dropped, 15);
  assert.strictEqual(d.items.filter(i => i.category === 'active').length, 10, 'every active point survives decimation');
  assert.deepStrictEqual(d.items.filter(i => i.category === 'watching').map(i => i.ticker), ['W9', 'W8', 'W7', 'W6', 'W5'],
    'then watching by most recent observation, stale last');
  d = m.decimate(many, 5);
  assert.strictEqual(d.items.length, 10, 'active points are never dropped, even over budget');
  assert.strictEqual(m.decimate(many, 100).dropped, 0);

  const tail = m.trailPoints(frames, tracks, 'A', 2, 3);
  assert.deepStrictEqual(tail.map(p => p.frame), [0, 1], 'only real positioned observations, oldest first (frame 2 has none)');
  assert.deepStrictEqual(m.trailPoints(frames, tracks, 'A', 1.9, 1).map(p => p.frame), [0, 1]);
  assert.deepStrictEqual(m.trailPoints(frames, tracks, 'nope', 1), []);

  // --- encodings / domain ---------------------------------------------------------
  assert.strictEqual(m.radiusForStreak(0), 3); assert.strictEqual(m.radiusForStreak(1), 4);
  assert.strictEqual(m.radiusForStreak(10), 10); assert.strictEqual(m.radiusForStreak(40), 10);
  assert.ok(m.radiusForStreak(5) > 4 && m.radiusForStreak(5) < 10);
  assert.strictEqual(m.radiusForStreak(null), 3);

  const dom = m.chartDomain(frames);
  assert.ok(dom.xMin <= 0 && dom.xMax >= 0.4, 'x domain always includes zero and every point');
  assert.strictEqual(dom.yMin, 40); assert.strictEqual(dom.yMax, 100); near(dom.thresholdY, 48, '60/125');
  assert.strictEqual(m.chartDomain([frame('x', [nq('L', 30, -0.3)])]).yMin, 20, 'a lower score widens the fixed domain');

  // --- labels -------------------------------------------------------------------
  assert.strictEqual(m.frameLabel(frame('2026-09-18', [])), 'Sep 18 (daily scan)');
  assert.strictEqual(m.frameLabel(frame('2026-09-18', [], { run_kind: 'legacy_report' })), 'Sep 18 (daily scan, top 50 only)');
  assert.strictEqual(
    m.frameLabel(frame('2026-09-18', [], { run_kind: 'intraday_rescore', generated_at: '2026-09-18T17:35:00Z' })),
    'Sep 18 13:35 ET (intraday)', 'intraday label is in Eastern time');
  assert.strictEqual(m.dropReasonLabel('phase_3'), 'Phase 3 (not an uptrend)');
  assert.strictEqual(m.dropReasonLabel('Not in Phase 2 (currently Phase 4) - Minervini requires confirmed uptrend'), 'Phase 4 (not an uptrend)');
  assert.strictEqual(m.dropReasonLabel('Fails Minervini Trend Template (5/8 criteria passed)'), 'Fails the trend template');
  assert.strictEqual(m.stateLabel({ evaluation: 'not_qualified' }), 'Below the buy line');
  assert.strictEqual(m.stateLabel(null), 'Unknown');

  // --- tracker table + filters ------------------------------------------------------
  const tracker = {
    tickers: {
      AAA: { tier: 'active', current_streak_days: 5, longest_streak_days: 5, sessions_qualified: 5, sessions_observed: 5,
        first_qualified: '2026-09-14', last_qualified: '2026-09-18', score_trend: 2.5, latest_daily_score: 110,
        latest: { evaluation: 'qualified', entry_quality: 'Good' }, position: { score: 110, rs: 0.4, is_current: true } },
      BBB: { tier: 'watching', current_streak_days: 0, longest_streak_days: 2, sessions_qualified: 2, sessions_observed: 4,
        first_qualified: '2026-09-15', last_qualified: '2026-09-16', score_trend: null, latest_daily_score: null,
        latest: { evaluation: 'not_scored', drop_reason: 'phase_3', entry_quality: 'Extended' }, position: { score: 90, rs: 0.1, is_current: false } },
      CCC: { tier: 'retired', current_streak_days: 0, longest_streak_days: 1, sessions_qualified: 1, sessions_observed: 12,
        first_qualified: '2026-09-01', last_qualified: '2026-09-01', score_trend: null, latest_daily_score: 70,
        latest: null, position: null },
    },
  };
  const rows = m.buildTrackerRows(tracker);
  const aaa = rows.find(r => r.ticker === 'AAA');
  assert.strictEqual(aaa.sessionsText, '5 of 5'); assert.strictEqual(aaa.state, 'Qualified'); assert.strictEqual(aaa.stale, false);
  const bbb = rows.find(r => r.ticker === 'BBB');
  assert.strictEqual(bbb.state, 'Phase 3 (not an uptrend)'); assert.strictEqual(bbb.stale, true, 'position older than the latest result is flagged');
  assert.deepStrictEqual(m.sortRows(rows, 'streak').map(r => r.ticker), ['AAA', 'BBB', 'CCC'], 'ties fall back to ticker order');
  assert.deepStrictEqual(m.sortRows(rows, 'score', 'ascending').map(r => r.ticker), ['CCC', 'BBB', 'AAA']);
  assert.deepStrictEqual(m.sortRows(rows, 'trend', 'descending').map(r => r.ticker), ['AAA', 'BBB', 'CCC'], 'missing values sort last');
  assert.deepStrictEqual(m.sortRows(rows, 'trend', 'ascending').map(r => r.ticker), ['AAA', 'BBB', 'CCC'], 'and stay last ascending');
  assert.deepStrictEqual(m.sortRows(rows, 'tier', 'ascending').map(r => r.ticker), ['AAA', 'BBB', 'CCC']);

  assert.deepStrictEqual([...m.filterTickers(tracker)].sort(), ['AAA', 'BBB'], 'default hides retired');
  assert.deepStrictEqual([...m.filterTickers(tracker, { tiers: new Set(['active', 'watching', 'retired']) })].sort(), ['AAA', 'BBB', 'CCC']);
  assert.deepStrictEqual([...m.filterTickers(tracker, { minStreak: 3 })], ['AAA']);
  assert.deepStrictEqual([...m.filterTickers(tracker, { entryQualities: new Set(['extended']) })], ['BBB']);
  assert.deepStrictEqual([...m.filterTickers(tracker, { search: ' bb ' })], ['BBB']);

  // --- player (injected clock + scheduler) ------------------------------------------
  function harness(opts2 = {}) {
    let clock = 0; let nextId = 1; const pending = new Map(); const updates = [];
    const player = m.createPlayer({
      frameCount: 3, stepDurationMs: 800, now: () => clock,
      requestFrame: (cb) => { const id = nextId++; pending.set(id, cb); return id; },
      cancelFrame: (id) => pending.delete(id),
      onUpdate: (s) => updates.push(s), ...opts2,
    });
    const advance = (ms) => { clock += ms; const cbs = [...pending.values()]; pending.clear(); cbs.forEach(cb => cb()); };
    return { player, advance, pending, updates, time: () => clock };
  }

  let h = harness();
  assert.strictEqual(h.player.state().t, 2, 'starts at the live edge');
  assert.strictEqual(h.player.state().atLive, true);
  h.player.seek(0);
  h.player.play();
  assert.strictEqual(h.player.state().playing, true);
  h.advance(400); near(h.player.state().t, 0.5, 'half way through the first step');
  h.advance(400); near(h.player.state().t, 1, 'lands exactly on frame 1');
  h.advance(800); near(h.player.state().t, 2, 'continues to the last frame');
  assert.strictEqual(h.player.state().playing, false, 'stops at the end');
  assert.strictEqual(h.pending.size, 0, 'and leaves no frame callback scheduled');

  h = harness(); h.player.seek(0); h.player.play(); h.advance(300);
  h.player.pause();
  const frozen = h.player.state().t;
  h.advance(5000); near(h.player.state().t, frozen, 'pause freezes the position'); assert.strictEqual(h.pending.size, 0);

  h = harness(); h.player.step(-1); h.advance(800); near(h.player.state().t, 1, 'step back animates one frame');
  h.player.scrub(0.4); near(h.player.state().t, 0.4, 'scrub sets a continuous position instantly'); assert.strictEqual(h.player.state().playing, false);

  h = harness({ reducedMotion: true });
  h.player.play(); assert.strictEqual(h.player.state().playing, false, 'no autoplay under reduced motion');
  h.player.step(-1); near(h.player.state().t, 1, 'steps jump instantly, no animation'); assert.strictEqual(h.pending.size, 0);
  h.player.toLive(); near(h.player.state().t, 2, 'live jump is instant too');

  // live update: follows at the live edge, does NOT yank when scrubbed into history
  h = harness(); h.player.setFrameCount(4); assert.strictEqual(h.player.state().frameCount, 4);
  h.advance(800); near(h.player.state().t, 3, 'at the live edge a new frame is followed with a tween');
  h = harness(); h.player.seek(0); h.player.setFrameCount(4);
  near(h.player.state().t, 0, 'scrubbed back: the position does not move'); assert.strictEqual(h.player.state().newAvailable, true);
  h.player.toLive(); h.advance(800); h.advance(800); h.advance(800);
  near(h.player.state().t, 3); assert.strictEqual(h.player.state().newAvailable, false);

  h = harness(); h.player.seek(0); h.player.play(); h.player.destroy();
  assert.strictEqual(h.pending.size, 0, 'destroy cancels any scheduled frame');
  assert.strictEqual(m.createPlayer({ frameCount: 1, now: () => 0, requestFrame: () => 1, cancelFrame: () => {} }).state().t, 0);

  // --- project rule: no emoji in the module ----------------------------------------------
  assert.ok(!EMOJI.test(fs.readFileSync(MODULE, 'utf8')), 'no emoji in source');

  console.log('test_market_motion.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.stack || e.message); process.exit(1); });
