"""EE-107-05-1: line Z=0.02+j0.2 pu, receiving end P=1.6 pu pf 0.8 lag, |VR|=1,
capacitor bank compensates Qc=1.2 pu at the receiving end.
"""
import cmath
import math

Z = 0.02 + 0.2j
VR = 1.0
P, pf, Qc = 1.6, 0.8, 1.2


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


QL = P * math.tan(math.acos(pf))
close(QL, 1.2, 1e-9)
# (1) line current: net receiving-end power after capacitor
Snet = complex(P, QL - Qc)
I = (Snet / VR).conjugate()
close(abs(I), 1.6, 1e-9)
Ploss = abs(I) ** 2 * Z.real
close(Ploss, 0.0512, 1e-9)
# (2) sending voltage
VS = VR + Z * I
close(abs(VS), 1.0805, 1e-3)
# (3) capacitor impedance (parallel at receiving end, V=1, Q=1.2)
Zc = VR**2 / complex(0, -Qc)  # Zc = V^2 / conj(S)  with S = -jQc
Zc = -1j * VR**2 / Qc
close(Zc.imag, -0.83333, 1e-4)
assert abs((VR * (VR / Zc).conjugate()).imag - (-Qc)) < 1e-9  # capacitor injects +Qc, i.e. Q=-1.2
# (4) sending-end power
SS = VS * I.conjugate()
close(SS.real, 1.6512, 1e-4)
close(SS.imag, 0.512, 1e-4)
# power balance: load + capacitor + line loss = sending end
Sline = abs(I) ** 2 * Z
close((complex(P, QL) + complex(0, -Qc) + Sline).real, SS.real, 1e-9)
close((complex(P, QL) + complex(0, -Qc) + Sline).imag, SS.imag, 1e-9)
print("PASS EE-107-05-1")
