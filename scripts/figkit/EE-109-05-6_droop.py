import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def dashed(x1, y1, x2, y2, color="#000"):
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="5 4"/>\n'
# Droop lines f = 60 - (P - P0)/beta_i for both units; operating points move from 60 Hz to 59.65 Hz.
W, H = 640, 380
ox, oy = 80, 320
X = lambda p: ox + (p - 150) * 0.98          # 150..650 MW -> 80..570 px
Y = lambda f: oy - (f - 59.45) * 380         # 59.45..60.15 Hz -> 320..54 px
b1, b2, f1 = 500 / 3, 800 / 3, 60 - 9 / 26
s = header(W, H)
s += arrow(ox, oy, 600, oy) + arrow(ox, oy, ox, 40)
s += dashed(ox, Y(60), 590, Y(60))
s += dashed(ox, Y(f1), 590, Y(f1), BLUE)
for p0, b in ((200, b1), (500, b2)):
    fa, fb = 60.1, 59.52
    s += line(X(p0 - b * (fa - 60)), Y(fa), X(p0 - b * (fb - 60)), Y(fb))
    p1 = p0 + b * (60 - f1)
    s += dashed(X(p0), Y(60), X(p0), oy) + dashed(X(p1), Y(f1), X(p1), oy, BLUE)
    s += dot(X(p0), Y(60)) + f'<circle cx="{X(p1):.1f}" cy="{Y(f1):.1f}" r="3.2" fill="{BLUE}" stroke="none"/>\n'
s += end_group()
s += text(ox - 8, Y(60) + 5, [("n", "60")], anchor="end")
s += ctext(BLUE, ox - 8, Y(f1) + 5, [("n", "59.65")], anchor="end")
s += text(ox - 10, 36, [("v", "f"), ("n", " (Hz)")], anchor="start")
s += text(600, oy + 40, [("v", "P"), ("n", " (MW)")], anchor="end")
s += text(X(200), oy + 22, [("n", "200")], anchor="middle")
s += ctext(BLUE, X(257.69) + 4, oy + 22, [("n", "257.69")], anchor="start")
s += text(X(500), oy + 22, [("n", "500")], anchor="middle")
s += ctext(BLUE, X(592.31) + 4, oy + 22, [("n", "592.31")], anchor="start")
s += text(X(200 - b1 * 0.1) + 16, Y(60.1) + 4, [("t", "機組 1")])
s += text(X(200 - b1 * 0.1) + 16, Y(60.1) + 24, [("t", "斜率 −1/"), ("v", "β"), ("sub", "1")])
s += text(X(500 - b2 * 0.1) + 16, Y(60.1) + 4, [("t", "機組 2")])
s += text(X(500 - b2 * 0.1) + 16, Y(60.1) + 24, [("t", "斜率 −1/"), ("v", "β"), ("sub", "2")])
s += ctext(BLUE, X(257.69) + 16, Y(f1) - 8, [("t", "新穩態："), ("n", "Δ"), ("v", "f"), ("n", " = −0.34615 Hz")])
s += text(590, Y(60) + 22, [("t", "負載增加前")], anchor="end")
s += text(330, 368, [("n", "Δ"), ("v", "P"), ("sub", "1"), ("n", " + "), ("n", "Δ"), ("v", "P"), ("sub", "2"), ("n", " = 57.69 + 92.31 = 150 MW")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-109-05-6-droop.svg'), 'w').write(s)
print(len(s))
