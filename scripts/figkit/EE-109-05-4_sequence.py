import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 530
XL, X3, X1, X2, X4, XR = 50, 160, 300, 460, 570, 660
s = header(W, H)
# ---- (a) positive / negative sequence ----
YT, YB = 80, 210
for X in (XL, XR):
    s += line(X, YT, X, 121) + ac_source(X, 135) + line(X, 149, X, YB)
s += coil(XL, YT, X3, YT, turns=4)                              # G1 0.2
s += coil(X3, YT, X1, YT, turns=4)                              # T1 0.25
s += coil(X1, YT, X2, YT, turns=5)                              # line 0.4
s += coil(X2, YT, X4, YT, turns=4)                              # T2 0.3
s += coil(X4, YT, XR, YT, turns=4)                              # G2 0.1
s += line(XL, YB, XR, YB)
for X in (X3, X1, X2, X4): s += dot(X, YT)
s += line(X1, YT, X1, YT + 30)                                  # fault terminal
s += line(X1 - 70, YB, X1 - 70, YB + 8) + ground(X1 - 70, YB + 8)
# ---- (b) zero sequence ----
Y0, YG = 330, 460
s += line(XL, Y0, XL, YG) + coil(XL, Y0, X3, Y0, turns=4)       # G1 0.05 bus3 → ref (via left wire)
s += line(X3, Y0, X3 + 20, Y0)                                  # T1 delta side: open
s += line(X1 - 40, Y0, X1, Y0) + line(X1 - 40, Y0, X1 - 40, Y0 + 20) + coil(X1 - 40, Y0 + 20, X1 - 40, YG - 10, turns=4) + line(X1 - 40, YG - 10, X1 - 40, YG)   # T1 0.25 bus1→ref
s += coil(X1, Y0, X2, Y0, turns=5)                              # line 0.5
s += line(X2, Y0, X2 + 40, Y0) + line(X2 + 40, Y0, X2 + 40, Y0 + 20) + coil(X2 + 40, Y0 + 20, X2 + 40, YG - 10, turns=4) + line(X2 + 40, YG - 10, X2 + 40, YG)  # T2 0.3
s += line(X4 - 20, Y0, X4, Y0) + coil(X4, Y0, XR, Y0, turns=4) + line(XR, Y0, XR, YG)   # G2 0.05 bus4 → ref
s += line(XL, YG, XR, YG)
for X in (X3, X1, X2, X4): s += dot(X, Y0)
s += line(X1, Y0, X1, Y0 + 30)
s += line(X1 + 80, YG, X1 + 80, YG + 8) + ground(X1 + 80, YG + 8)
s += end_group()
lab = lambda X, Y, parts: text(X, Y, parts, anchor="middle")
for X, n in ((X3, "3"), (X1, "1"), (X2, "2"), (X4, "4")):
    s += lab(X, YT - 36, [("t", "匯流排 "), ("n", n)])
    s += lab(X, Y0 - 36, [("t", "匯流排 "), ("n", n)])
for Y in (YT, Y0):                                              # fault point F at the end of the bus-1 stub
    s += ctext(RED, X1 + 8, Y + 34, [("v", "F")])
for X, v, nm in (((XL + X3) / 2, "0.2", "G"), ((X3 + X1) / 2, "0.25", "T"), ((X1 + X2) / 2, "0.4", "L"), ((X2 + X4) / 2, "0.3", "T"), ((X4 + XR) / 2, "0.1", "G")):
    s += lab(X, YT + 30, [("v", "j"), ("n", v)])
s += lab((XL + X3) / 2, YT - 16, [("v", "G"), ("sub", "1")])
s += lab((X3 + X1) / 2, YT - 16, [("v", "T"), ("sub", "1")])
s += lab((X1 + X2) / 2, YT - 16, [("t", "線路")])
s += lab((X2 + X4) / 2, YT - 16, [("v", "T"), ("sub", "2")])
s += lab((X4 + XR) / 2, YT - 16, [("v", "G"), ("sub", "2")])
s += ctext(BLUE, XL + 20, 140, [("v", "E"), ("n", " = 1∠0°")])
s += ctext(BLUE, XR - 20, 140, [("v", "E"), ("n", " = 1∠0°")], anchor="end")
s += text(350, YB + 46, [("t", "（a）正序網路（負序相同但無電源）：兩側皆經發電機到參考點")], anchor="middle")
s += lab((XL + X3) / 2, Y0 + 30, [("v", "j"), ("n", "0.05")])
s += lab((XL + X3) / 2, Y0 - 16, [("v", "G"), ("sub", "1")])
s += text(X1 - 50, (Y0 + YG) / 2 + 5, [("v", "j"), ("n", "0.25")], anchor="end")
s += text(X1 - 50, (Y0 + YG) / 2 + 25, [("v", "T"), ("sub", "1")], anchor="end")
s += lab((X1 + X2) / 2, Y0 + 30, [("v", "j"), ("n", "0.5")])
s += text(X2 + 50, (Y0 + YG) / 2 + 5, [("v", "j"), ("n", "0.3")])
s += text(X2 + 50, (Y0 + YG) / 2 + 25, [("v", "T"), ("sub", "2")])
s += lab((X4 + XR) / 2, Y0 + 30, [("v", "j"), ("n", "0.05")])
s += lab((X4 + XR) / 2, Y0 - 16, [("v", "G"), ("sub", "2")])
s += text(X3 + 24, Y0 + 30, [("t", "Δ 側開路")])
s += text(X4 - 24, Y0 + 30, [("t", "Δ 側開路")], anchor="end")
s += text(350, YG + 46, [("t", "（b）零序網路：Y 接地側經變壓器電抗入地，Δ 側斷開")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-109-05-4-sequence.svg'), 'w').write(s)
print(len(s))
