# -*- coding: utf-8 -*-
"""Pure, explainable weakness projection tests."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestWeaknessProjection(unittest.TestCase):
    def _run(self, expression):
        source = (ROOT / "src/domain/weaknessProjection.js").read_text(encoding="utf-8")
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

    def stream(self):
        return {
            "schemaVersion": "knowledge-issue-events.v1",
            "examFamily": "PE",
            "graphRevisions": ["kg-v1-test"],
            "events": [
                {"eventId": "e1", "attemptId": "a1", "qid": "EE-114-01-1", "examFamily": "PE", "eventType": "confirm", "primaryKnowledgeNodeId": "old-node", "secondaryKnowledgeNodeIds": [], "rating": 1, "diagnosisConfidence": .8, "recordedAt": "2026-09-01T00:00:00.000Z", "graphRevisionRef": 0, "errorType": "觀念混淆", "evidence": ["evidence-old"]},
                {"eventId": "e2", "attemptId": "a1", "qid": "EE-114-01-1", "examFamily": "PE", "eventType": "correct", "primaryKnowledgeNodeId": "new-node", "secondaryKnowledgeNodeIds": ["prereq"], "rating": 1, "diagnosisConfidence": .9, "recordedAt": "2026-09-11T00:00:00.000Z", "graphRevisionRef": 0, "supersedesEventId": "e1", "errorType": "觀念混淆", "customText": "我卡在邊界條件", "evidence": ["evidence-new"]},
                {"eventId": "e3", "attemptId": "a2", "qid": "EE-114-01-2", "examFamily": "PE", "eventType": "none-of-above", "primaryKnowledgeNodeId": None, "secondaryKnowledgeNodeIds": [], "rating": 3, "diagnosisConfidence": .3, "recordedAt": "2026-09-12T00:00:00.000Z", "graphRevisionRef": 0, "errorType": None, "evidence": ["unknown-evidence"]},
                {"eventId": "e4", "attemptId": "a3", "qid": "EE-114-01-3", "examFamily": "PE", "eventType": "skip", "primaryKnowledgeNodeId": None, "secondaryKnowledgeNodeIds": [], "rating": 1, "diagnosisConfidence": 0, "recordedAt": "2026-07-01T00:00:00.000Z", "graphRevisionRef": 0},
                {"eventId": "g1", "attemptId": "g1", "qid": "GK-114-01-1", "examFamily": "GK", "eventType": "confirm", "primaryKnowledgeNodeId": "gk-node", "secondaryKnowledgeNodeIds": [], "rating": 1, "diagnosisConfidence": .9, "recordedAt": "2026-09-12T00:00:00.000Z", "graphRevisionRef": 0}
            ]
        }

    def graph(self):
        return {
            "graphRevision": "kg-v1-test",
            "nodes": {
                "old-node": {"nodeId": "old-node", "title": "舊問題", "nodeType": "mechanism", "examFamily": "PE", "lifecycle": "retired", "successorNodeIds": ["new-node"]},
                "new-node": {"nodeId": "new-node", "title": "新問題", "nodeType": "mechanism", "examFamily": "PE", "lifecycle": "active"},
                "prereq": {"nodeId": "prereq", "title": "前置問題", "nodeType": "procedure", "examFamily": "PE", "lifecycle": "active"},
                "gk-node": {"nodeId": "gk-node", "title": "GK 問題", "nodeType": "mechanism", "examFamily": "GK", "lifecycle": "active"}
            }
        }

    def test_rebuild_is_deterministic_and_migrations_are_resolved(self):
        original_events = json.dumps(self.stream()["events"], ensure_ascii=False, sort_keys=True)
        expression = f"""
