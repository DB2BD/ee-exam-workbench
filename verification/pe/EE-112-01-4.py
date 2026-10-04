"""EE-112-01-4 independent check: Laplace-domain nodal solve and inverse transform.

Givens (official crop): -3u(t) A source arrow up (into top); 0.2 H (i down);
20 mF (v, + top); 0.5 ohm; 3u(t) A source arrow down (out of top); zero initial state.
"""
import sympy as sp

s, t = sp.symbols("s t", positive=True)
Iin = (-3 - 3) / s                       # net injection into the top node
Y = 1 / (sp.Rational(1, 5) * s) + sp.Rational(1, 50) * s + 2
V = sp.simplify(Iin / Y)
Ii = sp.simplify(V / (sp.Rational(1, 5) * s))
v = sp.inverse_laplace_transform(V, s, t)
i = sp.inverse_laplace_transform(Ii, s, t)
r = sp.sqrt(10)
s1, s2 = -50 + 15 * r, -50 - 15 * r
i_exp = -6 + (3 + r) * sp.exp(s1 * t) + (3 - r) * sp.exp(s2 * t)
v_exp = r * (sp.exp(s2 * t) - sp.exp(s1 * t))
for tv in (0.001, 0.01, 0.05, 0.3, 2.0):
    assert abs(float((i - i_exp).subs(t, tv))) < 1e-9
    assert abs(float((v - v_exp).subs(t, tv))) < 1e-9
print("PASS EE-112-01-4")
