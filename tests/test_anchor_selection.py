# -*- coding: utf-8 -*-
"""v1.3.8 基本分選題演算法：src/domain/anchorSelection.js（純函式）與 practiceStore 錨章佇列。"""

import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "src/domain/anchorSelection.js"
STORE = "src/state/practiceStore.js"

# 3 subjects x 4 chapters (a-d); a-c are 主攻, d is 基本分.  Years include 114 and 108 (mock papers).
YEARS = {"a": [114, 113, 112, 111], "b": [113, 112, 111, 110], "c": [112, 111, 110, 109], "d": [108, 107, 106, 105]}
BANK = [
    {"id": f"EE-{year}-{s}-{n}", "subject": s, "year": year, "chapter": f"ch-{s}-{ch}", "points": 20}
    for s in ("01", "02", "03")
    for n, ch in enumerate("abcd", start=1)
    for year in YEARS[ch]
]
ALLOCATION = {"subjects": {
    "01": {"name": "電路學", "target": 75, "mainChapters": ["ch-01-a", "ch-01-b", "ch-01-c"], "sharedChapters": []},
    "02": {"name": "電子學", "target": 55, "mainChapters": ["ch-02-a", "ch-02-b", "ch-02-c"], "sharedChapters": []},
    "03": {"name": "工程數學", "target": 60, "mainChapters": ["ch-03-a", "ch-03-b", "ch-03-c"], "sharedChapters": ["ch-03-c"]},
}}
MOCK_LOCKED = [q["id"] for q in BANK if q["year"] in (114, 108)]

PRELUDE = f"""
const DAY = 86400000;
const NOW = Date.UTC(2026, 9, 12, 1, 0, 0);
const BANK = {json.dumps(BANK)};
const ALLOC = {json.dumps(ALLOCATION)};
const MOCK_LOCKED = {json.dumps(MOCK_LOCKED)};
let _rid = 0;
function rec(qid, mark, extra) {{
  const e = extra || {{}};
  const marks = Array.isArray(mark) ? mark : [mark];
  return Object.assign({{ id: 'r' + (_rid++), qid, at: NOW - (e.age === undefined ? 5 : e.age) * DAY, source: 'today',
    parts: marks.map((m, i) => ({{ label: 'p' + i, points: 10, mark: m }})), errors: e.errors || [] }},
    e.legacy ? {{ legacy: true }} : {{}});
}}
function mk(extra) {{
  return anchorContext(Object.assign({{ now: NOW, questions: BANK, allocation: ALLOC, records: [], dueQids: [], dueDates: {{}},
    locked: [], reserved: [], completionByQuestion: {{}}, estimates: {{}}, schedule: {{ tasks: {{}} }} }}, extra || {{}}));
}}
"""


def node(script):
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def run(expression, files=(ANCHOR,), setup=""):
    script = (
        "const vm = require('vm');\nconst ctx = { console: { log() {}, warn() {}, error() {} } }; vm.createContext(ctx);\n"
        + "".join(f"vm.runInContext({json.dumps((ROOT / f).read_text(encoding='utf-8'))}, ctx, {{ filename: {json.dumps(f)} }});\n" for f in files)
        + f"vm.runInContext({json.dumps(PRELUDE + setup + 'globalThis.__r = (' + expression + ');')}, ctx);\n"
        + "process.stdout.write(JSON.stringify(ctx.__r));\n"
    )
    return node(script)


