"""EE-104-03-1 independent check (official crop): y''+4t y'-4y=0, y(0)=0, y'(0)=-7 via Laplace."""
import sympy as sp

s, t = sp.symbols("s t", positive=True)
Y = sp.Function("Y")
# L{y''}=s^2 Y+7 ; L{t y'}=-d/ds(sY)= -Y - sY' ; so s^2 Y + 7 + 4(-Y - sY') - 4Y = 0
eq = sp.Eq(s**2 * Y(s) + 7 - 4 * Y(s) - 4 * s * Y(s).diff(s) - 4 * Y(s), 0)
sol = sp.dsolve(eq, Y(s)).rhs
C1 = sp.symbols("C1")
# a Laplace transform must vanish as s->oo: kill the e^{s^2/8} branch
assert sp.limit(sol.subs(C1, 0), s, sp.oo) == 0
sol0 = sp.simplify(sol.subs(C1, 0))
assert sp.simplify(sol0 + 7 / s**2) == 0
y = sp.inverse_laplace_transform(sol0, s, t)
assert sp.simplify(y + 7 * t) == 0
yy = -7 * t
assert sp.simplify(sp.diff(yy, t, 2) + 4 * t * sp.diff(yy, t) - 4 * yy) == 0
assert yy.subs(t, 0) == 0 and sp.diff(yy, t).subs(t, 0) == -7
# numeric ODE integration cross-check (mpmath Taylor ODE solver)
import mpmath as mp
f = mp.odefun(lambda tt, u: [u[1], 4 * u[0] - 4 * tt * u[1]], 0, [0, -7])
assert abs(f(2)[0] - (-14)) < 1e-8
print("PASS EE-104-03-1")
