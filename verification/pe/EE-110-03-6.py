"""EE-110-03-6 independent check: det, eigenpairs and diagonalization of A."""
import numpy as np
import sympy as sp

A = sp.Matrix([[3, 0, -2], [0, 2, 0], [-2, 0, 0]])
assert A.det() == -8
P = sp.Matrix([[-2, 0, 1], [0, 1, 0], [1, 0, 2]])  # columns: lambda = 4, 2, -1
D = sp.diag(4, 2, -1)
assert P.inv() * A * P == D
# Independent: numpy eigenvalues and product / trace
w = np.linalg.eigvalsh(np.array(A.tolist(), dtype=float))
assert np.allclose(sorted(w), [-1, 2, 4])
assert abs(np.prod(w) + 8) < 1e-9 and abs(w.sum() - 5) < 1e-9
print("PASS EE-110-03-6")
