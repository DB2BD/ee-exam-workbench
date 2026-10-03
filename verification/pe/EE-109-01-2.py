"""EE-109-01-2 (descriptive): quantitative checks of the pole/stability claims.

Each claim in the note is checked on a concrete transfer function by computing
its impulse response with SymPy:
  LHP poles (incl. repeated) -> h(t) absolutely integrable (BIBO stable);
  simple j-axis pole -> bounded but not integrable; resonant input grows;
  repeated j-axis or RHP pole -> unbounded h(t).
"""
import sympy as sp

t, s = sp.symbols("t s", positive=True)
w = 2

def h(H):
    return sp.simplify(sp.inverse_laplace_transform(H, s, t))

# LHP distinct and repeated: integrable
for H in (1 / ((s + 1) * (s + 3)), 1 / (s + 2) ** 2, 5 / (s**2 + 2 * s + 5)):
    ht = h(H)
    assert sp.limit(ht, t, sp.oo) == 0
    val = sp.integrate(sp.Abs(ht).rewrite(sp.Piecewise), (t, 0, 50))
    assert sp.N(val) < 10

# simple j-axis pair: h = sin(2t)/2, bounded, not absolutely integrable; resonance
ht = h(1 / (s**2 + w**2))
assert sp.simplify(ht - sp.sin(w * t) / w) == 0
y = h(1 / (s**2 + w**2) * w / (s**2 + w**2))      # bounded input sin(2t)
assert sp.simplify(y - (sp.sin(w * t) - w * t * sp.cos(w * t)) / (2 * w**2)) == 0  # grows ~ t

# repeated j-axis and RHP: unbounded
assert sp.limit(sp.Abs(h(1 / s**2)), t, sp.oo) == sp.oo
assert sp.limit(h(1 / (s - 1)), t, sp.oo) == sp.oo

# second-order poles: zeta>0 LHP, zeta=0 axis, zeta<0 RHP
z = sp.symbols("zeta", real=True)
wn = 1
x = sp.symbols("x")
roots = sp.solve(x**2 + 2 * z * wn * x + wn**2, x)
assert len(roots) == 2
for zv, sign in ((sp.Rational(1, 2), -1), (0, 0), (-sp.Rational(1, 2), 1)):
    re = {sp.sign(sp.re(r.subs(z, zv))) for r in roots}
    assert re == {sign}
print("PASS EE-109-01-2 (descriptive)")
