"""v1.8.5 首頁與練習視窗的人性化調整：配速行語氣、練習進度、亮色警示字對比、返回鍵與目前分頁標記。"""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def node(sources, expression):
    code = "\n".join((ROOT / s).read_text(encoding="utf-8") for s in sources)
    script = ("const vm = require('vm'); const ctx = { console }; vm.createContext(ctx);"
              f"vm.runInContext({json.dumps(code + chr(10) + 'globalThis.__r = (' + expression + ');')}, ctx);"
              "process.stdout.write(JSON.stringify(ctx.__r));")
    return json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)


def luminance(hex_color):
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


class TestHumaneUi(unittest.TestCase):
    def test_pace_line_is_its_own_toned_line(self):
        src = ["src/components/icons.js", "src/components/todayTask.js"]
        behind = node(src, "todayTaskPaceHtml({ paceText: '落後約 4 小時（2 項未按日程完成）', pacing: { behindCount: 2 } })")
        ahead = node(src, "todayTaskPaceHtml({ paceText: '超前約 2 小時', pacing: { behindCount: 0 } })")
        even = node(src, "todayTaskPaceHtml({ paceText: '照日程', pacing: { behindCount: 0 } })")
        self.assertEqual(behind, '<p class="today-pacing-pace is-behind">落後約 4 小時（2 項未按日程完成）</p>')
        self.assertIn('class="today-pacing-pace is-ahead"', ahead)
        self.assertIn('class="today-pacing-pace">照日程', even)
        self.assertEqual(node(src, "todayTaskPaceHtml({ paceText: '' })"), "")

    def test_practice_progress_text(self):
        src = ["src/components/dailyPractice.js"]
        self.assertEqual(node(src, "(dailyPracticeState = { activeSession: { questionIds: ['a', 'b', 'c'], currentIndex: 0 } }, dailyPracticeGetProgressText())"), "第 1／3 題")
        self.assertEqual(node(src, "(dailyPracticeState = { activeSession: null }, dailyPracticeGetProgressText())"), "")

    def test_warning_text_meets_contrast_in_both_themes(self):
        base = (ROOT / "src/styles/base.css").read_text(encoding="utf-8")
        light, dark = base.split('[data-theme="dark"]', 1)
        token = lambda block, name: re.search(r"--" + name + r":\s*(#[0-9a-fA-F]{6})", block).group(1)
        for block in (light, dark):
            ink = token(block, "warn-ink")
            for bg in ("surface", "warn-light", "bg"):
                self.assertGreaterEqual(contrast(ink, token(block, bg)), 4.5, (ink, bg))
        css = (ROOT / "src/styles/components.css").read_text(encoding="utf-8")
        for selector in (".sb-drag", ".sb-gap", ".sb-risk "):
            rule = css[css.index(selector + "{") if selector + "{" in css else css.index(selector):]
            self.assertIn("var(--warn-ink)", rule[:rule.index("}")], selector)

    def test_tabs_mark_current_page_and_back_button_is_wired(self):
        main = (ROOT / "src/main.js").read_text(encoding="utf-8")
        self.assertIn("setAttribute('aria-current', 'page')", main)
        self.assertIn("window.addEventListener('popstate', appHistoryOnPopState)", main)
        modal = (ROOT / "src/components/solutionModal.js").read_text(encoding="utf-8")
        self.assertIn("appHistoryModalOpened()", modal)
        self.assertIn("appHistoryModalClosed()", modal)
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<nav class="main-tabs" aria-label="主要分頁">', index)
        self.assertIn('id="tab-btn-practice" aria-current="page"', index)


if __name__ == "__main__":
    unittest.main()
