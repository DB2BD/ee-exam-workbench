# -*- coding: utf-8 -*-
"""驗算 folds into a closed <details>; 失分點 is removed when the recall box already shows it, folded otherwise.

The DOM behaviour is exercised in the browser by scripts/qa_guards.cjs; this file pins the wiring.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODAL = (ROOT / "src" / "components" / "solutionModal.js").read_text(encoding="utf-8")
GUARDS = (ROOT / "scripts" / "qa_guards.cjs").read_text(encoding="utf-8")


class TestFoldSectionsWiring(unittest.TestCase):
    def test_render_calls_tidy_with_recall_box_flag(self):
        self.assertIn("solutionModalTidySections(rightPane, { hideTraps: trapsShownInRecallBox });", MODAL)
        self.assertIn("trapsShownInRecallBox = !!recallHints.trapsMd;", MODAL)
        # tidy runs before KaTeX auto-render so moved nodes are still rendered
        self.assertLess(MODAL.index("solutionModalTidySections(rightPane"), MODAL.index("renderMathInElement(rightPane"))

    def test_fold_is_closed_and_labelled(self):
        fn = MODAL[MODAL.index("function solutionModalTidySections"):MODAL.index("function syncRecallRevealPresentation")]
        self.assertIn("'驗算（點開查看）'", fn)
        self.assertIn("'失分點（點開查看）'", fn)
        self.assertNotIn(".open = true", fn)

    def test_browser_scenarios_exist(self):
        self.assertIn("modal: 驗算 and 失分點 folded closed in browse mode", GUARDS)
        self.assertIn("modal: recall mode shows 失分點 only in step ③", GUARDS)


if __name__ == "__main__":
    unittest.main()
