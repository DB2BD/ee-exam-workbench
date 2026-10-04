"""Regress the retained 8-ohm branch in the 114 circuit superposition answer."""

import cmath
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "02_題解/技師題解/01_電路學/canonical/EE-114-01-4.md"


class TestSuperposition114(unittest.TestCase):
    def test_ten_radian_current_source_keeps_the_resistor(self):
        text = NOTE.read_text(encoding="utf-8")
        admittance = 1 / 8 + 1j * (10 * 0.2 - 1 / (10 * 1))
        voltage = 6 / admittance
        self.assertAlmostEqual(voltage.real, 0.2068608861, places=8)
        self.assertAlmostEqual(voltage.imag, -3.1442854680, places=8)
        self.assertAlmostEqual(abs(voltage), 3.1510827553, places=8)
        self.assertAlmostEqual(math.degrees(cmath.phase(voltage)) + 90, 3.7640348649, places=8)
        self.assertIn(r"\frac6{1/8+j1.9}", text)
        self.assertIn("3.15108", text)
        self.assertIn("3.76403", text)
        self.assertNotIn(r"V_{o,10}=\frac6{j1.9}=-j3.1579", text)

    def test_five_radian_voltage_divider_is_independent(self):
        text = NOTE.read_text(encoding="utf-8")
        admittance = 1j * (5 * 0.2 - 1 / (5 * 1))
        voltage = 75 / (1 + 8 * admittance)
        self.assertAlmostEqual(abs(voltage), 11.5782660205, places=8)
        self.assertAlmostEqual(math.degrees(cmath.phase(voltage)), -81.1193408495, places=8)
        self.assertIn("11.5783", text)
        self.assertIn("81.1193", text)


if __name__ == "__main__":
    unittest.main()
