"""EE-107-05-2: 161/23.9 kV, 60 MVA, X=15 %, source j8 ohm on primary.
Load 60 MVA pf 0.8 lag (constant power) with primary terminal 161 kV.
"""
import cmath
import math

import sympy as sp

V1b, V2b, Sb = 161e3, 23.9e3, 60e6
XT = 0.15
Zs = 8.0 / (V1b**2 / Sb)
P, Q = 0.8, 0.6
V1 = 1.0


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


# (1) constant-power load: |V1|^2 = (V2 + Q X/V2)^2 + (P X/V2)^2
v = sp.symbols("v", positive=True)
roots = sp.Poly(sp.expand(((v**2 + Q * XT) ** 2 + (P * XT) ** 2) - V1**2 * v**2), v).nroots()
real_pos = [float(r.as_real_imag()[0]) for r in roots if abs(sp.im(r)) < 1e-12 and sp.re(r) > 0]
v2 = max(real_pos)  # normal (high-voltage) root
close(v2, 0.88971, 1e-4)
close(v2 * V2b / 1e3, 21.264, 1e-4)
I = ((P + 1j * Q) / v2).conjugate()   # V2 reference
V1c = v2 + 1j * XT * I
close(abs(V1c), 1.0, 1e-9)
Es = V1c + 1j * Zs * I
close(abs(Es) * V1b / 1e3, 163.37, 1e-3)
# (2) secondary current and overload check
I2 = Sb / (math.sqrt(3) * v2 * V2b)
close(I2, 1629.10, 1e-4)
I2rated = Sb / (math.sqrt(3) * V2b)
close(I2rated, 1449.41, 1e-4)
assert I2 > I2rated
# (3) regulation with constant source: no-load secondary = Es (pu)
VR = (abs(Es) - v2) / v2 * 100
close(VR, 14.05, 1e-3)
# (4) secondary three-phase short circuit with the same Es
Isc = abs(Es) / (Zs + XT) * I2rated
close(Isc, 8727.6, 1e-4)
print("PASS EE-107-05-2")
