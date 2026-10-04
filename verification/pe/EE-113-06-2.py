"""EE-113-06-2: minimum PF so the load-voltage drop (Vs-VL)/VL <= 5 %.

Method: exact phasor solution (constant-impedance load + shunt susceptance),
bisection on the capacitor susceptance; compared with the approximate drop formula.
"""
import numpy as np

Zl = 2 * 0.130 * (0.483 + 0.1083j)
ZL = 1.68 + 1.26j
Vs = 220.0
def VL(B):
    Zeq = 1 / (1 / ZL + 1j * B)
    return abs(Vs * Zeq / (Zl + Zeq)), Zeq
target = Vs / 1.05
a, b = 0.0, (1 / ZL).imag * -1
for _ in range(200):
    m = (a + b) / 2
    if (VL(a)[0] - target) * (VL(m)[0] - target) <= 0: b = m
    else: a = m
v, Zeq = VL((a + b) / 2)
pf_exact = np.cos(np.angle(Zeq))
assert abs(VL(0)[0] - 208.30) < 0.01            # uncorrected drop 5.62 % > 5 %
# approximate formula dV = (P/VL)(R + X tan(phi))
P = target**2 * ZL.real / abs(ZL)**2
t = ((Vs - target) * target / P - Zl.real) / Zl.imag
pf_approx = 1 / np.sqrt(1 + t * t)
for pf in (pf_exact, pf_approx):
    assert abs(pf - 0.9803) / 0.9803 < 0.005
print("PASS EE-113-06-2")
