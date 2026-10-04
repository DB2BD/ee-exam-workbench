"""EE-104-06-5: 5th-harmonic network, 380 V bus, base case 500 kW = AC-side kW, pf1 = 1 (assumption)."""
import numpy as np

Sb, VLL = 2.0, 380.0                       # MVA, V
Xs = Sb / 250
XT = 0.061
h = 5
Z_up = 1j * h * (Xs + XT)
XC = {"A": Sb / 0.4, "B": Sb / 0.2}        # fundamental capacitor reactance, pu
Z = {k: 1j * (h * 0.06 * x - x / h) for k, x in XC.items()}
assert abs(Z["A"] - 0.5j) < 1e-12 and abs(Z["B"] - 1.0j) < 1e-12
Zbus = 1 / (1 / Z_up + 1 / Z["A"] + 1 / Z["B"])
Ib = Sb * 1e6 / (np.sqrt(3) * VLL)
I1 = 500e3 / (np.sqrt(3) * VLL)
I5 = 0.2 * I1
V5 = abs(Zbus) * I5 / Ib * VLL
Isrc, IA, IB = (abs(V5 / VLL * Ib / z) for z in (Z_up, Z["A"], Z["B"]))
for got, ref in zip((V5, Isrc, IA, IB), (3.2211, 74.6606, 51.5158, 25.7579)):
    assert abs(got - ref) / ref < 0.005
assert abs(Isrc + IA + IB - I5) / I5 < 1e-9   # all branches inductive at h=5 -> same phase
# scaling branches (pf1 = 0.95; DC output with eta = 0.90)
for scale, ref in ((1 / 0.95, (3.3907, 78.5901, 54.2272, 27.1136)),
                   (1 / (0.90 * 0.95), (3.7674, 87.3223, 60.2524, 30.1262))):
    for got, r in zip((V5, Isrc, IA, IB), ref):
        assert abs(got * scale - r) / r < 0.005
# branch: kvar ratings are net of the 6 % reactor (Xc - XL = V^2/Q)
Zn = {k: 1j * (h * 0.06 * x / 0.94 - x / 0.94 / h) for k, x in XC.items()}
Zb2 = 1 / (1 / Z_up + 1 / Zn["A"] + 1 / Zn["B"])
V5n = abs(Zb2) * I5 / Ib * VLL
assert abs(V5n - 3.3225) / 3.3225 < 0.005
assert abs(V5n / VLL * Ib / abs(Zn["A"]) - 49.95) / 49.95 < 0.005
print("PASS EE-104-06-5")
