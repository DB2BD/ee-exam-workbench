"""EE-112-01-2 independent check: nodal analysis with the coupled-inductor inductance matrix.

Givens (official crop): vg = 660 cos(5000t) V; 34 ohm in series with L1 = 10 mH
(dot at its right end); L2 = 20 mH from top node to bottom (dot at its bottom end),
M = 8 mH; 100 ohm in parallel with L2. Peak phasors.
Coil currents are defined entering the dotted terminals, voltages measured dot(+) to undot(-).
"""
import numpy as np

w = 5000.0
Lm = np.array([[10e-3, 8e-3], [8e-3, 20e-3]])
Zm = 1j * w * Lm
# Unknowns: x = [iA, iB, V] with iA into L1's dotted (right) end, iB into L2's dotted (bottom) end,
# V = top-node voltage. Source-side current through 34 ohm, left->right, equals -iA.
# Coil 1: vA = V_right - V_left = V - (660 - 34*(-iA)) ; coil 2: vB = 0 - V.
A = np.zeros((3, 3), dtype=complex)
b = np.zeros(3, dtype=complex)
# coil 1 equation: Zm[0]@[iA,iB] = V - 660 - 34*iA
A[0] = [Zm[0, 0] + 34, Zm[0, 1], -1]; b[0] = -660
# coil 2 equation: Zm[1]@[iA,iB] = -V
A[1] = [Zm[1, 0], Zm[1, 1], 1]
# KCL at top node: current in from L1 (-iA) = current down L2 (-iB) + V/100
A[2] = [-1, 1, -1 / 100]
iA, iB, V = np.linalg.solve(A, b)
P = abs(V) ** 2 / (2 * 100)
assert abs(P - 612.5) / 612.5 < 5e-3, P
assert abs(V / 100 - 3.5) < 1e-9
print("PASS EE-112-01-2")
