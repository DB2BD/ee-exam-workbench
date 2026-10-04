"""EE-105-06-4: lumen method for a 30 m x 20 m factory."""
import math

A = 30 * 20
E, Cu, MF = 1500, 0.7, 0.65
phi_total = E * A / (Cu * MF)
lumens_per_fixture = 3 * 3000               # 3-40 W fixture, 3 lamps of 3000 lm
N = math.ceil(phi_total / lumens_per_fixture)
assert abs(phi_total - 1_978_022) / 1_978_022 < 0.005
assert N == 220
E_act = N * lumens_per_fixture * Cu * MF / A
assert abs(E_act - 1501.5) / 1501.5 < 0.005
assert (N - 1) * lumens_per_fixture * Cu * MF / A < E       # 219 fixtures fall short -> 220 is the minimum
# layout: 20 along the 30 m side x 11 along the 20 m side
nx, ny = 20, 11
assert nx * ny == N
sx, sy = 30 / nx, 20 / ny
assert max(sx, sy) <= 1.0 * 4               # spacing within 1.0 x mounting height (4 m)
assert max(sx, sy) / min(sx, sy) < 1.25
print("PASS EE-105-06-4")
