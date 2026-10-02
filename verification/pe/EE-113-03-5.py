"""EE-113-03-5 independent check.

(1) r(t) = [3t, 4t^2, 8t^4] (official crop): tangent and unit tangent.
(2) Flux of F = 7x i + 3y j - z k out of x^2+y^2+z^2 = 9.
"""
import numpy as np
import sympy as sp

t = sp.symbols("t", real=True)
r = sp.Matrix([3 * t, 4 * t**2, 8 * t**4])
rp = r.diff(t)
assert rp == sp.Matrix([3, 8 * t, 32 * t**3])
speed2 = sp.expand(rp.dot(rp))
assert speed2 == 9 + 64 * t**2 + 1024 * t**6
T = rp / sp.sqrt(speed2)
assert sp.simplify(T.dot(T) - 1) == 0

x, y, z, th, ph = sp.symbols("x y z theta phi", real=True)
F = sp.Matrix([7 * x, 3 * y, -z])
div = sum(sp.diff(F[i], v) for i, v in enumerate((x, y, z)))
flux = div * sp.Rational(4, 3) * sp.pi * 3**3
assert flux == 324 * sp.pi

# Independent: direct surface integral on the sphere of radius 3.
R = 3
pos = sp.Matrix([R * sp.sin(th) * sp.cos(ph), R * sp.sin(th) * sp.sin(ph), R * sp.cos(th)])
normal_dA = pos.diff(th).cross(pos.diff(ph))  # outward for theta in (0, pi)
Fs = F.subs({x: pos[0], y: pos[1], z: pos[2]})
direct = sp.integrate(sp.integrate(sp.simplify(Fs.dot(normal_dA)), (ph, 0, 2 * sp.pi)), (th, 0, sp.pi))
assert sp.simplify(direct - 324 * sp.pi) == 0
print("PASS EE-113-03-5")
