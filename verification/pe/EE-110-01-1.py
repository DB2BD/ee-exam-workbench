"""EE-110-01-1 independent check: coupled coils with a bridging capacitor.

Givens (official crop): is = 10 cos t A (up) feeds the left top node; 1 ohm
(v1) and L1 = 3 H (dot top) from that node to the left bottom rail.  Right side:
L2 = 1 H (dot bottom) and 2 ohm (v2, + top) between the right top node and the
right bottom rail; M = 1 H; a 2 F capacitor joins the two top nodes.  The crop
shows the two bottom rails as separate wires (no common return).

Main check (as drawn): no return path -> capacitor current 0.  Solved with
mesh currents on the right loop and nodal on the left.  A second model with a
common ground is evaluated only to document the alternative reading.
"""
import sympy as sp

w = 1
jw = sp.I * w
L1, L2, M, C = 3, 1, 1, 2
Is = 10

# --- As drawn: two isolated islands linked only by C (KCL on the right island
# forces the capacitor current to zero).  Unknowns: V1, iA (down through L1 into
# dot), ib (clockwise in right loop: down through 2 ohm, up through L2 into dot).
V1, iA, ib, ic = sp.symbols("V1 iA ib ic")
eqs = [
    sp.Eq(Is, V1 / 1 + iA + ic),
    sp.Eq(V1, jw * L1 * iA + jw * M * ib),            # L1 dot top; ib enters L2 dot
    sp.Eq(-2 * ib, jw * L2 * ib + jw * M * iA),       # right loop KVL (L2 dot-to-top drop)
    sp.Eq(ic, 0),                                     # isolated island: no net current
]
s = sp.solve(eqs, [V1, iA, ib, ic], dict=True)[0]
V2 = sp.nsimplify(sp.simplify(2 * s[ib]))
print("V2 (as drawn) =", V2)
assert sp.simplify(V2 + sp.Rational(20, 7)) == 0

# Check: right island current balance is automatic — capacitor carries none.
# --- Alternative reading: bottom rails joined (common reference).
x, y, ia, ic2 = sp.symbols("x y ia ic2")  # ic2 = current down through L2 (top -> dot bottom)
alt = [
    sp.Eq(Is, x + ia + (x - y) * jw * C),
    sp.Eq((y - x) * jw * C + y / 2 + ic2, 0),
    sp.Eq(x, jw * L1 * ia + jw * M * (-ic2)),
    sp.Eq(0 - y, jw * L2 * (-ic2) + jw * M * ia),
]
sa = sp.solve(alt, [x, y, ia, ic2], dict=True)[0]
Valt = complex(sp.N(sa[y]))
import cmath, math
print(f"V2 (common ground) = {abs(Valt):.5f} ang {math.degrees(cmath.phase(Valt)):.4f}", sp.simplify(sa[y]))
assert sp.simplify(sa[y] - (500 + 2400 * sp.I) / 601) == 0
print("PASS EE-110-01-1")
