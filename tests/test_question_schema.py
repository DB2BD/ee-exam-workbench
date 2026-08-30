# -*- coding: utf-8 -*-
"""QuestionRecord schema gate for both static exam databases."""

import json
import re
import subprocess
import unittest
from pathlib import Path

from scripts.question_schema import load_questions_from_bundle, validate_question_records


WORKSPACE = Path(__file__).resolve().parents[1]


class TestQuestionSchema(unittest.TestCase):
    def test_pe_bundle_has_named_record_contract(self):
        questions = load_questions_from_bundle(WORKSPACE / "dashboard-data.js", "sevenLayers")
        result = validate_question_records(questions, exam_family="PE")
        self.assertTrue(result.ok, result.errors[:5])
        self.assertEqual(result.count, 321)
        self.assertTrue(all(len(record) == 12 for record in questions))

    def test_gk_bundle_has_provenance_fields(self):
        questions = load_questions_from_bundle(WORKSPACE / "national-exams-data.js", "meta")
        result = validate_question_records(questions, exam_family="GK")
        self.assertTrue(result.ok, result.errors[:5])
        self.assertEqual(result.count, 161)
        self.assertTrue(all(len(record) >= 18 for record in questions))

    def test_validator_rejects_unknown_subject_and_malformed_status(self):
        malformed = [["EE-114-99-1", "99", 114, 1, "題目", [], "", "", 3, "verified", [], True]]
        result = validate_question_records(malformed, exam_family="PE")
        self.assertFalse(result.ok)
        self.assertTrue(any("subject" in error for error in result.errors))

    def test_js_compatibility_view_exposes_named_fields(self):
        record = ["EE-114-01-1", "01", 114, 1, "題目", ["電路學"], "solution.md", "paper.pdf", 3, "verified", [], True]
        probe = (
            "const fs=require('fs');"
            "const m=require('./src/domain/questionRecord.js');"
            "const input=JSON.parse(fs.readFileSync(0,'utf8'));"
            "process.stdout.write(JSON.stringify(m.toQuestionRecord(input,'PE')));"
        )
        completed = subprocess.run(
            ["node", "-e", probe], input=json.dumps(record), text=True,
            cwd=WORKSPACE, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        view = json.loads(completed.stdout)
        self.assertEqual(view["id"], "EE-114-01-1")
        self.assertEqual(view["subjectId"], "01")
        self.assertEqual(view["solutionStatus"], "verified")


if __name__ == "__main__":
    unittest.main()
