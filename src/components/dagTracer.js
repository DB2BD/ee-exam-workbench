// src/components/dagTracer.js
/**
 * Knowledge DAG Weakness Tracer Component.
 * Analyzes question prerequisites and renders actionable weakness tracing cards.
 */

function renderDagTracerCard(qid, sid, topic) {
  if (typeof KNOWLEDGE_DAG === 'undefined' || typeof mapQuestionToDagNodes !== 'function') {
    return '';
  }

  const matchedNodeIds = mapQuestionToDagNodes(sid, topic, '');
  if (!matchedNodeIds || matchedNodeIds.length === 0) return '';

  const targetNodeId = matchedNodeIds[0];
  const targetNode = KNOWLEDGE_DAG[targetNodeId];
  if (!targetNode) return '';

  const prereqChain = tracePrerequisiteChain(targetNodeId);
  if (!prereqChain || prereqChain.length === 0) return '';

  return `
    <div class="dag-tracer-card">
      <div class="dag-tracer-header">
        <div class="dag-tracer-title">
          <span>🕸️ 觀念相依 DAG 溯源與前置盲點補強</span>
          <span class="dag-tracer-badge">Level ${targetNode.level} 核心考點</span>
        </div>
        <span style="font-size: 0.8rem; color: var(--muted); font-weight: 600;">若本題卡關，建議依循下方拓撲鏈逆向複習：</span>
      </div>

      <div class="dag-chain-flow">
        ${prereqChain.map((node, idx) => {
          const isTarget = node.id === targetNodeId;
          const arrow = idx < prereqChain.length - 1 ? '<span class="dag-arrow">➔</span>' : '';
          return `
            <div class="dag-node-chip ${isTarget ? 'target' : 'prereq'}" title="核心公式：${node.coreFormula}">
              <span>${isTarget ? '🎯' : '📚'} ${node.name}</span>
              <span style="font-size: 0.72rem; opacity: 0.8;">L${node.level}</span>
            </div>
            ${arrow}
          `;
        }).join('')}
      </div>

      ${targetNode.keyTrap ? `
        <div class="dag-trap-alert">
          <strong>⚠️ 考場易錯陷阱提點：</strong> ${targetNode.keyTrap}
        </div>
      ` : ''}
    </div>
  `;
}
