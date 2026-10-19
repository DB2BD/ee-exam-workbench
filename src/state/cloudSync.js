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
 *   buildUserBackupSnapshot -> PATCH (or POST when no gist exists yet). No separate conflict logic,
 *   except two per-device safeguards applied to the remote copy before merging (see cloudSyncPrepareRemote).
 * - Pushes are debounced (30 s). Offline / failed syncs keep a pending flag and retry later.
 * - One tab syncs at a time (localStorage lock; other tabs follow through the storage event).
 * - Every storage / network access is wrapped; sync problems never break the app and never alert().
 */

const CLOUD_SYNC_KEY = 'EE_EXAM_CLOUD_SYNC_V1';
const CLOUD_SYNC_LOCK_KEY = 'EE_EXAM_CLOUD_SYNC_LOCK_V1';
const CLOUD_SYNC_FILE = 'ee-exam-progress.json';
const CLOUD_SYNC_DESCRIPTION = 'ee-exam-workbench-progress-v1';
const CLOUD_SYNC_API = 'https://api.github.com';
const CLOUD_SYNC_DEBOUNCE_MS = 30000;
const CLOUD_SYNC_OPEN_DELAY_MS = 1200;
const CLOUD_SYNC_LOCK_MS = 120000;
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

/**
 * Two safeguards on the remote copy before the normal merge (neither changes applyUserDataBackup):
 * - mockExamTimer is per-device state: keep the local one (a stale remote timer must not replace it).
 * - SM-2: the merge lets the imported entry win, so entries the local device reviewed on the same day or
 *   later are removed from the remote copy; the newer review always survives.
 */
function cloudSyncPrepareRemote(remote, local) {
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
  return out;
}

