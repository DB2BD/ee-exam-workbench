"""EE-114-03-5 independent check: complete solution of Ax=b and N(A).

A = [[0,-1,0,1],[0,1,-1,0]], b = [0,1]^T (official crop).
"""
import sympy as sp

A = sp.Matrix([[0, -1, 0, 1], [0, 1, -1, 0]])
b = sp.Matrix([0, 1])
xp = sp.Matrix([0, 0, -1, 0])
v1 = sp.Matrix([1, 0, 0, 0])
v2 = sp.Matrix([0, 1, 1, 1])
assert A * xp == b and A * v1 == sp.zeros(2, 1) and A * v2 == sp.zeros(2, 1)

# Independent: sympy nullspace / rank-nullity, and gauss_jordan general solution.
ns = A.nullspace()
assert A.rank() == 2 and len(ns) == 2
assert sp.Matrix.hstack(*ns, v1, v2).rank() == 2       # same span
sol, params = A.gauss_jordan_solve(b)
for vals in ([0, 0], [1, 2], [-3, 5]):
    xs = sol.subs(dict(zip(params, vals)))
    assert A * xs == b
    assert sp.Matrix.hstack(v1, v2, xs - xp).rank() == 2   # x - xp lies in span{v1,v2}
print("PASS EE-114-03-5")
