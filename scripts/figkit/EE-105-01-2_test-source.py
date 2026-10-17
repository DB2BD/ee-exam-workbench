"""EE-105-01-2: no independent source -> test voltage V_t at A-B (B = ground), test current I_t into A; I_x down the 1 kOhm."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 680, 330
X0, X1, XA, XT = 110, 290, 450, 590
YT, YB = 80, 270
s = header(W, H)
s += dep_vsrc(X0, YT, X0, YB)
s += line(X0, YT, 140, YT) + resistor(140, YT, 250, YT) + line(250, YT, X1, YT)
s += line(X1, YT, 330, YT) + resistor(330, YT, 420, YT) + line(420, YT, XT, YT)
s += resistor(X1, YT, X1, YB, lead=50) + resistor(XA, YT, XA, YB, lead=50)
s += line(X0, YB, XT, YB) + vsrc(XT, YT, XT, YB)
for p in ((X1, YT), (XA, YT), (X1, YB), (XA, YB)):
    s += dot(*p)
s += line(X1, YB, X1, YB + 12) + ground(X1, YB + 12)
s += tint_arrow(X1 - 20, 196, X1 - 20, 240)          # I_x down the 1 kOhm
s += tint_arrow(XT - 10, YT - 16, XT - 60, YT - 16)  # I_t from the test source into A
s += end_group()
s += text(20, 30, [("t", "無獨立源：在 "), ("v", "A"), ("t", "–"), ("v", "B"), ("t", " 加測試電壓 "), ("v", "V"), ("vsub", "t"), ("t", "（"), ("v", "B"), ("t", " 為地）；單位 V、kΩ、mA")])
s += text(X0 + 26, 172, [("n", "2000"), ("v", "I"), ("vsub", "x")])
s += text(X0 + 26, 196, [("n", "= 2"), ("v", "V"), ("sub", "1")])
s += text(195, YT - 16, [("n", "2 kΩ")], anchor="middle")
s += text(375, YT - 16, [("n", "3 kΩ")], anchor="middle")
s += text(X1 + 16, 176, [("n", "1 kΩ")])
s += text(XA + 16, 176, [("n", "2 kΩ")])
s += ttext(X1 + 8, YT + 24, [("v", "V"), ("sub", "1")], color=BLUE)
s += ttext(XA + 8, YT + 24, [("v", "V"), ("vsub", "t")], color=BLUE)
s += text(XA, YT - 12, [("v", "A")], anchor="middle")
s += text(XA, YB + 24, [("v", "B")], anchor="middle")
s += ttext(XT + 26, 182, [("v", "V"), ("vsub", "t")], color=BLUE)
s += ttext(X1 - 28, 224, [("v", "I"), ("vsub", "x")], anchor="end", color=RED)
s += ttext(XT - 35, YT - 26, [("v", "I"), ("vsub", "t")], anchor="middle", color=RED)
s += footer()
write('EE-105-01-2-test-source.svg', s)
