"""EE-109-06-5: capacitor for full-load PF 0.9 and resulting light-load PF.

Givens: Y load centre, 3300 V; full load 200 A PF 0.8 lag; light load 100 A PF 0.6 lag.
"""
import numpy as np

V = 3300.0
def s(i, pf):
    return np.sqrt(3) * V * i * complex(pf, np.sqrt(1 - pf**2)) / 1e3
s1, s2 = s(200, 0.8), s(100, 0.6)
qc = s1.imag - s1.real * np.tan(np.arccos(0.9))
assert abs(qc - 242.968) / 242.968 < 0.005               # boxed 242.97 kvar
pf2 = s2.real / abs(s2 - 1j * qc)
assert abs(pf2 - 0.84805) / 0.84805 < 0.005 and (s2.imag - qc) > 0   # boxed 0.848 lag
# independent: per-phase capacitor current and line-current reduction
ic = qc * 1e3 / (np.sqrt(3) * V)
i_new = abs(s1 - 1j * qc) * 1e3 / (np.sqrt(3) * V)
assert abs(i_new - 200 * 0.8 / 0.9) < 1e-6
assert abs(np.hypot(200 * 0.8, 200 * 0.6 - ic) - i_new) < 1e-6
print("PASS EE-109-06-5")
