"""EE-105-03-3 independent check (official crop): int Im(z) dz along z=t^3+it."""
import sympy as sp

t = sp.symbols("t", real=True)
z = t**3 + sp.I * t
val = sp.integrate(sp.im(z) * sp.diff(z, t), (t, 0, 1))
assert sp.simplify(val - (sp.Rational(3, 4) + sp.I / 2)) == 0
# check: Re part = int t*3t^2 = 3/4, Im part = int t = 1/2
assert sp.integrate(3 * t**3, (t, 0, 1)) == sp.Rational(3, 4) and sp.integrate(t, (t, 0, 1)) == sp.Rational(1, 2)
print("PASS EE-105-03-3")
