// -*- coding: utf-8 -*-
/**
 * cloudSync.js
 * ============
 * v1.6.0 cloud sync through one GitHub Gist (REST API, user supplied token).
 *
 * Rules:
 * - The token lives ONLY in localStorage key EE_EXAM_CLOUD_SYNC_V1. It is never read by
 *   buildUserBackupSnapshot, so it is in no backup file, no snapshot and no uploaded gist
 *   (an extra guard refuses to upload content that contains the token).
 * - Sync = fetch remote -> before-sync snapshot -> applyUserDataBackup(remote, 'merge') ->
 *   buildUserBackupSnapshot -> PATCH (or POST when no gist exists yet). applyUserDataBackup keeps its normal
 *   "imported wins" semantics; cloudSyncPrepareRemote first removes from the remote copy everything this device changed
 *   since the last sync (three-way merge against a local "last synced base", kept in its own key and never uploaded).
 * - After a PATCH the gist is read once more; if another device wrote meanwhile, one more merge round runs.
 * - A restore / replace import sets forcePush: the next sync overwrites the cloud with the local data.
 * - Pushes are debounced (30 s). Offline / failed syncs keep a pending flag and retry later.
 * - One tab syncs at a time (localStorage lock; other tabs follow through the storage event).
 * - Every storage / network access is wrapped; sync problems never break the app and never alert().
 */

const CLOUD_SYNC_KEY = 'EE_EXAM_CLOUD_SYNC_V1';
const CLOUD_SYNC_LOCK_KEY = 'EE_EXAM_CLOUD_SYNC_LOCK_V1';
const CLOUD_SYNC_BASE_KEY = 'EE_EXAM_CLOUD_SYNC_BASE_V1';
const CLOUD_SYNC_FILE = 'ee-exam-progress.json';
const CLOUD_SYNC_DESCRIPTION = 'ee-exam-workbench-progress-v1';
const CLOUD_SYNC_API = 'https://api.github.com';
const CLOUD_SYNC_DEBOUNCE_MS = 30000;
const CLOUD_SYNC_OPEN_DELAY_MS = 1200;
const CLOUD_SYNC_LOCK_MS = 120000;
const CLOUD_SYNC_LOCK_CONFIRM_MS = 50;
const CLOUD_SYNC_MAX_SOFT_FAILS = 3;
const CLOUD_SYNC_LOCKED_RETRY_MS = 15000;
const CLOUD_SYNC_RETRY_BASE_MS = 60000;
const CLOUD_SYNC_RETRY_MAX_MS = 600000;
const CLOUD_SYNC_MAX_PAGES = 10;
const CLOUD_SYNC_MAX_BYTES = 8 * 1024 * 1024;
const CLOUD_SYNC_TOKEN_RE = /^[A-Za-z0-9_\-]{20,255}$/;

const CLOUD_SYNC_MESSAGES = {
  badToken: '權杖格式不正確。',
  offline: '目前離線，稍後自動重試。',
  network: '無法連線到 GitHub，稍後自動重試。',
  auth: '權杖無效或已被撤銷，請重新連線。',
  forbidden: '權杖權限不足（需要 gist 權限）或已達 GitHub 使用上限。',
  server: 'GitHub 暫時無法使用，稍後自動重試。',
  http: '同步失敗，請稍後再試。',
  remoteInvalid: '雲端進度格式無法讀取，未上傳。',
  mergeFailed: '雲端進度無法合併，未上傳。',
  tooLarge: '進度資料超過雲端同步容量上限。',
  remoteTooLarge: '雲端進度資料過大，已拒絕讀取。',
  tokenLeak: '同步內容含有權杖，已中止上傳。',
  unavailable: '此瀏覽器不支援雲端同步。',
};

// ---- Pure helpers ---------------------------------------------------------

function cloudSyncPad2(n) {
  return String(n).padStart(2, '0');
}

/** 'M/D HH:mm' in local time ('' when invalid). */
function cloudSyncFormatWhen(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (!value || Number.isNaN(d.getTime())) return '';
  return `${d.getMonth() + 1}/${d.getDate()} ${cloudSyncPad2(d.getHours())}:${cloudSyncPad2(d.getMinutes())}`;
}

function cloudSyncTokenOk(token) {
  return typeof token === 'string' && CLOUD_SYNC_TOKEN_RE.test(token);
}

/** The single status line: the last error when there is one, otherwise 「上次同步：…」 ('' when not connected). */
function cloudSyncStatusText(state, errorText) {
  const st = state || {};
  if (errorText) return errorText;
  if (!st.token) return '';
  const when = cloudSyncFormatWhen(st.lastSyncAt);
  return `上次同步：${when || '尚未同步'}`;
}

/** Key-sorted JSON so two logically equal snapshots compare equal. */
function cloudSyncStable(value) {
  if (Array.isArray(value)) return '[' + value.map(cloudSyncStable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().filter(k => value[k] !== undefined)
      .map(k => JSON.stringify(k) + ':' + cloudSyncStable(value[k])).join(',') + '}';
  }
  return JSON.stringify(value === undefined ? null : value);
}

