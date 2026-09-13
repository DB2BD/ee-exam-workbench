// Append-only learner issue events, separated by exam family.
// The log is a durable evidence layer: a diagnosis is never silently
// overwritten, and every correction points back to the decision it replaces.

const PE_KNOWLEDGE_ISSUE_KEY = 'EE_KNOWLEDGE_ISSUES_PE_V1';
const GK_KNOWLEDGE_ISSUE_KEY = 'GK_KNOWLEDGE_ISSUES_GK_V1';
const KNOWLEDGE_ISSUE_SCHEMA = 'knowledge-issue-events.v1';
const KNOWLEDGE_ISSUE_ATTEMPT_KEY = 'EE_EXAM_ATTEMPT_ENVELOPES_V1';
const KNOWLEDGE_ISSUE_EVENT_TYPES = ['confirm', 'correct', 'none-of-above', 'skip', 'unknown'];
const KNOWLEDGE_ISSUE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/;
const KNOWLEDGE_ISSUE_REVISION_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/;
const KNOWLEDGE_ISSUE_DEFAULT_MAX_EVENTS = 5000;
const KNOWLEDGE_ISSUE_DEFAULT_MAX_BYTES = 3 * 1024 * 1024;

function knowledgeIssueFailure(code, message) {
  return { ok: false, duplicate: false, code, message, event: null, eventCount: null, payloadBytes: null };
}

function knowledgeIssueStorage(dependencies) {
  if (dependencies && dependencies.storage) return dependencies.storage;
  return typeof localStorage !== 'undefined' ? localStorage : null;
}

function knowledgeIssueStorageKey(examFamily) {
  return examFamily === 'PE' ? PE_KNOWLEDGE_ISSUE_KEY : examFamily === 'GK' ? GK_KNOWLEDGE_ISSUE_KEY : null;
}

function knowledgeIssueQidFamily(qid) {
  if (typeof qid !== 'string') return null;
  if (qid.startsWith('EE-')) return 'PE';
  if (qid.startsWith('GK-')) return 'GK';
  return null;
}

function knowledgeIssueGraph(dependencies) {
  if (dependencies && dependencies.graph && typeof dependencies.graph === 'object') return dependencies.graph;
  if (typeof globalThis !== 'undefined' && globalThis.CANONICAL_KNOWLEDGE_GRAPH) return globalThis.CANONICAL_KNOWLEDGE_GRAPH;
  return null;
}

