import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
# B-C line-to-line fault at P: positive and negative Thevenin networks in parallel at the fault point.
W, H = 640, 330
YT, YB = 90, 230
XS, XF, XR = 100, 320, 560
SY, R = 160, 20
s = header(W, H)
s += f'<circle cx="{XS}" cy="{SY}" r="{R}"/>\n'
s += line(XS - 5, SY - 9, XS + 5, SY - 9) + line(XS, SY - 14, XS, SY - 4) + line(XS - 5, SY + 9, XS + 5, SY + 9)
s += line(XS, SY - R, XS, YT) + line(XS, YT, 130, YT) + coil(120, YT, 220, YT, turns=4) + line(220, YT, XF, YT)
s += line(XF, YT, 420, YT) + coil(420, YT, 520, YT, turns=4) + line(520, YT, XR, YT) + line(XR, YT, XR, YB)
s += line(XR, YB, XS, YB) + line(XS, YB, XS, SY + R)
s += dot(XF, YT) + dot(XF, YB)
s += arrow(240, YT - 12, 292, YT - 12, color=RED)
s += arrow(400, YT - 12, 348, YT - 12, color=RED)
s += end_group()
s += text(170, 44, [("t", "正序網路")], anchor="middle")
s += text(470, 44, [("t", "負序網路")], anchor="middle")
s += ctext(BLUE, XS - 30, SY - 4, [("v", "V"), ("vsub", "f")], anchor="end")
s += ctext(BLUE, XS - 30, SY + 20, [("n", "1.03")], anchor="end")
s += text(170, YT + 30, [("v", "jX"), ("sub", "1"), ("n", " = "), ("v", "j"), ("n", "0.260849")], anchor="middle")
s += text(470, YT + 30, [("v", "jX"), ("sub", "2"), ("n", " = "), ("v", "j"), ("n", "0.260849")], anchor="middle")
s += text(XF, YT + 26, [("v", "P")], anchor="middle")
s += ctext(RED, 252, YT - 30, [("v", "I"), ("vsub", "A"), ("sub", "1")], anchor="middle")
s += ctext(RED, 392, YT - 30, [("v", "I"), ("vsub", "A"), ("sub", "2"), ("n", " = −"), ("v", "I"), ("vsub", "A"), ("sub", "1")], anchor="middle")
s += text(XF, YB + 30, [("t", "參考點（兩網路共用）")], anchor="middle")
s += text(XF, 300, [("v", "B"), ("t", "–"), ("v", "C"), ("t", " 線間故障：正、負序在 "), ("v", "P"), ("t", " 並聯；零序不接入（"), ("v", "I"), ("vsub", "A"), ("sub", "0"), ("n", " = 0"), ("t", "）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-108-05-3-ll-connection.svg'), 'w').write(s)
print(len(s))
