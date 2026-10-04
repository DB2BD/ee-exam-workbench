"""EE-110-05-2: power-flow equations and one fast-decoupled iteration.

Givens (official crop): Ybus diag -j19.98, off-diag j10; bus1 slack 1/0;
bus2 PV |V2|=1.05, PG2=0.6; bus3 PQ load 3+j1; flat start V3=1, th2=th3=0.
Main convention: B' = B'' = -Im(Ybus) of the non-slack buses, dP/|V| = B' dth,
dQ/|V| = B'' d|V|.
"""
import numpy as np

Y = np.array([[-19.98j, 10j, 10j], [10j, -19.98j, 10j], [10j, 10j, -19.98j]])
B = Y.imag
V = np.array([1.0, 1.05, 1.0]); th = np.zeros(3)
Vc = V * np.exp(1j * th)
S = Vc * np.conj(Y @ Vc)
P, Q = S.real, S.imag
assert abs(P[1]) < 1e-12 and abs(P[2]) < 1e-12
assert abs(Q[2] - (-0.52)) < 1e-9
dP = np.array([0.6 - P[1], -3.0 - P[2]])
dQ3 = -1.0 - Q[2]
assert abs(dQ3 - (-0.48)) < 1e-9
Bp = -B[1:, 1:]
dth = np.linalg.solve(Bp, dP / V[1:])
dV3 = dQ3 / V[2] / (-B[2, 2])
th3 = np.degrees(dth[1]); V3 = 1 + dV3
assert abs(dth[0] - (-0.062108)) < 1e-5
assert abs(dth[1] - (-0.181231)) < 1e-5
assert abs(th3 - (-10.384)) < 0.01
assert abs(V3 - 0.97598) < 1e-5

# Method 2: back-substitute into B' rows, then compare with one full Newton step
# from the same start (decoupling approximation: within 0.3 deg / 0.001 pu).
assert np.allclose(Bp @ dth, dP / V[1:], atol=1e-12)
def mism(x):
    t2, t3, v3 = x
    v = np.array([1.0, 1.05, v3]) * np.exp(1j * np.array([0, t2, t3]))
    s = v * np.conj(Y @ v)
    return np.array([0.6 - s[1].real, -3 - s[2].real, -1 - s[2].imag])
x = np.array([0.0, 0.0, 1.0]); h = 1e-7
J = np.column_stack([(mism(x + h * e) - mism(x)) / h for e in np.eye(3)])
dx = -np.linalg.solve(J, mism(x))
assert abs(np.degrees(dx[1] - dth[1])) < 0.3 and abs(dx[2] - dV3) < 1e-3
assert abs(np.degrees(dx[1]) - (-10.144)) < 0.01 and abs(1 + dx[2] - 0.97533) < 1e-4
# alternative conventions stay within 0.1 deg for theta3
alt = np.linalg.solve(np.array([[20, -10], [-10, 20.0]]), dP)
assert abs(np.degrees(alt[1]) - th3) < 0.1
print("PASS EE-110-05-2")
