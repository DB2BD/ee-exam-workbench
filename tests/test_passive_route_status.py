"""Regression locks for verified passive routes and ambiguity-safe answer cards."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = ROOT / "docs" / "上榜精確解答邊界_條件題處理.md"
EXPECTED_MANUAL_QIDS = {
    "EE-104-03-3",
    "EE-104-06-5",
    "EE-105-04-5",
    "EE-106-04-3",
    "EE-106-05-3",
    "EE-109-02-2",
    "EE-113-02-4",
    "EE-111-05-3",
    "EE-112-05-2",
    "EE-113-04-3",
    "EE-113-06-4",
    "EE-114-06-2",
    "EE-114-06-3",
}


class TestPassiveRouteStatus(unittest.TestCase):
    def test_furnace_short_model_keeps_actionable_manual_review_fields(self):
        from scripts.audit_pe_solutions import metadata
        from scripts.audit_passive_route_status import REVIEW_FIELDS

        solution = ROOT / "📝 個人題解與錯題本/06_工業配電/canonical/EE-114-06-2.md"
        values = metadata(solution)
        self.assertEqual(values["audit_status"], "needs_manual_review")
        self.assertEqual(values["status"], "needs_manual_review")
        self.assertIsNone(values["verified_at"])
        for field in REVIEW_FIELDS:
            with self.subTest(field=field):
                self.assertTrue(values.get(field))
        self.assertIn("code=114180", values["official_source_url"])
        self.assertIn("s=0712", values["official_source_url"])
        self.assertIn("尚未確認", values["verification_scope"])

        text = solution.read_text(encoding="utf-8")
        for phrase in ("條件主解", "不能據此宣稱唯一答案", "X_{F,sc}", "15.49", "62.26"):
            self.assertIn(phrase, text)

    def test_generator_fault_current_keeps_mw_to_mva_conversion_conditional(self):
        from scripts.audit_pe_solutions import metadata
        from scripts.audit_passive_route_status import REVIEW_FIELDS

        solution = ROOT / "📝 個人題解與錯題本/06_工業配電/canonical/EE-114-06-3.md"
        values = metadata(solution)
        self.assertEqual(values["audit_status"], "needs_manual_review")
        self.assertEqual(values["status"], "needs_manual_review")
        self.assertIsNone(values["verified_at"])
        for field in REVIEW_FIELDS:
            self.assertTrue(values.get(field), field)
        text = solution.read_text(encoding="utf-8")
        for phrase in (r"50\,\mathrm{MW}", r"30\,\mathrm{MW}", "額定 MVA", r"c_1=c_2=1.0", "2.2837", "2.6915"):
            self.assertIn(phrase, text)
        self.assertNotIn("EE-114-06-3", (ROOT / "docs/上榜預設24時段_核心題路徑.md").read_text(encoding="utf-8"))

    def test_transformer_voltage_conventions_are_explicit_in_mock_and_answer(self):
        solution = (ROOT / "📝 個人題解與錯題本/04_電機機械/canonical/EE-114-04-2.md").read_text(encoding="utf-8")
        mock = (ROOT / "docs/上榜被動模考_114年六科執行包.md").read_text(encoding="utf-8")
        for text in (solution, mock):
            for phrase in ("110\\sqrt2", "173.925", "122.984", "RMS", "峰值"):
                with self.subTest(phrase=phrase):
                    self.assertIn(phrase, text)

    def test_route_status_audit_passes(self):
        result = subprocess.run(
            ["python3", "scripts/audit_passive_route_status.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("needs_manual_review questions are isolated and documented", result.stdout)

    def test_boundary_cards_cover_the_current_manual_register(self):
        actual = set()
        for name in ("pe-solution-audit.json", "engineering-math-audit.json"):
            data = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
            actual.update(
                entry["qid"]
                for entry in data["entries"]
                if entry["audit_status"] == "needs_manual_review"
            )
        self.assertEqual(actual, EXPECTED_MANUAL_QIDS)

        text = BOUNDARY.read_text(encoding="utf-8")
        self.assertIn("13 題條件作答卡", text)
        for qid in EXPECTED_MANUAL_QIDS:
            with self.subTest(qid=qid):
                self.assertEqual(text.count(f"`{qid}`"), 1)
                self.assertIn(f"canonical/{qid}.md", text)

    def test_boundary_policy_is_exam_safe_and_noninteractive(self):
        text = BOUNDARY.read_text(encoding="utf-8")
        for phrase in (
            "不需要回填",
            "先寫假設",
            "條件解",
            "不當成唯一答案背誦",
            "不進入預設核心路徑",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
