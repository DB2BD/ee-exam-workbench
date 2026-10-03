"""EE-111-05-1 (descriptive): series compensation of a transmission line.

Quantitative argument checked: with series capacitor X_C = k X_L the net series
reactance is X_L(1-k), so P_max = V_S V_R / X rises by 1/(1-k); the stability
margin at a fixed transfer also improves (smaller power angle).
"""
import numpy as np

VS = VR = 1.0
XL = 0.5
for k in (0.3, 0.5, 0.7):
    X = XL * (1 - k)
    Pmax_comp = VS * VR / X
    Pmax_unc = VS * VR / XL
    assert abs(Pmax_comp / Pmax_unc - 1 / (1 - k)) < 1e-12
    # same transfer P = 1.0 pu needs a smaller angle when compensated
    P = 1.0
    d_unc = np.degrees(np.arcsin(P * XL / (VS * VR)))
    d_comp = np.degrees(np.arcsin(P * X / (VS * VR)))
    assert d_comp < d_unc
# 50 % compensation doubles P_max; delta for 1 pu over X_L=0.5 drops from 30 deg to 14.48 deg
assert abs(1 / (1 - 0.5) - 2) < 1e-12
assert abs(np.degrees(np.arcsin(0.25)) - 14.4775) < 1e-3
print("PASS EE-111-05-1")
