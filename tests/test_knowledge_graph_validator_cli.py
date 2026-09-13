# -*- coding: utf-8 -*-
"""CLI contract tests for canonical graph validation."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_graph(root: Path, nodes, edges=None, links=None):
    schema = {
        "schemaVersion": "canonical-knowledge-graph.v1",
        "nodeTypes": ["question", "mechanism", "procedure", "mainline"],
        "lifecycleStates": ["active", "retired", "merged"],
        "acyclicRelations": ["prerequisite"],
    }
    (root / "schema.json").write_text(json.dumps(schema), encoding="utf-8")
    (root / "nodes.json").write_text(json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "nodes": nodes}), encoding="utf-8")
    (root / "edges.json").write_text(json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "edges": edges or []}), encoding="utf-8")
    (root / "question-links.json").write_text(json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "links": links or {}}), encoding="utf-8")


def _node(node_id="pe-node"):
    return {
        "nodeId": node_id,
        "nodeType": "mechanism",
        "title": "Validator fixture",
        "examFamily": "PE",
        "lifecycle": "active",
        "provenance": {"source": "test"},
        "nodeRevisionHash": "fixture-v1",
    }


class TestKnowledgeGraphValidatorCLI(unittest.TestCase):
    def test_valid_graph_prints_revision_and_writes_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            graph_dir = Path(temp_dir) / "graph"
            graph_dir.mkdir()
            _write_graph(graph_dir, [_node()])
            report = Path(temp_dir) / "reports" / "validation.json"
            result = subprocess.run(
                [sys.executable, "scripts/validate_knowledge_graph.py", "--graph-dir", str(graph_dir), "--report", str(report), "--json"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            output = json.loads(result.stdout)
            saved = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0)
        self.assertTrue(output["valid"])
        self.assertRegex(output["graphRevision"], r"^kg-v1-[0-9a-f]{16}$")
        self.assertEqual(saved["graphRevision"], output["graphRevision"])
        self.assertTrue(output["generatedAt"])
        self.assertEqual(output["sourceIdentity"]["canonicalGraphRevision"], output["graphRevision"])
        self.assertEqual(output["outputIdentity"]["kind"], "canonical-validation")

    def test_invalid_graph_has_machine_error_and_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            graph_dir = Path(temp_dir)
            _write_graph(
                graph_dir,
                [_node()],
                edges=[{"from": "pe-node", "relation": "prerequisite", "to": "missing", "why": "bad", "confidence": 0.5, "evidence": ["test"], "reviewStatus": "draft"}],
            )
            result = subprocess.run(
                [sys.executable, "scripts/validate_knowledge_graph.py", "--graph-dir", str(graph_dir), "--json"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(output["valid"])
        self.assertTrue(any(error["code"] == "DANGLING_EDGE" for error in output["errors"]))
        self.assertTrue(all(error["path"] and error["message"] for error in output["errors"]))


if __name__ == "__main__":
    unittest.main()
