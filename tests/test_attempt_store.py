# -*- coding: utf-8 -*-
"""單次學習提交：冪等、故障回復與考別路由契約。"""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    "src/state/store.js",
    "src/state/sm2Store.js",
    "src/state/practiceStore.js",
    "src/state/recallStore.js",
    "src/state/attemptStore.js",
]


class TestAttemptStore(unittest.TestCase):
    def _run(self, expression, failure=""):
        source = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in SOURCES if (ROOT / path).exists())
        script = f"""
const vm = require('vm');
const data = {{
  EE_EXAM_DAILY_PRACTICE_V1: JSON.stringify({{version:1,completionByQuestion:{{}},activeSession:{{category:'PE',subjectId:'01',questionIds:['EE-Q'],currentIndex:0,revealedByQuestion:{{'EE-Q':true}},viewByQuestion:{{'EE-Q':'solution'}},revealLevelByQuestion:{{'EE-Q':4}},scrollByQuestion:{{'EE-Q':{{question:0,solution:0}}}},createdAt:'2026-09-08T00:00:00.000Z'}}}})
}};
let failed = false;
const localStorage = {{
  getItem(key) {{ return Object.prototype.hasOwnProperty.call(data,key) ? data[key] : null; }},
  setItem(key,value) {{
    if ({json.dumps(failure)} && key === {json.dumps(failure)} && !failed) {{ failed=true; throw new Error('quota'); }}
    data[key]=String(value);
  }},
  removeItem(key) {{ delete data[key]; }}
}};
const document = {{getElementById:()=>null,body:{{appendChild(){{}}}}}};
const context = {{console,localStorage,document,setTimeout,clearTimeout}};
vm.createContext(context);
vm.runInContext({json.dumps(source, ensure_ascii=False)}, context);
vm.runInContext("globalThis.dailyPracticeState=loadDailyPracticeStore().state;", context);
const result = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify({{result,data}}));
"""
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_daily_failure_rolls_back_and_same_attempt_can_retry_once(self):
        expression = r"""
(() => {
  const payload={attemptId:'a1',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'daily-practice',rating:5,revealStep:4,recallEntry:true,errorType:null};
  const first=submitLearningAttempt(payload);
  const afterFailure={recall:getRecallState('EE-Q').attempts,practice:loadDailyPracticeStore().state.completionByQuestion};
  const second=submitLearningAttempt(payload);
  const duplicate=submitLearningAttempt(payload);
  return {first,afterFailure,second,duplicate,recall:getRecallState('EE-Q').attempts,practice:loadDailyPracticeStore().state.completionByQuestion};
})()
"""
        result = self._run(expression, "EE_EXAM_RECALL_V1")["result"]
        self.assertFalse(result["first"]["ok"])
        self.assertEqual(result["afterFailure"], {"recall": 0, "practice": {}})
        self.assertTrue(result["second"]["ok"])
        self.assertTrue(result["duplicate"]["duplicate"])
        self.assertEqual(result["recall"], 1)
        self.assertIn("EE-Q", result["practice"])

    def test_due_review_sm2_failure_does_not_leave_recall_or_progress(self):
        expression = r"""
submitLearningAttempt({attemptId:'a2',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'due-review',rating:5,revealStep:4,recallEntry:true,errorType:null})
"""
        output = self._run(expression, "EE_EXAM_SM2_SCHEDULE_V1")
        self.assertFalse(output["result"]["ok"])
        self.assertNotIn("EE_EXAM_RECALL_V1", output["data"])
        self.assertNotIn("EE_EXAM_PROGRESS_V1", output["data"])

    def test_same_attempt_with_different_rating_is_rejected(self):
        expression = r"""
(() => {
  const base={attemptId:'a3',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'due-review',rating:3,revealStep:4,recallEntry:true,errorType:null};
  const first=submitLearningAttempt(base);
  const conflict=submitLearningAttempt(Object.assign({},base,{rating:5}));
  return {first,conflict,repetitions:sm2Schedule['EE-Q'].repetitions};
})()
"""
        result = self._run(expression)["result"]
        self.assertTrue(result["first"]["ok"])
        self.assertEqual(result["conflict"]["code"], "attempt_conflict")
        self.assertEqual(result["repetitions"], 1)

    def test_failed_attempt_retry_cannot_change_payload(self):
        expression = r"""
(() => {
  const base={attemptId:'a7',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'daily-practice',rating:3,revealStep:4,recallEntry:true,errorType:null};
  const first=submitLearningAttempt(base);
  const changed=submitLearningAttempt(Object.assign({},base,{rating:5}));
  return {first,changed};
})()
"""
        result = self._run(expression, "EE_EXAM_RECALL_V1")["result"]
        self.assertFalse(result["first"]["ok"])
        self.assertEqual(result["changed"]["code"], "attempt_conflict")

    def test_corrupt_recall_storage_blocks_submission_without_overwrite(self):
        expression = r"""
(() => {
  localStorage.setItem(RECALL_STORAGE_KEY,'{broken');
  initRecallStore();
  const before=localStorage.getItem(RECALL_STORAGE_KEY);
  const result=submitLearningAttempt({attemptId:'a8',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'daily-practice',rating:5,revealStep:4,recallEntry:true,errorType:null});
  return {result,before,after:localStorage.getItem(RECALL_STORAGE_KEY)};
})()
"""
        result = self._run(expression)["result"]
        self.assertFalse(result["result"]["ok"])
        self.assertEqual(result["result"]["code"], "store_load_failed")
        self.assertEqual(result["before"], result["after"])

    def test_parseable_but_invalid_store_shapes_are_not_overwritten(self):
        expression = r"""
(() => {
  localStorage.setItem(RECALL_STORAGE_KEY,'[]'); initRecallStore();
  localStorage.setItem(SM2_STORAGE_KEY,'[]'); initSM2Store();
  const beforeRecall=localStorage.getItem(RECALL_STORAGE_KEY), beforeSM2=localStorage.getItem(SM2_STORAGE_KEY);
  const result=submitLearningAttempt({attemptId:'a9',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'due-review',rating:5,revealStep:4,recallEntry:true,errorType:null});
  return {result,beforeRecall,beforeSM2,afterRecall:localStorage.getItem(RECALL_STORAGE_KEY),afterSM2:localStorage.getItem(SM2_STORAGE_KEY)};
})()
"""
        result = self._run(expression)["result"]
        self.assertEqual(result["result"]["code"], "store_load_failed")
        self.assertEqual(result["beforeRecall"], result["afterRecall"])
        self.assertEqual(result["beforeSM2"], result["afterSM2"])

    def test_parseable_but_invalid_progress_is_not_overwritten(self):
        expression = r"""
(() => {
  localStorage.setItem('EE_EXAM_PROGRESS_V1','[]');
  const before=localStorage.getItem('EE_EXAM_PROGRESS_V1');
  const result=submitLearningAttempt({attemptId:'a10',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'due-review',rating:5,revealStep:4,recallEntry:true,errorType:null});
  return {result,before,after:localStorage.getItem('EE_EXAM_PROGRESS_V1')};
})()
"""
        result = self._run(expression)["result"]
        self.assertEqual(result["result"]["code"], "invalid_progress")
        self.assertEqual(result["before"], result["after"])

    def test_failed_rollback_keeps_journal_and_blocks_new_attempts(self):
        expression = r"""
(() => {
  let dataWriteStarted=false;
  const broken={
    getItem:key=>localStorage.getItem(key), removeItem:key=>localStorage.removeItem(key),
    setItem(key,value){
      if (key===RECALL_STORAGE_KEY) { dataWriteStarted=true; throw new Error('recall quota'); }
      if (dataWriteStarted && key===DAILY_PRACTICE_STORAGE_KEY) throw new Error('rollback quota');
      localStorage.setItem(key,value);
    }
  };
  const payload={attemptId:'a4',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'daily-practice',rating:5,revealStep:4,recallEntry:true,errorType:null};
  const first=submitLearningAttempt(payload,{storage:broken});
  const second=submitLearningAttempt(Object.assign({},payload,{attemptId:'a5'}),{storage:broken});
  return {first,second,journal:JSON.parse(localStorage.getItem(ATTEMPT_RECOVERY_KEY)),recall:getRecallState('EE-Q').attempts};
})()
"""
        result = self._run(expression)["result"]
        self.assertEqual(result["first"]["code"], "recovery_required")
        self.assertEqual(result["second"]["code"], "recovery_required")
        self.assertEqual(result["journal"]["phase"], "recovery_required")
        self.assertEqual(result["recall"], 0)

    def test_progress_uses_question_family_not_background_tab(self):
        expression = r"""
(() => {
  currentExamCategory='GK'; progressState={background:1};
  const result=submitLearningAttempt({attemptId:'a6',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'due-review',rating:5,revealStep:4,recallEntry:true,errorType:null});
  return {result,pe:JSON.parse(localStorage.getItem('EE_EXAM_PROGRESS_V1')),gk:localStorage.getItem('GK_EXAM_PROGRESS_V1'),memory:progressState};
})()
"""
        result = self._run(expression)["result"]
        self.assertTrue(result["result"]["ok"])
        self.assertEqual(result["pe"]["EE-Q"], 1)
        self.assertIsNone(result["gk"])
        self.assertEqual(result["memory"], {"background": 1})

    def test_rating_three_records_hint_assisted_level_not_full_reveal_level(self):
        expression = r"""
(() => {
  const result=submitLearningAttempt({attemptId:'a11',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'due-review',rating:3,revealStep:4,recallEntry:true,errorType:null});
  return {result,recall:getRecallState('EE-Q')};
})()
"""
        result = self._run(expression)["result"]
        self.assertTrue(result["result"]["ok"])
        self.assertEqual(result["recall"]["lastAchieved"], 2)

    def test_daily_completion_keeps_assessment_details_for_summary(self):
        result = self._run("""(() => {
          const result=submitLearningAttempt({attemptId:'summary',question:{id:'EE-Q',examFamily:'PE'},sourceMode:'daily-practice',rating:1,revealStep:4,recallEntry:true,errorType:'公式忘記'});
          return {result,completion:loadDailyPracticeStore().state.completionByQuestion['EE-Q']};
        })()""")["result"]
        self.assertEqual(result["completion"]["rating"], 1)
        self.assertEqual(result["completion"]["errorType"], "公式忘記")
        self.assertEqual(result["result"]["nextAction"]["results"][0]["qid"], "EE-Q")

    def test_daily_follow_up_is_idempotent_and_never_postpones_earlier_date(self):
        result = self._run("""(() => {
          const first=scheduleDailyPracticeFollowUp('EE-Q',{now:'2026-09-08T12:00:00+08:00'});
          const second=scheduleDailyPracticeFollowUp('EE-Q',{now:'2026-09-08T12:00:00+08:00'});
          const schedule=JSON.parse(localStorage.getItem(SM2_STORAGE_KEY))['EE-Q'];
          localStorage.setItem(SM2_STORAGE_KEY,JSON.stringify({'EE-EARLY':{repetitions:2,interval:0,easeFactor:2.4,lastReviewed:'2026-09-08',nextReviewDate:'2026-09-08'}}));
          const earlier=scheduleDailyPracticeFollowUp('EE-EARLY',{now:'2026-09-08T12:00:00+08:00'});
          const earlySchedule=JSON.parse(localStorage.getItem(SM2_STORAGE_KEY))['EE-EARLY'];
          return {first,second,schedule,earlier,earlySchedule};
        })()""")["result"]
        self.assertTrue(result["first"]["ok"])
        self.assertFalse(result["first"]["duplicate"])
        self.assertTrue(result["second"]["duplicate"])
        self.assertEqual(result["schedule"]["repetitions"], 0)
        self.assertEqual(result["schedule"]["nextReviewDate"], result["first"]["nextReviewDate"])
        self.assertTrue(result["earlier"]["duplicate"])
        self.assertEqual(result["earlySchedule"]["nextReviewDate"], "2026-09-08")
        self.assertEqual(result["earlySchedule"]["repetitions"], 2)


if __name__ == "__main__":
    unittest.main()
