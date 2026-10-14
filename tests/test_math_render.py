# -*- coding: utf-8 -*-
"""Math rendering gate: every learner-facing field renders cleanly.

Runs scripts/audit_math_render.cjs (the app's own Markdown+KaTeX pipeline over
RECALL_HINTS, KNOWLEDGE_DAG / canonical graph formulas and traps,
CHEATSHEET_DATA and every bundled Markdown file) and asserts zero KaTeX parse
errors and zero leaked LaTeX source or bare `$`.  Also pins the helper that keeps
core formulas out of `$…$` when they are prose.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

AUDIT = ROOT / "scripts" / "audit_math_render.cjs"


def run_node(source):
    done = subprocess.run(["node", "-e", source], cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


class TestMathRenderGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audit.json"
            done = subprocess.run(
                ["node", str(AUDIT), "--quiet", "--out", str(out)],
                cwd=ROOT, capture_output=True, text=True,
            )
            cls.result = json.loads(out.read_text(encoding="utf-8"))
        cls.returncode = done.returncode
        cls.stderr = done.stderr

    def test_no_katex_errors_or_leaks(self):
        problems = [
            f"{p['group']} {p['id']} errors={p['errors'][:1]} leaks={p['leaks']}"
            for p in self.result["problems"]
        ]
        self.assertEqual(problems, [], "\n".join(problems[:30]))
        self.assertEqual(self.result["totals"]["errors"], 0)
        self.assertEqual(self.result["totals"]["leakFields"], 0)
        self.assertEqual(self.returncode, 0, self.stderr)

    def test_gate_covers_every_field_family(self):
        stats = self.result["stats"]
        for group in ("coreFormula", "keyTrap", "trapsMd", "activationMd", "cheatsheet", "bundledMd", "nationalBundledMd"):
            self.assertGreater(stats.get(group, {}).get("checked", 0), 0, group)
        self.assertGreater(stats["bundledMd"]["checked"], 300)
        self.assertGreater(stats["trapsMd"]["checked"], 250)


class TestAuditDetectsBadRendering(unittest.TestCase):
    """The gate must see real problems, and must not flag rendered math."""

    def _inspect(self, html):
        source = (
            "const {inspectHtml}=require('./scripts/audit_math_render.cjs');"
            f"process.stdout.write(JSON.stringify(inspectHtml({json.dumps(html)})));"
        )
        return json.loads(run_node(source))

    def test_rendered_katex_is_not_visible_text(self):
        html = '<p>ok <span class="katex"><span class="katex-mathml"><annotation>\\frac{1}{2}$</annotation></span><span class="base">x</span></span> done</p>'
        found = self._inspect(html)
        self.assertNotIn("\\frac", found["visible"])
        self.assertNotIn("$", found["visible"])
        self.assertEqual(found["errors"], [])

    def test_leaked_source_and_errors_are_found(self):
        found = self._inspect('<p>價格 \\frac{1}{2} 與 $x</p><span class="katex-error" title="ParseError: bad">\\tfrac</span>')
        self.assertIn("\\frac", found["visible"])
        self.assertIn("$", found["visible"])
        self.assertEqual(len(found["errors"]), 1)

    def test_code_blocks_may_contain_dollars(self):
        found = self._inspect("<pre><code>cost = $5 \\frac</code></pre><p>text</p>")
        self.assertEqual(found["visible"].strip(), "text")


class TestFormulaFieldHelpers(unittest.TestCase):
    def _render(self, expression):
        source = (
            "const fs=require('fs'),vm=require('vm');"
            "const c={console,window:{}};c.self=c;vm.createContext(c);"
            "['libs/katex.min.js','libs/marked.min.js','src/renderers/katexRenderer.js']"
            ".forEach(f=>vm.runInContext(fs.readFileSync(f,'utf8'),c));"
            "if(!c.katex&&c.window.katex)c.katex=c.window.katex;"
            "if(!c.marked&&c.window.marked)c.marked=c.window.marked;"
            f"process.stdout.write(JSON.stringify(vm.runInContext({json.dumps(expression)},c)));"
        )
        return json.loads(run_node(source))

    def test_sentence_fallback_is_plain_text(self):
        html = self._render("renderCoreFormulaHtml('先寫出本章節的核心公式，再代入題目條件。')")
        self.assertIn("formula-plain", html)
        self.assertNotIn("katex", html)

    def test_latex_formula_is_rendered(self):
        html = self._render("renderCoreFormulaHtml('V_x = V_s \\\\frac{R_x}{R_1 + R_2}')")
        self.assertIn('class="katex"', html)
        self.assertNotIn("katex-error", html)

    def test_formula_with_text_group_stays_math(self):
        self.assertFalse(self._render("isPlainTextFormula('x = 1 \\\\text{ (獨立電源單獨作用)}')"))
        self.assertTrue(self._render("isPlainTextFormula('先列已知量與未知量')"))

    def test_key_trap_inline_markdown_has_no_paragraph_wrapper(self):
        html = self._render("renderInlineMarkdownWithMath('三相功率乘以 $\\\\sqrt{3}$。')")
        self.assertNotIn("<p>", html)
        self.assertIn('class="katex"', html)


if __name__ == "__main__":
    unittest.main()
