"""EE-106-06-3: three single-phase 200 kVA transformers (3450-3300-3150 V / 110-220 V), 3-phase 3.3 kV
supply, 3-phase 380 V motor load; one unit replaced by (3450-3300-3150 V / 105-210 V).
Phasor/turn-ratio check of the delta-wye connection and of the substitute tap choice.
"""
import numpy as np

V_LINE_HV, V_LL_LV = 3300.0, 380.0
# delta primary: each winding sees the line voltage -> 3300 V tap
n = 3300.0 / 220.0
assert n == 15.0
v_ph = V_LINE_HV / n
v_ll = np.sqrt(3) * v_ph
assert abs(v_ph - 220.0) < 1e-9 and abs(v_ll - 381.05) < 0.01 and abs(v_ll - V_LL_LV) / V_LL_LV < 5e-3
# wye primary would put only 3300/sqrt3 = 1905 V on a winding (58 % of the 3300 V tap): rejected
assert abs(V_LINE_HV / np.sqrt(3) / 3300 - 0.5774) < 1e-4

# substitute unit: candidate (primary tap, secondary tap) combinations
ratios = {(p, s): p / s for p in (3450.0, 3300.0, 3150.0) for s in (105.0, 210.0)}
target = 15.0
best = min(ratios, key=lambda k: abs(ratios[k] - target))
assert best == (3150.0, 210.0) and ratios[best] == 15.0
assert abs(ratios[(3300.0, 210.0)] - 15.714) < 1e-3 and abs(ratios[(3450.0, 210.0)] - 16.429) < 1e-3
# secondary winding voltage of the substitute at each candidate, 3300 V applied
v2 = {k: V_LINE_HV / r for k, r in ratios.items() if k[1] == 210.0}
assert abs(v2[(3150.0, 210.0)] - 220.0) < 1e-9
assert abs(v2[(3300.0, 210.0)] - 210.0) < 1e-9
# 3150 V tap carries 3300 V: flux density 4.8 % above that tap's rating
assert abs(3300 / 3150 - 1 - 0.0476) < 5e-4
# phase-to-phase unbalance if (3300, 210) were used: one phase 210 V, two phases 220 V
va, vb, vc = 210 * np.exp(0j), 220 * np.exp(-2j * np.pi / 3), 220 * np.exp(2j * np.pi / 3)
vab = abs(va - vb)
vbc = abs(vb - vc)
assert vbc > vab                                  # line voltages differ -> unbalance
print("PASS EE-106-06-3")
