"""EE-109-04-3: 220 V Y, 60 Hz, 7.5 kW, 6-pole IM, R1 = .3, X1 = .5, R2 = .2, X2 = .4,
no magnetizing branch."""
import numpy as np

V = 220 / np.sqrt(3)
R1, X1, R2, X2 = 0.3, 0.5, 0.2, 0.4
ws = 2 * np.pi * 1200 / 60

def torque(s):
    I = V / abs(R1 + R2 / s + 1j * (X1 + X2))
    return 3 * I**2 * R2 / s / ws, I

Tst, Ist = torque(1.0)
assert abs(Tst - 72.67) / 72.67 <= 0.005
s = (1200 - 1188) / 1200
T2, I2 = torque(s)
assert abs(T2 - 18.66) / 18.66 <= 0.005
# independent: power balance P_conv = (1 - s) P_ag and T = P_conv / omega_m
Pag = 3 * I2**2 * R2 / s
wm = 2 * np.pi * 1188 / 60
assert abs((1 - s) * Pag / wm - T2) / T2 < 1e-12
print(f"Ist={Ist:.3f} Tst={Tst:.3f} s={s} I={I2:.4f} T={T2:.3f} Pconv={(1-s)*Pag:.1f} W")
print("PASS EE-109-04-3")
