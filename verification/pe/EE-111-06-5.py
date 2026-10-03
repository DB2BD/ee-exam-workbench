"""EE-111-06-5: low-resistance grounding resistor rating and 5-20 % criterion.

Stem givens: 161 kV, S_sc = 10000 MVA; transformer 161/33 kV, 100 MVA, Z = 12 %;
secondary neutral grounded through 18 ohm; criterion 5 %-20 % of secondary short-circuit current;
base 100 MVA.
"""
import numpy as np

V_LL, R_N, SB = 33e3, 18.0, 100e6
xs, xt = 100 / 10000, 0.12
v_r = V_LL / np.sqrt(3)
i_r = v_r / R_N
assert abs(v_r / 1e3 - 19.05) / 19.05 < 0.005       # boxed 19.05 kV
assert abs(i_r - 1058) / 1058 < 0.005                # boxed 1058 A
ib = SB / (np.sqrt(3) * V_LL)
i_sc = ib / (xs + xt)
assert abs(i_sc / 1e3 - 13.46) / 13.46 < 0.005       # boxed 13.46 kA
ratio = i_r / i_sc * 100
assert abs(ratio - 7.865) / 7.865 < 0.005 and 5 <= ratio <= 20    # boxed 7.87 % -> complies
# independent check: SLG fault through the resistor with sequence networks (Dyn transformer, Z0 = XT)
zb = V_LL ** 2 / SB
z1 = z2 = 1j * (xs + xt)
z0 = 1j * xt + 3 * R_N / zb
i_slg = abs(3 / (z1 + z2 + z0)) * ib
assert abs(i_slg - i_r) / i_r < 0.005                # resistor dominates: within 0.5 % of V/R
print("PASS EE-111-06-5")