class TestParametersAndPurity(unittest.TestCase):
    def test_no_random_and_parameters(self):
        src = (ROOT / ANCHOR).read_text(encoding="utf-8")
        self.assertNotIn("Math.random", src)
        self.assertNotIn("document.", src)
        self.assertNotIn("localStorage", src)
        for line in ("const ANCHORS_PER_SUBJECT = 2;", "const PRIOR_M0 = 0.2;", "const PRIOR_K = 0.5;",
                     "const LEGACY_WEIGHT = 0.6;", "const HALF_LIFE_DAYS = 21;", "const CF_BONUS = 0.15;",
                     "const KRS_PENALTY = 0.10;", "const SHARED_BONUS = 1.1;", "const HOLD_M = 0.9;",
                     "const COOLDOWN_REDO_DAYS = 2;", "const COOLDOWN_SCORED_DAYS = 7;",
                     "const IDLE_WEIGHT = 3;", "const IDLE_CAP_DAYS = 7;"):
            self.assertIn(line, src)
        self.assertIn("G = { untested: 0.5, cf: 0.7, mixed: 0.55, krs: 0.4, none: 0.55 }", src)

    def test_context_accepts_number_and_date_now(self):
        out = run("[anchorContext({ now: NOW, questions: [] }).now, anchorContext({ now: new Date(NOW), questions: [] }).now]")
        self.assertEqual(out, [1791766800000, 1791766800000])

    def test_in_build_list_before_today_task(self):
        build = (ROOT / "scripts/build_workbench.py").read_text(encoding="utf-8")
        self.assertLess(build.index("src/domain/studyPlan.js"), build.index(ANCHOR))
        self.assertLess(build.index(ANCHOR), build.index("src/components/todayTask.js"))


class TestDeterminism(unittest.TestCase):
    def test_same_ctx_and_shuffled_inputs_give_same_results(self):
        out = run("""(() => {
          const records = [
            rec('EE-113-01-1', 'x', {errors: ['K'], age: 5}), rec('EE-112-01-1', 'tri', {errors: ['C'], age: 4}),
            rec('EE-113-02-2', 'o', {age: 9}), rec('EE-112-02-2', 'tri', {age: 6}), rec('EE-112-03-3', 'x', {age: 8}),
            rec('EE-111-03-3', 'o', {age: 12, legacy: true}), rec('EE-113-01-2', 'x', {age: 7}),
          ];
          const dueQids = ['EE-113-01-1', 'EE-112-02-2', 'EE-112-03-3', 'EE-113-02-2', 'EE-113-01-2'];
          const dueDates = {'EE-113-01-1': '2026-10-10', 'EE-112-02-2': '2026-10-11', 'EE-112-03-3': '2026-10-10',
            'EE-113-02-2': '2026-10-12', 'EE-113-01-2': '2026-10-09'};
          const task = {code: 'FOCUS-01', kind: 'focus', subject: '電路學', qids: ['EE-113-01-1', 'EE-112-01-2']};
          const base = {records, dueQids, dueDates, locked: MOCK_LOCKED};
          const shuffled = {records: records.slice().reverse(), dueQids: dueQids.slice().reverse(), dueDates, locked: MOCK_LOCKED,
            questions: BANK.slice().reverse()};
          const summary = c => {
            const st = anchorChapterStats(c);
            return {
              anchors: ['01', '02', '03'].map(s => anchorChaptersFor(s, st)),
              queue: anchorQueue({subjects: ['03', '01', '02'], count: 12, ctx: c}),
              pick: anchorFocusPick({task, state: {completed: {}}, ctx: c}),
              due: anchorSortDue(dueQids.slice().reverse(), c),
              stats: Object.keys(st).sort().map(k => [k, st[k].score, st[k].m]),
            };
          };
          return [summary(mk(base)), summary(mk(base)), summary(mk(shuffled))];
        })()""")
        self.assertEqual(out[0], out[1])
        self.assertEqual(out[0], out[2])
        self.assertTrue(out[0]["queue"])


