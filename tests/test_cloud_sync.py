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
      headers: { get: k => (headers || {})[String(k).toLowerCase()] || null },
      json: async () => JSON.parse(JSON.stringify(body)), text: async () => String(body),
    });
    if (server.failStatus) return respond(server.failStatus, { message: 'x' });
    if (!server.validTokens.some(t => auth === 'Bearer ' + t)) return respond(401, { message: 'Bad credentials' });
    const body = init.body ? JSON.parse(init.body) : null;
    const etagOf = g => 'W/"' + g.id + '-' + g.version + '"';
    const listView = g => ({ id: g.id, description: g.description, public: g.public, created_at: g.created_at,
      files: Object.fromEntries(Object.keys(g.files).map(n => [n, { filename: n, size: g.files[n].content.length }])) });
    if (u.pathname === '/gists' && method === 'GET') {
      return respond(200, server.gists.map(listView));
    }
    if (u.pathname === '/gists' && method === 'POST') {
      server.seq += 1;
      const g = { id: 'gist' + server.seq, description: body.description, public: body.public, version: 1,
        created_at: new Date(Date.UTC(2026, 9, 20, 12, 0, server.seq)).toISOString(), files: body.files };
      server.gists.push(g);
      return respond(201, g, { etag: etagOf(g) });
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
      return respond(200, g, { etag: etagOf(g) });
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
    setTimeout: (fn, ms) => { const id = ++tid; timers.push({ id, fn, ms }); return id; },
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


def run_scenario(body):
    """Runs `body` (an async JS function body returning JSON) with the harness; returns the parsed result."""
    script = HARNESS + "\n(async () => {\n" + body + "\n})().then(r => process.stdout.write('@@' + JSON.stringify(r)))" \
        ".catch(e => { console.error(e); process.exit(1); });"
    done = subprocess.run(["node", "-e", script, json.dumps(SOURCES)], cwd=ROOT, capture_output=True, text=True)
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
        # list -> read -> (merge happens locally) -> PATCH
        self.assertEqual(out["seq"], ["GET /gists", "GET /gists/gist1", "PATCH /gists/gist1"])
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
