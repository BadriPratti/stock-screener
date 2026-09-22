import { fetchJSON } from '../core/api.js';
import { startJob } from '../core/jobs.js';
import { _liveGuarded, _startLive, liveBadgeHTML } from '../core/refresh.js';
import { content, currentView, pageMeta } from '../core/state.js';
import { loadConsistency } from '../core/pick-history.js';
import { mountMarketMap } from '../components/market-map.js';
import {
  analysisButtonHTML,
  cleanEmoji,
  escapeHtml,
  fidelityLink,
  loadMomentumStatus,
  paintMomentumSlots,
  redditCell,
  refreshAnalysisModal,
  renderTop20Table,
  safeHref,
  wireAnalysisButtons,
} from '../core/ui-helpers.js';

let _marketTop20Tickers = [];
let _marketSignalPrices = {};
let _marketSignalTickers = [];
let _marketSignalMeta = {};
let _marketMapController = null;
let _marketScanRequestToken = 0;
const MARKET_SECTION_IDS = ['map', 'overview', 'top20', 'signals'];
let _marketSection = 'map';
let _marketMapMount = null;
let _marketMapMountPromise = null;

export function marketSignalAnalysisSeries(signal, kind, history, contextKey = signal?.ticker) {
  if (!signal || !history || !history.length) return null;
  const isBuy = kind === 'buy';
  return {
    history,
    entry: null,
    stop: isBuy ? signal.stop_loss : signal.breakdown_level,
    meta: {
      contextKey,
      stopLabel: isBuy ? 'Scanner stop' : 'Breakdown level',
    },
  };
}

// The midday workflow scans a random ~100-stock sample and always writes the
// newest report, so "newest scan" is usually a sample, not the market. Samples
// stay selectable (and clearly labelled) but are never the default.
export function scanOptionLabel(scan) {
  const label = String(scan.date).replace('_', ' ');
  return scan.is_sample ? `${label} (${scan.total_universe}-stock sample)` : label;
}

export function pickDefaultScan(scans) {
  return scans.find(s => !s.is_sample) || scans[0];
}

function _normaliseMarketSection(sectionId) {
  return MARKET_SECTION_IDS.includes(sectionId) ? sectionId : 'map';
}

function _readMarketSection() {
  try {
    return _normaliseMarketSection(sessionStorage.getItem('market:section') || 'map');
  } catch {
    return 'map';
  }
}

export function _activateMarketSection(sectionId) {
  const activeSection = _normaliseMarketSection(sectionId);
  _marketSection = activeSection;
  try {
    sessionStorage.setItem('market:section', activeSection);
  } catch {
    // Storage may be unavailable in a restricted webview; tab switching still works.
  }

  const tabs = [...document.querySelectorAll('[role="tab"][data-market-section]')];
  tabs.forEach(tab => {
    const active = tab.dataset.marketSection === activeSection;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    tab.classList.toggle('active', active);
  });
  document.querySelectorAll('.market-section-panel').forEach(panel => {
    panel.hidden = panel.dataset.marketSectionPanel !== activeSection;
  });

  if (_marketMapController) {
    _marketMapController.setActive(activeSection === 'map');
  } else if (activeSection === 'map' && _marketMapMount && !_marketMapMountPromise) {
    _marketMapMountPromise = _marketMapMount().catch(() => null);
  }
}

export function _wireMarketSectionTabs() {
  const tabs = [...document.querySelectorAll('[role="tab"][data-market-section]')];
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => _activateMarketSection(tab.dataset.marketSection));
    tab.addEventListener('keydown', (event) => {
      let nextIndex;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = tabs.length - 1;
      if (nextIndex === undefined) return;
      event.preventDefault();
      const nextTab = tabs[nextIndex];
      _activateMarketSection(nextTab.dataset.marketSection);
      nextTab.focus();
    });
  });
}

function _restoreMarketSection() {
  _wireMarketSectionTabs();
  _activateMarketSection(_readMarketSection());
}

