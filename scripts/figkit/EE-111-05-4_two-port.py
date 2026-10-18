import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Per-phase ABCD two-port: reference directions of V_S, I_S (into port 1) and V_R, I_R (out of port 2).
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 270
YT, YB = 70, 190
XL, XR = 90, 550          # terminals
BX1, BX2 = 250, 390       # two-port box
s = header(W, H)
s += f'<path d="M{BX1} {YT - 20} L{BX2} {YT - 20} L{BX2} {YB + 20} L{BX1} {YB + 20} Z"/>\n'
s += line(XL, YT, BX1, YT) + line(XL, YB, BX1, YB) + line(BX2, YT, XR, YT) + line(BX2, YB, XR, YB)
for x in (XL, XR):
    s += f'<circle cx="{x}" cy="{YT}" r="3.5" fill="#fff"/>\n<circle cx="{x}" cy="{YB}" r="3.5" fill="#fff"/>\n'
s += arrow(140, YT - 14, 200, YT - 14, color=RED)          # I_S into port 1
s += arrow(440, YT - 14, 500, YT - 14, color=RED)          # I_R out of port 2
s += arrow(XL, YB - 8, XL, YT + 10, color=BLUE)             # V_S: neutral -> sending terminal
s += arrow(XR, YB - 8, XR, YT + 10, color=BLUE)             # V_R: neutral -> receiving terminal
s += end_group()
s += text((BX1 + BX2) / 2, 118, [("v", "A"), ("n", "  "), ("v", "B")], anchor="middle")
s += text((BX1 + BX2) / 2, 146, [("v", "C"), ("n", "  "), ("v", "D")], anchor="middle")
s += text((BX1 + BX2) / 2, YB + 44, [("n", "483 km "), ("t", "線路（每相）")], anchor="middle")
s += ctext(RED, 170, YT - 24, [("v", "I"), ("vsub", "S")], anchor="middle")
s += ctext(RED, 470, YT - 24, [("v", "I"), ("vsub", "R")], anchor="middle")
s += ctext(BLUE, XL - 12, 136, [("v", "V"), ("vsub", "S")], anchor="end")
s += ctext(BLUE, XR + 12, 136, [("v", "V"), ("vsub", "R")])
s += text(XL, YB + 26, [("t", "中性點")], anchor="middle")
s += text(XR, YB + 26, [("t", "中性點")], anchor="middle")
s += text(XR + 12, YT + 5, [("t", "負載")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-111-05-4-two-port.svg'), 'w').write(s)
print(len(s))
