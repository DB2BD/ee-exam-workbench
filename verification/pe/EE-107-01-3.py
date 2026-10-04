"""EE-107-01-3 independent check: full nodal solve (no Delta-Y shortcut) of the bridge network.

Givens (official crop): source 120/0 V, + terminal to node a (I0 flows into a), - terminal to node d.
Branches: a-b -j4 (I1 a->b), a-c 63.2+j2.4 (I2 a->c), b-c 10 (I3 b->c), b-d 20+j60 (I4 b->d),
c-d -j20 (I5 c->d).  V1 = Vb - Vd, V2 = Vc - Vd.
"""
import numpy as np

Zab, Zac, Zbc, Zbd, Zcd = -4j, 63.2 + 2.4j, 10, 20 + 60j, -20j
Va = 120.0
Y = np.array([[1/Zab + 1/Zbc + 1/Zbd, -1/Zbc],
              [-1/Zbc, 1/Zac + 1/Zbc + 1/Zcd]], dtype=complex)
rhs = np.array([Va / Zab, Va / Zac], dtype=complex)
Vb, Vc = np.linalg.solve(Y, rhs)
I1, I2, I3 = (Va - Vb) / Zab, (Va - Vc) / Zac, (Vb - Vc) / Zbc
I4, I5 = Vb / Zbd, Vc / Zcd
I0 = I1 + I2
def close(x, y): return abs(x - y) < 1e-6
assert close(Vb, 109.3333333333 + 8j) and close(Vc, 96 - 34.6666666667j)
assert close(I1, 2 + 8j/3) and close(I2, 0.4 + 0.53333333333j) and close(I3, 4/3 + 4.2666666667j)
assert close(I0, 2.4 + 3.2j)
assert close(I1 - I3 - I4, 0) and close(I2 + I3 - I5, 0)

# independent route requested by the problem: Delta(a,b,c) -> Y, then series/parallel
Zs = Zab + Zac + Zbc
Zan, Zbn, Zcn = Zab * Zac / Zs, Zab * Zbc / Zs, Zac * Zbc / Zs
Zleft, Zright = Zbn + Zbd, Zcn + Zcd
Ztot = Zan + Zleft * Zright / (Zleft + Zright)
I0_y = Va / Ztot
Vn = Va - I0_y * Zan
V1_y = Vn * Zbd / Zleft
V2_y = Vn * Zcd / Zright
assert close(I0_y, I0) and close(V1_y, Vb) and close(V2_y, Vc)
print("PASS EE-107-01-3")
