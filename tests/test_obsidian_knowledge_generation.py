# -*- coding: utf-8 -*-
"""Contract tests for generated and personal Obsidian knowledge paths."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_obsidian_knowledge.py"
GRAPH = ROOT / "data" / "knowledge"


class TestObsidianKnowledgeGeneration(unittest.TestCase):
    def _run_generator(self, graph_dir, output_root, report_path=None, personal_root=None):
        command = [
            "python3",
            str(GENERATOR),
            "--graph-dir",
            str(graph_dir),
            "--output-root",
            str(output_root),
            "--json",
        ]
        if report_path:
            command.extend(["--report", str(report_path)])
        if personal_root:
            command.extend(["--personal-root", str(personal_root)])
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    def test_golden_notes_have_stable_frontmatter_and_semantic_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "🧠 問題驅動知識庫"
            result = self._run_generator(GRAPH, output_root)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["valid"], report)
            self.assertEqual(report["generatedNoteCount"], 149)
            self.assertTrue(report["generatedAt"])
            self.assertEqual(report["sourceIdentity"]["canonicalGraphRevision"], report["graphRevision"])
            self.assertEqual(report["outputIdentity"]["kind"], "obsidian-generated-notes")
            mainline = output_root / "00_主線" / "pe-mainline-circuit.md"
            self.assertTrue(mainline.exists())
            content = mainline.read_text(encoding="utf-8")
            self.assertIn("generated: true", content)
            self.assertIn("nodeId: pe-mainline-circuit", content)
            self.assertIn("nodeType: mainline", content)
            self.assertIn("examFamily: PE", content)
            self.assertIn(f"graphRevision: {report['graphRevision']}", content)
            self.assertRegex(content, r"sourceHash: [0-9a-f]{64}")
            self.assertIn("[[ct-ohm-kcl-kvl]]", content)

            concept = output_root / "01_電路學" / "ct-thevenin-norton.md"
            concept_content = concept.read_text(encoding="utf-8")
            self.assertIn("[[ct-procedure-thevenin-controlled-source]]", concept_content)
            self.assertIn("[[EE-114-01-2]]", concept_content)

    def test_repeated_generation_is_deterministic_and_preserves_personal_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            output_root = temp / "🧠 問題驅動知識庫"
            personal_root = temp / "📝 個人知識補充"
            personal_root.mkdir(parents=True)
            personal = personal_root / "戴維寧與諾頓等效定理.md"
            personal.write_text("# 我的補充\n保留這段手寫筆記。\n", encoding="utf-8")

            first = self._run_generator(GRAPH, output_root, personal_root=personal_root)
            files_after_first = {
                path.relative_to(output_root): path.read_bytes()
                for path in output_root.rglob("*.md")
            }
            second = self._run_generator(GRAPH, output_root, personal_root=personal_root)
            files_after_second = {
                path.relative_to(output_root): path.read_bytes()
                for path in output_root.rglob("*.md")
            }

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(files_after_first, files_after_second)
            self.assertEqual(personal.read_text(encoding="utf-8"), "# 我的補充\n保留這段手寫筆記。\n")
            self.assertFalse((output_root / "戴維寧與諾頓等效定理.md").exists())

    def test_manual_edit_fails_closed_before_any_note_is_rewritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            output_root = temp / "🧠 問題驅動知識庫"
            self.assertEqual(self._run_generator(GRAPH, output_root).returncode, 0)
            drifted = output_root / "01_電路學" / "ct-thevenin-norton.md"
            original_drifted = drifted.read_text(encoding="utf-8")
            drifted.write_text(original_drifted + "\n## 我的手動修訂\n", encoding="utf-8")

            result = self._run_generator(GRAPH, output_root)

            self.assertEqual(result.returncode, 1)
            self.assertEqual(drifted.read_text(encoding="utf-8"), original_drifted + "\n## 我的手動修訂\n")
            report = json.loads(result.stdout)
            self.assertFalse(report["valid"])
            self.assertTrue(
                any(
                    error["code"] == "GENERATED_NOTE_DRIFT"
                    and error["nodeId"] == "ct-thevenin-norton"
                    and "regenerate" in error["message"]
                    for error in report["errors"]
                ),
                report,
            )

    def test_retired_edge_resolves_successor_and_keeps_history_in_note(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            graph = temp / "graph"
            shutil.copytree(GRAPH, graph)
            nodes_path = graph / "nodes.json"
            nodes = json.loads(nodes_path.read_text(encoding="utf-8"))
            for node in nodes["nodes"]:
                if node["nodeId"] == "ct-divider-equiv":
                    node["lifecycle"] = "retired"
                    node["successorNodeIds"] = ["ct-thevenin-norton"]
            nodes_path.write_text(json.dumps(nodes, ensure_ascii=False), encoding="utf-8")
            edges_path = graph / "edges.json"
            edges = json.loads(edges_path.read_text(encoding="utf-8"))
            edges["edges"].append(
                {
                    "from": "pe-mainline-circuit",
                    "relation": "enables",
                    "to": "ct-divider-equiv",
                    "why": "Historical divider concept remains discoverable through its successor.",
                    "confidence": 0.8,
                    "evidence": ["fixture:retired-edge"],
                    "reviewStatus": "approved",
                }
            )
            edges_path.write_text(json.dumps(edges, ensure_ascii=False), encoding="utf-8")

            output_root = temp / "🧠 問題驅動知識庫"
            result = self._run_generator(graph, output_root)

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (output_root / "00_主線" / "pe-mainline-circuit.md").read_text(encoding="utf-8")
            self.assertIn("retired target `ct-divider-equiv`", content)
            self.assertIn("[[ct-thevenin-norton]]", content)


if __name__ == "__main__":
    unittest.main()
