// -*- coding: utf-8 -*-
/**
 * snapshotStore.js
 * ================
 * Automatic in-browser snapshots of the user's learning data (v1.3.10).
 *
 * A snapshot is the full result of buildUserBackupSnapshot() (same format and schema as 「下載備份」)
 * plus metadata { id, takenAt, day, reason, counts }. Snapshots live in IndexedDB
 * (DB ee-exam-snapshots, store snapshots) and fall back to localStorage key
 * EE_EXAM_SNAPSHOTS_V1 (at most 2) when IndexedDB is unavailable or fails.
 *
 * Rules:
 * - Snapshots are never part of a backup file (buildUserBackupSnapshot does not read them).
 * - Every storage access is wrapped; a failing snapshot must never break the app.
 * - Pure functions (snapshotRetain, snapshotNeedsDaily, snapshotCounts, ...) are exported for node tests.
 */

const SNAPSHOT_DB_NAME = 'ee-exam-snapshots';
const SNAPSHOT_STORE_NAME = 'snapshots';
const SNAPSHOT_LS_KEY = 'EE_EXAM_SNAPSHOTS_V1';
const SNAPSHOT_LS_MAX = 2;
// A localStorage copy larger than this is skipped so two fallback snapshots can never fill the ~5 MB quota.
const SNAPSHOT_LS_MAX_CHARS = 1200000;
const SNAPSHOT_DAILY_KEEP_DAYS = 7;
const SNAPSHOT_EVENT_KEEP = 3;
const SNAPSHOT_SYNC_KEEP = 2;
const SNAPSHOT_REASONS = ['daily', 'before-import', 'before-restore', 'before-sync'];
const SNAPSHOT_EVENT_REASONS = ['before-import', 'before-restore'];
const SNAPSHOT_KIND_LABELS = { 'daily': '每日', 'before-import': '匯入前', 'before-restore': '還原前', 'before-sync': '同步前' };
const SNAPSHOT_DAILY_DELAY_MS = 300;

// ---- Pure helpers ---------------------------------------------------------

function snapshotPad2(n) {
  return String(n).padStart(2, '0');
}

/** Local calendar date YYYY-MM-DD of a Date / timestamp / ISO string ('' when invalid). */
function snapshotLocalDay(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return `${d.getFullYear()}-${snapshotPad2(d.getMonth() + 1)}-${snapshotPad2(d.getDate())}`;
}

/** Local 'YYYY-MM-DD HH:mm' for the snapshot list. */
function snapshotFormatWhen(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return `${snapshotLocalDay(d)} ${snapshotPad2(d.getHours())}:${snapshotPad2(d.getMinutes())}`;
}

function snapshotKindLabel(reason) {
  return SNAPSHOT_KIND_LABELS[reason] || '';
}

function snapshotDayOf(meta) {
  if (meta && typeof meta.day === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(meta.day)) return meta.day;
  return snapshotLocalDay(meta && meta.takenAt);
}

function snapshotScore(meta) {
  const c = (meta && meta.counts) || {};
  return (Number(c.records) || 0) + (Number(c.completed) || 0);
}

// Sort comparator: newest first (takenAt, then id for a stable order).
function snapshotNewestFirst(a, b) {
  const ta = String(a.takenAt || ''), tb = String(b.takenAt || '');
  if (ta !== tb) return ta < tb ? 1 : -1;
  const ia = String(a.id || ''), ib = String(b.id || '');
  if (ia === ib) return 0;
  return ia < ib ? 1 : -1;
}

/**
 * Counts of a backup snapshot: result-card records, completed scheduled tasks (only codes in
 * DAILY_SCHEDULE.tasks), SM-2 entries and recall entries.
 */
