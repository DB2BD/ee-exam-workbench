"""EE-108-05-3: 3-phase and B-C line-to-line fault at open-ended point P.

Base 1000 MVA; line base 500 kV.  Prefault voltage 515 kV -> 1.03 pu.
G1: X''=X1=X2=0.10, G2 (800 MVA): 0.15, T1 0.175 (1000 MVA), T2 0.16 (800 MVA),
line X1=0.15 on 1500 MVA -> 0.10, X0=0.40 -> 0.2667 (1000 MVA).
"""
import math

import numpy as np

SB, VBL = 1000.0, 500.0
Vf = 515.0 / VBL
xl1 = 0.15 * SB / 1500.0
xl0 = 0.40 * SB / 1500.0
xg1 = 0.10 * SB / 1000.0
xg2 = 0.15 * SB / 800.0
xt1 = 0.175 * SB / 1000.0
xt2 = 0.16 * SB / 800.0


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


close(xl1, 0.10, 1e-9); close(xg2, 0.1875, 1e-9); close(xt2, 0.20, 1e-9)

# Method 1: series-parallel reduction of positive sequence
za, zb = xg1 + xt1, xg2 + xt2
Z1 = xl1 + za * zb / (za + zb)
close(Z1, 0.26085, 1e-4)
I3 = Vf / Z1
IG1_pu = I3 * zb / (za + zb)
Ibase20 = SB * 1e6 / (math.sqrt(3) * 20e3)
IG1 = IG1_pu * Ibase20
close(IG1_pu, 2.3096, 1e-3)
close(IG1, 66672, 1e-3)

# Method 2: nodal solve (bus P=0, hv bus=1, G1 inner=2, G2 inner=3) with 1 pu sources
# 1 pu EMF behind G1+T1 and G2+T2; unit current injected at P gives Z1 and the G1 split
Y = np.zeros((2, 2), complex)  # nodes: hv bus (0), P (1)
y = lambda x: 1 / (1j * x)
Y[0, 0] = y(za) + y(zb) + y(xl1); Y[1, 1] = y(xl1); Y[0, 1] = Y[1, 0] = -y(xl1)
Zbus = np.linalg.inv(Y)
close(Zbus[1, 1].imag, Z1, 1e-9)
# fault current into P with Thevenin voltage: bus HV voltage = Vf - I3*j*xl1
Vh = Vf - 1j * xl1 * (-1j * I3)
close(abs(Vh) / za, IG1_pu, 1e-3)  # current through G1+T1 branch from the same node voltage

# Line-to-line (B-C): Ia1 = Vf/(Z1+Z2); |Ib| = sqrt(3)|Ia1|
Z2 = Z1
Ia1 = Vf / (Z1 + Z2)
a = np.exp(2j * math.pi / 3)
Ib = a**2 * Ia1 + a * (-Ia1)
close(abs(Ib), 3.4196, 1e-3)
Ibase500 = SB * 1e6 / (math.sqrt(3) * 500e3)
close(abs(Ib) * Ibase500, 3948.6, 1e-3)
# sanity: L-L = sqrt(3)/2 of the three-phase current
close(abs(Ib), math.sqrt(3) / 2 * I3, 1e-9)
print("PASS EE-108-05-3")
