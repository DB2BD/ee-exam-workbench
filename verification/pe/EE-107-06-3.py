"""EE-107-06-3: 69 kV delta / 11.4 kV wye, 40 MVA, LV leads HV by 30 deg; CT C400 3000/5 (11.4 kV)
and C400 400/5 (69 kV); three differential relays.  Relay currents and their ratio.

Phasor check: the 11.4 kV side CTs are connected in delta, the 69 kV side CTs in wye.
"""
import numpy as np

S = 40e6
I_H = S / (np.sqrt(3) * 69e3)
I_L = S / (np.sqrt(3) * 11.4e3)
assert abs(I_H - 334.70) < 0.01 and abs(I_L - 2025.79) < 0.01

e = lambda deg: np.exp(1j * np.deg2rad(deg))
# HV line currents (reference), LV leads by 30 deg (given); positive sequence a-b-c
iH = [I_H * e(0), I_H * e(-120), I_H * e(120)]
iL = [I_L * e(30), I_L * e(30 - 120), I_L * e(30 + 120)]
# CT secondaries (equal and opposite flow convention: power through the bank)
sH = [5 / 400 * i for i in iH]                       # wye CTs: relay current = CT secondary
sL = [5 / 3000 * i for i in iL]
dL = [sL[0] - sL[2], sL[1] - sL[0], sL[2] - sL[1]]   # delta CTs: Ia-Ic, Ib-Ia, Ic-Ib (lags 30 deg)
for k in range(3):
    assert abs(np.angle(dL[k] / sH[k])) < 1e-9       # (Ia-Ic) lags Ia by 30 deg and cancels the 30 deg lead
I_Hr, I_Lr = abs(sH[0]), abs(dL[0])
assert abs(I_Hr - 4.1837) / 4.1837 < 5e-4
assert abs(I_Lr - 5.8480) / 5.8480 < 5e-4            # sqrt(3) x single CT secondary
assert abs(abs(sL[0]) - 3.3763) / 3.3763 < 5e-4
assert abs(I_Lr / I_Hr - 1.398) / 1.398 < 5e-4       # boxed ratio LV/HV
assert abs(I_Hr / I_Lr - 0.7154) / 0.7154 < 5e-4
# wrong choices leave a 30 deg residual: wye CTs on the wye side, or the opposite delta direction
assert abs(np.degrees(np.angle((sL[0] - sL[1]) / sH[0])) - 60) < 1e-9
assert abs(np.degrees(np.angle(sL[0] / sH[0])) - 30) < 1e-9
print("PASS EE-107-06-3")
