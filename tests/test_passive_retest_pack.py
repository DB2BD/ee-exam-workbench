"""Regression coverage for the passive 108 six-subject retest pack."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "上榜被動複測_108年六科執行包.md"
CORE_PATH = ROOT / "docs" / "上榜預設24時段_核心題路徑.md"
CANONICAL_ROOT = ROOT / "📝 個人題解與錯題本"

SUBJECTS = (
    ("01", "電路學", (25, 25, 25, 25)),
    ("02", "電子學（含電力電子）", (20, 20, 20, 20, 20)),
    ("03", "工程數學", (20, 10, 20, 10, 20, 20)),
    ("04", "電機機械", (20, 20, 20, 20, 20)),
    ("05", "電力系統", (20, 20, 20, 20, 20)),
    ("06", "工業配電", (20, 20, 20, 20, 20)),
)


class TestPassiveRetestPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PACK.read_text(encoding="utf-8")
        cls.by_qid = {
            path.stem: path
            for path in CANONICAL_ROOT.glob("*/canonical/EE-108-*.md")
        }

    def test_all_30_questions_are_verified_and_each_subject_totals_100(self):
        expected_qids = []
        subject_positions = []
        for subject_code, subject_name, points in SUBJECTS:
            self.assertEqual(sum(points), 100, subject_name)
            subject_positions.append(self.text.index(f"| {subject_name} |"))
            for number in range(1, len(points) + 1):
                qid = f"EE-108-{subject_code}-{number}"
                expected_qids.append(qid)
                self.assertIn(qid, self.text)
                self.assertIn(qid, self.by_qid)
                canonical = self.by_qid[qid].read_text(encoding="utf-8")
                self.assertIn("audit_status: verified", canonical, qid)

        self.assertEqual(len(expected_qids), 30)
        self.assertEqual(len(set(expected_qids)), 30)
        self.assertEqual(subject_positions, sorted(subject_positions))

    def test_retest_contract_is_passive_and_blind(self):
        required_phrases = (
            "不需回填專案",
            "120 分鐘閉卷作答",
            "30 分鐘得分證據核對",
            "30 分鐘單題修復",
            "第一個盲測移轉點",
            "30 題，與 36 題核心路徑零重疊",
            "不與 114 年原始總分換算成改善幅度",
            "不是官方成績換算",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, self.text)

    def test_all_108_questions_are_unseen_in_the_core_route(self):
        qid_re = r"EE-\d{3}-\d{2}-\d+"
        retest_qids = set(re.findall(qid_re, self.text))
        core_qids = set(re.findall(qid_re, CORE_PATH.read_text(encoding="utf-8")))
        self.assertEqual(len(retest_qids), 30)
        self.assertFalse(retest_qids & core_qids)
        self.assertIn("108 年 30 題與核心路徑、混合橋接皆零重疊", self.text)

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
