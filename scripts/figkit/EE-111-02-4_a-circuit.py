"""EE-111-02-4: small-signal A circuit (open loop with feedback-network loading) of the shunt-series amplifier.
g11 = 0 -> R_F does not load the input (I_in flows only into r_pi1); g22 = R_F in series with R_L in the Q2
emitter loop.  Q1: g_m1 v_pi1 sinks current from the collector node C1; R_C to AC ground (V_CC);
Q2 (common collector): r_pi2 from C1 to emitter E2, beta_T i_b2 from the AC-grounded collector into E2;
I_o = (1 + beta_T) i_b2 flows down through R_L and R_F."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 720, 400
YT, YB = 110, 310
XI, XB, XG, XC, XE, XS = 60, 150, 260, 340, 470, 580
YX = 210
s = header(W, H)
s += isrc(XI, YB, XI, YT) + line(XI, YT, XB, YT) + resistor(XB, YT, XB, YB, zigs=6, lead=40)
s += dep_isrc(XG, YT, XG, YB) + line(XG, YT, XC, YT) + resistor(XC, YT, XC, YB, zigs=6, lead=40)
s += resistor(XC, YT, XE, YT, zigs=6, lead=30)
s += line(XE, YT, XS, YT) + dep_isrc(XS, YB, XS, YT)
s += resistor(XE, YT, XE, YX, zigs=5, lead=22) + resistor(XE, YX, XE, YB, zigs=5, lead=22)
s += line(XI, YB, XS, YB)
for x, y in ((XB, YT), (XC, YT), (XE, YT), (XE, YX), (XB, YB), (XG, YB), (XC, YB), (XE, YB)):
    s += dot(x, y)
s += ground(400, YB)
s += red_arrow(XI - 22, 240, XI - 22, 190)                       # I_in up into the base node
s += red_arrow(375, YT - 18, 425, YT - 18)                       # i_b2 C1 -> E2 through r_pi2
s += red_arrow(XE + 22, 135, XE + 22, 180)                       # I_o down through R_L
s += end_group()
t = []
t.append(text(10, 26, [("t", "A 電路："), ("v", "g"), ("sub", "11"), ("n", " = 0"), ("t", "（"), ("v", "R"), ("vsub", "F"),
                       ("t", " 不接在輸入端）；"), ("v", "g"), ("sub", "22"), ("n", " = "), ("v", "R"), ("vsub", "F"), ("t", " 串入輸出迴路")]))
t.append(ctext(XI - 30, 220, [("v", "I"), ("vsub", "in")], anchor="end"))
t.append(text(XB + 14, (YT + YB) / 2 + 5, [("v", "r"), ("vsub", "π"), ("sub", "1")]))
t.append(polarity(XB - 26, YT, YB, [("v", "v"), ("vsub", "π"), ("sub", "1")], color=BLUE, anchor="end"))
t.append(text(XB, YT - 12, [("v", "B"), ("sub", "1")], anchor="middle"))
t.append(text(XG - 24, (YT + YB) / 2 + 5, [("v", "g"), ("vsub", "m"), ("sub", "1"), ("v", "v"), ("vsub", "π"), ("sub", "1")], anchor="end"))
t.append(text(XC + 14, (YT + YB) / 2 + 5, [("v", "R"), ("vsub", "C")]))
t.append(text(XC, YT - 12, [("v", "C"), ("sub", "1")], anchor="middle"))
t.append(text((XC + XE) / 2, YT + 26, [("v", "r"), ("vsub", "π"), ("sub", "2")], anchor="middle"))
t.append(ctext(400, YT - 26, [("v", "i"), ("vsub", "b"), ("sub", "2")], anchor="middle"))
t.append(text(XE, YT - 12, [("v", "E"), ("sub", "2")], anchor="middle"))
t.append(text(XE - 14, (YT + YX) / 2 + 5, [("v", "R"), ("vsub", "L")], anchor="end"))
t.append(text(XE - 14, (YX + YB) / 2 + 5, [("v", "R"), ("vsub", "F")], anchor="end"))
t.append(text(XE + 10, YX + 20, [("v", "x")]))
t.append(ctext(XE + 30, 162, [("v", "I"), ("vsub", "o")]))
t.append(text(XS + 24, (YT + YB) / 2 + 5, [("v", "β"), ("vsub", "T"), ("v", "i"), ("vsub", "b"), ("sub", "2")]))
t.append(text(XS + 24, (YT + YB) / 2 + 27, [("t", "（集極交流接地）")], anchor="start"))
t.append(text(10, 350, [("t", "節點 "), ("v", "C"), ("sub", "1"), ("t", "："), ("v", "g"), ("vsub", "m"), ("sub", "1"), ("v", "v"), ("vsub", "π"), ("sub", "1"),
                        ("t", " 分給 "), ("v", "R"), ("vsub", "C"), ("t", " 與 "), ("v", "Q"), ("sub", "2"), ("t", " 基極（看入 "),
                        ("v", "r"), ("vsub", "π"), ("sub", "2"), ("n", " + (1 + "), ("v", "β"), ("vsub", "T"), ("n", ")("), ("v", "R"), ("vsub", "L"),
                        ("n", " + "), ("v", "R"), ("vsub", "F"), ("n", ")"), ("t", "）")]))
t.append(text(10, 376, [("v", "I"), ("vsub", "o"), ("n", " = (1 + "), ("v", "β"), ("vsub", "T"), ("n", ")"), ("v", "i"), ("vsub", "b"), ("sub", "2"),
                        ("t", "；圖中箭頭均為參考方向")]))
s += ''.join(t) + footer()
write('EE-111-02-4-a-circuit.svg', s)
