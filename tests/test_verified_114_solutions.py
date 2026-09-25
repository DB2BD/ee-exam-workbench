# -*- coding: utf-8 -*-
"""Regression checks for independently rechecked 114 PE solutions."""

import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ELECTRONICS_Q3 = ROOT / "📝 個人題解與錯題本/02_電子學_含電力電子/canonical/EE-114-02-3.md"
MACHINES_Q5 = ROOT / "📝 個人題解與錯題本/04_電機機械/canonical/EE-114-04-5.md"
ELECTRONICS_ANNUAL = ROOT / "📝 個人題解與錯題本/02_電子學_含電力電子/114年_電子學_全卷完整詳細題解.md"
ECONOMIC_DISPATCH_Q2 = ROOT / "📝 個人題解與錯題本/05_電力系統/canonical/EE-112-05-2.md"
POWER_112_ANNUAL = ROOT / "📝 個人題解與錯題本/05_電力系統/112年_電力系統_全卷完整詳細題解.md"
POWER_112_Q4 = ROOT / "📝 個人題解與錯題本/05_電力系統/canonical/EE-112-05-4.md"


class TestEE11402Q3Solution(unittest.TestCase):
    def test_switch_states_recalculate_the_inductor_waveform(self):
        text = ELECTRONICS_Q3.read_text(encoding="utf-8")
        self.assertIn("先開路、後短路", text)
        self.assertIn(r"L\dot i_L+Ri_L=V_S-E=-5", text)
        self.assertIn(r"L\dot i_L+Ri_L=-E=-10", text)
        self.assertIn("題面沒有", text)
        self.assertIn(r"i_L(1\,\mathrm{ms})=i_L(0)", text)
        self.assertIn("-15.025000", text)
        self.assertIn("-14.975000", text)
        tau = 0.025 / 0.5
        a = math.exp(-0.0005 / tau)
        i_start = -10 * (2 + a) / (1 + a)
        i_switch = -10 + (i_start + 10) * a
        i_end = -20 + (i_switch + 20) * a
        self.assertAlmostEqual(i_start, -15.02499979, places=6)
        self.assertAlmostEqual(i_switch, -14.97500021, places=6)
        self.assertAlmostEqual(i_end, i_start, places=10)
        self.assertLess(i_switch, 0)

    def test_annual_note_uses_the_same_switch_state_order(self):
        text = ELECTRONICS_ANNUAL.read_text(encoding="utf-8")
        self.assertIn("先開路、後短路", text)
        self.assertIn(r"L\dot i_L+Ri_L=V_S-E=-5", text)
        self.assertIn(r"L\dot i_L+Ri_L=-E=-10", text)
        self.assertIn("-15.025000", text)
        self.assertIn("-14.975000", text)


class TestEE11404Q5Solution(unittest.TestCase):
    def test_official_product_to_sum_typo_is_flagged(self):
        text = MACHINES_Q5.read_text(encoding="utf-8")
        mock = (ROOT / "docs/上榜被動模考_114年六科執行包.md").read_text(encoding="utf-8")
        for source in (text, mock):
            self.assertIn("Hint", source)
            self.assertIn("誤植", source)
            self.assertIn(r"\cos u\sin v", source)
        alpha = beta = math.pi / 2
        self.assertNotAlmostEqual(
            math.sin(alpha) * math.sin(beta),
            (math.sin(alpha + beta) + math.sin(alpha - beta)) / 2,
        )

    def test_average_torque_keeps_the_cosine_squared_factor(self):
        text = MACHINES_Q5.read_text(encoding="utf-8")
        standard = text.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"T=\tfrac12\phi^2\,d\mathcal R/d\theta", text)
        self.assertIn(r"T(t)=+2\mathcal R_1\Phi_m^2\cos^2(\omega t)\sin(4\omega_mt+4\delta)", standard)
        self.assertIn(r"T_{avg}=\tfrac12\mathcal R_1\Phi_m^2\sin4\delta", standard)
        self.assertIn(r"T_{avg}=+\frac{1}{2}\mathcal R_1\Phi_m^2\sin(4\delta)", text)
        self.assertIn(r"|T_{avg,max}|=\frac{1}{2}\mathcal R_1\Phi_m^2=3.4055", text)
        self.assertIn(r"0.642\;\mathrm{kW}", text)
        self.assertNotIn(r"T(t)=-2\mathcal R_1", standard)
        self.assertNotIn(r"T_{avg}=-\frac{1}{2}\mathcal R_1", text)
        self.assertNotIn(r"|T_{avg,max}|=\mathcal R_1\Phi_m^2=6.811", text)

        flux_peak = 8.2530e-3
        torque_max = 0.5 * 1.0e5 * flux_peak**2
        power_max = torque_max * 60 * math.pi
        self.assertAlmostEqual(torque_max, 3.4055, places=3)
        self.assertAlmostEqual(power_max / 1000, 0.6419, places=3)

        # Numerically integrate the official positive-sign torque expression
        # over one 60-Hz electrical cycle, for both synchronous directions.
        phase = math.pi / 8  # sin(4 delta)=1
        for direction in (1, -1):
            samples = 20_000
            normalized_mean = sum(
                2 * math.cos(2 * math.pi * k / samples) ** 2
                * math.sin(direction * 4 * math.pi * k / samples + 4 * phase)
                for k in range(samples)
            ) / samples
            self.assertAlmostEqual(normalized_mean, 0.5, places=6)


