import { jobPanelHTML } from '../components/job-panel.js';
import { wireJobCard } from '../core/jobs.js';
import { content, currentView } from '../core/state.js';

export function renderScanView() {
  if (currentView !== 'scan') return;
  content.innerHTML = `<div style="max-width:520px">${jobPanelHTML({
    id: 'scan',
    title: 'Run a Scan',
    description: 'Test scan covers ~100 stocks (~1 min). Full scan covers the ~3,800-stock universe (15-30 min).',
    paramsHTML: `
      <label style="flex:0 0 100%;flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-full" style="width:auto"> Full scan (unchecked = quick test scan)</label>
      <label style="flex:0 0 100%;flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="scan-agents" style="width:auto"> Enable AI agents (Fundamentals/Catalyst/Congress → Top 5 shortlist, needs ANTHROPIC_API_KEY)</label>
    `,
  })}</div>`;

  wireJobCard('scan', 'scan', () => ({
    full: document.getElementById('scan-full').checked,
    enable_llm_agents: document.getElementById('scan-agents').checked,
  }), async (st, resultEl) => {
    resultEl.innerHTML = '<a href="#/market" class="btn primary">View Market →</a> <a href="#/shortlist" class="btn">View Shortlist →</a>';
  });
}
