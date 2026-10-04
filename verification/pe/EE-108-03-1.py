"""EE-108-03-1 independent check (official crop): (a+x)^2 y'' - 2y = 3(a+x)^2 + 1."""
import sympy as sp

u, C1, C2 = sp.symbols("u C1 C2", positive=True)
y = sp.Function("y")
# Substituting u = a + x gives d/dx = d/du, so the ODE is Euler type in u.
ode = sp.Eq(u**2 * y(u).diff(u, 2) - 2 * y(u), 3 * u**2 + 1)
sol = sp.dsolve(ode, y(u)).rhs
claimed = C1 * u**2 + C2 / u + u**2 * sp.log(u) - sp.Rational(1, 2)
# Residual check of the claimed general solution (does not rely on dsolve's form).
res = u**2 * claimed.diff(u, 2) - 2 * claimed - (3 * u**2 + 1)
assert sp.simplify(res) == 0
# dsolve's family agrees with claimed after renaming constants.
diff = sp.simplify(sol - claimed)
assert sp.simplify(diff.diff(u, 2) * u**2 - 2 * diff) == 0
# Indicial equation r(r-1)-2 = 0
r = sp.symbols("r")
assert set(sp.solve(r * (r - 1) - 2, r)) == {2, -1}
# Resonant particular piece for 3u^2: C u^2 ln u needs C = 1; constant piece -1/2.
Cc = sp.symbols("Cc")
p1 = Cc * u**2 * sp.log(u)
assert sp.solve(sp.simplify(u**2 * p1.diff(u, 2) - 2 * p1 - 3 * u**2), Cc) == [1]
assert sp.simplify(u**2 * 0 - 2 * sp.Rational(-1, 2) - 1) == 0
print("PASS EE-108-03-1")
