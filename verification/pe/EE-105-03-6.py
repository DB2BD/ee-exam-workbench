"""EE-105-03-6 independent check (official crop): 2 black, 3 red, 4 white balls."""
from fractions import Fraction as Fr
from itertools import permutations, product

balls = ["B"] * 2 + ["R"] * 3 + ["W"] * 4
# without replacement: enumerate ordered pairs of distinct balls
pairs = list(permutations(range(9), 2))
p_ww = Fr(sum(balls[i] == "W" and balls[j] == "W" for i, j in pairs), len(pairs))
p_r2 = Fr(sum(balls[j] == "R" for i, j in pairs), len(pairs))
assert p_ww == Fr(1, 6) and p_r2 == Fr(1, 3)
# with replacement
pairs = list(product(range(9), repeat=2))
q_ww = Fr(sum(balls[i] == "W" and balls[j] == "W" for i, j in pairs), len(pairs))
q_r2 = Fr(sum(balls[j] == "R" for i, j in pairs), len(pairs))
assert q_ww == Fr(16, 81) and q_r2 == Fr(1, 3)
print("PASS EE-105-03-6")
