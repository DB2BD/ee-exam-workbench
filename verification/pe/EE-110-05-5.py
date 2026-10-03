"""EE-110-05-5: voltage regulation and equal-area sudden Pm step.

Givens (official crop): 3-ph Y 2500 kVA 6600 V, Xs = 8 ohm/phase,
full load pf 0.8 lag; P = Pmax sin(delta); delta0 = 10 deg, no damping.
"""
import numpy as np
import sympy as sp

V = 6600 / np.sqrt(3)
I = 2500e3 / (np.sqrt(3) * 6600)
E = V + 8j * I * np.exp(-1j * np.arccos(0.8))
VR = (abs(E) - V) / V * 100
assert abs(abs(E) - 5057.76) < 0.05
assert abs(VR - 32.73) < 0.01

d0 = np.radians(10)
x = sp.symbols("x")
d1 = float(sp.nsolve(sp.sin(x) * (sp.pi - x - d0) - sp.cos(d0) - sp.cos(x), x, 0.8))
ratio = np.sin(d1)
assert abs(np.degrees(d1) - 51.00) < 0.01
assert abs(ratio - 0.7772) < 5e-4
assert abs(ratio - np.sin(d0) - 0.6035) < 5e-4

# Method 2: integrate swing equation with Pm = ratio*Pmax (slightly below/above).
def max_angle(pm, dt=1e-4):
    d, w = d0, 0.0
    for _ in range(200000):
        w += (pm - np.sin(d)) * dt
        d += w * dt
        if w < 0:
            return d
        if d > np.pi:
            return None
    return d
assert max_angle(ratio * 0.995) is not None and max_angle(ratio * 1.005) is None
# with exact ratio the swing reaches pi - d1
assert abs(max_angle(ratio * 0.9999) - (np.pi - d1)) < 0.05
print("PASS EE-110-05-5")
