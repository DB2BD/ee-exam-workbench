"""EE-111-04-3 fig 2: 1800-rpm magnetization table (piecewise linear) and the R_fc = 0 field line 150.14 I_f."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
If = [0.0, 0.125, 0.25, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.48]
Ea = [5, 33.5, 67, 134, 160, 175, 190, 200, 214, 222]
W, H = 640, 380
ox, oy = 80, 320; sx, sy = 480 / 1.6, 260 / 240
P = lambda i, e: (ox + sx * i, oy - sy * e)
s = header(W, H)
s += arrow(ox, oy, ox + 520, oy) + arrow(ox, oy, ox, oy - 285)
for e in (50, 100, 150, 200):
    s += line(ox - 5, P(0, e)[1], ox, P(0, e)[1])
for i in (0.5, 1.0, 1.5):
    s += line(P(i, 0)[0], oy, P(i, 0)[0], oy + 5)
s += '<path d="M' + ' L'.join(f'{P(i, e)[0]:.1f} {P(i, e)[1]:.1f}' for i, e in zip(If, Ea)) + '" stroke-width="2"/>\n'
for i, e in zip(If, Ea):
    s += f'<circle cx="{P(i, e)[0]:.1f}" cy="{P(i, e)[1]:.1f}" r="2.2" fill="#000" stroke="none"/>\n'
s += line(*P(0, 0), *P(1.58, 150.14 * 1.58)).replace('/>', f' stroke="{BLUE}"/>')
X = P(1.4782, 221.94)
s += f'<circle cx="{X[0]:.1f}" cy="{X[1]:.1f}" r="4" fill="none" stroke="{BLUE}" stroke-width="1.5"/>\n'
s += f'<path d="M{X[0]:.1f} {X[1]+4:.1f} L{X[0]:.1f} {oy}" stroke-dasharray="4 3" stroke-width="1"/>\n'
s += f'<path d="M{ox} {X[1]:.1f} L{X[0]-4:.1f} {X[1]:.1f}" stroke-dasharray="4 3" stroke-width="1"/>\n'
s += end_group()
for e in (50, 100, 150, 200):
    s += text(ox - 9, P(0, e)[1] + 5, [("n", str(e))], anchor="end")
for i in (0.5, 1.0):
    s += text(P(i, 0)[0], oy + 22, [("n", f"{i:.1f}")], anchor="middle")
s += text(ox + 530, oy + 22, [("v", "I"), ("vsub", "f"), ("n", " (A)")], anchor="end")
s += text(ox + 8, oy - 280, [("v", "E"), ("vsub", "a"), ("n", " (V)")])
s += text(X[0], oy + 22, [("n", "1.4782")], anchor="middle")
s += text(ox - 9, X[1] + 5, [("n", "221.94")], anchor="end")
s += ctext(BLUE, X[0] - 12, X[1] - 12, [("t", "交點 "), ("v", "E"), ("vsub", "a"), ("n", " = 221.94 V")], anchor="end")
s += ctext(BLUE, P(1.42, 0)[0], P(0, 110)[1], [("t", "場阻線 "), ("v", "E"), ("vsub", "a"), ("n", " = 150.14"), ("v", "I"), ("vsub", "f")], anchor="end")
s += text(P(0.12, 0)[0], P(0, 240)[1], [("t", "磁化表（1800 rpm，表點直線連接）")])
s += text(W / 2, H - 8, [("t", "無載、"), ("v", "R"), ("vsub", "fc"), ("n", " = 0"), ("t", "：端電壓 "), ("v", "V"), ("vsub", "t"), ("n", " = 150(1.4782) = 221.73 V")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-111-04-3-field-line.svg'), 'w').write(s)
print(len(s))
