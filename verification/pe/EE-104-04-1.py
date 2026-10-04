"""EE-104-04-1: Y-shaped core in a ring. Nodes C (centre), T (top), B (lower right), A (lower left).
Six branches (spokes C-T, C-B, C-A; arcs T-B, B-A, A-T), every reluctance R.
N1 on spoke C-T (phi1 from C to T, mmf F1); N2 on arc B-A (phi2 from B to A, mmf F2)."""
import sympy as sp

R, F1, F2 = sp.symbols("R F1 F2", positive=True)
UT, UB, UA = sp.symbols("U_T U_B U_A")
UC = 0
p_CT = (F1 + UC - UT) / R      # phi1, mmf rise along the reference direction
p_BA = (F2 + UB - UA) / R      # phi2
p_CB = (UC - UB) / R
p_CA = (UC - UA) / R
p_TB = (UT - UB) / R
p_TA = (UT - UA) / R
inT = p_CT - p_TB - p_TA        # net flux into node T
inB = p_CB + p_TB - p_BA        # into B (BA leaves B)
inA = p_CA + p_TA + p_BA        # into A
sol = sp.solve([inT, inB, inA], [UT, UB, UA], dict=True)[0]
phi1 = sp.simplify(p_CT.subs(sol))
phi2 = sp.simplify(p_BA.subs(sol))
assert sp.simplify(phi1 - F1 / (2 * R)) == 0
assert sp.simplify(phi2 - F2 / (2 * R)) == 0
# numeric cross-check by direct linear solve
import numpy as np
vals = {R: 1.0, F1: 3.0, F2: 5.0}
M = sp.Matrix([[sp.diff(e, u) for u in (UT, UB, UA)] for e in (inT, inB, inA)]).subs(vals)
b = -sp.Matrix([e.subs({UT: 0, UB: 0, UA: 0}).subs(vals) for e in (inT, inB, inA)])
U = np.linalg.solve(np.array(M.tolist(), dtype=float), np.array(b.tolist(), dtype=float).ravel())
assert abs(3.0 - U[0] - 1.5) < 1e-9 and abs(5.0 + U[1] - U[2] - 2.5) < 1e-9
print("PASS EE-104-04-1")
