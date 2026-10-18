"""EE-106-02-2: small-signal open-loop model seen at the output node: short-circuit current g_mN v_d
(diff pair + mirror) flowing into the output node, in parallel with r_o2 || r_o4 = r_o/2 and the divider
R_2 + R_1 (series, to ground); the divider tap v_f = beta V_out drives the M_2 gate, v_d = V_in - v_f."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 680, 340
YT, YB = 90, 270
XI, XR, XD, XO = 170, 290, 420, 540
YF = (YT + YB) / 2
s = header(W, H)
s += dep_isrc(XI, YB, XI, YT) + line(XI, YT, XO - 3.5, YT) + terminal(XO, YT)
s += resistor(XR, YT, XR, YB, zigs=6, lead=40)
s += resistor(XD, YT, XD, YF, zigs=5, lead=14) + resistor(XD, YF, XD, YB, zigs=5, lead=14)
s += line(XI, YB, XD, YB) + dot(XR, YT) + dot(XD, YT) + dot(XD, YF) + dot(XR, YB)
s += line(XD, YF, 480, YF) + terminal(483.5, YF)
s += line(300, YB, 300, YB + 0) + line(355, YB, 355, YB + 8) + ground(355, YB + 8)
s += red_arrow(XI + 32, YT - 16, XI + 72, YT - 16)
s += end_group()
t = []
t.append(text(10, 24, [("t", "開迴路小訊號模型（從輸出節點看）：差動對＋電流鏡 = 短路電流 "), ("v", "g"), ("vsub", "mN"), ("v", "v"), ("vsub", "d")]))
t.append(text(XI - 24, YF - 2, [("v", "g"), ("vsub", "mN"), ("v", "v"), ("vsub", "d")], anchor="end"))
t.append(text(XI - 24, YF + 20, [("t", "（流入輸出節點）")], anchor="end"))
t.append(ctext(XI + 52, YT - 24, [("v", "i"), ("vsub", "sc")], anchor="middle"))
t.append(text(XR + 14, YF - 4, [("v", "r"), ("vsub", "o"), ("n", "/2")]))
t.append(text(XR + 14, YF + 18, [("n", "("), ("v", "r"), ("vsub", "o"), ("sub", "2"), ("n", " ∥ "), ("v", "r"), ("vsub", "o"), ("sub", "4"), ("n", ")")]))
t.append(text(XD - 14, (YT + YF) / 2 + 5, [("v", "R"), ("sub", "2")], anchor="end"))
t.append(text(XD - 14, (YF + YB) / 2 + 5, [("v", "R"), ("sub", "1")], anchor="end"))
t.append(ctext(XO, YT - 14, [("v", "V"), ("vsub", "out")], anchor="middle", color=BLUE))
t.append(ctext(492, YF + 5, [("v", "v"), ("vsub", "f"), ("n", " = "), ("v", "βV"), ("vsub", "out")], color=BLUE))
t.append(text(492, YF + 27, [("t", "→ "), ("v", "M"), ("sub", "2"), ("t", " 閘極")]))
t.append(text(10, 304, [("v", "v"), ("vsub", "d"), ("n", " = "), ("v", "V"), ("vsub", "in"), ("n", " − "), ("v", "v"), ("vsub", "f"), ("t", "，"), ("v", "β"), ("n", " = "), ("v", "R"), ("sub", "1"), ("n", "/("), ("v", "R"), ("sub", "1"), ("n", " + "), ("v", "R"), ("sub", "2"), ("n", ")")]))
t.append(text(10, 328, [("t", "輸出節點對地總電阻 "), ("v", "R"), ("vsub", "o"), ("n", " = ("), ("v", "r"), ("vsub", "o"), ("n", "/2) ∥ ("), ("v", "R"), ("sub", "1"), ("n", " + "), ("v", "R"), ("sub", "2"), ("n", ")")]))
s += ''.join(t) + footer()
write('EE-106-02-2-feedback.svg', s)
