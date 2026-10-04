"""EE-114-04-4: 3.2 kV, 1000 kVA, 0.9 lag, Y, 4-pole, 60 Hz generator.

Ra = 0.1, Xs = 2.0 ohm; core 15 kW, F&W 14 kW.
"""
import numpy as np

VL, S, pf, Ra, Xs = 3200.0, 1e6, 0.9, 0.1, 2.0
Vph = VL / np.sqrt(3)
Ia = S / (np.sqrt(3) * VL) * np.exp(-1j * np.arccos(pf))
Ef = Vph + Ia * (Ra + 1j * Xs)
assert abs(abs(Ef) - 2045.74) / 2045.74 <= 0.005
assert abs(np.degrees(np.angle(Ef)) - 8.91) / 8.91 <= 0.005

P_in = S * pf + 3 * abs(Ia) ** 2 * Ra + 15e3 + 14e3
wm = 2 * np.pi * (120 * 60 / 4) / 60
T = P_in / wm
assert abs(T - 4980) / 4980 <= 0.005
# independent: air-gap power from 3 Re(Ef Ia*) must equal Pout + Pcu
Pgap = 3 * (Ef * np.conj(Ia)).real
assert abs(Pgap - 909765.625) < 1e-3
print(f"|Ef|={abs(Ef):.2f} V delta={np.degrees(np.angle(Ef)):.3f} deg P_in={P_in:.1f} W T={T:.1f} N.m")
print("PASS EE-114-04-4")
