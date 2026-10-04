"""EE-111-01-2 independent check: coupled-coil circuit by nodal analysis.

Givens (official crop): vs = 36 cos(2t + 30 deg) V; 5 ohm in series to the top of
L1 = 3 H (dot top); L2 = 1.5 H (dot top) feeds 0.125 F then 4 ohm; both coil
bottoms meet at a node tied to ground through 2 ohm; M = 0.5 H.  I1, I2 are
clockwise mesh currents.  The check uses node voltages + coil currents (not
mesh equations).
"""
import cmath
import math

import sympy as sp

w = 2
Vs = 36 * sp.exp(sp.I * sp.pi / 6)
L1, L2, M = 3, sp.Rational(3, 2), sp.Rational(1, 2)
Cc = sp.Rational(1, 8)
# Unknowns: node x (5 ohm / L1 top), node m (coil bottoms), node y (L2 top),
# iA = current down through L1 (into dot), iB = current up through L2 (out of dot).
x, m, y, iA, iB = sp.symbols("x m y iA iB")
jw = sp.I * w
eqs = [
    sp.Eq((Vs - x) / 5, iA),                      # series 5 ohm carries iA
    sp.Eq(x - m, jw * L1 * iA - jw * M * iB),     # L1 (dot top), L2 current enters dot = -iB
    sp.Eq(y - m, jw * L2 * (-iB) + jw * M * iA),  # L2 dot-top voltage
    sp.Eq(m / 2, iA - iB),                        # KCL at bottom node
    sp.Eq(iB, y / (1 / (jw * Cc) + 4)),           # cap + 4 ohm back to ground
]
s = sp.solve(eqs, [x, m, y, iA, iB], dict=True)[0]
I1 = complex(sp.N(s[iA]))
I2 = complex(sp.N(s[iB]))
P4 = 0.5 * abs(I2) ** 2 * 4
print(f"I1 = {abs(I1):.5f} ang {math.degrees(cmath.phase(I1)):.4f}")
print(f"I2 = {abs(I2):.5f} ang {math.degrees(cmath.phase(I2)):.4f}")
print(f"P4 = {P4:.5f} W")
# boxed answers (peak phasors, cosine reference)
assert abs(abs(I1) - 4.25383) / 4.25383 < 1e-5 and abs(math.degrees(cmath.phase(I1)) + 8.517) < 1e-3
assert abs(abs(I2) - 1.56374) / 1.56374 < 1e-5 and abs(math.degrees(cmath.phase(I2)) - 27.510) < 1e-3
assert abs(P4 - 4.8906) / 4.8906 < 1e-4
print("PASS EE-111-01-2")
