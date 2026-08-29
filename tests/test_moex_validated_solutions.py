# -*- coding: utf-8 -*-
"""Independent numerical locks for the first validated 114 circuit paper."""

import cmath
import math
import pathlib
import unittest


WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
SOLUTION = WORKSPACE / "📝 個人題解與錯題本" / "🏛️_國考同級題解" / "01_電路學" / "GK_114年_電路學_全卷完整詳細題解.md"
SOLUTION_113 = WORKSPACE / "📝 個人題解與錯題本" / "🏛️_國考同級題解" / "01_電路學" / "GK_113年_電路學_全卷完整詳細題解.md"
SOLUTION_110 = WORKSPACE / "📝 個人題解與錯題本" / "🏛️_國考同級題解" / "01_電路學" / "GK_110年_電路學_全卷完整詳細題解.md"


class TestMoexValidatedSolutions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solution_text = SOLUTION.read_text(encoding="utf-8")

    def test_solution_metadata_is_bound_to_questions(self):
        self.assertIn("source_pdf_sha256: de506894783a42a57c1fc823e44d079dc6d05df5550d91fbf621c9f3d8c08f4d", self.solution_text)
        self.assertIn("validated_question_ids: [GK-114-01-1, GK-114-01-2, GK-114-01-3, GK-114-01-4]", self.solution_text)

    def test_113_solution_hash_is_real_manifest_hash(self):
        source = (WORKSPACE / "data/moex-national-exams.json").read_text(encoding="utf-8")
        self.assertIn("8fc6cfaed5498a07aec5d414840ccf725eb908af5819fe51d65608d10ae0ec08", source)
        solution = (WORKSPACE / "📝 個人題解與錯題本" / "🏛️_國考同級題解" / "01_電路學" / "GK_113年_電路學_全卷完整詳細題解.md").read_text(encoding="utf-8")
        self.assertIn("source_pdf_sha256: 8fc6cfaed5498a07aec5d414840ccf725eb908af5819fe51d65608d10ae0ec08", solution)

    def test_113_rc_solution_coefficients(self):
        solution = SOLUTION_113.read_text(encoding="utf-8")
        self.assertIn("validated_question_ids: [GK-113-01-1, GK-113-01-2, GK-113-01-3, GK-113-01-4]", solution)
        self.assertAlmostEqual(0.5 * 20, 10.0)
        self.assertAlmostEqual(20 / 4, 5.0)
        self.assertAlmostEqual(0.4 / 5, 0.08)
        self.assertAlmostEqual(0.5 * 0.4 * 5 * 5, 5.0)

    def test_113_abcd_matrix_and_power_results(self):
        # [1 2; 0 1] [1 0; 1/4 1] [1 6; 0 1]
        a, b, c, d = 1.5, 11.0, 0.25, 2.5
        self.assertAlmostEqual(a * d - b * c, 1.0)
        self.assertAlmostEqual(8 * 8 / (4 * 8), 2.0)
        self.assertAlmostEqual((20 / math.sqrt(2)) ** 2 * 4, 800.0)

    def test_110_thevenin_and_transient_results(self):
        solution = SOLUTION_110.read_text(encoding="utf-8")
        self.assertIn("source_pdf_sha256: 2060a527e32418392c8c40b266d5a14dcc7ad11b0fa550189774408fb04b2e9b", solution)
        self.assertIn("validated_question_ids: [GK-110-01-1, GK-110-01-2, GK-110-01-3, GK-110-01-4]", solution)
        self.assertAlmostEqual(6 / 0.0075, 800.0)
        self.assertAlmostEqual(6 - (8 + 20 * 0), -2.0)
        self.assertAlmostEqual(-20 + 5 * 8, 20.0)

    def test_110_complex_and_resistive_maximum_power(self):
        vth_peak_sq = 50 ** 2 + 50 ** 2
        rth, xth = 100.0, 25.0
        zmag = math.hypot(rth, xth)
        p_conjugate = vth_peak_sq / (8 * rth)
        p_resistive = vth_peak_sq / (4 * (rth + zmag))
        self.assertAlmostEqual(p_conjugate, 6.25)
        self.assertAlmostEqual(zmag, 25 * math.sqrt(17))
        self.assertLess(p_resistive, p_conjugate)

    def test_q1_nodal_values_and_kcl(self):
        va, vb = -4.0, -1.6
        self.assertAlmostEqual((va - 12) / 40 + va / 80 + (va - vb) / 48 + 0.5, 0.0)
        self.assertAlmostEqual((vb - va) / 48 + vb / 32, 0.0)
        self.assertAlmostEqual((12 - va) / 40, 0.4)
        self.assertAlmostEqual(va / 80, -0.05)
        self.assertAlmostEqual((vb - va) / 48, 0.05)
        self.assertAlmostEqual(-vb / 32, 0.05)

    def test_q2_piecewise_time_constants_and_continuity(self):
        inductance = 2e-3
        self.assertAlmostEqual(inductance / 2.0, 1e-3)
        parallel_resistance = (2.0 * 2.0) / (2.0 + 2.0)
        self.assertAlmostEqual(inductance / parallel_resistance, 2e-3)

    def test_q3_transformer_polarity_and_kvl(self):
        def polar(magnitude, degrees):
            return magnitude * cmath.exp(1j * math.radians(degrees))

        v2 = polar(48, 30)
        v1 = -v2 / 2
        i2 = v2 / 24
        i1 = -2 * i2
        vs = v1 + (6 - 1j * 6) * i1
        self.assertAlmostEqual(abs(v1), 24.0, places=8)
        self.assertAlmostEqual(abs(i1), 4.0, places=8)
        self.assertAlmostEqual(vs.real, -53.5692193817, places=8)
        self.assertAlmostEqual(vs.imag, -3.2153903092, places=8)

    def test_q4_current_limit_sets_maximum_gain(self):
        gain = 0.2 / (1 / 50 + 1 / 10000)
        r1 = 10000 / gain
        r2 = 10000 - r1
        self.assertAlmostEqual(gain, 2000 / 201, places=10)
        self.assertAlmostEqual(r1, 1005.0, places=8)
        self.assertAlmostEqual(r2, 8995.0, places=8)
        self.assertLess(gain, 15.0)


if __name__ == "__main__":
    unittest.main()
