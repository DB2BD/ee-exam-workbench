// src/features/breakdownDrill/store.js
/**
 * 破題訓練 (breakdown drill, optional feature — delete src/features/breakdownDrill/ to remove it): records, spacing
 * and round selection.
 *
 * Storage key EE_EXAM_BREAKDOWN_DRILL_V1 = { version: 1, records: [...], active: {...} | null }
 *   record = { id, qid, at, chapter, picked, typeOk, startOk, timedOut, secs }
 *   records are append-only (merge = union by id); `active` (the round in progress) is per-device and is
 *   never written into a backup.
 *
 * Spacing (Leitner, per question, from its own records in time order): a drill with the right type AND a right
 * first step moves the box up by one, anything else resets it to 0.  The question is due again
 * BREAKDOWN_DRILL_INTERVALS[min(box, 3)] local days after its last drill (box 0 = the next day).
 *
 * Round (breakdownDrillBuildRound, pure, rng injectable):
 *   1. due questions (earliest due first, then lower box), at most half of the round unless new ones run out;
 *   2. never-drilled questions: weak chapters (mastery < BREAKDOWN_DRILL_WEAK_M) first, subjects interleaved;
 *   3. reordered so two neighbours are never the same subject when that is possible.
 */

const BREAKDOWN_DRILL_STORAGE_KEY = 'EE_EXAM_BREAKDOWN_DRILL_V1';
const BREAKDOWN_DRILL_ROUND_SIZE = 8;
const BREAKDOWN_DRILL_SECONDS = 120;
const BREAKDOWN_DRILL_OPTIONS = 4;
const BREAKDOWN_DRILL_INTERVALS = [1, 3, 7, 14];
const BREAKDOWN_DRILL_WEAK_M = 0.5;
const BREAKDOWN_DRILL_EXP = 5;
const BREAKDOWN_DRILL_TYPE_EXP = 5;
const BREAKDOWN_DRILL_MAX_RECORDS = 5000;

