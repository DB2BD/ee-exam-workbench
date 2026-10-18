"""EE-105-02-1: open-circuit time constant of the bridging C: v_S = 0, C_1, C_2 shorted, C_i, C_o open.
Input side R_in' = R_s || R_i, output side R_out' = R_o || R_L, g_m v_i from Y to ground;
test current I_x enters node X from the test source and returns from node Y; v_x = v_X - v_Y."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 640, 320
YT, YB, YU = 160, 270, 92
XRI, XX, XY, XRO = 110, 200, 420, 520
s = header(W, H)
s += line(XRI, YT, XX, YT) + resistor(XRI, YT, XRI, YB, zigs=6, lead=24)
s += line(XX, YT, XX, YU) + isrc(XY, YU, XX, YU) + line(XY, YU, XY, YT)
s += line(XY, YT, XRO, YT) + dep_isrc(XY, YT, XY, YB) + resistor(XRO, YT, XRO, YB, zigs=6, lead=24)
s += line(XRI, YB, XRO, YB) + dot(XX, YT) + dot(XY, YT) + dot(XY, YB)
s += line(310, YB, 310, YB + 8) + ground(310, YB + 8)
s += end_group()
t = []
t.append(text(10, 24, [("v", "v"), ("vsub", "S"), ("n", " = 0"), ("t", "，"), ("v", "C"), ("sub", "1"), ("n", "、"), ("v", "C"), ("sub", "2"), ("t", " 短路，"), ("v", "C"), ("vsub", "i"), ("n", "、"), ("v", "C"), ("vsub", "o"), ("t", " 開路，在 "), ("v", "C"), ("t", " 的位置接測試電流 "), ("v", "I"), ("vsub", "x")]))
t.append(text(XRI - 12, (YT + YB) / 2 - 4, [("v", "R"), ("vsub", "in"), ("n", "′")], anchor="end"))
t.append(text(XRI - 12, (YT + YB) / 2 + 16, [("n", "1.60 kΩ")], anchor="end"))
t.append(text(XRO + 12, (YT + YB) / 2 - 4, [("v", "R"), ("vsub", "out"), ("n", "′")]))
t.append(text(XRO + 12, (YT + YB) / 2 + 16, [("n", "6 kΩ")]))
t.append(text(XY - 22, (YT + YB) / 2 + 5, [("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "i")], anchor="end"))
t.append(text(XX - 8, YT - 8, [("v", "X")], anchor="end"))
t.append(text(XY + 8, YT - 8, [("v", "Y")]))
t.append(ctext((XX + XY) / 2, YU - 24, [("v", "I"), ("vsub", "x")], anchor="middle"))
t.append(polarity(XX + 14, YT + 4, YB - 4, [("v", "v"), ("vsub", "i")]))
t.append(ctext(XX + 18, YU + 22, [("n", "+")], anchor="middle", color=BLUE))
t.append(ctext(XY - 18, YU + 22, [("n", "−")], anchor="middle", color=BLUE))
t.append(ctext((XX + XY) / 2, YU + 40, [("v", "v"), ("vsub", "x")], anchor="middle", color=BLUE))
t.append(text(10, 308, [("v", "R"), ("vsub", "C"), ("n", " = "), ("v", "v"), ("vsub", "x"), ("n", "/"), ("v", "I"), ("vsub", "x")]))
s += ''.join(t) + footer()
write('EE-105-02-1-octc-c.svg', s)
