"""Check open-delta capacity from winding current rather than a memorized ratio."""

import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "📝 個人題解與錯題本/06_工業配電/canonical/EE-114-06-1.md"


class TestOpenDelta114(unittest.TestCase):
    def test_rated_current_limits_balanced_load(self):
        winding_rating = 50_000
        secondary_voltage = 220
        line_current = winding_rating / secondary_voltage
        capacity = math.sqrt(3) * secondary_voltage * line_current
        self.assertAlmostEqual(line_current, 227.2727272727)
        self.assertAlmostEqual(capacity / 1000, 86.6025403784)
        self.assertAlmostEqual(capacity / (3 * winding_rating), 1 / math.sqrt(3))
        self.assertAlmostEqual(capacity / (2 * winding_rating), math.sqrt(3) / 2)
        # Both remaining windings reach rating, but their VA magnitudes
        # cannot simply be added as the balanced three-phase load capacity.
        self.assertAlmostEqual(secondary_voltage * line_current, winding_rating)
        self.assertLess(capacity, 2 * winding_rating)

    def test_solution_states_voltage_current_and_power_boundary(self):
        note = NOTE.read_text(encoding="utf-8")
        for phrase in (r"3300/220\,\mathrm{V}", r"I_{2N}",
                       "227.2727", r"S_{3\phi,\max}", "未給功率因數"):
            self.assertIn(phrase, note)
        self.assertNotIn("(Delta-", note)
        self.assertEqual(note.count("## 驗算"), 1)
