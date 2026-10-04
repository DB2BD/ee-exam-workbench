"""EE-114-03-4 independent check: Fourier series of f = 0 on (-pi,0], x on (0,pi], period 2pi."""
import numpy as np

trap = getattr(np, "trapezoid", None) or np.trapz
import sympy as sp

x = sp.symbols("x", real=True)
n = sp.symbols("n", integer=True, positive=True)
a0 = sp.integrate(x, (x, 0, sp.pi)) / sp.pi
an = sp.integrate(x * sp.cos(n * x), (x, 0, sp.pi)) / sp.pi
bn = sp.integrate(x * sp.sin(n * x), (x, 0, sp.pi)) / sp.pi
assert sp.simplify(a0 - sp.pi / 2) == 0
assert sp.simplify(an - ((-1) ** n - 1) / (sp.pi * n**2)) == 0
assert sp.simplify(bn - (-1) ** (n + 1) / n) == 0

# Independent: numerical coefficients by FFT-style quadrature, then series values.
xs = np.linspace(-np.pi, np.pi, 400_001)
fx = np.where(xs > 0, xs, 0.0)
for k in range(1, 6):
    ak = trap(fx * np.cos(k * xs), xs) / np.pi
    bk = trap(fx * np.sin(k * xs), xs) / np.pi
    assert abs(ak - ((-1) ** k - 1) / (np.pi * k * k)) < 1e-6
    assert abs(bk - (-1) ** (k + 1) / k) < 1e-6

def S(xv, N=200_000):
    k = np.arange(1, N + 1)
    return np.pi / 4 + np.sum(((-1.0) ** k - 1) / (np.pi * k**2) * np.cos(k * xv)
                              + (-1.0) ** (k + 1) / k * np.sin(k * xv))

assert abs(S(np.pi) - np.pi / 2) < 1e-4          # jump: average of 0 and pi
assert abs(S(np.pi / 2) - np.pi / 2) < 1e-4      # continuity point
assert abs(S(0.0)) < 1e-4
print("PASS EE-114-03-4")
