"""EE-107-03-2 independent check (official crop): A = [[0,9,4],[-1,-2,2],[-2,0,2]]."""
import numpy as np
import sympy as sp

A = sp.Matrix([[0, 9, 4], [-1, -2, 2], [-2, 0, 2]])
lam = sp.symbols("lambda")
cp = sp.expand((lam * sp.eye(3) - A).det())
assert sp.expand(cp - (lam + 2) * (lam**2 - 2 * lam + 17)) == 0
assert set(sp.solve(cp, lam)) == {-2, 1 + 4 * sp.I, 1 - 4 * sp.I}
pairs = [
    (-2, sp.Matrix([18, -8, 9])),
    (1 + 4 * sp.I, sp.Matrix([1 - 4 * sp.I, 1, 2])),
    (1 - 4 * sp.I, sp.Matrix([1 + 4 * sp.I, 1, 2])),
]
for val, vec in pairs:
    assert sp.simplify(A * vec - val * vec) == sp.zeros(3, 1)
P = sp.Matrix.hstack(*[v for _, v in pairs])
D = sp.diag(*[l for l, _ in pairs])
assert sp.simplify(P.inv() * A * P - D) == sp.zeros(3, 3)
assert sp.simplify(P * D * P.inv() - A) == sp.zeros(3, 3)
# Independent: numeric eigenvalues, trace, det
ev = np.linalg.eigvals(np.array(A.tolist(), dtype=float))
assert np.allclose(sorted(ev, key=lambda c: (c.real, c.imag)), sorted([-2, 1 - 4j, 1 + 4j], key=lambda c: (c.real, c.imag)))
assert A.trace() == 0 and A.det() == -34
print("PASS EE-107-03-2")
