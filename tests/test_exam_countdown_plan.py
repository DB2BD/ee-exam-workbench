"""Regression coverage for the date-anchored passive exam route."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "上榜倒數節奏_115年電機技師.md"


class TestExamCountdownPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PLAN.read_text(encoding="utf-8")

    def test_official_dates_and_budget_are_explicit(self):
        for phrase in (
            "2026-09-23",
            "2026-11-14 至 2026-11-15",
            "52 個日曆日",
            "69 小時",
            "2026-08-04 至 2026-08-13",
            "https://wwwc.moex.gov.tw/main/exam/wFrmPropertyDetail.aspx?c=115180&m=7975",
        ):
            self.assertIn(phrase, self.text)

    def test_route_budget_is_complete_and_noninteractive(self):
        for phrase in (
            "24 × 60 分鐘",
            "6 × 90 分鐘",
            "6 × 180 分鐘",
            "不需要回填日期、分數、錯因或每日可用時間",
            "不等待個人化分析",
            "不依單科感覺或分數改序",
            "24 核心 → 混合橋接 → 114 模考 → 108 複測",
            "11/13 停止新增練習",
        ):
            self.assertIn(phrase, self.text)
        self.assertEqual(len(re.findall(r"\| [1-8] \|", self.text)), 8)

    def test_local_links_resolve(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        local_links = [target for target in links if "://" not in target]
        self.assertGreaterEqual(len(local_links), 5)
        for raw_target in local_links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (PLAN.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)


if __name__ == "__main__":
    unittest.main()
