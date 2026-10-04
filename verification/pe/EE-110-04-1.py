"""EE-110-04-1: core lc = 45 cm, Ac = 15 cm^2, mu_r = 3300, N1 = 100, N2 = 85 in series,
I = 0.55 A dc.  Winding sense read from the crop (see note): N1 traversed downward,
N2 (same helix handedness) traversed upward -> fluxes up in left leg / down in right leg,
i.e. the same circulation -> cumulative (aiding) series.
"""
import numpy as np

# winding sense from the drawing: front-segment current direction (+x right) and
# axial field = z_hat x (front current)  (front face at +z)
z = np.array([0, 0, 1.0])
front_N1 = np.array([1.0, 0, 0])     # N1 front strokes carry current to the right
front_N2 = np.array([-1.0, 0, 0])    # N2 front strokes carry current to the left
B1 = np.cross(z, front_N1)           # +y : up in left leg
B2 = np.cross(z, front_N2)           # -y : down in right leg
# circulation sign (clockwise positive): up on left leg, down on right leg
circ1 = +B1[1]
circ2 = -B2[1]
assert circ1 > 0 and circ2 > 0      # aiding

mu = 3300 * 4e-7 * np.pi
lc, Ac, I = 0.45, 15e-4, 0.55
F = (100 + 85) * I
B = mu * F / lc
W = B**2 / (2 * mu) * Ac * lc
assert abs(B - 0.9377) / 0.9377 <= 0.005
assert abs(W * 1e3 - 71.56) / 71.56 <= 0.005
# independent: W = 1/2 L_total I^2 with L_total = (N1+N2)^2 / R
R = lc / (mu * Ac)
L = (100 + 85) ** 2 / R
assert abs(0.5 * L * I**2 - W) / W < 1e-12
# misread (differential) branch for the trap list
Bd = mu * 15 * I / lc
assert abs(Bd - 0.07603) / 0.07603 <= 0.005
print(f"R={R:.1f} F={F:.2f} B={B:.5f} T W={W*1e3:.3f} mJ L={L*1e3:.2f} mH (diff: {Bd:.5f} T)")
print("PASS EE-110-04-1")
