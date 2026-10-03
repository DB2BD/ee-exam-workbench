"""EE-108-06-5: shunt capacitor on an 11.4 kV feeder (800 kVA, pf 0.8 lag, 120 kvar, Z=0.26+j0.72 ohm).

Balanced three-phase, 11.4 kV line voltage held, Z per phase.  Capacity gained is read as the
kVA released at the same 640 kW (see the note's conditions).
"""
import math
import numpy as np

V = 11.4e3
R, X = 0.26, 0.72
S1, pf1, Qc = 800e3, 0.8, 120e3
P = S1 * pf1
Q1 = S1 * math.sqrt(1 - pf1**2)
Q2 = Q1 - Qc
S2 = math.hypot(P, Q2)

I1 = S1 / (math.sqrt(3) * V)
I2 = S2 / (math.sqrt(3) * V)
dI = I1 - I2
assert abs(dI - 3.327) / 3.327 < 5e-4                       # boxed (一)

# voltage drop along the line: (P R + Q X)/V_LL  (independent of the I(R cos + X sin) route)
dv = lambda p, q: (p * R + q * X) / V
d_dv = dv(P, Q1) - dv(P, Q2)
assert abs(d_dv - 7.579) / 7.579 < 5e-4                     # boxed (二)
dv_alt = lambda i, c, sn: math.sqrt(3) * i * (R * c + X * sn)
assert abs(dv_alt(I1, 0.8, 0.6) - dv(P, Q1)) < 1e-9
assert abs(dv_alt(I2, P / S2, Q2 / S2) - dv(P, Q2)) < 1e-9

loss = lambda s: s**2 * R / V**2                            # 3 I^2 R = S^2 R / V^2
d_loss = loss(S1) - loss(S2)
assert abs(d_loss - 201.662) / 201.662 < 5e-4               # boxed (三)
assert abs(3 * I1**2 * R - loss(S1)) < 1e-6

d_s = (S1 - S2) / 1e3
assert abs(d_s - 65.698) / 65.698 < 5e-4                    # boxed (四)
print("PASS EE-108-06-5")
