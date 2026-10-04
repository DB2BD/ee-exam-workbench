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
        cards = brh.activations_from_cards(brh.RESCUE_CARDS.read_text(encoding="utf-8"))
        self.assertEqual(len(cards), 14)
        self.assertGreaterEqual(len(moves), len(cards))
        # Curated rescue cards win over written first moves.
        for qid, move in cards.items():
            self.assertEqual(self.hints[qid]["activationMd"], move)
        for qid in traps:
            self.assertTrue(all(line.startswith("- ") for line in self.hints[qid]["trapsMd"].splitlines()), qid)

    def test_card_first_move_stops_before_the_solution_link(self):
        move = self.hints["EE-114-01-3"]["activationMd"]
        self.assertIn("直流穩態", move)
        self.assertNotIn("完整題解核對", move)
        self.assertNotIn("第一個", move)
        self.assertIn("搖擺方程", self.hints["EE-114-05-5"]["activationMd"])


class TestLeakCheck(unittest.TestCase):
    NOTE = "## 已知與所求\n\n電源 660 V、34 Ω。\n\n## 考場標準作答\n\n\\(\\boxed{P=612.5\\ \\mathrm W}\\)，\\(\\boxed{I=3.5\\,A}\\)，\\(\\boxed{V=660}\\)\n"

    def test_answer_values_are_flagged_but_givens_are_not(self):
        self.assertEqual(sorted(brh.answer_numbers(self.NOTE)), ["3.5", "612.5"])
        self.assertEqual(brh.leaked_numbers("先求功率 612.5 W", self.NOTE), ["612.5"])
        self.assertEqual(brh.leaked_numbers("以 660 V 與 34 Ω 列 KVL", self.NOTE), [])
        self.assertEqual(brh.leaked_numbers("係數 13.5 不是答案", self.NOTE), [])

    def test_percent_given_may_appear_as_decimal(self):
        note = "## 已知與所求\n\n變壓器電抗 5%。\n\n## 考場標準作答\n\n\\(\\boxed{X=0.05}\\)，\\(\\boxed{I=0.25}\\)\n"
        self.assertEqual(brh.leaked_numbers("以 0.05 pu 列阻抗", note), [])
        self.assertEqual(brh.leaked_numbers("電流 0.25", note), ["0.25"])

    def test_every_generated_first_move_passes_the_leak_check(self):
        notes = {p.stem: p.read_text(encoding="utf-8") for p in ROOT.glob(brh.CANONICAL_GLOB)}
        written = brh.written_hints()
        for qid, move in written.items():
            self.assertEqual(brh.leaked_numbers(move, notes[qid]), [], qid)


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




class TestStageThreeMasking(unittest.TestCase):
    def test_result_values_in_traps_are_masked(self):
        note = "## 已知與所求\n\n電源 220 V。\n\n## 考場標準作答\n\n\\(\\boxed{V=380.0}\\)\n"
        out = brh.mask_trap_numbers("- 忘記乘 \\(\\sqrt3\\)，答成 219.39 V；會得 15 Ω；正確 380.0 V；電源 220 V", note)
        self.assertNotIn("219.39", out)
        self.assertNotIn("380.0", out)
        self.assertIn("答成 □", out)
        self.assertIn("220 V", out)

    def test_generated_traps_hide_known_leaks(self):
        traps = brh.build()["EE-107-04-4"]["trapsMd"]
        self.assertNotIn("228.83", traps)


if __name__ == "__main__":
    unittest.main()
