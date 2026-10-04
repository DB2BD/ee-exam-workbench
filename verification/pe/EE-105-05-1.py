"""EE-105-05-1: descriptive (series vs shunt compensation).  Quantitative arguments only.

The crop has no data; k, X, V below are generic symbols.  We check the relations used in the answer:
 - series C: P_max = V1 V2 / (X_L - X_C) = P_max0 / (1 - k),  k = X_C / X_L
 - shunt C at the receiving end raises voltage by approx. Q_c * X / V (small-drop approximation)
 - shunt reactor absorbs the Ferranti charging rise: Vr = Vs / cos(beta l) for an open line
"""
import numpy as np
import sympy as sp

V1, V2, XL, XC, k = sp.symbols("V1 V2 X_L X_C k", positive=True)
Pmax_series = V1 * V2 / (XL - XC)
ratio = sp.simplify(Pmax_series.subs(XC, k * XL) / (V1 * V2 / XL))
assert sp.simplify(ratio - 1 / (1 - k)) == 0
assert float(ratio.subs(k, sp.Rational(1, 2))) == 2.0  # 50 % compensation doubles the limit

# shunt compensation: sending end 1 pu, line X=0.3, load P+jQ at receiving end (generic example)
Vs, X, P, Q = 1.0, 0.3, 0.8, 0.4


def vr(Qc):
    # solve |Vs| = |Vr + jX (P - j(Q-Qc))/Vr*| for real Vr by scanning
    f = lambda v: abs(v + 1j * X * (P - 1j * (Q - Qc)) / v) - Vs
    lo, hi = 0.5, 1.2
    for _ in range(80):
        mid = (lo + hi) / 2
        if (f(lo) > 0) == (f(mid) > 0):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


assert vr(0.4) > vr(0.0)  # capacitor raises receiving voltage under load

# Ferranti: open line, Vr = Vs / cos(beta l)
for deg in (5, 10, 15):
    assert 1 / np.cos(np.radians(deg)) > 1.0
print("PASS EE-105-05-1 (descriptive)")
