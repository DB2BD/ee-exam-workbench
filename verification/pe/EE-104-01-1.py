"""EE-104-01-1: Thevenin equivalent at a-b.  Ground = 9 V source negative terminal.
Nodes: T (9 V +, = 9 V), X (between 5 ohm, 25 ohm, current source), A, B (b terminal).
20 ohm T-A; 5 ohm T-X; 25 ohm X-G; 1.8 A X->A; 60 ohm A-B; 10 ohm G-B."""
import sympy as sp
X, A, B = sp.symbols("X A B")
# open circuit
s = sp.solve([sp.Eq((9 - X) / 5, X / 25 + sp.Rational(9, 5)),
              sp.Eq(sp.Rational(9, 5) + (9 - A) / 20, (A - B) / 60),
              sp.Eq((A - B) / 60, B / 10)], [X, A, B])
Vth = s[A] - s[B]
assert Vth == 30, Vth
# Rth by test source Vt across a-b with 9 V shorted (T = G = 0) and 1.8 A open
Vt = sp.symbols("Vt")
Ia = Vt / 60 + Vt / (20 + 10)       # test source sees 60 || (20+10)
Rth = sp.simplify(Vt / Ia)
assert Rth == 20, Rth
# Norton cross-check: short a-b (A = B), solve for short-circuit current
X2, A2, B2, Isc = sp.symbols("X2 A2 B2 Isc")
s2 = sp.solve([sp.Eq((9 - X2) / 5, X2 / 25 + sp.Rational(9, 5)),
               sp.Eq(sp.Rational(9, 5) + (9 - A2) / 20, Isc),
               sp.Eq(Isc, B2 / 10), sp.Eq(A2, B2)], [X2, A2, B2, Isc])
assert sp.simplify(Vth / s2[Isc] - 20) == 0, s2
print("PASS EE-104-01-1")
