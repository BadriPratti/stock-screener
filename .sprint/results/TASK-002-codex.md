Reading additional input from stdin...
OpenAI Codex v0.154.0
--------
[1mworkdir:[0m /Users/badripratti/Desktop/stock-screener
[1mmodel:[0m gpt-5.6-sol
[1mprovider:[0m openai
[1mapproval:[0m never
[1msandbox:[0m workspace-write [workdir, /tmp, $TMPDIR]
[1mreasoning effort:[0m medium
[1mreasoning summaries:[0m none
[1msession id:[0m 01a09ddb-d3c1-7062-968c-369e361e0b57
--------
[36muser[0m

You are implementing TASK-002 in an approved sprint.

Repository:
/Users/badripratti/Desktop/stock-screener

Task:
Build a design system for the dashboard UI WITHOUT touching any existing
view-rendering logic yet (that's later tasks). This is purely additive —
new CSS tokens and new reusable component-builder JS modules that later
tasks will consume.

Goal:
1. In static/css/dashboard.css, expand the existing :root custom properties
   (currently just --bg, --surface, --surface-2, --border, --text, --muted,
   --green, --red, --yellow, --blue, --purple) into a fuller token set:
   - Semantic color roles (surface elevations, borders at different
     emphasis levels, text at different emphasis levels)
   - A 4/8px spacing scale as custom properties
   - A typography scale (font sizes for display/heading/body/caption/mono)
   - Control heights (button/input sizing)
   - Radius, shadow, and focus-ring tokens
   - Keep the EXISTING dark palette as the visual baseline — don't change
     how anything currently looks, just formalize the tokens
   Do not delete or rename any existing custom property that other CSS
   rules still reference — check with grep before renaming anything.
2. Create new static/js/components/ with small, framework-free component
   builder functions (each returns an HTML string, matching the existing
   codebase's template-literal style):
   - metric-card.js: a stat card (label, value, sub-label, color variant)
   - status-pill.js: a status badge (idle/running/success/error, matching
     existing .status-pill CSS classes)
   - data-table.js: a sortable table shell (headers, rows, sort-by-column
     support) — this should be genuinely reusable, not tied to one view's
     data shape
   - empty-state.js: a 'no data yet' placeholder block
   - job-panel.js: the run/output/status-pill card pattern already used in
     Run Simulation (see jobCardHTML in static/js/dashboard.js) — extract
     and generalize it
   Use ES module syntax (export function ...). These will be consumed by
   later view-migration tasks via <script type="module"> — no bundler,
   no build step, this repo has none and won't be adding one.

Constraints:
- Do NOT modify static/js/dashboard.js, static/js/charts.js, or
  templates/dashboard.html in this task — purely additive new files plus
  CSS token additions.
- Do NOT change any existing visual appearance — this is a foundation for
  later tasks to build on, not a visible redesign yet.
- Match the existing code's style: no comments explaining WHAT the code
  does, only WHY when something is non-obvious. No emoji anywhere (this
  codebase deliberately has none — professional/clean UI is a hard
  requirement from the user).

Acceptance criteria:
- static/css/dashboard.css still parses as valid CSS and the existing
  dashboard still renders identically (no visual regression) — you can
  verify by checking that you only ADDED custom properties and didn't
  remove/rename ones that grep shows are still referenced.
- New static/js/components/*.js files are syntactically valid
  (node --check each file after stripping the 'export' keyword, or just
  ensure valid JS syntax).
- Each component function is genuinely reusable — not hard-coded to one
  specific view's exact data shape.

When finished:
1. Show your diff / list of new files.
2. Explain the token set you chose and why.
3. Confirm no existing custom property was removed/renamed (show the grep
   check you ran).

[35m[3mcodex[0m[0m
I’ll inspect the existing CSS tokens, component styles, and `jobCardHTML` pattern first. Then I’ll add only the token definitions and new ES modules, followed by CSS/JS syntax checks and a scoped diff review.
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'pwd && rg -n "''^:root|--(bg|surface|surface-2|border|text|muted|green|red|yellow|blue|purple)'"\\b|status-pill|jobCardHTML\" static/css/dashboard.css static/js/dashboard.js && rg --files static/js static/css | sort"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
/Users/badripratti/Desktop/stock-screener
static/css/dashboard.css:1::root {
static/css/dashboard.css:2:  --bg: #0f1117;
static/css/dashboard.css:3:  --surface: #1a1d27;
static/css/dashboard.css:4:  --surface-2: #21242f;
static/css/dashboard.css:5:  --border: #2a2d3a;
static/css/dashboard.css:6:  --text: #e4e6eb;
static/css/dashboard.css:7:  --muted: #8b8fa3;
static/css/dashboard.css:8:  --green: #22c55e;
static/css/dashboard.css:9:  --red: #ef4444;
static/css/dashboard.css:10:  --yellow: #eab308;
static/css/dashboard.css:11:  --blue: #3b82f6;
static/css/dashboard.css:12:  --purple: #a855f7;
static/css/dashboard.css:15:body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
static/css/dashboard.css:22:  width: 220px; flex-shrink: 0; background: var(--surface);
static/css/dashboard.css:23:  border-right: 1px solid var(--border); padding: 20px 0;
static/css/dashboard.css:29:  color: var(--muted); text-decoration: none;
static/css/dashboard.css:32:.nav-item:hover { color: var(--text); background: rgba(255,255,255,0.03); }
static/css/dashboard.css:33:.nav-item.active { color: var(--text); background: rgba(59,130,246,0.08); border-left-color: var(--blue); }
static/css/dashboard.css:35:.nav-item-sub { display: block; font-size: 10.5px; color: var(--muted); opacity: 0.75; margin-top: 1px; }
static/css/dashboard.css:36:.sidebar-footer { margin-top: auto; padding: 16px 20px 0; color: var(--muted); font-size: 11px; }
static/css/dashboard.css:40:  background: var(--surface); border-bottom: 1px solid var(--border);
static/css/dashboard.css:44:.page-meta { color: var(--muted); font-size: 13px; }
static/css/dashboard.css:48:.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px; transition: all 0.15s; }
static/css/dashboard.css:49:.btn:hover { border-color: var(--blue); }
static/css/dashboard.css:50:.btn.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
static/css/dashboard.css:60:.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
static/css/dashboard.css:61:.stat-card .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
static/css/dashboard.css:63:.stat-card .sub { color: var(--muted); font-size: 12px; margin-top: 4px; }
static/css/dashboard.css:64:.stat-card.green .value { color: var(--green); }
static/css/dashboard.css:65:.stat-card.red .value { color: var(--red); }
static/css/dashboard.css:66:.stat-card.blue .value { color: var(--blue); }
static/css/dashboard.css:67:.stat-card.yellow .value { color: var(--yellow); }
static/css/dashboard.css:68:.stat-card.purple .value { color: var(--purple); }
static/css/dashboard.css:70:.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 16px; }
static/css/dashboard.css:72:.card .card-sub { color: var(--muted); font-size: 12px; margin-top: -10px; margin-bottom: 14px; }
static/css/dashboard.css:78:.signal-table th { text-align: left; padding: 10px 12px; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
static/css/dashboard.css:79:.signal-table td { padding: 12px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: top; }
static/css/dashboard.css:82:.ticker { font-weight: 700; font-size: 14px; color: var(--blue); }
static/css/dashboard.css:83:.score-bar { height: 6px; border-radius: 3px; background: var(--border); overflow: hidden; width: 80px; display: inline-block; vertical-align: middle; margin-left: 6px; }
static/css/dashboard.css:88:.badge.good { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:89:.badge.extended { background: rgba(234,179,8,0.15); color: var(--yellow); }
static/css/dashboard.css:90:.badge.poor { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:91:.badge.critical { background: rgba(239,68,68,0.25); color: var(--red); }
static/css/dashboard.css:92:.badge.high { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:93:.badge.medium { background: rgba(234,179,8,0.15); color: var(--yellow); }
static/css/dashboard.css:94:.badge.neutral { background: rgba(255,255,255,0.08); color: var(--muted); }
static/css/dashboard.css:104:.momentum-badge.stable { background: rgba(34,197,94,0.15); color: var(--green); border-color: rgba(34,197,94,0.3); }
static/css/dashboard.css:109:.reasons-list li { font-size: 11px; color: var(--muted); padding: 1px 0; }
static/css/dashboard.css:111:.expand-btn { background: none; border: none; color: var(--blue); cursor: pointer; font-size: 11px; padding: 2px 0; }
static/css/dashboard.css:115:.trade-link.buy { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:117:.trade-link.sell { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:120:.no-data { text-align: center; padding: 60px 20px; color: var(--muted); }
static/css/dashboard.css:121:.no-data h2 { font-size: 18px; margin-bottom: 8px; color: var(--text); }
static/css/dashboard.css:123:.banner { background: rgba(234,179,8,0.1); border: 1px solid rgba(234,179,8,0.3); color: var(--yellow); border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 20px; }
static/css/dashboard.css:124:.banner a { color: var(--yellow); text-decoration: underline; }
static/css/dashboard.css:131:.source-note.email { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.3); color: var(--purple); }
static/css/dashboard.css:132:.source-note.historical { background: rgba(59,130,246,0.08); border-color: rgba(59,130,246,0.3); color: var(--blue); }
static/css/dashboard.css:137:.regime-badge.risk-on { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:138:.regime-badge.risk-off { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:139:.regime-badge.transitional { background: rgba(234,179,8,0.15); color: var(--yellow); }
static/css/dashboard.css:141:.scan-select { background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 6px; font-size: 13px; }
static/css/dashboard.css:146:.news-headline { display: block; padding: 7px 0; border-bottom: 1px solid var(--border); text-decoration: none; }
static/css/dashboard.css:148:.news-headline-title { font-size: 12.5px; color: var(--text); line-height: 1.4; }
static/css/dashboard.css:149:.news-headline:hover .news-headline-title { color: var(--blue); }
static/css/dashboard.css:150:.news-headline-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }
static/css/dashboard.css:154:.pick-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px; position: relative; }
static/css/dashboard.css:156:.pick-rank { position: absolute; top: 14px; right: 16px; color: var(--muted); font-size: 12px; font-weight: 700; }
static/css/dashboard.css:160:.pick-scores .score-block .label { color: var(--muted); font-size: 10px; text-transform: uppercase; }
static/css/dashboard.css:164:.agent-badge.pos { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:165:.agent-badge.neg { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:166:.agent-badge.neu { background: rgba(255,255,255,0.06); color: var(--muted); }
static/css/dashboard.css:167:.agent-badge-sub { font-size: 11px; color: var(--muted); margin: -3px 0 3px 2px; }
static/css/dashboard.css:168:.backfill-note { font-size: 11px; color: var(--yellow); margin-bottom: 10px; }
static/css/dashboard.css:173:  background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px;
static/css/dashboard.css:174:  color: var(--text); cursor: pointer; padding: 0;
static/css/dashboard.css:177:.chart-toggle-btn:hover { border-color: var(--blue); color: var(--blue); background: rgba(59,130,246,0.1); }
static/css/dashboard.css:178:.chart-toggle-btn.active { border-color: var(--blue); background: rgba(59,130,246,0.12); color: var(--blue); }
static/css/dashboard.css:184:  font-size: 11px; font-weight: 600; color: var(--green); margin-left: 10px;
static/css/dashboard.css:186:.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: live-pulse 2s ease-in-out infinite; }
static/css/dashboard.css:190:.sim-card .sim-desc { color: var(--muted); font-size: 12px; margin-bottom: 14px; }
static/css/dashboard.css:192:.sim-params label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--muted); }
static/css/dashboard.css:194:  background: var(--surface-2); border: 1px solid var(--border); color: var(--text);
static/css/dashboard.css:198:  background: #0a0b10; border: 1px solid var(--border); border-radius: 8px; padding: 12px;
static/css/dashboard.css:199:  font-family: 'SF Mono', Menlo, monospace; font-size: 11px; color: var(--muted);
static/css/dashboard.css:202:.status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-left: 10px; }
static/css/dashboard.css:203:.status-pill.idle { background: rgba(255,255,255,0.06); color: var(--muted); }
static/css/dashboard.css:204:.status-pill.running { background: rgba(59,130,246,0.15); color: var(--blue); }
static/css/dashboard.css:205:.status-pill.success { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:206:.status-pill.error { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:211:.toast { position: fixed; bottom: 24px; right: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; font-size: 13px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); z-index: 100; transition: opacity 0.3s; max-width: 360px; }
static/js/dashboard.js:178:  if (count == null) return '<span style="color:var(--muted)">-</span>';
static/js/dashboard.js:179:  if (count === 0) return '<span style="color:var(--muted)">0</span>';
static/js/dashboard.js:181:  return `<span style="color:${hot ? 'var(--yellow)' : 'var(--text)'};font-weight:${hot ? 700 : 400}">${count}</span>`;
static/js/dashboard.js:256:    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${escapeHtml(red[0].flag)}${more}</div>`;
static/js/dashboard.js:260:    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
static/js/dashboard.js:290:function jobCardHTML(id, title, desc, paramsHTML) {
static/js/dashboard.js:293:      <h2>${title} <span class="status-pill idle" id="${id}-pill">idle</span></h2>
static/js/dashboard.js:345:        pill.className = 'status-pill running';
static/js/dashboard.js:349:        pill.className = `status-pill ${st.status}`;
static/js/dashboard.js:386:    pill.className = 'status-pill running';
static/js/dashboard.js:446:        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
static/js/dashboard.js:513:      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
static/js/dashboard.js:521:      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
static/js/dashboard.js:548:      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
static/js/dashboard.js:601:    bodyEl.innerHTML = `<div style="color:var(--muted);font-size:13px">${emptyMsg}</div>`;
static/js/dashboard.js:605:    bodyEl.innerHTML = '<div style="color:var(--muted);font-size:13px"><span class="spinner"></span> Fetching real headlines…</div>';
static/js/dashboard.js:615:      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
static/js/dashboard.js:622:  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
static/js/dashboard.js:631:      : '<div style="color:var(--muted);font-size:12px">No recent headlines.</div>';
static/js/dashboard.js:657:      <div class="stat-card blue"><div class="label">Top Score</div><div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div><div class="sub">${scan.buy_signals.length ? scan.buy_signals[0].ticker : '-'}</div></div>
static/js/dashboard.js:667:          <div><div style="color:var(--muted);font-size:11px">Phase</div><div style="font-size:18px;font-weight:700">${scan.spy.phase} - ${scan.spy.phase_name || ''}</div></div>
static/js/dashboard.js:668:          <div><div style="color:var(--muted);font-size:11px">Confidence</div><div style="font-size:18px;font-weight:700">${scan.spy.confidence || '?'}%</div></div>
static/js/dashboard.js:674:      <h2 style="color:var(--green)">Buy Signals</h2>
static/js/dashboard.js:681:      <h2 style="color:var(--red)">Sell Signals</h2>
static/js/dashboard.js:699:  if (!signals.length) return '<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
static/js/dashboard.js:702:    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
static/js/dashboard.js:715:      <td style="color:${(s.rr_ratio || 0) >= 3 ? 'var(--green)' : (s.rr_ratio || 0) >= 2 ? 'var(--text)' : 'var(--yellow)'}">${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : '-'}</td>
static/js/dashboard.js:716:      <td style="color:${(s.rs || 0) > 0.1 ? 'var(--green)' : (s.rs || 0) > 0 ? 'var(--text)' : 'var(--red)'}">${s.rs != null ? s.rs.toFixed(3) : '-'}</td>
static/js/dashboard.js:725:  if (!signals.length) return '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
static/js/dashboard.js:760:        <span style="color:var(--muted);font-size:13px">Showing ${data.position_analyses.length} position${data.position_analyses.length === 1 ? '' : 's'} from your last upload.</span>
static/js/dashboard.js:766:      <h2>Upload Your Positions <span class="status-pill idle" id="pos-pill">idle</span></h2>
static/js/dashboard.js:772:      <input type="file" id="pos-file" accept=".csv" style="margin-bottom:12px;display:block;color:var(--text);font-size:13px">
static/js/dashboard.js:823:      pill.className = 'status-pill running';
static/js/dashboard.js:831:        pill.className = 'status-pill error';
static/js/dashboard.js:843:    pill.className = 'status-pill running';
static/js/dashboard.js:851:        pill.className = `status-pill ${st.status}`;
static/js/dashboard.js:874:    const gainColor = a.current_gain_pct >= 0 ? 'var(--green)' : 'var(--red)';
static/js/dashboard.js:882:      extra += `<div class="agent-badge-sub" style="color:var(--green);margin-top:6px">Add-on candidate — ${a.add_on_rationale}</div>`;
static/js/dashboard.js:885:      extra += `<div class="agent-badge-sub" style="color:var(--yellow)">${w}</div>`;
static/js/dashboard.js:936:      for those, see <a href="#/shortlist" style="color:var(--blue)">Shortlist</a> or
static/js/dashboard.js:937:      <a href="#/market" style="color:var(--blue)">Market</a>. Run a fresh one from
static/js/dashboard.js:938:      <a href="#/run" style="color:var(--blue)">Run Simulation</a>.
static/js/dashboard.js:986:      <h2>Trades <span style="font-weight:400;color:var(--muted);font-size:12px">(click a column to sort)</span></h2>
static/js/dashboard.js:1023:    <td style="color:${(t.return_pct || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">${(t.return_pct || 0).toFixed(2)}%</td>
static/js/dashboard.js:1024:    <td style="color:${(t.dollar_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">$${(t.dollar_pnl || 0).toFixed(2)}</td>
static/js/dashboard.js:1033:      ${jobCardHTML('top3', 'Quick Backtest (Top 3)', 'What would the top-3 buy signals have been N days ago, held to today?', `
static/js/dashboard.js:1038:      ${jobCardHTML('mc', 'Monte Carlo', 'Re-samples many top-3 portfolios from one fetched pool — win rate distribution, not one basket.', `
static/js/dashboard.js:1044:      ${jobCardHTML('wf', 'Full Walk-Forward', 'Rigorous multi-period backtest — walks a fixed universe through many historical dates. Slow (minutes+).', `
static/js/dashboard.js:1061:      <strong style="color:${res.total_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.total_profit.toFixed(2)} (${res.total_return_pct.toFixed(2)}%)</strong>
static/js/dashboard.js:1073:    if (res.error || !res.iterations_run) { resultEl.innerHTML = '<div style="color:var(--muted);font-size:13px">Not enough qualifiers found.</div>'; return; }
static/js/dashboard.js:1075:      Win rate <strong>${res.win_rate.toFixed(1)}%</strong> · avg <strong style="color:${res.avg_profit >= 0 ? 'var(--green)' : 'var(--red)'}">$${res.avg_profit.toFixed(2)} (${res.avg_pct.toFixed(2)}%)</strong>
static/js/dashboard.js:1094:      <h2>Run a Scan <span class="status-pill idle" id="scan-pill">idle</span></h2>
static/css/dashboard.css
static/js/charts.js
static/js/dashboard.js

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '1,235p' static/css/dashboard.css && sed -n '270,330p' static/js/dashboard.js && sed -n '960,1055p' static/js/dashboard.js && find . -maxdepth 2 -type f \\( -name 'package.json' -o -name 'pyproject.toml' -o -name 'requirements*.txt' -o -name 'AGENTS.md' \\) -print"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface-2: #21242f;
  --border: #2a2d3a;
  --text: #e4e6eb;
  --muted: #8b8fa3;
  --green: #22c55e;
  --red: #ef4444;
  --yellow: #eab308;
  --blue: #3b82f6;
  --purple: #a855f7;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
a { color: inherit; }

/* --- App shell: sidebar + main --- */
.app { display: flex; min-height: 100vh; }

.sidebar {
  width: 220px; flex-shrink: 0; background: var(--surface);
  border-right: 1px solid var(--border); padding: 20px 0;
  display: flex; flex-direction: column; position: sticky; top: 0; height: 100vh;
}
.brand { font-size: 15px; font-weight: 700; padding: 0 20px 20px; }
.nav-item {
  display: block; padding: 8px 20px;
  color: var(--muted); text-decoration: none;
  border-left: 3px solid transparent; transition: all 0.15s;
}
.nav-item:hover { color: var(--text); background: rgba(255,255,255,0.03); }
.nav-item.active { color: var(--text); background: rgba(59,130,246,0.08); border-left-color: var(--blue); }
.nav-item-title { display: block; font-size: 14px; font-weight: 500; }
.nav-item-sub { display: block; font-size: 10.5px; color: var(--muted); opacity: 0.75; margin-top: 1px; }
.sidebar-footer { margin-top: auto; padding: 16px 20px 0; color: var(--muted); font-size: 11px; }

.main { flex: 1; min-width: 0; }
.topbar {
  background: var(--surface); border-bottom: 1px solid var(--border);
  padding: 18px 32px; display: flex; align-items: baseline; gap: 14px;
}
.topbar h1 { font-size: 19px; font-weight: 700; }
.page-meta { color: var(--muted); font-size: 13px; }
.content { max-width: 1300px; margin: 0 auto; padding: 24px 32px 60px; }

/* --- Buttons --- */
.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px; transition: all 0.15s; }
.btn:hover { border-color: var(--blue); }
.btn.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
.btn.primary:hover { opacity: 0.9; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* --- Layout helpers --- */
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }

.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
.stat-card .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.stat-card .value { font-size: 28px; font-weight: 700; }
.stat-card .sub { color: var(--muted); font-size: 12px; margin-top: 4px; }
.stat-card.green .value { color: var(--green); }
.stat-card.red .value { color: var(--red); }
.stat-card.blue .value { color: var(--blue); }
.stat-card.yellow .value { color: var(--yellow); }
.stat-card.purple .value { color: var(--purple); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 16px; }
.card h2 { font-size: 15px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.card .card-sub { color: var(--muted); font-size: 12px; margin-top: -10px; margin-bottom: 14px; }

.chart-wrap { position: relative; height: 250px; }

/* --- Signal tables (Market view) --- */
.signal-table { width: 100%; border-collapse: collapse; }
.signal-table th { text-align: left; padding: 10px 12px; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
.signal-table td { padding: 12px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: top; }
.signal-table tr:hover { background: rgba(59,130,246,0.04); }

.ticker { font-weight: 700; font-size: 14px; color: var(--blue); }
.score-bar { height: 6px; border-radius: 3px; background: var(--border); overflow: hidden; width: 80px; display: inline-block; vertical-align: middle; margin-left: 6px; }
.score-bar .fill { height: 100%; border-radius: 3px; }
.score-num { font-weight: 600; font-size: 13px; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.badge.good { background: rgba(34,197,94,0.15); color: var(--green); }
.badge.extended { background: rgba(234,179,8,0.15); color: var(--yellow); }
.badge.poor { background: rgba(239,68,68,0.15); color: var(--red); }
.badge.critical { background: rgba(239,68,68,0.25); color: var(--red); }
.badge.high { background: rgba(239,68,68,0.15); color: var(--red); }
.badge.medium { background: rgba(234,179,8,0.15); color: var(--yellow); }
.badge.neutral { background: rgba(255,255,255,0.08); color: var(--muted); }

/* --- Momentum status indicator (hot / stable / basing / avoid) + day streak --- */
.momentum-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 9px; border-radius: 5px; font-size: 11px; font-weight: 700;
  border: 1px solid transparent; white-space: nowrap;
}
.momentum-badge .streak { font-weight: 500; opacity: 0.85; }
.momentum-badge.hot { background: rgba(239,68,68,0.18); color: #ff6b6b; border-color: rgba(239,68,68,0.35); }
.momentum-badge.stable { background: rgba(34,197,94,0.15); color: var(--green); border-color: rgba(34,197,94,0.3); }
.momentum-badge.basing { background: rgba(59,130,246,0.12); color: #7dd3fc; border-color: rgba(59,130,246,0.3); }
.momentum-badge.avoid { background: rgba(0,0,0,0.35); color: #f87171; border-color: rgba(239,68,68,0.4); }

.reasons-list { list-style: none; padding: 0; margin-top: 4px; }
.reasons-list li { font-size: 11px; color: var(--muted); padding: 1px 0; }

.expand-btn { background: none; border: none; color: var(--blue); cursor: pointer; font-size: 11px; padding: 2px 0; }
.expand-btn:hover { text-decoration: underline; }

.trade-link { display: inline-flex; align-items: center; gap: 4px; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; white-space: nowrap; border: 1px solid transparent; }
.trade-link.buy { background: rgba(34,197,94,0.15); color: var(--green); }
.trade-link.buy:hover { background: rgba(34,197,94,0.28); }
.trade-link.sell { background: rgba(239,68,68,0.15); color: var(--red); }
.trade-link.sell:hover { background: rgba(239,68,68,0.28); }

.no-data { text-align: center; padding: 60px 20px; color: var(--muted); }
.no-data h2 { font-size: 18px; margin-bottom: 8px; color: var(--text); }

.banner { background: rgba(234,179,8,0.1); border: 1px solid rgba(234,179,8,0.3); color: var(--yellow); border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 20px; }
.banner a { color: var(--yellow); text-decoration: underline; }

/* "This is what your email sends" / "this is historical, not email" style notes */
.source-note {
  padding: 10px 14px; border-radius: 8px; font-size: 12px; line-height: 1.5;
  margin-bottom: 18px; border: 1px solid;
}
.source-note.email { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.3); color: var(--purple); }
.source-note.historical { background: rgba(59,130,246,0.08); border-color: rgba(59,130,246,0.3); color: var(--blue); }
.source-note b { font-weight: 700; }
.source-note a { text-decoration: underline; }

.regime-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.regime-badge.risk-on { background: rgba(34,197,94,0.15); color: var(--green); }
.regime-badge.risk-off { background: rgba(239,68,68,0.15); color: var(--red); }
.regime-badge.transitional { background: rgba(234,179,8,0.15); color: var(--yellow); }

.scan-select { background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 6px; font-size: 13px; }

/* --- Market view: news sections --- */
.news-ticker-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
.news-ticker-block { min-width: 0; }
.news-headline { display: block; padding: 7px 0; border-bottom: 1px solid var(--border); text-decoration: none; }
.news-headline:last-child { border-bottom: none; }
.news-headline-title { font-size: 12.5px; color: var(--text); line-height: 1.4; }
.news-headline:hover .news-headline-title { color: var(--blue); }
.news-headline-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }

/* --- Shortlist cards --- */
.shortlist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.pick-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px; position: relative; }
.pick-card.backfilled { border-color: rgba(234,179,8,0.35); }
.pick-rank { position: absolute; top: 14px; right: 16px; color: var(--muted); font-size: 12px; font-weight: 700; }
.pick-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
.pick-header .ticker { font-size: 20px; }
.pick-scores { display: flex; gap: 16px; margin-bottom: 12px; }
.pick-scores .score-block .label { color: var(--muted); font-size: 10px; text-transform: uppercase; }
.pick-scores .score-block .value { font-size: 16px; font-weight: 700; }
.pick-badges { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.agent-badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600; width: fit-content; }
.agent-badge.pos { background: rgba(34,197,94,0.15); color: var(--green); }
.agent-badge.neg { background: rgba(239,68,68,0.15); color: var(--red); }
.agent-badge.neu { background: rgba(255,255,255,0.06); color: var(--muted); }
.agent-badge-sub { font-size: 11px; color: var(--muted); margin: -3px 0 3px 2px; }
.backfill-note { font-size: 11px; color: var(--yellow); margin-bottom: 10px; }

.chart-toggle-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; flex-shrink: 0;
  background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px;
  color: var(--text); cursor: pointer; padding: 0;
}
.chart-toggle-btn svg { width: 17px; height: 17px; }
.chart-toggle-btn:hover { border-color: var(--blue); color: var(--blue); background: rgba(59,130,246,0.1); }
.chart-toggle-btn.active { border-color: var(--blue); background: rgba(59,130,246,0.12); color: var(--blue); }
.position-chart-wrap { height: 180px; margin-top: 14px; }

/* --- "Live" auto-refresh indicator --- */
.live-badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 600; color: var(--green); margin-left: 10px;
}
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: live-pulse 2s ease-in-out infinite; }
@keyframes live-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }

/* --- Run Simulation panels --- */
.sim-card .sim-desc { color: var(--muted); font-size: 12px; margin-bottom: 14px; }
.sim-params { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
.sim-params label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--muted); }
.sim-params input {
  background: var(--surface-2); border: 1px solid var(--border); color: var(--text);
  padding: 6px 8px; border-radius: 6px; font-size: 13px; width: 90px;
}
.job-output {
  background: #0a0b10; border: 1px solid var(--border); border-radius: 8px; padding: 12px;
  font-family: 'SF Mono', Menlo, monospace; font-size: 11px; color: var(--muted);
  max-height: 220px; overflow-y: auto; white-space: pre-wrap; margin-top: 12px; display: none;
}
.status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-left: 10px; }
.status-pill.idle { background: rgba(255,255,255,0.06); color: var(--muted); }
.status-pill.running { background: rgba(59,130,246,0.15); color: var(--blue); }
.status-pill.success { background: rgba(34,197,94,0.15); color: var(--green); }
.status-pill.error { background: rgba(239,68,68,0.15); color: var(--red); }

.spinner { display: inline-block; width: 10px; height: 10px; border: 2px solid rgba(255,255,255,0.2); border-top-color: currentColor; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.toast { position: fixed; bottom: 24px; right: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; font-size: 13px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); z-index: 100; transition: opacity 0.3s; max-width: 360px; }
// to know when it's safe to start the next refresh cycle. It used to resolve
// as soon as the initial POST came back, which silently defeated that guard.
async function startJob(kind, body, onUpdate) {
  const { job_id } = await fetchJSON(`/api/jobs/${kind}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  return new Promise((resolve) => {
    const poll = async () => {
      const st = await fetchJSON(`/api/jobs/${job_id}`);
      onUpdate(st);
      if (st.status === 'running' || st.status === 'queued') {
        setTimeout(poll, 1500);
      } else {
        resolve(job_id);
      }
    };
    poll();
  });
}

function jobCardHTML(id, title, desc, paramsHTML) {
  return `
    <div class="card sim-card">
      <h2>${title} <span class="status-pill idle" id="${id}-pill">idle</span></h2>
      <div class="sim-desc">${desc}</div>
      <div class="sim-params">${paramsHTML}</div>
      <button class="btn primary" id="${id}-run">Run</button>
      <div class="job-output" id="${id}-output"></div>
      <div id="${id}-result" style="margin-top:12px"></div>
    </div>`;
}

// Job cards (Run Simulation, Full Scan) kick off long-running background jobs
// (a real detached subprocess on the server — it was never actually stopped by
// navigating away). What used to break on navigation was the UI side: the
// click handler closed over the specific DOM nodes present at click-time, so
// leaving the page and coming back re-rendered a fresh "idle" card with no
// memory of the job still running (or just finished) underneath it. _activeJobs
// tracks job_id per card id at module scope — outside any view's DOM — so it
// survives a route change, and wireJobCard reconnects to it on every render.
const _activeJobs = {}; // cardId -> most recent job_id for that card (running OR finished), survives across renders
const _watchingJobIds = {}; // cardId -> job_id an active setTimeout poll loop is already chasing

function watchJob(id, jobId, onResult) {
  _activeJobs[id] = jobId;
  // Reconnecting to a job you're already polling (e.g. navigating back and
  // forth while it runs) would otherwise stack up a duplicate setTimeout
  // chain each time — same end state, just wasted polling. The next tick of
  // the existing loop repaints the freshly-mounted card within ~1.5s anyway.
  if (_watchingJobIds[id] === jobId) return;
  _watchingJobIds[id] = jobId;

  const poll = async () => {
    const st = await fetchJSON(`/api/jobs/${jobId}`);
    if (st.error) {
      // The server prunes finished jobs after a while — if you reconnect to
      // one long after it ended, just drop back to idle instead of crashing
      // on the missing `output` field.
      if (_activeJobs[id] === jobId) delete _activeJobs[id];
      if (_watchingJobIds[id] === jobId) delete _watchingJobIds[id];
      return;
    fetchJSON('/api/backtest/trades' + (path ? '?path=' + encodeURIComponent(path) : '')),
  ]);
  if (_currentView !== 'backtests') return; // navigated away before this resolved
  const summary = summaryData.summary || {};
  const trades = tradesData.trades || [];

  if (!summary.total_trades) {
    document.getElementById('backtestBody').innerHTML = `
      <div class="no-data"><h2>No backtest history yet</h2><p>Run a Walk-Forward simulation from the Run Simulation page.</p></div>`;
    return;
  }
  pageMeta.textContent = summaryData.generated ? `Generated ${new Date(summaryData.generated).toLocaleString()}` : '';

  document.getElementById('backtestBody').innerHTML = `
    <div class="stats-row">
      <div class="stat-card ${summary.win_rate_pct >= 40 ? 'green' : 'yellow'}"><div class="label">Win Rate</div><div class="value">${(summary.win_rate_pct || 0).toFixed(1)}%</div><div class="sub">${summary.total_trades} trades</div></div>
      <div class="stat-card ${summary.avg_return_pct >= 0 ? 'green' : 'red'}"><div class="label">Avg Return</div><div class="value">${(summary.avg_return_pct || 0).toFixed(2)}%</div><div class="sub">median ${(summary.median_return_pct || 0).toFixed(2)}%</div></div>
      <div class="stat-card blue"><div class="label">Sharpe-like</div><div class="value">${(summary.sharpe_like || 0).toFixed(2)}</div><div class="sub">avg win ${(summary.avg_win_pct || 0).toFixed(1)}% / loss ${(summary.avg_loss_pct || 0).toFixed(1)}%</div></div>
      <div class="stat-card red"><div class="label">Max Drawdown</div><div class="value">${(summary.max_drawdown_pct || 0).toFixed(1)}%</div><div class="sub">$${(summary.max_drawdown_dollars || 0).toFixed(0)}</div></div>
      <div class="stat-card purple"><div class="label">Avg Days Held</div><div class="value">${(summary.avg_days_held || 0).toFixed(1)}</div><div class="sub">${summary.total_periods || '?'} periods</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Cumulative P&amp;L (by exit date)</h2><div class="chart-wrap"><canvas id="equityChart"></canvas></div></div>
      <div class="card"><h2>Exit Reasons</h2><div class="chart-wrap"><canvas id="exitChart"></canvas></div></div>
    </div>
    <div class="card">
      <h2>Trades <span style="font-weight:400;color:var(--muted);font-size:12px">(click a column to sort)</span></h2>
      <div style="overflow-x:auto"><table class="signal-table" id="tradesTable">
        <thead><tr>
          <th data-key="ticker">Ticker</th><th data-key="period">Entry Date</th><th data-key="score">Score</th>
          <th data-key="exit_reason">Exit Reason</th><th data-key="days_held">Days Held</th><th data-key="return_pct">Return %</th><th data-key="dollar_pnl">$ P&amp;L</th>
        </tr></thead>
        <tbody>${renderTradeRows(trades)}</tbody>
      </table></div>
    </div>`;

  renderEquityCurveChart('equityChart', tradesData.equity_curve || []);
  renderExitReasonChart('exitChart', summary.exit_reasons || {});

  let sortKey = null, sortDir = 1;
  document.querySelectorAll('#tradesTable th[data-key]').forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      sortDir = sortKey === key ? -sortDir : 1;
      sortKey = key;
      const sorted = [...trades].sort((a, b) => {
        const av = a[key], bv = b[key];
        if (typeof av === 'string') return sortDir * String(av).localeCompare(String(bv));
        return sortDir * ((av || 0) - (bv || 0));
      });
      document.querySelector('#tradesTable tbody').innerHTML = renderTradeRows(sorted);
    });
  });
}

function renderTradeRows(trades) {
  return trades.map(t => `<tr>
    <td><span class="ticker">${t.ticker}</span></td>
    <td>${t.period || '-'}</td>
    <td>${t.score ?? '-'}</td>
    <td><span class="badge ${t.exit_reason === 'stop_loss' ? 'poor' : t.exit_reason === 'sell_signal' ? 'medium' : 'good'}">${(t.exit_reason || '-').replace('_', ' ')}</span></td>
    <td>${t.days_held ?? '-'}</td>
    <td style="color:${(t.return_pct || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">${(t.return_pct || 0).toFixed(2)}%</td>
    <td style="color:${(t.dollar_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'}">$${(t.dollar_pnl || 0).toFixed(2)}</td>
  </tr>`).join('');
}

// --- View: Run Simulation --------------------------------------------------

function renderRunView() {
  content.innerHTML = `
    <div class="grid-3">
      ${jobCardHTML('top3', 'Quick Backtest (Top 3)', 'What would the top-3 buy signals have been N days ago, held to today?', `
        <label>Days back<input type="number" id="top3-days" value="7"></label>
        <label>Sample size<input type="number" id="top3-sample" value="150"></label>
        <label>Investment $<input type="number" id="top3-investment" value="1000"></label>
      `)}
      ${jobCardHTML('mc', 'Monte Carlo', 'Re-samples many top-3 portfolios from one fetched pool — win rate distribution, not one basket.', `
        <label>Days back<input type="number" id="mc-days" value="7"></label>
        <label>Pool size<input type="number" id="mc-pool" value="300"></label>
        <label>Sample size<input type="number" id="mc-sample" value="150"></label>
        <label>Iterations<input type="number" id="mc-iterations" value="100"></label>
      `)}
      ${jobCardHTML('wf', 'Full Walk-Forward', 'Rigorous multi-period backtest — walks a fixed universe through many historical dates. Slow (minutes+).', `
        <label>Universe size<input type="number" id="wf-universe_size" value="250"></label>
        <label>Lookback (mo)<input type="number" id="wf-lookback_months" value="9"></label>
        <label>Top N/period<input type="number" id="wf-top_n" value="10"></label>
        <label>Max hold (days)<input type="number" id="wf-max_hold_days" value="60"></label>
      `)}
    </div>`;

  wireJobCard('top3', 'backtest-top3', () => ({
    days: +document.getElementById('top3-days').value,
    sample: +document.getElementById('top3-sample').value,
    investment: +document.getElementById('top3-investment').value,
./requirements.txt

[35m[3mcodex[0m[0m
The existing palette maps cleanly to semantic aliases: background/base, raised and elevated surfaces, default/subtle/strong borders, and primary/secondary/disabled text. I’ll keep every legacy token untouched and define the new roles in terms of those values where possible, so adding the foundation cannot alter current rendering. The component APIs will accept generic configuration objects and escape text by default, with explicit HTML hooks only where composability requires them.
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'git status --short && git diff -- static/css/dashboard.css static/js/dashboard.js static/js/charts.js templates/dashboard.html && rg -n "function (escapeHtml|.*HTML)|const escapeHtml|=>.*replace" static/js/dashboard.js | head -40'[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 36ms:[0m
 M .sprint/SPRINT_PLAN.md
 M .sprint/STATUS.md
?? .sprint/council/
?? .sprint/results/TASK-002-codex.md
?? tests/js/
57:function liveBadgeHTML() {
82:function chartToggleButtonHTML(chartId) {
137:function momentumBadgeHTML(entry) {
194:function escapeHtml(text) {
230:function catalystBadgeHTML(sentiment) {
240:function congressBadgeHTML(signal) {
249:function fundamentalsFlagsHTML(audit) {
290:function jobCardHTML(id, title, desc, paramsHTML) {
593:function _newsSectionHTML(group, title, bodyHTML) {
620:function _renderNewsGroupHTML(newsByTicker) {
752:function _positionsUploadCardHTML(data, expanded) {

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "find tests/js -maxdepth 2 -type f -print -exec sed -n '1,240p' {} \\; && sed -n '185,205p' static/js/dashboard.js && sed -n '1,220p' .sprint/results/TASK-002-codex.md"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
tests/js/test_live_guard.js
// Characterization test for _liveGuarded (static/js/dashboard.js) — locks in
// the current dedup behavior BEFORE the router/jobs/refresh extraction
// (TASK-003) touches this code. If this test breaks during that refactor,
// it means the extraction changed real behavior, not just moved code.
//
// Plain Node, no test framework/dependency — matches this repo's "no build
// step" frontend. Run with: node tests/js/test_live_guard.js

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(
  path.join(__dirname, '..', '..', 'static', 'js', 'dashboard.js'), 'utf8'
);

function extract(fnName) {
  const start = src.indexOf(`function ${fnName}(`);
  if (start === -1) throw new Error(`${fnName} not found in dashboard.js`);
  let depth = 0, i = src.indexOf('{', start);
  const bodyStart = i;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') { depth--; if (depth === 0) break; }
  }
  return src.slice(start, i + 1);
}

// eslint-disable-next-line no-eval
eval(extract('_liveGuarded'));

async function main() {
  // Test 1: sequential calls with the same key both run (no false-positive dedup)
  let runs = 0;
  await _liveGuarded('a', async () => { runs++; });
  await _liveGuarded('a', async () => { runs++; });
  assert.strictEqual(runs, 2, 'sequential calls with the same key should both execute');

  // Test 2: a call that's still in-flight blocks a concurrent call with the SAME key
  let concurrentRuns = 0;
  let resolveFirst;
  const firstCall = _liveGuarded('b', () => new Promise(r => { resolveFirst = r; })
    .then(() => { concurrentRuns++; }));
  // second call fires while the first is still pending
  await _liveGuarded('b', async () => { concurrentRuns++; });
  assert.strictEqual(concurrentRuns, 0, 'overlapping call with the same key must be skipped, not queued');
  resolveFirst();
  await firstCall;
  assert.strictEqual(concurrentRuns, 1, 'only the first in-flight call should have run');

  // Test 3: different keys never block each other
  let cRuns = 0, dRuns = 0;
  let resolveC;
  const cCall = _liveGuarded('c', () => new Promise(r => { resolveC = r; }).then(() => { cRuns++; }));
  await _liveGuarded('d', async () => { dRuns++; });
  assert.strictEqual(dRuns, 1, 'a different key must not be blocked by an in-flight call under another key');
  resolveC();
  await cCall;
  assert.strictEqual(cRuns, 1);

  // Test 4: the guard clears after completion, allowing a later call through
  let eRuns = 0;
  await _liveGuarded('e', async () => { eRuns++; });
  await _liveGuarded('e', async () => { eRuns++; });
  assert.strictEqual(eRuns, 2, 'the in-flight marker must be released after the guarded call resolves');

  console.log('test_live_guard.js: all assertions passed');
}

main().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
  return (text || '').replace(/[🟢🔴🟡⭐⚠✓🚨]/g, '').trim();
}

// Escapes free text before it's interpolated into innerHTML. Needed anywhere
// the string didn't originate from this codebase — news headlines/publishers
// (raw Yahoo Finance feed data), and LLM-generated summaries/flags (ultimately
// derived from external filings/press) — a crafted string containing HTML
// could otherwise execute JS in the dashboard's own origin, which has several
// unauthenticated routes (sync, scan, positions upload).
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text == null ? '' : String(text);
  return div.innerHTML;
}

// Only allow http(s) URLs as link targets — a "javascript:" (or other
// executable) scheme in externally-sourced data (e.g. a news item's URL)
// would otherwise run when clicked, same class of risk as the innerHTML issue.
function safeHref(url) {
  try {
    const parsed = new URL(url, location.href);
Reading additional input from stdin...
OpenAI Codex v0.154.0
--------
[1mworkdir:[0m /Users/badripratti/Desktop/stock-screener
[1mmodel:[0m gpt-5.6-sol
[1mprovider:[0m openai
[1mapproval:[0m never
[1msandbox:[0m workspace-write [workdir, /tmp, $TMPDIR]
[1mreasoning effort:[0m medium
[1mreasoning summaries:[0m none
[1msession id:[0m 01a09ddb-d3c1-7062-968c-369e361e0b57
--------
[36muser[0m

You are implementing TASK-002 in an approved sprint.

Repository:
/Users/badripratti/Desktop/stock-screener

Task:
Build a design system for the dashboard UI WITHOUT touching any existing
view-rendering logic yet (that's later tasks). This is purely additive —
new CSS tokens and new reusable component-builder JS modules that later
tasks will consume.

Goal:
1. In static/css/dashboard.css, expand the existing :root custom properties
   (currently just --bg, --surface, --surface-2, --border, --text, --muted,
   --green, --red, --yellow, --blue, --purple) into a fuller token set:
   - Semantic color roles (surface elevations, borders at different
     emphasis levels, text at different emphasis levels)
   - A 4/8px spacing scale as custom properties
   - A typography scale (font sizes for display/heading/body/caption/mono)
   - Control heights (button/input sizing)
   - Radius, shadow, and focus-ring tokens
   - Keep the EXISTING dark palette as the visual baseline — don't change
     how anything currently looks, just formalize the tokens
   Do not delete or rename any existing custom property that other CSS
   rules still reference — check with grep before renaming anything.
2. Create new static/js/components/ with small, framework-free component
   builder functions (each returns an HTML string, matching the existing
   codebase's template-literal style):
   - metric-card.js: a stat card (label, value, sub-label, color variant)
   - status-pill.js: a status badge (idle/running/success/error, matching
     existing .status-pill CSS classes)
   - data-table.js: a sortable table shell (headers, rows, sort-by-column
     support) — this should be genuinely reusable, not tied to one view's
     data shape
   - empty-state.js: a 'no data yet' placeholder block
   - job-panel.js: the run/output/status-pill card pattern already used in
     Run Simulation (see jobCardHTML in static/js/dashboard.js) — extract
     and generalize it
   Use ES module syntax (export function ...). These will be consumed by
   later view-migration tasks via <script type="module"> — no bundler,
   no build step, this repo has none and won't be adding one.

Constraints:
- Do NOT modify static/js/dashboard.js, static/js/charts.js, or
  templates/dashboard.html in this task — purely additive new files plus
  CSS token additions.
- Do NOT change any existing visual appearance — this is a foundation for
  later tasks to build on, not a visible redesign yet.
- Match the existing code's style: no comments explaining WHAT the code
  does, only WHY when something is non-obvious. No emoji anywhere (this
  codebase deliberately has none — professional/clean UI is a hard
  requirement from the user).

Acceptance criteria:
- static/css/dashboard.css still parses as valid CSS and the existing
  dashboard still renders identically (no visual regression) — you can
  verify by checking that you only ADDED custom properties and didn't
  remove/rename ones that grep shows are still referenced.
- New static/js/components/*.js files are syntactically valid
  (node --check each file after stripping the 'export' keyword, or just
  ensure valid JS syntax).
- Each component function is genuinely reusable — not hard-coded to one
  specific view's exact data shape.

When finished:
1. Show your diff / list of new files.
2. Explain the token set you chose and why.
3. Confirm no existing custom property was removed/renamed (show the grep
   check you ran).

[35m[3mcodex[0m[0m
I’ll inspect the existing CSS tokens, component styles, and `jobCardHTML` pattern first. Then I’ll add only the token definitions and new ES modules, followed by CSS/JS syntax checks and a scoped diff review.
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'pwd && rg -n "''^:root|--(bg|surface|surface-2|border|text|muted|green|red|yellow|blue|purple)'"\\b|status-pill|jobCardHTML\" static/css/dashboard.css static/js/dashboard.js && rg --files static/js static/css | sort"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
/Users/badripratti/Desktop/stock-screener
static/css/dashboard.css:1::root {
static/css/dashboard.css:2:  --bg: #0f1117;
static/css/dashboard.css:3:  --surface: #1a1d27;
static/css/dashboard.css:4:  --surface-2: #21242f;
static/css/dashboard.css:5:  --border: #2a2d3a;
static/css/dashboard.css:6:  --text: #e4e6eb;
static/css/dashboard.css:7:  --muted: #8b8fa3;
static/css/dashboard.css:8:  --green: #22c55e;
static/css/dashboard.css:9:  --red: #ef4444;
static/css/dashboard.css:10:  --yellow: #eab308;
static/css/dashboard.css:11:  --blue: #3b82f6;
static/css/dashboard.css:12:  --purple: #a855f7;
static/css/dashboard.css:15:body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
static/css/dashboard.css:22:  width: 220px; flex-shrink: 0; background: var(--surface);
static/css/dashboard.css:23:  border-right: 1px solid var(--border); padding: 20px 0;
static/css/dashboard.css:29:  color: var(--muted); text-decoration: none;
static/css/dashboard.css:32:.nav-item:hover { color: var(--text); background: rgba(255,255,255,0.03); }
static/css/dashboard.css:33:.nav-item.active { color: var(--text); background: rgba(59,130,246,0.08); border-left-color: var(--blue); }
static/css/dashboard.css:35:.nav-item-sub { display: block; font-size: 10.5px; color: var(--muted); opacity: 0.75; margin-top: 1px; }
static/css/dashboard.css:36:.sidebar-footer { margin-top: auto; padding: 16px 20px 0; color: var(--muted); font-size: 11px; }
static/css/dashboard.css:40:  background: var(--surface); border-bottom: 1px solid var(--border);
static/css/dashboard.css:44:.page-meta { color: var(--muted); font-size: 13px; }
static/css/dashboard.css:48:.btn { padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px; transition: all 0.15s; }
static/css/dashboard.css:49:.btn:hover { border-color: var(--blue); }
static/css/dashboard.css:50:.btn.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
static/css/dashboard.css:60:.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
static/css/dashboard.css:61:.stat-card .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
static/css/dashboard.css:63:.stat-card .sub { color: var(--muted); font-size: 12px; margin-top: 4px; }
static/css/dashboard.css:64:.stat-card.green .value { color: var(--green); }
static/css/dashboard.css:65:.stat-card.red .value { color: var(--red); }
static/css/dashboard.css:66:.stat-card.blue .value { color: var(--blue); }
static/css/dashboard.css:67:.stat-card.yellow .value { color: var(--yellow); }
static/css/dashboard.css:68:.stat-card.purple .value { color: var(--purple); }
static/css/dashboard.css:70:.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 16px; }
static/css/dashboard.css:72:.card .card-sub { color: var(--muted); font-size: 12px; margin-top: -10px; margin-bottom: 14px; }
static/css/dashboard.css:78:.signal-table th { text-align: left; padding: 10px 12px; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
static/css/dashboard.css:79:.signal-table td { padding: 12px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: top; }
static/css/dashboard.css:82:.ticker { font-weight: 700; font-size: 14px; color: var(--blue); }
static/css/dashboard.css:83:.score-bar { height: 6px; border-radius: 3px; background: var(--border); overflow: hidden; width: 80px; display: inline-block; vertical-align: middle; margin-left: 6px; }
static/css/dashboard.css:88:.badge.good { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:89:.badge.extended { background: rgba(234,179,8,0.15); color: var(--yellow); }
static/css/dashboard.css:90:.badge.poor { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:91:.badge.critical { background: rgba(239,68,68,0.25); color: var(--red); }
static/css/dashboard.css:92:.badge.high { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:93:.badge.medium { background: rgba(234,179,8,0.15); color: var(--yellow); }
static/css/dashboard.css:94:.badge.neutral { background: rgba(255,255,255,0.08); color: var(--muted); }
static/css/dashboard.css:104:.momentum-badge.stable { background: rgba(34,197,94,0.15); color: var(--green); border-color: rgba(34,197,94,0.3); }
static/css/dashboard.css:109:.reasons-list li { font-size: 11px; color: var(--muted); padding: 1px 0; }
static/css/dashboard.css:111:.expand-btn { background: none; border: none; color: var(--blue); cursor: pointer; font-size: 11px; padding: 2px 0; }
static/css/dashboard.css:115:.trade-link.buy { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:117:.trade-link.sell { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:120:.no-data { text-align: center; padding: 60px 20px; color: var(--muted); }
static/css/dashboard.css:121:.no-data h2 { font-size: 18px; margin-bottom: 8px; color: var(--text); }
static/css/dashboard.css:123:.banner { background: rgba(234,179,8,0.1); border: 1px solid rgba(234,179,8,0.3); color: var(--yellow); border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 20px; }
static/css/dashboard.css:124:.banner a { color: var(--yellow); text-decoration: underline; }
static/css/dashboard.css:131:.source-note.email { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.3); color: var(--purple); }
static/css/dashboard.css:132:.source-note.historical { background: rgba(59,130,246,0.08); border-color: rgba(59,130,246,0.3); color: var(--blue); }
static/css/dashboard.css:137:.regime-badge.risk-on { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:138:.regime-badge.risk-off { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:139:.regime-badge.transitional { background: rgba(234,179,8,0.15); color: var(--yellow); }
static/css/dashboard.css:141:.scan-select { background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 6px; font-size: 13px; }
static/css/dashboard.css:146:.news-headline { display: block; padding: 7px 0; border-bottom: 1px solid var(--border); text-decoration: none; }
static/css/dashboard.css:148:.news-headline-title { font-size: 12.5px; color: var(--text); line-height: 1.4; }
static/css/dashboard.css:149:.news-headline:hover .news-headline-title { color: var(--blue); }
static/css/dashboard.css:150:.news-headline-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }
static/css/dashboard.css:154:.pick-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px; position: relative; }
static/css/dashboard.css:156:.pick-rank { position: absolute; top: 14px; right: 16px; color: var(--muted); font-size: 12px; font-weight: 700; }
static/css/dashboard.css:160:.pick-scores .score-block .label { color: var(--muted); font-size: 10px; text-transform: uppercase; }
static/css/dashboard.css:164:.agent-badge.pos { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:165:.agent-badge.neg { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:166:.agent-badge.neu { background: rgba(255,255,255,0.06); color: var(--muted); }
static/css/dashboard.css:167:.agent-badge-sub { font-size: 11px; color: var(--muted); margin: -3px 0 3px 2px; }
static/css/dashboard.css:168:.backfill-note { font-size: 11px; color: var(--yellow); margin-bottom: 10px; }
static/css/dashboard.css:173:  background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px;
static/css/dashboard.css:174:  color: var(--text); cursor: pointer; padding: 0;
static/css/dashboard.css:177:.chart-toggle-btn:hover { border-color: var(--blue); color: var(--blue); background: rgba(59,130,246,0.1); }
static/css/dashboard.css:178:.chart-toggle-btn.active { border-color: var(--blue); background: rgba(59,130,246,0.12); color: var(--blue); }
static/css/dashboard.css:184:  font-size: 11px; font-weight: 600; color: var(--green); margin-left: 10px;
static/css/dashboard.css:186:.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: live-pulse 2s ease-in-out infinite; }
static/css/dashboard.css:190:.sim-card .sim-desc { color: var(--muted); font-size: 12px; margin-bottom: 14px; }
static/css/dashboard.css:192:.sim-params label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--muted); }
static/css/dashboard.css:194:  background: var(--surface-2); border: 1px solid var(--border); color: var(--text);
static/css/dashboard.css:198:  background: #0a0b10; border: 1px solid var(--border); border-radius: 8px; padding: 12px;
static/css/dashboard.css:199:  font-family: 'SF Mono', Menlo, monospace; font-size: 11px; color: var(--muted);
static/css/dashboard.css:202:.status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-left: 10px; }
static/css/dashboard.css:203:.status-pill.idle { background: rgba(255,255,255,0.06); color: var(--muted); }
static/css/dashboard.css:204:.status-pill.running { background: rgba(59,130,246,0.15); color: var(--blue); }
static/css/dashboard.css:205:.status-pill.success { background: rgba(34,197,94,0.15); color: var(--green); }
static/css/dashboard.css:206:.status-pill.error { background: rgba(239,68,68,0.15); color: var(--red); }
static/css/dashboard.css:211:.toast { position: fixed; bottom: 24px; right: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; font-size: 13px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); z-index: 100; transition: opacity 0.3s; max-width: 360px; }
static/js/dashboard.js:178:  if (count == null) return '<span style="color:var(--muted)">-</span>';
static/js/dashboard.js:179:  if (count === 0) return '<span style="color:var(--muted)">0</span>';
static/js/dashboard.js:181:  return `<span style="color:${hot ? 'var(--yellow)' : 'var(--text)'};font-weight:${hot ? 700 : 400}">${count}</span>`;
static/js/dashboard.js:256:    html += `<div class="agent-badge-sub" style="color:var(--red)">Red flag: ${escapeHtml(red[0].flag)}${more}</div>`;
static/js/dashboard.js:260:    html += `<div class="agent-badge-sub" style="color:var(--green)">Green flag: ${escapeHtml(green[0].flag)}${more}</div>`;
static/js/dashboard.js:290:function jobCardHTML(id, title, desc, paramsHTML) {
static/js/dashboard.js:293:      <h2>${title} <span class="status-pill idle" id="${id}-pill">idle</span></h2>
static/js/dashboard.js:345:        pill.className = 'status-pill running';
static/js/dashboard.js:349:        pill.className = `status-pill ${st.status}`;
static/js/dashboard.js:386:    pill.className = 'status-pill running';
static/js/dashboard.js:446:        <div class="pick-badges">${badges || '<span style="color:var(--muted);font-size:12px">No agent data</span>'}</div>
static/js/dashboard.js:513:      `<a href="${l.url}" target="_blank" rel="noopener" style="display:block;font-size:11px;color:var(--blue);text-decoration:none;margin-bottom:3px;">${l.label}${l.title ? ': ' + l.title.slice(0, 60) : ''}</a>`
static/js/dashboard.js:521:      <td>${links || '<span style="color:var(--muted);font-size:11px">No linked source yet</span>'}</td>
static/js/dashboard.js:548:      <a href="#/shortlist" style="color:var(--purple)">Shortlist</a> is just this data filtered down to 5.
static/js/dashboard.js:601:    bodyEl.innerHTML = `<div style="color:var(--muted);font-size:13px">${emptyMsg}</div>`;
static/js/dashboard.js:605:    bodyEl.innerHTML = '<div style="color:var(--muted);font-size:13px"><span class="spinner"></span> Fetching real headlines…</div>';
static/js/dashboard.js:615:      el.innerHTML = `<div style="color:var(--red);font-size:13px">Couldn't fetch news (${st.status}).</div>`;
static/js/dashboard.js:622:  if (!tickers.length) return '<div style="color:var(--muted);font-size:13px">No news found.</div>';
static/js/dashboard.js:631:      : '<div style="color:var(--muted);font-size:12px">No recent headlines.</div>';
static/js/dashboard.js:657:      <div class="stat-card blue"><div class="label">Top Score</div><div class="value">${topScore}<span style="font-size:14px;color:var(--muted)">/125</span></div><div class="sub">${scan.buy_signals.length ? scan.buy_signals[0].ticker : '-'}</div></div>
static/js/dashboard.js:667:          <div><div style="color:var(--muted);font-size:11px">Phase</div><div style="font-size:18px;font-weight:700">${scan.spy.phase} - ${scan.spy.phase_name || ''}</div></div>
static/js/dashboard.js:668:          <div><div style="color:var(--muted);font-size:11px">Confidence</div><div style="font-size:18px;font-weight:700">${scan.spy.confidence || '?'}%</div></div>
static/js/dashboard.js:674:      <h2 style="color:var(--green)">Buy Signals</h2>
static/js/dashboard.js:681:      <h2 style="color:var(--red)">Sell Signals</h2>
static/js/dashboard.js:699:  if (!signals.length) return '<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:30px">No buy signals</td></tr>';
static/js/dashboard.js:702:    const barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--blue)' : 'var(--yellow)';
static/js/dashboard.js:715:      <td style="color:${(s.rr_ratio || 0) >= 3 ? 'var(--green)' : (s.rr_ratio || 0) >= 2 ? 'var(--text)' : 'var(--yellow)'}">${s.rr_ratio ? s.rr_ratio.toFixed(1) + ':1' : '-'}</td>
static/js/dashboard.js:716:      <td style="color:${(s.rs || 0) > 0.1 ? 'var(--green)' : (s.rs || 0) > 0 ? 'var(--text)' : 'var(--red)'}">${s.rs != null ? s.rs.toFixed(3) : '-'}</td>
static/js/dashboard.js:725:  if (!signals.length) return '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:30px">No sell signals</td></tr>';
static/js/dashboard.js:760:        <span style="color:var(--muted);font-size:13px">Showing ${data.position_analyses.length} position${data.position_analyses.length === 1 ? '' : 's'} from your last upload.</span>
static/js/dashboard.js:766:      <h2>Upload Your Positions <span class="status-pill idle" id="pos-pill">idle</span></h2>
static/js/dashboard.js:772:      <input type="file" id="pos-file" accept=".csv" style="margin-bottom:12px;display:block;color:var(--text);font-size:13px">
static/js/dashboard.js:823:      pill.className = 'status-pill running';
static/js/dashboard.js:831:        pill.className = 'status-pill error';
static/js/dashboard.js:843:    pill.className = 'status-pill running';
static/js/dashboard.js:851:        pill.className = `status-pill ${st.status}`;
static/js/dashboard.js:874:    const gainColor = a.current_gain_pct >= 0 ? 'var(--green)' : 'var(--red)';
static/js/dashboard.js:882:      extra += `<div class="agent-badge-sub" style="color:var(--green);margin-top:6px">Add-on candidate — ${a.add_on_rationale}</div>`;
static/js/dashboard.js:885:      extra += `<div class="agent-badge-sub" style="color:var(--yellow)">${w}</div>`;
static/js/dashboard.js:936:      for those, see <a href="#/shortlist" style="color:var(--blue)">Shortlist</a> or

[1mapply patch[0m
[1mpatch:[0m completed
[2m/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css[0m
diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,57 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,57 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }

[1mapply patch[0m
[1mpatch:[0m completed
[2m/Users/badripratti/Desktop/stock-screener/static/js/components/data-table.js[0m
[2m/Users/badripratti/Desktop/stock-screener/static/js/components/empty-state.js[0m
[2m/Users/badripratti/Desktop/stock-screener/static/js/components/job-panel.js[0m
[2m/Users/badripratti/Desktop/stock-screener/static/js/components/metric-card.js[0m
[2m/Users/badripratti/Desktop/stock-screener/static/js/components/status-pill.js[0m
diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,57 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,57 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

[35m[3mcodex[0m[0m
The five builders are now in place. They preserve the current class/ID conventions for later migration, while remaining data-shape agnostic: tables accept column accessors/renderers/comparators, job panels accept arbitrary parameter/output/result markup, and all ordinary text/attributes are escaped. I’m moving through syntax, token-preservation, and diff-scope checks now.
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'set -e
for file in static/js/components/*.js; do
  node --input-type=module --check < "$file"
  echo "syntax ok: $file"
done
python3 - <<'"'PY'
from pathlib import Path
try:
    import tinycss2
except ImportError:
    print('tinycss2 unavailable; CSS parse check skipped')
else:
    path = Path('static/css/dashboard.css')
    rules = tinycss2.parse_stylesheet(path.read_text(), skip_comments=False, skip_whitespace=False)
    errors = [rule for rule in rules if rule.type == 'error']
    if errors:
        raise SystemExit('\\n'.join(str(error) for error in errors))
    print(f'CSS parse ok: {path}')
PY
git diff --check
if rg -n \"[🟢🔴🟡⭐⚠✓🚨]\" static/js/components static/css/dashboard.css; then
  exit 1
else
  echo 'no emoji found in TASK-002 files'
fi"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 285ms:[0m
syntax ok: static/js/components/data-table.js
syntax ok: static/js/components/empty-state.js
syntax ok: static/js/components/job-panel.js
syntax ok: static/js/components/metric-card.js
syntax ok: static/js/components/status-pill.js
tinycss2 unavailable; CSS parse check skipped
no emoji found in TASK-002 files

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,57 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'rg -n -C 5 "TASK-002|metric-card|data-table|job-panel|design system" .sprint README.md docs 2>/dev/null || true
command -v stylelint || true
command -v csslint || true
command -v sass || true
command -v node'[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
.sprint/SPRINT_PLAN.md-1-# UI Modernization Sprint Plan
.sprint/SPRINT_PLAN.md-2-
.sprint/SPRINT_PLAN.md-3-Full plan detail in the converged Engineering Council output (Claude + Codex;
.sprint/SPRINT_PLAN.md-4-Antigravity unavailable — headless permission tooling gap, not re-litigated).
.sprint/SPRINT_PLAN.md-5-
.sprint/SPRINT_PLAN.md:6:Decision: native ES modules + design system on vanilla JS. No React/Vue, no
.sprint/SPRINT_PLAN.md-7-build step — matches mac_app/'s "no rebuild needed" packaging model and
.sprint/SPRINT_PLAN.md-8-avoids re-risking the job-polling/live-refresh concurrency code already
.sprint/SPRINT_PLAN.md-9-fixed this session.
.sprint/SPRINT_PLAN.md-10-
.sprint/SPRINT_PLAN.md-11-## Tasks (revised ownership — objective split per updated sprint-build skill)
.sprint/SPRINT_PLAN.md-12-
.sprint/SPRINT_PLAN.md-13-- TASK-001 | Claude | Characterization tests for fragile async behaviors | no deps
.sprint/SPRINT_PLAN.md:14:- TASK-002 | Codex  | Design tokens (CSS) + reusable component builders | no deps
.sprint/SPRINT_PLAN.md-15-- TASK-003 | Claude | Extract router/jobs/refresh/api into core modules | deps: 001
.sprint/SPRINT_PLAN.md-16-- TASK-004 | Codex  | Migrate Positions + Shortlist views | deps: 002, 003
.sprint/SPRINT_PLAN.md-17-- TASK-005 | Codex  | Migrate Market + Backtests views | deps: 002, 003
.sprint/SPRINT_PLAN.md-18-- TASK-006 | Codex  | Migrate Simulations + Scan views + auto-sync form-state fix | deps: 002, 003
.sprint/SPRINT_PLAN.md-19-- TASK-007 | Claude | Nav/IA restructure (Monitor/Analyze/Run groups) | deps: 004,005,006
--
.sprint/STATUS.md-1-TASK-001 | Claude | RUNNING
.sprint/STATUS.md:2:TASK-002 | Codex  | RUNNING
.sprint/STATUS.md-3-TASK-003 | Claude | PENDING (blocked by 001)
.sprint/STATUS.md-4-TASK-004 | Codex  | PENDING (blocked by 002,003)
.sprint/STATUS.md-5-TASK-005 | Codex  | PENDING (blocked by 002,003)
.sprint/STATUS.md-6-TASK-006 | Codex  | PENDING (blocked by 002,003)
.sprint/STATUS.md-7-TASK-007 | Claude | PENDING (blocked by 004,005,006)
--
.sprint/council/codex-ui-redesign.md-3096-
.sprint/council/codex-ui-redesign.md-3097-The UI feels unstructured because the presentation system is fragmented even though the feature set is substantial.
.sprint/council/codex-ui-redesign.md-3098-
.sprint/council/codex-ui-redesign.md-3099-- Navigation is one undifferentiated list of six destinations. Monitoring pages, historical analysis, and destructive/expensive actions have equal visual weight in [dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:13).
.sprint/council/codex-ui-redesign.md-3100-- The shell provides only a title, free-form metadata, and a global Sync button. Views must invent their own hierarchy inside `content` ([dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:42)).
.sprint/council/codex-ui-redesign.md:3101:- The CSS has a small color palette, but not a complete design system. There are no semantic typography, spacing, elevation, focus, control-size, responsive, or light-theme tokens ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1)).
.sprint/council/codex-ui-redesign.md-3102-- Responsiveness is minimal: only `.grid-2` has an explicit breakpoint, while the sidebar remains fixed at 220px and tables depend on horizontal scrolling ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:21), [dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:54)).
.sprint/council/codex-ui-redesign.md-3103-- `dashboard.js` is 1,156 lines containing routing, API access, escaping, polling, job lifecycle, state, event binding, and all six view templates. That makes consistent UX changes risky and encourages one-off markup ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1)).
.sprint/council/codex-ui-redesign.md-3104-- There are approximately 73 inline `style` attributes and 41 `innerHTML` operations. For example, the Market view defines layout, color, tables, metrics, and chart containers in one large string ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:653)). This bypasses reusable CSS patterns and scatters behavior through DOM IDs.
.sprint/council/codex-ui-redesign.md-3105-- Each screen uses slightly different loading, error, empty-state, and action conventions. `fetchJSON`, for example, assumes every response is valid JSON and does not check HTTP status ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:164)).
.sprint/council/codex-ui-redesign.md-3106-- The UI uses very small 10–13px text extensively, particularly secondary navigation, table headers, badges, and descriptions. That increases visual density without establishing useful hierarchy.
--
.sprint/council/codex-ui-redesign.md-3146-    jobs.js
.sprint/council/codex-ui-redesign.md-3147-    refresh.js
.sprint/council/codex-ui-redesign.md-3148-    state.js
.sprint/council/codex-ui-redesign.md-3149-  components/
.sprint/council/codex-ui-redesign.md-3150-    page-header.js
.sprint/council/codex-ui-redesign.md:3151:    metric-card.js
.sprint/council/codex-ui-redesign.md:3152:    data-table.js
.sprint/council/codex-ui-redesign.md-3153-    status.js
.sprint/council/codex-ui-redesign.md:3154:    job-panel.js
.sprint/council/codex-ui-redesign.md-3155-    empty-state.js
.sprint/council/codex-ui-redesign.md-3156-  views/
.sprint/council/codex-ui-redesign.md-3157-    positions.js
.sprint/council/codex-ui-redesign.md-3158-    shortlist.js
.sprint/council/codex-ui-redesign.md-3159-    market.js
--
.sprint/council/codex-ui-redesign.md-3345-
.sprint/council/codex-ui-redesign.md-3346-The UI feels unstructured because the presentation system is fragmented even though the feature set is substantial.
.sprint/council/codex-ui-redesign.md-3347-
.sprint/council/codex-ui-redesign.md-3348-- Navigation is one undifferentiated list of six destinations. Monitoring pages, historical analysis, and destructive/expensive actions have equal visual weight in [dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:13).
.sprint/council/codex-ui-redesign.md-3349-- The shell provides only a title, free-form metadata, and a global Sync button. Views must invent their own hierarchy inside `content` ([dashboard.html](/Users/badripratti/Desktop/stock-screener/templates/dashboard.html:42)).
.sprint/council/codex-ui-redesign.md:3350:- The CSS has a small color palette, but not a complete design system. There are no semantic typography, spacing, elevation, focus, control-size, responsive, or light-theme tokens ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1)).
.sprint/council/codex-ui-redesign.md-3351-- Responsiveness is minimal: only `.grid-2` has an explicit breakpoint, while the sidebar remains fixed at 220px and tables depend on horizontal scrolling ([dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:21), [dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:54)).
.sprint/council/codex-ui-redesign.md-3352-- `dashboard.js` is 1,156 lines containing routing, API access, escaping, polling, job lifecycle, state, event binding, and all six view templates. That makes consistent UX changes risky and encourages one-off markup ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:1)).
.sprint/council/codex-ui-redesign.md-3353-- There are approximately 73 inline `style` attributes and 41 `innerHTML` operations. For example, the Market view defines layout, color, tables, metrics, and chart containers in one large string ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:653)). This bypasses reusable CSS patterns and scatters behavior through DOM IDs.
.sprint/council/codex-ui-redesign.md-3354-- Each screen uses slightly different loading, error, empty-state, and action conventions. `fetchJSON`, for example, assumes every response is valid JSON and does not check HTTP status ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:164)).
.sprint/council/codex-ui-redesign.md-3355-- The UI uses very small 10–13px text extensively, particularly secondary navigation, table headers, badges, and descriptions. That increases visual density without establishing useful hierarchy.
--
.sprint/council/codex-ui-redesign.md-3395-    jobs.js
.sprint/council/codex-ui-redesign.md-3396-    refresh.js
.sprint/council/codex-ui-redesign.md-3397-    state.js
.sprint/council/codex-ui-redesign.md-3398-  components/
.sprint/council/codex-ui-redesign.md-3399-    page-header.js
.sprint/council/codex-ui-redesign.md:3400:    metric-card.js
.sprint/council/codex-ui-redesign.md:3401:    data-table.js
.sprint/council/codex-ui-redesign.md-3402-    status.js
.sprint/council/codex-ui-redesign.md:3403:    job-panel.js
.sprint/council/codex-ui-redesign.md-3404-    empty-state.js
.sprint/council/codex-ui-redesign.md-3405-  views/
.sprint/council/codex-ui-redesign.md-3406-    positions.js
.sprint/council/codex-ui-redesign.md-3407-    shortlist.js
.sprint/council/codex-ui-redesign.md-3408-    market.js
--
.sprint/results/TASK-002-codex.md-10-[1mreasoning summaries:[0m none
.sprint/results/TASK-002-codex.md-11-[1msession id:[0m 01a09ddb-d3c1-7062-968c-369e361e0b57
.sprint/results/TASK-002-codex.md-12---------
.sprint/results/TASK-002-codex.md-13-[36muser[0m
.sprint/results/TASK-002-codex.md-14-
.sprint/results/TASK-002-codex.md:15:You are implementing TASK-002 in an approved sprint.
.sprint/results/TASK-002-codex.md-16-
.sprint/results/TASK-002-codex.md-17-Repository:
.sprint/results/TASK-002-codex.md-18-/Users/badripratti/Desktop/stock-screener
.sprint/results/TASK-002-codex.md-19-
.sprint/results/TASK-002-codex.md-20-Task:
.sprint/results/TASK-002-codex.md:21:Build a design system for the dashboard UI WITHOUT touching any existing
.sprint/results/TASK-002-codex.md-22-view-rendering logic yet (that's later tasks). This is purely additive —
.sprint/results/TASK-002-codex.md-23-new CSS tokens and new reusable component-builder JS modules that later
.sprint/results/TASK-002-codex.md-24-tasks will consume.
.sprint/results/TASK-002-codex.md-25-
.sprint/results/TASK-002-codex.md-26-Goal:
--
.sprint/results/TASK-002-codex.md-38-   Do not delete or rename any existing custom property that other CSS
.sprint/results/TASK-002-codex.md-39-   rules still reference — check with grep before renaming anything.
.sprint/results/TASK-002-codex.md-40-2. Create new static/js/components/ with small, framework-free component
.sprint/results/TASK-002-codex.md-41-   builder functions (each returns an HTML string, matching the existing
.sprint/results/TASK-002-codex.md-42-   codebase's template-literal style):
.sprint/results/TASK-002-codex.md:43:   - metric-card.js: a stat card (label, value, sub-label, color variant)
.sprint/results/TASK-002-codex.md-44-   - status-pill.js: a status badge (idle/running/success/error, matching
.sprint/results/TASK-002-codex.md-45-     existing .status-pill CSS classes)
.sprint/results/TASK-002-codex.md:46:   - data-table.js: a sortable table shell (headers, rows, sort-by-column
.sprint/results/TASK-002-codex.md-47-     support) — this should be genuinely reusable, not tied to one view's
.sprint/results/TASK-002-codex.md-48-     data shape
.sprint/results/TASK-002-codex.md-49-   - empty-state.js: a 'no data yet' placeholder block
.sprint/results/TASK-002-codex.md:50:   - job-panel.js: the run/output/status-pill card pattern already used in
.sprint/results/TASK-002-codex.md-51-     Run Simulation (see jobCardHTML in static/js/dashboard.js) — extract
.sprint/results/TASK-002-codex.md-52-     and generalize it
.sprint/results/TASK-002-codex.md-53-   Use ES module syntax (export function ...). These will be consumed by
.sprint/results/TASK-002-codex.md-54-   later view-migration tasks via <script type="module"> — no bundler,
.sprint/results/TASK-002-codex.md-55-   no build step, this repo has none and won't be adding one.
--
.sprint/results/TASK-002-codex.md-613-[1m/bin/zsh -lc 'git status --short && git diff -- static/css/dashboard.css static/js/dashboard.js static/js/charts.js templates/dashboard.html && rg -n "function (escapeHtml|.*HTML)|const escapeHtml|=>.*replace" static/js/dashboard.js | head -40'[0m in /Users/badripratti/Desktop/stock-screener
.sprint/results/TASK-002-codex.md-614-[32m succeeded in 36ms:[0m
.sprint/results/TASK-002-codex.md-615- M .sprint/SPRINT_PLAN.md
.sprint/results/TASK-002-codex.md-616- M .sprint/STATUS.md
.sprint/results/TASK-002-codex.md-617-?? .sprint/council/
.sprint/results/TASK-002-codex.md:618:?? .sprint/results/TASK-002-codex.md
.sprint/results/TASK-002-codex.md-619-?? tests/js/
.sprint/results/TASK-002-codex.md-620-57:function liveBadgeHTML() {
.sprint/results/TASK-002-codex.md-621-82:function chartToggleButtonHTML(chartId) {
.sprint/results/TASK-002-codex.md-622-137:function momentumBadgeHTML(entry) {
.sprint/results/TASK-002-codex.md-623-194:function escapeHtml(text) {
--
.sprint/results/TASK-002-codex.md-628-593:function _newsSectionHTML(group, title, bodyHTML) {
.sprint/results/TASK-002-codex.md-629-620:function _renderNewsGroupHTML(newsByTicker) {
.sprint/results/TASK-002-codex.md-630-752:function _positionsUploadCardHTML(data, expanded) {
.sprint/results/TASK-002-codex.md-631-
.sprint/results/TASK-002-codex.md-632-[35m[3mexec[0m[0m
.sprint/results/TASK-002-codex.md:633:[1m/bin/zsh -lc "find tests/js -maxdepth 2 -type f -print -exec sed -n '1,240p' {} \\; && sed -n '185,205p' static/js/dashboard.js && sed -n '1,220p' .sprint/results/TASK-002-codex.md"[0m in /Users/badripratti/Desktop/stock-screener
.sprint/results/TASK-002-codex.md-634-[32m succeeded in 0ms:[0m
.sprint/results/TASK-002-codex.md-635-tests/js/test_live_guard.js
.sprint/results/TASK-002-codex.md-636-// Characterization test for _liveGuarded (static/js/dashboard.js) — locks in
.sprint/results/TASK-002-codex.md-637-// the current dedup behavior BEFORE the router/jobs/refresh extraction
.sprint/results/TASK-002-codex.md-638-// (TASK-003) touches this code. If this test breaks during that refactor,
--
.sprint/results/TASK-002-codex.md-736-[1mreasoning summaries:[0m none
.sprint/results/TASK-002-codex.md-737-[1msession id:[0m 01a09ddb-d3c1-7062-968c-369e361e0b57
.sprint/results/TASK-002-codex.md-738---------
.sprint/results/TASK-002-codex.md-739-[36muser[0m
.sprint/results/TASK-002-codex.md-740-
.sprint/results/TASK-002-codex.md:741:You are implementing TASK-002 in an approved sprint.
.sprint/results/TASK-002-codex.md-742-
.sprint/results/TASK-002-codex.md-743-Repository:
.sprint/results/TASK-002-codex.md-744-/Users/badripratti/Desktop/stock-screener
.sprint/results/TASK-002-codex.md-745-
.sprint/results/TASK-002-codex.md-746-Task:
.sprint/results/TASK-002-codex.md:747:Build a design system for the dashboard UI WITHOUT touching any existing
.sprint/results/TASK-002-codex.md-748-view-rendering logic yet (that's later tasks). This is purely additive —
.sprint/results/TASK-002-codex.md-749-new CSS tokens and new reusable component-builder JS modules that later
.sprint/results/TASK-002-codex.md-750-tasks will consume.
.sprint/results/TASK-002-codex.md-751-
.sprint/results/TASK-002-codex.md-752-Goal:
--
.sprint/results/TASK-002-codex.md-764-   Do not delete or rename any existing custom property that other CSS
.sprint/results/TASK-002-codex.md-765-   rules still reference — check with grep before renaming anything.
.sprint/results/TASK-002-codex.md-766-2. Create new static/js/components/ with small, framework-free component
.sprint/results/TASK-002-codex.md-767-   builder functions (each returns an HTML string, matching the existing
.sprint/results/TASK-002-codex.md-768-   codebase's template-literal style):
.sprint/results/TASK-002-codex.md:769:   - metric-card.js: a stat card (label, value, sub-label, color variant)
.sprint/results/TASK-002-codex.md-770-   - status-pill.js: a status badge (idle/running/success/error, matching
.sprint/results/TASK-002-codex.md-771-     existing .status-pill CSS classes)
.sprint/results/TASK-002-codex.md:772:   - data-table.js: a sortable table shell (headers, rows, sort-by-column
.sprint/results/TASK-002-codex.md-773-     support) — this should be genuinely reusable, not tied to one view's
.sprint/results/TASK-002-codex.md-774-     data shape
.sprint/results/TASK-002-codex.md-775-   - empty-state.js: a 'no data yet' placeholder block
.sprint/results/TASK-002-codex.md:776:   - job-panel.js: the run/output/status-pill card pattern already used in
.sprint/results/TASK-002-codex.md-777-     Run Simulation (see jobCardHTML in static/js/dashboard.js) — extract
.sprint/results/TASK-002-codex.md-778-     and generalize it
.sprint/results/TASK-002-codex.md-779-   Use ES module syntax (export function ...). These will be consumed by
.sprint/results/TASK-002-codex.md-780-   later view-migration tasks via <script type="module"> — no bundler,
.sprint/results/TASK-002-codex.md-781-   no build step, this repo has none and won't be adding one.
--
.sprint/results/TASK-002-codex.md-1074- * { margin: 0; padding: 0; box-sizing: border-box; }
.sprint/results/TASK-002-codex.md-1075- body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
.sprint/results/TASK-002-codex.md-1076-
.sprint/results/TASK-002-codex.md-1077-[1mapply patch[0m
.sprint/results/TASK-002-codex.md-1078-[1mpatch:[0m completed
.sprint/results/TASK-002-codex.md:1079:[2m/Users/badripratti/Desktop/stock-screener/static/js/components/data-table.js[0m
.sprint/results/TASK-002-codex.md-1080-[2m/Users/badripratti/Desktop/stock-screener/static/js/components/empty-state.js[0m
.sprint/results/TASK-002-codex.md:1081:[2m/Users/badripratti/Desktop/stock-screener/static/js/components/job-panel.js[0m
.sprint/results/TASK-002-codex.md:1082:[2m/Users/badripratti/Desktop/stock-screener/static/js/components/metric-card.js[0m
.sprint/results/TASK-002-codex.md-1083-[2m/Users/badripratti/Desktop/stock-screener/static/js/components/status-pill.js[0m
.sprint/results/TASK-002-codex.md-1084-diff --git a/static/css/dashboard.css b/static/css/dashboard.css
.sprint/results/TASK-002-codex.md-1085-index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
.sprint/results/TASK-002-codex.md-1086---- a/static/css/dashboard.css
.sprint/results/TASK-002-codex.md-1087-+++ b/static/css/dashboard.css
--
.sprint/results/TASK-002-codex.md-1141-+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
.sprint/results/TASK-002-codex.md-1142-+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
.sprint/results/TASK-002-codex.md-1143- }
.sprint/results/TASK-002-codex.md-1144- * { margin: 0; padding: 0; box-sizing: border-box; }
.sprint/results/TASK-002-codex.md-1145- body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
.sprint/results/TASK-002-codex.md:1146:diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
.sprint/results/TASK-002-codex.md-1147-new file mode 100644
.sprint/results/TASK-002-codex.md-1148-index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
.sprint/results/TASK-002-codex.md-1149---- /dev/null
.sprint/results/TASK-002-codex.md:1150:+++ b/static/js/components/data-table.js
.sprint/results/TASK-002-codex.md-1151-@@ -0,0 +1,90 @@
.sprint/results/TASK-002-codex.md-1152-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1153-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1154-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1155-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1258-+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
.sprint/results/TASK-002-codex.md-1259-+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
.sprint/results/TASK-002-codex.md-1260-+
.sprint/results/TASK-002-codex.md-1261-+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
.sprint/results/TASK-002-codex.md-1262-+}
.sprint/results/TASK-002-codex.md:1263:diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
.sprint/results/TASK-002-codex.md-1264-new file mode 100644
.sprint/results/TASK-002-codex.md-1265-index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
.sprint/results/TASK-002-codex.md-1266---- /dev/null
.sprint/results/TASK-002-codex.md:1267:+++ b/static/js/components/job-panel.js
.sprint/results/TASK-002-codex.md-1268-@@ -0,0 +1,37 @@
.sprint/results/TASK-002-codex.md-1269-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1270-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1271-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1272-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1301-+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
.sprint/results/TASK-002-codex.md-1302-+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
.sprint/results/TASK-002-codex.md-1303-+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
.sprint/results/TASK-002-codex.md-1304-+    </div>`;
.sprint/results/TASK-002-codex.md-1305-+}
.sprint/results/TASK-002-codex.md:1306:diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
.sprint/results/TASK-002-codex.md-1307-new file mode 100644
.sprint/results/TASK-002-codex.md-1308-index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
.sprint/results/TASK-002-codex.md-1309---- /dev/null
.sprint/results/TASK-002-codex.md:1310:+++ b/static/js/components/metric-card.js
.sprint/results/TASK-002-codex.md-1311-@@ -0,0 +1,17 @@
.sprint/results/TASK-002-codex.md-1312-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1313-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1314-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1315-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1410-+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
.sprint/results/TASK-002-codex.md-1411-+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
.sprint/results/TASK-002-codex.md-1412- }
.sprint/results/TASK-002-codex.md-1413- * { margin: 0; padding: 0; box-sizing: border-box; }
.sprint/results/TASK-002-codex.md-1414- body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
.sprint/results/TASK-002-codex.md:1415:diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
.sprint/results/TASK-002-codex.md-1416-new file mode 100644
.sprint/results/TASK-002-codex.md-1417-index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
.sprint/results/TASK-002-codex.md-1418---- /dev/null
.sprint/results/TASK-002-codex.md:1419:+++ b/static/js/components/data-table.js
.sprint/results/TASK-002-codex.md-1420-@@ -0,0 +1,90 @@
.sprint/results/TASK-002-codex.md-1421-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1422-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1423-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1424-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1527-+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
.sprint/results/TASK-002-codex.md-1528-+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
.sprint/results/TASK-002-codex.md-1529-+
.sprint/results/TASK-002-codex.md-1530-+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
.sprint/results/TASK-002-codex.md-1531-+}
.sprint/results/TASK-002-codex.md:1532:diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
.sprint/results/TASK-002-codex.md-1533-new file mode 100644
.sprint/results/TASK-002-codex.md-1534-index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
.sprint/results/TASK-002-codex.md-1535---- /dev/null
.sprint/results/TASK-002-codex.md:1536:+++ b/static/js/components/job-panel.js
.sprint/results/TASK-002-codex.md-1537-@@ -0,0 +1,37 @@
.sprint/results/TASK-002-codex.md-1538-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1539-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1540-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1541-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1570-+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
.sprint/results/TASK-002-codex.md-1571-+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
.sprint/results/TASK-002-codex.md-1572-+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
.sprint/results/TASK-002-codex.md-1573-+    </div>`;
.sprint/results/TASK-002-codex.md-1574-+}
.sprint/results/TASK-002-codex.md:1575:diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
.sprint/results/TASK-002-codex.md-1576-new file mode 100644
.sprint/results/TASK-002-codex.md-1577-index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
.sprint/results/TASK-002-codex.md-1578---- /dev/null
.sprint/results/TASK-002-codex.md:1579:+++ b/static/js/components/metric-card.js
.sprint/results/TASK-002-codex.md-1580-@@ -0,0 +1,17 @@
.sprint/results/TASK-002-codex.md-1581-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1582-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1583-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1584-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1643-PY
.sprint/results/TASK-002-codex.md-1644-git diff --check
.sprint/results/TASK-002-codex.md-1645-if rg -n \"[🟢🔴🟡⭐⚠✓🚨]\" static/js/components static/css/dashboard.css; then
.sprint/results/TASK-002-codex.md-1646-  exit 1
.sprint/results/TASK-002-codex.md-1647-else
.sprint/results/TASK-002-codex.md:1648:  echo 'no emoji found in TASK-002 files'
.sprint/results/TASK-002-codex.md-1649-fi"[0m in /Users/badripratti/Desktop/stock-screener
.sprint/results/TASK-002-codex.md-1650-[32m succeeded in 285ms:[0m
.sprint/results/TASK-002-codex.md:1651:syntax ok: static/js/components/data-table.js
.sprint/results/TASK-002-codex.md-1652-syntax ok: static/js/components/empty-state.js
.sprint/results/TASK-002-codex.md:1653:syntax ok: static/js/components/job-panel.js
.sprint/results/TASK-002-codex.md:1654:syntax ok: static/js/components/metric-card.js
.sprint/results/TASK-002-codex.md-1655-syntax ok: static/js/components/status-pill.js
.sprint/results/TASK-002-codex.md-1656-tinycss2 unavailable; CSS parse check skipped
.sprint/results/TASK-002-codex.md:1657:no emoji found in TASK-002 files
.sprint/results/TASK-002-codex.md-1658-
.sprint/results/TASK-002-codex.md-1659-diff --git a/static/css/dashboard.css b/static/css/dashboard.css
.sprint/results/TASK-002-codex.md-1660-index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
.sprint/results/TASK-002-codex.md-1661---- a/static/css/dashboard.css
.sprint/results/TASK-002-codex.md-1662-+++ b/static/css/dashboard.css
--
.sprint/results/TASK-002-codex.md-1716-+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
.sprint/results/TASK-002-codex.md-1717-+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
.sprint/results/TASK-002-codex.md-1718- }
.sprint/results/TASK-002-codex.md-1719- * { margin: 0; padding: 0; box-sizing: border-box; }
.sprint/results/TASK-002-codex.md-1720- body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
.sprint/results/TASK-002-codex.md:1721:diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
.sprint/results/TASK-002-codex.md-1722-new file mode 100644
.sprint/results/TASK-002-codex.md-1723-index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
.sprint/results/TASK-002-codex.md-1724---- /dev/null
.sprint/results/TASK-002-codex.md:1725:+++ b/static/js/components/data-table.js
.sprint/results/TASK-002-codex.md-1726-@@ -0,0 +1,90 @@
.sprint/results/TASK-002-codex.md-1727-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1728-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1729-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1730-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1833-+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
.sprint/results/TASK-002-codex.md-1834-+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
.sprint/results/TASK-002-codex.md-1835-+
.sprint/results/TASK-002-codex.md-1836-+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
.sprint/results/TASK-002-codex.md-1837-+}
.sprint/results/TASK-002-codex.md:1838:diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
.sprint/results/TASK-002-codex.md-1839-new file mode 100644
.sprint/results/TASK-002-codex.md-1840-index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
.sprint/results/TASK-002-codex.md-1841---- /dev/null
.sprint/results/TASK-002-codex.md:1842:+++ b/static/js/components/job-panel.js
.sprint/results/TASK-002-codex.md-1843-@@ -0,0 +1,37 @@
.sprint/results/TASK-002-codex.md-1844-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1845-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1846-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1847-+    .replaceAll('<', '&lt;')
--
.sprint/results/TASK-002-codex.md-1876-+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
.sprint/results/TASK-002-codex.md-1877-+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
.sprint/results/TASK-002-codex.md-1878-+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
.sprint/results/TASK-002-codex.md-1879-+    </div>`;
.sprint/results/TASK-002-codex.md-1880-+}
.sprint/results/TASK-002-codex.md:1881:diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
.sprint/results/TASK-002-codex.md-1882-new file mode 100644
.sprint/results/TASK-002-codex.md-1883-index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
.sprint/results/TASK-002-codex.md-1884---- /dev/null
.sprint/results/TASK-002-codex.md:1885:+++ b/static/js/components/metric-card.js
.sprint/results/TASK-002-codex.md-1886-@@ -0,0 +1,17 @@
.sprint/results/TASK-002-codex.md-1887-+function escapeHtml(value) {
.sprint/results/TASK-002-codex.md-1888-+  return String(value ?? '')
.sprint/results/TASK-002-codex.md-1889-+    .replaceAll('&', '&amp;')
.sprint/results/TASK-002-codex.md-1890-+    .replaceAll('<', '&lt;')
/opt/homebrew/bin/node

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,57 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '3120,3185p' .sprint/council/codex-ui-redesign.md"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 0ms:[0m
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:47) — Flask/static configuration.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:280) — background subprocess/job implementation.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:524) — job API.
- [dashboard.py](/Users/badripratti/Desktop/stock-screener/dashboard.py:670) — dashboard and data routes.
- [mac_app/main.py](/Users/badripratti/Desktop/stock-screener/mac_app/main.py:29) — live project-root loading and threaded pywebview host.
- [mac_app/setup.py](/Users/badripratti/Desktop/stock-screener/mac_app/setup.py:16) — py2app contents.
- [mac_app/README.md](/Users/badripratti/Desktop/stock-screener/mac_app/README.md:9) — current “frontend changes require no app rebuild” deployment assumption.

There are currently no dashboard/API/polling tests under `tests/`.

## 4. Recommended solution

Use a design-system-on-vanilla-JS approach, combined with a serious modular refactor. Do not introduce React/Vue or a required runtime build step for this iteration.

The application has only six routes, no authentication or collaborative state, and relatively simple interactions. Its complexity comes from asynchronous jobs and refresh lifecycle—not from a component tree that requires a virtual DOM. A framework would reorganize the code, but it would not automatically solve the product hierarchy and would substantially increase rewrite and packaging risk.

### Proposed frontend structure

Use native ES modules served directly by Flask:

```text
static/js/
  app.js
  core/
    api.js
    router.js
    jobs.js
    refresh.js
    state.js
  components/
    page-header.js
    metric-card.js
    data-table.js
    status.js
    job-panel.js
    empty-state.js
  views/
    positions.js
    shortlist.js
    market.js
    backtests.js
    simulations.js
    scan.js
  charts/
    theme.js
    renderers.js
```

These can run directly in WebKit using `<script type="module">`; no bundler is required.

### Information architecture

Group navigation by intent:

- Monitor: Positions, Shortlist, Market
- Analyze: Backtests
- Run: Simulations, Full Scan

Make expensive actions visually distinct from passive monitoring. Give every screen the same header anatomy:

- Title and one-line purpose
- “Last updated” or selected snapshot
- Live/sync state
- Contextual primary action

Resolve the current default-route inconsistency: routing defaults to Positions, while the Shortlist section is commented as the default landing view ([dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:26), [dashboard.js](/Users/badripratti/Desktop/stock-screener/static/js/dashboard.js:399)).

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..c52ac0856a9a12e270d54f92b42f6d1031734a63
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,57 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

[1mapply patch[0m
[1mpatch:[0m completed
[2m/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css[0m
diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "node --input-type=module <<'NODE'
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

async function load(name) {
  const source = await fs.readFile("'`static/js/components/${name}.js`, '"'utf8');
  return import("'`data:text/javascript;base64,${Buffer.from(source).toString('"'base64')}"'`);
}

const { metricCardHTML } = await load('"'metric-card');
const { statusPillHTML } = await load('status-pill');
const { dataTableHTML } = await load('data-table');
const { emptyStateHTML } = await load('empty-state');
const { jobPanelHTML } = await load('job-panel');

assert.match(metricCardHTML({ label: '<Label>', value: 0, subLabel: 'sub', variant: 'green' }), /class=\"stat-card green\"/);
assert.match(metricCardHTML({ label: '<Label>', value: 0 }), /&lt;Label&gt;/);
assert.match(statusPillHTML({ status: 'error', id: 'scan-pill' }), /class=\"status-pill error\" id=\"scan-pill\">error/);
const table = dataTableHTML({
  headers: [{ key: 'score', label: 'Score' }, { key: 'name', label: 'Name', sortable: false }],
  rows: [{ score: 2, name: 'B' }, { score: 10, name: 'A' }],
  sortBy: 'score',
  sortDirection: 'desc',
});
assert.ok(table.indexOf('<td>10</td>') < table.indexOf('<td>2</td>'));
assert.match(table, /data-sort-by=\"score\" data-sort-direction=\"desc\"/);
assert.match(table, /aria-sort=\"descending\"/);
assert.match(emptyStateHTML({ title: 'None', message: '<unsafe>' }), /&lt;unsafe&gt;/);
assert.match(jobPanelHTML({ id: 'mc', title: 'Monte Carlo', paramsHTML: '<label>Runs</label>' }), /id=\"mc-run\"/);
assert.match(jobPanelHTML({ id: 'mc', title: 'Monte Carlo', paramsHTML: '<label>Runs</label>' }), /<div class=\"sim-params\"><label>Runs<\\/label><\\/div>/);
console.log('component smoke tests: all assertions passed');
NODE
baseline_tokens="'$(git show HEAD:static/css/dashboard.css | sed -n '"'/"'^:root {/,/''^}/p'"' | rg -o -- '--[a-z0-9-]+(?=:)' | sort)
current_tokens="'$(sed -n '"'/"'^:root {/,/''^}/p'"' static/css/dashboard.css | rg -o -- '--[a-z0-9-]+(?=:)' | sort)
missing_tokens="'$(comm -23 <(print -r -- "$baseline_tokens") <(print -r -- "$current_tokens"))
if [[ -n "$missing_tokens" ]]; then
  print -r -- "missing legacy tokens:"
  print -r -- "$missing_tokens"
  exit 1
fi
print -r -- '"'legacy token preservation: all baseline tokens remain'
print -r -- \""'$baseline_tokens"
'[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 49ms:[0m
(node:75451) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
component smoke tests: all assertions passed
rg: regex parse error:
    (?:--[a-z0-9-]+(?=:))
                   ^^^
error: look-around, including look-ahead and look-behind, is not supported

Consider enabling PCRE2 with the --pcre2 flag, which can handle backreferences
and look-around.
rg: regex parse error:
    (?:--[a-z0-9-]+(?=:))
                   ^^^
error: look-around, including look-ahead and look-behind, is not supported

Consider enabling PCRE2 with the --pcre2 flag, which can handle backreferences
and look-around.
legacy token preservation: all baseline tokens remain


diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..207bed98e502794d1b0825044521e7b2354cb7d1
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = status,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..8c76b9c598fd916f8b54ffec5271088be95741c3
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = status, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label)}</span>`;
+}

[1mapply patch[0m
[1mpatch:[0m completed
[2m/Users/badripratti/Desktop/stock-screener/static/js/components/job-panel.js[0m
[2m/Users/badripratti/Desktop/stock-screener/static/js/components/status-pill.js[0m
diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..583ab569571f82bc85da93856eb6bf36a999c20b
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = null,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..3b70f940cb4234908d9e54fc45928a9f66ffd8d5
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
+}

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..583ab569571f82bc85da93856eb6bf36a999c20b
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = null,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..3b70f940cb4234908d9e54fc45928a9f66ffd8d5
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
+}

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'set -e
baseline_tokens=$(git show HEAD:static/css/dashboard.css | sed -n '"'/"'^:root {/,/''^}/p'"' | rg -o -- '--[a-z0-9-]+:' | tr -d ':' | sort)
current_tokens="'$(sed -n '"'/"'^:root {/,/''^}/p'"' static/css/dashboard.css | rg -o -- '--[a-z0-9-]+:' | tr -d ':' | sort)
missing_tokens="'$(comm -23 <(print -r -- "$baseline_tokens") <(print -r -- "$current_tokens"))
[[ -z "$missing_tokens" ]]
print -r -- '"'legacy token preservation: all baseline tokens remain'
for token in "'$=baseline_tokens; do
  references=$(rg -o --glob '"'*.css' --glob '*.js' -- \"var\\\\("'$token'"\\\\)\" static | wc -l | tr -d ' ')
  print -r -- \""'$token references=$references"
done
print -r -- '"'forbidden tracked-file diff:'
git diff --name-only -- static/js/dashboard.js static/js/charts.js templates/dashboard.html
print -r -- 'TASK-002 status:'
git status --short -- static/css/dashboard.css static/js/components static/js/dashboard.js static/js/charts.js templates/dashboard.html
print -r -- 'TASK-002 diff stat:'
git diff --stat -- static/css/dashboard.css
for file in static/js/components/*.js; do wc -l \""'$file"; done'[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 188ms:[0m
legacy token preservation: all baseline tokens remain
--bg references=2
--blue references=20
--border references=16
--green references=21
--muted references=37
--purple references=4
--red references=18
--surface references=9
--surface-2 references=3
--text references=14
--yellow references=12
forbidden tracked-file diff:
TASK-002 status:
 M static/css/dashboard.css
?? static/js/components/
TASK-002 diff stat:
 static/css/dashboard.css | 53 ++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 53 insertions(+)
      90 static/js/components/data-table.js
      15 static/js/components/empty-state.js
      37 static/js/components/job-panel.js
      17 static/js/components/metric-card.js
      17 static/js/components/status-pill.js

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..583ab569571f82bc85da93856eb6bf36a999c20b
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = null,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..3b70f940cb4234908d9e54fc45928a9f66ffd8d5
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
+}

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'git diff -- static/css/dashboard.css
for file in static/js/components/*.js; do
  git diff --no-index -- /dev/null "$file" || [[ $? -eq 1 ]]
done'[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 90ms:[0m
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 00000000..c2766566
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 00000000..f03ebb27
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 00000000..583ab569
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = null,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 00000000..639cdf91
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 00000000..3b70f940
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
+}

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..583ab569571f82bc85da93856eb6bf36a999c20b
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = null,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..3b70f940cb4234908d9e54fc45928a9f66ffd8d5
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
+}

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'npm root -g && find "$(npm root -g)" -maxdepth 2 -type d '"\\( -name postcss -o -name css-tree -o -name stylelint \\) -print 2>/dev/null
set -e
for file in static/js/components/*.js; do node --input-type=module --check < \""'$file"; done
node tests/js/test_live_guard.js
git diff --check
git diff --quiet -- static/js/dashboard.js static/js/charts.js templates/dashboard.html
python3 - <<'"'PY'
from pathlib import Path
css = Path('static/css/dashboard.css').read_text()
assert css.count('{') == css.count('}'), 'unbalanced CSS blocks'
root = css[css.index(':root {'):css.index('}\\n', css.index(':root {'))]
for line in root.splitlines()[1:]:
    line = line.strip()
    if line:
        assert line.startswith('--') and line.endswith(';') and ':' in line, line
print('CSS custom-property block structure: valid')
PY
printf '%s\\n' 'final verification: passed'"[0m in /Users/badripratti/Desktop/stock-screener
[32m succeeded in 388ms:[0m
/opt/homebrew/lib/node_modules
(node:75586) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
test_live_guard.js: all assertions passed
CSS custom-property block structure: valid
final verification: passed

diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..583ab569571f82bc85da93856eb6bf36a999c20b
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = null,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..3b70f940cb4234908d9e54fc45928a9f66ffd8d5
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
+}

[35m[3mcodex[0m[0m
Implemented TASK-002 as a purely additive foundation.

Changed files:

- [dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1) — 53 new token declarations.
- [metric-card.js](/Users/badripratti/Desktop/stock-screener/static/js/components/metric-card.js:1)
- [status-pill.js](/Users/badripratti/Desktop/stock-screener/static/js/components/status-pill.js:1)
- [data-table.js](/Users/badripratti/Desktop/stock-screener/static/js/components/data-table.js:1)
- [empty-state.js](/Users/badripratti/Desktop/stock-screener/static/js/components/empty-state.js:1)
- [job-panel.js](/Users/badripratti/Desktop/stock-screener/static/js/components/job-panel.js:1)

The token set adds:

- Semantic aliases for base, raised, elevated, and inset surfaces.
- Subtle/default/strong borders and primary/secondary/disabled text.
- Semantic success, danger, warning, and accent colors.
- A 4px-based spacing scale covering existing dashboard measurements.
- Display, heading, body, caption, and monospace typography sizes.
- Small/medium/large control heights plus button/input aliases.
- Radius, shadow, and focus-ring scales.

Existing palette values remain the source of truth, and none of the new tokens are applied to existing rules yet, so the dashboard appearance is unchanged.

The builders escape ordinary text by default. The table supports arbitrary object/array shapes, accessors, renderers, comparators, initial sorting, sortable metadata, and `aria-sort`. The job panel preserves the existing `id-pill`, `id-run`, `id-output`, and `id-result` conventions.

Verification passed:

- All five ES modules passed `node --input-type=module --check`.
- Component smoke tests passed, including sorting and escaping.
- `git diff --check` passed.
- Existing `test_live_guard.js` passed.
- No changes detected in `dashboard.js`, `charts.js`, or `dashboard.html`.
- No emoji found in the task files.

Legacy-token grep comparison:

```sh
baseline_tokens=$(git show HEAD:static/css/dashboard.css \
  | sed -n '/^:root {/,/^}/p' \
  | rg -o -- '--[a-z0-9-]+:' | tr -d ':' | sort)

current_tokens=$(sed -n '/^:root {/,/^}/p' static/css/dashboard.css \
  | rg -o -- '--[a-z0-9-]+:' | tr -d ':' | sort)

comm -23 <(print -r -- "$baseline_tokens") \
         <(print -r -- "$current_tokens")
```

Result: empty—every original token remains. Current reference counts were also confirmed for all 11 legacy properties: `--bg`, `--surface`, `--surface-2`, `--border`, `--text`, `--muted`, `--green`, `--red`, `--yellow`, `--blue`, and `--purple`.
diff --git a/static/css/dashboard.css b/static/css/dashboard.css
index ca42eb40e52d922b64ebd8c69f1727e434bb25c7..56186fda63a0b24ee54d56994b37177d7c3650c1
--- a/static/css/dashboard.css
+++ b/static/css/dashboard.css
@@ -10,6 +10,59 @@
   --yellow: #eab308;
   --blue: #3b82f6;
   --purple: #a855f7;
+
+  --color-surface-base: var(--bg);
+  --color-surface-raised: var(--surface);
+  --color-surface-elevated: var(--surface-2);
+  --color-surface-inset: #0a0b10;
+  --color-border-subtle: rgba(255,255,255,0.06);
+  --color-border-default: var(--border);
+  --color-border-strong: #3a3e4d;
+  --color-text-primary: var(--text);
+  --color-text-secondary: var(--muted);
+  --color-text-disabled: rgba(139,143,163,0.5);
+  --color-success: var(--green);
+  --color-danger: var(--red);
+  --color-warning: var(--yellow);
+  --color-accent: var(--blue);
+  --color-accent-secondary: var(--purple);
+
+  --space-1: 4px;
+  --space-2: 8px;
+  --space-3: 12px;
+  --space-4: 16px;
+  --space-5: 20px;
+  --space-6: 24px;
+  --space-8: 32px;
+  --space-10: 40px;
+  --space-12: 48px;
+  --space-15: 60px;
+
+  --font-size-display: 28px;
+  --font-size-heading-lg: 19px;
+  --font-size-heading: 15px;
+  --font-size-body: 13px;
+  --font-size-body-sm: 12px;
+  --font-size-caption: 11px;
+  --font-size-mono: 11px;
+  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
+  --font-family-mono: 'SF Mono', Menlo, monospace;
+
+  --control-height-sm: 28px;
+  --control-height-md: 34px;
+  --control-height-lg: 40px;
+  --input-height: var(--control-height-sm);
+  --button-height: var(--control-height-md);
+
+  --radius-sm: 4px;
+  --radius-md: 6px;
+  --radius-lg: 8px;
+  --radius-xl: 10px;
+  --radius-2xl: 12px;
+  --radius-pill: 999px;
+  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
+  --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
+  --focus-ring: 0 0 0 3px rgba(59,130,246,0.3);
 }
 * { margin: 0; padding: 0; box-sizing: border-box; }
 body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
diff --git a/static/js/components/data-table.js b/static/js/components/data-table.js
new file mode 100644
index 0000000000000000000000000000000000000000..c276656613dd1ed39862bf3dab6d9faaeda81b86
--- /dev/null
+++ b/static/js/components/data-table.js
@@ -0,0 +1,90 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+function normalizeHeader(header, index) {
+  if (typeof header === 'string') {
+    return { key: header, label: header, sortable: true, index };
+  }
+
+  return {
+    ...header,
+    key: header.key ?? index,
+    label: header.label ?? header.key ?? '',
+    sortable: header.sortable !== false,
+    index,
+  };
+}
+
+function cellValue(row, header) {
+  if (typeof header.value === 'function') return header.value(row);
+  return row?.[header.key];
+}
+
+function compareValues(left, right) {
+  if (left == null && right == null) return 0;
+  if (left == null) return 1;
+  if (right == null) return -1;
+  if (typeof left === 'number' && typeof right === 'number') return left - right;
+  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: 'base' });
+}
+
+export function dataTableHTML({
+  headers = [],
+  rows = [],
+  id = '',
+  caption = '',
+  sortBy = null,
+  sortDirection = 'asc',
+  emptyMessage = 'No data yet',
+  rowClass = null,
+} = {}) {
+  const columns = headers.map(normalizeHeader);
+  const direction = sortDirection === 'desc' ? 'desc' : 'asc';
+  const sortColumn = columns.find(column => String(column.key) === String(sortBy) && column.sortable);
+  const sortedRows = [...rows];
+
+  if (sortColumn) {
+    const compare = typeof sortColumn.compare === 'function' ? sortColumn.compare : compareValues;
+    const multiplier = direction === 'desc' ? -1 : 1;
+    sortedRows.sort((left, right) => multiplier * compare(
+      cellValue(left, sortColumn),
+      cellValue(right, sortColumn),
+      left,
+      right,
+    ));
+  }
+
+  const tableId = id ? ` id="${escapeHtml(id)}"` : '';
+  const sortAttributes = sortColumn
+    ? ` data-sort-by="${escapeHtml(sortColumn.key)}" data-sort-direction="${direction}"`
+    : '';
+  const captionHTML = caption ? `<caption>${escapeHtml(caption)}</caption>` : '';
+  const headerHTML = columns.map(column => {
+    const sortableAttributes = column.sortable
+      ? ` data-key="${escapeHtml(column.key)}" data-sort-key="${escapeHtml(column.key)}"`
+      : '';
+    const ariaSort = sortColumn === column ? ` aria-sort="${direction === 'asc' ? 'ascending' : 'descending'}"` : '';
+    return `<th${sortableAttributes}${ariaSort}>${escapeHtml(column.label)}</th>`;
+  }).join('');
+  const rowsHTML = sortedRows.map((row, rowIndex) => {
+    const className = typeof rowClass === 'function' ? rowClass(row, rowIndex) : rowClass;
+    const classAttribute = className ? ` class="${escapeHtml(className)}"` : '';
+    const cells = columns.map(column => {
+      const value = cellValue(row, column);
+      const content = typeof column.render === 'function'
+        ? column.render(value, row, rowIndex)
+        : escapeHtml(value);
+      return `<td>${content ?? ''}</td>`;
+    }).join('');
+    return `<tr${classAttribute}>${cells}</tr>`;
+  }).join('');
+  const bodyHTML = rowsHTML || `<tr><td colspan="${Math.max(columns.length, 1)}">${escapeHtml(emptyMessage)}</td></tr>`;
+
+  return `<div style="overflow-x:auto"><table class="signal-table"${tableId}${sortAttributes}>${captionHTML}<thead><tr>${headerHTML}</tr></thead><tbody>${bodyHTML}</tbody></table></div>`;
+}
diff --git a/static/js/components/empty-state.js b/static/js/components/empty-state.js
new file mode 100644
index 0000000000000000000000000000000000000000..f03ebb27e9b2f54011582a97b9ee54732d4feb6a
--- /dev/null
+++ b/static/js/components/empty-state.js
@@ -0,0 +1,15 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+export function emptyStateHTML({ title = 'No data yet', message = '', actionHTML = '', id = '' } = {}) {
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+  const messageHTML = message ? `<p>${escapeHtml(message)}</p>` : '';
+
+  return `<div class="no-data"${idAttribute}><h2>${escapeHtml(title)}</h2>${messageHTML}${actionHTML}</div>`;
+}
diff --git a/static/js/components/job-panel.js b/static/js/components/job-panel.js
new file mode 100644
index 0000000000000000000000000000000000000000..583ab569571f82bc85da93856eb6bf36a999c20b
--- /dev/null
+++ b/static/js/components/job-panel.js
@@ -0,0 +1,37 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function jobPanelHTML({
+  id,
+  title,
+  description = '',
+  paramsHTML = '',
+  runLabel = 'Run',
+  status = 'idle',
+  statusLabel = null,
+  outputHTML = '',
+  resultHTML = '',
+} = {}) {
+  if (!id) throw new TypeError('jobPanelHTML requires an id');
+
+  const safeId = escapeHtml(id);
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+
+  return `
+    <div class="card sim-card">
+      <h2>${escapeHtml(title)} <span class="status-pill ${normalizedStatus}" id="${safeId}-pill">${escapeHtml(statusLabel ?? normalizedStatus)}</span></h2>
+      <div class="sim-desc">${escapeHtml(description)}</div>
+      <div class="sim-params">${paramsHTML}</div>
+      <button class="btn primary" id="${safeId}-run">${escapeHtml(runLabel)}</button>
+      <div class="job-output" id="${safeId}-output">${outputHTML}</div>
+      <div id="${safeId}-result" style="margin-top:12px">${resultHTML}</div>
+    </div>`;
+}
diff --git a/static/js/components/metric-card.js b/static/js/components/metric-card.js
new file mode 100644
index 0000000000000000000000000000000000000000..639cdf915641d1888a9c471240d613aee4f98965
--- /dev/null
+++ b/static/js/components/metric-card.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const variants = new Set(['green', 'red', 'blue', 'yellow', 'purple']);
+
+export function metricCardHTML({ label, value, subLabel = '', variant = '' } = {}) {
+  const variantClass = variants.has(variant) ? ` ${variant}` : '';
+  const sub = subLabel === '' ? '' : `<div class="sub">${escapeHtml(subLabel)}</div>`;
+
+  return `<div class="stat-card${variantClass}"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>${sub}</div>`;
+}
diff --git a/static/js/components/status-pill.js b/static/js/components/status-pill.js
new file mode 100644
index 0000000000000000000000000000000000000000..3b70f940cb4234908d9e54fc45928a9f66ffd8d5
--- /dev/null
+++ b/static/js/components/status-pill.js
@@ -0,0 +1,17 @@
+function escapeHtml(value) {
+  return String(value ?? '')
+    .replaceAll('&', '&amp;')
+    .replaceAll('<', '&lt;')
+    .replaceAll('>', '&gt;')
+    .replaceAll('"', '&quot;')
+    .replaceAll("'", '&#039;');
+}
+
+const statuses = new Set(['idle', 'running', 'success', 'error']);
+
+export function statusPillHTML({ status = 'idle', label = null, id = '' } = {}) {
+  const normalizedStatus = statuses.has(status) ? status : 'idle';
+  const idAttribute = id ? ` id="${escapeHtml(id)}"` : '';
+
+  return `<span class="status-pill ${normalizedStatus}"${idAttribute}>${escapeHtml(label ?? normalizedStatus)}</span>`;
+}

[2mtokens used[0m
62,725
Implemented TASK-002 as a purely additive foundation.

Changed files:

- [dashboard.css](/Users/badripratti/Desktop/stock-screener/static/css/dashboard.css:1) — 53 new token declarations.
- [metric-card.js](/Users/badripratti/Desktop/stock-screener/static/js/components/metric-card.js:1)
- [status-pill.js](/Users/badripratti/Desktop/stock-screener/static/js/components/status-pill.js:1)
- [data-table.js](/Users/badripratti/Desktop/stock-screener/static/js/components/data-table.js:1)
- [empty-state.js](/Users/badripratti/Desktop/stock-screener/static/js/components/empty-state.js:1)
- [job-panel.js](/Users/badripratti/Desktop/stock-screener/static/js/components/job-panel.js:1)

The token set adds:

- Semantic aliases for base, raised, elevated, and inset surfaces.
- Subtle/default/strong borders and primary/secondary/disabled text.
- Semantic success, danger, warning, and accent colors.
- A 4px-based spacing scale covering existing dashboard measurements.
- Display, heading, body, caption, and monospace typography sizes.
- Small/medium/large control heights plus button/input aliases.
- Radius, shadow, and focus-ring scales.

Existing palette values remain the source of truth, and none of the new tokens are applied to existing rules yet, so the dashboard appearance is unchanged.

The builders escape ordinary text by default. The table supports arbitrary object/array shapes, accessors, renderers, comparators, initial sorting, sortable metadata, and `aria-sort`. The job panel preserves the existing `id-pill`, `id-run`, `id-output`, and `id-result` conventions.

Verification passed:

- All five ES modules passed `node --input-type=module --check`.
- Component smoke tests passed, including sorting and escaping.
- `git diff --check` passed.
- Existing `test_live_guard.js` passed.
- No changes detected in `dashboard.js`, `charts.js`, or `dashboard.html`.
- No emoji found in the task files.

Legacy-token grep comparison:

```sh
baseline_tokens=$(git show HEAD:static/css/dashboard.css \
  | sed -n '/^:root {/,/^}/p' \
  | rg -o -- '--[a-z0-9-]+:' | tr -d ':' | sort)

current_tokens=$(sed -n '/^:root {/,/^}/p' static/css/dashboard.css \
  | rg -o -- '--[a-z0-9-]+:' | tr -d ':' | sort)

comm -23 <(print -r -- "$baseline_tokens") \
         <(print -r -- "$current_tokens")
```

Result: empty—every original token remains. Current reference counts were also confirmed for all 11 legacy properties: `--bg`, `--surface`, `--surface-2`, `--border`, `--text`, `--muted`, `--green`, `--red`, `--yellow`, `--blue`, and `--purple`.
