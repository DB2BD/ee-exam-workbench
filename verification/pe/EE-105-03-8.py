"""EE-105-03-8 independent check (official crop): orthogonal Y with Y^T A Y diagonal."""
import numpy as np
import sympy as sp

A = sp.Matrix([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
assert A.eigenvals() == {2: 1, -1: 2}
q1 = sp.Matrix([1, 1, 1]) / sp.sqrt(3)
q2 = sp.Matrix([1, -1, 0]) / sp.sqrt(2)
q3 = sp.Matrix([1, 1, -2]) / sp.sqrt(6)
Y = sp.Matrix.hstack(q1, q2, q3)
assert sp.simplify(Y.T * Y) == sp.eye(3)
assert sp.simplify(Y.T * A * Y) == sp.diag(2, -1, -1)
# numpy cross-check
w, V = np.linalg.eigh(np.array(A.tolist(), float))
D = V.T @ np.array(A.tolist(), float) @ V
assert np.allclose(np.sort(np.diag(D)), [-1, -1, 2]) and np.allclose(D, np.diag(np.diag(D)))
print("PASS EE-105-03-8")
