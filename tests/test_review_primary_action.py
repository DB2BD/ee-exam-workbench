# -*- coding: utf-8 -*-
"""v1.3.6：複習頁單一主按鈕決策（node 以 stdin 執行）。"""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ReviewPrimaryActionTests(unittest.TestCase):
    def test_primary_action(self):
        src = (ROOT / "src/components/reviewPage.js").read_text(encoding="utf-8")
        m = re.search(r"function reviewPrimaryAction\(.*?\n}\n", src, re.S)
        self.assertTrue(m)
        script = m.group(0) + "process.stdout.write(JSON.stringify([reviewPrimaryAction(12), reviewPrimaryAction(0), reviewPrimaryAction('x')]));"
        done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        out = json.loads(done.stdout)
        self.assertEqual(out[0], {"label": "開始複習 12 題", "action": "start"})
        self.assertEqual(out[1]["action"], "none")
        self.assertEqual(out[2]["action"], "none")

    def test_wired_in_page_and_styles(self):
        src = (ROOT / "src/components/reviewPage.js").read_text(encoding="utf-8")
        self.assertIn("data-review-start", src)
        css = (ROOT / "src/styles/components.css").read_text(encoding="utf-8")
        self.assertIn(".btn-review-primary", css)


if __name__ == "__main__":
    unittest.main()
