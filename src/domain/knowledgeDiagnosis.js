// -*- coding: utf-8 -*-
// Deterministic, bounded knowledge diagnosis.  This module is deliberately
// pure: it never reads localStorage and it never writes a diagnosis event.

const KNOWLEDGE_DIAGNOSIS_VERSION = 'knowledge-diagnosis.v1';
const DIAGNOSIS_ERROR_TYPES = ['題型辨識錯', '起手式不會', '公式忘記', '計算錯', '觀念混淆'];
const DIAGNOSIS_CONFIDENCE_FLOOR = 0.8;

function diagnosisGraphValue(graph) {
  if (graph && typeof graph === 'object') return graph;
  if (typeof globalThis !== 'undefined' && globalThis.CANONICAL_KNOWLEDGE_GRAPH) return globalThis.CANONICAL_KNOWLEDGE_GRAPH;
  return null;
}

function diagnosisNodes(graph) {
  if (!graph || !graph.nodes) return {};
  if (Array.isArray(graph.nodes)) return Object.fromEntries(graph.nodes.map(node => [node.nodeId, node]));
  return graph.nodes;
}

function diagnosisQuestion(question) {
  if (Array.isArray(question)) {
    const qid = question[0];
    return { id: qid, qid, examFamily: String(qid || '').startsWith('GK-') ? 'GK' : 'PE' };
  }
  const value = question && typeof question === 'object' ? question : {};
  const qid = value.id || value.qid;
  return Object.assign({}, value, { id: qid, qid, examFamily: value.examFamily || (String(qid || '').startsWith('GK-') ? 'GK' : 'PE') });
}

function diagnosisAssessment(assessment) {
  const value = assessment && typeof assessment === 'object' ? assessment : {};
  const result = value.result && typeof value.result === 'object' ? value.result : value;
  return {
    attemptId: value.attemptId || value.sessionId || (value.attempt && (value.attempt.attemptId || value.attempt.sessionId)) || null,
    status: value.attemptStatus || value.status || (value.attempt && value.attempt.status) || null,
    rating: Number(result.rating ?? value.rating),
    errorType: result.errorType || value.errorType || null,
    graphRevision: value.graphRevision || value.graphRevisionRef || result.graphRevision
      || (value.attempt && (value.attempt.graphRevision || value.attempt.graphRevisionRef)) || null,
  };
}

function diagnosisUnknown(reasonCode, reason, assessment, graph, extra = {}) {
  return Object.assign({
    diagnosisVersion: KNOWLEDGE_DIAGNOSIS_VERSION,
    attemptId: assessment.attemptId,
    graphRevision: graph && graph.graphRevision ? graph.graphRevision : assessment.graphRevision,
    status: 'unknown',
    likelyQuestions: [],
    firstPrerequisiteGap: null,
    reason,
    reasonCode,
    confidence: 0,
    needsConfirmation: true,
  }, extra);
}

function diagnosisSuccessors(nodeId, nodes, trail = []) {
  const node = nodes[nodeId];
  if (!node || !['retired', 'merged'].includes(node.lifecycle) || !Array.isArray(node.successorNodeIds) || node.successorNodeIds.length === 0) return [nodeId];
  if (trail.includes(nodeId)) return [nodeId];
  return [...new Set(node.successorNodeIds.flatMap(id => diagnosisSuccessors(id, nodes, [...trail, nodeId])))];
}

function diagnosisCandidate(node, why, confidence, evidence, rank, historicalNodeId = null) {
  const candidate = {
    nodeId: node.nodeId,
    title: node.title,
    nodeType: node.nodeType,
    examFamily: node.examFamily,
    why,
    confidence: Math.max(0, Math.min(1, Number(confidence) || 0)),
    evidence: Array.isArray(evidence) ? [...evidence] : [],
    rank,
  };
  // These fields turn a graph match into something the learner can act on.
  // The diagnosis still only uses approved graph evidence; it never invents
  // a new concept from the learner's self-report.
  if (node.coreFormula) candidate.coreFormula = node.coreFormula;
  if (node.keyTrap) candidate.keyTrap = node.keyTrap;
  if (node.level !== undefined) candidate.level = Number(node.level) || 0;
  if (node.subjectName) candidate.subjectName = node.subjectName;
  if (historicalNodeId && historicalNodeId !== node.nodeId) candidate.historicalNodeId = historicalNodeId;
  return candidate;
}

