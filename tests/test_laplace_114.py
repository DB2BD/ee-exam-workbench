"""Independent time-domain check for the 114 dependent-source Laplace answer."""

import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "02_題解/技師題解/01_電路學/canonical/EE-114-01-5.md"


class TestLaplace114(unittest.TestCase):
    def test_time_domain_supernode_equation_and_transient(self):
        note = NOTE.read_text(encoding="utf-8")
        self.assertIn(r"\dot v_o+4v_o=125", note)
        self.assertIn(r"v_c=v_a-2i_x=\frac35v_o+\frac25\dot v_o", note)
        self.assertIn(r"31.25(1-e^{-4t})", note)
        for t in (0.0, 0.05, 0.25, 1.0):
            value = 31.25 * (1 - math.exp(-4 * t))
            derivative = 125 * math.exp(-4 * t)
            self.assertAlmostEqual(derivative + 4 * value, 125.0)
            current = value / 5
            middle_node_voltage = 0.6 * value + 0.4 * derivative
            self.assertAlmostEqual(current + middle_node_voltage / 5, 10.0)


if __name__ == "__main__":
    unittest.main()
