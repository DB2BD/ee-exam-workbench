"""EE-106-03-2 independent check (official crop): least squares of Ax=b."""
import numpy as np
import sympy as sp

A = sp.Matrix([[2, 1], [1, 2], [1, 1], [0, 1]])
b = sp.Matrix([1, 0, 2, -1])
ata = A.T * A
atb = A.T * b
assert ata == sp.Matrix([[6, 5], [5, 7]]) and atb == sp.Matrix([4, 2])
x = ata.LUsolve(atb)
assert x == sp.Matrix([sp.Rational(18, 17), -sp.Rational(8, 17)])
# Independent: numpy lstsq, normal equations residual orthogonality
xn, *_ = np.linalg.lstsq(np.array(A.tolist(), float), np.array(b.tolist(), float).ravel(), rcond=None)
assert np.allclose(xn, [18 / 17, -8 / 17])
r = b - A * x
assert A.T * r == sp.zeros(2, 1)
# Pythagoras for the projection: |b|^2 = |Ax|^2 + |r|^2
assert (b.T * b)[0] == ((A * x).T * (A * x))[0] + (r.T * r)[0]
print("PASS EE-106-03-2")
