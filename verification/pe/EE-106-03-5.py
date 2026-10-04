"""EE-106-03-5 independent check (official crop): z = 1 - sqrt(3) i, find z^12."""
import cmath
import sympy as sp

z = 1 - sp.sqrt(3) * sp.I
assert sp.simplify(sp.Abs(z) - 2) == 0
assert sp.simplify(sp.arg(z) + sp.pi / 3) == 0
val = sp.expand((z**12))
assert val == 4096
# Independent: polar form numerics and repeated squaring
zn = complex(1, -3**0.5)
assert abs(zn**12 - 4096) / 4096 <= 0.005
assert abs(2**12 * cmath.exp(-12j * cmath.pi / 3) - 4096) / 4096 <= 0.005
z2 = sp.expand(z**2)
z3 = sp.expand(z2 * z)
assert z3 == -8 and sp.expand(z3**4) == 4096
print("PASS EE-106-03-5")
