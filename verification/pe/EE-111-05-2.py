"""EE-111-05-2: bolted three-phase fault at bus 5 via the given Zbus.

Givens (official crop): Zbus (j-values, pu) as printed; line 1-2 j0.168;
prefault voltages 1.0 pu, load currents neglected.
Second method: build Ybus from the one-line diagram, invert, and compare.
"""
import numpy as np

close = lambda a, b, tol=0.005: abs(a - b) <= tol * abs(b)
Z = 1j * np.array([
    [0.0793, 0.0558, 0.0382, 0.0511, 0.0608],
    [0.0558, 0.1338, 0.0664, 0.0630, 0.0605],
    [0.0382, 0.0664, 0.0875, 0.0720, 0.0603],
    [0.0511, 0.0630, 0.0720, 0.2321, 0.1002],
    [0.0608, 0.0605, 0.0603, 0.1002, 0.1301],
])
k = 4  # bus 5
If = 1 / Z[k, k]
V = 1 - Z[:, k] / Z[k, k]
I21 = (V[1] - V[0]) / 0.168j
assert close(If, -7.6864j)
assert close(V[2].real, 0.53651) and abs(V[2].imag) < 1e-12
assert close(V[1].real, 0.53497) and close(V[0].real, 0.53267)
assert close(I21, -0.013725j)
assert close(abs(I21), 0.01373)

# Method 2: assemble Ybus from the diagram and invert.
branches = {(0, 1): 0.168, (1, 2): 0.126, (0, 4): 0.126, (4, 2): 0.210, (4, 3): 0.252, (3, 2): 0.336}
Y = np.zeros((5, 5), complex)
for (a, b), x in branches.items():
    y = 1 / (1j * x)
    Y[a, a] += y; Y[b, b] += y; Y[a, b] -= y; Y[b, a] -= y
Y[0, 0] += 1 / 0.1111j
Y[2, 2] += 1 / 0.1333j
Zc = np.linalg.inv(Y)
assert np.allclose(Zc.imag, Z.imag, atol=6e-5)
Vc = 1 - Zc[:, k] / Zc[k, k]
assert abs(Vc[2] - V[2]) < 5e-4
# branch current from the computed network: same order (rounding of Zbus to 4 d.p.)
I21c = (Vc[1] - Vc[0]) / 0.168j
assert abs(abs(I21c) - abs(I21)) < 2e-3
# KCL at bus 5 with the computed network: sum of line currents into bus 5 = fault current
inflow = (Vc[0] - Vc[4]) / 0.126j + (Vc[2] - Vc[4]) / 0.210j + (Vc[3] - Vc[4]) / 0.252j
assert abs(inflow - 1 / Zc[k, k]) < 1e-9
print("PASS EE-111-05-2")
