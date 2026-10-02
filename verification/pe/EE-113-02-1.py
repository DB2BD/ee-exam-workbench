"""EE-113-02-1 independent check: two ideal diodes, states and Vo.

Givens (official crop): +12 V -> 10k -> node x; D1 anode x, cathode ground;
D2 anode x, cathode Vo; Vo -> 5k -> -12 V.
Method: enumerate all four ideal-diode state combinations, solve each linear
circuit, keep only the self-consistent one (on: I >= 0, off: Vd <= 0).
"""
import itertools

import sympy as sp

vx, vo = sp.symbols("vx vo")
consistent = []
for d1, d2 in itertools.product((True, False), repeat=2):
    eqs = []
    i_top = (12 - vx) / 10e3
    i_bot = (vo + 12) / 5e3
    if d1:
        eqs.append(sp.Eq(vx, 0))
    if d2:
        eqs.append(sp.Eq(vx, vo))
    else:
        eqs.append(sp.Eq(i_bot, 0))
    if not d1:
        eqs.append(sp.Eq(i_top, i_bot if d2 else 0))
    else:
        pass
    sol = sp.solve(eqs, [vx, vo], dict=True)
    if not sol:
        continue
    sol = sol[0]
    X, O = float(sol[vx]), float(sol[vo])
    iD2 = float(i_bot.subs(sol)) if d2 else 0.0
    iD1 = float(i_top.subs(sol)) - iD2 if d1 else 0.0
    ok = (iD1 >= 0 if d1 else X <= 1e-12) and (iD2 >= 0 if d2 else X - O <= 1e-12)
    if ok:
        consistent.append((d1, d2, X, O, iD2))

assert len(consistent) == 1, consistent
d1, d2, X, O, I = consistent[0]
assert (d1, d2) == (False, True)
assert abs(O - (-4.0)) < 1e-9 and abs(I - 1.6e-3) < 1e-12
# KVL check from the top side
assert abs(12 - I * 10e3 - O) < 1e-9
print(f"D1 off, D2 on, Vo={O:.3f} V, I={I*1e3:.3f} mA")
print("PASS EE-113-02-1")
