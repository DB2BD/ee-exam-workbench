# -*- coding: utf-8 -*-
"""Regression gates for the generated historical topic-coverage report."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "🧠 核心考點知識庫"
    / "📊_電機工程技師_6大考科11年高頻考點統計與命中率分析.md"
)


class TestTopicFrequencyReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = REPORT.read_text(encoding="utf-8")

    def test_generated_report_is_current(self):
        completed = subprocess.run(
            [sys.executable, "scripts/analyze_topic_frequency.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_subject_denominators_match_the_question_database(self):
        expected = (
            "| 01 電路學 | 48 | 11 |",
            "| 02 電子學（含電力電子） | 48 | 11 |",
            "| 03 工程數學 | 67 | 11 |",
            "| 04 電機機械 | 55 | 11 |",
            "| 05 電力系統 | 50 | 11 |",
            "| 06 工業配電 | 55 | 11 |",
        )
        for row_start in expected:
            with self.subTest(row_start=row_start):
                self.assertIn(row_start, self.source)

    def test_top_chapters_use_year_coverage_then_question_count(self):
        expected = (
            "| 1 | 二階 RLC 暫態分析 | 7 | 7 年",
            "| 1 | 二極體整流與濾波電路 | 10 | 9 年",
            "| 1 | 機率與統計 | 14 | 11 年",
            "| 1 | 直流電機 (分激/串激特性與調速) | 11 | 10 年",
            "| 1 | 電力潮流與導納矩陣 | 8 | 8 年",
            "| 1 | 短路容量計算 (MVA 法) | 12 | 10 年",
        )
        for row_start in expected:
            with self.subTest(row_start=row_start):
                self.assertIn(row_start, self.source)

    def test_power_quality_count_does_not_claim_all_questions_are_harmonics(self):
        self.assertIn("| 2 | 電力品質：電壓閃爍與諧波分析 | 7 | 6 年", self.source)
        self.assertIn("電弧爐電壓閃爍／變動 4 題、諧波／共振 3 題", self.source)
        self.assertNotIn("| 2 | 非線性負載諧波分析與抑制", self.source)

    def test_dc_dc_count_excludes_the_switching_rl_question_from_converter_claims(self):
        self.assertIn("真正 DC–DC 轉換器 10 題／7 年，另 1 題為 114 年開關 RL 暫態", self.source)
        self.assertIn("不可把整個節點數字當作 buck-boost 題型命中率", self.source)

    def test_report_does_not_turn_history_into_a_guarantee(self):
        self.assertIn("323 道大題", self.source)
        self.assertIn("不是未來命中率預測", self.source)
        self.assertIn("任一科 0 分不予及格", self.source)
        for forbidden in (
            "80/20",
            "每年必考",
            "送分主力",
            "必拿分",
            "投資報酬率",
            "總題數統計：55 題",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.source)

    def test_passive_route_links_are_present(self):
        for target in (
            "../docs/上榜預設24時段_核心題路徑.md",
            "../docs/上榜混合橋接_六科12題.md",
            "../docs/上榜被動模考_114年六科執行包.md",
            "../docs/上榜被動複測_108年六科執行包.md",
            "../docs/上榜錯因修復索引_114-108.md",
        ):
            with self.subTest(target=target):
                self.assertIn(target, self.source)
                self.assertTrue((REPORT.parent / target).resolve().is_file())

    def test_readme_uses_the_same_no_fill_default_route(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "## 預設備考順序",
            "不等待自評、不要求把分數或錯因回填到專案",
            "24 個核心時段",
            "六科 12 題混合橋接",
            "114 年六科計時模考",
            "108 年六科被動複測",
            "59 題錯因修復索引",
        ):
            self.assertIn(phrase, readme)
        self.assertNotIn("第一階段（單科靶心攻堅，約 60 天）", readme)
        self.assertNotIn("低命中率內容", (ROOT / "dashboard-data.js").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
