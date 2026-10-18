"""EE-109-01-3: original diamond circuit, centre node grounded, with the two supernodes {1,2} and {3,4} outlined."""
import math, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 440
O = (320, 220)
N1, N2, N3, N4 = (320, 50), (510, 220), (320, 390), (130, 220)
s = header(W, H)
# grounded resistors (radial)
s += resistor(N1[0], N1[1], O[0], O[1], zigs=6, lead=55)
s += resistor(O[0], O[1], N2[0], N2[1], zigs=6, lead=50)
s += resistor(O[0], O[1], N3[0], N3[1], zigs=6, lead=55)
s += resistor(N4[0], N4[1], O[0], O[1], zigs=6, lead=50)
s += line(O[0], O[1], O[0] + 22, O[1] + 18) + ground(O[0] + 22, O[1] + 18)
# rim sources
s += isrc(*N4, *N1)                    # I_41: 1 A from node 4 to node 1
s += vsrc(*N1, *N2)                    # V_12: + at node 1
s += isrc(*N2, *N3)                    # I_23: 3 A from node 2 to node 3
s += vsrc(*N3, *N4)                    # V_34: + at node 3
for P in (N1, N2, N3, N4, O):
    s += dot(*P)


def oval(P, Q, rx_pad=14, ry=24):
    cx, cy = (P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2
    ang = math.degrees(math.atan2(Q[1] - P[1], Q[0] - P[0]))
    rx = math.hypot(Q[0] - P[0], Q[1] - P[1]) / 2 + rx_pad
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry}" transform="rotate({ang:.2f} {cx:.1f} {cy:.1f})" '
            f'stroke="{BLUE}" stroke-dasharray="6 4" stroke-width="1.3"/>\n')


s += oval(N1, N2) + oval(N3, N4)
s += end_group()
s += text(N1[0] - 28, N1[1] - 2, [("v", "V"), ("sub", "1")], anchor="end")
s += text(N2[0] + 10, N2[1] + 30, [("v", "V"), ("sub", "2")])
s += text(N3[0] + 12, N3[1] + 22, [("v", "V"), ("sub", "3")])
s += text(N4[0] - 32, N4[1] + 6, [("v", "V"), ("sub", "4")], anchor="end")
s += text(O[0] + 12, 150, [("v", "R"), ("sub", "1"), ("n", " = 1 Ω")])
s += text(415, O[1] - 14, [("v", "R"), ("sub", "2"), ("n", " = 2 Ω")], anchor="middle")
s += text(O[0] + 12, 300, [("v", "R"), ("sub", "3"), ("n", " = 3 Ω")])
s += text(225, O[1] - 14, [("v", "R"), ("sub", "4"), ("n", " = 4 Ω")], anchor="middle")
s += text(196, 120, [("v", "I"), ("sub", "41"), ("n", " = 1 A")], anchor="end")
s += text(444, 300, [("v", "I"), ("sub", "23"), ("n", " = 3 A")])
s += ttext(458, 100, [("v", "V"), ("sub", "12"), ("n", " = 2 V")], color=BLUE)
s += ttext(190, 352, [("v", "V"), ("sub", "34"), ("n", " = 4 V")], anchor="end", color=BLUE)
s += ttext(560, 70, [("t", "超節點 {1, 2}")], anchor="middle", color=BLUE)
s += ttext(130, 400, [("t", "超節點 {3, 4}")], anchor="middle", color=BLUE)
s += footer()
write('EE-109-01-3-supernodes.svg', s)
