"""EE-105-03-5 independent check (official crop): CDF with jump at x=1."""
import sympy as sp

x = sp.symbols("x")
R = sp.Rational
F = lambda v: 0 if v < 0 else (R(v) / 3 if v < 1 else (R(v) / 2 if v < 2 else 1))
Fm = lambda v: 0 if v <= 0 else (R(v) / 3 if v <= 1 else (R(v) / 2 if v <= 2 else 1))  # left limits
assert Fm(R(1, 2)) == F(R(1, 2)) == R(1, 6)  # continuous at 1/2: no atom
assert Fm(1) == R(1, 3) and F(1) == R(1, 2)  # atom of 1/6 at x=1
assert F(R(3, 2)) == R(3, 4)
assert F(R(3, 2)) - Fm(R(1, 2)) == R(7, 12)
assert 1 - F(R(3, 2)) == R(1, 4)
# independent: P = continuous part + atom
cont = sp.integrate(R(1, 3), (x, R(1, 2), 1)) + sp.integrate(R(1, 2), (x, 1, R(3, 2))) + (F(1) - Fm(1))
assert cont == R(7, 12)
print("PASS EE-105-03-5")