/** Picks the gist to use from a gists listing: right description and file, oldest first (stable across devices). */
function cloudSyncPickGist(list) {
  const hits = (Array.isArray(list) ? list : []).filter(g => g && typeof g.id === 'string'
    && g.description === CLOUD_SYNC_DESCRIPTION && g.files && g.files[CLOUD_SYNC_FILE]);
  hits.sort((a, b) => {
    const ta = String(a.created_at || ''), tb = String(b.created_at || '');
    if (ta !== tb) return ta < tb ? -1 : 1;
    return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
  });
  return hits[0] || null;
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
  const empty = { token: '', gistId: '', lastSyncAt: 0, lastRemoteEtag: '', dirtySeq: 0, syncedSeq: 0 };
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

// ---- Runtime (timers, status, lock) ---------------------------------------

let cloudSyncError = '';
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

function cloudSyncSetError(text) {
  cloudSyncError = text || '';
  cloudSyncNotify();
}

function cloudSyncStatusNow() {
  return { running: cloudSyncRunning, error: cloudSyncError, text: cloudSyncStatusText(cloudSyncLoad(), cloudSyncError) };
}

function cloudSyncClearTimers() {
  try { if (cloudSyncDebounceTimer) clearTimeout(cloudSyncDebounceTimer); } catch (_) { /* ignore */ }
  try { if (cloudSyncRetryTimer) clearTimeout(cloudSyncRetryTimer); } catch (_) { /* ignore */ }
  cloudSyncDebounceTimer = null;
  cloudSyncRetryTimer = null;
  cloudSyncRetryCount = 0;
}

function cloudSyncAcquireLock() {
  const store = cloudSyncStorage();
  if (!store) return true;
  try {
    const now = Date.now();
    let held = null;
    try { held = JSON.parse(store.getItem(CLOUD_SYNC_LOCK_KEY) || 'null'); } catch (_) { held = null; }
    if (held && held.owner !== cloudSyncTabId && Number(held.until) > now) return false;
    store.setItem(CLOUD_SYNC_LOCK_KEY, JSON.stringify({ owner: cloudSyncTabId, until: now + CLOUD_SYNC_LOCK_MS }));
    const check = JSON.parse(store.getItem(CLOUD_SYNC_LOCK_KEY) || 'null');
    return !!check && check.owner === cloudSyncTabId;
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
  let data = null;
  try {
    data = isAbsolute ? await res.text() : await res.json();
  } catch (_) {
    return { ok: false, status, error: { kind: 'http', text: CLOUD_SYNC_MESSAGES.http, retry: false } };
  }
  return { ok: true, status, etag, data };
}

/** Finds our gist by its fixed description. Resolves { ok, gist|null } or { ok:false, error }. */
async function cloudSyncFindGist(token) {
  for (let page = 1; page <= CLOUD_SYNC_MAX_PAGES; page += 1) {
    const res = await cloudSyncApi(token, 'GET', `/gists?per_page=100&page=${page}`);
    if (!res.ok) return res;
    const list = Array.isArray(res.data) ? res.data : [];
    const hit = cloudSyncPickGist(list);
    if (hit) return { ok: true, gist: hit };
    if (list.length < 100) break;
  }
  return { ok: true, gist: null };
}

/** The file text of a gist API object; follows raw_url when GitHub truncated a large file. */
async function cloudSyncReadGistContent(token, gist) {
  const file = gist && gist.files ? gist.files[CLOUD_SYNC_FILE] : null;
  if (!file) return { ok: true, content: null };
  if (file.truncated && typeof file.raw_url === 'string') {
    const raw = await cloudSyncApi(token, 'GET', file.raw_url);
    if (!raw.ok) return raw;
    return { ok: true, content: String(raw.data) };
  }
  return { ok: true, content: typeof file.content === 'string' ? file.content : null };
}

/**
 * Looks up the remote copy. Resolves
 * { ok, gistId|'', content|null, etag, unchanged } or { ok:false, error }.
 */
async function cloudSyncFetchRemote(state) {
  let gistId = state.gistId;
  if (gistId) {
    const res = await cloudSyncApi(state.token, 'GET', `/gists/${encodeURIComponent(gistId)}`, undefined,
      state.lastRemoteEtag ? { 'If-None-Match': state.lastRemoteEtag } : undefined);
    if (res.ok && res.notModified) return { ok: true, gistId, content: null, etag: state.lastRemoteEtag, unchanged: true };
    if (res.ok) {
      const read = await cloudSyncReadGistContent(state.token, res.data);
      if (!read.ok) return read;
      return { ok: true, gistId, content: read.content, etag: res.etag || '', unchanged: false };
    }
    if (res.status !== 404) return res;
    gistId = ''; // the gist was deleted: look for another one, else create a new one
  }
  const found = await cloudSyncFindGist(state.token);
  if (!found.ok) return found;
  if (!found.gist) return { ok: true, gistId: '', content: null, etag: '', unchanged: false };
  const full = await cloudSyncApi(state.token, 'GET', `/gists/${encodeURIComponent(found.gist.id)}`);
  if (!full.ok) return full;
  const read = await cloudSyncReadGistContent(state.token, full.data);
  if (!read.ok) return read;
  return { ok: true, gistId: found.gist.id, content: read.content, etag: full.etag || '', unchanged: false };
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
  cloudSyncSetError(error.text);
  if (error.retry) cloudSyncScheduleBackoff();
  return { ok: false, error: error.text, kind: error.kind, retry: !!error.retry, keptPending: startSeqKept !== false };
}

async function cloudSyncRunOnce(reason) {
  const state = cloudSyncLoad();
  if (!state.token) return { ok: false, skipped: 'disconnected' };
  if (typeof navigator !== 'undefined' && navigator.onLine === false) {
    return cloudSyncFail({ kind: 'offline', text: CLOUD_SYNC_MESSAGES.offline, retry: false });
  }
  if (!cloudSyncAcquireLock()) {
    // Another tab is syncing; it works on the same shared data. Check back for anything marked meanwhile.
    cloudSyncScheduleRetry(CLOUD_SYNC_LOCKED_RETRY_MS, 'locked-retry');
    return { ok: false, skipped: 'locked' };
  }
  cloudSyncRunning = true;
  cloudSyncNotify();
  try {
    const startSeq = state.dirtySeq;
    const remote = await cloudSyncFetchRemote(state);
    if (!remote.ok) {
      if (remote.status === 401) cloudSyncClearTimers();
      return cloudSyncFail(remote.error);
    }

    let remoteSignature = '';
    let changedLocally = false;
    if (remote.content !== null && remote.content !== undefined && String(remote.content).trim() !== '') {
      let parsed;
      try { parsed = JSON.parse(remote.content); } catch (_) { parsed = null; }
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return cloudSyncFail({ kind: 'remoteInvalid', text: CLOUD_SYNC_MESSAGES.remoteInvalid, retry: false });
      remoteSignature = cloudSyncSignature(parsed);
      const local = buildUserBackupSnapshot({ skipMetadata: true });
      const before = cloudSyncSignature(local);
      if (typeof snapshotTake === 'function') {
        try { await snapshotTake('before-sync', { skipIfEmpty: true }); } catch (_) { /* snapshots never block syncing */ }
      }
      if (typeof gkDataLoaded === 'function' && typeof ensureGkData === 'function' && !gkDataLoaded()) {
        let ok = false;
        try { ok = await ensureGkData(); } catch (_) { ok = false; }
        if (!ok) return cloudSyncFail({ kind: 'mergeFailed', text: CLOUD_SYNC_MESSAGES.mergeFailed, retry: true });
      }
      const result = applyUserDataBackup(cloudSyncPrepareRemote(parsed, local), 'merge');
      if (!result || !result.success) return cloudSyncFail({ kind: 'mergeFailed', text: CLOUD_SYNC_MESSAGES.mergeFailed, retry: false });
      changedLocally = cloudSyncSignature(buildUserBackupSnapshot({ skipMetadata: true })) !== before;
    } else if (remote.unchanged) {
      remoteSignature = null; // 304: the remote is what we last wrote or merged
    }

    const merged = buildUserBackupSnapshot({ skipMetadata: true });
    const needsPush = remote.unchanged ? cloudSyncPending(cloudSyncLoad())
      : (remoteSignature === '' || remoteSignature !== cloudSyncSignature(merged));
    let etag = remote.etag;
    let gistId = remote.gistId;
    if (needsPush) {
      const content = JSON.stringify(merged);
      if (content.length > CLOUD_SYNC_MAX_BYTES) return cloudSyncFail({ kind: 'tooLarge', text: CLOUD_SYNC_MESSAGES.tooLarge, retry: false });
      if (state.token && content.indexOf(state.token) >= 0) return cloudSyncFail({ kind: 'tokenLeak', text: CLOUD_SYNC_MESSAGES.tokenLeak, retry: false });
      const pushed = await cloudSyncPush(state, gistId, content);
      if (!pushed.ok) return cloudSyncFail(pushed.error);
      etag = pushed.etag || '';
      if (pushed.data && typeof pushed.data.id === 'string') gistId = pushed.data.id;
    }
    cloudSyncUpdate(current => Object.assign({}, current, {
      gistId: gistId || current.gistId,
      lastRemoteEtag: etag || '',
      lastSyncAt: Date.now(),
      syncedSeq: Math.max(current.syncedSeq, startSeq),
    }));
    cloudSyncRetryCount = 0;
    cloudSyncSetError('');
    if (changedLocally) cloudSyncRefreshUi();
    return { ok: true, pushed: needsPush, merged: changedLocally, reason };
  } catch (_) {
    return cloudSyncFail({ kind: 'http', text: CLOUD_SYNC_MESSAGES.http, retry: true });
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
  if (!cloudSyncSave({ token, gistId: '', lastSyncAt: 0, lastRemoteEtag: '', dirtySeq: 0, syncedSeq: 0 })) {
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
    if (store) { store.removeItem(CLOUD_SYNC_KEY); store.removeItem(CLOUD_SYNC_LOCK_KEY); }
  } catch (_) { /* ignore */ }
  if (!(options && options.keepError)) cloudSyncError = '';
  cloudSyncNotify();
}

function cloudSyncNow() {
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
    cloudSyncConnect, cloudSyncDisconnect, cloudSyncNow, cloudSyncMarkDirty, cloudSyncInit, cloudSyncRun,
  };
}
