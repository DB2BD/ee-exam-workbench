"""EE-106-02-4: half-wave rectifier with freewheeling diode, (a) positive half: D1 conducts; (b) negative half: D2 freewheels I_o."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

YT, YB = 70, 230


def panel(ox, pos):
    s = ''
    s += ac_source(ox + 50, 150, r=16) + line(ox + 50, 134, ox + 50, YT) + line(ox + 50, 166, ox + 50, YB)
    s += diode(ox + 50, YT, ox + 200, YT)                                      # D1: anode at source, cathode at node
    s += diode(ox + 200, YB, ox + 200, YT)                                     # D2: anode bottom, cathode node
    s += line(ox + 200, YT, ox + 300, YT) + resistor(ox + 300, YT, ox + 300, 140, zigs=6, lead=10)
    s += coil(ox + 300, 140, ox + 300, YB, turns=4)
    s += line(ox + 50, YB, ox + 300, YB)
    s += dot(ox + 200, YT) + dot(ox + 200, YB)
    s += red_arrow(ox + 236, 50, ox + 276, 50)                                  # I_o
    if pos:
        s += red_arrow(ox + 90, 50, ox + 130, 50)                               # i_D1 = I_o
    else:
        s += red_arrow(ox + 184, 180, ox + 184, 130)                            # i_D2 = I_o upward
    s += end_group()
    t = []
    if pos:
        t.append(text(ox + 6, 24, [("t", "(a) 正半週 "), ("n", "0 &lt; "), ("v", "θ"), ("n", " &lt; π")]))
    else:
        t.append(text(ox + 6, 24, [("t", "(b) 負半週 "), ("n", "π &lt; "), ("v", "θ"), ("n", " &lt; 2π")]))
    t.append(text(ox + 28, 155, [("v", "v"), ("vsub", "s")], anchor="end"))
    t.append(text(ox + 125, 98, [("v", "D"), ("sub", "1"), ("t", " 導通" if pos else " 截止")], anchor="middle"))
    t.append(text(ox + 214, 156, [("v", "D"), ("sub", "2")]))
    t.append(text(ox + 214, 180, [("t", "截止" if pos else "導通")]))
    t.append(text(ox + 260, 104, [("n", "+")]))
    t.append(text(ox + 260, 160, [("v", "v"), ("vsub", "o")]))
    t.append(text(ox + 260, 220, [("n", "−")]))
    t.append(text(ox + 314, 110, [("v", "R")]))
    t.append(text(ox + 314, 190, [("v", "L")]))
    t.append(ctext(ox + 280, 46, [("v", "I"), ("vsub", "o")]))
    if pos:
        t.append(ctext(ox + 82, 46, [("v", "i"), ("vsub", "D"), ("sub", "1")], anchor="end"))
        t.append(text(ox + 6, 264, [("v", "v"), ("vsub", "s"), ("n", " &gt; 0"), ("t", "：電源經 "), ("v", "D"), ("sub", "1"), ("t", " 供電")]))
        t.append(text(ox + 6, 288, [("v", "v"), ("vsub", "o"), ("n", " = "), ("v", "v"), ("vsub", "s"), ("t", "，"), ("v", "i"), ("vsub", "D"), ("sub", "1"), ("n", " = "), ("v", "I"), ("vsub", "o"), ("t", "，"), ("v", "i"), ("vsub", "D"), ("sub", "2"), ("n", " = 0")]))
    else:
        t.append(ctext(ox + 178, 150, [("v", "i"), ("vsub", "D"), ("sub", "2")], anchor="end"))
        t.append(text(ox + 6, 264, [("v", "v"), ("vsub", "s"), ("n", " &lt; 0"), ("t", "：電感電流經 "), ("v", "D"), ("sub", "2"), ("t", " 續流")]))
        t.append(text(ox + 6, 288, [("v", "v"), ("vsub", "o"), ("n", " = 0"), ("t", "，"), ("v", "i"), ("vsub", "D"), ("sub", "1"), ("n", " = 0"), ("t", "，"), ("v", "i"), ("vsub", "D"), ("sub", "2"), ("n", " = "), ("v", "I"), ("vsub", "o")]))
    return s, ''.join(t)


W, H = 720, 300
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(360, False)
s += a + G_OPEN + b + ta + tb + footer()
write('EE-106-02-4-two-states.svg', s)