function snapshotCounts(data, schedule) {
  const d = data && typeof data === 'object' ? data : {};
  const sched = schedule !== undefined ? schedule : (typeof DAILY_SCHEDULE !== 'undefined' ? DAILY_SCHEDULE : null);
  const records = d.resultCard && Array.isArray(d.resultCard.records) ? d.resultCard.records.length : 0;
  const completedMap = d.todayTask && d.todayTask.completed && typeof d.todayTask.completed === 'object' ? d.todayTask.completed : {};
  const tasks = sched && sched.tasks && typeof sched.tasks === 'object' ? sched.tasks : null;
  const completed = Object.keys(completedMap).filter(code => !tasks || Object.prototype.hasOwnProperty.call(tasks, code)).length;
  const sm2 = d.sm2Schedule && typeof d.sm2Schedule === 'object' ? Object.keys(d.sm2Schedule).length : 0;
  const recall = d.recallState && typeof d.recallState === 'object' ? Object.keys(d.recallState).length : 0;
  return { records, completed, sm2, recall };
}

/** Nothing worth saving: no result cards, no completed tasks and no SM-2 entries. */
function snapshotIsEmpty(counts) {
  const c = counts || {};
  return !(Number(c.records) > 0) && !(Number(c.completed) > 0) && !(Number(c.sm2) > 0);
}

/**
 * Which snapshot ids to keep.
 * 1. daily: one per local date (newest of the day), the latest 7 distinct dates.
 * 2. before-import / before-restore: newest 3 (together).
 * 3. before-sync (v1.6.0 cloud sync): newest 2, kept apart so frequent syncs never push out a before-import snapshot.
 * 4. Always the snapshot with the most records (counts.records + counts.completed; ties: newer).
 * Everything else is dropped.
 */
function snapshotRetain(list) {
  const items = (Array.isArray(list) ? list : []).filter(r => r && typeof r.id === 'string');
  const keep = new Set();
  const dailyByDay = new Map();
  items.filter(r => r.reason === 'daily').forEach(r => {
    const day = snapshotDayOf(r);
    const current = dailyByDay.get(day);
    if (!current || snapshotNewestFirst(r, current) < 0) dailyByDay.set(day, r);
  });
  Array.from(dailyByDay.keys()).sort().reverse().slice(0, SNAPSHOT_DAILY_KEEP_DAYS).forEach(day => keep.add(dailyByDay.get(day).id));
  items.filter(r => SNAPSHOT_EVENT_REASONS.indexOf(r.reason) >= 0)
    .sort(snapshotNewestFirst).slice(0, SNAPSHOT_EVENT_KEEP).forEach(r => keep.add(r.id));
  items.filter(r => r.reason === 'before-sync')
    .sort(snapshotNewestFirst).slice(0, SNAPSHOT_SYNC_KEEP).forEach(r => keep.add(r.id));
  const best = snapshotBest(items);
  if (best) keep.add(best.id);
  return items.filter(r => keep.has(r.id)).map(r => r.id);
}

/** The snapshot with the most records (ties: newer), or null. */
function snapshotBest(list) {
  let best = null;
  (Array.isArray(list) ? list : []).forEach(r => {
    if (!r) return;
    if (!best) { best = r; return; }
    const a = snapshotScore(r), b = snapshotScore(best);
    if (a > b || (a === b && snapshotNewestFirst(r, best) < 0)) best = r;
  });
  return best;
}

/** Retention for the localStorage fallback: apply the normal rules, then cap to `max` (best first, then newest). */
function snapshotCapLocal(list, max) {
  const limit = Number.isInteger(max) && max >= 0 ? max : SNAPSHOT_LS_MAX;
  const kept = new Set(snapshotRetain(list));
  const pool = (Array.isArray(list) ? list : []).filter(r => r && kept.has(r.id));
  if (pool.length <= limit) return pool.map(r => r.id);
  const best = snapshotBest(pool);
  const rest = pool.filter(r => r !== best).sort(snapshotNewestFirst);
  return [best].concat(rest).slice(0, limit).map(r => r.id);
}

