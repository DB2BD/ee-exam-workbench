"""Shared skeleton for EE-113-05-2: Eg' - jXg' - G - jXl - M - jXm' - Em' over a reference wire."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
W, H = 680, 320
YT, YB = 90, 250
XL, XR = 60, 620           # internal EMF sources
XG, XM = 230, 450          # generator terminal (fault point), motor terminal

def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')

def skeleton():
    s = header(W, H)
    for X in (XL, XR):
        s += line(X, YT, X, 156) + ac_source(X, 170) + line(X, 184, X, YB)
    s += coil(XL, YT, 190, YT, turns=4) + line(190, YT, XG, YT)            # Xg' = 0.25
    s += line(XG, YT, 290, YT) + coil(290, YT, 390, YT, turns=4) + line(390, YT, XM, YT)  # Xl = 0.1
    s += line(XM, YT, 490, YT) + coil(490, YT, XR, YT, turns=4)            # Xm' = 0.2
    s += line(XL, YB, XR, YB)
    s += dot(XG, YT) + dot(XM, YT)
    return s

def labels():
    s = text(125, YT - 16, [("v", "j"), ("n", "0.25")], anchor="middle")
    s += text(340, YT - 16, [("v", "j"), ("n", "0.1")], anchor="middle")
    s += text(555, YT - 16, [("v", "j"), ("n", "0.2")], anchor="middle")
    s += text(125, YT + 40, [("t", "（"), ("v", "X"), ("vsub", "g"), ("n", "′"), ("t", "）")], anchor="middle")
    s += text(340, YT + 40, [("t", "（"), ("v", "X"), ("vsub", "l"), ("t", "）")], anchor="middle")
    s += text(555, YT + 40, [("t", "（"), ("v", "X"), ("vsub", "m"), ("n", "′"), ("t", "）")], anchor="middle")
    s += text(XG, YT - 40, [("t", "發電機端 G")], anchor="middle")
    s += text(XM, YT - 40, [("t", "電動機端 M")], anchor="middle")
    s += text(XL + 22, 176, [("v", "E"), ("vsub", "g"), ("n", "′")])
    s += text(XR - 22, 176, [("v", "E"), ("vsub", "m"), ("n", "′")], anchor="end")
    return s

def write(s, name):
    p = pathlib.Path(__file__).resolve().parents[2].joinpath(f'02_題解/技師題解/05_電力系統/figures/EE-113-05-2-{name}.svg')
    p.write_text(s); print(len(s))
