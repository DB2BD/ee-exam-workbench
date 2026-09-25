"""Guard the official 113 electronics Q3 Buck/BCM topology and results."""

import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-113-02-3.md"


class TestBuckBCM113(unittest.TestCase):
    def test_solution_matches_the_series_switch_and_freewheel_diode(self):
        note = NOTE.read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("chapter: 降壓型轉換器的邊界導通模式", note)
        self.assertIn("![官方題目裁切圖]", note)
        self.assertIn("降壓型Buck轉換器二操作狀態等效電路圖.svg", note)
        for expression in (r"v_L=V_s-V_o", r"v_L=-V_o", r"\boxed{V_o=DV_s}",
                           r"\boxed{L_{\min}=\frac{(1-D)R}{2f_s}}", r"\frac{1}{4RCf_s}"):
            with self.subTest(expression=expression):
                self.assertIn(expression, standard)
        self.assertNotIn(r"\boxed{V_o=\frac{V_s}{1-D}}", standard)

    def test_independent_boundary_and_capacitor_charge(self):
        source, duty, resistance, frequency, capacitance = 12, 0.4, 10, 25_000, 100e-6
        output = duty * source
        boundary_inductance = (1 - duty) * resistance / (2 * frequency)
        load_current = output / resistance
        peak = (source - output) * duty / (boundary_inductance * frequency)
        fall = output * (1 - duty) / (boundary_inductance * frequency)
        ripple = load_current / (4 * capacitance * frequency)
        self.assertAlmostEqual(boundary_inductance, 120e-6)
        self.assertAlmostEqual(peak, fall)
        self.assertAlmostEqual(peak, 2 * load_current)
        self.assertAlmostEqual(ripple / output, 1 / (4 * resistance * capacitance * frequency))
        self.assertAlmostEqual(ripple, 0.048)


if __name__ == "__main__":
    unittest.main()
