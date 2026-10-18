import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def cap_h(x1, x2, y):
    m = (x1 + x2) / 2
    return line(x1, y, m - 4, y) + line(m - 4, y - 13, m - 4, y + 13) + line(m + 4, y - 13, m + 4, y + 13) + line(m + 4, y, x2, y)
def cap_v(x, y1, y2):
    m = (y1 + y2) / 2
    return line(x, y1, x, m - 4) + line(x - 13, m - 4, x + 13, m - 4) + line(x - 13, m + 4, x + 13, m + 4) + line(x, m + 4, x, y2)
def switch_h(x1, x2, y):
    return dot(x1, y) + dot(x2, y) + line(x1, y, x2 - 6, y - 14)
def switch_v(x, y1, y2):
    return dot(x, y1) + dot(x, y2) + line(x, y1, x + 14, y2 - 6)
W, H = 700, 330
YW = 150                              # main conductor
XS, XR = 70, 470                      # sending / receiving bus
XA, XB = 150, 270                     # series-capacitor bank terminals
XC, XL = 540, 620                     # shunt capacitor / shunt reactor branches
s = header(W, H)
s += f'<path d="M{XS} {YW - 45} L{XS} {YW + 45}" stroke-width="5"/>\n'
s += f'<path d="M{XR} {YW - 45} L{XR} {YW + 45}" stroke-width="5"/>\n'
s += line(XS, YW, XA, YW) + cap_h(XA, XB, YW)                         # series C
s += line(XA, YW, XA, 60) + line(XB, YW, XB, 60)
s += line(XA, 105, 180, 105) + resistor(180, 105, 240, 105, zigs=6, lead=6) + line(240, 105, XB, 105)   # MOV
s += line(XA, 60, 190, 60) + switch_h(190, 230, 60) + line(230, 60, XB, 60)                          # bypass switch
s += line(XB, YW, 300, YW) + coil(300, YW, 430, YW, turns=5) + line(430, YW, XR, YW)                  # line X_L
s += line(XR, YW, 660, YW)
s += arrow(660, YW, 690, YW)                                                                         # to load
s += line(XC, YW, XC, 172) + switch_v(XC, 172, 198) + line(XC, 198, XC, 210) + cap_v(XC, 210, 250) + line(XC, 250, XC, 262) + ground(XC, 262)
s += line(XL, YW, XL, 180) + coil(XL, 180, XL, 250, turns=4) + line(XL, 250, XL, 262) + ground(XL, 262)
s += dot(XA, YW) + dot(XB, YW) + dot(XA, 105) + dot(XB, 105) + dot(XC, YW) + dot(XL, YW)
s += end_group()
s += ctext(BLUE, XS, YW - 56, [("v", "V"), ("vsub", "S"), ("n", "∠"), ("v", "δ")], anchor="middle")
s += text(XS, YW + 68, [("t", "送電端")], anchor="middle")
s += ctext(BLUE, XR, YW - 56, [("v", "V"), ("vsub", "R"), ("n", "∠0°")], anchor="middle")
s += text(XR, YW + 68, [("t", "受電端")], anchor="middle")
s += text((XA + XB) / 2, 40, [("t", "旁路開關")], anchor="middle")
s += text((XA + XB) / 2, 90, [("n", "MOV")], anchor="middle")
s += text((XA + XB) / 2, YW + 34, [("n", "−"), ("v", "j"), ("v", "X"), ("vsub", "C")], anchor="middle")
s += text((XA + XB) / 2, YW + 56, [("t", "串聯電容器")], anchor="middle")
s += text(365, YW - 20, [("v", "j"), ("v", "X"), ("vsub", "L")], anchor="middle")
s += text(365, YW + 34, [("t", "線路")], anchor="middle")
s += text(690, YW - 14, [("v", "P"), ("n", " + "), ("v", "j"), ("v", "Q")], anchor="end")
s += text(XC - 18, 236, [("v", "Q"), ("vsub", "c")], anchor="end")
s += text(XL + 16, 220, [("v", "Q"), ("vsub", "r")])
s += text(XC, 300, [("t", "並聯電容器")], anchor="middle")
s += text(XL + 22, 300, [("t", "並聯電抗器")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-105-05-1-one-line.svg'), 'w').write(s)
print(len(s))
