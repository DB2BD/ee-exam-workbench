"""EE-107-04-5: 3-phase 4-pole induction motor 200 V, 50 Hz, 10 kW input at rated; constant V/f, slip fixed 5 %.
Conversion efficiency 90 % at the first operating point."""
import math
P, V1, f1, f2, s, eta, pole = 10e3, 200.0, 50.0, 30.0, 0.05, 0.90, 4
ns1 = 120 * f1 / pole
n1 = (1 - s) * ns1
Pm = eta * P
T1 = Pm / (2 * math.pi * n1 / 60)
V2 = V1 / f1 * f2
n2 = (1 - s) * 120 * f2 / pole
assert n1 == 1425
assert abs(T1 - 60.31) / 60.31 <= 0.005
assert abs(V2 - 120) < 1e-9 and abs(n2 - 855) < 1e-9
# independent: via air-gap power Pag = Pm/(1-s) and Tem = Pag/ws
Tag = (Pm / (1 - s)) / (2 * math.pi * ns1 / 60)
assert abs(Tag - T1) < 1e-9
print(f"n1={n1} T1={T1:.4f} V2={V2} n2={n2}")
print("PASS EE-107-04-5")
