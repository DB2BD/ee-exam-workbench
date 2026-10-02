"""EE-112-03-5 independent check: F(t) = (cos t + t sin t, sin t - t cos t, t^2), t >= 0."""
import sympy as sp

t = sp.symbols("t", positive=True)
F = sp.Matrix([sp.cos(t) + t * sp.sin(t), sp.sin(t) - t * sp.cos(t), t**2])
Fp = sp.simplify(F.diff(t))
assert sp.simplify(Fp - t * sp.Matrix([sp.cos(t), sp.sin(t), 2])) == sp.zeros(3, 1)
speed = sp.sqrt(sp.simplify(Fp.dot(Fp)))
assert sp.simplify(speed - sp.sqrt(5) * t) == 0
T = sp.simplify(Fp / speed)
assert sp.simplify(T - sp.Matrix([sp.cos(t), sp.sin(t), 2]) / sp.sqrt(5)) == sp.zeros(3, 1)

# Method 1: kappa = |T'| / |F'|
k1 = sp.simplify(sp.sqrt(sp.simplify(T.diff(t).dot(T.diff(t)))) / speed)
# Method 2: kappa = |F' x F''| / |F'|^3
c = Fp.cross(F.diff(t, 2))
k2 = sp.simplify(sp.sqrt(sp.simplify(c.dot(c))) / speed**3)
assert sp.simplify(k1 - 1 / (5 * t)) == 0 and sp.simplify(k2 - 1 / (5 * t)) == 0
print("PASS EE-112-03-5")
