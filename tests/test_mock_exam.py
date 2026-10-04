# -*- coding: utf-8 -*-
"""WP5b：模考分頁純函式測試（node 以 stdin 執行，無瀏覽器）。"""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ["src/data/questionPoints.generated.js", "src/components/mockExam.js"]


def run_node(expression):
    src = "\n".join((ROOT / f).read_text(encoding="utf-8") for f in FILES)
    dash = (ROOT / "dashboard-data.js")
    script = f"""
const vm = require('vm');
const ctx = {{ console }};
vm.createContext(ctx);
vm.runInContext({json.dumps(src, ensure_ascii=False)}, ctx);
vm.runInContext({json.dumps(ROWS_SETUP)}, ctx);
const out = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, ctx);
process.stdout.write(JSON.stringify(out));
"""
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    if done.returncode:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


# 以 QUESTION_POINTS 的 qid 產生等價的 DB_DATA 列（題號、PDF 檔名為測試用）。
ROWS_SETUP = r"""
var ROWS = Object.keys(QUESTION_POINTS).map(function (qid) {
  var m = /^EE-(\d+)-(\d+)-(\d+)$/.exec(qid);
  return [qid, m[2], m[1], Number(m[3]), 'T', [], 'sol/' + qid, '依年度分類/' + m[1] + '年/' + m[1] + '年_科目.pdf'];
});
function rec(qid, marks, at, mockId, errors) {
  var q = QUESTION_POINTS[qid];
  var parts = marks.map(function (m, i) { return { label: 'p' + i, points: q.total / marks.length, mark: m }; });
  var f = { o: 1, tri: 0.5, x: 0 };
  var est = parts.reduce(function (s, p) { return s + p.points * f[p.mark]; }, 0);
  return { qid: qid, at: at, source: 'mock', mockId: mockId, parts: parts, errors: errors || [], total: q.total, estimate: est };
}
"""


