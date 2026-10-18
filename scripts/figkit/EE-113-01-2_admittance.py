"""EE-113-01-2: two-node circuit with every element's admittance; right source leaves V2 (= +j0.5 A injected)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 720, 340
YT, YB = 110, 280
X1S, XR5, XC10, P1, P2, XL5, XR10, X2S = 50, 142, 220, 255, 375, 425, 520, 610
s = header(W, H)
s += isrc(X1S, YB, X1S, YT)                                    # 1∠0° A up into V1
s += line(X1S, YT, P1, YT) + line(P2, YT, X2S, YT) + line(X1S, YB, X2S, YB)
s += resistor(XR5, YT, XR5, YB, lead=50)
s += cap(XC10, YT, XC10, YB)
s += line(P1, YT - 34, P1, YT + 30) + line(P2, YT - 34, P2, YT + 30)
s += cap(P1, YT - 34, P2, YT - 34)
s += line(P1, YT + 30, 280, YT + 30) + coil(280, YT + 30, 350, YT + 30, turns=3) + line(350, YT + 30, P2, YT + 30)
s += coil(XL5, YT + 50, XL5, YB - 50, turns=4) + line(XL5, YT, XL5, YT + 50) + line(XL5, YB - 50, XL5, YB)
s += resistor(XR10, YT, XR10, YB, lead=50)
s += isrc(X2S, YT, X2S, YB)                                    # 0.5∠-90° A down (leaves V2)
for x in (XR5, XC10, P1, P2, XL5, XR10):
    s += dot(x, YT)
for x in (XR5, XC10, XL5, XR10):
    s += dot(x, YB)
s += line(315, YB, 315, YB + 8) + ground(315, YB + 8)
s += end_group()
s += text(20, 28, [("v", "ω"), ("n", " = 10 rad/s"), ("t", "；括號內為導納")])
s += text(170, YT - 14, [("v", "V"), ("sub", "1")], anchor="middle")
s += text(475, YT - 14, [("v", "V"), ("sub", "2")], anchor="middle")
s += text(X1S + 20, 190, [("n", "1∠0° A")])
s += text(XR5 + 12, 210, [("n", "5 Ω")]) + text(XR5 + 12, 232, [("n", "(0.20 S)")])
s += text(XC10 + 14, 240, [("n", "−"), ("v", "j"), ("n", "10 Ω")]) + text(XC10 + 14, 262, [("n", "("), ("v", "j"), ("n", "0.10 S)")])
s += text(315, YT - 58, [("n", "−"), ("v", "j"), ("n", "5 Ω")], anchor="middle")
s += text(315, YT + 58, [("v", "j"), ("n", "10 Ω")], anchor="middle")
s += text(315, YT + 82, [("v", "Y"), ("sub", "12"), ("n", " = "), ("v", "j"), ("n", "0.10 S")], anchor="middle")
s += text(XL5 + 10, 190, [("v", "j"), ("n", "5 Ω")]) + text(XL5 + 10, 212, [("n", "(−"), ("v", "j"), ("n", "0.20 S)")])
s += text(XR10 + 12, 210, [("n", "10 Ω")]) + text(XR10 + 12, 232, [("n", "(0.10 S)")])
s += text(X2S + 22, 190, [("n", "0.5∠−90° A")])
s += text(X2S + 22, 212, [("t", "流出 "), ("v", "V"), ("sub", "2")])
s += footer()
write('EE-113-01-2-admittance.svg', s)
