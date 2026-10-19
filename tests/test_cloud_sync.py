# -*- coding: utf-8 -*-
"""v1.6.0 cloud sync (GitHub Gist): every test runs the real stores in node vm contexts against a mocked GitHub API.

No real token and no network: `fetch` is an in-memory fake shared by two simulated devices.
"""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    "dashboard-data.js",
    "national-exams-data.js",
    "src/data/knowledge-dag.js",
    "src/data/questionPoints.generated.js",
    "src/data/targetAllocation.generated.js",
    "src/data/dailySchedule.generated.js",
    "src/domain/studyPlan.js",
    "src/state/practiceStore.js",
    "src/state/sm2Store.js",
    "src/state/snapshotStore.js",
    "src/state/resultCardStore.js",
    "src/state/cloudSync.js",
    "src/components/todayTask.js",
]

HARNESS = r'''
const fs = require('fs'), vm = require('vm');
const sources = JSON.parse(process.argv[1]);
const FAKE_TOKEN = 'ghp_FAKEFAKEFAKEFAKEFAKEFAKEFAKE0001';
const FAKE_TOKEN_2 = 'ghp_FAKEFAKEFAKEFAKEFAKEFAKEFAKE0002';

function makeServer() {
  const server = { gists: [], calls: [], offline: false, failStatus: 0, validTokens: [FAKE_TOKEN, FAKE_TOKEN_2], seq: 0 };
  server.fetchFor = (device) => async (url, init) => {
    init = init || {};
    const u = new URL(url);
    const method = init.method || 'GET';
    const auth = (init.headers || {}).Authorization || '';
    server.calls.push({ device: device.name, method, path: u.pathname + u.search, auth, ifNoneMatch: (init.headers || {})['If-None-Match'] || '' });
    if (server.offline) throw new TypeError('Failed to fetch');
    const respond = (status, body, headers) => ({
      ok: status >= 200 && status < 300, status,
      headers: { get: k => Object.assign({}, headers || {}, server.contentLength ? { 'content-length': server.contentLength } : {})[String(k).toLowerCase()] || null },
      json: async () => JSON.parse(JSON.stringify(body)), text: async () => String(body),
    });
    if (server.failStatus) return respond(server.failStatus, { message: 'x' });
    if (!server.validTokens.some(t => auth === 'Bearer ' + t)) return respond(401, { message: 'Bad credentials' });
    const body = init.body ? JSON.parse(init.body) : null;
    const etagOf = g => 'W/"' + g.id + '-' + g.version + '"';
    const listView = g => ({ id: g.id, description: g.description, public: g.public, created_at: g.created_at, updated_at: g.updated_at || new Date(Date.UTC(2026, 9, 20, 13, 0, g.version)).toISOString(),
      files: Object.fromEntries(Object.keys(g.files).map(n => [n, { filename: n, size: g.files[n].content.length }])) });
    if (u.pathname === '/gists' && method === 'GET') {
      const per = Number(u.searchParams.get('per_page')) || 30, page = Number(u.searchParams.get('page')) || 1;
      return respond(200, server.gists.slice((page - 1) * per, page * per).map(listView));
    }
    if (u.pathname === '/gists' && method === 'POST') {
      server.seq += 1;
      const g = { id: 'gist' + server.seq, description: body.description, public: body.public, version: 1,
        created_at: new Date(Date.UTC(2026, 9, 20, 12, 0, server.seq)).toISOString(), files: body.files };
      server.gists.push(g);
      const out = respond(201, JSON.parse(JSON.stringify(g)), { etag: etagOf(g) });
      if (server.afterPost) server.afterPost(g);
      return out;
    }
    const m = u.pathname.match(/^\/gists\/([^/]+)$/);
    const g = m ? server.gists.find(x => x.id === m[1]) : null;
    if (!g) return respond(404, { message: 'Not Found' });
    if (method === 'GET') {
      if ((init.headers || {})['If-None-Match'] === etagOf(g)) return respond(304, {});
      return respond(200, g, { etag: etagOf(g) });
    }
    if (method === 'PATCH') {
      Object.assign(g.files, body.files);
      g.version += 1;
      const out = respond(200, JSON.parse(JSON.stringify(g)), { etag: etagOf(g) });
      if (server.afterPatch) server.afterPatch(g);
      return out;
    }
    return respond(405, {});
  };
  return server;
}

function makeDevice(server, name) {
  const data = {};
  const timers = [];
  let tid = 0;
  const localStorage = {
    getItem: k => Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null,
    setItem: (k, v) => { data[k] = String(v); },
    removeItem: k => { delete data[k]; },
  };
  const device = { name, data, timers };
  const ctx = {
    console: { log() {}, warn() {}, error() {} }, localStorage, currentExamCategory: 'PE', progressState: {}, starredState: {}, recallState: {},
    getManualTopicLabels: () => ({}), navigator: { onLine: true },
    setTimeout: (fn, ms) => {
      if (ms <= 100) { if (device.onShortDelay) device.onShortDelay(); setImmediate(fn); return 0; } // lock confirmation delay
      const id = ++tid; timers.push({ id, fn, ms }); return id;
    },
    clearTimeout: id => { const i = timers.findIndex(t => t.id === id); if (i >= 0) timers.splice(i, 1); },
  };
  ctx.fetch = server.fetchFor(device);
  vm.createContext(ctx);
  for (const file of sources) vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
  device.ctx = ctx;
  device.eval = expr => vm.runInContext(expr, ctx);
  device.records = () => (JSON.parse(data.EE_EXAM_RESULT_CARD_V1 || '{"records":[]}').records || []).map(r => r.id).sort();
  device.setRecords = (ids, qid, note) => {
    data.EE_EXAM_RESULT_CARD_V1 = JSON.stringify({ version: 1, records: ids.map(id => ({ id, qid: qid || 'EE-114-01-2', at: 1, source: 'today', tier: 'main',
      parts: [{ label: '整題', points: 20, mark: 'o' }], errors: [], note: note || '', total: 20, estimate: 20 })) });
  };
  device.fireTimers = async () => {
    const due = timers.splice(0);
    for (const t of due) await t.fn();
    for (let i = 0; i < 20; i++) { const pending = vm.runInContext('cloudSyncInFlight', ctx); if (!pending) break; await pending; await new Promise(r => setImmediate(r)); }
  };
  device.cloud = () => JSON.parse(data.EE_EXAM_CLOUD_SYNC_V1 || 'null');
  return device;
}
const server = makeServer();
const d1 = makeDevice(server, 'phone');
const d2 = makeDevice(server, 'pc');
const gistRecords = () => JSON.parse(server.gists[0].files['ee-exam-progress.json'].content).resultCard.records.map(r => r.id).sort();
const count = (method, device) => server.calls.filter(c => c.method === method && (!device || c.device === device)).length;
'''


