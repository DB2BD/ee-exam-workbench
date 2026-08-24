// src/components/dagGraphViewer.js
/**
 * Standalone Knowledge DAG Graph Viewer Component.
 * Visualizes the full prerequisite graph for all 6 subjects.
 */

let currentDagSubjectFilter = 'all';

function setDagSubjectFilter(sid) {
  currentDagSubjectFilter = sid;
  renderDagGraphVisualizer();
}

function renderDagGraphVisualizer() {
  const container = document.getElementById('dag-graph-viewer-content');
  if (!container || typeof KNOWLEDGE_DAG === 'undefined') return;

  const nodes = Object.values(KNOWLEDGE_DAG).filter(n => {
    if (currentDagSubjectFilter === 'all') return true;
    return n.subject === currentDagSubjectFilter;
  });

  container.innerHTML = `
    <div class="dag-vis-header">
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button class="pill ${currentDagSubjectFilter === 'all' ? 'active' : ''}" onclick="setDagSubjectFilter('all')">全部考科 (60+ 節點)</button>
        <button class="pill ${currentDagSubjectFilter === '01' ? 'active' : ''}" onclick="setDagSubjectFilter('01')">⚡ 01. 電路學</button>
        <button class="pill ${currentDagSubjectFilter === '02' ? 'active' : ''}" onclick="setDagSubjectFilter('02')">🔌 02. 電子學</button>
        <button class="pill ${currentDagSubjectFilter === '03' ? 'active' : ''}" onclick="setDagSubjectFilter('03')">📐 03. 工程數學</button>
        <button class="pill ${currentDagSubjectFilter === '04' ? 'active' : ''}" onclick="setDagSubjectFilter('04')">⚙️ 04. 電機機械</button>
        <button class="pill ${currentDagSubjectFilter === '05' ? 'active' : ''}" onclick="setDagSubjectFilter('05')">🏢 05. 電力系統</button>
        <button class="pill ${currentDagSubjectFilter === '06' ? 'active' : ''}" onclick="setDagSubjectFilter('06')">🏭 06. 工業配電</button>
      </div>
      <span style="font-size: 0.84rem; color: var(--muted); font-weight: 600;">共 ${nodes.length} 個知識拓撲節點</span>
    </div>

    <div class="dag-vis-grid">
      ${nodes.map(n => {
        const prereqNames = n.prereqs.map(pid => KNOWLEDGE_DAG[pid] ? KNOWLEDGE_DAG[pid].name : pid);
        return `
          <div class="dag-vis-card">
            <div class="dag-vis-card-head">
              <span class="dag-vis-card-title">${n.name}</span>
              <span class="dag-vis-card-level">⭐ Level ${n.level}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--accent-dark); font-weight: 600; margin-bottom: 4px;">
              考科：${n.subjectName}
            </div>
            <div class="dag-vis-card-formula">
              <code>$${n.coreFormula}$</code>
            </div>
            ${prereqNames.length > 0 ? `
              <div class="dag-vis-card-prereqs">
                <span>前置必備：</span>
                ${prereqNames.map(pn => `<span class="dag-prereq-tag">⬅️ ${pn}</span>`).join('')}
              </div>
            ` : '<div style="font-size: 0.76rem; color: var(--success); margin-top: 6px;">🌱 基礎起始概念 (無前置相依)</div>'}
          </div>
        `;
      }).join('')}
    </div>
  `;

  // Apply math rendering if auto-render is available
  if (typeof renderMathInElement !== 'undefined') {
    renderMathInElement(container, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false}
      ],
      throwOnError: false
    });
  }
}
