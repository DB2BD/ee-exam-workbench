// Website projection for the append-only knowledge issue streams.

let weaknessViewRange = '7d';
let weaknessViewFamily = null;

function weaknessViewEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[character]));
}

function weaknessViewCurrentFamily() {
  const current = typeof currentExamCategory !== 'undefined' ? currentExamCategory : 'PE';
  return weaknessViewFamily && ['PE', 'GK'].includes(weaknessViewFamily) ? weaknessViewFamily : (['PE', 'GK'].includes(current) ? current : 'PE');
}

function setWeaknessRange(range) {
  weaknessViewRange = ['7d', '30d', 'all'].includes(range) ? range : '7d';
  renderWeaknessView();
}

function setWeaknessFamily(family) {
  weaknessViewFamily = ['PE', 'GK'].includes(family) ? family : null;
  renderWeaknessView();
}

function weaknessViewOpenQuestion(qid) {
  if (!qid) return false;
  const record = typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null;
  if (record && typeof openSolutionModal === 'function') {
    const question = typeof toQuestionRecord === 'function' ? toQuestionRecord(record) : null;
    openSolutionModal(null, question ? question.solutionLink : record[6], qid, question ? question.number : record[3], { mode: 'browse' });
    return true;
  }
  if (typeof window !== 'undefined' && window.location) window.location.hash = `q=${encodeURIComponent(qid)}`;
  return true;
}

function weaknessViewTraceHtml(node) {
  const trace = Array.isArray(node.supersessionChain) ? node.supersessionChain : [];
  const historical = trace.filter(item => !item.effective);
  if (!historical.length) return '';
  const rows = historical.map(item => `
    <li class="weakness-trace-row">
      <span><code>${weaknessViewEscape(item.eventId || '—')}</code> · ${weaknessViewEscape(item.eventType || '未分類')}</span>
      <span>${weaknessViewEscape(item.recordedAt || '—')} · ${weaknessViewEscape((item.nodeIds || []).join('、') || '未指定節點')}</span>
    </li>`).join('');
  const status = node.traceStatus === 'incomplete' ? ' · 部分事件無法追溯' : '';
  return `<details class="weakness-supersession-trace"><summary>歷史事件（${historical.length}）${status}</summary><ul>${rows}</ul></details>`;
}

function weaknessViewNodeCard(node) {
  const eventRows = (node.events || []).map(event => `
    <li class="weakness-event-row">
      <span><code>${weaknessViewEscape(event.eventId)}</code> · ${weaknessViewEscape(event.qid)}</span>
      <span>${weaknessViewEscape(event.recordedAt || '')} · ${weaknessViewEscape(event.errorType || '未分類')}</span>
      ${event.customText ? `<small>補充說明：${weaknessViewEscape(event.customText)}</small>` : ''}
      ${(event.evidence || []).length ? `<small>證據：${weaknessViewEscape(event.evidence.join('；'))}</small>` : '<small>證據：未提供</small>'}
      <button type="button" class="pill" onclick="weaknessViewOpenQuestion('${weaknessViewEscape(event.qid)}')">查看題目</button>
    </li>`).join('');
  return `<details class="weakness-node-card" open>
    <summary><strong>${weaknessViewEscape(node.title)}</strong> · ${node.role === 'secondary' ? '前置缺口' : '主要問題'} · ${node.rawCount} 次／${node.distinctQids} 題</summary>
    <p>最後出現：${weaknessViewEscape(node.lastSeen || '—')} · 確認率：${Math.round((Number(node.confirmationRate) || 0) * 100)}%</p>
    <p>診斷狀態：${weaknessViewEscape(node.reviewState || 'confirmed')}</p>
    <p>下一步：${weaknessViewEscape(node.nextAction && node.nextAction.label || '進入知識回想')}</p>
    ${node.historicalNodeIds && node.historicalNodeIds.length ? `<p>歷史節點：${weaknessViewEscape(node.historicalNodeIds.join('、'))}</p>` : ''}
    ${weaknessViewTraceHtml(node)}
    <ul>${eventRows || '<li>目前沒有可展開的事件。</li>'}</ul>
  </details>`;
}

