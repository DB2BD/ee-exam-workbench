"""EE-111-02-2: SEPIC equivalent circuits, switch on (0 < t < DT) and off (DT < t < T)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

Y_T, Y_B = 80, 230
XS, XA, XB, XC2, XR = 30, 122, 190, 262, 322


def panel(ox, on):
    s = ''
    s += dc_source(ox + XS, 155) + line(ox + XS, 139, ox + XS, Y_T) + line(ox + XS, 171, ox + XS, Y_B)
    s += coil(ox + XS, Y_T, ox + XA, Y_T, turns=4)
    s += line(ox + XA, Y_T, ox + XA, 125) + switch(ox + XA, 125, ox + XA, 185, closed=on) + line(ox + XA, 185, ox + XA, Y_B)
    s += cap(ox + XA, Y_T, ox + XB, Y_T, w=24)
    s += coil(ox + XB, Y_T, ox + XB, Y_B, turns=4)
    s += diode(ox + XB, Y_T, ox + XC2, Y_T, size=9)
    s += cap(ox + XC2, Y_T, ox + XC2, Y_B, w=24)
    s += line(ox + XC2, Y_T, ox + XR, Y_T) + resistor(ox + XR, Y_T, ox + XR, Y_B, zigs=8, lead=35)
    s += line(ox + XS, Y_B, ox + XR, Y_B)
    for x, y in ((XA, Y_T), (XB, Y_T), (XC2, Y_T), (XA, Y_B), (XB, Y_B), (XC2, Y_B)):
        s += dot(ox + x, y)
    s += red_arrow(ox + 56, 56, ox + 92, 56)                          # i_L1
    s += red_arrow(ox + XB + 16, 190, ox + XB + 16, 120)              # i_L2 upward
    if on:
        s += red_arrow(ox + XB - 14, 100, ox + XA + 14, 100)          # C1 current b -> a (= i_L2)
        s += red_arrow(ox + XR - 16, 120, ox + XR - 16, 168)          # C2 feeds the load
    else:
        s += red_arrow(ox + XA + 14, 100, ox + XB - 14, 100)          # C1 current a -> b (= i_L1)
        s += red_arrow(ox + XB + 22, 50, ox + XC2 - 22, 50)           # diode current
    s += end_group()
    t = []
    if on:
        t.append(text(ox + 6, 24, [("t", "(a) 開關導通："), ("n", "0 &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "DT")]))
    else:
        t.append(text(ox + 6, 24, [("t", "(b) 開關截止："), ("v", "DT"), ("n", " &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "T")]))
    t.append(text(ox + 6, 196, [("v", "V"), ("vsub", "in")]))
    t.append(text(ox + 76, 108, [("v", "L"), ("sub", "1")], anchor="middle"))
    t.append(ctext(ox + 96, 50, [("v", "i"), ("vsub", "L"), ("sub", "1")]))
    t.append(text(ox + XA - 6, 160, [("t", "導通" if on else "截止")], anchor="end"))
    t.append(text(ox + 156, 52, [("v", "C"), ("sub", "1")], anchor="middle"))
    t.append(text(ox + XA + 6, 76, [("n", "+")]))
    t.append(text(ox + XB - 6, 76, [("n", "−")], anchor="end"))
    t.append(text(ox + XB - 10, 166, [("v", "L"), ("sub", "2")], anchor="end"))
    t.append(ctext(ox + XB + 24, 150, [("v", "i"), ("vsub", "L"), ("sub", "2")]))
    t.append(text(ox + 226, 104, [("v", "D"), ("t", " 截止" if on else " 導通")], anchor="middle"))
    t.append(text(ox + XC2 - 16, 170, [("v", "C"), ("sub", "2")], anchor="end"))
    t.append(text(ox + XR + 10, 160, [("v", "R")]))
    if on:
        t.append(ctext(ox + 156, 118, [("v", "i"), ("vsub", "L"), ("sub", "2")], anchor="middle"))
        t.append(ctext(ox + XR - 22, 150, [("v", "I"), ("vsub", "o")], anchor="end"))
        t.append(text(ox + 6, 262, [("v", "v"), ("vsub", "L"), ("sub", "1"), ("n", " = "), ("v", "V"), ("vsub", "in"), ("t", "，"), ("v", "v"), ("vsub", "L"), ("sub", "2"), ("n", " = "), ("v", "V"), ("vsub", "C"), ("sub", "1"), ("n", " = "), ("v", "V"), ("vsub", "in")]))
        t.append(text(ox + 6, 286, [("v", "C"), ("sub", "1"), ("t", " 放出 "), ("v", "I"), ("vsub", "L"), ("sub", "2"), ("t", "，"), ("v", "C"), ("sub", "2"), ("t", " 放出 "), ("v", "I"), ("vsub", "o")]))
    else:
        t.append(ctext(ox + 156, 118, [("v", "i"), ("vsub", "L"), ("sub", "1")], anchor="middle"))
        t.append(ctext(ox + 226, 40, [("v", "i"), ("vsub", "L"), ("sub", "1"), ("n", " + "), ("v", "i"), ("vsub", "L"), ("sub", "2")], anchor="middle"))
        t.append(text(ox + 6, 262, [("v", "v"), ("vsub", "L"), ("sub", "1"), ("n", " = "), ("v", "v"), ("vsub", "L"), ("sub", "2"), ("n", " = −"), ("v", "V"), ("vsub", "o")]))
        t.append(text(ox + 6, 286, [("v", "C"), ("sub", "1"), ("t", " 吸收 "), ("v", "I"), ("vsub", "L"), ("sub", "1")]))
    return s, ''.join(t)


W, H = 720, 300
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(360, False)
s += a + G_OPEN + b + ta + tb + footer()
write('EE-111-02-2-on-off.svg', s)
