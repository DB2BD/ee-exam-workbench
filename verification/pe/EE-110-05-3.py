"""EE-110-05-3: simultaneous A-ground and B-C fault at feeder end.

Givens (official crop): E=1/0, X1=0.1 (feeder positive seq.),
Ia=-j9, Ib=-6.92 pu.  Fault conditions: Va=0, Vb=Vc, Ib+Ic=0.
"""
import numpy as np

a = np.exp(2j * np.pi / 3)
Ia, Ib = -9j, -6.92
Ic = -Ib
Ainv = np.array([[1, 1, 1], [1, a, a * a], [1, a * a, a]]) / 3
I0, I1, I2 = Ainv @ np.array([Ia, Ib, Ic])
close = lambda x, y: abs(x - y) <= 0.005 * abs(y)
assert close(I0, -3j) and close(I1, -6.9953j) and close(I2, 0.9953j)
V1 = 1 - 0.1j * I1
V2 = V1  # Vb = Vc  =>  V1 = V2
V0 = -(V1 + V2)  # Va = 0
assert close(V2, 0.30047)
X0 = (-V0 / I0 / 1j).real
assert close(X0, 0.2003)

# Method 2: rebuild phase voltages/currents from sequences and check the fault conditions
Aseq = np.array([[1, 1, 1], [1, a * a, a], [1, a, a * a]])
Vabc = Aseq @ np.array([V0, V1, V2])
Iabc = Aseq @ np.array([I0, I1, I2])
assert abs(Vabc[0]) < 1e-12 and abs(Vabc[1] - Vabc[2]) < 1e-12
assert abs(Iabc[1] + Iabc[2]) < 1e-12 and abs(Iabc[0] - Ia) < 1e-12
# implied Z2 is ~0.30 pu (positive, reactive) -> physically sensible
Z2 = -V2 / I2
assert 0.29 < Z2.imag < 0.31
print("PASS EE-110-05-3")