class TestMasteryAndAnchors(unittest.TestCase):
    def test_single_legacy_circle_does_not_reach_one(self):
        out = run("""(() => {
          const st = anchorChapterStats(mk({records: [rec('EE-113-01-1', 'o', {age: 0, legacy: true})]}));
          return [st['ch-01-a'].m, st['ch-01-a'].g];
        })()""")
        self.assertAlmostEqual(out[0], (0.6 + 0.1) / (0.6 + 0.5))
        self.assertLess(out[0], 1)
        self.assertIsNone(out[1])  # all ○: g not needed

    def test_cf_adds_krs_subtracts_untested_prior(self):
        out = run("""(() => {
          const st = anchorChapterStats(mk({records: [
            rec('EE-113-01-1', 'tri', {age: 0, errors: ['C']}),
            rec('EE-113-01-2', 'tri', {age: 0, errors: ['K']}),
            rec('EE-112-01-3', 'tri', {age: 0}),
          ]}));
          const f = c => ({m: st[c].m, g: st[c].g, untested: st[c].untested});
          return {cf: f('ch-01-a'), krs: f('ch-01-b'), none: f('ch-01-c'), fresh: f('ch-01-d')};
        })()""")
        self.assertAlmostEqual(out["cf"]["m"], (0.65 + 0.1) / 1.5)
        self.assertAlmostEqual(out["krs"]["m"], (0.40 + 0.1) / 1.5)
        self.assertAlmostEqual(out["none"]["m"], (0.50 + 0.1) / 1.5)
        self.assertEqual((out["cf"]["g"], out["krs"]["g"], out["none"]["g"]), (0.7, 0.4, 0.55))
        self.assertAlmostEqual(out["fresh"]["m"], 0.2)
        self.assertEqual((out["fresh"]["g"], out["fresh"]["untested"]), (0.5, True))

    def test_anchors_are_main_only_and_exactly_two(self):
        out = run("""(() => {
          const st = anchorChapterStats(mk({}));
          return ['01', '02', '03'].map(s => anchorChaptersFor(s, st));
        })()""")
        for s, anchors in zip(("01", "02", "03"), out):
            self.assertEqual(len(anchors), 2)
            for ch in anchors:
                self.assertIn(ch, ALLOCATION["subjects"][s]["mainChapters"])

    def test_undrillable_chapter_is_not_an_anchor_unless_held(self):
        out = run("""(() => {
          const reserved = BANK.filter(q => q.chapter === 'ch-02-a').map(q => q.id);
          const st = anchorChapterStats(mk({reserved}));
          const stHold = anchorChapterStats(mk({
            records: ['EE-114-01-1', 'EE-113-01-1', 'EE-112-01-1', 'EE-111-01-1'].map(q => rec(q, 'o', {age: 1})),
          }));
          return {
            drill: st['ch-02-a'].drillable, m: st['ch-02-a'].m, anchors: anchorChaptersFor('02', st),
            holdM: stHold['ch-01-a'].m, holdDrill: stHold['ch-01-a'].drillable, hold: anchorChaptersFor('01', stHold),
          };
        })()""")
        self.assertEqual(out["drill"], 0)
        self.assertLess(out["m"], 0.9)
        self.assertNotIn("ch-02-a", out["anchors"])
        self.assertEqual(len(out["anchors"]), 2)
        self.assertGreaterEqual(out["holdM"], 0.9)
        self.assertEqual(out["holdDrill"], 0)
        self.assertIn("ch-01-a", out["hold"])  # 守住錨

    def test_shared_chapter_gets_bonus(self):
        out = run("""(() => {
          const noShare = JSON.parse(JSON.stringify(ALLOC)); noShare.subjects['03'].sharedChapters = [];
          const a = anchorChapterStats(mk({}))['ch-03-c'].score;
          const b = anchorChapterStats(mk({allocation: noShare}))['ch-03-c'].score;
          return [a, b];
        })()""")
        self.assertAlmostEqual(out[0] / out[1], 1.1)


