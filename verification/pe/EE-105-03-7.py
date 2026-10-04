"""EE-105-03-7 independent check (official crop): linear map from basis images."""
import sympy as sp

M = sp.Matrix([[2, -1], [-3, 3]])  # columns = T(e1), T(e2)
assert M * sp.Matrix([7, 6]) == sp.Matrix([8, -3])
assert 7 * sp.Matrix([2, -3]) + 6 * sp.Matrix([-1, 3]) == sp.Matrix([8, -3])
print("PASS EE-105-03-7")
