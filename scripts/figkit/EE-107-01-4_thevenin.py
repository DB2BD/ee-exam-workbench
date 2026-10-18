"""EE-107-01-4: Thevenin equivalent seen from a-b (V_oc = V_a - V_b reference, + at a) with R_L = R_th."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 560, 300
XS, XT, XL = 110, 330, 440
YT, YB = 70, 230
s = header(W, H)
s += vsrc(XS, YT, XS, YB)
s += line(XS, YT, 170, YT) + resistor(170, YT, 260, YT) + line(260, YT, XT - 4, YT) + terminal(XT, YT)
s += line(XS, YB, XT - 4, YB) + terminal(XT, YB)
s += line(XT + 4, YT, XL, YT) + resistor(XL, YT, XL, YB, zigs=6, lead=40) + line(XL, YB, XT + 4, YB)
s += line(XL - 16, 172, XL + 18, 124) + arrow(XL + 8, 138, XL + 18, 124)         # variable-resistor arrow
s += end_group()
s += ttext(XS - 24, 146, [("v", "V"), ("vsub", "oc")], anchor="end", color=BLUE)
s += ttext(XS - 24, 168, [("n", "= −210 V")], anchor="end", color=BLUE)
s += text(215, YT - 16, [("v", "R"), ("vsub", "th"), ("n", " = 35 Ω")], anchor="middle")
s += text(XT, YT - 14, [("v", "a")], anchor="middle")
s += text(XT, YB + 24, [("v", "b")], anchor="middle")
s += text(XL + 24, 156, [("v", "R"), ("vsub", "L")])
s += text(XL + 24, 178, [("n", "= "), ("v", "R"), ("vsub", "th")])
s += text(20, 288, [("t", "負號表示 "), ("v", "a"), ("t", " 端實際比 "), ("v", "b"), ("t", " 端低 210 V；功率只看 |"), ("v", "V"), ("vsub", "oc"), ("n", "|")])
s += footer()
write('EE-107-01-4-thevenin.svg', s)
