import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 330
YT, YB = 90, 260                  # top wire, reference (neutral) wire
XL, XR = 60, 640                  # source x
X3, X1, X2 = 200, 350, 500        # bus x
s = header(W, H)
for X in (XL, XR):                # EMF sources 1∠0 between top wire and reference
    s += line(X, YT, X, 161) + ac_source(X, 175) + line(X, 189, X, YB)
s += coil(XL, YT, 160, YT, turns=4) + line(160, YT, X3, YT)                 # Xd'' (bus 3 gen)
s += line(X3, YT, 220, YT) + coil(220, YT, 310, YT, turns=5) + line(310, YT, X1, YT)   # Xt
s += line(X1, YT, 390, YT) + coil(390, YT, 470, YT, turns=4) + line(470, YT, X2, YT)   # XL
s += line(X2, YT, 540, YT) + coil(540, YT, XR, YT, turns=4)                 # Xd'' (bus 2 gen)
s += line(X1, YT, X1, 135) + coil(X1, 135, X1, 205, turns=4) + line(X1, 205, X1, YB)  # Zf
s += line(XL, YB, XR, YB)
for X in (X3, X1, X2): s += dot(X, YT)
s += dot(X1, YB)
s += line(X1 + 150, YB, X1 + 150, YB + 14) + ground(X1 + 150, YB + 14)
s += arrow(318, YT + 20, 342, YT + 20, color=RED)       # I31 toward bus 1
s += arrow(382, YT + 20, 358, YT + 20, color=RED)       # I21 toward bus 1
s += arrow(X1 + 26, 150, X1 + 26, 192, color=RED)        # If down through Zf
s += end_group()
s += text(X3, YT - 16, [("n", "Bus 3")], anchor="middle")
s += text(X1, YT - 16, [("n", "Bus 1")], anchor="middle")
s += text(X2, YT - 16, [("n", "Bus 2")], anchor="middle")
s += text(110, YT - 16, [("v", "j"), ("n", "0.1")], anchor="middle")
s += text(265, YT - 16, [("v", "j"), ("n", "0.4")], anchor="middle")
s += text(430, YT - 16, [("v", "j"), ("n", "0.2")], anchor="middle")
s += text(590, YT - 16, [("v", "j"), ("n", "0.1")], anchor="middle")
s += text(110, YT + 50, [("t", "（"), ("v", "X"), ("vsub", "d"), ("n", "″"), ("t", "）")], anchor="middle")
s += text(265, YT + 50, [("t", "（"), ("v", "X"), ("vsub", "t"), ("n", " "), ("t", "）")], anchor="middle")
s += text(430, YT + 50, [("t", "（"), ("v", "X"), ("vsub", "L"), ("n", " "), ("t", "）")], anchor="middle")
s += text(590, YT + 50, [("t", "（"), ("v", "X"), ("vsub", "d"), ("n", "″"), ("t", "）")], anchor="middle")
s += ctext(BLUE, XL + 22, 180, [("n", "1∠0°")])
s += ctext(BLUE, XR - 22, 180, [("n", "1∠0°")], anchor="end")
s += ctext(RED, 318, YT + 42, [("v", "I"), ("sub", "31")], anchor="middle")
s += ctext(RED, 382, YT + 42, [("v", "I"), ("sub", "21")], anchor="middle")
s += ctext(RED, X1 + 34, 176, [("v", "I"), ("vsub", "f")])
s += text(X1 - 24, 166, [("v", "Z"), ("vsub", "f")], anchor="end")
s += text(X1 - 24, 186, [("v", "j"), ("n", "0.0125")], anchor="end")
s += text(350, 312, [("t", "參考點（中性點）；求 "), ("v", "Z"), ("sub", "th"), ("t", " 時兩個 EMF 短路")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-114-05-4-fault-network.svg'), 'w').write(s)
print(len(s))
