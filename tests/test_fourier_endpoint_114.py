"""Keep the 114 math Fourier answer honest at its periodic jump."""

import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "📝 個人題解與錯題本/03_工程數學/canonical/EE-114-03-4.md"


class TestFourierEndpoint114(unittest.TestCase):
    def test_score_answer_distinguishes_function_from_series_at_jump(self):
        note = NOTE.read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"\boxed{f(x)\sim", standard)
        self.assertIn(r"f(\pi)=\pi", standard)
        self.assertIn(r"\pi/2", standard)
        self.assertIn("不能寫成逐點處處相等", standard)

    def test_independent_coefficients_and_endpoint_limit(self):
        # Integrals over [0, pi]: a0=pi/2,
        # an=((−1)^n−1)/(pi*n²), bn=(−1)^(n+1)/n.
        a0 = math.pi / 2
        for n in (1, 2, 3, 4):
            an = ((-1) ** n - 1) / (math.pi * n * n)
            bn = (-1) ** (n + 1) / n
            self.assertAlmostEqual(an, 0 if n % 2 == 0 else -2 / (math.pi * n * n))
            self.assertAlmostEqual(bn, (1 if n % 2 else -1) / n)
        partial_at_pi = a0 / 2 + sum(
            ((-1) ** n - 1) / (math.pi * n * n) * ((-1) ** n)
            for n in range(1, 20_001)
        )
        self.assertAlmostEqual(partial_at_pi, math.pi / 2, places=4)
        self.assertNotAlmostEqual(partial_at_pi, math.pi, places=2)

    def test_sine_coefficient_is_checked_at_a_nonzero_sine_point(self):
        note = NOTE.read_text(encoding="utf-8")
        self.assertIn(r"x=\pi/2", note)
        self.assertIn("不能**驗證", note)
        partial_at_half_pi = math.pi / 4 + sum(
            (((-1) ** n - 1) / (math.pi * n * n)) * math.cos(n * math.pi / 2)
            + ((-1) ** (n + 1) / n) * math.sin(n * math.pi / 2)
            for n in range(1, 100_001)
        )
        self.assertAlmostEqual(partial_at_half_pi, math.pi / 2, places=4)
        wrong_scale = math.pi / 4 + (partial_at_half_pi - math.pi / 4) / math.pi
        self.assertNotAlmostEqual(wrong_scale, math.pi / 2, places=2)


if __name__ == "__main__":
    unittest.main()
