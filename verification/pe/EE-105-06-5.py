"""EE-105-06-5: harmonic equivalent circuit and parallel resonance at the 480 V bus."""
import numpy as np

Sb, Vb = 2.0, 0.480
Zb = Vb**2 / Sb
Zs = Sb / 100
Rs = Zs / np.sqrt(1 + 2.5**2)
Xs = 2.5 * Rs
assert abs(abs(complex(Rs, Xs)) - Zs) < 1e-12
RT = Rs * Zb
XT = (Xs + 0.06) * Zb
XC = Vb**2 / 0.6
C = 1 / (2 * np.pi * 60 * XC)
assert abs(RT - 0.000856) / 0.000856 < 0.005
assert abs(XT - 0.00905) / 0.00905 < 0.005
assert abs(XC - 0.384) / 0.384 < 0.005
assert abs(C - 6.908e-3) / 6.908e-3 < 0.005
# independent: resonance by scanning the imaginary part of the bus admittance (with RT included)
h = np.linspace(2, 12, 2_000_001)
Y = 1 / (RT + 1j * h * XT) + 1j * h / XC
hr = h[np.argmin(abs(Y.imag))]
assert abs(hr - 6.5135) / 6.5135 < 0.005
assert abs(60 * hr - 390.8) / 390.8 < 0.005
# kVA formula: h = sqrt(Ssc/Qc)
assert abs(np.sqrt(2000 / (Xs + 0.06) / 600) - hr) < 5e-3
print("PASS EE-105-06-5")
