"""EE-105-02-1 independent check: amplifier with C1, C2, Ci, Co and bridging C (official crop).

Givens: gm=40 mA/V, Rs=2k, Ri=8k, Ro=15k, RL=10k, Ci=5 pF, Co=1 pF, C1=0.01 uF,
C2=0.04 uF, C=3.32 pF.  Topology from the crop: Rs-C1 to amplifier input node x (Ri, Ci to
ground), current source gm*vx at output node y (Ro, Co to ground), C between x and y,
C2 from y to RL.  Method: full MNA model; SCTC / OCTC resistances are measured by test
sources, the exact -3 dB points of the same model are used as a cross-check.
"""
import numpy as np

gm, Rs, Ri, Ro, RL = 40e-3, 2e3, 8e3, 15e3, 10e3
Ci, Co, C1, C2, C = 5e-12, 1e-12, 0.01e-6, 0.04e-6, 3.32e-12


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


def vo_over_vs(f, caps=True):
    s = 2j * np.pi * f
    sC1, sC2 = (s * C1, s * C2) if caps else (1e9, 1e9)
    sCi, sCo, sC = (s * Ci, s * Co, s * C) if caps else (0, 0, 0)
    # unknowns a, x, y, o ; vs = 1
    A = np.array([
        [1 / Rs + sC1, -sC1, 0, 0],
        [-sC1, sC1 + 1 / Ri + sCi + sC, -sC, 0],
        [0, gm - sC, 1 / Ro + sCo + sC + sC2, -sC2],
        [0, 0, -sC2, sC2 + 1 / RL],
    ], dtype=complex)
    b = np.array([1 / Rs, 0, 0, 0], dtype=complex)
    return np.linalg.solve(A, b)[3]


def thevenin(G, p, q=None):
    """Resistance between node p and node q (ground if None) from a 1 A test source."""
    I = np.zeros(G.shape[0]); I[p] += 1
    if q is not None:
        I[q] -= 1
    v = np.linalg.solve(G, I)
    return v[p] - (v[q] if q is not None else 0)


big = 1e4
# nodes: 0=a(after Rs), 1=x, 2=y, 3=o
def dc_matrix(short_c1, short_c2):
    G = np.zeros((4, 4))
    def add(i, j, g):
        G[i, i] += g
        if j is not None:
            G[j, j] += g; G[i, j] -= g; G[j, i] -= g
    add(0, None, 1 / Rs); add(1, None, 1 / Ri); add(2, None, 1 / Ro); add(3, None, 1 / RL)
    if short_c1: add(0, 1, big)
    if short_c2: add(2, 3, big)
    G[2, 1] += gm  # dependent source gm*vx drawn out of node y
    return G


# OCTC for the high-frequency side: C1, C2 shorted, internal caps open
G = dc_matrix(True, True)
# resistances seen by Ci, Co, C when the dependent source is active
R_i = thevenin(G, 1)
R_o = thevenin(G, 2)
R_c = thevenin(G, 1, 2)
tau = R_i * Ci + R_o * Co + R_c * C
fH = 1 / (2 * np.pi * tau)

# SCTC for the low-frequency side: one coupling cap at a time, the other shorted
R_c1 = thevenin(dc_matrix(False, True), 0, 1)
R_c2 = thevenin(dc_matrix(True, False), 2, 3)
fL = 1 / (2 * np.pi * R_c1 * C1) + 1 / (2 * np.pi * R_c2 * C2)

Apb = vo_over_vs(1e5 / 10, caps=False).real
mid = 192.0
assert close(Apb, -192)
assert close(R_i, 1.6e3) and close(R_o, 6e3) and close(R_c, 391.6e3)
assert close(tau, 1314.1e-9) and close(fH, 121.1e3)
assert close(R_c1, 10e3) and close(R_c2, 25e3) and close(fL, 1750.7)


def f3db(lo, hi, rising):
    ref = mid
    for _ in range(200):
        m = np.sqrt(lo * hi)
        v = abs(vo_over_vs(m)) / ref
        if (v < 1 / np.sqrt(2)) == rising:
            lo = m
        else:
            hi = m
    return m

fH_full = f3db(5e4, 5e6, False)
fL_full = f3db(10, 5e4, True)
Ci_, Co_, C_ = Ci, Co, C
Ci = Co = C = 0  # low-frequency side alone: internal capacitances open
fL_exact = f3db(10, 5e4, True)
Ci, Co, C = Ci_, Co_, C_
assert close(fL_exact, 1607, 0.01)  # exact two-pole value of the coupling network
assert abs(fL_full - fL) / fL < 0.05 and abs(fH_full - fH) / fH < 0.10  # estimates vs full model
print(f"Apb={Apb:.2f} fL(SCTC)={fL:.1f} Hz fL(2-pole)={fL_exact:.1f} fH(OCTC)={fH:.0f} Hz fH(full model)={fH_full:.0f}")
print("PASS EE-105-02-1")
