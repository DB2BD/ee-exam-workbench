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
  if (historicalNodeId && historicalNodeId !== node.nodeId) candidate.historicalNodeId = historicalNodeId;
  return candidate;
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

  const errorType = assessment.errorType;
  if (errorType === '計算錯') {
    return diagnosisUnknown('calculation-only', '目前只有計算錯證據，先重算流程，不直接宣稱概念弱點。', assessment, baseGraph, {
      confidence: 0.2,
      reason: '目前只有計算錯證據，先重算流程，不直接宣稱概念弱點。',
    });
  }
  if (errorType && !DIAGNOSIS_ERROR_TYPES.includes(errorType)) {
    return diagnosisUnknown('unsupported-error-type', '錯因類型未在 deterministic diagnosis 規則內。', assessment, baseGraph);
  }
  if (assessment.rating === 5 && !errorType) {
    return diagnosisUnknown('no-error-signal', '作答已獨立完成且沒有額外錯因，暫不提出概念弱點。', assessment, baseGraph, {
      status: 'clear', confidence: 1, needsConfirmation: false,
    });
  }

  const rawEdges = Array.isArray(baseGraph.edges) ? baseGraph.edges : [];
  const linkConfidence = typeof link.confidence === 'number' ? link.confidence : 0;
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
    recall: recall && typeof recall === 'object' ? { level: Number(recall.level) || 0, lastAchieved: Number(recall.lastAchieved) || 0 } : null,
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { KNOWLEDGE_DIAGNOSIS_VERSION, diagnose };
}
