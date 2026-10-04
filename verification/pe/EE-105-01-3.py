"""EE-105-01-3: 12 angle 45 deg V source across 4 ohm and (2 - j1) ohm.  The crop does not say rms or peak; both readings are checked and neither is the main answer."""
import numpy as np
V = 12 * np.exp(1j * np.radians(45))
I1 = V / 4
I2 = V / (2 - 1j)
I = I1 + I2
P_abs = abs(I1) ** 2 * 4 + abs(I2) ** 2 * 2
S = V * np.conj(I)
assert abs(P_abs - 93.6) / 93.6 < 5e-3, P_abs
assert abs(S.real - 93.6) / 93.6 < 5e-3, S
assert abs(S.imag + 28.8) / 28.8 < 5e-3, S
# alternative: Zin = 4 || (2-j)
Zin = 1 / (1 / 4 + 1 / (2 - 1j))
assert abs(abs(V) ** 2 / np.conj(Zin) - S) < 1e-9
# peak/amplitude-phasor reading: every average power is halved
assert abs(0.5 * S.real - 46.8) < 1e-9
print("PASS EE-105-01-3")
