"""EE-108-01-4 independent check: coupled inductors, sinusoidal steady state, w = 2 rad/s.

Givens (official crop): v_s = 10*sqrt(2)*cos(2t) V in series with 1 ohm and primary L1 = 1 H,
secondary L2 = 1 H, M = 0.5 H, load 1 ohm || 1 F.  i1 enters the primary at the top
(undotted) terminal; the primary dot is at the bottom.  i2 flows to the right on the top
wire, i.e. it leaves the secondary at the top terminal, which carries the dot, so
i2 enters the undotted (bottom) terminal: both reference currents enter undotted
terminals, hence coupling terms are +jwM.
"""
import numpy as np

w = 2.0
L1 = L2 = 1.0
M = 0.5
ZL = 1 / (1 / 1.0 + 1j * w * 1.0)
Vs = 10 * np.sqrt(2)                      # peak phasor, cos reference
# mesh equations: unknowns I1, I2
A = np.array([[1 + 1j * w * L1, 1j * w * M],
              [1j * w * M, 1j * w * L2 + ZL]], dtype=complex)
I1, I2 = np.linalg.solve(A, np.array([Vs, 0]))
amp, ph = abs(I2), np.degrees(np.angle(I2))
assert abs(amp - 5) / 5 < 5e-3, amp
assert abs(ph - 135) < 0.1, ph
# the opposite (subtractive) polarity would give a different answer - guard against a silent sign choice
A_bad = A.copy(); A_bad[0, 1] = A_bad[1, 0] = -1j * w * M
J1, J2 = np.linalg.solve(A_bad, np.array([Vs, 0]))
assert abs(abs(J2) - 5) > 0.1 or abs(np.degrees(np.angle(J2)) - 135) > 1
print("PASS EE-108-01-4")
