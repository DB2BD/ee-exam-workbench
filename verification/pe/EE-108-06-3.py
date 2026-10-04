"""EE-108-06-3: V-V (open-delta) bank giving 3-phase 220 V, 1-phase 220 V and 110 V (4-wire).

Givens: two single-phase transformers, 11.4 kV primary, 110-220 V secondary (centre tap).
Phasor check of the secondary voltages from the winding arrangement.
"""
import numpy as np

VP = 220.0
e = lambda deg: np.exp(1j * np.deg2rad(deg))
V_xy = VP * e(0)                  # T1 secondary (X-Y), centre tap N
V_yz = VP * e(-120)               # T2 secondary (Y-Z), 120 deg from T1 (primaries on AB, BC)
V_zx = -(V_xy + V_yz)             # KVL around the open delta
for v in (V_xy, V_yz, V_zx):
    assert abs(abs(v) - 220.0) < 1e-9                      # three 220 V line voltages
V_xn = V_xy / 2                                            # X to centre tap
V_yn = -V_xy / 2                                           # Y to centre tap
V_zn = V_yn - V_yz                                         # Z to N via Y (V_ZY = -V_YZ)
assert abs(abs(V_xn) - 110.0) < 1e-9 and abs(abs(V_yn) - 110.0) < 1e-9
assert abs(abs(V_zn) - 110 * np.sqrt(3)) < 1e-9 and abs(abs(V_zn) - 190.526) < 5e-4   # high leg
assert abs((V_xy + V_yz + V_zx)) < 1e-9
print("PASS EE-108-06-3")
