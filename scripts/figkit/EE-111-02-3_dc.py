"""EE-111-02-3: dc bias (coupling capacitor open; gate draws no dc current).

I_R1 flows V_DD -> R_1 -> gate node -> R_2 -> ground (same current in both); I_D flows
V_DD -> R_D -> drain -> source -> R_S -> ground.  V_S = I_D R_S = V_OV and V_G = V_GS + V_S."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YGN, YB = 50, 200, 350         # V_DD rail, gate row, ground row
XR, GX = 210, 330                  # divider column, gate plate x

W, H = 640, 420
s = header(W, H)
sym, (xd, yd), (xs, ys) = nmos(GX, YGN, lead=24)
s += sym
YDN, YSN = yd - 10, ys + 10        # drain / source node rows
s += line(XR, YT, xd, YT) + dot(XR, YT)
s += resistor(XR, YT, XR, YGN, zigs=6, lead=24) + resistor(XR, YGN, XR, YB, zigs=6, lead=24)
s += line(XR, YGN, GX, YGN) + dot(XR, YGN)
s += cap(70, YGN, XR - 50, YGN) + terminal(66.5, YGN)
s += line(XR - 50, YGN, XR, YGN)
s += resistor(xd, YT, xd, YDN, zigs=6, lead=12) + line(xd, YDN, xd, yd) + dot(xd, YDN)
s += line(xs, ys, xs, YSN) + dot(xs, YSN) + resistor(xs, YSN, xs, YB, zigs=6, lead=24)
s += line(xs, YSN, xs + 56.5, YSN) + terminal(xs + 60, YSN) + terminal(xs + 60, YB)
s += line(XR, YB, xs + 56.5, YB) + line(270, YB, 270, YB + 10) + ground(270, YB + 10)
# currents
s += red_arrow(XR - 22, 90, XR - 22, 134)          # I_R1 through R_1
s += red_arrow(XR - 22, 248, XR - 22, 292)         # I_R2 = I_R1 through R_2
s += red_arrow(xd + 24, 62, xd + 24, 104)          # I_D through R_D
s += red_arrow(xs + 24, ys + 26, xs + 24, ys + 70)  # I_D through R_S
s += end_group()
t = []
t.append(text(XR + 10, YT - 12, [("v", "V"), ("vsub", "DD"), ("n", " = 1.8 V")]))
t.append(text(XR + 14, 132, [("v", "R"), ("sub", "1")]))
t.append(text(XR + 14, 286, [("v", "R"), ("sub", "2")]))
t.append(ctext(XR - 30, 118, [("v", "I"), ("vsub", "R"), ("sub", "1"), ("n", " = 0.167 mA")], anchor="end"))
t.append(ctext(XR - 30, 276, [("v", "I"), ("vsub", "R"), ("sub", "2"), ("n", " = "), ("v", "I"), ("vsub", "R"), ("sub", "1")], anchor="end"))
t.append(text(74, YGN - 24, [("v", "v"), ("vsub", "in")]))
t.append(text(110, YGN + 34, [("t", "直流開路")], anchor="middle"))
t.append(btext(XR + 14, YGN + 26, [("v", "V"), ("vsub", "G"), ("n", " = 590.20 mV")]))
t.append(text(xd - 14, 96, [("v", "R"), ("vsub", "D"), ("n", " = 200 Ω")], anchor="end"))
t.append(ctext(xd + 32, 90, [("v", "I"), ("vsub", "D"), ("n", " = 3.17 mA")]))
t.append(text(xd + 10, YGN + 4, [("v", "M"), ("sub", "1")]))
t.append(text(xs - 14, 300, [("v", "R"), ("vsub", "S"), ("n", " = 30 Ω")], anchor="end"))
t.append(ctext(xs + 32, ys + 54, [("v", "I"), ("vsub", "D")]))
t.append(polarity(xs + 70, YSN, YB, [("v", "V"), ("vsub", "S"), ("n", " = "), ("v", "V"), ("vsub", "OV"), ("n", " = 95.10 mV")]))
t.append(text(20, 404, [("v", "V"), ("vsub", "G"), ("n", " = "), ("v", "V"), ("vsub", "GS"), ("n", " + "), ("v", "V"), ("vsub", "S"),
                        ("n", " = ("), ("v", "V"), ("vsub", "TH"), ("n", " + "), ("v", "V"), ("vsub", "OV"), ("n", ") + "), ("v", "V"), ("vsub", "OV"),
                        ("t", "；閘極不取直流電流")]))
s += ''.join(t) + footer()
write('EE-111-02-3-dc.svg', s)
