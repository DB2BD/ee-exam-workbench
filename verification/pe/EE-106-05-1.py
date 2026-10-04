"""EE-106-05-1: 60 Hz, 161 kV, 40 km short line r=0.15 ohm/km, L=1.3 mH/km, shunt C
neglected; receiving end 161 kV, 300 MVA, pf 0.8 lagging.
"""
import cmath
import math

L_km = 40.0
R = 0.15 * L_km
X = 2 * math.pi * 60 * 1.3e-3 * L_km
VRll, S = 161e3, 300e6


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


close(R, 6.0, 1e-9)
close(X, 19.604, 1e-4)
VR = VRll / math.sqrt(3)
I = S / (math.sqrt(3) * VRll) * cmath.exp(-1j * math.acos(0.8))
close(abs(I), 1075.8, 1e-4)
VS = VR + (R + 1j * X) * I
close(abs(VS) * math.sqrt(3) / 1e3, 193.18, 1e-4)         # kV line-to-line
close(abs(VS) / 1e3, 111.53, 1e-4)                          # kV per phase
close(math.degrees(cmath.phase(VS)), 6.693, 2e-3)
SS = 3 * VS * I.conjugate()
close(SS.real / 1e6, 260.83, 1e-4)
close(SS.imag / 1e6, 248.07, 1e-4)
close(abs(SS) / 1e6, 359.97, 1e-3)
Ploss = 3 * abs(I) ** 2 * R
close(Ploss / 1e6, 20.833, 1e-4)
PR = S * 0.8
# voltage regulation (no shunt branch: no-load receiving voltage = |VS|)
VRpct = (abs(VS) - VR) / VR * 100
close(VRpct, 19.99, 1e-3)
eff = PR / SS.real * 100
close(eff, 92.01, 1e-3)
# independent: approximate drop formula and power balance
approx = (I.real * R + (-I.imag) * X) / VR * 100
assert abs(approx - VRpct) < 2.0   # first-order estimate within 2 points
close(PR + Ploss, SS.real, 1e-9)
print("PASS EE-106-05-1")
