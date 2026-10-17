"""EE-105-01-1: node voltages V1..V3, top-branch current I_T reference (left -> right) and I_O (down)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 390
X1, X2, X3 = 140, 330, 520
YT, YM, YB = 80, 200, 330
s = header(W, H)
s += line(X1, YT, 210, YT) + vsrc(290, YT, 210, YT) + line(290, YT, 360, YT)
s += resistor(360, YT, 460, YT) + line(460, YT, X3, YT) + line(X1, YT, X1, YM) + line(X3, YT, X3, YM)
s += resistor(X1, YM, X2, YM, lead=50) + isrc(X2, YM, X3, YM)
s += isrc(X1, YB, X1, YM)
s += resistor(X2, YM, X2, YB, lead=40) + resistor(X3, YM, X3, YB, lead=40)
s += line(X1, YB, X3, YB) + line(X2, YB, X2, YB + 14) + ground(X2, YB + 14)
for x, y in ((X1, YM), (X2, YM), (X3, YM), (X2, YB)):
    s += dot(x, y)
s += tint_arrow(385, YT + 22, 435, YT + 22)          # I_T reference: left -> right
s += tint_arrow(X2 - 22, 245, X2 - 22, 290)          # I_O down
s += end_group()
s += text(20, 28, [("t", "下方導線為參考地；單位 V、kΩ、mA")])
s += text(250, YT - 26, [("n", "6 V")], anchor="middle")
s += text(410, YT - 16, [("n", "1 kΩ")], anchor="middle")
s += text(235, YM - 16, [("n", "1 kΩ")], anchor="middle")
s += text(425, YM - 26, [("n", "4 mA")], anchor="middle")
s += text(X1 - 24, 272, [("n", "2 mA")], anchor="end")
s += text(X2 + 16, 272, [("n", "2 kΩ")])
s += text(X3 + 16, 272, [("n", "2 kΩ")])
s += ttext(X1 + 8, YM + 22, [("v", "V"), ("sub", "1")], color=BLUE)
s += ttext(X2 + 8, YM + 22, [("v", "V"), ("sub", "2")], color=BLUE)
s += ttext(X3 + 8, YM + 22, [("v", "V"), ("sub", "3")], color=BLUE)
s += ttext(410, YT + 44, [("v", "I"), ("vsub", "T")], anchor="middle", color=RED)
s += ttext(X2 - 30, 274, [("v", "I"), ("vsub", "O")], anchor="end", color=RED)
s += footer()
write('EE-105-01-1-nodes.svg', s)
