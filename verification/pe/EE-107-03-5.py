"""EE-107-03-5 independent check (official crop): 20 fuses, 5 defective, draw 3."""
from fractions import Fraction
from itertools import combinations, product
from math import comb

import sympy as sp

x = sp.symbols("x")
# With replacement: Binomial(3, 1/4)
binom = {k: Fraction(comb(3, k)) * Fraction(1, 4) ** k * Fraction(3, 4) ** (3 - k) for k in range(4)}
assert binom == {0: Fraction(27, 64), 1: Fraction(27, 64), 2: Fraction(9, 64), 3: Fraction(1, 64)}
# Brute force over ordered draws with replacement
items = [1] * 5 + [0] * 15
cnt = {k: 0 for k in range(4)}
for draw in product(range(20), repeat=3):
    cnt[sum(items[i] for i in draw)] += 1
assert {k: Fraction(v, 20**3) for k, v in cnt.items()} == binom
# Without replacement: hypergeometric
hyper = {k: Fraction(comb(5, k) * comb(15, 3 - k), comb(20, 3)) for k in range(4)}
assert hyper == {0: Fraction(91, 228), 1: Fraction(35, 76), 2: Fraction(5, 38), 3: Fraction(1, 114)}
cnt = {k: 0 for k in range(4)}
for draw in combinations(range(20), 3):
    cnt[sum(items[i] for i in draw)] += 1
assert {k: Fraction(v, comb(20, 3)) for k, v in cnt.items()} == hyper
assert sum(binom.values()) == 1 and sum(hyper.values()) == 1
assert sum(k * p for k, p in binom.items()) == Fraction(3, 4) == sum(k * p for k, p in hyper.items())
print("PASS EE-107-03-5")
