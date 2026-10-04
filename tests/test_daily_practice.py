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
            ["node", "-"], input=script, cwd=WORKSPACE, capture_output=True, text=True,
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

    def test_legacy_session_is_migrated_to_named_view_reveal_and_dual_scroll_state(self):
        key = "EE_EXAM_DAILY_PRACTICE_V1"
        legacy = {
            "version": 1, "completionByQuestion": {}, "activeSession": {
                "category": "PE", "subjectId": "01", "questionIds": ["q1"],
                "currentIndex": 0, "revealedByQuestion": {"q1": True},
                "scrollByQuestion": {"q1": 120}, "createdAt": "2026-09-06T00:00:00.000Z",
            }
        }
        result = self._run("loadDailyPracticeStore()", {key: json.dumps(legacy)})["result"]
        session = result["state"]["activeSession"]
        self.assertEqual(session["viewByQuestion"]["q1"], "question")
        self.assertEqual(session["revealLevelByQuestion"]["q1"], 0)
        self.assertEqual(session["scrollByQuestion"]["q1"], {"question": 120, "solution": 0})
        self.assertEqual(session["modalByQuestion"]["q1"], {
            "leftScroll": 0, "rightScroll": 0, "subQuestion": 0, "revealStep": 0, "pane": "question", "open": False,
        })

    def test_modal_reader_state_is_per_question_and_round_trips(self):
        expression = """(() => {
          const session=createPracticeSession('PE','01',['q1','q2'],{now:1234});
          session.modalByQuestion.q1={leftScroll:120,rightScroll:640,subQuestion:2,revealStep:3,pane:'solution',open:true};
          const saved=savePracticeSession(session);
          return {saved,session:loadPracticeSession().session};
        })()"""
        result = self._run(expression)["result"]
        self.assertTrue(result["saved"]["ok"])
        self.assertEqual(result["session"]["modalByQuestion"]["q1"]["rightScroll"], 640)
        self.assertEqual(result["session"]["modalByQuestion"]["q1"]["revealStep"], 3)
        self.assertEqual(result["session"]["modalByQuestion"]["q2"]["rightScroll"], 0)


class TestWeightedPracticeQueue(TestDailyPractice):
    """WP5a: 依目標分配 = weighted random without replacement, PE only, 7-day avoidance."""

    POOL = [
        {"id": "EE-w3a", "w": 3}, {"id": "EE-w3b", "w": 3}, {"id": "EE-w1", "w": 1},
        {"id": "EE-w05", "w": 0.5}, {"id": "EE-w0", "w": 0}, {"id": "GK-x", "w": 3},
    ]

    def weighted(self, random_expr, extra="", pool=None, count=3):
        pool = pool if pool is not None else self.POOL
        expression = (
            "(() => { const pool = " + json.dumps(pool) + "; const W = {}; pool.forEach(p => W[p.id] = p.w); "
            "return createWeightedPracticeQueue(pool.map(p => ({id:p.id, subjectId:'01'})), "
            "{count:" + str(count) + ", now:100 * 86400000, weightOf: id => W[id], random: " + random_expr + extra + "}); })()"
        )
        return self._run(expression)["result"]

    def test_deterministic_draw_follows_weights_without_replacement(self):
        # total weight 7.5 over [3, 3, 1, 0.5]; zero-weight and GK items are never candidates.
        self.assertEqual(self.weighted("() => 0"), ["EE-w3a", "EE-w3b", "EE-w1"])
        # 0.5 * 7.5 = 3.75 -> skips w3a(3), lands in w3b; next: 0.5 * 4.5 = 2.25 -> w3a; then 0.5 * 1.5 = 0.75 -> w1
        self.assertEqual(self.weighted("() => 0.5"), ["EE-w3b", "EE-w3a", "EE-w1"])
        # highest value picks the last candidate each time
        self.assertEqual(self.weighted("() => 0.9999"), ["EE-w05", "EE-w1", "EE-w3b"])

    def test_never_returns_duplicates_zero_weight_or_non_pe(self):
        for value in ("0", "0.13", "0.37", "0.61", "0.99"):
            ids = self.weighted(f"() => {value}")
            self.assertEqual(len(ids), 3)
            self.assertEqual(len(set(ids)), 3)
            self.assertNotIn("EE-w0", ids)
            self.assertNotIn("GK-x", ids)

    def test_recent_completions_are_excluded_from_weighted_pool(self):
        # EE-w3a completed 1 day ago; the other three candidates remain -> exactly the pool of 3.
        ids = self.weighted("() => 0", extra=", completionByQuestion: {'EE-w3a': 99 * 86400000}")
        self.assertNotIn("EE-w3a", ids)
        self.assertEqual(sorted(ids), ["EE-w05", "EE-w1", "EE-w3b"])
        # completed exactly 7 days ago is eligible again
        ids = self.weighted("() => 0", extra=", completionByQuestion: {'EE-w3a': 93 * 86400000}")
        self.assertIn("EE-w3a", ids)

    def test_falls_back_to_plain_random_when_fewer_than_three_weighted_candidates(self):
        pool = [{"id": "EE-a", "w": 3}, {"id": "EE-b", "w": 0}, {"id": "EE-c", "w": 0}, {"id": "EE-d", "w": 0}]
        ids = self.weighted("() => 0.3", pool=pool)
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(set(ids)), 3)
        self.assertTrue(set(ids).issubset({"EE-a", "EE-b", "EE-c", "EE-d"}))

    def test_uses_study_plan_weights_by_default(self):
        expression = (
            "(() => { const qs = [{id:'EE-114-01-3', subjectId:'01'}, {id:'EE-114-01-1', subjectId:'01'}, "
            "{id:'EE-114-02-1', subjectId:'02'}, {id:'EE-114-02-2', subjectId:'02'}]; "
            "globalThis.practiceWeightFor = id => (id.endsWith('-1') ? 3 : 1); "
            "return createWeightedPracticeQueue(qs, {count:3, now: 1e12, random: () => 0}); })()"
        )
        ids = self._run(expression)["result"]
        # pool weights [1, 3, 3, 1] in input order; random()=0 always takes the first remaining item
        self.assertEqual(ids, ["EE-114-01-3", "EE-114-01-1", "EE-114-02-1"])


if __name__ == "__main__":
    unittest.main()
