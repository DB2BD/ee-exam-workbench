# -*- coding: utf-8 -*-
"""Coverage and runtime contracts for the promoted PE/GK graph."""

import json
import subprocess
import unittest
from pathlib import Path

from scripts.question_schema import load_questions_from_bundle


ROOT = Path(__file__).resolve().parents[1]


class TestFullKnowledgeGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes = {
            node["nodeId"]: node
            for node in json.loads((ROOT / "data/knowledge/nodes.json").read_text(encoding="utf-8"))["nodes"]
        }
        cls.links = json.loads(
            (ROOT / "data/knowledge/question-links.json").read_text(encoding="utf-8")
        )["links"]
        cls.pe_qids = {row[0] for row in load_questions_from_bundle(ROOT / "dashboard-data.js")}
        cls.gk_qids = {row[0] for row in load_questions_from_bundle(ROOT / "national-exams-data.js")}

    def test_every_question_record_has_an_approved_family_isolated_link(self):
        expected = {f"PE:{qid}" for qid in self.pe_qids} | {f"GK:{qid}" for qid in self.gk_qids}
        self.assertEqual(set(self.links), expected)
        self.assertEqual(len(self.links), 484)
        for key, link in self.links.items():
            family, qid = key.split(":", 1)
            self.assertEqual(link["qid"], qid)
            self.assertEqual(link["examFamily"], family)
            self.assertEqual(link["reviewStatus"], "approved")
            self.assertNotEqual(link["sourcePriority"], "unknown")
            subject = qid.split("-")[2]
            self.assertTrue(link["nodeIds"])
            for node_id in link["nodeIds"]:
                node = self.nodes[node_id]
                self.assertEqual(node["examFamily"], family)
                self.assertEqual(str(node["subject"]), subject)

    def test_gk_link_is_consumable_by_the_existing_adapter(self):
        script = """
const fs = require('fs');
const vm = require('vm');
const module = { exports: {} };
const sandbox = { console, module };
vm.runInNewContext(fs.readFileSync('src/data/knowledge-dag.js', 'utf8'), sandbox);
vm.runInNewContext(fs.readFileSync('src/data/knowledge-dag.generated.js', 'utf8'), sandbox);
const mapped = module.exports.mapQuestionToDagNodes('01', '', '', 'GK-112-01-3');
const otherSubject = module.exports.mapQuestionToDagNodes('02', '', '', 'GK-112-01-3');
process.stdout.write(JSON.stringify({ mapped, otherSubject, enabled: sandbox.CANONICAL_GRAPH_ENABLED }));
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mapped"], ["gk-ct-divider-equiv"])
        self.assertEqual(payload["otherSubject"], [])
        self.assertTrue(payload["enabled"])


if __name__ == "__main__":
    unittest.main()
