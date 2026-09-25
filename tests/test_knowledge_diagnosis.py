# -*- coding: utf-8 -*-
"""Deterministic and fail-closed diagnosis contract tests."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestKnowledgeDiagnosis(unittest.TestCase):
    def _run(self, expression):
        source = (ROOT / "src/domain/knowledgeDiagnosis.js").read_text(encoding="utf-8")
        script = f"""
const vm = require('vm');
const context = {{console}};
vm.createContext(context);
vm.runInContext({json.dumps(source, ensure_ascii=False)}, context);
const result = vm.runInContext({json.dumps(expression, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(result));
"""
        completed = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def _graph(self):
        return {
            "graphRevision": "kg-v1-test",
            "nodes": {
                "pe-procedure": {"nodeId": "pe-procedure", "nodeType": "procedure", "title": "標準解法流程", "examFamily": "PE", "lifecycle": "active", "coreFormula": "先列已知量與未知量", "keyTrap": "不要跳過適用條件"},
                "pe-mechanism": {"nodeId": "pe-mechanism", "nodeType": "mechanism", "title": "核心機制", "examFamily": "PE", "lifecycle": "active", "coreFormula": "V=ZI", "keyTrap": "注意相量方向"},
                "pe-prerequisite": {"nodeId": "pe-prerequisite", "nodeType": "mechanism", "title": "前置概念", "examFamily": "PE", "lifecycle": "active"},
                "gk-mechanism": {"nodeId": "gk-mechanism", "nodeType": "mechanism", "title": "GK 概念", "examFamily": "GK", "lifecycle": "active"},
            },
            "edges": [
                {"from": "pe-prerequisite", "relation": "prerequisite", "to": "pe-mechanism", "why": "先具備前置概念。", "confidence": 0.9, "evidence": ["test:edge"], "reviewStatus": "approved"},
                {"from": "pe-mechanism", "relation": "enables", "to": "pe-procedure", "why": "機制支撐解法流程。", "confidence": 0.9, "evidence": ["test:edge"], "reviewStatus": "approved"},
            ],
            "questionLinks": {
                "PE:EE-114-01-2": {"qid": "EE-114-01-2", "examFamily": "PE", "nodeIds": ["pe-procedure", "pe-mechanism"], "confidence": 0.95, "evidence": ["test:link"], "reviewStatus": "approved"},
                "GK:GK-114-01-1": {"qid": "GK-114-01-1", "examFamily": "GK", "nodeIds": ["gk-mechanism"], "confidence": 0.95, "evidence": ["test:link"], "reviewStatus": "approved"},
            },
        }

    def test_committed_conceptual_error_is_bounded_and_deterministic(self):
        graph = json.dumps(self._graph(), ensure_ascii=False)
        expression = f"""
const graph={graph};
const input={{id:'EE-114-01-2',examFamily:'PE'}};
const assessment={{attemptId:'a1',attemptStatus:'committed',rating:1,errorType:'起手式不會',graphRevision:'kg-v1-test'}};
const first=diagnose(input,assessment,graph,{{lastAchieved:1}});
const second=diagnose(input,assessment,graph,{{lastAchieved:1}});
({{first,second}})
"""
        result = self._run(expression)
        self.assertEqual(result["first"], result["second"])
        self.assertEqual(result["first"]["status"], "mapped")
        self.assertLessEqual(len(result["first"]["likelyQuestions"]), 3)
        self.assertLessEqual(len(result["first"]["likelyQuestions"]), 3)
        self.assertIsNotNone(result["first"]["firstPrerequisiteGap"])
        self.assertTrue(result["first"]["needsConfirmation"])
        self.assertTrue(all(item["why"] for item in result["first"]["likelyQuestions"]))
        self.assertEqual(result["first"]["actionPlan"]["targetNodeId"], "pe-procedure")
        self.assertTrue(result["first"]["actionPlan"]["steps"])
        self.assertEqual(result["first"]["actionPlan"]["coreFormula"], "先列已知量與未知量")
        self.assertIn("適用條件", result["first"]["actionPlan"]["keyTrap"])

    def test_calculation_only_error_does_not_assert_conceptual_weakness(self):
        graph = json.dumps(self._graph(), ensure_ascii=False)
        result = self._run(f"diagnose({{id:'EE-114-01-2',examFamily:'PE'}},{{attemptId:'a2',attemptStatus:'committed',rating:1,errorType:'計算錯',graphRevision:'kg-v1-test'}},{graph},{{lastAchieved:1}})")
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["likelyQuestions"], [])
        self.assertIsNone(result["firstPrerequisiteGap"])
        self.assertTrue(result["needsConfirmation"])
        self.assertEqual(result["reasonCode"], "calculation-only")
        self.assertEqual(result["actionPlan"]["errorType"], "計算錯")
        self.assertEqual(result["actionPlan"]["targetNodeId"], "pe-procedure")
        self.assertGreaterEqual(len(result["actionPlan"]["steps"]), 3)

    def test_active_attempt_and_unknown_mapping_fail_closed(self):
        graph = json.dumps(self._graph(), ensure_ascii=False)
        active = self._run("diagnose({id:'EE-114-01-2',examFamily:'PE'},{attemptId:'a3',attemptStatus:'active',rating:1,errorType:'觀念混淆',graphRevision:'kg-v1-test'}," + graph + ",null)")
        unknown = self._run("diagnose({id:'EE-114-99-9',examFamily:'PE'},{attemptId:'a4',attemptStatus:'committed',rating:1,errorType:'觀念混淆',graphRevision:'kg-v1-test'}," + graph + ",null)")
        self.assertEqual(active["reasonCode"], "attempt-not-committed")
        self.assertEqual(active["likelyQuestions"], [])
        self.assertEqual(unknown["reasonCode"], "no-approved-question-link")
        self.assertEqual(unknown["likelyQuestions"], [])

    def test_cross_family_link_is_not_leaked_into_pe_diagnosis(self):
        graph = self._graph()
        graph["questionLinks"]["PE:EE-114-01-3"] = {
            "qid": "EE-114-01-3", "examFamily": "PE", "nodeIds": ["gk-mechanism"],
            "confidence": 0.95, "evidence": ["test:cross"], "reviewStatus": "approved",
        }
        result = self._run(
            f"diagnose({{id:'EE-114-01-3',examFamily:'PE'}},{{attemptId:'a5',attemptStatus:'committed',rating:1,errorType:'觀念混淆',graphRevision:'kg-v1-test'}},{json.dumps(graph, ensure_ascii=False)},null)"
        )
        self.assertEqual(result["reasonCode"], "cross-family-link")
        self.assertEqual(result["likelyQuestions"], [])


if __name__ == "__main__":
    unittest.main()