export async function renderMarketView() {
  const viewToken = ++_marketScanRequestToken;
  if (_marketMapController) {
    _marketMapController.destroy();
    _marketMapController = null;
  }
  _marketMapMount = null;
  _marketMapMountPromise = null;
  const scans = await fetchJSON('/api/scans');
  if (currentView !== 'market' || viewToken !== _marketScanRequestToken) return; // navigated away before this resolved
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
      <span class="scan-select-note" id="scanSelectNote"></span>
    </div>
    <div id="marketBody"></div>`;
  const sel = document.getElementById('scanSelect');
  scans.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.path;
    opt.textContent = scanOptionLabel(s);
    sel.appendChild(opt);
  });
  sel.addEventListener('change', () => loadMarketScan(sel.value));
  const defaultScan = pickDefaultScan(scans);
  sel.value = defaultScan.path;
  if (scans[0].is_sample && defaultScan !== scans[0]) {
    document.getElementById('scanSelectNote').textContent =
      'Showing the latest full-market scan. Newer sample scans are in the list but not selected by default.';
  }
  loadMarketScan(defaultScan.path);
  _startLive(() => {
    _liveGuarded('market-motion', () => _marketMapController?.pollLatest());
    _liveGuarded('market-news', () => loadMarketNews(true));
    _liveGuarded('market-momentum', () => loadMomentumStatus(
      _marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap)
    ));
    _liveGuarded('market-signal-charts', () => loadMarketSignalCharts(_marketSignalTickers, true));
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

export function _newsSectionHTML(group, title, bodyHTML) {
  return `<div class="card" id="news-${group}-card"><h2>${title} ${liveBadgeHTML()}</h2><div id="news-${group}-body">${bodyHTML}</div></div>`;
}

export async function _loadNewsGroup(group, tickers, emptyMsg, silent) {
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

// Pure by design (exported for tests/js characterization coverage): maps
// buy_signals to {x, y, signal} scatter points. Only keeps signals with a
// finite score, a positive max_score, and a finite rs — a missing/null field
// on any of these would otherwise plot as (0,0) or NaN, silently misleading
// rather than just being omitted. Y is score-as-percentage-of-max rather
// than the raw score, since max_score isn't always the same fixed number.
export function buildBuyOpportunityPoints(buySignals) {
  return (buySignals || [])
    .filter(s => Number.isFinite(s.score) && Number.isFinite(s.max_score) && s.max_score > 0 && Number.isFinite(s.rs))
    .map(s => ({ x: s.rs, y: (s.score / s.max_score) * 100, signal: s }));
}

function _buyOpportunityChartCardHTML(buySignals) {
  const plotted = buildBuyOpportunityPoints(buySignals).length;
  const total = (buySignals || []).length;
  const omitted = total - plotted;
  const omittedNote = omitted > 0
    ? ` (${omitted} signal${omitted === 1 ? '' : 's'} without a plottable score/RS not shown)`
    : '';
  return `
    <div class="card">
      <h2>Buy Opportunity Map</h2>
      <div class="card-sub">Right = stronger relative momentum · Up = higher scanner conviction${omittedNote}</div>
      <div class="scatter-chart-wrap"><canvas id="marketScatterChart"></canvas></div>
      <div style="color:var(--muted);font-size:11px;margin-top:8px">Hover a dot for details, click to jump to it in the Buy Signals table below.</div>
    </div>`;
}

function _renderBuyOpportunityChart(buySignals) {
  const points = buildBuyOpportunityPoints(buySignals);
  renderMarketScatterChart('marketScatterChart', points, _showBuySignal);
}

// A row this jumps to now lives inside a page-level tab panel (MR-002) that
// may be `hidden`, and the tracker table itself may still be behind its
// closed-by-default disclosure (MR-003) — scrolling to it before making it
// visible would silently no-op, so the outer section (and, for the tracker
// table, the map's own selection API rather than reaching into its DOM
// directly) must be activated first.
function _showMarketTicker(ticker) {
  const buyRow = document.querySelector(`#buySignalsBody tr[data-ticker="${ticker}"]`);
  if (buyRow) {
    _activateMarketSection('signals');
    _activateSignalTab('buy');
    _highlightBuyRow({ ticker });
    return;
  }
  // Only reachable while the Map tab is already active (that's the only time
  // the persistent map's dots are interactive), so no outer-section switch is
  // needed here — just hand off to the map's own selection API instead of
  // reaching into its tracked-table DOM directly, since MR-003 only builds
  // those rows once the table's disclosure has actually been opened.
  _marketMapController?.selectTicker(ticker);
}

export function _showBuySignal(signal) {
  _activateMarketSection('signals');
  _activateSignalTab('buy');
  _highlightBuyRow(signal);
}

