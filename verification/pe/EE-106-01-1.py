"""EE-106-01-1 independent check: Laplace solution of V_ab, cross-checked by time-domain state equations.

Givens (official crop): series branch from b to a: 6cos(6t)u(t) V (+ on the circuit side, i.e. raising the
potential toward a), 2 ohm, 4*delta(t) V source (- left, + right), L = 2 H; a-b shunt: 2 ohm, 8*delta(t) A
(arrow up into a), C = 2 F, V_ab + at a.  Zero initial energy (not stated, assumed).
"""
import numpy as np
import sympy as sp

s, t = sp.symbols("s t", positive=True)
Vs = 6 * s / (s**2 + 36) + 4                      # source EMF raising potential toward a
Zser = 2 + 2 * s
Va = sp.symbols("Va")
# node a:  (Vs - Va)/Zser + 8 = Va/2 + 2 s Va
Vab = sp.solve(sp.Eq((Vs - Va) / Zser + 8, Va / 2 + 2 * s * Va), Va)[0]
Vab = sp.simplify(Vab)
den = sp.factor(sp.denom(sp.together(Vab)))
vt = sp.inverse_laplace_transform(Vab, s, t)
vt = sp.simplify(vt)

# closed form to be reported
w = sp.sqrt(7) / 8
closed = (sp.exp(-5 * t / 8) * (sp.Rational(148939, 36862) * sp.cos(w * t)
          + sp.Rational(104225, 36862) * sp.sqrt(7) * sp.sin(w * t))
          + (45 * sp.sin(6 * t) - 213 * sp.cos(6 * t)) / 5266)
f_ref = sp.lambdify(t, vt, "numpy")
f_closed = sp.lambdify(t, closed, "numpy")
tt = np.linspace(0.01, 12, 400)
assert np.max(np.abs(f_ref(tt) - f_closed(tt))) < 1e-9

# time-domain check: impulses set i(0+) = 4/L = 2 A and v(0+) = 8/C... node: C dv/dt = i + 8 delta - v/2 -> v(0+) = 8/2 = 4
L, C = 2.0, 2.0
x = np.array([2.0, 4.0])                         # [i_L, v_C] at 0+
def rhs(tm, x):
    i, v = x
    e = 6 * np.cos(6 * tm)
    return np.array([(e - 2 * i - v) / L, (i - v / 2) / C])
h, T = 1e-4, 12.0
n = int(T / h)
ts = np.linspace(0, T, n + 1)
xs = np.zeros((n + 1, 2)); xs[0] = x
for k in range(n):
    tm = ts[k]
    k1 = rhs(tm, xs[k]); k2 = rhs(tm + h / 2, xs[k] + h / 2 * k1)
    k3 = rhs(tm + h / 2, xs[k] + h / 2 * k2); k4 = rhs(tm + h, xs[k] + h * k3)
    xs[k + 1] = xs[k] + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
idx = np.searchsorted(ts, tt)
assert np.max(np.abs(xs[idx, 1] - f_closed(ts[idx]))) < 1e-5
assert abs(float(closed.subs(t, 0)) - 4.0) < 1e-3
print("PASS EE-106-01-1")
