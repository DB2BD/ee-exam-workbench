# -*- coding: utf-8 -*-
"""v1.2 WP7: shell consolidation — three tabs plus a collapsed 更多, one-line header, PE-only head, no service worker."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts/build_workbench.py").read_text(encoding="utf-8")
MAIN_JS = (ROOT / "src/main.js").read_text(encoding="utf-8")


def head():
    return INDEX[:INDEX.index("</head>")]


def main_tabs():
    start = INDEX.index('<div class="main-tabs">')
    end = INDEX.index("<!-- TAB 0: Daily Practice -->", start)
    return INDEX[start:end]


class TestV12Shell(unittest.TestCase):
    def test_exactly_four_top_level_entries(self):
        tabs = main_tabs()
        details_start = tabs.index("<details")
        details_end = tabs.index("</details>")
        top = tabs[:details_start] + tabs[details_end:]
        buttons = re.findall(r'<button class="main-tab-btn[^"]*" id="(tab-btn-[a-z]+)"', top)
        self.assertEqual(buttons, ["tab-btn-practice", "tab-btn-mock", "tab-btn-scoreboard"])
        self.assertEqual(tabs.count("<details"), 1)
        self.assertIn("⋯ 更多", tabs)
        self.assertNotIn("<details open", tabs)
        for label in ("🎯 今天", "📄 模考", "📊 成績"):
            self.assertIn(label, top)
        menu = tabs[details_start:details_end]
        self.assertEqual(re.findall(r'id="(tab-btn-[a-z]+)"', menu), ["tab-btn-questions", "tab-btn-passbook", "tab-btn-backup"])
        self.assertIn("openPassbookModal()", menu)
        self.assertIn("openBackupModal()", menu)

    def test_no_old_tab_buttons_or_panes(self):
        for old in ("review", "weakness", "dag", "layers", "stats", "quicksheet", "calcguide"):
            self.assertNotIn(f'id="tab-btn-{old}"', INDEX, old)
            self.assertNotIn(f'id="tab-pane-{old}"', INDEX, old)
        self.assertNotIn("120 分鐘計時全真模考", INDEX)
        self.assertNotIn("openCalculatorGuideModal()\"><span>", INDEX)

    def test_old_mock_markup_and_timer_css_removed(self):
        for old in ("exam-select-subj", "exam-select-yr", 'id="exam-timer"', "btn-timer-toggle",
                    "mock-exam-questions", "timer-controls", "btn-timer", "timer-display", "loadMockExam()"):
            self.assertNotIn(old, INDEX, old)
        self.assertIn('id="tab-pane-mock"', INDEX)
        self.assertNotIn("loadMockExamTimerState", INDEX)

    def test_header_line_and_no_stat_cards(self):
        self.assertIn('id="header-summary-line"', INDEX)
        for old in ("stats-grid", 'class="stat-card', 'id="stat-total"', 'id="bar-mastered"', "onDueFlashcardsClick"):
            self.assertNotIn(old, INDEX, old)
        for piece in ("今天：", "｜到期 ", "scoreboardSummaryLine()", "function updateHeaderSummary", "result-card-saved"):
            self.assertIn(piece, INDEX, piece)
        store = (ROOT / "src/state/resultCardStore.js").read_text(encoding="utf-8")
        self.assertIn("new CustomEvent('result-card-saved'", store)

    def test_hero_is_pe_only_and_gk_switcher_hidden(self):
        hero = re.search(r'<div class="title-area">.*?</div>', INDEX, re.S).group(0)
        self.assertNotIn("484", hero)
        self.assertNotIn("GK", hero)
        self.assertNotIn("公務高考", hero)
        self.assertNotIn("category-switcher", INDEX)
        self.assertNotIn("cat-tab-GK", INDEX)

    def test_no_gk_script_tags_in_head(self):
        h = head()
        self.assertNotIn("national-exams-data.js", h)
        self.assertNotIn("national-solutions-bundle.js", h)
        self.assertNotRegex(INDEX, r'<script[^>]+src="[^"]*national-')
        # Lazy loader is present for any GK path.
        self.assertIn("function ensureGkData", INDEX)

    def test_no_unguarded_gk_data_references_at_init(self):
        for path in (ROOT / "src").rglob("*.js"):
            if "/data/" in str(path):
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "NATIONAL_EXAMS_DATA" in line and "typeof NATIONAL_EXAMS_DATA" not in line and "const NATIONAL" not in line:
                    # Allowed only on lines that follow a typeof guard in the same expression or block.
                    ctx = path.read_text(encoding="utf-8").splitlines()[max(0, n - 4):n]
                    self.assertTrue(any("typeof NATIONAL_EXAMS_DATA" in c for c in ctx), f"{path}:{n}")

    def test_no_service_worker_register_and_unregister_snippet_present(self):
        self.assertNotIn("serviceWorker.register", INDEX)
        self.assertNotIn("serviceWorker.register", BUILD)
        self.assertIn("navigator.serviceWorker.getRegistrations()", INDEX)
        self.assertIn("r.unregister()", INDEX)
        self.assertTrue((ROOT / "sw.js").exists())

    def test_switch_tab_routes_scoreboard_and_ignores_missing_panes(self):
        self.assertIn("renderScoreboard(document.getElementById('scoreboard-container'))", MAIN_JS)
        self.assertIn("if (!activePane) return;", MAIN_JS)
        for old in ("renderDagGraphVisualizer", "renderReviewPage()", "renderWeaknessView", "renderQuickReviewSheet"):
            self.assertNotIn(old, MAIN_JS.split("function handleUrlHashRouting")[0], old)

    def test_corrections_section_lives_in_today_pane(self):
        pane_start = INDEX.index('id="tab-pane-practice"')
        pane_end = INDEX.index("<!-- TAB 1: Questions Explorer -->", pane_start)
        self.assertIn('id="review-corrections"', INDEX[pane_start:pane_end])

    def test_recall_entry_opens_cover_on_mobile_for_every_mode(self):
        src = (ROOT / "src/components/solutionModal.js").read_text(encoding="utf-8")
        self.assertIn("const shouldOpenRecallPane = currentSolutionRecallEntry;", src)


if __name__ == "__main__":
    unittest.main()
