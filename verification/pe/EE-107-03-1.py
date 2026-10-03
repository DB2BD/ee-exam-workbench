"""EE-107-03-1 independent check (official crop): 3(1+t^2) y' = 2 t y (y^3 - 1), y(0)=2."""
import sympy as sp

t, C = sp.symbols("t C")
y = sp.Function("y")
ode = sp.Eq(3 * (1 + t**2) * y(t).diff(t), 2 * t * y(t) * (y(t) ** 3 - 1))
# Claimed implicit general integral: 1 - y^-3 = C (1+t^2)  <=>  y^3 = 1/(1 - C(1+t^2))
Y = (1 / (1 - C * (1 + t**2))) ** sp.Rational(1, 3)
res = 3 * (1 + t**2) * Y.diff(t) - 2 * t * Y * (Y**3 - 1)
assert sp.simplify(res) == 0
# y(0)=2 -> C = 7/8
Cval = sp.solve(sp.Eq(Y.subs(t, 0), 2), C)
assert Cval == [sp.Rational(7, 8)]
Yp = Y.subs(C, sp.Rational(7, 8))
assert sp.simplify(Yp**3 - 8 / (1 - 7 * t**2)) == 0
for tv in (0, 0.1, -0.2, 0.3, 0.37):
    a = float(Yp.subs(t, tv))
    b = 2 * (1 - 7 * tv**2) ** (-1 / 3)
    assert abs(a - b) / b <= 0.005
# Singular (constant) solutions
for c in (0, 1):
    assert (3 * (1 + t**2) * 0 - 2 * t * c * (c**3 - 1)) == 0
# Independent: w = y^-3 satisfies the linear ODE w' = 2t/(1+t^2) (w - 1)
wsol = sp.Integer(1) - sp.Rational(7, 8) * (1 + t**2)
wexpr = 1 / Yp**3
assert sp.simplify(wexpr - wsol) == 0
assert sp.simplify(wsol.diff(t) - 2 * t / (1 + t**2) * (wsol - 1)) == 0
print("PASS EE-107-03-1")
