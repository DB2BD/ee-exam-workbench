"""EE-114-02-3 independent check: switch-mode R-L-E circuit, iL(t) on 0..1 ms.

Givens (official crop): L = 25 mH, R = 0.5 ohm, VS = 5 V, E = 10 V; diode anode at the
switch node, cathode at VS+; iL flows from the switch node through L, R into E+.
Fig.(b): vQ = 0 (Q open) on 0-0.5 ms, vQ = VQ (Q shorted) on 0.5-1 ms, period 1 ms.
No initial current is given: periodic steady state iL(1 ms) = iL(0).
The stem orders the approximations e^-x ~ 1-x and (1-x)^2 ~ 1-2x: the boxed answer is
iL = -15 + 100 t (0..0.5 ms) and -14.95 - 101 (t - 0.5 ms) (0.5..1 ms), t in s.
Method: SymPy dsolve of each interval + periodic boundary; cross-check with a
fine explicit time-stepping of the switched ODE including the diode condition.
"""
import math

import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


L, R, VS, E = sp.Rational(25, 1000), sp.Rational(1, 2), 5, 10
t, i0 = sp.symbols("t i0")
f = sp.Function("i")
seg1 = sp.dsolve(sp.Eq(L * f(t).diff(t) + R * f(t), VS - E), f(t), ics={f(0): i0}).rhs
im = seg1.subs(t, sp.Rational(1, 2000))
seg2 = sp.dsolve(sp.Eq(L * f(t).diff(t) + R * f(t), -E), f(t), ics={f(0): im}).rhs
i0s = sp.solve(sp.Eq(seg2.subs(t, sp.Rational(1, 2000)), i0), i0)[0]
I0, Im = float(i0s), float(im.subs(i0, i0s))
assert I0 < 0 and Im < 0   # diode conducts in segment 1 (iL < 0)

# Main (boxed) answer with the stated approximations: a ~ 1-x, a^2 ~ 1-2x, x = 0.01
x = 0.01
I0_lin = (-20 + 10 * (1 - x) + 10 * (1 - 2 * x)) / (2 * x)     # (1-a^2) i0 = -20+10a+10a^2
Im_lin = -10 + (I0_lin + 10) * (1 - x)
assert abs(I0_lin - (-15.0)) < 1e-9 and abs(Im_lin - (-14.95)) < 1e-9
tau = 0.05
seg1_lin = lambda tt: -10 + (I0_lin + 10) * (1 - tt / tau)          # -> -15 + 100 t
seg2_lin = lambda tt: -20 + (Im_lin + 20) * (1 - (tt - 5e-4) / tau)  # -> -14.95 - 101 (t-0.5ms)
for tt in (0.0, 2e-4, 5e-4):
    assert abs(seg1_lin(tt) - (-15 + 100 * tt)) < 1e-9
for tt in (5e-4, 8e-4, 1e-3):
    assert abs(seg2_lin(tt) - (-14.95 - 101 * (tt - 5e-4))) < 1e-9
assert abs(seg2_lin(1e-3) - (-15.0005)) < 1e-9

# Exact periodic solution (cross-check, within 0.5 %)
assert abs(I0 - (-15.0249998)) < 1e-6 and abs(Im - (-14.9750002)) < 1e-6
assert close(I0_lin, I0) and close(Im_lin, Im)
t_s = sp.Rational(3, 10000)
assert close(-15 + 100 * float(t_s), float(seg1.subs({i0: i0s, t: t_s})))
assert close(-14.95 - 101 * float(t_s), float(seg2.subs({i0: i0s, t: t_s})))

# Independent time stepping with diode logic, starting from 0 A and many periods.
dt, i = 1e-7, 0.0
Lf, Rf = 0.025, 0.5
for cyc in range(400):
    for k in range(10000):
        tt = k * dt
        q_on = tt >= 0.5e-3
        if q_on:
            va = 0.0
        else:
            va = VS if i < 0 else None
        if va is None:          # Q open, diode off -> iL forced to 0
            i = 0.0
            continue
        i += dt * (va - Rf * i - E) / Lf
    if cyc == 399:
        pass
start = i
for k in range(5000):
    i += dt * (VS - Rf * i - E) / Lf
assert close(start, I0) and close(i, Im)
print(f"approx iL(0)={I0_lin:.3f} A, iL(0.5ms)={Im_lin:.3f} A; exact {I0:.6f}/{Im:.6f} A; step-sim {start:.4f}/{i:.4f}")
print("PASS EE-114-02-3")
