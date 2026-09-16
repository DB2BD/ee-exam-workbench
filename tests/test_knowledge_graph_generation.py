# -*- coding: utf-8 -*-
"""Contract tests for the deterministic website knowledge-graph generator."""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build_knowledge_graph.py"
GRAPH = ROOT / "data" / "knowledge"


class TestKnowledgeGraphGeneration(unittest.TestCase):
    def _run_generator(self, graph_dir, output_path, report_path=None, *extra):
        command = [
            "python3",
            str(GENERATOR),
            "--graph-dir",
            str(graph_dir),
            "--output",
            str(output_path),
            "--json",
        ]
        if report_path:
            command.extend(["--report", str(report_path)])
        command.extend(extra)
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    def test_valid_graph_produces_byte_stable_bundle_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            first = temp / "first.js"
            second = temp / "second.js"
            report = temp / "report.json"

            first_result = self._run_generator(GRAPH, first, report)
            second_result = self._run_generator(GRAPH, second)

            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertIn("globalThis.CANONICAL_GRAPH_ENABLED = true;", first.read_text(encoding="utf-8"))
            self.assertIn("kg-v1-9b95af550b0b1b9e", first.read_text(encoding="utf-8"))

            result = json.loads(first_result.stdout)
            saved_report = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(result, saved_report)
            self.assertEqual(result["graphRevision"], "kg-v1-9b95af550b0b1b9e")
            self.assertEqual(result["mappedQuestionCount"], 484)
            self.assertEqual(result["unknownQuestionCount"], 0)
            self.assertEqual(result["coverage"]["actual"], 484)
            self.assertEqual(result["coverage"]["required"], 484)
            self.assertTrue(result["generatedAt"])
            self.assertEqual(result["sourceIdentity"]["canonicalGraphRevision"], result["graphRevision"])
            self.assertEqual(result["outputIdentity"]["kind"], "website-bundle")

    def test_generated_bundle_is_consumable_by_the_existing_adapter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "knowledge-dag.generated.js"
            generated = self._run_generator(GRAPH, output)
            self.assertEqual(generated.returncode, 0, generated.stderr)

            script = f"""
const fs = require('fs');
const vm = require('vm');
const module = {{ exports: {{}} }};
const sandbox = {{ console, module }};
vm.runInNewContext(fs.readFileSync('src/data/knowledge-dag.js', 'utf8'), sandbox);
vm.runInNewContext(fs.readFileSync({json.dumps(str(output))}, 'utf8'), sandbox);
const mapped = module.exports.mapQuestionToDagNodes('01', '', '', 'EE-114-01-2');
const unknown = module.exports.mapQuestionToDagNodes('01', '', '', 'EE-114-99-9');
process.stdout.write(JSON.stringify({{mapped, unknown, enabled: sandbox.CANONICAL_GRAPH_ENABLED,
  canonicalProcedure: Boolean(sandbox.CANONICAL_KNOWLEDGE_GRAPH.nodes['ct-procedure-thevenin-controlled-source'])}}));
"""
            result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mapped"], ["ct-thevenin-norton"])
            self.assertEqual(payload["unknown"], [])
            self.assertTrue(payload["enabled"])
            self.assertTrue(payload["canonicalProcedure"])

    def test_invalid_graph_keeps_prior_bundle_and_reports_actionable_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            graph = temp / "graph"
            shutil.copytree(GRAPH, graph)
            output = temp / "knowledge-dag.generated.js"
            output.write_text("prior accepted bundle\n", encoding="utf-8")
            edges_path = graph / "edges.json"
            edges = json.loads(edges_path.read_text(encoding="utf-8"))
            edges["edges"][0]["to"] = "missing-node"
            edges_path.write_text(json.dumps(edges, ensure_ascii=False), encoding="utf-8")

            result = self._run_generator(graph, output)

            self.assertEqual(result.returncode, 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "prior accepted bundle\n")
            payload = json.loads(result.stdout)
            errors = payload["errors"]
            self.assertTrue(any(error["code"] == "DANGLING_EDGE" and "missing-node" in error["message"] for error in errors))

    def test_coverage_regression_keeps_prior_bundle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            graph = temp / "graph"
            shutil.copytree(GRAPH, graph)
            output = temp / "knowledge-dag.generated.js"
            output.write_text("prior accepted bundle\n", encoding="utf-8")
            links_path = graph / "question-links.json"
            links = json.loads(links_path.read_text(encoding="utf-8"))
            links["links"] = dict(list(links["links"].items())[:7])
            links_path.write_text(json.dumps(links, ensure_ascii=False), encoding="utf-8")

            result = self._run_generator(graph, output)

            self.assertEqual(result.returncode, 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "prior accepted bundle\n")
            payload = json.loads(result.stdout)
            self.assertIn("COVERAGE_INCOMPLETE", {error["code"] for error in payload["errors"]})


class TestKnowledgeGraphBuildIntegration(unittest.TestCase):
    def test_workbench_lists_generated_bundle_after_canonical_dag(self):
        source = (ROOT / "scripts" / "build_workbench.py").read_text(encoding="utf-8")
        canonical_position = source.index("'src/data/knowledge-dag.js'")
        generated_position = source.index("'src/data/knowledge-dag.generated.js'")
        self.assertLess(canonical_position, generated_position)


if __name__ == "__main__":
    unittest.main()
