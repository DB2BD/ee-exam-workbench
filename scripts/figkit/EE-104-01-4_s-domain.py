"""EE-104-01-4: s-domain circuit (zero initial state): Ig = 0.02/s, 50 + 10^4/s branch (V_phi on C), dependent source, sL."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 680, 340
XG, XRC, XD, XL = 110, 270, 430, 580
YT, YB = 80, 280
s = header(W, H)
s += line(XG, YT, XL, YT) + line(XG, YB, XL, YB)
s += isrc(XG, YB, XG, YT, r=18)                                       # ig, arrow up into top node
s += resistor(XRC, YT, XRC, 160, lead=14) + line(XRC, 160, XRC, 195) + cap(XRC, 195, XRC, 245) + line(XRC, 245, XRC, YB)
cx, cy, h = XD, 180, 22                                               # dependent current source, arrow down
s += line(XD, YT, XD, cy - h) + line(XD, cy + h, XD, YB)
s += f'<path d="M{cx - h} {cy} L{cx} {cy - h} L{cx + h} {cy} L{cx} {cy + h} Z"/>\n'
s += arrow(cx, cy - 11, cx, cy + 11)
s += line(XL, YT, XL, 130) + coil(XL, 130, XL, 230) + line(XL, 230, XL, YB)
for x in (XRC, XD):
    s += dot(x, YT) + dot(x, YB)
s += line(XRC, YB, XRC, YB + 12) + ground(XRC, YB + 12)
s += end_group()
s += text(20, 30, [("v", "s"), ("t", " 域（零初值，無初值源）；下方導線為參考地")])
s += text(XG - 26, 176, [("v", "I"), ("vsub", "g"), ("n", " = 0.02/"), ("v", "s")], anchor="end")
s += text(XRC + 16, 126, [("n", "50 Ω")])
s += text(XRC + 22, 214, [("n", "1/("), ("v", "sC"), ("n", ")")])
s += text(XRC + 22, 236, [("n", "= 10000/"), ("v", "s")])
s += ttext(XRC - 20, 206, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XRC - 20, 226, [("v", "V"), ("vsub", "ϕ")], anchor="end", color=BLUE)
s += ttext(XRC - 20, 248, [("n", "−")], anchor="middle", color=BLUE)
s += text(XD + 28, 176, [("n", "0.015"), ("v", "V"), ("vsub", "ϕ")])
s += text(XL + 18, 176, [("v", "sL"), ("n", " = "), ("v", "s")])
s += ttext(XD - 40, YT + 24, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XD - 40, 186, [("v", "V"), ("vsub", "o")], anchor="middle", color=BLUE)
s += ttext(XD - 40, YB - 12, [("n", "−")], anchor="middle", color=BLUE)
s += footer()
write('EE-104-01-4-s-domain.svg', s)
