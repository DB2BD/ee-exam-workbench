"""EE-105-03-4 independent check (official crop): contour integral on |z|=2."""
import numpy as np
import sympy as sp

z = sp.symbols("z")
f = (z**2 - 2 * z + sp.I) / (z - 1 + sp.I)
z0 = 1 - sp.I
assert abs(complex(z0)) < 2
res = sp.simplify((z**2 - 2 * z + sp.I).subs(z, z0))
I = sp.expand(2 * sp.pi * sp.I * res)
assert sp.simplify(I - (-2 * sp.pi - 4 * sp.pi * sp.I)) == 0
# numerical contour integral
th = np.linspace(0, 2 * np.pi, 200001)
zz = 2 * np.exp(1j * th)
g = (zz**2 - 2 * zz + 1j) / (zz - 1 + 1j)
num = np.trapezoid(g * 2j * np.exp(1j * th), th)
assert abs(num - complex(-2 * np.pi, -4 * np.pi)) < 1e-6
print("PASS EE-105-03-4")
