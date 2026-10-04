"""EE-105-01-4: balanced 3-phase, VL = 34.5 kV, 60 Hz, load 24 MVA pf 0.78 lag; wye capacitors (connected to neutral) to reach pf 0.94 lead."""
import numpy as np
VL, f = 34.5e3, 60.0
S = 24e6; pf = 0.78
P = S * pf; Q = S * np.sqrt(1 - pf**2)
Qnew = -P * np.tan(np.arccos(0.94))
Qc = Q - Qnew                       # total capacitive var needed
w = 2 * np.pi * f
Vph = VL / np.sqrt(3)
C = Qc / (3 * w * Vph**2)
assert abs(C - 48.62e-6) / 48.62e-6 < 5e-3, C
# check: apply C and compute resulting pf
Qres = Q - 3 * w * C * Vph**2
pf_res = P / np.hypot(P, Qres)
assert abs(pf_res - 0.94) < 1e-6 and Qres < 0
print("PASS EE-105-01-4")
