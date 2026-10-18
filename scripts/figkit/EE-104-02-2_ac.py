"""EE-104-02-2: mid-band ac equivalent (T model, base grounded by C_B, capacitors short).

r_e and the controlled source g_m v_be both return to the base, which is ac ground; R_B therefore
hangs from the collector to ground.  Reference: g_m v_be flows C -> B (down), v_be = 0 - v_e."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YR = 100, 280
XV, XRS1, XRS2, XRI, XE, XRE, XRe = 60, 90, 190, 212, 250, 250, 340
XC, XRB, XRL, XO = 440, 520, 600, 660
W, H = 720, 360
s = header(W, H)
s += line(XV, YT, XRS1, YT) + resistor(XRS1, YT, XRS2, YT, zigs=6, lead=12) + line(XRS2, YT, XRe, YT)
s += vsrc(XV, YT, XV, YR)
s += dot(XE, YT) + resistor(XRE, YT, XRE, YR, zigs=6, lead=40) + resistor(XRe, YT, XRe, YR, zigs=6, lead=40)
s += dashed(XRI, YT - 40, XRI, YT + 30) + arrow(XRI - 40, YT - 30, XRI - 2, YT - 30)
# collector side
s += dep_isrc(XC, YT, XC, YR) + line(XC, YT, XO - 3.5, YT) + dot(XC, YT) + dot(XRB, YT) + dot(XRL, YT) + terminal(XO, YT)
s += resistor(XRB, YT, XRB, YR, zigs=6, lead=40) + resistor(XRL, YT, XRL, YR, zigs=6, lead=40)
s += line(XV, YR, XRL, YR) + line(XRL, YR, XO - 3.5, YR) + terminal(XO, YR)
for x in (XRE, XRe, XC, XRB):
    s += dot(x, YR)
s += line(395, YR, 395, YR + 10) + ground(395, YR + 10)
s += end_group()
t = []
t.append(text(XV - 24, 195, [("v", "v"), ("vsub", "s")], anchor="end"))
t.append(text((XRS1 + XRS2) / 2, YT + 28, [("v", "R"), ("vsub", "s"), ("n", " = 50 Ω")], anchor="middle"))
t.append(text(XRI - 44, YT - 38, [("v", "R"), ("vsub", "i")]))
t.append(text(XE - 8, YT - 10, [("v", "E")], anchor="end"))
t.append(btext(XE + 8, YT - 10, [("v", "v"), ("vsub", "e")]))
t.append(text(XRE + 14, 200, [("v", "R"), ("vsub", "E")]))
t.append(text(XRE + 14, 220, [("n", "1 kΩ")]))
t.append(text(XRe + 14, 200, [("v", "r"), ("vsub", "e")]))
t.append(text(XRe + 14, 220, [("n", "50 Ω")]))
t.append(text(XC - 22, YT - 10, [("v", "C")], anchor="end"))
t.append(text(XC - 24, 165, [("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "be")], anchor="end"))
t.append(text(XRB + 14, 200, [("v", "R"), ("vsub", "B")]))
t.append(text(XRB + 14, 220, [("n", "100 kΩ")]))
t.append(text(XRL + 14, 200, [("v", "R"), ("vsub", "L")]))
t.append(text(XRL + 14, 220, [("n", "1.5 kΩ")]))
t.append(polarity(XO + 14, YT, YR, [("v", "v"), ("vsub", "o")]))
t.append(text(300, YR + 34, [("t", "基極 "), ("v", "B"), ("t", " 經 "), ("v", "C"), ("vsub", "B"), ("t", " 交流接地＝下方共同線")], anchor="middle"))
t.append(text(20, YR + 62, [("v", "v"), ("vsub", "be"), ("n", " = 0 − "), ("v", "v"), ("vsub", "e"), ("t", "；"),
                            ("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "be"), ("t", " 參考方向由 "), ("v", "C"), ("t", " 流向 "), ("v", "B"), ("t", "（向下）")]))
s += ''.join(t) + footer()
write('EE-104-02-2-ac.svg', s)
