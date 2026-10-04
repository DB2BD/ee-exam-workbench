"""EE-106-05-2: 3-bus balanced fault at bus 1 through Zf; no-load, EMFs = 1 pu.

Reactances (100 MVA pu): G1 0.1 + T1 0.1 at bus 1; G2 0.2 + T2 0.2 at bus 2;
lines 1-2 j0.8, 1-3 j0.4, 2-3 j0.4.  Zf is read as j0.11 (reactive).
"""
import numpy as np


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


def build():
    Y = np.zeros((3, 3), complex)

    def add(i, j, x):
        y = 1 / (1j * x)
        if j is None:
            Y[i, i] += y
        else:
            Y[i, i] += y; Y[j, j] += y; Y[i, j] -= y; Y[j, i] -= y

    add(0, None, 0.1 + 0.1)
    add(1, None, 0.2 + 0.2)
    add(0, 1, 0.8); add(0, 2, 0.4); add(1, 2, 0.4)
    return Y


Y = build()
Z = np.linalg.inv(Y)
close(Z[0, 0].imag, 0.16, 1e-9)
close(Z[2, 0].imag, 0.12, 1e-9)
Vf = 1.0   # no load: all bus voltages equal the common EMF
assert np.allclose(Z @ (Y @ np.ones(3)), np.ones(3))

Zf = 0.11j
If = Vf / (Z[0, 0] + Zf)
close(abs(If), 3.7037, 1e-4)
V = Vf - Z[:, 0] * If
close(abs(V[2]), 0.55556, 1e-4)
close(abs(V[0]), 0.40741, 1e-4)
close(abs(V[1]), 0.70370, 1e-4)
assert abs(V[0] - If * Zf) < 1e-12      # fault-bus voltage across Zf

# independent hand reduction: (1-3-2 path 0.4+0.4) || line 0.8 = 0.4; + gen branch 0.4 = 0.8
# Z11 = 0.2 || 0.8 = 0.16 ; with 1 A injected at bus 1: V1=0.16, V2=V1*0.4/0.8, V3=(V1+V2)/2
z11 = 0.2 * 0.8 / (0.2 + 0.8)
v2h = z11 * 0.4 / 0.8
v3h = (z11 + v2h) / 2
close(z11, Z[0, 0].imag, 1e-9)
close(v2h, Z[1, 0].imag, 1e-9)
close(v3h, Z[2, 0].imag, 1e-9)
# nodal KCL with source currents and fault current
src = np.array([1 / 0.2j, 1 / 0.4j, 0])
src[0] -= If
assert np.allclose(Y @ V, src, atol=1e-12)
print("PASS EE-106-05-2")
