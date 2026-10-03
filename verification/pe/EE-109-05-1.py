"""EE-109-05-1: instantaneous power decomposition (symbolic identity).

p(t) = V I cos(a-b)[1+cos 2(wt+a)] + V I sin(a-b) sin 2(wt+a);
P = V I cos(a-b) (average), Q = V I sin(a-b) (amplitude of the zero-mean term).
"""
import sympy as sp

V, I, w, t, a, b = sp.symbols("V I omega t alpha beta", real=True)
p = sp.sqrt(2) * V * sp.cos(w * t + a) * sp.sqrt(2) * I * sp.cos(w * t + b)
P = V * I * sp.cos(a - b)
Q = V * I * sp.sin(a - b)
decomp = P * (1 + sp.cos(2 * (w * t + a))) + Q * sp.sin(2 * (w * t + a))
assert sp.simplify(sp.expand_trig(p - decomp)) == 0
T = 2 * sp.pi / w
avg = sp.simplify(sp.integrate(p.subs(w, 1), (t, 0, 2 * sp.pi)) / (2 * sp.pi))
assert sp.simplify(avg - P) == 0
# Method 2: complex power S = V I* gives the same P and Q
S = V * sp.exp(sp.I * a) * I * sp.exp(-sp.I * b)
assert sp.simplify(sp.re(sp.expand_complex(S)) - P) == 0
assert sp.simplify(sp.im(sp.expand_complex(S)) - Q) == 0
print("PASS EE-109-05-1")
