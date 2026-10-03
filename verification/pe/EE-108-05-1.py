"""EE-108-05-1: cylindrical-rotor generator on infinite bus; Xd=1.7241 pu, V=1<0,
I=0.8 pu at pf 0.9 lagging.  (1) Ei magnitude/angle, P, Q.  (2) P fixed, field +20%:
delta and Q.
"""
import cmath
import math

import sympy as sp

Xd, V, Ia, pf = 1.7241, 1.0, 0.8, 0.9


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


# (1) phasor: Ei = V + jXd*I, I lags V by acos(0.9)
I = Ia * cmath.exp(-1j * math.acos(pf))
Ei = V + 1j * Xd * I
S = V * I.conjugate()
close(abs(Ei), 2.0260)
close(math.degrees(cmath.phase(Ei)), 37.785)
close(S.real, 0.72)
close(S.imag, 0.3487)

# (1) cross-check with power-angle equations at the solved delta
d1 = cmath.phase(Ei)
close(abs(Ei) * V / Xd * math.sin(d1), S.real)
close((abs(Ei) * V * math.cos(d1) - V**2) / Xd, S.imag)

# (2) excitation +20 % (linear magnetisation => Ei scales), P unchanged
E2 = 1.2 * abs(Ei)
close(E2, 2.4312)
d2 = math.asin(S.real * Xd / E2)
Q2 = (E2 * math.cos(d2) - V) / Xd * V
close(math.degrees(d2), 30.70)
close(Q2, 0.6325)

# independent symbolic solve of (2)
dd = sp.symbols("dd", positive=True)
sol = sp.nsolve(E2 * sp.sin(dd) / Xd - S.real, dd, 0.5)
close(float(sol), d2, 1e-9)
# phasor rebuild: I2 = (E2<d2 - 1)/(jXd) must give same P and Q
I2 = (E2 * cmath.exp(1j * d2) - V) / (1j * Xd)
S2 = V * I2.conjugate()
close(S2.real, 0.72)
close(S2.imag, Q2)
print("PASS EE-108-05-1")