class TestPoolEligibility(unittest.TestCase):
    def test_locked_and_reserved_excluded_then_released(self):
        out = run("""(() => {
          const pool = c => anchorPool(c).map(e => e.qid);
          const closed = pool(mk({locked: MOCK_LOCKED, reserved: ['EE-113-01-1']}));
          const open = pool(mk({}));
          return {closed114: closed.filter(q => q.startsWith('EE-114-') || q.startsWith('EE-108-')), res: closed.includes('EE-113-01-1'),
            open114: open.includes('EE-114-01-1'), openRes: open.includes('EE-113-01-1')};
        })()""")
        self.assertEqual(out, {"closed114": [], "res": False, "open114": True, "openRes": True})

    def test_cooldown_two_days(self):
        out = run("""(() => {
          const c = mk({records: [rec('EE-113-01-1', 'x', {age: 1.9}), rec('EE-112-01-1', 'x', {age: 2})]});
          const pool = anchorPool(c).map(e => e.qid);
          return [pool.includes('EE-113-01-1'), pool.includes('EE-112-01-1')];
        })()""")
        self.assertEqual(out, [False, True])

    def test_completion_by_question_also_cools_down(self):
        out = run("""(() => {
          const c = mk({completionByQuestion: {'EE-113-01-1': NOW - DAY}});
          return anchorPool(c).map(e => e.qid).includes('EE-113-01-1');
        })()""")
        self.assertFalse(out)

    def test_circle_only_when_due(self):
        out = run("""(() => {
          const records = [rec('EE-113-01-1', 'o', {age: 5}), rec('EE-112-01-1', 'o', {age: 5})];
          const pool = anchorPool(mk({records, dueQids: ['EE-112-01-1']}));
          const find = q => pool.find(e => e.qid === q);
          return [!!find('EE-113-01-1'), find('EE-112-01-1') && find('EE-112-01-1').tier];
        })()""")
        self.assertEqual(out, [False, "P4"])

    def test_tier_classification(self):
        out = run("""(() => {
          const records = [
            rec('EE-113-01-1', 'tri', {errors: []}), rec('EE-112-01-1', 'x', {errors: ['C', 'F']}),
            rec('EE-111-01-1', 'x', {errors: []}), rec('EE-113-01-2', 'tri', {errors: ['C', 'K']}),
            rec('EE-112-01-2', 'x', {errors: ['S']}),
          ];
          const pool = anchorPool(mk({records}));
          const t = q => pool.find(e => e.qid === q).tier;
          return ['EE-113-01-1', 'EE-112-01-1', 'EE-111-01-1', 'EE-113-01-2', 'EE-112-01-2', 'EE-113-02-1'].map(t);
        })()""")
        self.assertEqual(out, ["P1", "P1", "P2", "P2", "P2", "P3"])

    def test_queue_order_tiers_then_year_desc(self):
        out = run("""(() => {
          const locked = MOCK_LOCKED;
          const a1 = anchorChaptersFor('01', anchorChapterStats(mk({locked})))[0];
          const qs = BANK.filter(q => q.chapter === a1 && !locked.includes(q.id)).sort((x, y) => y.year - x.year).map(q => q.id);
          const records = [rec(qs[0], 'tri', {errors: []}), rec(qs[1], 'x', {errors: ['R']}), rec(qs[2], 'tri', {errors: ['C']})];
          const queue = anchorSubjectQueue('01', mk({records, locked}));
          return {qs, queue: queue.filter(q => qs.includes(q)), a1, still: anchorChaptersFor('01', anchorChapterStats(mk({records, locked}))).includes(a1)};
        })()""")
        self.assertTrue(out["still"])
        qs = out["qs"]
        # P1 (tri, newest first: qs[0], qs[2]) before P2 (x with R: qs[1])
        self.assertEqual(out["queue"], [qs[0], qs[2], qs[1]])



FOCUS_BANK = """
function fbank(list) { return list.map(([id, chapter]) => ({ id, subject: '01', chapter })); }
const FALLOC = { subjects: { '01': { name: '電路學', target: 75, mainChapters: ['ch-x', 'ch-y'], sharedChapters: [] } } };
const FTASK = { code: 'FOCUS-02', kind: 'focus', subject: '電路學', qids: ['EE-100-01-1', 'EE-100-01-2'] };
const FSCHED = { tasks: {
  'FOCUS-01': { code: 'FOCUS-01', kind: 'focus', subject: '電路學', qids: [] },
  'FOCUS-02': FTASK,
  'FOCUS-03': { code: 'FOCUS-03', kind: 'focus', subject: '電路學', qids: [] },
  'FOCUS-04': { code: 'FOCUS-04', kind: 'focus', subject: '電子學', qids: [] },
  'CORE-01': { code: 'CORE-01', kind: 'core', subject: '電路學', qids: [] } } };
function fctx(list, extra) {
  return anchorContext(Object.assign({ now: NOW, questions: fbank(list), allocation: FALLOC, records: [], dueQids: [], dueDates: {},
    locked: [], reserved: [], estimates: {}, schedule: FSCHED }, extra || {}));
}
"""


def focus(expression):
    return run(expression, setup=FOCUS_BANK)


