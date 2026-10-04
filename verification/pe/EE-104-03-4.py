"""EE-104-03-4 independent check (official crop): joint density moments."""
import sympy as sp

x, y = sp.symbols("x y")
f = x * (y + sp.Rational(3, 2))
I = lambda g: sp.integrate(g * f, (x, 0, 1), (y, 0, 1))
assert I(1) == 1
assert I(x) == sp.Rational(2, 3)
assert I(y) == sp.Rational(13, 24)
assert I(x**2) == sp.Rational(1, 2)
assert I(x * y) == sp.Rational(13, 36)
fx = sp.integrate(f, (y, 0, 1)); fy = sp.integrate(f, (x, 0, 1))
assert sp.simplify(fx * fy - f) == 0  # independent
print("PASS EE-104-03-4")
