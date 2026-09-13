// Pure projection of append-only knowledge issue events.
// It deliberately returns explainable evidence instead of maintaining a
// mutable counter, so importing or replaying the same stream is safe.

const WEAKNESS_PROJECTION_VERSION = 'weakness-projection.v1';
const WEAKNESS_PRIORITY_VERSION = 'weakness-priority.v1';
const WEAKNESS_RANGES = { '7d': 7, '30d': 30, all: null };
const WEAKNESS_PENDING_TYPES = ['none-of-above', 'skip', 'unknown'];
const WEAKNESS_DAY_MS = 24 * 60 * 60 * 1000;

function weaknessObject(value) {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

function weaknessStreamValue(stream) {
  if (Array.isArray(stream)) return { examFamily: null, events: stream, graphRevisions: [] };
  if (!weaknessObject(stream)) return { examFamily: null, events: [], graphRevisions: [] };
  return {
    examFamily: stream.examFamily || null,
    events: Array.isArray(stream.events) ? stream.events : [],
    graphRevisions: Array.isArray(stream.graphRevisions) ? stream.graphRevisions : [],
  };
}

function weaknessGraph(options) {
  if (options && weaknessObject(options.graph)) return options.graph;
  if (typeof globalThis !== 'undefined' && weaknessObject(globalThis.CANONICAL_KNOWLEDGE_GRAPH)) return globalThis.CANONICAL_KNOWLEDGE_GRAPH;
  return { graphRevision: null, nodes: {} };
}

function weaknessEventTime(event) {
  const parsed = Date.parse(event && event.recordedAt);
  return Number.isFinite(parsed) ? parsed : null;
}

function weaknessReferenceTime(events, options) {
  if (options && options.now !== undefined) {
    const provided = Date.parse(options.now);
    if (Number.isFinite(provided)) return { timeMs: provided, mode: 'explicit' };
    return { timeMs: null, mode: 'invalid-explicit' };
  }
  return {
    timeMs: events.reduce((latest, event) => Math.max(latest, weaknessEventTime(event) || 0), 0),
    mode: 'latest-event-replay',
  };
}

function weaknessResolvedNodeIds(nodeId, nodes, trail = []) {
  const node = nodes[nodeId];
  if (!node || !['retired', 'merged'].includes(node.lifecycle)
      || !Array.isArray(node.successorNodeIds) || node.successorNodeIds.length === 0
      || trail.includes(nodeId)) return [nodeId];
  const resolved = node.successorNodeIds.flatMap(successor => weaknessResolvedNodeIds(successor, nodes, [...trail, nodeId]));
  return [...new Set(resolved)];
}

function weaknessNodeInfo(nodeId, family, graph) {
  const nodes = graph && weaknessObject(graph.nodes) ? graph.nodes : {};
  const node = nodes[nodeId];
  if (!weaknessObject(node) || (family && node.examFamily !== family)) {
    return { nodeId, title: nodeId, nodeType: 'unknown', examFamily: family || null, lifecycle: 'unknown' };
  }
  return {
    nodeId,
    title: node.title || node.name || nodeId,
    nodeType: node.nodeType || 'unknown',
    examFamily: node.examFamily || family || null,
    lifecycle: node.lifecycle || 'active',
  };
}

function weaknessEventSummary(event, role, nodeId = null, historicalNodeId = null) {
  return {
    eventId: event.eventId || null,
    attemptId: event.attemptId || null,
    qid: event.qid || null,
    eventType: event.eventType || null,
    role,
    nodeId,
    historicalNodeId,
    rating: Number(event.rating) || null,
    errorType: event.errorType || null,
    recordedAt: event.recordedAt || null,
    graphRevisionRef: event.graphRevisionRef === undefined ? null : event.graphRevisionRef,
    diagnosisConfidence: Number(event.diagnosisConfidence) || 0,
    sourceMode: event.sourceMode || null,
    customText: typeof event.customText === 'string' ? event.customText : null,
    evidence: Array.isArray(event.evidence) ? event.evidence.slice(0, 10) : [],
  };
}

function weaknessEventNodeIds(event) {
  return [...new Set([
    event && event.primaryKnowledgeNodeId,
    ...(event && Array.isArray(event.secondaryKnowledgeNodeIds) ? event.secondaryKnowledgeNodeIds : []),
  ].filter(id => typeof id === 'string' && id))];
}

function weaknessSupersessionTrace(event, eventById) {
  const chain = [];
  const missingEventIds = [];
  const seen = new Set(event && event.eventId ? [event.eventId] : []);
  let previousId = event && event.supersedesEventId ? event.supersedesEventId : null;
  while (previousId) {
    if (seen.has(previousId)) {
      missingEventIds.push(previousId);
      break;
    }
    const previous = eventById.get(previousId);
    if (!previous) {
      missingEventIds.push(previousId);
      break;
    }
    seen.add(previousId);
    chain.push({
      eventId: previous.eventId || null,
      supersedesEventId: previous.supersedesEventId || null,
      eventType: previous.eventType || null,
      recordedAt: previous.recordedAt || null,
      nodeIds: weaknessEventNodeIds(previous),
      effective: false,
    });
    previousId = previous.supersedesEventId || null;
  }
  chain.reverse();
  chain.push({
    eventId: event && event.eventId ? event.eventId : null,
    supersedesEventId: event && event.supersedesEventId ? event.supersedesEventId : null,
    eventType: event && event.eventType ? event.eventType : null,
    recordedAt: event && event.recordedAt ? event.recordedAt : null,
    nodeIds: weaknessEventNodeIds(event),
    effective: true,
  });
  return {
    chain,
    missingEventIds,
    traceStatus: missingEventIds.length ? 'incomplete' : 'complete',
  };
}

function weaknessEffectiveEvents(events) {
  const superseded = new Set(events.map(event => event && event.supersedesEventId).filter(Boolean));
  return events.filter(event => weaknessObject(event) && !superseded.has(event.eventId));
}

function weaknessAggregate(info, role) {
  return Object.assign(info, {
    role,
    rawCount: 0,
    distinctQids: 0,
    lastSeen: null,
    ratings: { '1': 0, '3': 0, '5': 0 },
    errorTypes: {},
    sourceModes: {},
    confirmationRate: 0,
    acceptanceMetrics: {
      totalCount: 0,
      confirmedCount: 0,
      correctedCount: 0,
      pendingCount: 0,
      acceptedRate: 0,
    },
    reviewState: role === 'secondary' ? 'secondary-confirmed' : 'confirmed',
    priority: { score: 0, components: {} },
    priorityVersion: WEAKNESS_PRIORITY_VERSION,
    ratingSeverityTotal: 0,
    historicalNodeIds: [],
    events: [],
    supersessionChain: [],
    traceStatus: 'complete',
    missingEventIds: [],
    nextAction: role === 'primary'
      ? { type: 'review-knowledge', nodeId: info.nodeId, label: '進入知識回想' }
      : { type: 'review-prerequisite', nodeId: info.nodeId, label: '先補前置問題' },
  });
}

function weaknessSaturation(value, scale) {
  const number = Math.max(0, Number(value) || 0);
  return number / (number + scale);
}

function weaknessPriority(aggregate, referenceMs) {
  const lastSeenMs = weaknessEventTime({ recordedAt: aggregate.lastSeen });
  const recency = lastSeenMs === null || !referenceMs
    ? 0
    : Math.max(0, Math.min(1, 1 - Math.max(0, referenceMs - lastSeenMs) / (30 * WEAKNESS_DAY_MS)));
  const frequency = weaknessSaturation(aggregate.rawCount, 3);
  const breadth = weaknessSaturation(aggregate.distinctQids, 3);
  const severity = aggregate.rawCount ? aggregate.ratingSeverityTotal / aggregate.rawCount : 0;
  const acceptance = aggregate.acceptanceMetrics.totalCount
    ? aggregate.acceptanceMetrics.confirmedCount / aggregate.acceptanceMetrics.totalCount : 0;
  const score = 0.35 * frequency + 0.25 * breadth + 0.2 * recency + 0.15 * severity + 0.05 * acceptance;
  return {
    score: Number(score.toFixed(6)),
    components: {
      frequency: Number(frequency.toFixed(6)),
      breadth: Number(breadth.toFixed(6)),
      recency: Number(recency.toFixed(6)),
      severity: Number(severity.toFixed(6)),
      acceptance: Number(acceptance.toFixed(6)),
    },
  };
}

function buildWeaknessProjection(stream, options = {}) {
  const value = weaknessStreamValue(stream);
  const graph = weaknessGraph(options);
  const requestedFamily = options.examFamily || value.examFamily || null;
  const family = ['PE', 'GK'].includes(requestedFamily) ? requestedFamily : null;
  const requestedRange = WEAKNESS_RANGES[options.range] === undefined ? '30d' : options.range;
  const rangeDays = WEAKNESS_RANGES[requestedRange];
  const reference = weaknessReferenceTime(value.events, options);
  const referenceMs = reference.timeMs;
  const cutoff = rangeDays === null ? null : referenceMs - rangeDays * 24 * 60 * 60 * 1000;
  const excludedEvents = [];
  const candidates = weaknessEffectiveEvents(value.events)
    .filter(event => !family || event.examFamily === family)
    .filter(event => {
      const time = weaknessEventTime(event);
      let reason = null;
      if (referenceMs === null) reason = 'INVALID_TIME_ANCHOR';
      else if (time === null) reason = 'INVALID_RECORDED_AT';
      else if (time > referenceMs) reason = 'FUTURE_THAN_TIME_ANCHOR';
      else if (cutoff !== null && time < cutoff) reason = 'BEFORE_TIME_CUTOFF';
      if (reason) {
        excludedEvents.push({ eventId: event.eventId || null, recordedAt: event.recordedAt || null, reason });
        return false;
      }
      return true;
    })
    .sort((left, right) => (weaknessEventTime(left) || 0) - (weaknessEventTime(right) || 0)
      || String(left.eventId || '').localeCompare(String(right.eventId || '')));
  const nodes = graph && weaknessObject(graph.nodes) ? graph.nodes : {};
  const eventById = new Map(value.events.filter(weaknessObject).map(event => [event.eventId, event]));
  const priorNodeIds = event => {
    const ids = [];
    let previous = event && event.supersedesEventId ? eventById.get(event.supersedesEventId) : null;
    const seen = new Set();
    while (previous && !seen.has(previous.eventId)) {
      seen.add(previous.eventId);
      if (previous.primaryKnowledgeNodeId) ids.push(previous.primaryKnowledgeNodeId);
      if (Array.isArray(previous.secondaryKnowledgeNodeIds)) ids.push(...previous.secondaryKnowledgeNodeIds);
      previous = previous.supersedesEventId ? eventById.get(previous.supersedesEventId) : null;
    }
    return [...new Set(ids)];
  };
  const aggregates = new Map();
  const pending = [];
  const pendingTypes = new Set(WEAKNESS_PENDING_TYPES);
  candidates.forEach(event => {
    const eventFamily = family || event.examFamily || null;
    const primary = typeof event.primaryKnowledgeNodeId === 'string' && event.primaryKnowledgeNodeId
      ? event.primaryKnowledgeNodeId : null;
    const secondary = Array.isArray(event.secondaryKnowledgeNodeIds)
      ? [...new Set(event.secondaryKnowledgeNodeIds.filter(id => typeof id === 'string' && id))] : [];
    if (pendingTypes.has(event.eventType) || !primary) {
      pending.push(weaknessEventSummary(event, 'pending'));
      return;
    }
    const addNodeEvent = (historicalNodeId, role) => {
      weaknessResolvedNodeIds(historicalNodeId, nodes).forEach(nodeId => {
        const key = `${role}:${nodeId}`;
        if (!aggregates.has(key)) aggregates.set(key, weaknessAggregate(weaknessNodeInfo(nodeId, eventFamily, graph), role));
        const aggregate = aggregates.get(key);
        aggregate.rawCount += 1;
        aggregate.lastSeen = event.recordedAt || aggregate.lastSeen;
        const historicalIds = [historicalNodeId, ...priorNodeIds(event)];
        historicalIds.forEach(id => {
          if (id && id !== nodeId && !aggregate.historicalNodeIds.includes(id)) aggregate.historicalNodeIds.push(id);
        });
        const qid = event.qid || null;
        if (qid && !aggregate.events.some(item => item.qid === qid)) aggregate.distinctQids += 1;
        const rating = String(Number(event.rating));
        if (Object.prototype.hasOwnProperty.call(aggregate.ratings, rating)) aggregate.ratings[rating] += 1;
        aggregate.ratingSeverityTotal += Number(event.rating) === 1 ? 1 : Number(event.rating) === 3 ? 0.5 : 0;
        if (event.errorType) aggregate.errorTypes[event.errorType] = (aggregate.errorTypes[event.errorType] || 0) + 1;
        if (event.sourceMode) aggregate.sourceModes[event.sourceMode] = (aggregate.sourceModes[event.sourceMode] || 0) + 1;
        aggregate.acceptanceMetrics.totalCount += 1;
        if (event.eventType === 'confirm') aggregate.acceptanceMetrics.confirmedCount += 1;
        else if (event.eventType === 'correct') aggregate.acceptanceMetrics.correctedCount += 1;
        else aggregate.acceptanceMetrics.pendingCount += 1;
        aggregate.acceptanceMetrics.acceptedRate = aggregate.acceptanceMetrics.totalCount
          ? (aggregate.acceptanceMetrics.confirmedCount + aggregate.acceptanceMetrics.correctedCount) / aggregate.acceptanceMetrics.totalCount : 0;
        aggregate.reviewState = event.eventType === 'correct' ? 'corrected' : role === 'secondary' ? 'secondary-confirmed' : 'confirmed';
        aggregate.events.push(weaknessEventSummary(event, role, nodeId, historicalNodeId === nodeId ? null : historicalNodeId));
        const trace = weaknessSupersessionTrace(event, eventById);
        trace.chain.forEach(item => {
          if (!aggregate.supersessionChain.some(existing => existing.eventId === item.eventId)) {
            aggregate.supersessionChain.push(item);
          }
        });
        trace.missingEventIds.forEach(eventId => {
          if (!aggregate.missingEventIds.includes(eventId)) aggregate.missingEventIds.push(eventId);
        });
        if (trace.traceStatus === 'incomplete') aggregate.traceStatus = 'incomplete';
        aggregate.confirmationRate = aggregate.rawCount ? (role === 'primary' ? 1 : 0) : 0;
      });
    };
    addNodeEvent(primary, 'primary');
    secondary.forEach(nodeId => addNodeEvent(nodeId, 'secondary'));
  });
  aggregates.forEach(aggregate => {
    aggregate.priority = weaknessPriority(aggregate, referenceMs);
  });
  const projectionNodes = [...aggregates.values()]
    .sort((left, right) => right.priority.score - left.priority.score
      || right.rawCount - left.rawCount || String(left.nodeId).localeCompare(String(right.nodeId)) || left.role.localeCompare(right.role));
  const qids = new Set(candidates.map(event => event.qid).filter(Boolean));
  return {
    projectionVersion: WEAKNESS_PROJECTION_VERSION,
    examFamily: family || 'all',
    range: requestedRange,
    timeAnchor: referenceMs ? new Date(referenceMs).toISOString() : null,
    timeAnchorMode: reference.mode,
    since: cutoff === null ? null : new Date(cutoff).toISOString(),
    until: referenceMs ? new Date(referenceMs).toISOString() : null,
    graphRevision: graph.graphRevision || null,
    nodes: projectionNodes,
    excludedEvents,
    pendingClassification: {
      count: pending.length,
      distinctQids: new Set(pending.map(event => event.qid).filter(Boolean)).size,
      events: pending,
      nextAction: { type: 'classify-pending', label: '補充分類待處理事件' },
    },
    totals: {
      effectiveEventCount: candidates.length,
      mappedEventCount: candidates.length - pending.length,
      pendingEventCount: pending.length,
      distinctQids: qids.size,
    },
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { WEAKNESS_PROJECTION_VERSION, WEAKNESS_PRIORITY_VERSION, buildWeaknessProjection };
}