function breakdownDrillIsPlain_(value) {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function breakdownDrillEmpty() {
  return { version: 1, records: [], active: null };
}

/** A valid record copy, or null. */
function breakdownDrillValidRecord(value) {
  if (!breakdownDrillIsPlain_(value)) return null;
  if (typeof value.id !== 'string' || !value.id || typeof value.qid !== 'string' || !/^EE-\d{3}-\d{2}-\d+$/.test(value.qid)) return null;
  const at = Number(value.at);
  if (!Number.isFinite(at) || at <= 0) return null;
  return {
    id: value.id,
    qid: value.qid,
    at,
    chapter: typeof value.chapter === 'string' ? value.chapter : '',
    picked: typeof value.picked === 'string' ? value.picked : '',
    typeOk: value.typeOk === true,
    startOk: value.startOk === true,
    timedOut: value.timedOut === true,
    secs: Number.isFinite(Number(value.secs)) ? Math.max(0, Math.round(Number(value.secs))) : 0
  };
}

/** Normalised state (invalid or duplicate records dropped, records sorted by time). */
function breakdownDrillNormalize(value) {
  const src = breakdownDrillIsPlain_(value) ? value : {};
  const seen = {};
  const records = [];
  (Array.isArray(src.records) ? src.records : []).forEach(r => {
    const rec = breakdownDrillValidRecord(r);
    if (!rec || seen[rec.id]) return;
    seen[rec.id] = true;
    records.push(rec);
  });
  records.sort((a, b) => (a.at - b.at) || (a.id < b.id ? -1 : (a.id > b.id ? 1 : 0)));
  const active = breakdownDrillIsPlain_(src.active) && Array.isArray(src.active.qids) ? {
    qids: src.active.qids.filter(q => typeof q === 'string'),
    index: Math.max(0, Math.floor(Number(src.active.index) || 0)),
    startedAt: Number(src.active.startedAt) || 0,
    results: Array.isArray(src.active.results) ? src.active.results.filter(id => typeof id === 'string') : []
  } : null;
  return { version: 1, records: records.slice(-BREAKDOWN_DRILL_MAX_RECORDS), active };
}

/** Union by record id (both sides kept, the local copy wins a clash); `active` is the local one. */
function breakdownDrillMerge(localState, importedState) {
  const local = breakdownDrillNormalize(localState);
  const imported = breakdownDrillNormalize(importedState);
  const byId = {};
  imported.records.forEach(r => { byId[r.id] = r; });
  local.records.forEach(r => { byId[r.id] = r; });
  return breakdownDrillNormalize({ version: 1, records: Object.keys(byId).map(id => byId[id]), active: local.active });
}

/** The part of the state that goes into a backup (records only). */
function breakdownDrillBackupPart(state) {
  return { version: 1, records: breakdownDrillNormalize(state).records };
}

function breakdownDrillStorage_(storage) {
  if (storage !== undefined) return storage;
  return typeof localStorage !== 'undefined' ? localStorage : null;
}

function loadBreakdownDrillState(storage) {
  const store = breakdownDrillStorage_(storage);
  if (!store) return breakdownDrillEmpty();
  try {
    const raw = store.getItem(BREAKDOWN_DRILL_STORAGE_KEY);
    return raw ? breakdownDrillNormalize(JSON.parse(raw)) : breakdownDrillEmpty();
  } catch (_) {
    return breakdownDrillEmpty();
  }
}

function saveBreakdownDrillState(state, storage) {
  const store = breakdownDrillStorage_(storage);
  if (!store) return false;
  try {
    store.setItem(BREAKDOWN_DRILL_STORAGE_KEY, JSON.stringify(breakdownDrillNormalize(state)));
  } catch (_) {
    return false;
  }
  if (storage === undefined && typeof cloudSyncMarkDirty === 'function') cloudSyncMarkDirty();
  return true;
}

/** Drill records (time order). */
function getBreakdownDrillRecords(storage) {
  return loadBreakdownDrillState(storage).records;
}

// ---- Spacing --------------------------------------------------------------------------

function breakdownDrillDayKey_(ms) {
  const d = new Date(ms);
  const p = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
}

function breakdownDrillAddDays_(ms, days) {
  const d = new Date(ms);
  return breakdownDrillDayKey_(new Date(d.getFullYear(), d.getMonth(), d.getDate() + days, 12).getTime());
}

/** { qid: { box, lastAt, dueDay, count, lastOk } } from the records. */
function breakdownDrillSpacing(records) {
  const out = {};
  const list = (Array.isArray(records) ? records : []).slice().sort((a, b) => a.at - b.at);
  list.forEach(r => {
    if (!r || typeof r.qid !== 'string') return;
    const cur = out[r.qid] || { box: 0, lastAt: 0, dueDay: '', count: 0, lastOk: false };
    const ok = r.typeOk === true && r.startOk === true;
    cur.box = ok ? cur.box + 1 : 0;
    cur.lastAt = Number(r.at);
    cur.count += 1;
    cur.lastOk = ok;
    cur.dueDay = breakdownDrillAddDays_(cur.lastAt, BREAKDOWN_DRILL_INTERVALS[Math.min(cur.box, BREAKDOWN_DRILL_INTERVALS.length - 1)]);
    out[r.qid] = cur;
  });
  return out;
}

/** Questions whose next drill day has come, earliest first. */
function breakdownDrillDueQids(records, now) {
  const today = breakdownDrillDayKey_(Number.isFinite(Number(now)) ? Number(now) : Date.now());
  const spacing = breakdownDrillSpacing(records);
  return Object.keys(spacing).filter(q => spacing[q].dueDay <= today).sort((a, b) =>
    (spacing[a].dueDay < spacing[b].dueDay ? -1 : (spacing[a].dueDay > spacing[b].dueDay ? 1 : 0))
    || (spacing[a].box - spacing[b].box) || (a < b ? -1 : (a > b ? 1 : 0)));
}

// ---- Round ----------------------------------------------------------------------------

function breakdownDrillShuffle_(list, rng) {
  const out = list.slice();
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1));
    const t = out[i]; out[i] = out[j]; out[j] = t;
  }
  return out;
}

/** Reorder so neighbours differ in subject where possible (stable greedy). */
function breakdownDrillSpread(items) {
  const rest = items.slice();
  const out = [];
  while (rest.length) {
    const prev = out.length ? out[out.length - 1].subject : null;
    let i = rest.findIndex(x => x.subject !== prev);
    if (i < 0) i = 0;
    out.push(rest.splice(i, 1)[0]);
  }
  return out;
}

/**
 * Pure.  input = { bank: [{ id, subject, chapter }], records, now, mastery: { chapterId: m }, size, rng }.
 * Returns the qids of one round.
 */
