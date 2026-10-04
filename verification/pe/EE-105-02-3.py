"""EE-105-02-3 independent check: adjustable diode limiter (ideal op-amp, Vd = 0.7 V).

Givens: R1=15k, RF=60k, R2=4k, R3=1k, R4=5k, R5=1k, VA=15, -VB=-15, VD=0.7, vS=5 V.
Topology (crop): inverting node n (virtual ground, vp=0); D1 anode n -> cathode Vx, Vx between
R2 (to +VA) and R3 (to vo); D2 anode Vy -> cathode n, Vy between R5 (to vo) and R4 (to -VB).
Method: enumerate the four ideal-diode states, solve each linear system, keep the consistent one.
"""
import itertools
import numpy as np

R1, RF, R2, R3, R4, R5 = 15e3, 60e3, 4e3, 1e3, 5e3, 1e3
VA, VB, VD = 15.0, 15.0, 0.7


def solve(vs):
    for d1, d2 in itertools.product([0, 1], repeat=2):
        # unknowns: vo, vx, vy, i1 (n->Vx through D1), i2 (Vy->n through D2)
        A = np.zeros((5, 5)); b = np.zeros(5)
        # node n: vs/R1 + vo/RF + i2 - i1 = 0
        A[0] = [1 / RF, 0, 0, -1, 1]; b[0] = -vs / R1
        # node Vx: (VA-vx)/R2 + (vo-vx)/R3 + i1 = 0
        A[1] = [1 / R3, -(1 / R2 + 1 / R3), 0, 1, 0]; b[1] = -VA / R2
        # node Vy: (-VB-vy)/R4 + (vo-vy)/R5 - i2 = 0
        A[2] = [1 / R5, 0, -(1 / R4 + 1 / R5), 0, -1]; b[2] = VB / R4
        if d1: A[3] = [0, 1, 0, 0, 0]; b[3] = -VD
        else:  A[3] = [0, 0, 0, 1, 0]; b[3] = 0
        if d2: A[4] = [0, 0, 1, 0, 0]; b[4] = VD
        else:  A[4] = [0, 0, 0, 0, 1]; b[4] = 0
        vo, vx, vy, i1, i2 = np.linalg.solve(A, b)
        ok1 = (i1 >= -1e-12) if d1 else (0 - vx < VD + 1e-12)
        ok2 = (i2 >= -1e-12) if d2 else (vy - 0 < VD + 1e-12)
        if ok1 and ok2:
            return vo, d1, d2
    raise RuntimeError("no consistent state")


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


def knee(lo, hi, state_lo):
    """bisect the input voltage where the diode pattern leaves state_lo."""
    for _ in range(80):
        m = 0.5 * (lo + hi)
        if solve(m)[1:] == state_lo:
            lo = m
        else:
            hi = m
    return lo


vs_min = knee(0.0, -3.0, (0, 0))   # D2 turns on (positive limiting knee)
vs_max = knee(0.0, 3.0, (0, 0))    # D1 turns on (negative limiting knee)
vo_max, vo_min = solve(vs_min)[0], solve(vs_max)[0]
assert close(vo_max, 3.84) and close(vo_min, -4.625)
assert close(vs_min, -0.96) and close(vs_max, 1.15625)
assert solve(vs_min - 0.01)[1:] == (0, 1) and solve(vs_max + 0.01)[1:] == (1, 0)
assert close(solve(0.5)[0], -2.0)  # linear region: -RF/R1 = -4
# beyond the knee the output keeps moving with slope -(RF || R3)/R1 (RF stays in the loop)
slope = -(RF * R3 / (RF + R3)) / R1
v5 = solve(5.0)[0]
assert close(slope, -0.06557, 0.001)
assert close(v5, vo_min + slope * (5.0 - vs_max))
assert close(v5, -4.87705, 0.001)
assert close(solve(-2.0)[0], vo_max + (-RF * R5 / (RF + R5) / R1) * (-2.0 - vs_min))
print(f"vo_max={vo_max:.4f} vo_min={vo_min:.4f} vS_min={vs_min:.4f} vS_max={vs_max:.5f} vo(5V)={v5:.5f} slope={slope:.5f}")
print("PASS EE-105-02-3")
