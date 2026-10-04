"""EE-105-06-2: induction motor starting voltage drop (per unit, Sb = 3000 kVA, Vb = 480 V)."""
import numpy as np

Pout = 2000 * 0.746e3
S_rated = Pout / 0.9 / 0.86
I_rated = S_rated / (np.sqrt(3) * 460)
I_start = 5.5 * I_rated
Ib = 3000e3 / (np.sqrt(3) * 480)
i = I_start / Ib * np.exp(-1j * np.arccos(0.1))
assert abs(abs(i) - 3.68768) / 3.68768 < 0.005
Xsys, XT = 3 / 500, 0.05                    # pure reactance (X/R not given)
def drop(X):
    return (1 - abs(1 - 1j * X * i)) * 100
d114, d480 = drop(Xsys), drop(Xsys + XT)
assert abs(d114 - 2.2013) / 2.2013 < 0.005
assert abs(d480 - 20.5206) / 20.5206 < 0.005
# independent: ohmic KVL at 480 V base using start impedance angle
Zb = 480**2 / 3000e3
V = 1 - 1j * (Xsys + XT) * i
assert abs(abs(V) - (1 - d480 / 100)) < 1e-12
Zm = (460 / 480) / abs(i) * np.exp(1j * np.arccos(0.1))      # constant-impedance branch
assert abs(abs(Zm) - 0.2599) < 5e-4
assert abs((1 - abs(1 - 1j * Xsys / (Zm + 1j * (Xsys + XT)))) * 100 - 1.89) < 0.02
assert abs((1 - abs(Zm / (Zm + 1j * (Xsys + XT)))) * 100 - 17.67) < 0.05
print("PASS EE-105-06-2")
