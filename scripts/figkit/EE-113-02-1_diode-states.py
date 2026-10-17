"""EE-113-02-1: ideal-diode trial states. (a) both on -> I_D1 < 0 contradiction; (b) D1 off, D2 on -> consistent."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

XM, XL, XR, YX, YO = 150, 90, 220, 140, 220


def terminal(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3.5" fill="#fff"/>\n'


def panel(ox, both_on):
    s = ''
    s += terminal(ox + XM, 34) + line(ox + XM, 37.5, ox + XM, 50) + resistor(ox + XM, 50, ox + XM, 120, zigs=6, lead=10)
    s += line(ox + XM, 120, ox + XM, YX) + line(ox + XL, YX, ox + XR, YX) + dot(ox + XM, YX)
    # D1 branch (left) to ground
    if both_on:
        s += line(ox + XL, YX, ox + XL, 210)
    else:
        s += line(ox + XL, YX, ox + XL, 164.5) + line(ox + XL, 185.5, ox + XL, 210)
        s += terminal(ox + XL, 168) + terminal(ox + XL, 182)
    s += ground(ox + XL, 210)
    # D2 branch (right): short in both trials
    s += line(ox + XR, YX, ox + XR, YO) + dot(ox + XR, YO) + line(ox + XR, YO, ox + XR + 50, YO) + terminal(ox + XR + 53.5, YO)
    s += resistor(ox + XR, YO, ox + XR, 290, zigs=6, lead=10) + line(ox + XR, 290, ox + XR, 300) + terminal(ox + XR, 303.5)
    # currents
    s += red_arrow(ox + XM + 18, 62, ox + XM + 18, 102)
    s += red_arrow(ox + XR + 18, 152, ox + XR + 18, 196)
    if both_on:
        s += red_arrow(ox + XL + 18, 156, ox + XL + 18, 192)
    s += end_group()
    t = []
    t.append(text(ox + 6, 22, [("t", "(a) 假設 "), ("v", "D"), ("sub", "1"), ("t", "、"), ("v", "D"), ("sub", "2"), ("t", " 皆導通")] if both_on else
                  [("t", "(b) "), ("v", "D"), ("sub", "1"), ("t", " 截止、"), ("v", "D"), ("sub", "2"), ("t", " 導通")]))
    t.append(text(ox + XM + 10, 40, [("n", "+12 V")]))
    t.append(text(ox + XM - 12, 90, [("n", "10 kΩ")], anchor="end"))
    t.append(text(ox + XR - 12, 262, [("n", "5 kΩ")], anchor="end"))
    t.append(text(ox + XR + 10, 323, [("n", "−12 V")]))
    t.append(text(ox + XR + 62, YO + 5, [("v", "V"), ("vsub", "o")]))
    t.append(text(ox + XR - 6, 206, [("v", "D"), ("sub", "2"), ("t", "：短路")], anchor="end"))
    if both_on:
        t.append(text(ox + XL - 10, 184, [("v", "D"), ("sub", "1"), ("t", "：短路")], anchor="end"))
        t.append(ctext(ox + XM + 28, 88, [("n", "1.20 mA")]))
        t.append(ctext(ox + XR + 28, 180, [("n", "2.40 mA")]))
        t.append(ctext(ox + 30, 246, [("v", "I"), ("vsub", "D"), ("sub", "1"), ("n", " = −1.20 mA")], anchor="start"))
        t.append(text(ox + XM + 8, YX - 8, [("v", "V"), ("vsub", "x"), ("n", " = 0")], anchor="start", color=BLUE).replace('fill="#000"', f'fill="{BLUE}"', 1))
        t.append(text(ox + 6, 350, [("v", "I"), ("vsub", "D"), ("sub", "1"), ("n", " &lt; 0"), ("t", "：與導通矛盾")]))
    else:
        t.append(text(ox + XL - 10, 180, [("v", "D"), ("sub", "1"), ("t", "：開路")], anchor="end"))
        t.append(ctext(ox + XM + 28, 88, [("v", "I"), ("n", " = 1.60 mA")]))
        t.append(ctext(ox + XR + 28, 180, [("v", "I")]))
        t.append(text(ox + XM + 8, YX - 8, [("v", "V"), ("vsub", "x"), ("n", " = −4 V")], anchor="start").replace('fill="#000"', f'fill="{BLUE}"', 1))
        t.append(text(ox + 6, 350, [("v", "I"), ("n", " &gt; 0"), ("t", "、"), ("v", "V"), ("vsub", "D"), ("sub", "1"), ("n", " = −4 V &lt; 0"), ("t", "：自洽")]))
    return s, ''.join(t)


W, H = 720, 364
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(360, False)
s += a + G_OPEN + b + ta + tb + footer()
write('EE-113-02-1-diode-states.svg', s)
