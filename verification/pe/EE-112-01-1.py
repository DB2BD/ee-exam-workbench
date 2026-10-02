"""EE-112-01-1 independent check: full nodal solve with conductance matrix (no Delta-Y).

Givens (official crop): 120 V (+ top) -> 5 k to node T; bridge T-L 6 k, T-R 18 k,
L-R 12 k, L-B 4 k, R-B 6 k; B is the source's negative terminal (reference).
"""
import sympy as sp

vT, vL, vR = sp.symbols("vT vL vR")
k = 1000
eqs = [
    sp.Eq((vT - 120) / (5 * k) + (vT - vL) / (6 * k) + (vT - vR) / (18 * k), 0),
    sp.Eq((vL - vT) / (6 * k) + (vL - vR) / (12 * k) + vL / (4 * k), 0),
    sp.Eq((vR - vT) / (18 * k) + (vR - vL) / (12 * k) + vR / (6 * k), 0),
]
s = sp.solve(eqs, [vT, vL, vR], dict=True)[0]
Is = (120 - s[vT]) / (5 * k)
P = 120 * Is
assert P == sp.Rational(6, 5)
# Tellegen check: source power equals the sum of resistor powers.
edges = [(120, s[vT], 5), (s[vT], s[vL], 6), (s[vT], s[vR], 18), (s[vL], s[vR], 12), (s[vL], 0, 4), (s[vR], 0, 6)]
assert sum((a - b) ** 2 / (r * k) for a, b, r in edges) == P
print("PASS EE-112-01-1")
