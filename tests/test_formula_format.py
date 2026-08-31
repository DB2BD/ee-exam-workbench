# -*- coding: utf-8 -*-
"""Regression checks for the Markdown/KaTeX display pipeline."""

from pathlib import Path
import json
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestFormulaFormat(unittest.TestCase):
    def _render_with_bundled_katex(self, markdown):
        """Run the production renderer in a small Node VM fixture."""
        script = r'''
const fs = require('fs'), vm = require('vm');
const ctx = { console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync('libs/katex.min.js', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('libs/marked.min.js', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('src/renderers/katexRenderer.js', 'utf8'), ctx);
process.stdout.write(ctx.processMarkdownWithMath(process.argv[1]));
'''
        return subprocess.run(
            ['node', '-e', script, markdown],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def test_escaped_currency_does_not_close_inline_formula(self):
        rendered = self._render_with_bundled_katex(
            r'成本函數 $C=6P\quad (\text{\$/h})$。'
        )
        self.assertNotIn('katex-error', rendered)
        self.assertIn('class="katex"', rendered)

    def test_multiline_formula_sources_have_valid_environment_closures(self):
        path = ROOT / "📝 個人題解與錯題本/03_工程數學/canonical/EE-106-03-6.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn(r"\end{cases}", text)
        self.assertNotIn(r"}end{cases}", text)

        path = ROOT / "📝 個人題解與錯題本/06_工業配電/canonical/EE-113-06-4.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn(r"\mathrm{kV}\\)", text)

    def test_all_question_level_canonical_notes_render_without_katex_errors(self):
        paths = sorted(str(path.relative_to(ROOT)) for path in (
            ROOT / "📝 個人題解與錯題本"
        ).glob("**/canonical/*.md"))
        script = r'''
const fs = require('fs'), vm = require('vm');
const ctx = { console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync('libs/katex.min.js', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('libs/marked.min.js', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('src/renderers/katexRenderer.js', 'utf8'), ctx);
const paths = JSON.parse(fs.readFileSync(0, 'utf8'));
const failures = paths.filter(path => {
  const rendered = ctx.processMarkdownWithMath(fs.readFileSync(path, 'utf8'));
  return rendered.includes('katex-error') || rendered.includes('@@KATEX_');
});
process.stdout.write(JSON.stringify(failures));
'''
        result = subprocess.run(
            ['node', '-e', script],
            cwd=ROOT,
            input=json.dumps(paths, ensure_ascii=False),
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), [], result.stderr)

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
        self.assertIn(r"/\\\(([\s\S]+?)\\\)/g", source)
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
