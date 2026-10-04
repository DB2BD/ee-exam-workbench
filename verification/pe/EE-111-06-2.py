"""EE-111-06-2: synchronous motor full-voltage start, voltage dips (69 kV bus and 3.3 kV).

Stem givens: 69 kV bus S_sc = 500 MVA; transformer 69/3.3 kV, 5000 kVA, Z = 5 %;
motor 3300 V, 3000 kW, I_start = 5 I_rated, starting PF = 0, base 5000 kVA.
Rated kVA is not in the stem: the reference-book convention eta*pf = 0.85
(named constant below) is the main branch; the sensitivity table k = 0.80-1.00
mirrors 「條件與疑義」.
"""
import numpy as np

SB = 5.0
S_SC = 500.0
X_T = 0.05
P_MOTOR_MW = 3.0
START_MULT = 5.0
K_REF = 0.85            # reference-book rated kVA = 3000 kW / 0.85

def dips(k):
    xs = SB / S_SC
    xm = SB / (START_MULT * P_MOTOR_MW / k)
    # nodal solution with complex phasors: pure reactances (start PF = 0)
    i = 1.0 / (1j * (xs + X_T + xm))
    v69 = 1.0 - 1j * xs * i
    v33 = 1.0 - 1j * (xs + X_T) * i
    return (1 - abs(v33)) * 100, (1 - abs(v69)) * 100, xs, xm

d2, d69, xs, xm = dips(K_REF)
assert abs(xs - 0.01) < 1e-12
assert abs(xm - 0.283333) < 1e-6
assert abs(d2 - 17.48) / 17.48 < 0.005        # boxed 17.48 %
assert abs(d69 - 2.913) / 2.913 < 0.005       # boxed 2.913 %
# reference book rounds X_M = 0.283 -> 17.5 % / 2.92 %
assert round(0.06 / (0.06 + 0.283) * 100, 1) == 17.5 and round(0.01 / (0.06 + 0.283) * 100, 2) == 2.92
# independent check: voltage divider ratio  dV69/dV2 = Xs/(Xs+XT)
assert abs(d69 / d2 - xs / (xs + X_T)) < 1e-12
table = {k: dips(k)[:2] for k in (0.80, 0.85, 0.90, 1.00)}
expect = {0.80: (18.3673, 3.0612), 0.85: (17.4757, 2.9126), 0.90: (16.6667, 2.7778), 1.00: (15.2542, 2.5424)}
for k, (a, b) in expect.items():
    assert abs(table[k][0] - a) < 5e-5 and abs(table[k][1] - b) < 5e-5, (k, table[k])
print("PASS EE-111-06-2")
