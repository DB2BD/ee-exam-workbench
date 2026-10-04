"""EE-105-03-1 independent check (official crop): ODE whose general solution is y=e^{3x}(2+c1 sin x+c2 cos x)."""
import sympy as sp

x, c1, c2, r = sp.symbols("x c1 c2 r")
y = sp.exp(3 * x) * (2 + c1 * sp.sin(x) + c2 * sp.cos(x))
# homogeneous part e^{3x}(c1 sin x + c2 cos x): roots 3 +/- i
char = sp.expand((r - (3 + sp.I)) * (r - (3 - sp.I)))
assert char == r**2 - 6 * r + 10
# particular solution 2e^{3x}: L[2e^{3x}] = 2(9-18+10)e^{3x}
rhs = sp.simplify(2 * (9 - 18 + 10) * sp.exp(3 * x))
assert sp.simplify(rhs - 2 * sp.exp(3 * x)) == 0
# direct substitution of the whole family (arbitrary c1, c2)
res = sp.simplify(sp.diff(y, x, 2) - 6 * sp.diff(y, x) + 10 * y - 2 * sp.exp(3 * x))
assert res == 0
# the family has two free constants: Wronskian of the homogeneous basis is nonzero
u, v = sp.exp(3 * x) * sp.sin(x), sp.exp(3 * x) * sp.cos(x)
W = sp.simplify(u * sp.diff(v, x) - v * sp.diff(u, x))
assert sp.simplify(W + sp.exp(6 * x)) == 0
print("PASS EE-105-03-1")
