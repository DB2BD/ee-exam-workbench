"""EE-114-06-1: open-delta (V-V) capacity of two remaining 50 kVA, 3300/220 V units.

Method: phasor model of the two remaining windings carrying a balanced load;
the limiting quantity is winding rated current.
"""
import numpy as np

S1, V2 = 50e3, 220.0
I_rated = S1 / V2
# Open delta: windings ab and bc present. Balanced line currents Ia, Ib, Ic of magnitude I.
# Ia flows only through winding ab, Ic only through winding bc -> winding current = line current.
a = np.exp(-2j * np.pi / 3)
Ia, Ib, Ic = 1.0, a, a**2
w_ab, w_bc = Ia, -Ic            # KCL at terminals a and c
assert abs(abs(w_ab) - 1) < 1e-12 and abs(abs(w_bc) - 1) < 1e-12
I_line_max = I_rated / max(abs(w_ab), abs(w_bc))
S_vv = np.sqrt(3) * V2 * I_line_max
assert abs(I_rated - 227.2727) < 1e-3
assert abs(S_vv / 1e3 - 86.60) / 86.60 < 0.005
assert abs(S_vv / (3 * S1) - 0.577) < 0.005 and abs(S_vv / (2 * S1) - 0.866) < 0.005
print("PASS EE-114-06-1")
