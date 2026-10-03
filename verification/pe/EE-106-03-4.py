"""EE-106-03-4 independent check (official crop): y(t) = 1 - sinh t + int_0^t (1+tau) y(t-tau) dtau."""
import sympy as sp

t, s, tau = sp.symbols("t s tau", positive=True)
Y = sp.symbols("Y")
# Laplace transform of the kernel (1+t) and of the forcing 1 - sinh t
K = sp.laplace_transform(1 + t, t, s, noconds=True)
F = sp.laplace_transform(1 - sp.sinh(t), t, s, noconds=True)
Ysol = sp.simplify(sp.solve(sp.Eq(Y, F + K * Y), Y)[0])
assert sp.simplify(Ysol - s / (s**2 - 1)) == 0
ysol = sp.inverse_laplace_transform(Ysol, s, t)
assert sp.simplify(ysol.rewrite(sp.cosh) - sp.cosh(t)) == 0
# Independent: substitute y = cosh t back into the original equation
y = sp.cosh
lhs = y(t)
rhs = 1 - sp.sinh(t) + sp.integrate((1 + tau) * y(t - tau), (tau, 0, t))
assert sp.simplify((lhs - rhs).rewrite(sp.exp)) == 0
print("PASS EE-106-03-4")
