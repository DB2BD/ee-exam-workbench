"""EE-113-01-3 independent check: full 3x3 coupled branch-impedance solve (no balanced shortcut).

Givens (official crop): Delta, each branch R=1 ohm + L=2 H, mutual M=1 H between
every pair; dots at the L terminal adjacent to R, i.e. entered by the cyclic
branch currents a->b, b->c, c->a. v_ab = 110*sqrt2 sin(t+25°), positive sequence.
Sine-reference peak phasors.
"""
import cmath
import math
import numpy as np

w, R, L, M = 1.0, 1.0, 2.0, 1.0
a = cmath.exp(-2j * math.pi / 3)
Vab = 110 * math.sqrt(2) * cmath.exp(1j * math.radians(25))
Vbc, Vca = Vab * a, Vab * a**2
Z = np.full((3, 3), 1j * w * M) + np.diag([R + 1j * w * L - 1j * w * M] * 3)
Iab, Ibc, Ica = np.linalg.solve(Z, np.array([Vab, Vbc, Vca]))
Ia = Iab - Ica
assert abs(abs(Ia) - 110 * math.sqrt(3)) / (110 * math.sqrt(3)) < 5e-3, abs(Ia)
assert abs(math.degrees(cmath.phase(Ia)) - (-50)) < 0.05
print("PASS EE-113-01-3")
