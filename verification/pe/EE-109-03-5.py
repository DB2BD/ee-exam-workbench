"""EE-109-03-5 independent check: inverse of the crop's 3x3 matrix."""
import numpy as np
import sympy as sp

A = sp.Matrix([[-7, 2, 3], [-13, -2, 7], [8, 2, -2]])
claimed = sp.Matrix([[-1, 1, 2], [3, -1, 1], [-1, 3, 4]]) / 10
assert A.det() == 100
assert A * claimed == sp.eye(3) and claimed * A == sp.eye(3)
# Independent: Gauss-Jordan on [A | I] via rref
R = A.row_join(sp.eye(3)).rref()[0]
assert R[:, 3:] == claimed
assert np.allclose(np.linalg.inv(np.array(A.tolist(), dtype=float)), np.array(claimed.tolist(), dtype=float))
print("PASS EE-109-03-5")