// Scrolls to and briefly pulses a ticker's row in the Buy Signals table —
// used as the scatter chart's click handler. Does not open the Fidelity
// trade link directly: a dense chart is easy to mis-click, and jumping to
// the row (rather than an outbound broker link) lets the user confirm the
// full breakdown before intentionally clicking Trade themselves.
function _highlightBuyRow(signal) {
  const row = document.querySelector(`#buySignalsBody tr[data-ticker="${signal.ticker}"]`);
  if (!row) return;
  row.scrollIntoView({ behavior: 'smooth', block: 'center' });
  row.classList.add('row-highlight-pulse');
  setTimeout(() => row.classList.remove('row-highlight-pulse'), 2000);
}

function _marketSignalSeries(contextKey) {
  const signalMeta = _marketSignalMeta[contextKey];
  if (!signalMeta) return null;
  const h = _marketSignalPrices[signalMeta.ticker];
  if (!h || !h.length) return null;
  return marketSignalAnalysisSeries(signalMeta.signal, signalMeta.kind, h, contextKey);
}

// Fetches price history for every ticker shown in the Buy/Sell tables (both,
// regardless of which tab is active — the chart-toggle button on a sell row
// works even if the sell panel hasn't been the visible tab yet since the
// tickers/prices are fetched once up front, not per-tab). Reuses the same
// batched price-history job Shortlist/Positions use — one job, not one
// request per ticker.
async function loadMarketSignalCharts(tickers, silent) {
  if (!tickers.length) return;
  await startJob('price-history', { tickers, group: 'market-signals' }, async (st) => {
    if (st.status !== 'success') return;
    const data = await fetchJSON('/api/price-history/market-signals');
    _marketSignalPrices = data.prices || {};
    if (silent) {
      refreshAnalysisModal(_marketSignalSeries);
    } else {
      const card = document.getElementById('marketSignalsCard');
      if (card) wireAnalysisButtons(card, _marketSignalSeries);
    }
  });
}

function _signalTabLabel(label, shownCount, totalCount) {
  return totalCount !== shownCount
    ? `${label} (${shownCount} of ${totalCount})`
    : `${label} (${shownCount})`;
}

export function _signalTabsHTML(scan) {
  const buyTotal = scan.stats.buy_count ?? scan.buy_signals.length;
  const sellTotal = scan.stats.sell_count ?? scan.sell_signals.length;
  return `
    <div class="card" id="marketSignalsCard">
      <div class="signal-tabs-header">
        <div>
          <h2 style="margin-bottom:2px">Market Signals</h2>
          <div class="card-sub" style="margin:0">Calculated ${escapeHtml(scan.generated || scan.scan_date || 'unknown')}</div>
        </div>
        <div class="signal-tabs" role="tablist" aria-label="Market signal type">
          <button class="btn signal-tab active" id="buySignalsTab" type="button" role="tab" data-signal-tab="buy" aria-selected="true" aria-controls="buySignalsPanel" tabindex="0">${_signalTabLabel('Buy', scan.buy_signals.length, buyTotal)}</button>
          <button class="btn signal-tab" id="sellSignalsTab" type="button" role="tab" data-signal-tab="sell" aria-selected="false" aria-controls="sellSignalsPanel" tabindex="-1">${_signalTabLabel('Sell', scan.sell_signals.length, sellTotal)}</button>
        </div>
      </div>
      <div id="buySignalsPanel" role="tabpanel" aria-labelledby="buySignalsTab">
        <div style="overflow-x:auto"><table class="signal-table">
          <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Price</th><th scope="col">Score</th><th scope="col">Entry</th><th scope="col">Stop Loss</th><th scope="col">R:R</th><th scope="col">RS</th><th scope="col">Reddit</th><th scope="col">Key Reasons</th><th scope="col">Trade</th></tr></thead>
          <tbody id="buySignalsBody">${renderBuyRows(scan.buy_signals)}</tbody>
        </table></div>
      </div>
      <div id="sellSignalsPanel" role="tabpanel" aria-labelledby="sellSignalsTab" hidden>
        <div style="overflow-x:auto"><table class="signal-table">
          <thead><tr><th scope="col">#</th><th scope="col">Ticker</th><th scope="col">Price</th><th scope="col">Score</th><th scope="col">Severity</th><th scope="col">Breakdown</th><th scope="col">Reddit</th><th scope="col">Reasons</th><th scope="col">Trade</th></tr></thead>
          <tbody id="sellSignalsBody"></tbody>
        </table></div>
      </div>
    </div>`;
}

