import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 330
XL, XJ, XR, YT, YB = 110, 300, 490, 80, 260
def isrc(x, y, up):
    a = arrow(x, y + 10, x, y - 10) if up else arrow(x, y - 10, x, y + 10)
    return f'<circle cx="{x}" cy="{y}" r="18"/>\n' + a
s = header(W, H)
SY = (YT + YB) // 2
s += line(XL, YT, XL, SY - 18) + isrc(XL, SY, True) + line(XL, SY + 18, XL, YB)
s += line(XR, YT, XR, SY - 18) + isrc(XR, SY, False) + line(XR, SY + 18, XR, YB)
s += line(XL, YT, XR, YT)
s += line(XJ, YT, XJ, 130) + coil(XJ, 130, XJ, 200, turns=4) + line(XJ, 200, XJ, YB)       # relay coil
s += line(XL, YB, 170, YB) + resistor(170, YB, 240, YB) + line(240, YB, 360, YB) + resistor(360, YB, 430, YB) + line(430, YB, XR, YB)
s += dot(XJ, YT) + dot(XJ, YB)
s += arrow(180, YT - 16, 240, YT - 16, color=RED)
s += arrow(370, YT - 16, 430, YT - 16, color=RED)
s += arrow(XJ + 24, 140, XJ + 24, 190, color=RED)
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
s += ctext(RED, 210, YT - 28, [("v", "I"), ("n", "′"), ("sub", "1")])
s += ctext(RED, 400, YT - 28, [("v", "I"), ("n", "′"), ("sub", "2")])
s += ctext(RED, XJ + 34, 170, [("v", "I"), ("n", "′")])
s += lab(XL - 26, SY - 4, [("t", "CT"), ("sub", "1")], "end")
s += ctext(RED, XL - 26, SY + 20, [("v", "I"), ("sub", "1"), ("n", "/"), ("v", "n"), ("sub", "1")], anchor="end")
s += lab(XR + 26, SY - 4, [("t", "CT"), ("sub", "2")], "start")
s += ctext(RED, XR + 26, SY + 20, [("v", "I"), ("sub", "2"), ("n", "/"), ("v", "n"), ("sub", "2")], anchor="start")
s += lab(XJ - 14, 170, [("t", "差動電驛")], "end")
s += lab(205, YB + 28, [("v", "R")]) + lab(395, YB + 28, [("v", "R")])
s += lab(XJ + 10, YT - 8, [("t", "接點")], "start")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-106-05-4-ct-circuit.svg'), 'w').write(s)
print(len(s))
