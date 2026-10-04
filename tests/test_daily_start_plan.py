"""Regression coverage for the v1.3 41-day compact schedule document (2/4 h daily budget)."""

from datetime import date, timedelta
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "01_備考計畫" / "逐日開工表_115年.md"
ROW_RE = re.compile(
    r"^\| (?P<date>2026-\d{2}-\d{2})（[^）]+） \| (?P<budget>\d+) \| (?P<task>.+) \|$",
    re.MULTILINE,
)
START, END = date(2026, 10, 4), date(2026, 11, 13)


class TestDailyStartPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PLAN.read_text(encoding="utf-8")
        cls.rows = list(ROW_RE.finditer(cls.text))
        cls.by_date = {row.group("date"): row.groupdict() for row in cls.rows}

    def test_every_calendar_day_occurs_once_in_order(self):
        expected = [(START + timedelta(days=n)).isoformat() for n in range((END - START).days + 1)]
        self.assertEqual(len(expected), 41)
        self.assertEqual([row.group("date") for row in self.rows], expected)
        self.assertEqual(START.weekday(), 6, "2026-10-04 is a Sunday")

    def test_daily_budget_is_two_hours_on_weekdays_and_four_on_weekends(self):
        for row in self.rows:
            d = date.fromisoformat(row.group("date"))
            if row.group("date") >= "2026-11-12":
                expected = 0  # EXAM-CHECK / STOP
            else:
                expected = 4 if d.weekday() >= 5 else 2
            with self.subTest(day=row.group("date")):
                self.assertEqual(int(row.group("budget")), expected)

    def test_all_fixed_work_units_occur_exactly_once(self):
        schedule = "\n".join(row.group("task") for row in self.rows)
        # CORE-01..06 are done on paper: kept as task codes, never dated.
        self.assertEqual(re.findall(r"`CORE-(\d{2})`", schedule), [f"{n:02d}" for n in range(7, 25)])
        for prefix, count in (("WEAK", 14), ("REINF", 9), ("WRAP", 3)):
            with self.subTest(prefix=prefix):
                self.assertEqual(re.findall(rf"`{prefix}-(\d{{2}})`", schedule), [f"{n:02d}" for n in range(1, count + 1)])
        for prefix in ("MOCK114", "BLIND108"):
            codes = re.findall(rf"`{prefix}-(\d{{2}})`", schedule)
            # weekday papers appear on two days (閉卷, 核對), weekend papers once
            self.assertEqual(sorted(set(codes)), [f"{n:02d}" for n in range(1, 7)])
        self.assertEqual(schedule.count("`BUFFER`"), 1)

    def test_retired_codes_are_gone_from_the_dated_table(self):
        schedule = "\n".join(row.group("task") for row in self.rows)
        for retired in ("MIX-", "EXT-", "RECOVERY"):
            self.assertNotIn(retired, schedule)
        self.assertFalse((ROOT / "docs" / "上榜擴章日_強科與電力配電.md").exists())
        for phrase in ("`MIX-01`", "`EXT-01`", "已退休"):
            self.assertIn(phrase, self.text)

    def test_weekday_papers_split_over_two_days_and_weekend_papers_are_whole(self):
        for prefix in ("MOCK114", "BLIND108"):
            for n in range(1, 7):
                code = f"{prefix}-{n:02d}"
                days = [(d, r["task"]) for d, r in self.by_date.items() if f"`{code}`" in r["task"]]
                if len(days) == 2:
                    (d1, t1), (d2, t2) = days
                    self.assertEqual(date.fromisoformat(d2) - date.fromisoformat(d1), timedelta(days=1), code)
                    self.assertLess(date.fromisoformat(d1).weekday(), 5, code)
                    self.assertIn(f"`{code}`（第 1 天：閉卷 120 分鐘）", t1)
                    self.assertIn(f"`{code}`（第 2 天：核對＋修復 60 分鐘）", t2)
                else:
                    self.assertEqual(len(days), 1, code)
                    self.assertGreaterEqual(date.fromisoformat(days[0][0]).weekday(), 5, code)
                    self.assertIn(f"`{code}`（一次做完 180 分鐘）", days[0][1])

    def test_twelve_papers_finish_by_the_hard_milestone(self):
        last = max(d for d, r in self.by_date.items() if re.search(r"`(MOCK114|BLIND108)-\d{2}`", r["task"]))
        self.assertEqual(last, "2026-10-31")
        self.assertEqual(self.by_date["2026-11-01"]["task"], "`BUFFER`")

    def test_milestones_row(self):
        section = self.text.split("## 關卡", 1)[1].split("\n## ", 1)[0]
        rows = [l for l in section.splitlines() if l.startswith("| 2026-")]
        self.assertEqual(len(rows), 3)
        self.assertRegex(rows[0], r"2026-10-17.*弱題分析關卡.*否")
        self.assertRegex(rows[1], r"2026-10-31.*模考截止.*是")
        self.assertIn("不可延後", rows[1])
        self.assertRegex(rows[2], r"2026-11-11.*補強完成.*否")

    def test_buffer_reinforcement_wrap_and_last_days(self):
        for day, code in (("2026-11-02", "REINF-01"), ("2026-11-06", "REINF-05"), ("2026-11-09", "WRAP-01"),
                          ("2026-11-10", "WRAP-02"), ("2026-11-11", "WRAP-03")):
            self.assertIn(f"`{code}`", self.by_date[day]["task"], day)
        self.assertEqual(self.by_date["2026-11-12"]["task"], "`EXAM-CHECK`")
        self.assertEqual(self.by_date["2026-11-13"]["task"], "`STOP`")
        for phrase in ("不開新題", "停止新增練習", "速查手冊", "條件題卡", "錯因回顧"):
            self.assertIn(phrase, self.text)

    def test_plan_is_passive_and_documents_pacing_rules(self):
        for phrase in (
            "不選科、不回填專案",
            "平日 2 小時、週末 4 小時",
            "先離開，明天核對",
            "**每科至少保留 1 個母題核心時段**",
            "**12 份模考卷與 10/31 期限永不刪減**",
            "113 年整卷",
            "不跳過 114 年六科計時演練",
        ):
            self.assertIn(phrase, self.text)

    def test_all_local_links_resolve(self):
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", self.text)
        self.assertGreaterEqual(len(links), 8)
        for raw_target in links:
            target = unquote(raw_target.split("#", 1)[0])
            resolved = (PLAN.parent / target).resolve()
            with self.subTest(target=raw_target):
                self.assertTrue(resolved.is_file(), resolved)


if __name__ == "__main__":
    unittest.main()