export function _activateSignalTab(name, sellSignals = []) {
  const buyTab = document.getElementById('buySignalsTab');
  const sellTab = document.getElementById('sellSignalsTab');
  const buyPanel = document.getElementById('buySignalsPanel');
  const sellPanel = document.getElementById('sellSignalsPanel');
  if (!buyTab || !sellTab || !buyPanel || !sellPanel) return;

  const showBuy = name === 'buy';
  if (!showBuy) {
    const sellBody = document.getElementById('sellSignalsBody');
    if (sellBody && sellBody.dataset.rendered !== 'true') {
      sellBody.innerHTML = renderSellRows(sellSignals);
      sellBody.dataset.rendered = 'true';
      // Sell rows' analysis buttons don't exist until this lazy render,
      // so they must be wired here rather than only at initial page load —
      // the same reason the Buy panel's toggles are wired separately, right
      // after loadMarketSignalCharts's price fetch resolves.
      const card = document.getElementById('marketSignalsCard');
      if (card) wireAnalysisButtons(card, _marketSignalSeries);
    }
  }

  buyTab.setAttribute('aria-selected', String(showBuy));
  sellTab.setAttribute('aria-selected', String(!showBuy));
  buyTab.tabIndex = showBuy ? 0 : -1;
  sellTab.tabIndex = showBuy ? -1 : 0;
  buyTab.classList.toggle('active', showBuy);
  sellTab.classList.toggle('active', !showBuy);
  buyPanel.hidden = !showBuy;
  sellPanel.hidden = showBuy;
}

export function _wireSignalTabs(sellSignals) {
  const tabs = [...document.querySelectorAll('[role="tab"][data-signal-tab]')];
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => _activateSignalTab(tab.dataset.signalTab, sellSignals));
    tab.addEventListener('keydown', (event) => {
      let nextIndex;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = tabs.length - 1;
      if (nextIndex === undefined) return;
      event.preventDefault();
      const nextTab = tabs[nextIndex];
      _activateSignalTab(nextTab.dataset.signalTab, sellSignals);
      nextTab.focus();
    });
  });
}

