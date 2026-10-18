"""EE-106-02-1: input networks of A1: + node M fed by v_in through R_4 and by v_X through R_5;
- node N fed by v_out through R_6 and by v_Y through R_3.  Ideal op amp: no input current, v_M = v_N."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 640, 300
Y1, Y2, YP, YN = 80, 240, 130, 190
XA, XM, XB = 40, 200, 360
s = header(W, H)
for y in (Y1, Y2):
    s += terminal(XA, y) + line(XA + 3.5, y, 60, y) + resistor(60, y, 160, y, zigs=6, lead=14) + line(160, y, 240, y)
    s += resistor(240, y, 340, y, zigs=6, lead=14) + line(340, y, XB - 3.5, y) + terminal(XB, y) + dot(XM, y)
s += line(XM, Y1, XM, YP) + line(XM, YP, 470, YP) + line(XM, Y2, XM, YN) + line(XM, YN, 470, YN)
s += '<path d="M470 110 L470 210 L570 160 Z"/>\n' + line(570, 160, 610, 160) + terminal(613.5, 160)
s += line(478, YP, 488, YP) + line(483, YP - 5, 483, YP + 5) + line(478, YN, 488, YN)
s += end_group()
t = []
t.append(text(10, 24, [("v", "A"), ("sub", "1"), ("t", " 兩個輸入節點：輸入不取電流，各為兩電阻的加權分壓；虛短 "), ("v", "v"), ("vsub", "M"), ("n", " = "), ("v", "v"), ("vsub", "N")]))
t.append(text(XA, Y1 - 12, [("v", "v"), ("vsub", "in")], anchor="middle"))
t.append(text(110, Y1 - 14, [("v", "R"), ("sub", "4")], anchor="middle"))
t.append(text(290, Y1 - 14, [("v", "R"), ("sub", "5")], anchor="middle"))
t.append(text(XB, Y1 - 12, [("v", "v"), ("vsub", "X")], anchor="middle"))
t.append(ctext(XM + 8, Y1 + 22, [("v", "M")], color=BLUE))
t.append(text(XA, Y2 + 26, [("v", "v"), ("vsub", "out")], anchor="middle"))
t.append(text(110, Y2 + 26, [("v", "R"), ("sub", "6")], anchor="middle"))
t.append(text(290, Y2 + 26, [("v", "R"), ("sub", "3")], anchor="middle"))
t.append(text(XB, Y2 + 26, [("v", "v"), ("vsub", "Y")], anchor="middle"))
t.append(ctext(XM + 8, Y2 - 12, [("v", "N")], color=BLUE))
t.append(text(500, 165, [("v", "A"), ("sub", "1")]))
t.append(text(613, 145, [("v", "v"), ("vsub", "out")], anchor="middle"))
t.append(text(380, YP - 8, [("v", "v"), ("vsub", "M")], anchor="middle"))
t.append(text(380, YN + 20, [("v", "v"), ("vsub", "N")], anchor="middle"))
s += ''.join(t) + footer()
write('EE-106-02-1-summing.svg', s)
