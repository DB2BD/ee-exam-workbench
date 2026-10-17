import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 690, 300
YT, YB = 80, 230
XS, XR, XL, XC = 70, 380, 470, 590      # sending source, receiving node, load, capacitor
s = header(W, H)
s += line(XS, YT, XS, 141) + ac_source(XS, 155) + line(XS, 169, XS, YB)
s += line(XS, YT, 110, YT) + resistor(110, YT, 180, YT) + line(180, YT, 200, YT) + coil(200, YT, 300, YT, turns=4) + line(300, YT, XC, YT)
s += line(XL, YT, XL, 125) + f'<path d="M{XL - 12} 125 L{XL + 12} 125 L{XL + 12} 185 L{XL - 12} 185 Z"/>\n' + line(XL, 185, XL, YB)   # load
s += line(XC, YT, XC, 151) + line(XC - 14, 151, XC + 14, 151) + line(XC - 14, 159, XC + 14, 159) + line(XC, 159, XC, YB)                # capacitor
s += line(XS, YB, XC, YB)
s += line(XR, YB, XR, YB + 8) + ground(XR, YB + 8)
s += dot(XR, YT) + dot(XR, YB) + dot(XL, YT) + dot(XL, YB)
s += arrow(XR, YB - 6, XR, YT + 14, color=BLUE)          # V_R: reference -> receiving node (+)
s += arrow(312, YT - 14, 356, YT - 14, color=RED)
s += end_group()
s += ctext(BLUE, XS + 24, 150, [("v", "V"), ("vsub", "S")])
s += ctext(BLUE, XS + 24, 172, [("n", "= 1.0805∠17.23°")])
s += text(205, YT - 16, [("v", "Z"), ("n", " = 0.02 + "), ("v", "j"), ("n", "0.2")], anchor="middle")
s += text(205, YT + 30, [("t", "輸電線路")], anchor="middle")
s += ctext(RED, 334, YT - 24, [("v", "I"), ("n", " = 1.6∠0°")], anchor="middle")
s += text(XR + 10, YT + 28, [("t", "受電端")])
s += ctext(BLUE, XR - 10, 160, [("v", "V"), ("vsub", "R")], anchor="end")
s += ctext(BLUE, XR - 10, 182, [("n", "= 1∠0°")], anchor="end")
s += text(XL + 18, 150, [("v", "S"), ("vsub", "L")])
s += text(XL + 18, 172, [("n", "= 1.6 + "), ("v", "j"), ("n", "1.2")])
s += text(XC + 20, 150, [("v", "S"), ("vsub", "C")])
s += text(XC + 20, 172, [("n", "= −"), ("v", "j"), ("n", "1.2")])
s += text(345, 284, [("t", "標么值；電容器組與負載並聯於受電端")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-107-05-1-circuit.svg'), 'w').write(s)
print(len(s))
