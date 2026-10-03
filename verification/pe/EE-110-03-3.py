"""EE-110-03-3 independent check: Fourier series of x - x^2 on (-L, L), main case L = pi."""
import mpmath as mp
import sympy as sp

x, L = sp.symbols("x L", positive=True)
n = sp.symbols("n", integer=True, positive=True)
f = x - x**2
a0 = sp.integrate(f, (x, -L, L)) / L
an = sp.simplify(sp.integrate(f * sp.cos(n * sp.pi * x / L), (x, -L, L)) / L)
bn = sp.simplify(sp.integrate(f * sp.sin(n * sp.pi * x / L), (x, -L, L)) / L)
assert sp.simplify(a0 - (-2 * L**2 / 3)) == 0
assert sp.simplify(an - (-4 * L**2 * (-1) ** n / (n**2 * sp.pi**2))) == 0
assert sp.simplify(bn - (2 * L * (-1) ** (n + 1) / (n * sp.pi))) == 0
# L = pi
assert sp.simplify(an.subs(L, sp.pi) - (-4 * (-1) ** n / n**2)) == 0
assert sp.simplify(bn.subs(L, sp.pi) - 2 * (-1) ** (n + 1) / n) == 0
# Independent: numeric partial sum at x = 1 (interior point) with L = pi
N = 20000
S = -mp.pi**2 / 3 + mp.nsum(lambda k: -4 * (-1) ** k / k**2 * mp.cos(k), [1, mp.inf])
Sb = sum(2 * (-1) ** (k + 1) / k * mp.sin(k) for k in range(1, N))
assert abs(S + Sb - (1 - 1)) < 1e-3
# Endpoint x = pi converges to average of f(-pi), f(pi) = -pi^2
Se = -mp.pi**2 / 3 + mp.nsum(lambda k: -4 / k**2, [1, mp.inf])
assert abs(Se + mp.pi**2) < 1e-10
print("PASS EE-110-03-3")
