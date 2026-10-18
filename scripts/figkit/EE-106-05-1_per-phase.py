import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 300
YT, YB = 80, 220
XS, XR, XL = 80, 440, 545          # sending source, receiving node, load
s = header(W, H)
s += line(XS, YT, XS, 136) + ac_source(XS, 150) + line(XS, 164, XS, YB)
s += line(XS, YT, 130, YT) + resistor(130, YT, 210, YT) + line(210, YT, 240, YT) + coil(240, YT, 340, YT, turns=4) + line(340, YT, XL, YT)
s += line(XL, YT, XL, 120) + f'<path d="M{XL - 13} 120 L{XL + 13} 120 L{XL + 13} 180 L{XL - 13} 180 Z"/>\n' + line(XL, 180, XL, YB)
s += line(XS, YB, XL, YB)
s += dot(XR, YT) + dot(XR, YB) + dot(XS, YT) + dot(XS, YB)
s += arrow(XR, YB - 6, XR, YT + 14, color=BLUE)          # V_R: reference -> receiving node (+)
s += arrow(360, YT - 12, 410, YT - 12, color=RED)        # I
s += end_group()
s += ctext(BLUE, XS + 24, 146, [("v", "V"), ("vsub", "S")])
s += ctext(BLUE, XS + 24, 168, [("n", "（待求）")])
s += text(170, YT - 18, [("v", "R"), ("n", " = 6 Ω")], anchor="middle")
s += text(290, YT - 18, [("v", "j"), ("v", "X"), ("n", " = "), ("v", "j"), ("n", "19.604 Ω")], anchor="middle")
s += ctext(RED, XR - 14, YT + 28, [("v", "I"), ("n", " = 1075.81∠−36.87° A")], anchor="end")
s += ctext(BLUE, XR - 12, 156, [("v", "V"), ("vsub", "R")], anchor="end")
s += ctext(BLUE, XR - 12, 178, [("n", "92.95∠0° kV")], anchor="end")
s += text(XL + 22, 144, [("t", "負載（每相）")])
s += text(XL + 22, 166, [("n", "pf 0.8 "), ("t", "落後")])
s += text(XS - 10, YB + 22, [("t", "中性點")], anchor="middle")
s += text(340, 280, [("t", "每相等效（短線：只有串聯 "), ("v", "R"), ("n", " + "), ("v", "j"), ("v", "X"), ("t", "，無並聯電容）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-106-05-1-per-phase.svg'), 'w').write(s)
print(len(s))
