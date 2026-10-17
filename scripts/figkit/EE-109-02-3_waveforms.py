"""EE-109-02-3: flyback one period at the DCM/CrCM boundary: v_p, i_p, i_s."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

W, H = 680, 480
X0, XT = 120, 600          # t = 0 and t = T
XD = X0 + 0.75 * (XT - X0)  # t = DT
s = header(W, H)
# axes: (y_zero, top)
Yv, Yi, Ys = 95, 255, 420
for y, top in ((Yv, 30), (Yi, 165), (Ys, 300)):
    s += arrow(X0, y, XT + 30, y) + arrow(X0, y + (60 if y == Yv else 8), X0, top)
# v_p: +32.93 -> 24 px, -98.80 -> 72 px
s += poly([(X0, Yv), (X0, Yv - 24), (XD, Yv - 24), (XD, Yv + 72), (XT, Yv + 72), (XT, Yv)], color=BLUE)
# i_p: 0 -> 60 A (75 px)
s += poly([(X0, Yi), (XD, Yi - 75), (XD, Yi), (XT, Yi)], color=RED)
# i_s: 240 A (105 px) -> 0
s += poly([(X0, Ys), (XD, Ys), (XD, Ys - 105), (XT, Ys)], color=RED)
for y0, y1 in ((Yv - 30, Ys + 6),):
    s += dashed(XD, 40, XD, Ys + 6) + dashed(XT, 40, XT, Ys + 6)
s += dashed(X0, Yi - 75, XD, Yi - 75) + dashed(X0, Ys - 105, XD, Ys - 105)
# dimension arrows for DT and (1-D)T
s += arrow((X0 + XD) / 2, Ys + 36, X0, Ys + 36) + arrow((X0 + XD) / 2, Ys + 36, XD, Ys + 36)
s += arrow((XD + XT) / 2, Ys + 36, XD, Ys + 36) + arrow((XD + XT) / 2, Ys + 36, XT, Ys + 36)
s += end_group()
t = []
t.append(text(X0 + 10, 40, [("v", "v"), ("vsub", "p")]))
t.append(text(X0 + 10, 172, [("v", "i"), ("vsub", "p")]))
t.append(text(X0 + 10, 307, [("v", "i"), ("vsub", "s")]))
t.append(text(X0 + 40, Yv - 32, [("v", "V"), ("vsub", "s"), ("n", " − "), ("v", "V"), ("vsub", "t"), ("n", " = 32.93 V")]).replace('fill="#000"', f'fill="{BLUE}"', 1))
t.append(text(XD - 8, Yv + 70, [("n", "−("), ("v", "N"), ("vsub", "p"), ("n", "/"), ("v", "N"), ("vsub", "s"), ("n", ")("), ("v", "V"), ("vsub", "o"), ("n", " + "), ("v", "V"), ("vsub", "d"), ("n", ") = −98.80 V")], anchor="end").replace('fill="#000"', f'fill="{BLUE}"', 1))
t.append(text(X0 - 10, Yi - 70, [("v", "I"), ("vsub", "p(max)"), ("n", " = 60 A")], anchor="end"))
t.append(text(X0 - 10, Ys - 100, [("v", "I"), ("vsub", "s(max)"), ("n", " = 240 A")], anchor="end"))
t.append(text(X0 + 250, Yi - 12, [("t", "斜率 ("), ("v", "V"), ("vsub", "s"), ("n", " − "), ("v", "V"), ("vsub", "t"), ("n", ")/"), ("v", "L"), ("vsub", "p")], anchor="middle"))
t.append(text(XD - 12, Ys - 50, [("v", "i"), ("vsub", "s"), ("t", " 平均 = "), ("v", "I"), ("vsub", "o"), ("n", " = 30 A")], anchor="end"))
t.append(text((X0 + XD) / 2, Ys + 56, [("v", "DT"), ("n", " = 500 μs")], anchor="middle"))
t.append(text(XT + 4, Ys + 24, [("v", "T")], anchor="middle"))
t.append(text(XT + 34, Ys + 5, [("v", "t")]))
t.append(text((XD + XT) / 2, Ys + 56, [("n", "("), ("n", "1 − "), ("v", "D"), ("n", ")"), ("v", "T"), ("n", " = 166.67 μs")], anchor="middle"))
s += ''.join(t) + footer()
write('EE-109-02-3-waveforms.svg', s)
