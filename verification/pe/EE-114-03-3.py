"""EE-114-03-3 independent check: y'' + 4y' + 4y = 0, y(0) = 1, y'(0) = 3.

The crop prints the second condition as y^(1) = 3; read as y'(0) = 3.
"""
import sympy as sp

t = sp.symbols("t")
y = sp.Function("y")
sol = sp.dsolve(sp.Eq(y(t).diff(t, 2) + 4 * y(t).diff(t) + 4 * y(t), 0), y(t),
                ics={y(0): 1, y(t).diff(t).subs(t, 0): 3}).rhs
expected = (1 + 5 * t) * sp.exp(-2 * t)
assert sp.simplify(sol - expected) == 0

# Independent: Laplace transform route, (s^2+4s+4)Y = s*y0 + y1 + 4*y0.
s = sp.symbols("s", positive=True)
Y = (s * 1 + 3 + 4 * 1) / (s + 2) ** 2
assert sp.simplify(sp.inverse_laplace_transform(Y, s, t) - expected * sp.Heaviside(t)) == 0
print("PASS EE-114-03-3")
