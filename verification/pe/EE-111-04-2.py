"""EE-111-04-2: wound-rotor IM, T = 207.63 s / (s^2 + 0.0925 s + 0.0382), 4 pole 60 Hz."""
import sympy as sp

s = sp.symbols("s", positive=True)
T = 207.63 * s / (s**2 + 0.0925 * s + 0.0382)
ns = 120 * 60 / 4
roots = sorted(float(x) for x in sp.solve(sp.Eq(T, 100), s))
s1 = [x for x in roots if 0 < x < 1][0]
n1 = ns * (1 - s1)
assert abs(n1 - 1765.0) / 1765.0 <= 0.005
# (2) R2 -> 2R2: torque depends on R2/s only -> s2 = 2 s1
Rr, R1, X, V, w = sp.symbols("R_2 R_1 X V omega", positive=True)
Tgen = 3 * V**2 * (Rr / s) / (w * ((R1 + Rr / s) ** 2 + X**2))
assert sp.simplify(Tgen.subs({Rr: 2 * Rr, s: 2 * s}) - Tgen) == 0
s2 = 2 * s1
n2 = ns * (1 - s2)
assert abs(n2 - 1730.0) / 1730.0 <= 0.005
assert abs((n2 - n1) - (-35.0)) / 35.0 <= 0.005
# independent check: given formula with R2 doubled evaluated at s2 equals 100 N.m
# (T_new(s) = T_old(s/2))
assert abs(float(T.subs(s, s2 / 2)) - 100) < 1e-6
# (3) 1700 rpm
s3 = 1 - 1700 / ns
ratio = s3 / s1
assert abs(ratio - 2.857) / 2.857 <= 0.005
print(f"s1={s1:.7f} n1={n1:.3f} n2={n2:.3f} ratio={ratio:.5f}")
print("PASS EE-111-04-2")
