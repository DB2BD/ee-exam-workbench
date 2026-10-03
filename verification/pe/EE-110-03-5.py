"""EE-110-03-5 independent check: directional derivative of x^2y-xy^2+xz^2 at (1,-1,1) along (1,-2,1)."""
import sympy as sp

x, y, z, h = sp.symbols("x y z h")
f = x**2 * y - x * y**2 + x * z**2
g = sp.Matrix([f.diff(v) for v in (x, y, z)]).subs({x: 1, y: -1, z: 1})
u = sp.Matrix([1, -2, 1]) / sp.sqrt(6)
assert sp.simplify(g.dot(u) + sp.sqrt(6)) == 0
# Independent: limit definition along the line
p = sp.Matrix([1, -1, 1]) + h * u
D = sp.limit((f.subs({x: p[0], y: p[1], z: p[2]}) - f.subs({x: 1, y: -1, z: 1})) / h, h, 0)
assert sp.simplify(D + sp.sqrt(6)) == 0
print("PASS EE-110-03-5")
