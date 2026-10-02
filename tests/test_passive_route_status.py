"""Regression locks for verified passive routes and ambiguity-safe answer cards."""

import json
import re
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
    "EE-112-03-2",
    "EE-112-05-2",
    "EE-113-04-4",
    "EE-113-06-4",
    "EE-114-06-2",
    "EE-114-06-3",
    "EE-114-06-4",
}
# Promoted back to verified on 2026-10-02: the answer is independent of the magnetization curve.
PROMOTED_FROM_MANUAL_QIDS = {"EE-113-04-3"}


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

    def test_motor_branch_design_keeps_code_table_values_conditional(self):
        from scripts.audit_pe_solutions import metadata
        from scripts.audit_passive_route_status import REVIEW_FIELDS

        solution = ROOT / "📝 個人題解與錯題本/06_工業配電/canonical/EE-114-06-4.md"
        values = metadata(solution)
        self.assertEqual(values["audit_status"], "needs_manual_review")
        self.assertIsNone(values["verified_at"])
        self.assertEqual(values["review_disposition"], "code_table_values_not_in_stem")
        for field in REVIEW_FIELDS:
            self.assertTrue(values.get(field), field)
        text = solution.read_text(encoding="utf-8")
        for phrase in ("條件與疑義", "屋內線路裝置規則", "95.5", "125", "150", "22", "38"):
            self.assertIn(phrase, text)
        for route in ("docs/上榜預設24時段_核心題路徑.md", "docs/上榜被動模考_114年六科執行包.md"):
            self.assertNotIn("EE-114-06-4", (ROOT / route).read_text(encoding="utf-8"), route)

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
        self.assertIn("# 上榜精確解答邊界：15 題條件題安全作答卡", text)
        self.assertIn("15 題條件作答卡", text)
        card_qids = [
            match.group(1)
            for line in text.splitlines()
            if (match := re.match(r"^\| \[`(EE-\d{3}-\d{2}-\d+)`\]", line))
        ]
        self.assertEqual(len(card_qids), 15)
        self.assertEqual(set(card_qids), EXPECTED_MANUAL_QIDS)
        for qid in PROMOTED_FROM_MANUAL_QIDS:
            self.assertNotIn(qid, text)
        for qid in EXPECTED_MANUAL_QIDS:
            with self.subTest(qid=qid):
                self.assertEqual(text.count(f"`{qid}`"), 1)
                self.assertIn(f"canonical/{qid}.md", text)

    def test_new_boundary_cards_state_assumption_and_both_branches(self):
        rows = {
            match.group(1): line
            for line in BOUNDARY.read_text(encoding="utf-8").splitlines()
            if (match := re.match(r"^\| \[`(EE-\d{3}-\d{2}-\d+)`\]", line))
        }
        expected = {
            "EE-114-06-4": ("屋內線路裝置規則", "1/3", "78.7", "95.5", "22", "125", "75", "38", "150", "52.49", "不列預設模考計分"),
            "EE-113-04-4": ("0.2/s", "189.35", "40.23", "115.9", "90.32", "197.85", "87.50", "57.67", "功率平衡"),
            "EE-112-03-2": ("[-2,2)", "a_0=2", "b_n=0", "a_0=4", "b_n=-8/(n\\pi)", "基本區間"),
        }
        for qid, phrases in expected.items():
            for phrase in phrases:
                with self.subTest(qid=qid, phrase=phrase):
                    self.assertIn(phrase, rows[qid])

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
