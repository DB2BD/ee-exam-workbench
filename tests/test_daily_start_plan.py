"""Regression coverage for the 52-day no-input daily start plan."""

from datetime import date, timedelta
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "上榜逐日開工表_115年.md"
ROW_RE = re.compile(
    r"^\| (?P<date>2026-\d{2}-\d{2})（[^）]+） \| "
    r"(?P<task>.+?) \| (?P<hours>\d+(?:\.5)?) \| (?P<entry>.+) \|$",
    re.MULTILINE,
)


class TestDailyStartPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PLAN.read_text(encoding="utf-8")
        cls.rows = list(ROW_RE.finditer(cls.text))

    def test_every_calendar_day_occurs_once_in_order(self):
        start = date(2026, 9, 23)
        end = date(2026, 11, 13)
        expected = [
            (start + timedelta(days=offset)).isoformat()
            for offset in range((end - start).days + 1)
        ]
        actual = [row.group("date") for row in self.rows]
        self.assertEqual(len(expected), 52)
        self.assertEqual(actual, expected)

    def test_all_fixed_work_units_occur_exactly_once(self):
        schedule = "\n".join(row.group("task") for row in self.rows)
        for prefix, count in (
            ("CORE", 24),
            ("MIX", 6),
            ("MOCK114", 6),
            ("BLIND108", 6),
        ):
            actual = re.findall(rf"`{prefix}-(\d{{2}})`", schedule)
            expected = [f"{number:02d}" for number in range(1, count + 1)]
            with self.subTest(prefix=prefix):
                self.assertEqual(actual, expected)

    def test_daily_hours_recompute_to_69(self):
        self.assertEqual(sum(float(row.group("hours")) for row in self.rows), 69.0)

    def test_last_two_days_open_no_new_questions(self):
        by_date = {row.group("date"): row.groupdict() for row in self.rows}
        self.assertIn("`EXAM-CHECK`", by_date["2026-11-12"]["task"])
        self.assertEqual(float(by_date["2026-11-12"]["hours"]), 0)
        self.assertIn("`STOP`", by_date["2026-11-13"]["task"])
        self.assertEqual(float(by_date["2026-11-13"]["hours"]), 0)
        self.assertIn("不開新題", self.text)
        self.assertIn("停止新增練習", self.text)

    def test_plan_is_passive_and_has_a_direct_day_one_start(self):
        for phrase in (
            "日期列是準時完成前項時的建議節奏",
            "不選科、不重排進度，也不回填專案",
            "若尚未開始，第一個任務固定是 `CORE-01`",
            "若已開始，直接接最早未完成代碼",
            "日期列不表示使用者已完成較早任務",
            "先開 [官方題目 EE-114-01-3]",
            "停筆後才開 [canonical 題解]",
            "不跳過 114 年六科計時演練去追 108 年數量",
        ):
            self.assertIn(phrase, self.text)

    def test_all_local_links_resolve(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        self.assertEqual(len(links), 44)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (PLAN.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)


if __name__ == "__main__":
    unittest.main()
