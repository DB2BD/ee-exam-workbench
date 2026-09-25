"""Independent constants and score answers for the 114 power-system mock."""

import cmath
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "📝 個人題解與錯題本/05_電力系統/canonical"


class TestPowerSystem114OfficialValues(unittest.TestCase):
    def test_all_five_score_answers_show_the_official_question(self):
        for number in range(1, 6):
            with self.subTest(number=number):
                note = (NOTES / f"EE-114-05-{number}.md").read_text(encoding="utf-8")
                self.assertIn("![官方題目裁切圖]", note)
                self.assertIn("## 考場標準作答", note)

    def test_complex_power_uses_rms_and_current_conjugate(self):
        # Official Q1: V=100∠alpha, I=I_rms∠60°, P=500√3 W, Q=500 var.
        power = complex(500 * math.sqrt(3), 500)
        current_rms = abs(power) / 100
        voltage_angle = math.degrees(cmath.phase(power)) + 60
        self.assertAlmostEqual(current_rms, 10)
        self.assertAlmostEqual(voltage_angle, 90)
        note = (NOTES / "EE-114-05-1.md").read_text(encoding="utf-8")
        self.assertIn(r"\boxed{I_{rms}=|S|/|V|=1000/100=10", note)
        self.assertIn(r"\boxed{\alpha=90^\circ}", note)

    def test_pv_limit_and_flat_start_newton_step(self):
        # Official Q2: 100-MVA base, Pg=100 MW, Pl=250 MW, Ql=100 Mvar.
        p_net = (100 - 250) / 100
        angle = math.asin(p_net / 10)
        q_generated = 100 * (10 * (1 - math.cos(angle)) + 1)
        self.assertAlmostEqual(math.degrees(angle), -8.6269266, places=5)
        self.assertAlmostEqual(q_generated, 111.3140, places=3)
        self.assertGreater(q_generated, 100)
        # At delta=0, |V|=1 the Jacobian is diag(10,10).
        self.assertAlmostEqual(p_net / 10, -0.15)
        self.assertAlmostEqual(math.degrees(-0.15), -8.5943669, places=5)

    def test_convex_dispatch_satisfies_both_marginal_costs(self):
        # Official Q3: C1=400+6P1+.004P1², C2=400+6.8P2+.002P2².
        demand = 550
        p1 = (6.8 + 0.004 * demand - 6) / (0.008 + 0.004)
        p2 = demand - p1
        self.assertAlmostEqual(p1, 250)
        self.assertAlmostEqual(p2, 300)
        self.assertAlmostEqual(6 + 0.008 * p1, 6.8 + 0.004 * p2)
        self.assertTrue(0 <= p1 <= 800 and 0 <= p2 <= 800)

    def test_two_pole_swing_equation_keeps_electrical_mechanical_units(self):
        # Official Q5: two poles, 60 Hz, H=4.32 s, 60 MW on 250 MVA,
        # then electrical load removed for 12 cycles at constant acceleration.
        frequency, inertia, mechanical_power = 60, 4.32, 60 / 250
        alpha_electrical = (2 * math.pi * frequency) * mechanical_power / (2 * inertia)
        seconds = 12 / frequency
        rpm = 120 * frequency / 2 + alpha_electrical * seconds * 60 / (2 * math.pi)
        self.assertAlmostEqual(alpha_electrical, 10 * math.pi / 3)
        self.assertAlmostEqual(rpm, 3620)


if __name__ == "__main__":
    unittest.main()
