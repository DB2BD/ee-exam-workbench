"""EE-104-03-5 independent check (official crop): line integral along straight segment."""
import sympy as sp

u = sp.symbols("u")
P0, P1 = sp.Matrix([1, 1, 1]), sp.Matrix([-2, 1, 3])
r = P0 + u * (P1 - P0)
X, Y, Z = r
dX, dY, dZ = [sp.diff(c, u) for c in r]
integrand = X * Y * Z * dX - sp.cos(Y * Z) * dY + X * Z * dZ
val = sp.integrate(sp.simplify(integrand), (u, 0, 1))
assert val == sp.Rational(3, 2)
print("PASS EE-104-03-5")