function renderWeaknessView(options = {}) {
  const container = typeof document !== 'undefined' && typeof document.getElementById === 'function'
    ? document.getElementById('weakness-view') : null;
  if (!container) return null;
  const family = weaknessViewCurrentFamily();
  const range = ['7d', '30d', 'all'].includes(options.range) ? options.range : weaknessViewRange;
  weaknessViewRange = range;
  let log = { examFamily: family, events: [], graphRevisions: [] };
  if (typeof knowledgeIssueReadLog === 'function') {
    const loaded = knowledgeIssueReadLog(family);
    if (loaded && loaded.ok && loaded.log) log = loaded.log;
  }
  const graph = typeof CANONICAL_KNOWLEDGE_GRAPH !== 'undefined' ? CANONICAL_KNOWLEDGE_GRAPH : null;
  const now = options.now === undefined ? new Date().toISOString() : options.now;
  const projection = typeof buildWeaknessProjection === 'function'
    ? buildWeaknessProjection(log, { graph, examFamily: family, range, now })
    : { nodes: [], pendingClassification: { count: 0, events: [] }, totals: { effectiveEventCount: 0 } };
  const rangeLabels = { '7d': '近 7 天', '30d': '近 30 天', all: '全部時間' };
  const rangeButtons = Object.entries(rangeLabels).map(([key, label]) => `<button type="button" class="pill ${range === key ? 'active' : ''}" data-weakness-range="${key}" onclick="setWeaknessRange('${key}')">${label}</button>`).join('');
  const familyButtons = [['PE', '專技高考'], ['GK', '公務高考']].map(([key, label]) => `<button type="button" class="pill ${family === key ? 'active' : ''}" data-weakness-family="${key}" onclick="setWeaknessFamily('${key}')">${label}</button>`).join('');
  const nodes = (projection.nodes || []).map(weaknessViewNodeCard).join('');
  const pending = projection.pendingClassification || { count: 0, events: [] };
  const pendingRows = (pending.events || []).map(event => `<li class="weakness-event-row"><span><code>${weaknessViewEscape(event.eventId)}</code> · ${weaknessViewEscape(event.qid)}</span><span>${weaknessViewEscape(event.eventType || '待分類')} · ${weaknessViewEscape(event.recordedAt || '')}</span>${event.customText ? `<small>補充說明：${weaknessViewEscape(event.customText)}</small>` : ''}${(event.evidence || []).length ? `<small>證據：${weaknessViewEscape(event.evidence.join('；'))}</small>` : ''}<button type="button" class="pill" onclick="weaknessViewOpenQuestion('${weaknessViewEscape(event.qid)}')">查看題目</button></li>`).join('');
  container.innerHTML = `<section class="weakness-shell">
    <div class="weakness-header"><div><h2>🧭 我的弱點</h2><p>由 issue event stream 重算；每個節點都能展開回看 QID、事件與證據。</p></div><div class="weakness-toolbar" aria-label="弱點篩選">${familyButtons}${rangeButtons}</div></div>
    <p class="weakness-summary">${weaknessViewEscape(family)} · ${weaknessViewEscape(rangeLabels[range])} · 有效事件 ${Number(projection.totals && projection.totals.effectiveEventCount) || 0} 筆 · 待分類 ${Number(pending.count) || 0} 筆</p>
    <div class="weakness-node-list">${nodes || '<p class="weakness-empty">目前沒有符合範圍的已確認問題點。</p>'}</div>
    <details class="weakness-pending-card" ${pending.count ? 'open' : ''}><summary>待分類事件（${Number(pending.count) || 0}）</summary><ul>${pendingRows || '<li>目前沒有待分類事件。</li>'}</ul></details>
  </section>`;
  return projection;
}
