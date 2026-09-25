"""Regression coverage for the six-subject exam answer skeleton."""

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKELETON = ROOT / "docs" / "上榜考場得分骨架_六科.md"
EXPECTED_BY_SUBJECT = {
    "01": {"EE-114-01-3", "EE-112-01-2"},
    "02": {"EE-110-02-3", "EE-112-02-3"},
    "03": {"EE-113-03-6", "EE-113-03-3"},
    "04": {"EE-112-04-5", "EE-114-04-4"},
    "05": {"EE-114-05-2", "EE-114-05-5"},
    "06": {"EE-113-06-4", "EE-110-06-4"},
}


class TestExamAnswerSkeleton(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKELETON.read_text(encoding="utf-8")
        cls.qids = set(re.findall(r"EE-\d{3}-\d{2}-\d+", cls.text))
        cls.status = {}
        for name in ("pe-solution-audit.json", "engineering-math-audit.json"):
            data = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
            cls.status.update({entry["qid"]: entry["audit_status"] for entry in data["entries"]})

    def test_six_subjects_have_two_verified_anchor_answers(self):
        expected = set().union(*EXPECTED_BY_SUBJECT.values())
        self.assertEqual(self.qids, expected)
        for subject, qids in EXPECTED_BY_SUBJECT.items():
            self.assertIn(f"## {subject} ", self.text)
            self.assertEqual({qid for qid in self.qids if qid.split("-")[2] == subject}, qids)
            for qid in qids:
                self.assertEqual(self.status.get(qid), "verified", qid)

    def test_skeleton_requires_exam_visible_evidence_without_fake_scoring(self):
        for phrase in (
            "不是官方配分表",
            "不替每一步捏造分數",
            "定義",
            "起手式",
            "中間量",
            "結論",
            "快驗",
            "先寫假設，再給條件解",
            "停筆前 30 秒",
            "閱卷者必須看得見得分證據",
        ):
            self.assertIn(phrase, self.text)

    def test_every_local_link_resolves(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        self.assertEqual(len(links), 14)
        self.assertIn("./上榜考場120分鐘得分節奏.md", links)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (SKELETON.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)

    def test_learner_visible_math_has_no_tab_corruption(self):
        self.assertNotIn("\t", self.text)
        self.assertIn(r"\(Y_{\text{bus}}\)", self.text)
        self.assertIn(r"\(i_L(0^-)=i_L(0^+)\)", self.text)
        self.assertIn(r"\(S_b\)", self.text)
        self.assertIn(r"\(V_b\)", self.text)


if __name__ == "__main__":
    unittest.main()
