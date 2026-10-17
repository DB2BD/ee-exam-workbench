import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from power_parts import switch
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 340; s = header(W, H); y, g, xa, xf, xb = 110, 260, 60, 430, 640
for x in (xa, xb):
    s += line(x, g, x, 199) + ac_source(x, 185) + line(x, 171, x, y)
s += line(xa, y, 90, y) + coil(90, y, 160, y) + line(160, y, 190, y) + coil(190, y, 260, y) + line(260, y, 290, y)
s += switch(290, y, 360, y, True) + line(360, y, xf, y)
s += line(xb, y, 610, y) + coil(610, y, 540, y) + line(540, y, 520, y) + switch(520, y, 450, y, True) + line(450, y, xf, y)
s += dot(xf, y) + f'<path d="M{xf} {y} L{xf} {g}" stroke="{RED}" stroke-dasharray="6 4"/>\n' + dot(xf, g)
s += line(xa, g, xb, g)
s += arrow(370, y + 16, 414, y + 16, RED) + arrow(500, y + 16, 446, y + 16, RED) + arrow(xf + 14, 150, xf + 14, 220, RED)
s += end_group()
s += text(125, 80, [("v", "jX"), ("vsub", "sys")], anchor="middle") + text(125, 140, [("v", "j"), ("n", "0.01")], anchor="middle")
s += text(225, 80, [("v", "jX"), ("vsub", "T")], anchor="middle") + text(225, 140, [("v", "j"), ("n", "0.06")], anchor="middle")
s += text(175, 50, [("v", "X"), ("sub", "1"), ("n", " = 0.07")], anchor="middle")
s += text(575, 80, [("v", "jX"), ("sub", "2"), ("n", " = "), ("v", "j"), ("n", "0.80")], anchor="middle")
s += text(325, 80, [("n", "CB1")], anchor="middle") + text(485, 80, [("n", "CB2")], anchor="middle")
s += text(xf, 40, [("n", "F"), ("t", "（480 V 匯流排）")], anchor="middle")
s += ctext(RED, 418, 150, [("v", "I"), ("sub", "1"), ("n", " = 34 366 A")], anchor="end")
s += ctext(RED, 446, 150, [("v", "I"), ("sub", "2"), ("n", " = 3007 A")], anchor="start")
s += ctext(RED, xf + 22, 192, [("v", "I"), ("vsub", "F"), ("sub", "2"), ("n", " = 37.37 kA")])
for x, nm, dx, an in ((xa, "系統＋主變", 20, "start"), (xb, "發電機 G", -24, "end")):
    s += text(x + dx, 190 if dx > 0 else 240, [("v", "E"), ("n", "″ = 1∠0°")], anchor=an) + text(x, 290, [("t", nm)], anchor="middle")
s += text(350, 322, [("t", "圖為（二）兩 CB 閉合；（一）CB2 開路，移除發電機支路。"), ("v", "S"), ("vsub", "b"), ("n", " = 2000 kVA"), ("t", "，"), ("v", "I"), ("vsub", "b"), ("n", " = 2405.63 A")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-105-06-3-reactance.svg'), 'w').write(s)
print(len(s))
