"""EE-110-03-7 independent check: p(x) = a(x+1), 0<=x<=2."""
import mpmath as mp
import sympy as sp

x, a = sp.symbols("x a", positive=True)
aval = sp.solve(sp.integrate(a * (x + 1), (x, 0, 2)) - 1, a)[0]
assert aval == sp.Rational(1, 4)
p = aval * (x + 1)
EX = sp.integrate(x * p, (x, 0, 2))
var = sp.integrate((x - EX) ** 2 * p, (x, 0, 2))
assert EX == sp.Rational(7, 6) and var == sp.Rational(11, 36)
# Independent: numeric quadrature via CDF tail formula E[X] = int_0^2 (1-F)
Fc = lambda u: (u**2 / 2 + u) / 4
ex = mp.quad(lambda u: 1 - Fc(u), [0, 2])
ex2 = mp.quad(lambda u: 2 * u * (1 - Fc(u)), [0, 2])
assert abs(ex - mp.mpf(7) / 6) < 1e-12 and abs(ex2 - ex**2 - mp.mpf(11) / 36) < 1e-12
print("PASS EE-110-03-7")
