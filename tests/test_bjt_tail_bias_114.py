"""Keep the 114 differential-pair bias assumption visible beside its numbers."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "02_題解/技師題解/02_電子學_含電力電子/canonical/EE-114-02-1.md"


class TestBJTTailBias114(unittest.TestCase):
    def test_numeric_answer_states_its_bias_and_beta_assumptions(self):
        note = NOTE.read_text(encoding="utf-8")
        self.assertIn("數值答案的偏壓前提", note)
        self.assertIn("直流分流", note)
        self.assertIn("唯一精確答案", note)
        self.assertIn(r"I_C\approx I_E", note)
        for expected in ("0.975610", "0.0390244", "1025", "514.097", "312.195"):
            self.assertIn(expected, note)

    def test_finite_beta_branch_recalculates_the_three_cases(self):
        beta = 40
        emitter_current = 0.001  # conditional: total tail emitter current is 2 mA
        collector_current = emitter_current * beta / (beta + 1)
        gm = collector_current / 0.025
        r_pi = beta / gm
        a = gm + 1 / r_pi
        emitter_factor = a / (1 / 2000 + 2 * a)
        for ratio, expected_ri, expected_gain in (
            (-1, 1025.0, 156.097561),
            (1, 165025.0, 0.0),
            (-3, 514.096573, 312.195122),
        ):
            with self.subTest(ratio=ratio):
                ri = r_pi / (1 - emitter_factor * (1 + ratio))
                gain = gm * 2000 * (1 - ratio)
                self.assertAlmostEqual(ri, expected_ri, places=3)
                self.assertAlmostEqual(gain, expected_gain, places=5)


if __name__ == "__main__":
    unittest.main()
