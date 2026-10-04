"""EE-112-03-2 independent check: Fourier coefficients, period 4.

The official crop defines f = -2x on [-2,0) and 2x on [0,4) with f(x+4)=f(x);
the two pieces span 6 units, which conflicts with period 4.
Branch A (main answer): fundamental interval [-2,2), i.e. f = 2|x| (triangle wave).
Branch B (alternative): take the full-period piece f = 2x on [0,4) (sawtooth).
"""
import numpy as np
import sympy as sp

x = sp.symbols("x", real=True)
n = sp.symbols("n", integer=True, positive=True)
L = 2
trap = getattr(np, "trapezoid", None) or np.trapz

# Branch A: f = 2|x| on [-2, 2)
a0 = sp.integrate(2 * sp.Abs(x), (x, -2, 2)) / (2 * L)  # constant term (mean value)
an = 2 / sp.Integer(L) * sp.integrate(2 * x * sp.cos(n * sp.pi * x / L), (x, 0, 2))
bn = sp.integrate(-2 * x * sp.sin(n * sp.pi * x / L), (x, -2, 0)) / L + sp.integrate(2 * x * sp.sin(n * sp.pi * x / L), (x, 0, 2)) / L
assert a0 == 2
assert sp.simplify(an - 8 * ((-1) ** n - 1) / (n**2 * sp.pi**2)) == 0
assert sp.simplify(bn) == 0
# series at x=0 must give f(0)=0
k = np.arange(1, 200_001)
val0 = 2 + np.sum(8 * ((-1.0) ** k - 1) / (k**2 * np.pi**2))
assert abs(val0) < 1e-5
# independent numeric coefficient check
xs = np.linspace(-2, 2, 400_001)
fx = 2 * np.abs(xs)
for kk in range(1, 6):
    ak = trap(fx * np.cos(kk * np.pi * xs / 2), xs) / 2
    assert abs(ak - 8 * ((-1) ** kk - 1) / (kk**2 * np.pi**2)) < 1e-6

# Branch B: f = 2x on [0, 4)
a0B = sp.integrate(2 * x, (x, 0, 4)) / 4
anB = sp.integrate(2 * x * sp.cos(n * sp.pi * x / L), (x, 0, 4)) / L
bnB = sp.integrate(2 * x * sp.sin(n * sp.pi * x / L), (x, 0, 4)) / L
assert a0B == 4 and sp.simplify(anB) == 0
assert sp.simplify(bnB + 8 / (n * sp.pi)) == 0
# series at x=1: 4 - sum 8/(k pi) sin(k pi/2) = 4 - (8/pi)(pi/4) = 2 = f(1)
valB = 4 - np.sum(8 / (k * np.pi) * np.sin(k * np.pi / 2))
assert abs(valB - 2) < 1e-4
print("PASS EE-112-03-2")
