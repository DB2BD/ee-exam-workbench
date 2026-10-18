"""EE-111-01-4: two-port with node voltages V_a, V_b (bottom rail = reference), CCCS 4 I1 injecting into b, I1 and I2 entering."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 660, 320
XP1, XA, XB, XP2 = 60, 230, 410, 580
YT, YB = 90, 260
s = header(W, H)
s += terminal(XP1, YT) + terminal(XP1, YB) + terminal(XP2, YT) + terminal(XP2, YB)
s += line(XP1 + 4, YT, 110, YT) + resistor(110, YT, 190, YT) + line(190, YT, XA, YT)
s += line(XA, YT, 280, YT) + resistor(280, YT, 360, YT) + line(360, YT, XB, YT)
s += line(XB, YT, 460, YT) + resistor(460, YT, 540, YT) + line(540, YT, XP2 - 4, YT)
s += resistor(XA, YT, XA, YB, zigs=6, lead=45)
s += line(XP1 + 4, YB, XP2 - 4, YB)
# dependent current source (diamond) from the bottom rail up into node b
h, cy = 20, (YT + YB) / 2
s += line(XB, YT, XB, cy - h) + line(XB, cy + h, XB, YB)
s += f'<path d="M{XB - h} {cy} L{XB} {cy - h} L{XB + h} {cy} L{XB} {cy + h} Z"/>\n'
s += arrow(XB, cy + 11, XB, cy - 11)
for x in (XA, XB):
    s += dot(x, YT) + dot(x, YB)
s += tint_arrow(68, YT - 16, 100, YT - 16)                  # I1 into port 1
s += tint_arrow(572, YT - 16, 540, YT - 16)                 # I2 into port 2
s += end_group()
s += text(150, YT - 16, [("n", "1 Ω")], anchor="middle")
s += text(320, YT - 16, [("n", "2 Ω")], anchor="middle")
s += text(500, YT + 30, [("n", "1 Ω")], anchor="middle")
s += text(XA - 14, 182, [("n", "2 Ω")], anchor="end")
s += ttext(XB + 26, 182, [("n", "4"), ("v", "I"), ("sub", "1")], color=RED)
s += ttext(84, YT - 24, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(556, YT - 24, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += text(XA, YT - 12, [("v", "a")], anchor="middle")
s += text(XB, YT - 12, [("v", "b")], anchor="middle")
s += ttext(XA + 14, YT + 26, [("v", "V"), ("vsub", "a")], color=BLUE)
s += ttext(XB - 14, YT + 26, [("v", "V"), ("vsub", "b")], anchor="end", color=BLUE)
for x, lab in ((XP1 + 14, "1"), (XP2 - 14, "2")):
    a = "start" if x < 300 else "end"
    s += ttext(x, YT + 34, [("n", "+")], anchor=a, color=BLUE)
    s += ttext(x, 182, [("v", "V"), ("sub", lab)], anchor=a, color=BLUE)
    s += ttext(x, YB - 16, [("n", "−")], anchor=a, color=BLUE)
s += text(320, YB + 30, [("t", "下方導線為參考節點（0 V）")], anchor="middle")
s += footer()
write('EE-111-01-4-nodes.svg', s)
