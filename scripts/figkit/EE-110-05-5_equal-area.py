import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
W, H = 640, 360
ox, oy, sx, sy = 70, 290, 460 / math.pi, 220      # δ (rad) → x, P/Pmax → y
X = lambda d: ox + sx * d
Y = lambda p: oy - sy * p
d0 = math.radians(10); d1 = 0.890149; dm = math.pi - d1; pm = math.sin(d1); p0 = math.sin(d0)
def curve(a, b, n=60):
    return [(X(a + (b - a) * k / n), Y(math.sin(a + (b - a) * k / n))) for k in range(n + 1)]
pts = lambda P: ' L'.join(f'{x:.1f} {y:.1f}' for x, y in P)
s = header(W, H)
# A1: between Pm line and sine, δ0..δ1
A1 = curve(d0, d1)
s += f'<path d="M{X(d0):.1f} {Y(pm):.1f} L{pts(A1)} Z" fill="{FILL_RED}" stroke="none"/>\n'
A2 = curve(d1, dm)
s += f'<path d="M{pts(A2)} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(ox, oy, ox + 500, oy) + arrow(ox, oy, ox, oy - 260)
s += f'<path d="M{pts(curve(0, math.pi, 120))}"/>\n'
s += f'<path d="M{ox} {Y(pm):.1f} L{X(math.pi) + 10:.1f} {Y(pm):.1f}" stroke="{RED}"/>\n'
s += f'<path d="M{ox} {Y(p0):.1f} L{X(d0) + 30:.1f} {Y(p0):.1f}" stroke-dasharray="4 3" stroke-width="1"/>\n'
for d in (d0, d1, dm):
    top = Y(math.sin(d)) if d != d0 else Y(pm)
    s += f'<path d="M{X(d):.1f} {oy} L{X(d):.1f} {top:.1f}" stroke-dasharray="4 3" stroke-width="1"/>\n'
s += dot(X(d0), Y(p0)) + dot(X(d1), Y(pm)) + dot(X(dm), Y(pm))
s += end_group()
s += text(ox + 506, oy + 5, [("v", "δ")])
s += text(ox - 6, oy - 266, [("v", "P")], anchor="end")
s += text(X(1.0) - 6, Y(0.97), [("v", "P"), ("vsub", "e"), ("n", " = "), ("v", "P"), ("sub", "max"), ("n", " sin "), ("v", "δ")], anchor="end")
s += text(X(math.pi) + 10, Y(pm) - 10, [("v", "P"), ("vsub", "m"), ("n", " = "), ("v", "P"), ("sub", "max"), ("n", " sin "), ("v", "δ"), ("sub", "1")], anchor="end", color=RED)
s += text(ox - 6, Y(p0) + 5, [("n", "0.1736")], anchor="end")
s += text(ox - 6, Y(pm) + 5, [("n", "0.7772")], anchor="end")
s += text(X(d0), oy + 20, [("v", "δ"), ("sub", "0")], anchor="middle")
s += text(X(d1), oy + 20, [("v", "δ"), ("sub", "1")], anchor="middle")
s += text(X(dm), oy + 20, [("v", "π"), ("n", " − "), ("v", "δ"), ("sub", "1")], anchor="middle")
s += text(X(d0), oy + 40, [("n", "10°")], anchor="middle")
s += text(X(d1), oy + 40, [("n", "51.00°")], anchor="middle")
s += text(X(dm), oy + 40, [("n", "129.00°")], anchor="middle")
s += text(X(math.pi), oy + 20, [("v", "π")], anchor="middle")
s += text(X(0.62), Y(pm) + 40, [("v", "A"), ("sub", "1")], anchor="middle")
s += text(X(1.57), Y(pm) - 20, [("v", "A"), ("sub", "2")], anchor="middle")
s += text(560, 30, [("t", "縱軸以 "), ("v", "P"), ("sub", "max"), ("t", " 為單位")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-110-05-5-equal-area.svg'), 'w').write(s)
print(len(s))
