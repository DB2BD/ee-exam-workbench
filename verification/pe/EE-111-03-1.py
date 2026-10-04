"""EE-111-03-1 independent check: (x^2-x)y'' - 2x y' + 2y = 0, y1 = x."""
import sympy as sp

x = sp.symbols("x", positive=True)
L = lambda f: sp.simplify((x**2 - x) * sp.diff(f, x, 2) - 2 * x * sp.diff(f, x) + 2 * f)
assert L(x) == 0
# Reduction of order: P = -2x/(x^2-x) = -2/(x-1)
P = -2 * x / (x**2 - x)
y2 = sp.simplify(x * sp.integrate(sp.simplify(sp.exp(-sp.integrate(P, x)) / x**2), x))
claimed = x**2 - 2 * x * sp.log(x) - 1
assert L(claimed) == 0
assert sp.simplify(sp.diff(y2 / x, x) - sp.diff(claimed / x, x)) == 0  # same up to multiple of y1
# Independent: Wronskian of x and claimed equals Abel's formula C(x-1)^2
W = sp.simplify(x * sp.diff(claimed, x) - claimed)
assert sp.simplify(W - (x - 1) ** 2) == 0
# Independent numeric check: mpmath ODE solver from x=2 with data of y2, compare at x=5
import mpmath as mp
f2 = sp.lambdify(x, claimed, "mpmath"); d2 = sp.lambdify(x, sp.diff(claimed, x), "mpmath")
sol = mp.odefun(lambda xx, Y: [Y[1], (2 * xx * Y[1] - 2 * Y[0]) / (xx**2 - xx)], 2, [f2(2), d2(2)])
assert abs(sol(5)[0] - f2(5)) / abs(f2(5)) < 1e-8
print("PASS EE-111-03-1")
