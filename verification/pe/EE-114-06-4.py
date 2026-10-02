"""EE-114-06-4 (table-dependent): Y-Delta starting and motor feeder sizing, 220 V.

Stem givens: 3-phase 220 V, 20 HP (code letter E, 4.5-4.99 kVA/HP) and 10 HP, PVC conduit.
The code tables are NOT in the stem; the named constants below are the assumed
table values listed in the note's 「條件與疑義」 and must be checked against the
屋內線路裝置規則 tables.
"""
import numpy as np

V = 220.0

# ---- assumed table values (mirror 「條件與疑義」) ----
FLC_A = {20: 54.0, 10: 28.0}                                    # 220 V 3-phase full-load current
AMPACITY_PVC_CONDUIT_3W = {5.5: 30, 8: 40, 14: 55, 22: 70, 30: 90, 38: 100}   # mm2 -> A
BREAKER_MULT = {"B-E": 2.00, "F-V": 2.50}                       # inverse-time breaker, by code letter
CODE_20HP = "B-E"                                               # given: code letter E
CODE_10HP_ASSUMED = "F-V"                                       # not given -> 250 %
STANDARD_AT = [50, 60, 75, 100, 125, 150, 175, 200]

# ---- (一) starting current, star vs delta (phasor/impedance ratio) ----
for kva_per_hp in (4.5, 4.99):
    I_dol = kva_per_hp * 20e3 / (np.sqrt(3) * V)
    Zw = V / (I_dol / np.sqrt(3))            # delta winding impedance from DOL line current
    I_star = (V / np.sqrt(3)) / Zw
    assert abs(I_star / I_dol - 1 / 3) < 1e-12
I_star_lo = 4.5 * 20e3 / (np.sqrt(3) * V) / 3
I_star_hi = 4.99 * 20e3 / (np.sqrt(3) * V) / 3
assert abs(I_star_lo - 78.7) / 78.7 < 0.005 and abs(I_star_hi - 87.3) / 87.3 < 0.005   # boxed 78.7-87.3 A

# ---- (二) conductor sizing ----
def smallest_conductor(required):
    return min(s for s, a in AMPACITY_PVC_CONDUIT_3W.items() if a >= required)

req20 = 1.25 * FLC_A[20]
req10 = 1.25 * FLC_A[10]
req_feeder = 1.25 * max(FLC_A.values()) + min(FLC_A.values())
assert (req20, req10, req_feeder) == (67.5, 35.0, 95.5)
assert smallest_conductor(req20) == 22          # boxed 20 HP branch 22 mm2
assert smallest_conductor(req10) == 8           # boxed 10 HP branch 8 mm2
assert smallest_conductor(req_feeder) == 38     # boxed feeder 38 mm2

# ---- breaker AT ----
at20 = min(a for a in STANDARD_AT if a >= BREAKER_MULT[CODE_20HP] * FLC_A[20])
at10 = min(a for a in STANDARD_AT if a >= BREAKER_MULT[CODE_10HP_ASSUMED] * FLC_A[10])
at_feeder = max(a for a in STANDARD_AT if a <= at20 + FLC_A[10])
assert at20 == 125 and at10 == 75 and at_feeder == 150      # boxed 125 / 75 / 150 AT
# branch noted in 「條件與疑義」: 10 HP also code E -> 60 AT, feeder unchanged
assert min(a for a in STANDARD_AT if a >= BREAKER_MULT["B-E"] * FLC_A[10]) == 60
assert at_feeder >= at20
print("PASS EE-114-06-4")
