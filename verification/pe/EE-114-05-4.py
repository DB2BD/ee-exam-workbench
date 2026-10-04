"""EE-114-05-4 independent check: three-phase fault through Zf at bus 1.

Givens (official crop): G at bus 3 Xd'' = j0.1, transformer 3-1 Xt = j0.4,
line 1-2 XL = j0.2, G at bus 2 Xd'' = j0.1, E = 1∠0 for both (no load),
Zf = j0.0125 pu at bus 1.
"""
import numpy as np

# Method: nodal analysis with Norton sources (buses 1, 2, 3), Zbus column.
y_g = 1 / 0.1j
y_t = 1 / 0.4j
y_l = 1 / 0.2j
Ybus = np.array([
    [y_t + y_l, -y_l, -y_t],
    [-y_l, y_l + y_g, 0],
    [-y_t, 0, y_t + y_g],
])
Zbus = np.linalg.inv(Ybus)
Zth = Zbus[0, 0]
Zf = 0.0125j
If = 1.0 / (Zth + Zf)
V = np.ones(3) - Zbus[:, 0] * If  # superposition: prefault 1.0 everywhere
I31 = (V[2] - V[0]) * y_t
I21 = (V[1] - V[0]) * y_l

close = lambda a, b: abs(a - b) <= 0.005 * max(abs(b), 1e-12)
assert close(Zth, 0.1875j)
assert close(If, -5j)
assert close(V[0], 0.0625) and close(V[1], 0.6875) and close(V[2], 0.8125)
assert close(I31, -1.875j) and close(I21, -3.125j)
assert close(-I31, 1.875j) and close(-I21, 3.125j)
# KCL at bus 1 and fault-impedance voltage.
assert abs(I31 + I21 - If) < 1e-9
assert abs(V[0] - If * Zf) < 1e-9
print("PASS EE-114-05-4")
