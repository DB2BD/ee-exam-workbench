"""EE-111-03-6 independent check: triangular pdf on [0,2]."""
import mpmath as mp
import sympy as sp

x = sp.symbols("x")
p = sp.Piecewise((x, (x >= 0) & (x <= 1)), (2 - x, (x > 1) & (x <= 2)), (0, True))
mom = lambda k: sp.integrate(x**k * p, (x, 0, 2))
assert mom(0) == 1
EX = mom(1); var = mom(2) - EX**2; EX3 = mom(3)
assert EX == 1 and var == sp.Rational(1, 6) and EX3 == sp.Rational(3, 2)
# Independent: X = U1 + U2 (sum of two U(0,1)) has this pdf; Monte Carlo-free check via mpmath
pn = lambda xx: xx if xx <= 1 else 2 - xx
assert abs(mp.quad(lambda xx: (xx - 1) ** 2 * pn(xx), [0, 1, 2]) - mp.mpf(1) / 6) < 1e-12
# E[(U1+U2)^3] = sum binomial moments, E[U^k]=1/(k+1)
EU = lambda k: sp.Rational(1, k + 1)
e3 = sum(sp.binomial(3, k) * EU(k) * EU(3 - k) for k in range(4))
assert e3 == sp.Rational(3, 2)
print("PASS EE-111-03-6")
