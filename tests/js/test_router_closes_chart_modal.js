const assert = require('assert');
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(path.join(__dirname, '..', '..', 'static', 'js', 'core', 'router.js'), 'utf8');
const routeStart = src.indexOf('export function route()');
const closeCall = src.indexOf('closeChartModal();', routeStart);
const stopCall = src.indexOf('_stopLive();', routeStart);
assert.ok(closeCall > routeStart && closeCall < stopCall, 'route must close the modal before stopping or replacing the active view');
console.log('test_router_closes_chart_modal.js: all assertions passed');
