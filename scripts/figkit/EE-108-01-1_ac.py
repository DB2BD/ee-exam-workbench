"""EE-108-01-1: 5 rad/s phasor circuit (6 A source open), cosine-reference peak phasors."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 330
XS, XA = 70, 520
YT, YB = 110, 270
P1, P2 = 300, 430                                              # parallel L || C block
s = header(W, H)
s += line(XS, YT, XS, 176) + ac_source(XS, 190) + line(XS, 204, XS, YB)
s += line(XS, YT, 100, YT) + resistor(100, YT, 160, YT, lead=6) + line(160, YT, 180, YT)
s += coil(180, YT, 250, YT, turns=3) + line(250, YT, P1, YT)
s += line(P1, YT - 24, P1, YT + 24) + line(P2, YT - 24, P2, YT + 24)
s += line(P1, YT - 24, 330, YT - 24) + coil(330, YT - 24, 400, YT - 24, turns=3) + line(400, YT - 24, P2, YT - 24)
s += cap(P1, YT + 24, P2, YT + 24)
s += dot(P1, YT) + dot(P2, YT)
s += line(P2, YT, XA, YT) + resistor(XA, YT, XA, YB, lead=40) + line(XS, YB, XA, YB)
s += dot(XA, YT)
s += dashed(288, YT - 46, 442, YT - 46) + dashed(442, YT - 46, 442, YT + 52) + dashed(442, YT + 52, 288, YT + 52) + dashed(288, YT + 52, 288, YT - 46)
s += tint_arrow(105, YT - 14, 150, YT - 14)
s += end_group()
s += text(20, 28, [("t", "交流單獨作用（6 A 開路），"), ("v", "ω"), ("n", " = 5 rad/s"), ("t", "，峰值相量")])
s += ttext(XS - 20, 182, [("n", "+")], color=BLUE) + ttext(XS - 20, 210, [("n", "−")], color=BLUE)
s += ttext(XS + 24, 196, [("v", "V"), ("n", " = 12∠0° V")], color=BLUE)
s += ttext(128, YT - 26, [("v", "I"), ("sub", "ac")], anchor="middle", color=RED)
s += text(130, YT + 28, [("n", "1 Ω")], anchor="middle")
s += text(215, YT - 16, [("v", "Z"), ("vsub", "L"), ("n", " = "), ("v", "j"), ("n", "1 Ω")], anchor="middle")
s += text(365, YT - 56, [("v", "Z"), ("vsub", "L"), ("n", " = "), ("v", "j"), ("n", "1 Ω")], anchor="middle")
s += text(365, YT + 74, [("v", "Z"), ("vsub", "C"), ("n", " = −"), ("v", "j"), ("n", "2 Ω")], anchor="middle")
s += text(365, YT + 98, [("v", "Z"), ("vsub", "p"), ("n", " = "), ("v", "j"), ("n", "2 Ω"), ("t", "（虛線框）")], anchor="middle")
s += text(XA, YT - 12, [("v", "a")], anchor="middle")
s += text(XA + 14, 196, [("n", "2 Ω")])
s += text(XA + 60, 196, [("t", "（6 A 開路）")])
s += footer()
write('EE-108-01-1-ac.svg', s)
