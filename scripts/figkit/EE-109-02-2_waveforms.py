"""EE-109-02-2: boost CCM one period: e_L, i_L, i_c (discharge charge shaded)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

W, H = 680, 580
X0, XT = 150, 590
XD = (X0 + XT) / 2
Ye, Yi, Yc = 100, 345, 490
s = header(W, H)
# shaded discharge area in i_c (on interval, -3 A -> 30 px below axis)
s += f'<rect x="{X0}" y="{Yc}" width="{XD - X0}" height="30" fill="{FILL_RED}" stroke="none"/>\n'
s += arrow(X0, Ye, XT + 30, Ye) + arrow(X0, Ye + 50, X0, 35)
s += arrow(X0, Yi, XT + 30, Yi) + arrow(X0, Yi + 8, X0, 170)
s += arrow(X0, Yc, XT + 30, Yc) + arrow(X0, Yc + 50, X0, 400)
# e_L: +15 V / -15 V -> 36 px
s += poly([(X0, Ye - 36), (XD, Ye - 36), (XD, Ye + 36), (XT, Ye + 36), (XT, Ye - 36)], color=BLUE)
# i_L: 10 px per A
yl = lambda a: Yi - 20 * a
s += poly([(X0, yl(4.5)), (XD, yl(7.5)), (XT, yl(4.5))], color=RED)
s += dashed(X0, yl(6), XT, yl(6)) + dashed(X0, yl(7.5), XD, yl(7.5))
# i_c: 10 px per A
yc = lambda a: Yc - 10 * a
s += poly([(X0, yc(-3)), (XD, yc(-3)), (XD, yc(4.5)), (XT, yc(1.5)), (XT, yc(-3))], color=RED)
s += dashed(XD, 40, XD, Yc + 56) + dashed(XT, 40, XT, Yc + 56)
s += arrow((X0 + XD) / 2, Yc + 64, X0, Yc + 64) + arrow((X0 + XD) / 2, Yc + 64, XD, Yc + 64)
s += arrow((XD + XT) / 2, Yc + 64, XD, Yc + 64) + arrow((XD + XT) / 2, Yc + 64, XT, Yc + 64)
s += end_group()
t = []
t.append(text(X0 + 10, 42, [("v", "e"), ("vsub", "L")]))
t.append(text(X0 + 10, 182, [("v", "i"), ("vsub", "L")]))
t.append(text(X0 + 10, 410, [("v", "i"), ("vsub", "c")]))
t.append(text(X0 - 8, Ye - 31, [("v", "V"), ("vsub", "s"), ("n", " = 15 V")], anchor="end"))
t.append(text(XD + 10, Ye + 58, [("v", "V"), ("vsub", "s"), ("n", " − "), ("v", "V"), ("vsub", "o"), ("n", " = −15 V")]))
t.append(text(X0 - 8, yl(7.5) + 5, [("v", "I"), ("vsub", "L"), ("sub", ",peak"), ("n", " = 7.50 A")], anchor="end"))
t.append(text(X0 - 8, yl(6) + 5, [("v", "I"), ("vsub", "L"), ("n", " = 6 A")], anchor="end"))
t.append(text(X0 - 8, yl(4.5) + 8, [("v", "I"), ("vsub", "L"), ("sub", ",min"), ("n", " = 4.50 A")], anchor="end"))
t.append(text(XT + 8, yl(6) + 5, [("n", "Δ"), ("v", "I"), ("vsub", "L"), ("n", " = 3 A")]))
t.append(text(X0 - 8, yc(-3) + 5, [("n", "−"), ("v", "I"), ("vsub", "o"), ("n", " = −3 A")], anchor="end"))
t.append(text(XD + 8, yc(4.5) - 8, [("v", "i"), ("vsub", "L"), ("n", " − "), ("v", "I"), ("vsub", "o"), ("n", " = 4.50 A")]))
t.append(text(XT - 6, yc(1.5) - 20, [("v", "i"), ("vsub", "c"), ("n", " = 1.50 A")], anchor="end"))
t.append(text((X0 + XD) / 2, Yc + 22, [("t", "放電 "), ("v", "I"), ("vsub", "o"), ("v", "DT"), ("n", " = 60 μC")], anchor="middle"))
t.append(text((X0 + XD) / 2, Yc + 84, [("v", "DT"), ("n", " = 20 μs")], anchor="middle"))
t.append(text((XD + XT) / 2, Yc + 84, [("n", "(1 − "), ("v", "D"), ("n", ")"), ("v", "T"), ("n", " = 20 μs")], anchor="middle"))
t.append(text(XT + 34, Yc + 5, [("v", "t")]))
t.append(text(XT + 4, Yc + 22, [("v", "T")]))
s += ''.join(t) + footer()
write('EE-109-02-2-waveforms.svg', s)
