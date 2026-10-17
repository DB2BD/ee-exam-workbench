"""EE-108-01-4: phasor-domain coupled circuit — primary dot bottom, secondary dot top, I1 and I2 reference directions, Z_L."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 720, 330, 90, 260
XS, XP, XQ, XR, XC = 130, 310, 410, 540, 620
s = header(W, H)
s += line(XS, YT, XS, 159) + ac_source(XS, 175, r=16) + line(XS, 191, XS, YB)
s += line(XS, YT, 160, YT) + resistor(160, YT, 240, YT) + line(240, YT, XP, YT)
s += line(XP, YT, XP, 125) + coil(XP, 125, XP, 225, turns=4) + line(XP, 225, XP, YB) + line(XS, YB, XP, YB)
s += line(XQ, YT, XQ, 125) + coil(XQ, 225, XQ, 125, turns=4) + line(XQ, 225, XQ, YB)
s += line(XQ, YT, XC, YT) + line(XQ, YB, XC, YB)
s += resistor(XR, YT, XR, YB, zigs=6, lead=40) + cap(XC, YT, XC, YB)
s += dot(XR, YT) + dot(XR, YB)
s += '<circle cx="298" cy="238" r="3.6" fill="#000" stroke="none"/>\n'   # primary dot: bottom
s += '<circle cx="422" cy="112" r="3.6" fill="#000" stroke="none"/>\n'   # secondary dot: top
s += tint_arrow(250, YT - 12, 288, YT - 12)                             # I1 enters primary top
s += tint_arrow(432, YT - 12, 470, YT - 12)                             # I2 to the right on the top wire
s += f'<rect x="{XR - 16}" y="{YT + 14}" width="{XC - XR + 30}" height="{YB - YT - 28}" fill="none" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += end_group()
s += text(20, 28, [("t", "峰值相量（cos 基準），"), ("v", "ω"), ("n", " = 2 rad/s"), ("t", "；● 同名端（一次側下端、二次側上端）")])
s += text(XS + 22, 158, [("n", "+")]) + text(XS + 22, 204, [("n", "−")])
s += text(XS - 24, 172, [("v", "V"), ("vsub", "s")], anchor="end")
s += text(XS - 24, 194, [("n", "10√2∠0° V")], anchor="end")
s += text(200, YT - 16, [("n", "1 Ω")], anchor="middle")
s += ttext(269, YT - 24, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(451, YT - 24, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += text(XP - 14, 168, [("v", "jωL"), ("sub", "1")], anchor="end")
s += text(XP - 14, 190, [("n", "= "), ("v", "j"), ("n", "2 Ω")], anchor="end")
s += text(XQ + 14, 168, [("v", "jωL"), ("sub", "2")])
s += text(XQ + 14, 190, [("n", "= "), ("v", "j"), ("n", "2 Ω")])
s += text((XP + XQ) / 2, YB + 30, [("v", "jωM"), ("n", " = "), ("v", "j"), ("n", "1 Ω")], anchor="middle")
s += text(XR + 12, 186, [("n", "1 Ω")])
s += text(XC + 20, 172, [("v", "Z"), ("vsub", "C")])
s += text(XC + 20, 194, [("n", "= −"), ("v", "j"), ("n", "0.50 Ω")])
s += ttext((XR + XC) / 2 + 4, YB + 30, [("v", "Z"), ("vsub", "L"), ("n", " = 0.20 − "), ("v", "j"), ("n", "0.40 Ω")], anchor="middle", color=BLUE)
s += footer()
write('EE-108-01-4-phasor-circuit.svg', s)
