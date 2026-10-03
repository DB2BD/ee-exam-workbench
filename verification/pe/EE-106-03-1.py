"""EE-106-03-1 independent check (official crop): inverse of A = [[1,-1,0,0],[1,2,0,0],[0,0,1,2],[0,0,2,1]]."""
import numpy as np
import sympy as sp

A = sp.Matrix([[1, -1, 0, 0], [1, 2, 0, 0], [0, 0, 1, 2], [0, 0, 2, 1]])
third = sp.Rational(1, 3)
claimed = sp.Matrix([
    [2 * third, third, 0, 0],
    [-third, third, 0, 0],
    [0, 0, -third, 2 * third],
    [0, 0, 2 * third, -third],
])
assert A * claimed == sp.eye(4)
assert claimed * A == sp.eye(4)
assert A.inv() == claimed
assert A.det() == -9
assert np.allclose(np.linalg.inv(np.array(A.tolist(), dtype=float)), np.array(claimed.tolist(), dtype=float))
print("PASS EE-106-03-1")