class TestFocusPick(unittest.TestCase):
    def test_example_is_p2_fresh_is_p3_and_scored_is_fresh(self):
        out = focus("""(() => {
          const list = [['EE-113-01-1', 'ch-x'], ['EE-112-01-1', 'ch-x'], ['EE-111-01-1', 'ch-x'], ['EE-110-01-1', 'ch-x']];
          const records = [rec('EE-113-01-1', 'x', {errors: ['C'], age: 5}), rec('EE-112-01-1', 'x', {errors: ['K'], age: 5})];
          return anchorFocusPick({task: FTASK, state: {completed: {}}, ctx: fctx(list, {records})});
        })()""")
        self.assertEqual(out["chapter"], "ch-x")
        # P2 (EE-112-01-1, x with K) wins over P1 (EE-113-01-1); the new question is the first never-recorded one.
        self.assertEqual(out["qids"], ["EE-112-01-1", "EE-111-01-1"])
        self.assertEqual(out["scoredQids"], ["EE-111-01-1"])
        self.assertNotEqual(out["qids"][0], out["qids"][1])

    def test_no_example_two_fresh_questions(self):
        out = focus("""(() => {
          const list = [['EE-113-01-1', 'ch-x'], ['EE-112-01-1', 'ch-x'], ['EE-111-01-1', 'ch-x']];
          return anchorFocusPick({task: FTASK, state: {completed: {}}, ctx: fctx(list)});
        })()""")
        self.assertEqual(out["qids"], ["EE-113-01-1", "EE-112-01-1"])
        self.assertEqual(out["scoredQids"], ["EE-112-01-1"])

    def test_fresh_fallback_needs_seven_days(self):
        out = focus("""(() => {
          const list = [['EE-113-01-1', 'ch-x'], ['EE-112-01-1', 'ch-x']];
          const pick = age => anchorFocusPick({task: FTASK, state: {completed: {}}, ctx: fctx(list, {records: [
            rec('EE-113-01-1', 'x', {errors: ['K'], age: 5}), rec('EE-112-01-1', 'tri', {errors: ['C'], age: age})]})});
          return [pick(6), pick(8)];
        })()""")
        self.assertIsNone(out[0])
        self.assertEqual(out[1]["qids"], ["EE-113-01-1", "EE-112-01-1"])
        self.assertEqual(out[1]["scoredQids"], ["EE-112-01-1"])

    def test_empty_pool_returns_null(self):
        out = focus("""(() => {
          const list = [['EE-113-01-1', 'ch-x'], ['EE-112-01-1', 'ch-x'], ['EE-111-01-1', 'ch-y'], ['EE-110-01-1', 'ch-y']];
          return anchorFocusPick({task: FTASK, state: {completed: {}}, ctx: fctx(list, {locked: list.map(x => x[0])})});
        })()""")
        self.assertIsNone(out)

    def test_anchors_rotate_by_mastery_ascending_but_queue_follows_score(self):
        out = focus("""(() => {
          // ch-x: more years (freq) and a recent ○ (m high); ch-y: an × with K (m low). score(x) > score(y), m(x) > m(y).
          const list = [['EE-113-01-1', 'ch-x'], ['EE-112-01-1', 'ch-x'], ['EE-111-01-1', 'ch-x'], ['EE-110-01-1', 'ch-x'], ['EE-109-01-1', 'ch-x'],
                        ['EE-113-01-2', 'ch-y'], ['EE-112-01-2', 'ch-y'], ['EE-111-01-2', 'ch-y'], ['EE-110-01-2', 'ch-y']];
          const records = [rec('EE-109-01-1', 'o', {age: 10}), rec('EE-113-01-2', 'x', {errors: ['K'], age: 5})];
          const c = fctx(list, {records});
          const st = anchorChapterStats(c);
          const at = done => anchorFocusPick({task: FTASK, state: {completed: done}, ctx: c}).chapter;
          return {
            score: [st['ch-x'].score, st['ch-y'].score], m: [st['ch-x'].m, st['ch-y'].m],
            anchors: anchorChaptersFor('01', st), focusOrder: anchorFocusOrder('01', st),
            rounds: [at({}), at({'FOCUS-01': 'x'}), at({'FOCUS-01': 'x', 'FOCUS-03': 'x'}), at({'FOCUS-01': 'x', 'FOCUS-04': 'x', 'CORE-01': 'x'})],
            queue: anchorQueue({subjects: ['01'], count: 6, ctx: c}).map(q => st['ch-x'].lists.P3.concat(st['ch-x'].lists.P2).includes(q) ? 'x' : 'y'),
          };
        })()""")
        self.assertGreater(out["score"][0], out["score"][1])
        self.assertGreater(out["m"][0], out["m"][1])
        self.assertEqual(out["anchors"], ["ch-x", "ch-y"])          # score order
        self.assertEqual(out["focusOrder"], ["ch-y", "ch-x"])       # m ascending
        # k = completed FOCUS rounds of the subject (other subject / CORE codes do not count)
        self.assertEqual(out["rounds"][:3], ["ch-y", "ch-x", "ch-y"])
        self.assertEqual(out["rounds"][3], "ch-x")
        # queue: P2 of ch-y first (tier order), then P3 interleaved A1 (x, higher score) before A2 (y)
        self.assertEqual(out["queue"][:3], ["y", "x", "y"])

    def test_equal_mastery_higher_score_first(self):
        out = focus("""(() => {
          const list = [['EE-113-01-1', 'ch-x'], ['EE-112-01-1', 'ch-x'], ['EE-111-01-1', 'ch-x'], ['EE-110-01-1', 'ch-x'],
                        ['EE-113-01-2', 'ch-y'], ['EE-112-01-2', 'ch-y'], ['EE-111-01-2', 'ch-y']];
          const c = fctx(list);
          const st = anchorChapterStats(c);
          const at = done => anchorFocusPick({task: FTASK, state: {completed: done}, ctx: c}).chapter;
          return {m: [st['ch-x'].m, st['ch-y'].m], rounds: [at({}), at({'FOCUS-01': 'x'})]};
        })()""")
        self.assertEqual(out["m"][0], out["m"][1])
        self.assertEqual(out["rounds"], ["ch-x", "ch-y"])

    def test_overflows_to_third_chapter(self):
        out = focus("""(() => {
          const falloc = {subjects: {'01': {name: '電路學', target: 75, mainChapters: ['ch-x', 'ch-y', 'ch-z'], sharedChapters: []}}};
          const list = [['EE-113-01-1', 'ch-x'], ['EE-112-01-1', 'ch-y'], ['EE-113-01-3', 'ch-z'], ['EE-112-01-3', 'ch-z'], ['EE-111-01-3', 'ch-z']];
          const c = fctx(list, {allocation: falloc, locked: ['EE-113-01-1', 'EE-112-01-1']});
          return anchorFocusPick({task: FTASK, state: {completed: {}}, ctx: c});
        })()""")
        # ch-x / ch-y are fully locked (not anchors: nothing to drill, m < 0.9); ch-z is the only candidate
        self.assertEqual(out["chapter"], "ch-z")