def run_scenario(body, sources=None):
    """Runs `body` (an async JS function body returning JSON) with the harness; returns the parsed result."""
    script = HARNESS + "\n(async () => {\n" + body + "\n})().then(r => process.stdout.write('@@' + JSON.stringify(r)))" \
        ".catch(e => { console.error(e); process.exit(1); });"
    done = subprocess.run(["node", "-e", script, json.dumps(sources or SOURCES)], cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.split("@@", 1)[1])


class TestFirstTimeCreate(unittest.TestCase):
    def test_creates_one_secret_gist_with_progress_file(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
const res = await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const g = server.gists[0];
return { res, n: server.gists.length, pub: g.public, desc: g.description, files: Object.keys(g.files),
  posts: count('POST'), schema: JSON.parse(g.files['ee-exam-progress.json'].content).schema,
  ids: gistRecords(), cloud: d1.cloud(), status: await d1.eval('cloudSyncStatusNow().text'),
  auth: server.calls.every(c => c.auth === 'Bearer ' + FAKE_TOKEN) };
''')
        self.assertTrue(out["res"]["ok"])
        self.assertEqual(out["n"], 1)
        self.assertEqual(out["posts"], 1)
        self.assertIs(out["pub"], False)
        self.assertEqual(out["desc"], "ee-exam-workbench-progress-v1")
        self.assertEqual(out["files"], ["ee-exam-progress.json"])
        self.assertEqual(out["schema"], "ee-exam-user-backup")
        self.assertEqual(out["ids"], ["a"])
        self.assertEqual(out["cloud"]["gistId"], "gist1")
        self.assertTrue(out["status"].startswith("上次同步："))
        self.assertTrue(out["auth"])


class TestSecondDeviceAndMerge(unittest.TestCase):
    def test_second_device_finds_gist_merges_then_pushes(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d2.setRecords(['b']);
const before = server.calls.length;
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const seq = server.calls.slice(before).map(c => c.method + ' ' + c.path.split('?')[0]);
const snaps = JSON.parse(d2.data.EE_EXAM_SNAPSHOTS_V1 || '[]');
return { seq, gists: server.gists.length, posts: count('POST'), local: d2.records(), remote: gistRecords(),
  snaps: snaps.map(s => ({ reason: s.reason, records: s.counts.records })) };
''')
        self.assertEqual(out["gists"], 1)
        self.assertEqual(out["posts"], 1, "the second device must not create another gist")
        # list -> read -> (merge happens locally) -> PATCH -> read back
        # (the final GET compares the gist after our write)
        self.assertEqual(out["seq"], ["GET /gists", "GET /gists/gist1", "PATCH /gists/gist1", "GET /gists/gist1"])
        self.assertEqual(out["local"], ["a", "b"])
        self.assertEqual(out["remote"], ["a", "b"])
        # the before-sync snapshot holds the data from before the merge (only 'b')
        self.assertEqual(out["snaps"], [{"reason": "before-sync", "records": 1}])

    def test_both_devices_end_with_both_cards(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.setRecords(['a']); await d1.eval('cloudSyncMarkDirty()'); await d1.fireTimers();
d2.setRecords(['b']); await d2.eval('cloudSyncMarkDirty()'); await d2.fireTimers();
await d1.eval('cloudSyncNow()');
return { d1: d1.records(), d2: d2.records(), remote: gistRecords() };
''')
        self.assertEqual(out["d1"], ["a", "b"])
        self.assertEqual(out["d2"], ["a", "b"])
        self.assertEqual(out["remote"], ["a", "b"])

    def test_nothing_changed_means_no_second_upload(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const patches = count('PATCH');
await d1.eval('cloudSyncNow()');
const last = server.calls[server.calls.length - 1];
return { patches, after: count('PATCH'), ifNoneMatch: last.ifNoneMatch };
''')
        self.assertEqual(out["after"], out["patches"])
        self.assertTrue(out["ifNoneMatch"])

    def test_newer_local_sm2_review_survives_older_remote(self):
        out = run_scenario(r'''
const q = 'EE-114-01-2';
const entry = day => ({ repetitions: 1, interval: 4, easeFactor: 2.5, lastReviewed: day, nextReviewDate: '2026-12-01' });
d1.data.EE_EXAM_SM2_SCHEDULE_V1 = JSON.stringify({ [q]: entry('2026-10-10') });
d1.eval('initSM2Store()');
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d2.data.EE_EXAM_SM2_SCHEDULE_V1 = JSON.stringify({ [q]: entry('2026-10-18') });
d2.eval('initSM2Store()');
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
await d1.eval('cloudSyncNow()');
return { d2: JSON.parse(d2.data.EE_EXAM_SM2_SCHEDULE_V1)[q].lastReviewed,
  d1: JSON.parse(d1.data.EE_EXAM_SM2_SCHEDULE_V1)[q].lastReviewed,
  remote: JSON.parse(server.gists[0].files['ee-exam-progress.json'].content).sm2Schedule[q].lastReviewed };
''')
        self.assertEqual(out, {"d2": "2026-10-18", "d1": "2026-10-18", "remote": "2026-10-18"})


