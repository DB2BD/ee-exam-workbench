"""EE-109-01-4: circuit with node names A, B and state-variable references v_C (A +) and i_L (down)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 720, 410
XL, XA, XB, XR, XO = 80, 220, 420, 520, 640
YU, YT, YM, YB = 70, 150, 220, 350
s = header(W, H)
s += vsrc(XL, YT, XL, YB, r=18)                                  # 10u(t), + on top
s += line(XL, YT, XA, YT)
# parallel block A-B: current source (arrow left), C1, R1
s += line(XA, YU, XA, YM) + line(XB, YU, XB, YM)
s += line(XA, YU, 298, YU) + isrc(342, YU, 298, YU, r=18) + line(342, YU, XB, YU)
s += cap(XA, YT, XB, YT)
s += line(XA, YM, 280, YM) + resistor(280, YM, 360, YM) + line(360, YM, XB, YM)
s += line(XB, YT, XO, YT)
s += line(XR, YT, XR, 175) + resistor(XR, 175, XR, 245, lead=6) + coil(XR, 255, XR, 320) + line(XR, 245, XR, 255) + line(XR, 320, XR, YB)
s += line(XL, YB, 280, YB) + vsrc(280, YB, 340, YB, r=16) + line(340, YB, XO, YB)
s += dot(XA, YT) + dot(XB, YT) + dot(XR, YT) + dot(XR, YB)
s += terminal(XO, YT) + terminal(XO, YB)
s += tint_arrow(XR - 18, 182, XR - 18, 226)                       # i_L down
s += end_group()
s += text(20, 28, [("t", "零初值；參考點為右下端（"), ("v", "v"), ("sub", "2"), ("t", " 負端）")])
s += text(XL + 26, 256, [("n", "10"), ("v", "u"), ("n", "("), ("v", "t"), ("n", ") V")])
s += text(310, YB + 40, [("n", "4"), ("v", "δ"), ("n", "("), ("v", "t"), ("n", ") V")], anchor="middle")
s += text(366, YU - 24, [("n", "6"), ("v", "δ"), ("n", "("), ("v", "t"), ("n", ") A")])
s += text(320, YT + 40, [("v", "C"), ("sub", "1"), ("n", " = 1 F")], anchor="middle")
s += text(320, YM + 30, [("v", "R"), ("sub", "1"), ("n", " = 1 Ω")], anchor="middle")
s += text(XR + 14, 216, [("v", "R"), ("sub", "2"), ("n", " = 1 Ω")])
s += text(XR + 14, 294, [("v", "L"), ("sub", "2"), ("n", " = 1 H")])
s += text(XA - 8, YT - 10, [("v", "A")], anchor="end")
s += text(XB + 8, YT - 10, [("v", "B")])
s += ttext(XA + 16, YT - 18, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XB - 16, YT - 18, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(262, YT - 18, [("v", "v"), ("vsub", "C")], anchor="middle", color=BLUE)
s += ttext(XR - 24, 210, [("v", "i"), ("vsub", "L")], anchor="end", color=RED)
s += ttext(XO + 12, YT + 6, [("n", "+")], color=BLUE) + ttext(XO + 12, YB + 6, [("n", "−")], color=BLUE)
s += ttext(XO + 12, 256, [("v", "v"), ("sub", "2")], color=BLUE)
s += footer()
write('EE-109-01-4-states.svg', s)
