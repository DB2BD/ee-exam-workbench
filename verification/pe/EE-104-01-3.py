"""EE-104-01-3: balanced wye source Van = 120 angle 20 deg Vrms, two parallel wye loads: (8+j6) ohm/phase and another with a-phase S = 600 angle 36 deg VA."""
import numpy as np
Van = 120 * np.exp(1j * np.radians(20))
Z1 = 8 + 6j
S1 = 3 * abs(Van)**2 / np.conj(Z1)       # total 3-phase of load 1
S2a = 600 * np.exp(1j * np.radians(36))
S = S1 + 3 * S2a
assert abs(S.real - 4912.23) / 4912.23 < 5e-3, S
assert abs(S.imag - 3650.0) / 3650.0 < 5e-3, S
# cross-check via line current: S_total = 3 Van Ia*
Ia = Van / Z1 + np.conj(S2a / Van)
assert abs(3 * Van * np.conj(Ia) - S) < 1e-6
print("PASS EE-104-01-3")