class TestDebounceAndTriggers(unittest.TestCase):
    def test_changes_within_30_seconds_upload_once(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const patches = count('PATCH');
d1.setRecords(['a']);
for (let i = 0; i < 3; i++) await d1.eval('cloudSyncMarkDirty()');
const timersBefore = d1.timers.map(t => t.ms);
const pendingBefore = await d1.eval('cloudSyncPending()');
const patchesIdle = count('PATCH');
await d1.fireTimers();
return { timersBefore, pendingBefore, noUploadYet: patchesIdle === patches, uploaded: count('PATCH') - patches,
  pendingAfter: await d1.eval('cloudSyncPending()'), remote: gistRecords() };
''')
        self.assertEqual(out["timersBefore"], [30000])
        self.assertTrue(out["pendingBefore"])
        self.assertTrue(out["noUploadYet"])
        self.assertEqual(out["uploaded"], 1)
        self.assertFalse(out["pendingAfter"])
        self.assertEqual(out["remote"], ["a"])

    def test_sm2_review_marks_dirty_only_when_connected(self):
        out = run_scenario(r'''
await d1.eval("recordSM2Review('EE-114-01-2', 5)");
const idle = d1.timers.length;
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
await d2.eval("recordSM2Review('EE-114-01-2', 5)");
return { idle, timers: d2.timers.map(t => t.ms), pending: await d2.eval('cloudSyncPending()') };
''')
        self.assertEqual(out["idle"], 0)
        self.assertEqual(out["timers"], [30000])
        self.assertTrue(out["pending"])

    def test_today_task_save_marks_dirty(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.eval('saveTodayTaskState({ completed: {}, active: null })');
return { timers: d1.timers.map(t => t.ms) };
''')
        self.assertEqual(out["timers"], [30000])


class TestOfflineRetry(unittest.TestCase):
    def test_network_failure_keeps_pending_and_retries_with_backoff(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.setRecords(['a']);
await d1.eval('cloudSyncMarkDirty()');
server.offline = true;
await d1.fireTimers();
const failed = { status: await d1.eval('cloudSyncStatusNow().text'), pending: await d1.eval('cloudSyncPending()'), retry: d1.timers.map(t => t.ms) };
server.offline = false;
await d1.fireTimers();
return { failed, status: await d1.eval('cloudSyncStatusNow().text'), pending: await d1.eval('cloudSyncPending()'), remote: gistRecords() };
''')
        self.assertEqual(out["failed"]["status"], "無法連線到 GitHub，稍後自動重試。")
        self.assertTrue(out["failed"]["pending"])
        self.assertEqual(out["failed"]["retry"], [60000])
        self.assertTrue(out["status"].startswith("上次同步："))
        self.assertFalse(out["pending"])
        self.assertEqual(out["remote"], ["a"])

    def test_browser_offline_waits_for_the_online_event(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.setRecords(['a']);
await d1.eval('cloudSyncMarkDirty()');
d1.ctx.navigator.onLine = false;
const calls = server.calls.length;
await d1.fireTimers();
const offline = { status: await d1.eval('cloudSyncStatusNow().text'), pending: await d1.eval('cloudSyncPending()'), noRequest: server.calls.length === calls };
d1.ctx.navigator.onLine = true;
await d1.eval("cloudSyncRun('online')");
return { offline, pendingAfter: await d1.eval('cloudSyncPending()'), remote: gistRecords() };
''')
        self.assertEqual(out["offline"], {"status": "目前離線，稍後自動重試。", "pending": True, "noRequest": True})
        self.assertFalse(out["pendingAfter"])
        self.assertEqual(out["remote"], ["a"])


class TestTokenStaysLocal(unittest.TestCase):
    def test_token_is_in_no_backup_snapshot_or_gist(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("recordSM2Review('EE-114-01-2', 5)");
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
await d1.eval('cloudSyncMarkDirty()'); await d1.fireTimers();
await d1.eval("snapshotTake('daily')");
const T = FAKE_TOKEN;
const inKeys = Object.keys(d1.data).filter(k => d1.data[k].includes(T));
return {
  inKeys,
  snapshot: JSON.stringify(await d1.eval('buildUserBackupSnapshot()')).includes(T),
  exported: (await d1.eval('exportAllUserDataJSON()')).includes(T),
  captured: JSON.stringify(await d1.eval("snapshotCapture('daily')")).includes(T),
  stored: (d1.data.EE_EXAM_SNAPSHOTS_V1 || '').includes(T),
  gist: server.gists.some(g => JSON.stringify(g).includes(T)),
  errorText: (await d1.eval('cloudSyncStatusNow().text')).includes(T),
};
''')
        self.assertEqual(out["inKeys"], ["EE_EXAM_CLOUD_SYNC_V1"])
        for key in ("snapshot", "exported", "captured", "stored", "gist", "errorText"):
            self.assertFalse(out[key], key)

    def test_upload_is_refused_when_content_would_contain_the_token(self):
        out = run_scenario(r'''
d1.setRecords(['a'], 'EE-114-01-2', FAKE_TOKEN);
const res = await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
return { res, gists: server.gists.length, text: await d1.eval('cloudSyncStatusNow().text') };
''')
        self.assertFalse(out["res"]["ok"])
        self.assertEqual(out["gists"], 0)
        self.assertEqual(out["text"], "同步內容含有權杖，已中止上傳。")

    def test_disconnect_deletes_the_local_token_but_not_the_gist(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.eval('cloudSyncDisconnect()');
return { cloud: d1.cloud(), gists: server.gists.length, status: await d1.eval('cloudSyncStatusNow().text'), connected: await d1.eval('cloudSyncConnected()') };
''')
        self.assertIsNone(out["cloud"])
        self.assertEqual(out["gists"], 1)
        self.assertEqual(out["status"], "")
        self.assertFalse(out["connected"])


