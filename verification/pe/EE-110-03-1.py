"""EE-110-03-1 independent check: f(t) = 2t^2 + int_0^t f(t-tau) e^{-tau} dtau."""
import sympy as sp

t, s, tau = sp.symbols("t s tau", positive=True)
F = sp.symbols("F")
Fs = sp.solve(sp.Eq(F, 4 / s**3 + F / (s + 1)), F)[0]
f = sp.inverse_laplace_transform(Fs, s, t)
claimed = 2 * t**2 + sp.Rational(2, 3) * t**3
assert sp.simplify(f - claimed) == 0
# Independent: substitute back into the integral equation in the time domain
rhs = 2 * t**2 + sp.integrate(claimed.subs(t, t - tau) * sp.exp(-tau), (tau, 0, t))
assert sp.simplify(rhs - claimed) == 0
print("PASS EE-110-03-1")
