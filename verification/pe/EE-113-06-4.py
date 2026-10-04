"""EE-113-06-4 (conditional): initial symmetrical subtransient fault at F, Sb = 3 MVA.

Method: nodal admittance solution (all EMFs 1 pu in phase), branch currents through CB.
"""
import numpy as np

Xs, XT1 = 3 / 250, 0.05
XSM = 0.15 * 3 / 1 * (6.3 / 6.6) ** 2
XT2 = 0.035 * 3 / 0.75
XIM = 0.25 * 3 / 0.5
# nodes: 1 = 6.6 kV bus, F = fault (V=0)
Y11 = 1/(1j*(Xs+XT1)) + 1/(1j*XSM) + 1/(1j*XT2)
I1 = 1/(1j*(Xs+XT1)) + 1/(1j*XSM)
V1 = I1 / Y11
I_cb = V1 / (1j * XT2)
I_im = 1 / (1j * XIM)
Ib = 3e6 / (np.sqrt(3) * 480)
S_cb, S_f = 3 * abs(I_cb), 3 * abs(I_cb + I_im)
assert abs(S_cb - 15.475381) < 1e-5 and abs(S_f - 17.475381) < 1e-5
assert abs(abs(I_cb) * Ib / 1e3 - 18.613991) < 1e-5
assert abs(abs(I_cb + I_im) * Ib / 1e3 - 21.019617) < 1e-5
print("PASS EE-113-06-4")
