"""EE-110-05-4: loss formula, incremental loss and IC at bus 1.

Givens (official crop): IC1 = 0.007 PG1 + 4, IC2 = 0.007 PG2 + 4 ($/MWh, MW);
PD = 300 MW, base 100 MW; P1 = 3(1-cos t) + 10 sin t, P2 = 3(1-cos t) - 10 sin t,
t = theta12; part 3 at t = -5 deg.
"""
import numpy as np
import sympy as sp

t = sp.symbols("t")
P1 = 3 * (1 - sp.cos(t)) + 10 * sp.sin(t)
P2 = 3 * (1 - sp.cos(t)) - 10 * sp.sin(t)
PL = sp.simplify(P1 + P2)
assert sp.simplify(PL - 6 * (1 - sp.cos(t))) == 0
ITL = sp.simplify(sp.diff(PL, t) / sp.diff(P2, t))
assert sp.simplify(ITL - 6 * sp.sin(t) / (3 * sp.sin(t) - 10 * sp.cos(t))) == 0
tv = sp.rad(-5)
itl = float(ITL.subs(t, tv))
assert abs(itl - 0.05115) / 0.05115 < 0.005
PG1 = 300 + 100 * float(P1.subs(t, tv))
IC1 = 0.007 * PG1 + 4
assert abs(PG1 - 213.99) < 0.01
assert abs(IC1 - 5.4979) < 1e-3

# Method 2: numerical derivative of PL w.r.t. PG2 by perturbing theta.
f = lambda th: (6 * (1 - np.cos(th)), 100 * (3 * (1 - np.cos(th)) - 10 * np.sin(th)))
h = 1e-6; th0 = np.radians(-5)
(pl1, pg1), (pl2, pg2) = f(th0 - h), f(th0 + h)
assert abs(100 * (pl2 - pl1) / (pg2 - pg1) - itl) < 1e-6
# power balance: PG1 + PG2 = PD + PL (MW)
PG2 = 100 * float(P2.subs(t, tv))
assert abs(PG1 + PG2 - 300 - 100 * float(PL.subs(t, tv))) < 1e-9
print("PASS EE-110-05-4")
