"""EE-110-03-2 independent check: y' = y^2 e^{-2x}."""
import sympy as sp

x, C = sp.symbols("x C")
y = sp.Function("y")
sol = sp.dsolve(sp.Eq(y(x).diff(x), y(x) ** 2 * sp.exp(-2 * x)))
claimed = 1 / (C + sp.exp(-2 * x) / 2)
assert sp.simplify(claimed.diff(x) - claimed**2 * sp.exp(-2 * x)) == 0
# dsolve family must be the same one-parameter family: 1/y + ... is linear in e^{-2x}
inv = sp.simplify(1 / sol.rhs)
assert sp.simplify(sp.diff(inv, x) - sp.diff(1 / claimed, x)) == 0
# zero solution
assert sp.diff(sp.Integer(0), x) == 0
print("PASS EE-110-03-2")
