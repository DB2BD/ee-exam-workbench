"""EE-104-02-5: loop broken at the op-amp output: V_o drives the C-R ladder; the last R ends on the
inverting input (virtual ground, 0 V).  Reference currents I_3, I_2, I_1 flow left -> right through
the three capacitors (as in the official figure); node voltages V_3, V_2, V_1 to ground."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 720, 290
YT, YG = 100, 210
XS, N3, N2, N1, XN = 40, 170, 300, 430, 540
s = header(W, H)
s += vsrc(XS, YT, XS, YG) + line(XS, YG, XS, YG + 6) + ground(XS, YG + 6)
s += cap(XS, YT, N3, YT) + cap(N3, YT, N2, YT) + cap(N2, YT, N1, YT)
s += resistor(N1, YT, XN, YT, zigs=6, lead=20)
for x in (N3, N2):
    s += resistor(x, YT, x, YG, zigs=6, lead=24) + line(x, YG, x, YG + 6) + ground(x, YG + 6) + dot(x, YT)
s += dot(N1, YT) + dot(XN, YT) + line(XN, YT, XN, YG) + line(XN, YG, XN, YG + 6) + ground(XN, YG + 6)
for xa in (XS + 22, N3 + 22, N2 + 22):
    s += red_arrow(xa, YT - 18, xa + 30, YT - 18)
s += end_group()
t = []
t.append(text(10, 26, [("t", "迴路在運算放大器輸出端斷開：以 "), ("v", "V"), ("vsub", "o"), ("t", " 驅動 RC 網路，求 "), ("v", "β"), ("n", " = "), ("v", "V"), ("sub", "1"), ("n", "/"), ("v", "V"), ("vsub", "o")]))
t.append(ctext(XS - 22, (YT + YG) / 2 + 5, [("v", "V"), ("vsub", "o")], anchor="end", color=BLUE))
for x, lab in ((XS + 37, "3"), (N3 + 37, "2"), (N2 + 37, "1")):
    t.append(ctext(x, YT - 26, [("v", "I"), ("sub", lab)], anchor="middle"))
for x, lab in ((N3, "3"), (N2, "2"), (N1, "1")):
    t.append(ctext(x - 2, YT - 10, [("v", "V"), ("sub", lab)], anchor="middle", color=BLUE))
for xc in ((XS + N3) / 2, (N3 + N2) / 2, (N2 + N1) / 2):
    t.append(text(xc, YT + 34, [("v", "C")], anchor="middle"))
for x in (N3, N2):
    t.append(text(x + 14, (YT + YG) / 2 + 12, [("v", "R")]))
t.append(text((N1 + XN) / 2, YT - 16, [("v", "R")], anchor="middle"))
t.append(text(XN + 10, YT + 5, [("t", "反相端")]))
t.append(text(XN + 10, YT + 27, [("t", "虛接地 0 V")]))
t.append(text(10, 272, [("t", "反相級："), ("v", "V"), ("vsub", "o"), ("n", "′ = −("), ("v", "R"), ("vsub", "f"), ("n", "/"), ("v", "R"), ("n", ")"), ("v", "V"), ("sub", "1"), ("t", "　　迴路增益 "), ("v", "L"), ("n", " = "), ("v", "V"), ("vsub", "o"), ("n", "′/"), ("v", "V"), ("vsub", "o"), ("n", " = "), ("v", "Aβ")]))
s += ''.join(t) + footer()
write('EE-104-02-5-ladder.svg', s)