/** True when no daily snapshot exists for today (todayIso: 'YYYY-MM-DD' or an ISO timestamp). */
function snapshotNeedsDaily(list, todayIso) {
  const today = /^\d{4}-\d{2}-\d{2}$/.test(String(todayIso)) ? String(todayIso) : snapshotLocalDay(todayIso);
  if (!today) return false;
  return !(Array.isArray(list) ? list : []).some(r => r && r.reason === 'daily' && snapshotDayOf(r) === today);
}

/** Two-tap confirm for the 還原 button: first tap arms that row, second tap on the same row runs. */
function snapshotConfirmStep(armedId, clickedId) {
  if (armedId && armedId === clickedId) return { armed: null, run: true };
  return { armed: clickedId || null, run: false };
}

/** Row text for the backup modal: '<日期 時間>', kind, counts. */
function snapshotRowParts(meta) {
  const c = (meta && meta.counts) || {};
  return {
    when: snapshotFormatWhen(meta && meta.takenAt),
    kind: snapshotKindLabel(meta && meta.reason),
    counts: `結果卡 ${Number(c.records) || 0} 筆・已完成 ${Number(c.completed) || 0} 項`,
  };
}

function snapshotRecordOk(r) {
  return !!r && typeof r === 'object' && typeof r.id === 'string' && r.id.length > 0
    && typeof r.takenAt === 'string' && !Number.isNaN(Date.parse(r.takenAt))
    && SNAPSHOT_REASONS.indexOf(r.reason) >= 0
    && !!r.counts && typeof r.counts === 'object'
    && !!r.data && typeof r.data === 'object' && !Array.isArray(r.data);
}

function snapshotMeta(r) {
  return { id: r.id, takenAt: r.takenAt, day: snapshotDayOf(r), reason: r.reason, counts: r.counts };
}

// ---- Capture --------------------------------------------------------------

/**
 * Builds a snapshot record synchronously from the current data (so it reflects the state at the call,
 * even when persisting finishes later). Returns null when nothing should be taken or building fails.
 * options: { now, skipIfEmpty }
 */
