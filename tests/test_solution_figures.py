"""Tests for scripts/check_solution_figures.py and the SVG figure staging path (v1.5.0).

All fixtures live in temporary directories; no real note or figure is touched.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_solution_figures as figs  # noqa: E402

GOOD_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300">
<rect width="600" height="300" rx="8" fill="#fff"/>
<line x1="10" y1="10" x2="100" y2="10" stroke="#000"/>
<text x="20" y="40" font-size="16" fill="#000"><tspan class="v">R</tspan><tspan class="n sub" font-size="12" baseline-shift="sub">1</tspan><tspan class="n"> = 12 </tspan><tspan class="t">歐姆</tspan></text>
</svg>
"""
NAME = "EE-999-05-1-demo.svg"
NOTE = "![官方題目裁切圖](../../../01_原始試題/x.png)\n\n![圖 1：示意電路](../figures/%s)\n" % NAME


class FigureCheckerTests(unittest.TestCase):
    def build(self, svg=GOOD_SVG, note=NOTE, name=NAME):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        subject = root / "05_電力系統"
        (subject / "canonical").mkdir(parents=True)
        (subject / "figures").mkdir()
        (subject / "canonical" / "EE-999-05-1.md").write_text(note, encoding="utf-8")
        if svg is not None:
            (subject / "figures" / name).write_text(svg, encoding="utf-8")
        return root

    def problems(self, **kwargs):
        return [item for _path, item in figs.collect(self.build(**kwargs))["problems"]]

    def assert_problem(self, prefix, **kwargs):
        found = self.problems(**kwargs)
        self.assertTrue(any(item.startswith(prefix) for item in found), (prefix, found))

    def test_good_figure_passes(self):
        result = figs.collect(self.build())
        self.assertEqual(result["problems"], [])
        self.assertEqual((result["figures"], result["references"]), (1, 1))

    def test_unparseable_xml(self):
        self.assert_problem("parse:", svg="<svg><rect></svg>")

    def test_viewbox_width_range(self):
        self.assert_problem("viewbox:", svg=GOOD_SVG.replace("0 0 600 300", "0 0 400 300"))
        self.assert_problem("viewbox:", svg=GOOD_SVG.replace("0 0 600 300", "0 0 800 300"))
        self.assert_problem("viewbox:", svg=GOOD_SVG.replace(' viewBox="0 0 600 300"', ""))

    def test_white_background_rect_required(self):
        self.assert_problem("background:", svg=GOOD_SVG.replace('fill="#fff"', 'fill="#eee"'))
        self.assert_problem("background:", svg=GOOD_SVG.replace('width="600" height="300"', 'width="100" height="100"'))
        self.assertEqual(self.problems(svg=GOOD_SVG.replace('width="600" height="300"', 'width="100%" height="100%"')), [])

    def test_size_limit(self):
        self.assert_problem("size:", svg=GOOD_SVG.replace("</svg>", "<!--" + "x" * 31000 + "--></svg>"))

    def test_external_references_and_raster_are_rejected(self):
        for extra in (
            '<image href="a.png" width="10" height="10"/>',
            '<use href="http://example.com/a.svg#x"/>',
            '<rect width="5" height="5" fill="url(http://x/y)"/>',
            '<image href="data:image/png;base64,AAAA"/>',
            "<script>alert(1)</script>",
        ):
            self.assert_problem("external:", svg=GOOD_SVG.replace("</svg>", extra + "</svg>"))
        self.assertEqual(self.problems(svg=GOOD_SVG.replace("</svg>", '<use href="#a"/></svg>')), [])

    def test_fixed_palette_only(self):
        self.assert_problem("color:", svg=GOOD_SVG.replace('stroke="#000"', 'stroke="#27ae60"'))
        self.assert_problem("color:", svg=GOOD_SVG.replace("</svg>", '<path d="M0 0" style="fill:red"/></svg>'))
        for color in ("#111", "#C0392B", "#1f5fa8", "#fde2e0", "#e3eefa", "white", "none"):
            self.assertEqual(self.problems(svg=GOOD_SVG.replace("</svg>", '<path d="M0 0" fill="%s" stroke="#1f5fa8"/></svg>' % color)), [])

    def test_text_needs_font_class_and_no_underscore_subscripts(self):
        self.assert_problem("text:", svg=GOOD_SVG.replace("</svg>", '<text x="1" y="1" font-size="16">Bus 1</text></svg>'))
        self.assert_problem("text:", svg=GOOD_SVG.replace("</svg>", '<text x="1" y="1"><tspan class="n">ok</tspan>tail</text></svg>'))
        self.assert_problem("text:underscore", svg=GOOD_SVG.replace("</svg>", '<text x="1" y="1" class="v">I_f</text></svg>'))
        self.assertEqual(self.problems(svg=GOOD_SVG.replace("</svg>", '<text x="1" y="1" class="t">好</text></svg>')), [])

    def test_sanitizer_strips_active_content(self):
        dirty = GOOD_SVG.replace("</svg>", '<script>x()</script><a href="http://e.com" onclick="y()"><rect onload="z()" width="1" height="1"/></a><use href="#ok"/></svg>')
        clean = figs.sanitize_svg('<?xml version="1.0"?>' + dirty)
        for bad in ("<script", "onclick", "onload", "http://e.com", "<?xml"):
            self.assertNotIn(bad, clean)
        self.assertIn('href="#ok"', clean)

    def test_every_reference_must_exist(self):
        self.assert_problem("exists:", svg=None)

    def test_every_figure_must_be_referenced(self):
        found = figs.collect(self.build(note="![官方題目裁切圖](../../../01_原始試題/x.png)\n"))["problems"]
        self.assertTrue(any(item.startswith("referenced:") for _p, item in found), found)

    def test_reference_form_caption_and_name(self):
        self.assert_problem("form:", note=NOTE.replace("../figures/", "figures/"))
        self.assert_problem("caption:", note=NOTE.replace("圖 1：示意電路", "示意電路"))
        self.assert_problem("name:", svg=GOOD_SVG, name="demo.svg", note=NOTE.replace(NAME, "demo.svg"))

    def test_official_crop_svgs_are_not_treated_as_figures(self):
        note = NOTE + "![x](../../../../01_原始試題/依考科/y/images/a.svg)\n"
        self.assertEqual(self.problems(note=note), [])

    def test_cli_exit_code(self):
        root = self.build()
        ok = subprocess.run([sys.executable, str(SCRIPTS / "check_solution_figures.py"), "--root", str(root)],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        (root / "05_電力系統" / "figures" / NAME).unlink()
        bad = subprocess.run([sys.executable, str(SCRIPTS / "check_solution_figures.py"), "--root", str(root), "--json"],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertTrue(json.loads(bad.stdout)["problems"])


class FigureStagingTests(unittest.TestCase):
    """stage_pages_artifact copies figures and verifies the IMAGE_MAP targets exist."""

    def make_site(self, root: Path, include_figure=True):
        figure_rel = f"02_題解/技師題解/05_電力系統/figures/{NAME}"
        if include_figure:
            target = root / figure_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(GOOD_SVG, encoding="utf-8")
        (root / "index.html").write_text("<html></html>", encoding="utf-8")
        (root / "dashboard-data.js").write_text(
            "const DB_DATA = {\n  questions: [],\n\n  sevenLayers: {}\n};\nconst QUESTION_CROP_MAP = {};\n", encoding="utf-8")
        (root / "national-exams-data.js").write_text("const N = {\n  questions: []\n};\n", encoding="utf-8")
        (root / "solutions-bundle.js").write_text(
            "const BUNDLED_MD = {};\nconst IMAGE_MAP = " + json.dumps({NAME: figure_rel, figure_rel: figure_rel}) + ";\n", encoding="utf-8")
        (root / "national-solutions-bundle.js").write_text("const NATIONAL_BUNDLED_MD = {};\nconst NATIONAL_IMAGE_MAP = {};\n", encoding="utf-8")
        for name in ("katex.min.css", "katex.min.js", "auto-render.min.js", "marked.min.js"):
            (root / "libs").mkdir(exist_ok=True)
            (root / "libs" / name).write_text("", encoding="utf-8")
        return figure_rel

    def stage(self, root: Path, dest: Path):
        env = dict(os.environ, PAGES_STAGE_ROOT=str(root), PAGES_STAGE_DEST=str(dest))
        return subprocess.run([sys.executable, str(SCRIPTS / "stage_pages_artifact.py")], env=env, capture_output=True, text=True)

    def test_figure_is_copied_and_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, dest = Path(tmp) / "src", Path(tmp) / "site"
            root.mkdir()
            rel = self.make_site(root)
            result = self.stage(root, dest)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((dest / rel).read_text(encoding="utf-8"), GOOD_SVG)

    def test_mapped_figure_missing_from_disk_fails_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, dest = Path(tmp) / "src", Path(tmp) / "site"
            root.mkdir()
            self.make_site(root, include_figure=False)
            result = self.stage(root, dest)
            self.assertNotEqual(result.returncode, 0)


class InlineFigureRendererTests(unittest.TestCase):
    """src/renderers/markdownRenderer.js: figures become inline <figure class="sol-figure">."""

    def run_node(self, html, figure_map):
        renderer = Path(__file__).resolve().parents[1] / "src/renderers/markdownRenderer.js"
        script = (
            "const fs=require('fs');const vm=require('vm');"
            "const sandbox={console};"
            + ("sandbox.FIGURE_SVG=%s;" % json.dumps(figure_map) if figure_map is not None else "")
            + "vm.createContext(sandbox);"
            "vm.runInContext(fs.readFileSync(%s,'utf8')+%s,sandbox);"
            "process.stdout.write(sandbox.out);"
        ) % (json.dumps(str(renderer)), json.dumps(";this.out=inlineSolutionFigures(" + json.dumps(html) + ");"))
        return subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout

    def test_known_figure_is_inlined_with_caption_and_paragraph_removed(self):
        svg = '<svg viewBox="0 0 600 300"><text class="v">I</text></svg>'
        out = self.run_node('<p><img src="../figures/EE-1-01-1-a.svg" alt="圖 1：電路"></p><p>後文</p>', {"EE-1-01-1-a.svg": svg})
        self.assertEqual(out, '<figure class="sol-figure">%s<figcaption>圖 1：電路</figcaption></figure><p>後文</p>' % svg)

    def test_missing_figure_and_other_images_fall_back_to_img(self):
        html = '<p><img src="../figures/EE-1-01-1-zz.svg" alt="圖 1"></p><img src="x/crop.png" alt="c">'
        self.assertEqual(self.run_node(html, {"EE-1-01-1-a.svg": "<svg/>"}), html)

    def test_function_without_bundle_is_a_noop(self):
        html = '<img src="figures/a.svg">'
        self.assertEqual(self.run_node(html, None), html)


if __name__ == "__main__":
    unittest.main()
