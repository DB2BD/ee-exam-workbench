// src/state/resultCardStore.js
/**
 * Unified 作答結果卡 records: EE_EXAM_RESULT_CARD_V1 = { version: 1, records: [...], migrated?: true }.
 * Pure model/score helpers plus localStorage persistence (every storage access guarded).
 * Depends on: QUESTION_POINTS, studyPlan.js (studyTierFor, scoreFactorFor) and sm2Store.js
 * (recordSM2Review, backupValidateResultCard) loaded earlier.
 */

const RESULT_CARD_STORAGE_KEY = 'EE_EXAM_RESULT_CARD_V1';
const RESULT_CARD_ERROR_CODES = ['R', 'S', 'F', 'C', 'K', 'U', 'T'];
const RESULT_CARD_ERROR_LABELS = {
  R: '題型', S: '起手式', F: '公式', C: '計算', K: '觀念', U: '單位方向', T: '時間'
};
const RESULT_CARD_SOURCES = ['today', 'random', 'review', 'mock', 'ext', 'legacy'];
const RESULT_CARD_MARKS = ['o', 'tri', 'x'];
const RESULT_CARD_WHOLE_LABEL = '整題';
const RESULT_CARD_LEGACY_ERROR_MAP = {
  '題型辨識錯': 'R', '起手式不會': 'S', '公式忘記': 'F', '計算錯': 'C', '觀念混淆': 'K'
};

function resultCardStorage_(options) {
  if (options && options.storage) return options.storage;
  try { return typeof localStorage !== 'undefined' ? localStorage : null; } catch (_) { return null; }
}

