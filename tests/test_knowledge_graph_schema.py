# -*- coding: utf-8 -*-
"""Contract tests for the canonical knowledge graph validator."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.knowledge_graph import validate_graph_directory


ROOT = Path(__file__).resolve().parents[1]


def _write_graph(root: Path, *, nodes, edges=None, links=None):
    (root / "schema.json").write_text(
        json.dumps(
            {
                "schemaVersion": "canonical-knowledge-graph.v1",
                "nodeTypes": ["question", "mechanism", "procedure", "mainline"],
                "lifecycleStates": ["active", "retired", "merged"],
                "acyclicRelations": ["prerequisite"],
            }
        ),
        encoding="utf-8",
    )
    (root / "nodes.json").write_text(json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "nodes": nodes}), encoding="utf-8")
    (root / "edges.json").write_text(json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "edges": edges or []}), encoding="utf-8")
    (root / "question-links.json").write_text(json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "links": links or {}}), encoding="utf-8")


def _node(node_id="pe-mechanism", node_type="mechanism", family="PE"):
    return {
        "nodeId": node_id,
        "nodeType": node_type,
        "title": "Test mechanism",
        "examFamily": family,
        "lifecycle": "active",
        "provenance": {"source": "golden-fixture", "evidence": ["fixture:1"]},
        "nodeRevisionHash": "fixture-hash",
    }


class TestKnowledgeGraphSchema(unittest.TestCase):
    def test_project_golden_slice_is_reviewed_and_in_scope(self):
        result = validate_graph_directory(ROOT / "data" / "knowledge")

        self.assertTrue(result["valid"], result)
        self.assertEqual(result["nodeCount"], 145)
        self.assertEqual(result["questionLinkCount"], 482)
        self.assertGreaterEqual(result["edgeCount"], 120)

        golden = json.loads((ROOT / "data" / "knowledge" / "golden-fixture.json").read_text(encoding="utf-8"))
        self.assertEqual(golden["schemaVersion"], "canonical-knowledge-golden.v1")
        self.assertEqual(golden["reviewStatus"], "human-reviewed")
        self.assertGreaterEqual(len(golden["nodeIds"]), 20)
        self.assertLessEqual(len(golden["nodeIds"]), 30)
        self.assertEqual(len(golden["nodeIds"]), len(set(golden["nodeIds"])))
        self.assertGreater(len(golden["questionIds"]), 0)
        self.assertEqual(len(golden["questionIds"]), len(set(golden["questionIds"])))
        nodes = json.loads((ROOT / "data" / "knowledge" / "nodes.json").read_text(encoding="utf-8"))["nodes"]
        self.assertTrue(set(golden["nodeIds"]).issubset({node["nodeId"] for node in nodes}))

    def test_valid_graph_has_deterministic_revision(self):
        nodes = [_node()]
        edges = [{
            "from": "pe-procedure",
            "relation": "prerequisite",
            "to": "pe-mechanism",
            "why": "The procedure requires the mechanism.",
            "confidence": 0.9,
            "evidence": ["fixture:edge"],
            "reviewStatus": "approved",
        }]
        nodes.insert(0, _node("pe-procedure", "procedure"))
        links = {
            "PE:EE-114-01-1": {
                "qid": "EE-114-01-1",
                "examFamily": "PE",
                "nodeIds": ["pe-procedure"],
                "confidence": 0.9,
                "evidence": ["fixture:q"],
                "reviewStatus": "approved",
                "sourcePriority": "manual",
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_graph(root, nodes=nodes, edges=edges, links=links)
            first = validate_graph_directory(root)
            second = validate_graph_directory(root)

        self.assertTrue(first["valid"], first)
        self.assertEqual(first["graphRevision"], second["graphRevision"])
        self.assertTrue(first["errors"] == [])

    def test_invalid_references_and_cycles_are_reported_with_stable_codes(self):
        nodes = [_node(), _node("gk-mechanism", family="GK")]
        edges = [
            {
                "from": "pe-mechanism",
                "relation": "prerequisite",
                "to": "missing",
                "why": "Missing target",
                "confidence": 0.5,
                "evidence": ["fixture:bad"],
                "reviewStatus": "draft",
            },
            {
                "from": "pe-mechanism",
                "relation": "prerequisite",
                "to": "gk-mechanism",
                "why": "Cross family",
                "confidence": 0.5,
                "evidence": ["fixture:bad"],
                "reviewStatus": "draft",
            },
        ]
        links = {
            "GK:EE-114-01-1": {
                "qid": "EE-114-01-1",
                "examFamily": "GK",
                "nodeIds": ["gk-mechanism"],
                "confidence": 0.9,
                "evidence": ["fixture:q"],
                "reviewStatus": "approved",
                "sourcePriority": "manual",
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_graph(root, nodes=nodes, edges=edges, links=links)
            result = validate_graph_directory(root)

        codes = {error["code"] for error in result["errors"]}
        self.assertFalse(result["valid"])
        self.assertIn("DANGLING_EDGE", codes)
        self.assertIn("CROSS_FAMILY_EDGE", codes)
        self.assertIn("QID_FAMILY_MISMATCH", codes)

    def test_lifecycle_successor_preserves_history(self):
        nodes = [
            _node("pe-old", "mechanism"),
            dict(_node("pe-new", "mechanism"), lifecycle="active"),
        ]
        nodes[0]["lifecycle"] = "merged"
        nodes[0]["successorNodeIds"] = ["pe-new"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_graph(root, nodes=nodes)
            result = validate_graph_directory(root)

        self.assertTrue(result["valid"], result)


if __name__ == "__main__":
    unittest.main()
