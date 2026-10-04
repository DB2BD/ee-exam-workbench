"""EE-110-06-2: transformer sizing by demand/diversity factors and daily energy.

Stem table: devices 1-8 kVA, fD, fL; diversity among devices 1.35 (A: 1-3), 1.56 (B: 4-6), 1.6 (C: 7-8);
between transformers 1.25; efficiency 100 %; PF 0.9 lag for energy.
"""
import numpy as np

cap = np.array([9, 30, 25, 50, 30, 20, 16, 25.0])
fD = np.array([0.9, 0.83, 0.65, 0.63, 0.8, 0.75, 0.7, 0.65])
fL = np.array([0.7, 0.65, 0.65, 0.7, 0.78, 0.75, 0.5, 0.6])
groups = {"A": ([0, 1, 2], 1.35), "B": ([3, 4, 5], 1.56), "C": ([6, 7], 1.6)}
STANDARD_KVA = [10, 15, 20, 30, 50, 75, 100, 150, 200]   # assumed 3-phase standard series (「條件與疑義」)
md = cap * fD
S = {g: md[idx].sum() / f for g, (idx, f) in groups.items()}
assert abs(S["A"] - 36.48) / 36.48 < 0.005 and abs(S["B"] - 45.19) / 45.19 < 0.005 and abs(S["C"] - 17.16) / 17.16 < 0.005
s_main = sum(S.values()) / 1.25
assert abs(s_main - 79.06) / 79.06 < 0.005
pick = {g: min(k for k in STANDARD_KVA if k >= v) for g, v in {**S, "main": s_main}.items()}
assert pick == {"A": 50, "B": 50, "C": 20, "main": 100}
E = 24 * 0.9 * (md * fL).sum()
assert abs(E - 2155.41) / 2155.41 < 0.005        # boxed 2155.41 kWh
# independent: energy = sum over groups of (group avg kVA) -> same total
E2 = sum(24 * 0.9 * (cap[idx] * fD[idx] * fL[idx]).sum() for idx, _ in groups.values())
assert abs(E - E2) < 1e-9
print("PASS EE-110-06-2")
