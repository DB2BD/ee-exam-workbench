"""EE-113-06-5: CT ratio from the CO-7 TD5 curve read off the official crop.

Method: digitise the official figure (log x-axis 1-20, linear y-axis 0-7 s) by pixel
tracing; find the multiple M where TD5 = 1.0 s; CTR = I_F / (M * tap).
"""
import math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
im = np.array(Image.open(ROOT / "01_原始試題/依考科/06_工業配電/images/questions/PE_113年_工業配電_Q05.png").convert("L")).astype(int)
x1, x20, y0, y7 = 223.5, 1106.5, 1632, 675          # plot frame (pixel)
def col_times(M):
    x = int(round(x1 + (x20 - x1) * math.log10(M) / math.log10(20)))
    col = np.min(im[:, x-1:x+2], axis=1); out = []; y = 1628
    while y > 680:
        if col[y] < 70:
            s = y
            while col[y] < 70: y -= 1
            out.append((y0 - (s + y) / 2) * 7 / (y0 - y7))
        y -= 1
    return out                                       # bottom-up: 1/2, 1, 2, 3, 4, 5, ...
td5 = {M: col_times(M)[5] for M in (12, 13, 14, 15, 18)}
assert all(a > b for a, b in zip(list(td5.values()), list(td5.values())[1:]))
assert td5[14] > 1.0 > td5[18]
M = 15 + (18 - 15) * (td5[15] - 1.0) / (td5[15] - td5[18])
assert 14.5 < M < 16.0
assert col_times(6)[5] > 1.3                         # M = 6 on TD5 is about 1.5 s, not 1.0 s
ctr = 10800 / (M * 6)
std = [n / 5 for n in (400, 500, 600, 750, 800, 1000, 1200, 1500)]
best = min(std, key=lambda r: abs(r - ctr))
assert best == 120                                   # 600/5
assert abs(10800 / 120 / 6 - 15) < 1e-12
print("PASS EE-113-06-5")
