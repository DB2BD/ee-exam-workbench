"""Protect the turns-ratio boundary on 113 electronics Q4."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-113-02-4.md"


class TestFullBridgeBCM113(unittest.TestCase):
    def test_turns_ratio_is_declared_before_any_answer(self):
        text = NOTE.read_text(encoding="utf-8")
        self.assertIn("audit_status: needs_manual_review", text)
        self.assertIn("review_blocker:", text)
        self.assertIn("![官方題目裁切圖]", text)
        self.assertIn(r"\boxed{\frac{V_o}{V_s}=2Dn_h}", text)
        self.assertIn(r"n_h=N_s/N_p", text)
        self.assertIn(r"n_h=N_s/(2N_p)", text)
        self.assertNotIn(r"\boxed{\frac{V_o}{V_s}=2D\frac{N_s}{N_p}}", text)

    def test_both_turns_conventions_share_the_same_bcm_inductor(self):
        source, duty, resistance, frequency = 100.0, 0.2, 10.0, 20_000.0
        primary_turns, full_secondary_turns = 100.0, 50.0
        half_turns = full_secondary_turns / 2
        rectified_fraction = 2 * duty
        output = rectified_fraction * half_turns / primary_turns * source
        boundary_inductance = (1 - rectified_fraction) * resistance / (4 * frequency)
        # Per half-cycle, the inductor rises and falls by the same amount.
        rise = ((half_turns / primary_turns) * source - output) * duty / (boundary_inductance * frequency)
        fall = output * (0.5 - duty) / (boundary_inductance * frequency)
        self.assertAlmostEqual(output / source, duty * full_secondary_turns / primary_turns)
        self.assertAlmostEqual(rise, fall)
        self.assertAlmostEqual(rise / 2, output / resistance)
        self.assertAlmostEqual(boundary_inductance, 75e-6)


if __name__ == "__main__":
    unittest.main()
