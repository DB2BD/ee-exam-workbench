import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Qualitative power-angle curves on the synchronous units' own base: same Pm, weaker grid in plan B
# (larger transfer reactance -> lower Pmax) -> larger delta_0 and smaller delta_cr, i.e. a smaller
# margin delta_cr - delta_0.  Shape only (illustrative Pmax,A = 1, Pmax,B = 0.7, Pm = 0.5); no values shown.
W, H = 620, 400
ox, oy = 70, 290
X = lambda deg: ox + deg * 2.6
Y = lambda p: oy - p * 220
PA, PB, PM = 1.0, 0.7, 0.5
def dcr(pmax):
    d0 = math.asin(PM / pmax); dm = math.pi - d0
    return d0, math.acos(PM / pmax * (dm - d0) + math.cos(dm))
s = header(W, H)
s += arrow(ox, oy, X(190), oy) + arrow(ox, oy, ox, 40)
for pmax, dash in ((PA, ''), (PB, ' stroke-dasharray="7 4"')):
    pts = ' L'.join(f'{X(d):.1f} {Y(pmax * math.sin(math.radians(d))):.1f}' for d in range(0, 181, 3))
    s += f'<path d="M{pts}"{dash}/>\n'
s += f'<path d="M{ox} {Y(PM):.1f} L{X(180):.1f} {Y(PM):.1f}" stroke-width="1"/>\n'
ticks = []
for pmax, row in ((PA, 0), (PB, 1)):
    d0, dc = dcr(pmax)
    for ang in (d0, dc):
        x = X(math.degrees(ang))
        y = Y(PM) if ang == d0 else Y(pmax * math.sin(ang))
        s += f'<path d="M{x:.1f} {y:.1f} L{x:.1f} {oy + 6 + 22 * row}" stroke-width="1" stroke-dasharray="4 3"/>\n'
        s += dot(x, y)
        ticks.append((x, row, ang == d0))
s += end_group()
for x, row, is0 in ticks:
    case = "A" if row == 0 else "B"
    sub = [("sub", "0,"), ("vsub", case)] if is0 else [("vsub", "cr," + case)]
    s += text(x, oy + 22 + 22 * row, [("v", "δ")] + sub, anchor="middle")
s += text(X(190) + 4, oy + 5, [("v", "δ")])
s += text(ox - 8, 36, [("v", "P")], anchor="start")
s += text(ox - 8, Y(PM) + 5, [("v", "P"), ("vsub", "m")], anchor="end")
s += f'<path d="M430 44 L466 44" stroke="#000" stroke-width="1.5"/>\n<path d="M430 72 L466 72" stroke="#000" stroke-width="1.5" stroke-dasharray="7 4"/>\n'
s += text(474, 49, [("t", "甲案 "), ("v", "P"), ("sub", "max,"), ("vsub", "A"), ("n", " sin "), ("v", "δ")])
s += text(474, 77, [("t", "乙案 "), ("v", "P"), ("sub", "max,"), ("vsub", "B"), ("n", " sin "), ("v", "δ")])
s += text(310, 362, [("t", "系統變弱："), ("v", "P"), ("sub", "max"), ("t", " 降低 → "), ("v", "δ"), ("sub", "0"), ("t", " 增大、"), ("v", "δ"), ("vsub", "cr"), ("t", " 減小")], anchor="middle")
s += text(310, 386, [("t", "裕度 "), ("v", "δ"), ("vsub", "cr"), ("n", " − "), ("v", "δ"), ("sub", "0"), ("t", " 變小（同步機自身基準，示意）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-105-05-4-power-angle.svg'), 'w').write(s)
print(len(s))