/** Signature of a backup payload without the fields that always differ (export time, derived capacity). */
function cloudSyncSignature(payload) {
  if (!payload || typeof payload !== 'object') return '';
  const copy = Object.assign({}, payload);
  delete copy.exportedAt;
  delete copy.learningDataCapacity;
  return cloudSyncStable(copy);
}

function cloudSyncIsPlain(value) {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

/** The maps that merge as "imported wins": the part of a payload kept as the last synced base. */
function cloudSyncBaseExtract(payload) {
  const p = cloudSyncIsPlain(payload) ? payload : {};
  const pick = v => (cloudSyncIsPlain(v) ? JSON.parse(JSON.stringify(v)) : {});
  const byCategory = v => {
    const out = {};
    if (cloudSyncIsPlain(v)) Object.keys(v).forEach(cat => { out[cat] = pick(v[cat]); });
    return out;
  };
  return {
    progressByCategory: byCategory(p.progressByCategory),
    starredByCategory: byCategory(p.starredByCategory),
    recallState: pick(p.recallState),
    manualTopicLabels: pick(p.manualTopicLabels),
    completionByQuestion: pick(cloudSyncIsPlain(p.dailyPractice) ? p.dailyPractice.completionByQuestion : null),
  };
}

/**
 * Three-way step for one map: a key whose local value differs from the base (changed, added or deleted locally)
 * is removed from the remote copy, so the merge cannot bring the stale cloud value back.
 */
function cloudSyncKeepLocalChanges(remoteMap, localMap, baseMap) {
  if (!cloudSyncIsPlain(remoteMap)) return remoteMap;
  const mine = cloudSyncIsPlain(localMap) ? localMap : {};
  const base = cloudSyncIsPlain(baseMap) ? baseMap : {};
  const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const out = Object.assign({}, remoteMap);
  const keys = new Set(Object.keys(mine).concat(Object.keys(base)));
  keys.forEach(k => {
    if (has(mine, k) !== has(base, k) || cloudSyncStable(mine[k]) !== cloudSyncStable(base[k])) delete out[k];
  });
  return out;
}

/**
 * Safeguards on the remote copy before the normal merge (none changes applyUserDataBackup):
 * - mockExamTimer is per-device state: keep the local one (a stale remote timer must not replace it).
 * - SM-2: the merge lets the imported entry win, so entries the local device reviewed on the same day or
 *   later are removed from the remote copy; the newer review always survives.
 * - With a last synced base: progress, starred, recall, manual labels and daily-practice completions that this
 *   device changed (or deleted) since that base are removed from the remote copy, so the local edit survives.
 */
function cloudSyncPrepareRemote(remote, local, base) {
  const out = Object.assign({}, remote);
  if (local && Object.prototype.hasOwnProperty.call(local, 'mockExamTimer')) out.mockExamTimer = local.mockExamTimer;
  const localSm2 = local && local.sm2Schedule && typeof local.sm2Schedule === 'object' ? local.sm2Schedule : {};
  if (out.sm2Schedule && typeof out.sm2Schedule === 'object' && !Array.isArray(out.sm2Schedule)) {
    const kept = {};
    Object.keys(out.sm2Schedule).forEach(qid => {
      const mine = localSm2[qid];
      const theirs = out.sm2Schedule[qid];
      const mineDay = mine && typeof mine.lastReviewed === 'string' ? mine.lastReviewed : '';
      const theirDay = theirs && typeof theirs.lastReviewed === 'string' ? theirs.lastReviewed : '';
      if (mine && mineDay >= theirDay) return;
      kept[qid] = theirs;
    });
    out.sm2Schedule = kept;
  }
  if (cloudSyncIsPlain(base) && cloudSyncIsPlain(local)) {
    ['progressByCategory', 'starredByCategory'].forEach(field => {
      if (!cloudSyncIsPlain(out[field])) return;
      const next = {};
      Object.keys(out[field]).forEach(cat => {
        next[cat] = cloudSyncKeepLocalChanges(out[field][cat],
          cloudSyncIsPlain(local[field]) ? local[field][cat] : {}, cloudSyncIsPlain(base[field]) ? base[field][cat] : {});
      });
      out[field] = next;
    });
    ['recallState', 'manualTopicLabels'].forEach(field => {
      if (cloudSyncIsPlain(out[field])) out[field] = cloudSyncKeepLocalChanges(out[field], local[field], base[field]);
    });
    if (cloudSyncIsPlain(out.dailyPractice) && cloudSyncIsPlain(out.dailyPractice.completionByQuestion)) {
      const localDone = cloudSyncIsPlain(local.dailyPractice) ? local.dailyPractice.completionByQuestion : {};
      out.dailyPractice = Object.assign({}, out.dailyPractice, {
        completionByQuestion: cloudSyncKeepLocalChanges(out.dailyPractice.completionByQuestion, localDone, base.completionByQuestion),
      });
    }
  }
  return out;
}

/** The gists of a listing with the right description and file, oldest first (stable across devices). */
function cloudSyncPickGists(list) {
  const hits = (Array.isArray(list) ? list : []).filter(g => g && typeof g.id === 'string'
    && g.description === CLOUD_SYNC_DESCRIPTION && g.files && g.files[CLOUD_SYNC_FILE]);
  hits.sort((a, b) => {
    const ta = String(a.created_at || ''), tb = String(b.created_at || '');
    if (ta !== tb) return ta < tb ? -1 : 1;
    return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
  });
  return hits;
}

/** The gist to use from a gists listing: the oldest match. */
function cloudSyncPickGist(list) {
  return cloudSyncPickGists(list)[0] || null;
}

function cloudSyncTooLargeError() {
  return { kind: 'remoteTooLarge', text: CLOUD_SYNC_MESSAGES.remoteTooLarge, retry: false };
}

function cloudSyncErrorForStatus(status) {
  if (status === 401) return { kind: 'auth', text: CLOUD_SYNC_MESSAGES.auth, retry: false };
  if (status === 403 || status === 429) return { kind: 'forbidden', text: CLOUD_SYNC_MESSAGES.forbidden, retry: status === 429 };
  if (status >= 500) return { kind: 'server', text: CLOUD_SYNC_MESSAGES.server, retry: true };
  return { kind: 'http', text: CLOUD_SYNC_MESSAGES.http, retry: false };
}

// ---- Local state (token, gist id, markers) --------------------------------

function cloudSyncStorage() {
  try { return typeof localStorage !== 'undefined' ? localStorage : null; } catch (_) { return null; }
}

function cloudSyncLoad() {
  const empty = { token: '', gistId: '', lastSyncAt: 0, lastRemoteEtag: '', dirtySeq: 0, syncedSeq: 0, forcePush: false };
  try {
    const store = cloudSyncStorage();
    const raw = store ? store.getItem(CLOUD_SYNC_KEY) : null;
    const parsed = raw ? JSON.parse(raw) : null;
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return empty;
    return {
      token: typeof parsed.token === 'string' ? parsed.token : '',
      gistId: typeof parsed.gistId === 'string' ? parsed.gistId : '',
      lastSyncAt: Number(parsed.lastSyncAt) || 0,
      lastRemoteEtag: typeof parsed.lastRemoteEtag === 'string' ? parsed.lastRemoteEtag : '',
      dirtySeq: Number(parsed.dirtySeq) || 0,
      syncedSeq: Number(parsed.syncedSeq) || 0,
      forcePush: parsed.forcePush === true,
    };
  } catch (_) {
    return empty;
  }
}

function cloudSyncSave(state) {
  try {
    const store = cloudSyncStorage();
    if (!store) return false;
    store.setItem(CLOUD_SYNC_KEY, JSON.stringify(state));
    return true;
  } catch (_) {
    return false;
  }
}

/** Reads, patches and writes the state in one step (so concurrent markers are not overwritten by stale copies). */
function cloudSyncUpdate(patchFn) {
  const next = patchFn(cloudSyncLoad());
  if (next && next.token) cloudSyncSave(next);
  return next;
}

function cloudSyncConnected() {
  return !!cloudSyncLoad().token;
}

function cloudSyncPending(state) {
  const st = state || cloudSyncLoad();
  return !!st.token && st.dirtySeq > st.syncedSeq;
}

function cloudSyncBaseLoad() {
  try {
    const store = cloudSyncStorage();
    const raw = store ? store.getItem(CLOUD_SYNC_BASE_KEY) : null;
    const parsed = raw ? JSON.parse(raw) : null;
    return cloudSyncIsPlain(parsed) ? parsed : null;
  } catch (_) {
    return null;
  }
}

function cloudSyncBaseSave(payload) {
  try {
    const store = cloudSyncStorage();
    if (store) store.setItem(CLOUD_SYNC_BASE_KEY, JSON.stringify(cloudSyncBaseExtract(payload)));
  } catch (_) { /* no base: the next sync falls back to the plain merge */ }
}

// ---- Runtime (timers, status, lock) ---------------------------------------

let cloudSyncError = '';
let cloudSyncErrorKind = '';
let cloudSyncSoftFails = 0;
let cloudSyncDupChecked = false;
let cloudSyncRunning = false;
let cloudSyncInFlight = null;
let cloudSyncRerun = false;
let cloudSyncDebounceTimer = null;
let cloudSyncRetryTimer = null;
let cloudSyncRetryCount = 0;
const cloudSyncTabId = 'tab-' + Math.random().toString(36).slice(2, 10);

function cloudSyncNotify() {
  try { if (typeof renderCloudSyncSection === 'function') renderCloudSyncSection(); } catch (_) { /* UI is optional */ }
}

function cloudSyncSetError(text, kind) {
  cloudSyncError = text || '';
  cloudSyncErrorKind = text ? (kind || '') : '';
  cloudSyncNotify();
}

function cloudSyncStatusNow() {
  return { running: cloudSyncRunning, error: cloudSyncError, kind: cloudSyncErrorKind, text: cloudSyncStatusText(cloudSyncLoad(), cloudSyncError) };
}

function cloudSyncClearTimers() {
  try { if (cloudSyncDebounceTimer) clearTimeout(cloudSyncDebounceTimer); } catch (_) { /* ignore */ }
  try { if (cloudSyncRetryTimer) clearTimeout(cloudSyncRetryTimer); } catch (_) { /* ignore */ }
  cloudSyncDebounceTimer = null;
  cloudSyncRetryTimer = null;
  cloudSyncRetryCount = 0;
}

function cloudSyncDelay(ms) {
  return new Promise(resolve => {
    try { setTimeout(resolve, ms); } catch (_) { resolve(); }
  });
}

/** Writes a random owner stamp, waits briefly, re-reads it and proceeds only when it is still ours. */
async function cloudSyncAcquireLock() {
  const store = cloudSyncStorage();
  if (!store) return true;
  try {
    const now = Date.now();
    let held = null;
    try { held = JSON.parse(store.getItem(CLOUD_SYNC_LOCK_KEY) || 'null'); } catch (_) { held = null; }
    if (held && held.owner !== cloudSyncTabId && Number(held.until) > now) return false;
    const nonce = Math.random().toString(36).slice(2, 12);
    store.setItem(CLOUD_SYNC_LOCK_KEY, JSON.stringify({ owner: cloudSyncTabId, nonce, until: now + CLOUD_SYNC_LOCK_MS }));
    await cloudSyncDelay(CLOUD_SYNC_LOCK_CONFIRM_MS);
    const check = JSON.parse(store.getItem(CLOUD_SYNC_LOCK_KEY) || 'null');
    return !!check && check.owner === cloudSyncTabId && check.nonce === nonce;
  } catch (_) {
    return true; // storage trouble: do not block syncing in a single tab
  }
}

function cloudSyncReleaseLock() {
  const store = cloudSyncStorage();
  if (!store) return;
  try {
    const held = JSON.parse(store.getItem(CLOUD_SYNC_LOCK_KEY) || 'null');
    if (held && held.owner === cloudSyncTabId) store.removeItem(CLOUD_SYNC_LOCK_KEY);
  } catch (_) { /* ignore */ }
}

function cloudSyncScheduleRetry(delayMs, reason) {
  try {
    if (cloudSyncRetryTimer) clearTimeout(cloudSyncRetryTimer);
    cloudSyncRetryTimer = setTimeout(() => {
      cloudSyncRetryTimer = null;
      cloudSyncRun(reason || 'retry').catch(() => {});
    }, delayMs);
  } catch (_) { /* no timers available */ }
}

function cloudSyncScheduleBackoff() {
  cloudSyncRetryCount += 1;
  const delay = Math.min(CLOUD_SYNC_RETRY_BASE_MS * Math.pow(2, cloudSyncRetryCount - 1), CLOUD_SYNC_RETRY_MAX_MS);
  cloudSyncScheduleRetry(delay, 'retry');
}

// ---- GitHub API -----------------------------------------------------------

/** One API call. Never rejects and never includes the token in its result. */
async function cloudSyncApi(token, method, urlOrPath, body, extraHeaders) {
  if (typeof fetch !== 'function') return { ok: false, status: 0, error: { kind: 'unavailable', text: CLOUD_SYNC_MESSAGES.unavailable, retry: false } };
  const isAbsolute = /^https:\/\//.test(urlOrPath);
  const headers = Object.assign({ Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' }, extraHeaders || {});
  if (token && !isAbsolute) headers.Authorization = 'Bearer ' + token;
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  let res;
  try {
    res = await fetch(isAbsolute ? urlOrPath : CLOUD_SYNC_API + urlOrPath, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      cache: 'no-store',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
    });
  } catch (_) {
    const offline = typeof navigator !== 'undefined' && navigator.onLine === false;
    return { ok: false, status: 0, error: { kind: offline ? 'offline' : 'network', text: offline ? CLOUD_SYNC_MESSAGES.offline : CLOUD_SYNC_MESSAGES.network, retry: true } };
  }
  const status = Number(res && res.status) || 0;
  const etag = res && res.headers && typeof res.headers.get === 'function' ? (res.headers.get('etag') || '') : '';
  if (status === 304) return { ok: true, status, notModified: true, etag, data: null };
  if (!res.ok) return { ok: false, status, error: cloudSyncErrorForStatus(status) };
  const declared = res.headers && typeof res.headers.get === 'function' ? Number(res.headers.get('content-length')) : NaN;
  if (declared > CLOUD_SYNC_MAX_BYTES) return { ok: false, status, error: cloudSyncTooLargeError() };
  let data = null;
  try {
    data = isAbsolute ? await res.text() : await res.json();
  } catch (_) {
    return { ok: false, status, error: { kind: 'http', text: CLOUD_SYNC_MESSAGES.http, retry: false } };
  }
  return { ok: true, status, etag, data };
}

/**
 * Lists gists (up to CLOUD_SYNC_MAX_PAGES pages) and stops at the first page that has matches by description.
 * Resolves { ok, hits } (oldest first, possibly empty) or { ok:false, error }.
 */
async function cloudSyncFindGists(token) {
  for (let page = 1; page <= CLOUD_SYNC_MAX_PAGES; page += 1) {
    const res = await cloudSyncApi(token, 'GET', `/gists?per_page=100&page=${page}`);
    if (!res.ok) return res;
    const list = Array.isArray(res.data) ? res.data : [];
    const hits = cloudSyncPickGists(list);
    if (hits.length) return { ok: true, hits };
    if (list.length < 100) break;
  }
  return { ok: true, hits: [] };
}

/** The file text of a gist API object; follows raw_url when GitHub truncated a large file. Refuses oversized files. */
async function cloudSyncReadGistContent(token, gist) {
  const file = gist && gist.files ? gist.files[CLOUD_SYNC_FILE] : null;
  if (!file) return { ok: true, content: null };
  if (Number(file.size) > CLOUD_SYNC_MAX_BYTES) return { ok: false, status: 200, error: cloudSyncTooLargeError() };
  let content = null;
  if (file.truncated && typeof file.raw_url === 'string') {
    const raw = await cloudSyncApi(token, 'GET', file.raw_url);
    if (!raw.ok) return raw;
    content = String(raw.data);
  } else {
    content = typeof file.content === 'string' ? file.content : null;
  }
  if (content !== null && content.length > CLOUD_SYNC_MAX_BYTES) return { ok: false, status: 200, error: cloudSyncTooLargeError() };
  return { ok: true, content };
}

async function cloudSyncGetGist(token, gistId, etag) {
  const res = await cloudSyncApi(token, 'GET', `/gists/${encodeURIComponent(gistId)}`, undefined, etag ? { 'If-None-Match': etag } : undefined);
  if (!res.ok || res.notModified) return res;
  const read = await cloudSyncReadGistContent(token, res.data);
  if (!read.ok) return read;
  return { ok: true, content: read.content, etag: res.etag || '' };
}

/**
 * Looks up the remote copy. Resolves
 * { ok, gistId|'', content|null, etag, unchanged, extras:[gistId] } or { ok:false, error }.
 * The gists listing runs once per app start (and right after a POST): when several gists carry our description the
 * oldest is used and the newer ones are returned as extras to be merged in (nothing is deleted).
 */
async function cloudSyncFetchRemote(state, options) {
  const force = !!(options && options.force);
  let first = null;
  if (state.gistId) {
    const res = await cloudSyncGetGist(state.token, state.gistId, state.lastRemoteEtag);
    if (res.ok && res.notModified) first = { ok: true, gistId: state.gistId, content: null, etag: state.lastRemoteEtag, unchanged: true, extras: [] };
    else if (res.ok) first = { ok: true, gistId: state.gistId, content: res.content, etag: res.etag, unchanged: false, extras: [] };
    else if (res.status !== 404) return res;
    // 404: the gist was deleted; look for another one, else create a new one
  }
  if (first && cloudSyncDupChecked) return first;
  const found = await cloudSyncFindGists(state.token);
  if (!found.ok) return first || found;
  cloudSyncDupChecked = true;
  const hits = found.hits;
  if (first) {
    if (!hits.some(h => h.id === state.gistId)) return first; // not in the listing (beyond the page cap): keep the bound one
    if (hits[0].id === state.gistId) {
      first.extras = force ? [] : hits.slice(1).map(h => h.id);
      return first;
    }
  }
  if (!hits.length) return { ok: true, gistId: '', content: null, etag: '', unchanged: false, extras: [] };
  const chosen = hits[0];
  const full = await cloudSyncGetGist(state.token, chosen.id, '');
  if (!full.ok) return full;
  return { ok: true, gistId: chosen.id, content: full.content, etag: full.etag, unchanged: false,
    extras: force ? [] : hits.slice(1).map(h => h.id) };
}

async function cloudSyncPush(state, gistId, content) {
  const files = { [CLOUD_SYNC_FILE]: { content } };
  if (gistId) return cloudSyncApi(state.token, 'PATCH', `/gists/${encodeURIComponent(gistId)}`, { files });
  return cloudSyncApi(state.token, 'POST', '/gists', { description: CLOUD_SYNC_DESCRIPTION, public: false, files });
}

// ---- Sync -----------------------------------------------------------------

function cloudSyncRefreshUi() {
  try {
    if (typeof todayTaskRefresh === 'function') todayTaskRefresh();
    if (typeof initDailyPracticeHome === 'function') initDailyPracticeHome();
    if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
    if (typeof renderQuestions === 'function') renderQuestions();
    if (typeof renderScoreboardIfVisible === 'function') renderScoreboardIfVisible();
    if (typeof renderReviewPage === 'function') renderReviewPage();
  } catch (_) { /* UI refresh is best-effort */ }
}

function cloudSyncFail(error, startSeqKept) {
  cloudSyncSetError(error.text, error.kind);
  if (error.retry) cloudSyncScheduleBackoff();
  return { ok: false, error: error.text, kind: error.kind, retry: !!error.retry, keptPending: startSeqKept !== false };
}

/** Unexpected (programming / merge) failures retry with backoff only CLOUD_SYNC_MAX_SOFT_FAILS times in a row. */
function cloudSyncSoftFail(kind, text) {
  cloudSyncSoftFails += 1;
  return cloudSyncFail({ kind, text, retry: cloudSyncSoftFails < CLOUD_SYNC_MAX_SOFT_FAILS });
}

/**
 * One fetch -> merge -> push round. Resolves a failure from cloudSyncFail, or
 * { ok:true, pushed, merged, again, merged payload, forced, gistId, etag } where `again` asks for one more round.
 */
async function cloudSyncRound(state, round) {
  const allowAgain = round === 0;
  const force = state.forcePush === true;
  const remote = await cloudSyncFetchRemote(state, { force });
  if (!remote.ok) {
    if (remote.status === 401) cloudSyncClearTimers();
    return cloudSyncFail(remote.error);
  }

  let remoteSignature = '';
  let changedLocally = false;
  const hasContent = remote.content !== null && remote.content !== undefined && String(remote.content).trim() !== '';
  const extraContents = [];
  if (!force) {
    for (const id of (remote.extras || [])) {
      const extra = await cloudSyncGetGist(state.token, id, '');
      if (extra.ok && !extra.notModified && extra.content && String(extra.content).trim() !== '') extraContents.push(extra.content);
    }
  }
  if (!force && (hasContent || extraContents.length)) {
    let parsed = null;
    if (hasContent) {
      try { parsed = JSON.parse(remote.content); } catch (_) { parsed = null; }
      if (!cloudSyncIsPlain(parsed)) return cloudSyncFail({ kind: 'remoteInvalid', text: CLOUD_SYNC_MESSAGES.remoteInvalid, retry: false });
      remoteSignature = cloudSyncSignature(parsed);
    }
    const before = cloudSyncSignature(buildUserBackupSnapshot({ skipMetadata: true }));
    if (round === 0 && typeof snapshotTake === 'function') {
      try { await snapshotTake('before-sync', { skipIfEmpty: true }); } catch (_) { /* snapshots never block syncing */ }
    }
    if (typeof gkDataLoaded === 'function' && typeof ensureGkData === 'function' && !gkDataLoaded()) {
      let ok = false;
      try { ok = await ensureGkData(); } catch (_) { ok = false; }
      if (!ok) return cloudSyncSoftFail('mergeFailed', CLOUD_SYNC_MESSAGES.mergeFailed);
    }
    const base = cloudSyncBaseLoad();
    const mergeIn = payload => {
      const local = buildUserBackupSnapshot({ skipMetadata: true });
      const result = applyUserDataBackup(cloudSyncPrepareRemote(payload, local, base), 'merge');
      return !!(result && result.success);
    };
    if (parsed && !mergeIn(parsed)) return cloudSyncFail({ kind: 'mergeFailed', text: CLOUD_SYNC_MESSAGES.mergeFailed, retry: false });
    for (const text of extraContents) {
      let extraParsed = null;
      try { extraParsed = JSON.parse(text); } catch (_) { extraParsed = null; }
      if (cloudSyncIsPlain(extraParsed)) mergeIn(extraParsed); // a duplicate that cannot be read is simply skipped
    }
    changedLocally = cloudSyncSignature(buildUserBackupSnapshot({ skipMetadata: true })) !== before;
  } else if (remote.unchanged) {
    remoteSignature = null; // 304: the remote is what we last wrote or merged
  }

  const merged = buildUserBackupSnapshot({ skipMetadata: true });
  const needsPush = force ? true
    : (remote.unchanged ? (cloudSyncPending(cloudSyncLoad()) || changedLocally)
      : (remoteSignature === '' || remoteSignature !== cloudSyncSignature(merged)));
  let etag = remote.etag;
  let gistId = remote.gistId;
  let again = false;
  if (needsPush) {
    const content = JSON.stringify(merged);
    if (content.length > CLOUD_SYNC_MAX_BYTES) return cloudSyncFail({ kind: 'tooLarge', text: CLOUD_SYNC_MESSAGES.tooLarge, retry: false });
    if (state.token && content.indexOf(state.token) >= 0) return cloudSyncFail({ kind: 'tokenLeak', text: CLOUD_SYNC_MESSAGES.tokenLeak, retry: false });
    const pushed = await cloudSyncPush(state, gistId, content);
    if (!pushed.ok) return cloudSyncFail(pushed.error);
    etag = pushed.etag || '';
    if (gistId) {
      if (allowAgain) {
        // Another device may have written around our PATCH: read once more and compare.
        const check = await cloudSyncGetGist(state.token, gistId, '');
        if (check.ok && !check.notModified) {
          let differs = false;
          if (check.content !== null && check.content !== undefined) {
            try { differs = cloudSyncSignature(JSON.parse(check.content)) !== cloudSyncSignature(merged); } catch (_) { differs = true; }
          } else if (pushed.etag && check.etag && pushed.etag !== check.etag) {
            differs = true;
          }
          if (differs) again = true;
          else if (check.etag) etag = check.etag;
        }
      }
    } else if (pushed.data && typeof pushed.data.id === 'string') {
      gistId = pushed.data.id;
      // Right after a POST: two devices may have created a gist at the same time. Use (and later merge into) the oldest.
      const found = await cloudSyncFindGists(state.token);
      cloudSyncDupChecked = true;
      if (found.ok && found.hits.length && found.hits[0].id !== gistId && allowAgain) {
        gistId = found.hits[0].id;
        etag = '';
        again = true;
      }
    }
  }
  if (gistId && gistId !== state.gistId) {
    cloudSyncUpdate(current => Object.assign({}, current, { gistId, lastRemoteEtag: again ? '' : current.lastRemoteEtag }));
  }
  if (again) cloudSyncUpdate(current => Object.assign({}, current, { lastRemoteEtag: '' }));
  return { ok: true, pushed: needsPush, merged: changedLocally, again, payload: merged, forced: force, gistId, etag };
}

async function cloudSyncRunOnce(reason) {
  const state = cloudSyncLoad();
  if (!state.token) return { ok: false, skipped: 'disconnected' };
  if (typeof navigator !== 'undefined' && navigator.onLine === false) {
    return cloudSyncFail({ kind: 'offline', text: CLOUD_SYNC_MESSAGES.offline, retry: false });
  }
  cloudSyncRunning = true;
  cloudSyncNotify();
  if (!(await cloudSyncAcquireLock())) {
    // Another tab is syncing; it works on the same shared data. Check back for anything marked meanwhile.
    cloudSyncRunning = false;
    cloudSyncNotify();
    cloudSyncScheduleRetry(CLOUD_SYNC_LOCKED_RETRY_MS, 'locked-retry');
    return { ok: false, skipped: 'locked' };
  }
  try {
    const startSeq = state.dirtySeq;
    let result = null;
    let changedLocally = false;
    let pushedAny = false;
    let forced = false;
    for (let round = 0; round < 2; round += 1) {
      const current = cloudSyncLoad();
      if (!current.token) return { ok: false, skipped: 'disconnected' };
      result = await cloudSyncRound(current, round);
      if (!result.ok) return result;
      changedLocally = changedLocally || result.merged;
      pushedAny = pushedAny || result.pushed;
      forced = forced || result.forced;
      if (!result.again) break;
    }
    cloudSyncBaseSave(result.payload);
    cloudSyncUpdate(current => Object.assign({}, current, {
      gistId: result.gistId || current.gistId,
      lastRemoteEtag: result.etag || '',
      lastSyncAt: Date.now(),
      syncedSeq: Math.max(current.syncedSeq, startSeq),
      forcePush: forced ? false : current.forcePush,
    }));
    cloudSyncRetryCount = 0;
    cloudSyncSoftFails = 0;
    cloudSyncSetError('');
    if (changedLocally) cloudSyncRefreshUi();
    return { ok: true, pushed: pushedAny, merged: changedLocally, reason };
  } catch (_) {
    return cloudSyncSoftFail('http', CLOUD_SYNC_MESSAGES.http);
  } finally {
    cloudSyncReleaseLock();
    cloudSyncRunning = false;
    cloudSyncNotify();
  }
}

/** Runs one sync (a second call while one is running is queued behind it). Never rejects. */
function cloudSyncRun(reason) {
  if (cloudSyncInFlight) {
    cloudSyncRerun = true;
    return cloudSyncInFlight;
  }
  if (reason === 'locked-retry' && !cloudSyncPending()) return Promise.resolve({ ok: true, skipped: 'nothing-pending' });
  cloudSyncInFlight = cloudSyncRunOnce(reason || 'manual').catch(() => ({ ok: false })).then(result => {
    cloudSyncInFlight = null;
    if (cloudSyncRerun) {
      cloudSyncRerun = false;
      cloudSyncRun('rerun').catch(() => {});
    }
    return result;
  });
  return cloudSyncInFlight;
}

// ---- Public API -----------------------------------------------------------

/** Call after local progress changed (result card, today task, SM-2 review, import). Debounced upload. */
function cloudSyncMarkDirty() {
  try {
    const state = cloudSyncLoad();
    if (!state.token) return false;
    cloudSyncSave(Object.assign({}, state, { dirtySeq: state.dirtySeq + 1 }));
    if (cloudSyncDebounceTimer) clearTimeout(cloudSyncDebounceTimer);
    cloudSyncDebounceTimer = setTimeout(() => {
      cloudSyncDebounceTimer = null;
      cloudSyncRun('push').catch(() => {});
    }, CLOUD_SYNC_DEBOUNCE_MS);
    return true;
  } catch (_) {
    return false;
  }
}

/** Saves the token and runs the first sync. A token GitHub rejects is not kept. */
async function cloudSyncConnect(rawToken) {
  const token = String(rawToken === undefined || rawToken === null ? '' : rawToken).trim();
  if (!cloudSyncTokenOk(token)) {
    cloudSyncSetError(CLOUD_SYNC_MESSAGES.badToken);
    return { ok: false, error: CLOUD_SYNC_MESSAGES.badToken };
  }
  cloudSyncClearTimers();
  cloudSyncDupChecked = false;
  try { const store = cloudSyncStorage(); if (store) store.removeItem(CLOUD_SYNC_BASE_KEY); } catch (_) { /* ignore */ }
  if (!cloudSyncSave({ token, gistId: '', lastSyncAt: 0, lastRemoteEtag: '', dirtySeq: 0, syncedSeq: 0, forcePush: false })) {
    cloudSyncSetError(CLOUD_SYNC_MESSAGES.unavailable);
    return { ok: false, error: CLOUD_SYNC_MESSAGES.unavailable };
  }
  cloudSyncSetError('');
  const result = await cloudSyncRun('connect');
  if (result && result.ok === false && result.kind === 'auth') cloudSyncDisconnect({ keepError: true });
  return result;
}

/** Removes the token and every sync marker from this device (the gist itself is not touched). */
function cloudSyncDisconnect(options) {
  cloudSyncClearTimers();
  try {
    const store = cloudSyncStorage();
    if (store) { store.removeItem(CLOUD_SYNC_KEY); store.removeItem(CLOUD_SYNC_LOCK_KEY); store.removeItem(CLOUD_SYNC_BASE_KEY); }
  } catch (_) { /* ignore */ }
  cloudSyncDupChecked = false;
  if (!(options && options.keepError)) { cloudSyncError = ''; cloudSyncErrorKind = ''; }
  cloudSyncNotify();
}

/** Sets the force-push flag: the next sync skips merging and overwrites the cloud copy with this device's data. */
function cloudSyncForcePush() {
  try {
    const state = cloudSyncLoad();
    if (!state.token) return false;
    cloudSyncSave(Object.assign({}, state, { forcePush: true }));
    return cloudSyncMarkDirty();
  } catch (_) {
    return false;
  }
}

/** options.overwrite: overwrite the cloud copy with the local data (used after the user confirmed it). */
function cloudSyncNow(options) {
  if (options && options.overwrite) cloudSyncForcePush();
  return cloudSyncRun('manual');
}

/** Another tab changed our key (connect / disconnect / finished sync): follow it. */
function cloudSyncOnStorage(event) {
  try {
    const key = event ? event.key : null;
    if (key !== null && key !== undefined && key !== CLOUD_SYNC_KEY) return;
    if (!cloudSyncConnected()) cloudSyncClearTimers();
    cloudSyncNotify();
  } catch (_) { /* best effort */ }
}

/** Startup hook: pull on open (after the daily snapshot), listen for results, coming back online and other tabs. */
function cloudSyncInit() {
  try {
    if (typeof window !== 'undefined' && typeof window.addEventListener === 'function') {
      window.addEventListener('result-card-saved', cloudSyncMarkDirty);
      window.addEventListener('online', () => {
        if (cloudSyncConnected()) cloudSyncRun('online').catch(() => {});
      });
      window.addEventListener('storage', cloudSyncOnStorage);
    }
    if (cloudSyncConnected()) setTimeout(() => { cloudSyncRun('open').catch(() => {}); }, CLOUD_SYNC_OPEN_DELAY_MS);
  } catch (_) { /* sync never breaks startup */ }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CLOUD_SYNC_KEY, CLOUD_SYNC_FILE, CLOUD_SYNC_DESCRIPTION, CLOUD_SYNC_DEBOUNCE_MS,
    cloudSyncFormatWhen, cloudSyncStatusText, cloudSyncSignature, cloudSyncPrepareRemote, cloudSyncPickGist,
    cloudSyncConnect, cloudSyncDisconnect, cloudSyncNow, cloudSyncForcePush, cloudSyncMarkDirty, cloudSyncInit, cloudSyncRun,
  };
}
