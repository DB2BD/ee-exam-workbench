"""EE-109-06-2: line-to-line % voltage drop, 220 V Delta vs 380 V Y, 100 kVA PF 0.9 lag.

Givens: z = 0.1 + j0.2 ohm/km per conductor, 50 m, balanced 100 kVA, PF 0.9 lag.
Rated condition: receiving-end line voltage = nominal (220 V or 380 V).
"""
import numpy as np

z = (0.1 + 0.2j) * 0.05
pf = 0.9
def drop(v_ll):
    i = 100e3 / (np.sqrt(3) * v_ll)
    approx = np.sqrt(3) * i * (z.real * pf + z.imag * np.sqrt(1 - pf**2))
    # exact phasor: per-phase receiving voltage reference, sending = Vr + I Z
    vr = v_ll / np.sqrt(3)
    iph = i * np.exp(-1j * np.arccos(pf))
    vs = abs(vr + iph * z) * np.sqrt(3)
    return approx / v_ll * 100, (vs - v_ll) / v_ll * 100, i

a220, e220, i220 = drop(220.0)
a380, e380, i380 = drop(380.0)
assert abs(i220 - 262.43) < 0.01 and abs(i380 - 151.93) < 0.01
assert abs(a220 - 1.830) / 1.830 < 0.005          # boxed 1.830 %
assert abs(a380 - 0.6135) / 0.6135 < 0.005        # boxed 0.6135 %
# independent: exact phasor result (1.840 % / 0.6146 %) within 1 % of the approximate formula; ratio (220/380)^2
assert abs(e220 - a220) / a220 < 0.01 and abs(e380 - a380) / a380 < 0.01
assert abs(a380 / a220 - (220 / 380) ** 2) < 1e-12
print("PASS EE-109-06-2")
