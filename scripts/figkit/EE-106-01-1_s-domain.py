"""EE-106-01-1: s-domain equivalent circuit (zero initial state): impulses -> constants, L -> 2s, C -> 1/(2s)."""
import re, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 360
XL, XR, XI, XC, XO = 80, 410, 490, 590, 664
YT, YB = 90, 310
s = header(W, H)
s += vsrc(XL, YT, XL, YB, r=18)
s += line(XL, YT, 105, YT) + resistor(105, YT, 175, YT) + line(175, YT, 195, YT)
s += vsrc(265, YT, 195, YT, r=18)                       # 4 (V*s): - left, + right
s += line(265, YT, 290, YT) + coil(290, YT, 360, YT, turns=4) + line(360, YT, XO - 4, YT)
s += resistor(XR, YT, XR, YB, lead=70)
s += isrc(XI, YB, XI, YT, r=18)                          # 8 (A*s) up into a
s += cap(XC, YT, XC, YB)
s += line(XL, YB, XO - 4, YB) + terminal(XO, YT) + terminal(XO, YB)
for p in ((XR, YT), (XI, YT), (XC, YT), (XR, YB), (XI, YB), (XC, YB)):
    s += dot(*p)
s += tint_arrow(362, YT + 18, 398, YT + 18)              # I_L(s) towards a
s += end_group()
s += text(20, 30, [("t", "零初始狀態的 "), ("v", "s"), ("t", " 域等效電路（阻抗單位 Ω；"), ("v", "b"), ("t", " 為參考）")])
s += text(XL + 26, 196, [("n", "6"), ("v", "s"), ("n", "/("), ("v", "s"), ("n", "@SUP2@ + 36)")])
s += text(140, YT - 16, [("n", "2 Ω")], anchor="middle")
s += text(230, YT - 28, [("n", "4")], anchor="middle")
s += text(325, YT - 16, [("n", "2"), ("v", "s"), ("n", " Ω")], anchor="middle")
s += ttext(380, YT + 44, [("v", "I"), ("vsub", "L"), ("n", "("), ("v", "s"), ("n", ")")], anchor="middle", color=RED)
s += text(XR - 16, 206, [("n", "2 Ω")], anchor="end")
s += text(XI + 26, 206, [("n", "8")])
s += text(XC - 20, 272, [("n", "1/(2"), ("v", "s"), ("n", ") Ω")], anchor="end")
s += text(XR, YT - 14, [("v", "a")], anchor="middle")
s += text(XR, YB + 26, [("v", "b")], anchor="middle")
s += ttext(XO, YT + 34, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XO, 206, [("v", "V"), ("vsub", "ab"), ("n", "("), ("v", "s"), ("n", ")")], anchor="middle", color=BLUE)
s += ttext(XO, YB - 20, [("n", "−")], anchor="middle", color=BLUE)
s += footer()
s = s.replace('@SUP2@ + 36)', '</tspan><tspan class="n" font-family="KaTeX_Main, \'Times New Roman\', serif" font-size="12" baseline-shift="super">2</tspan>'
              '<tspan class="n" font-family="KaTeX_Main, \'Times New Roman\', serif"> + 36)')
write('EE-106-01-1-s-domain.svg', s)
