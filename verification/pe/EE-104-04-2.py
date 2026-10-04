"""EE-104-04-2 (descriptive) quantitative arguments.

Givens (official crop): 1.0 kVA, 200 V : 100 V, 60 Hz single-phase transformer;
LV side feeds a 10 ohm resistor; HV side connected to 200 V, 50 Hz.
"""
from fractions import Fraction as F

S, V1, V2, f_rated, f_new, R = F(1000), F(200), F(100), F(60), F(50), F(10)
a = V1 / V2

flux_ratio = (V1 / f_new) / (V1 / f_rated)          # E = 4.44 f N Phi
assert flux_ratio == F(6, 5)                         # 120 % of rated flux

I2 = (V1 / a) / R                                   # ratio unchanged: 100 V on the load
assert I2 == 10 == S / V2                            # load draws exactly rated current
I1 = V1 / (a**2 * R)                                 # independent: reflected 40 ohm
assert I1 == 5 == S / V1 and V1 * I1 == V2 * I2 == S

assert f_new / f_rated == F(5, 6)                    # leakage reactance ~ f
assert (f_new / f_rated) ** 2 * flux_ratio**2 == 1   # eddy loss ~ f^2 B^2: unchanged
hyst = [float(f_new / f_rated) * float(flux_ratio) ** n for n in (1.6, 2.0)]
assert abs(hyst[0] - 1.12) / 1.12 <= 0.005 and abs(hyst[1] - 1.2) / 1.2 <= 0.005

V_safe = V1 * f_new / f_rated                        # keep rated V/f
assert abs(float(V_safe) - 166.7) / 166.7 <= 0.005
P_safe = (V_safe / a) ** 2 / R
assert abs(float(V_safe / a) - 83.3) / 83.3 <= 0.005 and abs(float(P_safe) - 694) / 694 <= 0.005
print("PASS EE-104-04-2 (descriptive: quantitative arguments)")
