"""EE-112-04-2: 5000 kVA, 230/13.8 kV, R = 1 %, X = 5 %; LV open-circuit test
13.8 kV, 21.1 A, 90.8 kW; load 4000 kW, 0.8 lag at 13.8 kV on the LV side."""
import numpy as np

S, V = 5e6, 13.8e3
Zb = V**2 / S
Req, Xeq = 0.01 * Zb, 0.05 * Zb
Rc = V**2 / 90.8e3
Q = np.sqrt((V * 21.1) ** 2 - 90.8e3**2)
Xm = V**2 / Q
for val, ref in ((Req, 0.38088), (Xeq, 1.9044), (Rc, 2097.4), (Xm, 688.35)):
    assert abs(val - ref) / ref <= 0.005
I = 4000e3 / (0.8 * V) * np.exp(-1j * np.arccos(0.8))
V1 = V + I * (Req + 1j * Xeq)
VR = (abs(V1) - V) / V
assert abs(VR - 0.03856) / 0.03856 <= 0.005
# independent: per-unit exact formula with I = 1 pu at 0.8 lag
Vpu = abs(1 + (0.8 - 0.6j) * (0.01 + 0.05j))
assert abs((Vpu - 1) - VR) < 1e-12
# admittance check of the OC branch: |1/Rc + 1/(jXm)| * V = 21.1 A
assert abs(abs(1 / Rc + 1 / (1j * Xm)) * V - 21.1) < 1e-9
print(f"Req={Req:.5f} Xeq={Xeq:.4f} Rc={Rc:.2f} Xm={Xm:.2f} VR={VR*100:.3f} %")
print("PASS EE-112-04-2")
