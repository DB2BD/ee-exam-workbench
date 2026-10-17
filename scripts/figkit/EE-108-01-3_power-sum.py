"""EE-108-01-3: complex-power vector addition S_T = S_Y + S_Delta (to scale)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 420
OX, OY, K = 70, 190, 0.032
P = lambda p, q: (OX + K * p, OY - K * q)
s = header(W, H)
s += arrow(40, OY, 610, OY) + arrow(OX, 405, OX, 42)
(xy, yy), (xt, yt) = P(2904, 3872), P(14520, -4840)
s += arrow(OX, OY, xy, yy) + arrow(xy, yy, xt, yt)
s += arrow(OX, OY, xt, yt, color=BLUE)
s += dashed(xt, OY, xt, yt)
s += end_group()
s += text(626, OY - 10, [("v", "P"), ("n", " (W)")], anchor="end")
s += text(OX - 8, 56, [("v", "Q"), ("n", " (var)")], anchor="end")
s += text(xy + 10, yy + 4, [("v", "S"), ("vsub", "Y"), ("n", " = 2904 + "), ("v", "j"), ("n", "3872 VA")])
s += text(380, 150, [("v", "S"), ("sub", "Δ"), ("n", " = 11616 − "), ("v", "j"), ("n", "8712 VA")])
s += ttext(270, 320, [("v", "S"), ("vsub", "T"), ("n", " = 14520 − "), ("v", "j"), ("n", "4840 VA")], anchor="end", color=BLUE)
s += text(xt + 6, OY + 20, [("n", "14520")])
s += text(20, 22, [("t", "複數功率相加（按比例）：感性 "), ("v", "S"), ("vsub", "Y"), ("t", " 向上、容性 "), ("v", "S"), ("sub", "Δ"), ("t", " 向下")])
s += footer()
write('EE-108-01-3-power-sum.svg', s)
