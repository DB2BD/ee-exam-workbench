"""EE-111-05-4: long line via ABCD constants.

Givens (official crop): 345 kV, 400 MVA, pf 0.8 lag at receiving end;
A=D=0.8180/1.3 deg, B=172.2/84.2 deg ohm, C=0.001933/90.4 deg S.
"""
import numpy as np

pol = lambda m, a: m * np.exp(1j * np.radians(a))
close = lambda a, b: abs(a - b) <= 0.005 * abs(b)
A = D = pol(0.8180, 1.3); B = pol(172.2, 84.2); C = pol(0.001933, 90.4)
VR = 345e3 / np.sqrt(3)
IR = pol(400e6 / (np.sqrt(3) * 345e3), -np.degrees(np.arccos(0.8)))
VS = A * VR + B * IR
IS = C * VR + D * IR
assert close(abs(IR), 669.4)
assert close(abs(VS) / 1e3, 256.74) and abs(np.degrees(np.angle(VS)) - 20.15) < 0.05
assert close(abs(IS), 447.67) and abs(np.degrees(np.angle(IS)) - 8.54) < 0.05
VD = (abs(VS) - VR) / VR * 100
assert close(VD, 28.89)
# no-load
VRnl = abs(VS) / abs(A)
ISnl = C * VS / A
assert close(VRnl / 1e3, 313.86)
assert close(abs(ISnl), 606.69) and abs(np.degrees(np.angle(ISnl)) - 109.25) < 0.05
VReg = (VRnl - VR) / VR * 100
assert close(VReg, 57.57)

# Method 2: inverse ABCD (AD-BC=1) maps (VS, IS) back to (VR, IR)
assert abs(A * D - B * C - 1) < 0.01
VR2 = D * VS - B * IS
IR2 = -C * VS + A * IS
assert abs(VR2 - VR) / VR < 0.01 and abs(IR2 - IR) / abs(IR) < 0.02
# complex power at the sending end exceeds the receiving 320 MW
PS = 3 * (VS * np.conj(IS)).real
assert PS > 320e6
print("PASS EE-111-05-4")
