"""EE-109-05-5: economic dispatch with quadratic B-coefficient losses.

Givens (official crop): Ci = 6 PGi + 5e-3 PGi^2 $/h; PL = 0.5e-3 PG1^2 + 0.2e-3 PG2^2;
PD = 600 MW.
"""
import sympy as sp

P1, P2, lam = sp.symbols("P1 P2 lambda", real=True)
C1 = 6 * P1 + sp.Rational(5, 1000) * P1**2
C2 = 6 * P2 + sp.Rational(5, 1000) * P2**2
PL = sp.Rational(5, 10000) * P1**2 + sp.Rational(2, 10000) * P2**2
L = C1 + C2 + lam * (600 + PL - P1 - P2)
eqs = [sp.diff(L, s) for s in (P1, P2, lam)]
sol = sp.nsolve(eqs, [P1, P2, lam], [250, 400, 10], prec=30)
p1, p2, lm = (float(v) for v in sol)
assert abs(p1 - 268.996) < 0.01 and abs(p2 - 399.028) < 0.01 and abs(lm - 11.888) < 0.001
assert abs(float(PL.subs({P1: p1, P2: p2})) - 68.024) < 0.01

# Method 2: penalty-factor form and power balance with the unrounded values.
pf1 = 1 / (1 - 0.001 * p1); pf2 = 1 / (1 - 0.0004 * p2)
assert abs((6 + 0.01 * p1) * pf1 - (6 + 0.01 * p2) * pf2) < 1e-9
assert abs(p1 + p2 - 600 - 0.0005 * p1**2 - 0.0002 * p2**2) < 1e-9
# eliminate lambda: P1 as a function of P2 (P1 = 6(1-0.0004P2)... closed form)
p1_from_p2 = (lm - 6) / (0.01 + 0.001 * lm)
assert abs(p1_from_p2 - p1) < 1e-9
print("PASS EE-109-05-5")
