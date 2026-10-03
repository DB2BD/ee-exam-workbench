"""EE-107-03-4 independent check (official crop): Fourier series of f = 0 on (-pi,0), sin x on [0,pi)."""
import numpy as np
import sympy as sp

x = sp.symbols("x", real=True)
n = sp.symbols("n", integer=True, positive=True)
a0 = sp.integrate(sp.sin(x), (x, 0, sp.pi)) / sp.pi
assert a0 == 2 / sp.pi
an_gen = sp.simplify(sp.integrate(sp.sin(x) * sp.cos(n * x), (x, 0, sp.pi)) / sp.pi)
for k in range(2, 9):
    ak = sp.integrate(sp.sin(x) * sp.cos(k * x), (x, 0, sp.pi)) / sp.pi
    expected = 0 if k % 2 else 2 / (sp.pi * (1 - k**2))
    assert sp.simplify(ak - expected) == 0, k
assert sp.integrate(sp.sin(x) * sp.cos(x), (x, 0, sp.pi)) == 0
assert sp.integrate(sp.sin(x) ** 2, (x, 0, sp.pi)) / sp.pi == sp.Rational(1, 2)  # b1
for k in range(2, 8):
    assert sp.integrate(sp.sin(x) * sp.sin(k * x), (x, 0, sp.pi)) == 0


def partial(xv, N=4000):
    s = 1 / np.pi + 0.5 * np.sin(xv)
    for m in range(1, N + 1):
        s += (2 / np.pi) * np.cos(2 * m * xv) / (1 - 4 * m * m)
    return s


for xv, fv in ((-2.0, 0.0), (1.0, np.sin(1.0)), (2.5, np.sin(2.5)), (np.pi / 2, 1.0)):
    assert abs(partial(xv) - fv) <= 5e-4 + 0.005 * abs(fv), (xv, partial(xv), fv)
# Jump point x=0: midpoint of 0 and 0 -> 0; endpoint x=pi: (0 + sin(pi))/2 = 0
assert abs(partial(0.0)) < 1e-3 and abs(partial(np.pi)) < 1e-3
# Parseval: (1/pi) int f^2 = 1/2 = a0^2/2 + b1^2 + sum a_{2k}^2
import mpmath as mp
par = 2 / mp.pi**2 + mp.mpf(1) / 4 + mp.nsum(lambda k: (2 / (mp.pi * (4 * k * k - 1))) ** 2, [1, mp.inf])
assert abs(par - 0.5) / 0.5 <= 0.005
print("PASS EE-107-03-4")
