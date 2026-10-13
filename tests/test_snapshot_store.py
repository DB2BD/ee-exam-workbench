# -*- coding: utf-8 -*-
"""v1.3.10 automatic snapshots: retention rules, daily trigger, localStorage fallback and restore round trip."""

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
    "src/state/resultCardStore.js",
    "src/state/snapshotStore.js",
]
RESULT_KEY = "EE_EXAM_RESULT_CARD_V1"
TASK_KEY = "EE_EXAM_TODAY_TASK_V1"
LS_KEY = "EE_EXAM_SNAPSHOTS_V1"


def record(rid, qid="EE-114-01-2", mark="o"):
    return {"id": rid, "qid": qid, "at": 1, "source": "today", "tier": "main",
            "parts": [{"label": "整題", "points": 20, "mark": mark}], "errors": [], "note": "", "total": 20, "estimate": 20}


def run_js(expression, storage=None, extra=""):
    """Runs an (async) JS expression inside a vm context with all store sources loaded."""
    script = r'''
const fs = require('fs'), vm = require('vm');
const sources = JSON.parse(process.argv[1]);
const data = JSON.parse(process.argv[3]);
const localStorage = {
  getItem: k => Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null,
  setItem: (k, v) => { data[k] = String(v); },
  removeItem: k => { delete data[k]; },
};
const ctx = { console, localStorage, setTimeout, currentExamCategory: 'PE', progressState: {}, starredState: {}, recallState: {}, getManualTopicLabels: () => ({}) };
vm.createContext(ctx);
for (const file of sources) vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
if (process.argv[4]) vm.runInContext(process.argv[4], ctx);
Promise.resolve(vm.runInContext('(async () => (' + process.argv[2] + '))()', ctx)).then(result => {
  process.stdout.write(JSON.stringify({ result, storage: data }));
}).catch(error => { console.error(error); process.exit(1); });
'''
    done = subprocess.run(
        ["node", "-e", script, json.dumps(SOURCES), expression, json.dumps(storage or {}, ensure_ascii=False), extra],
        cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.splitlines()[-1])  # data files log progress lines first


SEED_STORAGE = {
    RESULT_KEY: json.dumps({"version": 1, "records": [record("a"), record("b", "EE-114-01-3", "x")]}),
    TASK_KEY: json.dumps({"completed": {"CORE-01": "2026-10-12T10:00:00.000Z", "ZZZ-99": "2026-10-12T11:00:00.000Z"}, "active": None}),
}


class TestRetentionRules(unittest.TestCase):
    def retain(self, items):
        return run_js("snapshotRetain(%s)" % json.dumps(items))["result"]

    @staticmethod
    def snap(sid, takenAt, reason="daily", records=0, completed=0):
        return {"id": sid, "takenAt": takenAt, "day": takenAt[:10], "reason": reason,
                "counts": {"records": records, "completed": completed, "sm2": 0, "recall": 0}}

    def test_daily_keeps_newest_per_day_and_seven_days(self):
        items = []
        for day in range(1, 10):  # 9 distinct days, 1..9
            items.append(self.snap("d%d-early" % day, "2026-10-%02dT08:00:00.000" % day, records=day))
            items.append(self.snap("d%d-late" % day, "2026-10-%02dT20:00:00.000" % day, records=day))
        kept = self.retain(items)
        # Local day comes from `day`; the newest per day wins, only days 3..9 survive.
        self.assertEqual(sorted(kept), sorted("d%d-late" % d for d in range(3, 10)))

    def test_events_keep_newest_three_together(self):
        items = [self.snap("e%d" % i, "2026-10-%02dT09:00:00.000" % (i + 1), reason=("before-import" if i % 2 else "before-restore"), records=1)
                 for i in range(6)]
        self.assertEqual(sorted(self.retain(items)), ["e3", "e4", "e5"])

    def test_most_records_snapshot_is_never_dropped(self):
        old_best = self.snap("old-best", "2026-08-01T09:00:00.000", records=91, completed=23)
        items = [old_best] + [self.snap("d%d" % d, "2026-10-%02dT09:00:00.000" % d, records=2) for d in range(1, 10)]
        kept = self.retain(items)
        self.assertIn("old-best", kept)
        self.assertEqual(len(kept), 8)

    def test_best_tie_prefers_newer_and_event_can_be_best(self):
        a = self.snap("a", "2026-01-01T09:00:00.000", records=10)
        b = self.snap("b", "2026-02-01T09:00:00.000", records=10)
        self.assertEqual(self.retain([a, b]).count("b"), 1)
        ev_old = self.snap("ev-old", "2026-03-01T09:00:00.000", reason="before-import", records=50)
        newer = [self.snap("ev%d" % i, "2026-10-%02dT09:00:00.000" % (i + 1), reason="before-restore", records=1) for i in range(3)]
        kept = self.retain([ev_old] + newer)
        self.assertIn("ev-old", kept)
        self.assertEqual(len(kept), 4)

    def test_empty_and_garbage_input(self):
        self.assertEqual(self.retain([]), [])
        self.assertEqual(run_js("snapshotRetain(null)")["result"], [])

    def test_needs_daily(self):
        items = [self.snap("a", "2026-10-12T09:00:00.000", records=1), self.snap("e", "2026-10-13T09:00:00.000", reason="before-import")]
        self.assertTrue(run_js("snapshotNeedsDaily(%s, '2026-10-13')" % json.dumps(items))["result"])
        items.append(self.snap("b", "2026-10-13T10:00:00.000"))
        self.assertFalse(run_js("snapshotNeedsDaily(%s, '2026-10-13')" % json.dumps(items))["result"])
        self.assertTrue(run_js("snapshotNeedsDaily([], '2026-10-13')")["result"])

    def test_local_storage_cap_keeps_best_and_newest(self):
        items = [self.snap("best", "2026-08-01T09:00:00.000", reason="before-import", records=40),
                 self.snap("e1", "2026-10-10T09:00:00.000", reason="before-import", records=1),
                 self.snap("e2", "2026-10-11T09:00:00.000", reason="before-import", records=1)]
        self.assertEqual(sorted(run_js("snapshotCapLocal(%s, 2)" % json.dumps(items))["result"]), ["best", "e2"])

    def test_two_tap_confirm_step(self):
        out = run_js("[snapshotConfirmStep(null, 'a'), snapshotConfirmStep('a', 'a'), snapshotConfirmStep('a', 'b')]")["result"]
        self.assertEqual(out, [{"armed": "a", "run": False}, {"armed": None, "run": True}, {"armed": "b", "run": False}])


