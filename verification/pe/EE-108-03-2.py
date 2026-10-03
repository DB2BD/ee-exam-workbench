"""EE-108-03-2 independent check (official crop): eigen-pairs of A = [[2,0,0],[1,0,2],[0,0,3]]."""
import sympy as sp

A = sp.Matrix([[2, 0, 0], [1, 0, 2], [0, 0, 3]])
lam = sp.symbols("lambda")
assert sp.factor((A - lam * sp.eye(3)).det()) == -lam * (lam - 2) * (lam - 3)
pairs = {0: sp.Matrix([0, 1, 0]), 2: sp.Matrix([2, 1, 0]), 3: sp.Matrix([0, 2, 3])}
for val, vec in pairs.items():
    assert A * vec == val * vec
    assert (A - val * sp.eye(3)).nullspace()[0].cross(vec).norm() == 0  # same line
P = sp.Matrix.hstack(*pairs.values())
D = sp.diag(*pairs.keys())
assert P.det() != 0
assert P.inv() * A * P == D
# Independent: trace and determinant
assert A.trace() == 5 and A.det() == 0
print("PASS EE-108-03-2")
