"""EE-107-04-1: three 66 kVA, 6600/220 V single-phase transformers, 3-phase 4-wire 11.4 kV source,
load 165 kVA / 380 V / 0.8 pf lag.  Actual source line voltage 10.92 kV.
Main model: load draws 165 kVA (constant apparent power).  Branch: load is a fixed impedance rated 165 kVA at 380 V."""
import numpy as np

Sunit, Vp, Vs = 66e3, 6600.0, 220.0
Vsrc_nom, Vload, Sload, pf = 11.4e3, 380.0, 165e3, 0.8
a = Vp / Vs
# connection check: Y-Y with neutral reproduces the supplied/required voltages
assert abs(Vsrc_nom / np.sqrt(3) - Vp) / Vp < 0.005          # primary phase 6.58 kV ~ 6.6 kV
assert abs(Vs * np.sqrt(3) - Vload) / Vload < 0.005          # secondary line 381 V ~ 380 V
assert 3 * Sunit >= Sload                                    # 198 kVA >= 165 kVA
V_actual = 10.92e3
# main model (constant 165 kVA)
IL = Sload / (np.sqrt(3) * V_actual)
util = (Sload / 3) / Sunit
assert abs(IL - 8.724) / 8.724 <= 0.005
assert abs(util - 0.8333) / 0.8333 <= 0.005
# independent: phase-by-phase, power balance of each transformer
Iph_prim = (Sload / 3) / (V_actual / np.sqrt(3))
assert abs(Iph_prim - IL) < 1e-9                            # Y: line = phase current
Iline_sec = Sload / (np.sqrt(3) * Vload)                    # 250.7 A at 380 V, rated 300 A per unit
assert Iline_sec < Sunit / Vs
# branch: constant impedance load (rated 165 kVA at 380 V) on the sagging bus
k = V_actual / Vsrc_nom
Vsec_line = V_actual / a                                   # Y-Y: line ratio = phase ratio
S_actual = Sload * (Vsec_line / Vload) ** 2
IL_b = S_actual / (np.sqrt(3) * V_actual)
util_b = S_actual / 3 / Sunit
print(f"main: IL={IL:.4f} A util={util*100:.2f}% | Z-branch: Vsec={Vsec_line:.1f} V S={S_actual/1e3:.2f} kVA IL={IL_b:.3f} A util={util_b*100:.2f}%")
assert abs(IL_b - 8.005) / 8.005 <= 0.005
assert abs(util_b - 0.7646) / 0.7646 <= 0.005
assert abs(S_actual - 151.40e3) / 151.40e3 <= 0.005
# secondary-side check (independent): 364 V, 165 kVA -> 261.7 A, /30 -> 8.724 A
assert abs(Sload / (np.sqrt(3) * 364.0) - 261.7) / 261.7 <= 0.005
assert abs(Sload / (np.sqrt(3) * 364.0) / 30 - 8.724) / 8.724 <= 0.005
assert abs(S_actual / (np.sqrt(3) * 364.0) - 240.1) / 240.1 <= 0.005
assert abs(IL_b - Sload / (np.sqrt(3) * Vsrc_nom) * k) / IL_b < 0.002
print("PASS EE-107-04-1")
