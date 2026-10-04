"""EE-109-06-4: lumen-method lighting design.

Givens: 60 m x 30 m, height 10 m, E = 300 lx, CU = 0.52, M = 0.52, 400 W HPS 23000 lm, 2-lamp fixture.
"""
import math

A = 60 * 30
F = 2 * 23000
n = 300 * A / (F * 0.52 * 0.52)
assert abs(n - 43.41) / 43.41 < 0.005
N = math.ceil(n)
assert N == 44                                       # boxed 44 fixtures
rows, cols = 4, 11
assert rows * cols == N
e_avg = N * F * 0.52 * 0.52 / A
assert abs(e_avg - 304.05) / 304.05 < 0.005 and e_avg >= 300   # boxed 304.05 lx
sx, sy = 60 / cols, 30 / rows
assert abs(sx - 5.45) < 0.01 and sy == 7.5 and max(sx, sy) <= 1.0 * 10   # spacing <= ~1.0 H
# independent: illuminance per fixture area
assert abs(F * 0.52 * 0.52 / (sx * sy) - e_avg) < 1e-9
assert N * 2 * 400 == 35200
print("PASS EE-109-06-4")
