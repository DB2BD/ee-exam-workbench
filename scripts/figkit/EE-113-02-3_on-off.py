"""EE-113-02-3: Buck converter, equivalent circuits of the two operating states (BCM)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

Y_T, Y_B = 70, 230


def panel(ox, on):
    s = ''
    s += dc_source(ox + 40, 150) + line(ox + 40, 134, ox + 40, Y_T) + line(ox + 40, 166, ox + 40, Y_B)
    s += switch(ox + 40, Y_T, ox + 130, Y_T, closed=on)
    s += diode(ox + 130, Y_B, ox + 130, Y_T)                    # D1: anode at ground, cathode at node x
    s += coil(ox + 130, Y_T, ox + 240, Y_T, turns=4)
    s += cap(ox + 240, Y_T, ox + 240, Y_B)
    s += line(ox + 240, Y_T, ox + 315, Y_T) + resistor(ox + 315, Y_T, ox + 315, Y_B, zigs=8, lead=40)
    s += line(ox + 40, Y_B, ox + 315, Y_B)
    for x, y in ((130, Y_T), (240, Y_T), (130, Y_B), (240, Y_B)):
        s += dot(ox + x, y)
    s += red_arrow(ox + 166, 46, ox + 206, 46)                  # i_L
    if not on:
        s += red_arrow(ox + 108, 186, ox + 108, 120)            # freewheel current up through D1
    s += end_group()
    t = []
    if on:
        t.append(text(ox + 6, 24, [("t", "(a) "), ("v", "S"), ("t", " 導通："), ("n", "0 ≤ "), ("v", "t"), ("n", " &lt; "), ("v", "DT"), ("vsub", "s")]))
    else:
        t.append(text(ox + 6, 24, [("t", "(b) "), ("v", "S"), ("t", " 截止："), ("v", "DT"), ("vsub", "s"), ("n", " ≤ "), ("v", "t"), ("n", " &lt; "), ("v", "T"), ("vsub", "s")]))
    t.append(text(ox + 18, 155, [("v", "V"), ("vsub", "s")], anchor="end"))
    t.append(text(ox + 85, 58 if on else 44, [("v", "S")], anchor="middle"))
    t.append(text(ox + 144, 156, [("v", "D"), ("sub", "1")]))
    t.append(text(ox + 144, 176, [("t", "截止" if on else "導通")]))
    t.append(ctext(ox + 212, 42, [("v", "i"), ("vsub", "L")]))
    t.append(text(ox + 185, 96, [("v", "L")], anchor="middle"))
    t.append(text(ox + 146, 92, [("n", "+")]))
    t.append(text(ox + 226, 92, [("n", "−")], anchor="end"))
    t.append(text(ox + 222, 160, [("v", "C")], anchor="end"))
    t.append(text(ox + 302, 156, [("v", "R")], anchor="end"))
    t.append(text(ox + 326, 92, [("n", "+")]))
    t.append(text(ox + 326, 222, [("n", "−")]))
    t.append(text(ox + 328, 160, [("v", "V"), ("vsub", "o")]))
    if on:
        t.append(text(ox + 6, 262, [("v", "v"), ("vsub", "L"), ("n", " = "), ("v", "V"), ("vsub", "s"), ("n", " − "), ("v", "V"), ("vsub", "o"), ("t", "，"), ("v", "i"), ("vsub", "L"), ("t", " 由 0 上升")]))
        t.append(text(ox + 6, 286, [("v", "D"), ("sub", "1"), ("t", " 陰極接 "), ("v", "V"), ("vsub", "s"), ("t", "，逆偏")]))
    else:
        t.append(ctext(ox + 100, 156, [("v", "i"), ("vsub", "L")], anchor="end"))
        t.append(text(ox + 6, 262, [("v", "v"), ("vsub", "L"), ("n", " = −"), ("v", "V"), ("vsub", "o"), ("t", "，"), ("v", "i"), ("vsub", "L"), ("t", " 降回 0")]))
        t.append(text(ox + 6, 286, [("v", "i"), ("vsub", "L"), ("t", " 經 "), ("v", "D"), ("sub", "1"), ("t", " 續流")]))
    return s, ''.join(t)


W, H = 720, 300
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(360, False)
s += a + G_OPEN + b + ta + tb + footer()
write('EE-113-02-3-on-off.svg', s)
