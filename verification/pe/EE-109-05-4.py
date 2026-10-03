"""EE-109-05-4: sequence Thevenin impedances at bus 1, 3-phase and b-c faults.

Givens (official crop table): G1 0.2/0.2/0.05, G2 0.1/0.1/0.05,
T1 0.25 (all), T2 0.3 (all), line 1-2 0.4/0.4/0.5.
Figure: T1 delta on G1 side (bus 3), grounded Y on bus 1; T2 grounded Y on
bus 2, delta on G2 side (bus 4); generator neutrals grounded.
"""
import numpy as np

par = lambda a, b: a * b / (a + b)
Z1 = par(0.2 + 0.25, 0.4 + 0.3 + 0.1)
Z2 = Z1
Z0 = par(0.25, 0.5 + 0.3)  # generators isolated by the delta windings
assert abs(Z1 - 0.288) < 1e-12 and abs(Z0 - 0.190476) < 1e-6
If3 = 1 / (1j * Z1)
assert abs(If3 - (-3.4722j)) < 1e-4
Ia1 = 1 / (1j * (Z1 + Z2))
a = np.exp(2j * np.pi / 3)
Ib = (a * a - a) * Ia1
Ic = -Ib
assert abs(Ib - (-3.0070)) < 1e-4

# Method 2: phase-domain check of the b-c fault: build sequence voltages and
# confirm Vb = Vc, Ia = 0 with the Thevenin model.
V1 = 1 - 1j * Z1 * Ia1
V2 = -1j * Z2 * (-Ia1)
A = np.array([[1, 1, 1], [1, a * a, a], [1, a, a * a]])
Vabc = A @ np.array([0, V1, V2])
Iabc = A @ np.array([0, Ia1, -Ia1])
assert abs(Vabc[1] - Vabc[2]) < 1e-12 and abs(Iabc[0]) < 1e-12
assert abs(abs(Iabc[1]) - np.sqrt(3) / 2 * abs(If3)) < 1e-9
# Ybus-style: Z1 via admittance sum
assert abs(1 / (1 / 0.45 + 1 / 0.8) - Z1) < 1e-12
print("PASS EE-109-05-4")
