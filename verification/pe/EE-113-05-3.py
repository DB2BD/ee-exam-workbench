"""EE-113-05-3 independent check: identify alpha, beta from two lambda points.

Givens (official crop): two 1300 MW units, C1 = 500 + 8P1 + 0.005P1^2,
C2 = 700 + alpha P2 + beta P2^2; PD = 800 -> lambda = 10; PD = 1500 -> lambda = 12;
losses neglected.
"""
import sympy as sp
import numpy as np

a, b = sp.symbols("alpha beta", real=True)
eqs = []
for PD, lam in ((800, 10), (1500, 12)):
    P1 = sp.Rational(lam - 8) / sp.Rational(1, 100)
    P2 = PD - P1
    assert 0 <= P1 <= 1300 and 0 <= P2 <= 1300
    eqs.append(sp.Eq(a + 2 * b * P2, lam))
sol = sp.solve(eqs, [a, b], dict=True)[0]
assert sol[a] == sp.Rational(76, 10) and sol[b] == sp.Rational(2, 1000)

# Method 2: re-dispatch numerically with the identified coefficients.
for PD, lam in ((800, 10), (1500, 12)):
    p = np.arange(0, PD + 0.001, 0.01)
    p = p[(p <= 1300) & (PD - p <= 1300)]
    cost = 8 * p + 0.005 * p**2 + 7.6 * (PD - p) + 0.002 * (PD - p) ** 2
    p1 = p[np.argmin(cost)]
    assert abs(8 + 0.01 * p1 - lam) / lam <= 0.005
print("PASS EE-113-05-3")
