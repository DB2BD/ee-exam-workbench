"""EE-110-02-1: collector-feedback bias circuit (the stem asks to draw it).

R_C from V_CC to the collector node carries I_C + I_B; R_B from the collector node back to the base
carries I_B (C -> B); emitter grounded.  V_CE is taken at the collector node, V_BE at the base, both
against the ground reference line."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

BX, BY = 300, 230                 # base bar centre
YCN, YG = 150, 320                # collector node row, ground reference line
XRB, XO = 200, 470                # R_B column, output terminal column

W, H = 600, 410
s = header(W, H)
sym, (xc, yc), (xe, ye) = npn(BX, BY, lead=30)
s += sym
# V_CC -> R_C -> collector node -> collector
s += terminal(xc, 36) + resistor(xc, 39.5, xc, YCN, zigs=6, lead=16) + line(xc, YCN, xc, yc) + dot(xc, YCN)
# collector node -> R_B -> base
s += line(XRB, YCN, xc, YCN) + resistor(XRB, YCN, XRB, BY, zigs=6, lead=12) + line(XRB, BY, BX, BY)
s += dot(262, BY)
# emitter -> ground reference line
s += line(xe, ye, xe, YG) + dot(xe, YG) + line(236, YG, XO - 3.5, YG) + line(xe, YG, xe, YG + 12) + ground(xe, YG + 12)
s += terminal(XO, YG)
# output terminal at the collector node (V_CE)
s += line(xc, YCN, XO - 3.5, YCN) + terminal(XO, YCN)
# currents (reference directions used in the KVL equations)
s += red_arrow(xc + 24, 62, xc + 24, 112)          # I_C + I_B down through R_C
s += red_arrow(XRB + 20, 168, XRB + 20, 212)       # I_B down through R_B (C -> B)
s += red_arrow(xc + 14, 160, xc + 14, 190)         # I_C into the collector
s += end_group()
t = []
t.append(text(xc + 12, 32, [("v", "V"), ("vsub", "CC"), ("n", " = 12 V")]))
t.append(text(xc - 14, 92, [("v", "R"), ("vsub", "C")], anchor="end"))
t.append(text(xc - 14, 112, [("n", "10 kΩ")], anchor="end"))
t.append(ctext(xc + 32, 92, [("v", "I"), ("vsub", "C"), ("n", " + "), ("v", "I"), ("vsub", "B")]))
t.append(text(XRB - 14, 186, [("v", "R"), ("vsub", "B")], anchor="end"))
t.append(text(XRB - 14, 206, [("n", "100 kΩ")], anchor="end"))
t.append(ctext(XRB + 28, 196, [("v", "I"), ("vsub", "B")]))
t.append(ctext(xc + 22, 184, [("v", "I"), ("vsub", "C")]))
t.append(text(xc + 10, YCN - 8, [("t", "集極 "), ("v", "C")]))
t.append(text(262, BY - 10, [("t", "基極 "), ("v", "B")], anchor="middle"))
t.append(text(xe + 10, YG - 8, [("t", "射極 "), ("v", "E")]))
t.append(polarity(XO + 16, YCN, YG, [("v", "V"), ("vsub", "CE")]))
t.append(polarity(262, BY, YG, [("v", "V"), ("vsub", "BE")], anchor="end"))
t.append(text(20, 372, [("t", "集極迴路："), ("v", "V"), ("vsub", "CC"), ("n", " → "), ("v", "R"), ("vsub", "C"), ("n", " → "), ("v", "C"),
                        ("n", " → "), ("v", "E"), ("t", "；基極迴路："), ("v", "C"), ("n", " → "), ("v", "R"), ("vsub", "B"), ("n", " → "),
                        ("v", "B"), ("n", " → "), ("v", "E")]))
t.append(text(20, 396, [("t", "電流方向為 KVL 所用參考方向；"), ("v", "R"), ("vsub", "C"), ("t", " 同時流過 "), ("v", "I"), ("vsub", "C"),
                        ("t", " 與 "), ("v", "I"), ("vsub", "B")]))
s += ''.join(t) + footer()
write('EE-110-02-1-circuit.svg', s)
