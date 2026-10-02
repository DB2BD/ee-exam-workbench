"""EE-112-04-3: 208 V, Y synchronous motor, Xs = 1.6 ohm, lossless;
If = 2.7 A gives 50 A at unity pf; same load at 0.8 leading.
Field current assumes the unsaturated (linear) E_A ~ I_f model."""
import numpy as np

V = 208 / np.sqrt(3)
Xs = 1.6
E1 = V - 1j * Xs * 50
assert abs(abs(E1) - 144.30) / 144.30 <= 0.005
assert abs(np.degrees(np.angle(E1)) - (-33.67)) / 33.67 <= 0.005
I2 = 50 / 0.8 * np.exp(1j * np.arccos(0.8))
E2 = V - 1j * Xs * I2
If2 = 2.7 * abs(E2) / abs(E1)
assert abs(If2 - 3.687) / 3.687 <= 0.005
# independent: constant power => E_A sin(delta) constant = Xs * P / (3 V)
P = 3 * V * 50
assert abs(abs(E1.imag) - Xs * P / (3 * V)) < 1e-9 and abs(abs(E2.imag) - Xs * P / (3 * V)) < 1e-9
print(f"E1={abs(E1):.3f} V delta={np.degrees(np.angle(E1)):.3f} E2={abs(E2):.3f} If2={If2:.4f} A")
print("PASS EE-112-04-3")
