"""EE-108-03-3 independent check (official crop): T = xy+yz+zx at (1,1,1), direction 3i - 4k."""
import sympy as sp

x, y, z = sp.symbols("x y z")
T = x * y + y * z + z * x
grad = sp.Matrix([T.diff(v) for v in (x, y, z)]).subs({x: 1, y: 1, z: 1})
assert grad == sp.Matrix([2, 2, 2])
d = sp.Matrix([3, 0, -4])
dd = grad.dot(d / d.norm())
assert dd == sp.Rational(-2, 5)
# Independent: finite-difference quotient along the unit direction
t = sp.symbols("t")
u = d / d.norm()
g = T.subs({x: 1 + t * u[0], y: 1 + t * u[1], z: 1 + t * u[2]})
assert sp.limit((g - g.subs(t, 0)) / t, t, 0) == sp.Rational(-2, 5)
print("PASS EE-108-03-3")
