"""EE-113-03-3 independent check: integral of sqrt(2)/(1+16x^4) over the real line."""
import math
import sympy as sp
import mpmath as mp

z = sp.symbols("z")
# Residue route on 1/(1+z^4) in the upper half plane.
poles = [sp.exp(sp.I * sp.pi / 4), sp.exp(3 * sp.I * sp.pi / 4)]
res = sum(1 / (4 * p**3) for p in poles)
J = sp.nsimplify(sp.simplify(sp.expand_complex(2 * sp.pi * sp.I * res)))
assert sp.simplify(J - sp.pi / sp.sqrt(2)) == 0
I = sp.sqrt(2) / 2 * J
assert sp.simplify(I - sp.pi / 2) == 0

# Independent: direct numerical quadrature.
val = float(mp.quad(lambda x: mp.sqrt(2) / (1 + 16 * x**4), [-mp.inf, 0, mp.inf]))
assert abs(val - math.pi / 2) < 1e-9
print("PASS EE-113-03-3")
