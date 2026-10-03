"""EE-106-06-4: 30 MVA, 11.4/69 kV, Y-delta transformer with differential relay 87.
(一) device 87 meaning; (二) three-phase CT connection; (三) CT1 (11.4 kV, Y side) and CT2 (69 kV,
delta side) ratios chosen for sensitivity.

CT1 is delta-connected (Y-side CTs), CT2 wye-connected.  Standard 5 A multi-ratio series is
assumed (named constant below); selection rules: CT primary >= rated line current and relay
current at rated load <= 5 A, smallest ratio satisfying both (highest sensitivity).
"""
import numpy as np

S = 30e6
I1 = S / (np.sqrt(3) * 11.4e3)       # 11.4 kV, wye side (CT1)
I2 = S / (np.sqrt(3) * 69e3)         # 69 kV, delta side (CT2)
assert abs(I1 - 1519.34) < 0.01 and abs(I2 - 251.02) < 0.01

STD_CT_PRIMARY = [50, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500, 3000, 4000, 5000]
RELAY_RATED = 5.0

ct2 = min(p for p in STD_CT_PRIMARY if p >= I2 and RELAY_RATED * I2 / p <= RELAY_RATED)
ct1 = min(p for p in STD_CT_PRIMARY if p >= I1 and np.sqrt(3) * RELAY_RATED * I1 / p <= RELAY_RATED)
assert (ct1, ct2) == (3000, 300)
r1 = np.sqrt(3) * 5 * I1 / ct1        # delta CTs: x sqrt(3)
r2 = 5 * I2 / ct2
assert abs(r1 - 4.3849) / 4.3849 < 5e-4 and abs(r2 - 4.1837) / 4.1837 < 5e-4
mismatch = r1 / r2 - 1
assert abs(mismatch * 100 - 4.8) < 0.05
# the smaller 2500 CT1 would push the relay above 5 A; 2000/5 leaves a large mismatch
assert np.sqrt(3) * 5 * I1 / 2500 > 5.0
assert abs(np.sqrt(3) * 5 * I1 / 2000 / r2 - 1.5707) < 5e-3
# ideal CT1 ratio matching CT2=300/5 (sqrt3 compensation)
n1 = np.sqrt(3) * I1 / I2 * 60
assert abs(n1 - 629.0) < 0.1
print("PASS EE-106-06-4")
