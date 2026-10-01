"""EE-114-01-2 independent check: Norton equivalent at a-b.

Givens (official crop): node 1 has 6 ohm to b and a 10 A source pointing up (into node 1);
dependent source 2Vx between node 1 (+) and a (-); 2 ohm from a to b with Vx = Va - Vb.
"""
import sympy as sp

V1, Va, I = sp.symbols("V1 Va I")

# Full nodal model with an external current I injected into a (b = reference).
eqs = [
    sp.Eq(V1 - Va, 2 * Va),                      # dependent source, Vx = Va
    sp.Eq(10, V1 / 6 + (Va / 2 - I)),            # KCL at node 1: source branch carries Va/2 - I
]
sol = sp.solve(eqs, [V1, Va], dict=True)[0]
Va_of_I = sp.simplify(sol[Va])                   # port law Va = Voc + R*I
Voc = Va_of_I.subs(I, 0)
R_th = sp.diff(Va_of_I, I)
assert Voc == 10 and R_th == 1

# Independent: short-circuit current (Vx = 0 forces V1 = 0, all 10 A to the short).
V1s, Isc = sp.symbols("V1s Isc")
s = sp.solve([sp.Eq(V1s - 0, 0), sp.Eq(10, V1s / 6 + Isc)], [V1s, Isc], dict=True)[0]
assert s[Isc] == 10
assert Voc / s[Isc] == R_th
print("PASS EE-114-01-2")