class TestRealDataSmoke(unittest.TestCase):
    FILES = ["dashboard-data.js", "src/data/dailySchedule.generated.js", "src/data/questionPoints.generated.js",
             "src/data/targetAllocation.generated.js", "src/domain/studyPlan.js", ANCHOR]

    def test_cold_start_anchors_and_focus_pick(self):
        out = run("""(() => {
          const c = anchorContext({ now: NOW, records: [], dueQids: [], locked: [], reserved: [] });
          const st = anchorChapterStats(c);
          const anchors = anchorSubjectIds(c).map(s => [s, anchorChaptersFor(s, st)]);
          const task = DAILY_SCHEDULE.tasks['FOCUS-01'];
          return {anchors, main: TARGET_ALLOCATION.subjects, pick: anchorFocusPick({task, state: {completed: {}}, ctx: c})};
        })()""", files=self.FILES)
        self.assertEqual(len(out["anchors"]), 6)
        for sid, anchors in out["anchors"]:
            self.assertEqual(len(anchors), 2, sid)
            for ch in anchors:
                self.assertIn(ch, out["main"][sid]["mainChapters"], sid)
        pick = out["pick"]
        self.assertIsNotNone(pick)
        self.assertEqual(len(set(pick["qids"])), 2)
        self.assertTrue(all(re.fullmatch(r"EE-\d+-06-\d+", q) for q in pick["qids"]))
        self.assertEqual(pick["scoredQids"], [pick["qids"][1]])
        self.assertIn(pick["chapter"], out["main"]["06"]["mainChapters"])


