"""EE-110-05-1: (1) cylindrical rotor power angle; (2) salient pole Xd, Xq.

Givens (official crop): (1) Xs=0.7, two parallel lines 0.6 each, V=1, E=1.5,
P=0.75.  (2) unity pf load P=1.0, V=1.05, E=1.4, delta=25 deg.
"""
import numpy as np
import sympy as sp

X = 0.7 + 0.6 * 0.6 / 1.2
delta1 = np.degrees(np.arcsin(0.75 * X / (1.5 * 1.0)))
assert abs(X - 1.0) < 1e-12 and abs(delta1 - 30.0) < 1e-9

V, E, P, d = 1.05, 1.4, 1.0, np.radians(25)
I = P / V  # unity pf, I in phase with V
Iq, Id = I * np.cos(d), I * np.sin(d)
Xq = V * np.sin(d) / Iq
Xd = (E - V * np.cos(d)) / Id
assert abs(Xq - 0.5141) / 0.5141 < 0.005
assert abs(Xd - 1.1140) / 1.1140 < 0.005

# Method 2: salient-pole power-angle equation and Q=0 must both hold.
xd, xq = sp.symbols("xd xq", positive=True)
Pexpr = E * V / xd * sp.sin(d) + V**2 / 2 * (1 / xq - 1 / xd) * sp.sin(2 * d)
Qexpr = E * V / xd * sp.cos(d) - V**2 * (sp.cos(d) ** 2 / xd + sp.sin(d) ** 2 / xq)
sol = sp.nsolve([Pexpr - P, Qexpr], [xd, xq], [1.0, 0.5])
assert abs(float(sol[0]) - Xd) < 1e-6 and abs(float(sol[1]) - Xq) < 1e-6
# phasor rebuild: E' = V + jXq I lies on the q axis at 25 deg
Eq_axis = V + 1j * Xq * I
assert abs(np.degrees(np.angle(Eq_axis)) - 25) < 1e-9
print("PASS EE-110-05-1")
