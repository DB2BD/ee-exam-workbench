"""EE-109-05-2: bundled 345 kV line, nominal-pi real power transfer.

Givens (official crop): 2-conductor bundle, d = 40 cm, flat spacing 10 m,
diameter 3.195 cm, GMR 1.268 cm, transposed, R and G neglected, 200 km,
60 Hz, VS = 345/30 deg kV, VR = 327.75/0 deg kV (line values).
"""
import numpy as np

eps0 = 8.854e-12
GMD = (10 * 10 * 20) ** (1 / 3)
DsL = np.sqrt(0.01268 * 0.40)
DsC = np.sqrt(0.03195 / 2 * 0.40)
L = 2e-7 * np.log(GMD / DsL)
C = 2 * np.pi * eps0 / np.log(GMD / DsC)
w, l = 2 * np.pi * 60, 200e3
X = w * L * l
Y = w * C * l
assert abs(GMD - 12.599) < 1e-3
assert abs(L - 1.0351e-6) / 1.0351e-6 < 0.005
assert abs(C - 1.0994e-11) / 1.0994e-11 < 0.005
assert abs(X - 78.05) / 78.05 < 0.005
P = 345 * 327.75 * np.sin(np.radians(30)) / X  # MW, 3-phase with line kV
assert abs(P - 724.4) / 724.4 < 0.005

# Method 2: per-phase complex power through the nominal pi (shunt halves draw only Q).
VS = 345e3 / np.sqrt(3) * np.exp(1j * np.radians(30))
VR = 327.75e3 / np.sqrt(3)
Iseries = (VS - VR) / (1j * X)
IR = Iseries - 1j * Y / 2 * VR
SR = 3 * VR * np.conj(IR)
IS = Iseries + 1j * Y / 2 * VS
SS = 3 * VS * np.conj(IS)
assert abs(SR.real / 1e6 - P) < 1e-6 and abs(SS.real / 1e6 - P) < 1e-6
print("PASS EE-109-05-2")
