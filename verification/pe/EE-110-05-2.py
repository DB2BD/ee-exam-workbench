"""EE-110-05-2: power-flow equations and one fast-decoupled iteration.

Givens (official crop): Ybus diag -j19.98, off-diag j10; bus1 slack 1/0;
bus2 PV |V2|=1.05, PG2=0.6; bus3 PQ load 3+j1; flat start V3=1, th2=th3=0.
Main convention (user-approved 2026-10-18): standard sequential FDLF
(Stott-Alsac): B' = B'' = -Im(Ybus) of the non-slack buses; first solve
dP/|V| = B' dth and update the angles, then compute Q3 at the UPDATED angles
and solve dQ/|V| = B'' d|V|.  -> theta3 = -10.38 deg, |V3| = 0.96 pu.
The simultaneous variant (dQ at the flat start, Saadat) gives |V3| = 0.98.
"""
import numpy as np

Y = np.array([[-19.98j, 10j, 10j], [10j, -19.98j, 10j], [10j, 10j, -19.98j]])
B = Y.imag


def inject(Vm, th):
    Vc = Vm * np.exp(1j * th)
    return Vc * np.conj(Y @ Vc)


Vm = np.array([1.0, 1.05, 1.0]); th = np.zeros(3)
S = inject(Vm, th)
assert abs(S[1].real) < 1e-12 and abs(S[2].real) < 1e-12
dP = np.array([0.6 - S[1].real, -3.0 - S[2].real])
Bp = -B[1:, 1:]
dth = np.linalg.solve(Bp, dP / Vm[1:])
assert abs(dth[0] - (-0.0621084)) < 1e-6
assert abs(dth[1] - (-0.181235)) < 1e-6
th1 = np.array([0.0, dth[0], dth[1]])
th3 = np.degrees(th1[2])
assert abs(th3 - (-10.384)) < 0.01

# Q-V half step at the updated angles (sequential FDLF)
S1 = inject(Vm, th1)
Q3 = S1[2].imag
assert abs(Q3 - (-0.28180)) < 1e-4
dQ3 = -1.0 - Q3
dV3 = dQ3 / Vm[2] / (-B[2, 2])
V3 = 1 + dV3
assert abs(V3 - 0.96405) < 1e-4
assert round(V3, 2) == 0.96

# Method 2: Q3 from the closed-form expansion used in the note
Q3_formula = -(1 * 1 * 10 * np.cos(th1[2])) - 1 * 1.05 * 10 * np.cos(th1[2] - th1[1]) + 19.98
assert abs(Q3_formula - Q3) < 1e-12
# back-substitute into B' rows
assert np.allclose(Bp @ dth, dP / Vm[1:], atol=1e-12)

# Simultaneous variant (dQ at the flat start) -> |V3| = 0.98 (documented alternative)
dQ3_flat = -1.0 - S[2].imag
assert abs(dQ3_flat - (-0.48)) < 1e-9
assert round(1 + dQ3_flat / 19.98, 2) == 0.98

# One full Newton step from the same start: same order of correction
def mism(x):
    t2, t3, v3 = x
    s = inject(np.array([1.0, 1.05, v3]), np.array([0, t2, t3]))
    return np.array([0.6 - s[1].real, -3 - s[2].real, -1 - s[2].imag])
x = np.array([0.0, 0.0, 1.0]); h = 1e-7
J = np.column_stack([(mism(x + h * e) - mism(x)) / h for e in np.eye(3)])
dx = -np.linalg.solve(J, mism(x))
assert abs(np.degrees(dx[1]) - (-10.144)) < 0.01 and abs(1 + dx[2] - 0.97533) < 1e-4
# XB variant of B' (shunt omitted, diagonal 20): theta3 within 0.1 deg
alt = np.linalg.solve(np.array([[20, -10], [-10, 20.0]]), dP)
assert abs(np.degrees(alt[1]) - th3) < 0.1
print("PASS EE-110-05-2")
