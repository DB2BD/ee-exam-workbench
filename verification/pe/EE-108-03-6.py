"""EE-108-03-6 independent check (official crop): E[X]=2, E[X(X-4)]=5."""
import sympy as sp

EX2 = sp.symbols("EX2")
EX = 2
sol = sp.solve(sp.Eq(EX2 - 4 * EX, 5), EX2)
assert sol == [13]
var_x = sol[0] - EX**2
assert var_x == 9
assert -4 * EX + 10 == 2
var_y = 16 * var_x
assert var_y == 144 and sp.sqrt(var_y) == 12
# Independent: Var(Y)=E[Y^2]-E[Y]^2 with Y=-4X+10
EY2 = 16 * sol[0] - 80 * EX + 100
assert EY2 - 2**2 == 144
print("PASS EE-108-03-6")
