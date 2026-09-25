"""Acceptance gate for all passive mock and retest score-oriented solutions."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestMockScoreSolutionAudit(unittest.TestCase):
    def test_annual_mock_solution_pages_are_current(self):
        completed = subprocess.run(
            [sys.executable, "scripts/sync_mock_score_solutions.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_all_59_mock_questions_have_aligned_substantive_scoring_sections(self):
        completed = subprocess.run(
            [sys.executable, "scripts/audit_mock_score_solutions.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
