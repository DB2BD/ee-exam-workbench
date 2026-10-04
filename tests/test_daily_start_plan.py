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
            ("EXT", 9),
        ):
            actual = re.findall(rf"`{prefix}-(\d{{2}})`", schedule)
            expected = [f"{number:02d}" for number in range(1, count + 1)]
            with self.subTest(prefix=prefix):
                self.assertEqual(actual, expected)

    def test_daily_hours_recompute_to_82_5(self):
        # 69 h mandatory + 9 optional EXT days x 1.5 h.
        self.assertEqual(sum(float(row.group("hours")) for row in self.rows), 82.5)

    def test_ext_days_replace_recovery_and_are_marked_optional(self):
        by_date = {row.group("date"): row.groupdict() for row in self.rows}
        for day, code in (("2026-10-16", "01"), ("2026-10-18", "02"), ("2026-10-20", "03"),
                          ("2026-10-23", "04"), ("2026-10-25", "05"), ("2026-10-29", "06"),
                          ("2026-10-31", "07"), ("2026-11-03", "08"), ("2026-11-07", "09")):
            with self.subTest(day=day):
                self.assertEqual(by_date[day]["task"], f"`EXT-{code}`")
                self.assertEqual(float(by_date[day]["hours"]), 1.5)
                self.assertIn("上榜擴章日_強科與電力配電.md", by_date[day]["entry"])
        recovery = [d for d, r in by_date.items() if r["task"] == "`RECOVERY`"]
        self.assertEqual(recovery, ["2026-10-21", "2026-10-27", "2026-11-02",
                                    "2026-11-05", "2026-11-09", "2026-11-10"])
        self.assertIn("選做", self.text)

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
        self.assertEqual(len(links), 54)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (PLAN.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)


if __name__ == "__main__":
    unittest.main()