function resultCardPlainObject_(value) {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function resultCardRound_(value) {
  return Math.round(value * 100) / 100;
}

function resultCardPointsFor_(qid) {
  try {
    if (typeof QUESTION_POINTS !== 'undefined' && QUESTION_POINTS && QUESTION_POINTS[qid]) return QUESTION_POINTS[qid];
  } catch (_) { /* fall through */ }
  return null;
}

function resultCardTierFor_(qid) {
  try {
    if (typeof studyTierFor === 'function') {
      const tier = studyTierFor(qid);
      if (tier === 'main' || tier === 'basic') return tier;
    }
  } catch (_) { /* fall through */ }
  return 'main';
}

function buildResultModel(qid) {
  const entry = resultCardPointsFor_(qid);
  const parts = entry && Array.isArray(entry.parts) ? entry.parts.filter(p => p && Number.isFinite(Number(p.points))) : [];
  const total = entry && Number.isFinite(Number(entry.total)) ? Number(entry.total)
    : parts.reduce((sum, p) => sum + Number(p.points), 0);
  return {
    qid,
    tier: resultCardTierFor_(qid),
    total,
    parts: parts.length
      ? parts.map(p => ({ label: String(p.label), points: Number(p.points) }))
      : [{ label: RESULT_CARD_WHOLE_LABEL, points: total }]
  };
}

function scoreResult(model, marks) {
  const list = Array.isArray(marks) ? marks : [];
  let estimate = 0;
  let answered = 0;
  model.parts.forEach((part, index) => {
    const mark = list[index];
    if (RESULT_CARD_MARKS.indexOf(mark) < 0) return;
    answered += 1;
    estimate += part.points * scoreFactorFor(model.tier, mark);
  });
  return {
    estimate: resultCardRound_(estimate),
    total: model.total,
    answered,
    complete: model.parts.length > 0 && answered === model.parts.length
  };
}

/** Worst mark among parts mapped to an SM-2 rating: any x -> 1, else any tri -> 3, else 5. */
function resultCardSM2Rating(marks) {
  const list = (marks || []).filter(m => RESULT_CARD_MARKS.indexOf(m) >= 0);
  if (!list.length) return null;
  if (list.indexOf('x') >= 0) return 1;
  if (list.indexOf('tri') >= 0) return 3;
  return 5;
}

function resultCardEmptyState_() {
  return { version: 1, records: [] };
}

function resultCardValidate_(value) {
  const errors = [];
  const state = typeof backupValidateResultCard === 'function'
    ? backupValidateResultCard(value, errors)
    : null;
  if (!state) return { ok: false, state: resultCardEmptyState_() };
  return errors.length ? { ok: false, state: resultCardEmptyState_() } : { ok: true, state };
}

/** Returns { ok, state, error }. A missing key is ok+empty; unreadable or malformed data is ok:false. */
function loadResultCardState(options) {
  const storage = resultCardStorage_(options);
  if (!storage) return { ok: false, state: resultCardEmptyState_(), error: 'no_storage' };
  let raw;
  try { raw = storage.getItem(RESULT_CARD_STORAGE_KEY); } catch (_) {
    return { ok: false, state: resultCardEmptyState_(), error: 'read_failed' };
  }
  if (raw === null || raw === undefined || raw === '') return { ok: true, state: resultCardEmptyState_(), error: null };
  let parsed;
  try { parsed = JSON.parse(raw); } catch (_) {
    return { ok: false, state: resultCardEmptyState_(), error: 'invalid_json' };
  }
  const checked = resultCardValidate_(parsed);
  return checked.ok ? { ok: true, state: checked.state, error: null }
    : { ok: false, state: resultCardEmptyState_(), error: 'invalid_shape' };
}

function resultCardWrite_(storage, state) {
  try { storage.setItem(RESULT_CARD_STORAGE_KEY, JSON.stringify(state)); return true; } catch (_) { return false; }
}

function resultCardNormalizeErrors_(errors) {
  const out = [];
  (Array.isArray(errors) ? errors : []).forEach(code => {
    if (RESULT_CARD_ERROR_CODES.indexOf(code) >= 0 && out.indexOf(code) < 0) out.push(code);
  });
  return out;
}

function resultCardNormalizeRecord_(record) {
  if (!resultCardPlainObject_(record) || typeof record.qid !== 'string' || !record.qid) return null;
  const model = buildResultModel(record.qid);
  const srcParts = Array.isArray(record.parts) && record.parts.length ? record.parts : null;
  if (!srcParts || !srcParts.every(p => resultCardPlainObject_(p) && RESULT_CARD_MARKS.indexOf(p.mark) >= 0)) return null;
  const tier = record.tier === 'basic' || record.tier === 'main' ? record.tier : model.tier;
  const parts = srcParts.map((p, i) => ({
    label: String(p.label != null ? p.label : (model.parts[i] ? model.parts[i].label : RESULT_CARD_WHOLE_LABEL)),
    points: Number.isFinite(Number(p.points)) ? Number(p.points) : (model.parts[i] ? model.parts[i].points : 0),
    mark: p.mark
  }));
  const total = Number.isFinite(Number(record.total)) ? Number(record.total)
    : parts.reduce((sum, p) => sum + p.points, 0);
  const estimate = resultCardRound_(parts.reduce((sum, p) => sum + p.points * scoreFactorFor(tier, p.mark), 0));
  const at = Number.isFinite(Number(record.at)) ? Number(record.at) : Date.now();
  const source = RESULT_CARD_SOURCES.indexOf(record.source) >= 0 ? record.source : 'today';
  const out = {
    id: typeof record.id === 'string' && record.id ? record.id : `rc-${at}-${record.qid}-${Math.random().toString(36).slice(2, 8)}`,
    qid: record.qid,
    at,
    source,
    tier,
    parts,
    errors: resultCardNormalizeErrors_(record.errors),
    note: typeof record.note === 'string' ? record.note.slice(0, 2000) : '',
    total,
    estimate
  };
  if (typeof record.mockId === 'string' && record.mockId) out.mockId = record.mockId;
  if (record.legacy === true) out.legacy = true;
  return out;
}

/**
 * Saves one record (replacing any record with the same id) and, for non-legacy records,
 * schedules spaced repetition through recordSM2Review (reuses the existing SM-2 math).
 */
function saveResultRecord(record, options) {
  const storage = resultCardStorage_(options);
  if (!storage) return { ok: false, error: 'no_storage', record: null, sm2: null };
  const normalized = resultCardNormalizeRecord_(record);
  if (!normalized) return { ok: false, error: 'invalid_record', record: null, sm2: null };
  resultCardEnsureMigrated_(options);
  const loaded = loadResultCardState({ storage });
  if (!loaded.ok) return { ok: false, error: loaded.error, record: null, sm2: null };
  const state = loaded.state;
  const others = state.records.filter(r => r.id !== normalized.id);
  const next = { version: 1, records: others.concat([normalized]) };
  if (state.migrated === true) next.migrated = true;
  if (!resultCardWrite_(storage, next)) return { ok: false, error: 'write_failed', record: null, sm2: null };
  let sm2 = null;
  if (!normalized.legacy && !(options && options.skipSM2)) {
    const rating = resultCardSM2Rating(normalized.parts.map(p => p.mark));
    if (rating !== null && typeof recordSM2Review === 'function') {
      try { sm2 = recordSM2Review(normalized.qid, rating); } catch (_) { sm2 = { ok: false, error: 'sm2_failed' }; }
    }
  }
  if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function' && typeof CustomEvent === 'function') {
    try { window.dispatchEvent(new CustomEvent('result-card-saved', { detail: { qid: normalized.qid } })); } catch (_) { /* header refresh is best-effort */ }
  }
  return { ok: true, error: null, record: normalized, sm2 };
}