function breakdownDrillBuildRound(input) {
  const o = input || {};
  const rng = typeof o.rng === 'function' ? o.rng : Math.random;
  const size = Math.max(1, Math.floor(Number(o.size) || BREAKDOWN_DRILL_ROUND_SIZE));
  const mastery = breakdownDrillIsPlain_(o.mastery) ? o.mastery : {};
  const bank = (Array.isArray(o.bank) ? o.bank : []).filter(q => q && typeof q.id === 'string' && q.chapter);
  const byId = {};
  bank.forEach(q => { byId[q.id] = q; });
  const records = Array.isArray(o.records) ? o.records : [];
  const drilled = {};
  records.forEach(r => { if (r && typeof r.qid === 'string') drilled[r.qid] = true; });

  const due = breakdownDrillDueQids(records, o.now).filter(q => byId[q]);
  const isWeak = q => {
    const m = Number(mastery[q.chapter]);
    return !Number.isFinite(m) || m < BREAKDOWN_DRILL_WEAK_M;
  };
  const groups = {};
  breakdownDrillShuffle_(bank.filter(q => !drilled[q.id]), rng).forEach(q => {
    (groups[q.subject] = groups[q.subject] || []).push(q);
  });
  Object.keys(groups).forEach(s => {
    groups[s] = groups[s].filter(isWeak).concat(groups[s].filter(q => !isWeak(q)));
  });
  const subjects = breakdownDrillShuffle_(Object.keys(groups).sort(), rng);
  const fresh = [];
  for (let i = 0; fresh.length < bank.length; i += 1) {
    let added = false;
    subjects.forEach(s => { if (i < groups[s].length) { fresh.push(groups[s][i]); added = true; } });
    if (!added) break;
  }

  const dueCap = fresh.length >= size - Math.ceil(size / 2) ? Math.ceil(size / 2) : size - fresh.length;
  const picked = due.slice(0, dueCap).map(q => byId[q]);
  fresh.forEach(q => { if (picked.length < size) picked.push(q); });
  due.slice(dueCap).forEach(q => { if (picked.length < size) picked.push(byId[q]); });
  if (picked.length < size) {
    // Everything drilled and nothing due: repeat the least recently drilled questions.
    const spacing = breakdownDrillSpacing(records);
    const taken = {};
    picked.forEach(q => { taken[q.id] = true; });
    bank.filter(q => !taken[q.id]).sort((a, b) => ((spacing[a.id] || {}).lastAt || 0) - ((spacing[b.id] || {}).lastAt || 0) || (a.id < b.id ? -1 : 1))
      .forEach(q => { if (picked.length < size) picked.push(q); });
  }
  return breakdownDrillSpread(picked).map(q => q.id);
}

/** Four chapter options for a question: its own chapter plus other chapters of the same subject, shuffled. */
function breakdownDrillOptions(question, bank, rng) {
  const random = typeof rng === 'function' ? rng : Math.random;
  const others = [];
  (Array.isArray(bank) ? bank : []).forEach(q => {
    if (q && q.subject === question.subject && q.chapter && q.chapter !== question.chapter && others.indexOf(q.chapter) < 0) others.push(q.chapter);
  });
  others.sort();
  const chosen = breakdownDrillShuffle_(others, random).slice(0, BREAKDOWN_DRILL_OPTIONS - 1);
  return breakdownDrillShuffle_(chosen.concat([question.chapter]), random);
}

/** EXP earned by drill records: 5 each, 5 more for the right type. */
function breakdownDrillExp(records) {
  return (Array.isArray(records) ? records : []).reduce((n, r) =>
    n + (r ? BREAKDOWN_DRILL_EXP + (r.typeOk === true ? BREAKDOWN_DRILL_TYPE_EXP : 0) : 0), 0);
}

// Backup / cloud sync: the records travel as the optional top-level field `breakdownDrill` (see BACKUP_EXTENSIONS in
// src/state/sm2Store.js); the round in progress stays on this device.
if (typeof registerBackupExtension === 'function') {
  registerBackupExtension({
    field: 'breakdownDrill',
    key: BREAKDOWN_DRILL_STORAGE_KEY,
    read: storage => loadBreakdownDrillState(storage || null),
    toBackup: breakdownDrillBackupPart,
    validate: (value, errors) => {
      if (!breakdownDrillIsPlain_(value) || value.version !== 1 || !Array.isArray(value.records)) {
        const message = 'breakdownDrill 破題訓練資料格式無效。';
        if (typeof backupError === 'function') backupError(errors, message); else errors.push(message);
        return null;
      }
      return breakdownDrillBackupPart(value);
    },
    merge: breakdownDrillMerge,
    replace: (local, value) => breakdownDrillNormalize({ version: 1, records: value.records, active: null }),
    count: state => breakdownDrillNormalize(state).records.length
  });
}
