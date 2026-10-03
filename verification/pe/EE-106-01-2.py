"""EE-106-01-2 independent check: dv_C3/dt of the 3x3 grid circuit.

Givens (official crop): centre node O joins R5, R6, R7, R8, L2, L3, C1(bottom plate), C3(top plate).
Outer ring: TL -R1- TM -R2- TR ; TL -L1- ML ; TR -C2- MR ; ML -Vs1(+top)- BL ; MR -Vs2(+top)- BR ;
BL -R3- BM -R4- BR.  C1: TM-O, C3: O-BM, R5: TL-O, R6: TR-O, R7: BL-O, R8: O-BR, L2: ML-O, L3: O-MR.
State sign conventions (the crop gives none): v_C1 = V_TM - V_O, v_C2 = V_TR - V_MR, v_C3 = V_O - V_BM,
i_L1 flows TL->ML, i_L2 flows ML->O, i_L3 flows O->MR.

Check = full nodal/MNA solve with capacitors as voltage sources and inductors as current sources
versus the closed-form state equation, for random element values.
"""
import numpy as np

rng = np.random.default_rng(106)

def formula(R, C3, v1, v2, v3, i1, i2, i3, Vs2):
    R2, R3, R4, R6, R7, R8 = (R[k] for k in ("R2", "R3", "R4", "R6", "R7", "R8"))
    D = R2 * R4 * R6 + R2 * R4 * R8 + R2 * R6 * R8 + R4 * R6 * R8
    E = R2 * R6 + R2 * R8 + R6 * R8
    return (
        -R6 * R8 / D * v1
        + R8 * (R2 + R6) / D * (v2 + Vs2)
        - (1 / (R3 + R7) + E / D) * v3
        - R7 / (R3 + R7) * (i1 - i2)
        - R2 * R6 * R8 / D * i3
    ) / C3

def mna(R, v1, v2, v3, i1, i2, i3, Vs1, Vs2):
    names = ["TL", "TM", "TR", "ML", "MR", "BL", "BM", "BR"]   # O is ground
    ix = {n: k for k, n in enumerate(names)}
    nv = 5                                                      # C1, C2, C3, Vs1, Vs2 branch currents
    N = len(names) + nv
    A = np.zeros((N, N)); b = np.zeros(N)
    def res(p, q, r):
        g = 1 / r
        for node in (p, q):
            if node is not None:
                A[ix[node], ix[node]] += g
        if p is not None and q is not None:
            A[ix[p], ix[q]] -= g; A[ix[q], ix[p]] -= g
    res("TL", "TM", R["R1"]); res("TM", "TR", R["R2"]); res("BL", "BM", R["R3"]); res("BM", "BR", R["R4"])
    res("TL", None, R["R5"]); res("TR", None, R["R6"]); res("BL", None, R["R7"]); res("BR", None, R["R8"])
    def isrc(frm, to, val):          # current val flows frm -> to through the source
        if frm is not None: b[ix[frm]] -= val
        if to is not None: b[ix[to]] += val
    isrc("TL", "ML", i1); isrc("ML", None, i2); isrc(None, "MR", i3)
    # voltage sources: V(p) - V(q) = value, branch current k flows p -> q inside the source
    def vsrc(k, p, q, val):
        row = len(names) + k
        if p is not None: A[row, ix[p]] += 1; A[ix[p], row] += 1
        if q is not None: A[row, ix[q]] -= 1; A[ix[q], row] -= 1
        b[row] = val
    vsrc(0, "TM", None, v1)          # C1
    vsrc(1, "TR", "MR", v2)          # C2
    vsrc(2, None, "BM", v3)          # C3: V_O - V_BM = v3, current O -> BM = C3 dv3/dt
    vsrc(3, "ML", "BL", Vs1)
    vsrc(4, "MR", "BR", Vs2)
    x = np.linalg.solve(A, b)
    return x[len(names) + 2]         # i_C3 flowing O -> BM through C3

for _ in range(50):
    R = {f"R{k}": rng.uniform(0.5, 9) for k in range(1, 9)}
    C3 = rng.uniform(0.5, 3)
    st = rng.uniform(-5, 5, 8)
    v1, v2, v3, i1, i2, i3, Vs1, Vs2 = st
    ref = mna(R, v1, v2, v3, i1, i2, i3, Vs1, Vs2) / C3
    got = formula(R, C3, v1, v2, v3, i1, i2, i3, Vs2)
    assert abs(ref - got) <= 1e-9 * max(1, abs(ref)), (ref, got)
    # R1, R5 and Vs1 must not change the answer
    R_alt = dict(R); R_alt["R1"] *= 3; R_alt["R5"] *= 0.4
    assert abs(mna(R_alt, v1, v2, v3, i1, i2, i3, Vs1 + 7, Vs2) / C3 - ref) < 1e-9
print("PASS EE-106-01-2")
