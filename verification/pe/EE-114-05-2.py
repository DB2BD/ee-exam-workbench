"""EE-114-05-2 independent check: two-bus load flow, Q-limit, one NR step.

Givens (official crop): V1 = 1∠0 slack, y12 = -j10 pu, 100 MVA base,
bus 2: Pg = 100 MW, load 250 MW + 100 Mvar; (二) Qg2 max = 100 Mvar,
flat start delta2 = 0, |V2| = 1.
"""
import numpy as np

Y = np.array([[-10j, 10j], [10j, -10j]])
V1 = 1.0
P2_spec = (100 - 250) / 100


def injections(V2, d2):
    V = np.array([V1, V2 * np.exp(1j * d2)])
    S = V * np.conj(Y @ V)
    return S[1].real, S[1].imag


# (一) PV bus |V2| = 1: solve P2(delta) = -1.5 by bisection on the low-angle branch.
lo, hi = -np.pi / 2, 0.0
for _ in range(200):
    mid = (lo + hi) / 2
    if injections(1.0, mid)[0] > P2_spec:
        hi = mid
    else:
        lo = mid
d2 = (lo + hi) / 2
Q2_net = injections(1.0, d2)[1]
Qg2 = (Q2_net + 1.0) * 100  # add back the 100 Mvar load
assert abs(np.degrees(d2) - (-8.627)) / 8.627 <= 0.005
assert abs(Qg2 - 111.31) / 111.31 <= 0.005
assert Qg2 > 100

# Line-flow cross-check: power sent from bus 1 equals 150 MW.
V2c = np.exp(1j * d2)
S12 = V1 * np.conj(-10j * (V1 - V2c)) * 100
assert abs(S12.real - 150) < 1e-6

# (二) PQ bus: Qg2 fixed at 100 -> Q2_spec = 0. One NR step with numerical Jacobian.
Q2_spec = (100 - 100) / 100
x = np.array([0.0, 1.0])  # delta2, |V2|
f = lambda x: np.array(injections(x[1], x[0]))
mismatch = np.array([P2_spec, Q2_spec]) - f(x)
h = 1e-7
J = np.column_stack([(f(x + h * e) - f(x - h * e)) / (2 * h) for e in np.eye(2)])
x1 = x + np.linalg.solve(J, mismatch)
assert abs(x1[0] - (-0.15)) / 0.15 <= 0.005
assert abs(np.degrees(x1[0]) - (-8.594)) / 8.594 <= 0.005
assert abs(x1[1] - 1.0) <= 0.005
print("PASS EE-114-05-2")
