"""EE-113-01-4: s-domain two-port with element admittances and the KCL reference directions at both top nodes."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 700, 330, 100, 260
XP1, XN1, XN2, XD, XP2 = 60, 190, 430, 550, 650
XC0, XC1 = 280, 340
s = header(W, H)
s += line(XP1 + 4, YT, XC0, YT) + cap(XC0, YT, XC1, YT) + line(XC1, YT, XP2 - 4, YT)
s += line(XP1 + 4, YB, XP2 - 4, YB)
s += resistor(XN1, YT, XN1, YB, zigs=6, lead=40)
s += resistor(XN2, YT, XN2, YB, zigs=6, lead=40)
cx, cy, h = XD, (YT + YB) / 2, 22                                  # VCCS 4 V1, arrow up into node 2
s += line(XD, YT, XD, cy - h) + line(XD, cy + h, XD, YB)
s += f'<path d="M{cx - h} {cy} L{cx} {cy - h} L{cx + h} {cy} L{cx} {cy + h} Z"/>\n'
s += arrow(cx, cy + 11, cx, cy - 11)
for x in (XN1, XN2, XD):
    s += dot(x, YT) + dot(x, YB)
for x in (XP1, XP2):
    s += terminal(x, YT) + terminal(x, YB)
s += tint_arrow(95, YT, 135, YT)                                   # I1 enters port 1
s += tint_arrow(625, YT, 585, YT)                                  # I2 enters port 2
s += tint_arrow(XN1 + 16, 118, XN1 + 16, 150)                      # 1 S branch, downward
s += tint_arrow(XN2 + 16, 118, XN2 + 16, 150)                      # 3 S branch, downward
s += tint_arrow(292, YT - 26, 328, YT - 26)                        # capacitor branch, node 1 -> node 2
s += end_group()
s += ttext(115, YT - 12, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(605, YT - 12, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += ttext(XN1 + 24, 140, [("n", "1·"), ("v", "V"), ("sub", "1")], color=RED)
s += ttext(XN2 + 24, 140, [("n", "3"), ("v", "V"), ("sub", "2")], color=RED)
s += ttext(310, YT - 38, [("n", "2"), ("v", "s"), ("n", "("), ("v", "V"), ("sub", "1"), ("n", " − "), ("v", "V"), ("sub", "2"), ("n", ")")],
           anchor="middle", color=RED)
s += text(310, YT + 38, [("n", "2 F → "), ("v", "sC"), ("n", " = 2"), ("v", "s"), ("n", " S")], anchor="middle")
s += text(XN1 + 16, 196, [("n", "1 Ω")])
s += text(XN1 + 16, 218, [("n", "→ 1 S")])
s += text(XN2 + 16, 196, [("n", "1/3 Ω")])
s += text(XN2 + 16, 218, [("n", "→ 3 S")])
s += text(XD + 28, cy + 5, [("n", "4"), ("v", "V"), ("sub", "1")])
for x, nm, anc, dx in ((XP1, "1", "middle", 0), (XP2, "2", "middle", 0)):
    s += ttext(x, YT + 30, [("n", "+")], anchor=anc, color=BLUE)
    s += ttext(x, cy + 5, [("v", "V"), ("sub", nm)], anchor=anc, color=BLUE)
    s += ttext(x, YB - 14, [("n", "−")], anchor=anc, color=BLUE)
s += text(XN1 + 10, YT - 12, [("t", "節點 1")])
s += text(XN2 + 10, YT - 12, [("t", "節點 2")])
s += text(30, 305, [("v", "s"), ("t", " 域導納；下導線為兩埠共同參考端")])
s += footer()
write('EE-113-01-4-kcl.svg', s)
