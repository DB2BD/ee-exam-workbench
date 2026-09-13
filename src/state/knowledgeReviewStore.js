// Independent retrieval practice state for canonical knowledge nodes.
// Question Recall/SM-2 never reads or writes this store.

const PE_KNOWLEDGE_REVIEW_KEY = 'EE_KNOWLEDGE_REVIEWS_PE_V1';
const GK_KNOWLEDGE_REVIEW_KEY = 'GK_KNOWLEDGE_REVIEWS_GK_V1';
const KNOWLEDGE_REVIEW_SCHEMA = 'knowledge-reviews.v1';
const KNOWLEDGE_REVIEW_VERSION = 'knowledge-review.v1';
const KNOWLEDGE_REVIEW_RATINGS = [1, 3, 5];

function knowledgeReviewStorage(dependencies) {
  if (dependencies && dependencies.storage) return dependencies.storage;
  return typeof localStorage !== 'undefined' ? localStorage : null;
}

function knowledgeReviewKey(family) {
  return family === 'PE' ? PE_KNOWLEDGE_REVIEW_KEY : family === 'GK' ? GK_KNOWLEDGE_REVIEW_KEY : null;
}

function knowledgeReviewObject(value) {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

function knowledgeReviewFailure(code, message) {
  return { ok: false, duplicate: false, code, message, reviewId: null, state: null, event: null };
}

function knowledgeReviewGraph(dependencies) {
  if (dependencies && dependencies.graph && knowledgeReviewObject(dependencies.graph)) return dependencies.graph;
  if (typeof globalThis !== 'undefined' && knowledgeReviewObject(globalThis.CANONICAL_KNOWLEDGE_GRAPH)) return globalThis.CANONICAL_KNOWLEDGE_GRAPH;
  return null;
}

function knowledgeReviewNodeId(value) {
  return typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/.test(value) ? value : null;
}

function knowledgeReviewReadLog(family, dependencies) {
  const storage = knowledgeReviewStorage(dependencies);
  const key = knowledgeReviewKey(family);
  if (!storage || !key) return { ok: false, code: 'storage_unavailable', message: '無法讀取知識回想紀錄。', log: null };
  let raw;
  try { raw = storage.getItem(key); } catch (_) {
    return { ok: false, code: 'storage_read_failed', message: '無法讀取知識回想紀錄。', log: null };
  }
  if (!raw) return { ok: true, log: { schemaVersion: KNOWLEDGE_REVIEW_SCHEMA, examFamily: family, graphRevisions: [], reviews: {} } };
  let log;
  try { log = JSON.parse(raw); } catch (_) {
    return { ok: false, code: 'review_log_invalid', message: '知識回想紀錄格式損壞，未寫入。', log: null };
  }
  if (!knowledgeReviewObject(log) || log.schemaVersion !== KNOWLEDGE_REVIEW_SCHEMA || log.examFamily !== family
      || !Array.isArray(log.graphRevisions) || !knowledgeReviewObject(log.reviews)) {
    return { ok: false, code: 'review_log_invalid', message: '知識回想紀錄版本或格式無效，未寫入。', log: null };
  }
  return { ok: true, log };
}

function knowledgeReviewResolveNodeIds(nodeId, graph, trail = []) {
  const nodes = graph && knowledgeReviewObject(graph.nodes) ? graph.nodes : {};
  const node = nodes[nodeId];
  if (!knowledgeReviewObject(node) || !Array.isArray(node.successorNodeIds)
      || !['retired', 'merged'].includes(node.lifecycle) || node.successorNodeIds.length === 0 || trail.includes(nodeId)) return [nodeId];
  return [...new Set(node.successorNodeIds.flatMap(successor => knowledgeReviewResolveNodeIds(successor, graph, [...trail, nodeId])))];
}

function knowledgeReviewResolvedNode(nodeId, family, graph) {
  const nodes = graph && knowledgeReviewObject(graph.nodes) ? graph.nodes : {};
  const original = nodes[nodeId];
  if (!knowledgeReviewObject(original) || original.examFamily !== family) return { ok: false, code: 'family_mismatch', message: '知識節點不屬於目前考試類別或不存在。' };
  const resolved = knowledgeReviewResolveNodeIds(nodeId, graph);
  if (resolved.length !== 1) return { ok: false, code: 'lifecycle_split_requires_confirmation', message: '此知識節點已分拆，請先選擇要回想的後續節點。' };
  const target = nodes[resolved[0]];
  if (!knowledgeReviewObject(target) || target.examFamily !== family || target.lifecycle !== 'active') {
    return { ok: false, code: 'lifecycle_unavailable', message: '此知識節點目前沒有可用的後續節點。' };
  }
  return { ok: true, node: target, nodeId: resolved[0], migratedFrom: resolved[0] === nodeId ? null : nodeId };
}

function knowledgeReviewNow(dependencies) {
  const date = dependencies && dependencies.now !== undefined ? new Date(dependencies.now) : new Date();
  return Number.isNaN(date.getTime()) ? new Date() : date;
}

function knowledgeReviewDate(date) {
  return date.toISOString().slice(0, 10);
}

function calculateKnowledgeReviewItem(currentItem, rating, nowValue) {
  const now = nowValue instanceof Date ? new Date(nowValue.getTime()) : new Date(nowValue || Date.now());
  const item = currentItem || { repetitions: 0, interval: 0, easeFactor: 2.5 };
  let repetitions = Number(item.repetitions) || 0;
  let interval = Number(item.interval) || 0;
  let easeFactor = Number(item.easeFactor) || 2.5;
  if (rating < 3) {
    repetitions = 0; interval = 1; easeFactor = Math.max(1.3, easeFactor - 0.2);
  } else if (rating === 3) {
    if (repetitions === 0) interval = 1; else if (repetitions === 1) interval = 3; else interval = Math.max(1, Math.round(interval * 1.2));
    repetitions += 1; easeFactor = Math.max(1.3, easeFactor - 0.05);
  } else {
    if (repetitions === 0) interval = 1; else if (repetitions === 1) interval = 4; else interval = Math.max(1, Math.round(interval * easeFactor));
    repetitions += 1; easeFactor = Math.min(3.0, easeFactor + 0.1);
  }
  const next = new Date(now.getTime());
  next.setDate(next.getDate() + interval);
  return { repetitions, interval, easeFactor: Number(easeFactor.toFixed(2)), lastReviewed: knowledgeReviewDate(now), nextReviewDate: knowledgeReviewDate(next) };
}

function knowledgeReviewHash(value) {
  let hash = 2166136261;
  const text = String(value);
  for (let index = 0; index < text.length; index += 1) { hash ^= text.charCodeAt(index); hash = Math.imul(hash, 16777619); }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

function beginKnowledgeRecall(nodeId, examFamily, dependencies) {
  const graph = knowledgeReviewGraph(dependencies);
  if (!['PE', 'GK'].includes(examFamily) || !knowledgeReviewNodeId(nodeId)) return knowledgeReviewFailure('invalid_node', '知識節點識別無效。');
  const resolved = knowledgeReviewResolvedNode(nodeId, examFamily, graph);
  if (!resolved.ok) return knowledgeReviewFailure(resolved.code, resolved.message);
  const now = knowledgeReviewNow(dependencies);
  return {
    ok: true, duplicate: false, code: 'recall_started', message: '已開始知識回想；完成明確自評後才會排程。',
    reviewId: `knowledge:${examFamily}:${resolved.nodeId}`, nodeId: resolved.nodeId, examFamily,
    recallId: `recall-${knowledgeReviewHash(`${examFamily}:${resolved.nodeId}:${now.toISOString()}`)}`,
    scheduled: false,
  };
}

function readKnowledgeReview(nodeId, examFamily, dependencies) {
  const graph = knowledgeReviewGraph(dependencies);
  if (!['PE', 'GK'].includes(examFamily) || !knowledgeReviewNodeId(nodeId)) return null;
  const resolved = knowledgeReviewResolvedNode(nodeId, examFamily, graph);
  if (!resolved.ok) return null;
  const loaded = knowledgeReviewReadLog(examFamily, dependencies);
  if (!loaded.ok) return null;
  const reviewId = `knowledge:${examFamily}:${resolved.nodeId}`;
  const state = loaded.log.reviews[reviewId];
  return state ? Object.assign({}, state, { migratedFrom: resolved.migratedFrom }) : null;
}

function recordKnowledgeReview(input, dependencies) {
  const value = knowledgeReviewObject(input) ? input : {};
  const family = value.examFamily;
  if (!['PE', 'GK'].includes(family) || !knowledgeReviewNodeId(value.nodeId)) return knowledgeReviewFailure('invalid_node', '知識節點或考試類別無效。');
  if (!KNOWLEDGE_REVIEW_RATINGS.includes(Number(value.rating))) return knowledgeReviewFailure('invalid_rating', '知識回想評分必須是 1、3 或 5。');
  if (!(dependencies && dependencies.explicitRecall === true) && value.explicitRecall !== true) {
    return knowledgeReviewFailure('explicit_recall_required', '只有完成明確知識回想後才能建立排程。');
  }
  const graph = knowledgeReviewGraph(dependencies);
  const resolved = knowledgeReviewResolvedNode(value.nodeId, family, graph);
  if (!resolved.ok) return knowledgeReviewFailure(resolved.code, resolved.message);
  const loaded = knowledgeReviewReadLog(family, dependencies);
  if (!loaded.ok) return knowledgeReviewFailure(loaded.code, loaded.message);
  const log = loaded.log;
  const reviewId = `knowledge:${family}:${resolved.nodeId}`;
  const current = log.reviews[reviewId] || null;
  const now = knowledgeReviewNow(dependencies);
  const reviewEventId = knowledgeReviewNodeId(value.reviewEventId)
    || `review-event-${knowledgeReviewHash(`${reviewId}:${Number(value.rating)}:${Number(value.recallLevel) || 0}:${now.toISOString()}`)}`;
  const eventFingerprint = `${reviewId}:${reviewEventId}:${Number(value.rating)}:${Number(value.recallLevel) || 0}`;
  if (current && Array.isArray(current.history)) {
    const previous = current.history.find(event => event.reviewEventId === reviewEventId);
    if (previous) {
      if (previous.eventFingerprint === eventFingerprint) return { ok: true, duplicate: true, code: 'duplicate', message: '相同的知識回想評分已保存。', reviewId, state: current, event: previous };
      return knowledgeReviewFailure('review_event_conflict', '相同的回想事件識別對應不同評分，未寫入。');
    }
  }
  const nextItem = calculateKnowledgeReviewItem(current, Number(value.rating), now);
  const revision = graph && typeof graph.graphRevision === 'string' ? graph.graphRevision : null;
  const revisions = revision && !log.graphRevisions.includes(revision) ? [...log.graphRevisions, revision] : log.graphRevisions.slice();
  const event = {
    reviewEventId, eventFingerprint, reviewVersion: KNOWLEDGE_REVIEW_VERSION, reviewId,
    nodeId: resolved.nodeId, migratedFrom: resolved.migratedFrom, examFamily: family,
    rating: Number(value.rating), recallLevel: Number(value.recallLevel) || 0, explicitRecall: true,
    recordedAt: now.toISOString(), graphRevisionRef: revision === null ? null : revisions.indexOf(revision),
    previousNextReviewDate: current ? current.nextReviewDate : null, nextReviewDate: nextItem.nextReviewDate,
  };
  const state = Object.assign({
    reviewId, nodeId: resolved.nodeId, examFamily: family, reviewVersion: KNOWLEDGE_REVIEW_VERSION,
    history: [], graphRevisionRef: event.graphRevisionRef, migratedFrom: resolved.migratedFrom,
  }, current || {}, nextItem, { reviewId, nodeId: resolved.nodeId, examFamily: family, graphRevisionRef: event.graphRevisionRef, migratedFrom: resolved.migratedFrom, history: [...(current && current.history || []), event], updatedAt: now.toISOString() });
  const nextLog = { schemaVersion: KNOWLEDGE_REVIEW_SCHEMA, examFamily: family, graphRevisions: revisions, reviews: Object.assign({}, log.reviews, { [reviewId]: state }) };
  const maxBytes = Number.isInteger(dependencies && dependencies.maxBytes) ? dependencies.maxBytes : 3 * 1024 * 1024;
  let serialized;
  try { serialized = JSON.stringify(nextLog); } catch (_) { return knowledgeReviewFailure('serialization_failed', '知識回想紀錄無法序列化，未寫入。'); }
  if (serialized.length > maxBytes) return knowledgeReviewFailure('capacity_bytes', '知識回想紀錄已達容量上限，未寫入。');
  const storage = knowledgeReviewStorage(dependencies);
  try { storage.setItem(knowledgeReviewKey(family), serialized); } catch (_) { return knowledgeReviewFailure('storage_write_failed', '知識回想紀錄無法保存，未寫入。'); }
  return { ok: true, duplicate: false, code: 'ok', message: '知識回想評分已保存並排程。', reviewId, nodeId: resolved.nodeId, migratedFrom: resolved.migratedFrom, state, event };
}

function listDueKnowledgeReviews(examFamily, nowValue, dependencies) {
  const loaded = knowledgeReviewReadLog(examFamily, dependencies);
  if (!loaded.ok) return [];
  const today = knowledgeReviewDate(nowValue instanceof Date ? nowValue : new Date(nowValue || Date.now()));
  return Object.values(loaded.log.reviews).filter(state => state && state.nextReviewDate && state.nextReviewDate <= today).sort((left, right) => String(left.nextReviewDate).localeCompare(String(right.nextReviewDate)) || left.reviewId.localeCompare(right.reviewId));
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PE_KNOWLEDGE_REVIEW_KEY,
    GK_KNOWLEDGE_REVIEW_KEY,
    KNOWLEDGE_REVIEW_SCHEMA,
    calculateKnowledgeReviewItem,
    beginKnowledgeRecall,
    readKnowledgeReview,
    recordKnowledgeReview,
    listDueKnowledgeReviews,
  };
}
