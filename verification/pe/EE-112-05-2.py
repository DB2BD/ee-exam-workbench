"""EE-112-05-2 independent check: beta, gamma from two lambda points with 800 MW limits.

Givens (official crop): two 800 MW plants, C1 = 400 + 7.0P1 + gamma P1^2,
C2 = 450 + beta P2 + 0.002P2^2; PD = 550 -> lambda = 8, PD = 1300 -> lambda = 10.
The note is needs_manual_review: this script checks every candidate branch.
"""
import sympy as sp
import numpy as np

b, g = sp.symbols("beta gamma", positive=True)

# Branch A: both units interior at both points (limits ignored).
P1a, P1b = 1 / (2 * g), 3 / (2 * g)
solA = sp.solve([sp.Eq(b + sp.Rational(4, 1000) * (550 - P1a), 8),
                 sp.Eq(b + sp.Rational(4, 1000) * (1300 - P1b), 10)], [b, g], dict=True)[0]
assert solA[g] == sp.Rational(1, 250) and solA[b] == sp.Rational(63, 10)
assert 1300 - P1b.subs(g, solA[g]) == 925  # violates 800 MW

# Branch B: P2 = 800 at the 1300 MW point.
gB = sp.Rational(10 - 7, 2 * 500)
bB = 8 - sp.Rational(4, 1000) * (550 - 1 / (2 * gB))
assert gB == sp.Rational(3, 1000) and abs(float(bB) - 6.4667) < 1e-4
assert bB + sp.Rational(4, 1000) * 800 <= 10  # KKT at upper limit

# Branch C: P1 = 800 at the 1300 MW point, P2 free.
bC = 10 - sp.Rational(4, 1000) * 500
gC = sp.Rational(8 - 7, 2 * 550)  # P2 = (8 - bC)/0.004 = 0 at 550 MW
assert bC == 8 and gC == sp.Rational(1, 1100)
assert 7 + 2 * gC * 800 <= 10

# Independent check: constrained dispatch by grid search reproduces both lambdas
# for branches B and C (they are genuinely valid optima under 0..800 limits).
def dispatch(beta, gamma, PD):
    p = np.arange(max(0, PD - 800), min(800, PD) + 1e-9, 0.01)
    cost = 7 * p + gamma * p**2 + beta * (PD - p) + 0.002 * (PD - p) ** 2
    return round(float(p[np.argmin(cost)]), 6)

for beta, gamma in ((float(bB), float(gB)), (float(bC), float(gC))):
    for PD, lam in ((550, 8), (1300, 10)):
        p1 = dispatch(beta, gamma, PD)
        p2 = PD - p1
        free = [7 + 2 * gamma * p1 if 1e-3 < p1 < 800 - 1e-3 else None,
                beta + 0.004 * p2 if 1e-3 < p2 < 800 - 1e-3 else None]
        lam_num = next(x for x in free if x is not None)
        assert abs(lam_num - lam) / lam <= 0.005
# Unconstrained pair under hard limits: 1300 MW -> P1 = 500, lambda = IC1 = 11 != 10.
p1 = dispatch(6.3, 0.004, 1300)
assert abs(p1 - 500) < 1e-3 and abs(7 + 2 * 0.004 * p1 - 11) < 1e-6
print("PASS EE-112-05-2")
