"""EE-113-03-1 independent check: y'' - 4y' + 5y = e^{2x} csc x (official crop).

Note: the crop has a minus sign on 4y' and e^{+2x}.
"""
import sympy as sp

x, C1, C2 = sp.symbols("x C1 C2", real=True)
y = sp.exp(2 * x) * (C1 * sp.cos(x) + C2 * sp.sin(x) - x * sp.cos(x) + sp.sin(x) * sp.log(sp.sin(x)))
residual = sp.diff(y, x, 2) - 4 * sp.diff(y, x) + 5 * y - sp.exp(2 * x) / sp.sin(x)
assert sp.simplify(residual) == 0

# Independent: variation of parameters with the Wronskian of e^{2x}cos x, e^{2x}sin x.
y1, y2 = sp.exp(2 * x) * sp.cos(x), sp.exp(2 * x) * sp.sin(x)
g = sp.exp(2 * x) / sp.sin(x)
W = sp.simplify(y1 * sp.diff(y2, x) - y2 * sp.diff(y1, x))
assert sp.simplify(W - sp.exp(4 * x)) == 0
u1 = sp.integrate(sp.simplify(-y2 * g / W), x)
u2 = sp.integrate(sp.simplify(y1 * g / W), x)
yp = sp.simplify(u1 * y1 + u2 * y2)
target = sp.exp(2 * x) * (-x * sp.cos(x) + sp.sin(x) * sp.log(sp.sin(x)))
assert sp.simplify(yp - target) == 0
# characteristic roots 2 ± i
r = sp.symbols("r")
assert set(sp.solve(r**2 - 4 * r + 5, r)) == {2 + sp.I, 2 - sp.I}
print("PASS EE-113-03-1")
