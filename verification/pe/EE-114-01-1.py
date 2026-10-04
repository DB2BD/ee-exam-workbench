"""EE-114-01-1 independent check: full nodal (MNA) solve of the 3-node circuit.

Givens (official crop): 6 ohm v1-v3; 25 V source + at v1, - at v2; dependent
source 5I with - at v2, + at v3; 2 ohm v1-gnd (I downward), 4 ohm v2-gnd, 3 ohm v3-gnd.
"""
import sympy as sp

v1, v2, v3, i25, idep = sp.symbols("v1 v2 v3 i25 idep")
I = v1 / 2
# MNA: KCL at each node with voltage-source branch currents as unknowns
# (i25 flows v1 -> v2 through the 25 V source, idep flows v2 -> v3 through 5I).
eqs = [
    sp.Eq(v1 / 2 + (v1 - v3) / 6 + i25, 0),
    sp.Eq(v2 / 4 - i25 + idep, 0),
    sp.Eq(v3 / 3 + (v3 - v1) / 6 - idep, 0),
    sp.Eq(v1 - v2, 25),
    sp.Eq(v3 - v2, 5 * I),
]
s = sp.solve(eqs, [v1, v2, v3, i25, idep], dict=True)[0]
assert s[v1] == sp.Rational(175, 23)
assert s[v2] == sp.Rational(-400, 23)
assert s[v3] == sp.Rational(75, 46)
assert I.subs(s) == sp.Rational(175, 46)
# 6-ohm current is internal to the supernode: boundary KCL must close without it.
assert sp.simplify((v1 / 2 + v2 / 4 + v3 / 3).subs(s)) == 0
print("PASS EE-114-01-1")