function diagnosisActionPlan(errorType, candidate, prerequisite, assessment) {
  const type = errorType || '未指定錯因';
  const title = candidate && candidate.title ? candidate.title : '本題的解題流程';
  const targetNodeId = candidate && candidate.nodeId ? candidate.nodeId : null;
  const plans = {
    '題型辨識錯': {
      title: '先學會辨識這類題目',
      steps: ['遮住詳解，先寫「題目要我求什麼」與「已知哪些量」。', '再寫出你選用的模型，以及它的適用條件。', '用同一模型重做本題的第一行。'],
    },
    '起手式不會': {
      title: '先補第一個解題動作',
      steps: ['先列已知量、未知量、要求量。', '寫出第一個方程式、等效電路或邊界條件。', '只做前兩步後再回頭核對詳解。'],
    },
    '公式忘記': {
      title: '先回想公式與使用條件',
      steps: ['先不看詳解，寫出公式與每個符號的單位。', '說明公式何時可以用、何時不能用。', '用題目數值代入一次並檢查量綱。'],
    },
    '計算錯': {
      title: '先排除計算誤差',
      steps: ['重新抄一次代入式，不直接重看最後答案。', '逐項檢查單位、正負號、角度／弧度與有效位數。', '把中間結果代回原方程式確認。'],
    },
    '觀念混淆': {
      title: '先分清楚兩個容易混淆的概念',
      steps: ['寫出你混淆的兩個概念各自代表什麼。', '各寫一個適用條件或反例。', '用本題條件說明為什麼應選其中一個。'],
    },
  };
  const selected = plans[type] || {
    title: '把卡住的步驟留下來',
    steps: ['寫下你做到的最後一步。', '標記下一步需要哪個公式、條件或模型。', '保存後在待分類事件中補回這筆紀錄。'],
  };
  return {
    title: selected.title,
    targetNodeId,
    targetTitle: title,
    errorType: type,
    steps: selected.steps,
    coreFormula: candidate && candidate.coreFormula ? candidate.coreFormula : null,
    keyTrap: candidate && candidate.keyTrap ? candidate.keyTrap : null,
    prerequisite: prerequisite && prerequisite.title ? prerequisite.title : null,
    reviewPrompt: targetNodeId
      ? `完成這三步後，回想「${title}」一次，再用另一題確認。`
      : '保存你的最後一步，下一次才能把診斷變成可追蹤的複習任務。',
    rating: Number(assessment && assessment.rating) || null,
  };
}

function diagnosisRouteScore(node, errorType) {
  const preferred = {
    '題型辨識錯': ['procedure', 'mainline', 'mechanism', 'question'],
    '起手式不會': ['procedure', 'mainline', 'mechanism', 'question'],
    '公式忘記': ['mechanism', 'procedure', 'mainline', 'question'],
    '觀念混淆': ['mechanism', 'procedure', 'mainline', 'question'],
  }[errorType] || ['procedure', 'mechanism', 'mainline', 'question'];
  const index = preferred.indexOf(node.nodeType);
  return index < 0 ? preferred.length : index;
}

