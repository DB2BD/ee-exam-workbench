"""EE-111-03-5 independent check: div/curl of F and line integral of 3x^2dx+2yz dy+y^2 dz."""
import mpmath as mp
import sympy as sp

x, y, z, t = sp.symbols("x y z t")
F = sp.Matrix([x**2 * y**3 * sp.sin(z), x**2 * y**2 * z**2, 4 * sp.cos(x * y * z)])
div = sum(sp.diff(F[i], v) for i, v in enumerate((x, y, z)))
assert sp.simplify(div - (2 * x * y**3 * sp.sin(z) + 2 * x**2 * y * z**2 - 4 * x * y * sp.sin(x * y * z))) == 0
curl = sp.Matrix([
    sp.diff(F[2], y) - sp.diff(F[1], z),
    sp.diff(F[0], z) - sp.diff(F[2], x),
    sp.diff(F[1], x) - sp.diff(F[0], y),
])
claimed = sp.Matrix([
    -4 * x * z * sp.sin(x * y * z) - 2 * x**2 * y**2 * z,
    x**2 * y**3 * sp.cos(z) + 4 * y * z * sp.sin(x * y * z),
    2 * x * y**2 * z**2 - 3 * x**2 * y**2 * sp.sin(z),
])
assert sp.simplify(curl - claimed) == sp.zeros(3, 1)
# (二) direct parametrization along two different paths (path independence)
G = sp.Matrix([3 * x**2, 2 * y * z, y**2])
def line(r):
    integrand = (G.subs({x: r[0], y: r[1], z: r[2]}).T * sp.diff(sp.Matrix(r), t))[0]
    return sp.integrate(sp.expand(integrand), (t, 0, 1))
straight = line([t, 1 - 2 * t, 2 + 5 * t])
curved = line([t**3, 1 - 2 * t**2, 2 + 5 * t])
assert straight == 6 and curved == 6
print("PASS EE-111-03-5")
