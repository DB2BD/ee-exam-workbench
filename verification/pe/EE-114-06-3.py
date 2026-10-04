"""EE-114-06-3 (conditional): cogeneration fault on the 69 kV side, 100 MVA base.

Branches: generator MVA = MW (pf 1.0) and MVA = MW/0.8.
Method: nodal solution with internal EMFs set so the pre-fault HV voltage is 65/69 pu.
"""
import numpy as np

Sb = 100e6
Ib22 = Sb / (np.sqrt(3) * 22e3)
VF = 65 / 69
for pf, (Itot, I1, I2) in ((1.0, (2.2837, 3745.7, 2247.4)), (0.8, (2.6915, 4414.6, 2648.8))):
    X1 = 0.25 * 100 / (50 / pf)
    X2 = 0.25 * 100 / (30 / pf)
    XT = 0.10
    # Nodal: generator bus g, fault at HV bus (V=0). E1=E2=VF (no load current).
    Y = np.array([[1/(1j*X1) + 1/(1j*X2) + 1/(1j*XT)]])
    Iinj = np.array([VF/(1j*X1) + VF/(1j*X2)])
    Vg = np.linalg.solve(Y, Iinj)[0]
    i1 = (VF - Vg) / (1j*X1); i2 = (VF - Vg) / (1j*X2); it = Vg / (1j*XT)
    assert abs(i1 + i2 - it) < 1e-12
    assert abs(abs(it) - Itot) / Itot < 0.005
    assert abs(abs(i1) * Ib22 - I1) / I1 < 0.005
    assert abs(abs(i2) * Ib22 - I2) / I2 < 0.005
print("PASS EE-114-06-3")
