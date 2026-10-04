"""EE-112-03-6 independent check.

A = [[1,3,0],[0,0,1],[1,3,1]], b = [2,4,6]^T, c = [1,6,7]^T (official crop).
(1) all solutions of [A b] x = c, x in R^4; (2) eigenvalues / unit eigenvectors of A.
"""
import numpy as np
import sympy as sp

A = sp.Matrix([[1, 3, 0], [0, 0, 1], [1, 3, 1]])
b = sp.Matrix([2, 4, 6])
c = sp.Matrix([1, 6, 7])
M = A.row_join(b)
t, s = sp.symbols("t s")
x = sp.Matrix([1 - 3 * t - 2 * s, t, 6 - 4 * s, s])
assert sp.simplify(M * x - c) == sp.zeros(3, 1)
assert M.rank() == 2 and M.row_join(c).rank() == 2   # consistent, 2 free parameters
sol, params = M.gauss_jordan_solve(c)
assert len(params) == 2

lam = sp.symbols("lam")
assert sp.expand((lam * sp.eye(3) - A).det() - lam * (lam**2 - 2 * lam - 2)) == 0
r3 = sp.sqrt(3)
pairs = [
    (0, sp.Matrix([-3, 1, 0]), 10),
    (1 - r3, sp.Matrix([(3 + r3) / 2, -(1 + r3) / 2, 1]), 5 + 2 * r3),
    (1 + r3, sp.Matrix([(3 - r3) / 2, (r3 - 1) / 2, 1]), 5 - 2 * r3),
]
for l, v, n2 in pairs:
    assert sp.simplify(A * v - l * v) == sp.zeros(3, 1)
    assert sp.simplify(v.dot(v) - n2) == 0

# Independent: numpy eigen-decomposition (unit vectors up to sign).
w, V = np.linalg.eig(np.array(A.tolist(), dtype=float))
for l, v, n2 in pairs:
    i = int(np.argmin(abs(w - float(l))))
    u = np.array([float(e) for e in v]) / float(sp.sqrt(n2))
    assert abs(abs(np.dot(u, V[:, i])) - 1) < 1e-9
assert abs(sum(w) - 2) < 1e-12 and abs(np.prod(w)) < 1e-12   # trace 2, det 0
print("PASS EE-112-03-6")