class TestAnchorSortDue(unittest.TestCase):
    def test_anchor_first_then_mark_then_due_date(self):
        out = run("""(() => {
          const two = JSON.parse(JSON.stringify(ALLOC)); two.subjects['01'].mainChapters = ['ch-01-a', 'ch-01-b'];
          const anchors = ['ch-01-a', 'ch-01-b'];
          const ids = ch => BANK.filter(q => q.chapter === ch).sort((x, y) => y.year - x.year).map(q => q.id);
          const qa = ids(anchors[0]), qb = ids(anchors[1]);
          const qd = ids('ch-01-d');
          const records = [rec(qa[0], 'x', {age: 6}), rec(qa[1], 'tri', {age: 6}), rec(qb[0], 'x', {age: 6}), rec(qa[2], 'o', {age: 6}),
            rec(qd[0], 'x', {age: 6}), rec(qd[1], 'tri', {age: 6})];
          const dueDates = {[qa[0]]: '2026-10-10', [qa[1]]: '2026-10-09', [qb[0]]: '2026-10-08', [qa[2]]: '2026-10-01', [qd[0]]: '2026-10-01', [qd[1]]: '2026-10-02'};
          const c = mk({records, dueDates, dueQids: Object.keys(dueDates), allocation: two});
          const stillAnchors = anchorChaptersFor('01', anchorChapterStats(c));
          return {same: JSON.stringify(stillAnchors) === JSON.stringify(anchors), expected: [qb[0], qa[0], qa[1], qa[2], qd[0], qd[1]],
            sorted: anchorSortDue(Object.keys(dueDates).reverse(), c)};
        })()""")
        self.assertTrue(out["same"])
        # anchor chapters first (x by due date, then tri, then ○), the non-anchor chapter last (x before tri)
        self.assertEqual(out["sorted"], out["expected"])

    def test_count_unchanged_and_input_not_mutated(self):
        out = run("""(() => {
          const ids = ['EE-113-01-1', 'EE-112-02-2', 'EE-111-03-3', 'EE-999-01-1'];
          const copy = ids.slice();
          const sorted = anchorSortDue(ids, mk({}));
          return {same: JSON.stringify(ids) === JSON.stringify(copy), n: sorted.length, set: sorted.slice().sort()};
        })()""")
        self.assertTrue(out["same"])
        self.assertEqual(out["n"], 4)


