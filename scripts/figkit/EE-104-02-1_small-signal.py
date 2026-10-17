"""EE-104-02-1: PMOS small-signal equivalent (+5 V and -5 V are ac ground; R_S unbypassed; R_D || C_L at the drain).

Reference direction: i_d = g_m v_sg flows source -> drain; it enters S from ground through R_S
(source-node KCL -v_s/R_S = i_d) and leaves D through R_D || C_L (v_o = i_d Z)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YD, YR = 90, 200, 300            # source node row, drain node row, ground rail
XG, XRS, XS, XRD, XCL, XO = 80, 210, 330, 450, 560, 650

W, H = 720, 366
s = header(W, H)
# gate: v_i from G to ground (200 kOhm in parallel with the ideal source does not change v_g)
s += terminal(XG, YT) + vsrc(XG, YT + 3.5, XG, YR)
# source node S: R_S to ground, dependent source S -> D
s += line(XRS, YT, XS, YT) + dot(XS, YT) + resistor(XRS, YT, XRS, YR, zigs=6, lead=40)
s += dep_isrc(XS, YT, XS, YD)
# drain node D: R_D and C_L to ground, output terminal
s += line(XS, YD, XO - 3.5, YD) + dot(XS, YD) + dot(XRD, YD) + dot(XCL, YD) + terminal(XO, YD)
s += resistor(XRD, YD, XRD, YR, zigs=6, lead=14) + cap(XCL, YD, XCL, YR)
s += line(XG, YR, XCL, YR) + dot(XRS, YR) + dot(XRD, YR) + line(270, YR, 270, YR + 10) + ground(270, YR + 10) + line(XCL, YR, XO, YR) + terminal(XO, YR)
# currents (reference i_d: up through R_S into S, S -> D, down out of D)
s += red_arrow(XRS - 22, 250, XRS - 22, 150)
s += red_arrow(XS + 50, YD + 14, XS + 100, YD + 14)
s += end_group()
t = []
t.append(text(XG + 12, YT - 10, [("v", "G")]))
t.append(btext(XG + 12, YT + 14, [("v", "v"), ("vsub", "g"), ("n", " = "), ("v", "v"), ("vsub", "i")]))
t.append(text(XG - 24, 200, [("v", "v"), ("vsub", "i")], anchor="end"))
t.append(text(XS, YT - 14, [("v", "S")], anchor="middle"))
t.append(btext(XS + 10, YT - 14, [("n", "（"), ("v", "v"), ("vsub", "s"), ("n", "）")]))
t.append(text(XRS + 14, 200, [("v", "R"), ("vsub", "S"), ("n", " = 5.50 kΩ")]))
t.append(ctext(XRS - 30, 205, [("v", "i"), ("vsub", "d")], anchor="end"))
t.append(text(XS + 24, 140, [("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "sg")]))
t.append(text(XS + 24, 162, [("n", "0.40 mA/V × "), ("v", "v"), ("vsub", "sg")]))
t.append(text(XS - 10, YD + 22, [("v", "D")], anchor="end"))
t.append(ctext(XS + 75, YD + 34, [("v", "i"), ("vsub", "d")], anchor="middle"))
t.append(text(XRD + 14, 256, [("v", "R"), ("vsub", "D")]))
t.append(text(XRD + 14, 276, [("n", "9.50 kΩ")]))
t.append(text(XCL + 20, 256, [("v", "C"), ("vsub", "L")]))
t.append(text(XCL + 20, 276, [("n", "10 pF")]))
t.append(polarity(XO + 18, YD, YR, [("v", "v"), ("vsub", "o")]))
t.append(text(20, 354, [("v", "v"), ("vsub", "sg"), ("n", " = "), ("v", "v"), ("vsub", "s"), ("n", " − "), ("v", "v"), ("vsub", "i"), ("t", "；"),
                        ("n", "+5 V、−5 V "), ("t", "對交流皆為地；閘極不取電流")]))
s += ''.join(t) + footer()
write('EE-104-02-1-small-signal.svg', s)
