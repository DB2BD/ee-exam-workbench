"""EE-106-03-7 independent check (official crop): variance of a fair six-sided die."""
from fractions import Fraction

faces = range(1, 7)
p = Fraction(1, 6)
mean = sum(p * v for v in faces)
second = sum(p * v * v for v in faces)
var = second - mean**2
assert mean == Fraction(7, 2) and second == Fraction(91, 6) and var == Fraction(35, 12)
# Independent: definition E[(X-mu)^2]
assert sum(p * (v - mean) ** 2 for v in faces) == Fraction(35, 12)
assert Fraction(6**2 - 1, 12) == Fraction(35, 12)  # discrete uniform formula
assert abs(float(var) - 2.9167) / 2.9167 <= 0.005
print("PASS EE-106-03-7")
