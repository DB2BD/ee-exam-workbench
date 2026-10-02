"""EE-113-04-5: 240 V, 60 Hz capacitor-start motor at standstill,
Zm = 3.5 + j6.2, Za = 7.2 + j4.8 ohm."""
import numpy as np

V, w = 240.0, 2 * np.pi * 60
Zm, Za = 3.5 + 6.2j, 7.2 + 4.8j
Im = V / Zm

def gap(Xc):                                 # phase(Ia) - phase(Im) - 90 deg
    Ia = V / (Za - 1j * Xc)
    return np.angle(Ia) - np.angle(Im) - np.pi / 2

lo, hi = 0.1, 50.0                           # bisection root, not the tan formula
for _ in range(200):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if gap(lo) * gap(mid) > 0 else (lo, mid)
Xc = (lo + hi) / 2
C = 1 / (w * Xc)
assert abs(C * 1e6 - 299.236) / 299.236 <= 0.005

def torque(Ia):                              # T ~ |Im||Ia| sin(angle between)
    return abs(Im) * abs(Ia) * np.sin(np.angle(Ia) - np.angle(Im))

ratio = torque(V / (Za - 1j * Xc)) / torque(V / Za)
assert abs(ratio - 2.31609) / 2.31609 <= 0.005
# independent: torque ~ Im(Ia * conj(Im)) cross-product form
cross = lambda Ia: (Ia * np.conj(Im)).imag
assert abs(cross(V / (Za - 1j * Xc)) / cross(V / Za) - ratio) < 1e-9
print(f"Xc={Xc:.6f} C={C*1e6:.3f} uF ratio={ratio:.5f}")
print("PASS EE-113-04-5")
