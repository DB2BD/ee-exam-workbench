"""EE-106-06-5: harmonic parallel resonance, S_sc = 15.68 MVA, capacitor 320 kvar."""
import math

S_SC, QC = 15.68e6, 320e3
h = math.sqrt(S_SC / QC)
assert abs(h - 7.0) < 1e-12                                     # boxed
# independent: reactance route, X_s = V^2/S_sc, X_c = V^2/Qc, h X_s = X_c / h
V = 1.0
xs, xc = V**2 / S_SC, V**2 / QC
assert abs(xc / xs - 49.0) < 1e-9
assert abs(7 * xs - xc / 7) < 1e-18
# 6-pulse rectifier characteristic harmonics 6k +/- 1 contain 7
assert 7 in {6 * k + s for k in range(1, 5) for s in (-1, 1)}
print("PASS EE-106-06-5")
