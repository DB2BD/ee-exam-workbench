"""EE-107-02-3 independent check: buck-boost, f = 25 kHz, Vd = 15 V, L = 40 uH, Vo = 10 V, Po = 12 W.

Method: CCM candidate D and boundary inductance -> mode; DCM power balance P = Vd^2 D^2/(2 L f) (lossless).
Then rebuild the DCM cycle (peak current, fall time, charge balance) as a cross-check.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


Vd, L, f, Vo, Po = 15, sp.Rational(40, 10**6), 25_000, 10, 12
R = sp.Rational(Vo**2, Po)
Dc = sp.Rational(Vo, Vd + Vo)
LB = (1 - Dc) ** 2 * R / (2 * f)
assert close(R, 8.3333) and close(Dc, 0.4) and close(LB * 1e6, 60) and LB > L     # -> DCM
D = sp.symbols("D", positive=True)
Dsol = sp.solve(sp.Eq(Vd**2 * D**2 / (2 * L * f), Po), D)[0]
assert close(Dsol, 0.32660)
Ipk = Vd * Dsol / (L * f)
D2 = L * f * Ipk / Vo                       # fall time fraction: L Ipk = Vo D2 T
assert close(D2, 0.48990) and close(Dsol + D2, 0.81650) and Dsol + D2 < 1
Io = Ipk * D2 / 2                           # mean output current = triangle area over the period
assert close(Io * Vo, Po) and close(Io, 1.2)
assert close(Vo / Vd, float(Dsol / D2))     # volt-second balance Vd D = Vo D2
# using the CCM duty in the DCM law would deliver a wrong power
assert close(Vd**2 * 0.4**2 / (2 * L * f), 18)
print(f"R={float(R):.4f} Dccm={float(Dc)} LB={float(LB)*1e6:.1f} uH D={float(Dsol):.5f} D2={float(D2):.5f} Ipk={float(Ipk):.3f}")
print("PASS EE-107-02-3")
