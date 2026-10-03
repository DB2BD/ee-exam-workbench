"""EE-107-06-2: 100 HP, 3-phase 220 V motor feeder, 120 m, Z=0.195+j0.0909 ohm/km, X factor 1.2, pf 0.85.

Stem gives no full-load current.  Named constants below are the branches discussed in the note:
reference-book 1 HP = 1 kVA, year answer 250 A, historical table 163-7-3 258 A, current table
258-3 238 A, and 100 HP with efficiency 1.  They are assumptions, not stem data.
"""
import math

V, L_KM, PF = 220.0, 0.120, 0.85
R, X = 0.195, 1.2 * 0.0909
K = R * PF + X * math.sqrt(1 - PF**2)                   # ohm/km along the voltage axis
assert abs(K - 0.223211456) < 1e-8

I_BOOK = 100e3 / (math.sqrt(3) * V)                      # 1 HP = 1 kVA (reference book)
I_YEAR_TABLE, I_HIST_TABLE, I_CURRENT_TABLE = 250.0, 258.0, 238.0
I_HP_746 = 100 * 746 / (math.sqrt(3) * V * PF)           # eta = 1

def drop(i, length=L_KM):
    dv = math.sqrt(3) * i * K * length
    return dv, dv / V * 100

def lmax(i):
    return 0.05 * V / (math.sqrt(3) * i * K) * 1000       # metres

assert abs(I_BOOK - 262.43) < 0.005
dv, pct = drop(I_BOOK)                                    # reference-book main answer
assert abs(dv - 12.175) / 12.175 < 5e-4 and abs(pct - 5.53) / 5.53 < 1e-3
assert abs(lmax(I_BOOK) - 108.42) / 108.42 < 5e-4

for i, pct_want, l_want in ((I_YEAR_TABLE, 5.2720, 113.81), (I_HIST_TABLE, 5.4407, 110.28),
                            (I_CURRENT_TABLE, 5.0189, 119.55), (I_HP_746, 4.8570, 123.53)):
    assert abs(drop(i)[1] - pct_want) / pct_want < 5e-4
    assert abs(lmax(i) - l_want) / l_want < 5e-4
assert abs(I_HP_746 - 230.323) < 0.005
# drop is proportional to I x L: L_max x %drop(at 120 m) = 5 % x 120 m
for i in (I_BOOK, I_YEAR_TABLE, I_HIST_TABLE, I_CURRENT_TABLE, I_HP_746):
    assert abs(lmax(i) * drop(i)[1] - 5 * 120) < 1e-9
print("PASS EE-107-06-2")
