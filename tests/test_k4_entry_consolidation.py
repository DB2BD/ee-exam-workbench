# -*- coding: utf-8 -*-
"""K4 複習入口收斂: 首頁只留兩個主入口，其餘收進「更多練習方式」；維護者工具需 ?maint=1。"""

import json
import re
import subprocess
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
INDEX = WORKSPACE / "index.html"
REVIEW_JS = WORKSPACE / "src/components/reviewPage.js"
DAILY_JS = WORKSPACE / "src/components/dailyPractice.js"


def practice_pane():
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('id="tab-pane-practice"')
    end = html.index('<!-- TAB 1: Questions Explorer -->', start)
    return html[start:end]


def primary_section(pane):
    open_i = pane.index('<section class="home-primary-actions"')
    close_i = pane.index('</section>', open_i)
    return pane[open_i:close_i]


def run_node(source):
    out = subprocess.run(["node", "-"], input=source, capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout)


class TestHomeLayout(unittest.TestCase):
    # v1.2: the learner uses 排程任務, 隨機練習 3 題 and 到期複習 daily, so all
    # three sit on the 今天 pane; there is no collapsed 「更多練習方式」 anymore.
    def test_random_three_and_due_review_are_primary(self):
        pane = practice_pane()
        primary = primary_section(pane)
        self.assertLess(pane.index('id="today-task-card"'), pane.index('<section class="home-primary-actions"'))
        self.assertIn('id="home-action-start"', primary)
        self.assertIn("dailyPracticePrepareNewRound()", primary)
        self.assertIn("隨機練習 3 題", primary)
        self.assertIn('id="home-action-due"', primary)
        self.assertIn("homeStartDueReview()", primary)
        self.assertEqual(len(re.findall(r"<button", primary)), 2)
        self.assertNotIn('<details class="more-practice"', pane)
        self.assertIn('id="daily-practice-container"', pane)
        self.assertIn('id="home-action-continue"', pane)

    def test_due_button_default_disabled_with_message(self):
        primary = primary_section(practice_pane())
        self.assertRegex(primary, r'id="home-action-due"[^>]*disabled')
        self.assertIn("今天沒有到期題", primary)

    def test_due_refresh_logic(self):
        src = DAILY_JS.read_text(encoding="utf-8")
        start = src.index("function homeDueReviewRefresh")
        end = src.index("function homeStartDueReview")
        fn = src[start:end]
        script = f"""
{fn}
const mk = n => {{ global.getDueQuestionsList = () => new Array(n).fill('x');
  global.document = {{ getElementById: () => global.btn }};
  global.btn = {{ disabled: null, innerHTML: '', setAttribute() {{}} }};
  homeDueReviewRefresh(); return {{ d: global.btn.disabled, h: global.btn.innerHTML }}; }};
console.log(JSON.stringify([mk(0), mk(5)]));
"""
        zero, five = run_node(script)
        self.assertTrue(zero["d"])
        self.assertIn("今天沒有到期題", zero["h"])
        self.assertFalse(five["d"])
        self.assertIn("到期複習（5 題）", five["h"])


class TestMaintGate(unittest.TestCase):
    def _fn(self):
        src = REVIEW_JS.read_text(encoding="utf-8")
        start = src.index("function isMaintMode")
        end = src.index("function openManualLabelModal")
        return src[start:end]

    def test_maint_flag_parsing(self):
        script = f"""
{self._fn()}
const r = s => {{ global.location = {{ search: s }}; return isMaintMode(); }};
console.log(JSON.stringify([r(''), r('?maint=1'), r('?a=1&maint=1'), r('?maint=10'), r('?xmaint=1')]));
"""
        self.assertEqual(run_node(script), [False, True, True, False, False])

    def test_open_modal_and_button_gated(self):
        src = REVIEW_JS.read_text(encoding="utf-8")
        body = src[src.index("function openManualLabelModal"):]
        self.assertIn("if (!isMaintMode()) return;", body[:200])
        self.assertIn("isMaintMode() && manual > 0", src)

    def test_review_secondary_actions_collapsed(self):
        src = REVIEW_JS.read_text(encoding="utf-8")
        i = src.index('<details class="more-practice more-practice-inline">')
        j = src.index("</details>", i)
        self.assertIn("data-review-open", src[i:j])
        self.assertLess(src.index("data-review-recall"), i)
        # The 複習中心 pane (and #btn-start-review) is gone in v1.2; due review starts from 今天.
        html = INDEX.read_text(encoding="utf-8")
        self.assertNotIn('id="btn-start-review"', html)
        self.assertIn("function startReviewSession", html)


if __name__ == "__main__":
    unittest.main()
