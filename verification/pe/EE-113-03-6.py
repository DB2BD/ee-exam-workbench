"""EE-113-03-6 independent check: p(x,y) = k e^{-x-y/2} on x,y >= 0."""
import mpmath as mp
import sympy as sp

x, y, k = sp.symbols("x y k", positive=True)
p = k * sp.exp(-x - y / 2)
kval = sp.solve(sp.integrate(p, (x, 0, sp.oo), (y, 0, sp.oo)) - 1, k)[0]
assert kval == sp.Rational(1, 2)
p = p.subs(k, kval)
EY = sp.integrate(y * p, (x, 0, sp.oo), (y, 0, sp.oo))
assert EY == 2
E = sp.integrate(x**3 * y**2 * p, (x, 0, sp.oo), (y, 0, sp.oo))
assert E == 48

# Independent: numerical double integrals (mpmath).
f = lambda xx, yy: 0.5 * mp.exp(-xx - yy / 2)
tot = float(mp.quad(f, [0, mp.inf], [0, mp.inf]))
ey = float(mp.quad(lambda xx, yy: yy * f(xx, yy), [0, mp.inf], [0, mp.inf]))
e32 = float(mp.quad(lambda xx, yy: xx**3 * yy**2 * f(xx, yy), [0, mp.inf], [0, mp.inf]))
assert abs(tot - 1) < 1e-6 and abs(ey - 2) < 1e-5 and abs(e32 - 48) / 48 < 1e-5
print("PASS EE-113-03-6")
