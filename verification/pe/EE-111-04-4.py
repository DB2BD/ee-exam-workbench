"""EE-111-04-4: 11 kV Y, 25 MVA, Xs = 4.5 ohm cylindrical generator, If = 200 A at
rated V and rated current, pf 0.85 lag.  (2)(3) use the linearized (saturated-Xs) OCC.
"""
import numpy as np

VL, S, Xs, If = 11e3, 25e6, 4.5, 200.0
V = VL / np.sqrt(3)
I = S / (np.sqrt(3) * VL) * np.exp(-1j * np.arccos(0.85))
E = V + 1j * Xs * I
VR = (abs(E) - V) / V * 100
assert abs(VR - 68.64) / 68.64 <= 0.005
# reference-book E = 10710.78 V gives 68.65 %, not 68.87 %
assert abs((10710.78 - V) / V * 100 - 68.65) < 0.01
# (2) linear OCC through the operating point: E proportional to If
If_occ = If * V / abs(E)
assert abs(If_occ - 118.595) / 118.595 <= 0.005
# (3) SCR = If_occ / If_scc = 1 / Xs_pu
Zb = VL**2 / S
Xpu = Xs / Zb
If_scc = If_occ * Xpu
assert abs(If_scc - 110.264) / 110.264 <= 0.005
# independent check of (3): short circuit, E_sc = Xs * I_rated (per phase), same E/If slope
E_sc = Xs * abs(I)
If_scc_direct = If * E_sc / abs(E)
assert abs(If_scc_direct - If_scc) < 1e-9
print(f"|E|={abs(E):.3f} VR={VR:.4f}% If_occ={If_occ:.3f} Xpu={Xpu:.7f} If_scc={If_scc:.3f}")
print("PASS EE-111-04-4")
