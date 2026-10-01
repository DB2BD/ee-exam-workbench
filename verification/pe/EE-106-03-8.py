"""EE-106-03-8 independent check: expected area of a coin drawn at random.

Givens (official crop): 10 coins with radii 1, 2, ..., 10; one is chosen at random
(each equally likely).
"""
import sympy as sp

k = sp.symbols("k", integer=True, positive=True)
expected = sp.summation(sp.pi * k**2, (k, 1, 10)) / 10
assert sp.simplify(expected - sp.Rational(77, 2) * sp.pi) == 0

# Independent: E[r^2] = Var(r) + E[r]^2 for the discrete uniform on 1..10.
mean = sp.Rational(11, 2)
var = sp.Rational(10**2 - 1, 12)
assert sp.simplify(sp.pi * (var + mean**2) - expected) == 0
assert abs(float(expected) - 120.95) / 120.95 <= 0.005
print("PASS EE-106-03-8")
