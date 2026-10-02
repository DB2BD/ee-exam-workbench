"""EE-113-03-2 independent check: L{(sin bt - bt cos bt)/(2 b^3)}."""
import sympy as sp
import mpmath as mp

t, s, b = sp.symbols("t s beta", positive=True)
f = (sp.sin(b * t) - b * t * sp.cos(b * t)) / (2 * b**3)
F = sp.laplace_transform(f, t, s, noconds=True)
assert sp.simplify(F - 1 / (s**2 + b**2) ** 2) == 0

# Independent: numerical Laplace integral at beta=2, s=3 (and beta=-1.5 to cover beta<0).
for bv, sv in ((2.0, 3.0), (-1.5, 1.2)):
    fn = lambda tt: (mp.sin(bv * tt) - bv * tt * mp.cos(bv * tt)) / (2 * bv**3) * mp.exp(-sv * tt)
    val = float(mp.quad(fn, [0, 10, 40, mp.inf]))
    assert abs(val - 1 / (sv**2 + bv**2) ** 2) / (1 / (sv**2 + bv**2) ** 2) <= 1e-6
print("PASS EE-113-03-2")
