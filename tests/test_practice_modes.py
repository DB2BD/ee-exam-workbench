# -*- coding: utf-8 -*-
"""v1.3 B：各科輪流／補強模式、依日期的預設與 dailyPracticeStartWithMode。"""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = (ROOT / "src/state/practiceStore.js").read_text(encoding="utf-8")
UI = (ROOT / "src/components/dailyPractice.js").read_text(encoding="utf-8")
DAY = 86400000

# 6 subjects x 4 questions; chapter c<s><k//2>, tier main for k<2 else basic.
QUESTIONS = [
    {"id": f"EE-114-0{s}-{k}", "subjectId": f"0{s}"} for s in range(1, 7) for k in range(1, 5)
]


def node(script):
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def store_eval(expression, setup=""):
    script = f"""
const vm = require('vm');
const ctx = {{ console }}; vm.createContext(ctx);
vm.runInContext({json.dumps(STORE)}, ctx);
vm.runInContext({json.dumps(setup + "globalThis.__r = (" + expression + ");")}, ctx);
process.stdout.write(JSON.stringify(ctx.__r));
"""
    return node(script)


COMMON = f"""
const QS = {json.dumps(QUESTIONS)};
const DAY = 86400000;
const NOW = Date.UTC(2026, 9, 5, 4, 0, 0);
const subj = id => /^EE-\\d+-(\\d+)-/.exec(id)[1];
const tierOf = id => Number(id.split('-')[3]) <= 2 ? 'main' : 'basic';
const chapterOf = q => 'ch-' + q.id.split('-')[2] + '-' + (Number(q.id.split('-')[3]) <= 2 ? 'a' : 'b');
function seq(...v) {{ let i = 0; return () => v[i++ % v.length]; }}
function rec(qid, mark, extra) {{ return Object.assign({{id: qid + Math.random(), qid, at: NOW - DAY, source: 'today',
  parts: [{{label: '整題', points: 10, mark}}], errors: []}}, extra || {{}}); }}
const opts = extra => Object.assign({{count: 3, now: NOW, random: seq(0.1, 0.6, 0.35, 0.8), tierOf, chapterOf, lockedQids: []}}, extra || {{}});
"""


class TestBalanced(unittest.TestCase):
    def test_three_distinct_subjects(self):
        for r in ("0", "0.5", "0.99"):
            ids = store_eval(f"createBalancedPracticeQueue(QS, opts({{random: () => {r}}}))", COMMON)
            self.assertEqual(len(ids), 3)
            self.assertEqual(len({i.split("-")[2] for i in ids}), 3)

    def test_least_practised_subjects_first(self):
        # subjects 01-03 practised a lot in the window, 04-06 never -> picks come from 04-06
        recs = [f"rec('EE-114-0{s}-{k}', 'o')" for s in (1, 2, 3) for k in (1, 2)]
        ids = store_eval(f"createBalancedPracticeQueue(QS, opts({{records: [{','.join(recs)}]}}))", COMMON)
        self.assertEqual({i.split("-")[2] for i in ids}, {"04", "05", "06"})

    def test_old_records_do_not_count(self):
        recs = [f"rec('EE-114-0{s}-1', 'o', {{at: NOW - 20 * {DAY}}})" for s in (4, 5, 6)]
        recs += [f"rec('EE-114-0{s}-2', 'o')" for s in (1, 2, 3)]
        ids = store_eval(f"createBalancedPracticeQueue(QS, opts({{records: [{','.join(recs)}]}}))", COMMON)
        self.assertEqual({i.split("-")[2] for i in ids}, {"04", "05", "06"})

    def test_rotation_evens_out_over_rounds(self):
        script = """(() => {
const records = []; const counts = {};
for (let round = 0; round < 12; round++) {
  const ids = createBalancedPracticeQueue(QS, opts({records, random: seq(0.2, 0.7, 0.4, 0.9, 0.1)}));
  ids.forEach(id => { records.push(rec(id, 'o', {at: NOW - 1000})); counts[subj(id)] = (counts[subj(id)] || 0) + 1; });
}
return counts; })()"""
        counts = store_eval(script, COMMON)
        values = list(counts.values())
        self.assertEqual(len(values), 6)
        self.assertEqual(sum(values), 36)
        self.assertLessEqual(max(values) - min(values), 1)

    def test_prefers_main_but_includes_basic(self):
        script = """(() => { let main = 0, basic = 0; let n = 0;
const rnd = () => { n += 1; return ((n * 0.6180339887) % 1); };
for (let i = 0; i < 200; i++) {
  createBalancedPracticeQueue(QS, opts({random: rnd})).forEach(id => { tierOf(id) === 'main' ? main++ : basic++; });
}
return {main, basic}; })()"""
        out = store_eval(script, COMMON)
        self.assertGreater(out["main"], out["basic"])
        self.assertGreater(out["basic"], 0)

    def test_excludes_recent_and_locked(self):
        locked = [q["id"] for q in QUESTIONS if q["subjectId"] != "06"]
        ids = store_eval(f"createBalancedPracticeQueue(QS, opts({{lockedQids: {json.dumps(locked)}, count: 2}}))", COMMON)
        self.assertEqual({i.split("-")[2] for i in ids}, {"06"})
        done = "{" + ",".join(f"'EE-114-06-{k}': NOW - DAY" for k in (1, 2, 3)) + "}"
        ids = store_eval(f"createBalancedPracticeQueue(QS, opts({{completionByQuestion: {done}}}))", COMMON)
        self.assertNotIn("EE-114-06-1", ids)
        self.assertNotIn("EE-114-06-2", ids)
        self.assertNotIn("EE-114-06-3", ids)


