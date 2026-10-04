# -*- coding: utf-8 -*-
"""v1.2 pre-release fixes (second QA round): scheduled mocks are real mocks, cheat-sheet lock,
due-review summary, backup preview text.  Node runs via stdin; no browser."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    "src/data/dailySchedule.generated.js", "src/data/questionPoints.generated.js",
    "src/components/mockExam.js", "src/domain/pacing.js", "src/components/todayTask.js",
]


def run_node(expression, extra=""):
    src = "\n".join((ROOT / f).read_text(encoding="utf-8") for f in FILES)
    script = f"""
const vm = require('vm');
const ctx = {{ console }};
vm.createContext(ctx);
vm.runInContext({json.dumps(src, ensure_ascii=False)}, ctx);
vm.runInContext({json.dumps(extra, ensure_ascii=False)}, ctx);
const out = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, ctx);
process.stdout.write(JSON.stringify(out));
"""
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    if done.returncode:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


ROWS = r"""
var ROWS = Object.keys(QUESTION_POINTS).map(function (qid) {
  var m = /^EE-(\d+)-(\d+)-(\d+)$/.exec(qid);
  return [qid, m[2], m[1], Number(m[3]), 'T', [], 'sol/' + qid, 'x/' + m[1] + '.pdf'];
});
function rec(qid, marks, at, mockId) {
  var q = QUESTION_POINTS[qid];
  var f = { o: 1, tri: 0.5, x: 0 };
  var parts = marks.map(function (m, i) { return { label: 'p' + i, points: q.total / marks.length, mark: m }; });
  var est = parts.reduce(function (s, p) { return s + p.points * f[p.mark]; }, 0);
  return { qid: qid, at: at, source: 'mock', mockId: mockId, parts: parts, errors: [], total: q.total, estimate: est };
}
"""


class ScheduledMockIsRealMock(unittest.TestCase):
    def test_start_generates_mock_id_and_keeps_it_across_phases_and_reload(self):
        out = run_node("""(function () {
          var s = todayTaskStartFrom(todayTaskEmptyState(), 'MOCK114-06', 1000);
          s = todayTaskStart(s, 5000);
          var id = s.active.mockId;
          var s2 = todayTaskAdvance(s, 9000);
          var reloaded = todayTaskNormalizeState(JSON.parse(JSON.stringify(s2)));
          var vm = todayTaskViewModel(reloaded, 9000 + 1000);
          return { code: s.active.code, id: id, kept: s2.active.mockId, reloaded: reloaded.active.mockId,
                   source: vm.active.resultSource, vmId: vm.active.resultMockId, qids: vm.active.resultQids, review: vm.active.isReview };
        })()""")
        self.assertEqual(out["code"], "MOCK114-06")
        self.assertRegex(out["id"], r"^114-06-\d+$")
        self.assertEqual(out["kept"], out["id"])
        self.assertEqual(out["reloaded"], out["id"])
        self.assertEqual(out["source"], "mock")
        self.assertEqual(out["vmId"], out["id"])
        self.assertTrue(out["review"])
        self.assertEqual(out["qids"], ["EE-114-06-1", "EE-114-06-5"])

    def test_scored_subsets_match_mock_exam(self):
        out = run_node("""(function () {
          var res = {};
          ['MOCK114-06', 'BLIND108-02', 'MOCK114-01'].forEach(function (code) {
            var t = DAILY_SCHEDULE.tasks[code];
            var m = /^EE-(\\d+)-(\\d+)-/.exec(t.qids[0]);
            var paper = mockExamPaper(ROWS, m[1], m[2]);
            res[code] = { task: todayTaskScoredQids(t), paper: paper.scoredQids };
          });
          return res;
        })()""", ROWS)
        for code, v in out.items():
            self.assertEqual(v["task"], v["paper"], code)
        self.assertEqual(out["BLIND108-02"]["task"], [f"EE-108-02-{i}" for i in range(1, 5)])

    def test_non_mock_tasks_keep_today_source_and_no_mock_id(self):
        out = run_node("""(function () {
          var s = todayTaskStart(todayTaskEmptyState(), 1000);
          var a = todayTaskAdvance(todayTaskAdvance(s, 2000), 3000);
          var vm = todayTaskViewModel(a, 3500);
          return { code: s.active.code, hasId: 'mockId' in s.active, source: vm.active.resultSource, id: vm.active.resultMockId };
        })()""")
        self.assertFalse(out["hasId"])
        self.assertEqual(out["source"], "today")
        self.assertEqual(out["id"], "")

    def test_task_run_records_count_in_scoreboard_and_history(self):
        out = run_node("""(function () {
          var s = todayTaskStartFrom(todayTaskEmptyState(), 'MOCK114-06', 1000);
          s = todayTaskStart(s, 5000);
          var id = s.active.mockId;
          var recs = [rec('EE-114-06-1', ['o'], 6000, id), rec('EE-114-06-5', ['tri'], 6100, id)];
          var latest = latestMockScoreBySubject(recs, ROWS);
          var hist = mockExamHistory(recs, ROWS);
          return { latest: latest['06'], complete: hist[0].complete, total: hist[0].summary.total };
        })()""", ROWS)
        self.assertEqual(out["latest"]["total"], 40)
        self.assertEqual(out["latest"]["estimate"], 30)
        self.assertTrue(out["complete"])

    def test_normalize_keeps_skipped_for_own_qids_only(self):
        out = run_node("""(function () {
          var s = todayTaskStartFrom(todayTaskEmptyState(), 'MOCK114-06', 1000);
          s = todayTaskStart(s, 5000);
          s = todayTaskAdvance(s, 6000);
          s.active.skipped = ['EE-114-06-1', 'bogus'];
          var n = todayTaskNormalizeState(JSON.parse(JSON.stringify(s)));
          var vm = todayTaskViewModel(n, 6500);
          var adv = todayTaskAdvance(n, 7000);
          return { skipped: n.active.skipped, vm: vm.active.skipped, advSkipped: adv.active.skipped || null };
        })()""")
        self.assertEqual(out["skipped"], ["EE-114-06-1"])
        self.assertEqual(out["vm"], ["EE-114-06-1"])
        self.assertIsNone(out["advSkipped"])


class MockTabCompletesScheduledTask(unittest.TestCase):
    def test_full_paper_completes_matching_task_once(self):
        out = run_node("""(function () {
          var s0 = todayTaskEmptyState();
          var r = todayTaskCompleteMock(s0, '114', '01', 4000);
          var again = todayTaskCompleteMock(r.state, '114', '01', 5000);
          return { code: r.code, done: Object.keys(r.state.completed), again: again.code,
                   current: todayTaskCurrentCode(r.state), s0: Object.keys(s0.completed).length };
        })()""")
        self.assertEqual(out["code"], "MOCK114-01")
        self.assertEqual(out["done"], ["MOCK114-01"])
        self.assertIsNone(out["again"])
        self.assertEqual(out["s0"], 0)
        # order rules unchanged: the earliest uncompleted task is still current
        self.assertNotEqual(out["current"], "MOCK114-01")

    def test_blind108_and_unrelated_papers(self):
        out = run_node("""(function () {
          var b = todayTaskCompleteMock(todayTaskEmptyState(), 108, '02', 1);
          var none = todayTaskCompleteMock(todayTaskEmptyState(), '113', '01', 1);
          var all = {};
          DAILY_SCHEDULE.order.forEach(function (c) { all[c] = 'x'; });
          var s = todayTaskStartFrom(todayTaskEmptyState(), 'MOCK114-03', 1000);
          s = todayTaskStart(s, 2000);
          var active = todayTaskCompleteMock(s, '114', '03', 3000);
          return { b: b.code, none: none.code, activeCleared: active.state.active === null, code: active.code };
        })()""")
        self.assertEqual(out["b"], "BLIND108-02")
        self.assertIsNone(out["none"])
        self.assertTrue(out["activeCleared"])
        self.assertEqual(out["code"], "MOCK114-03")

    def test_mock_exam_wires_the_sync_and_notice(self):
        src = (ROOT / "src/components/mockExam.js").read_text(encoding="utf-8")
        self.assertIn("todayTaskSyncMockCompletion", src)
        self.assertIn("已同步完成排程任務", src)


class CheatsheetLock(unittest.TestCase):
    def render(self, locked):
        data = {
            "subjects": [{"name": "電路學", "categories": [{"label": "甲", "items": [
                {"text": "ITEM-ALL-LOCKED", "qids": ["EE-114-01-1", "EE-114-01-2"]},
                {"text": "ITEM-MIXED", "qids": ["EE-114-01-3", "EE-112-01-2"]},
                {"text": "ITEM-OPEN", "qids": ["EE-111-01-1"]},
            ]}]}],
            "assumption_templates": [
                {"subject_name": "電路學", "situation": "TPL-LOCKED", "how_to_write": "x", "qids": ["EE-108-01-4"]},
                {"subject_name": "電路學", "situation": "TPL-OPEN", "how_to_write": "x", "qids": ["EE-105-01-3"]},
            ],
        }
        script = f"""
        const {{ renderCheatsheetSectionHtml }} = require({json.dumps(str(ROOT / 'src/components/passbookGenerator.js'))});
        process.stdout.write(renderCheatsheetSectionHtml({json.dumps(data, ensure_ascii=False)}, {{ lockedQids: {json.dumps(locked)} }}));
        """
        done = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def test_locked_qids_are_dropped_and_all_locked_items_removed(self):
        html = self.render(["EE-114-01-1", "EE-114-01-2", "EE-114-01-3", "EE-108-01-4"])
        self.assertNotIn("ITEM-ALL-LOCKED", html)
        self.assertNotIn("TPL-LOCKED", html)
        self.assertIn("ITEM-MIXED", html)
        self.assertIn("EE-112-01-2", html)
        self.assertNotIn("EE-114-01-3", html)
        self.assertIn("ITEM-OPEN", html)
        self.assertIn("TPL-OPEN", html)
        self.assertNotIn("EE-114", html.replace("EE-112", ""))

    def test_nothing_locked_keeps_everything(self):
        html = self.render([])
        for token in ("ITEM-ALL-LOCKED", "ITEM-MIXED", "ITEM-OPEN", "TPL-LOCKED", "EE-114-01-1"):
            self.assertIn(token, html)

    def test_whole_subject_locked_hides_the_section(self):
        data = {"subjects": [{"name": "電路學", "categories": [{"label": "甲", "items": [{"text": "T", "qids": ["EE-114-01-1"]}]}]}]}
        script = f"""
        const {{ renderCheatsheetSectionHtml }} = require({json.dumps(str(ROOT / 'src/components/passbookGenerator.js'))});
        process.stdout.write(JSON.stringify(renderCheatsheetSectionHtml({json.dumps(data)}, {{ lockedQids: ['EE-114-01-1'] }})));
        """
        done = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
        self.assertEqual(json.loads(done.stdout), "")


def load_fn(path, name):
    text = (ROOT / path).read_text(encoding="utf-8")
    m = re.search(r"^function " + name + r"\b.*?^}\n", text, re.S | re.M)
    assert m, name
    return m.group(0)


class DueReviewSummaryAndBackupText(unittest.TestCase):
    def node(self, body):
        done = subprocess.run(["node", "-"], input=body, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def test_due_review_summary_text(self):
        fns = load_fn("src/components/reviewPage.js", "reviewSessionSummaryText")
        out = self.node(fns + """
        const r = {
          done: reviewSessionSummaryText({ rated: ['a', 'b', 'c', 'd'], skipped: [], marks: { a: 'o', b: 'o', c: 'tri', d: 'x' } }),
          skip: reviewSessionSummaryText({ rated: ['a'], skipped: ['b', 'a'], marks: { a: 'o' } }),
          allSkip: reviewSessionSummaryText({ rated: [], skipped: ['b'], marks: {} }),
        };
        process.stdout.write(JSON.stringify(r));""")
        self.assertEqual(out["done"], "到期複習完成：4 題，○ 2／△ 1／× 1")
        self.assertTrue(out["skip"].startswith("到期複習完成：1 題，○ 1／△ 0／× 0"))
        self.assertIn("略過 1 題", out["skip"])
        self.assertIn("略過 1 題", out["allSkip"])

    def test_due_review_marks_from_records(self):
        fn = load_fn("src/components/reviewPage.js", "reviewSessionMarkFor")
        out = self.node(fn + """
        process.stdout.write(JSON.stringify([
          reviewSessionMarkFor({ estimate: 20, total: 20 }), reviewSessionMarkFor({ estimate: 10, total: 20 }),
          reviewSessionMarkFor({ estimate: 0, total: 20 }), reviewSessionMarkFor(null, 5), reviewSessionMarkFor(null, 3), reviewSessionMarkFor(null, 1)]));""")
        self.assertEqual(out, ["o", "tri", "x", "o", "tri", "x"])

    def test_backup_preview_lists_result_cards_and_task_progress(self):
        fn = load_fn("src/components/header.js", "formatBackupSummary")
        out = self.node(fn + """
        process.stdout.write(JSON.stringify(formatBackupSummary({ version: '1.2', progressByCategory: { PE: 3, GK: 1 },
          starredByCategory: {}, resultCardRecords: 12, todayTaskDone: 7, todayTaskActive: true, practiceCompleted: 2 })));""")
        self.assertIn("作答結果卡紀錄 12 筆", out)
        self.assertIn("排程任務已完成 7 項", out)
        self.assertIn("進行中", out)
        self.assertNotRegex(out, r"[0-9][^\s 　·（）／\n]*·[^\s]")  # items are separated by ' · '


if __name__ == "__main__":
    unittest.main()
