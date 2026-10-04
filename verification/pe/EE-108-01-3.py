"""EE-108-01-3 independent check: two balanced loads in parallel on a 3-phase line.

Givens (official crop): Z_Y = 6+j8 ohm per phase, Z_Delta = 8-j6 ohm per phase,
v_ab(t) = 220*sqrt(2)*cos(120*pi*t) (volts, unit not printed in the crop) => line-to-line 220 V rms.
Phase sequence is irrelevant to P and Q of a balanced load.  Solve with explicit phase currents.
"""
import cmath
import math

VL = 220.0
ZY = 6 + 8j
ZD = 8 - 6j
# Y load: phase voltage = VL/sqrt(3), phase currents explicit (reference Van at 0 deg for abc sequence)
a = cmath.exp(-2j * math.pi / 3)
Van = VL / math.sqrt(3)
Vph = [Van, Van * a, Van * a**2]
Iy = [v / ZY for v in Vph]
S_Y = sum(v * i.conjugate() for v, i in zip(Vph, Iy))
# Delta load: line voltages across the Delta branches
Vll = [Van * (1 - a) , Van * (a - a**2), Van * (a**2 - 1)]
assert abs(abs(Vll[0]) - VL) < 1e-9
Id = [v / ZD for v in Vll]
S_D = sum(v * i.conjugate() for v, i in zip(Vll, Id))
S = S_Y + S_D
P, Q = S.real, S.imag
assert abs(P - 14520) / 14520 < 5e-3, P
assert abs(Q + 4840) / 4840 < 5e-3, Q
# per-load values for the note
assert abs(S_Y - (2904 + 3872j)) < 1
assert abs(S_D - (11616 - 8712j)) < 1
print("PASS EE-108-01-3")
