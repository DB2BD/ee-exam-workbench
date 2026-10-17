"""EE-112-01-2: coupled-inductor circuit with dots, mesh currents I1, I2 and the L2 current I1 - I2."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 720, 320, 90, 260
XS, XN, XR = 120, 410, 615
s = header(W, H)
s += line(XS, YT, XS, 161) + ac_source(XS, 175) + line(XS, 189, XS, YB)
s += line(XS, YT, 150, YT) + resistor(150, YT, 230, YT) + line(230, YT, 250, YT)
s += coil(250, YT, 340, YT, turns=4) + line(340, YT, XN, YT)
s += coil(XN, 120, XN, 230, turns=4) + line(XN, YT, XN, 120) + line(XN, 230, XN, YB)
s += line(XN, YT, XR, YT) + resistor(XR, YT, XR, YB, zigs=6, lead=50) + line(XS, YB, XR, YB)
s += dot(XN, YT) + dot(XN, YB)
s += '<circle cx="348" cy="76" r="3.6" fill="#000" stroke="none"/>\n'      # L1 dot: right end
s += '<circle cx="396" cy="238" r="3.6" fill="#000" stroke="none"/>\n'     # L2 dot: bottom end
s += mesh_arrow(285, 180, 34)
s += mesh_arrow(530, 180, 34)
s += tint_arrow(382, 150, 382, 192)                                         # I1 - I2 down through L2
s += end_group()
s += text(20, 28, [("t", "峰值相量，"), ("v", "ω"), ("n", " = 5000 rad/s；● 同名端（"), ("v", "L"), ("sub", "1"), ("t", " 右端、"),
                   ("v", "L"), ("sub", "2"), ("t", " 下端）")])
s += ttext(XS + 18, 152, [("n", "+")], color=BLUE) + ttext(XS + 18, 206, [("n", "−")], color=BLUE)
s += text(XS - 22, 172, [("v", "V"), ("vsub", "g")], anchor="end")
s += text(XS - 22, 194, [("n", "660∠0° V")], anchor="end")
s += text(190, YT - 16, [("n", "34 Ω")], anchor="middle")
s += text(295, YT - 18, [("v", "jωL"), ("sub", "1"), ("n", " = "), ("v", "j"), ("n", "50 Ω")], anchor="middle")
s += text(XN + 18, 170, [("v", "jωL"), ("sub", "2")])
s += text(XN + 18, 192, [("n", "= "), ("v", "j"), ("n", "100 Ω")])
s += text(335, 128, [("v", "jωM"), ("n", " = "), ("v", "j"), ("n", "40 Ω")], anchor="middle")
s += text(XR + 16, 180, [("v", "R"), ("n", " = 100 Ω")])
s += ttext(285, 186, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(530, 186, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += ttext(376, 214, [("v", "I"), ("sub", "1"), ("n", " − "), ("v", "I"), ("sub", "2")], anchor="end", color=RED)
s += footer()
write('EE-112-01-2-mesh.svg', s)