function diagnose(question, assessmentInput, graphInput, recall) {
  const questionValue = diagnosisQuestion(question);
  const assessment = diagnosisAssessment(assessmentInput);
  const graph = diagnosisGraphValue(graphInput);
  const baseGraph = graph && typeof graph === 'object' ? graph : null;
  if (!assessment.attemptId || !['committed', 'acknowledged'].includes(assessment.status)) {
    return diagnosisUnknown('attempt-not-committed', '作答尚未完成 durable commit，暫不建立診斷。', assessment, baseGraph, { status: 'blocked' });
  }
  if (!baseGraph || !baseGraph.graphRevision) return diagnosisUnknown('graph-unavailable', '目前沒有可驗證的 knowledge graph revision。', assessment, baseGraph);
  if (assessment.graphRevision && assessment.graphRevision !== baseGraph.graphRevision) {
    return diagnosisUnknown('graph-revision-mismatch', '作答引用的 graph revision 與目前版本不同，需重新檢查。', assessment, baseGraph);
  }
  if (![1, 3, 5].includes(assessment.rating)) {
    return diagnosisUnknown('invalid-assessment', '自評結果無效，暫不建立診斷。', assessment, baseGraph);
  }
  const qid = questionValue.qid;
  const family = questionValue.examFamily;
  if (!qid || !['PE', 'GK'].includes(family)) return diagnosisUnknown('invalid-question', '題目 QID 或考試類別無效。', assessment, baseGraph);
  const qidFamily = String(qid).startsWith('GK-') ? 'GK' : String(qid).startsWith('EE-') ? 'PE' : null;
  if (qidFamily && qidFamily !== family) return diagnosisUnknown('cross-family-question', '題目 QID 與考試類別不一致。', assessment, baseGraph);

  const nodes = diagnosisNodes(baseGraph);
  const links = baseGraph.questionLinks || baseGraph.links || {};
  const link = links[`${family}:${qid}`];
  if (!link || link.reviewStatus !== 'approved' || !Array.isArray(link.nodeIds)) {
    return diagnosisUnknown('no-approved-question-link', '目前沒有足夠證據把這題連到 canonical knowledge node。', assessment, baseGraph);
  }
  if (link.examFamily !== family) return diagnosisUnknown('cross-family-link', '題目連結的 exam family 不一致，已拒絕跨考別診斷。', assessment, baseGraph);
  const linked = [];
  for (const originalId of link.nodeIds) {
    const original = nodes[originalId];
    if (!original || original.examFamily !== family) return diagnosisUnknown('cross-family-link', '題目連結包含不同 exam family 的 node，已拒絕診斷。', assessment, baseGraph);
    for (const resolvedId of diagnosisSuccessors(originalId, nodes)) {
      const node = nodes[resolvedId];
      if (node && node.examFamily === family && !linked.some(item => item.node.nodeId === resolvedId)) {
        linked.push({ node, historicalNodeId: originalId });
      }
    }
  }
  if (linked.length === 0) return diagnosisUnknown('no-supported-node', '題目連結沒有可供目前 viewer 使用的 node。', assessment, baseGraph);

  const linkConfidence = typeof link.confidence === 'number' ? link.confidence : 0;
  const errorType = assessment.errorType;
  if (errorType === '計算錯') {
    const calculationTarget = linked[0]
      ? diagnosisCandidate(linked[0].node, '本題的 approved question link 提供計算核對入口。', linkConfidence, link.evidence, 1, linked[0].historicalNodeId)
      : null;
    return diagnosisUnknown('calculation-only', '目前只有計算錯證據，先重算流程，不直接宣稱概念弱點。', assessment, baseGraph, {
      confidence: 0.2,
      reason: '目前只有計算錯證據，先重算流程，不直接宣稱概念弱點。',
      actionPlan: diagnosisActionPlan('計算錯', calculationTarget, null, assessment),
    });
  }
  if (errorType && !DIAGNOSIS_ERROR_TYPES.includes(errorType)) {
    return diagnosisUnknown('unsupported-error-type', '錯因類型未在 deterministic diagnosis 規則內。', assessment, baseGraph);
  }
  if (assessment.rating === 5 && !errorType) {
    const mastered = linked[0]
      ? diagnosisCandidate(linked[0].node, '本題已完成獨立作答，保留作為日後回想入口。', linkConfidence, link.evidence, 1, linked[0].historicalNodeId)
      : null;
    return diagnosisUnknown('no-error-signal', '作答已獨立完成且沒有額外錯因，暫不提出概念弱點。', assessment, baseGraph, {
      status: 'clear', confidence: 1, needsConfirmation: false,
      actionPlan: diagnosisActionPlan(null, mastered, null, assessment),
    });
  }

  const rawEdges = Array.isArray(baseGraph.edges) ? baseGraph.edges : [];
  const candidates = linked
    .sort((left, right) => (
      diagnosisRouteScore(left.node, errorType) - diagnosisRouteScore(right.node, errorType)
      || right.node.nodeId.localeCompare(left.node.nodeId)
    ))
    .slice(0, 3)
    .map((item, index) => diagnosisCandidate(
      item.node,
      errorType === '公式忘記' ? '此題的證據指向公式或核心機制。'
        : errorType === '起手式不會' ? '此題的證據指向解題流程的第一個判斷。'
          : errorType === '題型辨識錯' ? '此題的證據指向題型與適用條件判斷。'
            : errorType === '觀念混淆' ? '此題的證據指向概念邊界與反例辨識。'
              : '此題的 approved question link 提供可追溯的候選。',
      Math.max(0, linkConfidence - index * 0.03),
      link.evidence,
      index + 1,
      item.historicalNodeId,
    ));

  let firstPrerequisiteGap = null;
  for (const candidate of candidates) {
    const prerequisite = rawEdges
      .filter(edge => edge.reviewStatus === 'approved' && edge.relation === 'prerequisite' && edge.to === candidate.nodeId)
      .sort((left, right) => String(left.from).localeCompare(String(right.from)))[0];
    if (!prerequisite || !nodes[prerequisite.from] || nodes[prerequisite.from].examFamily !== family) continue;
    firstPrerequisiteGap = diagnosisCandidate(
      nodes[prerequisite.from],
      prerequisite.why,
      Math.min(candidate.confidence, Number(prerequisite.confidence) || 0),
      prerequisite.evidence,
      1,
    );
    break;
  }
  const needsConfirmation = true;
  const primaryCandidate = candidates[0] || null;
  const actionPlan = diagnosisActionPlan(errorType, primaryCandidate, firstPrerequisiteGap, assessment);
  return {
    diagnosisVersion: KNOWLEDGE_DIAGNOSIS_VERSION,
    attemptId: assessment.attemptId,
    graphRevision: baseGraph.graphRevision,
    status: 'mapped',
    likelyQuestions: candidates,
    firstPrerequisiteGap,
    reason: errorType ? `依據「${errorType}」與題目連結提出候選，請確認最符合的問題點。` : '依據題目連結提出候選，請確認最符合的問題點。',
    reasonCode: 'evidence-backed-candidates',
    confidence: Math.max(0, Math.min(1, linkConfidence)),
    needsConfirmation,
    lowConfidence: linkConfidence < DIAGNOSIS_CONFIDENCE_FLOOR,
    actionPlan,
    recall: recall && typeof recall === 'object' ? { level: Number(recall.level) || 0, lastAchieved: Number(recall.lastAchieved) || 0 } : null,
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { KNOWLEDGE_DIAGNOSIS_VERSION, diagnose };
}
