"""EE-111-03-2 independent check: inverse Laplace of ln((s-a)/(s-b))."""
import mpmath as mp
import sympy as sp

t, s = sp.symbols("t s", positive=True)
a, b = sp.Rational(-1, 1), sp.Rational(-3, 1)  # sample values with convergent transforms
f = (sp.exp(b * t) - sp.exp(a * t)) / t
# Forward transform numerically at several s and compare with ln((s-a)/(s-b))
for sv in (0.5, 1.0, 2.0, 5.0):
    num = mp.quad(lambda tt: (mp.exp(-3 * tt) - mp.exp(-1 * tt)) / tt * mp.exp(-sv * tt), [0, mp.inf])
    assert abs(num - mp.log((sv + 1) / (sv + 3))) < 1e-10
# Symbolic: -dF/ds = L{t f(t)}
A, B = sp.symbols("a b")
F = sp.log((s - A) / (s - B))
tf = sp.inverse_laplace_transform(sp.simplify(-sp.diff(F, s)), s, t)
assert sp.simplify(tf - (sp.exp(B * t) - sp.exp(A * t))) == 0
print("PASS EE-111-03-2")
