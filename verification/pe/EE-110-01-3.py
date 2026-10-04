"""EE-110-01-3 independent check: series RLC resonance and peak vC/vL.

Givens (official crop): vs = 100 cos(2 pi f t) V; at f = 5 kHz, R = 10 ohm,
XL = 25 ohm, XC = 64 ohm.  The maxima of |VC| and |VL| are located by numeric
search over f (not by the closed-form formula).
"""
import numpy as np

f1, R, XL, XC, Vm = 5e3, 10.0, 25.0, 64.0, 100.0
L = XL / (2 * np.pi * f1)
C = 1 / (2 * np.pi * f1 * XC)
f0 = 1 / (2 * np.pi * np.sqrt(L * C))
Q0 = 2 * np.pi * f0 * L / R
assert abs(f0 - 8000) < 1e-6 and abs(Q0 - 4) < 1e-12

def amps(f):
    w = 2 * np.pi * f
    I = Vm / np.abs(R + 1j * (w * L - 1 / (w * C)))
    return I, I / (w * C), I * w * L

I0, VC0, VL0 = amps(f0)
assert abs(I0 - 10) < 1e-9 and abs(R * I0 - 100) < 1e-9
assert abs(VC0 - 400) < 1e-9 and abs(VL0 - 400) < 1e-9

f = np.linspace(7000, 9000, 2_000_001)
_, VC, VL = amps(f)
fC, VCmax = f[np.argmax(VC)], VC.max()
fL, VLmax = f[np.argmax(VL)], VL.max()
print(f"L={L:.6e} C={C:.6e} fC={fC:.3f} VCmax={VCmax:.4f} fL={fL:.3f} VLmax={VLmax:.4f}")
for got, exp in ((fC, 7874.008), (fL, 8128.008), (VCmax, 403.1621), (VLmax, 403.1621)):
    assert abs(got - exp) / exp < 1e-4, (got, exp)
print("PASS EE-110-01-3")
