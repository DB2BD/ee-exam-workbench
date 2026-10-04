"""EE-112-04-4: 380 V, Y induction motor starts at 330 A, pf 0.51 lag;
delta-connected capacitors cut the line current to 200 A (still lagging)."""
import numpy as np

V, w = 380.0, 2 * np.pi * 60
Im = 330 * (0.51 - 1j * np.sqrt(1 - 0.51**2))
Iq_new = -np.sqrt(200**2 - Im.real**2)        # lagging root
Ic_line = Iq_new - Im.imag
C = Ic_line / (np.sqrt(3) * w * V)
assert abs(C * 1e6 - 708.5) / 708.5 <= 0.005
# independent: reactive-power balance, Q_cap = 3 V^2 w C (delta, each across V_LL)
Q_motor = np.sqrt(3) * V * (-Im.imag)
Q_new = np.sqrt(3) * V * (-Iq_new)
assert abs((Q_motor - Q_new) - 3 * V**2 * w * C) < 1e-6
assert abs(abs(Im.real + 1j * Iq_new) - 200) < 1e-9
print(f"Ic_line={Ic_line:.3f} A C={C*1e6:.2f} uF")
print("PASS EE-112-04-4")
