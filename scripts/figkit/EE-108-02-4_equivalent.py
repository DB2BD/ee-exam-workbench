"""EE-108-02-4: equivalent circuit at node X: V_i - R - X, C and L_eq = R^2 C / 2 from X to ground,
X drives the non-inverting stage (gain 1 + 4R_1/R_1 = 5) to V_o."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 640, 270
YT, YB = 70, 210
XV, XX, XC, XL = 60, 230, 290, 380
s = header(W, H)
s += vsrc(XV, YT, XV, YB) + resistor(XV, YT, XX, YT, zigs=6, lead=50) + line(XX, YT, XL, YT)
s += cap(XC, YT, XC, YB) + coil(XL, YT, XL, YB, turns=4) + line(XV, YB, XL, YB)
s += dot(XX, YT) + dot(XC, YT) + dot(XC, YB) + ground(220, YB)
s += line(XL, YT, 440, YT)
s += '<path d="M440 40 L440 100 L520 70 Z"/>\n' + line(520, YT, 556.5, YT) + terminal(560, YT)
s += end_group()
t = []
t.append(text(XV - 22, (YT + YB) / 2 + 5, [("v", "V"), ("vsub", "i")], anchor="end"))
t.append(text((XV + XX) / 2, YT - 16, [("v", "R")], anchor="middle"))
t.append(text(XX, YT - 16, [("v", "X")], anchor="middle"))
t.append(text(XC - 20, (YT + YB) / 2 + 5, [("v", "C")], anchor="end"))
t.append(text(XL + 14, (YT + YB) / 2 - 4, [("v", "L"), ("vsub", "eq")]))
t.append(text(XL + 14, (YT + YB) / 2 + 20, [("n", "= "), ("v", "R"), ("n", "²"), ("v", "C"), ("n", "/2")]))
t.append(text(470, 76, [("n", "×5")], anchor="middle"))
t.append(text(560, YT - 14, [("v", "V"), ("vsub", "o")], anchor="middle"))
t.append(text(430, 128, [("t", "非反相級 "), ("n", "1 + 4"), ("v", "R"), ("sub", "1"), ("n", "/"), ("v", "R"), ("sub", "1"), ("n", " = 5")]))
t.append(text(10, 254, [("t", "GIC 由 "), ("v", "X"), ("t", " 看入等於接地電感 "), ("v", "L"), ("vsub", "eq"), ("t", "，與實體電容 "), ("v", "C"), ("t", " 並聯")]))
s += ''.join(t) + footer()
write('EE-108-02-4-equivalent.svg', s)
