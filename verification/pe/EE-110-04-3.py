"""EE-110-04-3: 380 V, 15 kW, 8-pole, Y synchronous motor, Xs = 5.8 ohm, Ra = 0."""
import numpy as np

Xs, P = 5.8, 15e3
V1 = 380 / np.sqrt(3)
I1 = P / (np.sqrt(3) * 380 * 0.8) * np.exp(-1j * np.arccos(0.8))
E1 = V1 - 1j * Xs * I1
assert abs(abs(I1) - 28.49) / 28.49 <= 0.005
assert abs(abs(E1) - 178.70) / 178.70 <= 0.005
assert abs(np.degrees(np.angle(E1)) - (-47.71)) / 47.71 <= 0.005
# (2) V = 342 V, |E| and P fixed
V2 = 342 / np.sqrt(3)
d2 = np.arcsin(P * Xs / (3 * V2 * abs(E1)))
E2 = abs(E1) * np.exp(-1j * d2)
I2 = (V2 - E2) / (1j * Xs)
pf2 = np.cos(np.angle(I2))
assert abs(np.degrees(d2) - 55.27) / 55.27 <= 0.005
assert abs(abs(I2) - 30.22) / 30.22 <= 0.005
assert abs(pf2 - 0.8379) / 0.8379 <= 0.005 and np.angle(I2) < 0   # lagging
# independent: complex power at terminals equals 15 kW at both points
for V, I in ((V1, I1), (V2, I2)):
    assert abs(3 * (V * np.conj(I)).real - P) < 1e-6
# 8-pole: ns = 900 rpm, torque unchanged
T = P / (2 * np.pi * 900 / 60)
print(f"I1={abs(I1):.3f} E={abs(E1):.3f} d1={np.degrees(np.angle(E1)):.3f} d2={np.degrees(d2):.3f} I2={abs(I2):.3f} pf2={pf2:.4f} T={T:.2f}")
print("PASS EE-110-04-3")
