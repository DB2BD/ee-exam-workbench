"""EE-114-03-1 independent check: total probability of spam.

Givens (official crop): mail split 70% / 20% / 10% to accounts 1, 2, 3;
spam rates 1%, 2%, 5% respectively.  Find P(spam) for a randomly chosen mail.
"""
import random
import sympy as sp

w = [sp.Rational(70, 100), sp.Rational(20, 100), sp.Rational(10, 100)]
s = [sp.Rational(1, 100), sp.Rational(2, 100), sp.Rational(5, 100)]
p = sum(a * b for a, b in zip(w, s))
assert p == sp.Rational(16, 1000)

# Independent: Monte Carlo over 2e6 mails with a fixed seed.
random.seed(1)
N, spam = 2_000_000, 0
for _ in range(N):
    u = random.random()
    rate = 0.01 if u < 0.7 else (0.02 if u < 0.9 else 0.05)
    spam += random.random() < rate
assert abs(spam / N - 0.016) / 0.016 <= 0.02
print("PASS EE-114-03-1")
