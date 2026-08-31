# -*- coding: utf-8 -*-
"""Regression checks for the Markdown/KaTeX display pipeline."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestFormulaFormat(unittest.TestCase):
    def test_renderer_converts_obsidian_image_embeds_before_markdown_parse(self):
        source = (ROOT / "src/renderers/katexRenderer.js").read_text(encoding="utf-8")
        self.assertIn("normalizeObsidianImageEmbeds", source)
        self.assertIn(r"!\[\[([^|\]]+?)(?:\|([^\]]+?))?\]\]", source)
        self.assertIn('width="${dimensions[1]}"', source)

    def test_image_resolver_handles_nested_paths_and_rendered_img_tags(self):
        source = (ROOT / "src/renderers/markdownRenderer.js").read_text(encoding="utf-8")
        self.assertIn("resolveRenderedImageSources", source)
        self.assertIn("decodeURIComponent(path)", source)
        self.assertIn("part === '..'", source)
        self.assertIn("basename", source)
        self.assertIn("html.replace(/(\\bsrc\\s*=", source)
        self.assertIn("resolveImageMapUrl(src, isGK, qid)", source)

    def test_national_image_map_has_images_subpath_aliases(self):
        source = (ROOT / "scripts/compile_national_exams.py").read_text(encoding="utf-8")
        self.assertIn("sub_img = rel_path.split('images/', 1)[-1]", source)
        self.assertIn("img_map['images/' + sub_img]", source)

    def test_pe_image_map_has_encoded_subpath_aliases(self):
        source = (ROOT / "scripts/compile_dashboard_database.py").read_text(encoding="utf-8")
        self.assertIn("img_map[urllib.parse.quote(sub_img)]", source)
        self.assertIn("img_map[urllib.parse.quote('images/' + sub_img)]", source)

    def test_renderer_supports_standard_latex_delimiters(self):
        source = (ROOT / "src/renderers/katexRenderer.js").read_text(encoding="utf-8")
        self.assertIn(r"/\\\[([\s\S]+?)\\\]/g", source)
        self.assertIn(r"/\\\(([^\n]+?)\\\)/g", source)
        self.assertIn("unicodeTextInMathMode", source)

    def test_renderer_normalizes_legacy_unbraced_unit_macros(self):
        source = (ROOT / "src/renderers/katexRenderer.js").read_text(encoding="utf-8")
        self.assertIn("function normalizeLatexSyntax", source)
        self.assertIn("latex = normalizeLatexSyntax(latex)", source)
        self.assertIn("\\\\mathrm\\s+", source)

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
