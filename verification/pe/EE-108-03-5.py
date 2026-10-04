"""EE-108-03-5 independent check (official crop): contour integral of dz/(z^2-1) on two unit circles."""
import numpy as np
import sympy as sp

z = sp.symbols("z")
f = 1 / (z**2 - 1)
assert sp.residue(f, z, 1) == sp.Rational(1, 2)
assert sp.residue(f, z, -1) == -sp.Rational(1, 2)


def contour(center, n=20000):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    zz = center + np.exp(1j * t)
    dz = 1j * np.exp(1j * t) * (2 * np.pi / n)
    return np.sum(dz / (zz**2 - 1))


for center, exact in ((1.0, 1j * np.pi), (-1.0, -1j * np.pi)):
    val = contour(center)
    # circle through z=0 and z=2 with centre 1 does not touch the poles; check against numeric quadrature
    assert abs(val - exact) / abs(exact) <= 0.005, (center, val)
print("PASS EE-108-03-5")
