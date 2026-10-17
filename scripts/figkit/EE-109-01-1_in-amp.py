"""EE-109-01-1: three-op-amp instrumentation amplifier, virtual-short potentials and the shared current i_g."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *


def opamp(xl, yt, yb, xa, minus_top=True):
    """Op-amp triangle: left edge x = xl from yt to yb, apex at x = xa; marks - / + near the inputs."""
    ym = (yt + yb) / 2
    s = f'<path d="M{xl} {yt} L{xl} {yb} L{xa} {ym} Z"/>\n'
    y_minus, y_plus = (yt + 0.25 * (yb - yt), yt + 0.75 * (yb - yt)) if minus_top else (yt + 0.75 * (yb - yt), yt + 0.25 * (yb - yt))
    s += line(xl + 6, y_minus, xl + 14, y_minus)
    s += line(xl + 6, y_plus, xl + 14, y_plus) + line(xl + 10, y_plus - 4, xl + 10, y_plus + 4)
    return s


W, H = 700, 400
XN, XO, XP, XA3 = 210, 350, 490, 530
YR1, YR2 = 150, 240
s = header(W, H)
# top op-amp A1: + at y=70 (v1), - at y=110
s += opamp(250, 50, 130, 320, minus_top=False)
s += terminal(60, 70) + line(64, 70, 250, 70)
s += line(XN, 110, 250, 110) + line(XN, 110, XN, YR1)
s += line(320, 90, XO, 90) + line(XO, 90, XO, YR1)
s += resistor(XN, YR1, XO, YR1, zigs=6, lead=35)
# Rg between the two inverting nodes
s += resistor(XN, YR1, XN, YR2, zigs=6, lead=20)
# bottom op-amp A2: - at y=280, + at y=320 (v2)
s += opamp(250, 290, 370, 320, minus_top=True)
s += line(XN, YR2, XN, 310) + line(XN, 310, 250, 310)
s += terminal(60, 350) + line(64, 350, 250, 350)
s += line(320, 330, XO, 330) + line(XO, 330, XO, YR2)
s += resistor(XN, YR2, XO, YR2, zigs=6, lead=35)
# difference stage
s += resistor(XO, YR1, XP, YR1, zigs=6, lead=35) + resistor(XO, YR2, XP, YR2, zigs=6, lead=35)
s += line(XP, YR1, XA3, YR1) + line(XP, YR2, XA3, YR2)
s += opamp(XA3, 120, 270, 620, minus_top=True)
s += line(620, 195, 680, 195) + terminal(684, 195)
s += line(XP, YR1, XP, 92) + line(XP, 92, 540, 92) + resistor(540, 92, 640, 92, zigs=6, lead=14) + line(640, 92, 660, 92) + line(660, 92, 660, 195)
s += resistor(XP, YR2, XP, 350, zigs=6, lead=24) + ground(XP, 350)
for x, y in ((XN, YR1), (XN, YR2), (XO, YR1), (XO, YR2), (XP, YR1), (XP, YR2), (660, 195)):
    s += dot(x, y)
# i_g path: v_o1 -> top R1 -> Rg (down) -> bottom R1 -> v_o2
s += tint_arrow(XN - 16, 178, XN - 16, 214)
s += tint_arrow(300, YR1 + 14, 262, YR1 + 14)
s += tint_arrow(262, YR2 + 14, 300, YR2 + 14)
s += end_group()
s += text(20, 28, [("t", "理想運放：虛短 "), ("v", "v"), ("sub", "+"), ("n", " = "), ("v", "v"), ("sub", "−"), ("t", "，虛斷（輸入端電流 0）")])
s += text(44, 76, [("v", "v"), ("sub", "1")], anchor="end")
s += text(44, 356, [("v", "v"), ("sub", "2")], anchor="end")
s += ttext(XN - 8, YR1 - 10, [("v", "v"), ("sub", "1")], anchor="end", color=BLUE)
s += ttext(XN - 8, YR2 + 22, [("v", "v"), ("sub", "2")], anchor="end", color=BLUE)
s += text(XN + 16, 200, [("v", "R"), ("vsub", "g")])
s += text(285, YR1 - 12, [("v", "R"), ("sub", "1")], anchor="middle")
s += text(285, YR2 - 14, [("v", "R"), ("sub", "1")], anchor="middle")
s += ttext(281, YR1 + 34, [("v", "i"), ("vsub", "g")], anchor="middle", color=RED)
s += ttext(281, YR2 + 36, [("v", "i"), ("vsub", "g")], anchor="middle", color=RED)
s += ttext(XN - 24, 202, [("v", "i"), ("vsub", "g")], anchor="end", color=RED)
s += ttext(XO + 8, 112, [("v", "v"), ("vsub", "o"), ("sub", "1")], color=BLUE)
s += ttext(XO + 8, 300, [("v", "v"), ("vsub", "o"), ("sub", "2")], color=BLUE)
s += text(420, YR1 - 14, [("v", "R"), ("sub", "2")], anchor="middle")
s += text(420, YR2 + 26, [("v", "R"), ("sub", "2")], anchor="middle")
s += text(590, 76, [("v", "R"), ("sub", "0")], anchor="middle")
s += text(XP + 14, 305, [("v", "R"), ("sub", "0")])
s += text(684, 222, [("v", "v"), ("sub", "0")], anchor="middle")
s += footer()
write('EE-109-01-1-in-amp.svg', s)