function resultCardEnsureMigrated_(options) {
  if (options && options.autoMigrate === false) return;
  try { migrateLegacyResultRecords(options); } catch (_) { /* migration is best-effort */ }
}

function getResultRecords(filter, options) {
  const f = filter || {};
  resultCardEnsureMigrated_(options);
  const records = loadResultCardState(options).state.records;
  return records.filter(r => {
    if (f.qid && r.qid !== f.qid) return false;
    if (f.source && r.source !== f.source) return false;
    if (f.mockId && r.mockId !== f.mockId) return false;
    if (Number.isFinite(f.since) && r.at < f.since) return false;
    if (f.excludeLegacy && r.legacy) return false;
    if (typeof f.predicate === 'function' && !f.predicate(r)) return false;
    return true;
  }).sort((a, b) => a.at - b.at);
}

function latestRecordFor(qid, options) {
  const list = getResultRecords({ qid }, options);
  return list.length ? list[list.length - 1] : null;
}

/**
 * One-time conversion of daily-practice self-ratings (1/3/5 -> x/tri/o, whole question) into
 * legacy records. Originals are only read. The done flag lives inside the result-card key.
 * Attempt envelopes (EE_EXAM_ATTEMPT_ENVELOPES_V1) carry no rating, so they yield nothing.
 */
function migrateLegacyResultRecords(options) {
  const storage = resultCardStorage_(options);
  if (!storage) return { ok: false, migrated: 0, error: 'no_storage' };
  const loaded = loadResultCardState({ storage });
  if (!loaded.ok) return { ok: false, migrated: 0, error: loaded.error };
  if (loaded.state.migrated === true) return { ok: true, migrated: 0, already: true };
  let practice = null;
  try {
    const raw = storage.getItem('EE_EXAM_DAILY_PRACTICE_V1');
    practice = raw ? JSON.parse(raw) : null;
  } catch (_) { practice = null; }
  const completions = practice && resultCardPlainObject_(practice.completionByQuestion) ? practice.completionByQuestion : {};
  const markFor = { 1: 'x', 3: 'tri', 5: 'o' };
  const known = {};
  loaded.state.records.forEach(r => { known[r.id] = true; });
  const added = [];
  Object.keys(completions).forEach(qid => {
    const value = completions[qid];
    if (!resultCardPlainObject_(value) || !markFor[Number(value.rating)]) return;
    const at = Number(value.completedAt);
    if (!Number.isFinite(at) && typeof value.completedAt !== 'string') return;
    const atMs = Number.isFinite(at) ? at : Date.parse(value.completedAt);
    if (!Number.isFinite(atMs)) return;
    const id = `legacy-${qid}-${atMs}`;
    if (known[id]) return;
    const model = buildResultModel(qid);
    const code = RESULT_CARD_LEGACY_ERROR_MAP[value.errorType];
    const record = resultCardNormalizeRecord_({
      id, qid, at: atMs, source: 'legacy', tier: model.tier,
      parts: [{ label: RESULT_CARD_WHOLE_LABEL, points: model.total, mark: markFor[Number(value.rating)] }],
      errors: code ? [code] : [], note: '', total: model.total, legacy: true
    });
    if (record) { added.push(record); known[id] = true; }
  });
  const next = { version: 1, records: loaded.state.records.concat(added), migrated: true };
  if (!resultCardWrite_(storage, next)) return { ok: false, migrated: 0, error: 'write_failed' };
  return { ok: true, migrated: added.length, already: false };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    RESULT_CARD_STORAGE_KEY, RESULT_CARD_ERROR_CODES, RESULT_CARD_ERROR_LABELS,
    buildResultModel, scoreResult, resultCardSM2Rating, saveResultRecord, getResultRecords,
    latestRecordFor, loadResultCardState, migrateLegacyResultRecords
  };
}
