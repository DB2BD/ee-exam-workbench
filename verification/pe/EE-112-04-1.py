"""EE-112-04-1: mu_r = 950, l_c = 32 cm, A_c = 20 cm^2, N = 70, in series with
60 ohm across 220 V, 60 Hz."""
import numpy as np

mu0 = 4e-7 * np.pi
mur, lc, Ac, N, R, V, f = 950, 0.32, 20e-4, 70, 60.0, 220.0, 60.0
L = mu0 * mur * N**2 * Ac / lc
assert abs(L - 0.03656) / 0.03656 <= 0.005
w = 2 * np.pi * f
I = V / abs(R + 1j * w * L)
phi_max = L * I * np.sqrt(2) / N               # flux linkage = L i at the current peak
assert abs(phi_max - 2.640e-3) / 2.640e-3 <= 0.005
# independent: Faraday, V_L,peak = N w phi_max, and B = phi/A with H l = N i
VL = I * w * L
assert abs(np.sqrt(2) * VL / (N * w) - phi_max) < 1e-12
B = mu0 * mur * N * I * np.sqrt(2) / lc
assert abs(B * Ac - phi_max) < 1e-12
print(f"L={L*1e3:.3f} mH I={I:.4f} A phi_max={phi_max:.5e} Wb")
print("PASS EE-112-04-1")
