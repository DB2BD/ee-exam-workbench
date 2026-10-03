"""EE-109-05-3: two-bus Newton-Raphson, two iterations.

Givens (official crop): V1 = 1/0 slack, y12 = -j10, bus-2 load 200 MW + 50 Mvar,
base 100 MVA, start V2 = 1.0, delta2 = 0.
"""
import numpy as np
import sympy as sp

d, v = sp.symbols("delta V", real=True)
Y = sp.Matrix([[-10 * sp.I, 10 * sp.I], [10 * sp.I, -10 * sp.I]])
P2 = 10 * v * sp.sin(d)           # |V2||V1||Y21| cos(90deg - delta2)
Q2 = -10 * v * sp.cos(d) + 10 * v**2
# symbolic check against S2 = V2 (Y21 V1 + Y22 V2)*
V2c = v * sp.exp(sp.I * d)
S2 = sp.expand_complex(V2c * sp.conjugate(Y[1, 0] * 1 + Y[1, 1] * V2c))
assert sp.simplify(sp.re(S2) - P2) == 0 and sp.simplify(sp.im(S2) - Q2) == 0

J = sp.Matrix([P2, Q2]).jacobian([d, v])
x = np.array([0.0, 1.0])
hist = []
for _ in range(2):
    sub = {d: x[0], v: x[1]}
    mis = np.array([-2.0 - float(P2.subs(sub)), -0.5 - float(Q2.subs(sub))])
    Jn = np.array(J.subs(sub), dtype=float)
    x = x + np.linalg.solve(Jn, mis)
    hist.append(x.copy())
assert abs(hist[0][0] - (-0.2)) < 1e-12 and abs(hist[0][1] - 0.95) < 1e-12
assert abs(np.degrees(hist[1][0]) - (-12.482)) < 0.001
assert abs(hist[1][1] - 0.92303) < 1e-5

# Method 2: exact solution of the two-bus equations (closed form) is close by.
# 10 V sin d = -2,  10V^2 - 10 V cos d = -0.5  ->  quadratic in V^2
u = sp.symbols("u", positive=True)  # u = V^2
roots = sp.solve(sp.Eq((10 * u + 0.5) ** 2 + 4, 100 * u), u)
Vex = max(float(sp.sqrt(r)) for r in roots)
dex = np.degrees(np.arcsin(-0.2 / Vex))
assert abs(Vex - 0.92195) < 1e-5 and abs(dex - (-12.529)) < 0.001
assert abs(hist[1][1] - Vex) < 0.002 and abs(np.degrees(hist[1][0]) - dex) < 0.06
print("PASS EE-109-05-3")
