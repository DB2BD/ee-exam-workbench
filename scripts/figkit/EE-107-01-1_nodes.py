"""EE-107-01-1: node voltages V1, V2, ground reference, CCVS 15 i_phi and the KCL branch currents at node V1."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 360
XL, XM, XR = 130, 330, 530
YT, YM, YB = 60, 160, 300
s = header(W, H)
s += line(XL, YT, 270, YT) + resistor(270, YT, 390, YT) + line(390, YT, XR, YT)
s += line(XL, YT, XL, YM) + line(XR, YT, XR, YM)
s += resistor(XL, YM, XM, YM, lead=55) + resistor(XM, YM, XR, YM, lead=55)
s += vsrc(XL, YM, XL, YB)
s += resistor(XM, YM, XM, YB, lead=45)
s += dep_vsrc(XR, YM, XR, YB)
s += line(XL, YB, XR, YB) + ground(XM, YB + 14) + line(XM, YB, XM, YB + 14)
for x, y in ((XL, YM), (XM, YM), (XR, YM), (XM, YB)):
    s += dot(x, y)
s += tint_arrow(205, YM + 22, 255, YM + 22)          # I_5: left node -> V1
s += tint_arrow(405, YM + 22, 455, YM + 22)          # I_4: V1 -> V2
s += tint_arrow(XM - 22, 205, XM - 22, 250)          # i_phi down through 20 ohm
s += end_group()
s += text(20, 28, [("t", "下方導線為參考地；左節點被 50 V 源定為 50 V")])
s += text(330, YT - 14, [("n", "1 Ω")], anchor="middle")
s += text(230, YM - 16, [("n", "5 Ω")], anchor="middle")
s += text(430, YM - 16, [("n", "4 Ω")], anchor="middle")
s += text(XL - 24, 236, [("n", "50 V")], anchor="end")
s += text(XM + 16, 236, [("n", "20 Ω")])
s += text(XR + 26, 236, [("n", "15"), ("v", "i"), ("vsub", "ϕ")])
s += ttext(XM + 8, YM - 10, [("v", "V"), ("sub", "1")], color=BLUE)
s += ttext(XR + 8, YM - 10, [("v", "V"), ("sub", "2")], color=BLUE)
s += ttext(230, YM + 44, [("v", "I"), ("sub", "5")], anchor="middle", color=RED)
s += ttext(430, YM + 44, [("v", "I"), ("sub", "4")], anchor="middle", color=RED)
s += ttext(XM - 30, 234, [("v", "i"), ("vsub", "ϕ")], anchor="end", color=RED)
s += footer()
write('EE-107-01-1-nodes.svg', s)
