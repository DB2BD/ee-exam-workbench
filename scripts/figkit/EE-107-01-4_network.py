"""EE-107-01-4: a-b network with R_L removed; ideal 4:1 transformer, primary dot top, secondary dot bottom.

Reference directions as in the note: I_p into the primary dot, I_c through the secondary coil from a to N
(leaving the secondary dot), I_p + I_c down through 20 ohm; V_p (+ at primary dot), V_s = V_N - V_a (+ at N).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 360
XS, XP, XN, XSEC, XA = 80, 270, 310, 350, 560
YT, YB, YC0, YC1, YN = 80, 310, 105, 195, 235
s = header(W, H)
s += vsrc(XS, YT, XS, YB)
s += line(XS, YT, 110, YT) + resistor(110, YT, 200, YT) + line(200, YT, XP, YT)
s += line(XP, YT, XP, YC0) + coil(XP, YC0, XP, YC1) + line(XP, YC1, XP, YN) + line(XP, YN, XN, YN)
s += line(XSEC, YT, XSEC, YC0) + coil(XSEC, YC1, XSEC, YC0) + line(XSEC, YC1, XSEC, YN) + line(XSEC, YN, XN, YN)
s += line(XN - 5, 112, XN - 5, 188) + line(XN + 5, 112, XN + 5, 188)          # iron core
s += resistor(XN, YN, XN, YB, zigs=6, lead=14)
s += line(XSEC, YT, XA - 4, YT) + terminal(XA, YT)
s += line(XS, YB, XA - 4, YB) + terminal(XA, YB)
s += dot(XP, YT) + dot(XN, YN) + dot(XN, YB)
s += '<circle cx="256" cy="112" r="3.6" fill="#000" stroke="none"/>\n'       # primary dot: top
s += '<circle cx="364" cy="188" r="3.6" fill="#000" stroke="none"/>\n'       # secondary dot: bottom (N side)
s += tint_arrow(212, YT, 248, YT)                                            # I_p into the primary dot
s += tint_arrow(470, YT, 430, YT)                                            # I_c from a into the secondary coil
s += tint_arrow(XN + 22, 252, XN + 22, 286)                                  # I_p + I_c down through 20 ohm
s += end_group()
s += text(155, YT - 16, [("n", "60 Ω")], anchor="middle")
s += text(XN - 14, 285, [("n", "20 Ω")], anchor="end")
s += text(XN, 40, [("t", "理想 "), ("n", "4 : 1")], anchor="middle")
s += ttext(XS + 24, 190, [("n", "840∠0° V")], color=BLUE)
s += ttext(XS + 24, 212, [("t", "（有效值）")], color=BLUE)
s += ttext(230, YT - 12, [("v", "I"), ("vsub", "p")], anchor="middle", color=RED)
s += ttext(450, YT - 12, [("v", "I"), ("vsub", "c")], anchor="middle", color=RED)
s += ttext(XN + 32, 274, [("v", "I"), ("vsub", "p"), ("n", " + "), ("v", "I"), ("vsub", "c")], color=RED)
s += ttext(XP - 22, 136, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XP - 22, 190, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XP - 30, 168, [("v", "V"), ("vsub", "p")], anchor="end", color=BLUE)
s += ttext(XSEC + 22, 180, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XSEC + 22, 128, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XSEC + 32, 160, [("v", "V"), ("vsub", "s")], color=BLUE)
s += text(XP + 9, YT + 20, [("n", "1")])
s += text(XN - 12, YN - 8, [("v", "N")], anchor="end")
s += text(XA + 14, YT + 6, [("v", "a")])
s += text(XA + 14, YB + 6, [("v", "b")])
s += text(XA + 14, YB + 28, [("t", "（參考 0 V）")], anchor="middle")
s += text(470, 200, [("v", "R"), ("vsub", "L"), ("t", " 已移開")], anchor="middle")
s += text(470, 222, [("t", "（求 "), ("v", "V"), ("vsub", "oc"), ("t", "、"), ("v", "R"), ("vsub", "th"), ("t", "）")], anchor="middle")
s += footer()
write('EE-107-01-4-network.svg', s)
