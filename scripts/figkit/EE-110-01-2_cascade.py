"""EE-110-01-2: s-domain ladder split into four cascaded sections (series R1, shunt Y2 = 1/R2 + sC, series sL, shunt 1/R3)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 330
YT, YB = 100, 250
XP1, XP2 = 50, 650
s = header(W, H)
s += terminal(XP1, YT) + terminal(XP1, YB) + terminal(XP2, YT) + terminal(XP2, YB)
s += line(XP1 + 4, YT, 115, YT) + resistor(115, YT, 190, YT) + line(190, YT, 370, YT)       # R1
s += line(XP1 + 4, YB, XP2 - 4, YB)
# shunt R2 || C at x = 250 (R2) and 310 (C)
s += line(280, YT, 280, 135) + line(250, 135, 310, 135) + line(250, 215, 310, 215) + line(280, 215, 280, YB)
s += resistor(250, 135, 250, 215, zigs=6, lead=8) + cap(310, 135, 310, 215, gap=8, w=24)
s += coil(370, YT, 460, YT, turns=4) + line(460, YT, XP2 - 4, YT)                            # L
s += resistor(548, YT, 548, YB, zigs=6, lead=30)                                             # R3
s += dot(280, YT) + dot(280, YB) + dot(548, YT) + dot(548, YB)
for x0, x1 in ((92, 205), (205, 345), (345, 485), (485, 612)):
    s += dashed(x0, 52, x1, 52) + dashed(x1, 52, x1, 280) + dashed(x1, 280, x0, 280) + dashed(x0, 280, x0, 52)
s += tint_arrow(56, YT - 14, 86, YT - 14)
s += tint_arrow(644, YT - 14, 616, YT - 14)
s += end_group()
s += text(148, 42, [("n", "①")], anchor="middle") + text(275, 42, [("n", "②")], anchor="middle")
s += text(415, 42, [("n", "③")], anchor="middle") + text(548, 42, [("n", "④")], anchor="middle")
s += text(152, YT + 30, [("v", "R"), ("sub", "1")], anchor="middle")
s += text(240, 180, [("v", "R"), ("sub", "2")], anchor="end")
s += text(326, 180, [("v", "C")])
s += text(415, YT + 30, [("v", "sL")], anchor="middle")
s += text(560, 180, [("v", "R"), ("sub", "3")])
s += text(148, 304, [("v", "Z"), ("n", " = "), ("v", "R"), ("sub", "1")], anchor="middle")
s += text(415, 304, [("v", "Z"), ("n", " = "), ("v", "sL")], anchor="middle")
s += text(548, 304, [("v", "Y"), ("n", " = 1/"), ("v", "R"), ("sub", "3")], anchor="middle")
s += text(275, 304, [("v", "Y"), ("sub", "2"), ("n", " = 1/"), ("v", "R"), ("sub", "2"), ("n", " + "), ("v", "sC")], anchor="middle")
s += ttext(70, YT - 22, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(632, YT - 22, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += ttext(XP1 + 16, YT + 34, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XP1 + 16, 182, [("v", "V"), ("sub", "1")], anchor="middle", color=BLUE)
s += ttext(XP1 + 16, YB - 18, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XP2 - 16, YT + 34, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XP2 - 16, 182, [("v", "V"), ("sub", "2")], anchor="middle", color=BLUE)
s += ttext(XP2 - 16, YB - 18, [("n", "−")], anchor="middle", color=BLUE)
s += footer()
write('EE-110-01-2-cascade.svg', s)
