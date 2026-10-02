"""Regression coverage for the passive 114 six-subject mock pack."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "上榜被動模考_114年六科執行包.md"
CORE_PATH = ROOT / "docs" / "上榜預設24時段_核心題路徑.md"
DIAGNOSTIC = ROOT / "docs" / "上榜基線_114年六科診斷.md"
CANONICAL_ROOT = ROOT / "📝 個人題解與錯題本"
EXPECTED_CORE_OVERLAP = {
    "EE-114-01-3",
    "EE-114-04-4",
    "EE-114-05-2",
    "EE-114-05-5",
}

SUBJECTS = (
    ("01", "電路學", (20, 20, 20, 20, 20)),
    ("02", "電子學（含電力電子）", (25, 25, 25, 25)),
    ("03", "工程數學", (15, 15, 20, 20, 30)),
    ("04", "電機機械", (20, 20, 20, 20, 20)),
    ("05", "電力系統", (20, 20, 20, 20, 20)),
    ("06", "工業配電", (20, 20)),
)
SCORED_06_QUESTIONS = (1, 5)
BOUNDARY_06_QIDS = ("EE-114-06-2", "EE-114-06-3", "EE-114-06-4")


class TestPassiveMockPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PACK.read_text(encoding="utf-8")
        cls.by_qid = {
            path.stem: path
            for path in CANONICAL_ROOT.glob("*/canonical/EE-114-*.md")
        }

    def test_fixed_order_points_and_all_questions_are_declared(self):
        expected_qids = []
        subject_positions = []
        for subject_code, subject_name, points in SUBJECTS:
            self.assertEqual(sum(points), 40 if subject_code == "06" else 100, subject_name)
            subject_positions.append(self.text.index(f"| {subject_name} |"))
            question_numbers = SCORED_06_QUESTIONS if subject_code == "06" else range(1, len(points) + 1)
            for question_number, point_value in zip(question_numbers, points):
                qid = f"EE-114-{subject_code}-{question_number}"
                expected_qids.append(qid)
                self.assertIn(qid, self.text)
                self.assertIn(qid, self.by_qid)
                canonical = self.by_qid[qid].read_text(encoding="utf-8")
                self.assertIn("audit_status: verified", canonical, qid)

        self.assertEqual(len(expected_qids), 26)
        self.assertEqual(len(set(expected_qids)), 26)
        self.assertEqual(set(re.findall(r"EE-\d{3}-\d{2}-\d+", self.text)), set(expected_qids))
        self.assertEqual(subject_positions, sorted(subject_positions))

    def test_furnace_boundary_practice_is_excluded_from_scoring(self):
        for qid in BOUNDARY_06_QIDS:
            self.assertNotIn(qid, self.text)
        for phrase in (
            "工業配電仍做官方原卷 120 分鐘",
            "原卷第 2、3、4 題只作邊界練習",
            "兩題合計 40 分",
            "不把兩題成績換算成 100 分",
            "預設計分總額為 540 分",
            "工業配電第 2、3、4 題不列入此選題",
            "不判唯一數值對錯",
            "屋內線路裝置規則",
        ):
            self.assertIn(phrase, self.text)
        for stale in ("每科配分合計 100 分", "三題合計 60 分", "預設計分總額為 560 分", "原卷第 2、3 題只作"):
            self.assertNotIn(stale, self.text)
        row = next(line for line in self.text.splitlines() if line.startswith("| 6 | 工業配電 |"))
        self.assertEqual(re.findall(r"EE-\d{3}-\d{2}-\d+", row), ["EE-114-06-1", "EE-114-06-5"])
        self.assertIn("上榜精確解答邊界_條件題處理.md", self.text)

    def test_optional_diagnostic_does_not_score_ambiguous_furnace_questions(self):
        diagnostic = DIAGNOSTIC.read_text(encoding="utf-8")
        self.assertIn("26 題列入預設計分（合計 540 分）", diagnostic)
        for qid in BOUNDARY_06_QIDS:
            row = next(line for line in diagnostic.splitlines() if qid in line)
            self.assertIn("不計分", row)
            self.assertIn("不列分", row)

    def test_pack_is_explicitly_no_fill_and_has_mock_repair_contract(self):
        required_phrases = (
            "這不是回填表",
            "不需把日期、分數或錯因回填到專案",
            "閉卷模考 120 分鐘",
            "得分證據核對 30 分鐘",
            "單題修復 30 分鐘",
            "不能說「已建立未接觸基線」或「已確認進步」",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, self.text)
        for code in "RSFCKUT":
            self.assertIn(f"`{code}`", self.text)

    def test_pack_discloses_all_core_question_contamination(self):
        qid_re = r"EE-\d{3}-\d{2}-\d+"
        mock_qids = set(re.findall(qid_re, self.text))
        core_qids = set(re.findall(qid_re, CORE_PATH.read_text(encoding="utf-8")))
        self.assertEqual(mock_qids & core_qids, EXPECTED_CORE_OVERLAP)
        self.assertIn("26 題預設計分題中有 4 題", self.text)
        self.assertIn("計時演練", self.text)
        self.assertIn("不是未接觸題目的能力基線", self.text)
        for qid in EXPECTED_CORE_OVERLAP:
            self.assertIn(qid, self.text)

    def test_every_local_markdown_link_resolves(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        self.assertGreaterEqual(len(links), 13)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            if not target or "://" in target:
                continue
            resolved = (PACK.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.exists(), resolved)


if __name__ == "__main__":
    unittest.main()
