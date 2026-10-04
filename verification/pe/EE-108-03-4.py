"""EE-108-03-4 independent check (official crop): flux of F=(x,y,z) through the unit sphere."""
import sympy as sp

th, ph = sp.symbols("theta phi")
# Direct surface integral: n = position vector on the unit sphere, dA = sin(theta) dtheta dphi
x = sp.sin(th) * sp.cos(ph)
y = sp.sin(th) * sp.sin(ph)
z = sp.cos(th)
integrand = (x * x + y * y + z * z) * sp.sin(th)
flux = sp.integrate(sp.integrate(integrand, (th, 0, sp.pi)), (ph, 0, 2 * sp.pi))
assert sp.simplify(flux - 4 * sp.pi) == 0
# Divergence theorem: div F = 3, volume 4/3 pi
assert sp.simplify(3 * sp.Rational(4, 3) * sp.pi - flux) == 0
print("PASS EE-108-03-4")
