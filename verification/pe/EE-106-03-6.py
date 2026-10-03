"""EE-106-03-6 independent check (official crop): f = k x e^{-x} (x>0), 0 otherwise."""
import sympy as sp

x, k, u = sp.symbols("x k u", positive=True)
kval = sp.solve(sp.Eq(sp.integrate(k * x * sp.exp(-x), (x, 0, sp.oo)), 1), k)
assert kval == [1]
F = sp.integrate(u * sp.exp(-u), (u, 0, x))
assert sp.simplify(F - (1 - (1 + x) * sp.exp(-x))) == 0
# Independent: F is increasing from 0 to 1 and F' = f
assert sp.simplify(F.diff(x) - x * sp.exp(-x)) == 0
assert F.subs(x, 0) == 0 and sp.limit(F, x, sp.oo) == 1
print("PASS EE-106-03-6")