class TestPracticeQueues(unittest.TestCase):
    """practiceStore wired to the anchor queues (weighted / balanced / reinforce)."""

    FILES = [ANCHOR, STORE]
    SETUP = """
const QS = BANK.map(q => ({ id: q.id, subjectId: q.subject }));
let randomCalls = 0;
const counting = () => { randomCalls += 1; return 0.5; };
function opts(extra) {
  return Object.assign({ count: 3, now: NOW, random: counting, lockedQids: MOCK_LOCKED, reservedQids: [], records: [], dueQids: [],
    anchorCtx: { questions: BANK, allocation: ALLOC, estimates: {}, schedule: { tasks: {} } } }, extra || {});
}
"""

    def go(self, expression):
        return run(expression, files=self.FILES, setup=self.SETUP)

    def test_weighted_heads_come_from_anchor_p1_p2_without_random(self):
        out = self.go("""(() => {
          const records = [rec('EE-113-02-1', 'tri', {errors: ['C'], age: 4}), rec('EE-113-03-1', 'tri', {errors: ['C'], age: 4})];
          const ids = createWeightedPracticeQueue(QS, opts({records}));
          const c = anchorContext({ now: NOW, records, dueQids: [], locked: MOCK_LOCKED, reserved: [],
            questions: BANK, allocation: ALLOC, estimates: {}, schedule: { tasks: {} } });
          const pool = anchorPool(c);
          return { ids, tiers: ids.map(q => pool.find(e => e.qid === q).tier), calls: randomCalls };
        })()""")
        # subject priority (no estimates): 01 (75) > 03 (60) > 02 (55); each subject contributes the head of its anchor queue
        self.assertEqual(out["ids"][1:], ["EE-113-03-1", "EE-113-02-1"])
        self.assertEqual(out["ids"][0].split("-")[2], "01")
        self.assertEqual(out["tiers"], ["P3", "P1", "P1"])
        self.assertEqual(out["calls"], 0)

    def test_balanced_one_per_subject_without_random(self):
        out = self.go("""(() => {
          const ids = createBalancedPracticeQueue(QS, opts({}));
          return { ids, calls: randomCalls };
        })()""")
        self.assertEqual(len({i.split("-")[2] for i in out["ids"]}), 3)
        self.assertEqual(out["calls"], 0)

    def test_reinforce_due_anchor_before_mock_miss_and_no_random(self):
        out = self.go("""(() => {
          const records = [
            rec('EE-113-01-1', 'tri', {errors: ['C'], age: 4}),                              // due, anchor chapter ch-01-a
            rec('EE-113-02-2', 'x', {source: 'mock', mockId: 'm1', age: 4}),
            rec('EE-112-03-2', 'tri', {source: 'mock', mockId: 'm2', age: 4}),
          ];
          const ids = createReinforcePracticeQueue(QS, opts({records, dueQids: ['EE-113-01-1']}));
          const c = anchorContext({ now: NOW, records, dueQids: ['EE-113-01-1'], locked: MOCK_LOCKED, reserved: [],
            questions: BANK, allocation: ALLOC, estimates: {}, schedule: { tasks: {} } });
          return { ids, anchors: anchorChaptersFor('01', anchorChapterStats(c)), calls: randomCalls };
        })()""")
        self.assertIn("ch-01-a", out["anchors"])
        self.assertEqual(out["ids"][0], "EE-113-01-1")
        self.assertEqual(len(out["ids"]), 3)
        self.assertEqual(len(set(out["ids"])), 3)
        self.assertEqual(out["calls"], 0)

    def test_random_only_used_to_fill(self):
        out = self.go("""(() => {
          const small = opts({count: 3});
          const anchored = createWeightedPracticeQueue(QS, small);
          const callsAfterEnough = randomCalls;
          const big = createWeightedPracticeQueue(QS, opts({count: 40}));
          return { anchored, callsAfterEnough, bigLen: big.length, bigUnique: new Set(big).size, callsAfterBig: randomCalls };
        })()""")
        self.assertEqual(out["callsAfterEnough"], 0)
        self.assertGreater(out["callsAfterBig"], 0)
        self.assertEqual(out["bigUnique"], out["bigLen"])

    def test_locked_never_drawn(self):
        out = self.go("""(() => {
          const all = [];
          ['createWeightedPracticeQueue', 'createBalancedPracticeQueue', 'createReinforcePracticeQueue'].forEach(fn => {
            all.push(...globalThis[fn](QS, opts({count: 30})));
          });
          return all.filter(q => MOCK_LOCKED.includes(q));
        })()""")
        self.assertEqual(out, [])


class TestTierPromotion(unittest.TestCase):
    FILES = ["src/data/questionPoints.generated.js", "src/data/targetAllocation.generated.js", "src/domain/studyPlan.js",
             "src/state/sm2Store.js", "src/state/resultCardStore.js", "src/components/resultCard.js",
             "src/components/scoreboard.js"]

    def test_load_characteristics_is_main_everywhere(self):
        out = run("""(() => {
          const q = 'EE-112-06-2';
          const vm = resultCardViewModel(q, [], [], 'today');
          const tier = studyTierFor(q), weight = practiceWeightFor(q);
          const before = TARGET_ALLOCATION.questionTiers;
          const mainShare = scoreboardTierShares('06').main;
          const saved = {};
          Object.keys(before).filter(k => before[k].chapter === 'dist-load-characteristics' && k.startsWith('EE-')).forEach(k => { saved[k] = before[k].tier; before[k].tier = 'basic'; });
          const demotedShare = scoreboardTierShares('06').main;
          return { tier, weight, circle: vm.markButtons[0].text, hint: vm.hint, tierLabel: vm.tierLabel,
            mainShare, demotedShare, n: Object.keys(saved).length };
        })()""", files=self.FILES)
        self.assertEqual(out["tier"], "main")
        self.assertEqual(out["weight"], 3)
        self.assertEqual(out["circle"], "全對")
        self.assertEqual(out["hint"], "")
        self.assertEqual(out["tierLabel"], "主攻")
        self.assertEqual(out["n"], 6)
        self.assertGreater(out["mainShare"], out["demotedShare"])


if __name__ == "__main__":
    unittest.main()
