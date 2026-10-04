"""EE-109-04-2: separately excited DC machine, Ra = 0.02, 125 V open circuit at 3000 rpm."""
import numpy as np

Ra = 0.02
k = 125 / 3000                       # V/rpm
# (1) generator 4000 rpm, Pout = Vt Ia = 21.5 kW
Ea1 = k * 4000
r = np.roots([Ra, -Ea1, 21500])
Ia1 = r.min()
Vt1 = Ea1 - Ra * Ia1
assert abs(Ia1 - 131.061) / 131.061 <= 0.005
assert abs(Vt1 - 164.05) / 164.05 <= 0.005
assert abs(r.max() - 8202.27) / 8202.27 <= 0.005
# (2) motor, Vt = 213 V, Pmech = Ea Ia = 21.5 kW
r2 = np.roots([Ra, -213, 21500])
Ia2 = r2.min()
Ea2 = 213 - Ra * Ia2
assert abs(Ia2 - 101.914) / 101.914 <= 0.005
# (3) torque
n2 = Ea2 / k
T = 21500 / (n2 * 2 * np.pi / 60)
assert abs(T - 40.55) / 40.55 <= 0.005
# independent: T = K_T Ia with K_T = 125 V / omega(3000 rpm)
KT = 125 / (3000 * 2 * np.pi / 60)
assert abs(KT * Ia2 - T) < 1e-9
assert abs(Vt1 * Ia1 - 21500) < 1e-6
print(f"Ia1={Ia1:.4f} Vt1={Vt1:.3f} (other root {r.max():.2f}) Ia2={Ia2:.4f} Ea2={Ea2:.3f} n={n2:.2f} T={T:.3f}")
print("PASS EE-109-04-2")