class TestCounts(unittest.TestCase):
    def test_completed_counts_only_scheduled_codes(self):
        out = run_js("snapshotCounts(JSON.parse(buildUserBackupSnapshot({skipMetadata:true}) && JSON.stringify(buildUserBackupSnapshot({skipMetadata:true}))))",
                     storage=SEED_STORAGE)["result"]
        self.assertEqual(out["records"], 2)
        self.assertEqual(out["completed"], 1)

    def test_empty_detection_ignores_recall(self):
        self.assertTrue(run_js("snapshotIsEmpty({records:0, completed:0, sm2:0, recall:5})")["result"])
        self.assertFalse(run_js("snapshotIsEmpty({records:0, completed:0, sm2:1, recall:0})")["result"])

    def test_snapshot_does_not_touch_backup_metadata(self):
        out = run_js("(() => { buildUserBackupSnapshot({skipMetadata:true}); return localStorage.getItem('EE_EXAM_BACKUP_META_V1'); })()")["result"]
        self.assertIsNone(out)
        out = run_js("(() => { buildUserBackupSnapshot(); return localStorage.getItem('EE_EXAM_BACKUP_META_V1') !== null; })()")["result"]
        self.assertTrue(out)


class TestTriggersAndStorage(unittest.TestCase):
    def test_daily_skips_empty_data(self):
        out = run_js("(async () => { const r = await snapshotRunDaily(); return { r, list: (await snapshotListMeta()).length, ls: localStorage.getItem('%s') }; })()" % LS_KEY)
        self.assertEqual(out["result"]["list"], 0)
        self.assertTrue(out["result"]["r"]["skipped"])
        self.assertIsNone(out["result"]["ls"])

    def test_daily_takes_one_per_day(self):
        out = run_js("""(async () => {
          const now = Date.parse('2026-10-13T09:00:00');
          const first = await snapshotRunDaily({ now });
          const second = await snapshotRunDaily({ now: now + 3600000 });
          const next = await snapshotRunDaily({ now: now + 86400000 });
          const list = await snapshotListMeta();
          return { first: first.ok, second: second.skipped === true, next: next.ok, days: list.map(m => m.day), reasons: list.map(m => m.reason), counts: list[0].counts };
        })()""", storage=SEED_STORAGE)["result"]
        self.assertTrue(out["first"])
        self.assertTrue(out["second"])
        self.assertTrue(out["next"])
        self.assertEqual(out["days"], ["2026-10-14", "2026-10-13"])
        self.assertEqual(out["reasons"], ["daily", "daily"])
        self.assertEqual(out["counts"]["records"], 2)
        self.assertEqual(out["counts"]["completed"], 1)

    def test_local_storage_fallback_keeps_at_most_two(self):
        out = run_js("""(async () => {
          for (let i = 0; i < 5; i++) await snapshotTake('before-import', { now: Date.parse('2026-10-1' + i + 'T09:00:00') });
          const stored = JSON.parse(localStorage.getItem('%s'));
          return { n: stored.length, takenAt: stored.map(s => s.takenAt).sort(), meta: (await snapshotListMeta()).length };
        })()""" % LS_KEY, storage=SEED_STORAGE)["result"]
        self.assertEqual(out["n"], 2)
        self.assertEqual(out["meta"], 2)

    def test_snapshot_failure_is_silent(self):
        out = run_js("""(async () => {
          localStorage.setItem = () => { throw new Error('quota'); };
          const r = await snapshotTake('before-import');
          const d = await snapshotRunDaily();
          return { r: r.ok, d: d.ok };
        })()""", storage=SEED_STORAGE)["result"]
        self.assertEqual(out, {"r": False, "d": False})

    def test_snapshot_is_not_in_backup_file(self):
        out = run_js("""(async () => {
          await snapshotTake('before-import');
          return JSON.stringify(buildUserBackupSnapshot()).indexOf('snap-') >= 0;
        })()""", storage=SEED_STORAGE)["result"]
        self.assertFalse(out)

    def test_restore_round_trip(self):
        out = run_js("""(async () => {
          const before = JSON.parse(localStorage.getItem('%(rc)s'));
          const taken = await snapshotTake('before-import');
          localStorage.setItem('%(rc)s', JSON.stringify({ version: 1, records: [] }));
          localStorage.setItem('%(task)s', JSON.stringify({ completed: {}, active: null }));
          const res = await snapshotRestore(taken.id);
          const after = JSON.parse(localStorage.getItem('%(rc)s'));
          const reasons = (await snapshotListMeta()).map(m => m.reason).sort();
          return { ok: res.success, error: res.error || null, before: before.records.map(r => r.id), after: after.records.map(r => r.id),
                   completed: Object.keys(JSON.parse(localStorage.getItem('%(task)s')).completed), reasons };
        })()""" % {"rc": RESULT_KEY, "task": TASK_KEY}, storage=SEED_STORAGE)["result"]
        self.assertTrue(out["ok"], out["error"])
        self.assertEqual(sorted(out["after"]), sorted(out["before"]))
        self.assertEqual(out["completed"], ["CORE-01", "ZZZ-99"])  # restore is a faithful round trip of what was stored
        self.assertEqual(out["reasons"], ["before-import", "before-restore"])

    def test_restore_missing_snapshot_reports_error(self):
        out = run_js("snapshotRestore('nope')")["result"]
        self.assertFalse(out["success"])
        self.assertTrue(out["error"])

    def test_indexeddb_backend_is_used_when_available(self):
        fake = r'''
const store = new Map();
const mkReq = fn => { const r = {}; setTimeout(() => { r.result = fn(); if (r.onsuccess) r.onsuccess(); }, 0); return r; };
globalThis.indexedDB = { open() {
  const req = {};
  const db = { objectStoreNames: { contains: () => false }, createObjectStore() {}, close() {},
    transaction() {
      const tx = {};
      const os = { getAll: () => mkReq(() => Array.from(store.values())), put: v => mkReq(() => { store.set(v.id, v); return v.id; }), delete: k => mkReq(() => { store.delete(k); }) };
      setTimeout(() => setTimeout(() => tx.oncomplete && tx.oncomplete(), 0), 0);
      tx.objectStore = () => os;
      return tx;
    } };
  setTimeout(() => { req.result = db; if (req.onupgradeneeded) req.onupgradeneeded(); if (req.onsuccess) req.onsuccess(); }, 0);
  return req;
} };
'''
        out = run_js("""(async () => {
          for (let i = 1; i <= 5; i++) await snapshotTake('before-restore', { now: Date.parse('2026-10-0' + i + 'T09:00:00') });
          return { ids: (await snapshotListMeta()).length, ls: localStorage.getItem('%s') };
        })()""" % LS_KEY, storage=SEED_STORAGE, extra=fake)["result"]
        self.assertEqual(out["ids"], 3)
        self.assertIsNone(out["ls"])


class TestWiring(unittest.TestCase):
    def test_build_lists_snapshot_store_after_sm2(self):
        text = (ROOT / "scripts/build_workbench.py").read_text(encoding="utf-8")
        self.assertLess(text.index("'src/state/sm2Store.js'"), text.index("'src/state/snapshotStore.js'"))
        self.assertIn("snapshot-list", text)

    def test_pure_functions_are_exported(self):
        text = (ROOT / "src/state/snapshotStore.js").read_text(encoding="utf-8")
        for name in ("snapshotRetain", "snapshotNeedsDaily", "snapshotCounts"):
            self.assertRegex(text, r"module\.exports = \{[^}]*\b%s\b" % name)


if __name__ == "__main__":
    unittest.main()
