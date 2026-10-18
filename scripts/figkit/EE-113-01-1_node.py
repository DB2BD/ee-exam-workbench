"""EE-113-01-1: single-node circuit after reducing 15 + (6 || 6) to R_right = 18 ohm; KCL reference directions."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 720, 330, 80, 270
X6, X3, X9, XD, XR, X4 = 70, 200, 320, 440, 560, 660
s = header(W, H)
s += line(X6, YT, X4, YT) + line(X6, YB, X4, YB)
s += isrc(X6, YB, X6, YT, r=18)                                   # 6 A, arrow up into the top node
s += isrc(X4, YT, X4, YB, r=18)                                   # 4 A, arrow down out of the top node
for x in (X3, X9, XR):
    s += resistor(x, YT, x, YB, zigs=6, lead=50)
cx, cy, h = XD, (YT + YB) / 2, 22                                 # CCCS 0.9 i3, arrow up
s += line(XD, YT, XD, cy - h) + line(XD, cy + h, XD, YB)
s += f'<path d="M{cx - h} {cy} L{cx} {cy - h} L{cx + h} {cy} L{cx} {cy + h} Z"/>\n'
s += arrow(cx, cy + 11, cx, cy - 11)
for x in (X3, X9, XD, XR):
    s += dot(x, YT) + dot(x, YB)
s += line(X3, YB, X3, YB + 12) + ground(X3, YB + 12)
for x in (X3, X9, XR):
    s += tint_arrow(x + 16, 96, x + 16, 128)                      # resistor currents, reference downward
s += end_group()
s += text(X6 - 24, 181, [("n", "6 A")], anchor="end")
s += text(X4 + 26, 181, [("n", "4 A")])
s += ttext(X6 + 50, YT + 26, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(X6 + 50, 181, [("v", "v"), ("vsub", "x")], anchor="middle", color=BLUE)
s += ttext(X6 + 50, YB - 12, [("n", "−")], anchor="middle", color=BLUE)
s += text(X3 + 16, 186, [("n", "3 Ω")])
s += text(X9 + 16, 186, [("n", "9 Ω")])
s += text(XD + 28, 181, [("n", "0.9"), ("v", "i"), ("sub", "3")])
s += text(XR + 16, 176, [("v", "R"), ("sub", "right")])
s += text(XR + 16, 198, [("n", "= 18 Ω")])
s += ttext(X3 + 24, 117, [("v", "i"), ("sub", "3"), ("n", " = "), ("v", "v"), ("vsub", "x"), ("n", "/3")], color=RED)
s += ttext(X9 + 24, 117, [("v", "v"), ("vsub", "x"), ("n", "/9")], color=RED)
s += ttext(XR + 24, 117, [("v", "v"), ("vsub", "x"), ("n", "/18")], color=RED)
s += text(X6 - 40, 40, [("t", "上導線為唯一未知節點（電壓 "), ("v", "v"), ("vsub", "x"), ("t", "），下導線為參考節點")])
s += footer()
write('EE-113-01-1-node.svg', s)
