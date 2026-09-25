"""Year landing pages must reflect official paper headers, not learner guesses."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestYearReadmes(unittest.TestCase):
    def test_generated_year_pages_are_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/build_year_readmes.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_priority_years_do_not_infer_learner_mastery(self):
        for year in (114, 108):
            source = (ROOT / "依年度分類" / f"{year}年" / "README.md").read_text(encoding="utf-8")
            with self.subTest(year=year):
                self.assertNotIn("🟢 已掌握", source)
                self.assertNotIn("平均 60 分及格", source)
                self.assertNotIn("滿分詳細題解", source)
                self.assertEqual(source.count("[完整題解]"), 6)
                self.assertEqual(source.count("[PDF]"), 6)

    def test_108_calculator_rules_and_exam_codes_match_official_headers(self):
        source = (ROOT / "依年度分類" / "108年" / "README.md").read_text(encoding="utf-8")
        expected_rows = (
            ("電路學", "01130", "禁止使用電子計算器"),
            ("電子學（包括電力電子學）", "01110", "禁止使用電子計算器"),
            ("工程數學", "01150", "禁止使用電子計算器"),
            ("電機機械", "01120", "可以使用電子計算器"),
            ("電力系統", "01140", "可以使用電子計算器"),
            ("工業配電", "01160", "可以使用電子計算器"),
        )
        for subject, code, calculator_rule in expected_rows:
            self.assertIn(f"| {subject} | `{code}` | 120 分鐘 | {calculator_rule} |", source)

    def test_generated_examples_do_not_invent_learner_progress(self):
        paths = (
            ROOT / "📝 個人題解與錯題本" / "TEMPLATE_題解與錯題筆記範本.md",
            ROOT / "📝 個人題解與錯題本" / "01_電路學" / "114年_電路學_第一題_節點電壓法.md",
            ROOT / "📝 個人題解與錯題本" / "03_工程數學" / "114年_工程數學_第三題_二階線性ODE.md",
            ROOT / "📝 個人題解與錯題本" / "03_工程數學" / "114年_工程數學_第五題_線性系統完整解與零空間.md",
            ROOT / "📝 個人題解與錯題本" / "05_電力系統" / "114年_電力系統_第二題_單線接地故障SLG.md",
        )
        for path in paths:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("掌握狀態: ⚪ 未作答", source)
                self.assertNotIn("最後複習日期: 2026-08-16", source)
                self.assertNotRegex(source, r"自我評分:\s*\d+")

    def test_exam_strategy_states_the_complete_official_rule_without_guarantees(self):
        path = ROOT / "🧠 核心考點知識庫" / "📊_電機工程技師_6大考科11年高頻考點統計與命中率分析.md"
        source = path.read_text(encoding="utf-8")
        for phrase in (
            "323 道大題",
            "任一科 0 分不予及格",
            "全程到考人數 16%",
            "總成績至少 50 分",
            "缺考科目視為 0 分",
            "LawContent.aspx?id=FL016893",
        ):
            self.assertIn(phrase, source)
        for forbidden in ("330 道大題", "平均 70 分及格", "輕鬆跨過及格線", "確保 100% 算對"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
