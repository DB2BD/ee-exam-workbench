"""EE-114-01-4 independent check: time-domain ODE, undetermined coefficients.

Givens (official crop): 75 sin(5t) V source in series with 8 ohm to node vo;
0.2 F, 1 H and 6 cos(10t) A source (pointing up, into vo) all from vo to ground.
Differentiated KCL: C v'' + v'/R + v/L = d/dt[vs/R + is]; no phasors used.
"""
import math
import sympy as sp

t = sp.symbols("t", real=True)
a, b, c, d = sp.symbols("a b c d", real=True)
R, C, L = 8, sp.Rational(1, 5), 1
v = a * sp.sin(5 * t) + b * sp.cos(5 * t) + c * sp.sin(10 * t) + d * sp.cos(10 * t)
res = sp.expand(C * v.diff(t, 2) + v.diff(t) / R + v / L
                - sp.diff(75 * sp.sin(5 * t) / R + 6 * sp.cos(10 * t), t))
eqs = [res.coeff(f) for f in (sp.sin(5 * t), sp.cos(5 * t), sp.sin(10 * t), sp.cos(10 * t))]
sol = sp.solve(eqs, [a, b, c, d], dict=True)[0]
A, B, Cc, D = (float(sol[k]) for k in (a, b, c, d))
amp5, ph5 = math.hypot(A, B), math.degrees(math.atan2(B, A))      # a sin + b cos = amp sin(5t+ph)
amp10, ph10 = math.hypot(Cc, D), math.degrees(math.atan2(D, Cc))

def close(x, y, tol=5e-3):
    return abs(x - y) <= tol * abs(y)

assert close(amp5, 11.5783), amp5
assert close(ph5, -81.1193), ph5
assert close(amp10, 3.15108), amp10
assert close(ph10, 3.76403), ph10
print("PASS EE-114-01-4")
