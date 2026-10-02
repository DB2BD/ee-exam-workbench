"""EE-113-05-1 independent check: parallel Δ/Y loads behind line impedance.

Givens (official crop): V_LL = 210 V balanced, Zl = 1 + j1 Ω per line,
Z_Δ = 24 - j30 Ω per phase, Z_Y = 12 + j5 Ω per phase.
"""
import numpy as np

Zl, ZD, ZY = 1 + 1j, 24 - 30j, 12 + 5j
VLL = 210.0
close = lambda a, b: abs(a - b) <= 0.005 * abs(b)

# Method 1: per-phase equivalent.
Zload = (ZD / 3) * ZY / (ZD / 3 + ZY)
Zin = Zl + Zload
Vph = VLL / np.sqrt(3)
I = Vph / Zin
S = 3 * Vph * np.conj(I)
assert close(Zload, 7.8118 - 2.0471j)
assert close(Zin, 8.8118 - 1.0471j)
assert close(abs(I), 13.663)
assert close(S.real, 4935.0) and close(S.imag, -586.40)
assert close(abs(S), 4969.7)
assert close(S.real / abs(S), 0.99301) and S.imag < 0  # leading

# Method 2: full three-phase mesh solved by nodal analysis (abc + Y neutral).
a = np.exp(2j * np.pi / 3)
Es = Vph * np.array([1, a**-1, a])  # source phase voltages, source neutral = 0
# Unknown node voltages: load buses A, B, C and Y-neutral N.
yl, yD, yY = 1 / Zl, 1 / ZD, 1 / ZY
Y = np.zeros((4, 4), complex)
J = np.zeros(4, complex)
for k in range(3):
    Y[k, k] += yl + 2 * yD + yY
    J[k] += yl * Es[k]
    for m in range(3):
        if m != k:
            Y[k, m] -= yD
    Y[k, 3] -= yY
    Y[3, k] -= yY
    Y[3, 3] += yY
V = np.linalg.solve(Y, J)
Iline = (Es - V[:3]) * yl
S3 = np.sum(Es * np.conj(Iline))
assert close(abs(Iline[0]), abs(I))
assert close(S3, S)
print("PASS EE-113-05-1")
