# -*- coding: utf-8 -*-
"""v1.3: one inline-SVG icon set replaces decorative emoji."""

import glob
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS_JS = ROOT / "src/components/icons.js"
BUILD = (ROOT / "scripts/build_workbench.py").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")

REQUIRED = ["calendar", "file-text", "bar-chart", "more-horizontal", "shuffle", "rotate-ccw", "play",
            "alert-triangle", "check", "sun", "moon", "x", "star", "image", "eye"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿️]")
# ➔ (U+2794): the Casio fx-82 key-sequence arrow in the calculator guide / passbook. It is content, not decoration.
ALLOWED = {"➔"}


def node(expr):
    src = ICONS_JS.read_text(encoding="utf-8")
    out = subprocess.run(["node", "-e", src + "\nconsole.log(JSON.stringify(" + expr + "));"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


class TestIcons(unittest.TestCase):
    def test_every_required_icon_is_valid_svg(self):
        for name in REQUIRED:
            svg = node("uiIcon(%s)" % json.dumps(name))
            self.assertTrue(svg.startswith("<svg") and svg.endswith("</svg>"), name)
            for token in ('viewBox="0 0 24 24"', 'fill="none"', 'stroke="currentColor"', 'stroke-width="1.75"',
                          'stroke-linecap="round"', 'stroke-linejoin="round"', 'width="1em"', 'height="1em"',
                          'aria-hidden="true"', 'class="ui-icon"'):
                self.assertIn(token, svg, name)
            self.assertGreater(svg.count("<"), 2, name)

    def test_unknown_name_is_empty_and_options_work(self):
        self.assertEqual(node("uiIcon('no-such-icon')"), "")
        self.assertEqual(node("uiIcon()"), "")
        svg = node("uiIcon('star', { filled: true, size: '2em', class: 'x' })")
        self.assertIn('fill="currentColor"', svg)
        self.assertIn('width="2em"', svg)
        self.assertIn('class="ui-icon x"', svg)

    def test_no_decorative_emoji_left_in_ui_sources(self):
        files = glob.glob(str(ROOT / "src/**/*.js"), recursive=True) + glob.glob(str(ROOT / "src/**/*.css"), recursive=True)
        files.append(str(ROOT / "scripts/build_workbench.py"))
        bad = []
        for f in files:
            if ".generated." in f:
                continue
            for i, line in enumerate(Path(f).read_text(encoding="utf-8").splitlines(), 1):
                for ch in EMOJI.findall(line):
                    if ch not in ALLOWED:
                        bad.append("%s:%d %r" % (Path(f).name, i, ch))
        self.assertEqual(bad, [])

    def test_build_order(self):
        js = re.search(r"js_files = \[(.*?)\]", BUILD, re.S).group(1)
        css = re.search(r"css_files = \[(.*?)\]", BUILD, re.S).group(1)
        js_list = re.findall(r"'([^']+)'", js)
        css_list = re.findall(r"'([^']+)'", css)
        self.assertEqual(css_list[-1], "src/styles/v13-icons.css")
        icon_idx = js_list.index("src/components/icons.js")
        users = [f for f in js_list if f.endswith(".js") and f != "src/components/icons.js"
                 and "uiIcon" in (ROOT / f).read_text(encoding="utf-8")]
        self.assertTrue(users)
        for f in users:
            self.assertLess(icon_idx, js_list.index(f), f)
        # the bundled page really contains it
        self.assertIn("function uiIcon(", INDEX)
        self.assertLess(INDEX.index("function uiIcon("), INDEX.index("function themeButtonLabel"))

    def test_shell_tabs_use_icons(self):
        for name in ("calendar", "file-text", "bar-chart", "more-horizontal", "shuffle", "rotate-ccw", "moon"):
            self.assertIn('data-ui-icon="%s"' % name, INDEX)


if __name__ == "__main__":
    unittest.main()
