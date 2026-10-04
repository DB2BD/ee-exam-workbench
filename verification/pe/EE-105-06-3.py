"""EE-105-06-3: three-phase fault at the 480 V bus, Sb = 2000 kVA."""
import numpy as np

Sb, Vb = 2000.0, 480.0
Ib = Sb * 1e3 / (np.sqrt(3) * Vb)
Xsys = Sb / 200e3
X1 = Xsys + 0.06
X2 = 0.20 * Sb / 500
I1 = Ib / X1 / 1e3
Xeq = X1 * X2 / (X1 + X2)
I2 = Ib / Xeq / 1e3
assert abs(I1 - 34.366) / 34.366 < 0.005
assert abs(I2 - 37.373) / 37.373 < 0.005
assert abs(Xeq - 0.0643678) / 0.0643678 < 0.005
# independent: sum of branch currents
assert abs(I2 - (Ib / X1 + Ib / X2) / 1e3) < 1e-9
print("PASS EE-105-06-3")
