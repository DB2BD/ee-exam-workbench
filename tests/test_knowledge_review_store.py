# -*- coding: utf-8 -*-
"""Independent knowledge-node retrieval SRS tests."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestKnowledgeReviewStore(unittest.TestCase):
    def _run(self, expression, setup=""):
        source = (ROOT / "src/state/knowledgeReviewStore.js").read_text(encoding="utf-8")
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

    def setup(self):
        return r"""
globalThis.CANONICAL_KNOWLEDGE_GRAPH={graphRevision:'kg-v1-test',nodes:{
  'pe-node':{nodeId:'pe-node',title:'PE 機制',examFamily:'PE',lifecycle:'active'},
  'old-node':{nodeId:'old-node',title:'舊名稱',examFamily:'PE',lifecycle:'retired',successorNodeIds:['pe-node']},
  'split-node':{nodeId:'split-node',title:'待拆分',examFamily:'PE',lifecycle:'merged',successorNodeIds:['pe-node','other-node']},
  'other-node':{nodeId:'other-node',title:'另一機制',examFamily:'PE',lifecycle:'active'},
  'gk-node':{nodeId:'gk-node',title:'GK 機制',examFamily:'GK',lifecycle:'active'}
}};
"""

    def test_read_does_not_schedule_and_explicit_rating_is_auditable_and_idempotent(self):
        expression = r"""
(() => {
  const read=readKnowledgeReview('pe-node','PE',{now:'2026-09-13T00:00:00.000Z'});
  const before=localStorage.getItem(PE_KNOWLEDGE_REVIEW_KEY);
  const blocked=recordKnowledgeReview({nodeId:'pe-node',examFamily:'PE',rating:1,reviewEventId:'r1'},{now:'2026-09-13T00:00:00.000Z'});
  const first=recordKnowledgeReview({nodeId:'pe-node',examFamily:'PE',rating:1,reviewEventId:'r1',recallLevel:2},{explicitRecall:true,now:'2026-09-13T00:00:00.000Z'});
  const retry=recordKnowledgeReview({nodeId:'pe-node',examFamily:'PE',rating:1,reviewEventId:'r1',recallLevel:2},{explicitRecall:true,now:'2026-09-13T00:00:00.000Z'});
  const log=JSON.parse(localStorage.getItem(PE_KNOWLEDGE_REVIEW_KEY));
  return {read,before,blocked,first,retry,history:log.reviews['knowledge:PE:pe-node'].history,questionKey:localStorage.getItem('EE_EXAM_SM2_SCHEDULE_V1')};
})()
"""
        payload = self._run(expression, self.setup())["result"]
        self.assertIsNone(payload["read"])
        self.assertIsNone(payload["before"])
        self.assertEqual(payload["blocked"]["code"], "explicit_recall_required")
        self.assertTrue(payload["first"]["ok"])
        self.assertTrue(payload["retry"]["duplicate"])
        self.assertEqual(len(payload["history"]), 1)
        self.assertIsNone(payload["questionKey"])

    def test_lifecycle_migration_and_family_isolation(self):
        expression = r"""
(() => {
  const migrated=recordKnowledgeReview({nodeId:'old-node',examFamily:'PE',rating:5,reviewEventId:'old-r1'},{explicitRecall:true,now:'2026-09-13T00:00:00.000Z'});
  const split=recordKnowledgeReview({nodeId:'split-node',examFamily:'PE',rating:3,reviewEventId:'split-r1'},{explicitRecall:true,now:'2026-09-13T00:00:00.000Z'});
  const gk=recordKnowledgeReview({nodeId:'gk-node',examFamily:'GK',rating:1,reviewEventId:'gk-r1'},{explicitRecall:true,now:'2026-09-13T00:00:00.000Z'});
  return {migrated,split,gk,pe:localStorage.getItem(PE_KNOWLEDGE_REVIEW_KEY),gkLog:localStorage.getItem(GK_KNOWLEDGE_REVIEW_KEY)};
})()
"""
        payload = self._run(expression, self.setup())["result"]
        self.assertTrue(payload["migrated"]["ok"])
        self.assertEqual(payload["migrated"]["reviewId"], "knowledge:PE:pe-node")
        self.assertEqual(payload["migrated"]["migratedFrom"], "old-node")
        self.assertEqual(payload["split"]["code"], "lifecycle_split_requires_confirmation")
        self.assertTrue(payload["gk"]["ok"])
        self.assertNotIn("gk-node", payload["pe"])
        self.assertIn("gk-node", payload["gkLog"])


if __name__ == "__main__":
    unittest.main()
