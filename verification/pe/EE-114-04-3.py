"""EE-114-04-3 (descriptive): two-phase rotating field from Fig. 3.

Read from the crop: M at top (x into page), M' bottom (dot), A at right (x),
A' left (dot).  Waveforms: i_A = Im sin(theta), i_M = -Im cos(theta),
ticks t_k at theta = 45 deg * k.
"""
import numpy as np

def field(pos_into, pos_out, current):
    """B direction at origin from two conductors (into / out of page)."""
    total = np.zeros(2)
    for pos, sign in ((pos_into, -1), (pos_out, +1)):     # current along +z * sign
        r = -np.array(pos, float)                        # wire -> origin
        cross = sign * current * np.array([-r[1], r[0]])  # z_hat x r
        total += cross / np.dot(r, r)
    return total

main_axis = field((0, 1), (0, -1), 1.0)
aux_axis = field((1, 0), (-1, 0), 1.0)
assert np.allclose(main_axis / np.linalg.norm(main_axis), [-1, 0])   # main: -x
assert np.allclose(aux_axis / np.linalg.norm(aux_axis), [0, 1])      # aux: +y

angles = []
for k in (1, 3, 5, 7):
    th = np.pi / 4 * k
    iM, iA = -np.cos(th), np.sin(th)
    assert np.isclose(abs(iM), 1 / np.sqrt(2)) and np.isclose(abs(iA), 1 / np.sqrt(2))
    phi = iM * np.array([-1, 0]) + iA * np.array([0, 1])
    assert np.isclose(np.linalg.norm(phi), 1.0)                       # |Phi| = Phi_m
    angles.append(np.degrees(np.arctan2(phi[1], phi[0])) % 360)
assert np.allclose(angles, [45, 135, 225, 315])                      # CCW
# swap A-A': aux component changes sign -> angle = -theta -> clockwise
rev = []
for k in (1, 3, 5, 7):
    th = np.pi / 4 * k
    phi = -np.cos(th) * np.array([-1, 0]) - np.sin(th) * np.array([0, 1])
    rev.append(np.degrees(np.arctan2(phi[1], phi[0])) % 360)
assert np.allclose(rev, [315, 225, 135, 45])
print("angles", angles, "reversed", rev)
print("PASS EE-114-04-3 (descriptive: field directions and rotation sense)")
