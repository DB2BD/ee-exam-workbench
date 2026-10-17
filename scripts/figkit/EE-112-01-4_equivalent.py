"""EE-112-01-4: parallel RLC with the two step current sources merged into one injection i_s."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 640, 300, 80, 250
XS, XL, XC, XR = 110, 260, 400, 530
s = header(W, H)
s += isrc(XS, YB, XS, YT)                                  # arrow up: injection into the top node
s += coil(XL, YT, XL, YB, turns=5) + cap(XC, YT, XC, YB) + resistor(XR, YT, XR, YB, zigs=6, lead=50)
s += line(XS, YT, XR, YT) + line(XS, YB, XR, YB)
for x in (XL, XC):
    s += dot(x, YT) + dot(x, YB)
s += tint_arrow(XL + 18, 148, XL + 18, 188)                # i down through L
s += end_group()
s += text(20, 30, [("t", "兩電流源合併為注入上節點的 "), ("v", "i"), ("vsub", "s"), ("n", " = −3"), ("v", "u"), ("n", "("), ("v", "t"),
                   ("n", ") − 3"), ("v", "u"), ("n", "("), ("v", "t"), ("n", ") = −6"), ("v", "u"), ("n", "("), ("v", "t"), ("n", ") A")])
s += text(XS - 24, 162, [("v", "i"), ("vsub", "s")], anchor="end")
s += text(XS - 24, 184, [("n", "= −6"), ("v", "u"), ("n", "("), ("v", "t"), ("n", ") A")], anchor="end")
s += text(XL - 20, 170, [("v", "L"), ("n", " = 0.2 H")], anchor="end")
s += ttext(XL + 28, 174, [("v", "i"), ("n", "("), ("v", "t"), ("n", ")")], color=RED)
s += ttext(XC - 20, 128, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XC - 20, 216, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XC - 20, 174, [("v", "v"), ("n", "("), ("v", "t"), ("n", ")")], anchor="end", color=BLUE)
s += text(XC + 22, 174, [("v", "C"), ("n", " = 20 mF")])
s += text(XR + 18, 174, [("v", "R"), ("n", " = 0.5 Ω")])
s += footer()
write('EE-112-01-4-equivalent.svg', s)
