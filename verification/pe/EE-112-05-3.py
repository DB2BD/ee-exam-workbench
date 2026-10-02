"""EE-112-05-3 independent check: Ybus with off-nominal taps.

Givens (official crop): T1 Bus1-Bus3, X = j0.01, tap 0.8:1 (arrow at bus 1 side);
lines 3-4 j0.1 and j0.2; T2 Bus4-Bus2, X = j0.2, tap 1.25:1 (arrow at bus 4 side).
"""
import numpy as np

# Method: build Ybus from the ideal-transformer current relations
# (I_i = -I'_k / a, V' = V_i / a on the impedance side), via an incidence formulation.
def branch(y, a):
    # Two-port: ideal a:1 at bus i, series y toward bus k.
    # I_k = y (V_k - V_i/a);  I_i = -(1/a) * (-I_k)... derive numerically:
    Vi, Vk = np.eye(2)
    M = np.zeros((2, 2), complex)
    for col, (vi, vk) in enumerate(zip(Vi, Vk)):
        i_series = y * (vi / a - vk)  # current from tap side through y to k
        M[0, col] = i_series / a      # current injected at bus i
        M[1, col] = -i_series          # current injected at bus k
    return M

Y = np.zeros((4, 4), complex)
for (i, k), y, a in (((0, 2), 1 / 0.01j, 0.8), ((3, 1), 1 / 0.2j, 1.25), ((2, 3), 1 / 0.1j + 1 / 0.2j, 1.0)):
    M = branch(y, a)
    idx = [i, k]
    for r in range(2):
        for c in range(2):
            Y[idx[r], idx[c]] += M[r, c]

expected = np.array([
    [-156.25j, 0, 125j, 0],
    [0, -5j, 0, 4j],
    [125j, 0, -115j, 15j],
    [0, 4j, 15j, -18.2j],
])
assert np.allclose(Y, expected, rtol=0.005, atol=1e-9)
# Reciprocity: symmetric Ybus for lossless real-tap transformers.
assert np.allclose(Y, Y.T)
print("PASS EE-112-05-3")
