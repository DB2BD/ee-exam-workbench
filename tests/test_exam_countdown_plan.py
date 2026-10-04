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
            "2026-10-04",
            "2026-11-14 至 2026-11-15",
            "41 個日曆日",
            "平日 2 小時、週末 4 小時",
            "2026-08-04 至 2026-08-13",
            "https://wwwc.moex.gov.tw/main/exam/wFrmPropertyDetail.aspx?c=115180&m=7975",
        ):
            self.assertIn(phrase, self.text)

    def test_route_budget_is_complete_and_noninteractive(self):
        for phrase in (
            "18 × 60 分鐘",
            "14 × 75 分鐘",
            "6 × 180 分鐘",
            "不需要回填日期、分數或錯因",
            "不等待個人化分析",
            "不依單科感覺或分數改序",
            "12 份模考卷與 10/31 期限永不刪減",
            "每科至少保留 1 個母題時段",
            "11/13 停止新增練習",
            "10/31（不可延後）",
        ):
            self.assertIn(phrase, self.text)
        for retired in ("混合橋接", "擴章日", "69 小時", "52 天"):
            self.assertNotIn(retired, self.text)

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
