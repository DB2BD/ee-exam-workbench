"""EE-109-03-2 independent check: iint_R x e^{y^2} dA, R: first quadrant bounded by y=x^2, y=4, x=0."""
import mpmath as mp
import sympy as sp

x, y = sp.symbols("x y", nonnegative=True)
I = sp.integrate(x * sp.exp(y**2), (x, 0, sp.sqrt(y)), (y, 0, 4))
claimed = (sp.exp(16) - 1) / 4
assert sp.simplify(I - claimed) == 0
# Independent: original dx-outer order numerically (y from x^2 to 4, x from 0 to 2)
num = mp.quad(lambda xx: xx * mp.quad(lambda yy: mp.exp(yy**2), [xx**2, 4]), [0, 2])
assert abs(num - float(claimed)) / float(claimed) < 1e-9
print("PASS EE-109-03-2")
