import { content, pageTitle, pageMeta, setCurrentView } from './state.js';
import { _stopLive } from './refresh.js';

// Populated by initRouter with the VIEWS map from dashboard.js. Kept as
// module state rather than an import to avoid a circular dependency —
// dashboard.js defines the view render functions and imports route()/
// initRouter() from here, so router.js can't import VIEWS back from
// dashboard.js at module-evaluation time.
let _views = {};

export function route() {
  _stopLive();
  const hash = (location.hash || '#/positions').replace('#/', '');
  const view = _views[hash] ? hash : 'positions';
  setCurrentView(view);
  document.querySelectorAll('.nav-item').forEach(a => {
    const isActive = a.dataset.view === view;
    a.classList.toggle('active', isActive);
    if (isActive) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  pageTitle.textContent = _views[view].title;
  pageMeta.innerHTML = '';
  content.innerHTML = '<div class="no-data"><span class="spinner"></span> Loading…</div>';
  _views[view].render();
}

export function initRouter(viewsMap) {
  _views = viewsMap;
  window.addEventListener('hashchange', route);
  route();
}
