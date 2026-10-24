# -*- coding: utf-8 -*-
"""破題訓練 (optional feature in src/features/breakdownDrill/): generated data, spacing, round selection, options,
records, backup merge and the hooks it uses.  Skipped entirely when the feature folder has been deleted."""

import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURE = ROOT / "src" / "features" / "breakdownDrill"
PACKAGE = (ROOT / "package.json").read_text(encoding="utf-8")
CORE_FILES = [ROOT / "src" / "state" / "sm2Store.js", ROOT / "src" / "state" / "cloudSync.js", ROOT / "src" / "main.js",
              ROOT / "src" / "components" / "homeStatus.js", ROOT / "src" / "components" / "icons.js",
              ROOT / "scripts" / "build_workbench.py", ROOT / "package.json"]

if not FEATURE.is_dir():
    raise unittest.SkipTest("破題訓練 feature removed")

SCRIPT = r'''
const fs = require('fs'), vm = require('vm');
const storageData = {};
const localStorage = {
  getItem: key => Object.prototype.hasOwnProperty.call(storageData, key) ? storageData[key] : null,
  setItem: (key, value) => { storageData[key] = String(value); },
  removeItem: key => { delete storageData[key]; },
};
const ctx = { console, localStorage, currentExamCategory: 'PE', progressState: {}, starredState: {}, recallState: {},
  getManualTopicLabels: () => ({}), storageData };
vm.createContext(ctx);
for (const file of ['dashboard-data.js', 'national-exams-data.js', 'src/data/knowledge-dag.js', 'src/state/practiceStore.js',
                    'src/state/sm2Store.js', 'src/features/breakdownDrill/data.generated.js', 'src/features/breakdownDrill/store.js']) {
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
}
vm.runInContext(`
  function seeded(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  const DAY = 86400000;
  const NOW = new Date(2026, 9, 23, 20, 0, 0).getTime();
  const at = (m, d, h) => new Date(2026, m - 1, d, h === undefined ? 12 : h).getTime();
  const drill = (qid, when, ok, id) => ({ id: id || ('bd-' + qid + '-' + when), qid, at: when, chapter: 'c', picked: 'c', typeOk: ok, startOk: ok, timedOut: false, secs: 60 });
  function realBank() {
    return Object.keys(BREAKDOWN_DRILL).map(id => ({ id, subject: id.split('-')[2], chapter: BREAKDOWN_DRILL[id].chapter }));
  }
`, ctx);
const result = vm.runInContext(process.argv[1], ctx);
process.stdout.write(JSON.stringify(result === undefined ? null : result));
'''


def run_js(expression):
    done = subprocess.run(["node", "-e", SCRIPT, expression], cwd=ROOT, capture_output=True, text=True)
    if done.returncode:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout.splitlines()[-1])


