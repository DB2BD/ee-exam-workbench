# -*- coding: utf-8 -*-
"""Static integrity gates for the versioned textbook taxonomy data layer."""

import json
import re
import unittest
from pathlib import Path

from scripts.question_schema import load_questions_from_bundle


WORKSPACE = Path(__file__).resolve().parents[1]
TAXONOMY = WORKSPACE / "data" / "taxonomy"


def load_json(name):
    return json.loads((TAXONOMY / name).read_text(encoding="utf-8"))


def parse_dag_nodes():
    text = (WORKSPACE / "src/data/knowledge-dag.js").read_text(encoding="utf-8")
    pattern = re.compile(
        r"'([a-z0-9-]+)':\s*\{\s*"
        r"id:\s*'[^']+',\s*subject:\s*'([^']+)',\s*"
        r"subjectName:\s*'[^']+',\s*name:\s*'([^']+)'",
        re.DOTALL,
    )
    return {node_id: {"subjectId": subject, "name": name} for node_id, subject, name in pattern.findall(text)}


class TestTaxonomyData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aliases = load_json("alias-map.json")
        cls.golden = load_json("golden-set.json")
        cls.overrides = load_json("overrides.json")
        cls.override_schema = load_json("override-schema.json")
        cls.dag = parse_dag_nodes()
        cls.questions = {
            row[0]: row for row in load_questions_from_bundle(WORKSPACE / "dashboard-data.js")
        }

    def test_alias_map_is_complete_and_matches_canonical_dag_names(self):
        self.assertEqual(self.aliases["schemaVersion"], "1.0.0")
        self.assertRegex(self.aliases["taxonomyVersion"], r"^\d{4}\.\d{2}\.\d{2}$")
        chapters = {}
        for subject_id, subject in self.aliases["subjects"].items():
            self.assertIn(subject_id, {"01", "02", "03", "04", "05", "06"})
            self.assertIsInstance(subject["chapters"], dict)
            for chapter_id, chapter in subject["chapters"].items():
                self.assertNotIn(chapter_id, chapters, f"duplicate taxonomy node {chapter_id}")
                chapters[chapter_id] = (subject_id, chapter)
                self.assertIn(chapter_id, self.dag, f"alias map references unknown DAG node {chapter_id}")
                self.assertEqual(subject_id, self.dag[chapter_id]["subjectId"])
                self.assertEqual(chapter["name"], self.dag[chapter_id]["name"])
                self.assertIsInstance(chapter["aliases"], list)
                self.assertGreaterEqual(len(chapter["aliases"]), 1)
                self.assertTrue(all(isinstance(alias, str) and alias.strip() for alias in chapter["aliases"]))
        self.assertEqual(set(chapters), set(self.dag), "every DAG node must have one alias-map entry")

    def test_override_manifest_is_empty_but_schema_contract_is_present(self):
        self.assertEqual(self.overrides["schemaVersion"], self.override_schema["properties"]["schemaVersion"] and "1.0.0")
        self.assertEqual(self.overrides["taxonomyVersion"], self.aliases["taxonomyVersion"])
        self.assertIsInstance(self.overrides["overrides"], list)
        self.assertIn("$defs", self.override_schema)
        definition = self.override_schema["$defs"]["override"]
        self.assertIn("questionId", definition["required"])
        self.assertIn("primaryChapterId", definition["required"])
        self.assertIn("reason", definition["required"])

    def test_golden_positive_cases_reference_existing_questions_and_dag_nodes(self):
        self.assertEqual(self.golden["labeling"]["status"], "human-reviewed")
        seen = set()
        positive_by_chapter = {}
        for group in self.golden["positiveCases"]:
            subject_id = group["subjectId"]
            chapter_id = group["chapterId"]
            self.assertIn(chapter_id, self.dag)
            self.assertEqual(subject_id, self.dag[chapter_id]["subjectId"])
            self.assertIsInstance(group["rationale"], str)
            self.assertTrue(group["rationale"].strip())
            self.assertGreaterEqual(len(group["questionIds"]), 1)
            positive_by_chapter[chapter_id] = len(group["questionIds"])
            for question_id in group["questionIds"]:
                self.assertNotIn(question_id, seen, f"positive QID appears in multiple primary chapters: {question_id}")
                seen.add(question_id)
                self.assertIn(question_id, self.questions, f"golden set references missing PE QID: {question_id}")
                self.assertEqual(self.questions[question_id][1], subject_id)

        exceptions = self.golden["coverageExceptions"]
        self.assertEqual(set(positive_by_chapter) | set(exceptions), set(self.dag))
        target = self.golden["labeling"]["positiveTargetPerChapter"]
        for chapter_id, count in positive_by_chapter.items():
            if count < target:
                self.assertIn(chapter_id, exceptions)
        for chapter_id in exceptions:
            self.assertIsInstance(exceptions[chapter_id], str)
            self.assertTrue(exceptions[chapter_id].strip())

    def test_golden_hard_negatives_are_distinct_and_traceable(self):
        positive_ids = {qid for group in self.golden["positiveCases"] for qid in group["questionIds"]}
        negative_ids = set()
        for case in self.golden["hardNegatives"]:
            qid = case["questionId"]
            self.assertNotIn(qid, negative_ids)
            self.assertNotIn(qid, positive_ids, f"hard negative cannot also be a positive primary label: {qid}")
            negative_ids.add(qid)
            self.assertIn(qid, self.questions)
            self.assertEqual(self.questions[qid][1], case["subjectId"])
            self.assertIn(case["actualChapterId"], self.dag)
            self.assertIn(case["confusableWith"], self.dag)
            self.assertNotEqual(case["actualChapterId"], case["confusableWith"])
            self.assertTrue(case["rationale"].strip())


if __name__ == "__main__":
    unittest.main()
