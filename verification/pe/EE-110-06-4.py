"""EE-110-06-4: arc-furnace flicker at A (69 kV bus) and series reactor for <= 1.5 %.

Stem givens: S_sc = 1500 MVA; base 69 kV, 12.5 MVA; Z_L = j4.0 ohm; main T 8 %, furnace T 7 %
(on 12.5 MVA); Z_F = j0.35 pu.  A is on the 69 kV bus, upstream of Z_L.
"""
import numpy as np

SB, VB = 12.5, 69.0
xs = SB / 1500
xl = 4.0 / (VB**2 / SB)
x_all = xs + xl + 0.08 + 0.07 + 0.35
dva = xs / x_all * 100
assert abs(dva - 1.606) / 1.606 < 0.005                 # boxed 1.606 %
xr = xs / 0.015 - x_all
assert abs(xr - 0.03672) / 0.03672 < 0.005              # boxed 0.03672 pu
# independent: phasor KVL with furnace shorted, A-bus voltage magnitude
i = 1 / (1j * (x_all + xr))
va = 1 - 1j * xs * i
assert abs((1 - abs(va)) * 100 - 1.5) < 1e-9
# branch kept in 「條件與疑義」: observation point B
x_up_b = xs + xl + 0.08 + 0.07
assert f"{x_up_b:.9f}" == "0.168835329" and f"{x_up_b/x_all*100:.4f}" == "32.5412"
assert f"{x_up_b/0.015 - x_all:.6f}" == "10.736853"
print("PASS EE-110-06-4")
