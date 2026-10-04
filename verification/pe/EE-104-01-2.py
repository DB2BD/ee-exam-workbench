"""EE-104-01-2: w = 4000 rad/s; Zab real => find k.  L1=12.5 mH, L2=8 mH; secondary loop: 5 ohm + 12.5 uF + L2."""
import numpy as np
w = 4000.0
L1, L2, C = 12.5e-3, 8e-3, 12.5e-6
Z22 = 5 + 1j * w * L2 + 1 / (1j * w * C)
# Zab = 20 + jwL1 + (wM)^2 / Z22  (sign of M drops out). Solve Im = 0 for (wM)^2
wM2 = -(w * L1) / (1 / Z22).imag
M = np.sqrt(wM2) / w
k = M / np.sqrt(L1 * L2)
assert abs(k - 0.6634) / 0.6634 < 5e-3, k
# full two-mesh check with both coupling signs
for sgn in (1, -1):
    Z = np.array([[20 + 1j * w * L1, sgn * 1j * w * M], [sgn * 1j * w * M, Z22]])
    Zab = 1 / np.linalg.inv(Z)[0, 0]
    assert abs(Zab.imag) < 1e-6 * abs(Zab), Zab
print("PASS EE-104-01-2")
