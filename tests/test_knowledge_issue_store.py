# -*- coding: utf-8 -*-
"""Append-only issue event, idempotence, capacity and family isolation tests."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestKnowledgeIssueStore(unittest.TestCase):
    def _run(self, expression, setup=""):
        source = (ROOT / "src/state/knowledgeIssueStore.js").read_text(encoding="utf-8")
        script = f"""
const vm = require('vm');
const data = {{}};
const localStorage = {{
  getItem:key=>Object.prototype.hasOwnProperty.call(data,key) ? data[key] : null,
  setItem:(key,value)=>{{data[key]=String(value);}},
  removeItem:key=>{{delete data[key];}},
}};
const context = {{console, localStorage}};
vm.createContext(context);
vm.runInContext({json.dumps(source, ensure_ascii=False)}, context);
vm.runInContext({json.dumps(setup, ensure_ascii=False)}, context);
const result = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify({{result,data}}));
"""
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def _base_setup(self):
        return r"""
globalThis.CANONICAL_KNOWLEDGE_GRAPH={graphRevision:'kg-v1-test',nodes:{
  'pe-node':{nodeId:'pe-node',examFamily:'PE',lifecycle:'active'},
  'gk-node':{nodeId:'gk-node',examFamily:'GK',lifecycle:'active'}
}};
localStorage.setItem('EE_EXAM_ATTEMPT_ENVELOPES_V1',JSON.stringify({schemaVersion:'learning-attempts.v1',attempts:{'a1':{sessionId:'a1',status:'committed',qid:'EE-114-01-2',examFamily:'PE',sourceMode:'due-review'}}}));
"""

    def test_confirm_is_idempotent_and_keeps_revision_header(self):
        expression = r"""
(() => {
  const event={attemptId:'a1',qid:'EE-114-01-2',examFamily:'PE',rating:1,errorType:'觀念混淆',eventType:'confirm',primaryKnowledgeNodeId:'pe-node',secondaryKnowledgeNodeIds:['pe-node'],systemTopNodeId:'pe-node',candidateCount:1,selectedCandidateRank:1,diagnosisConfidence:.9,diagnosisVersion:'knowledge-diagnosis.v1',graphRevisionRef:'kg-v1-test'};
  const first=appendKnowledgeIssueEvent(event);
  const second=appendKnowledgeIssueEvent(event);
  const log=JSON.parse(localStorage.getItem(PE_KNOWLEDGE_ISSUE_KEY));
  return {first,second,count:log.events.length,revision:log.graphRevisions,event:log.events[0]};
})()
"""
        payload = self._run(expression, self._base_setup())["result"]
        self.assertTrue(payload["first"]["ok"])
        self.assertFalse(payload["first"]["duplicate"])
        self.assertTrue(payload["second"]["duplicate"])
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["revision"], ["kg-v1-test"])
        self.assertEqual(payload["event"]["graphRevisionRef"], 0)
        self.assertEqual(payload["event"]["secondaryKnowledgeNodeIds"], ["pe-node"])

    def test_correction_appends_and_supersedes_without_mutating_original(self):
        expression = r"""
(() => {
  const base={attemptId:'a1',qid:'EE-114-01-2',examFamily:'PE',rating:1,errorType:'觀念混淆',eventType:'confirm',primaryKnowledgeNodeId:'pe-node',candidateCount:2,diagnosisConfidence:.8,diagnosisVersion:'knowledge-diagnosis.v1',graphRevisionRef:'kg-v1-test'};
  const first=appendKnowledgeIssueEvent(base);
  const correction=appendKnowledgeIssueEvent(Object.assign({},base,{eventType:'correct',primaryKnowledgeNodeId:'pe-node',customText:'修正後的說明'}));
  const log=JSON.parse(localStorage.getItem(PE_KNOWLEDGE_ISSUE_KEY));
  return {first,correction,events:log.events};
})()
"""
        payload = self._run(expression, self._base_setup())["result"]
        self.assertTrue(payload["correction"]["ok"])
        self.assertEqual(len(payload["events"]), 2)
        self.assertEqual(payload["events"][0]["eventType"], "confirm")
        self.assertEqual(payload["events"][1]["eventType"], "correct")
        self.assertEqual(payload["events"][1]["supersedesEventId"], payload["events"][0]["eventId"])

    def test_unknown_outcome_has_no_node_and_cross_family_is_rejected(self):
        expression = r"""
(() => {
  const unknown=appendKnowledgeIssueEvent({attemptId:'a1',qid:'EE-114-01-2',examFamily:'PE',rating:1,errorType:'觀念混淆',eventType:'none-of-above',customText:'我遇到一個未知的邊界。',candidateCount:2,diagnosisConfidence:.4,diagnosisVersion:'knowledge-diagnosis.v1',graphRevisionRef:'kg-v1-test'});
  const before=localStorage.getItem(PE_KNOWLEDGE_ISSUE_KEY);
  const cross=appendKnowledgeIssueEvent({attemptId:'a1',qid:'EE-114-01-2',examFamily:'GK',rating:1,eventType:'confirm',primaryKnowledgeNodeId:'gk-node',candidateCount:1,diagnosisConfidence:.9,diagnosisVersion:'knowledge-diagnosis.v1',graphRevisionRef:'kg-v1-test'});
  return {unknown,cross,before,after:localStorage.getItem(PE_KNOWLEDGE_ISSUE_KEY)};
})()
"""
        payload = self._run(expression, self._base_setup())["result"]
        self.assertTrue(payload["unknown"]["ok"])
        self.assertIsNone(payload["unknown"]["event"]["primaryKnowledgeNodeId"])
        self.assertEqual(payload["cross"]["code"], "family_mismatch")
        self.assertEqual(payload["before"], payload["after"])

    def test_uncommitted_and_capacity_fail_before_changing_log(self):
        expression = r"""
(() => {
  const event={attemptId:'a1',qid:'EE-114-01-2',examFamily:'PE',rating:1,eventType:'skip',candidateCount:0,diagnosisConfidence:0,diagnosisVersion:'knowledge-diagnosis.v1',graphRevisionRef:'kg-v1-test'};
  const first=appendKnowledgeIssueEvent(event,{maxEvents:1});
  const before=localStorage.getItem(PE_KNOWLEDGE_ISSUE_KEY);
  const second=appendKnowledgeIssueEvent(Object.assign({},event,{attemptId:'a2'}),{maxEvents:1});
  const after=localStorage.getItem(PE_KNOWLEDGE_ISSUE_KEY);
  localStorage.setItem('EE_EXAM_ATTEMPT_ENVELOPES_V1',JSON.stringify({schemaVersion:'learning-attempts.v1',attempts:{'a3':{sessionId:'a3',status:'active',qid:'EE-114-01-2',examFamily:'PE',sourceMode:'due-review'}}}));
  const active=appendKnowledgeIssueEvent(Object.assign({},event,{attemptId:'a3'}));
  return {first,second,active,before,after};
})()
"""
        payload = self._run(expression, self._base_setup())["result"]
        self.assertTrue(payload["first"]["ok"])
        self.assertEqual(payload["second"]["code"], "capacity_events")
        self.assertFalse(payload["active"]["ok"])
        self.assertEqual(payload["active"]["code"], "attempt_not_committed")
        self.assertEqual(payload["before"], payload["after"])


if __name__ == "__main__":
    unittest.main()