class TestGeneratedData(unittest.TestCase):
    def test_every_pe_note_has_chapter_and_logic(self):
        r = run_js("""(() => {
          const ids = Object.keys(BREAKDOWN_DRILL);
          return { n: ids.length,
            missing: ids.filter(q => !BREAKDOWN_DRILL[q].chapter || !BREAKDOWN_DRILL[q].logicMd || !KNOWLEDGE_DAG[BREAKDOWN_DRILL[q].chapter]),
            subjects: Array.from(new Set(ids.map(q => q.split('-')[2]))).sort() }; })()""")
        self.assertEqual(r["n"], 323)
        self.assertEqual(r["missing"], [])
        self.assertEqual(r["subjects"], ["01", "02", "03", "04", "05", "06"])

    def test_generator_is_up_to_date_and_wired(self):
        done = subprocess.run(["python3", "src/features/breakdownDrill/build.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("up to date", done.stdout)
        self.assertIn("build_features.py", PACKAGE)
        manifest = json.loads((FEATURE / "feature.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["js"], ["data.generated.js", "store.js", "component.js"])
        for rel in manifest["js"] + manifest["css"]:
            self.assertTrue((FEATURE / rel).is_file(), rel)

    def test_build_loads_feature_files_before_main(self):
        done = subprocess.run(["python3", "-c", "import sys; sys.argv=['x']; sys.path.insert(0, 'scripts'); "
                               "import build_workbench as b; print(__import__('json').dumps(b.feature_files()))"],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        css, js = json.loads(done.stdout.splitlines()[-1])
        self.assertIn("src/features/breakdownDrill/style.css", css)
        self.assertEqual(js[-3:], ["src/features/breakdownDrill/data.generated.js", "src/features/breakdownDrill/store.js",
                                   "src/features/breakdownDrill/component.js"])
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index("// === src/features/breakdownDrill/component.js ==="), html.index("// === src/main.js ==="))
        self.assertGreater(html.index("// === src/features/breakdownDrill/store.js ==="), html.index("// === src/components/homeStatus.js ==="))

    def test_core_never_names_the_feature(self):
        for path in CORE_FILES:
            text = path.read_text(encoding="utf-8")
            hit = re.search(r"(?i)breakdown|破題訓練", text)
            self.assertIsNone(hit, f"{path.relative_to(ROOT)} names the optional feature: {hit and hit.group(0)}")


class TestSpacing(unittest.TestCase):
    def test_leitner_boxes_and_due_days(self):
        r = run_js("""(() => {
          const recs = [drill('EE-110-04-1', at(10, 20), true), drill('EE-110-04-1', at(10, 21), true),
                        drill('EE-111-04-1', at(10, 22), false),
                        drill('EE-112-04-1', at(10, 10), true), drill('EE-112-04-1', at(10, 13), false)];
          const sp = breakdownDrillSpacing(recs);
          return { a: sp['EE-110-04-1'], b: sp['EE-111-04-1'], c: sp['EE-112-04-1'],
                   due: breakdownDrillDueQids(recs, NOW), dueLater: breakdownDrillDueQids(recs, at(10, 28)) }; })()""")
        self.assertEqual((r["a"]["box"], r["a"]["dueDay"], r["a"]["count"]), (2, "2026-10-28", 2))  # 2 right: 7 days
        self.assertEqual((r["b"]["box"], r["b"]["dueDay"]), (0, "2026-10-23"))  # wrong: next day
        self.assertEqual((r["c"]["box"], r["c"]["dueDay"]), (0, "2026-10-14"))  # a miss resets the box
        self.assertEqual(r["due"], ["EE-112-04-1", "EE-111-04-1"])  # earliest due first
        self.assertEqual(r["dueLater"], ["EE-112-04-1", "EE-111-04-1", "EE-110-04-1"])


class TestRound(unittest.TestCase):
    def test_round_shape_new_bank(self):
        r = run_js("""(() => {
          const bank = realBank();
          const a = breakdownDrillBuildRound({ bank, records: [], now: NOW, mastery: {}, rng: seeded(7) });
          const b = breakdownDrillBuildRound({ bank, records: [], now: NOW, mastery: {}, rng: seeded(7) });
          const subj = a.map(q => q.split('-')[2]);
          return { a, same: JSON.stringify(a) === JSON.stringify(b), unique: new Set(a).size,
                   adjacent: subj.some((s, i) => i && s === subj[i - 1]), subjects: new Set(subj).size }; })()""")
        self.assertEqual(len(r["a"]), 8)
        self.assertTrue(r["same"])  # reproducible with the same rng
        self.assertEqual(r["unique"], 8)
        self.assertFalse(r["adjacent"])
        self.assertEqual(r["subjects"], 6)  # interleaved across all six subjects

    def test_due_first_capped_at_half_and_weak_first(self):
        r = run_js("""(() => {
          const bank = realBank();
          const dueQids = bank.slice(0, 6).map(q => q.id);
          const records = dueQids.map((q, i) => drill(q, at(10, 20, i), false));
          const round = breakdownDrillBuildRound({ bank, records, now: NOW, mastery: {}, rng: seeded(3) });
          // weak-first: every chapter strong except one chapter of subject 04
          const mastery = {};
          bank.forEach(q => { mastery[q.chapter] = 0.9; });
          mastery['emach-dc-motor-generator'] = 0.3;
          const weakRound = breakdownDrillBuildRound({ bank, records: [], now: NOW, mastery, rng: seeded(11) });
          const sub04 = weakRound.filter(q => q.split('-')[2] === '04');
          return { dueInRound: round.filter(q => dueQids.includes(q)).length, size: round.length,
                   firstOf04: sub04.length ? BREAKDOWN_DRILL[sub04[0]].chapter : null }; })()""")
        self.assertEqual(r["size"], 8)
        self.assertEqual(r["dueInRound"], 4)  # at most half of the round
        self.assertEqual(r["firstOf04"], "emach-dc-motor-generator")

    def test_due_fills_when_new_run_out_and_repeats_when_all_done(self):
        r = run_js("""(() => {
          const bank = realBank().filter(q => q.subject === '04').slice(0, 10);
          const done = bank.slice(0, 8).map((q, i) => drill(q.id, at(10, 20, i), false));
          const allDone = bank.map((q, i) => drill(q.id, at(10, 22, i), true));
          return { mixed: breakdownDrillBuildRound({ bank, records: done, now: NOW, rng: seeded(5) }).length,
                   repeat: breakdownDrillBuildRound({ bank, records: allDone, now: NOW, rng: seeded(5) }) }; })()""")
        self.assertEqual(r["mixed"], 8)
        self.assertEqual(len(r["repeat"]), 8)  # nothing due, nothing new: least recently drilled come back

    def test_options(self):
        r = run_js("""(() => {
          const bank = realBank();
          const out = bank.slice(0, 60).map((q, i) => {
            const o = breakdownDrillOptions(q, bank, seeded(i + 1));
            const sameSubject = o.every(ch => bank.some(b => b.chapter === ch && b.subject === q.subject));
            return o.length === 4 && new Set(o).size === 4 && o.includes(q.chapter) && sameSubject;
          });
          return out.every(Boolean); })()""")
        self.assertTrue(r)


class TestTypeOptions(unittest.TestCase):
    def test_type_options_prefer_confusers_then_chapter_then_subject(self):
        r = run_js("""(() => {
          const T = { a: {subject: '05', chapter: 'c1', confusers: ['b']}, b: {subject: '05', chapter: 'c1', confusers: ['a']},
                      c: {subject: '05', chapter: 'c1', confusers: ['a']}, d: {subject: '05', chapter: 'c2', confusers: ['a']},
                      e: {subject: '05', chapter: 'c3', confusers: ['a']}, z: {subject: '04', chapter: 'x', confusers: ['a']} };
          const runs = [];
          for (let i = 1; i <= 30; i++) runs.push(breakdownDrillOptions({ subject: '05', chapter: 'c1', type: 'a' }, [], seeded((i * 2654435761) >>> 0), T).slice().sort().join(''));
          const solo = breakdownDrillOptions({ subject: '04', chapter: 'x', type: 'z' }, [], seeded(1), T);
          return { runs: Array.from(new Set(runs)).sort(), solo };
        })()""")
        # b (confuser) and c (same chapter) always present; the 4th is d or e (same subject); never z (other subject)
        self.assertEqual(r["runs"], ["abcd", "abce"])
        self.assertEqual(r["solo"], ["z"])  # nothing else in the subject: only the answer

    def test_real_types_give_four_distinct_same_subject_options(self):
        r = run_js("""(() => {
          const out = [];
          Object.keys(BREAKDOWN_DRILL).forEach((qid, i) => {
            const q = { subject: qid.split('-')[2], chapter: BREAKDOWN_DRILL[qid].chapter, type: BREAKDOWN_DRILL[qid].type };
            const o = breakdownDrillOptions(q, [], seeded(i + 1), BREAKDOWN_DRILL_TYPES);
            const own = BREAKDOWN_DRILL_TYPES[q.type];
            out.push(o.length === 4 && new Set(o).size === 4 && o.includes(q.type)
              && o.every(id => BREAKDOWN_DRILL_TYPES[id].subject === own.subject)
              && own.confusers.filter(c => BREAKDOWN_DRILL_TYPES[c].subject === own.subject).slice(0, 3).every(c => o.includes(c)));
          });
          return { n: out.length, ok: out.every(Boolean) };
        })()""")
        self.assertEqual(r["n"], 323)
        self.assertTrue(r["ok"])


class TestRecordsAndBackup(unittest.TestCase):
    def test_normalize_merge_and_exp(self):
        r = run_js("""(() => {
          const a = { version: 1, records: [drill('EE-110-04-1', at(10, 20), true, 'x1'), { id: 'bad' }, drill('EE-110-04-2', at(10, 19), false, 'x2')],
                      active: { qids: ['EE-110-04-1'], index: 0, startedAt: 1, results: [] } };
          const b = { version: 1, records: [drill('EE-110-04-3', at(10, 21), true, 'x3'), drill('EE-110-04-1', at(10, 20), false, 'x1')] };
          const m = breakdownDrillMerge(a, b);
          return { ids: m.records.map(x => x.id), x1ok: m.records[1].typeOk, active: !!m.active,
                   backup: Object.keys(breakdownDrillBackupPart(a)),
                   exp: breakdownDrillExp(m.records) }; })()""")
        self.assertEqual(r["ids"], ["x2", "x1", "x3"])  # invalid dropped, time order
        self.assertTrue(r["x1ok"])  # local copy wins an id clash
        self.assertTrue(r["active"])
        self.assertEqual(r["backup"], ["version", "records"])  # the round in progress never goes into a backup
        self.assertEqual(r["exp"], 25)  # 10 + 5 + 10

    def test_snapshot_import_merge_and_replace(self):
        r = run_js("""(() => {
          localStorage.setItem('EE_EXAM_BREAKDOWN_DRILL_V1', JSON.stringify({ version: 1,
            records: [drill('EE-110-04-1', at(10, 20), true, 'local')], active: { qids: ['EE-110-04-1'], index: 0, startedAt: 1, results: [] } }));
          const snap = buildUserBackupSnapshot({ skipMetadata: true });
          const incoming = JSON.parse(JSON.stringify(snap));
          incoming.breakdownDrill.records = [drill('EE-111-04-1', at(10, 21), false, 'remote')];
          const merged = applyUserDataBackup(incoming, 'merge');
          const afterMerge = JSON.parse(localStorage.getItem('EE_EXAM_BREAKDOWN_DRILL_V1'));
          const old = JSON.parse(JSON.stringify(snap)); delete old.breakdownDrill;
          const legacy = applyUserDataBackup(old, 'replace');
          const afterLegacy = JSON.parse(localStorage.getItem('EE_EXAM_BREAKDOWN_DRILL_V1'));
          const replaced = applyUserDataBackup(incoming, 'replace');
          const afterReplace = JSON.parse(localStorage.getItem('EE_EXAM_BREAKDOWN_DRILL_V1'));
          const broken = JSON.parse(JSON.stringify(snap)); broken.breakdownDrill = { version: 2 };
          return { snapKeys: Object.keys(snap.breakdownDrill), snapCount: snap.breakdownDrill.records.length,
                   merged: merged.success, mergedCount: merged.summary.extensions, afterMerge: afterMerge.records.map(x => x.id), keptActive: !!afterMerge.active,
                   legacy: legacy.success, afterLegacy: afterLegacy.records.map(x => x.id),
                   replaced: replaced.success, afterReplace: afterReplace.records.map(x => x.id), replaceActive: afterReplace.active,
                   broken: applyUserDataBackup(broken, 'merge').success }; })()""")
        self.assertEqual(r["snapKeys"], ["version", "records"])
        self.assertEqual(r["snapCount"], 1)
        self.assertTrue(r["merged"])
        self.assertEqual(r["mergedCount"], {"breakdownDrill": 2})
        self.assertEqual(r["afterMerge"], ["local", "remote"])
        self.assertTrue(r["keptActive"])
        self.assertTrue(r["legacy"])
        self.assertEqual(r["afterLegacy"], ["local", "remote"])  # an older backup without the field leaves drills alone
        self.assertTrue(r["replaced"])
        self.assertEqual(r["afterReplace"], ["remote"])
        self.assertIsNone(r["replaceActive"])
        self.assertFalse(r["broken"])


class TestHeldPapers(unittest.TestCase):
    def test_unfinished_mock_and_blind_papers_are_never_drilled(self):
        script = SCRIPT.replace("'src/features/breakdownDrill/store.js']", "'src/features/breakdownDrill/store.js', 'src/features/breakdownDrill/component.js']")
        expr = """(() => {
          DAILY_SCHEDULE = { order: ['MOCK114-04', 'BLIND108-02', 'BLIND108-04', 'CORE-01'] };
          todayTaskState = { completed: { 'MOCK114-04': '2026-10-10T00:00:00Z', 'BLIND108-04': '2026-10-22T00:00:00Z' } };
          practiceLockedQids = () => new Set(['EE-110-01-1']);
          practiceReservedQids = () => ['EE-111-01-1'];
          anchorBankFromGlobals_ = () => Object.keys(BREAKDOWN_DRILL).map(id => ({ id, subject: id.split('-')[2], year: Number(id.split('-')[1]), crop: true }));
          const bank = breakdownDrillBank().map(q => q.id);
          return { n: bank.length, b108_02: bank.filter(q => q.startsWith('EE-108-02-')).length, b108_04: bank.filter(q => q.startsWith('EE-108-04-')).length,
                   b114_04: bank.filter(q => q.startsWith('EE-114-04-')).length, locked: bank.includes('EE-110-01-1'), reserved: bank.includes('EE-111-01-1') }; })()"""
        done = subprocess.run(["node", "-e", script.replace("const ctx = {", "const ctx = { DAILY_SCHEDULE: null, todayTaskState: null, practiceLockedQids: null, practiceReservedQids: null, anchorBankFromGlobals_: null,"), expr],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        r = json.loads(done.stdout.splitlines()[-1])
        self.assertEqual(r["b108_02"], 0)  # unfinished blind test: whole paper held back, even questions outside the lock list
        self.assertGreater(r["b108_04"], 0)  # finished blind test: drillable
        self.assertGreater(r["b114_04"], 0)
        self.assertFalse(r["locked"])
        self.assertFalse(r["reserved"])


class TestComponentWiring(unittest.TestCase):
    def test_component_uses_store_and_refreshes_status(self):
        js = (FEATURE / "component.js").read_text(encoding="utf-8")
        self.assertIn("saveBreakdownDrillState(state)", js)
        self.assertIn("homeStatusRefresh()", js)
        self.assertIn("registerHomeStatusExpSource(", js)
        self.assertIn("'ee:data-merged'", js)
        store = (FEATURE / "store.js").read_text(encoding="utf-8")
        self.assertIn("cloudSyncMarkDirty()", store)
        self.assertIn("registerBackupExtension(", store)
        self.assertTrue(re.search(r"BREAKDOWN_DRILL_SECONDS = 120;", store))


if __name__ == "__main__":
    unittest.main()
