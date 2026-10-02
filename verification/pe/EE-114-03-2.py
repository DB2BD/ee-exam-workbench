"""EE-114-03-2 independent check: contour integral of exp(1/z^2) over |z|=1.

Givens (official crop): C is the unit circle centred at the origin (counter-clockwise).
"""
import numpy as np

trap = getattr(np, "trapezoid", None) or np.trapz
import sympy as sp

z = sp.symbols("z")
# Laurent series: exp(w) with w = 1/z^2 -> only even negative powers of z.
series = sum(z ** (-2 * k) / sp.factorial(k) for k in range(8))
coeff_m1 = sp.Poly(sp.expand(series * z**14), z).coeff_monomial(z**13)
assert coeff_m1 == 0  # residue at z = 0

# Independent: numerical quadrature on z = e^{i t}.
t = np.linspace(0, 2 * np.pi, 200_001)
zz = np.exp(1j * t)
val = trap(np.exp(1 / zz**2) * 1j * zz, t)
assert abs(val) < 1e-8
print("PASS EE-114-03-2")
