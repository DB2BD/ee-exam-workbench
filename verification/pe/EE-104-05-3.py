"""EE-104-05-3: two identical 550 MVA, 20 kV gens (X''d=25 %) each via a 550 MVA 20/345 kV step-up (X=15 %).

Bus 345 kV = 1 pu before the fault; assumed P = 440 MW delivered to the bus by EACH unit (crop: "均為 440 MW");
fault contributions 2.5 kA and 3.0 kA.  Pre-fault E'' recovered from the fault currents.
The system-side impedance is not given, so the requested fault current is the sum of the two generating units' phasors.
"""
import math

import numpy as np


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


Sb, Vh = 550.0, 345.0
Ib = Sb / (math.sqrt(3) * Vh)          # kA
Xs = 0.25 + 0.15
P = 440.0 / Sb
close(P, 0.8, 1e-9)

res = []
for If_kA in (2.5, 3.0):
    E = Xs * If_kA / Ib                 # |E''|
    # solve |1 + jXs (P - jq)|... : E'' = (1 + Xs q) + j Xs P
    q = (math.sqrt(E**2 - (Xs * P) ** 2) - 1) / Xs
    I = P - 1j * q
    Ev = 1 + 1j * Xs * I
    close(abs(Ev), E, 1e-12)
    Vt = 1 + 0.15j * I
    res.append((E, q, I, Ev, Vt))
(E1, q1, I1, Ev1, Vt1), (E2, q2, I2, Ev2, Vt2) = res
close(E1, 1.086468, 1e-5); close(E2, 1.303762, 1e-5)
close(math.degrees(np.angle(Ev1)), 17.1295, 1e-4); close(math.degrees(np.angle(Ev2)), 14.2081, 1e-4)
close(abs(Vt1) * 20, 20.4285, 1e-4); close(abs(Vt2) * 20, 22.1098, 1e-4)
close(q1 * Sb, 52.627, 1e-4); close(q2 * Sb, 362.836, 1e-4)

# fault current back-check and phasor sum
If1, If2 = Ev1 / (1j * Xs), Ev2 / (1j * Xs)
close(abs(If1) * Ib, 2.5, 1e-9); close(abs(If2) * Ib, 3.0, 1e-9)
tot = abs(If1 + If2) * Ib
close(tot, 5.4982, 1e-4)

# power balance at the bus: S = V I*
close((1 * np.conj(I1)).imag * Sb, q1 * Sb, 1e-9)
# the alternative root cos(delta)<0 (delta>90 deg) needs a huge leading Q and dP/d(delta)<0 -> rejected
for E in (E1, E2):
    q_hi = (-math.sqrt(E**2 - (Xs * P) ** 2) - 1) / Xs
    assert q_hi * Sb < -2000          # > 2000 Mvar absorbed: not a normal operating point
print("tot", tot, "PASS EE-104-05-3")
