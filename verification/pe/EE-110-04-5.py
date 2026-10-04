"""EE-110-04-5: 208 V Y, 6-pole, 60 Hz IM, R1 = .10, R2 = .07, X1 = X2 = .21, Xm = 10;
start with / without series starting reactor Xst.
"""
import numpy as np

R1, R2, X1, X2, Xm = 0.10, 0.07, 0.21, 0.21, 10.0
V = 208 / np.sqrt(3)
ws = 2 * np.pi * 1200 / 60
Zr = R2 + 1j * X2
Zp = 1j * Xm * Zr / (1j * Xm + Zr)
Z = R1 + 1j * X1 + Zp
Is = V / Z
I2 = Is * 1j * Xm / (1j * Xm + Zr)
T = 3 * abs(I2) ** 2 * R2 / ws
assert abs(abs(Is) - 267.78) / 267.78 <= 0.005
assert abs(T - 114.95) / 114.95 <= 0.005
# (2) |Z + j Xst| = sqrt(3) |Z|
Xst = np.sqrt(3 * abs(Z) ** 2 - Z.real**2) - Z.imag
assert abs(Xst - 0.3424) / 0.3424 <= 0.005
Is2 = V / (Z + 1j * Xst)
I22 = Is2 * 1j * Xm / (1j * Xm + Zr)
T2 = 3 * abs(I22) ** 2 * R2 / ws
assert abs(abs(Is2) - abs(Is) / np.sqrt(3)) < 1e-9
assert abs(T2 - 38.32) / 38.32 <= 0.005
# independent: Thevenin route for torque at s = 1
Vth = V * 1j * Xm / (R1 + 1j * (X1 + Xm))
Zth = (R1 + 1j * X1) * 1j * Xm / (R1 + 1j * (X1 + Xm))
Tth = 3 * abs(Vth) ** 2 * R2 / (ws * abs(Zth + Zr) ** 2)
assert abs(Tth - T) / T < 1e-9
print(f"|Z|={abs(Z):.5f} Is={abs(Is):.2f} I2={abs(I2):.2f} T={T:.3f} Xst={Xst:.5f} Is2={abs(Is2):.2f} T2={T2:.3f}")
print("PASS EE-110-04-5")
