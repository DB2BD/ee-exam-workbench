import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# One phase's square 4-bundle: sub-conductor 1 sees d, d and sqrt(2) d to the other three.
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def dim(x1, y1, x2, y2):
    return (f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{BLUE}" stroke-width="1.2" stroke-dasharray="5 3"/>\n')
W, H = 560, 360
S = 180; X0, Y0 = 170, 70
pts = {1: (X0, Y0 + S), 2: (X0 + S, Y0 + S), 3: (X0, Y0), 4: (X0 + S, Y0)}
R = 14
s = header(W, H)
s += dim(*pts[1], *pts[2]) + dim(*pts[1], *pts[3]) + dim(*pts[1], *pts[4])
for k, (x, y) in pts.items():
    s += f'<circle cx="{x}" cy="{y}" r="{R}" fill="#fff"/>\n'
s += end_group()
for k, (x, y) in pts.items():
    s += text(x, y + 6, [("n", str(k))], anchor="middle")
s += ctext(BLUE, X0 + S / 2, Y0 + S + 34, [("v", "d"), ("n", " = 50 cm")], anchor="middle")
s += ctext(BLUE, X0 - 24, Y0 + S / 2 + 5, [("v", "d"), ("n", " = 50 cm")], anchor="end")
s += ctext(BLUE, X0 + S / 2 + 12, Y0 + S / 2 + 26, [("n", "√2 "), ("v", "d")])
s += text(X0 + S + 30, Y0 + 6, [("t", "每根子導線")])
s += text(X0 + S + 30, Y0 + 30, [("t", "自身：GMR 或 "), ("v", "r")])
s += text(W / 2, H - 22, [("t", "子導線 1 到其他三根："), ("v", "d"), ("n", "、"), ("v", "d"), ("n", "、√2 "), ("v", "d"), ("t", "（四根情況相同）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-112-05-1-bundle.svg'), 'w').write(s)
print(len(s))
