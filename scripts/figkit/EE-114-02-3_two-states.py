"""EE-114-02-3: equivalent circuits of the two switch states (Q open -> D clamps v_a = V_S; Q shorted -> v_a = 0)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

Y_T, Y_B = 70, 230


def panel(ox, q_open):
    s = ''
    # V_S source on the left (+ on top)
    s += dc_source(ox + 40, 150) + line(ox + 40, 134, ox + 40, Y_T) + line(ox + 40, 166, ox + 40, Y_B)
    # diode: anode at node a (x=150), cathode at V_S+ (left)
    s += line(ox + 40, Y_T, ox + 70, Y_T) + diode(ox + 150, Y_T, ox + 70, Y_T)
    # Q between node a and the bottom rail
    s += line(ox + 150, Y_T, ox + 150, 120) + switch(ox + 150, 120, ox + 150, 180, closed=not q_open) + line(ox + 150, 180, ox + 150, Y_B)
    # L horizontal, then R and E down the right side
    s += coil(ox + 150, Y_T, ox + 260, Y_T, turns=4)
    s += line(ox + 260, Y_T, ox + 310, Y_T) + resistor(ox + 310, Y_T, ox + 310, 140, zigs=6, lead=12)
    s += dc_source(ox + 310, 170, r=15) + line(ox + 310, 185, ox + 310, Y_B)
    s += line(ox + 40, Y_B, ox + 310, Y_B)
    s += dot(ox + 150, Y_T) + dot(ox + 150, Y_B)
    s += red_arrow(ox + 186, 48, ox + 226, 48)            # i_L reference direction
    s += end_group()
    t = []
    if q_open:
        t.append(text(ox + 6, 24, [("t", "(a) "), ("v", "Q"), ("t", " 開路："), ("n", "0 ≤ "), ("v", "t"), ("n", " &lt; 0.5 ms")]))
    else:
        t.append(text(ox + 6, 24, [("t", "(b) "), ("v", "Q"), ("t", " 短路："), ("n", "0.5 ≤ "), ("v", "t"), ("n", " &lt; 1 ms")]))
    t.append(text(ox + 18, 155, [("v", "V"), ("sub", "S")], anchor="end"))
    t.append(text(ox + 108, 52, [("v", "D"), ("t", " 導通" if q_open else " 截止")], anchor="middle"))
    t.append(text(ox + 128, 156, [("v", "Q")], anchor="end"))
    t.append(text(ox + 160, 104, [("n", "+")]))
    t.append(text(ox + 160, 214, [("n", "−")]))
    t.append(text(ox + 186 if q_open else ox + 162, 156 if q_open else 132, [("v", "v"), ("vsub", "a")]))
    t.append(ctext(ox + 232, 44, [("v", "i"), ("vsub", "L")]))
    t.append(text(ox + 205, 96, [("v", "L")], anchor="middle"))
    t.append(text(ox + 322, 110, [("v", "R")]))
    t.append(text(ox + 334, 175, [("v", "E")]))
    if q_open:
        t.append(text(ox + 6, 262, [("v", "i"), ("vsub", "L"), ("n", " &lt; 0"), ("t", " 經 "), ("v", "D"), ("t", " 流入 "), ("v", "V"), ("sub", "S"), ("t", "："), ("v", "v"), ("vsub", "a"), ("n", " = "), ("v", "V"), ("sub", "S"), ("n", " = 5 V")]))
        t.append(text(ox + 6, 288, [("v", "L"), ("n", " d"), ("v", "i"), ("vsub", "L"), ("n", "/d"), ("v", "t"), ("n", " + "), ("v", "Ri"), ("vsub", "L"), ("n", " = 5 − 10 = −5 V")]))
    else:
        t.append(text(ox + 6, 262, [("v", "Q"), ("t", " 短路使 "), ("v", "v"), ("vsub", "a"), ("n", " = 0"), ("t", "，"), ("v", "D"), ("t", " 反偏 "), ("n", "5 V")]))
        t.append(text(ox + 6, 288, [("v", "L"), ("n", " d"), ("v", "i"), ("vsub", "L"), ("n", "/d"), ("v", "t"), ("n", " + "), ("v", "Ri"), ("vsub", "L"), ("n", " = 0 − 10 = −10 V")]))
    return s, ''.join(t)


W, H = 720, 300
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(360, False)
s += a + G_OPEN + b + ta + tb + footer()
write('EE-114-02-3-two-states.svg', s)
