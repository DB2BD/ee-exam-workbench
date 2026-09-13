# -*- coding: utf-8 -*-
"""Behavioral tests for the canonical-to-legacy DAG adapter."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestKnowledgeGraphAdapter(unittest.TestCase):
    def _run(self, expression):
        script = f"""
const fs = require('fs');
const vm = require('vm');
const module = {{ exports: {{}} }};
const sandbox = {{ console, module,
  CANONICAL_GRAPH_ENABLED: true,
  CANONICAL_KNOWLEDGE_GRAPH: {{
    questionLinks: {{
      'PE:EE-114-01-2': {{ nodeIds: ['ct-thevenin-norton'], reviewStatus: 'approved' }}
    }},
    nodes: {{ 'ct-thevenin-norton': {{ examFamily: 'PE' }} }}
  }}
}};
vm.runInNewContext(fs.readFileSync('src/data/knowledge-dag.js', 'utf8'), sandbox);
process.stdout.write(JSON.stringify({expression}));
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_known_qid_uses_canonical_link(self):
        self.assertEqual(self._run("module.exports.mapQuestionToDagNodes('01', '任意文字', '', 'EE-114-01-2')"), ["ct-thevenin-norton"])

    def test_unknown_qid_is_fail_closed_when_canonical_mode_is_enabled(self):
        self.assertEqual(self._run("module.exports.mapQuestionToDagNodes('01', '完全未命中', '', 'EE-114-99-9')"), [])

    def test_resolver_exposes_unknown_reason(self):
        result = self._run("module.exports.resolveCanonicalQuestionMapping('01', 'EE-114-99-9')")
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["reason"], "no-approved-question-link")


if __name__ == "__main__":
    unittest.main()