class TestReinforce(unittest.TestCase):
    def reinforce(self, records, **extra):
        extra_js = "".join(f", {k}: {json.dumps(v)}" for k, v in extra.items())
        return store_eval(f"createReinforcePracticeQueue(QS, opts({{records: [{','.join(records)}]{extra_js}}}))", COMMON)

    def test_mock_misses_first_then_same_chapter(self):
        ids = self.reinforce([
            "rec('EE-114-01-3', 'x', {source: 'mock', mockId: 'm1'})",
            "rec('EE-114-02-1', 'tri', {source: 'mock', mockId: 'm2'})",
        ])
        self.assertEqual(set(ids[:2]), {"EE-114-01-3", "EE-114-02-1"})
        self.assertEqual(ids[0], "EE-114-01-3")  # x before tri
        self.assertEqual(len(ids), 3)
        # third pick is same chapter as a miss, main tier first: ch-01-b has 01-4 only -> 01-4 (b chapter) or 02-2
        self.assertIn(ids[2], {"EE-114-01-4", "EE-114-02-2"})

    def test_same_chapter_main_first(self):
        ids = self.reinforce(["rec('EE-114-03-3', 'x', {source: 'mock'})"], random=0)
        # chapters of the miss: ch-03-b (03-3, 03-4); the main-tier 'same chapter' pool is empty there,
        # so the same-chapter basic one follows, then fill
        self.assertEqual(ids[0], "EE-114-03-3")
        self.assertEqual(ids[1], "EE-114-03-4")

    def test_error_chapters_when_no_mock(self):
        ids = self.reinforce([
            "rec('EE-114-05-1', 'x', {errors: ['F', 'C']})",
            "rec('EE-114-05-2', 'x', {errors: ['K']})",
            "rec('EE-114-02-1', 'tri', {errors: ['S']})",
        ])
        # 05-1 / 05-2 latest records are x so they stay eligible; chapter ch-05-a has most errors
        self.assertIn(ids[0], {"EE-114-05-1", "EE-114-05-2"})
        self.assertEqual(len(ids), 3)

    def test_latest_circle_is_not_repeated(self):
        ids = self.reinforce([
            "rec('EE-114-01-3', 'x', {source: 'mock', at: NOW - 3 * " + str(DAY) + "})",
            "rec('EE-114-01-3', 'o', {source: 'today', at: NOW - " + str(DAY) + "})",
            "rec('EE-114-02-1', 'x', {source: 'mock'})",
        ])
        self.assertNotIn("EE-114-01-3", ids)
        self.assertEqual(ids[0], "EE-114-02-1")

    def test_falls_back_to_balanced_when_empty(self):
        ids = self.reinforce([])
        self.assertEqual(len(ids), 3)
        self.assertEqual(len({i.split("-")[2] for i in ids}), 3)
        ids = self.reinforce(["rec('EE-114-01-1', 'o', {source: 'mock'})"])
        self.assertNotIn("EE-114-01-1", ids)
        self.assertEqual(len(ids), 3)

    def test_locked_and_recent_excluded(self):
        ids = self.reinforce(
            ["rec('EE-114-01-3', 'x', {source: 'mock'})", "rec('EE-114-02-1', 'x', {source: 'mock'})"],
            lockedQids=["EE-114-01-3"], completionByQuestion={"EE-114-02-1": 1791158400000 - DAY})
        self.assertNotIn("EE-114-01-3", ids)
        self.assertNotIn("EE-114-02-1", ids)


