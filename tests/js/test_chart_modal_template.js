const assert = require('assert');
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', '..', 'templates', 'dashboard.html'), 'utf8');
const contentEnd = html.indexOf('</main>');
const modalStart = html.indexOf('id="priceAnalysisModal"');

assert.ok(modalStart > contentEnd, 'modal must be outside the view content and app shell');
assert.match(html, /id="priceAnalysisModal"[^>]*role="dialog"[^>]*aria-modal="true"[^>]*aria-labelledby="priceAnalysisTitle"[^>]*hidden/);
assert.match(html, /id="priceAnalysisClose"[^>]*type="button"[^>]*aria-label="Close price analysis"/);
assert.match(html, /<canvas id="priceAnalysisChart"><\/canvas>/);
assert.match(html, /data-chart-range="1m"/);
assert.match(html, /id="priceAnalysisSMA20"/);
assert.match(html, /id="priceAnalysisLatest"/);
console.log('test_chart_modal_template.js: all assertions passed');
