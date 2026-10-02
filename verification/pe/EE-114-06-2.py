"""EE-114-06-2 (conditional): arc-furnace bus voltage drop, 25 MVA base.

Model stated in note: electrode short keeps the whole Z_F = j0.4 in the path;
arc broken = open circuit. Branch X_F,sc = 0 also checked.
"""
import numpy as np

Xs = 25 / 2000
Zu = 1j * (Xs + 0.01 + 0.06)
for XFsc, expect in ((0.4, 15.49), (0.0, 62.26)):
    Zd = 1j * (0.05 + XFsc)
    I = 1 / (Zu + Zd)                  # mesh current, E = 1 pu
    Vbus = 1 - I * Zu
    # independent: voltage divider seen from the load side
    Vdiv = Zd / (Zu + Zd)
    assert abs(Vbus - Vdiv) < 1e-12
    drop = (1 - abs(Vbus)) * 100
    assert abs(drop - expect) / expect < 0.005, drop
open_drop = 0.0                        # I = 0 when arc is broken
assert open_drop == 0.0
print("PASS EE-114-06-2")
