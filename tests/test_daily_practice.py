# -*- coding: utf-8 -*-
"""公共測試：每日練習抽題與練習紀錄儲存契約。"""

import json
import subprocess
import unittest
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
STORE_SOURCE = WORKSPACE / "src/state/practiceStore.js"


class TestDailyPractice(unittest.TestCase):
    def _run(self, expression, storage=None):
        source = STORE_SOURCE.read_text(encoding="utf-8") if STORE_SOURCE.exists() else ""
        storage_json = json.dumps(storage or {}, ensure_ascii=False)
        script = f"""
const vm = require('vm');
const data = {storage_json};
const localStorage = {{
  getItem: key => Object.prototype.hasOwnProperty.call(data, key) ? data[key] : null,
  setItem: (key, value) => {{ data[key] = String(value); }},
}};
const context = {{ console, localStorage }};
vm.createContext(context);
vm.runInContext({json.dumps(source + chr(10) + 'globalThis.__result = (' + expression + ');', ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify({{result: context.__result, storage: data}}));
"""
        completed = subprocess.run(
            ["node", "-e", script], cwd=WORKSPACE, capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    @staticmethod
    def questions():
        return [
            {"id": "EE-a", "subjectId": "01"},
            {"id": "EE-b", "subjectId": "01"},
            {"id": "EE-c", "subjectId": "01"},
            {"id": "EE-d", "subjectId": "01"},
            {"id": "EE-e", "subjectId": "02"},
        ]

    def test_queue_defaults_to_three_unique_questions_in_subject_scope(self):
        expression = (
            "(() => { const qs = " + json.dumps(self.questions(), ensure_ascii=False) + "; "
            "const result = createDailyPracticeQueue(qs, {subjectId:'01', now:1000000, random:() => 0.4}); "
            "return {ids:result, unique:new Set(result).size}; })()"
        )
        result = self._run(expression)["result"]
        self.assertEqual(len(result["ids"]), 3)
        self.assertEqual(result["unique"], 3)
        self.assertTrue(set(result["ids"]).issubset({"EE-a", "EE-b", "EE-c", "EE-d"}))

    def test_queue_uses_actual_count_when_only_one_or_two_candidates_exist(self):
        expression = (
            "(() => { const qs = " + json.dumps(self.questions()[:2], ensure_ascii=False) + "; "
            "return createDailyPracticeQueue(qs, {subjectId:'01', count:3, random:() => 0.2}); })()"
        )
        self.assertEqual(len(self._run(expression)["result"]), 2)
        expression = (
            "(() => { const qs = " + json.dumps(self.questions()[:1], ensure_ascii=False) + "; "
            "return createDailyPracticeQueue(qs, {subjectId:'01', count:3, random:() => 0.2}); })()"
        )
        self.assertEqual(len(self._run(expression)["result"]), 1)

    def test_random_source_can_produce_different_legal_combinations(self):
        qs = self.questions()
        expression = (
            "(() => { const qs = " + json.dumps(qs, ensure_ascii=False) + "; "
            "const a = createDailyPracticeQueue(qs, {subjectId:'01', count:2, random:() => 0.01}); "
            "let i=0; const b = createDailyPracticeQueue(qs, {subjectId:'01', count:2, random:() => (++i % 3) / 3}); "
            "return {a,b}; })()"
        )
        result = self._run(expression)["result"]
        self.assertNotEqual(result["a"], result["b"])
        self.assertEqual(len(set(result["a"])), 2)
        self.assertEqual(len(set(result["b"])), 2)

    def test_recent_completion_is_avoided_and_exactly_seven_days_is_eligible(self):
        now = 8 * 24 * 60 * 60 * 1000
        week = 7 * 24 * 60 * 60 * 1000
        qs = self.questions()[:3]
        completions = {"EE-a": now - week + 1, "EE-b": now - week, "EE-c": now - 2 * 60 * 60 * 1000}
        expression = (
            "(() => { const qs = " + json.dumps(qs, ensure_ascii=False) + "; const done = "
            + json.dumps(completions, ensure_ascii=False)
            + "; return createDailyPracticeQueue(qs, {subjectId:'01', count:2, now:"
            + str(now)
            + ", completionByQuestion:done, random:() => 0}); })()"
        )
        result = self._run(expression)["result"]
        self.assertIn("EE-b", result)
        self.assertNotIn("EE-c", result)

    def test_recent_fallback_is_oldest_first_when_priority_pool_is_short(self):
        now = 10 * 24 * 60 * 60 * 1000
        week = 7 * 24 * 60 * 60 * 1000
        qs = self.questions()[:4]
        completions = {
            "EE-a": now - week + 1,
            "EE-b": now - week + 2,
            "EE-c": now - 2 * 60 * 60 * 1000,
            "EE-d": now - 1 * 60 * 60 * 1000,
        }
        expression = (
            "(() => { const qs = " + json.dumps(qs, ensure_ascii=False) + "; return createDailyPracticeQueue(qs, "
            + "{subjectId:'01', count:3, now:" + str(now) + ", completionByQuestion:"
            + json.dumps(completions, ensure_ascii=False)
            + ", random:() => 0}); })()"
        )
        result = self._run(expression)["result"]
        self.assertEqual(result[0:2], ["EE-a", "EE-b"])
        self.assertEqual(result[2], "EE-c")

    def test_selection_maximizes_chapters_then_traceable_types(self):
        qs = [
            {"id": "q1"}, {"id": "q2"}, {"id": "q3"}, {"id": "q4"},
        ]
        expression = (
            "(() => { const qs = " + json.dumps(qs, ensure_ascii=False) + "; "
            "const chapter = {q1:'A',q2:'A',q3:'B',q4:'C'}; const type = {q1:'x',q2:'y',q3:'x',q4:'x'}; "
            "const ids = createDailyPracticeQueue(qs, {count:3, random:() => 0.1, chapterOf:q => chapter[q.id], typeOf:q => type[q.id]}); "
            "return ids; })()"
        )
        result = self._run(expression)["result"]
        self.assertEqual(len(set(result)), 3)
        self.assertEqual(len({{"q1": "A", "q2": "A", "q3": "B", "q4": "C"}[qid] for qid in result}), 3)

    def test_unknown_chapter_and_type_do_not_create_fake_diversity(self):
        qs = [{"id": "q1"}, {"id": "q2"}, {"id": "q3"}]
        expression = (
            "createDailyPracticeQueue(" + json.dumps(qs, ensure_ascii=False)
            + ", {count:3, random:() => 0.2})"
        )
        self.assertEqual(len(set(self._run(expression)["result"])), 3)

    def test_session_and_completion_share_one_versioned_storage_key(self):
        expression = "(() => { const s=createPracticeSession('PE','01',['q1','q2'],{now:1234}); const saved=savePracticeSession(s); const before=loadDailyPracticeStore(); const marked=markPracticeQuestionCompleted('q1', 2000); const after=loadDailyPracticeStore(); return {s,saved,before,marked,after}; })()"
        result = self._run(expression)["result"]
        self.assertEqual(result["s"]["questionIds"], ["q1", "q2"])
        self.assertEqual(result["s"]["currentIndex"], 0)
        self.assertEqual(result["after"]["state"]["completionByQuestion"]["q1"], 2000)
        self.assertEqual(result["after"]["state"]["activeSession"]["questionIds"], ["q1", "q2"])
        self.assertEqual(len(self._run(expression)["storage"]), 1)

    def test_opening_or_loading_does_not_record_completion(self):
        expression = "(() => { const s=createPracticeSession('PE','01',['q1'],{now:1234}); savePracticeSession(s); return loadDailyPracticeStore(); })()"
        result = self._run(expression)["result"]
        self.assertEqual(result["state"]["completionByQuestion"], {})

    def test_reload_preserves_session_order_and_corruption_does_not_overwrite(self):
        expression = "(() => { const s=createPracticeSession('PE','01',['q2','q1'],{now:1234}); savePracticeSession(s); const loaded=loadPracticeSession(); return loaded; })()"
        result = self._run(expression)["result"]
        self.assertEqual(result["session"]["questionIds"], ["q2", "q1"])

        key = "EE_EXAM_DAILY_PRACTICE_V1"
        corrupt = {key: "{not-json"}
        expression = "(() => { const read=loadDailyPracticeStore(); const save=savePracticeSession(createPracticeSession('PE','01',['q1'],{now:1})); return {read,save}; })()"
        result = self._run(expression, corrupt)
        self.assertIsNotNone(result["result"]["read"]["error"])
        self.assertFalse(result["result"]["save"]["ok"])
        self.assertEqual(result["storage"][key], "{not-json")

    def test_session_progress_and_completion_commit_in_one_write(self):
        expression = """(() => {
          const session=createPracticeSession('PE','01',['q1','q2'],{now:1234});
          savePracticeSession(session);
          session.currentIndex=1;
          session.revealedByQuestion.q1=true;
          session.scrollByQuestion.q1={question:120,solution:45};
          const result=commitPracticeProgress(session,'q1',2000);
          return {result,loaded:loadDailyPracticeStore()};
        })()"""
        result = self._run(expression)["result"]
        self.assertTrue(result["result"]["ok"])
        state = result["loaded"]["state"]
        self.assertEqual(state["activeSession"]["currentIndex"], 1)
        self.assertTrue(state["activeSession"]["revealedByQuestion"]["q1"])
        self.assertEqual(state["activeSession"]["scrollByQuestion"]["q1"]["solution"], 45)
        self.assertEqual(state["completionByQuestion"]["q1"], 2000)

    def test_corrupt_session_requires_explicit_safe_reset(self):
        key = "EE_EXAM_DAILY_PRACTICE_V1"
        result = self._run(
            "(() => { const reset=resetDailyPracticeStore(); return {reset,loaded:loadDailyPracticeStore()}; })()",
            {key: "{not-json"},
        )["result"]
        self.assertTrue(result["reset"]["ok"])
        self.assertEqual(result["loaded"]["state"], {
            "version": 1,
            "completionByQuestion": {},
            "activeSession": None,
        })

    def test_invalid_reveal_or_scroll_state_is_rejected(self):
        expression = """(() => {
          const session=createPracticeSession('PE','01',['q1'],{now:1234});
          session.revealedByQuestion.q1='yes';
          const reveal=savePracticeSession(session);
          session.revealedByQuestion.q1=true;
          session.scrollByQuestion.q1={question:-1,solution:0};
          const scroll=savePracticeSession(session);
          return {reveal,scroll};
        })()"""
        result = self._run(expression)["result"]
        self.assertFalse(result["reveal"]["ok"])
        self.assertFalse(result["scroll"]["ok"])


if __name__ == "__main__":
    unittest.main()
