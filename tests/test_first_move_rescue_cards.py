"""Regression coverage for the passive first-move rescue cards."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "docs" / "上榜起手式急救卡_114-108.md"
REPAIR_INDEX = ROOT / "docs" / "上榜錯因修復索引_114-108.md"

EXPECTED = {
    "EE-114-01-1": "S",
    "EE-114-01-3": "S",
    "EE-114-01-5": "S",
    "EE-114-02-1": "S",
    "EE-114-03-3": "S",
    "EE-114-03-5": "S",
    "EE-114-05-2": "S",
    "EE-114-05-5": "T",
    "EE-108-01-2": "S",
    "EE-108-02-3": "S",
    "EE-108-02-5": "T",
    "EE-108-03-1": "S",
    "EE-108-04-3": "T",
    "EE-108-05-2": "T",
    "EE-108-05-5": "S",
}


class TestFirstMoveRescueCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CARDS.read_text(encoding="utf-8")
        cls.index_text = REPAIR_INDEX.read_text(encoding="utf-8")
        cls.headings = re.findall(
            r"^### `(EE-(?:114|108)-\d{2}-\d+)` — `([ST])` ",
            cls.text,
            re.MULTILINE,
        )

    def test_exactly_the_15_s_or_t_repair_questions_have_one_card(self):
        self.assertEqual(len(self.headings), 15)
        self.assertEqual(dict(self.headings), EXPECTED)
        self.assertEqual(len({qid for qid, _ in self.headings}), 15)

        index_st = {
            (qid, code)
            for qid, code in re.findall(
                r"^\| `(EE-(?:114|108)-\d{2}-\d+)` .* \| ([ST])：",
                self.index_text,
                re.MULTILINE,
            )
        }
        self.assertEqual(index_st, set(EXPECTED.items()))

    def test_each_card_has_one_matching_canonical_link(self):
        links = re.findall(r"\[完整題解核對\]\(([^)]+)\)", self.text)
        self.assertEqual(len(links), 15)
        linked_qids = set()
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (CARDS.parent / target).resolve()
            self.assertTrue(resolved.is_file(), resolved)
            linked_qids.add(resolved.stem)
        self.assertEqual(linked_qids, set(EXPECTED))

    def test_cards_are_partial_cues_not_final_answer_sheets(self):
        self.assertIn("只揭露第一個可得分動作", self.text)
        self.assertIn("不提供最後答案", self.text)
        self.assertIn("不記分、不回填", self.text)
        self.assertNotIn("\\boxed", self.text)
        self.assertNotRegex(self.text, r"(?m)^## 得分點拆解$")
        self.assertNotRegex(self.text, r"(?m)^## 完整教學推導$")

    def test_route_canonical_notes_have_no_broken_qquad_commands(self):
        for raw_target in re.findall(r"\[完整題解核對\]\(([^)]+)\)", self.text):
            target = unquote(raw_target.split("#", 1)[0])
            content = (CARDS.parent / target).resolve().read_text(encoding="utf-8")
            qid = Path(target).stem
            with self.subTest(qid=qid):
                self.assertIsNone(re.search(r"(?<!\\)qquad", content))


if __name__ == "__main__":
    unittest.main()
