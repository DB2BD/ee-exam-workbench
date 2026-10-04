"""EE-106-03-3 independent check (official crop): y'' + 4y' + 4y = 2 e^{-2x} / x^2."""
import sympy as sp

x = sp.symbols("x", positive=True)
C1, C2 = sp.symbols("C1 C2")
y = C1 * sp.exp(-2 * x) + C2 * x * sp.exp(-2 * x) - 2 * sp.exp(-2 * x) * sp.log(x)
res = y.diff(x, 2) + 4 * y.diff(x) + 4 * y - 2 * sp.exp(-2 * x) / x**2
assert sp.simplify(res) == 0
# Variation of parameters ingredients: y1=e^{-2x}, y2=x e^{-2x}, W=e^{-4x}
y1, y2 = sp.exp(-2 * x), x * sp.exp(-2 * x)
W = sp.simplify(y1 * y2.diff(x) - y2 * y1.diff(x))
assert sp.simplify(W - sp.exp(-4 * x)) == 0
g = 2 * sp.exp(-2 * x) / x**2
u1 = sp.integrate(sp.simplify(-y2 * g / W), x)
u2 = sp.integrate(sp.simplify(y1 * g / W), x)
yp = sp.simplify(u1 * y1 + u2 * y2)
assert sp.simplify(yp.diff(x, 2) + 4 * yp.diff(x) + 4 * yp - g) == 0
# u1' = -2/x, u2' = 2/x^2
assert sp.simplify(sp.diff(u1, x) + 2 / x) == 0 and sp.simplify(sp.diff(u2, x) - 2 / x**2) == 0
print("PASS EE-106-03-3")
