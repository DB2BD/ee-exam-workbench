"""EE-107-01-5 independent check: balanced Y generator feeding a Delta load through line impedances.

Givens (official crop): positive sequence, internal phase voltage 120 V, generator impedance
0.2+j0.5 ohm/phase, line 0.3+j0.9 ohm/phase, Delta load 118.5+j85.8 ohm/phase.
Solved as a full three-phase network by loop currents in the Delta (no Delta-to-Y shortcut).
"""
import numpy as np

a = np.exp(-2j * np.pi / 3)
E = np.array([120, 120 * a, 120 * a**2], dtype=complex)        # Ean, Ebn, Ecn (positive sequence)
Zs = 0.2 + 0.5j + 0.3 + 0.9j                                  # generator + line per phase
ZD = 118.5 + 85.8j
# unknowns: line currents Ia, Ib, Ic (Ia+Ib+Ic=0) and Delta phase currents Iab, Ibc, Ica
# Delta voltages: Vab = Iab ZD ... ; Vab = (Ea - Ia Zs) - (Eb - Ib Zs)
A = np.zeros((7, 7), dtype=complex)
b = np.zeros(7, dtype=complex)
# x = [Ia, Ib, Ic, Iab, Ibc, Ica, dummy]
for k, (p, q, d) in enumerate([(0, 1, 3), (1, 2, 4), (2, 0, 5)]):
    A[k, d] = ZD
    A[k, p] = Zs
    A[k, q] = -Zs
    b[k] = E[p] - E[q]
for k, (p, d1, d2) in enumerate([(0, 3, 5), (1, 4, 3), (2, 5, 4)]):   # KCL: Ia = Iab - Ica ...
    A[3 + k, p] = 1
    A[3 + k, d1] = -1
    A[3 + k, d2] = 1
A[6, 6] = 1
x = np.linalg.solve(A, b)
Ia, Ib, Ic = x[:3]
def pol(z): return abs(z), np.degrees(np.angle(z))
for z, (m, ph) in zip((Ia, Ib, Ic), [(2.4, -36.87), (2.4, -156.87), (2.4, 83.13)]):
    assert abs(abs(z) - m) / m < 5e-3
    assert abs(np.degrees(np.angle(z)) - ph) < 0.05
assert abs(Ia + Ib + Ic) < 1e-9
# per-phase equivalent
Zy = ZD / 3
assert abs(Zy - (39.5 + 28.6j)) < 1e-9
assert abs((Zs + Zy) - (40 + 30j)) < 1e-9
print("PASS EE-107-01-5")
