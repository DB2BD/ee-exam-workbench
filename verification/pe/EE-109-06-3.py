"""EE-109-06-3: per-unit impedance diagram and 3-phase fault 50 m down the feeder.

Givens: S_sc = 100 MVA at the boundary; T 1000 kVA 11.4 kV/220 V X = 5 %; feeder 0.11 + j0.13 ohm/km;
base 1000 kVA, 220 V; fault at 50 m.
"""
import numpy as np

SB, VB = 1000e3, 220.0
zb = VB**2 / SB
xs = SB / 100e6
xt = 0.05
zl = (0.11 + 0.13j) * 0.05 / zb
assert abs(xs - 0.01) < 1e-12 and abs(zl - (0.113636 + 0.134298j)) < 1e-6   # boxed diagram values
z = 1j * xs + 1j * xt + zl
i = SB / (np.sqrt(3) * VB) / abs(z)
assert abs(i / 1e3 - 11.659) / 11.659 < 0.005      # boxed 11.659 kA
# independent: ohmic calculation on the 220 V side
z_ohm = 1j * (xs + xt) * zb + (0.11 + 0.13j) * 0.05
assert abs((VB / np.sqrt(3)) / abs(z_ohm) - i) < 1e-6
print("PASS EE-109-06-3")
