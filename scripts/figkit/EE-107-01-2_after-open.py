"""EE-107-01-2: t >= 0 circuit (switch open): i1, i2 referenced downward, v(t) + on top, i_4ohm and i3 in the resistor network."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 720, 320
X1, X2, XSW, XV, X40, X15, X10 = 130, 250, 340, 392, 440, 580, 660
YT, YB = 80, 250
s = header(W, H)
s += line(X1, YT, 470, YT) + resistor(470, YT, 550, YT) + line(550, YT, X10, YT)
s += line(X1, YB, X10, YB)
s += coil(X1, YT, X1, YB, turns=5) + coil(X2, YT, X2, YB, turns=5)
s += line(XSW, YT, XSW, 120) + switch(XSW, 120, XSW, 210, closed=False) + line(XSW, 210, XSW, YB)
s += resistor(X40, YT, X40, YB, lead=50) + resistor(X15, YT, X15, YB, lead=50) + resistor(X10, YT, X10, YB, lead=50)
for x in (X2, XSW, X40, X15):
    s += dot(x, YT) + dot(x, YB)
s += tint_arrow(X1 + 20, 130, X1 + 20, 176) + tint_arrow(X2 + 20, 130, X2 + 20, 176)
s += tint_arrow(490, YT + 18, 530, YT + 18)
s += tint_arrow(X10 - 20, 130, X10 - 20, 176)
s += end_group()
s += text(20, 30, [("v", "t"), ("n", " ≥ 0 "), ("t", "開關打開：兩電感接到電阻網路；電感電流參考方向向下")])
s += text(X1 - 18, 160, [("v", "L"), ("sub", "1")], anchor="end") + text(X1 - 18, 182, [("n", "5 H")], anchor="end")
s += text(X2 - 18, 160, [("v", "L"), ("sub", "2")], anchor="end") + text(X2 - 18, 182, [("n", "20 H")], anchor="end")
s += ttext(X1 + 30, 158, [("v", "i"), ("sub", "1")], color=RED) + ttext(X2 + 30, 158, [("v", "i"), ("sub", "2")], color=RED)
s += ttext(X1, YB + 28, [("v", "i"), ("sub", "1"), ("n", "(0) = −8 A")], anchor="middle", color=RED)
s += ttext(X2, YB + 28, [("v", "i"), ("sub", "2"), ("n", "(0) = −4 A")], anchor="middle", color=RED)
s += text(XSW - 12, 176, [("v", "t"), ("n", " = 0")], anchor="end")
s += ttext(XV + 10, YT + 30, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XV + 10, 230, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XV + 10, 140, [("v", "v"), ("n", "("), ("v", "t"), ("n", ")")], anchor="middle", color=BLUE)
s += text(X40 + 16, 170, [("n", "40 Ω")])
s += text(510, YT - 16, [("n", "4 Ω")], anchor="middle")
s += ttext(510, YT + 44, [("v", "i"), ("sub", "4Ω")], anchor="middle", color=RED)
s += text(X15 - 16, 170, [("n", "15 Ω")], anchor="end")
s += text(X10 + 16, 170, [("n", "10 Ω")])
s += ttext(X10 - 28, 158, [("v", "i"), ("sub", "3")], anchor="end", color=RED)
s += footer()
write('EE-107-01-2-after-open.svg', s)
