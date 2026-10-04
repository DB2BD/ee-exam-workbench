"""EE-110-03-4 independent check: line integral of x dx - yz dy + e^z dz, x=t^3, y=-t, z=t^2, 1<=t<=2."""
import mpmath as mp
import sympy as sp

t = sp.symbols("t")
X, Y, Z = t**3, -t, t**2
I = sp.integrate(X * X.diff(t) - Y * Z * Y.diff(t) + sp.exp(Z) * Z.diff(t), (t, 1, 2))
claimed = sp.Rational(111, 4) + sp.exp(4) - sp.E
assert sp.simplify(I - claimed) == 0
# Independent: numeric quadrature
num = mp.quad(lambda u: u**3 * 3 * u**2 - (-u) * u**2 * (-1) + mp.exp(u**2) * 2 * u, [1, 2])
assert abs(num - float(claimed)) / float(claimed) < 1e-12
print("PASS EE-110-03-4")