function snapshotCapture(reason, options) {
  try {
    if (SNAPSHOT_REASONS.indexOf(reason) < 0 || typeof buildUserBackupSnapshot !== 'function') return null;
    const opts = options || {};
    const data = buildUserBackupSnapshot({ skipMetadata: true });
    const counts = snapshotCounts(data);
    if (opts.skipIfEmpty && snapshotIsEmpty(counts)) return null;
    const now = new Date(Number.isFinite(opts.now) ? opts.now : Date.now());
    return {
      id: `snap-${now.getTime().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
      takenAt: now.toISOString(),
      day: snapshotLocalDay(now),
      reason,
      counts,
      data,
    };
  } catch (_) {
    return null;
  }
}

// ---- Storage backends -----------------------------------------------------

let snapshotDbPromise = null;
let snapshotChain = Promise.resolve();

function snapshotOpenDb() {
  if (snapshotDbPromise) return snapshotDbPromise;
  snapshotDbPromise = new Promise(resolve => {
    try {
      if (typeof indexedDB === 'undefined' || !indexedDB) { resolve(null); return; }
      const request = indexedDB.open(SNAPSHOT_DB_NAME, 1);
      request.onupgradeneeded = () => {
        try {
          const db = request.result;
          if (!db.objectStoreNames.contains(SNAPSHOT_STORE_NAME)) db.createObjectStore(SNAPSHOT_STORE_NAME, { keyPath: 'id' });
        } catch (_) { /* open will fail below */ }
      };
      request.onsuccess = () => {
        const db = request.result;
        db.onversionchange = () => { try { db.close(); } catch (_) { /* ignore */ } snapshotDbPromise = null; };
        resolve(db);
      };
      request.onerror = () => resolve(null);
      request.onblocked = () => resolve(null);
    } catch (_) {
      resolve(null);
    }
  });
  return snapshotDbPromise;
}

// Runs work(store) in one transaction; resolves with the last request's result. Rejects on any failure.
function snapshotIdbTx(mode, work) {
  return snapshotOpenDb().then(db => new Promise((resolve, reject) => {
    if (!db) { reject(new Error('indexedDB unavailable')); return; }
    try {
      const tx = db.transaction(SNAPSHOT_STORE_NAME, mode);
      let result;
      const request = work(tx.objectStore(SNAPSHOT_STORE_NAME));
      if (request) request.onsuccess = () => { result = request.result; };
      tx.oncomplete = () => resolve(result);
      tx.onerror = () => reject(tx.error || new Error('indexedDB error'));
      tx.onabort = () => reject(tx.error || new Error('indexedDB aborted'));
    } catch (e) {
      reject(e);
    }
  }));
}

function snapshotLsRead() {
  try {
    if (typeof localStorage === 'undefined') return [];
    const raw = localStorage.getItem(SNAPSHOT_LS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter(snapshotRecordOk) : [];
  } catch (_) {
    return [];
  }
}

function snapshotLsWrite(list) {
  try {
    if (typeof localStorage === 'undefined') return false;
    if (!list.length) localStorage.removeItem(SNAPSHOT_LS_KEY);
    else localStorage.setItem(SNAPSHOT_LS_KEY, JSON.stringify(list));
    return true;
  } catch (_) {
    return false;
  }
}

/** All stored snapshots as [{ src: 'idb'|'ls', rec }]. Never rejects. */
async function snapshotReadEntries() {
  const out = [];
  try {
    const rows = await snapshotIdbTx('readonly', store => store.getAll());
    (Array.isArray(rows) ? rows : []).forEach(r => { if (snapshotRecordOk(r)) out.push({ src: 'idb', rec: r }); });
  } catch (_) { /* fall back to localStorage only */ }
  snapshotLsRead().forEach(r => { if (!out.some(e => e.rec.id === r.id)) out.push({ src: 'ls', rec: r }); });
  return out;
}

/** Stores one record: IndexedDB first, localStorage (max 2, size-guarded) when that fails. */
async function snapshotStoreRecord(rec) {
  try {
    await snapshotIdbTx('readwrite', store => store.put(rec));
    return 'idb';
  } catch (_) { /* fall through to localStorage */ }
  try {
    const raw = JSON.stringify(rec);
    if (raw.length > SNAPSHOT_LS_MAX_CHARS) return null;
    const list = snapshotLsRead().filter(r => r.id !== rec.id);
    list.push(rec);
    const keepIds = new Set(snapshotCapLocal(list, SNAPSHOT_LS_MAX));
    return snapshotLsWrite(list.filter(r => keepIds.has(r.id))) ? 'ls' : null;
  } catch (_) {
    return null;
  }
}

/** Applies the retention rules to everything stored. Never rejects. */
async function snapshotPrune() {
  try {
    const entries = await snapshotReadEntries();
    const keep = new Set(snapshotRetain(entries.map(e => e.rec)));
    const dropIdb = entries.filter(e => e.src === 'idb' && !keep.has(e.rec.id)).map(e => e.rec.id);
    if (dropIdb.length) {
      try { await snapshotIdbTx('readwrite', store => { let last; dropIdb.forEach(id => { last = store.delete(id); }); return last; }); } catch (_) { /* leave extras */ }
    }
    const lsAll = entries.filter(e => e.src === 'ls').map(e => e.rec);
    if (lsAll.length) {
      const lsKeep = new Set(snapshotCapLocal(lsAll.filter(r => keep.has(r.id)), SNAPSHOT_LS_MAX));
      if (lsKeep.size !== lsAll.length) snapshotLsWrite(lsAll.filter(r => lsKeep.has(r.id)));
    }
  } catch (_) { /* pruning is best effort */ }
}

function snapshotEnqueue(task) {
  const run = () => Promise.resolve().then(task).catch(() => ({ ok: false }));
  snapshotChain = snapshotChain.then(run, run);
  return snapshotChain;
}

// ---- Public API -----------------------------------------------------------

/**
 * Persists a record built by snapshotCapture() (storage + retention). Resolves with { ok, id?, store? }; never rejects.
 */
function snapshotSaveCaptured(rec) {
  if (!rec) return Promise.resolve({ ok: false, skipped: true });
  return snapshotEnqueue(async () => {
    const where = await snapshotStoreRecord(rec);
    if (!where) return { ok: false };
    await snapshotPrune();
    return { ok: true, id: rec.id, store: where };
  });
}

/**
 * Takes a snapshot now. The data is read synchronously at the call; persisting is asynchronous.
 * Resolves with { ok, id?, skipped? } and never rejects.
 */
function snapshotTake(reason, options) {
  return snapshotSaveCaptured(snapshotCapture(reason, options));
}

/** Takes today's daily snapshot when none exists yet (and the data is not empty). */
function snapshotRunDaily(options) {
  const opts = options || {};
  const now = Number.isFinite(opts.now) ? opts.now : Date.now();
  return snapshotEnqueue(async () => {
    const entries = await snapshotReadEntries();
    if (!snapshotNeedsDaily(entries.map(e => e.rec), snapshotLocalDay(now))) return { ok: false, skipped: true };
    const rec = snapshotCapture('daily', { now, skipIfEmpty: true });
    if (!rec) return { ok: false, skipped: true };
    const where = await snapshotStoreRecord(rec);
    if (!where) return { ok: false };
    await snapshotPrune();
    return { ok: true, id: rec.id, store: where };
  });
}

/** Snapshot metadata, newest first. Never rejects. */
async function snapshotListMeta() {
  try {
    const entries = await snapshotReadEntries();
    return entries.map(e => snapshotMeta(e.rec)).sort(snapshotNewestFirst);
  } catch (_) {
    return [];
  }
}

/** One full record by id, or null. */
async function snapshotLoad(id) {
  const entries = await snapshotReadEntries();
  const hit = entries.find(e => e.rec.id === id);
  return hit ? hit.rec : null;
}

/**
 * Restores a snapshot (replace mode): takes a before-restore snapshot first, then applies the data
 * through the normal backup validation. Resolves with applyUserDataBackup's result; never rejects.
 */
async function snapshotRestore(id) {
  try {
    const rec = await snapshotLoad(id);
    if (!rec) return { success: false, error: '匯入失敗：JSON 格式無效，未修改任何資料。' };
    await snapshotTake('before-restore');
    if (typeof applyUserDataBackup !== 'function') return { success: false, error: '備份還原功能尚未載入。' };
    return applyUserDataBackup(JSON.stringify(rec.data), 'replace');
  } catch (_) {
    return { success: false, error: '匯入失敗：寫入本機儲存空間時發生錯誤，已回復原資料。' };
  }
}

/** Asks the browser not to evict our storage. Result is ignored. */
function snapshotRequestPersistence() {
  try {
    if (typeof navigator !== 'undefined' && navigator.storage && typeof navigator.storage.persist === 'function') {
      const pending = navigator.storage.persist();
      if (pending && typeof pending.catch === 'function') pending.catch(() => {});
    }
  } catch (_) { /* ignore */ }
}

/** Startup hook: ask for persistence and take today's snapshot without blocking rendering. */
function snapshotInitAuto() {
  snapshotRequestPersistence();
  try {
    setTimeout(() => { snapshotRunDaily().catch(() => {}); }, SNAPSHOT_DAILY_DELAY_MS);
  } catch (_) { /* ignore */ }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    SNAPSHOT_LS_KEY, SNAPSHOT_LS_MAX, SNAPSHOT_DB_NAME, SNAPSHOT_STORE_NAME,
    snapshotLocalDay, snapshotFormatWhen, snapshotKindLabel, snapshotCounts, snapshotIsEmpty,
    snapshotRetain, snapshotBest, snapshotCapLocal, snapshotNeedsDaily, snapshotConfirmStep, snapshotRowParts,
    snapshotRecordOk, snapshotCapture, snapshotSaveCaptured, snapshotTake, snapshotRunDaily, snapshotListMeta, snapshotLoad,
    snapshotRestore, snapshotInitAuto, snapshotRequestPersistence,
  };
}
