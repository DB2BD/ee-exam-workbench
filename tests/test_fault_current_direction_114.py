"""Protect current reference directions in the 114 power-system fault answer."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "📝 個人題解與錯題本/05_電力系統/canonical/EE-114-05-4.md"


class TestFaultCurrentDirection114(unittest.TestCase):
    def test_score_answer_declares_and_reverses_line_current_directions(self):
        note = NOTE.read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("![官方題目裁切圖]", note)
        self.assertIn("題圖未指定線路電流正方向", standard)
        for name in (r"I_{31}", r"I_{21}", r"I_{13}", r"I_{12}"):
            self.assertIn(name, standard)

    def test_independent_branch_kcl_and_reverse_reference(self):
        left, right, fault = 0.1 + 0.4, 0.2 + 0.1, 0.0125
        thevenin = 1 / (1 / left + 1 / right)
        fault_current = 1 / (1j * (thevenin + fault))
        bus1 = fault_current * 1j * fault
        current31 = (1 - bus1) / (1j * left)
        current21 = (1 - bus1) / (1j * right)
        self.assertAlmostEqual(thevenin, 0.1875)
        self.assertAlmostEqual(fault_current.imag, -5)
        self.assertAlmostEqual(bus1.real, 0.0625)
        self.assertAlmostEqual(current31.imag, -1.875)
        self.assertAlmostEqual(current21.imag, -3.125)
        self.assertAlmostEqual(current31 + current21, fault_current)
        self.assertAlmostEqual((-current31).imag, 1.875)
        self.assertAlmostEqual((-current21).imag, 3.125)


if __name__ == "__main__":
    unittest.main()
