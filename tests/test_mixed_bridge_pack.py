"""Regression coverage for the six-subject mixed bridge."""

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "上榜混合橋接_六科12題.md"
CANONICAL_ROOT = ROOT / "📝 個人題解與錯題本"
EXPECTED_BY_SUBJECT = {
    "01": {"EE-111-01-3", "EE-113-01-3"},
    "02": {"EE-104-02-3", "EE-106-02-5"},
    "03": {"EE-107-03-5", "EE-112-03-4"},
    "04": {"EE-111-04-3", "EE-112-04-3"},
    "05": {"EE-105-05-2", "EE-110-05-5"},
    "06": {"EE-114-06-3", "EE-113-06-3"},
}
REQUIRED_SECTIONS = (
    "## 考場標準作答",
    "## 得分點拆解",
    "## 完整教學推導",
    "## 獨立驗算",
    "## 常見失分",
)


class TestMixedBridgePack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PACK.read_text(encoding="utf-8")
        cls.qids = set(re.findall(r"EE-\d{3}-\d{2}-\d+", cls.text))
        cls.status = {}
        for name in ("pe-solution-audit.json", "engineering-math-audit.json"):
            data = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
            cls.status.update({entry["qid"]: entry["audit_status"] for entry in data["entries"]})

    def test_exactly_two_verified_variation_questions_per_subject(self):
        expected = set().union(*EXPECTED_BY_SUBJECT.values())
        self.assertEqual(self.qids, expected)
        self.assertEqual(len(self.qids), 12)
        for subject, qids in EXPECTED_BY_SUBJECT.items():
            with self.subTest(subject=subject):
                self.assertEqual({qid for qid in self.qids if qid.split("-")[2] == subject}, qids)
            for qid in qids:
                self.assertEqual(self.status.get(qid), "verified", qid)
                matches = list(CANONICAL_ROOT.glob(f"*/canonical/{qid}.md"))
                self.assertEqual(len(matches), 1, qid)
                canonical = matches[0].read_text(encoding="utf-8")
                for heading in REQUIRED_SECTIONS:
                    self.assertEqual(canonical.count(heading), 1, f"{qid}: {heading}")

    def test_question_and_solution_links_resolve(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        self.assertGreaterEqual(len(links), 25)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            if not target or "://" in target:
                continue
            resolved = (PACK.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)

    def test_pack_is_fixed_blind_and_noninteractive(self):
        for phrase in (
            "未顯示章節",
            "50 分鐘閉卷",
            "20 分鐘得分證據核對",
            "20 分鐘重寫",
            "不需要回填日期、分數或錯因",
            "不依成績更改後續順序",
            "114 年六科被動模考",
        ):
            self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