class MockExamTests(unittest.TestCase):
    def test_every_full_paper_totals_100(self):
        out = run_node("""(function () {
          var bad = [];
          for (var y = 104; y <= 114; y++) for (var s = 1; s <= 6; s++) {
            var sid = ('0' + s).slice(-2);
            var p = mockExamPaper(ROWS, y, sid);
            if (p.items.length && p.total !== 100) bad.push([y, sid, p.total]);
            if (!p.items.length) bad.push([y, sid, 'empty']);
          }
          return bad;
        })()""")
        self.assertEqual(out, [])

    def test_114_distribution_scoring_subset(self):
        p = run_node("mockExamPaper(ROWS, 114, '06')")
        self.assertEqual(p["total"], 100)
        self.assertEqual(p["scoredTotal"], 40)
        self.assertEqual(p["scoredQids"], ["EE-114-06-1", "EE-114-06-5"])
        self.assertEqual([i["scored"] for i in p["items"]], [True, False, False, False, True])
        self.assertIn("只計第 1、5 題", p["scoringNote"])
        other = run_node("mockExamPaper(ROWS, 114, '03')")
        self.assertEqual(other["scoredTotal"], 100)
        self.assertEqual(other["scoringNote"], "")

    def test_time_caps_and_pdf(self):
        caps = run_node("[10, 15, 20, 25, 30].map(mockExamTimeCap)")
        self.assertEqual(caps, [9, 13.5, 18, 22.5, 27])
        p = run_node("mockExamPaper(ROWS, 114, '03')")
        self.assertEqual([i["timeCap"] for i in p["items"]], [13.5, 13.5, 18, 18, 27])
        self.assertEqual(p["pdfUrl"], "data/official_pdfs/pe/114%E5%B9%B4_%E7%A7%91%E7%9B%AE.pdf")
        self.assertIn("5 分鐘掃卷＋90 分鐘第一輪＋17 分鐘搶分＋8 分鐘收尾", p["reminder"])

    def test_summary_fix_first_and_tiebreak(self):
        # 114 工數：Q3、Q4 各 20 分且皆 △／×，Q5 30 分為 ○ -> 同分取題號較早的 Q3
        s = run_node("""mockExamSummary([
          rec('EE-114-03-1', ['o'], 1, 'm'), rec('EE-114-03-2', ['o'], 2, 'm'),
          rec('EE-114-03-3', ['x'], 3, 'm', ['S', 'C']), rec('EE-114-03-4', ['tri'], 4, 'm', ['C']),
          rec('EE-114-03-5', ['o', 'o'], 5, 'm')])""")
        self.assertEqual(s["fixFirst"]["qid"], "EE-114-03-3")
        self.assertEqual(s["errorTally"], {"S": 1, "C": 2})
        self.assertEqual(s["estimate"], 15 + 15 + 0 + 10 + 30)
        self.assertEqual(s["total"], 100)
        # 配分較高者優先：Q5 為 △ 時先修 Q5
        s2 = run_node("""mockExamSummary([rec('EE-114-03-3', ['x'], 3, 'm'), rec('EE-114-03-5', ['tri', 'o'], 5, 'm')])""")
        self.assertEqual(s2["fixFirst"]["qid"], "EE-114-03-5")
        # 全部 ○ -> 無先修題；同題多筆取最新
        s3 = run_node("""mockExamSummary([rec('EE-114-03-1', ['x'], 1, 'm'), rec('EE-114-03-1', ['o'], 9, 'm')])""")
        self.assertIsNone(s3["fixFirst"])
        self.assertEqual(s3["estimate"], 15)

    def test_latest_mock_score_by_subject(self):
        out = run_node("""(function () {
          var all = [];
          ['EE-114-03-1','EE-114-03-2','EE-114-03-3','EE-114-03-4','EE-114-03-5'].forEach(function (q) { all.push(rec(q, ['o'], 1000, '114-03-1000')); });
          ['EE-113-03-1','EE-113-03-2','EE-113-03-3','EE-113-03-4','EE-113-03-5','EE-113-03-6'].forEach(function (q) { all.push(rec(q, ['x'], 2000, '113-03-2000')); });
          // 未評完的較新模考不得取代
          all.push(rec('EE-114-03-1', ['x'], 3000, '114-03-3000'));
          // 114 配電只評 Q1、Q5（共 40 分），全 ○ -> 40／40，換算 100
          all.push(rec('EE-114-06-1', ['o'], 4000, '114-06-4000'));
          all.push(rec('EE-114-06-5', ['o'], 4001, '114-06-4000'));
          all.push({ qid: 'EE-114-01-1', at: 5, source: 'today', parts: [], errors: [], total: 20, estimate: 20 });
          return latestMockScoreBySubject(all, ROWS);
        })()""")
        self.assertEqual(sorted(out.keys()), ["03", "06"])
        self.assertEqual(out["03"]["mockId"], "113-03-2000")
        self.assertEqual(out["03"]["estimate"], 0)
        self.assertEqual(out["06"]["estimate"], 40)
        self.assertEqual(out["06"]["total"], 40)
        self.assertEqual(out["06"]["scaled"], 100)

    def test_history_marks_incomplete(self):
        out = run_node("""mockExamHistory([rec('EE-114-03-1', ['o'], 3000, '114-03-3000')], ROWS).map(function (h) { return [h.mockId, h.complete, h.expectedCount]; })""")
        self.assertEqual(out, [["114-03-3000", False, 5]])

    def test_shortcuts_from_schedule_codes(self):
        out = run_node("""(function () {
          var sched = { tasks: {
            'MOCK114-01': { kind: 'mock114', subject: '電路學', qids: ['EE-114-01-1'] },
            'BLIND108-02': { kind: 'blind108', subject: '電子學', qids: ['EE-108-02-1'] } } };
          return mockExamShortcuts(sched).map(function (s) { return [s.label, s.items.map(function (i) { return [i.code, i.year, i.sid]; })]; });
        })()""")
        self.assertEqual(out, [["114 年模考", [["MOCK114-01", "114", "01"]]], ["108 年盲測", [["BLIND108-02", "108", "02"]]]])

    def test_mock_id_format(self):
        out = run_node("[mockExamNewId(114, '03', 1788000000000), mockExamParseId('114-03-1788000000000')]")
        self.assertEqual(out[0], "114-03-1788000000000")
        self.assertEqual(out[1]["subjectId"], "03")

    def test_no_timer_anywhere(self):
        text = (ROOT / "src/components/mockExam.js").read_text(encoding="utf-8")
        for token in ["setInterval", "setTimeout", "startExamTimer", "pauseExamTimer", "resetExamTimer", "getMockExamPacingInfo", "countdown"]:
            self.assertNotIn(token, text)
        self.assertFalse((ROOT / "src/components/mockExamTimer.js").exists())
        build = (ROOT / "scripts/build_workbench.py").read_text(encoding="utf-8")
        self.assertNotIn("mockExamTimer.js", build)
        self.assertIn("src/components/mockExam.js", build)


class G2aTests(unittest.TestCase):
    def test_summary_shows_actual_marks(self):
        out = run_node("""(function () {
          var r = rec('EE-114-03-3', ['o', 'x'], 1, 'm1');
          var q = mockExamSummary([r]).perQuestion[0];
          return [mockExamMarksText(q), mockExamMarksText({parts: [{label: '整題', mark: 'tri'}]})];
        })()""")
        self.assertEqual(out[0], "p0 ○　p1 ×")
        self.assertEqual(out[1], "△")

    def test_solution_button_docks_card_without_mount(self):
        src = (ROOT / "src/components/mockExam.js").read_text(encoding="utf-8")
        body = src.split("function mockExamOpenSolution(qid)")[1].split("function mockExamPickerHtml")[0]
        self.assertIn("openSolutionModal(", body)
        opts = body.split("openResultCard({")[1].split("});")[0]
        self.assertNotIn("mount", opts)
        self.assertIn("source: 'mock'", opts)


if __name__ == "__main__":
    unittest.main()
