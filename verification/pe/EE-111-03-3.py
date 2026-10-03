"""EE-111-03-3 independent check: contour |z|=2.5 ccw."""
import mpmath as mp
import sympy as sp

z = sp.symbols("z")
f1 = (2 * z + 1) / ((z + 3) * (z - 1))
f2 = (2 * z + 1) / ((z + 3) * (z - 1) ** 2)
I1 = 2 * sp.pi * sp.I * sum(sp.residue(f1, z, p) for p in (1,))
I2 = 2 * sp.pi * sp.I * sum(sp.residue(f2, z, p) for p in (1,))
assert sp.simplify(I1 - 3 * sp.pi * sp.I / 2) == 0
assert sp.simplify(I2 - 5 * sp.pi * sp.I / 8) == 0
# Independent: numerical contour integral
def contour(g):
    gl = sp.lambdify(z, g, "mpmath")
    return mp.quad(lambda th: gl(2.5 * mp.exp(1j * th)) * 2.5j * mp.exp(1j * th), mp.linspace(0, 2 * mp.pi, 17))
assert abs(contour(f1) - 1.5j * mp.pi) < 1e-9
assert abs(contour(f2) - 0.625j * mp.pi) < 1e-9
print("PASS EE-111-03-3")
