"""EE-111-01-3: s-domain circuit — R in parallel with series L-C forms Z_p, divided against R_o."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 640, 300, 80, 250
XS, XN, XL, XO = 100, 360, 490, 600
s = header(W, H)
s += (f'<rect x="{XN - 40}" y="{YT + 22}" width="{XL - XN + 92}" height="{YB - YT - 44}" fill="{FILL_BLUE}" '
      f'stroke="{BLUE}" stroke-dasharray="6 4"/>\n')
s += vsrc(XS, YT, XS, YB)
s += line(XS, YT, 170, YT) + resistor(170, YT, 270, YT) + line(270, YT, XO, YT)
s += line(XS, YB, XO, YB)
s += resistor(XN, YT, XN, YB, zigs=6, lead=50)
s += line(XL, YT, XL, 115) + coil(XL, 115, XL, 160, turns=3) + line(XL, 160, XL, 180) + cap(XL, 180, XL, 220) + line(XL, 220, XL, YB)
for x in (XN, XL):
    s += dot(x, YT) + dot(x, YB)
s += terminal(XO, YT) + terminal(XO, YB)
s += end_group()
s += text(20, 32, [("t", "零初值 "), ("v", "s"), ("t", " 域：電感 → "), ("v", "sL"), ("t", "，電容 → "), ("n", "1/("), ("v", "sC"), ("n", ")")])
s += text(XS - 24, (YT + YB) / 2 + 6, [("v", "V"), ("vsub", "i"), ("n", "("), ("v", "s"), ("n", ")")], anchor="end")
s += text(220, YT - 14, [("v", "R"), ("vsub", "o")], anchor="middle")
s += text(XN - 16, (YT + YB) / 2 + 6, [("v", "R")], anchor="end")
s += text(XL + 16, 143, [("v", "sL")])
s += text(XL + 16, 206, [("n", "1/("), ("v", "sC"), ("n", ")")])
s += ttext(XL - 14, 175, [("v", "Z"), ("vsub", "LC")], anchor="end", color=BLUE)
s += ttext(XN - 32, YT + 44, [("v", "Z"), ("vsub", "p")], color=BLUE)
s += ttext(XO + 4, YT + 30, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XO + 4, YB - 18, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XO + 2, (YT + YB) / 2 + 6, [("v", "V"), ("vsub", "o"), ("n", "("), ("v", "s"), ("n", ")")], anchor="middle", color=BLUE)
s += footer()
write('EE-111-01-3-s-domain.svg', s)
