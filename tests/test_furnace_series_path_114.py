"""Check electrode-short KVL with the depicted series path retained."""
import unittest
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "📝 個人題解與錯題本/06_工業配電/canonical/EE-114-06-2.md"


class TestFurnaceSeriesPath114(unittest.TestCase):
    def test_retired_generator_cannot_overwrite_annual_answers(self):
        annual = ROOT / "📝 個人題解與錯題本/06_工業配電/114年_工業配電_全卷完整詳細題解.md"
        before = annual.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / "scripts/gen_distribution_114.py")],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("已停用", result.stderr)
        self.assertEqual(annual.read_bytes(), before)

    def test_complex_kvl_and_bus_voltage(self):
        upstream = 1j * (25 / 2000 + 0.01 + 0.06)
        downstream = 1j * (0.05 + 0.4)
        current = 1 / (upstream + downstream)
        bus = 1 - current * upstream
        self.assertAlmostEqual(abs(current), 1.8779342723)
        self.assertAlmostEqual(bus.real, 0.8450704225)
        self.assertAlmostEqual(bus.imag, 0)
        self.assertAlmostEqual(abs(bus - current * downstream), 0)
        self.assertAlmostEqual(abs(current * (upstream + downstream) - 1), 0)
        self.assertAlmostEqual((1 - abs(bus)) * 100, 15.4929577465)
        open_current = 0j
        open_bus = 1 - open_current * upstream
        self.assertEqual(open_bus, 1)
        self.assertAlmostEqual(100 * (abs(open_bus) - abs(bus)) / 1, 15.4929577465)

    def assert_main_model(self, note):
        main = note.split("## 考場標準作答", 1)[1].split("\n## ", 1)[0]
        self.assertIn(r"\frac1{j0.5325}", main)
        self.assertIn(r"X_d=0.05+0.4=0.45", main)
        self.assertIn(r"0.84507", main)
        self.assertIn(r"\boxed{15.49\%}", main)
        self.assertIn(r"\boxed{0\%}", main)
        self.assertIn(r"\frac{1-0.84507}{1}", main)
        self.assertNotIn("62.26", main)

    def test_main_answer_contains_the_retained_path_equations(self):
        self.assert_main_model(NOTE.read_text(encoding="utf-8"))

    def test_main_answer_mutations_are_detected(self):
        note = NOTE.read_text(encoding="utf-8")
        for before, after in ((r"\frac1{j0.5325}", r"\frac1{j0.1325}"),
                              (r"\boxed{15.49\%}", r"\boxed{62.26\%}")):
            mutated = note.replace(before, after, 1)
            self.assertNotEqual(note, mutated)
            with self.assertRaises(AssertionError):
                self.assert_main_model(mutated)

    def test_bypassed_path_is_a_different_model(self):
        self.assertAlmostEqual(100 * 0.0825 / (0.0825 + 0.05), 62.2641509434)
        note = NOTE.read_text(encoding="utf-8")
        for phrase in ("15.49", "0.5325", "## 舊答案的條件界線",
                       "沒有畫出繞過", "不是取得官方評分答案"):
            self.assertIn(phrase, note)
        self.assertNotIn("沿用既有 verified", note)
