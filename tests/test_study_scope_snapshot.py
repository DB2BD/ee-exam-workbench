"""Public study-scope numbers must match the current audit manifests."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestStudyScopeSnapshot(unittest.TestCase):
    def test_current_counts_in_readme_plan_and_proposal(self):
        pe = json.loads((ROOT / "data/pe-solution-audit.json").read_text(encoding="utf-8"))["summary"]
        math = json.loads((ROOT / "data/engineering-math-audit.json").read_text(encoding="utf-8"))["summary"]
        total = pe["questions"] + math["questions"]
        verified = pe["verified"] + math["verified"]
        reference = pe["reference_book_verified"]
        manual = pe["needs_manual_review"] + math["needs_manual_review"]
        self.assertEqual(total, verified + reference + manual)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        plan = (ROOT / "docs/產品化企劃書_2026-09-05.md").read_text(encoding="utf-8")
        proposal = (ROOT / "docs/spectra/changes/formal-textbook-product-proposal/proposal.md").read_text(encoding="utf-8")
        self.assertIn(f"{verified} 題 `verified`、{reference} 題 `reference_book_verified`、{manual} 題保留人工覆核", readme)
        self.assertIn(f"PE {total} 題，其中 {verified} 題 `verified`、{reference} 題 `reference_book_verified`、{manual} 題保留人工覆核", plan)
        self.assertIn(f"非工程數學 {pe['questions']} 題（{pe['verified']} verified、{reference} reference_book_verified、{pe['needs_manual_review']} needs_manual_review）", plan)
        self.assertIn(f"工程數學 {math['questions']} 題（{math['verified']} verified、{math['needs_manual_review']} needs_manual_review）", plan)
        self.assertIn(f"目前 {manual} 題人工覆核", proposal)


if __name__ == "__main__":
    unittest.main()
