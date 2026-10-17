"""EE-106-02-5: non-inverting buck-boost, (a) Q1, Q2 on: v_L = V_in; (b) Q1, Q2 off: i_L freewheels through D1, D2, v_L = -V_o."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

YT, YB = 66, 176
XS, XA, XB, XO, XR = 64, 180, 330, 460, 560


def panel(oy, on):
    def Y(y):
        return oy + y
    s = ''
    s += dc_source(XS, Y(121)) + line(XS, Y(105), XS, Y(YT)) + line(XS, Y(137), XS, Y(YB))
    s += switch(XS, Y(YT), XA, Y(YT), closed=on)                               # Q1
    s += diode(XA, Y(YB), XA, Y(YT))                                            # D1: anode ground, cathode node a
    s += coil(XA, Y(YT), XB, Y(YT), turns=4)                                    # L
    s += line(XB, Y(YT), XB, Y(91)) + switch(XB, Y(91), XB, Y(151), closed=on) + line(XB, Y(151), XB, Y(YB))   # Q2
    s += diode(XB, Y(YT), XO, Y(YT))                                            # D2: anode node b, cathode output
    s += cap(XO, Y(YT), XO, Y(YB))
    s += line(XO, Y(YT), XR, Y(YT)) + resistor(XR, Y(YT), XR, Y(YB), zigs=6, lead=24)
    s += line(XS, Y(YB), XR, Y(YB))
    for x in (XA, XB, XO):
        s += dot(x, Y(YT)) + dot(x, Y(YB))
    s += red_arrow(235, Y(44), 275, Y(44))                                      # i_L
    if on:
        s += red_arrow(102, Y(44), 142, Y(44))                                   # through Q1
        s += red_arrow(348, Y(100), 348, Y(140))                                # through Q2
    else:
        s += red_arrow(162, Y(150), 162, Y(110))                                # up through D1
        s += red_arrow(375, Y(44), 415, Y(44))                                  # through D2
    s += end_group()
    t = []
    if on:
        t.append(text(8, Y(20), [("t", "(a) "), ("v", "Q"), ("sub", "1"), ("t", "、"), ("v", "Q"), ("sub", "2"), ("t", " 導通："), ("n", "0 &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "DT"), ("vsub", "s")]))
    else:
        t.append(text(8, Y(20), [("t", "(b) "), ("v", "Q"), ("sub", "1"), ("t", "、"), ("v", "Q"), ("sub", "2"), ("t", " 截止："), ("v", "DT"), ("vsub", "s"), ("n", " &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "T"), ("vsub", "s")]))
    t.append(text(XS - 22, Y(126), [("v", "V"), ("vsub", "in")], anchor="end"))
    t.append(text(122, Y(96 if on else 104), [("v", "Q"), ("sub", "1")], anchor="middle"))
    t.append(text(XA + 16, Y(126), [("v", "D"), ("sub", "1")]))
    t.append(text(255, Y(96), [("v", "L")], anchor="middle"))
    t.append(text(XA + 16, Y(58), [("n", "+")]))
    t.append(text(XB - 16, Y(58), [("n", "−")], anchor="end"))
    t.append(ctext(280, Y(40), [("v", "i"), ("vsub", "L")]))
    t.append(text(XB - 12, Y(126), [("v", "Q"), ("sub", "2")], anchor="end"))
    t.append(text((XB + XO) / 2, Y(96), [("v", "D"), ("sub", "2")], anchor="middle"))
    t.append(text(XO - 20, Y(126), [("v", "C")], anchor="end"))
    t.append(text(XR + 14, Y(126), [("v", "R")]))
    t.append(text(XR + 30, Y(84), [("n", "+")]))
    t.append(text(XR + 30, Y(172), [("n", "−")]))
    t.append(text(XR + 46, Y(130), [("v", "V"), ("vsub", "o")]))
    if on:
        t.append(text(8, Y(210), [("v", "v"), ("vsub", "L"), ("n", " = "), ("v", "V"), ("vsub", "in"), ("t", "；"), ("v", "D"), ("sub", "1"), ("t", "（陰極接 "), ("v", "V"), ("vsub", "in"), ("t", "）、"), ("v", "D"), ("sub", "2"), ("t", "（陽極接地）皆逆偏截止")]))
        t.append(text(8, Y(234), [("v", "Q"), ("sub", "1"), ("t", " 電流 = "), ("v", "i"), ("vsub", "L"), ("t", "（上升），"), ("v", "C"), ("t", " 單獨供給負載")]))
    else:
        t.append(text(8, Y(210), [("v", "i"), ("vsub", "L"), ("t", " 不能突變，迫使 "), ("v", "D"), ("sub", "1"), ("t", "、"), ("v", "D"), ("sub", "2"), ("t", " 導通："), ("v", "v"), ("vsub", "L"), ("n", " = 0 − "), ("v", "V"), ("vsub", "o"), ("n", " = −"), ("v", "V"), ("vsub", "o")]))
        t.append(text(8, Y(234), [("v", "Q"), ("sub", "1"), ("t", " 電流 = 0；"), ("v", "i"), ("vsub", "L"), ("t", "（下降）全部經 "), ("v", "D"), ("sub", "2"), ("t", " 送往輸出")]))
    return s, ''.join(t)


W, H = 720, 500
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(252, False)
s += a + G_OPEN + b + ta + tb + footer()
write('EE-106-02-5-on-off.svg', s)
