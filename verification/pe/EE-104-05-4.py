"""EE-104-05-4: 3-bus network, line j0.1 (1-2), j0.2 (2-3), j0.25 (1-3); sources j0.4 at bus 1, j0.5 at bus 3.

Bus 2 no load: all bus voltages 1.25 pu (equal EMFs).  Then load Z=0.4+j0.3 at bus 2, then extra -j0.3 in parallel.
"""
import numpy as np


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


y12, y23, y13 = 1 / 0.1j, 1 / 0.2j, 1 / 0.25j
yg1, yg3 = 1 / 0.4j, 1 / 0.5j
Y = np.array([[y12 + y13 + yg1, -y12, -y13],
              [-y12, y12 + y23, -y23],
              [-y13, -y23, y13 + y23 + yg3]])
assert np.allclose(Y, np.array([[-16.5j, 10j, 4j], [10j, -15j, 5j], [4j, 5j, -11j]]))
Z = np.linalg.inv(Y)
close(Z[0, 0].imag, 0.245614, 1e-4); close(Z[1, 1].imag, 0.290351, 1e-4)
close(Z[2, 2].imag, 0.258772, 1e-4); close(Z[0, 1].imag, 0.228070, 1e-4)
close(Z[0, 2].imag, 0.192982, 1e-4); close(Z[1, 2].imag, 0.214912, 1e-4)
assert np.allclose(Z, Z.T)

# Method A: Thevenin at bus 2 with Z_bus
V0 = np.full(3, 1.25 + 0j)


def solve_zbus(Zl):
    I = V0[1] / (Zl + Z[1, 1])
    V = V0 - Z[:, 1] * I
    return V


V_a = solve_zbus(0.4 + 0.3j)
Zlc = 1 / (1 / (0.4 + 0.3j) + 1 / (-0.3j))
close(Zlc.real, 0.225, 1e-9); close(Zlc.imag, -0.3, 1e-9)
V_b = solve_zbus(Zlc)
close(abs(V_a[0]), 0.945996, 1e-4); close(abs(V_a[1]), 0.876453, 1e-4); close(abs(V_a[2]), 0.961631, 1e-4)
close(abs(V_b[0]), 1.816750, 1e-4); close(abs(V_b[1]), 2.081420, 1e-4); close(abs(V_b[2]), 1.764423, 1e-4)

# Method B: nodal solution with the sources as Norton currents E*yg and load admittance added to Y22
for Zl, Vref in ((0.4 + 0.3j, V_a), (Zlc, V_b)):
    Yn = Y.copy()
    Yn[1, 1] += 1 / Zl
    Inj = np.array([1.25 * yg1, 0, 1.25 * yg3])
    Vn = np.linalg.solve(Yn, Inj)
    assert np.allclose(Vn, Vref, atol=1e-9)
print("PASS EE-104-05-4")
