"""Regression coverage for learner-visible math markup on the passive route."""

import unittest
from pathlib import Path

from scripts.audit_route_math_markup import audit, route_qids


ROOT = Path(__file__).resolve().parents[1]


class TestRouteMathMarkup(unittest.TestCase):
    def test_all_94_routed_canonical_notes_have_no_bare_latex_commands(self):
        self.assertEqual(len(route_qids()), 94)
        self.assertEqual(audit(), [])

    def test_known_learner_visible_repairs_remain_fixed(self):
        circuit = (
            ROOT
            / "📝 個人題解與錯題本"
            / "01_電路學"
            / "canonical"
            / "EE-108-01-2.md"
        ).read_text(encoding="utf-8")
        distribution = (
            ROOT
            / "📝 個人題解與錯題本"
            / "06_工業配電"
            / "canonical"
            / "EE-108-06-4.md"
        ).read_text(encoding="utf-8")
        probability = (
            ROOT
            / "📝 個人題解與錯題本"
            / "03_工程數學"
            / "canonical"
            / "EE-113-03-6.md"
        ).read_text(encoding="utf-8")

        self.assertIn("\\quad i_1", circuit)
        self.assertNotIn(",quad ", circuit)
        self.assertIn(r"\(20\,\mathrm{kVA}\)", distribution)
        self.assertNotIn("20,mathrm", distribution)
        self.assertIn(r"\qquad y\ge0", probability)
        self.assertNotIn(",qquad y", probability)


if __name__ == "__main__":
    unittest.main()
