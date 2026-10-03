"""EE-108-04-3: 3-phase Y, 220 V, 60 Hz, 6-pole induction motor.
R1=0.29 X1=0.5 R2=0.144 X2=0.21 Xphi=13.25 (per phase, stator side), rotational+core = 403 W, s=0.02."""
import numpy as np

VL, f, P, s = 220.0, 60.0, 6, 0.02
R1, X1, R2, X2, Xm, Prot = 0.29, 0.5, 0.144, 0.21, 13.25, 403.0
Vph = VL / np.sqrt(3)
ns = 120 * f / P
n = (1 - s) * ns
ws = 2 * np.pi * ns / 60
wm = 2 * np.pi * n / 60
# method A: series-parallel impedance
Z2 = R2 / s + 1j * X2
Zm = 1j * Xm
Zp = Z2 * Zm / (Z2 + Zm)
Zin = R1 + 1j * X1 + Zp
I1 = Vph / Zin
I2 = I1 * Zm / (Z2 + Zm)
Pag = 3 * abs(I2) ** 2 * R2 / s
Pdev = (1 - s) * Pag
Pout = Pdev - Prot
Tout = Pout / wm
Pin = 3 * (Vph * np.conj(I1)).real
eta = Pout / Pin
# method B: Thevenin at the rotor branch (independent route)
Zs = R1 + 1j * X1
Vth = Vph * Zm / (Zs + Zm)
Zth = Zs * Zm / (Zs + Zm)
I2b = Vth / (Zth + Z2)
Pag_b = 3 * abs(I2b) ** 2 * R2 / s
assert abs(Pag - Pag_b) < 1e-6
assert n == 1176
assert abs(Pag - 5747.72) / 5747.72 <= 0.005
assert abs(Tout - 42.47) / 42.47 <= 0.005
assert abs(eta - 0.8637) / 0.8637 <= 0.005
# loss-sum cross-check
Pcu1 = 3 * abs(I1) ** 2 * R1
Pcu2 = 3 * abs(I2) ** 2 * R2
assert abs(Pin - (Pout + Pcu1 + Pcu2 + Prot)) < 1e-6
print(f"n={n} |I1|={abs(I1):.4f} |I2|={abs(I2):.4f} Pag={Pag:.2f} Tout={Tout:.3f} Pin={Pin:.2f} eta={eta:.4f}")
print("PASS EE-108-04-3")
