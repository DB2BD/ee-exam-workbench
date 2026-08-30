# -*- coding: utf-8 -*-
"""Regression checks for the Markdown/KaTeX display pipeline."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestFormulaFormat(unittest.TestCase):
    def test_renderer_supports_standard_latex_delimiters(self):
        source = (ROOT / "src/renderers/katexRenderer.js").read_text(encoding="utf-8")
        self.assertIn(r"/\\\[([\s\S]+?)\\\]/g", source)
        self.assertIn(r"/\\\(([^\n]+?)\\\)/g", source)

    def test_known_malformed_formula_delimiters_are_fixed(self):
        files = [
            ROOT / "🧠 核心考點知識庫/01_電路學/01_直流電路與戴維寧諾頓等效.md",
            ROOT / "🧠 核心考點知識庫/01_電路學/02_交流穩態相量與功率因數改善.md",
            ROOT / "📝 個人題解與錯題本/01_電路學/111年_電路學_全卷完整詳細題解.md",
            ROOT / "📝 個人題解與錯題本/05_電力系統/110年_電力系統_全卷完整詳細題解.md",
            ROOT / "📝 個人題解與錯題本/05_電力系統/111年_電力系統_全卷完整詳細題解.md",
            ROOT / "📝 個人題解與錯題本/05_電力系統/112年_電力系統_全卷完整詳細題解.md",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\$\$[^\n]*\$\$\n\s*\$\$\n\\begin\{")
            self.assertNotIn(r"\cos$(", text)

    def test_display_blocks_are_balanced_in_touched_files(self):
        files = [
            ROOT / "🧠 核心考點知識庫/01_電路學/01_直流電路與戴維寧諾頓等效.md",
            ROOT / "📝 個人題解與錯題本/01_電路學/111年_電路學_全卷完整詳細題解.md",
            ROOT / "📝 個人題解與錯題本/05_電力系統/110年_電力系統_全卷完整詳細題解.md",
            ROOT / "📝 個人題解與錯題本/05_電力系統/111年_電力系統_全卷完整詳細題解.md",
            ROOT / "📝 個人題解與錯題本/05_電力系統/112年_電力系統_全卷完整詳細題解.md",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8")
            # A line-level count catches accidental nested $$ introduced by a
            # matrix block while allowing normal inline $...$ formulas.
            self.assertEqual(text.count("$$") % 2, 0, path.name)


if __name__ == "__main__":
    unittest.main()