class TestErrorStatus(unittest.TestCase):
    def test_rejected_token_is_not_kept_and_shows_one_error_line(self):
        out = run_scenario(r'''
server.validTokens = [];
const res = await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
return { res, cloud: d1.cloud(), text: await d1.eval('cloudSyncStatusNow().text'), timers: d1.timers.length };
''')
        self.assertFalse(out["res"]["ok"])
        self.assertIsNone(out["cloud"])
        self.assertEqual(out["text"], "權杖無效或已被撤銷，請重新連線。")
        self.assertEqual(out["timers"], 0)

    def test_malformed_token_makes_no_request(self):
        out = run_scenario(r'''
const res = await d1.eval("cloudSyncConnect('bad token')");
return { res, calls: server.calls.length, cloud: d1.cloud(), text: await d1.eval('cloudSyncStatusNow().text') };
''')
        self.assertFalse(out["res"]["ok"])
        self.assertEqual(out["calls"], 0)
        self.assertIsNone(out["cloud"])

    def test_forbidden_and_server_errors_use_fixed_texts(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
server.failStatus = 403;
await d1.eval('cloudSyncNow()');
const forbidden = await d1.eval('cloudSyncStatusNow().text');
server.failStatus = 503;
await d1.eval('cloudSyncNow()');
return { forbidden, server: await d1.eval('cloudSyncStatusNow().text'), retry: d1.timers.map(t => t.ms), stillConnected: await d1.eval('cloudSyncConnected()') };
''')
        self.assertEqual(out["forbidden"], "權杖權限不足（需要 gist 權限）或已達 GitHub 使用上限。")
        self.assertEqual(out["server"], "GitHub 暫時無法使用，稍後自動重試。")
        self.assertEqual(out["retry"], [60000])
        self.assertTrue(out["stillConnected"])

    def test_unreadable_remote_is_not_overwritten(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
server.gists[0].files['ee-exam-progress.json'].content = 'not json';
server.gists[0].version += 1;
d1.setRecords(['a']);
await d1.eval('cloudSyncNow()');
return { text: await d1.eval('cloudSyncStatusNow().text'), content: server.gists[0].files['ee-exam-progress.json'].content };
''')
        self.assertEqual(out["text"], "雲端進度格式無法讀取，未上傳。")
        self.assertEqual(out["content"], "not json")

    def test_other_tab_holding_the_lock_skips_this_run(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.data.EE_EXAM_CLOUD_SYNC_LOCK_V1 = JSON.stringify({ owner: 'tab-other', until: Date.now() + 60000 });
const calls = server.calls.length;
const res = await d1.eval("cloudSyncRun('manual')");
return { res, noRequest: server.calls.length === calls, retry: d1.timers.map(t => t.ms) };
''')
        self.assertEqual(out["res"]["skipped"], "locked")
        self.assertTrue(out["noRequest"])
        self.assertEqual(out["retry"], [15000])


# Question ids that exist in the bundled data (PE).
QIDS_JS = "const Q = d1.eval('DB_DATA.questions.slice(0, 5).map(q => q[0])');"
RECALL_JS = "const R = level => ({ level, streak: 0, attempts: 1, lastAchieved: 1, lastErrorType: null, lastReviewed: null });"


class TestThreeWayMerge(unittest.TestCase):
    def test_local_edits_and_deletions_survive_a_stale_cloud_copy(self):
        out = run_scenario(QIDS_JS + RECALL_JS + r'''
const put = (d, o) => {
  if (o.progress) d.data.EE_EXAM_PROGRESS_V1 = JSON.stringify(o.progress);
  if (o.starred) d.data.EE_EXAM_STARRED_V1 = JSON.stringify(o.starred);
  if (o.recall) d.eval('recallState = ' + JSON.stringify(o.recall));
  if (o.done) d.eval('saveDailyPracticeStore(' + JSON.stringify({ version: 1, completionByQuestion: o.done, activeSession: null }) + ').ok');
};
const get = d => ({
  progress: JSON.parse(d.data.EE_EXAM_PROGRESS_V1 || '{}'), starred: JSON.parse(d.data.EE_EXAM_STARRED_V1 || '{}'),
  recall: d.eval('JSON.parse(JSON.stringify(recallState))'), done: JSON.parse(d.data.EE_EXAM_DAILY_PRACTICE_V1 || '{}').completionByQuestion,
});
const cloud = () => { const j = JSON.parse(server.gists[0].files['ee-exam-progress.json'].content);
  return { progress: j.progressByCategory.PE, starred: j.starredByCategory.PE, recall: j.recallState, done: j.dailyPractice.completionByQuestion }; };
const [q1, q2, q3] = Q;
put(d1, { progress: { [q1]: 1, [q2]: 1 }, starred: { [q1]: true, [q2]: true }, recall: { [q1]: R(1), [q2]: R(1) }, done: { [q1]: 1000, [q2]: 1000 } });
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
// Device 1 edits (change q1, delete q2) but has not synced yet.
put(d1, { progress: { [q1]: 2 }, starred: { [q1]: false }, recall: { [q1]: R(3) }, done: { [q1]: 2000 } });
// Device 2 syncs an unrelated change (q3) while the cloud still holds the old q1 / q2 values.
put(d2, { progress: { [q1]: 1, [q2]: 1, [q3]: 1 } });
await d2.eval('cloudSyncMarkDirty()');
await d2.eval('cloudSyncNow()');
await d1.eval('cloudSyncMarkDirty()');
await d1.eval('cloudSyncNow()');
return { q1, q2, q3, d1: get(d1), cloud: cloud() };
''')
        q1, q2, q3 = out["q1"], out["q2"], out["q3"]
        for label, got in (("device 1", out["d1"]), ("cloud", out["cloud"])):
            self.assertEqual(got["progress"].get(q1), 2, label + " progress edit survives")
            self.assertNotIn(q2, got["progress"], label + " progress deletion wins")
            self.assertEqual(got["progress"].get(q3), 1, label + " keeps the other device's change")
            self.assertIs(got["starred"].get(q1), False, label + " starred edit survives")
            self.assertNotIn(q2, got["starred"], label + " starred deletion wins")
            self.assertEqual(got["recall"][q1]["level"], 3, label + " recall edit survives")
            self.assertNotIn(q2, got["recall"], label + " recall deletion wins")
            self.assertEqual(got["done"][q1], 2000, label + " daily practice completion edit survives")
            self.assertNotIn(q2, got["done"], label + " daily practice deletion wins")

    def test_pure_prepare_covers_every_map_including_manual_labels(self):
        out = run_scenario(r'''
const base = { progressByCategory: { PE: { a: 1, b: 1 }, GK: {} }, starredByCategory: { PE: { a: true }, GK: {} },
  recallState: { a: { level: 1 } }, manualTopicLabels: { a: { chapterId: 'c1' }, b: { chapterId: 'c1' } }, completionByQuestion: { a: 1 } };
const local = { progressByCategory: { PE: { a: 2, b: 1, n: 1 }, GK: {} }, starredByCategory: { PE: { a: true }, GK: {} },
  recallState: { a: { level: 1 } }, manualTopicLabels: { a: { chapterId: 'c2' } }, dailyPractice: { completionByQuestion: { a: 1 } } };
const remote = { progressByCategory: { PE: { a: 1, b: 5, n: 9, r: 1 }, GK: {} }, starredByCategory: { PE: { a: false, z: true }, GK: {} },
  recallState: { a: { level: 4 } }, manualTopicLabels: { a: { chapterId: 'c9' }, b: { chapterId: 'c9' }, x: { chapterId: 'c9' } },
  dailyPractice: { completionByQuestion: { a: 7 }, activeSession: null } };
const out = d1.eval('cloudSyncPrepareRemote(' + JSON.stringify(remote) + ',' + JSON.stringify(local) + ',' + JSON.stringify(base) + ')');
const noBase = d1.eval('cloudSyncPrepareRemote(' + JSON.stringify(remote) + ',' + JSON.stringify(local) + ', null)');
return { out, noBase };
''')
        out_ = out["out"]
        self.assertEqual(out_["progressByCategory"]["PE"], {"b": 5, "r": 1})  # a changed locally, n added locally
        self.assertEqual(out_["starredByCategory"]["PE"], {"a": False, "z": True})  # a unchanged locally: the cloud value may apply
        self.assertEqual(out_["recallState"], {"a": {"level": 4}})
        self.assertEqual(out_["manualTopicLabels"], {"x": {"chapterId": "c9"}})  # a edited locally, b deleted locally
        self.assertEqual(out_["dailyPractice"]["completionByQuestion"], {"a": 7})
        self.assertEqual(out["noBase"]["progressByCategory"]["PE"], {"a": 1, "b": 5, "n": 9, "r": 1}, "no base: plain merge")

    def test_base_is_stored_apart_and_never_uploaded(self):
        out = run_scenario(QIDS_JS + r'''
d1.data.EE_EXAM_PROGRESS_V1 = JSON.stringify({ [Q[0]]: 1 });
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const base = JSON.parse(d1.data.EE_EXAM_CLOUD_SYNC_BASE_V1 || 'null');
const inGist = JSON.stringify(server.gists).includes('EE_EXAM_CLOUD_SYNC_BASE');
const inBackup = (await d1.eval('exportAllUserDataJSON()')).includes('completionByQuestion') && JSON.stringify(await d1.eval('buildUserBackupSnapshot()')).includes('"base"');
d1.eval('cloudSyncDisconnect()');
return { base, inGist, inBackup, left: d1.data.EE_EXAM_CLOUD_SYNC_BASE_V1 || null, q: Q[0] };
''')
        self.assertEqual(out["base"]["progressByCategory"]["PE"], {out["q"]: 1})
        self.assertFalse(out["inGist"])
        self.assertFalse(out["inBackup"])
        self.assertIsNone(out["left"])

    def test_progress_save_and_star_toggle_mark_dirty(self):
        out = run_scenario(r'''
const fs2 = require('fs');
d1.eval(fs2.readFileSync('src/state/store.js', 'utf8').replace(/^let currentExamCategory[^\n]*\n/m, '').replace('reloadProgressState();\n', ''));
d1.ctx.document = { getElementById: () => null, createElement: () => ({ classList: { add() {}, remove() {} } }), body: { appendChild() {} } };
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.eval("progressState['EE-114-01-2'] = 1; saveProgress()");
const afterProgress = d1.timers.map(t => t.ms);
const seq1 = d1.cloud().dirtySeq;
d1.eval("toggleStarred('EE-114-01-2')");
return { afterProgress, grew: d1.cloud().dirtySeq > seq1 };
''')
        self.assertEqual(out["afterProgress"], [30000])
        self.assertTrue(out["grew"])


class TestForcePush(unittest.TestCase):
    def test_restore_or_replace_overwrites_the_cloud_instead_of_merging(self):
        out = run_scenario(r'''
d1.setRecords(['a', 'b']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
// Device 2 restores an older state that only has 'z'; connected, so the force flag is set.
d2.setRecords(['z']);
d2.eval('cloudSyncForcePush()');
const flagged = d2.cloud().forcePush;
await d2.eval('cloudSyncNow()');
return { flagged, after: d2.cloud().forcePush, cloud: gistRecords(), local: d2.records() };
''')
        self.assertTrue(out["flagged"])
        self.assertFalse(out["after"], "the flag is cleared once the push succeeded")
        self.assertEqual(out["cloud"], ["z"])
        self.assertEqual(out["local"], ["z"])

    def test_not_connected_sets_no_flag_and_header_uses_force_push(self):
        out = run_scenario("return { set: d1.eval('cloudSyncForcePush()'), key: d1.data.EE_EXAM_CLOUD_SYNC_V1 || null };")
        self.assertFalse(out["set"])
        self.assertIsNone(out["key"])
        header = (ROOT / "src/components/header.js").read_text(encoding="utf-8")
        self.assertIn("cloudSyncForcePush", header)
        self.assertEqual(header.count("cloudSyncForcePush()"), 2)  # snapshot restore + replace import


class TestDuplicateGists(unittest.TestCase):
    def test_existing_duplicates_are_merged_into_the_oldest_and_nothing_is_deleted(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
// A second gist with the same description appeared (newer) holding another card.
const content = JSON.parse(server.gists[0].files['ee-exam-progress.json'].content);
content.resultCard.records = [Object.assign({}, content.resultCard.records[0], { id: 'dup' })];
server.gists.push({ id: 'gistDup', description: 'ee-exam-workbench-progress-v1', public: false, version: 1, created_at: '2027-01-01T00:00:00.000Z',
  files: { 'ee-exam-progress.json': { content: JSON.stringify(content) } } });
d2.setRecords(['b']);
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const cloud = d2.cloud();
return { gists: server.gists.map(g => g.id), bound: cloud.gistId, local: d2.records(),
  remote: JSON.parse(server.gists[0].files['ee-exam-progress.json'].content).resultCard.records.map(r => r.id).sort(), posts: count('POST') };
''')
        self.assertEqual(out["gists"], ["gist1", "gistDup"])
        self.assertEqual(out["bound"], "gist1")
        self.assertEqual(out["posts"], 1)
        self.assertEqual(out["local"], ["a", "b", "dup"])
        self.assertEqual(out["remote"], ["a", "b", "dup"])

    def test_bound_device_checks_for_duplicates_once_per_app_start(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const lists = () => server.calls.filter(c => c.method === 'GET' && c.path.startsWith('/gists?')).length;
const start = lists();
await d1.eval('cloudSyncNow()'); await d1.eval('cloudSyncNow()');
return { extra: lists() - start };
''')
        self.assertEqual(out["extra"], 0, "the connect run already listed; later syncs do not list again")

    def test_gist_created_by_a_race_is_rebound_to_the_oldest_after_post(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
server.afterPost = () => {
  server.afterPost = null;
  const other = JSON.parse(JSON.stringify(JSON.parse(server.gists[0].files['ee-exam-progress.json'].content)));
  other.resultCard.records = [Object.assign({}, other.resultCard.records[0], { id: 'raced' })];
  server.gists.unshift({ id: 'gistOld', description: 'ee-exam-workbench-progress-v1', public: false, version: 1, created_at: '2026-01-01T00:00:00.000Z',
    files: { 'ee-exam-progress.json': { content: JSON.stringify(other) } } });
};
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const old = server.gists.find(g => g.id === 'gistOld');
return { gists: server.gists.map(g => g.id), bound: d1.cloud().gistId, local: d1.records(),
  oldRecords: JSON.parse(old.files['ee-exam-progress.json'].content).resultCard.records.map(r => r.id).sort() };
''')
        self.assertEqual(out["gists"], ["gistOld", "gist1"])
        self.assertEqual(out["bound"], "gistOld")
        self.assertEqual(out["oldRecords"], ["a", "raced"])
        self.assertEqual(out["local"], ["a", "raced"])

    def test_match_beyond_the_first_page_is_found_not_duplicated(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
for (let i = 0; i < 100; i++) server.gists.unshift({ id: 'f' + i, description: 'other', public: false, version: 1, created_at: '2026-01-01T00:00:00.000Z', files: { 'x.txt': { content: 'x' } } });
d2.setRecords(['b']);
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
return { posts: count('POST'), bound: d2.cloud().gistId, local: d2.records() };
''')
        self.assertEqual(out["posts"], 1)
        self.assertEqual(out["bound"], "gist1")
        self.assertEqual(out["local"], ["a", "b"])

    def test_lock_is_confirmed_after_a_short_delay_and_lost_when_another_tab_wins(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const stamps = [];
d1.onShortDelay = () => { stamps.push(JSON.parse(d1.data.EE_EXAM_CLOUD_SYNC_LOCK_V1)); };
await d1.eval("cloudSyncRun('manual')");
const won = { stamped: stamps.length, nonce: typeof stamps[0].nonce === 'string' && stamps[0].nonce.length >= 6, lockLeft: d1.data.EE_EXAM_CLOUD_SYNC_LOCK_V1 || null };
// Another tab overwrites the lock during the confirmation delay.
d1.onShortDelay = () => { d1.data.EE_EXAM_CLOUD_SYNC_LOCK_V1 = JSON.stringify({ owner: 'tab-other', nonce: 'zzz', until: Date.now() + 60000 }); };
const calls = server.calls.length;
const res = await d1.eval("cloudSyncRun('manual')");
return { won, res, noRequest: server.calls.length === calls, owner: JSON.parse(d1.data.EE_EXAM_CLOUD_SYNC_LOCK_V1).owner };
''')
        self.assertEqual(out["won"]["stamped"], 1)
        self.assertTrue(out["won"]["nonce"])
        self.assertIsNone(out["won"]["lockLeft"])
        self.assertEqual(out["res"]["skipped"], "locked")
        self.assertTrue(out["noRequest"])
        self.assertEqual(out["owner"], "tab-other", "the other tab's lock is not removed by us")


class TestWriteRace(unittest.TestCase):
    def test_another_device_writing_after_our_patch_triggers_one_more_merge_round(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.setRecords(['a', 'b']);
await d1.eval('cloudSyncMarkDirty()');
server.afterPatch = g => {
  server.afterPatch = null;
  const content = JSON.parse(g.files['ee-exam-progress.json'].content);
  content.resultCard.records = [Object.assign({}, content.resultCard.records[0], { id: 'c' })]; // the other device overwrote without merging
  g.files['ee-exam-progress.json'].content = JSON.stringify(content);
  g.version += 1;
};
const patches = count('PATCH');
await d1.eval('cloudSyncNow()');
return { patches: count('PATCH') - patches, local: d1.records(), remote: gistRecords() };
''')
        self.assertEqual(out["patches"], 2)
        self.assertEqual(out["local"], ["a", "b", "c"])
        self.assertEqual(out["remote"], ["a", "b", "c"])

    def test_at_most_one_extra_round(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.setRecords(['a', 'b']);
await d1.eval('cloudSyncMarkDirty()');
let n = 0;
server.afterPatch = g => {
  const content = JSON.parse(g.files['ee-exam-progress.json'].content);
  content.resultCard.records = [Object.assign({}, content.resultCard.records[0], { id: 'w' + (++n) })];
  g.files['ee-exam-progress.json'].content = JSON.stringify(content);
  g.version += 1;
};
const patches = count('PATCH');
const res = await d1.eval('cloudSyncNow()');
return { res, patches: count('PATCH') - patches };
''')
        self.assertTrue(out["res"]["ok"])
        self.assertEqual(out["patches"], 2)


class TestDownloadCap(unittest.TestCase):
    def test_oversized_gist_file_is_refused_before_reading(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
server.gists[0].files['ee-exam-progress.json'].size = 9 * 1024 * 1024;
server.gists[0].version += 1;
const patches = count('PATCH');
const res = await d1.eval('cloudSyncNow()');
return { res, text: await d1.eval('cloudSyncStatusNow().text'), patches: count('PATCH') - patches, timers: d1.timers.length };
''')
        self.assertFalse(out["res"]["ok"])
        self.assertEqual(out["res"]["kind"], "remoteTooLarge")
        self.assertEqual(out["text"], "雲端進度資料過大，已拒絕讀取。")
        self.assertEqual(out["patches"], 0)
        self.assertEqual(out["timers"], 0)

    def test_oversized_content_length_is_refused(self):
        out = run_scenario(r'''
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
server.gists[0].version += 1;
server.contentLength = String(9 * 1024 * 1024);
const res = await d1.eval('cloudSyncNow()');
return { res };
''')
        self.assertEqual(out["res"]["kind"], "remoteTooLarge")


class TestRetryPolicy(unittest.TestCase):
    def test_programming_errors_stop_retrying_after_three_attempts(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.setRecords(['a']);
d1.eval('var attempts = 0; buildUserBackupSnapshot = () => { attempts += 1; throw new Error("bug"); }');
await d1.eval('cloudSyncNow()');
const timersAfter1 = d1.timers.length;
await d1.fireTimers();
await d1.fireTimers();
return { attempts: d1.eval('attempts'), timersAfter1, timers: d1.timers.length, text: await d1.eval('cloudSyncStatusNow().text') };
''')
        self.assertEqual(out["attempts"], 3)
        self.assertEqual(out["timersAfter1"], 1)
        self.assertEqual(out["timers"], 0, "no retry timer after the third failure")
        self.assertEqual(out["text"], "同步失敗，請稍後再試。")

    def test_network_errors_keep_retrying_with_growing_backoff(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.setRecords(['a']);
server.offline = true;
const delays = [];
await d1.eval('cloudSyncNow()'); delays.push(d1.timers.map(t => t.ms)[0]);
for (let i = 0; i < 4; i++) { await d1.fireTimers(); delays.push(d1.timers.map(t => t.ms)[0]); }
return { delays };
''')
        self.assertEqual(out["delays"], [60000, 120000, 240000, 480000, 600000])

    def test_malformed_remote_is_not_retried_and_needs_a_confirmed_overwrite(self):
        out = run_scenario(r'''
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
server.gists[0].files['ee-exam-progress.json'].content = 'not json';
server.gists[0].version += 1;
d1.setRecords(['a']);
const res = await d1.eval('cloudSyncNow()');
const first = { kind: res.kind, timers: d1.timers.length, status: await d1.eval('cloudSyncStatusNow().kind'), content: server.gists[0].files['ee-exam-progress.json'].content };
const res2 = await d1.eval('cloudSyncNow({ overwrite: true })');
return { first, ok: res2.ok, remote: gistRecords(), status: await d1.eval('cloudSyncStatusNow().kind') };
''')
        self.assertEqual(out["first"]["kind"], "remoteInvalid")
        self.assertEqual(out["first"]["timers"], 0)
        self.assertEqual(out["first"]["status"], "remoteInvalid")
        self.assertEqual(out["first"]["content"], "not json")
        self.assertTrue(out["ok"])
        self.assertEqual(out["remote"], ["a"])
        self.assertEqual(out["status"], "")
        header = (ROOT / "src/components/header.js").read_text(encoding="utf-8")
        self.assertIn("雲端資料格式錯誤，要用本機進度覆寫雲端嗎？", header)


class TestPureHelpers(unittest.TestCase):
    def test_status_line_and_snapshot_retention(self):
        out = run_scenario(r'''
const when = new Date(2026, 9, 20, 21, 35).getTime();
const snap = (id, takenAt, reason) => ({ id, takenAt, day: takenAt.slice(0, 10), reason, counts: { records: 0, completed: 0, sm2: 0, recall: 0 } });
const list = [snap('s1', '2026-10-20T01:00:00.000Z', 'before-sync'), snap('s2', '2026-10-20T02:00:00.000Z', 'before-sync'),
  snap('s3', '2026-10-20T03:00:00.000Z', 'before-sync'), snap('i1', '2026-10-01T03:00:00.000Z', 'before-import')];
return {
  ok: d1.eval('cloudSyncStatusText({ token: "x", lastSyncAt: ' + when + ' }, "")'),
  none: d1.eval('cloudSyncStatusText({ token: "x", lastSyncAt: 0 }, "")'),
  err: d1.eval('cloudSyncStatusText({ token: "x", lastSyncAt: 1 }, "錯誤")'),
  off: d1.eval('cloudSyncStatusText({ token: "", lastSyncAt: 1 }, "")'),
  retained: d1.eval('snapshotRetain(' + JSON.stringify(list) + ')').sort(),
  label: d1.eval("snapshotKindLabel('before-sync')"),
};
''')
        self.assertEqual(out["ok"], "上次同步：10/20 21:35")
        self.assertEqual(out["none"], "上次同步：尚未同步")
        self.assertEqual(out["err"], "錯誤")
        self.assertEqual(out["off"], "")
        self.assertEqual(out["retained"], ["i1", "s2", "s3"])
        self.assertEqual(out["label"], "同步前")


if __name__ == "__main__":
    unittest.main()


ATTEMPT_SOURCES = [p for p in SOURCES if p != "src/state/cloudSync.js"] + [
    "src/state/store.js", "src/state/recallStore.js", "src/state/attemptStore.js", "src/state/cloudSync.js"]


class TestReReviewFixes(unittest.TestCase):
    def test_attempt_commit_marks_dirty_and_the_value_survives_a_stale_cloud(self):
        out = run_scenario(r"""
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const before = d1.cloud().dirtySeq;
const res = d1.eval("submitLearningAttempt({attemptId:'a1',question:{id:'EE-114-01-2',examFamily:'PE'},sourceMode:'due-review',rating:5,revealStep:4,recallEntry:true,errorType:null})");
const marked = d1.cloud().dirtySeq - before;
const cloudHas = () => !!JSON.parse(server.gists[0].files['ee-exam-progress.json'].content).recallState['EE-114-01-2'];
await d1.eval('cloudSyncNow()');
const pushed = cloudHas();
const mine = d1.eval("JSON.stringify(recallState['EE-114-01-2'])");
// another device rewrites the gist with the old value (no entry)
const old = JSON.parse(server.gists[0].files['ee-exam-progress.json'].content);
delete old.recallState['EE-114-01-2'];
server.gists[0].files['ee-exam-progress.json'].content = JSON.stringify(old); server.gists[0].version += 1;
await d1.eval('cloudSyncNow()');
return { ok: res.ok, marked, pushed, kept: d1.eval("JSON.stringify(recallState['EE-114-01-2'])") === mine, cloudKept: cloudHas() };
""", ATTEMPT_SOURCES)
        self.assertTrue(out["ok"])
        self.assertGreaterEqual(out["marked"], 1)
        self.assertTrue(out["pushed"])
        self.assertTrue(out["kept"])
        self.assertTrue(out["cloudKept"])

    def test_base_is_kept_when_no_push_happened(self):
        out = run_scenario(QIDS_JS + RECALL_JS + r"""
const [q1] = Q;
d1.eval('recallState = ' + JSON.stringify({ [q1]: R(1) }));
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const patches = count('PATCH');
// local edit without a dirty mark: the next sync gets 304 and must not adopt it as the base
d1.eval('recallState = ' + JSON.stringify({ [q1]: R(3) }));
await d1.eval('cloudSyncNow()');
const base = JSON.parse(d1.data.EE_EXAM_CLOUD_SYNC_BASE_V1).recallState;
return { base: base[q1] ? base[q1].level : null, noPatch: count('PATCH') === patches };
""")
        self.assertEqual(out["base"], 1)
        self.assertTrue(out["noPatch"])

    def test_merged_duplicate_gist_does_not_resurrect_deleted_data_after_restart(self):
        out = run_scenario(r"""
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const content = JSON.parse(server.gists[0].files['ee-exam-progress.json'].content);
content.resultCard.records = [Object.assign({}, content.resultCard.records[0], { id: 'dup' })];
server.gists.push({ id: 'gistDup', description: 'ee-exam-workbench-progress-v1', public: false, version: 1, created_at: '2027-01-01T00:00:00.000Z',
  files: { 'ee-exam-progress.json': { content: JSON.stringify(content) } } });
d2.setRecords(['b']);
await d2.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
const merged = d2.records();
// the user deletes 'dup' locally and syncs
d2.setRecords(['a', 'b']);
await d2.eval('cloudSyncMarkDirty()');
await d2.eval('cloudSyncNow()');
// restart: a fresh runtime on the same storage
const d3 = makeDevice(server, 'pc');
Object.assign(d3.data, d2.data);
await d3.eval('cloudSyncNow()');
return { merged, after: d3.records(), remote: gistRecords() };
""")
        self.assertEqual(out["merged"], ["a", "b", "dup"])
        self.assertEqual(out["after"], ["a", "b"])
        self.assertEqual(out["remote"], ["a", "b"])

    def test_self_created_gist_is_recorded_as_merged_after_post_race(self):
        out = run_scenario(r"""
d1.setRecords(['a']);
server.afterPost = () => {
  server.afterPost = null;
  const other = JSON.parse(server.gists[0].files['ee-exam-progress.json'].content);
  server.gists.unshift({ id: 'gistOld', description: 'ee-exam-workbench-progress-v1', public: false, version: 1, created_at: '2026-01-01T00:00:00.000Z',
    files: { 'ee-exam-progress.json': { content: JSON.stringify(other) } } });
};
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
return { merged: Object.keys(d1.cloud().mergedExtras || {}) };
""")
        self.assertIn("gist1", out["merged"])

    def test_sm2_without_last_reviewed_compares_next_review_date(self):
        out = run_scenario(r"""
const f = d1.eval('cloudSyncPrepareRemote');
const e = (last, next) => ({ repetitions: 0, interval: 1, easeFactor: 2.5, lastReviewed: last, nextReviewDate: next });
const run = (mine, theirs) => Object.keys(f({ sm2Schedule: { q: theirs } }, { sm2Schedule: { q: mine } }, null).sm2Schedule);
return { localLater: run(e(null, '2026-12-05'), e('2026-10-01', '2026-12-01')), remoteLater: run(e(null, '2026-11-01'), e('2026-10-01', '2026-12-01')),
  tie: run(e(null, '2026-12-01'), e('2026-10-01', '2026-12-01')), remoteNull: run(e('2026-10-01', '2026-11-01'), e(null, '2026-12-01')) };
""")
        self.assertEqual(out, {"localLater": [], "remoteLater": ["q"], "tie": [], "remoteNull": ["q"]})

    def test_force_push_set_during_a_round_is_not_cleared(self):
        out = run_scenario(r"""
d1.setRecords(['a']);
await d1.eval("cloudSyncConnect('" + FAKE_TOKEN + "')");
d1.eval('cloudSyncForcePush()');
server.afterPatch = () => { server.afterPatch = null; d1.eval('cloudSyncForcePush()'); };
await d1.eval('cloudSyncNow()');
const flagAfterFirst = d1.cloud().forcePush;
await d1.fireTimers();
await d1.eval('cloudSyncNow()');
return { flagAfterFirst, final: d1.cloud().forcePush };
""")
        self.assertTrue(out["flagAfterFirst"])
        self.assertFalse(out["final"])
