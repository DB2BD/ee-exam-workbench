"""EE-110-01-4 independent check: unbalanced Y load on a 4-wire supply.

Givens (official crop): Zan = 8/_30, Zbn = 4/_-50, Zcn = 6/_20 ohm; Vab =
208/_0, Vbc = 208/_-120, Vca = 208/_120 V rms; Y-Y four-wire (neutral tied).
The check uses complex power S = V I* per phase and also I^2 R.
"""
import cmath
import math

d = math.radians
Vab, Vbc = cmath.rect(208, 0), cmath.rect(208, d(-120))
# phase voltages from line voltages for a balanced set with neutral: Van - Vbn = Vab, etc.
Van = (Vab - cmath.rect(208, d(120))) / 3  # (Vab - Vca)/3
Vbn = Van - Vab
Vcn = Vbn - Vbc
Z = [cmath.rect(8, d(30)), cmath.rect(4, d(-50)), cmath.rect(6, d(20))]
P = 0.0
P_r = 0.0
for V, Zp in zip((Van, Vbn, Vcn), Z):
    I = V / Zp
    P += (V * I.conjugate()).real
    P_r += abs(I) ** 2 * Zp.real
print(f"|Van|={abs(Van):.4f} ang={math.degrees(cmath.phase(Van)):.2f}  P={P:.3f} W  P(I2R)={P_r:.3f}")
assert abs(P - P_r) < 1e-9
assert abs(P - 6137.22) / 6137.22 < 1e-5
print("PASS EE-110-01-4")
