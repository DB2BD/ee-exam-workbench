"""EE-114-02-1: small-signal T-model of the differential pair.

+V_CC is ac ground (R_C tops), the tail current source I_S is an ac open (only R_S remains from the
common emitter node to ground).  Reference directions: i_e1, i_e2 flow from each base node through r_e
into the common emitter node; i_e1 + i_e2 flows down through R_S; alpha*i_e flows C -> B inside the
dependent source; i_1 flows from the v_1 source into the Q1 base.  v_o is taken + at C2, - at C1."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 720, 470
YTOP, YC, YB, YEW, YG = 50, 130, 230, 320, 400
XS1, XQ1, XE, XQ2, XS2 = 70, 250, 360, 470, 650

s = header(W, H)
s += line(XQ1 - 40, YTOP, XQ2 + 40, YTOP)                        # ac-ground rail (+V_CC)
for xq in (XQ1, XQ2):
    s += resistor(xq, YTOP, xq, YC, zigs=6, lead=18) + dot(xq, YTOP) + dot(xq, YC)
    s += dep_isrc(xq, YC, xq, YB)                                 # alpha i_e : C -> B
    s += dot(xq, YB)
    s += resistor(xq, YB, xq, YEW, zigs=6, lead=24)               # r_e : B -> E
s += line(XQ1, YEW, XQ2, YEW) + dot(XE, YEW)
s += resistor(XE, YEW, XE, YG, zigs=6, lead=18)                   # R_S
# input sources and base wires
s += vsrc(XS1, YB, XS1, YG) + line(XS1, YB, XQ1, YB)
s += vsrc(XS2, YB, XS2, YG) + line(XS2, YB, XQ2, YB)
s += line(XS1, YG, XS2, YG) + dot(XE, YG) + line(XE, YG, XE, YG + 8) + ground(XE, YG + 8)
# output terminals between the collectors
s += line(XQ1, YC, XE - 40 - 3.5, YC) + terminal(XE - 40, YC)
s += line(XQ2, YC, XE + 40 + 3.5, YC) + terminal(XE + 40, YC)
# reference currents (red)
s += red_arrow(XS1 + 50, YB - 14, XS1 + 100, YB - 14)              # i_1
s += red_arrow(XQ1 - 22, YB + 30, XQ1 - 22, YEW - 30)             # i_e1
s += red_arrow(XQ2 + 22, YB + 30, XQ2 + 22, YEW - 30)             # i_e2
s += red_arrow(XE - 22, YEW + 22, XE - 22, YG - 22)               # i_e1 + i_e2
# R_i: looking into the Q1 base
s += arrow(XQ1 - 78, YB + 18, XQ1 - 40, YB + 18)
s += end_group()

t = []
t.append(text(XE, YTOP - 14, [("t", "+"), ("v", "V"), ("vsub", "CC"), ("t", "（交流接地）")], anchor="middle"))
for xq, k in ((XQ1, "1"), (XQ2, "2")):
    side, anc = (-12, "end") if k == "1" else (12, "start")
    t.append(text(xq + side, (YTOP + YC) / 2 + 6, [("v", "R"), ("vsub", "C"), ("n", " = 2 kΩ")], anchor=anc))
    t.append(text(xq + side * 2.2, (YC + YB) / 2 + 6, [("v", "α"), ("v", "i"), ("vsub", "e"), ("sub", k)], anchor=anc))
    t.append(text(xq + (8 if k == "1" else -8), YC - 8, [("v", "C"), ("sub", k)], anchor="start" if k == "1" else "end"))
    t.append(text(xq + (8 if k == "1" else -8), YB + 20, [("v", "B"), ("sub", k)], anchor="start" if k == "1" else "end"))
    t.append(text(xq - side, (YB + YEW) / 2 + 6, [("v", "r"), ("vsub", "e"), ("n", " = 25 Ω")], anchor="start" if k == "1" else "end"))
t.append(ctext(XQ1 - 30, (YB + YEW) / 2 + 6, [("v", "i"), ("vsub", "e"), ("sub", "1")], anchor="end"))
t.append(ctext(XQ2 + 30, (YB + YEW) / 2 + 6, [("v", "i"), ("vsub", "e"), ("sub", "2")]))
t.append(ctext(XS1 + 75, YB - 22, [("v", "i"), ("sub", "1")], anchor="middle"))
t.append(text(XQ1 - 82, YB + 24, [("v", "R"), ("vsub", "i")], anchor="end"))
t.append(text(XE + 10, YEW - 8, [("v", "E")]))
t.append(btext(XE + 10, YEW + 18, [("v", "v"), ("vsub", "e")]))
t.append(text(XE + 12, (YEW + YG) / 2 + 12, [("v", "R"), ("vsub", "S"), ("n", " = 2 kΩ")]))
t.append(ctext(XE - 30, (YEW + YG) / 2 + 12, [("v", "i"), ("vsub", "e"), ("sub", "1"), ("n", " + "), ("v", "i"), ("vsub", "e"), ("sub", "2")], anchor="end"))
t.append(btext(XS1 - 22, (YB + YG) / 2 + 6, [("v", "v"), ("sub", "1")], anchor="end"))
t.append(btext(XS2 - 22, (YB + YG) / 2 + 6, [("v", "v"), ("sub", "2"), ("n", " = "), ("v", "k"), ("v", "v"), ("sub", "1")], anchor="end"))
t.append(btext(XE - 40, YC + 24, [("n", "−")], anchor="middle"))
t.append(btext(XE + 40, YC + 24, [("n", "+")], anchor="middle"))
t.append(btext(XE, YC + 6, [("v", "v"), ("vsub", "o")], anchor="middle"))
t.append(text(20, 440, [("t", "尾端電流源 "), ("v", "I"), ("vsub", "S"), ("t", " 交流開路（不畫），只剩 "), ("v", "R"), ("vsub", "S"),
                        ("t", "；紅色為 KCL 參考方向")]))
t.append(text(20, 462, [("v", "v"), ("vsub", "o"), ("n", " = "), ("v", "v"), ("vsub", "c"), ("sub", "2"), ("n", " − "), ("v", "v"),
                        ("vsub", "c"), ("sub", "1"), ("t", "（"), ("n", "+"), ("t", " 端在 "), ("v", "C"), ("sub", "2"), ("t", "）")]))
s += ''.join(t) + footer()
write('EE-114-02-1-t-model.svg', s)
