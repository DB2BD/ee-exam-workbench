"""EE-112-03-1 independent check: 2y'' + y' + 2y = g(t), y(0)=y'(0)=0,
g = 1 on 5 <= t < 20, 0 otherwise (official crop)."""
import mpmath as mp
import sympy as sp

t, s = sp.symbols("t s", positive=True)
w = sp.sqrt(15) / 4
Phi = sp.Rational(1, 2) - sp.Rational(1, 2) * sp.exp(-t / 4) * (sp.cos(w * t) + sp.sin(w * t) / sp.sqrt(15))
# Phi is the unit-step response: L{Phi} = 1/(s(2s^2+s+2)).
assert sp.simplify(sp.laplace_transform(Phi, t, s, noconds=True) - 1 / (s * (2 * s**2 + s + 2))) == 0
assert sp.simplify(2 * Phi.diff(t, 2) + Phi.diff(t) + 2 * Phi - 1) == 0
assert Phi.subs(t, 0) == 0 and sp.simplify(Phi.diff(t).subs(t, 0)) == 0

def y(tv):
    tv = mp.mpf(tv)
    out = mp.mpf(0)
    for shift, sign in ((5, 1), (20, -1)):
        if tv >= shift:
            out += sign * float(Phi.subs(t, tv - shift))
    return out

# Independent: numerical ODE integration (mpmath odefun) on each interval.
f = lambda tt, Y: [Y[1], ((1 if 5 <= tt < 20 else 0) - Y[1] - 2 * Y[0]) / 2]
sol0 = mp.odefun(lambda tt, Y: [Y[1], (1 - Y[1] - 2 * Y[0]) / 2], 5, [0, 0])
for tv in (8, 12, 19.5):
    assert abs(sol0(tv)[0] - y(tv)) < 1e-8
Y20 = sol0(20)
sol1 = mp.odefun(lambda tt, Y: [Y[1], (-Y[1] - 2 * Y[0]) / 2], 20, Y20)
for tv in (22, 30):
    assert abs(sol1(tv)[0] - y(tv)) < 1e-8
assert y(3) == 0
print("PASS EE-112-03-1")
