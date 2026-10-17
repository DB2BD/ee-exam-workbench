"""EE-104-01-2: coupled coils with dots (both top), mesh currents I1, I2 (clockwise) and phasor impedances."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 320
XA, XL1, XL2, XC = 70, 250, 380, 590
YT, YB = 90, 260
s = header(W, H)
s += terminal(XA, YT) + line(XA + 4, YT, 100, YT) + resistor(100, YT, 190, YT) + line(190, YT, XL1, YT)
s += line(XL1, YT, XL1, 125) + coil(XL1, 125, XL1, 225) + line(XL1, 225, XL1, YB)
s += line(XL1, YB, XA + 4, YB) + terminal(XA, YB)
s += line(XL2, YT, XL2, 125) + coil(XL2, 125, XL2, 225) + line(XL2, 225, XL2, YB)
s += line(XL2, YT, 430, YT) + resistor(430, YT, 520, YT) + line(520, YT, XC, YT)
s += cap(XC, YT, XC, YB) + line(XC, YB, XL2, YB)
s += '<circle cx="236" cy="122" r="3.6" fill="#000" stroke="none"/>\n'
s += '<circle cx="394" cy="122" r="3.6" fill="#000" stroke="none"/>\n'
s += '<path d="M272 150 Q315 132 358 150" stroke-width="1.2"/>\n'
s += mesh_arrow(140, 180, 28)
s += mesh_arrow(520, 180, 28)
s += end_group()
s += text(20, 28, [("t", "相量域，"), ("v", "ω"), ("n", " = 4000 rad/s"), ("t", "；● 同名端（兩線圈上端）；互阻抗取 −"), ("v", "jωM")])
s += text(XA - 10, YT + 6, [("v", "a")], anchor="end") + text(XA - 10, YB + 6, [("v", "b")], anchor="end")
s += ttext(XA + 2, 160, [("n", "+")], anchor="middle", color=BLUE) + ttext(XA + 2, 200, [("v", "V"), ("vsub", "ab")], anchor="middle", color=BLUE)
s += ttext(XA + 2, 238, [("n", "−")], anchor="middle", color=BLUE)
s += text(145, YT - 16, [("n", "20 Ω")], anchor="middle")
s += text(475, YT - 16, [("n", "5 Ω")], anchor="middle")
s += text(XL1 - 16, 172, [("v", "jωL"), ("sub", "1")], anchor="end") + text(XL1 - 16, 194, [("n", "= "), ("v", "j"), ("n", "50 Ω")], anchor="end")
s += text(XL2 + 16, 172, [("v", "jωL"), ("sub", "2")]) + text(XL2 + 16, 194, [("n", "= "), ("v", "j"), ("n", "32 Ω")])
s += text(XC + 20, 170, [("n", "−"), ("v", "j"), ("n", "/("), ("v", "ωC"), ("n", ") =")])
s += text(XC + 20, 194, [("n", "−"), ("v", "j"), ("n", "20 Ω")])
s += text(315, 120, [("v", "M")], anchor="middle")
s += ttext(140, 186, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(520, 186, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += footer()
write('EE-104-01-2-coupled.svg', s)
