import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 300
SX, YT, YB = 90, 60, 250
XN, XL, XC = 320, 420, 530
s = header(W, H)
SY = (YT + YB) // 2
s += f'<circle cx="{SX}" cy="{SY}" r="18"/>\n'
s += line(SX - 5, SY - 8, SX + 5, SY - 8) + line(SX, SY - 13, SX, SY - 3) + line(SX - 5, SY + 8, SX + 5, SY + 8)
s += line(SX, YT, SX, SY - 18) + line(SX, SY + 18, SX, YB)
s += line(SX, YT, 150, YT) + coil(150, YT, 270, YT, turns=5) + line(270, YT, XC, YT)      # Z22
s += line(XL, YT, XL, 85) + resistor(XL, 85, XL, 145) + line(XL, 145, XL, 160) + coil(XL, 160, XL, 220, turns=3) + line(XL, 220, XL, YB)   # Z_L
s += line(XC, YT, XC, 95) + line(XC, 140, XC, 150)                                          # switch for (三)
s += line(XC, 95, XC + 16, 128) + dot(XC, 95) + dot(XC, 140)
s += line(XC, 150, XC, 160) + line(XC - 14, 160, XC + 14, 160) + line(XC - 14, 168, XC + 14, 168) + line(XC, 168, XC, YB)   # capacitor
s += line(SX, YB, XC, YB) + dot(XN, YT) + dot(XN, YB) + dot(XL, YT) + dot(XL, YB)
s += arrow(338, YT - 16, 392, YT - 16, color=RED)
s += arrow(XN, YB - 6, XN, YT + 8, color=BLUE)                                              # V2: reference -> bus 2
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
s += ctext(BLUE, SX - 26, SY - 4, [("v", "V"), ("n", "⁽⁰⁾")], anchor="end")
s += ctext(BLUE, SX - 26, SY + 18, [("n", "1.25∠0°")], anchor="end")
s += lab(210, YT - 16, [("v", "Z"), ("sub", "22"), ("n", " = "), ("v", "j"), ("n", "0.29035")])
s += lab(XN, YT - 30, [("n", "Bus 2")])
s += ctext(BLUE, XN - 8, 170, [("v", "V"), ("sub", "2")], anchor="end")
s += ctext(RED, 365, YT - 26, [("v", "I"), ("vsub", "L"), ("t", "（二）／"), ("v", "I"), ("vsub", "LC"), ("t", "（三）")], anchor="start")
s += lab(XL + 12, 120, [("n", "0.4")], "start") + lab(XL + 12, 196, [("v", "j"), ("n", "0.3")], "start")
s += lab(XL - 12, 160, [("v", "Z"), ("vsub", "L")], "end")
s += lab(XC + 20, 168, [("n", "−"), ("v", "j"), ("n", "0.3")], "start")
s += lab(XC - 10, 98, [("t", "（三）閉合")], "end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-104-05-4-thevenin.svg'), 'w').write(s)
print(len(s))
