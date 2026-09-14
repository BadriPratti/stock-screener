export const content = document.getElementById('content');
export const pageTitle = document.getElementById('pageTitle');
export const pageMeta = document.getElementById('pageMeta');

// Tracks which view is actually on screen right now. View render functions
// are async — if you navigate away while one is still awaiting its first
// fetch, that stale call resolves later and, without this check, would paint
// its (now-irrelevant) content over whatever view you've since navigated to.
// Every render function checks `currentView === '<its own name>'` right
// after each await, before touching pageMeta/content, and bails out silently
// if it's lost the race. Only router.js writes this; everything else reads it.
export let currentView = null;
export function setCurrentView(view) {
  currentView = view;
}
