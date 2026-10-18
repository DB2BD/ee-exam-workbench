import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# P–δ curves before / after series compensation (shape only, illustrative k = 0.5; no values shown).
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 400
ox, oy = 70, 300
X = lambda deg: ox + deg * 2.6
Y = lambda p: oy - p * 120
PU, PC, P0 = 1.0, 2.0, 0.8
s = header(W, H)
s += arrow(ox, oy, X(195), oy) + arrow(ox, oy, ox, 34)
for pmax, extra in ((PU, ' stroke-dasharray="7 4"'), (PC, f' stroke="{BLUE}"')):
    pts = ' L'.join(f'{X(d):.1f} {Y(pmax * math.sin(math.radians(d))):.1f}' for d in range(0, 181, 3))
    s += f'<path d="M{pts}"{extra}/>\n'
s += f'<path d="M{ox} {Y(P0):.1f} L{X(180):.1f} {Y(P0):.1f}" stroke-width="1"/>\n'
for pmax in (PU, PC):
    y = Y(pmax)
    s += f'<path d="M{ox} {y:.1f} L{X(90):.1f} {y:.1f}" stroke-width="1" stroke-dasharray="4 3"/>\n'
s += f'<path d="M{X(90):.1f} {Y(PC):.1f} L{X(90):.1f} {oy}" stroke-width="1" stroke-dasharray="4 3"/>\n'
dc = math.degrees(math.asin(P0 / PC)); du = math.degrees(math.asin(P0 / PU))
for d in (dc, du):
    s += f'<path d="M{X(d):.1f} {Y(P0):.1f} L{X(d):.1f} {oy}" stroke-width="1" stroke-dasharray="4 3"/>\n' + dot(X(d), Y(P0))
s += end_group()
s += text(X(195) + 4, oy + 5, [("v", "δ")])
s += text(ox - 6, 30, [("v", "P")], anchor="end")
s += text(ox - 8, Y(PU) + 5, [("v", "P"), ("sub", "max,"), ("vsub", "u")], anchor="end")
s += ctext(BLUE, ox - 8, Y(PC) + 5, [("v", "P"), ("sub", "max,"), ("vsub", "c")], anchor="end")
s += text(ox - 8, Y(P0) + 5, [("v", "P"), ("sub", "0")], anchor="end")
s += text(X(dc), oy + 22, [("v", "δ"), ("vsub", "c")], anchor="middle")
s += text(X(du), oy + 22, [("v", "δ"), ("vsub", "u")], anchor="middle")
s += text(X(90), oy + 22, [("n", "90°")], anchor="middle")
s += text(X(180), oy + 22, [("n", "180°")], anchor="middle")
s += f'<path d="M420 50 L456 50" stroke="#000" stroke-width="1.5" stroke-dasharray="7 4"/>\n<path d="M420 78 L456 78" stroke="{BLUE}" stroke-width="1.5"/>\n'
s += text(464, 55, [("t", "未補償 "), ("v", "V"), ("vsub", "S"), ("v", "V"), ("vsub", "R"), ("n", "/"), ("v", "X"), ("vsub", "L"), ("n", "·sin "), ("v", "δ")])
s += ctext(BLUE, 464, 83, [("t", "補償後 "), ("v", "V"), ("vsub", "S"), ("v", "V"), ("vsub", "R"), ("n", "/"), ("v", "X"), ("vsub", "eq"), ("n", "·sin "), ("v", "δ")])
s += text(W / 2, 360, [("t", "同一 "), ("v", "P"), ("sub", "0"), ("t", "：補償後 "), ("v", "δ"), ("vsub", "c"), ("n", " &lt; "), ("v", "δ"), ("vsub", "u"), ("t", "，離 90° 的裕度變大（示意，"), ("v", "k"), ("n", " = 0.5"), ("t", "）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-111-05-1-power-angle.svg'), 'w').write(s)
print(len(s))
