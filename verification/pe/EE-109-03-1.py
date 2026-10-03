"""EE-109-03-1 independent check: y'' - 10y' + 25y = 75x + 20."""
import sympy as sp

x, C1, C2 = sp.symbols("x C1 C2")
y = sp.Function("y")
sol = sp.dsolve(y(x).diff(x, 2) - 10 * y(x).diff(x) + 25 * y(x) - 75 * x - 20)
claimed = (C1 + C2 * x) * sp.exp(5 * x) + 3 * x + 2
assert sp.simplify(claimed.diff(x, 2) - 10 * claimed.diff(x) + 25 * claimed - 75 * x - 20) == 0
assert sp.simplify(sol.rhs.subs({sp.Symbol("C1"): 0, sp.Symbol("C2"): 0}) - (3 * x + 2)) == 0
print("PASS EE-109-03-1")
