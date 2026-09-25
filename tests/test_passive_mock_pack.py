"""Regression coverage for the passive 114 six-subject mock pack."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "上榜被動模考_114年六科執行包.md"
CORE_PATH = ROOT / "docs" / "上榜預設24時段_核心題路徑.md"
CANONICAL_ROOT = ROOT / "📝 個人題解與錯題本"
EXPECTED_CORE_OVERLAP = {
    "EE-114-01-3",
    "EE-114-04-4",
    "EE-114-05-2",
    "EE-114-05-5",
    "EE-114-06-3",
}

SUBJECTS = (
    ("01", "電路學", (20, 20, 20, 20, 20)),
    ("02", "電子學（含電力電子）", (25, 25, 25, 25)),
    ("03", "工程數學", (15, 15, 20, 20, 30)),
    ("04", "電機機械", (20, 20, 20, 20, 20)),
    ("05", "電力系統", (20, 20, 20, 20, 20)),
    ("06", "工業配電", (20, 20, 20, 20, 20)),
)


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
            self.assertEqual(sum(points), 100, subject_name)
            subject_positions.append(self.text.index(f"| {subject_name} |"))
            for question_number, point_value in enumerate(points, start=1):
                qid = f"EE-114-{subject_code}-{question_number}"
                expected_qids.append(qid)
                self.assertIn(qid, self.text)
                self.assertIn(qid, self.by_qid)
                canonical = self.by_qid[qid].read_text(encoding="utf-8")
                self.assertIn("audit_status: verified", canonical, qid)

        self.assertEqual(len(expected_qids), 29)
        self.assertEqual(len(set(expected_qids)), 29)
        self.assertEqual(subject_positions, sorted(subject_positions))

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
        self.assertIn("29 題中有 5 題", self.text)
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
