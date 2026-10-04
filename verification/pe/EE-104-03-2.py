"""EE-104-03-2 independent check (official crop): eigen-decomposition."""
import sympy as sp

A = sp.Matrix([[1, 0, 0], [0, 1, 1], [0, 1, 1]])
assert A.eigenvals() == {0: 1, 1: 1, 2: 1}
v0, v1, v2 = sp.Matrix([0, 1, -1]), sp.Matrix([1, 0, 0]), sp.Matrix([0, 1, 1])
assert A * v0 == 0 * v0 and A * v1 == v1 and A * v2 == 2 * v2
P = sp.Matrix.hstack(v0, v1, v2)
L = sp.diag(0, 1, 2)
assert P.det() == -2  # nonzero: eigenvectors independent
assert P * L * P.inv() == A
print("PASS EE-104-03-2")
