"""EE-109-01-1 independent check: three-op-amp instrumentation amplifier.

Givens (official crop): top op-amp (+) = v1, bottom op-amp (+) = v2; each (-)
input tied to one end of Rg and through R1 to its own output; top output ->
R2 -> (-) of the output op-amp (R0 feedback); bottom output -> R2 -> (+) of the
output op-amp with R0 to ground.  Solved as one linear system (all node KCL).
"""
import sympy as sp

v1, v2, R0, R1, R2, Rg = sp.symbols("v1 v2 R0 R1 R2 Rg", positive=True)
a, b, oa, ob, n, p, vo = sp.symbols("a b oa ob n p vo")
eqs = [
    sp.Eq(a, v1), sp.Eq(b, v2),                     # virtual shorts, input stage
    sp.Eq((a - b) / Rg + (a - oa) / R1, 0),          # KCL at top (-) node
    sp.Eq((b - a) / Rg + (b - ob) / R1, 0),          # KCL at bottom (-) node
    sp.Eq((p - ob) / R2 + p / R0, 0),                # output stage (+) node
    sp.Eq(n, p),                                     # virtual short, output stage
    sp.Eq((n - oa) / R2 + (n - vo) / R0, 0),         # output stage (-) node
]
s = sp.solve(eqs, [a, b, oa, ob, n, p, vo], dict=True)[0]
expected = R0 / R2 * (1 + 2 * R1 / Rg) * (v2 - v1)
assert sp.simplify(s[vo] - expected) == 0
print("vo =", sp.factor(s[vo]))
print("PASS EE-109-01-1")
