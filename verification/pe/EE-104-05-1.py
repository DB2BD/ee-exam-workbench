"""EE-104-05-1: sequence-network SLG fault at the system bus, ES closed / open.

Base 500 MVA; 18 kV gen side, 345 kV bus side.
Gen X1=X2=X''d=0.25, X0=0.12 ; MT X1=X2=0.15, X0=0.10 (Delta gen side / grounded-Y bus side, ES grounds the Y neutral)
System source X1=X2=X0=0.025 (Yg).  AT/ST loads ignored for the fault (crop).  Prefault bus voltage 1.0 pu (345 kV).
Voltage part: bus 360 MW + j270 Mvar delivered to the system source; ST load B (50 MVA, 0.8 lag, constant Z)
hangs on the same bus, load A hangs on the generator terminal.
"""
import math

import numpy as np


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


Sb, Vb_hv, Vb_lv = 500.0, 345.0, 18.0
Ib_hv = Sb / (math.sqrt(3) * Vb_hv)  # kA

# ---- (1) generator terminal voltage ----
Ssys = (360 + 270j) / Sb
Isys = np.conj(Ssys) / 1.0
# load B: rated 50 MVA, pf 0.8 lag at rated voltage -> Z = (0.8+j0.6) pu on 50 MVA; ST X = 0.10 on 50 MVA
zB = (0.8 + 0.6j + 0.1j) * Sb / 50.0
close(zB.real, 8.0, 1e-9); close(zB.imag, 7.0, 1e-9)
IB = 1.0 / zB
Imt = Isys + IB
Vt = 1.0 + 0.15j * Imt
Vt_kV = abs(Vt) * Vb_lv
close(abs(Vt), 1.09677, 1e-3)
close(Vt_kV, 19.742, 1e-3)
# alternative: ignore load B
Vt_noB = abs(1.0 + 0.15j * Isys) * Vb_lv
close(Vt_noB, 19.555, 1e-3)

# ---- (2) SLG fault ----
par = lambda a, b: a * b / (a + b)
Z1 = par(0.025, 0.25 + 0.15)
Z2 = Z1
close(Z1, 0.0235294, 1e-4)
res = {}
for name, Z0 in (("ES on", par(0.025, 0.10)), ("ES off", 0.025)):
    If = 3 * 1.0 / (Z1 + Z2 + Z0)
    I0 = If / 3
    V0 = I0 * Z0
    res[name] = (If, If * Ib_hv, V0 * Vb_hv / math.sqrt(3))
close(res["ES on"][1], 37.43, 2e-3)
close(res["ES off"][1], 34.83, 2e-3)
close(res["ES on"][2], 59.41, 2e-3)
close(res["ES off"][2], 69.10, 2e-3)

# cross-check by phase-domain sequence transform (ES on)
Z0 = par(0.025, 0.10)
a = np.exp(2j * math.pi / 3)
A = np.array([[1, 1, 1], [1, a**2, a], [1, a, a**2]])
Z012 = np.diag([Z0, Z1, Z2])
Iseq = np.array([1, 1, 1]) * (1.0 / (Z0 + Z1 + Z2) / 1j)
Iabc = A @ Iseq
assert abs(Iabc[1]) < 1e-9 and abs(Iabc[2]) < 1e-9
close(abs(Iabc[0]) * Ib_hv, res["ES on"][1], 1e-9)
V0_seq = -(Z0 * 1j) * Iseq[0]
close(abs(V0_seq) * Vb_hv / math.sqrt(3), res["ES on"][2], 1e-9)

# MT 345 kV winding current (alternative reading), ES on / off
for name, Z0_, zshare in (("on", par(0.025, 0.10), 0.025 / 0.125), ("off", 0.025, 0.0)):
    I1 = 1.0 / (2 * Z1 + Z0_)
    Imt_a = 2 * I1 * 0.025 / 0.425 + I1 * zshare
    print("MT winding a-phase current ES", name, Imt_a * Ib_hv)

print("Vt", Vt_kV, "alt", Vt_noB, res)
print("PASS EE-104-05-1")
