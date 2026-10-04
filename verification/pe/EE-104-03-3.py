"""EE-104-03-3 independent check (official crop): Cauchy PV of (3x+2)/(x(x-4)(x^2+9))."""
import mpmath as mp
import sympy as sp

x = sp.symbols("x", real=True)
f = (3 * x + 2) / (x * (x - 4) * (x**2 + 9))
pf = sp.apart(f)
R = sp.Rational
assert sp.simplify(pf - (-R(1, 18) / x + R(7, 50) / (x - 4) - (19 * x + 126) / (225 * (x**2 + 9)))) == 0
# PV = pi*i*(sum residues on real axis) + 2*pi*i*Res(3i)
z = sp.symbols("z")
fz = (3 * z + 2) / (z * (z - 4) * (z**2 + 9))
res0 = sp.residue(fz, z, 0)
res4 = sp.residue(fz, z, 4)
res3i = sp.residue(fz, z, 3 * sp.I)
pv = sp.simplify(sp.pi * sp.I * (res0 + res4) + 2 * sp.pi * sp.I * res3i)
assert sp.simplify(pv + 14 * sp.pi / 75) == 0
assert abs(float(pv) + 14 * float(sp.pi) / 75) < 1e-12
# brute-force symmetric exclusion around both real poles
mp.mp.dps = 30
g = lambda t: (3 * t + 2) / (t * (t - 4) * (t * t + 9))
e = mp.mpf("1e-9")
val = mp.quad(g, [-mp.inf, -1, -e]) + mp.quad(g, [e, 1, 4 - e]) + mp.quad(g, [4 + e, 5, mp.inf])
assert abs(val - (-14 * mp.pi / 75)) / abs(val) < 1e-6
# ordinary improper integral diverges: residues at the poles are nonzero
assert res0 != 0 and res4 != 0
print("PASS EE-104-03-3")
