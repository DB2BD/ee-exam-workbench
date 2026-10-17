"""EE-111-01-2: coupled coils (dots on top), clockwise mesh currents I1, I2, shared 2 ohm carrying I1 - I2."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB, YM = 680, 340, 90, 300, 210
XS, X1, X2, XC, XR = 110, 290, 350, 320, 580
s = header(W, H)
s += vsrc(XS, YT, XS, YB)
s += line(XS, YT, 140, YT) + resistor(140, YT, 220, YT) + line(220, YT, X1, YT)
s += coil(X1, YT, X1, 180, turns=4) + line(X1, 180, X1, YM)
s += coil(X2, 180, X2, YT, turns=4) + line(X2, 180, X2, YM)
s += line(X1, YM, X2, YM) + dot(XC, YM) + resistor(XC, YM, XC, YB, zigs=6, lead=14)
s += line(X2, YT, 420, YT) + cap(420, YT, 480, YT) + line(480, YT, XR, YT)
s += resistor(XR, YT, XR, YB, zigs=6, lead=60)
s += line(XS, YB, XR, YB) + dot(XC, YB)
s += '<circle cx="276" cy="104" r="3.6" fill="#000" stroke="none"/>\n'   # L1 dot: top
s += '<circle cx="364" cy="104" r="3.6" fill="#000" stroke="none"/>\n'   # L2 dot: top
s += mesh_arrow(205, 225, 34)
s += mesh_arrow(470, 225, 34)
s += tint_arrow(XC + 16, 235, XC + 16, 272)                                  # I1 - I2 down through 2 ohm
s += end_group()
s += text(20, 30, [("t", "峰值相量（cos 基準），"), ("v", "ω"), ("n", " = 2 rad/s"), ("t", "；● 同名端（兩線圈皆在上端）")])
s += ttext(XS + 20, YT + 80, [("n", "+")], color=BLUE) + ttext(XS + 20, YB - 72, [("n", "−")], color=BLUE)
s += ttext(XS - 22, 190, [("v", "V"), ("vsub", "s")], anchor="end", color=BLUE)
s += ttext(XS - 22, 212, [("n", "36∠30° V")], anchor="end", color=BLUE)
s += text(180, YT - 14, [("n", "5 Ω")], anchor="middle")
s += text(X1 - 14, 132, [("v", "jωL"), ("sub", "1")], anchor="end")
s += text(X1 - 14, 154, [("n", "= "), ("v", "j"), ("n", "6 Ω")], anchor="end")
s += text(X2 + 14, 132, [("v", "jωL"), ("sub", "2")])
s += text(X2 + 14, 154, [("n", "= "), ("v", "j"), ("n", "3 Ω")])
s += text(XC, 62, [("v", "jωM"), ("n", " = "), ("v", "j"), ("n", "1 Ω")], anchor="middle")
s += text(450, YT - 22, [("v", "Z"), ("vsub", "C"), ("n", " = −"), ("v", "j"), ("n", "4 Ω")], anchor="middle")
s += text(XR + 16, 200, [("n", "4 Ω")])
s += text(XC - 16, 262, [("n", "2 Ω")], anchor="end")
s += ttext(205, 231, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(470, 231, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += ttext(XC + 24, 290, [("v", "I"), ("sub", "1"), ("n", " − "), ("v", "I"), ("sub", "2")], color=RED)
s += footer()
write('EE-111-01-2-mesh.svg', s)