export async function loadMarketScan(path) {
  const requestToken = ++_marketScanRequestToken;
  const [scan, top20] = await Promise.all([
    fetchJSON('/api/scan?path=' + encodeURIComponent(path)),
    fetchJSON('/api/top20'),
  ]);
  if (currentView !== 'market' || requestToken !== _marketScanRequestToken) return; // stale selections never paint
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
    <div class="market-section-tabs" role="tablist" aria-label="Market sections">
      <button class="btn market-section-tab active" id="marketSectionTab-map" type="button" role="tab" data-market-section="map" aria-selected="true" aria-controls="marketSectionPanel-map" tabindex="0">Buy Opportunity Map</button>
      <button class="btn market-section-tab" id="marketSectionTab-overview" type="button" role="tab" data-market-section="overview" aria-selected="false" aria-controls="marketSectionPanel-overview" tabindex="-1">Overview</button>
      <button class="btn market-section-tab" id="marketSectionTab-top20" type="button" role="tab" data-market-section="top20" aria-selected="false" aria-controls="marketSectionPanel-top20" tabindex="-1">Top 20</button>
      <button class="btn market-section-tab" id="marketSectionTab-signals" type="button" role="tab" data-market-section="signals" aria-selected="false" aria-controls="marketSectionPanel-signals" tabindex="-1">Signals</button>
    </div>
    <div class="market-section-panel" id="marketSectionPanel-map" role="tabpanel" aria-labelledby="marketSectionTab-map" data-market-section-panel="map">
      <div id="marketMotionMount"><div class="card"><span class="spinner"></span> Loading persistent Buy Opportunity Map...</div></div>
    </div>
    <div class="market-section-panel" id="marketSectionPanel-overview" role="tabpanel" aria-labelledby="marketSectionTab-overview" data-market-section-panel="overview" hidden>
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
      <div id="newsSections" style="margin-top:24px"></div>
    </div>
    <div class="market-section-panel" id="marketSectionPanel-top20" role="tabpanel" aria-labelledby="marketSectionTab-top20" data-market-section-panel="top20" hidden>
      ${renderTop20Table(top20.top20 || [])}
    </div>
    <div class="market-section-panel" id="marketSectionPanel-signals" role="tabpanel" aria-labelledby="marketSectionTab-signals" data-market-section-panel="signals" hidden>
      ${_signalTabsHTML(scan)}
    </div>
  `;

  renderBreadthChart('breadthChart', scan.breadth);
  _wireSignalTabs(scan.sell_signals);
  if (_marketMapController) {
    _marketMapController.destroy();
    _marketMapController = null;
  }
  _marketMapMountPromise = null;
  _marketMapMount = async () => {
    const mountedMap = await mountMarketMap({
      mount: document.getElementById('marketMotionMount'),
      fetchJSON,
      chartApi: window.StockCharts,
      fallback: () => _renderBuyOpportunityChart(scan.buy_signals),
      onTickerClick: _showMarketTicker,
      isCurrent: () => currentView === 'market' && requestToken === _marketScanRequestToken,
    });
    if (currentView !== 'market' || requestToken !== _marketScanRequestToken) {
      mountedMap?.destroy();
      return null;
    }
    _marketMapController = mountedMap;
    _marketMapController?.setActive(_marketSection === 'map');
    return mountedMap;
  };
  _restoreMarketSection();
  loadMarketNews();
  if (_marketSection === 'map') await _marketMapMountPromise;
  if (currentView !== 'market' || requestToken !== _marketScanRequestToken) return;

  // The live-refresh closure must always read the current scan selection.
  _marketTop20Tickers = (top20.top20 || []).map(s => s.ticker);
  loadMomentumStatus(_marketTop20Tickers, 'market-top20', (statusMap) => paintMomentumSlots(_marketTop20Tickers, statusMap));
  loadConsistency(_marketTop20Tickers, 'top20');

  // Union of both tabs' tickers, fetched once regardless of which tab is
  // active — a chart toggle on a lazily-rendered Sell row still needs its
  // price data to already be present the moment that row exists.
  _marketSignalTickers = [...new Set([...scan.buy_signals, ...scan.sell_signals].map(s => s.ticker))];
  _marketSignalMeta = {};
  scan.buy_signals.forEach(signal => { _marketSignalMeta[`buy:${signal.ticker}`] = { kind: 'buy', ticker: signal.ticker, signal }; });
  scan.sell_signals.forEach(signal => { _marketSignalMeta[`sell:${signal.ticker}`] = { kind: 'sell', ticker: signal.ticker, signal }; });
  loadMarketSignalCharts(_marketSignalTickers);
}

window.addEventListener('stock-data-updated', () => {
  if (currentView === 'market') _marketMapController?.refresh();
});
window.addEventListener('hashchange', () => {
  if (_marketMapController) {
    _marketMapController.destroy();
    _marketMapController = null;
  }
  _marketMapMount = null;
  _marketMapMountPromise = null;
  _marketScanRequestToken += 1;
});

function renderBuyRows(signals) {
  if (!signals.length) return '<tr><td colspan="11" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
  return signals.map(s => {
    const pct = (s.score / (s.max_score || 125)) * 100;
    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
    const entryClass = (s.entry_quality || '').toLowerCase();
    const topReasons = (s.reasons || []).slice(0, 3).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    const extra = (s.reasons || []).slice(3);
    const extraHTML = extra.length
      ? `<div class="extra-reasons" style="display:none">${extra.map(r => `<li>${cleanEmoji(r)}</li>`).join('')}</div><button class="expand-btn" onclick="toggleReasons(this)">+${extra.length} more</button>`
      : '';
    return `<tr data-ticker="${s.ticker}">
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span> ${analysisButtonHTML(s.ticker, `buy:${s.ticker}`, true)}</td>
      <td>${s.current_price != null ? '$' + s.current_price.toFixed(2) : '-'}</td>
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
  if (!signals.length) return '<tr><td colspan="9" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
  return signals.map(s => {
    const sevClass = (s.severity || 'medium').toLowerCase();
    const reasons = (s.reasons || []).map(r => `<li>${cleanEmoji(r)}</li>`).join('');
    return `<tr data-ticker="${s.ticker}">
      <td>${s.rank}</td>
      <td><span class="ticker">${s.ticker}</span> ${analysisButtonHTML(s.ticker, `sell:${s.ticker}`, true)}</td>
      <td>${s.current_price != null ? '$' + s.current_price.toFixed(2) : '-'}</td>
      <td><span class="score-num">${s.score}</span></td>
      <td><span class="badge ${sevClass}">${(s.severity || '?').toUpperCase()}</span></td>
      <td>${s.breakdown_level ? '$' + s.breakdown_level.toFixed(2) : '-'}</td>
      <td>${redditCell(s.reddit_mentions)}</td>
      <td><ul class="reasons-list">${reasons}</ul></td>
      <td>${fidelityLink(s.ticker, 'Sell', 'sell')}</td>
    </tr>`;
  }).join('');
}
