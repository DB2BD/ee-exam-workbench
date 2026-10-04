"""EE-105-05-2: two Gauss-Seidel iterations on the 3-bus system of the figure.

Figure: bus1 swing V1=1.04<0, y13=-j8 (bus1-bus3), y23=-j12 (bus2-bus3), no 1-2 line.
Loads: S2 = -(0.6+j0.5), S3 = -(0.9+j0.8) pu.  Flat start V2=V3=1<0.
"""
import numpy as np

V1 = 1.04
y13, y23 = -8j, -12j
Y22, Y33 = y23, y13 + y23          # -j12, -j20
Y23 = -y23                         # +j12
Y31 = -y13                         # +j8
S2, S3 = complex(-0.6, -0.5), complex(-0.9, -0.8)


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


assert Y33 == -20j and Y23 == 12j and Y31 == 8j

v2 = v3 = 1 + 0j
hist = []
for k in range(2):
    v2 = (np.conj(S2) / np.conj(v2) - Y23 * v3) / Y22
    v3 = (np.conj(S3) / np.conj(v3) - Y23 * v2 - Y31 * V1) / Y33
    hist.append((v2, v3))

(v21, v31), (v22, v32) = hist
close(v21.real, 0.958333); close(v21.imag, -0.05)
close(v31.real, 0.951); close(v31.imag, -0.075)
close(abs(v22), 0.913486); close(np.degrees(np.angle(v22)), -7.8504)
close(abs(v32), 0.921111); close(np.degrees(np.angle(v32)), -7.3973)

# independent residual check: bus-power mismatch after iteration 2
Vv = np.array([V1, v22, v32])
# Y-bus built from series admittances y=-jb: Y_ii = sum y, Y_ij = -y_ij
Y = np.array([[-8j, 0, 8j], [0, -12j, 12j], [8j, 12j, -20j]])
S_inj = Vv * np.conj(Y @ Vv)
mis2, mis3 = abs(S_inj[1] - S2), abs(S_inj[2] - S3)
assert mis2 > 1e-3 and mis3 > 1e-3  # two iterations are not converged; just record it

# converged solution as reference (not asked)
a, b = v22, v32
for _ in range(2000):
    a = (np.conj(S2) / np.conj(a) - Y23 * b) / Y22
    b = (np.conj(S3) / np.conj(b) - Y23 * a - Y31 * V1) / Y33
print("converged", abs(a), np.degrees(np.angle(a)), abs(b), np.degrees(np.angle(b)))
print("PASS EE-105-05-2")
