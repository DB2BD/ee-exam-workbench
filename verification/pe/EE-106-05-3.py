"""EE-106-05-3 (needs_manual_review): 3-bus load flow, Bus1 slack V1=1<0, Bus2 PV
(P2=1, |V2|=1), Bus3 PQ load 1+j0.9; lines j0.8 (1-2), j0.4 (1-3), j0.4 (2-3).

Checks the quantities independent of the operating-branch choice (Ybus, P1 = 0,
Q direction 2->3) and reproduces both positive-voltage roots with Jacobian diagnostics.
"""
import itertools

import numpy as np


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


x12, x13, x23 = 0.8, 0.4, 0.4
y12, y13, y23 = (1 / (1j * x) for x in (x12, x13, x23))
Y = np.array([[y12 + y13, -y12, -y13],
              [-y12, y12 + y23, -y23],
              [-y13, -y23, y13 + y23]])
assert np.allclose(Y, [[-3.75j, 1.25j, 2.5j], [1.25j, -3.75j, 2.5j], [2.5j, 2.5j, -5j]])


def injections(x):
    d2, d3, v3 = x
    V = np.array([1.0, np.exp(1j * d2), v3 * np.exp(1j * d3)])
    S = V * np.conj(Y @ V)
    return V, S


def F(x):
    _, S = injections(x)
    return np.array([S[1].real - 1.0, S[2].real + 1.0, S[2].imag + 0.9])


def jac(x, h=1e-7):
    f0 = F(x)
    J = np.zeros((3, 3))
    for k in range(3):
        xp = np.array(x, float); xp[k] += h
        xm = np.array(x, float); xm[k] -= h
        J[:, k] = (F(xp) - F(xm)) / (2 * h)
    return J


roots = []
for d2, d3, v3 in itertools.product([0.0, 0.3, -0.3], [0.0, -0.3, 0.3], [1.0, 0.7, 0.4, 0.2]):
    x = np.array([d2, d3, v3], float)
    try:
        for _ in range(60):
            x = x - np.linalg.solve(jac(x), F(x))
    except np.linalg.LinAlgError:
        continue
    if x[2] > 0 and np.max(np.abs(F(x))) < 1e-10:
        if not any(np.allclose(x, r, atol=1e-6) for r in roots):
            roots.append(x)
roots.sort(key=lambda r: -r[2])
assert len(roots) == 2, roots
hi, lo = roots
close(hi[2], 0.686921, 1e-5); close(np.degrees(hi[0]), 13.9298, 1e-4); close(np.degrees(hi[1]), -10.0918, 1e-4)
close(lo[2], 0.396731, 1e-5); close(np.degrees(lo[0]), 17.2987, 1e-4); close(np.degrees(lo[1]), -22.0091, 1e-4)

for r in roots:
    V, S = injections(r)
    assert abs(S[0].real) < 1e-9           # P1 = 0 on both branches
    S23 = V[1] * np.conj((V[1] - V[2]) / (1j * x23))
    assert S23.imag > 0                     # Q flows from bus 2 to bus 3 on both branches
# lossless: P1 = -(P2 + P3) = 0 without solving
assert abs(-(1.0 + (-1.0))) < 1e-15

# Jacobian diagnostics
Jh, Jl = jac(hi), jac(lo)
close(np.linalg.det(Jh), 10.8587, 1e-4)
close(np.linalg.det(Jl), -4.96510, 1e-4)
assert np.linalg.det(Jh) > 0 > np.linalg.det(Jl)       # determinant changes sign between roots
close(np.linalg.svd(Jh, compute_uv=False)[-1], 1.30072, 1e-4)
close(np.linalg.svd(Jl, compute_uv=False)[-1], 0.99092, 1e-4)
Vh, Sh = injections(hi)
close((Vh[1] * np.conj((Vh[1] - Vh[2]) / (1j * x23))).imag, 0.93143, 1e-4)
Vl, Sl = injections(lo)
close((Vl[1] * np.conj((Vl[1] - Vl[2]) / (1j * x23))).imag, 1.73257, 1e-4)
print("PASS EE-106-05-3")
