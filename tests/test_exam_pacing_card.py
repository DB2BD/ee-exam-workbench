"""Regression coverage for the passive 120-minute scoring cadence."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "docs" / "上榜考場120分鐘得分節奏.md"


class TestExamPacingCard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CARD.read_text(encoding="utf-8")

    def test_fixed_timeline_totals_120_minutes(self):
        for phrase in (
            "0–5 分鐘",
            "5–95 分鐘",
            "95–112 分鐘",
            "112–120 分鐘",
            "5+90+17+8=120",
        ):
            self.assertIn(phrase, self.text)

    def test_point_caps_use_exactly_90_first_pass_minutes(self):
        expected = {10: 9.0, 15: 13.5, 20: 18.0, 25: 22.5, 30: 27.0}
        rows = {
            int(points): float(minutes)
            for points, minutes in re.findall(
                r"^\| (10|15|20|25|30) 分 \| (\d+(?:\.5)?) 分鐘 \|$",
                self.text,
                re.MULTILINE,
            )
        }
        self.assertEqual(rows, expected)
        for points, minutes in rows.items():
            self.assertEqual(minutes, points * 0.9)

    def test_both_mock_distributions_are_explicit_and_recompute_to_90(self):
        for phrase in (
            "5 題 × 20 分：每題最多 18 分鐘",
            "4 題 × 25 分：每題最多 22.5 分鐘",
            "13.5＋13.5＋18＋18＋27＝90 分鐘",
            "18＋9＋18＋9＋18＋18＝90 分鐘",
        ):
            self.assertIn(phrase, self.text)

    def test_strategy_is_score_first_but_not_fake_scoring_or_input_dependent(self):
        for phrase in (
            "不是官方配分表",
            "不需要把任何紀錄回填專案",
            "先做 `A`，再做 `B`，最後處理 `C`",
            "連續 8 分鐘仍寫不出下一個有效步驟",
            "配分最高且下一步已知道",
            "不捏造精確分數",
            "120 分鐘停筆",
        ):
            self.assertIn(phrase, self.text)

    def test_all_local_links_resolve(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        self.assertEqual(len(links), 3)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (CARD.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)


if __name__ == "__main__":
    unittest.main()