const stream={json.dumps(self.stream(), ensure_ascii=False)};
const graph={json.dumps(self.graph(), ensure_ascii=False)};
const first=buildWeaknessProjection(stream,{{graph,range:'7d',now:'2026-09-13T00:00:00.000Z'}});
const second=buildWeaknessProjection(stream,{{graph,range:'7d',now:'2026-09-13T00:00:00.000Z'}});
({{first,second}})
"""
        result = self._run(expression)
        self.assertEqual(result["first"], result["second"])
        self.assertEqual(result["first"]["range"], "7d")
        self.assertEqual(result["first"]["timeAnchor"], "2026-09-13T00:00:00.000Z")
        self.assertEqual(result["first"]["timeAnchorMode"], "explicit")
        self.assertEqual(result["first"]["totals"]["effectiveEventCount"], 2)
        node = next(item for item in result["first"]["nodes"] if item["nodeId"] == "new-node")
        self.assertEqual(node["rawCount"], 1)
        self.assertEqual(node["distinctQids"], 1)
        self.assertEqual(node["historicalNodeIds"], ["old-node"])
        self.assertEqual(node["events"][0]["eventId"], "e2")
        self.assertEqual(node["events"][0]["evidence"], ["evidence-new"])
        self.assertEqual(node["events"][0]["customText"], "我卡在邊界條件")
        self.assertEqual(node["priorityVersion"], "weakness-priority.v1")
        self.assertIn("score", node["priority"])
        self.assertIn("reviewState", node)
        self.assertEqual(node["acceptanceMetrics"]["totalCount"], 1)
        self.assertEqual([item["eventId"] for item in node["supersessionChain"]], ["e1", "e2"])
        self.assertEqual([item["effective"] for item in node["supersessionChain"]], [False, True])
        self.assertEqual(node["traceStatus"], "complete")
        self.assertEqual(json.dumps(self.stream()["events"], ensure_ascii=False, sort_keys=True), original_events)
        self.assertEqual(result["first"]["pendingClassification"]["count"], 1)
        self.assertEqual(result["first"]["pendingClassification"]["events"][0]["qid"], "EE-114-01-2")

    def test_omitted_now_is_labeled_as_latest_event_replay(self):
        stream = {
            "examFamily": "PE",
            "events": [
                {
                    "eventId": "replay-e1",
                    "qid": "EE-114-01-1",
                    "examFamily": "PE",
                    "eventType": "confirm",
                    "primaryKnowledgeNodeId": "new-node",
                    "secondaryKnowledgeNodeIds": [],
                    "rating": 1,
                    "recordedAt": "2026-09-12T00:00:00.000Z",
                }
            ],
        }
        result = self._run(
            "buildWeaknessProjection(" + json.dumps(stream, ensure_ascii=False) + "," + json.dumps({"graph": self.graph(), "range": "all"}, ensure_ascii=False) + ")"
        )
        self.assertEqual(result["timeAnchor"], "2026-09-12T00:00:00.000Z")
        self.assertEqual(result["timeAnchorMode"], "latest-event-replay")

    def test_missing_correction_predecessor_is_reported_without_inventing_a_node(self):
        stream = {
            "examFamily": "PE",
            "events": [{
                "eventId": "orphan-correction",
                "qid": "EE-114-01-9",
                "examFamily": "PE",
                "eventType": "correct",
                "primaryKnowledgeNodeId": "new-node",
                "secondaryKnowledgeNodeIds": [],
                "rating": 1,
                "supersedesEventId": "missing-original",
                "recordedAt": "2026-09-12T00:00:00.000Z",
            }],
        }
        result = self._run(
            "buildWeaknessProjection(" + json.dumps(stream, ensure_ascii=False) + "," + json.dumps({"graph": self.graph(), "range": "all", "now": "2026-09-13T00:00:00.000Z"}, ensure_ascii=False) + ")"
        )
        node = result["nodes"][0]
        self.assertEqual(node["traceStatus"], "incomplete")
        self.assertEqual(node["missingEventIds"], ["missing-original"])
        self.assertEqual([item["eventId"] for item in node["supersessionChain"]], ["orphan-correction"])
        self.assertTrue(node["supersessionChain"][0]["effective"])

    def test_time_filters_explain_future_and_out_of_window_events(self):
        stream = {
            "examFamily": "PE",
            "events": [
                {
                    "eventId": "in-range",
                    "qid": "EE-114-01-1",
                    "examFamily": "PE",
                    "eventType": "confirm",
                    "primaryKnowledgeNodeId": "new-node",
                    "secondaryKnowledgeNodeIds": [],
                    "rating": 1,
                    "recordedAt": "2026-09-10T00:00:00.000Z",
                },
                {
                    "eventId": "future",
                    "qid": "EE-114-01-2",
                    "examFamily": "PE",
                    "eventType": "confirm",
                    "primaryKnowledgeNodeId": "new-node",
                    "secondaryKnowledgeNodeIds": [],
                    "rating": 1,
                    "recordedAt": "2026-09-14T00:00:00.000Z",
                },
                {
                    "eventId": "outside",
                    "qid": "EE-114-01-3",
                    "examFamily": "PE",
                    "eventType": "confirm",
                    "primaryKnowledgeNodeId": "old-node",
                    "secondaryKnowledgeNodeIds": [],
                    "rating": 1,
                    "recordedAt": "2026-09-01T00:00:00.000Z",
                },
            ],
        }
        result = self._run(
            "buildWeaknessProjection(" + json.dumps(stream, ensure_ascii=False) + "," + json.dumps({"graph": self.graph(), "range": "7d", "now": "2026-09-13T00:00:00.000Z"}, ensure_ascii=False) + ")"
        )
        self.assertEqual(result["totals"]["effectiveEventCount"], 1)
        self.assertEqual(
            {item["eventId"]: item["reason"] for item in result["excludedEvents"]},
            {"future": "FUTURE_THAN_TIME_ANCHOR", "outside": "BEFORE_TIME_CUTOFF"},
        )

    def test_priority_formula_is_versioned_and_orders_severity_and_recency(self):
        stream = {
            "schemaVersion": "knowledge-issue-events.v1",
            "examFamily": "PE",
            "graphRevisions": ["kg-v1-test"],
            "events": [
                {"eventId": "recent", "attemptId": "recent", "qid": "EE-114-01-1", "examFamily": "PE", "eventType": "confirm", "primaryKnowledgeNodeId": "new-node", "secondaryKnowledgeNodeIds": [], "rating": 1, "diagnosisConfidence": .9, "recordedAt": "2026-09-12T00:00:00.000Z", "graphRevisionRef": 0, "evidence": ["recent"]},
                {"eventId": "old", "attemptId": "old", "qid": "EE-114-01-2", "examFamily": "PE", "eventType": "confirm", "primaryKnowledgeNodeId": "old-node", "secondaryKnowledgeNodeIds": [], "rating": 5, "diagnosisConfidence": .9, "recordedAt": "2026-08-01T00:00:00.000Z", "graphRevisionRef": 0, "evidence": ["old"]},
            ],
        }
        graph = {
            "graphRevision": "kg-v1-test",
            "nodes": {
                "new-node": {"nodeId": "new-node", "title": "新問題", "nodeType": "mechanism", "examFamily": "PE", "lifecycle": "active"},
                "old-node": {"nodeId": "old-node", "title": "舊問題", "nodeType": "mechanism", "examFamily": "PE", "lifecycle": "active"},
            },
        }
        result = self._run(
            "buildWeaknessProjection(" + json.dumps(stream, ensure_ascii=False) + "," + json.dumps({"graph": graph, "range": "all", "now": "2026-09-13T00:00:00.000Z"}, ensure_ascii=False) + ")"
        )
        self.assertEqual(result["projectionVersion"], "weakness-projection.v1")
        self.assertEqual(result["nodes"][0]["nodeId"], "new-node")
        self.assertEqual(result["nodes"][0]["priorityVersion"], "weakness-priority.v1")
        self.assertGreater(result["nodes"][0]["priority"]["score"], result["nodes"][1]["priority"]["score"])

    def test_time_ranges_and_secondary_role_are_separate(self):
        expression = f"""
const stream={json.dumps(self.stream(), ensure_ascii=False)};
const graph={json.dumps(self.graph(), ensure_ascii=False)};
const recent=buildWeaknessProjection(stream,{{graph,range:'30d',now:'2026-09-13T00:00:00.000Z'}});
const all=buildWeaknessProjection(stream,{{graph,range:'all',now:'2026-09-13T00:00:00.000Z'}});
({{recent,all}})
"""
        result = self._run(expression)
        prerequisite = next(item for item in result["recent"]["nodes"] if item["nodeId"] == "prereq")
        self.assertEqual(prerequisite["role"], "secondary")
        self.assertEqual(prerequisite["rawCount"], 1)
        self.assertEqual(result["recent"]["totals"]["effectiveEventCount"], 2)
        self.assertEqual(result["all"]["totals"]["effectiveEventCount"], 3)
        self.assertEqual(result["all"]["pendingClassification"]["count"], 2)


if __name__ == "__main__":
    unittest.main()