function knowledgeIssueOwnObject(value) {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

function knowledgeIssueUtf8Bytes(value) {
  const text = String(value);
  try {
    return encodeURIComponent(text).replace(/%[0-9A-F]{2}|./g, 'x').length;
  } catch (_) {
    return text.length * 4;
  }
}

function knowledgeIssueCleanText(value, maxLength) {
  if (value === null || value === undefined) return '';
  const text = String(value).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').trim();
  return text.length <= maxLength ? text : text.slice(0, maxLength);
}

function knowledgeIssueReadLog(examFamily, dependencies) {
  const storage = knowledgeIssueStorage(dependencies);
  const key = knowledgeIssueStorageKey(examFamily);
  if (!storage || !key) return { ok: false, code: 'storage_unavailable', message: '無法保存問題事件。', log: null };
  let raw;
  try { raw = storage.getItem(key); } catch (_) {
    return { ok: false, code: 'storage_read_failed', message: '無法讀取問題事件，未寫入。', log: null };
  }
  if (!raw) return { ok: true, log: { schemaVersion: KNOWLEDGE_ISSUE_SCHEMA, examFamily, graphRevisions: [], events: [] } };
  let log;
  try { log = JSON.parse(raw); } catch (_) {
    return { ok: false, code: 'log_invalid', message: '問題事件紀錄格式損壞，未寫入。', log: null };
  }
  if (!knowledgeIssueOwnObject(log) || log.schemaVersion !== KNOWLEDGE_ISSUE_SCHEMA
      || log.examFamily !== examFamily || !Array.isArray(log.graphRevisions) || !Array.isArray(log.events)) {
    return { ok: false, code: 'log_invalid', message: '問題事件紀錄版本或格式無效，未寫入。', log: null };
  }
  if (log.graphRevisions.some(revision => typeof revision !== 'string' || !KNOWLEDGE_ISSUE_REVISION_PATTERN.test(revision))) {
    return { ok: false, code: 'log_invalid', message: '問題事件紀錄的 graph revision 無效，未寫入。', log: null };
  }
  if (log.events.some(event => !knowledgeIssueOwnObject(event) || event.examFamily !== examFamily
      || typeof event.eventId !== 'string' || !KNOWLEDGE_ISSUE_ID_PATTERN.test(event.eventId))) {
    return { ok: false, code: 'log_invalid', message: '問題事件紀錄包含無效事件，未寫入。', log: null };
  }
  return { ok: true, log };
}

function knowledgeIssueReadAttempt(attemptId, event, dependencies) {
  if (dependencies && dependencies.attemptStatus) {
    const supplied = typeof dependencies.attemptStatus === 'object'
      ? dependencies.attemptStatus : { status: dependencies.attemptStatus };
    return { ok: true, envelope: supplied };
  }
  const storage = knowledgeIssueStorage(dependencies);
  if (!storage) return { ok: false, code: 'storage_unavailable', message: '無法驗證作答提交狀態。', envelope: null };
  let raw;
  try { raw = storage.getItem(KNOWLEDGE_ISSUE_ATTEMPT_KEY); } catch (_) {
    return { ok: false, code: 'attempt_store_read_failed', message: '無法讀取作答提交狀態，未寫入。', envelope: null };
  }
  if (!raw) return { ok: false, code: 'attempt_not_committed', message: '作答尚未完成提交，暫不保存問題事件。', envelope: null };
  let store;
  try { store = JSON.parse(raw); } catch (_) {
    return { ok: false, code: 'attempt_store_invalid', message: '作答提交紀錄格式損壞，未寫入。', envelope: null };
  }
  const envelope = store && store.schemaVersion === 'learning-attempts.v1' && store.attempts
    ? store.attempts[attemptId] : null;
  if (!knowledgeIssueOwnObject(envelope) || !['committed', 'acknowledged'].includes(envelope.status)) {
    return { ok: false, code: 'attempt_not_committed', message: '作答尚未完成提交，暫不保存問題事件。', envelope: null };
  }
  return { ok: true, envelope };
}

function knowledgeIssueNode(graph, nodeId, family) {
  if (!nodeId) return null;
  const nodes = graph && knowledgeIssueOwnObject(graph.nodes) ? graph.nodes : {};
  const node = nodes[nodeId];
  if (!knowledgeIssueOwnObject(node) || node.examFamily !== family) return null;
  return node;
}

function knowledgeIssueValidateEvent(input, graph, family) {
  const value = knowledgeIssueOwnObject(input) ? input : {};
  if (value.examFamily !== family) return { ok: false, code: 'family_mismatch', message: '問題事件的考試類別不一致。' };
  if (typeof value.attemptId !== 'string' || !KNOWLEDGE_ISSUE_ID_PATTERN.test(value.attemptId)) {
    return { ok: false, code: 'invalid_event', message: '問題事件缺少有效的 attempt ID。' };
  }
  if (typeof value.qid !== 'string' || value.qid.length > 200) {
    return { ok: false, code: 'invalid_event', message: '問題事件缺少有效的 QID。' };
  }
  const qidFamily = knowledgeIssueQidFamily(value.qid);
  if (qidFamily !== family) return { ok: false, code: 'family_mismatch', message: 'QID 與考試類別不一致。' };
  if (!KNOWLEDGE_ISSUE_EVENT_TYPES.includes(value.eventType)) {
    return { ok: false, code: 'invalid_event', message: '問題事件類型無效。' };
  }
  if (![1, 3, 5].includes(Number(value.rating))) {
    return { ok: false, code: 'invalid_event', message: '自評結果無效。' };
  }
  const candidateCount = Number(value.candidateCount ?? 0);
  if (!Number.isInteger(candidateCount) || candidateCount < 0 || candidateCount > 3) {
    return { ok: false, code: 'invalid_event', message: '診斷候選數量無效。' };
  }
  const confidence = Number(value.diagnosisConfidence ?? 0);
  if (!Number.isFinite(confidence) || confidence < 0 || confidence > 1) {
    return { ok: false, code: 'invalid_event', message: '診斷信心值無效。' };
  }
  const rank = value.selectedCandidateRank === null || value.selectedCandidateRank === undefined
    ? null : Number(value.selectedCandidateRank);
  if (rank !== null && (!Number.isInteger(rank) || rank < 1 || rank > candidateCount)) {
    return { ok: false, code: 'invalid_event', message: '選取候選排名無效。' };
  }
  const primary = value.primaryKnowledgeNodeId || null;
  const secondary = Array.isArray(value.secondaryKnowledgeNodeIds) ? value.secondaryKnowledgeNodeIds : [];
  const systemTop = value.systemTopNodeId || null;
  if (['confirm', 'correct'].includes(value.eventType) && !primary) {
    return { ok: false, code: 'invalid_event', message: '確認或修正事件必須指定主要問題點。' };
  }
  if (['none-of-above', 'skip', 'unknown'].includes(value.eventType) && primary) {
    return { ok: false, code: 'invalid_event', message: '此事件類型不可指定主要問題點。' };
  }
  const ids = [primary, systemTop, ...secondary].filter(Boolean);
  if (ids.some(id => typeof id !== 'string' || !KNOWLEDGE_ISSUE_ID_PATTERN.test(id))) {
    return { ok: false, code: 'invalid_event', message: '問題 node ID 無效。' };
  }
  if (primary && !knowledgeIssueNode(graph, primary, family)) {
    return { ok: false, code: 'family_mismatch', message: '主要問題點不屬於目前考試類別或不存在。' };
  }
  if (systemTop && !knowledgeIssueNode(graph, systemTop, family)) {
    return { ok: false, code: 'family_mismatch', message: '系統主節點不屬於目前考試類別或不存在。' };
  }
  if (secondary.some(id => !knowledgeIssueNode(graph, id, family))) {
    return { ok: false, code: 'family_mismatch', message: '前置問題點不屬於目前考試類別或不存在。' };
  }
  const revision = value.graphRevisionRef || (graph && graph.graphRevision) || null;
  if (revision !== null && (typeof revision !== 'string' || !KNOWLEDGE_ISSUE_REVISION_PATTERN.test(revision))) {
    return { ok: false, code: 'invalid_event', message: 'graph revision 無效。' };
  }
  return {
    ok: true,
    value: {
      attemptId: value.attemptId,
      qid: value.qid,
      examFamily: family,
      rating: Number(value.rating),
      errorType: knowledgeIssueCleanText(value.errorType, 100) || null,
      eventType: value.eventType,
      primaryKnowledgeNodeId: primary,
      secondaryKnowledgeNodeIds: [...new Set(secondary)].slice(0, 3),
      systemTopNodeId: systemTop,
      candidateCount,
      selectedCandidateRank: rank,
      diagnosisConfidence: confidence,
      evidence: Array.isArray(value.evidence)
        ? value.evidence.filter(item => typeof item === 'string').map(item => knowledgeIssueCleanText(item, 200)).filter(Boolean).slice(0, 10)
        : [],
      customText: knowledgeIssueCleanText(value.customText, 500) || null,
      sourceMode: knowledgeIssueCleanText(value.sourceMode, 40) || null,
      diagnosisVersion: knowledgeIssueCleanText(value.diagnosisVersion, 100) || 'knowledge-diagnosis.v1',
      graphRevisionRef: revision,
      recordedAt: typeof value.recordedAt === 'string' && value.recordedAt.length <= 80 ? value.recordedAt : new Date().toISOString(),
    },
  };
}

function knowledgeIssueStableSerialize(value) {
  if (Array.isArray(value)) return `[${value.map(knowledgeIssueStableSerialize).join(',')}]`;
  if (knowledgeIssueOwnObject(value)) return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${knowledgeIssueStableSerialize(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}

function knowledgeIssueHash(value) {
  let hash = 2166136261;
  const text = String(value);
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

function knowledgeIssueDecisionFingerprint(event) {
  const decision = Object.assign({}, event);
  delete decision.recordedAt;
  delete decision.eventId;
  delete decision.supersedesEventId;
  return knowledgeIssueHash(knowledgeIssueStableSerialize(decision));
}

function knowledgeIssueEffectiveEvent(events, attemptId) {
  const related = events.filter(event => event.attemptId === attemptId);
  if (!related.length) return null;
  const superseded = new Set(related.map(event => event.supersedesEventId).filter(Boolean));
  return [...related].reverse().find(event => !superseded.has(event.eventId)) || related[related.length - 1];
}

function appendKnowledgeIssueEvent(input, dependencies) {
  const value = knowledgeIssueOwnObject(input) ? input : {};
  const family = value.examFamily;
  if (!['PE', 'GK'].includes(family)) return knowledgeIssueFailure('family_mismatch', '問題事件缺少有效的考試類別。');
  const qidFamily = knowledgeIssueQidFamily(value.qid);
  if (qidFamily !== family) return knowledgeIssueFailure('family_mismatch', 'QID 與考試類別不一致。');
  const graph = knowledgeIssueGraph(dependencies);
  if (!graph || typeof graph.graphRevision !== 'string') return knowledgeIssueFailure('graph_unavailable', '目前沒有可驗證的 knowledge graph revision。');
  const validated = knowledgeIssueValidateEvent(value, graph, family);
  if (!validated.ok) return knowledgeIssueFailure(validated.code, validated.message);
  const loaded = knowledgeIssueReadLog(family, dependencies);
  if (!loaded.ok) return knowledgeIssueFailure(loaded.code, loaded.message);
  const log = loaded.log;
  const normalized = validated.value;
  const fingerprint = knowledgeIssueDecisionFingerprint(normalized);
  const current = knowledgeIssueEffectiveEvent(log.events, normalized.attemptId);
  if (current && current.decisionFingerprint === fingerprint) {
    return { ok: true, duplicate: true, code: 'duplicate', message: '相同的問題決定已保存。', event: current, eventCount: log.events.length, payloadBytes: knowledgeIssueUtf8Bytes(JSON.stringify(log)) };
  }
  const maxEvents = Number.isInteger(dependencies && dependencies.maxEvents) ? dependencies.maxEvents : KNOWLEDGE_ISSUE_DEFAULT_MAX_EVENTS;
  const maxBytes = Number.isInteger(dependencies && dependencies.maxBytes) ? dependencies.maxBytes : KNOWLEDGE_ISSUE_DEFAULT_MAX_BYTES;
  if (log.events.length >= maxEvents) return knowledgeIssueFailure('capacity_events', '問題事件數量已達上限，未寫入。');
  const attempt = knowledgeIssueReadAttempt(normalized.attemptId, normalized, dependencies);
  if (!attempt.ok) return knowledgeIssueFailure(attempt.code, attempt.message);
  if (attempt.envelope.qid !== normalized.qid || attempt.envelope.examFamily !== family) {
    return knowledgeIssueFailure('family_mismatch', '問題事件與已提交作答的 QID 或考試類別不一致。');
  }
  const revisionIndex = normalized.graphRevisionRef === null ? null : log.graphRevisions.indexOf(normalized.graphRevisionRef);
  const revisions = revisionIndex >= 0 ? log.graphRevisions.slice() : normalized.graphRevisionRef === null
    ? log.graphRevisions.slice() : [...log.graphRevisions, normalized.graphRevisionRef];
  const nextRevisionIndex = normalized.graphRevisionRef === null ? null : revisions.indexOf(normalized.graphRevisionRef);
  const occurrence = log.events.filter(event => event.attemptId === normalized.attemptId).length;
  const event = Object.assign({}, normalized, {
    eventId: `issue-${knowledgeIssueHash(`${fingerprint}:${occurrence}`)}`,
    decisionFingerprint: fingerprint,
    graphRevisionRef: nextRevisionIndex,
    supersedesEventId: current ? current.eventId : null,
  });
  const nextLog = { schemaVersion: KNOWLEDGE_ISSUE_SCHEMA, examFamily: family, graphRevisions: revisions, events: [...log.events, event] };
  const payloadBytes = knowledgeIssueUtf8Bytes(JSON.stringify(nextLog));
  if (nextLog.events.length > maxEvents) return knowledgeIssueFailure('capacity_events', '問題事件數量已達上限，未寫入。');
  if (payloadBytes > maxBytes) return knowledgeIssueFailure('capacity_bytes', '問題事件容量已達上限，未寫入。');
  const storage = knowledgeIssueStorage(dependencies);
  try { storage.setItem(knowledgeIssueStorageKey(family), JSON.stringify(nextLog)); }
  catch (_) { return knowledgeIssueFailure('storage_write_failed', '問題事件無法保存，未變更原紀錄。'); }
  return { ok: true, duplicate: false, code: 'ok', message: '問題事件已保存。', event, eventCount: nextLog.events.length, payloadBytes };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PE_KNOWLEDGE_ISSUE_KEY,
    GK_KNOWLEDGE_ISSUE_KEY,
    KNOWLEDGE_ISSUE_SCHEMA,
    appendKnowledgeIssueEvent,
    knowledgeIssueReadLog,
    knowledgeIssueValidateEvent,
  };
}
