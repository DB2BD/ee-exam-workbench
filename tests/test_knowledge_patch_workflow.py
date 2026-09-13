# -*- coding: utf-8 -*-
"""Offline context packet and revision-aware candidate workflow tests."""

import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import scripts.knowledge_patch_workflow as workflow
from scripts.knowledge_graph import validate_graph_directory
from scripts.knowledge_patch_workflow import (
    approve_candidate,
    build_context_packet,
    inspect_candidate,
    reject_candidate,
    rebase_candidate,
)


ROOT = Path(__file__).resolve().parents[1]


class TestKnowledgePatchWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph_dir = ROOT / "data/knowledge"
        cls.graph = json.loads(json.dumps(__import__("scripts.knowledge_patch_workflow", fromlist=["load_graph_bundle"]).load_graph_bundle(cls.graph_dir), ensure_ascii=False))
        cls.node_id = "ct-thevenin-norton"

    def candidate(self):
        node = self.graph["nodes"][self.node_id]
        updated = json.loads(json.dumps(node, ensure_ascii=False))
        updated["title"] = "戴維寧與諾頓等效定理（含驗算提醒）"
        updated["nodeRevisionHash"] = "candidate-ct-thevenin-v2"
        return {
            "schemaVersion": "knowledge-patch-candidate.v1",
            "candidateVersion": 1,
            "candidateId": "candidate-thevenin-1",
            "baseGraphRevision": self.graph["graphRevision"],
            "examFamily": "PE",
            "qid": "EE-114-01-2",
            "sourceIssueEventIds": ["issue-e1"],
            "intent": "補充受控源的驗算提醒",
            "likelyQuestions": ["EE-114-01-2"],
            "reuse": [self.node_id],
            "create": [],
            "update": [self.node_id],
            "questionLinks": [],
            "evidence": ["issue-e1", "src/data/knowledge/knowledge-dag.js"],
            "expectedNodeHashes": {self.node_id: node["nodeRevisionHash"]},
            "operations": {"upsertNodes": [updated], "addEdges": [], "upsertQuestionLinks": []},
        }

    def test_candidate_version_is_required_before_review(self):
        candidate = self.candidate()
        del candidate["candidateVersion"]
        report = inspect_candidate(candidate, self.graph)
        self.assertIn("CANDIDATE_VERSION", {error["code"] for error in report["errors"]})
        self.assertFalse(report["valid"])

    def test_context_packet_is_bounded_and_reproducible(self):
        issue = [{"eventId": "issue-e1", "attemptId": "a1", "qid": "EE-114-01-2", "examFamily": "PE", "eventType": "confirm", "primaryKnowledgeNodeId": self.node_id, "evidence": ["題目條件"]}]
        first = build_context_packet(self.graph, [self.node_id], issue, max_history=5)
        second = build_context_packet(self.graph, [self.node_id], issue, max_history=5)
        self.assertEqual(first, second)
        self.assertEqual(first["graphRevision"], self.graph["graphRevision"])
        self.assertEqual(first["issueHistory"][0]["eventId"], "issue-e1")
        self.assertLessEqual(first["payloadBytes"], 120000)
        self.assertIn("graphRevision", first["markdown"])

    def test_inspect_rejects_stale_hash_and_unsafe_pasted_text(self):
        stale = self.candidate()
        stale["baseGraphRevision"] = "kg-v1-stale"
        report = inspect_candidate(stale, self.graph)
        codes = {error["code"] for error in report["errors"]}
        self.assertIn("STALE_GRAPH_REVISION", codes)
        unsafe = self.candidate()
        unsafe["pastedText"] = "write this directly"
        report = inspect_candidate(unsafe, self.graph)
        self.assertIn("UNSAFE_ARBITRARY_TEXT", {error["code"] for error in report["errors"]})

    def test_reject_is_auditable_and_approve_rebases_into_new_revision_atomically(self):
        candidate = self.candidate()
        rebased = rebase_candidate(candidate, self.graph)
        self.assertTrue(rebased["ok"], rebased)
        self.assertEqual(rebased["candidate"]["baseGraphRevision"], self.graph["graphRevision"])
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            rejected = reject_candidate(candidate, root / "queue", "證據不足", reviewer_id="sol", reviewed_at="2026-09-13T10:00:00Z")
            self.assertEqual(rejected["status"], "rejected")
            rejected_record = json.loads((root / "queue/candidate-thevenin-1.review.json").read_text())
            self.assertEqual(rejected_record["reason"], "證據不足")
            self.assertEqual(rejected_record["reviewerId"], "sol")
            self.assertEqual(rejected_record["reviewedAt"], "2026-09-13T10:00:00Z")
            self.assertEqual(rejected_record["decision"], "rejected")
            self.assertEqual(rejected_record["candidateHash"], inspect_candidate(candidate, self.graph)["candidateHash"])
            approved = approve_candidate(candidate, self.graph, root / "revisions/candidate-thevenin-1", root / "queue", reviewer_id="sol", reviewed_at="2026-09-13T10:01:00Z", notes="已核對來源")
            self.assertEqual(approved["status"], "approved", approved)
            self.assertTrue(approved["graphRevision"].startswith("kg-v1-"))
            self.assertNotEqual(approved["graphRevision"], self.graph["graphRevision"])
            self.assertTrue((root / "revisions/candidate-thevenin-1/nodes.json").exists())
            approved_record = json.loads((root / "queue/candidate-thevenin-1.review.json").read_text())
            self.assertEqual(approved_record["status"], "approved")
            self.assertEqual(approved_record["decision"], "approved")
            self.assertEqual(approved_record["reviewerId"], "sol")
            self.assertEqual(approved_record["reviewedAt"], "2026-09-13T10:01:00Z")
            self.assertEqual(approved_record["notes"], "已核對來源")
            self.assertEqual(approved_record["candidateHash"], inspect_candidate(candidate, self.graph)["candidateHash"])
            self.assertEqual(approved_record["baseGraphRevision"], self.graph["graphRevision"])
            self.assertEqual(approved_record["graphRevision"], approved["graphRevision"])

    def test_cross_family_and_cycle_candidates_fail_without_writing(self):
        candidate = self.candidate()
        cross_node = json.loads(json.dumps(self.graph["nodes"][self.node_id], ensure_ascii=False))
        cross_node["nodeId"] = "gk-node"
        cross_node["examFamily"] = "GK"
        cross_node["nodeRevisionHash"] = "gk-hash"
        candidate["operations"]["upsertNodes"].append(cross_node)
        candidate["operations"]["addEdges"] = [{"from": "ct-thevenin-norton", "relation": "prerequisite", "to": "gk-node", "why": "bad", "confidence": .9, "evidence": ["bad"], "reviewStatus": "approved"}]
        report = inspect_candidate(candidate, self.graph)
        self.assertIn("CROSS_FAMILY", {error["code"] for error in report["errors"]})
        candidate = self.candidate()
        candidate["operations"]["addEdges"] = [{"from": "ct-thevenin-norton", "relation": "prerequisite", "to": "ct-ohm-kcl-kvl", "why": "cycle", "confidence": .9, "evidence": ["cycle"], "reviewStatus": "approved"}]
        report = inspect_candidate(candidate, self.graph)
        self.assertIn("CYCLE", {error["code"] for error in report["errors"]})

    def test_approve_rolls_back_revision_when_receipt_commit_fails(self):
        candidate = self.candidate()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "revisions/candidate-thevenin-1"
            queue = root / "queue"
            original_replace = workflow.os.replace

            def fail_receipt_commit(source, destination):
                if str(destination).endswith(".review.json"):
                    raise OSError("simulated receipt write failure")
                return original_replace(source, destination)

            with patch.object(workflow.os, "replace", side_effect=fail_receipt_commit):
                with self.assertRaises(OSError):
                    approve_candidate(candidate, self.graph, output, queue, reviewer_id="sol")
            self.assertFalse(output.exists())
            self.assertFalse((queue / "candidate-thevenin-1.review.json").exists())

    def test_cli_inspect_reports_version_and_stable_hash(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate_path = Path(temp_dir) / "candidate.json"
            candidate_path.write_text(json.dumps(self.candidate(), ensure_ascii=False), encoding="utf-8")
            commands = [
                ["python3", "scripts/knowledge_patch_workflow.py", "inspect", "--graph-dir", str(self.graph_dir), "--candidate", str(candidate_path)],
                ["python3", "scripts/knowledge_patch_workflow.py", "inspect", "--graph-dir", str(self.graph_dir), "--candidate", str(candidate_path)],
            ]
            results = [subprocess.run(command, cwd=ROOT, capture_output=True, text=True) for command in commands]
        self.assertTrue(all(result.returncode == 0 for result in results), [result.stderr for result in results])
        reports = [json.loads(result.stdout) for result in results]
        self.assertTrue(all(report["valid"] for report in reports))
        self.assertTrue(all(report["candidateVersion"] == 1 for report in reports))
        self.assertEqual(reports[0]["candidateHash"], reports[1]["candidateHash"])


if __name__ == "__main__":
    unittest.main()
