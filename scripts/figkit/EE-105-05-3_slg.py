import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 320
XL, XR, YT, YB = 110, 480, 80, 250
s = header(W, H)
SY = (YT + YB) // 2
s += f'<circle cx="{XL}" cy="{SY}" r="18"/>\n'
s += line(XL - 5, SY - 8, XL + 5, SY - 8) + line(XL, SY - 13, XL, SY - 3) + line(XL - 5, SY + 8, XL + 5, SY + 8)
s += line(XL, YT, XL, SY - 18) + line(XL, SY + 18, XL, YB)
s += line(XL, YT, 210, YT) + coil(210, YT, 330, YT, turns=5) + line(330, YT, XR, YT)            # X1
s += line(XR, YT, XR, 115) + coil(XR, 115, XR, 215, turns=4) + line(XR, 215, XR, YB)            # X2
s += line(XR, YB, 420, YB) + coil(420, YB, 330, YB, turns=4) + line(330, YB, 290, YB)           # X0
s += coil(290, YB, 180, YB, turns=4) + line(180, YB, XL, YB)                                    # 3Xn
s += dot(310, YB)
s += arrow(370, YT - 18, 430, YT - 18, color=RED)
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
s += ctext(BLUE, XL - 26, SY - 4, [("v", "E"), ("n", "″")], anchor="end")
s += ctext(BLUE, XL - 26, SY + 18, [("n", "1∠0°")], anchor="end")
s += lab(270, YT - 16, [("v", "jX"), ("sub", "1"), ("n", " = "), ("v", "j"), ("n", "0.20")])
s += lab(270, YT + 30, [("t", "正序")])
s += lab(XR + 16, 160, [("v", "jX"), ("sub", "2"), ("n", " = "), ("v", "j"), ("n", "0.20")], "start")
s += lab(XR + 16, 184, [("t", "負序")], "start")
s += lab(375, YB + 30, [("v", "jX"), ("sub", "0"), ("n", " = "), ("v", "j"), ("n", "0.05")])
s += lab(235, YB + 30, [("v", "j"), ("n", "3"), ("v", "X"), ("vsub", "n"), ("n", " = "), ("v", "j"), ("n", "0.24")])
s += lab(310, YB - 18, [("t", "零序")])
s += ctext(RED, 400, YT - 30, [("v", "I"), ("vsub", "a"), ("sub", "1"), ("n", " = "), ("v", "I"), ("vsub", "a"), ("sub", "2"), ("n", " = "), ("v", "I"), ("vsub", "a"), ("sub", "0")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-105-05-3-slg.svg'), 'w').write(s)
print(len(s))
