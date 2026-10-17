import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 330
XL, XR, YT, YB = 110, 470, 80, 260
s = header(W, H)
# left: V_f source (positive network Thevenin source)
SY = (YT + YB) // 2
s += f'<circle cx="{XL}" cy="{SY}" r="18"/>\n'
s += line(XL - 5, SY - 8, XL + 5, SY - 8) + line(XL, SY - 13, XL, SY - 3) + line(XL - 5, SY + 8, XL + 5, SY + 8)
s += line(XL, YT, XL, SY - 18) + line(XL, SY + 18, XL, YB)
s += line(XL, YT, 200, YT) + coil(200, YT, 330, YT, turns=5) + line(330, YT, XR, YT)          # Z1
s += line(XR, YT, XR, 120) + coil(XR, 120, XR, 220, turns=4) + line(XR, 220, XR, YB)          # Z2
s += line(XR, YB, 360, YB) + coil(360, YB, 230, YB, turns=5) + line(230, YB, XL, YB)          # Z0
s += arrow(370, YT - 18, 430, YT - 18, color=RED)
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
s += ctext(BLUE, XL - 26, SY - 4, [("v", "V"), ("vsub", "f")], anchor="end")
s += ctext(BLUE, XL - 26, SY + 18, [("n", "1∠0°")], anchor="end")
s += lab(265, YT - 16, [("v", "Z"), ("sub", "1"), ("n", " = "), ("v", "j"), ("n", "0.023529")])
s += lab(265, YT + 30, [("t", "正序")])
s += lab(XR + 16, 165, [("v", "Z"), ("sub", "2"), ("n", " = "), ("v", "j"), ("n", "0.023529")], "start")
s += lab(XR + 16, 189, [("t", "負序")], "start")
s += lab(295, YB - 18, [("t", "零序")])
s += lab(295, YB + 30, [("v", "Z"), ("sub", "0"), ("n", " = "), ("v", "j"), ("n", "0.02"), ("t", "（ES 投入）")])
s += lab(295, YB + 54, [("v", "Z"), ("sub", "0"), ("n", " = "), ("v", "j"), ("n", "0.025"), ("t", "（ES 切離）")])
s += ctext(RED, 400, YT - 30, [("v", "I"), ("vsub", "a"), ("sub", "1"), ("n", " = "), ("v", "I"), ("vsub", "a"), ("sub", "2"), ("n", " = "), ("v", "I"), ("vsub", "a"), ("sub", "0")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-104-05-1-slg.svg'), 'w').write(s)
print(len(s))
