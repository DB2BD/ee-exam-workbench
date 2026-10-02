"""EE-112-01-3 independent check: load-line fit with a symbolic load RL.

Givens (official crop): vs = 8 V, R1 = R2 = R3 = 10 ohm, CCVS r*ix (r = 5 ohm,
+ on the R2 side, - on the R3/output side), ix rightward through R1.
"""
import sympy as sp

va, vb, RL = sp.symbols("va vb RL", positive=True)
ix = (8 - va) / 10
icc = sp.symbols("icc")  # CCVS current from va to vb
eqs = [sp.Eq(va - vb, 5 * ix), sp.Eq(ix, va / 10 + icc), sp.Eq(icc, vb / 10 + vb / RL)]
s = sp.solve(eqs, [va, vb, icc], dict=True)[0]
VL = sp.simplify(s[vb])
IN, RN = sp.Rational(4, 15), sp.Rational(30, 7)
# Norton source IN in parallel with RN feeding RL must give the same load voltage for every RL.
assert sp.simplify(VL - IN * RN * RL / (RN + RL)) == 0
print("PASS EE-112-01-3")
