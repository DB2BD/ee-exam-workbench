"""EE-109-03-3 independent check: uniform 1/15 on [0,5]x[0,3], P(X>Y)."""
import numpy as np
import sympy as sp

x, y = sp.symbols("x y")
P = sp.integrate(sp.Rational(1, 15), (x, y, 5), (y, 0, 3))
assert P == sp.Rational(7, 10)
# Independent: complement via the other order, P(X<=Y) = int_0^3 x... 
Q = sp.integrate(sp.Rational(1, 15), (y, x, 3), (x, 0, 3))
assert 1 - Q == sp.Rational(7, 10)
# Grid count
g = np.linspace(0, 5, 2001)[:-1] + 5 / 4000
h = np.linspace(0, 3, 1201)[:-1] + 3 / 2400
Xg, Yg = np.meshgrid(g, h)
assert abs((Xg > Yg).mean() - 0.7) < 1e-3
print("PASS EE-109-03-3")
