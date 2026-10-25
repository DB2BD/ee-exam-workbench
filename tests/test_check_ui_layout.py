"""v1.4.0 核對題解＋作答結果卡介面：結果卡是版面內的停靠列，不再以浮層覆蓋題解。"""
import json
import re
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import node_runner  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BUILD = (ROOT / "scripts/build_workbench.py").read_text(encoding="utf-8")
RESULT_CARD = (ROOT / "src/components/resultCard.js").read_text(encoding="utf-8")
CSS_DIR = ROOT / "src/styles"


def all_css():
    return {p.name: p.read_text(encoding="utf-8") for p in CSS_DIR.glob("*.css")}


class TestDockMarkup(unittest.TestCase):
    def test_dock_is_a_row_of_the_split_body(self):
        body = BUILD.index('id="modal-split-body"')
        dock = BUILD.index('id="modal-result-dock"')
        self.assertGreater(dock, body)
        # the dock follows the solution pane inside the same split body
        self.assertGreater(dock, BUILD.index('id="modal-pane-right"'))
        self.assertIn('data-layout="split"', BUILD)

    def test_segmented_switch_ships_short_phone_labels(self):
        for needle in ('class="seg-short">題目<', 'class="seg-short">詳解<', 'class="seg-long">原題考卷<', 'class="seg-long">純詳解<'):
            self.assertIn(needle, BUILD)
        self.assertIn('aria-pressed="true"', BUILD)

    def test_new_stylesheet_registered_before_icons(self):
        css = re.findall(r"'(src/styles/[^']+)'", re.search(r"css_files = \[(.*?)\]", BUILD, re.S).group(1))
        self.assertIn("src/styles/v14-check-ui.css", css)
        self.assertLess(css.index("src/styles/v13-pacing.css"), css.index("src/styles/v14-check-ui.css"))
        self.assertEqual(css[-1], "src/styles/v13-icons.css")


class TestNoOverlayCss(unittest.TestCase):
    def test_docked_card_is_never_absolutely_positioned(self):
        for name, text in all_css().items():
            for block in re.findall(r"([^{}]*result-card--docked[^{}]*)\{([^}]*)\}", text):
                selector, body = block
                if ".result-card--viewport" in selector:
                    continue
                self.assertNotRegex(body, r"position:\s*absolute", f"{name}: {selector.strip()}")
        self.assertNotIn("absolute", re.search(r"\.result-card-saved-notice\s*\{[^}]*\}", all_css()["v14-check-ui.css"]).group(0))

    def test_split_body_is_a_grid_with_a_dock_row(self):
        modal = all_css()["modal.css"]
        split = re.search(r"\.modal-split-body\s*\{([^}]*)\}", modal).group(1)
        self.assertIn("display: grid", split)
        self.assertRegex(split, r"grid-template-rows:\s*minmax\(0, 1fr\) auto")
        dock = re.search(r"\.modal-result-dock\s*\{([^}]*)\}", modal).group(1)
        self.assertIn("grid-row: 2", dock)

    def test_phone_is_single_pane_whatever_the_inline_state(self):
        modal = all_css()["modal.css"]
        phone = modal[modal.index("@media (max-width: 760px) {\n  #solution-modal { padding: 0; }"):]
        self.assertIn('.modal-split-body:not([data-layout="exam-only"]) .modal-pane-left { display: none !important; }', phone)
        self.assertIn("grid-template-columns: minmax(0, 1fr)", phone)

    def test_phone_bar_never_wraps_into_vertical_text(self):
        css = all_css()["v14-check-ui.css"]
        phone = css[css.index("@media (max-width: 760px)"):]
        self.assertIn("flex-wrap: nowrap", phone)
        self.assertIn("white-space: nowrap", phone)
        self.assertIn("writing-mode: horizontal-tb", phone)


class TestResultCardDock(unittest.TestCase):
    def test_docked_card_mounts_in_the_dock_and_no_longer_pads_the_panes(self):
        self.assertIn("document.getElementById('modal-result-dock')", RESULT_CARD)
        self.assertNotIn("paddingBottom", RESULT_CARD)
        self.assertNotIn("syncPadding", RESULT_CARD)

    def test_sheet_handle_and_kept_hooks(self):
        for needle in ("result-card-handle", "result-card-expand", "result-card-collapse", "data-result-card-docked",
                       "做完了？記錄作答結果", "root.__resultCardDirty", "root.__resultCardCollapse", "root.__resultCardIsCollapsed"):
            self.assertIn(needle, RESULT_CARD)

    def test_set_modal_layout_tracks_layout_for_the_grid(self):
        source = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in ("src/components/icons.js", "src/components/solutionModal.js"))
        setup = r"""
const el = () => ({ style: {}, attrs: {}, classList: { add(){}, remove(){}, contains(){ return false; } }, setAttribute(k, v){ this.attrs[k] = v; }, getAttribute(k){ return this.attrs[k]; } });
const els = { 'modal-pane-left': el(), 'modal-pane-right': el(), 'modal-resizer': el(), 'modal-split-body': el() };
globalThis.document = { getElementById: id => els[id] || null, querySelectorAll: () => [] };
globalThis.window = { addEventListener(){} };
globalThis.__els = els;
"""
        expression = """(() => {
          const out = {};
          ['solution-only', 'exam-only', 'split'].forEach(mode => { setModalLayout(mode); out[mode] = __els['modal-split-body'].attrs['data-layout']; });
          return out;
        })()"""
        script = f"""
const vm = require('vm');
const context = {{ console }};
vm.createContext(context);
vm.runInContext({json.dumps(setup)}, context);
vm.runInContext({json.dumps(source, ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify(vm.runInContext({json.dumps(expression)}, context)));
"""
        done = node_runner.run(script, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout), {"solution-only": "solution-only", "exam-only": "exam-only", "split": "split"})


if __name__ == "__main__":
    unittest.main()
