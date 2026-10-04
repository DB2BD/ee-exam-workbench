# -*- coding: utf-8 -*-
"""K1 答案更正提醒: banner, badge, learner-record detection, build wiring."""

import json
import re
import subprocess
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SOURCES = [
    WORKSPACE / "src/data/answerCorrections.generated.js",
    WORKSPACE / "src/data/dailySchedule.generated.js",
    WORKSPACE / "src/components/answerCorrectionNotice.js",
]


def run_node(expression, storage=None, broken=False):
    code = "\n".join(p.read_text(encoding="utf-8") for p in SOURCES)
    code += "\nglobalThis.__result = (" + expression + ");"
    script = f"""
const vm = require('vm');
const data = {json.dumps(storage or {}, ensure_ascii=False)};
const localStorage = {{
  getItem: k => {"{ throw new Error('blocked'); }" if broken else "Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null"},
}};
const context = {{ console, localStorage }};
vm.createContext(context);
vm.runInContext({json.dumps(code, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(context.__result === undefined ? null : context.__result));
"""
    done = subprocess.run(["node", "-e", script], cwd=WORKSPACE, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def local_iso(y, m, d, hh=12):
    out = subprocess.run(
        ["node", "-e", f"process.stdout.write(new Date({y},{m - 1},{d},{hh},0).toISOString())"],
        capture_output=True, text=True, check=True)
    return out.stdout


def local_ms(y, m, d, hh=12):
    out = subprocess.run(
        ["node", "-e", f"process.stdout.write(String(new Date({y},{m - 1},{d},{hh},0).getTime()))"],
        capture_output=True, text=True, check=True)
    return int(out.stdout)


class TestBanner(unittest.TestCase):
    def test_non_corrected_qid_is_empty(self):
        self.assertEqual(run_node("answerCorrectionBannerHtml('EE-999-99-9')"), "")
        self.assertIsNone(run_node("answerCorrectionFor('EE-999-99-9')"))
        self.assertEqual(run_node("answerCorrectionBadgeHtml('EE-999-99-9')"), "")
        self.assertEqual(run_node("answerCorrectionBannerHtml(null)"), "")

    def test_prototype_keys_are_not_corrections(self):
        self.assertIsNone(run_node("answerCorrectionFor('constructor')"))

    def test_corrected_qid_banner_escaped(self):
        html = run_node("answerCorrectionBannerHtml('EE-112-01-2')")
        self.assertIn("本題答案已於", html)
        self.assertIn("612.5", html)
        self.assertIn("<details", html)
        self.assertIn("舊：", html)
        self.assertIn("原因：", html)
        # every dynamic value is escaped: only our own tags may appear
        tags = set(re.findall(r"</?([a-z]+)", html))
        self.assertEqual(tags, {"details", "summary", "div"})

    def test_every_correction_renders_and_escapes(self):
        qids = run_node("Object.keys(ANSWER_CORRECTIONS)")
        expected = json.loads((WORKSPACE / "data/answer-corrections.json").read_text(encoding="utf-8"))
        self.assertEqual(len(qids), len(expected["corrections"]))
        for qid in qids:
            html = run_node(f"answerCorrectionBannerHtml('{qid}')")
            self.assertTrue(html.startswith("<details"), qid)
            self.assertEqual(set(re.findall(r"</?([a-z]+)", html)), {"details", "summary", "div"}, qid)

    def test_escape_function(self):
        self.assertEqual(run_node("answerCorrectionEscape('<b>\"&\\'')"), "&lt;b&gt;&quot;&amp;&#39;")

    def test_badge(self):
        self.assertIn("答案已更正", run_node("answerCorrectionBadgeHtml('EE-112-01-2')"))


class TestAttempted(unittest.TestCase):
    QID = "EE-112-01-2"

    def decided(self):
        return run_node(f"ANSWER_CORRECTIONS['{self.QID}'].decided_at")

    def date_parts(self):
        y, m, d = map(int, self.decided().split("-"))
        return y, m, d

    def attempted(self, storage):
        return run_node("answerCorrectionsAttempted(localStorage)", storage)

    def envelope(self, status, **stamps):
        env = {"sessionId": "s1", "qid": self.QID, "examFamily": "PE", "status": status}
        env.update(stamps)
        return {"EE_EXAM_ATTEMPT_ENVELOPES_V1": json.dumps(
            {"schemaVersion": "learning-attempts.v1", "attempts": {"s1": env}})}

    def test_empty_storage(self):
        self.assertEqual(self.attempted({}), [])

    def test_storage_unavailable(self):
        self.assertEqual(run_node("answerCorrectionsAttempted(localStorage)", broken=True), [])
        self.assertEqual(run_node("answerCorrectionsAttempted(null)"), [])

    def test_attempt_before_included_after_excluded(self):
        y, m, d = self.date_parts()
        before = self.attempted(self.envelope("committed", committedAt=local_iso(y, m, d - 1 if d > 1 else 1, 12) if d > 1 else "2000-01-01T00:00:00.000Z"))
        self.assertEqual([r["qid"] for r in before], [self.QID])
        self.assertIsNotNone(before[0]["lastAttemptAt"])
        after = self.attempted(self.envelope("acknowledged", committedAt=local_iso(y, m, d + 1, 9)))
        self.assertEqual(after, [])

    def test_attempt_same_day_late_is_included_boundary_next_midnight_excluded(self):
        y, m, d = self.date_parts()
        same_day = self.attempted(self.envelope("committed", committedAt=local_iso(y, m, d, 23)))
        self.assertEqual([r["qid"] for r in same_day], [self.QID])
        next_midnight = self.attempted(self.envelope("committed", committedAt=local_iso(y, m, d + 1, 0)))
        self.assertEqual(next_midnight, [])

    def test_active_envelope_does_not_count(self):
        self.assertEqual(self.attempted(self.envelope("active", createdAt="2000-01-01T00:00:00Z")), [])

    def test_sm2_sources(self):
        y, m, d = self.date_parts()
        old = {"EE_EXAM_SM2_SCHEDULE_V1": json.dumps({self.QID: {"lastReviewed": "2000-01-01", "nextReviewDate": "2000-01-02"}})}
        self.assertEqual([r["qid"] for r in self.attempted(old)], [self.QID])
        null_review = {"EE_EXAM_SM2_SCHEDULE_V1": json.dumps({self.QID: {"lastReviewed": None}})}
        got = self.attempted(null_review)
        self.assertEqual([r["qid"] for r in got], [self.QID])
        self.assertIsNone(got[0]["lastAttemptAt"])
        late = {"EE_EXAM_SM2_SCHEDULE_V1": json.dumps({self.QID: {"lastReviewed": f"{y}-{m:02d}-{d + 1:02d}"}})}
        self.assertEqual(self.attempted(late), [])

    def test_practice_sources(self):
        y, m, d = self.date_parts()
        num = {"EE_EXAM_DAILY_PRACTICE_V1": json.dumps({"completionByQuestion": {self.QID: local_ms(y, m, d - 1 if d > 1 else 1) if d > 1 else 1000}})}
        self.assertEqual([r["qid"] for r in self.attempted(num)], [self.QID])
        obj_after = {"EE_EXAM_DAILY_PRACTICE_V1": json.dumps({"completionByQuestion": {self.QID: {"completedAt": local_ms(y, m, d + 2), "rating": 3}}})}
        self.assertEqual(self.attempted(obj_after), [])

    def test_progress_status(self):
        for value, expected in ((1, 1), (2, 1), (0, 0)):
            storage = {"EE_EXAM_PROGRESS_V1": json.dumps({self.QID: value})}
            self.assertEqual(len(self.attempted(storage)), expected, value)

    def test_today_task_completed_codes(self):
        task = run_node("Object.values(DAILY_SCHEDULE.tasks).find(t => t.qids.some(q => ANSWER_CORRECTIONS[q]))")
        qid = next(q for q in task["qids"])
        corrected = [q for q in task["qids"] if run_node(f"!!answerCorrectionFor('{q}')")]
        self.assertTrue(corrected)
        storage = {"EE_EXAM_TODAY_TASK_V1": json.dumps({"completed": {task["code"]: "2000-01-01T00:00:00.000Z"}})}
        got = {r["qid"] for r in self.attempted(storage)}
        self.assertTrue(set(corrected) <= got)
        storage = {"EE_EXAM_TODAY_TASK_V1": json.dumps({"completed": {task["code"]: "2099-01-01T00:00:00.000Z"}})}
        got = {r["qid"] for r in self.attempted(storage)}
        self.assertFalse(set(corrected) & got)
        self.assertTrue(qid)

    def test_latest_timestamp_wins_across_sources(self):
        y, m, d = self.date_parts()
        storage = {
            "EE_EXAM_SM2_SCHEDULE_V1": json.dumps({self.QID: {"lastReviewed": "2000-01-01"}}),
            "EE_EXAM_DAILY_PRACTICE_V1": json.dumps({"completionByQuestion": {self.QID: local_ms(y, m, d + 2)}}),
            "EE_EXAM_PROGRESS_V1": json.dumps({self.QID: 1}),
        }
        self.assertEqual(self.attempted(storage), [])

    def test_malformed_json_skipped(self):
        storage = {
            "EE_EXAM_ATTEMPT_ENVELOPES_V1": "{not json",
            "EE_EXAM_SM2_SCHEDULE_V1": "[1,2",
            "EE_EXAM_DAILY_PRACTICE_V1": "null",
            "EE_EXAM_PROGRESS_V1": "\"x\"",
            "GK_EXAM_PROGRESS_V1": "[]",
            "EE_EXAM_TODAY_TASK_V1": "{\"completed\": 5}",
        }
        self.assertEqual(self.attempted(storage), [])
        # one bad source must not hide a good one
        storage["EE_EXAM_PROGRESS_V1"] = json.dumps({self.QID: 2})
        self.assertEqual([r["qid"] for r in self.attempted(storage)], [self.QID])

    def test_non_corrected_qid_ignored(self):
        storage = {"EE_EXAM_PROGRESS_V1": json.dumps({"EE-999-99-9": 1})}
        self.assertEqual(self.attempted(storage), [])


class TestBuildWiring(unittest.TestCase):
    def test_build_orders_files(self):
        text = (WORKSPACE / "scripts/build_workbench.py").read_text(encoding="utf-8")
        data = text.index("'src/data/answerCorrections.generated.js'")
        comp = text.index("'src/components/answerCorrectionNotice.js'")
        self.assertLess(data, comp)
        self.assertLess(comp, text.index("'src/components/reviewPage.js'"))
        self.assertLess(comp, text.index("'src/components/solutionModal.js'"))
        self.assertLess(comp, text.index("'src/components/questionList.js'"))
        self.assertLess(text.index("'src/data/dailySchedule.generated.js'"), comp)

    def test_index_contains_component_and_host(self):
        html = (WORKSPACE / "index.html").read_text(encoding="utf-8")
        self.assertIn("// === src/components/answerCorrectionNotice.js ===", html)
        self.assertIn("const ANSWER_CORRECTIONS =", html)
        self.assertIn('id="review-corrections"', html)
        self.assertIn("insertAnswerCorrectionBanner(rightPane, currentModalQid)", html)
        self.assertIn("answerCorrectionBadgeHtml(qid)", html)

    def test_package_check_runs_generator(self):
        pkg = json.loads((WORKSPACE / "package.json").read_text(encoding="utf-8"))
        self.assertIn("build_answer_corrections.py", pkg["scripts"]["check"])


if __name__ == "__main__":
    unittest.main()