class TestEE11205Q2AuditDisposition(unittest.TestCase):
    def test_capacity_boundary_ambiguity_cannot_be_published_as_verified(self):
        text = ECONOMIC_DISPATCH_Q2.read_text(encoding="utf-8")
        self.assertIn("audit_status: needs_manual_review", text)
        self.assertIn("P_2=800", text)
        self.assertIn(r"P_{1b}=800", text)
        self.assertIn("不得把其中一組當成唯一答案", text)
        self.assertIn(r"\beta=8", text)
        self.assertIn(r"\gamma=\frac{1}{1100}=0.00090909", text)
        self.assertNotIn("6.8667", text)
        self.assertNotIn("0.001875", text)

        # The two boundary interpretations both satisfy the two supplied
        # lambda points, so the official crop does not identify one unique
        # coefficient pair without an additional boundary convention.
        beta_p2 = 8 - 0.004 * (550 - 1 / (2 * 0.003))
        gamma_p2 = (10 - 7) / (2 * 500)
        beta_p1 = 10 - 0.004 * 500
        gamma_p1 = (8 - 7) / (2 * 550)
        self.assertAlmostEqual(beta_p2, 6.4666666667, places=8)
        self.assertAlmostEqual(gamma_p2, 0.003, places=8)
        self.assertAlmostEqual(beta_p1, 8, places=8)
        self.assertAlmostEqual(gamma_p1, 1 / 1100, places=8)
        self.assertLessEqual(7 + 2 * gamma_p1 * 800, 10)


class TestAnnualPowerNotesFollowCanonicalPrimaryAnswers(unittest.TestCase):
    def test_112_q1_annual_note_matches_the_official_spacing(self):
        annual = POWER_112_ANNUAL.read_text(encoding="utf-8")
        q1 = annual.split("## 二、", 1)[0]
        self.assertIn(r"D_{ab}=15\,\mathrm{m}", q1)
        self.assertIn(r"D_{ca}=30\,\mathrm{m}", q1)
        self.assertIn("0.8873", q1)
        self.assertIn("0.01269", q1)
        self.assertNotIn("0.8061", q1)
        self.assertNotIn("故障前與復閉後的轉移電抗", q1)

    def test_112_q4_annual_note_does_not_promote_the_sensitivity_branch(self):
        annual = POWER_112_ANNUAL.read_text(encoding="utf-8")
        canonical = POWER_112_Q4.read_text(encoding="utf-8")
        self.assertIn("主答案", annual)
        self.assertIn("101.0936492", annual)
        self.assertIn("102.0837294", annual)
        self.assertIn("原題符號的歧義與替代結果", annual)
        self.assertIn("字面實阻抗結果", annual)
        self.assertIn("主解：等效接地電抗", canonical)
        self.assertNotIn("主分支取 $Z_f=0.01$ pu", annual)

    def test_112_q2_annual_note_keeps_all_capacity_branches_manual(self):
        annual = POWER_112_ANNUAL.read_text(encoding="utf-8")
        self.assertIn("6.4667", annual)
        self.assertIn("0.00090909", annual)
        self.assertIn(r"\beta=8", annual)
        self.assertIn("維持 `needs_manual_review`", annual)
        self.assertIn("不得把其中一組當成唯一答案", annual)
        self.assertNotIn("6.8667", annual)
        self.assertNotIn("0.001875", annual)


if __name__ == "__main__":
    unittest.main()
