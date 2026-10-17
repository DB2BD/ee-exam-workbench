"""EE-111-04-2 fig 1: T(s) curve of the given formula, load line 100 N·m, both roots of T(s)=100."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
T = lambda s: 207.63 * s / (s * s + 0.0925 * s + 0.0382)
W, H = 680, 360; X0, Y0 = 70, 310; KX, KY = 270.0, 0.50     # px per unit slip, px per N·m
P = lambda s, t: (X0 + KX * s, Y0 - KY * t)
s = header(W, H)
sm = 0.0382 ** 0.5
s += f'<rect x="{X0}" y="60" width="{KX * sm:.1f}" height="{Y0 - 60}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(X0, Y0, X0 + KX * 2.15, Y0) + arrow(X0, Y0, X0, 56)          # axes
pts = [P(k / 1000 * 2.1, T(k / 1000 * 2.1)) for k in range(0, 1001)]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + '"/>\n'
yl = Y0 - KY * 100
s += f'<path d="M{X0} {yl} L{X0 + KX * 2.1:.1f} {yl}" stroke="{BLUE}" stroke-dasharray="7 4"/>\n'
sm = 0.0382 ** 0.5
xm, ym = P(sm, T(sm))
s += f'<path d="M{xm:.1f} {ym:.1f} L{xm:.1f} {Y0}" stroke-dasharray="3 3" stroke-width="1"/>\n'
x1 = X0 + KX * 0.0194466; x2 = X0 + KX * 1.9644; x3 = X0 + KX * 1.0
s += f'<path d="M{x3:.1f} {Y0} L{x3:.1f} 70" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += dot(x1, yl) + dot(x2, yl) + dot(xm, ym)
s += line(x1, yl, 150, 196)                                             # leader to s1 label
s += end_group()
s += text(X0 + KX * 2.15, Y0 + 24, [("v", "s")], anchor="middle")
s += text(X0 + 10, 40, [("v", "T"), ("vsub", "mech"), ("n", " (N·m)")])
s += text(X0, Y0 + 22, [("n", "0")], anchor="middle")
s += text(x3, Y0 + 22, [("n", "1")], anchor="middle")
s += text(xm + 4, Y0 + 22, [("v", "s"), ("vsub", "T"), ("sub", "max"), ("n", " = 0.1954")])
s += text(xm, ym - 10, [("v", "T"), ("sub", "max")], anchor="middle")
s += text(152, 192, [("v", "s"), ("sub", "1"), ("n", " = 0.0194466（取）")])
s += text(x2 - 10, yl - 22, [("v", "s"), ("n", " = 1.9644（捨）")], anchor="middle")
s += ctext(BLUE, X0 + KX * 1.3, yl + 22, [("t", "負載 "), ("v", "T"), ("vsub", "L"), ("n", " = 100 N·m")])
s += text(X0 + 7, 282, [("t", "穩定")]) + text(X0 + 4, 300, [("t", "運轉區")])
s += text(x3 + 6, 90, [("v", "s"), ("n", " > 1：反轉制動區")])
s += text(x3 - 6, 90, [("v", "n"), ("n", " = 0")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-111-04-2-torque-slip.svg'), 'w').write(s)
print(len(s))
