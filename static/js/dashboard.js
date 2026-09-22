// Stock Screener dashboard — vanilla JS single-page app. Hash-based routing
// (no router library), fetch() for data, Chart.js (via charts.js) for charts.

import { fetchJSON } from './core/api.js';
import { route, initRouter } from './core/router.js';
import { currentView } from './core/state.js';
import { showToast, toggleReasons } from './core/ui-helpers.js';
import { renderBacktestsView } from './views/backtests.js';
import { renderConsistencyView } from './views/consistency.js';
import { renderMarketView } from './views/market.js';
import { renderPositionsView } from './views/positions.js';
import { renderRunView } from './views/run.js';
import { renderScanView } from './views/scan.js';
import { renderShortlistView } from './views/shortlist.js';

const VIEWS = {
  positions: { title: 'Positions', render: renderPositionsView },
  shortlist: { title: 'Shortlist', render: renderShortlistView },
  market: { title: 'Market', render: renderMarketView },
  backtests: { title: 'Backtests', render: renderBacktestsView },
  consistency: { title: 'Consistency', render: renderConsistencyView },
  run: { title: 'Run Simulation', render: renderRunView },
  scan: { title: 'Full Scan', render: renderScanView },
};

// Inline handlers need an explicit global now that dashboard.js is a module.
window.toggleReasons = toggleReasons;

// "Sync latest" reports a GIT fact (did `git pull` fetch new commits) which
// is a different question from "is the data actually recent" — the daily
// scan is a separate scheduled job that can go a while without producing a
// new commit (weekends, a workflow failure, zero qualifying candidates) even
// though `git pull` correctly and truthfully says "already up to date" every
// time. This surfaces the shortlist's own `generated` timestamp next to the
// button so that gap is visible instead of silently confusing.
const dataFreshnessEl = document.getElementById('dataFreshness');
function _relativeAge(isoString) {
  const then = new Date(isoString);
  const hours = (Date.now() - then.getTime()) / 36e5;
  if (hours < 1) return 'less than an hour ago';
  if (hours < 24) return `${Math.round(hours)}h ago`;
  const days = Math.round(hours / 24);
  return `${days} day${days === 1 ? '' : 's'} ago`;
}
async function refreshDataFreshness() {
  try {
    const data = await fetchJSON('/api/shortlist');
    dataFreshnessEl.textContent = data.generated
      ? `Latest scan: ${_relativeAge(data.generated)}`
      : 'Latest scan: never run';
  } catch {
    // Freshness is a nice-to-have status readout — a failed fetch here
    // shouldn't interrupt anything else on the page.
  }
}

// silent=true (used by auto-sync): stays quiet unless it actually pulls new
// data, so a background sync every few minutes doesn't spam toasts for
// "already up to date" or for a transient failure — the manual button still
// surfaces both of those explicitly when you click it yourself.
async function doSync(silent) {
  let res;
  try {
    res = await fetchJSON('/api/sync', { method: 'POST' });
    if (res.success) {
      window.dispatchEvent(new CustomEvent('stock-data-updated', { detail: { output: res.output || '' } }));
      if (!res.output.includes('Already up to date')) {
        const formInUse = silent && (currentView === 'run' || currentView === 'scan');
        showToast(formInUse ? 'Pulled latest data — will show on your next visit to this page.' : 'Pulled latest data — refreshing…');
        if (!formInUse && currentView !== 'market') route();
      } else if (!silent) {
        showToast('Already up to date.');
      }
    } else if (!silent) {
      showToast('Sync failed: ' + (res.output || 'unknown error').slice(0, 200));
    }
  } catch (e) {
    if (!silent) showToast('Sync error: ' + e.message);
    res = { success: false };
  }
  // Outside the try/catch above on purpose: this reflects the daily scan's
  // own data age, a separate concern from whether this particular git pull
  // succeeded — refreshDataFreshness() has its own internal error handling,
  // so it must never surface as a (misleading) "Sync error" toast.
  refreshDataFreshness();
  return res;
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

initRouter(VIEWS);
