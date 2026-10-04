"""Every lean-v1 verified note has a passing independent verification script."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_verify_scripts  # noqa: E402


class VerificationScriptTests(unittest.TestCase):
    def test_all_verification_scripts_pass_and_none_are_missing(self):
        self.assertEqual(run_verify_scripts.main([]), 0)


if __name__ == "__main__":
    unittest.main()
