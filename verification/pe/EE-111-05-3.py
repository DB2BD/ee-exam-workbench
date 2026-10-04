"""EE-111-05-3 (needs_manual_review): critical clearing angle/time, fault at
generator terminal (Pe=0 during fault), post-fault network = pre-fault.

Givens: H=6 MJ/MVA, Pm=1.0, Pmax=2.5. Frequency is NOT in the crop; time is
given as 0.2704*sqrt(60/f) and evaluated at f=60 Hz (conditional branch).
"""
import numpy as np
import sympy as sp

H, Pm, Pmax = 6.0, 1.0, 2.5
d0 = np.arcsin(Pm / Pmax)
dmax = np.pi - d0
cos_dcr = (Pm * (dmax - d0) + Pmax * np.cos(dmax)) / Pmax
dcr = np.arccos(cos_dcr)
assert abs(np.degrees(d0) - 23.578) < 1e-3
assert abs(np.degrees(dcr) - 89.375) < 1e-3

f = sp.symbols("f", positive=True)
tcr = sp.sqrt(4 * H * (dcr - d0) / (2 * sp.pi * f * Pm))
t60 = float(tcr.subs(f, 60))
assert abs(t60 - 0.2704) / 0.2704 < 0.005
assert abs(float(tcr.subs(f, 50)) - 0.2704 * np.sqrt(60 / 50)) / 0.2962 < 0.005

# Method 2: integrate the swing equation with Pe=0 and compare t(delta_cr).
ws = 2 * np.pi * 60
dt = 1e-6
d, w, t = d0, 0.0, 0.0
while d < dcr:
    w += (np.pi * 60 / H) * Pm * dt
    d += w * dt
    t += dt
assert abs(t - t60) < 1e-3
# equal areas
A1 = Pm * (dcr - d0)
A2 = Pmax * (np.cos(dcr) - np.cos(dmax)) - Pm * (dmax - dcr)
assert abs(A1 - A2) < 1e-9
print("PASS EE-111-05-3")
