"""EE-112-03-3 independent check: shooters A/B/C hit probs 0.75/0.72/0.70,
bullets 50/53/60.  (1) P(random bullet hits); (2) P(bullet from B | hit)."""
import random
import sympy as sp

p = [sp.Rational(75, 100), sp.Rational(72, 100), sp.Rational(70, 100)]
nb = [50, 53, 60]
N = sum(nb)
P_hit = sum(ni * pi for ni, pi in zip(nb, p)) / N
assert P_hit == sp.Rational(5883, 8150)
P_B = nb[1] * p[1] / sum(ni * pi for ni, pi in zip(nb, p))
assert P_B == sp.Rational(12, 37)

# Independent: Monte Carlo of the bullet-drawing experiment (fixed seed).
random.seed(7)
shooters = [0] * 50 + [1] * 53 + [2] * 60
probs = [0.75, 0.72, 0.70]
hits = hits_B = 0
M = 1_000_000
for _ in range(M):
    who = random.choice(shooters)
    if random.random() < probs[who]:
        hits += 1
        hits_B += who == 1
assert abs(hits / M - float(P_hit)) / float(P_hit) < 0.005
assert abs(hits_B / hits - float(P_B)) / float(P_B) < 0.01
print("PASS EE-112-03-3")
