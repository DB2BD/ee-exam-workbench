"""EE-109-05-6: two units in one area, droop sharing, D = 0.

Givens (official crop): 500 MVA and 800 MVA, R = 5 % on own base, 60 Hz,
initial 200 MW / 500 MW, load step +150 MW.
"""
import numpy as np

f0 = 60.0
b1 = 500 / (0.05 * f0)  # MW/Hz
b2 = 800 / (0.05 * f0)
df = -150 / (b1 + b2)
dP1, dP2 = -b1 * df, -b2 * df
assert abs(df - (-0.34615)) < 1e-5
assert abs(200 + dP1 - 257.69) < 0.01 and abs(500 + dP2 - 592.31) < 0.01

# Method 2: per-unit on a 1000 MVA base and the requirement that both units see
# the same frequency drop.
R1 = 0.05 * 1000 / 500; R2 = 0.05 * 1000 / 800
dfpu = -0.15 / (1 / R1 + 1 / R2)
assert abs(dfpu * 60 - df) < 1e-12
assert abs(-dfpu / R1 * 1000 - dP1) < 1e-9 and abs(dP1 + dP2 - 150) < 1e-9
assert abs(dP1 / dP2 - 500 / 800) < 1e-12
print("PASS EE-109-05-6")
