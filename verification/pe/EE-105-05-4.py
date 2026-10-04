"""EE-105-05-4: descriptive; quantitative support from the swing equation.

Crop: plan A = 100 % thermal; plan B = 50 % thermal + 50 % inverter-based renewables.
Assumption: the inverter-based share contributes no inertia (H_ren = 0), other parameters equal.
"""
import numpy as np

f0 = 60.0
H_th, share_th = 5.0, np.array([1.0, 0.5])
H_sys = share_th * H_th                # per-unit-of-load inertia
assert np.isclose(H_sys[1] / H_sys[0], 0.5)

# RoCoF = f0 * dP / (2 H)  for a given power imbalance dP (pu)
dP = 0.1
rocof = f0 * dP / (2 * H_sys)
assert np.isclose(rocof[1] / rocof[0], 2.0)

# Equal-area critical clearing time for a sustained-angle fault with Pe=0 during fault:
#   t_cr = sqrt(2 H (d_cr - d0) / (pi f0 Pm)) -> proportional to sqrt(H)  (same Pm, d_cr, d0)
Pm, d0, dcr = 1.0, np.radians(30), np.radians(100)
tcr = np.sqrt(2 * H_sys * (dcr - d0) / (np.pi * f0 * Pm))
assert np.isclose(tcr[1] / tcr[0], np.sqrt(0.5))

# short-circuit capacity: SCR falls with fewer synchronous machines (generic)
Ssc_sync = np.array([1.0, 0.5]) * 10.0
assert Ssc_sync[1] < Ssc_sync[0]
print("PASS EE-105-05-4 (descriptive)")
