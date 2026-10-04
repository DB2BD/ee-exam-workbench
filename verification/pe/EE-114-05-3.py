"""EE-114-05-3 independent check: equal incremental cost, losses neglected.

Givens (official crop): C1 = 400 + 6.0 P1 + 0.004 P1^2, C2 = 400 + 6.8 P2 + 0.002 P2^2
($/h, P in MW), two 800 MW units, demand 550 MW.
"""
import sympy as sp

P1, P2, lam = sp.symbols("P1 P2 lam", real=True)
C1 = 400 + sp.Rational(6) * P1 + sp.Rational(4, 1000) * P1**2
C2 = 400 + sp.Rational(68, 10) * P2 + sp.Rational(2, 1000) * P2**2

# Method 1: Lagrangian stationarity.
sol = sp.solve([sp.diff(C1, P1) - lam, sp.diff(C2, P2) - lam, P1 + P2 - 550], [P1, P2, lam], dict=True)[0]
assert sol[P1] == 250 and sol[P2] == 300 and sol[lam] == 8
assert 0 <= sol[P1] <= 800 and 0 <= sol[P2] <= 800

# Method 2: brute-force minimisation of total cost on a 0.01 MW grid.
import numpy as np
p = np.arange(0, 550.001, 0.01)
total = 800 + 6.0 * p + 0.004 * p**2 + 6.8 * (550 - p) + 0.002 * (550 - p) ** 2
best = p[np.argmin(total)]
assert abs(best - 250) / 250 <= 0.005
print("PASS EE-114-05-3")
