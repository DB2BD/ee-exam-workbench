# -*- coding: utf-8 -*-
"""Per-question hints for the four-stage recall reveal (stages ② and ③)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_recall_hints as brh  # noqa: E402

GENERATED = ROOT / "src" / "data" / "recallHints.generated.js"


def run_node(expression, setup=""):
    sources = [GENERATED, ROOT / "src" / "state" / "recallStore.js"]
    script = (
        "const vm = require('vm');\n"
        "const context = {console, localStorage: {getItem(){return null;}, setItem(){}}};\n"
        "vm.createContext(context);\n"
        + "".join(f"vm.runInContext({json.dumps(p.read_text(encoding='utf-8'))}, context);\n" for p in sources)
        + f"vm.runInContext({json.dumps(setup)}, context);\n"
        + f"process.stdout.write(JSON.stringify(vm.runInContext({json.dumps(expression)}, context)));\n"
    )
    # Feed the script on stdin: the generated data exceeds Linux's 128 KiB
    # per-argument limit, so `node -e <script>` fails in CI.
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    if done.returncode:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


class TestRecallHintsData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hints = brh.build()

    def test_generated_file_is_fresh(self):
        self.assertEqual(GENERATED.read_text(encoding="utf-8"), brh.render_js(self.hints))

    def test_traps_come_from_each_note_and_cards_supply_first_moves(self):
        traps = [q for q, h in self.hints.items() if "trapsMd" in h]
        moves = [q for q, h in self.hints.items() if "activationMd" in h]
        self.assertGreaterEqual(len(traps), 300)
        self.assertEqual(len(moves), 14)
        for qid in traps:
            self.assertTrue(all(line.startswith("- ") for line in self.hints[qid]["trapsMd"].splitlines()), qid)

    def test_card_first_move_stops_before_the_solution_link(self):
        move = self.hints["EE-114-01-3"]["activationMd"]
        self.assertIn("直流穩態", move)
        self.assertNotIn("完整題解核對", move)
        self.assertNotIn("第一個", move)
        self.assertIn("搖擺方程", self.hints["EE-114-05-5"]["activationMd"])


class TestRecallHintBundle(unittest.TestCase):
    SETUP = "getReviewTypeLabel = () => '章節'; getReviewChapterKey = () => null;"

    def test_bundle_carries_question_markdown_when_available(self):
        bundle = run_node("getRecallHintBundle('EE-114-01-3', ['EE-114-01-3'])", self.SETUP)
        self.assertIn("直流穩態", bundle["activationMd"])
        self.assertTrue(bundle["trapsMd"].startswith("- "))
        # Plain-text fallbacks stay for callers that do not render Markdown.
        self.assertTrue(bundle["activation"])
        self.assertTrue(bundle["trap"])

    def test_bundle_without_hints_keeps_chapter_template(self):
        bundle = run_node("getRecallHintBundle('GK-none', ['GK-none'])", self.SETUP)
        self.assertNotIn("activationMd", bundle)
        self.assertNotIn("trapsMd", bundle)


class TestBuildAndModalWiring(unittest.TestCase):
    def test_build_bundles_hints_before_recall_store(self):
        build = (ROOT / "scripts" / "build_workbench.py").read_text(encoding="utf-8")
        self.assertLess(build.index("src/data/recallHints.generated.js"), build.index("src/state/recallStore.js"))
        self.assertIn("build_recall_hints.py", (ROOT / "package.json").read_text(encoding="utf-8"))

    def test_modal_renders_question_hints_as_markdown(self):
        modal = (ROOT / "src" / "components" / "solutionModal.js").read_text(encoding="utf-8")
        self.assertIn("recallHints.activationMd", modal)
        self.assertIn("recallHints.trapsMd", modal)


if __name__ == "__main__":
    unittest.main()
