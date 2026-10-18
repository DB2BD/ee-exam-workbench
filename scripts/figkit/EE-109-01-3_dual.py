"""EE-109-01-3: dual network (window frame, centre node O) with clockwise mesh currents i'_1..i'_4.

Mesh k is the dual of node k: outer resistor R'_k = G_k; spokes T-O: I'_12 = 2 A (down), B-O: I'_34 = 4 A (up),
Lf-O: V'_41 = 1 V (+ at Lf, outer end), O-R: V'_23 = 3 V (+ at R, outer end).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 430
XL, XM, XR = 70, 320, 570
YT, YM, YB = 60, 210, 360
s = header(W, H)
# outer frame with one resistor per quadrant edge
s += line(XL, YM, XL, YT) + line(XL, YT, 140, YT) + resistor(140, YT, 260, YT) + line(260, YT, XM, YT)
s += line(XM, YT, 380, YT) + resistor(380, YT, 500, YT) + line(500, YT, XR, YT) + line(XR, YT, XR, YM)
s += line(XR, YM, XR, YB) + line(XR, YB, 500, YB) + resistor(500, YB, 380, YB) + line(380, YB, XM, YB)
s += line(XM, YB, 260, YB) + resistor(260, YB, 140, YB) + line(140, YB, XL, YB) + line(XL, YB, XL, YM)
# spokes
s += isrc(XM, YT, XM, YM)              # I'_12 = 2 A, T -> O (down)
s += isrc(XM, YB, XM, YM)              # I'_34 = 4 A, B -> O (up)
s += vsrc(XL, YM, XM, YM)              # V'_41 = 1 V, + at the outer (left) end
s += vsrc(XR, YM, XM, YM)              # V'_23 = 3 V, + at the outer (right) end
for P in ((XL, YM), (XM, YT), (XR, YM), (XM, YB), (XM, YM)):
    s += dot(*P)
s += mesh_arrow(185, 125, 30)
s += mesh_arrow(460, 125, 30)
s += mesh_arrow(460, 285, 30)
s += mesh_arrow(185, 285, 30)
s += end_group()
P = ("n", "′")
s += text(185, YT - 16, [("v", "R"), P, ("sub", "1"), ("n", " = 1 Ω")], anchor="middle")
s += text(460, YT - 16, [("v", "R"), P, ("sub", "2"), ("n", " = 0.5 Ω")], anchor="middle")
s += text(460, YB + 28, [("v", "R"), P, ("sub", "3"), ("n", " = 1/3 Ω")], anchor="middle")
s += text(185, YB + 28, [("v", "R"), P, ("sub", "4"), ("n", " = 1/4 Ω")], anchor="middle")
s += text(XM + 24, 128, [("v", "I"), P, ("sub", "12"), ("n", " = 2 A")])
s += text(XM + 24, 302, [("v", "I"), P, ("sub", "34"), ("n", " = 4 A")])
s += ttext(195, YM - 26, [("v", "V"), P, ("sub", "41"), ("n", " = 1 V")], anchor="middle", color=BLUE)
s += ttext(445, YM - 26, [("v", "V"), P, ("sub", "23"), ("n", " = 3 V")], anchor="middle", color=BLUE)
s += ttext(185, 131, [("v", "i"), P, ("sub", "1")], anchor="middle", color=RED)
s += ttext(460, 131, [("v", "i"), P, ("sub", "2")], anchor="middle", color=RED)
s += ttext(460, 291, [("v", "i"), P, ("sub", "3")], anchor="middle", color=RED)
s += ttext(185, 291, [("v", "i"), P, ("sub", "4")], anchor="middle", color=RED)
s += text(XM - 12, YM - 12, [("v", "O")], anchor="end")
s += text(XM, YT - 12, [("v", "T")], anchor="middle")
s += text(XM, YB + 24, [("v", "B")], anchor="middle")
s += text(20, 420, [("t", "網目 "), ("v", "k"), ("t", " ↔ 原節點 "), ("v", "k"), ("t", "；四個網目電流皆取順時針")])
s += footer()
write('EE-109-01-3-dual.svg', s)
