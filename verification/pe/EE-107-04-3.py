"""EE-107-04-3: 3-phase 4-pole Y induction motor 380 V 60 Hz, rated 1755 rpm.
Thevenin per phase: Vth = 210 V, Zth = 0.2 + j4.0, rotor Z_R = 0.8/s + j4.0."""
import numpy as np

Vth, Rth, Xth, R2, X2 = 210.0, 0.2, 4.0, 0.8, 4.0
ns = 120 * 60 / 4
ws = 2 * np.pi * ns / 60

def torque(s):
    I = Vth / ((Rth + R2 / s) + 1j * (Xth + X2))
    return 3 * abs(I) ** 2 * (R2 / s) / ws

s = 0.05
n = (1 - s) * ns
T5 = torque(s)
assert n == 1710
assert abs(T5 - 34.40) / 34.40 <= 0.005
smax = R2 / np.hypot(Rth, Xth + X2)
Tmax = torque(smax)
assert abs(smax - 0.1) / 0.1 <= 0.005
assert abs(Tmax - 42.78) / 42.78 <= 0.005
# closed form
Tmax_cf = 3 * Vth**2 / (2 * ws * (Rth + np.hypot(Rth, Xth + X2)))
assert abs(Tmax - Tmax_cf) < 1e-9
# independent: brute-force scan of the whole running range 0<s<=1
ss = np.linspace(1e-4, 1, 200001)
Ts = np.array([torque(x) for x in ss[::20]])
assert abs(Ts.max() - Tmax) / Tmax < 1e-4
assert abs(ss[::20][Ts.argmax()] - smax) < 1e-3
print(f"n={n} T(5%)={T5:.4f} smax={smax:.5f} Tmax={Tmax:.4f} (rated slip {(1800-1755)/1800:.3f})")
print("PASS EE-107-04-3")
