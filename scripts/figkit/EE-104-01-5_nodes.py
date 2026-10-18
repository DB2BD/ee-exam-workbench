"""EE-104-01-5: g-parameter circuit with node names P, Q, port reference directions and the two branch currents at Q."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 680, 330
X1, XP, XQ, X2 = 60, 330, 490, 620
YT, YB = 90, 270
s = header(W, H)
s += line(X1 + 4, YT, 90, YT) + resistor(90, YT, 170, YT) + line(170, YT, 190, YT)
s += coil(190, YT, 270, YT, turns=4) + line(270, YT, XP, YT)
s += line(XP, YT, 370, YT) + resistor(370, YT, 450, YT) + line(450, YT, X2 - 4, YT)
s += dep_vsrc(XP, YT, XP, YB)
s += cap(XQ, YT, XQ, YB)
s += line(X1 + 4, YB, X2 - 4, YB)
s += terminal(X1, YT) + terminal(X1, YB) + terminal(X2, YT) + terminal(X2, YB)
for p in ((XP, YT), (XQ, YT), (XP, YB), (XQ, YB)):
    s += dot(*p)
s += tint_arrow(84, YT - 16, 124, YT - 16)            # I1 into port 1
s += tint_arrow(600, YT - 16, 560, YT - 16)           # I2 into port 2 (towards Q)
s += tint_arrow(XQ + 18, 150, XQ + 18, 194)           # I_C down the -j50 ohm
s += tint_arrow(440, YT + 18, 390, YT + 18)           # I_R from Q to P through 500 ohm
s += end_group()
s += text(20, 30, [("t", "下方導線為參考；"), ("v", "P"), ("t", " 點電壓由相依源固定：")]
          + [("v", "V"), ("vsub", "P"), ("n", " = 100"), ("v", "I"), ("sub", "2")])
s += text(130, YT + 30, [("n", "20 Ω")], anchor="middle")
s += text(230, YT + 30, [("v", "j"), ("n", "10 Ω")], anchor="middle")
s += text(410, YT - 14, [("n", "500 Ω")], anchor="middle")
s += text(XP - 24, 186, [("n", "100"), ("v", "I"), ("sub", "2")], anchor="end")
s += text(XQ - 22, 186, [("n", "−"), ("v", "j"), ("n", "50 Ω")], anchor="end")
s += text(XP, YT - 14, [("v", "P")], anchor="middle")
s += text(XQ, YT - 14, [("v", "Q")], anchor="middle")
s += ttext(104, YT - 26, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(580, YT - 26, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += ttext(XQ + 30, 178, [("v", "I"), ("vsub", "C")], color=RED)
s += ttext(415, YT + 46, [("v", "I"), ("vsub", "R")], anchor="middle", color=RED)
s += ttext(X1, YT + 30, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(X1, 186, [("v", "V"), ("sub", "1")], anchor="middle", color=BLUE)
s += ttext(X1, YB - 18, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(X2, YT + 30, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(X2, 186, [("v", "V"), ("sub", "2")], anchor="middle", color=BLUE)
s += ttext(X2, YB - 18, [("n", "−")], anchor="middle", color=BLUE)
s += footer()
write('EE-104-01-5-nodes.svg', s)