class TestLockedAllModes(unittest.TestCase):
    def test_locked_never_selected(self):
        locked = [q["id"] for q in QUESTIONS if q["id"].endswith(("-1", "-2"))]
        recs = "[rec('EE-114-01-1','x',{source:'mock'}), rec('EE-114-02-2','x',{source:'mock'})]"
        for fn in ("createBalancedPracticeQueue", "createReinforcePracticeQueue", "createDailyPracticeQueue"):
            for r in (0, 0.5, 0.9):
                ids = store_eval(f"{fn}(QS, opts({{random: () => {r}, records: {recs}, lockedQids: {json.dumps(locked)}}}))", COMMON)
                self.assertEqual(len(ids), 3, fn)
                self.assertFalse(set(ids) & set(locked), fn)
        ids = store_eval(f"createWeightedPracticeQueue(QS, opts({{weightOf: () => 1, lockedQids: {json.dumps(locked)}}}))", COMMON)
        self.assertFalse(set(ids) & set(locked))


class TestDefaultModeByDate(unittest.TestCase):
    def test_phase_defaults(self):
        out = store_eval(
            "[[2026,10,4],[2026,10,17],[2026,10,18],[2026,11,1],[2026,11,2],[2026,12,1]]"
            ".map(a => practiceDefaultModeFor(new Date(a[0], a[1]-1, a[2], 12).getTime()))")
        self.assertEqual(out, ["balanced", "balanced", "weighted", "weighted", "reinforce", "reinforce"])


def ui_eval(body, date=(2026, 10, 5), questions=None, extra_setup=""):
    qs = questions or [[q["id"], q["subjectId"], 114, int(q["id"][-1]), "題", ["T"], "sol", "src", 3, "verified", ["F"], True] for q in QUESTIONS]
    y, m, d = date
    script = f"""
const vm = require('vm');
const RealDate = Date;
const fixed = new RealDate({y}, {m - 1}, {d}, 12).getTime();
class FakeDate extends RealDate {{
  constructor(...a) {{ if (a.length) super(...a); else super(fixed); }}
  static now() {{ return fixed; }}
}}
const els = {{}};
const el = id => els[id] || (els[id] = {{id, innerHTML:'', textContent:'', querySelector:()=>null, querySelectorAll:()=>[], classList:{{contains:()=>false}}}});
const store = {{}};
const ctx = {{ console, Date: FakeDate, document: {{getElementById: el, querySelector: () => null, querySelectorAll: () => []}},
  localStorage: {{getItem: k => k in store ? store[k] : null, setItem: (k, v) => {{ store[k] = String(v); }}}} }};
vm.createContext(ctx);
vm.runInContext({json.dumps(STORE)}, ctx);
vm.runInContext({json.dumps((ROOT / 'src/domain/questionRecord.js').read_text(encoding='utf-8'))}, ctx);
vm.runInContext({json.dumps(UI)}, ctx);
vm.runInContext({json.dumps(f'''
globalThis.showToast = () => {{}};
globalThis.currentExamCategory = 'PE';
globalThis.openSolutionModal = (...a) => {{ globalThis.opened = a; }};
globalThis.DB_DATA = {{subjects: [{{id:'01',name:'電路學',icon:'a'}},{{id:'02',name:'電子學',icon:'b'}},{{id:'03',name:'x',icon:'c'}},{{id:'04',name:'y',icon:'d'}},{{id:'05',name:'z',icon:'e'}},{{id:'06',name:'w',icon:'f'}}], questions: {json.dumps(qs)}}};
globalThis.NATIONAL_EXAMS_DATA = {{subjects: [], questions: []}};
globalThis.studyTierFor = id => Number(id.split('-')[3]) <= 2 ? 'main' : 'basic';
{extra_setup}
''')}, ctx);
vm.runInContext({json.dumps("globalThis.__r = (() => {" + body + "})();")}, ctx);
process.stdout.write(JSON.stringify(ctx.__r));
"""
    return node(script)


