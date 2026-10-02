"""EE-113-06-1: cumulative kWh meter curves -> max demand and daily load factor.

Readings transcribed from the official crop at t = 0,4,...,24 h.
Method: interval differences of the summed cumulative curve; check via per-plant sums.
"""
import numpy as np

A = [0, 400, 1000, 2500, 3600, 4200, 4600]
B = [0, 200, 600, 1400, 2400, 3000, 3200]
C = [0, 400, 1200, 3600, 5600, 6800, 7200]
tot = np.array(A) + np.array(B) + np.array(C)
P = np.diff(tot) / 4.0
Pmax = P.max()
assert Pmax == 1175 and int(np.argmax(P)) == 2      # 8-12 h
S = Pmax / 0.94
assert abs(S - 1250) < 1e-9
E = tot[-1]
# independent: per-plant interval energies summed
E2 = sum(np.diff(x).sum() for x in (A, B, C))
assert E == E2 == 15000
LF = E / (Pmax * 24)
assert abs(LF - 0.5319) < 0.0005
print("PASS EE-113-06-1")
