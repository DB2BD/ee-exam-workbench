"""EE-105-02-3: equivalent circuits of the limiter with the op-amp inverting node n at virtual ground.
(a) positive knee: D2 just conducting (V_y = +0.7 V, i_D2 = 0); (b) D1 conducting (V_x = -0.7 V), used for vS = 5 V."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *


def term(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3.2" fill="#fff"/>\n'


def panel_a(ox):
    s, t = '', []
    yr, yd, yb = 100, 190, 268          # R1/RF row, D2 row, -V_B terminal
    xn, xo = ox + 110, ox + 250
    s += term(ox + 24, yr) + resistor(ox + 27, yr, xn, yr, zigs=6, lead=18)
    s += resistor(xn, yr, xo, yr, zigs=6, lead=40) + term(xo + 40, yr) + line(xo, yr, xo + 37, yr)
    s += line(xn, yr, xn, yd) + diode(xo, yd, xn, yd)
    s += resistor(xo, yr, xo, yd, zigs=6, lead=16) + resistor(xo, yd, xo, yb - 3, zigs=6, lead=14) + term(xo, yb)
    for x, y in ((xn, yr), (xo, yr), (xo, yd)):
        s += dot(x, y)
    t.append(text(ox + 6, 24, [("t", "(a) 正限幅膝點："), ("v", "D"), ("sub", "2"), ("t", " 剛導通")]))
    t.append(text(ox + 24, yr - 14, [("v", "v"), ("vsub", "S")], anchor="middle"))
    t.append(text(ox + 72, yr + 26, [("v", "R"), ("sub", "1")], anchor="middle"))
    t.append(text((xn + xo) / 2, yr - 14, [("v", "R"), ("vsub", "F")], anchor="middle"))
    t.append(text(xn, yr - 14, [("v", "n")], anchor="middle"))
    t.append(ctext(xn + 8, yr + 44, [("n", "0 V")], color=BLUE))
    t.append(text(xo + 40, yr - 12, [("v", "v"), ("vsub", "O")], anchor="middle"))
    t.append(text(xo + 14, (yr + yd) / 2 + 5, [("v", "R"), ("sub", "5"), ("n", " = 1 kΩ")]))
    t.append(text(xo + 14, (yd + yb) / 2 + 5, [("v", "R"), ("sub", "4"), ("n", " = 5 kΩ")]))
    t.append(text((xn + xo) / 2, yd + 30, [("v", "D"), ("sub", "2")], anchor="middle"))
    t.append(ctext(xo + 14, yd - 6, [("v", "V"), ("vsub", "y"), ("n", " = +0.7 V")], color=BLUE))
    t.append(text(xo + 12, yb + 18, [("n", "−"), ("v", "V"), ("vsub", "B"), ("n", " = −15 V")], anchor="middle"))
    t.append(text(ox + 6, 312, [("v", "i"), ("vsub", "D"), ("sub", "2"), ("n", " = 0"), ("t", "，"), ("v", "v"), ("vsub", "O"), ("n", " = −4"), ("v", "v"), ("vsub", "S"), ("t", " 仍成立")]))
    return s, ''.join(t)


def panel_b(ox):
    s, t = '', []
    ya, yx, yr = 52, 130, 214            # +V_A terminal, D1 / V_x row, R1/RF row
    xn, xo = ox + 100, ox + 240
    s += term(xo, ya) + resistor(xo, ya + 3, xo, yx, zigs=6, lead=14)
    s += diode(xn, yx, xo, yx) + line(xn, yx, xn, yr)
    s += resistor(xo, yx, xo, yr, zigs=6, lead=16)
    s += term(ox + 24, yr) + resistor(ox + 27, yr, xn, yr, zigs=6, lead=18)
    s += resistor(xn, yr, xo, yr, zigs=6, lead=40) + line(xo, yr, xo + 37, yr) + term(xo + 40, yr)
    for x, y in ((xn, yr), (xo, yr), (xo, yx)):
        s += dot(x, y)
    s += red_arrow(ox + 34, yr - 24, ox + 74, yr - 24)          # i_R1 into n
    s += red_arrow(xn + 30, yx - 22, xn + 80, yx - 22)          # i_1 through D1, n -> V_x
    s += red_arrow(xo + 30, yr + 26, xn + 50, yr + 26)          # i_F, v_O -> n (reference)
    s += red_arrow(xo - 16, ya + 12, xo - 16, ya + 46)          # i_R2, +V_A -> V_x
    s += red_arrow(xo - 16, yx + 18, xo - 16, yx + 52)          # i_R3, V_x -> v_O
    t.append(text(ox + 6, 24, [("t", "(b) "), ("v", "D"), ("sub", "1"), ("t", " 導通（"), ("v", "v"), ("vsub", "S"), ("n", " = 5 V"), ("t", "）")]))
    t.append(text(xo + 12, ya - 10, [("n", "+"), ("v", "V"), ("vsub", "A"), ("n", " = +15 V")], anchor="middle"))
    t.append(text(xo + 14, (ya + yx) / 2 + 5, [("v", "R"), ("sub", "2"), ("n", " = 4 kΩ")]))
    t.append(text(xo + 14, (yx + yr) / 2 + 5, [("v", "R"), ("sub", "3"), ("n", " = 1 kΩ")]))
    t.append(ctext(xo + 14, yx - 6, [("v", "V"), ("vsub", "x"), ("n", " = −0.7 V")], color=BLUE))
    t.append(text((xn + xo) / 2, yx + 30, [("v", "D"), ("sub", "1")], anchor="middle"))
    t.append(ctext(xn + 86, yx - 18, [("v", "i"), ("sub", "1")]))
    t.append(text(ox + 24, yr + 22, [("v", "v"), ("vsub", "S")], anchor="middle"))
    t.append(ctext(ox + 54, yr - 32, [("v", "i"), ("vsub", "R"), ("sub", "1")], anchor="middle"))
    t.append(text(ox + 62, yr + 22, [("v", "R"), ("sub", "1")], anchor="middle"))
    t.append(text(xn + 8, yr - 10, [("v", "n")]))
    t.append(ctext(xn - 8, yx + 44, [("n", "0 V")], anchor="end", color=BLUE))
    t.append(text((xn + xo) / 2, yr - 14, [("v", "R"), ("vsub", "F")], anchor="middle"))
    t.append(ctext(xn + 44, yr + 44, [("v", "i"), ("vsub", "F")], anchor="end"))
    t.append(text(xo + 40, yr - 12, [("v", "v"), ("vsub", "O")], anchor="middle"))
    t.append(text(ox + 6, 290, [("t", "節點 "), ("v", "n"), ("t", "："), ("v", "i"), ("vsub", "R"), ("sub", "1"), ("n", " + "), ("v", "i"), ("vsub", "F"), ("n", " = "), ("v", "i"), ("sub", "1")]))
    t.append(ctext(xo - 22, ya + 36, [("v", "i"), ("vsub", "R"), ("sub", "2")], anchor="end"))
    t.append(ctext(xo - 22, yx + 42, [("v", "i"), ("vsub", "R"), ("sub", "3")], anchor="end"))
    t.append(text(ox + 6, 312, [("t", "節點 "), ("v", "V"), ("vsub", "x"), ("t", "："), ("v", "i"), ("sub", "1"), ("n", " + "), ("v", "i"), ("vsub", "R"), ("sub", "2"), ("n", " = "), ("v", "i"), ("vsub", "R"), ("sub", "3")]))
    return s, ''.join(t)


W, H = 720, 330
s = header(W, H)
a, ta = panel_a(0)
b, tb = panel_b(360)
s += a + b + end_group() + ta + tb
s += f'<path d="M357 34 L357 316" stroke="#000" stroke-width="0.6" stroke-dasharray="3 3"/>\n'
s += footer()
write('EE-105-02-3-states.svg', s)
