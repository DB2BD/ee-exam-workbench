import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def cap_v(x, y1, y2):
    """Vertical capacitor between y1 and y2 (two plates, gap 8)."""
    m = (y1 + y2) / 2
    return line(x, y1, x, m - 4) + line(x - 13, m - 4, x + 13, m - 4) + line(x - 13, m + 4, x + 13, m + 4) + line(x, m + 4, x, y2)
W, H = 640, 366
YT, YB = 70, 300
XS, XA, XD, XY = 70, 330, 400, 560
s = header(W, H)
s += line(XS, YT, XS, 171) + ac_source(XS, 185) + line(XS, 199, XS, YB)                 # Vφ
s += line(XS, YT, 110, YT) + resistor(110, YT, 180, YT) + coil(190, YT, 270, YT, turns=4)
s += line(180, YT, 190, YT) + line(270, YT, XA, YT)                                       # Zl = 1 + j1
s += line(XA, YT, XY, YT)
s += line(XD, YT, XD, 100) + resistor(XD, 100, XD, 170) + line(XD, 170, XD, 200) + cap_v(XD, 200, 250) + line(XD, 250, XD, YB)   # ZΔ/3
s += line(XY, YT, XY, 100) + resistor(XY, 100, XY, 170) + line(XY, 170, XY, 190) + coil(XY, 190, XY, 250, turns=3) + line(XY, 250, XY, YB)  # ZY
s += line(XS, YB, XY, YB)
s += dot(XA, YT) + dot(XD, YT) + dot(XD, YB)
s += arrow(282, YT - 8, 318, YT - 8, color=RED)
s += end_group()
s += ctext(BLUE, XS + 22, 182, [("v", "V"), ("vsub", "φ")])
s += ctext(BLUE, XS + 22, 204, [("n", "121.24∠0° V")])
s += text(145, YT - 16, [("n", "1 Ω")], anchor="middle")
s += text(230, YT - 16, [("v", "j"), ("n", "1 Ω")], anchor="middle")
s += text(190, YT + 30, [("v", "Z"), ("vsub", "l")], anchor="middle")
s += ctext(RED, 300, YT - 28, [("v", "I"), ("vsub", "L")], anchor="middle")
s += text(XA, YT + 28, [("n", "a")], anchor="middle")
s += text(XD - 14, 140, [("n", "8 Ω")], anchor="end")
s += text(XD - 18, 230, [("n", "−"), ("v", "j"), ("n", "10 Ω")], anchor="end")
s += text(XD + 18, 186, [("v", "Z"), ("sub", "Δ"), ("n", "/3")])
s += text(XY + 14, 140, [("n", "12 Ω")])
s += text(XY + 14, 226, [("v", "j"), ("n", "5 Ω")])
s += text(XY - 18, 186, [("v", "Z"), ("sub", "Y")], anchor="end")
s += text(320, 346, [("t", "每相等效：中性點 n 為參考，"), ("v", "Z"), ("sub", "in"), ("n", " = "), ("v", "Z"), ("vsub", "l"), ("n", " + ("), ("v", "Z"), ("sub", "Δ"), ("n", "/3 ∥ "), ("v", "Z"), ("sub", "Y"), ("n", ")")], anchor="middle")
s += text(XS - 8, YB + 20, [("n", "n")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-113-05-1-per-phase.svg'), 'w').write(s)
print(len(s))
