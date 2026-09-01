# -*- coding: utf-8 -*-
"""Regression gates for canonical question -> textbook chapter alignment."""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from scripts.question_schema import load_questions_from_bundle


ROOT = Path(__file__).resolve().parents[1]


def load_taxonomy_map():
    text = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
    match = re.search(
        r"const QUESTION_TAXONOMY_MAP\s*=\s*(\{.*?\});\nconst SOLUTION_REVIEW_METADATA",
        text,
        re.DOTALL,
    )
    if not match:
        raise AssertionError("dashboard-data.js is missing QUESTION_TAXONOMY_MAP")
    payload = json.loads(match.group(1))
    if not isinstance(payload, dict):
        raise AssertionError("QUESTION_TAXONOMY_MAP must be an object")
    return payload


def load_dag_nodes():
    text = (ROOT / "src/data/knowledge-dag.js").read_text(encoding="utf-8")
    pattern = re.compile(
        r"'([a-z0-9-]+)':\s*\{\s*"
        r"id:\s*'[^']+',\s*subject:\s*'([^']+)'",
        re.DOTALL,
    )
    return dict(pattern.findall(text))


class TestQuestionTaxonomyAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = load_questions_from_bundle(ROOT / "dashboard-data.js")
        cls.question_by_id = {row[0]: row for row in cls.questions}
        cls.taxonomy = load_taxonomy_map()
        cls.dag = load_dag_nodes()

    def test_every_active_question_has_one_subject_valid_canonical_mapping(self):
        qids = set(self.question_by_id)
        self.assertEqual(set(self.taxonomy), qids)
        for qid, row in self.question_by_id.items():
            evidence = self.taxonomy[qid]
            self.assertIsInstance(evidence, dict, qid)
            chapter = evidence.get("primaryChapter")
            self.assertIn(chapter, self.dag, qid)
            self.assertEqual(self.dag[chapter], row[1], qid)
            self.assertIn(evidence.get("source"), {"canonical-chapter", "canonical-title-override"}, qid)
            self.assertIn("noteTitle", evidence, qid)

    def test_known_classifier_confusions_use_canonical_chapter(self):
        expected = {
            "EE-108-02-3": "el-feedback-stability",
            "EE-107-02-4": "el-pe-buck-boost",
            "EE-104-02-5": "el-active-filter",
            "EE-112-03-1": "em-laplace-transform",
            "EE-104-03-2": "em-eigen-diagonal",
            "EE-105-03-1": "em-second-order-ode-homogeneous",
            "EE-107-03-2": "em-eigen-diagonal",
            "EE-108-03-1": "em-second-order-ode-nonhomogeneous",
            "EE-108-03-2": "em-eigen-diagonal",
            "EE-108-03-4": "em-vector-analysis",
            "EE-113-03-4": "em-matrix-det-inv",
            "EE-104-05-1": "ps-unsymmetrical-faults",
            "EE-104-04-3": "emach-dc-motor-generator",
            "EE-105-04-3": "emach-induction-motor-torque",
            "EE-107-04-2": "emach-dc-motor-generator",
            "EE-107-04-3": "emach-induction-motor-equiv",
            "EE-108-04-2": "emach-dc-motor-generator",
            "EE-109-04-3": "emach-induction-motor-equiv",
            "EE-109-04-5": "emach-synchronous-salient-pole",
            "EE-110-04-4": "emach-dc-motor-generator",
            "EE-113-04-4": "emach-induction-motor-equiv",
            "EE-105-05-3": "ps-unsymmetrical-faults",
            "EE-106-05-4": "ps-system-protection-relay",
            "EE-107-05-1": "ps-transmission-line-models",
            "EE-109-05-4": "ps-symmetrical-components",
            "EE-109-05-6": "ps-transient-stability-equal-area",
            "EE-110-05-3": "ps-symmetrical-components",
            "EE-111-05-2": "ps-three-phase-fault",
            "EE-104-06-3": "dist-harmonics-mitigation",
            "EE-106-06-1": "dist-short-circuit-capacity",
            "EE-110-06-1": "dist-power-factor-correction",
            "EE-110-06-5": "dist-short-circuit-capacity",
            "EE-112-06-4": "dist-short-circuit-capacity",
            "EE-113-06-2": "dist-voltage-drop",
            "EE-112-06-5": "dist-protection-coordination",
            "EE-114-02-2": "el-mosfet-bias-small-signal",
        }
        for qid, chapter in expected.items():
            self.assertEqual(self.taxonomy[qid]["primaryChapter"], chapter, qid)

    def test_canonical_links_are_unique_and_qid_consistent(self):
        canonical_qids = set()
        for row in self.questions:
            qid, sid, year, number, _topic, _tags, solution_link = row[:7]
            self.assertIn("/canonical/", solution_link, qid)
            note = ROOT / solution_link
            self.assertTrue(note.is_file(), qid)
            raw = note.read_text(encoding="utf-8")
            qid_match = re.search(r"^qid:\s*(EE-\d{3}-\d{2}-\d+)\s*$", raw, re.M)
            self.assertIsNotNone(qid_match, qid)
            self.assertEqual(qid_match.group(1), qid)
            self.assertNotIn(qid, canonical_qids)
            canonical_qids.add(qid)
            self.assertEqual(qid.split("-")[1], str(year))
            self.assertEqual(qid.split("-")[2], sid)
            self.assertEqual(qid.split("-")[3], str(number))
        self.assertEqual(canonical_qids, set(self.question_by_id))

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for runtime taxonomy smoke test")
    def test_review_runtime_returns_canonical_mapping_for_all_questions(self):
        script = r'''
const fs = require('fs'), vm = require('vm');
const ctx = { console };
vm.createContext(ctx);
for (const file of ['dashboard-data.js', 'src/domain/questionRecord.js',
  'src/data/taxonomyAliases.js', 'src/data/knowledge-dag.js',
  'src/data/manualTopicLabels.js', 'src/components/reviewPage.js']) {
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
}
const result = vm.runInContext(`DB_DATA.questions.map(q => ({
  qid: q[0], expected: getManualTopicLabel(q[0]) || QUESTION_TAXONOMY_MAP[q[0]].primaryChapter,
  actual: getReviewChapterKey(q)
})).filter(x => x.expected !== x.actual)`, ctx);
process.stdout.write(JSON.stringify(result));
'''
        completed = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        # The VM writes a harmless database-load log before the JSON; decode
        # only the final JSON line so console output cannot mask a mismatch.
        payload = completed.stdout.strip().splitlines()[-1]
        self.assertEqual(json.loads(payload), [])


if __name__ == "__main__":
    unittest.main()
