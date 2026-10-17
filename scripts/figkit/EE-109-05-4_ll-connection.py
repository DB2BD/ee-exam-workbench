import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def dashed_box(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1} L{x2} {y1} L{x2} {y2} L{x1} {y2} Z" stroke-width="1" stroke-dasharray="5 4"/>\n'
W, H = 640, 330
YT, YB = 90, 230
XS, XF, XR = 100, 320, 560          # source, fault junction F, right return
SY, R = 160, 20
s = header(W, H)
# positive-sequence Thevenin: V_f (+ on top) in series with Z1
s += f'<circle cx="{XS}" cy="{SY}" r="{R}"/>\n'
s += line(XS - 5, SY - 9, XS + 5, SY - 9) + line(XS, SY - 14, XS, SY - 4) + line(XS - 5, SY + 9, XS + 5, SY + 9)
s += line(XS, SY - R, XS, YT) + line(XS, YT, 130, YT) + coil(120, YT, 220, YT, turns=4) + line(220, YT, XF, YT)
# negative-sequence Thevenin: Z2 only (no source)
s += line(XF, YT, 420, YT) + coil(420, YT, 520, YT, turns=4) + line(520, YT, XR, YT) + line(XR, YT, XR, YB)
s += line(XR, YB, XS, YB) + line(XS, YB, XS, SY + R)
s += line(XF, YB, XF, YB + 10) + ground(XF, YB + 10)
s += dot(XF, YT) + dot(XF, YB)
s += arrow(240, YT - 12, 292, YT - 12, color=RED)      # I_a1 out of + network toward F
s += arrow(400, YT - 12, 348, YT - 12, color=RED)      # I_a2 out of - network toward F
s += end_group()
s += text(170, 44, [("t", "正序網路")], anchor="middle")
s += text(470, 44, [("t", "負序網路")], anchor="middle")
s += ctext(BLUE, XS - 42, SY - 10, [("v", "V"), ("vsub", "f")], anchor="end")
s += ctext(BLUE, XS - 42, SY + 20, [("n", "1∠0°")], anchor="end")
s += text(170, YT + 30, [("v", "Z"), ("sub", "1"), ("n", " = "), ("v", "j"), ("n", "0.288")], anchor="middle")
s += text(470, YT + 30, [("v", "Z"), ("sub", "2"), ("n", " = "), ("v", "j"), ("n", "0.288")], anchor="middle")
s += ctext(RED, XF, YT + 26, [("v", "F")], anchor="middle")
s += ctext(RED, 252, YT - 30, [("v", "I"), ("vsub", "a"), ("sub", "1"), ("n", " = −"), ("v", "j"), ("n", "1.736")], anchor="middle")
s += ctext(RED, 392, YT - 30, [("v", "I"), ("vsub", "a"), ("sub", "2"), ("n", " = −"), ("v", "I"), ("vsub", "a"), ("sub", "1")], anchor="middle")
s += text(XF, YB + 44, [("t", "參考點（兩網路共用）")], anchor="middle")
s += text(XF, 312, [("t", "b-c 線間故障：正、負序在 F 並聯；零序網路不接入（"), ("v", "I"), ("vsub", "a"), ("sub", "0"), ("n", " = 0"), ("t", "）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-109-05-4-ll-connection.svg'), 'w').write(s)
print(len(s))
