import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 350
OX, OY = 80, 280                  # origin (t = 0, delta = 0)
D0, DCR = 230, 90                 # y of delta_0 and delta_cr
TA = 400                          # x of t_cr,A ; t_cr,B = TA * sqrt(0.5)
TB = OX + (TA - OX) * math.sqrt(0.5)
s = header(W, H)
s += arrow(OX, OY, 560, OY) + arrow(OX, OY, OX, 30)
def curve(tcr, xmax):
    k = (D0 - DCR) / (tcr - OX) ** 2
    pts = []
    x = OX
    while x <= xmax:
        y = D0 - k * (x - OX) ** 2
        if y < 50: break
        pts.append(f'{x:.1f} {y:.1f}'); x += 4
    return 'M' + ' L'.join(pts)
s += f'<path d="{curve(TA, 520)}"/>\n'
s += f'<path d="{curve(TB, 520)}" stroke="{BLUE}"/>\n'
s += f'<path d="M{OX} {DCR} L540 {DCR}" stroke-dasharray="5 4"/>\n'
s += f'<path d="M{TA:.1f} {DCR} L{TA:.1f} {OY}" stroke-dasharray="5 4"/>\n'
s += f'<path d="M{TB:.1f} {DCR} L{TB:.1f} {OY}" stroke-dasharray="5 4" stroke="{BLUE}"/>\n'
s += dot(TA, DCR) + dot(TB, DCR)
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
s += lab(566, OY + 5, [("v", "t")], "start") + lab(OX, 22, [("v", "δ")])
s += lab(OX - 8, D0 + 5, [("v", "δ"), ("sub", "0")], "end") + lab(OX - 8, DCR + 5, [("v", "δ"), ("vsub", "cr")], "end")
s += lab(TA, OY + 22, [("v", "t"), ("vsub", "cr,A")])
s += ctext(BLUE, TB, OY + 22, [("v", "t"), ("vsub", "cr,B")], anchor="middle")
s += lab(TA + 30, 150, [("t", "甲案 "), ("v", "H"), ("vsub", "A"), ("n", " = "), ("v", "H")], "start")
s += ctext(BLUE, TB - 40, 130, [("t", "乙案 "), ("v", "H"), ("vsub", "B"), ("n", " = 0.5"), ("v", "H")], anchor="end")
s += ctext(BLUE, 300, 338, [("v", "t"), ("vsub", "cr,B"), ("n", " = 0.71 "), ("v", "t"), ("vsub", "cr,A")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-105-05-4-swing.svg'), 'w').write(s)
print(len(s))
