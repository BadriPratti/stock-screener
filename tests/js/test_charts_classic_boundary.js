const assert = require('assert');
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(path.join(__dirname, '..', '..', 'static', 'js', 'charts.js'), 'utf8');
assert.ok(!/^\s*export\s/m.test(src), 'charts.js must remain a classic script without exports');
assert.match(src, /function renderAnalysisChart\(/);
assert.match(src, /function renderMarketMotionChart\(/);
assert.match(src, /renderAnalysisChart,[\s\S]*renderMarketMotionChart,[\s\S]*destroyChart,/);
assert.match(src, /_chartCleanups\[canvasId\]/, 'chart teardown invokes registered controller cleanup');
assert.match(src, /\(series\.referenceLines \|\| \[\]\)\.filter\(line => Number\.isFinite\(line\.value\)\)/,
  'reference lines must reject missing and non-finite values');
console.log('test_charts_classic_boundary.js: all assertions passed');
