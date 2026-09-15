# -*- coding: utf-8 -*-
"""Regression checks for the verified 114 PE power-system fault solution."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOLUTION = ROOT / "📝 個人題解與錯題本/05_電力系統/canonical/EE-114-05-4.md"


class TestEE11405Q4Solution(unittest.TestCase):
    def test_solution_accounts_for_transformer_and_kcl(self):
        text = SOLUTION.read_text(encoding="utf-8")
        expected = (
            "j0.4",
            "j0.5",
            "j0.1875",
            "-j5.0",
            "-j1.875",
            "-j3.125",
            "0.0625",
            "0.6875",
            "0.8125",
        )
        for value in expected:
            self.assertIn(value, text, value)
        self.assertNotIn("11.4286", text)
        self.assertNotIn("0.075", text)

    def test_diagram_values_recalculate_to_canonical_results(self):
        left_branch_x = 0.1 + 0.4
        right_branch_x = 0.2 + 0.1
        fault_x = 0.0125
        z_th_x = (left_branch_x * right_branch_x) / (left_branch_x + right_branch_x)
        fault_current = 1 / (z_th_x + fault_x)
        bus_1_voltage = fault_current * fault_x
        left_current = (1 - bus_1_voltage) / left_branch_x
        right_current = (1 - bus_1_voltage) / right_branch_x

        self.assertAlmostEqual(z_th_x, 0.1875)
        self.assertAlmostEqual(fault_current, 5.0)
        self.assertAlmostEqual(bus_1_voltage, 0.0625)
        self.assertAlmostEqual(left_current, 1.875)
        self.assertAlmostEqual(right_current, 3.125)
        self.assertAlmostEqual(left_current + right_current, fault_current)


if __name__ == "__main__":
    unittest.main()
