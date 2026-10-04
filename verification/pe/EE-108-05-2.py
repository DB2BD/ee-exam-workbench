"""EE-108-05-2: fast decoupled load flow, two iterations.

Bus1 slack V1=1.02<0; bus2 PV |V2|=1.01, PG2=0.7; bus3 PQ load 0.9+j0.8.
y13=-j8, y23=-j12 (series admittances, pu).  Flat start: theta=0, |V3|=1.0.
Iteration k = P-theta half step (B') then Q-V half step (B'') with updated angles.
"""
import numpy as np

V1, V2 = 1.02, 1.01
Y = np.array([[-8j, 0, 8j], [0, -12j, 12j], [8j, 12j, -20j]])
Ps = np.array([np.nan, 0.7, -0.9])
Q3s = -0.8

Bp = -Y.imag[1:, 1:]      # buses 2,3 (angles)
Bpp = -Y.imag[2:, 2:]     # bus 3 (voltage magnitude)
assert np.allclose(Bp, [[12, -12], [-12, 20]]) and np.allclose(Bpp, [[20]])


def inj(V, th):
    Vc = V * np.exp(1j * th)
    S = Vc * np.conj(Y @ Vc)
    return S.real, S.imag


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


V = np.array([V1, V2, 1.0])
th = np.zeros(3)
hist = []
for k in range(2):
    P, Q = inj(V, th)
    dP_over_V = (Ps[1:] - P[1:]) / V[1:]
    dth = np.linalg.solve(Bp, dP_over_V)
    th[1:] += dth
    P, Q = inj(V, th)
    dQ_over_V = (Q3s - Q[2]) / V[2]
    dV = dQ_over_V / Bpp[0, 0]
    V[2] += dV
    hist.append((dP_over_V.copy(), dth.copy(), dQ_over_V, dV, th.copy(), V.copy()))
    print(f"it{k+1}: dP/V={dP_over_V}, dth(rad)={dth}, dQ/V={dQ_over_V:.6f}, dV={dV:.6f}, "
          f"th(deg)={np.degrees(th[1:])}, V3={V[2]:.5f}")

# iteration 1 hand values
close(hist[0][0][0], 0.7 / 1.01)
close(hist[0][0][1], -0.9)
close(hist[0][1][0], 0.031885, 1e-3)
close(hist[0][1][1], -0.025868, 1e-3)
close(hist[0][2], -0.54294, 1e-3)
close(hist[0][5][2], 0.97285, 1e-3)
# after iteration 2
close(np.degrees(hist[1][4][1]), 1.9526, 1e-3)
close(np.degrees(hist[1][4][2]), -1.4481, 1e-3)
close(hist[1][5][2], 0.97169, 1e-3)

# independent full Newton-Raphson converged solution
x = np.array([0.0, 0.0, 1.0])  # th2, th3, V3


def F(x):
    V = np.array([V1, V2, x[2]])
    th = np.array([0, x[0], x[1]])
    P, Q = inj(V, th)
    return np.array([P[1] - Ps[1], P[2] - Ps[2], Q[2] - Q3s])


for _ in range(30):
    f = F(x)
    J = np.zeros((3, 3))
    for j in range(3):
        h = 1e-7
        xp = x.copy(); xp[j] += h
        J[:, j] = (F(xp) - f) / h
    x = x - np.linalg.solve(J, f)
assert np.max(np.abs(F(x))) < 1e-9
close(np.degrees(x[0]), 1.9623, 1e-3)
close(np.degrees(x[1]), -1.4455, 1e-3)
close(x[2], 0.97163, 1e-3)
# FDLF after 2 iterations is within 0.5 % of the converged magnitude
close(hist[1][5][2], x[2], 5e-3)
# slack power balance: P1 = 0.9 - 0.7 (lossless)
Vf = np.array([V1, V2, x[2]]); tf = np.array([0, x[0], x[1]])
P, Q = inj(Vf, tf)
close(P[0], 0.2, 1e-6)
print("PASS EE-108-05-2")
