"""EE-105-02-1: small-signal model of the amplifier stage (official topology): v_S - R_s - C_1 - input node
(R_i, C_i to ground, voltage v_i), transconductance g_m v_i drawn from the output node to ground with R_o, C_o,
bridging C between input and output nodes, C_2 to R_L (v_O)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 720, 330
YT, YB, YU = 130, 250, 70
XS, XR1, XR2, XC1a, XX = 40, 64, 124, 134, 214
XRI, XCI = 250, 310
XY, XRO, XCO, XC2, XRL, XO = 410, 470, 530, 560, 640, 690
s = header(W, H)
s += f'<circle cx="{XS}" cy="{(YT + YB) / 2}" r="16"/>\n' + line(XS, YT, XS, (YT + YB) / 2 - 16) + line(XS, (YT + YB) / 2 + 16, XS, YB)
s += f'<path d="M{XS - 8} {(YT + YB) / 2} C{XS - 4} {(YT + YB) / 2 - 8} {XS} {(YT + YB) / 2 - 8} {XS} {(YT + YB) / 2} S{XS + 4} {(YT + YB) / 2 + 8} {XS + 8} {(YT + YB) / 2}"/>\n'
s += line(XS, YT, XR1, YT) + resistor(XR1, YT, XR2, YT, zigs=6, lead=8) + line(XR2, YT, XC1a, YT)
s += cap(XC1a, YT, XX, YT) + line(XX, YT, XCI, YT)
s += resistor(XRI, YT, XRI, YB, zigs=6, lead=26) + cap(XCI, YT, XCI, YB)
s += line(XX, YT, XX, YU) + cap(XX, YU, XY, YU) + line(XY, YU, XY, YT)
s += dep_isrc(XY, YT, XY, YB) + line(XY, YT, XCO, YT) + resistor(XRO, YT, XRO, YB, zigs=6, lead=26) + cap(XCO, YT, XCO, YB)
s += cap(XCO, YT, XC2 + 50, YT) + line(XC2 + 50, YT, XRL, YT) + resistor(XRL, YT, XRL, YB, zigs=6, lead=26)
s += line(XRL, YT, XO - 3.5, YT) + terminal(XO, YT) + line(XS, YB, XO - 3.5, YB) + terminal(XO, YB)
for x in (XX, XRI, XY, XRO, XRL):
    s += dot(x, YT)
for x in (XRI, XCI, XY, XRO, XCO, XRL):
    s += dot(x, YB)
s += line(360, YB, 360, YB + 8) + ground(360, YB + 8)
s += end_group()
t = []
t.append(text(10, 24, [("t", "小訊號等效（放大器以跨導模型表示，"), ("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "i"), ("t", " 由輸出節點流向地）")]))
t.append(text(XS - 22, (YT + YB) / 2 + 5, [("v", "v"), ("vsub", "S")], anchor="end"))
t.append(text((XR1 + XR2) / 2, YT - 14, [("v", "R"), ("vsub", "s")], anchor="middle"))
t.append(text((XC1a + XX) / 2, YT - 22, [("v", "C"), ("sub", "1")], anchor="middle"))
t.append(text(XX + 6, YT - 8, [("t", "輸入")]))
t.append(text(XRI + 12, (YT + YB) / 2 + 5, [("v", "R"), ("vsub", "i")]))
t.append(text(XCI + 20, (YT + YB) / 2 + 5, [("v", "C"), ("vsub", "i")]))
t.append(text((XX + XY) / 2, YU - 20, [("v", "C"), ("n", " = 3.32 pF")], anchor="middle"))
t.append(text(XY + 4, YT - 10, [("t", "輸出")]))
t.append(text(XY - 22, (YT + YB) / 2 + 5, [("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "i")], anchor="end"))
t.append(text(XRO + 12, (YT + YB) / 2 + 5, [("v", "R"), ("vsub", "o")]))
t.append(text(XCO + 18, (YT + YB) / 2 + 30, [("v", "C"), ("vsub", "o")]))
t.append(text(XC2 + 25, YT - 22, [("v", "C"), ("sub", "2")], anchor="middle"))
t.append(text(XRL + 12, (YT + YB) / 2 + 5, [("v", "R"), ("vsub", "L")]))
t.append(polarity(XRI - 24, YT + 6, YB - 4, [("v", "v"), ("vsub", "i")], anchor="end"))
t.append(polarity(XO + 2, YT + 10, YB - 4, [("v", "v"), ("vsub", "O")]))
t.append(text(10, 290, [("v", "R"), ("vsub", "s"), ("n", " = 2 kΩ，"), ("v", "R"), ("vsub", "i"), ("n", " = 8 kΩ，"), ("v", "R"), ("vsub", "o"), ("n", " = 15 kΩ，"), ("v", "R"), ("vsub", "L"), ("n", " = 10 kΩ，"), ("v", "g"), ("vsub", "m"), ("n", " = 40 mA/V")]))
t.append(text(10, 314, [("v", "C"), ("sub", "1"), ("n", " = 0.01 μF，"), ("v", "C"), ("sub", "2"), ("n", " = 0.04 μF，"), ("v", "C"), ("vsub", "i"), ("n", " = 5 pF，"), ("v", "C"), ("vsub", "o"), ("n", " = 1 pF")]))
s += ''.join(t) + footer()
write('EE-105-02-1-model.svg', s)
