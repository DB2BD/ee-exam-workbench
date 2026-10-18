"""EE-114-01-5: s-domain circuit (zero initial current, so no initial-condition source); nodes a, c; I_x, I_m, V_o."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 640, 380, 90, 310
XS, XM, XL0, XL1, XR = 110, 270, 350, 450, 530
YC = 190                                                            # node c between dependent source and 5 ohm
s = header(W, H)
s += line(XS, YT, XL0, YT) + coil(XL0, YT, XL1, YT) + line(XL1, YT, XR, YT)
s += line(XS, YB, XR, YB)
s += isrc(XS, YB, XS, YT, r=18)                                     # I_s = 10/s, arrow up into node a
s += dep_vsrc(XM, YT, XM, YC)                                       # 2 I_x, + on top
s += resistor(XM, YC, XM, YB, zigs=6, lead=24)
s += resistor(XR, YT, XR, YB, zigs=6, lead=60)
s += dot(XM, YT) + dot(XM, YC) + dot(XM, YB)
s += line(XM, YB, XM, YB + 12) + ground(XM, YB + 12)
s += tint_arrow(370, YT - 26, 430, YT - 26)                         # I_x, node a -> right branch
s += tint_arrow(XM - 18, 226, XM - 18, 262)                         # I_m, middle branch downward
s += end_group()
s += text(XS - 26, 205, [("v", "I"), ("vsub", "s"), ("n", " = 10/"), ("v", "s")], anchor="end")
s += text(XM - 8, YT - 12, [("v", "a")], anchor="end")
s += text(XM - 12, YC + 5, [("v", "c")], anchor="end")
s += text(XM + 26, 145, [("n", "2"), ("v", "I"), ("vsub", "x")])
s += text(XM + 16, 255, [("n", "5 Ω")])
s += text(400, YT + 32, [("v", "sL"), ("n", " = 2"), ("v", "s"), ("n", " Ω")], anchor="middle")
s += ttext(400, YT - 38, [("v", "I"), ("vsub", "x")], anchor="middle", color=RED)
s += ttext(XM - 26, 250, [("v", "I"), ("vsub", "m")], anchor="end", color=RED)
s += text(XR - 16, 205, [("n", "5 Ω")], anchor="end")
s += ttext(XR + 26, YT + 40, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XR + 26, 205, [("v", "V"), ("vsub", "o")], anchor="middle", color=BLUE)
s += ttext(XR + 26, YB - 14, [("n", "−")], anchor="middle", color=BLUE)
s += text(20, 360, [("v", "s"), ("t", " 域（電感無初始電流，不加初值源）；下導線為參考節點")])
s += footer()
write('EE-114-01-5-s-domain.svg', s)
