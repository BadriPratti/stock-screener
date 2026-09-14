// --- "Live" auto-refresh -------------------------------------------------
// This is a local, single-user Flask app with no push/streaming layer, so
// "live" here means: while a view that supports it is open, quietly re-pull
// fresh data on a timer and patch it into the DOM. Stopped on every route
// change so a background view never keeps polling once you've navigated away.

export const LIVE_INTERVAL_MS = 90 * 1000; // 90 seconds — cheap yfinance-only pulls, no LLM cost
let _liveTimer = null;

export function _stopLive() {
  if (_liveTimer) { clearInterval(_liveTimer); _liveTimer = null; }
}
export function _startLive(fn) {
  _stopLive();
  _liveTimer = setInterval(fn, LIVE_INTERVAL_MS);
}
export function liveBadgeHTML() {
  return '<span class="live-badge"><span class="live-dot"></span>Live — updates every 90s</span>';
}

// If a live-refresh tick's job hasn't finished by the time the next tick
// fires (e.g. yfinance is slow), skip that tick instead of stacking another
// overlapping job on top — the next one will pick up fresh data anyway.
const _liveInFlight = new Set();
export async function _liveGuarded(key, fn) {
  if (_liveInFlight.has(key)) return;
  _liveInFlight.add(key);
  try {
    await fn();
  } finally {
    _liveInFlight.delete(key);
  }
}
