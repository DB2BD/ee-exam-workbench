"""EE-110-04-4: 3 hp, 180 V PMDC motor, Ra = 2.01 ohm, no-load 4200 rpm, losses neglected."""
import numpy as np

V, Ra, P = 180.0, 2.01, 3 * 746.0
k = V / 4200                                  # V per rpm (no-load Ia = 0)
roots = np.roots([Ra, -V, P])                 # Ea Ia = (V - Ra Ia) Ia = P
Ia = roots.min()
Ea = V - Ra * Ia
n = Ea / k
T = P / (n * 2 * np.pi / 60)
assert abs(Ia - 14.919) / 14.919 <= 0.005
assert abs(Ea - 150.01) / 150.01 <= 0.005
assert abs(n - 3500.3) / 3500.3 <= 0.005
assert abs(T - 6.106) / 6.106 <= 0.005
# independent: T = K Ia with K = Ea/omega from the no-load point
K = V / (4200 * 2 * np.pi / 60)
assert abs(K * Ia - T) < 1e-9
# rejected root: Ia = 74.6 A, efficiency Ea/V = 16.7 %
assert abs(roots.max() - 74.63) / 74.63 <= 0.005
print(f"Ia={Ia:.4f} Ea={Ea:.4f} n={n:.2f} T={T:.4f} K={K:.5f}")
print("PASS EE-110-04-4")
