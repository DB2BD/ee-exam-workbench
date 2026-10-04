"""EE-109-01-3 independent check: nodal solution and its dual network.

Givens (official crop): centre node = reference; 1, 2, 3, 4 ohm from V1, V2,
V3, V4 to it; 1 A source V4 -> V1; 2 V source (+ at V1) between V1, V2; 3 A
source V2 -> V3; 4 V source (+ at V3) between V4, V3.

1) Original circuit solved by full MNA (source currents as unknowns).
2) The dual network drawn in the note (window-frame, centre node O, spokes
   T-O: 2 A (T->O), R-O: 3 V (+ at R), B-O: 4 A (B->O), Lf-O: 1 V (+ at Lf);
   outer resistors Lf-T 1, T-R 0.5, R-B 1/3, B-Lf 1/4 ohm) is solved by nodal
   analysis; its clockwise mesh currents must equal V1..V4 numerically.
"""
import sympy as sp

V1, V2, V3, V4, i2v, i4v = sp.symbols("V1 V2 V3 V4 i2v i4v")
# i2v: current V1 -> V2 inside the 2 V source; i4v: current V4 -> V3 inside the 4 V source
eqs = [
    sp.Eq(V1 / 1 + i2v, 1),
    sp.Eq(V2 / 2 - i2v + 3, 0),
    sp.Eq(V3 / 3 - i4v - 3, 0),
    sp.Eq(V4 / 4 + i4v + 1, 0),
    sp.Eq(V1 - V2, 2),
    sp.Eq(V3 - V4, 4),
]
s = sp.solve(eqs, [V1, V2, V3, V4, i2v, i4v], dict=True)[0]
node = [s[V1], s[V2], s[V3], s[V4]]
assert node == [sp.Rational(-2, 3), sp.Rational(-8, 3), sp.Rational(36, 7), sp.Rational(8, 7)]

# Dual network, nodal analysis with O as reference.
T, B = sp.symbols("T B")
Lf, R = 1, 3  # voltage sources on the spokes
dual = [
    sp.Eq((Lf - T) / 1 - (T - R) / sp.Rational(1, 2) - 2, 0),  # KCL at T
    sp.Eq((R - B) / sp.Rational(1, 3) - (B - Lf) / sp.Rational(1, 4) - 4, 0),  # KCL at B
]
d = sp.solve(dual, [T, B], dict=True)[0]
i1 = (Lf - d[T]) / 1
i2 = (d[T] - R) / sp.Rational(1, 2)
i3 = (R - d[B]) / sp.Rational(1, 3)
i4 = (d[B] - Lf) / sp.Rational(1, 4)
assert [i1, i2, i3, i4] == node
print("V =", node, "dual mesh currents =", [i1, i2, i3, i4])
print("PASS EE-109-01-3")
