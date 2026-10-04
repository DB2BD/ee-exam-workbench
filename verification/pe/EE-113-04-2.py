"""EE-113-04-2: 600 kVA, 1800 rpm, 4.2 kV, 60 Hz, eta=0.9 synchronous generator,
rated current at 0.9 lag, Zs = 2 + j20 ohm per phase."""
import numpy as np

S, n, VL, f, eta, pf, Zs = 600e3, 1800, 4200.0, 60, 0.9, 0.9, 2 + 20j
P = 120 * f / n
assert P == 4
Zb = VL**2 / S
Zpu = Zs / Zb
assert abs(Zpu.real - 0.06803) / 0.06803 <= 0.005 and abs(Zpu.imag - 0.6803) / 0.6803 <= 0.005
Ia = S / (np.sqrt(3) * VL)
Pcu = 3 * Ia**2 * Zs.real
assert abs(Pcu - 40816) / 40816 <= 0.005
# independent: per-unit copper loss = I_pu^2 R_pu * S_base
assert abs(1.0**2 * Zpu.real * S - Pcu) < 1e-6
w = 2 * np.pi * n / 60
T_em = (S * pf + Pcu) / w
T_shaft = (S * pf / eta) / w
assert abs(T_em - 3081.3) / 3081.3 <= 0.005
assert abs(T_shaft - 3183.1) / 3183.1 <= 0.005
print(f"P={P} Zpu={Zpu:.5f} Pcu={Pcu:.1f} W Tem={T_em:.1f} Tshaft={T_shaft:.1f}")
print("PASS EE-113-04-2")
