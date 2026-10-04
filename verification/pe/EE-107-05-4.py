"""EE-107-05-4: Y load Za=10, Zb=-j10, Zc=j10 ohm; source phase voltages
220<0, 220<-120, 220<120 V.  (1) 3P4W: I1, I2, I0, In.  (2) 3P3W: I1, I2, max line I, Vn.
"""
import numpy as np

a = np.exp(2j * np.pi / 3)
V = np.array([220, 220 * a**2, 220 * a])      # a^2 = <-120, a = <120
Z = np.array([10, -10j, 10j])


def close(x, y, tol=5e-3):
    assert abs(x - y) <= tol * max(abs(y), 1e-9), (x, y)


def seq(I):
    I0 = (I[0] + I[1] + I[2]) / 3
    I1 = (I[0] + a * I[1] + a**2 * I[2]) / 3
    I2 = (I[0] + a**2 * I[1] + a * I[2]) / 3
    return I0, I1, I2


# (1) four-wire, neutral solidly tied
I = V / Z
I0, I1, I2 = seq(I)
close(abs(I[0]), 22, 1e-9); close(abs(I[1]), 22, 1e-9); close(abs(I[2]), 22, 1e-9)
close(abs(I1), 7.3333, 1e-4)
close(abs(I2), 5.3684, 1e-4)
close(abs(I0), 20.035, 1e-3)
In = I.sum()
close(abs(In), 60.105, 1e-3)
close(abs(In), 3 * abs(I0), 1e-9)

# (2) three-wire, floating load neutral
Y = 1 / Z
Vn = (V * Y).sum() / Y.sum()
close(abs(Vn), 601.05, 1e-4)
I3 = (V - Vn) * Y
assert abs(I3.sum()) < 1e-9
J0, J1, J2 = seq(I3)
assert abs(J0) < 1e-9
close(abs(J1), 22.0, 1e-9)
close(abs(J2), 60.105, 1e-4)
close(np.max(np.abs(I3)), 73.613, 1e-4)
close(abs(I3[0]), 38.105, 1e-4)
# independent check: line currents from the two line-to-line KVL equations + KCL
Aeq = np.array([[1, 1, 1], [Z[0], -Z[1], 0], [0, Z[1], -Z[2]]], dtype=complex)
beq = np.array([0, V[0] - V[1], V[1] - V[2]])
Imesh = np.linalg.solve(Aeq, beq)
assert np.allclose(Imesh, I3)
print("PASS EE-107-05-4")
