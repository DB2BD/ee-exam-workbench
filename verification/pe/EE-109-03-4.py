"""EE-109-03-4 independent check: Fourier series of x/pi on (-pi, pi), period 2pi."""
import mpmath as mp
import sympy as sp

x = sp.symbols("x")
n = sp.symbols("n", integer=True, positive=True)
f = x / sp.pi
a0 = sp.integrate(f, (x, -sp.pi, sp.pi)) / sp.pi
an = sp.integrate(f * sp.cos(n * x), (x, -sp.pi, sp.pi)) / sp.pi
bn = sp.simplify(sp.integrate(f * sp.sin(n * x), (x, -sp.pi, sp.pi)) / sp.pi)
assert a0 == 0 and sp.simplify(an) == 0
assert sp.simplify(bn - 2 * (-1) ** (n + 1) / (sp.pi * n)) == 0
# Independent: at x = pi/2 only odd n = 2m+1 survive, b_n sin(n pi/2) = (2/pi)(-1)^m/(2m+1)
# (Leibniz series): sum = (2/pi)(pi/4) = 1/2 = f(pi/2)
S = mp.nsum(lambda m: 2 * (-1) ** m / (mp.pi * (2 * m + 1)), [0, mp.inf])
assert sp.simplify((bn * sp.sin(n * sp.pi / 2)).subs(n, 5) - 2 / (5 * sp.pi)) == 0
assert abs(S - 0.5) < 1e-10
print("PASS EE-109-03-4")
