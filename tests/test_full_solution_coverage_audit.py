# -*- coding: utf-8 -*-
"""Regression gate for the annual solution-to-exam coverage audit."""

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts" / "audit_all_solutions_vs_exams.py"


class TestFullSolutionCoverageAudit(unittest.TestCase):
    def test_all_six_subjects_match_every_annual_question_count(self):
        result = subprocess.run(
            ["python3", str(AUDIT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[02_電子學_含電力電子] 104年", result.stdout)
        self.assertIn("[03_工程數學] 114年", result.stdout)
        self.assertIn("Total potential mismatches flagged: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
