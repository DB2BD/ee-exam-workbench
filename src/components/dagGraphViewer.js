// src/components/dagGraphViewer.js
/**
 * Standalone Knowledge DAG Graph Viewer Component.
 * Visualizes the full prerequisite graph for all 6 subjects.
 */

let currentDagSubjectFilter = 'all';
let currentKnowledgeRecall = null;

function knowledgeRecallEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[character]));
}

function startKnowledgeNodeRecall(nodeId) {
  const graph = typeof CANONICAL_KNOWLEDGE_GRAPH !== 'undefined' ? CANONICAL_KNOWLEDGE_GRAPH : null;
  const node = graph && graph.nodes ? graph.nodes[nodeId] : null;
  if (!node || typeof beginKnowledgeRecall !== 'function') {
    if (typeof showToast === 'function') showToast('此節點目前沒有可用的知識回想資料。');
    return false;
  }
  const started = beginKnowledgeRecall(nodeId, node.examFamily);
  if (!started || !started.ok) {
    if (typeof showToast === 'function') showToast(started && started.message || '知識回想無法開始。');
    return false;
  }
  currentKnowledgeRecall = started;
  renderDagGraphVisualizer();
  return true;
}

function submitKnowledgeRecallRating(rating) {
  if (!currentKnowledgeRecall || typeof recordKnowledgeReview !== 'function') return false;
  const saved = recordKnowledgeReview({
    nodeId: currentKnowledgeRecall.nodeId,
    examFamily: currentKnowledgeRecall.examFamily,
    rating,
    reviewEventId: currentKnowledgeRecall.recallId,
    recallLevel: 1,
    explicitRecall: true,
  }, { explicitRecall: true });
  if (!saved || !saved.ok) {
    if (typeof showToast === 'function') showToast(saved && saved.message || '知識回想評分未保存。');
    return false;
  }
  currentKnowledgeRecall = null;
  if (typeof showToast === 'function') showToast('知識回想已記錄，並建立獨立的節點複習排程。');
  renderDagGraphVisualizer();
  return true;
}

function renderKnowledgeRecallPanel() {
  if (!currentKnowledgeRecall) return '';
  return `<section class="knowledge-recall-card">
    <h3>🧠 知識節點回想：${knowledgeRecallEscape(currentKnowledgeRecall.nodeId)}</h3>
    <p>先遮住筆記，回想這個問題點的核心定義、適用條件與一個反例，再選擇回想程度。閱讀或查看節點不會自動排程。</p>
    <div class="knowledge-recall-actions">
      <button type="button" class="pill" onclick="submitKnowledgeRecallRating(1)">忘記</button>
      <button type="button" class="pill" onclick="submitKnowledgeRecallRating(3)">需要提示</button>
      <button type="button" class="pill" onclick="submitKnowledgeRecallRating(5)">能獨立回想</button>
    </div>
  </section>`;
}

function renderCanonicalKnowledgeRecallCatalog() {
  const graph = typeof CANONICAL_KNOWLEDGE_GRAPH !== 'undefined' ? CANONICAL_KNOWLEDGE_GRAPH : null;
  if (!graph || !graph.nodes) return '';
  const currentFamily = typeof currentExamCategory !== 'undefined' && ['PE', 'GK'].includes(currentExamCategory) ? currentExamCategory : null;
  const nodes = Object.values(graph.nodes).filter(node => node.lifecycle === 'active'
    && node.nodeType !== 'question' && (!currentFamily || node.examFamily === currentFamily));
  const due = typeof listDueKnowledgeReviews === 'function' && currentFamily
    ? listDueKnowledgeReviews(currentFamily, new Date()).length : 0;
  return `<section class="knowledge-recall-catalog">
    <div class="knowledge-recall-catalog-head"><div><h3>知識節點回想</h3><p>目前圖譜 revision：${knowledgeRecallEscape(graph.graphRevision || '—')} · ${currentFamily || '目前考科'} 待回想：${due}</p></div></div>
    <div class="knowledge-recall-grid">${nodes.map(node => `<article class="knowledge-recall-tile"><strong>${knowledgeRecallEscape(node.title || node.nodeId)}</strong><small>${knowledgeRecallEscape(node.examFamily)} · ${knowledgeRecallEscape(node.nodeId)}</small><button type="button" class="pill" onclick="startKnowledgeNodeRecall('${knowledgeRecallEscape(node.nodeId)}')">開始回想</button></article>`).join('')}</div>
  </section>`;
}

