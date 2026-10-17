"""EE-107-02-4: Cuk converter, the two switch states (Q on: C1 discharges through i_L2; Q off: C1 charges with i_L1)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

YT, YB = 66, 176           # top / bottom rail (panel-local)
XS, XA, XB, XO, XR = 40, 200, 320, 470, 560


def panel(oy, on):
    def Y(y):
        return oy + y
    s = ''
    s += dc_source(XS, Y(121)) + line(XS, Y(105), XS, Y(YT)) + line(XS, Y(137), XS, Y(YB))
    s += coil(XS, Y(YT), XA, Y(YT), turns=4)                                   # L1
    s += line(XA, Y(YT), XA, Y(91)) + switch(XA, Y(91), XA, Y(151), closed=on) + line(XA, Y(151), XA, Y(YB))   # Q
    s += cap(XA, Y(YT), XB, Y(YT))                                              # C1 (+ left, - right)
    s += diode(XB, Y(YT), XB, Y(YB))                                            # D_m: anode B (top), cathode ground
    s += coil(XB, Y(YT), XO, Y(YT), turns=4)                                    # L2
    s += cap(XO, Y(YT), XO, Y(YB))                                              # C2
    s += line(XO, Y(YT), XR, Y(YT)) + resistor(XR, Y(YT), XR, Y(YB), zigs=6, lead=24)
    s += line(XS, Y(YB), XR, Y(YB))
    for x in (XA, XB, XO):
        s += dot(x, Y(YT)) + dot(x, Y(YB))
    s += red_arrow(95, Y(40), 135, Y(40))                                       # i_L1 rightward
    s += red_arrow(415, Y(40), 375, Y(40))                                      # i_L2 leftward
    if on:
        s += red_arrow(280, Y(47), 240, Y(47))                                  # through C1: i_L2 leftward (discharge)
        s += red_arrow(182, Y(100), 182, Y(140))                                # Q carries i_L1 + i_L2
    else:
        s += red_arrow(240, Y(47), 280, Y(47))                                  # through C1: i_L1 rightward (charge)
        s += red_arrow(298, Y(100), 298, Y(140))                                # D carries i_L1 + i_L2
    s += end_group()
    t = []
    if on:
        t.append(text(8, Y(20), [("t", "(a) "), ("v", "Q"), ("t", " 導通："), ("n", "0 &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "DT"), ("n", " = 10 μs")]))
    else:
        t.append(text(8, Y(20), [("t", "(b) "), ("v", "Q"), ("t", " 截止："), ("v", "DT"), ("n", " &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "T"), ("n", " = 50 μs")]))
    t.append(text(XS - 22, Y(126), [("v", "V"), ("sub", "s")], anchor="end"))
    t.append(text(120, Y(92), [("v", "L"), ("sub", "1")], anchor="middle"))
    t.append(ctext(140, Y(36), [("v", "i"), ("vsub", "L"), ("sub", "1")]))
    t.append(text(XA + 12, Y(126), [("v", "Q")]))
    t.append(text(XA + 22, Y(58), [("n", "+")]))
    t.append(text(XB - 22, Y(58), [("n", "−")], anchor="end"))
    t.append(text((XA + XB) / 2, Y(98), [("v", "C"), ("sub", "1")], anchor="middle"))
    t.append(text(XB + 16, Y(126), [("v", "D"), ("vsub", "m"), ("t", " 截止" if on else " 導通")]))
    t.append(text(395, Y(92), [("v", "L"), ("sub", "2")], anchor="middle"))
    t.append(ctext(370, Y(36), [("v", "i"), ("vsub", "L"), ("sub", "2")], anchor="end"))
    t.append(text(XO - 20, Y(126), [("v", "C"), ("sub", "2")], anchor="end"))
    t.append(text(XR + 14, Y(126), [("t", "負載")]))
    if on:
        t.append(ctext(260, Y(28), [("v", "i"), ("vsub", "C"), ("sub", "1"), ("n", " = −"), ("v", "i"), ("vsub", "L"), ("sub", "2")], anchor="middle"))
        t.append(ctext(176, Y(126), [("v", "i"), ("vsub", "L"), ("sub", "1"), ("n", "+"), ("v", "i"), ("vsub", "L"), ("sub", "2")], anchor="end"))
        t.append(text(8, Y(210), [("v", "v"), ("vsub", "L"), ("sub", "1"), ("n", " = "), ("v", "V"), ("sub", "s"), ("n", " = 10 V"), ("t", "，"),
                                  ("v", "v"), ("vsub", "L"), ("sub", "2"), ("n", " = "), ("v", "V"), ("vsub", "C"), ("sub", "1"), ("n", " − "), ("v", "V"), ("vsub", "o"), ("n", " = 10 V"), ("t", "：兩電感電流皆上升")]))
        t.append(text(8, Y(234), [("v", "C"), ("sub", "1"), ("t", " 由 "), ("v", "i"), ("vsub", "L"), ("sub", "2"), ("t", " 放電，"), ("v", "Q"), ("t", " 承載 "), ("v", "i"), ("vsub", "L"), ("sub", "1"), ("n", " + "), ("v", "i"), ("vsub", "L"), ("sub", "2")]))
    else:
        t.append(ctext(260, Y(28), [("v", "i"), ("vsub", "C"), ("sub", "1"), ("n", " = "), ("v", "i"), ("vsub", "L"), ("sub", "1")], anchor="middle"))
        t.append(ctext(292, Y(126), [("v", "i"), ("vsub", "L"), ("sub", "1"), ("n", "+"), ("v", "i"), ("vsub", "L"), ("sub", "2")], anchor="end"))
        t.append(text(8, Y(210), [("v", "v"), ("vsub", "L"), ("sub", "1"), ("n", " = "), ("v", "V"), ("sub", "s"), ("n", " − "), ("v", "V"), ("vsub", "C"), ("sub", "1"), ("n", " = −2.50 V"), ("t", "，"),
                                  ("v", "v"), ("vsub", "L"), ("sub", "2"), ("n", " = −"), ("v", "V"), ("vsub", "o"), ("n", " = −2.50 V"), ("t", "：兩電感電流皆下降")]))
        t.append(text(8, Y(234), [("v", "C"), ("sub", "1"), ("t", " 由 "), ("v", "i"), ("vsub", "L"), ("sub", "1"), ("t", " 充電，"), ("v", "D"), ("vsub", "m"), ("t", " 承載 "), ("v", "i"), ("vsub", "L"), ("sub", "1"), ("n", " + "), ("v", "i"), ("vsub", "L"), ("sub", "2")]))
    return s, ''.join(t)


W, H = 720, 500
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(252, False)
s += a + G_OPEN + b + ta + tb + footer()
write('EE-107-02-4-on-off.svg', s)
