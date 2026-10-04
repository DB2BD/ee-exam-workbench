"""EE-106-01-4 independent check: I_o of the symmetric lattice with 30 V and 60 V sources.

Givens (official crop): left source 30 V (+ top), right source 60 V (+ top).  Top rail: 1 ohm, node T1,
2 ohm, node T2, 1 ohm to the right source; bottom rail likewise 1 ohm, B1, 2 ohm, B2, 1 ohm.
Crossed 3 ohm resistors: T1-B2 and T2-B1.  I_o flows leftward on the top rail out of the right
source's + terminal.
"""
import numpy as np
import sympy as sp

# --- direct nodal solve (reference answer)
n = {"Lp": 0, "T1": 1, "T2": 2, "Rp": 3, "Lm": 4, "B1": 5, "B2": 6, "Rm": 7}
def solve(vl, vr):
    A = np.zeros((10, 10)); b = np.zeros(10)
    def g(p, q, r):
        i, j = n[p], n[q]
        A[i, i] += 1 / r; A[j, j] += 1 / r; A[i, j] -= 1 / r; A[j, i] -= 1 / r
    g("Lp", "T1", 1); g("T1", "T2", 2); g("T2", "Rp", 1)
    g("Lm", "B1", 1); g("B1", "B2", 2); g("B2", "Rm", 1)
    g("T1", "B2", 3); g("T2", "B1", 3)
    # sources: V(Lp)-V(Lm)=vl (branch 8), V(Rp)-V(Rm)=vr (branch 9)
    for k, (p, q, v) in enumerate([("Lp", "Lm", vl), ("Rp", "Rm", vr)]):
        A[8 + k, n[p]] = 1; A[8 + k, n[q]] = -1; b[8 + k] = v
        A[n[p], 8 + k] = 1; A[n[q], 8 + k] = -1
    x = np.linalg.solve(A, b)
    return x
x = solve(30, 60)
# current leaving the right source + terminal into the top rail = -(branch current p->q inside the source)... compute from the 1 ohm
Io_direct = (x[n["Rp"]] - x[n["T2"]]) / 1
assert abs(Io_direct - 12.75) < 1e-9, Io_direct

# --- symmetric / antisymmetric decomposition (independent of the full solve)
E_sym, E_asym = (30 + 60) / 2, (60 - 30) / 2
# symmetric: no current across the axis, half circuit = E - 1 - 3 - 1 loop
I_sym = sp.Rational(45) / (1 + 3 + 1)
# antisymmetric: axis nodes at 0 V; solve half circuit with the cross branches carrying (x + y)/3
xx, yy, Ia = sp.symbols("xx yy Ia")
eqs = [
    sp.Eq(Ia, xx + (xx + yy) / 3),            # KCL at T2 : 2 ohm to the mirror node (-xx) and cross 3 ohm to B1 (= -yy)
    sp.Eq(Ia, -yy - (xx + yy) / 3),           # KCL at B2
    sp.Eq(xx - yy + 2 * Ia, 15),              # rail drops and the 15 V source
]
sol = sp.solve(eqs, [xx, yy, Ia], dict=True)[0]
assert sol[Ia] == sp.Rational(15, 4) and sol[xx] + sol[yy] == 0
Io = I_sym + sol[Ia]
assert Io == sp.Rational(51, 4)
assert abs(float(Io) - Io_direct) < 1e-9
# the antisymmetric half circuit is 1+1+1+1 = 4 ohm (cross branches carry no current)
assert abs(15 / 4 - float(sol[Ia])) < 1e-12
print("PASS EE-106-01-4")
