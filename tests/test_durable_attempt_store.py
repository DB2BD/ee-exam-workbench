# -*- coding: utf-8 -*-
"""Durable attempt lifecycle tests, including a simulated reload boundary."""

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


class TestDurableAttemptStore(unittest.TestCase):
    def _run(self, expression):
        source = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in SOURCES)
        script = f"""
const vm = require('vm');
const source = {json.dumps(source, ensure_ascii=False)};
const data = {{}};
function makeContext() {{
  const localStorage = {{
    getItem(key) {{ return Object.prototype.hasOwnProperty.call(data, key) ? data[key] : null; }},
    setItem(key, value) {{ data[key] = String(value); }},
    removeItem(key) {{ delete data[key]; }},
  }};
  const context = {{console, localStorage, document: {{getElementById: () => null, body: {{appendChild(){{}}}}}}}};
  vm.createContext(context);
  vm.runInContext(source, context);
  if (typeof context.loadDailyPracticeStore === 'function') context.dailyPracticeState = context.loadDailyPracticeStore().state;
  return context;
}}
const firstContext = makeContext();
firstContext.reload = code => vm.runInContext(code, makeContext());
const result = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, firstContext);
process.stdout.write(JSON.stringify({{result, data}}));
"""
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_begin_or_resume_persists_one_active_session(self):
        result = self._run(r"""
(() => {
  const first = beginOrResume({sessionId:'session-1',qid:'EE-114-01-2',examFamily:'PE',sourceMode:'due-review'},{now:'2026-09-13T10:00:00Z'});
  const second = reload("beginOrResume({sessionId:'session-1',qid:'EE-114-01-2',examFamily:'PE',sourceMode:'due-review'},{now:'2026-09-13T10:01:00Z'})");
  return {first,second,stored:JSON.parse(localStorage.getItem(ATTEMPT_ENVELOPES_KEY))};
})()
""")
        self.assertTrue(result["result"]["first"]["ok"])
        self.assertEqual(result["result"]["first"]["status"], "active")
        self.assertTrue(result["result"]["second"]["duplicate"])
        self.assertEqual(len(result["result"]["stored"]["attempts"]), 1)
        self.assertEqual(result["result"]["stored"]["attempts"]["session-1"]["examFamily"], "PE")

    def test_submit_is_idempotent_across_reload_and_ack_is_idempotent(self):
        result = self._run(r"""
(() => {
  const payload={attemptId:'session-2',question:{id:'EE-114-01-2',examFamily:'PE'},sourceMode:'due-review',rating:5,revealStep:4,recallEntry:true,errorType:null};
  const first = submitLearningAttempt(payload);
  const committed = JSON.parse(localStorage.getItem(ATTEMPT_ENVELOPES_KEY)).attempts['session-2'];
  const second = reload("submit(" + JSON.stringify(payload) + ")");
  const firstAck = reload("ack({sessionId:'session-2'})");
  const secondAck = reload("ack({sessionId:'session-2'})");
  return {first,committed,second,firstAck,secondAck,repetitions:sm2Schedule['EE-114-01-2'].repetitions};
})()
""")
        payload = result["result"]
        self.assertTrue(payload["first"]["ok"])
        self.assertEqual(payload["committed"]["status"], "committed")
        self.assertTrue(payload["second"]["duplicate"])
        self.assertEqual(payload["firstAck"]["status"], "acknowledged")
        self.assertTrue(payload["secondAck"]["duplicate"])
        self.assertEqual(payload["repetitions"], 1)

    def test_recover_keeps_committed_result_after_reload_before_ack(self):
        result = self._run(r"""
(() => {
  const payload={attemptId:'session-3',question:{id:'EE-114-01-3',examFamily:'PE'},sourceMode:'due-review',rating:3,revealStep:4,recallEntry:true,errorType:null};
  const committed = submitLearningAttempt(payload);
  const recovered = reload("recover()");
  const resumed = reload("beginOrResume({sessionId:'session-3',qid:'EE-114-01-3',examFamily:'PE',sourceMode:'due-review'})");
  return {committed,recovered,resumed,stored:JSON.parse(localStorage.getItem(ATTEMPT_ENVELOPES_KEY)).attempts['session-3']};
})()
""")
        payload = result["result"]
        self.assertTrue(payload["committed"]["ok"])
        self.assertTrue(payload["recovered"]["ok"])
        self.assertEqual(payload["resumed"]["status"], "committed")
        self.assertEqual(payload["stored"]["status"], "committed")

    def test_failed_commit_exposes_no_committed_attempt_and_rejects_cross_family(self):
        result = self._run(r"""
(() => {
  const payload={attemptId:'session-4',question:{id:'EE-114-01-2',examFamily:'PE'},sourceMode:'due-review',rating:5,revealStep:4,recallEntry:true,errorType:null};
  let envelopeWrites=0;
  const broken={
    getItem:key=>localStorage.getItem(key),
    removeItem:key=>localStorage.removeItem(key),
    setItem(key,value){
      if (key===ATTEMPT_ENVELOPES_KEY && ++envelopeWrites > 1) throw new Error('commit quota');
      localStorage.setItem(key,value);
    }
  };
  const failed = submitLearningAttempt(payload,{storage:broken});
  const after = recover();
  const crossFamily = beginOrResume({sessionId:'session-4',qid:'EE-114-01-2',examFamily:'GK',sourceMode:'due-review'});
  const raw = localStorage.getItem(ATTEMPT_ENVELOPES_KEY);
  const stored = raw ? JSON.parse(raw).attempts['session-4'] : null;
  return {failed,after,crossFamily,stored};
})()
""")
        payload = result["result"]
        self.assertFalse(payload["failed"]["ok"])
        self.assertNotEqual((payload["stored"] or {}).get("status"), "committed")
        self.assertTrue(payload["after"]["ok"])
        self.assertIn(payload["crossFamily"]["code"], {"attempt_conflict", "family_mismatch"})


if __name__ == "__main__":
    unittest.main()
