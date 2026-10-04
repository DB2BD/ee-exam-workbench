"""EE-105-01-5: series C-L with output across R: band-pass, w0 = 1000 rad/s, BW = 100 rad/s, C = 1 uF."""
import numpy as np
C, w0, BW = 1e-6, 1000.0, 100.0
L = 1 / (w0**2 * C)
R = BW * L
assert abs(L - 1) < 1e-9 and abs(R - 100) < 1e-6
# numeric check of |H| = R/|R + j(wL - 1/wC)| : peak at w0, -3 dB at w0 +- BW/2 band edges
H = lambda w: abs(R / (R + 1j * (w * L - 1 / (w * C))))
w = np.linspace(100, 3000, 2_000_001)
h = np.array([H(x) for x in w[::1000]])
ws = w[::1000]
assert abs(ws[np.argmax(h)] - w0) < 2
edges = ws[h >= 1 / np.sqrt(2)]
assert abs((edges[-1] - edges[0]) - BW) < 1.5
print("PASS EE-105-01-5")
