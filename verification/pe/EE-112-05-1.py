"""EE-112-05-1 independent check: transposed 4-bundle line L and C per km.

Givens (official crop): 4 conductors per phase (square bundle), spacing d = 50 cm,
diameter 3.5103 cm, GMR 1.4173 cm, horizontal Dab = Dbc = 15 m, Dac = 30 m.
"""
import numpy as np

eps0 = 8.854187817e-12
d, gmr, r = 0.5, 0.014173, 0.035103 / 2
phases = {"a": -15.0, "b": 0.0, "c": 15.0}
offsets = [(-d / 2, -d / 2), (d / 2, -d / 2), (-d / 2, d / 2), (d / 2, d / 2)]

# Method: brute-force GMR/GMD over every individual conductor pair.
def bundle_radius(self_r):
    prod = 1.0
    for i, (xi, yi) in enumerate(offsets):
        for j, (xj, yj) in enumerate(offsets):
            prod *= self_r if i == j else np.hypot(xi - xj, yi - yj)
    return prod ** (1 / 16)

def gmd(p, q):
    prod = 1.0
    for xi, yi in offsets:
        for xj, yj in offsets:
            prod *= np.hypot(phases[p] + xi - phases[q] - xj, yi - yj)
    return prod ** (1 / 16)

Deq = (gmd("a", "b") * gmd("b", "c") * gmd("c", "a")) ** (1 / 3)
L = 2e-7 * np.log(Deq / bundle_radius(gmr)) * 1e3 * 1e3  # mH/km
C = 2 * np.pi * eps0 / np.log(Deq / bundle_radius(r)) * 1e3 * 1e6  # uF/km
assert abs(L - 0.8873) / 0.8873 <= 0.005
assert abs(C - 0.01269) / 0.01269 <= 0.005
# Centre-to-centre approximation used in the hand solution.
assert abs(Deq - (15 * 15 * 30) ** (1 / 3)) / 18.9 <= 0.005
print("PASS EE-112-05-1")