function setDagSubjectFilter(sid) {
  currentDagSubjectFilter = sid;
  renderDagGraphVisualizer();
}

function renderDagGraphVisualizer() {
  const container = document.getElementById('dag-graph-viewer-content');
  if (!container || typeof KNOWLEDGE_DAG === 'undefined') return;

  const graph = typeof CANONICAL_KNOWLEDGE_GRAPH !== 'undefined' ? CANONICAL_KNOWLEDGE_GRAPH : null;
  const family = typeof currentExamCategory !== 'undefined' && ['PE', 'GK'].includes(currentExamCategory)
    ? currentExamCategory : 'PE';
  const nodes = (graph && graph.nodes
    ? Object.values(graph.nodes).filter(n => n.examFamily === family && n.nodeType !== 'question')
    : Object.values(KNOWLEDGE_DAG)).filter(n => {
    if (currentDagSubjectFilter === 'all') return true;
    return n.subject === currentDagSubjectFilter;
  });

  container.innerHTML = `
    <div class="dag-vis-header">
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button class="pill ${currentDagSubjectFilter === 'all' ? 'active' : ''}" onclick="setDagSubjectFilter('all')">全部考科 (${nodes.length} 節點)</button>
        <button class="pill ${currentDagSubjectFilter === '01' ? 'active' : ''}" onclick="setDagSubjectFilter('01')">⚡ 01. 電路學</button>
        <button class="pill ${currentDagSubjectFilter === '02' ? 'active' : ''}" onclick="setDagSubjectFilter('02')">🔌 02. 電子學</button>
        <button class="pill ${currentDagSubjectFilter === '03' ? 'active' : ''}" onclick="setDagSubjectFilter('03')">📐 03. 工程數學</button>
        <button class="pill ${currentDagSubjectFilter === '04' ? 'active' : ''}" onclick="setDagSubjectFilter('04')">⚙️ 04. 電機機械</button>
        <button class="pill ${currentDagSubjectFilter === '05' ? 'active' : ''}" onclick="setDagSubjectFilter('05')">🏢 05. 電力系統</button>
        <button class="pill ${currentDagSubjectFilter === '06' ? 'active' : ''}" onclick="setDagSubjectFilter('06')">🏭 06. 工業配電</button>
      </div>
      <span style="font-size: 0.84rem; color: var(--muted); font-weight: 600;">共 ${nodes.length} 個知識拓撲節點</span>
    </div>

    ${renderKnowledgeRecallPanel()}
    ${renderCanonicalKnowledgeRecallCatalog()}

    <div class="dag-vis-grid">
      ${nodes.map(n => {
        const prereqNames = (n.prereqs || []).map(pid => {
          const canonical = graph && graph.nodes ? graph.nodes[pid] : null;
          const legacy = KNOWLEDGE_DAG[pid];
          return canonical ? canonical.title : legacy ? legacy.name : pid;
        });
        const nodeTitle = n.title || n.name;
        const nodeFormula = n.coreFormula || '';
        const nodeSubject = n.subjectName || (n.examFamily === 'GK' ? '國考同級題庫' : '電機工程技師');
        return `
          <div class="dag-vis-card">
            <div class="dag-vis-card-head">
              <span class="dag-vis-card-title">${nodeTitle}</span>
              <span class="dag-vis-card-level">⭐ Level ${n.level || 0}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--accent-dark); font-weight: 600; margin-bottom: 4px;">
              考別：${n.examFamily} · 考科：${nodeSubject}
            </div>
            <div class="dag-vis-card-formula">
              <code>${nodeFormula ? `$${nodeFormula}$` : '先回想定義、適用條件與一個反例'}</code>
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