class TestUiModes(unittest.TestCase):
    def test_default_mode_and_labels(self):
        out = ui_eval("return {a: dailyPracticeLoadMode(), l: ['weighted','balanced','reinforce','all','01'].map(m => dailyPracticeModeLabel(m)), html: dailyPracticeModeSelectHtml()};")
        self.assertEqual(out["a"], "balanced")
        self.assertEqual(out["l"][:4], ["依目標分配", "各科輪流", "補強（模考錯題）", "全部隨機"])
        self.assertTrue(out["l"][4].startswith("只練"))
        for label in ("依目標分配", "各科輪流", "補強（模考錯題）", "全部隨機", "只練"):
            self.assertIn(label, out["html"])

    def test_dates_choose_default(self):
        for date, expected in (((2026, 10, 17), "balanced"), ((2026, 10, 18), "weighted"), ((2026, 11, 2), "reinforce")):
            self.assertEqual(ui_eval("return dailyPracticeLoadMode();", date=date), expected)

    def test_explicit_choice_overrides_until_phase_changes(self):
        out = ui_eval("""
dailyPracticeSetMode('all');
const same = dailyPracticeLoadMode();
const key = localStorage.getItem('EE_EXAM_DAILY_PRACTICE_MODE_PHASE_V1');
return {same, key};""")
        self.assertEqual(out, {"same": "all", "key": "p1"})
        # the same stored choice, read in the next phase, is ignored
        out = ui_eval("""
localStorage.setItem('EE_EXAM_DAILY_PRACTICE_MODE_V1', 'all');
localStorage.setItem('EE_EXAM_DAILY_PRACTICE_MODE_PHASE_V1', 'p1');
return dailyPracticeLoadMode();""", date=(2026, 10, 20))
        self.assertEqual(out, "weighted")
        out = ui_eval("""
localStorage.setItem('EE_EXAM_DAILY_PRACTICE_MODE_V1', 'all');
localStorage.setItem('EE_EXAM_DAILY_PRACTICE_MODE_PHASE_V1', 'p2');
return dailyPracticeLoadMode();""", date=(2026, 10, 20))
        self.assertEqual(out, "all")

    def test_start_with_mode_opens_first_question_on_cover(self):
        out = ui_eval("""
dailyPracticeStartWithMode('balanced');
const s = JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1')).activeSession;
return {ids: s.questionIds, mode: s.mode, opts: globalThis.opened[4], qid: globalThis.opened[2],
  html: document.getElementById('daily-practice-container').innerHTML, saved: localStorage.getItem('EE_EXAM_DAILY_PRACTICE_MODE_V1')};""")
        self.assertEqual(len(out["ids"]), 3)
        self.assertEqual(len({i.split("-")[2] for i in out["ids"]}), 3)
        self.assertEqual(out["mode"], "balanced")
        self.assertEqual(out["opts"], {"mode": "daily-practice", "recall": True})
        self.assertEqual(out["qid"], out["ids"][0])
        self.assertIn("各科輪流", out["html"])
        self.assertIsNone(out["saved"])  # does not overwrite the selector choice

    def test_start_with_reinforce_uses_mock_records(self):
        out = ui_eval("""
dailyPracticeStartWithMode('reinforce');
return JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1')).activeSession;""", date=(2026, 11, 3),
            extra_setup="globalThis.getResultRecords = () => [{id:'a', qid:'EE-114-04-3', at: Date.now() - 86400000, source:'mock', parts:[{label:'整題',points:10,mark:'x'}], errors:[]}, {id:'b', qid:'EE-114-05-1', at: Date.now() - 86400000, source:'mock', parts:[{label:'整題',points:10,mark:'tri'}], errors:[]}];")
        self.assertEqual(out["mode"], "reinforce")
        self.assertEqual(set(out["questionIds"][:2]), {"EE-114-04-3", "EE-114-05-1"})

    def test_locked_qids_excluded_via_schedule(self):
        out = ui_eval("""
const ids = [];
for (let i = 0; i < 20; i++) { dailyPracticeStartWithMode(['balanced','reinforce','weighted','all','01'][i % 5]);
  ids.push(...JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1')).activeSession.questionIds); }
return ids;""", extra_setup="globalThis.DAILY_SCHEDULE = {tasks: {M1: {kind: 'mock114', qids: ['EE-114-01-1','EE-114-01-2','EE-114-02-1','EE-114-03-1']}}}; globalThis.studyTierFor = id => 'main';")
        self.assertFalse(set(out) & {"EE-114-01-1", "EE-114-02-1", "EE-114-03-1"})


if __name__ == "__main__":
    unittest.main()
